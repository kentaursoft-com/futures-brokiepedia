"""Execution agent - handles order execution with risk checks."""
import logging
from typing import Dict, Optional
from .exchange_layer import ExchangeAbstractionLayer
from ..config.settings import settings

logger = logging.getLogger(__name__)

class ExecutionAgent:
    """Execute trades with full risk validation."""
    
    def __init__(self, exchange_layer: ExchangeAbstractionLayer):
        self.exchanges = exchange_layer
        self.execution_enabled = True
        self.open_positions: Dict[str, dict] = {}
        
    async def execute_signal(self, signal: dict, strategy: dict) -> Optional[dict]:
        """Execute a trading signal if all checks pass."""
        if not self.execution_enabled:
            logger.warning("Execution disabled - signal ignored")
            return None
        
        # Risk checks
        if not await self._validate_risk(signal):
            return None
        
        # Calculate position size
        position_size = await self._calculate_position_size(signal, strategy)
        if position_size <= 0:
            logger.warning("Position size calculation failed")
            return None
        
        # Execute order
        try:
            order = await self.exchanges.create_order(
                symbol=signal['symbol'],
                side=signal['direction'],
                order_type='market',
                amount=position_size,
                exchange_id='binance'
            )
            
            # Track position
            self.open_positions[order['id']] = {
                'symbol': signal['symbol'],
                'side': signal['direction'],
                'size': position_size,
                'entry_price': order['price'],
                'strategy': strategy.get('name', 'unknown'),
                'timestamp': order['timestamp']
            }
            
            logger.info(f"Executed {signal['direction']} {position_size} {signal['symbol']} @ {order['price']}")
            return order
            
        except Exception as e:
            logger.error(f"Execution failed: {e}")
            return None
    
    async def _validate_risk(self, signal: dict) -> bool:
        """Validate signal against risk parameters."""
        risk = settings.risk
        
        # Check max concurrent positions
        if len(self.open_positions) >= risk.MAX_CONCURRENT_POSITIONS:
            logger.warning(f"Max positions ({risk.MAX_CONCURRENT_POSITIONS}) reached")
            return False
        
        # Check drawdown
        # TODO: Implement actual drawdown tracking
        current_drawdown = 0.0
        if current_drawdown >= risk.HARD_DRAWDOWN_PCT:
            logger.error(f"Hard drawdown limit reached: {current_drawdown:.2f}%")
            self.execution_enabled = False
            return False
        
        if current_drawdown >= risk.SOFT_DRAWDOWN_PCT:
            logger.warning(f"Soft drawdown: reducing size by 50%")
            signal['size_multiplier'] = 0.5
        
        return True
    
    async def _calculate_position_size(self, signal: dict, strategy: dict) -> float:
        """Calculate position size using Kelly criterion."""
        # Get account equity
        try:
            balance = await self.exchanges.get_balance('binance')
            equity = balance['total'].get('USDT', 10000)
        except:
            equity = 10000  # Fallback
        
        # Risk per trade
        risk_pct = settings.risk.MAX_RISK_PER_TRADE_PCT / 100
        risk_amount = equity * risk_pct
        
        # Apply size reduction from conflicts
        size_multiplier = signal.get('size_multiplier', 1.0)
        risk_amount *= size_multiplier
        
        # Get stop distance from strategy
        stop_distance = strategy.get('stop_loss_pct', 0.02)
        
        # Calculate position size
        position_size = risk_amount / (stop_distance * signal.get('entry_price', 1))
        
        # Apply leverage limit
        max_notional = equity * settings.risk.MAX_LEVERAGE
        notional = position_size * signal.get('entry_price', 1)
        if notional > max_notional:
            position_size = max_notional / signal.get('entry_price', 1)
        
        return round(position_size, 6)
    
    async def kill_switch(self):
        """Emergency kill switch - close everything."""
        logger.critical("KILL SWITCH ACTIVATED")
        self.execution_enabled = False
        
        # Cancel all orders
        await self.exchanges.cancel_all_orders()
        
        # Close all positions
        await self.exchanges.close_all_positions()
        
        self.open_positions.clear()
        logger.critical("All positions closed and orders cancelled")
