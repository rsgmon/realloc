from dataclasses import dataclass
from typing import Dict, List
from realloc import Account, PortfolioModel, Trade

@dataclass
class ScenarioTest:
    """Represents a single rebalancing scenario test case"""
    name: str
    accounts: List[Account]
    model: PortfolioModel
    prices: Dict[str, float]
    expected_trades: List[Trade]
    description: str = ""

def create_basic_scenarios() -> List[ScenarioTest]:
    """Create basic test scenarios"""
    return [
        ScenarioTest(
            name="simple_two_account_balance",
            accounts=[
                Account("IRA", "A1", 1000, {"AAPL": 5}, {}),
                Account("Taxable", "A2", 2000, {"GOOG": 3}, {})
            ],
            model=PortfolioModel("50-50", {"AAPL": 0.5, "GOOG": 0.5}),
            prices={"AAPL": 100, "GOOG": 200},
            expected_trades=[
                Trade("A2", "AAPL", 5),
                Trade("A1", "GOOG", 2)
            ],
            description="Basic two account rebalancing with equal weights"
        )
    ]

def create_edge_case_scenarios() -> List[ScenarioTest]:
    """Create edge case test scenarios"""
    return [
        ScenarioTest(
            name="small_position_handling",
            accounts=[
                Account("IRA", "A1", 100, {"VTI": 0.1}, {})
            ],
            model=PortfolioModel("All-in", {"VTI": 1.0}),
            prices={"VTI": 200},
            expected_trades=[],
            description="Should not trade due to minimum trade size"
        )
    ]