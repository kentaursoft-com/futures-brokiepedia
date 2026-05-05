"""Momentum Agent - Measures price momentum using RSI and MACD."""

from .base_agent import BaseAgent


class MomentumAgent(BaseAgent):
    """Analyzes price momentum and strength."""
    
    def __init__(self, symbol: str = "BTCUSDT"):
        super().__init__("Momentum", symbol, "15m")
        
    async def analyze(self) -> dict:
        """Analyze momentum using RSI and MACD."""
        candles = await self.fetch_ohlcv(40)
        
        if len(candles) < 27:
            return {
                "department": "Momentum",
                "direction": "flat",
                "confidence": 0.0,
                "symbol": self.symbol,
                "timeframe": self.timeframe,
                "reason": "Insufficient data",
            }
        
        closes = [c["close"] for c in candles]
        
        # Calculate RSI
        rsi = self.calculate_rsi(closes, 14)
        
        # Calculate MACD
        macd_line, signal_line, histogram = self.calculate_macd(closes)
        
        if len(histogram) < 2:
            return {
                "department": "Momentum",
                "direction": "flat",
                "confidence": 0.0,
                "symbol": self.symbol,
                "timeframe": self.timeframe,
                "reason": "MACD calculation failed",
            }
        
        # Analyze momentum
        hist_current = histogram[-1]
        hist_prev = histogram[-2]
        
        # RSI signals
        rsi_oversold = rsi < 30
        rsi_overbought = rsi > 70
        
        # MACD signals
        macd_bullish = hist_current > 0 and hist_current > hist_prev
        macd_bearish = hist_current < 0 and hist_current < hist_prev
        
        # Combine signals
        if macd_bullish and rsi_oversold:
            direction = "long"
            confidence = 0.85
            reason = f"Strong bullish momentum (RSI: {rsi:.1f}, MACD histogram rising)"
        elif macd_bearish and rsi_overbought:
            direction = "short"
            confidence = 0.85
            reason = f"Strong bearish momentum (RSI: {rsi:.1f}, MACD histogram falling)"
        elif macd_bullish:
            direction = "long"
            confidence = 0.65
            reason = f"Bullish momentum building (RSI: {rsi:.1f})"
        elif macd_bearish:
            direction = "short"
            confidence = 0.65
            reason = f"Bearish momentum building (RSI: {rsi:.1f})"
        else:
            direction = "flat"
            confidence = 0.4
            reason = f"Neutral momentum (RSI: {rsi:.1f})"
        
        return {
            "department": "Momentum",
            "direction": direction,
            "confidence": round(confidence, 2),
            "symbol": self.symbol,
            "timeframe": self.timeframe,
            "reason": reason,
            "metrics": {
                "rsi": round(rsi, 1),
                "macd_histogram": round(hist_current, 4),
            },
        }
