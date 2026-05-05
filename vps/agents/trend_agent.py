"""Trend Agent - Identifies market direction using EMA crossovers."""

from .base_agent import BaseAgent


class TrendAgent(BaseAgent):
    """Analyzes long-term trend direction."""
    
    def __init__(self, symbol: str = "BTCUSDT"):
        super().__init__("Trend", symbol, "1h")
        
    async def analyze(self) -> dict:
        """Analyze trend using EMA crossover."""
        candles = await self.fetch_ohlcv(50)
        
        if len(candles) < 26:
            return {
                "department": "Trend",
                "direction": "flat",
                "confidence": 0.0,
                "symbol": self.symbol,
                "timeframe": self.timeframe,
                "reason": "Insufficient data",
            }
        
        closes = [c["close"] for c in candles]
        
        # Calculate EMAs
        ema_fast = self.calculate_ema(closes, 12)
        ema_slow = self.calculate_ema(closes, 26)
        
        if len(ema_fast) < 2 or len(ema_slow) < 2:
            return {
                "department": "Trend",
                "direction": "flat",
                "confidence": 0.0,
                "symbol": self.symbol,
                "timeframe": self.timeframe,
                "reason": "EMA calculation failed",
            }
        
        # Current values
        fast_current = ema_fast[-1]
        slow_current = ema_slow[-1]
        fast_prev = ema_fast[-2]
        slow_prev = ema_slow[-2]
        
        # Determine direction
        if fast_current > slow_current and fast_prev <= slow_prev:
            direction = "long"
            confidence = min(0.95, 0.7 + abs(fast_current - slow_current) / slow_current * 10)
            reason = "Golden cross (EMA12 crossed above EMA26)"
        elif fast_current < slow_current and fast_prev >= slow_prev:
            direction = "short"
            confidence = min(0.95, 0.7 + abs(fast_current - slow_current) / slow_current * 10)
            reason = "Death cross (EMA12 crossed below EMA26)"
        elif fast_current > slow_current:
            direction = "long"
            confidence = 0.6
            reason = "EMA12 above EMA26 (bullish)"
        else:
            direction = "short"
            confidence = 0.6
            reason = "EMA12 below EMA26 (bearish)"
        
        return {
            "department": "Trend",
            "direction": direction,
            "confidence": round(confidence, 2),
            "symbol": self.symbol,
            "timeframe": self.timeframe,
            "reason": reason,
            "metrics": {
                "ema12": round(fast_current, 2),
                "ema26": round(slow_current, 2),
            },
        }
