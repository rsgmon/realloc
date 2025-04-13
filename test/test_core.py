import pytest
from trade_generator.core import Account, TradeAccountMatrix, ScaledPortfolio, allocate_trades, split_trades

@pytest.fixture
def sample_accounts():
    return [
        Account("Taxable", "A001", 10000.0, {"AAPL": 10, "GOOG": 5}, {}),
        Account("IRA", "A002", 5000.0, {"AAPL": 2, "MSFT": 3}, {})
    ]

def test_allocate_trades():
    current = {"AAPL": 5, "GOOG": 3}
    target = {"AAPL": 10, "GOOG": 2}
    trades = allocate_trades(current, target)
    assert trades == {"AAPL": 5, "GOOG": -1}

def test_split_trades():
    current = {"AAPL": 5, "GOOG": 3}
    target = {"AAPL": 10, "GOOG": 2}
    trades = split_trades(current, target)
    assert trades == {"buy": {"AAPL": 5}, "sell": {"GOOG": 1}}

def test_trade_account_matrix_update(sample_accounts):
    prices = {"AAPL": 100, "GOOG": 200}
    trades = {"A001": {"AAPL": 2}, "A002": {"GOOG": -1}}
    tam = TradeAccountMatrix(sample_accounts, prices)
    tam.update(trades)
    assert tam.accounts["A001"].positions["AAPL"] == 12
    assert tam.accounts["A002"].positions["GOOG"] == -1 or "GOOG" not in tam.accounts["A002"].positions

def test_scaled_portfolio(sample_accounts):
    model = {"AAPL": 0.6, "GOOG": 0.4}
    prices = {"AAPL": 100, "GOOG": 200}
    portfolio = ScaledPortfolio(sample_accounts, model)
    trades = portfolio.generate_scaled_cash_constrained_trades(prices)
    assert isinstance(trades, dict)
