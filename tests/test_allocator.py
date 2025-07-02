import pytest
from realloc.accounts import Account
from realloc.models import PortfolioModel
from realloc.allocator import PortfolioAllocator


@pytest.fixture
def sample_accounts():
    return [
        Account(
            label="IRA",
            account_number="A1",
            cash=1000,
            positions={"AAPL": 5},
            targets={},
        ),
        Account(
            label="Taxable",
            account_number="A2",
            cash=2000,
            positions={"GOOG": 3},
            targets={},
        ),
    ]


@pytest.fixture
def sample_model():
    return PortfolioModel(name="Balanced", targets={"AAPL": 0.5, "GOOG": 0.5})


@pytest.fixture
def sample_prices():
    return {"AAPL": 100, "GOOG": 200}


@pytest.fixture
def allocator(sample_accounts, sample_model, sample_prices):
    return PortfolioAllocator(sample_accounts, sample_model, sample_prices)


# --------------------------------------------------------
# 🔥 Tests
# --------------------------------------------------------


def test_portfolio_allocator_initialization(allocator):
    assert allocator.accounts is not None
    assert allocator.model is not None
    assert allocator.prices is not None
    assert allocator.selector is None


def test_compute_portfolio_trades(allocator):
    trades = allocator.compute_portfolio_trades()
    assert isinstance(trades, dict)
    assert all(isinstance(k, str) and isinstance(v, int) for k, v in trades.items())


def test_rebalance_generates_trades(allocator):
    trades = allocator.rebalance()
    assert isinstance(trades, dict)
    assert allocator.tam is not None
    assert allocator.tam.cash_matrix is not None
    assert isinstance(allocator.get_cash_matrix(), dict)


def test_get_account_positions(allocator):
    positions = allocator.get_account_positions()
    assert isinstance(positions, dict)
    assert all(isinstance(k, str) and isinstance(v, dict) for k, v in positions.items())


def test_portfolio_trades_property(allocator):
    # Initially None
    assert allocator.portfolio_trades is None
    # After rebalance
    allocator.rebalance()
    assert isinstance(allocator.portfolio_trades, dict)


# --------------------------------------------------------
# 🛠 Bonus: Negative and Edge Cases
# --------------------------------------------------------


def test_rebalance_without_prices_fails(sample_accounts, sample_model):
    with pytest.raises(KeyError):
        bad_prices = {}  # empty prices
        allocator = PortfolioAllocator(sample_accounts, sample_model, bad_prices)
        allocator.rebalance()


def test_rebalance_with_missing_symbols(sample_accounts, sample_prices):
    bad_model = PortfolioModel(name="UnknownSymbols", targets={"XYZ": 1.0})
    allocator = PortfolioAllocator(sample_accounts, bad_model, sample_prices)
    with pytest.raises(KeyError):
        allocator.rebalance()
