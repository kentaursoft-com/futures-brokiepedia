#!/usr/bin/env python3
"""Real-time Binance market data feed — WebSocket to QuestDB + KV"""

import os
import json
import asyncio
import aiohttp
import aiohttp.web
from datetime import datetime, timezone
from typing import Dict, List, Optional
import websockets

# Configuration
SYMBOLS = ["BTCUSDT", "ETHUSDT", "SOLUSDT", "BNBUSDT"]
KLINES = ["1m", "5m", "15m", "1h"]
QUESTDB_URL = os.environ.get("QUESTDB_URL", "http://localhost:9001")
KV_UPDATE_INTERVAL = 5  # seconds

class BinanceWebSocketFeed:
    """Real-time Binance WebSocket feed handler."""
    
    def __init__(self):
        self.ws = None
        self.running = False
        self.last_candles: Dict[str, dict] = {}
        self.last_update = datetime.now(timezone.utc)
        self.symbols_tracked = SYMBOLS.copy()
        self._callbacks = []
        
    def on_candle(self, callback):
        """Register callback for new candles."""
        self._callbacks.append(callback)
        
    async def connect(self):
        """Connect to Binance combined stream."""
        streams = "/".join([f"{s.lower()}@kline_{k}" for s in SYMBOLS for k in ["1m"]])
        uri = f"wss://stream.binance.com:9443/ws/{streams}"
        
        print(f"[market] Connecting to Binance WebSocket: {uri[:60]}...")
        
        try:
            self.ws = await websockets.connect(uri)
            self.running = True
            print("[market] Binance WebSocket connected")
            
            # Start heartbeat
            asyncio.create_task(self._heartbeat())
            
            # Process messages
            async for message in self.ws:
                if not self.running:
                    break
                await self._handle_message(json.loads(message))
                
        except Exception as e:
            print(f"[market] WebSocket error: {e}")
            self.running = False
            raise
            
    async def _heartbeat(self):
        """Keep connection alive and update KV."""
        while self.running:
            try:
                await asyncio.sleep(KV_UPDATE_INTERVAL)
                
                # Update last candle timestamp
                self.last_update = datetime.now(timezone.utc)
                
                # Write to QuestDB
                await self._write_to_questdb()
                
                # Update KV
                await self._update_kv()
                
            except Exception as e:
                print(f"[market] Heartbeat error: {e}")
                
    async def _handle_message(self, msg: dict):
        """Process incoming WebSocket message."""
        if msg.get("e") != "kline":
            return
            
        k = msg["k"]
        symbol = msg["s"]
        
        candle = {
            "symbol": symbol,
            "interval": k["i"],
            "open": float(k["o"]),
            "high": float(k["h"]),
            "low": float(k["l"]),
            "close": float(k["c"]),
            "volume": float(k["v"]),
            "quote_volume": float(k["q"]),
            "trades": int(k["n"]),
            "timestamp": k["t"],
            "is_closed": k["x"],
        }
        
        key = f"{symbol}_{k['i']}"
        self.last_candles[key] = candle
        
        # Notify callbacks
        for cb in self._callbacks:
            try:
                await cb(candle)
            except Exception as e:
                print(f"[market] Callback error: {e}")
                
    async def _write_to_questdb(self):
        """Write candles to QuestDB via InfluxDB line protocol."""
        try:
            lines = []
            for key, candle in self.last_candles.items():
                if not candle.get("is_closed"):
                    continue
                
                # InfluxDB line protocol format
                # measurement,tags fields timestamp
                # timestamp in nanoseconds
                line = (
                    f"ohlcv_1m,symbol={candle['symbol']} "
                    f"open={candle['open']},high={candle['high']},"
                    f"low={candle['low']},close={candle['close']},"
                    f"volume={candle['volume']} "
                    f"{candle['timestamp'] * 1000000}"  # ms to ns
                )
                lines.append(line)
                
            if lines:
                async with aiohttp.ClientSession() as session:
                    async with session.post(
                        f"{QUESTDB_URL}/write",
                        data="\n".join(lines),
                        headers={"Content-Type": "text/plain"},
                    ) as resp:
                        if resp.status == 204:
                            print(f"[market] Wrote {len(lines)} candles to QuestDB")
                        else:
                            text = await resp.text()
                            print(f"[market] QuestDB write failed: {resp.status} {text[:100]}")
                            
        except Exception as e:
            print(f"[market] QuestDB write error: {e}")
            
    async def _update_kv(self):
        """Update Cloudflare KV with market state."""
        try:
            # Get latest prices
            prices = {}
            for key, candle in self.last_candles.items():
                symbol = candle["symbol"]
                if symbol not in prices or candle["timestamp"] > prices[symbol]["timestamp"]:
                    prices[symbol] = {
                        "price": candle["close"],
                        "timestamp": candle["timestamp"],
                    }
                    
            # Prepare KV data
            kv_data = {
                "market_data": {
                    "prices": prices,
                    "last_update": self.last_update.isoformat(),
                    "symbols_tracked": self.symbols_tracked,
                },
                "binance_ws_alive": {
                    "value": self.running,
                    "timestamp": int(self.last_update.timestamp() * 1000),
                },
            }
            
            # Write to KV via Cloudflare API
            await self._kv_put("market_state", kv_data)
            
        except Exception as e:
            print(f"[market] KV update error: {e}")
            
    async def _kv_put(self, key: str, value: dict):
        """Write to Cloudflare KV."""
        cf_account = os.environ.get("CF_ACCOUNT_ID")
        cf_token = os.environ.get("CF_API_TOKEN")
        kv_ns = os.environ.get("KV_LIVE_STATE_ID")
        
        if not all([cf_account, cf_token, kv_ns]):
            return
            
        url = (
            f"https://api.cloudflare.com/client/v4/accounts/"
            f"{cf_account}/storage/kv/namespaces/"
            f"{kv_ns}/values/{key}"
        )
        
        async with aiohttp.ClientSession() as session:
            async with session.put(
                url,
                data=json.dumps(value),
                headers={
                    "Authorization": f"Bearer {cf_token}",
                    "Content-Type": "application/json",
                },
            ) as resp:
                if resp.status != 200:
                    text = await resp.text()
                    print(f"[market] KV write failed: {resp.status} {text}")
                    
    async def disconnect(self):
        """Graceful disconnect."""
        self.running = False
        if self.ws:
            await self.ws.close()
            
    async def reconnect_loop(self):
        """Auto-reconnect loop."""
        while True:
            try:
                await self.connect()
            except Exception as e:
                print(f"[market] Connection lost, reconnecting in 5s... ({e})")
                await asyncio.sleep(5)


class MarketDataManager:
    """Manages all market data feeds and state."""
    
    def __init__(self):
        self.ws_feed = BinanceWebSocketFeed()
        self._price_cache: Dict[str, float] = {}
        self._running = False
        
    async def start(self):
        """Start all market data feeds."""
        self._running = True
        
        # Register callbacks
        self.ws_feed.on_candle(self._on_candle)
        
        # Start WebSocket
        asyncio.create_task(self.ws_feed.reconnect_loop())
        
        print("[market] Market data manager started")
        
    async def stop(self):
        """Stop all feeds."""
        self._running = False
        await self.ws_feed.disconnect()
        
    async def _on_candle(self, candle: dict):
        """Handle new candle."""
        self._price_cache[candle["symbol"]] = candle["close"]
        
    def get_price(self, symbol: str) -> Optional[float]:
        """Get latest price for symbol."""
        return self._price_cache.get(symbol)
        
    def get_all_prices(self) -> Dict[str, float]:
        """Get all latest prices."""
        return self._price_cache.copy()
        
    @property
    def is_connected(self) -> bool:
        """Check if WebSocket is connected."""
        return self.ws_feed.running


# Global instance
market_manager = MarketDataManager()


async def test():
    """Test the market data feed."""
    print("[test] Starting market data test...")
    
    manager = MarketDataManager()
    await manager.start()
    
    # Run for 30 seconds
    for i in range(30):
        await asyncio.sleep(1)
        prices = manager.get_all_prices()
        if prices:
            print(f"[test] Prices: {prices}")
            
    await manager.stop()
    print("[test] Test complete")


if __name__ == "__main__":
    asyncio.run(test())
