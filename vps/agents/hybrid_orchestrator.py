"""Hybrid Orchestrator - DeepSeek for consensus, OpenRouter for agents."""

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
from .deepseek_client import DeepSeekClient
from .llm_client import LLMClient

CF_ACCOUNT_ID = os.environ.get("CF_ACCOUNT_ID")
CF_API_TOKEN = os.environ.get("CF_API_TOKEN")
KV_NAMESPACE_ID = os.environ.get("KV_LIVE_STATE_ID")
QUESTDB_URL = "http://localhost:9001"


class HybridOrchestrator:
    """
    Hybrid architecture:
    - Individual agents use OpenRouter free models (fast, zero cost)
    - Orchestrator uses DeepSeek V4 Flash for high-level consensus (better reasoning)
    """

    def __init__(self, symbol: str = "BTCUSDT"):
        self.symbol = symbol
        self.running = False

        # Individual agents use OpenRouter (free models)
        self.agents = {
            "Trend": LLMTrendAgent(symbol),
            "Momentum": LLMMomentumAgent(symbol),
            "Volatility": LLMVolatilityAgent(symbol),
            "Sentiment": LLMSentimentAgent(symbol),
            "Funding": LLMFundingAgent(symbol),
            "Risk": LLMRiskAgent(symbol),
        }

        # Orchestrator uses DeepSeek for final consensus
        self.deepseek = DeepSeekClient("deepseek-chat")

        self.last_signals = []
        self.last_aggregated = None
        self.cycle_count = 0

        # Usage tracking
        self.orchestrator_usage = {
            "deepseek_calls": 0,
            "deepseek_tokens": 0,
            "deepseek_cost": 0.0,
        }
        self.agent_usage = {
            "openrouter_calls": 0,
            "openrouter_tokens": 0,
            "openrouter_cost": 0.0,
        }

    async def run_cycle(self) -> Dict[str, Any]:
        """Run one full hybrid analysis cycle."""
        print(f"[hybrid] Starting cycle #{self.cycle_count + 1}")
        print(f"[hybrid] Agents: OpenRouter (free) | Orchestrator: DeepSeek V4 Flash")

        # Step 1: Run all individual agents (OpenRouter, concurrent)
        tasks = [agent.run() for agent in self.agents.values()]
        signals = await asyncio.gather(*tasks, return_exceptions=True)

        # Process agent signals
        valid_signals = []
        agent_usage_this_cycle = {
            "calls": 0,
            "tokens": 0,
            "cost": 0.0,
        }

        for i, signal in enumerate(signals):
            agent_name = list(self.agents.keys())[i]

            if isinstance(signal, Exception):
                print(f"[hybrid] {agent_name} failed: {signal}")
                continue

            valid_signals.append(signal)

            # Track OpenRouter usage from agents
            usage = signal.get("usage", {})
            if usage:
                agent_usage_this_cycle["calls"] += 1
                agent_usage_this_cycle["tokens"] += usage.get("total_tokens", 0)
                agent_usage_this_cycle["cost"] += usage.get("cost_usd", 0)

        self.last_signals = valid_signals

        # Update agent usage totals
        self.agent_usage["openrouter_calls"] += agent_usage_this_cycle["calls"]
        self.agent_usage["openrouter_tokens"] += agent_usage_this_cycle["tokens"]
        self.agent_usage["openrouter_cost"] += agent_usage_this_cycle["cost"]

        print(f"[hybrid] Agents complete: {len(valid_signals)}/6 signals")

        # Step 2: DeepSeek consensus (orchestrator-level decision)
        aggregated = await self._deepseek_consensus(valid_signals)
        self.last_aggregated = aggregated

        # Track DeepSeek usage
        ds_usage = aggregated.get("orchestrator_usage", {})
        if ds_usage:
            self.orchestrator_usage["deepseek_calls"] += 1
            self.orchestrator_usage["deepseek_tokens"] += ds_usage.get("total_tokens", 0)
            self.orchestrator_usage["deepseek_cost"] += ds_usage.get("cost_usd", 0)

        print(f"[hybrid] Consensus: {aggregated['direction']} (confidence: {aggregated['confidence']})")
        print(f"[hybrid] DeepSeek cost this cycle: ${ds_usage.get('cost_usd', 0):.6f}")

        # Step 3: Update KV and QuestDB
        await self._update_kv(valid_signals, aggregated, agent_usage_this_cycle, ds_usage)
        await self._write_usage_to_questdb(agent_usage_this_cycle, ds_usage)

        self.cycle_count += 1
        return aggregated

    async def _deepseek_consensus(self, signals: List[Dict]) -> Dict:
        """Use DeepSeek V4 Flash for high-level consensus."""

        if not signals:
            return {
                "direction": "flat",
                "confidence": 0.0,
                "reason": "No signals to aggregate",
                "agents_reporting": 0,
            }

        # Check if DeepSeek is available
        if not self.deepseek.api_key or self.deepseek.api_key == "your_key_here":
            # Fallback: classical aggregation
            return self._classical_aggregate(signals)

        # Format signals for DeepSeek
        signals_text = []
        for s in signals:
            dept = s.get("department", "Unknown")
            direction = s.get("direction", "flat")
            confidence = s.get("confidence", 0)
            reason = s.get("reason", "")
            metrics = s.get("metrics", {})
            signals_text.append(
                f"- {dept}: {direction} (confidence: {confidence})\n  Reason: {reason}\n  Metrics: {metrics}"
            )

        system_prompt = """You are an elite crypto trading strategist. Analyze signals from multiple departments and make a final trading decision.

Return ONLY a JSON object:
{
  "direction": "long" | "short" | "flat",
  "confidence": 0.0-1.0,
  "reason": "2-3 sentence explanation of your reasoning",
  "metrics": {
    "consensus_strength": 0-10,
    "risk_assessment": "low|medium|high"
  }
}

Rules:
- Consider all department signals and their confidence levels
- Risk agent has veto power (if risk says flat with high confidence, respect it)
- Weight Trend and Momentum more heavily than Sentiment and Funding
- Only output HIGH confidence (>0.8) when multiple strong signals align
- Explain your reasoning clearly"""

        user_prompt = f"""Analyze these trading signals for {self.symbol}:

{chr(10).join(signals_text)}

Make a final trading decision. Consider:
1. Which signals agree vs disagree?
2. What's the overall trend direction?
3. Is risk acceptable?
4. What's the confidence level?

Return JSON with direction, confidence, and detailed reasoning."""

        result = await self.deepseek.analyze(system_prompt, user_prompt)

        if "error" in result:
            print(f"[hybrid] DeepSeek error: {result.get('error')}, falling back to classical")
            return self._classical_aggregate(signals)

        return {
            "direction": result.get("direction", "flat"),
            "confidence": result.get("confidence", 0.0),
            "reason": result.get("reason", "DeepSeek consensus"),
            "agents_reporting": len(signals),
            "signal_breakdown": signals,
            "orchestrator_usage": result.get("usage", {}),
            "deepseek_reasoning": True,
        }

    def _classical_aggregate(self, signals: List[Dict]) -> Dict:
        """Classical weighted aggregation fallback."""
        weights = {
            "Trend": 0.25, "Momentum": 0.20, "Volatility": 0.15,
            "Sentiment": 0.15, "Funding": 0.10, "Risk": 0.15,
        }

        direction_scores = {"long": 0.0, "short": 0.0, "flat": 0.0}
        total_weight = 0.0

        for signal in signals:
            dept = signal.get("department", "Unknown")
            direction = signal.get("direction", "flat")
            confidence = signal.get("confidence", 0)
            weight = weights.get(dept, 0.1)

            if dept == "Risk" and direction == "flat" and confidence > 0.7:
                return {
                    "direction": "flat",
                    "confidence": 0.95,
                    "reason": "RISK VETO",
                    "agents_reporting": len(signals),
                    "signal_breakdown": signals,
                    "orchestrator_usage": {},
                }

            if confidence < 0.3:
                continue

            if direction == "long":
                direction_scores["long"] += confidence * weight
            elif direction == "short":
                direction_scores["short"] += confidence * weight
            else:
                direction_scores["flat"] += confidence * weight

            total_weight += weight

        if direction_scores["long"] > direction_scores["short"] * 1.5:
            return {"direction": "long", "confidence": min(0.95, direction_scores["long"]), "reason": "Classical consensus (long)", "agents_reporting": len(signals), "signal_breakdown": signals, "orchestrator_usage": {}}
        elif direction_scores["short"] > direction_scores["long"] * 1.5:
            return {"direction": "short", "confidence": min(0.95, direction_scores["short"]), "reason": "Classical consensus (short)", "agents_reporting": len(signals), "signal_breakdown": signals, "orchestrator_usage": {}}
        else:
            return {"direction": "flat", "confidence": 0.5, "reason": "No clear consensus", "agents_reporting": len(signals), "signal_breakdown": signals, "orchestrator_usage": {}}

    async def _update_kv(self, signals: List[Dict], aggregated: Dict, agent_usage: Dict, orchestrator_usage: Dict):
        """Update Cloudflare KV."""
        try:
            if not all([CF_ACCOUNT_ID, CF_API_TOKEN, KV_NAMESPACE_ID]):
                return

            now = int(datetime.now(timezone.utc).timestamp() * 1000)

            kv_data = {
                "agent_signals": {
                    "departments": signals,
                    "departments_reporting": len(signals),
                    "aggregated": aggregated,
                    "llm_enabled": True,
                    "hybrid_mode": True,
                    "timestamp": now,
                    "exists": True,
                },
                "active_strategy_metrics": {
                    "strategy_name": f"Hybrid: OpenRouter Agents + DeepSeek Consensus ({self.symbol})",
                    "direction": aggregated.get("direction", "flat"),
                    "confidence": aggregated.get("confidence", 0),
                    "agents_active": len(signals),
                    "timestamp": now,
                    "exists": True,
                },
                "llm_usage": {
                    "cycle": self.cycle_count,
                    "hybrid_mode": True,
                    # Agent usage (OpenRouter free)
                    "agent_calls_this_cycle": agent_usage["calls"],
                    "agent_tokens_this_cycle": agent_usage["tokens"],
                    "agent_cost_this_cycle": agent_usage["cost"],
                    # Orchestrator usage (DeepSeek)
                    "orchestrator_calls_this_cycle": 1 if orchestrator_usage else 0,
                    "orchestrator_tokens_this_cycle": orchestrator_usage.get("total_tokens", 0),
                    "orchestrator_cost_this_cycle": orchestrator_usage.get("cost_usd", 0),
                    # Totals
                    "total_agent_calls": self.agent_usage["openrouter_calls"],
                    "total_agent_tokens": self.agent_usage["openrouter_tokens"],
                    "total_agent_cost": self.agent_usage["openrouter_cost"],
                    "total_orchestrator_calls": self.orchestrator_usage["deepseek_calls"],
                    "total_orchestrator_tokens": self.orchestrator_usage["deepseek_tokens"],
                    "total_orchestrator_cost": self.orchestrator_usage["deepseek_cost"],
                    "total_cost_usd": self.agent_usage["openrouter_cost"] + self.orchestrator_usage["deepseek_cost"],
                    "timestamp": now,
                    "exists": True,
                },
            }

            for key, value in kv_data.items():
                await self._kv_put(key, value)

        except Exception as e:
            print(f"[hybrid] KV update error: {e}")

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
                    print(f"[hybrid] KV write failed for {key}: {resp.status}")

    async def _write_usage_to_questdb(self, agent_usage: Dict, orchestrator_usage: Dict):
        """Write usage metrics to QuestDB."""
        try:
            now = datetime.now(timezone.utc)
            timestamp_ns = int(now.timestamp() * 1_000_000_000)

            # Agent usage line (OpenRouter)
            agent_line = (
                f"llm_usage,source=agent,type=openrouter "
                f"calls={agent_usage['calls']},"
                f"tokens={agent_usage['tokens']},"
                f"cost={agent_usage['cost']:.6f} "
                f"{timestamp_ns}"
            )

            # Orchestrator usage line (DeepSeek)
            orch_line = (
                f"llm_usage,source=orchestrator,type=deepseek "
                f"calls={1 if orchestrator_usage else 0},"
                f"tokens={orchestrator_usage.get('total_tokens', 0)},"
                f"cost={orchestrator_usage.get('cost_usd', 0):.6f} "
                f"{timestamp_ns + 1}"
            )

            async with aiohttp.ClientSession() as session:
                for line in [agent_line, orch_line]:
                    async with session.post(
                        f"{QUESTDB_URL}/write",
                        data=line,
                        headers={"Content-Type": "text/plain"},
                    ) as resp:
                        if resp.status == 204:
                            pass  # Success

        except Exception as e:
            print(f"[hybrid] QuestDB usage write error: {e}")

    async def run_loop(self, interval: int = 300):
        """Run hybrid analysis loop."""
        self.running = True
        print(f"[hybrid] Hybrid Orchestrator started (interval: {interval}s)")
        print(f"[hybrid] Architecture: OpenRouter (agents) + DeepSeek (consensus)")

        while self.running:
            try:
                await self.run_cycle()
            except Exception as e:
                print(f"[hybrid] Cycle error: {e}")

            for _ in range(interval):
                if not self.running:
                    break
                await asyncio.sleep(1)

        print("[hybrid] Orchestrator stopped")

    def stop(self):
        """Stop the orchestrator."""
        self.running = False

    def get_status(self) -> Dict:
        """Get current status with full usage breakdown."""
        return {
            "running": self.running,
            "cycle_count": self.cycle_count,
            "architecture": "hybrid",
            "agents": {
                "type": "openrouter",
                "model": "openrouter/free",
                "cost": "$0.00",
            },
            "orchestrator": {
                "type": "deepseek",
                "model": "deepseek-chat (V4 Flash)",
            },
            "usage": {
                "agents": self.agent_usage,
                "orchestrator": self.orchestrator_usage,
                "total_cost_usd": self.agent_usage["openrouter_cost"] + self.orchestrator_usage["deepseek_cost"],
            },
            "last_signals": self.last_signals,
            "last_aggregated": self.last_aggregated,
        }


# Global instance
hybrid_orchestrator = HybridOrchestrator()
