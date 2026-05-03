"""Market regime classifier using ADX and ATR."""
import logging
from typing import Dict, List
import numpy as np

logger = logging.getLogger(__name__)

class MarketRegimeClassifier:
    """Classify market regime based on ADX and ATR percentile."""
    
    REGIMES = [
        'trending_up',
        'trending_down',
        'ranging_tight',
        'ranging_wide',
        'high_volatility'
    ]
    
    def __init__(self, atr_lookback: int = 50):
        self.atr_lookback = atr_lookback
        self.atr_history: List[float] = []
        
    def calculate_adx(self, candles: List[dict], period: int = 14) -> float:
        """Calculate ADX from candle data."""
        if len(candles) < period + 1:
            return 0.0
        
        highs = [c['high'] for c in candles[-period*2:]]
        lows = [c['low'] for c in candles[-period*2:]]
        closes = [c['close'] for c in candles[-period*2:]]
        
        # Calculate +DM and -DM
        plus_dm = []
        minus_dm = []
        tr = []
        
        for i in range(1, len(closes)):
            high_diff = highs[i] - highs[i-1]
            low_diff = lows[i-1] - lows[i]
            
            plus_dm.append(max(high_diff, 0) if high_diff > low_diff else 0)
            minus_dm.append(max(low_diff, 0) if low_diff > high_diff else 0)
            
            tr.append(max(
                highs[i] - lows[i],
                abs(highs[i] - closes[i-1]),
                abs(lows[i] - closes[i-1])
            ))
        
        # Smooth with Wilder's method
        atr = np.mean(tr[-period:])
        plus_di = 100 * np.mean(plus_dm[-period:]) / atr if atr > 0 else 0
        minus_di = 100 * np.mean(minus_dm[-period:]) / atr if atr > 0 else 0
        
        dx = 100 * abs(plus_di - minus_di) / (plus_di + minus_di) if (plus_di + minus_di) > 0 else 0
        
        return dx
    
    def calculate_atr(self, candles: List[dict], period: int = 14) -> float:
        """Calculate Average True Range."""
        if len(candles) < period + 1:
            return 0.0
        
        tr_values = []
        for i in range(1, len(candles)):
            tr = max(
                candles[i]['high'] - candles[i]['low'],
                abs(candles[i]['high'] - candles[i-1]['close']),
                abs(candles[i]['low'] - candles[i-1]['close'])
            )
            tr_values.append(tr)
        
        return np.mean(tr_values[-period:])
    
    def calculate_atr_percentile(self, current_atr: float) -> float:
        """Calculate ATR percentile from history."""
        if not self.atr_history:
            return 0.5
        
        return sum(1 for atr in self.atr_history if atr < current_atr) / len(self.atr_history)
    
    def classify(self, candles: List[dict]) -> Dict[str, any]:
        """Classify market regime."""
        if len(candles) < 50:
            return {'regime': 'unknown', 'adx': 0, 'atr': 0, 'atr_percentile': 0}
        
        adx = self.calculate_adx(candles)
        atr = self.calculate_atr(candles)
        
        # Update ATR history
        self.atr_history.append(atr)
        if len(self.atr_history) > self.atr_lookback:
            self.atr_history.pop(0)
        
        atr_pct = self.calculate_atr_percentile(atr)
        
        # Regime classification logic
        if adx > 25:
            # Trending regime
            if candles[-1]['close'] > candles[-20]['close']:
                regime = 'trending_up'
            else:
                regime = 'trending_down'
        elif adx < 20:
            # Ranging regime
            if atr_pct > 0.7:
                regime = 'ranging_wide'
            else:
                regime = 'ranging_tight'
        else:
            # Transition zone
            if atr_pct > 0.8:
                regime = 'high_volatility'
            else:
                regime = 'ranging_tight'
        
        result = {
            'regime': regime,
            'adx': round(adx, 2),
            'atr': round(atr, 2),
            'atr_percentile': round(atr_pct, 2),
            'strategy_filter': self._get_strategy_filter(regime)
        }
        
        logger.info(f"Regime classified: {regime} (ADX: {adx:.1f}, ATR%: {atr_pct:.2f})")
        return result
    
    def _get_strategy_filter(self, regime: str) -> dict:
        """Get strategy filter based on regime."""
        filters = {
            'trending_up': {
                'allowed_strategies': ['ema_trend', 'funding_arb'],
                'position_size_multiplier': 1.0
            },
            'trending_down': {
                'allowed_strategies': ['ema_trend', 'funding_arb'],
                'position_size_multiplier': 1.0
            },
            'ranging_tight': {
                'allowed_strategies': ['rsi_divergence', 'vwap_reversion', 'funding_arb'],
                'position_size_multiplier': 0.5
            },
            'ranging_wide': {
                'allowed_strategies': ['rsi_divergence', 'vwap_reversion'],
                'position_size_multiplier': 0.75
            },
            'high_volatility': {
                'allowed_strategies': ['funding_arb'],
                'position_size_multiplier': 0.5
            }
        }
        return filters.get(regime, filters['ranging_tight'])
