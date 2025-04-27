import pytest
from core import (
    Account,
    TradeAccountMatrix,
    allocate_trades,
)


@pytest.fixture
def sample_accounts():
    return [
        Account(label="IRA", account_number="A1", cash=1000, positions={"AAPL": 5}, targets={}),
        Account(label="Taxable", account_number="A2", cash=500, positions={"GOOG": 2}, targets={}),
    ]


@pytest.fixture
def sample_prices():
    return {"AAPL": 100, "GOOG": 200}


@pytest.fixture
def sample_portfolio_trades():
    return {"AAPL": 5, "GOOG": -2}


@pytest.fixture
def tam(sample_accounts, sample_prices, sample_portfolio_trades):
    return TradeAccountMatrix(sample_accounts, sample_prices, sample_portfolio_trades)


# --------------------------------------------------------
# 🔥 Existing Improved
# --------------------------------------------------------

@pytest.mark.parametrize(
    "initial_positions, trades, expected_positions",
    [
        ({"AAPL": 5}, {"AAPL": 2}, {"AAPL": 7}),
        ({"AAPL": 5}, {"AAPL": -3}, {"AAPL": 2}),
        ({}, {"AAPL": 4}, {"AAPL": 4}),
    ],
)
def test_trade_account_matrix_update(initial_positions, trades, expected_positions):
    account = Account("Test", "A1", 1000, initial_positions, {})
    tam = TradeAccountMatrix(accounts=[account], prices={"AAPL": 100})
    tam.update({"A1": trades})
    assert account.positions == expected_positions


def test_trade_account_matrix_prevents_negative_position():
    acc = Account("Test", "001", 1000.0, {"AAPL": 5}, {}, enforce_no_negative_positions=True)
    tam = TradeAccountMatrix([acc], {"AAPL": 100.0})
    trades = {"001": {"AAPL": -10}}
    with pytest.raises(ValueError):
        tam.update(trades)


def test_trade_account_matrix_allows_valid_trades():
    acc = Account("Test", "001", 1000.0, {"AAPL": 5}, {}, enforce_no_negative_positions=True)
    tam = TradeAccountMatrix([acc], {"AAPL": 100.0})
    trades = {"001": {"AAPL": -2}}
    tam.update(trades)
    assert acc.positions["AAPL"] == 3


def test_trade_matrix_blocks_negative_position_update():
    acc = Account("T", "1", 1000, {"AAPL": 1}, {}, enforce_no_negative_positions=True)
    tam = TradeAccountMatrix([acc], {"AAPL": 100})
    with pytest.raises(ValueError):
        tam.update({"1": {"AAPL": -2}})


# --------------------------------------------------------
# ✨ New Coverage
# --------------------------------------------------------

def test_trade_account_matrix_to_dict_and_from_dict(tam, sample_accounts):
    serialized = tam.to_dict()
    deserialized = TradeAccountMatrix.from_dict(serialized, sample_accounts)

    assert isinstance(serialized, dict)
    assert isinstance(deserialized, TradeAccountMatrix)
    assert deserialized.cash_matrix == tam.cash_matrix
    assert deserialized.model_only == tam.model_only
    assert deserialized.prices == tam.prices
    assert deserialized.portfolio_trades == tam.portfolio_trades


def test_trade_account_matrix_model_only_detection():
    accounts = [Account("ModelOnly", "M001", 0, {}, {})]
    prices = {"FAKE": 100}
    portfolio_trades = {"FAKE": 10}  # Symbol not held by any account
    tam = TradeAccountMatrix(accounts, prices, portfolio_trades)

    assert tam.model_only == {"FAKE": 10}


def test_trade_account_matrix_update_portfolio_trades(sample_accounts, sample_prices):
    tam = TradeAccountMatrix(sample_accounts, sample_prices)
    target_shares = {"AAPL": 10, "GOOG": 3}  # Slightly different than current
    tam.update_portfolio_trades(target_shares)

    assert isinstance(tam.portfolio_trades, dict)
    assert "AAPL" in tam.portfolio_trades
    assert "GOOG" in tam.portfolio_trades


def test_trade_account_matrix_empty_update_does_nothing():
    acc = Account("Test", "001", 1000.0, {"AAPL": 5}, {}, enforce_no_negative_positions=True)
    tam = TradeAccountMatrix([acc], {"AAPL": 100.0})
    tam.update({})
    assert acc.positions["AAPL"] == 5
    assert tam.cash_matrix["001"] == 1000.0


def test_trade_account_matrix_handles_missing_price_gracefully():
    acc = Account("Test", "001", 1000.0, {"AAPL": 5}, {}, enforce_no_negative_positions=False)
    tam = TradeAccountMatrix([acc], {})  # Empty prices dict
    tam.update({"001": {"AAPL": 1}})
    assert acc.positions["AAPL"] == 6
    # Cash won't change because price was missing (defaults to 0)

