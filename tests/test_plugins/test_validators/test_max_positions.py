import pytest
from realloc.plugins.validators.max_position import MaxPositionValidator
from realloc.plugins.core.base import TradeInfo

@pytest.fixture
def max_position_validator():
    return MaxPositionValidator(max_position=1000)

def test_max_position_validator_name(max_position_validator):
    assert max_position_validator.name == "max_position"

def test_max_position_validator_accepts_within_limit(max_position_validator, basic_trade):
    is_valid, reason = max_position_validator.validate(basic_trade)
    assert is_valid
    assert reason == ""

def test_max_position_validator_rejects_exceeding_position(max_position_validator):
    trade = TradeInfo(
        symbol="AAPL",
        quantity=600,  # Would result in position of 1100
        price=150.0,
        current_position=500
    )
    is_valid, reason = max_position_validator.validate(trade)
    assert not is_valid
    assert "exceed max position" in reason

def test_max_position_validator_considers_absolute_value(max_position_validator):
    trade = TradeInfo(
        symbol="AAPL",
        quantity=-1200,  # Would result in position of -1200
        price=150.0,
        current_position=0
    )
    is_valid, reason = max_position_validator.validate(trade)
    assert not is_valid
    assert "exceed max position" in reason

def test_max_position_validator_handles_missing_current_position(max_position_validator):
    trade = TradeInfo(
        symbol="AAPL",
        quantity=100,
        price=150.0,
        current_position=None
    )
    is_valid, reason = max_position_validator.validate(trade)
    assert is_valid
    assert reason == ""