import pytest
from realloc.plugins.validators.minimum_value import MinimumValueValidator
from realloc.plugins.core.base import TradeInfo

def test_minimum_value_validator_name():
    validator = MinimumValueValidator()
    assert validator.name == "minimum_value_validator"

def test_minimum_value_validator_accepts_valid_trade(basic_trade):
    validator = MinimumValueValidator()
    is_valid, reason = validator.validate(basic_trade)
    assert is_valid
    assert reason == ""

def test_minimum_value_validator_rejects_small_trade(small_trade):
    validator = MinimumValueValidator()
    is_valid, reason = validator.validate(small_trade)
    assert not is_valid
    assert "below minimum" in reason

def test_minimum_value_validator_rejects_zero_quantity():
    trade = TradeInfo(
        symbol="AAPL",
        quantity=0,
        price=150.0,
        minimum_value=1000
    )
    validator = MinimumValueValidator()
    is_valid, reason = validator.validate(trade)
    assert not is_valid
    assert reason == "Zero quantity trade"

def test_minimum_value_validator_handles_zero_minimum():
    trade = TradeInfo(
        symbol="AAPL",
        quantity=1,
        price=150.0,
        minimum_value=0
    )
    validator = MinimumValueValidator()
    is_valid, reason = validator.validate(trade)
    assert is_valid
    assert reason == ""

def test_minimum_value_validator_uses_absolute_value():
    trade = TradeInfo(
        symbol="AAPL",
        quantity=-100,  # Selling
        price=150.0,
        minimum_value=1000
    )
    validator = MinimumValueValidator()
    is_valid, reason = validator.validate(trade)
    assert is_valid
    assert reason == ""