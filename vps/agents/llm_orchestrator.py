"""LLM Agent Orchestrator with usage tracking."""

import asyncio
import json
import os
from datetime import datetime, timezone
from typing import Dict, List, Any
import aiohttp

from .llm_agents import (
    LLMTrendAgent,
    LLMMomentumAgent,
    LLMVolatilityAgent,
    LLMSentimentAgent,
    LLMFundingAgent,
    LLMRiskAgent,
)
from .signal_aggregator import SignalAggregator
from .llm_client import LLMClient

CF_ACCOUNT_ID = os.environ.get("CF_ACCOUNT_ID")
CF_API_TOKEN = os.environ.get("CF_API_TOKEN")
KV_NAMESPACE_ID = os.environ.get("KV_LIVE_STATE_ID")
QUESTDB_URL = "http://localhost:9001"


class LLMOrchestrator:
    """Manages LLM-powered trading agents with full usage tracking."""
    
    def __init__(self, symbol: str = "BTCUSDT"):
        self.symbol = symbol
        self.running = False
        self.agents = {
            "Trend": LLMTrendAgent(symbol),
            "Momentum": LLMMomentumAgent(symbol),
            "Volatility": LLMVolatilityAgent(symbol),
            "Sentiment": LLMSentimentAgent(symbol),
            "Funding": LLMFundingAgent(symbol),
            "Risk": LLMRiskAgent(symbol),
        }
        self.aggregator = SignalAggregator()
        self.last_signals = []
        self.last_aggregated = None
        self.cycle_count = 0
        self.total_llm_calls = 0
        self.total_tokens = 0
        self.total_cost = 0.0
        
    async def run_cycle(self) -> Dict[str, Any]:
        """Run one full LLM analysis cycle."""
        print(f"[llm-agents] Starting LLM analysis cycle #{self.cycle_count + 1}")
        
        # Run all agents concurrently
        tasks = [agent.run() for agent in self.agents.values()]
        signals = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Filter out errors and track usage
        valid_signals = []
        cycle_usage = {
            "llm_calls": 0,
            "prompt_tokens": 0,
            "completion_tokens": 0,
            "total_tokens": 0,
            "cost_usd": 0.0,
            "response_time_ms": 0,
        }
        
        for i, signal in enumerate(signals):
            agent_name = list(self.agents.keys())[i]
            
            if isinstance(signal, Exception):
                print(f"[llm-agents] {agent_name} failed: {signal}")
                continue
            
            valid_signals.append(signal)
            
            # Track LLM usage
            usage = signal.get("usage", {})
            if usage:
                cycle_usage["llm_calls"] += 1
                cycle_usage["prompt_tokens"] += usage.get("prompt_tokens", 0)
                cycle_usage["completion_tokens"] += usage.get("completion_tokens", 0)
                cycle_usage["total_tokens"] += usage.get("total_tokens", 0)
                cycle_usage["cost_usd"] += usage.get("cost_usd", 0)
                cycle_usage["response_time_ms"] += usage.get("response_time_ms", 0)
        
        self.last_signals = valid_signals
        
        # Aggregate signals
        aggregated = self.aggregator.aggregate(valid_signals)
        self.last_aggregated = aggregated
        
        # Update totals
        self.total_llm_calls += cycle_usage["llm_calls"]
        self.total_tokens += cycle_usage["total_tokens"]
        self.total_cost += cycle_usage["cost_usd"]
        
        print(f"[llm-agents] Cycle complete: {aggregated['direction']} (confidence: {aggregated['confidence']})")
        print(f"[llm-agents] Usage this cycle: {cycle_usage['llm_calls']} calls, {cycle_usage['total_tokens']} tokens")
        
        # Update KV
        await self._update_kv(valid_signals, aggregated, cycle_usage)
        
        # Write usage to QuestDB
        await self._write_usage_to_questdb(cycle_usage)
        
        self.cycle_count += 1
        return aggregated
    
    async def _update_kv(self, signals: List[Dict], aggregated: Dict, usage: Dict):
        """Update Cloudflare KV with latest signals and usage."""
        try:
            if not all([CF_ACCOUNT_ID, CF_API_TOKEN, KV_NAMESPACE_ID]):
                return
            
            now = int(datetime.now(timezone.utc).timestamp() * 1000)
            
            # Per-agent usage stats
            agent_usage = {}
            for signal in signals:
                dept = signal.get("department", "Unknown")
                is_llm = signal.get("llm", False)
                su = signal.get("usage", {})
                agent_usage[dept] = {
                    "llm": is_llm,
                    "tokens": su.get("total_tokens", 0) if su else 0,
                    "cost": su.get("cost_usd", 0) if su else 0,
                }
            
            kv_data = {
                "agent_signals": {
                    "departments": signals,
                    "departments_reporting": len(signals),
                    "aggregated": aggregated,
                    "llm_enabled": True,
                    "timestamp": now,
                    "exists": True,
                },
                "active_strategy_metrics": {
                    "strategy_name": f"LLM Multi-Agent ({self.symbol})",
                    "direction": aggregated.get("direction", "flat"),
                    "confidence": aggregated.get("confidence", 0),
                    "agents_active": len(signals),
                    "llm_agents": sum(1 for s in signals if s.get("llm", False)),
                    "timestamp": now,
                    "exists": True,
                },
                "llm_usage": {
                    "cycle": self.cycle_count,
                    "calls_this_cycle": usage["llm_calls"],
                    "tokens_this_cycle": usage["total_tokens"],
                    "cost_this_cycle": usage["cost_usd"],
                    "total_calls": self.total_llm_calls,
                    "total_tokens": self.total_tokens,
                    "total_cost_usd": self.total_cost,
                    "agent_breakdown": agent_usage,
                    "timestamp": now,
                    "exists": True,
                },
            }
            
            # Write each key
            for key, value in kv_data.items():
                await self._kv_put(key, value)
                
        except Exception as e:
            print(f"[llm-agents] KV update error: {e}")
    
    async def _kv_put(self, key: str, value: dict):
        """Write to Cloudflare KV."""
        url = (
            f"https://api.cloudflare.com/client/v4/accounts/"
            f"{CF_ACCOUNT_ID}/storage/kv/namespaces/"
            f"{KV_NAMESPACE_ID}/values/{key}"
        )
        
        async with aiohttp.ClientSession() as session:
            async with session.put(
                url,
                data=json.dumps(value),
                headers={
                    "Authorization": f"Bearer {CF_API_TOKEN}",
                    "Content-Type": "application/json",
                },
            ) as resp:
                if resp.status != 200 and resp.status != 429:
                    text = await resp.text()
                    print(f"[llm-agents] KV write failed for {key}: {resp.status}")
    
    async def _write_usage_to_questdb(self, usage: Dict):
        """Write LLM usage metrics to QuestDB for monitoring."""
        try:
            now = datetime.now(timezone.utc)
            timestamp_ns = int(now.timestamp() * 1_000_000_000)
            
            line = (
                f"llm_usage,cycle={self.cycle_count} "
                f"calls={usage['llm_calls']},"
                f"prompt_tokens={usage['prompt_tokens']},"
                f"completion_tokens={usage['completion_tokens']},"
                f"total_tokens={usage['total_tokens']},"
                f"cost={usage['cost_usd']:.6f},"
                f"response_time_ms={usage['response_time_ms']} "
                f"{timestamp_ns}"
            )
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{QUESTDB_URL}/write",
                    data=line,
                    headers={"Content-Type": "text/plain"},
                ) as resp:
                    if resp.status == 204:
                        print(f"[llm-agents] Usage logged to QuestDB")
                    
        except Exception as e:
            print(f"[llm-agents] QuestDB usage write error: {e}")
    
    async def run_loop(self, interval: int = 300):
        """Run LLM agent analysis loop."""
        self.running = True
        print(f"[llm-agents] LLM Orchestrator started (interval: {interval}s)")
        print(f"[llm-agents] Using model: openrouter/free (zero cost)")
        
        while self.running:
            try:
                await self.run_cycle()
            except Exception as e:
                print(f"[llm-agents] Cycle error: {e}")
            
            # Wait for next cycle
            for _ in range(interval):
                if not self.running:
                    break
                await asyncio.sleep(1)
        
        print("[llm-agents] Orchestrator stopped")
    
    def stop(self):
        """Stop the orchestrator."""
        self.running = False
    
    def get_status(self) -> Dict:
        """Get current orchestrator status with usage."""
        return {
            "running": self.running,
            "cycle_count": self.cycle_count,
            "llm_enabled": True,
            "model": "openrouter/free",
            "total_llm_calls": self.total_llm_calls,
            "total_tokens": self.total_tokens,
            "total_cost_usd": self.total_cost,
            "last_signals": self.last_signals,
            "last_aggregated": self.last_aggregated,
            "agents": list(self.agents.keys()),
        }


# Global instance
llm_orchestrator = LLMOrchestrator()
