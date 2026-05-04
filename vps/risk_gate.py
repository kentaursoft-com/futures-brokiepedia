from dataclasses import dataclass

@dataclass
class RiskResult:
    approved: bool
    reason: str = ""
    halt: bool = False
    soft_warning: bool = False

class RiskGate:
    def __init__(self, max_risk_pct: float, max_positions: int,
                 soft_drawdown_pct: float, hard_drawdown_pct: float,
                 max_leverage: int):
        self.max_risk_pct = max_risk_pct
        self.max_positions = max_positions
        self.soft_drawdown_pct = soft_drawdown_pct
        self.hard_drawdown_pct = hard_drawdown_pct
        self.max_leverage = max_leverage

    def validate_order(self, account_equity: float,
                       order_risk_amount: float,
                       current_positions: int,
                       daily_drawdown_pct: float,
                       leverage: int) -> RiskResult:

        # Hard drawdown halt
        if daily_drawdown_pct >= self.hard_drawdown_pct:
            return RiskResult(
                approved=False,
                reason=f"Hard drawdown limit {self.hard_drawdown_pct}% "
                       f"reached — trading halted",
                halt=True
            )

        # Max position check
        if current_positions >= self.max_positions:
            return RiskResult(
                approved=False,
                reason=f"Max concurrent positions "
                       f"({self.max_positions}) reached"
            )

        # Leverage check
        if leverage > self.max_leverage:
            return RiskResult(
                approved=False,
                reason=f"Leverage {leverage}x exceeds "
                       f"max {self.max_leverage}x"
            )

        # Risk per trade check
        risk_pct = (order_risk_amount / account_equity) * 100
        if risk_pct > self.max_risk_pct:
            return RiskResult(
                approved=False,
                reason=f"Order risk {risk_pct:.1f}% exceeds "
                       f"max {self.max_risk_pct}%"
            )

        # Soft drawdown warning
        soft_warning = daily_drawdown_pct >= self.soft_drawdown_pct

        return RiskResult(
            approved=True,
            soft_warning=soft_warning,
            reason="soft drawdown warning" if soft_warning else ""
        )
