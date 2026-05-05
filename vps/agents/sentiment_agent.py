"""Sentiment Agent - Analyzes market sentiment using volume and price action."""

from .base_agent import BaseAgent


class SentimentAgent(BaseAgent):
    """Analyzes market sentiment using volume analysis."""
    
    def __init__(self, symbol: str = "BTCUSDT"):
        super().__init__("Sentiment", symbol, "1h")
        
    async def analyze(self) -> dict:
        """Analyze sentiment using volume and price action."""
        candles = await self.fetch_ohlcv(24)
        
        if len(candles) < 10:
            return {
                "department": "Sentiment",
                "direction": "flat",
                "confidence": 0.0,
                "symbol": self.symbol,
                "timeframe": self.timeframe,
                "reason": "Insufficient data",
            }
        
        # Volume analysis
        volumes = [c["volume"] for c in candles]
        avg_volume = sum(volumes[:-5]) / max(1, len(volumes) - 5)
        recent_volume = sum(volumes[-5:]) / 5
        
        # Price action
        closes = [c["close"] for c in candles]
        current_close = closes[-1]
        prev_close = closes[-2]
        
        # Count up vs down candles
        up_candles = 0
        down_candles = 0
        high_volume_up = 0
        high_volume_down = 0
        
        for i in range(1, len(candles)):
            is_up = candles[i]["close"] > candles[i-1]["close"]
            is_high_vol = candles[i]["volume"] > avg_volume
            
            if is_up:
                up_candles += 1
                if is_high_vol:
                    high_volume_up += 1
            else:
                down_candles += 1
                if is_high_vol:
                    high_volume_down += 1
        
        # Volume trend
        volume_surge = recent_volume > avg_volume * 1.5
        volume_decline = recent_volume < avg_volume * 0.5
        
        # Determine sentiment
        if volume_surge and current_close > prev_close:
            direction = "long"
            confidence = min(0.9, 0.75 + (recent_volume / avg_volume - 1) * 0.2)
            reason = f"Strong bullish volume (vol: {recent_volume/avg_volume:.1f}x avg)"
        elif volume_surge and current_close < prev_close:
            direction = "short"
            confidence = min(0.9, 0.75 + (recent_volume / avg_volume - 1) * 0.2)
            reason = f"Strong bearish volume (vol: {recent_volume/avg_volume:.1f}x avg)"
        elif high_volume_up > high_volume_down:
            direction = "long"
            confidence = 0.6
            reason = f"Bullish volume dominance ({high_volume_up} vs {high_volume_down} high-vol candles)"
        elif high_volume_down > high_volume_up:
            direction = "short"
            confidence = 0.6
            reason = f"Bearish volume dominance ({high_volume_down} vs {high_volume_up} high-vol candles)"
        else:
            direction = "flat"
            confidence = 0.45
            reason = "Mixed sentiment, no clear volume signal"
        
        return {
            "department": "Sentiment",
            "direction": direction,
            "confidence": round(confidence, 2),
            "symbol": self.symbol,
            "timeframe": self.timeframe,
            "reason": reason,
            "metrics": {
                "volume_ratio": round(recent_volume / avg_volume, 2),
                "up_candles": up_candles,
                "down_candles": down_candles,
            },
        }
