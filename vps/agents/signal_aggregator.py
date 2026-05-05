"""Signal Aggregator - Combines all agent signals into a unified trading signal."""

from typing import Dict, List, Any
from datetime import datetime, timezone


class SignalAggregator:
    """Aggregates signals from multiple agents into a unified decision."""
    
    def __init__(self):
        self.weights = {
            "Trend": 0.25,
            "Momentum": 0.20,
            "Volatility": 0.15,
            "Sentiment": 0.15,
            "Funding": 0.10,
            "Risk": 0.15,
        }
        
    def aggregate(self, signals: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Combine all signals into a unified trading decision."""
        if not signals:
            return {
                "direction": "flat",
                "confidence": 0.0,
                "reason": "No signals available",
                "agents_reporting": 0,
            }
        
        # Direction mapping
        direction_scores = {"long": 0.0, "short": 0.0, "flat": 0.0}
        total_weight = 0.0
        
        active_signals = []
        risk_clear = True
        
        for signal in signals:
            dept = signal.get("department", "Unknown")
            direction = signal.get("direction", "flat")
            confidence = signal.get("confidence", 0.0)
            weight = self.weights.get(dept, 0.1)
            
            # Risk agent has veto power
            if dept == "Risk":
                if direction == "flat" and confidence > 0.7:
                    risk_clear = False
                continue
            
            # Skip low confidence
            if confidence < 0.3:
                continue
            
            # Score direction
            if direction == "long":
                direction_scores["long"] += confidence * weight
            elif direction == "short":
                direction_scores["short"] += confidence * weight
            else:
                direction_scores["flat"] += confidence * weight
            
            total_weight += weight
            active_signals.append(signal)
        
        # Check risk veto
        if not risk_clear:
            return {
                "direction": "flat",
                "confidence": 0.95,
                "reason": "RISK VETO - Risk conditions too elevated",
                "agents_reporting": len(active_signals),
                "signal_breakdown": signals,
            }
        
        # Determine consensus
        if direction_scores["long"] > direction_scores["short"] * 1.5:
            direction = "long"
            confidence = min(0.95, direction_scores["long"] / max(total_weight, 0.001))
            reason = f"Strong long consensus ({len(active_signals)} agents agree)"
        elif direction_scores["short"] > direction_scores["long"] * 1.5:
            direction = "short"
            confidence = min(0.95, direction_scores["short"] / max(total_weight, 0.001))
            reason = f"Strong short consensus ({len(active_signals)} agents agree)"
        elif direction_scores["long"] > direction_scores["short"]:
            direction = "long"
            confidence = min(0.75, direction_scores["long"] / max(total_weight, 0.001))
            reason = f"Weak long bias ({len(active_signals)} agents)"
        elif direction_scores["short"] > direction_scores["long"]:
            direction = "short"
            confidence = min(0.75, direction_scores["short"] / max(total_weight, 0.001))
            reason = f"Weak short bias ({len(active_signals)} agents)"
        else:
            direction = "flat"
            confidence = 0.5
            reason = "No clear consensus"
        
        return {
            "direction": direction,
            "confidence": round(confidence, 2),
            "reason": reason,
            "agents_reporting": len(active_signals),
            "signal_breakdown": signals,
            "aggregated_scores": {
                "long_score": round(direction_scores["long"], 3),
                "short_score": round(direction_scores["short"], 3),
                "flat_score": round(direction_scores["flat"], 3),
            },
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
