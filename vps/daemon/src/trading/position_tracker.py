"""Real-time position tracking and P&L calculation."""
import logging
from datetime import datetime
from typing import Dict, List, Optional
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)

@dataclass
class Position:
    """Represents an open position."""
    id: str
    symbol: str
    side: str  # 'long' or 'short'
    size: float
    entry_price: float
    mark_price: float = 0.0
    unrealized_pnl: float = 0.0
    realized_pnl: float = 0.0
    exchange: str = 'binance'
    strategy: str = 'unknown'
    leverage: float = 1.0
    created_at: int = 0
    
    def update_mark_price(self, mark_price: float):
        """Update mark price and recalculate unrealized P&L."""
        self.mark_price = mark_price
        
        if self.side == 'long':
            self.unrealized_pnl = (mark_price - self.entry_price) * self.size * self.leverage
        else:  # short
            self.unrealized_pnl = (self.entry_price - mark_price) * self.size * self.leverage
    
    def close(self, exit_price: float) -> dict:
        """Close position and return trade summary."""
        if self.side == 'long':
            pnl = (exit_price - self.entry_price) * self.size * self.leverage
        else:
            pnl = (self.entry_price - exit_price) * self.size * self.leverage
        
        self.realized_pnl = pnl
        
        return {
            'id': self.id,
            'symbol': self.symbol,
            'side': self.side,
            'size': self.size,
            'entry_price': self.entry_price,
            'exit_price': exit_price,
            'pnl': pnl,
            'exchange': self.exchange,
            'strategy': self.strategy,
            'duration_seconds': int(datetime.now().timestamp()) - self.created_at
        }
    
    def to_dict(self) -> dict:
        """Convert to dictionary for serialization."""
        return {
            'id': self.id,
            'symbol': self.symbol,
            'side': self.side,
            'size': self.size,
            'entry_price': self.entry_price,
            'mark_price': self.mark_price,
            'unrealized_pnl': round(self.unrealized_pnl, 2),
            'realized_pnl': round(self.realized_pnl, 2),
            'exchange': self.exchange,
            'strategy': self.strategy,
            'leverage': self.leverage,
            'created_at': self.created_at
        }

class PositionTracker:
    """Track all open positions and calculate portfolio P&L."""
    
    def __init__(self, exchange_layer=None):
        self.positions: Dict[str, Position] = {}
        self.exchange_layer = exchange_layer
        self.equity = 10000.0
        self.initial_equity = 10000.0
        self.total_realized_pnl = 0.0
        self.peak_equity = 10000.0
        self.max_drawdown_pct = 0.0
        self.daily_pnl = 0.0
        self.daily_starting_equity = 10000.0
        self.trade_history: List[dict] = []
        
    def open_position(self, order: dict, strategy: str = 'unknown') -> Optional[Position]:
        """Open a new position from an order."""
        position_id = f"pos_{order['id']}"
        
        if position_id in self.positions:
            logger.warning(f"Position {position_id} already exists")
            return None
        
        position = Position(
            id=position_id,
            symbol=order['symbol'],
            side=order['side'],
            size=order['amount'],
            entry_price=order['price'] or order['average'],
            exchange=order.get('exchange', 'binance'),
            strategy=strategy,
            created_at=int(datetime.now().timestamp())
        )
        
        self.positions[position_id] = position
        logger.info(f"Opened {position.side} position: {position.size} {position.symbol} @ {position.entry_price}")
        
        return position
    
    def close_position(self, position_id: str, exit_price: float) -> Optional[dict]:
        """Close a position and record the trade."""
        position = self.positions.get(position_id)
        if not position:
            logger.warning(f"Position {position_id} not found")
            return None
        
        trade = position.close(exit_price)
        self.trade_history.append(trade)
        
        # Update equity
        self.total_realized_pnl += trade['pnl']
        self.equity += trade['pnl']
        self.daily_pnl += trade['pnl']
        
        # Update peak equity and drawdown
        if self.equity > self.peak_equity:
            self.peak_equity = self.equity
        
        drawdown = (self.peak_equity - self.equity) / self.peak_equity * 100
        if drawdown > self.max_drawdown_pct:
            self.max_drawdown_pct = drawdown
        
        del self.positions[position_id]
        
        logger.info(f"Closed position {position_id}: P&L ${trade['pnl']:.2f}")
        
        return trade
    
    async def update_prices(self):
        """Update all position mark prices from exchange."""
        if not self.exchange_layer:
            return
        
        for position in self.positions.values():
            try:
                ticker = await self.exchange_layer.get_ticker(
                    position.symbol, 
                    position.exchange
                )
                position.update_mark_price(ticker['last'])
            except Exception as e:
                logger.error(f"Failed to update price for {position.symbol}: {e}")
    
    def get_unrealized_pnl(self) -> float:
        """Get total unrealized P&L."""
        return sum(p.unrealized_pnl for p in self.positions.values())
    
    def get_total_pnl(self) -> float:
        """Get total P&L (realized + unrealized)."""
        return self.total_realized_pnl + self.get_unrealized_pnl()
    
    def get_current_drawdown(self) -> float:
        """Get current drawdown percentage."""
        if self.peak_equity <= 0:
            return 0.0
        return (self.peak_equity - self.equity) / self.peak_equity * 100
    
    def get_daily_return_pct(self) -> float:
        """Get daily return percentage."""
        if self.daily_starting_equity <= 0:
            return 0.0
        return (self.daily_pnl / self.daily_starting_equity) * 100
    
    def reset_daily_stats(self):
        """Reset daily statistics (call at midnight)."""
        self.daily_starting_equity = self.equity
        self.daily_pnl = 0.0
        logger.info(f"Daily stats reset. Starting equity: ${self.equity:.2f}")
    
    def get_portfolio_summary(self) -> dict:
        """Get complete portfolio summary."""
        unrealized = self.get_unrealized_pnl()
        total_pnl = self.get_total_pnl()
        
        return {
            'equity': round(self.equity, 2),
            'initial_equity': round(self.initial_equity, 2),
            'total_realized_pnl': round(self.total_realized_pnl, 2),
            'total_unrealized_pnl': round(unrealized, 2),
            'total_pnl': round(total_pnl, 2),
            'total_return_pct': round((total_pnl / self.initial_equity) * 100, 2),
            'current_drawdown_pct': round(self.get_current_drawdown(), 2),
            'max_drawdown_pct': round(self.max_drawdown_pct, 2),
            'daily_pnl': round(self.daily_pnl, 2),
            'daily_return_pct': round(self.get_daily_return_pct(), 2),
            'open_positions_count': len(self.positions),
            'total_trades': len(self.trade_history),
            'open_positions': [p.to_dict() for p in self.positions.values()]
        }
    
    def get_position(self, position_id: str) -> Optional[Position]:
        """Get a specific position."""
        return self.positions.get(position_id)
    
    def get_all_positions(self) -> List[dict]:
        """Get all open positions as dictionaries."""
        return [p.to_dict() for p in self.positions.values()]
    
    def get_trade_history(self, limit: int = 100) -> List[dict]:
        """Get recent trade history."""
        return self.trade_history[-limit:]
