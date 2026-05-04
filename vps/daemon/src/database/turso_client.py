"""Turso database client for persistent storage."""
import logging
import json
from datetime import datetime
from typing import Dict, List, Optional, Any
import libsql_client

from ..config.settings import settings

logger = logging.getLogger(__name__)

class TursoClient:
    """Client for Turso (libSQL) database."""
    
    def __init__(self):
        self.url = settings.database.TURSO_URL
        self.token = settings.database.TURSO_TOKEN
        self.client = None
        
    def connect(self):
        """Establish database connection."""
        try:
            if self.url and self.token:
                self.client = libsql_client.create_client(
                    url=self.url,
                    auth_token=self.token
                )
                logger.info("✅ Turso connected")
            else:
                logger.warning("Turso credentials not configured, using local mode")
        except Exception as e:
            logger.error(f"Failed to connect to Turso: {e}")
            raise
    
    def close(self):
        """Close database connection."""
        if self.client:
            self.client.close()
            logger.info("Turso connection closed")
    
    # === Trade Journal ===
    
    async def record_trade(self, trade: dict) -> bool:
        """Record a trade to the journal."""
        if not self.client:
            return False
        
        try:
            self.client.execute("""
                INSERT INTO trade_journal (
                    id, strategy_id, exchange, symbol, side,
                    entry_price, exit_price, size, pnl, fee,
                    regime, agent_reasoning_json, paper, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, [
                trade['id'],
                trade.get('strategy_id', 'unknown'),
                trade.get('exchange', 'binance'),
                trade['symbol'],
                trade['side'],
                trade['entry_price'],
                trade.get('exit_price'),
                trade['size'],
                trade.get('pnl'),
                trade.get('fee', 0),
                trade.get('regime', 'unknown'),
                json.dumps(trade.get('reasoning', {})),
                1 if trade.get('paper', True) else 0,
                int(datetime.now().timestamp())
            ])
            return True
        except Exception as e:
            logger.error(f"Failed to record trade: {e}")
            return False
    
    async def get_trades(self, limit: int = 100, paper_only: bool = True) -> List[dict]:
        """Get recent trades."""
        if not self.client:
            return []
        
        try:
            result = self.client.execute("""
                SELECT * FROM trade_journal 
                WHERE paper = ?
                ORDER BY created_at DESC
                LIMIT ?
            """, [1 if paper_only else 0, limit])
            
            return [dict(row) for row in result.rows]
        except Exception as e:
            logger.error(f"Failed to get trades: {e}")
            return []
    
    # === Ledger ===
    
    async def update_ledger(self, snapshot: dict) -> bool:
        """Update account ledger snapshot."""
        if not self.client:
            return False
        
        try:
            self.client.execute("""
                INSERT INTO ledger (
                    id, balance, equity, unrealized_pnl,
                    daily_pnl, daily_drawdown_pct, timestamp
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """, [
                snapshot['id'],
                snapshot['balance'],
                snapshot['equity'],
                snapshot['unrealized_pnl'],
                snapshot['daily_pnl'],
                snapshot['daily_drawdown_pct'],
                snapshot['timestamp']
            ])
            return True
        except Exception as e:
            logger.error(f"Failed to update ledger: {e}")
            return False
    
    async def get_ledger_history(self, limit: int = 100) -> List[dict]:
        """Get ledger history."""
        if not self.client:
            return []
        
        try:
            result = self.client.execute("""
                SELECT * FROM ledger
                ORDER BY timestamp DESC
                LIMIT ?
            """, [limit])
            
            return [dict(row) for row in result.rows]
        except Exception as e:
            logger.error(f"Failed to get ledger: {e}")
            return []
    
    # === Strategies ===
    
    async def create_strategy(self, strategy: dict) -> bool:
        """Create a new strategy."""
        if not self.client:
            return False
        
        try:
            self.client.execute("""
                INSERT INTO strategies (
                    id, version, parent_id, name, definition_json,
                    status, win_rate, sharpe, expectancy,
                    prompt_version_id, rejection_reason, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, [
                strategy['id'],
                strategy.get('version', 1),
                strategy.get('parent_id'),
                strategy['name'],
                json.dumps(strategy.get('definition', {})),
                strategy.get('status', 'draft'),
                strategy.get('win_rate', 0),
                strategy.get('sharpe', 0),
                strategy.get('expectancy', 0),
                strategy.get('prompt_version_id'),
                strategy.get('rejection_reason'),
                int(datetime.now().timestamp())
            ])
            return True
        except Exception as e:
            logger.error(f"Failed to create strategy: {e}")
            return False
    
    async def update_strategy_status(self, strategy_id: str, status: str) -> bool:
        """Update strategy status."""
        if not self.client:
            return False
        
        try:
            self.client.execute("""
                UPDATE strategies 
                SET status = ?, promoted_at = ?
                WHERE id = ?
            """, [status, int(datetime.now().timestamp()), strategy_id])
            return True
        except Exception as e:
            logger.error(f"Failed to update strategy: {e}")
            return False
    
    async def get_strategies(self, status: Optional[str] = None) -> List[dict]:
        """Get strategies, optionally filtered by status."""
        if not self.client:
            return []
        
        try:
            if status:
                result = self.client.execute("""
                    SELECT * FROM strategies WHERE status = ?
                    ORDER BY created_at DESC
                """, [status])
            else:
                result = self.client.execute("""
                    SELECT * FROM strategies
                    ORDER BY created_at DESC
                """)
            
            return [dict(row) for row in result.rows]
        except Exception as e:
            logger.error(f"Failed to get strategies: {e}")
            return []
    
    # === Backtest Results ===
    
    async def record_backtest(self, result: dict) -> bool:
        """Record backtest result."""
        if not self.client:
            return False
        
        try:
            self.client.execute("""
                INSERT INTO backtest_results (
                    id, strategy_id, win_rate, sharpe, max_drawdown,
                    expectancy, total_trades, fee_adjusted, regime,
                    passed_gate, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, [
                result['id'],
                result['strategy_id'],
                result['win_rate'],
                result['sharpe'],
                result['max_drawdown'],
                result['expectancy'],
                result['total_trades'],
                1 if result.get('fee_adjusted', False) else 0,
                result.get('regime', 'unknown'),
                1 if result.get('passed_gate', False) else 0,
                int(datetime.now().timestamp())
            ])
            return True
        except Exception as e:
            logger.error(f"Failed to record backtest: {e}")
            return False
    
    # === Performance Analytics ===
    
    async def get_performance_stats(self, days: int = 30) -> dict:
        """Get performance statistics."""
        if not self.client:
            return {}
        
        try:
            # Get trades from last N days
            since = int(datetime.now().timestamp()) - (days * 86400)
            
            result = self.client.execute("""
                SELECT 
                    COUNT(*) as total_trades,
                    SUM(CASE WHEN pnl > 0 THEN 1 ELSE 0 END) as winning_trades,
                    SUM(CASE WHEN pnl < 0 THEN 1 ELSE 0 END) as losing_trades,
                    SUM(pnl) as total_pnl,
                    AVG(pnl) as avg_pnl,
                    MAX(pnl) as max_pnl,
                    MIN(pnl) as min_pnl,
                    SUM(fee) as total_fees
                FROM trade_journal
                WHERE created_at > ? AND paper = 1
            """, [since])
            
            row = result.rows[0] if result.rows else {}
            
            total = row.get('total_trades', 0) or 0
            wins = row.get('winning_trades', 0) or 0
            
            return {
                'total_trades': total,
                'winning_trades': wins,
                'losing_trades': row.get('losing_trades', 0) or 0,
                'win_rate': (wins / total * 100) if total > 0 else 0,
                'total_pnl': row.get('total_pnl', 0) or 0,
                'avg_pnl': row.get('avg_pnl', 0) or 0,
                'max_pnl': row.get('max_pnl', 0) or 0,
                'min_pnl': row.get('min_pnl', 0) or 0,
                'total_fees': row.get('total_fees', 0) or 0,
                'period_days': days
            }
        except Exception as e:
            logger.error(f"Failed to get performance stats: {e}")
            return {}
    
    async def get_equity_curve(self, days: int = 30) -> List[dict]:
        """Get equity curve data."""
        if not self.client:
            return []
        
        try:
            since = int(datetime.now().timestamp()) - (days * 86400)
            
            result = self.client.execute("""
                SELECT timestamp, equity, daily_pnl
                FROM ledger
                WHERE timestamp > ?
                ORDER BY timestamp ASC
            """, [since])
            
            return [dict(row) for row in result.rows]
        except Exception as e:
            logger.error(f"Failed to get equity curve: {e}")
            return []
    
    # === Audit Log ===
    
    async def log_audit(self, event_type: str, payload: dict) -> bool:
        """Log an audit event."""
        if not self.client:
            return False
        
        try:
            self.client.execute("""
                INSERT INTO audit_log (id, event_type, payload_json, created_at)
                VALUES (?, ?, ?, ?)
            """, [
                f"audit_{int(datetime.now().timestamp())}_{event_type}",
                event_type,
                json.dumps(payload),
                int(datetime.now().timestamp())
            ])
            return True
        except Exception as e:
            logger.error(f"Failed to log audit: {e}")
            return False
