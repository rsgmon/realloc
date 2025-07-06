import pytest
from realloc.plugins.core.base import TradeInfo

@pytest.fixture
def basic_trade():
    return TradeInfo(
        symbol="AAPL",
        quantity=100,
        price=150.0,
        minimum_value=1000,
        current_position=500,
        account_balance=100000.0
    )

@pytest.fixture
def small_trade():
    return TradeInfo(
        symbol="AAPL",
        quantity=1,
        price=150.0,
        minimum_value=1000,
        current_position=0,
        account_balance=100000.0
    )