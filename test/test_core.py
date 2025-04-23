import pytest
from trade_generator import (Account, TradeAccountMatrix, ScaledPortfolio,
                                  allocate_trades, split_trades, PortfolioModel,
                                  select_account_for_buy_trade, select_account_for_sell_trade)

@pytest.fixture
def sample_portfoliomodel():
    return PortfolioModel("SampleModel", {"AAPL": 0.6, "GOOG": 0.4})

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
    prices = {"AAPL": 100, "GOOG": 200, "MSFT": 300}
    trades = {"A001": {"AAPL": 2}, "A002": {"GOOG": -1}}
    tam = TradeAccountMatrix(sample_accounts, prices)
    tam.update(trades)
    assert tam.accounts["A001"].positions["AAPL"] == 12
    assert tam.accounts["A002"].positions["GOOG"] == -1 or "GOOG" not in tam.accounts["A002"].positions

def test_scaled_portfolio(sample_accounts, sample_portfoliomodel):
    prices = {"AAPL": 100, "GOOG": 200}
    normalized_model = sample_portfoliomodel.normalize()
    portfolio = ScaledPortfolio(sample_accounts, normalized_model)
    trades = portfolio.generate_scaled_cash_constrained_trades(prices)
    assert isinstance(trades, dict)

def test_portfolio_model_init():
    model = PortfolioModel("Growth")
    assert model.name == "Growth"
    assert model.targets == {}

def test_add_update_get_target():
    model = PortfolioModel("Test")
    model.add_target("AAPL", 0.4)
    assert model.get_target("AAPL") == 0.4
    model.update_target("AAPL", 0.5)
    assert model.get_target("AAPL") == 0.5

def test_remove_target():
    model = PortfolioModel("Test", {"AAPL": 0.4, "GOOG": 0.6})
    model.remove_target("AAPL")
    assert "AAPL" not in model.targets

def test_normalize_targets():
    model = PortfolioModel("Test", {"AAPL": 2, "GOOG": 3})
    normalized = model.normalize()
    assert pytest.approx(normalized["AAPL"], 0.01) == 0.4
    assert pytest.approx(normalized["GOOG"], 0.01) == 0.6

def test_portfolio_model_serialization():
    original = PortfolioModel("Balanced", {"AAPL": 0.5, "GOOG": 0.5})
    data = original.to_dict()
    restored = PortfolioModel.from_dict(data)
    assert restored.name == original.name
    assert restored.targets == original.targets

def test_account_disallows_negative_starting_position():
    with pytest.raises(ValueError):
        Account(
            label="Test",
            account_number="001",
            cash=1000.0,
            positions={"AAPL": -10},
            targets={},
            enforce_no_negative_positions=True
        )

def test_trade_account_matrix_prevents_negative_position():
    acc = Account(
        label="Test",
        account_number="001",
        cash=1000.0,
        positions={"AAPL": 5},
        targets={},
        enforce_no_negative_positions=True
    )
    prices = {"AAPL": 100.0}
    tam = TradeAccountMatrix([acc], prices)
    trades = {"001": {"AAPL": -10}}
    with pytest.raises(ValueError):
        tam.update(trades)

def test_trade_account_matrix_allows_valid_trades():
    acc = Account(
        label="Test",
        account_number="001",
        cash=1000.0,
        positions={"AAPL": 5},
        targets={},
        enforce_no_negative_positions=True
    )
    prices = {"AAPL": 100.0}
    tam = TradeAccountMatrix([acc], prices)
    trades = {"001": {"AAPL": -2}}
    tam.update(trades)
    assert acc.positions["AAPL"] == 3

@pytest.fixture
def accounts():
    return [
        Account("A", "A001", 1000, {"AAPL": 5}, {}),
        Account("B", "A002", 2000, {"GOOG": 10}, {})
    ]

def test_select_account_for_buy_trade_existing_holder(accounts):
    prices = {"AAPL": 100, "GOOG": 200}
    selected = select_account_for_buy_trade("AAPL", 3, accounts, prices)
    assert selected == "A001"

def test_select_account_for_buy_trade_fallback_to_cash(accounts):
    prices = {"MSFT": 100}
    selected = select_account_for_buy_trade("MSFT", 5, accounts, prices)
    assert selected == "A002"  # B has more cash

def test_select_account_for_sell_trade_full_sell(accounts):
    selected = select_account_for_sell_trade("GOOG", 5, accounts)
    assert selected == "A002"

def test_select_account_for_sell_trade_partial(accounts):
    selected = select_account_for_sell_trade("AAPL", 10, accounts)
    assert selected == "A001"  # Only one with AAPL, partial

def test_select_account_for_sell_trade_none():
    accounts = [Account("C", "A003", 500, {}, {})]
    selected = select_account_for_sell_trade("TSLA", 1, accounts)
    assert selected is None
