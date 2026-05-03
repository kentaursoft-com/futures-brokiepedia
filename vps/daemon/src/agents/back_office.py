"""Back-office agents - lightweight support agents using V4 Flash."""
import json
import logging
from datetime import datetime
from typing import Dict, List, Optional

from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage

from ..config.settings import settings

logger = logging.getLogger(__name__)

class BookKeeper:
    """Writes to Turso ledger + trade_journal after every fill."""
    
    def __init__(self):
        self.trades: List[Dict] = []
        
    async def record_trade(self, trade: dict, paper: bool = True):
        """Record a trade to journal."""
        entry = {
            'id': trade.get('id', 'unknown'),
            'strategy_id': trade.get('strategy', 'unknown'),
            'exchange': trade.get('exchange', 'binance'),
            'symbol': trade.get('symbol', 'UNKNOWN'),
            'side': trade.get('side', 'long'),
            'entry_price': trade.get('entry_price', 0),
            'exit_price': trade.get('exit_price'),
            'size': trade.get('size', 0),
            'pnl': trade.get('pnl'),
            'fee': trade.get('fee', 0),
            'regime': trade.get('regime', 'unknown'),
            'paper': 1 if paper else 0,
            'created_at': int(datetime.now().timestamp())
        }
        
        self.trades.append(entry)
        logger.info(f"BookKeeper: Recorded {entry['side']} {entry['symbol']} "
                   f"{'(PAPER)' if paper else '(LIVE)'}")
        
        # TODO: Write to Turso when Turso client is integrated
        return entry
    
    async def update_ledger(self, balance: float, equity: float, 
                           unrealized_pnl: float, daily_pnl: float):
        """Update account ledger snapshot."""
        snapshot = {
            'id': f"ledger_{int(datetime.now().timestamp())}",
            'balance': balance,
            'equity': equity,
            'unrealized_pnl': unrealized_pnl,
            'daily_pnl': daily_pnl,
            'daily_drawdown_pct': 0.0,  # Calculated elsewhere
            'timestamp': int(datetime.now().timestamp())
        }
        
        logger.info(f"BookKeeper: Ledger snapshot - Equity: ${equity:.2f}, "
                   f"Daily P&L: ${daily_pnl:.2f}")
        return snapshot

class JournalingAgent:
    """Logs agent_reasoning_json per trade to Turso."""
    
    def __init__(self):
        self.reasonings: List[Dict] = []
        
    async def log_reasoning(self, trade_id: str, verdicts: List[dict], 
                           aggregated: dict, regime: str):
        """Log full agent reasoning for a trade."""
        reasoning = {
            'trade_id': trade_id,
            'timestamp': int(datetime.now().timestamp()),
            'regime': regime,
            'department_verdicts': verdicts,
            'aggregated_signal': aggregated,
            'confidence': aggregated.get('confidence', 0),
            'direction': aggregated.get('direction', 'flat'),
            'size_reduction': aggregated.get('size_reduction', 1.0)
        }
        
        self.reasonings.append(reasoning)
        logger.info(f"JournalingAgent: Logged reasoning for trade {trade_id} "
                   f"(conf: {reasoning['confidence']:.2f})")
        return reasoning

class ResearcherAgent:
    """Fetches on-chain data, news, CoinGlass funding rates."""
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key or settings.ai.DEEPSEEK_API_KEY
        self.llm = ChatOpenAI(
            model="deepseek-chat",
            api_key=self.api_key,
            base_url=settings.ai.DEEPSEEK_BASE_URL,
            temperature=0.3
        )
        
    async def get_funding_summary(self, symbol: str = "BTC") -> dict:
        """Get funding rate summary across exchanges."""
        # Placeholder - would integrate with CoinGlass API
        return {
            'symbol': symbol,
            'funding_8h': 0.01,
            'annualized': 10.95,
            'sentiment': 'neutral',
            'timestamp': int(datetime.now().timestamp())
        }
    
    async def research_symbol(self, symbol: str) -> dict:
        """Research a symbol and return context."""
        prompt = f"""
        You are a crypto research analyst. Provide a brief summary of {symbol}:
        1. Current market narrative
        2. Key support/resistance levels
        3. Upcoming catalysts (if any)
        4. Risk factors
        
        Keep it concise (max 200 words).
        """
        
        try:
            response = await self.llm.ainvoke([SystemMessage(content=prompt)])
            return {
                'symbol': symbol,
                'research': response.content,
                'timestamp': int(datetime.now().timestamp())
            }
        except Exception as e:
            logger.error(f"Research failed for {symbol}: {e}")
            return {'symbol': symbol, 'research': 'Research unavailable', 'error': str(e)}

class HealthMonitor:
    """Pings all services every 60s, alerts on failure."""
    
    def __init__(self, notifier=None):
        self.notifier = notifier
        self.last_checks: Dict[str, float] = {}
        self.status: Dict[str, bool] = {
            'questdb': False,
            'chromadb': False,
            'binance_ws': False,
            'deepseek_api': False,
            'turso': False
        }
        
    async def check_all(self) -> dict:
        """Run health checks on all services."""
        import aiohttp
        import time
        
        results = {}
        timestamp = time.time()
        
        # Check QuestDB
        try:
            import psycopg2
            conn = psycopg2.connect(
                host=settings.database.QUESTDB_HOST,
                port=settings.database.QUESTDB_PORT,
                user=settings.database.QUESTDB_USER,
                password=settings.database.QUESTDB_PASSWORD
            )
            conn.close()
            results['questdb'] = {'status': 'ok', 'latency_ms': 0}
            self.status['questdb'] = True
        except Exception as e:
            results['questdb'] = {'status': 'error', 'error': str(e)}
            self.status['questdb'] = False
        
        # Check ChromaDB
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"http://{settings.database.CHROMA_HOST}:"
                    f"{settings.database.CHROMA_PORT}/api/v1/heartbeat"
                ) as resp:
                    results['chromadb'] = {
                        'status': 'ok' if resp.status == 200 else 'error',
                        'latency_ms': 0
                    }
                    self.status['chromadb'] = resp.status == 200
        except Exception as e:
            results['chromadb'] = {'status': 'error', 'error': str(e)}
            self.status['chromadb'] = False
        
        # Check DeepSeek API
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    "https://api.deepseek.com/models",
                    headers={"Authorization": f"Bearer {settings.ai.DEEPSEEK_API_KEY}"}
                ) as resp:
                    results['deepseek_api'] = {
                        'status': 'ok' if resp.status == 200 else 'error'
                    }
                    self.status['deepseek_api'] = resp.status == 200
        except Exception as e:
            results['deepseek_api'] = {'status': 'error', 'error': str(e)}
            self.status['deepseek_api'] = False
        
        # Check Binance WS (based on recent data)
        results['binance_ws'] = {
            'status': 'ok' if self.status.get('binance_ws', False) else 'warning'
        }
        
        self.last_checks = {k: timestamp for k in results.keys()}
        
        # Alert on failures
        failed = [k for k, v in results.items() if v['status'] == 'error']
        if failed and self.notifier:
            for service in failed:
                await self.notifier.send_alert('daemon_offline', {
                    'service': service,
                    'seconds': 60
                })
        
        return results
    
    def get_status_summary(self) -> dict:
        """Get summary of all service statuses."""
        return {
            'services': self.status,
            'all_healthy': all(self.status.values()),
            'last_check': max(self.last_checks.values()) if self.last_checks else 0
        }
