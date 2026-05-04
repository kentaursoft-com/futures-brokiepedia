"""Live execution engine with full position and risk management."""
import logging
from datetime import datetime
from typing import Dict, Optional

from ..config.settings import settings
from ..database.turso_client import TursoClient
from .position_tracker import PositionTracker
from ..analytics.performance import PerformanceAnalytics

logger = logging.getLogger(__name__)

class LiveExecutionEngine:
    """Production-ready execution engine."""
    
    def __init__(self, exchange_layer, turso: TursoClient = None):
        self.exchanges = exchange_layer
        self.turso = turso
        self.positions = PositionTracker(exchange_layer)
        self.analytics = PerformanceAnalytics()
        self.execution_enabled = True
        self.paper_mode = settings.is_paper_trading()
        
        # Risk parameters
        self.risk = settings.risk
        
        # Daily tracking
        self.daily_trades = 0
        self.daily_losses = 0
        
    async def execute_signal(self, signal: dict, strategy: dict) -> Optional[dict]:
        """Execute a trading signal with full validation."""
        if not self.execution_enabled:
            logger.warning("Execution disabled - signal ignored")
            return None
        
        # Validate signal
        if not await self._validate_signal(signal):
            return None
        
        # Check risk limits
        if not await self._check_risk_limits(signal):
            return None
        
        # Calculate position size
        position_size = await self._calculate_position_size(signal, strategy)
        if position_size <= 0:
            logger.warning("Position size calculation failed")
            return None
        
        # Execute order
        try:
            order = await self._place_order(signal, position_size)
            
            if order:
                # Track position
                position = self.positions.open_position(order, strategy.get('name', 'unknown'))
                
                # Record to database
                if self.turso:
                    await self.turso.record_trade({
                        'id': order['id'],
                        'symbol': signal['symbol'],
                        'side': signal['direction'],
                        'entry_price': order['price'] or order['average'],
                        'size': position_size,
                        'exchange': 'binance',
                        'strategy': strategy.get('name', 'unknown'),
                        'regime': signal.get('regime', 'unknown'),
                        'paper': self.paper_mode,
                        'reasoning': signal.get('reasoning', {})
                    })
                
                # Update analytics
                self.analytics.add_equity_point(self.positions.equity)
                
                logger.info(
                    f"{'[PAPER] ' if self.paper_mode else '[LIVE] '}"
                    f"Executed {signal['direction']} {position_size} {signal['symbol']}"
                )
                
                return order
            
        except Exception as e:
            logger.error(f"Execution failed: {e}")
            return None
    
    async def close_position(self, position_id: str, reason: str = 'signal') -> Optional[dict]:
        """Close a position."""
        position = self.positions.get_position(position_id)
        if not position:
            logger.warning(f"Position {position_id} not found")
            return None
        
        try:
            # Get current price
            ticker = await self.exchanges.get_ticker(position.symbol, position.exchange)
            exit_price = ticker['last']
            
            # Close position
            trade = self.positions.close_position(position_id, exit_price)
            
            if trade:
                # Record to database
                if self.turso:
                    await self.turso.record_trade({
                        'id': f"close_{trade['id']}",
                        'symbol': trade['symbol'],
                        'side': trade['side'],
                        'entry_price': trade['entry_price'],
                        'exit_price': trade['exit_price'],
                        'size': trade['size'],
                        'pnl': trade['pnl'],
                        'exchange': trade['exchange'],
                        'strategy': trade['strategy'],
                        'paper': self.paper_mode
                    })
                
                # Update analytics
                self.analytics.add_trade(trade)
                self.analytics.add_equity_point(self.positions.equity)
                
                # Track daily stats
                self.daily_trades += 1
                if trade['pnl'] < 0:
                    self.daily_losses += 1
                
                logger.info(
                    f"Closed position {position_id}: "
                    f"P&L ${trade['pnl']:.2f} (Reason: {reason})"
                )
                
                return trade
            
        except Exception as e:
            logger.error(f"Failed to close position: {e}")
            return None
    
    async def update_positions(self):
        """Update all position prices and check stops."""
        await self.positions.update_prices()
        
        # Check for stop losses
        for position in self.positions.get_all_positions():
            await self._check_stop_loss(position)
    
    async def _check_stop_loss(self, position: dict):
        """Check if position hit stop loss."""
        # Simplified: 2% stop loss
        stop_pct = 0.02
        
        entry = position['entry_price']
        current = position['mark_price']
        
        if position['side'] == 'long':
            if current <= entry * (1 - stop_pct):
                await self.close_position(position['id'], 'stop_loss')
        else:
            if current >= entry * (1 + stop_pct):
                await self.close_position(position['id'], 'stop_loss')
    
    async def _validate_signal(self, signal: dict) -> bool:
        """Validate trading signal."""
        required = ['symbol', 'direction', 'entry_price']
        for field in required:
            if field not in signal:
                logger.error(f"Signal missing required field: {field}")
                return False
        
        if signal['direction'] not in ['long', 'short']:
            logger.error(f"Invalid direction: {signal['direction']}")
            return False
        
        return True
    
    async def _check_risk_limits(self, signal: dict) -> bool:
        """Check if trade violates risk limits."""
        # Check max positions
        if len(self.positions.positions) >= self.risk.MAX_CONCURRENT_POSITIONS:
            logger.warning(
                f"Max positions ({self.risk.MAX_CONCURRENT_POSITIONS}) reached"
            )
            return False
        
        # Check daily loss limit (max 3 losing trades)
        if self.daily_losses >= 3:
            logger.warning("Daily loss limit reached (3 trades)")
            return False
        
        # Check drawdown
        current_dd = self.positions.get_current_drawdown()
        if current_dd >= self.risk.HARD_DRAWDOWN_PCT:
            logger.error(f"Hard drawdown limit reached: {current_dd:.2f}%")
            self.execution_enabled = False
            return False
        
        if current_dd >= self.risk.SOFT_DRAWDOWN_PCT:
            logger.warning(f"Soft drawdown: reducing size by 50%")
            signal['size_multiplier'] = signal.get('size_multiplier', 1.0) * 0.5
        
        return True
    
    async def _calculate_position_size(self, signal: dict, strategy: dict) -> float:
        """Calculate position size using Kelly criterion with risk limits."""
        # Get account equity
        equity = self.positions.equity
        
        # Risk per trade
        risk_pct = self.risk.MAX_RISK_PER_TRADE_PCT / 100
        risk_amount = equity * risk_pct
        
        # Apply size reduction from conflicts
        size_multiplier = signal.get('size_multiplier', 1.0)
        risk_amount *= size_multiplier
        
        # Get stop distance from strategy
        stop_distance = strategy.get('stop_loss_pct', 0.02)
        
        # Calculate position size
        entry_price = signal.get('entry_price', 1)
        position_size = risk_amount / (stop_distance * entry_price)
        
        # Apply leverage limit
        max_notional = equity * self.risk.MAX_LEVERAGE
        notional = position_size * entry_price
        if notional > max_notional:
            position_size = max_notional / entry_price
        
        # Minimum position size
        if position_size < 0.001:
            logger.warning(f"Position size too small: {position_size}")
            return 0
        
        return round(position_size, 6)
    
    async def _place_order(self, signal: dict, amount: float) -> dict:
        """Place order on exchange."""
        if self.paper_mode:
            # Paper trading: simulate fill at current price
            return {
                'id': f"paper_{int(datetime.now().timestamp())}",
                'symbol': signal['symbol'],
                'side': signal['direction'],
                'amount': amount,
                'price': signal['entry_price'],
                'average': signal['entry_price'],
                'status': 'filled',
                'exchange': 'binance_paper',
                'timestamp': int(datetime.now().timestamp())
            }
        else:
            # Live trading: real order
            return await self.exchanges.create_order(
                symbol=signal['symbol'],
                side=signal['direction'],
                order_type='market',
                amount=amount,
                exchange_id='binance'
            )
    
    async def kill_switch(self, reason: str = 'manual'):
        """Emergency kill switch - close everything."""
        logger.critical(f"KILL SWITCH ACTIVATED - Reason: {reason}")
        self.execution_enabled = False
        
        # Close all positions
        for position in list(self.positions.positions.values()):
            await self.close_position(position.id, f'kill_switch_{reason}')
        
        logger.critical("Kill switch complete - all positions closed")
    
    def get_status(self) -> dict:
        """Get execution engine status."""
        return {
            'execution_enabled': self.execution_enabled,
            'paper_mode': self.paper_mode,
            'open_positions': len(self.positions.positions),
            'equity': round(self.positions.equity, 2),
            'daily_pnl': round(self.positions.daily_pnl, 2),
            'current_drawdown': round(self.positions.get_current_drawdown(), 2),
            'today_trades': self.daily_trades,
            'today_losses': self.daily_losses
        }
    
    def reset_daily_stats(self):
        """Reset daily statistics."""
        self.positions.reset_daily_stats()
        self.daily_trades = 0
        self.daily_losses = 0
        logger.info("Daily statistics reset")
