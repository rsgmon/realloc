import json
from pathlib import Path
import pytest
from realloc import Account, PortfolioModel, Trade, PortfolioStateManager
from realloc.plugins.rebalancers.default_rebalancer import DefaultRebalancer
from realloc.portfolio import (
    calculate_portfolio_positions,
    calculate_target_shares,
    compute_portfolio_trades
)


def load_json_scenario(file_path: Path) -> dict:
    """Load a single scenario from JSON file"""
    with open(file_path) as f:
        data = json.load(f)

    # Convert JSON data to scenario objects
    accounts = [Account(**acc) for acc in data["accounts"]]
    model = PortfolioModel(
        name=data["model"]["label"],
        targets=data["model"]["targets"]
    )
    expected_trades = [
        Trade(**trade) for trade in data["expected_trades"]
    ]

    return {
        "name": data["name"],
        "description": data.get("description", ""),
        "accounts": accounts,
        "model": model,
        "prices": data["prices"],
        "expected_trades": expected_trades
    }


def load_all_json_scenarios() -> list:
    """Load all JSON scenarios from test_cases directory"""
    scenarios = []
    test_cases_dir = Path(__file__).parent / "test_cases"
    for json_file in test_cases_dir.glob("*.json"):
        scenario = load_json_scenario(json_file)
        scenarios.append(scenario)
    return scenarios


def verify_scenario(scenario, rebalancer):
    """Execute and verify a single scenario"""
    # Calculate initial portfolio state
    combined_positions, total_cash = calculate_portfolio_positions(scenario["accounts"])

    # Calculate target shares
    target_shares = calculate_target_shares(
        combined_positions,
        total_cash,
        scenario["prices"],
        scenario["model"]
    )

    # Calculate required trades at portfolio level
    portfolio_level_trades = compute_portfolio_trades(
        combined_positions,
        target_shares,
        scenario["prices"]
    )

    # Initialize portfolio state manager with calculated trades
    tam = PortfolioStateManager(
        scenario["accounts"],
        scenario["prices"],
        portfolio_level_trades
    )

    # Execute rebalance
    actual_trades = rebalancer.execute_rebalance(
        portfolio_state=tam,
        target_shares=target_shares,
        max_iterations=10
    )

    # Verify number of trades matches
    assert len(actual_trades) == len(scenario["expected_trades"]), \
        f"Expected {len(scenario['expected_trades'])} trades, got {len(actual_trades)}"

    # Compare trades (order independent)
    for expected in scenario["expected_trades"]:
        matching_trade = next(
            (t for t in actual_trades
             if t.account_id == expected.account_id
             and t.symbol == expected.symbol),
            None
        )
        assert matching_trade is not None, \
            f"Missing expected trade: {expected}"
        assert matching_trade.shares == expected.shares, \
            f"Trade quantity mismatch for {expected.symbol} in account {expected.account_id}: " \
            f"expected {expected.shares}, got {matching_trade.shares}"


@pytest.mark.parametrize(
    "scenario",
    load_all_json_scenarios(),
    ids=lambda s: s["name"]
)
def test_json_scenarios(scenario):
    """Test scenarios loaded from JSON files"""
    rebalancer = DefaultRebalancer()
    verify_scenario(scenario, rebalancer)