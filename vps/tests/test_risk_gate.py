import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from risk_gate import RiskGate

# Initialize risk gate with spec parameters
@pytest.fixture
def gate():
    return RiskGate(
        max_risk_pct=2.0,
        max_positions=4,
        soft_drawdown_pct=3.0,
        hard_drawdown_pct=6.0,
        max_leverage=5
    )

def test_trade_exceeds_max_risk_rejected(gate):
    """Trade risking 3% of account must be rejected (max is 2%)"""
    result = gate.validate_order(
        account_equity=10000,
        order_risk_amount=300,  # 3% of 10000
        current_positions=0,
        daily_drawdown_pct=0.0,
        leverage=3
    )
    assert result.approved is False
    assert "risk" in result.reason.lower()

def test_trade_within_max_risk_approved(gate):
    """Trade risking 2% of account must be approved"""
    result = gate.validate_order(
        account_equity=10000,
        order_risk_amount=200,  # 2% of 10000
        current_positions=0,
        daily_drawdown_pct=0.0,
        leverage=3
    )
    assert result.approved is True

def test_fifth_position_rejected(gate):
    """Opening a 5th position must be rejected (max is 4)"""
    result = gate.validate_order(
        account_equity=10000,
        order_risk_amount=200,
        current_positions=4,  # already at max
        daily_drawdown_pct=0.0,
        leverage=3
    )
    assert result.approved is False
    assert "position" in result.reason.lower()

def test_hard_drawdown_triggers_halt(gate):
    """7% daily drawdown must trigger hard halt"""
    result = gate.validate_order(
        account_equity=10000,
        order_risk_amount=200,
        current_positions=0,
        daily_drawdown_pct=7.0,  # exceeds 6% hard limit
        leverage=3
    )
    assert result.approved is False
    assert result.halt is True

def test_soft_drawdown_reduces_size(gate):
    """3.5% drawdown must trigger soft warning (not halt)"""
    result = gate.validate_order(
        account_equity=10000,
        order_risk_amount=200,
        current_positions=0,
        daily_drawdown_pct=3.5,  # past 3% soft limit
        leverage=3
    )
    assert result.soft_warning is True
    assert result.halt is False

def test_leverage_exceeds_max_rejected(gate):
    """Order with 6x leverage must be rejected (max is 5x)"""
    result = gate.validate_order(
        account_equity=10000,
        order_risk_amount=200,
        current_positions=0,
        daily_drawdown_pct=0.0,
        leverage=6  # exceeds max of 5
    )
    assert result.approved is False
    assert "leverage" in result.reason.lower()

def test_max_leverage_approved(gate):
    """Order with exactly 5x leverage must be approved"""
    result = gate.validate_order(
        account_equity=10000,
        order_risk_amount=200,
        current_positions=0,
        daily_drawdown_pct=0.0,
        leverage=5
    )
    assert result.approved is True
