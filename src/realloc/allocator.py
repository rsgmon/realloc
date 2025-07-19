from typing import List, Dict, Optional
from realloc.accounts import Account
from realloc.models import PortfolioModel
from realloc.matrix import PortfolioStateManager
from realloc.trades import compute_portfolio_trades


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
        self.tam: Optional[PortfolioStateManager] = None
        self._portfolio_trades: Optional[Dict[str, int]] = None

    def compute_portfolio_trades(self):
        combined = {}
        total_cash = sum(acc.cash for acc in self.accounts)

        for acc in self.accounts:
            for sym, qty in acc.positions.items():
                combined[sym] = combined.get(sym, 0) + qty

        total_value = total_cash + sum(
            qty * self.prices[sym] for sym, qty in combined.items()
        )
        normalized = self.model.normalize()

        target_shares = {
            sym: (weight * total_value) / self.prices[sym]
            for sym, weight in normalized.items()
        }

        self._portfolio_trades = compute_portfolio_trades(combined, target_shares, self.prices)
        return self._portfolio_trades

    def rebalance(self) -> Dict[str, int]:
        if self._portfolio_trades is None:
            self.compute_portfolio_trades()

        self.tam = PortfolioStateManager(
            self.accounts, self.prices, self._portfolio_trades
        )
        return self.tam.portfolio_trades

    def get_cash_matrix(self) -> Dict[str, float]:
        return self.tam.cash_matrix if self.tam else {}

    def get_account_positions(self) -> Dict[str, Dict[str, float]]:
        return {acc.account_number: acc.positions for acc in self.accounts}

    @property
    def portfolio_trades(self) -> Optional[Dict[str, int]]:
        return self._portfolio_trades
