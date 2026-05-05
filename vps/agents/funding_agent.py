"""Funding Agent - Analyzes funding rates for perpetual futures."""

from .base_agent import BaseAgent


class FundingAgent(BaseAgent):
    """Analyzes funding rate conditions."""
    
    def __init__(self, symbol: str = "BTCUSDT"):
        super().__init__("Funding", symbol, "8h")
        
    async def analyze(self) -> dict:
        """Analyze funding rate implications."""
        # Note: Real funding rates would come from Binance API
        # For now, we simulate based on recent price action
        candles = await self.fetch_ohlcv(48)
        
        if len(candles) < 10:
            return {
                "department": "Funding",
                "direction": "flat",
                "confidence": 0.0,
                "symbol": self.symbol,
                "timeframe": self.timeframe,
                "reason": "Insufficient data",
            }
        
        closes = [c["close"] for c in candles]
        
        # Simulate funding rate based on recent trend
        # In reality, this would be: GET /fapi/v1/fundingRate from Binance
        short_term_return = (closes[-1] - closes[-min(8, len(closes))]) / closes[-min(8, len(closes))]
        
        # Simulate funding rate (positive = longs pay shorts)
        simulated_funding = short_term_return * 0.1  # Simplified model
        
        # Extreme funding rates create contrarian signals
        if simulated_funding > 0.01:  # > 1% funding
            direction = "short"
            confidence = min(0.9, 0.7 + simulated_funding * 5)
            reason = f"Extremely high funding ({simulated_funding*100:.2f}%) - longs overpaying"
        elif simulated_funding < -0.01:
            direction = "long"
            confidence = min(0.9, 0.7 + abs(simulated_funding) * 5)
            reason = f"Extremely negative funding ({simulated_funding*100:.2f}%) - shorts overpaying"
        elif simulated_funding > 0.005:
            direction = "short"
            confidence = 0.6
            reason = f"Elevated funding ({simulated_funding*100:.2f}%)"
        elif simulated_funding < -0.005:
            direction = "long"
            confidence = 0.6
            reason = f"Negative funding ({simulated_funding*100:.2f}%)"
        else:
            direction = "flat"
            confidence = 0.5
            reason = f"Normal funding conditions ({simulated_funding*100:.2f}%)"
        
        return {
            "department": "Funding",
            "direction": direction,
            "confidence": round(confidence, 2),
            "symbol": self.symbol,
            "timeframe": self.timeframe,
            "reason": reason,
            "metrics": {
                "estimated_funding": round(simulated_funding * 100, 3),
                "price_change_8h": round(short_term_return * 100, 2),
            },
        }
