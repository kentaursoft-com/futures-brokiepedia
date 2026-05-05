"""Base agent class for all trading departments."""

import asyncio
from abc import ABC, abstractmethod
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any
import aiohttp

QUESTDB_URL = "http://localhost:9001"


class BaseAgent(ABC):
    """Base class for all trading agents."""
    
    def __init__(self, name: str, symbol: str = "BTCUSDT", timeframe: str = "1h"):
        self.name = name
        self.symbol = symbol
        self.timeframe = timeframe
        self.last_signal = None
        self.last_analysis_time = None
        self.confidence = 0.0
        
    async def fetch_ohlcv(self, limit: int = 100) -> List[Dict]:
        """Fetch OHLCV data from QuestDB."""
        try:
            # Map timeframe to table
            table = f"ohlcv_{self.timeframe}" if self.timeframe in ["1m", "5m", "15m", "1h"] else "ohlcv_1m"
            
            sql = f"SELECT * FROM {table} WHERE symbol = '{self.symbol}' ORDER BY ts DESC LIMIT {limit}"
            
            async with aiohttp.ClientSession() as session:
                encoded_sql = sql.replace(" ", "%20").replace("'", "%27")
                async with session.get(
                    f"{QUESTDB_URL}/exec?query={encoded_sql}",
                ) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        rows = data.get("dataset", [])
                        cols = [c["name"] for c in data.get("columns", [])]
                        
                        # Convert to dict list, reverse to chronological order
                        result = []
                        for row in reversed(rows):
                            result.append({cols[i]: row[i] for i in range(len(cols))})
                        return result
                    else:
                        print(f"[{self.name}] QuestDB fetch failed: {resp.status}")
                        return []
                        
        except Exception as e:
            print(f"[{self.name}] Fetch error: {e}")
            return []
    
    def calculate_ema(self, prices: List[float], period: int) -> List[float]:
        """Calculate Exponential Moving Average."""
        if len(prices) < period:
            return prices
        
        multiplier = 2 / (period + 1)
        ema = [sum(prices[:period]) / period]
        
        for price in prices[period:]:
            ema.append((price - ema[-1]) * multiplier + ema[-1])
        
        return ema
    
    def calculate_sma(self, prices: List[float], period: int) -> float:
        """Calculate Simple Moving Average."""
        if len(prices) < period:
            return prices[-1] if prices else 0
        return sum(prices[-period:]) / period
    
    def calculate_rsi(self, prices: List[float], period: int = 14) -> float:
        """Calculate Relative Strength Index."""
        if len(prices) < period + 1:
            return 50.0
        
        gains = []
        losses = []
        
        for i in range(1, len(prices)):
            change = prices[i] - prices[i-1]
            gains.append(max(change, 0))
            losses.append(max(-change, 0))
        
        if len(gains) < period:
            return 50.0
        
        avg_gain = sum(gains[-period:]) / period
        avg_loss = sum(losses[-period:]) / period
        
        if avg_loss == 0:
            return 100.0
        
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        
        return rsi
    
    def calculate_atr(self, candles: List[Dict], period: int = 14) -> float:
        """Calculate Average True Range."""
        if len(candles) < period + 1:
            return 0.0
        
        tr_values = []
        for i in range(1, len(candles)):
            high = candles[i]["high"]
            low = candles[i]["low"]
            prev_close = candles[i-1]["close"]
            
            tr1 = high - low
            tr2 = abs(high - prev_close)
            tr3 = abs(low - prev_close)
            
            tr_values.append(max(tr1, tr2, tr3))
        
        return sum(tr_values[-period:]) / period
    
    def calculate_macd(self, prices: List[float]) -> tuple:
        """Calculate MACD line and signal."""
        ema12 = self.calculate_ema(prices, 12)
        ema26 = self.calculate_ema(prices, 26)
        
        # MACD line = EMA12 - EMA26
        macd_line = [ema12[i] - ema26[i] for i in range(len(ema26))]
        
        # Signal line = EMA9 of MACD
        signal_line = self.calculate_ema(macd_line, 9)
        
        # Histogram = MACD - Signal
        histogram = [macd_line[i] - signal_line[i] for i in range(len(signal_line))]
        
        return macd_line, signal_line, histogram
    
    def calculate_bollinger_bands(self, prices: List[float], period: int = 20, std_dev: float = 2.0) -> tuple:
        """Calculate Bollinger Bands."""
        if len(prices) < period:
            return prices[-1], prices[-1], prices[-1]
        
        sma = self.calculate_sma(prices, period)
        
        variance = sum((p - sma) ** 2 for p in prices[-period:]) / period
        std = variance ** 0.5
        
        upper = sma + (std_dev * std)
        lower = sma - (std_dev * std)
        
        return upper, sma, lower
    
    @abstractmethod
    async def analyze(self) -> Dict[str, Any]:
        """Analyze market and return signal."""
        pass
    
    async def run(self) -> Dict[str, Any]:
        """Run agent analysis cycle."""
        signal = await self.analyze()
        self.last_signal = signal
        self.last_analysis_time = datetime.now(timezone.utc).isoformat()
        return signal
