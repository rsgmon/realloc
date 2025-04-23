from typing import List, Optional, Dict

from core.accounts import Account

class TradeAccountMatrix:
    def __init__(
        self,
        accounts: List[Account],
        prices: Dict[str, float],
        portfolio_trades: Optional[Dict[str, int]] = None,
    ):
        self.accounts = {a.account_number: a for a in accounts}
        self.prices = prices.copy()
        self.portfolio_trades = portfolio_trades.copy() if portfolio_trades else {}
        self.cash_matrix: Dict[str, float] = {a.account_number: a.cash for a in accounts}
        self.model_only: Dict[str, int] = {
            sym: qty for sym, qty in self.portfolio_trades.items()
            if not any(sym in a.positions for a in accounts)
        }

    def update(self, trades: Dict[str, Dict[str, int]]) -> None:
        for account_number, trade_dict in trades.items():
            account = self.accounts[account_number]
            for symbol, qty in trade_dict.items():
                new_position = account.positions.get(symbol, 0) + qty
                if account.enforce_no_negative_positions and new_position < 0:
                    raise ValueError(f"Trade would result in negative position for {symbol} in account {account_number}")
                account.positions[symbol] = new_position
                trade_value = qty * self.prices.get(symbol, 0)
                self.cash_matrix[account_number] -= trade_value

    def update_portfolio_trades(self, target_shares: Dict[str, float]):
        combined_current = {}
        for account in self.accounts.values():
            for sym, qty in account.positions.items():
                combined_current[sym] = combined_current.get(sym, 0.0) + qty
        self.portfolio_trades = allocate_trades(combined_current, target_shares)

    def to_dict(self) -> Dict:
        return {
            "portfolio_trades": self.portfolio_trades,
            "prices": self.prices,
            "cash_matrix": self.cash_matrix,
            "model_only": self.model_only
        }

    @classmethod
    def from_dict(cls, data: Dict, accounts: List[Account]) -> 'TradeAccountMatrix':
        instance = cls(
            accounts=accounts,
            prices=data.get("prices", {}),
            portfolio_trades=data.get("portfolio_trades", {})
        )
        instance.cash_matrix = data.get("cash_matrix", {})
        instance.model_only = data.get("model_only", {})
        return instance