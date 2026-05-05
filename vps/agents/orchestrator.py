"""Agent Orchestrator - Runs all agents periodically and manages state."""

import asyncio
import json
import os
from datetime import datetime, timezone
from typing import Dict, List, Any
import aiohttp

from .trend_agent import TrendAgent
from .momentum_agent import MomentumAgent
from .volatility_agent import VolatilityAgent
from .sentiment_agent import SentimentAgent
from .funding_agent import FundingAgent
from .risk_agent import RiskAgent
from .signal_aggregator import SignalAggregator

CF_ACCOUNT_ID = os.environ.get("CF_ACCOUNT_ID")
CF_API_TOKEN = os.environ.get("CF_API_TOKEN")
KV_NAMESPACE_ID = os.environ.get("KV_LIVE_STATE_ID")


class AgentOrchestrator:
    """Manages all trading agents and their lifecycle."""
    
    def __init__(self, symbol: str = "BTCUSDT"):
        self.symbol = symbol
        self.running = False
        self.agents = {
            "Trend": TrendAgent(symbol),
            "Momentum": MomentumAgent(symbol),
            "Volatility": VolatilityAgent(symbol),
            "Sentiment": SentimentAgent(symbol),
            "Funding": FundingAgent(symbol),
            "Risk": RiskAgent(symbol),
        }
        self.aggregator = SignalAggregator()
        self.last_signals = []
        self.last_aggregated = None
        self.cycle_count = 0
        
    async def run_cycle(self) -> Dict[str, Any]:
        """Run one full analysis cycle."""
        print(f"[agents] Starting analysis cycle #{self.cycle_count + 1}")
        
        # Run all agents concurrently
        tasks = [agent.run() for agent in self.agents.values()]
        signals = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Filter out errors
        valid_signals = []
        for i, signal in enumerate(signals):
            if isinstance(signal, Exception):
                agent_name = list(self.agents.keys())[i]
                print(f"[agents] {agent_name} failed: {signal}")
            else:
                valid_signals.append(signal)
        
        self.last_signals = valid_signals
        
        # Aggregate signals
        aggregated = self.aggregator.aggregate(valid_signals)
        self.last_aggregated = aggregated
        
        print(f"[agents] Cycle complete: {aggregated['direction']} (confidence: {aggregated['confidence']})")
        
        # Update KV
        await self._update_kv(valid_signals, aggregated)
        
        self.cycle_count += 1
        return aggregated
    
    async def _update_kv(self, signals: List[Dict], aggregated: Dict):
        """Update Cloudflare KV with latest signals."""
        try:
            if not all([CF_ACCOUNT_ID, CF_API_TOKEN, KV_NAMESPACE_ID]):
                return
            
            now = int(datetime.now(timezone.utc).timestamp() * 1000)
            
            kv_data = {
                "agent_signals": {
                    "departments": signals,
                    "departments_reporting": len(signals),
                    "aggregated": aggregated,
                    "timestamp": now,
                    "exists": True,
                },
                "active_strategy_metrics": {
                    "strategy_name": f"Multi-Agent Consensus ({self.symbol})",
                    "direction": aggregated.get("direction", "flat"),
                    "confidence": aggregated.get("confidence", 0),
                    "agents_active": len(signals),
                    "timestamp": now,
                    "exists": True,
                },
            }
            
            # Write each key
            for key, value in kv_data.items():
                await self._kv_put(key, value)
                
        except Exception as e:
            print(f"[agents] KV update error: {e}")
    
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
                if resp.status != 200:
                    text = await resp.text()
                    # Only print on non-429 to avoid spam
                    if resp.status != 429:
                        print(f"[agents] KV write failed for {key}: {resp.status}")
    
    async def run_loop(self, interval: int = 300):
        """Run agent analysis loop."""
        self.running = True
        print(f"[agents] Orchestrator started (interval: {interval}s)")
        
        while self.running:
            try:
                await self.run_cycle()
            except Exception as e:
                print(f"[agents] Cycle error: {e}")
            
            # Wait for next cycle
            for _ in range(interval):
                if not self.running:
                    break
                await asyncio.sleep(1)
        
        print("[agents] Orchestrator stopped")
    
    def stop(self):
        """Stop the orchestrator."""
        self.running = False
    
    def get_status(self) -> Dict:
        """Get current orchestrator status."""
        return {
            "running": self.running,
            "cycle_count": self.cycle_count,
            "last_signals": self.last_signals,
            "last_aggregated": self.last_aggregated,
            "agents": list(self.agents.keys()),
        }


# Global instance
agent_orchestrator = AgentOrchestrator()
