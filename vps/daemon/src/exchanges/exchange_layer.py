"""Exchange Abstraction Layer using ccxt."""
import logging
from typing import Dict, List, Optional, Any
import ccxt.async_support as ccxt

logger = logging.getLogger(__name__)

class ExchangeAbstractionLayer:
    """Unified interface for all supported exchanges."""
    
    SUPPORTED_EXCHANGES = {
        'binance': ccxt.binanceusdm,
        'bybit': ccxt.bybit,
        'bitget': ccxt.bitget,
        'mexc': ccxt.mexc,
        'kucoin': ccxt.kucoinfutures,
        'bingx': ccxt.bingx,
        'okx': ccxt.okx,
        'gateio': ccxt.gateio
    }
    
    def __init__(self, config: dict = None):
        self.config = config or {}
        self.exchanges: Dict[str, Any] = {}
        self.paper_mode = True  # Default to paper
        
    async def initialize(self, exchange_ids: List[str] = None, 
                        api_keys: dict = None):
        """Initialize exchange connections."""
        exchange_ids = exchange_ids or list(self.SUPPORTED_EXCHANGES.keys())
        api_keys = api_keys or {}
        
        for ex_id in exchange_ids:
            if ex_id not in self.SUPPORTED_EXCHANGES:
                logger.warning(f"Exchange {ex_id} not supported")
                continue
                
            try:
                exchange_class = self.SUPPORTED_EXCHANGES[ex_id]
                config = {
                    'enableRateLimit': True,
                    'options': {
                        'defaultType': 'swap'  # Futures
                    }
                }
                
                # Add API credentials if available
                if ex_id in api_keys:
                    config.update(api_keys[ex_id])
                
                # Enable testnet for paper trading
                if self.paper_mode and ex_id == 'binance':
                    config['options']['defaultTestnet'] = True
                    
                exchange = exchange_class(config)
                await exchange.load_markets()
                
                self.exchanges[ex_id] = exchange
                logger.info(f"Initialized {ex_id}")
                
            except Exception as e:
                logger.error(f"Failed to initialize {ex_id}: {e}")
    
    async def get_ticker(self, symbol: str, exchange_id: str = 'binance') -> dict:
        """Get current ticker data."""
        exchange = self.exchanges.get(exchange_id)
        if not exchange:
            raise ValueError(f"Exchange {exchange_id} not initialized")
        
        ticker = await exchange.fetch_ticker(symbol)
        return {
            'symbol': symbol,
            'exchange': exchange_id,
            'bid': ticker['bid'],
            'ask': ticker['ask'],
            'last': ticker['last'],
            'high': ticker['high'],
            'low': ticker['low'],
            'volume': ticker['baseVolume'],
            'change': ticker['change'],
            'change_pct': ticker['percentage'],
            'timestamp': ticker['timestamp']
        }
    
    async def get_balance(self, exchange_id: str = 'binance') -> dict:
        """Get account balance."""
        exchange = self.exchanges.get(exchange_id)
        if not exchange:
            raise ValueError(f"Exchange {exchange_id} not initialized")
        
        balance = await exchange.fetch_balance()
        return {
            'exchange': exchange_id,
            'total': balance.get('total', {}),
            'free': balance.get('free', {}),
            'used': balance.get('used', {})
        }
    
    async def create_order(self, symbol: str, side: str, order_type: str,
                          amount: float, price: float = None,
                          params: dict = None, exchange_id: str = 'binance') -> dict:
        """Create an order."""
        exchange = self.exchanges.get(exchange_id)
        if not exchange:
            raise ValueError(f"Exchange {exchange_id} not initialized")
        
        params = params or {}
        
        try:
            order = await exchange.create_order(
                symbol, order_type, side, amount, price, params
            )
            logger.info(f"Order created: {order['id']} on {exchange_id}")
            return order
        except Exception as e:
            logger.error(f"Order creation failed: {e}")
            raise
    
    async def cancel_all_orders(self, symbol: str = None, 
                                exchange_id: str = None):
        """Cancel all open orders."""
        targets = [exchange_id] if exchange_id else self.exchanges.keys()
        
        for ex_id in targets:
            exchange = self.exchanges.get(ex_id)
            if not exchange:
                continue
                
            try:
                if symbol:
                    await exchange.cancel_all_orders(symbol)
                else:
                    # Cancel all orders across all symbols
                    open_orders = await exchange.fetch_open_orders()
                    for order in open_orders:
                        await exchange.cancel_order(order['id'], order['symbol'])
                logger.info(f"Cancelled all orders on {ex_id}")
            except Exception as e:
                logger.error(f"Failed to cancel orders on {ex_id}: {e}")
    
    async def close_all_positions(self, exchange_id: str = None):
        """Close all open positions at market."""
        targets = [exchange_id] if exchange_id else self.exchanges.keys()
        
        for ex_id in targets:
            exchange = self.exchanges.get(ex_id)
            if not exchange:
                continue
                
            try:
                positions = await exchange.fetch_positions()
                for pos in positions:
                    if float(pos['contracts']) != 0:
                        side = 'sell' if pos['side'] == 'long' else 'buy'
                        await exchange.create_market_order(
                            pos['symbol'], side, abs(float(pos['contracts']))
                        )
                logger.info(f"Closed all positions on {ex_id}")
            except Exception as e:
                logger.error(f"Failed to close positions on {ex_id}: {e}")
    
    async def get_funding_rate(self, symbol: str, 
                               exchange_id: str = 'binance') -> dict:
        """Get current funding rate."""
        exchange = self.exchanges.get(exchange_id)
        if not exchange:
            raise ValueError(f"Exchange {exchange_id} not initialized")
        
        funding = await exchange.fetch_funding_rate(symbol)
        return {
            'symbol': symbol,
            'exchange': exchange_id,
            'rate': funding['fundingRate'],
            'timestamp': funding['fundingTimestamp'],
            'interval': funding['fundingInterval']
        }
    
    async def close(self):
        """Close all exchange connections."""
        for ex_id, exchange in self.exchanges.items():
            try:
                await exchange.close()
                logger.info(f"Closed connection to {ex_id}")
            except Exception as e:
                logger.error(f"Error closing {ex_id}: {e}")
