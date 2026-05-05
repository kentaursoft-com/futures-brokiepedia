"""Risk Agent - Monitors risk conditions and provides position sizing guidance."""

from .base_agent import BaseAgent


class RiskAgent(BaseAgent):
    """Analyzes risk conditions and portfolio exposure."""
    
    def __init__(self, symbol: str = "BTCUSDT"):
        super().__init__("Risk", symbol, "1h")
        
    async def analyze(self) -> dict:
        """Analyze risk conditions."""
        candles = await self.fetch_ohlcv(50)
        
        if len(candles) < 20:
            return {
                "department": "Risk",
                "direction": "flat",
                "confidence": 0.0,
                "symbol": self.symbol,
                "timeframe": self.timeframe,
                "reason": "Insufficient data",
            }
        
        closes = [c["close"] for c in candles]
        current_price = closes[-1]
        
        # Calculate ATR for volatility
        atr = self.calculate_atr(candles, 14)
        atr_pct = (atr / current_price) * 100 if current_price > 0 else 0
        
        # Recent drawdown from recent high
        recent_high = max(closes[-20:])
        drawdown = (recent_high - current_price) / recent_high if recent_high > 0 else 0
        
        # Risk assessment
        if atr_pct > 5.0:
            # Extreme volatility - reduce exposure
            direction = "flat"
            confidence = 0.85
            reason = f"EXTREME VOLATILITY (ATR: {atr_pct:.2f}%) - No new positions"
        elif drawdown > 0.06:
            # Significant drawdown - halt
            direction = "flat"
            confidence = 0.9
            reason = f"HIGH DRAWDOWN ({drawdown*100:.1f}%) - Risk off"
        elif atr_pct > 3.0:
            # Elevated volatility
            direction = "flat"
            confidence = 0.7
            reason = f"Elevated volatility (ATR: {atr_pct:.2f}%) - Reduced sizing"
        elif drawdown > 0.03:
            # Moderate drawdown
            direction = "flat"
            confidence = 0.6
            reason = f"Moderate drawdown ({drawdown*100:.1f}%) - Caution"
        else:
            # Normal conditions
            direction = "long"  # Risk agent doesn't direct trades, just clears conditions
            confidence = 0.5
            reason = f"Normal risk (ATR: {atr_pct:.2f}%, DD: {drawdown*100:.1f}%)"
        
        return {
            "department": "Risk",
            "direction": direction,
            "confidence": round(confidence, 2),
            "symbol": self.symbol,
            "timeframe": self.timeframe,
            "reason": reason,
            "metrics": {
                "atr_pct": round(atr_pct, 2),
                "drawdown_pct": round(drawdown * 100, 2),
                "recent_high": round(recent_high, 2),
            },
        }
