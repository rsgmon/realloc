from typing import List, Dict, Optional, Tuple
from realloc.accounts import Account
from realloc.models import PortfolioModel


class PortfolioAllocator:
    def __init__(
            self,
            accounts: List[Account],
            model: PortfolioModel,
            prices: Dict[str, float],
            selector: Optional[object] = None,
    ):
        self.accounts = accounts
        self.model = model
        self.prices = prices
        self.selector = selector
        self._account_values: Optional[Dict[str, float]] = None
        self._total_portfolio_value: Optional[float] = None

    def compute_account_values(self) -> Dict[str, float]:
        """
        Compute the total value of each account including cash and positions.
        Returns a dictionary mapping account IDs to their total values.
        """
        if self._account_values is None:
            self._account_values = {
                acc.account_number: (
                        acc.cash + sum(qty * self.prices[sym] for sym, qty in acc.positions.items())
                )
                for acc in self.accounts
            }
        return self._account_values

    @property
    def total_portfolio_value(self) -> float:
        """Get the total value of all accounts combined."""
        if self._total_portfolio_value is None:
            self._total_portfolio_value = sum(self.compute_account_values().values())
        return self._total_portfolio_value

    def get_current_allocations(self) -> Dict[str, Dict[str, float]]:
        """
        Get current percentage allocations for each account.
        Returns dict of account_id -> {symbol: current_weight}
        """
        account_values = self.compute_account_values()
        current_allocations = {}

        for acc in self.accounts:
            if account_values[acc.account_number] == 0:
                current_allocations[acc.account_number] = {}
                continue

            acc_value = account_values[acc.account_number]
            allocations = {
                sym: (qty * self.prices[sym]) / acc_value
                for sym, qty in acc.positions.items()
            }
            # Add cash allocation
            allocations['CASH'] = acc.cash / acc_value
            current_allocations[acc.account_number] = allocations

        return current_allocations

    def compute_target_allocations(self) -> Dict[str, Dict[str, float]]:
        """
        Compute target percentage allocations for each account.
        Returns dict of account_id -> {symbol: target_weight}
        """
        normalized = self.model.normalize()
        return {
            acc.account_number: {sym: weight for sym, weight in normalized.items()}
            for acc in self.accounts
        }

    def compute_target_positions(self) -> Dict[str, Dict[str, float]]:
        """
        Compute target absolute positions (in shares) for each account.
        Returns dict of account_id -> {symbol: target_shares}
        """
        account_values = self.compute_account_values()
        normalized = self.model.normalize()

        target_positions = {}
        for acc in self.accounts:
            acc_value = account_values[acc.account_number]
            target_positions[acc.account_number] = {
                sym: (weight * acc_value) / self.prices[sym]
                for sym, weight in normalized.items()
            }

        return target_positions

    def get_allocation_differences(self) -> Dict[str, Dict[str, Tuple[float, float]]]:
        """
        Compare current vs target allocations for each account.
        Returns dict of account_id -> {symbol: (current_weight, target_weight)}
        """
        current = self.get_current_allocations()
        target = self.compute_target_allocations()

        differences = {}
        for acc_id in current:
            differences[acc_id] = {}
            for sym in set(current[acc_id].keys()) | set(target[acc_id].keys()):
                curr_weight = current[acc_id].get(sym, 0.0)
                target_weight = target[acc_id].get(sym, 0.0)
                differences[acc_id][sym] = (curr_weight, target_weight)

        return differences

    def get_account_positions(self) -> Dict[str, Dict[str, float]]:
        """Get current positions for each account."""
        return {acc.account_number: acc.positions for acc in self.accounts}