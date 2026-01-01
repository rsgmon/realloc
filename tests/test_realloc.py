import pytest
from realloc import (
    Account,
    ScaledPortfolio,
    compute_portfolio_trades,
    split_trades,
    PortfolioModel,
    select_account_for_buy_trade,
    calculate_buy_amounts,
    calculate_sell_amounts,
)


@pytest.fixture
def sample_portfoliomodel():
    return PortfolioModel("SampleModel", {"AAPL": 0.6, "GOOG": 0.4})


@pytest.fixture
def sample_accounts():
    return [
        Account("Taxable", "A001", 10000.0, {"AAPL": 10, "GOOG": 5}),
        Account("IRA", "A002", 5000.0, {"AAPL": 2, "MSFT": 3}),
    ]


@pytest.mark.parametrize(
    "current, target, expected",
    [
        ({"AAPL": 5}, {"AAPL": 10}, {"AAPL": 5}),
        ({"AAPL": 10}, {"AAPL": 5}, {"AAPL": -5}),
        ({"AAPL": 0}, {"AAPL": 0}, {"AAPL": 0}),
        ({}, {"AAPL": 5}, {"AAPL": 5}),
        ({"AAPL": 5, "GOOG": 2}, {"AAPL": 5, "GOOG": 2}, {"AAPL": 0, "GOOG": 0}),
    ],
)
def test_allocate_trades(current, target, expected):
    assert compute_portfolio_trades(current, target) == expected


@pytest.mark.parametrize(
    "current, target, expected_buy, expected_sell",
    [
        ({"AAPL": 5}, {"AAPL": 10}, {"AAPL": 5}, {}),
        ({"AAPL": 10}, {"AAPL": 5}, {}, {"AAPL": 5}),
        ({"AAPL": 5, "GOOG": 2}, {"AAPL": 10, "GOOG": 0}, {"AAPL": 5}, {"GOOG": 2}),
    ],
)
def test_split_trades(current, target, expected_buy, expected_sell):
    result = split_trades(current, target)
    assert result["buy"] == expected_buy
    assert result["sell"] == expected_sell


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
            enforce_no_negative_positions=True,
        )


def test_allocate_trades_handles_empty_input():
    assert compute_portfolio_trades({}, {}) == {}


def test_split_trades_with_zero_positions():
    current = {"AAPL": 0}
    target = {"AAPL": 0}
    result = split_trades(current, target)
    assert result == {"buy": {}, "sell": {}}


def test_calculate_buy_and_sell_with_missing_targets():
    current = [100, 50]
    targets = [None, 80]
    buys = calculate_buy_amounts(current, targets)
    sells = calculate_sell_amounts(current, targets)
    assert buys == [0, 30]
    assert sells == [100, 0]


def test_account_rejects_negative_positions_when_enforced():
    with pytest.raises(ValueError):
        Account(
            "Test", "123", 1000, {"AAPL": -5}, enforce_no_negative_positions=True
        )


def test_portfolio_model_rejects_negative_weights():
    with pytest.raises(ValueError):
        PortfolioModel("LongOnly", {"AAPL": -0.5})


def test_selector_prioritizes_holder_full():
    acc1 = Account(
        "A",
        "1",
        1000,
        {"GOOG": 0},
        {},
    )
    acc2 = Account(
        "B",
        "2",
        3000,
        {"GOOG": 10},
        {},
    )
    prices = {"GOOG": 100}
    cash = {"1": 1000, "2": 3000}
    result = select_account_for_buy_trade("GOOG", 10, [acc1, acc2], prices, cash)
    assert result == "2"


def test_selector_prefers_holder_partial_over_nonholder():
    acc1 = Account(
        "A",
        "1",
        1000,
        {"GOOG": 5},
        {},
    )
    acc2 = Account(
        "B",
        "2",
        3000,
        {},
        {},
    )
    prices = {"GOOG": 100}
    cash = {"1": 1000, "2": 3000}
    result = select_account_for_buy_trade("GOOG", 15, [acc1, acc2], prices, cash)
    assert result == "1"


def test_selector_fallbacks_to_nonholder_when_no_holder_can_buy():
    acc1 = Account(
        "A",
        "1",
        0,
        {"GOOG": 5},
        {},
    )
    acc2 = Account(
        "B",
        "2",
        1000,
        {},
        {},
    )
    prices = {"GOOG": 100}
    cash = {"1": 0, "2": 1000}
    result = select_account_for_buy_trade("GOOG", 5, [acc1, acc2], prices, cash)
    assert result == "2"


@pytest.mark.parametrize(
    "current,target,expected",
    [
        ([100], [120], [20]),
        ([50], [None], [0]),
        ([80], [80], [0]),
    ],
)
def test_calculate_buy_amounts_cases(current, target, expected):
    assert calculate_buy_amounts(current, target) == expected


@pytest.mark.parametrize(
    "current,target,expected",
    [
        ([120], [100], [20]),
        ([50], [None], [50]),
        ([80], [80], [0]),
    ],
)
def test_calculate_sell_amounts_cases(current, target, expected):
    assert calculate_sell_amounts(current, target) == expected


@pytest.mark.parametrize(
    "accounts,cash,expected",
    [
        # Full holder exists
        (
            [
                Account("A", "1", 1000, {"GOOG": 0}),
                Account("B", "2", 3000, {"GOOG": 10}),
            ],
            {"1": 1000, "2": 3000},
            "2",
        ),
        # Partial holder vs full non-holder
        (
            [
                Account("A", "1", 1000, {"GOOG": 5}),
                Account("B", "2", 3000, {}),
            ],
            {"1": 1000, "2": 3000},
            "1",
        ),
        # No holder, fallback to non-holder
        (
            [
                Account("A", "1", 0, {"GOOG": 5}),
                Account("B", "2", 1000, {}),
            ],
            {"1": 0, "2": 1000},
            "2",
        ),
    ],
)
def test_parametrized_selector_behavior(accounts, cash, expected):
    prices = {"GOOG": 100}
    result = select_account_for_buy_trade("GOOG", 5, accounts, prices, cash)
    assert result == expected
