"""Binance Futures WebSocket ingestion service."""
import asyncio
import json
import logging
from datetime import datetime
from typing import Callable, Dict, List, Optional
import websockets

logger = logging.getLogger(__name__)

class BinanceFuturesIngestion:
    """Real-time market data ingestion from Binance Futures."""
    
    def __init__(self, symbols: List[str] = None, on_candle: Callable = None):
        self.symbols = symbols or ['btcusdt']
        self.ws_url = "wss://fstream.binance.com/ws"
        self.websocket = None
        self.running = False
        self.on_candle = on_candle
        self.reconnect_delay = 5
        self.candles: Dict[str, dict] = {}
        
    def _get_stream_url(self) -> str:
        """Construct multiplex stream URL."""
        streams = "/".join([f"{s}@kline_1m" for s in self.symbols])
        return f"{self.ws_url}/stream?streams={streams}"
    
    async def connect(self):
        """Connect to Binance WebSocket."""
        self.running = True
        
        while self.running:
            try:
                logger.info(f"Connecting to Binance Futures WebSocket...")
                async with websockets.connect(self._get_stream_url()) as ws:
                    self.websocket = ws
                    logger.info("Connected to Binance Futures WebSocket")
                    self.reconnect_delay = 5
                    
                    async for message in ws:
                        await self._handle_message(json.loads(message))
                        
            except websockets.exceptions.ConnectionClosed:
                logger.warning("WebSocket connection closed, reconnecting...")
            except Exception as e:
                logger.error(f"WebSocket error: {e}")
            
            if self.running:
                await asyncio.sleep(self.reconnect_delay)
                self.reconnect_delay = min(self.reconnect_delay * 2, 60)
    
    async def _handle_message(self, data: dict):
        """Process incoming WebSocket message."""
        if 'data' not in data:
            return
            
        msg = data['data']
        if msg.get('e') == 'kline':
            await self._process_kline(msg)
    
    async def _process_kline(self, msg: dict):
        """Process kline/candlestick data."""
        k = msg['k']
        symbol = msg['s']
        
        candle = {
            'symbol': symbol,
            'timestamp': datetime.fromtimestamp(k['t'] / 1000),
            'open': float(k['o']),
            'high': float(k['h']),
            'low': float(k['l']),
            'close': float(k['c']),
            'volume': float(k['v']),
            'quote_volume': float(k['q']),
            'trades': int(k['n']),
            'is_closed': k['x']
        }
        
        self.candles[symbol] = candle
        
        if self.on_candle:
            await self.on_candle(candle)
    
    async def disconnect(self):
        """Disconnect from WebSocket."""
        self.running = False
        if self.websocket:
            await self.websocket.close()
    
    def get_latest_candle(self, symbol: str) -> Optional[dict]:
        """Get latest candle for symbol."""
        return self.candles.get(symbol)
