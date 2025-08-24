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
        ),
        Account(
            label="Taxable",
            account_number="A2",
            cash=2000,
            positions={"GOOG": 3},
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


def test_portfolio_allocator_initialization(allocator):
    assert allocator.accounts is not None
    assert allocator.model is not None
    assert allocator.prices is not None
    assert allocator.selector is None


def test_compute_account_values(allocator):
    values = allocator.compute_account_values()
    assert isinstance(values, dict)
    assert "A1" in values
    assert "A2" in values
    # Account A1: $1000 cash + (5 * $100 AAPL) = $1500
    assert values["A1"] == 1500
    # Account A2: $2000 cash + (3 * $200 GOOG) = $2600
    assert values["A2"] == 2600


def test_total_portfolio_value(allocator):
    # Total should be sum of both accounts: $1500 + $2600 = $4100
    assert allocator.total_portfolio_value == 4100


def test_get_current_allocations(allocator):
    current = allocator.get_current_allocations()
    assert isinstance(current, dict)
    assert len(current) == 2

    # Account A1 allocations
    assert "AAPL" in current["A1"]
    assert "CASH" in current["A1"]
    assert pytest.approx(current["A1"]["AAPL"]) == (500 / 1500)  # $500 AAPL / $1500 total
    assert pytest.approx(current["A1"]["CASH"]) == (1000 / 1500)  # $1000 cash / $1500 total

    # Account A2 allocations
    assert "GOOG" in current["A2"]
    assert "CASH" in current["A2"]
    assert pytest.approx(current["A2"]["GOOG"]) == (600 / 2600)  # $600 GOOG / $2600 total
    assert pytest.approx(current["A2"]["CASH"]) == (2000 / 2600)  # $2000 cash / $2600 total


def test_compute_target_allocations(allocator):
    target = allocator.compute_target_allocations()
    assert isinstance(target, dict)
    assert len(target) == 2

    # Both accounts should have same target allocations
    for acc_id in ["A1", "A2"]:
        assert "AAPL" in target[acc_id]
        assert "GOOG" in target[acc_id]
        assert target[acc_id]["AAPL"] == 0.5
        assert target[acc_id]["GOOG"] == 0.5


def test_compute_target_positions(allocator):
    positions = allocator.compute_target_positions()
    assert isinstance(positions, dict)
    assert len(positions) == 2

    # Account A1 ($1500 total)
    assert pytest.approx(positions["A1"]["AAPL"]) == (1500 * 0.5) / 100  # $750 / $100 per share
    assert pytest.approx(positions["A1"]["GOOG"]) == (1500 * 0.5) / 200  # $750 / $200 per share

    # Account A2 ($2600 total)
    assert pytest.approx(positions["A2"]["AAPL"]) == (2600 * 0.5) / 100  # $1300 / $100 per share
    assert pytest.approx(positions["A2"]["GOOG"]) == (2600 * 0.5) / 200  # $1300 / $200 per share


def test_get_allocation_differences(allocator):
    diffs = allocator.get_allocation_differences()
    assert isinstance(diffs, dict)
    assert len(diffs) == 2

    for acc_id in ["A1", "A2"]:
        assert "AAPL" in diffs[acc_id]
        assert "GOOG" in diffs[acc_id]
        assert isinstance(diffs[acc_id]["AAPL"], tuple)
        assert isinstance(diffs[acc_id]["GOOG"], tuple)
        assert len(diffs[acc_id]["AAPL"]) == 2
        assert len(diffs[acc_id]["GOOG"]) == 2


def test_get_account_positions(allocator):
    positions = allocator.get_account_positions()
    assert isinstance(positions, dict)
    assert positions["A1"] == {"AAPL": 5}
    assert positions["A2"] == {"GOOG": 3}


def test_allocator_with_empty_prices(sample_accounts, sample_model):
    with pytest.raises(KeyError):
        allocator = PortfolioAllocator(sample_accounts, sample_model, {})
        allocator.compute_account_values()


def test_allocator_with_missing_price(sample_accounts, sample_model, sample_prices):
    bad_model = PortfolioModel(name="BadModel", targets={"XYZ": 1.0})
    allocator = PortfolioAllocator(sample_accounts, bad_model, sample_prices)
    with pytest.raises(KeyError):
        allocator.compute_target_positions()