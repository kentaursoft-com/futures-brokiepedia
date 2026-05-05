"""Volatility Agent - Measures market volatility using ATR and Bollinger Bands."""

from .base_agent import BaseAgent


class VolatilityAgent(BaseAgent):
    """Analyzes market volatility conditions."""
    
    def __init__(self, symbol: str = "BTCUSDT"):
        super().__init__("Volatility", symbol, "1h")
        
    async def analyze(self) -> dict:
        """Analyze volatility using ATR and Bollinger Bands."""
        candles = await self.fetch_ohlcv(30)
        
        if len(candles) < 21:
            return {
                "department": "Volatility",
                "direction": "flat",
                "confidence": 0.0,
                "symbol": self.symbol,
                "timeframe": self.timeframe,
                "reason": "Insufficient data",
            }
        
        closes = [c["close"] for c in candles]
        current_price = closes[-1]
        
        # Calculate ATR
        atr = self.calculate_atr(candles, 14)
        
        # Calculate Bollinger Bands
        upper, middle, lower = self.calculate_bollinger_bands(closes, 20, 2.0)
        
        # Volatility metrics
        bb_width = (upper - lower) / middle if middle > 0 else 0
        atr_pct = (atr / current_price) * 100 if current_price > 0 else 0
        
        # Position relative to Bollinger Bands
        if current_price > upper:
            direction = "short"
            confidence = min(0.9, 0.7 + bb_width)
            reason = f"Price above upper Bollinger Band (volatility squeeze expansion likely)"
        elif current_price < lower:
            direction = "long"
            confidence = min(0.9, 0.7 + bb_width)
            reason = f"Price below lower Bollinger Band (mean reversion likely)"
        else:
            # Price within bands - check if near extremes
            band_position = (current_price - lower) / (upper - lower) if (upper - lower) > 0 else 0.5
            
            if band_position > 0.8:
                direction = "short"
                confidence = 0.55
                reason = f"Price near upper band (ATR: {atr_pct:.2f}%)"
            elif band_position < 0.2:
                direction = "long"
                confidence = 0.55
                reason = f"Price near lower band (ATR: {atr_pct:.2f}%)"
            else:
                direction = "flat"
                confidence = 0.5
                reason = f"Price within normal range (ATR: {atr_pct:.2f}%)"
        
        return {
            "department": "Volatility",
            "direction": direction,
            "confidence": round(confidence, 2),
            "symbol": self.symbol,
            "timeframe": self.timeframe,
            "reason": reason,
            "metrics": {
                "atr_pct": round(atr_pct, 2),
                "bb_width": round(bb_width, 4),
                "bb_position": round((current_price - lower) / (upper - lower), 2) if (upper - lower) > 0 else 0.5,
            },
        }
