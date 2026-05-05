"""LLM-powered trading agents using OpenRouter free models."""

import json
from typing import Dict, Any
from datetime import datetime, timezone

from .base_agent import BaseAgent
from .llm_client import LLMClient


class LLMTrendAgent(BaseAgent):
    """Trend analysis using LLM."""
    
    def __init__(self, symbol: str = "BTCUSDT"):
        super().__init__("Trend", symbol, "1h")
        self.llm = LLMClient("openrouter/free")
        
    async def analyze(self) -> dict:
        """Analyze trend using LLM."""
        candles = await self.fetch_ohlcv(30)
        
        if len(candles) < 5:
            return {
                "department": "Trend",
                "direction": "flat",
                "confidence": 0.0,
                "symbol": self.symbol,
                "timeframe": self.timeframe,
                "reason": "Insufficient data",
                "llm": False,
            }
        
        # Format candle data for LLM
        recent_candles = candles[-20:]
        price_data = []
        for c in recent_candles:
            price_data.append({
                "open": round(c["open"], 2),
                "high": round(c["high"], 2),
                "low": round(c["low"], 2),
                "close": round(c["close"], 2),
                "volume": round(c["volume"], 2),
                "time": c.get("ts", "")[:19] if isinstance(c.get("ts"), str) else "",
            })
        
        system_prompt = """You are a professional crypto trend analyst. Analyze OHLCV data and return ONLY a JSON object with:
{
  "direction": "long" | "short" | "flat",
  "confidence": 0.0-1.0,
  "reason": "brief explanation",
  "metrics": {"trend_strength": 0-10, "support": price, "resistance": price}
}
Rules:
- "long" if clear uptrend, "short" if clear downtrend, "flat" if sideways
- Confidence 0.9+ only for very strong trends
- Be concise, max 2 sentences for reason"""

        user_prompt = f"""Analyze {self.symbol} trend based on recent OHLCV data:
{json.dumps(price_data[-10:], indent=2)}

Current price: {price_data[-1]["close"]}

Return JSON with direction, confidence, and reasoning."""

        result = await self.llm.analyze(system_prompt, user_prompt)
        
        if "error" in result:
            # Fallback to classical
            return await self._classical_fallback(candles)
        
        return {
            "department": "Trend",
            "direction": result.get("direction", "flat"),
            "confidence": result.get("confidence", 0.0),
            "symbol": self.symbol,
            "timeframe": self.timeframe,
            "reason": result.get("reason", ""),
            "metrics": result.get("metrics", {}),
            "llm": True,
            "usage": result.get("usage", {}),
        }
    
    async def _classical_fallback(self, candles):
        """Fallback to classical EMA analysis."""
        closes = [c["close"] for c in candles]
        ema_fast = self.calculate_ema(closes, 12)
        ema_slow = self.calculate_ema(closes, 26)
        
        if len(ema_fast) < 2 or len(ema_slow) < 2:
            return {"department": "Trend", "direction": "flat", "confidence": 0.0, "symbol": self.symbol, "timeframe": self.timeframe, "reason": "EMA failed", "llm": False}
        
        fast_current = ema_fast[-1]
        slow_current = ema_slow[-1]
        
        if fast_current > slow_current:
            direction = "long"
            confidence = 0.6
        else:
            direction = "short"
            confidence = 0.6
        
        return {
            "department": "Trend",
            "direction": direction,
            "confidence": confidence,
            "symbol": self.symbol,
            "timeframe": self.timeframe,
            "reason": f"Classical EMA fallback (EMA12: {fast_current:.0f} vs EMA26: {slow_current:.0f})",
            "llm": False,
        }


class LLMMomentumAgent(BaseAgent):
    """Momentum analysis using LLM."""
    
    def __init__(self, symbol: str = "BTCUSDT"):
        super().__init__("Momentum", symbol, "15m")
        self.llm = LLMClient("openrouter/free")
        
    async def analyze(self) -> dict:
        """Analyze momentum using LLM."""
        candles = await self.fetch_ohlcv(30)
        
        if len(candles) < 5:
            return {"department": "Momentum", "direction": "flat", "confidence": 0.0, "symbol": self.symbol, "timeframe": self.timeframe, "reason": "Insufficient data", "llm": False}
        
        closes = [c["close"] for c in candles]
        rsi = self.calculate_rsi(closes, 14)
        
        recent_changes = []
        for i in range(max(0, len(candles)-5), len(candles)):
            change = ((candles[i]["close"] - candles[i]["open"]) / candles[i]["open"]) * 100
            recent_changes.append(round(change, 2))
        
        system_prompt = """You are a crypto momentum analyst. Analyze price momentum and return ONLY JSON:
{
  "direction": "long" | "short" | "flat",
  "confidence": 0.0-1.0,
  "reason": "brief explanation",
  "metrics": {"rsi": 0-100, "momentum_score": -10 to 10}
}
Rules:
- Consider RSI levels (oversold <30, overbought >70)
- Look at recent candle momentum
- "long" if momentum building bullish, "short" if bearish"""

        user_prompt = f"""Analyze {self.symbol} momentum:
- RSI(14): {rsi:.1f}
- Recent 5m changes (%): {recent_changes}
- Current price: {closes[-1]:.2f}

Return JSON analysis."""

        result = await self.llm.analyze(system_prompt, user_prompt)
        
        if "error" in result:
            return {"department": "Momentum", "direction": "flat", "confidence": 0.0, "symbol": self.symbol, "timeframe": self.timeframe, "reason": f"LLM error: {result.get('error', '')}", "llm": False}
        
        return {
            "department": "Momentum",
            "direction": result.get("direction", "flat"),
            "confidence": result.get("confidence", 0.0),
            "symbol": self.symbol,
            "timeframe": self.timeframe,
            "reason": result.get("reason", ""),
            "metrics": result.get("metrics", {}),
            "llm": True,
            "usage": result.get("usage", {}),
        }


class LLMVolatilityAgent(BaseAgent):
    """Volatility analysis using LLM."""
    
    def __init__(self, symbol: str = "BTCUSDT"):
        super().__init__("Volatility", symbol, "1h")
        self.llm = LLMClient("openrouter/free")
        
    async def analyze(self) -> dict:
        """Analyze volatility using LLM."""
        candles = await self.fetch_ohlcv(30)
        
        if len(candles) < 5:
            return {"department": "Volatility", "direction": "flat", "confidence": 0.0, "symbol": self.symbol, "timeframe": self.timeframe, "reason": "Insufficient data", "llm": False}
        
        closes = [c["close"] for c in candles]
        current_price = closes[-1]
        
        # Calculate basic stats
        atr = self.calculate_atr(candles, 14)
        atr_pct = (atr / current_price) * 100 if current_price > 0 else 0
        
        recent_ranges = []
        for c in candles[-5:]:
            range_pct = ((c["high"] - c["low"]) / c["low"]) * 100
            recent_ranges.append(round(range_pct, 2))
        
        system_prompt = """You are a volatility analyst. Analyze market volatility and return ONLY JSON:
{
  "direction": "long" | "short" | "flat",
  "confidence": 0.0-1.0,
  "reason": "brief explanation",
  "metrics": {"volatility_regime": "low|normal|high", "bb_position": 0-1}
}
Rules:
- High volatility often precedes breakouts
- Extreme volatility = caution (flat)
- Low volatility after consolidation = breakout setup"""

        user_prompt = f"""Analyze {self.symbol} volatility:
- ATR%: {atr_pct:.2f}%
- Recent candle ranges (%): {recent_ranges}
- Current price: {current_price:.2f}

Return JSON analysis."""

        result = await self.llm.analyze(system_prompt, user_prompt)
        
        if "error" in result:
            return {"department": "Volatility", "direction": "flat", "confidence": 0.0, "symbol": self.symbol, "timeframe": self.timeframe, "reason": f"LLM error: {result.get('error', '')}", "llm": False}
        
        return {
            "department": "Volatility",
            "direction": result.get("direction", "flat"),
            "confidence": result.get("confidence", 0.0),
            "symbol": self.symbol,
            "timeframe": self.timeframe,
            "reason": result.get("reason", ""),
            "metrics": result.get("metrics", {}),
            "llm": True,
            "usage": result.get("usage", {}),
        }


class LLMSentimentAgent(BaseAgent):
    """Sentiment analysis using LLM."""
    
    def __init__(self, symbol: str = "BTCUSDT"):
        super().__init__("Sentiment", symbol, "1h")
        self.llm = LLMClient("openrouter/free")
        
    async def analyze(self) -> dict:
        """Analyze sentiment using LLM."""
        candles = await self.fetch_ohlcv(24)
        
        if len(candles) < 5:
            return {"department": "Sentiment", "direction": "flat", "confidence": 0.0, "symbol": self.symbol, "timeframe": self.timeframe, "reason": "Insufficient data", "llm": False}
        
        volumes = [c["volume"] for c in candles[-10:]]
        avg_vol = sum(volumes) / len(volumes)
        vol_changes = []
        for i in range(1, len(volumes)):
            change = ((volumes[i] - volumes[i-1]) / volumes[i-1]) * 100 if volumes[i-1] > 0 else 0
            vol_changes.append(round(change, 1))
        
        up_count = sum(1 for c in candles[-10:] if c["close"] > c["open"])
        down_count = 10 - up_count
        
        system_prompt = """You are a market sentiment analyst. Analyze volume and price action, return ONLY JSON:
{
  "direction": "long" | "short" | "flat",
  "confidence": 0.0-1.0,
  "reason": "brief explanation",
  "metrics": {"sentiment_score": -10 to 10, "volume_trend": "increasing|decreasing|stable"}
}
Rules:
- High volume on up candles = bullish
- High volume on down candles = bearish
- Volume drying up = indecision"""

        user_prompt = f"""Analyze {self.symbol} sentiment:
- Volume changes (%): {vol_changes}
- Avg volume: {avg_vol:.0f}
- Up/Down candles (last 10): {up_count}/{down_count}

Return JSON analysis."""

        result = await self.llm.analyze(system_prompt, user_prompt)
        
        if "error" in result:
            return {"department": "Sentiment", "direction": "flat", "confidence": 0.0, "symbol": self.symbol, "timeframe": self.timeframe, "reason": f"LLM error: {result.get('error', '')}", "llm": False}
        
        return {
            "department": "Sentiment",
            "direction": result.get("direction", "flat"),
            "confidence": result.get("confidence", 0.0),
            "symbol": self.symbol,
            "timeframe": self.timeframe,
            "reason": result.get("reason", ""),
            "metrics": result.get("metrics", {}),
            "llm": True,
            "usage": result.get("usage", {}),
        }


class LLMFundingAgent(BaseAgent):
    """Funding rate analysis using LLM."""
    
    def __init__(self, symbol: str = "BTCUSDT"):
        super().__init__("Funding", symbol, "8h")
        self.llm = LLMClient("openrouter/free")
        
    async def analyze(self) -> dict:
        """Analyze funding implications using LLM."""
        candles = await self.fetch_ohlcv(20)
        
        if len(candles) < 5:
            return {"department": "Funding", "direction": "flat", "confidence": 0.0, "symbol": self.symbol, "timeframe": self.timeframe, "reason": "Insufficient data", "llm": False}
        
        closes = [c["close"] for c in candles]
        returns = []
        for i in range(1, len(closes)):
            ret = ((closes[i] - closes[i-1]) / closes[i-1]) * 100
            returns.append(round(ret, 2))
        
        current_price = closes[-1]
        price_8h_ago = closes[0] if len(closes) > 0 else current_price
        change_8h = ((current_price - price_8h_ago) / price_8h_ago) * 100
        
        system_prompt = """You are a funding rate analyst for perpetual futures. Analyze price action and return ONLY JSON:
{
  "direction": "long" | "short" | "flat",
  "confidence": 0.0-1.0,
  "reason": "brief explanation",
  "metrics": {"estimated_funding": "-1.0 to 1.0%", "crowded_side": "long|short|neutral"}
}
Rules:
- Strong uptrend often means high positive funding (longs pay shorts)
- Extreme positive funding = contrarian short signal
- Extreme negative funding = contrarian long signal"""

        user_prompt = f"""Analyze {self.symbol} funding implications:
- 8h price change: {change_8h:.2f}%
- Recent returns (%): {returns[-5:]}
- Current price: {current_price:.2f}

Return JSON analysis."""

        result = await self.llm.analyze(system_prompt, user_prompt)
        
        if "error" in result:
            return {"department": "Funding", "direction": "flat", "confidence": 0.0, "symbol": self.symbol, "timeframe": self.timeframe, "reason": f"LLM error: {result.get('error', '')}", "llm": False}
        
        return {
            "department": "Funding",
            "direction": result.get("direction", "flat"),
            "confidence": result.get("confidence", 0.0),
            "symbol": self.symbol,
            "timeframe": self.timeframe,
            "reason": result.get("reason", ""),
            "metrics": result.get("metrics", {}),
            "llm": True,
            "usage": result.get("usage", {}),
        }


class LLMRiskAgent(BaseAgent):
    """Risk analysis using LLM."""
    
    def __init__(self, symbol: str = "BTCUSDT"):
        super().__init__("Risk", symbol, "1h")
        self.llm = LLMClient("openrouter/free")
        
    async def analyze(self) -> dict:
        """Analyze risk using LLM."""
        candles = await self.fetch_ohlcv(30)
        
        if len(candles) < 5:
            return {"department": "Risk", "direction": "flat", "confidence": 0.0, "symbol": self.symbol, "timeframe": self.timeframe, "reason": "Insufficient data", "llm": False}
        
        closes = [c["close"] for c in candles]
        current_price = closes[-1]
        
        atr = self.calculate_atr(candles, 14)
        atr_pct = (atr / current_price) * 100 if current_price > 0 else 0
        
        recent_high = max(closes[-20:]) if len(closes) >= 20 else max(closes)
        drawdown = ((recent_high - current_price) / recent_high) * 100 if recent_high > 0 else 0
        
        daily_range = ((max(c["high"] for c in candles[-5:]) - min(c["low"] for c in candles[-5:])) / min(c["low"] for c in candles[-5:])) * 100
        
        system_prompt = """You are a risk management analyst. Assess market risk and return ONLY JSON:
{
  "direction": "long" | "short" | "flat",
  "confidence": 0.0-1.0,
  "reason": "brief explanation",
  "metrics": {"risk_level": "low|medium|high|extreme", "max_position_size": "0-100%"}
}
Rules:
- ATR > 5% = EXTREME risk, flat
- Drawdown > 6% = high risk, flat
- Normal conditions = allow trading
- Risk agent has VETO power"""

        user_prompt = f"""Assess {self.symbol} risk:
- ATR%: {atr_pct:.2f}%
- Drawdown from high: {drawdown:.2f}%
- Recent daily range: {daily_range:.2f}%
- Current price: {current_price:.2f}

Return JSON risk assessment."""

        result = await self.llm.analyze(system_prompt, user_prompt)
        
        if "error" in result:
            # Risk agent always has veto logic as fallback
            if atr_pct > 5 or drawdown > 6:
                return {"department": "Risk", "direction": "flat", "confidence": 0.9, "symbol": self.symbol, "timeframe": self.timeframe, "reason": f"HIGH RISK (ATR: {atr_pct:.2f}%, DD: {drawdown:.1f}%)", "llm": False}
            return {"department": "Risk", "direction": "long", "confidence": 0.5, "symbol": self.symbol, "timeframe": self.timeframe, "reason": f"Normal risk (ATR: {atr_pct:.2f}%)", "llm": False}
        
        return {
            "department": "Risk",
            "direction": result.get("direction", "flat"),
            "confidence": result.get("confidence", 0.0),
            "symbol": self.symbol,
            "timeframe": self.timeframe,
            "reason": result.get("reason", ""),
            "metrics": result.get("metrics", {}),
            "llm": True,
            "usage": result.get("usage", {}),
        }
