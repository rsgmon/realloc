from typing import List, Optional, Dict, Any, Tuple

from realloc.accounts import Account
from realloc.plugins.core.engine import PluginEngine, ValidationEngine
from realloc.models import PortfolioModel
from .trades import compute_portfolio_trades, TradeInfo, Trade


class PortfolioStateManager:
    def __init__(
        self,
        accounts: List[Account],
        prices: Dict[str, float],
        portfolio_trades: Optional[Dict[str, int]] = None,
    ):
        self.accounts = {a.account_number: a for a in accounts}
        if any(price <= 0 for price in prices.values()):
            raise ValueError("All prices must be positive")
        self.prices = prices.copy()
        self.portfolio_trades = portfolio_trades.copy() if portfolio_trades else {}
        self.cash_matrix: Dict[str, float] = {
            a.account_number: a.cash for a in accounts
        }
        self.model_only: Dict[str, int] = {
            sym: qty
            for sym, qty in self.portfolio_trades.items()
            if not any(sym in a.positions for a in accounts)
        }
        self.plugin_engine = PluginEngine()
        self.validation_engine = ValidationEngine()

    @property
    def portfolio_trades(self) -> Dict[str, int]:
        return self._portfolio_trades

    @portfolio_trades.setter
    def portfolio_trades(self, value: Dict[str, int]) -> None:
        self._portfolio_trades = value.copy() if value else {}

    def add_validator(self, name: str, **kwargs: Any) -> None:
        """Add a validator to the portfolio manager"""
        self.validation_engine.add_validator(name, **kwargs)

    def get_total_portfolio_value(self) -> float:
        """Calculate total portfolio value including cash across all accounts."""
        total_cash = sum(self.cash_matrix.values())
        total_positions = sum(
            qty * self.prices[sym]
            for acc in self.accounts.values()
            for sym, qty in acc.positions.items()
        )
        return total_cash + total_positions

    def is_trade_feasible(self, account_id: str, symbol: str, quantity: float) -> bool:
        """Check if a trade can be executed given current account state."""
        account = self.accounts[account_id]
        if quantity > 0:  # Buy
            return self.cash_matrix[account_id] >= quantity * self.prices[symbol]
        else:  # Sell
            return account.positions.get(symbol, 0) >= abs(quantity)

    def reconcile_positions(self) -> Dict[str, float]:
        """Compare portfolio-level positions with sum of account positions."""
        combined = {}
        for acc in self.accounts.values():
            for sym, qty in acc.positions.items():
                combined[sym] = combined.get(sym, 0) + qty
        return {
            sym: combined.get(sym, 0) - self.portfolio_trades.get(sym, 0)
            for sym in set(combined) | set(self.portfolio_trades)
        }

    def update(self, trades: List[Trade]) -> None:
        # Validate all account IDs first
        invalid_accounts = [
            trade.account_id for trade in trades
            if trade.account_id not in self.accounts
        ]
        if invalid_accounts:
            raise ValueError(f"Invalid account IDs: {invalid_accounts}")

        # Group trades by account for efficient processing
        account_trades = {}
        for trade in trades:
            if trade.account_id not in account_trades:
                account_trades[trade.account_id] = []
            account_trades[trade.account_id].append((trade.symbol, trade.shares))

        # Process trades for each account
        for account_id, account_trades_list in account_trades.items():
            account = self.accounts[account_id]

            # Update positions and cash for each trade
            for symbol, qty in account_trades_list:
                new_position = account.positions.get(symbol, 0) + qty
                if account.enforce_no_negative_positions and new_position < 0:
                    raise ValueError(
                        f"Trade would result in negative position for {symbol} in account {account_id}"
                    )
                account.positions[symbol] = new_position
                trade_value = qty * self.prices.get(symbol, 0)
                self.cash_matrix[account_id] -= trade_value

    def get_account_summary(self) -> List[Dict[str, Any]]:
        """Get summary of all accounts including positions and cash."""
        return [
            {
                "account_id": acc.account_number,
                "label": acc.label,
                "cash": self.cash_matrix[acc.account_number],
                "positions": acc.positions,
                "total_value": sum(
                    qty * self.prices[sym] for sym, qty in acc.positions.items()
                ) + self.cash_matrix[acc.account_number]
            }
            for acc in self.accounts.values()
        ]

    def update_portfolio_trades(self, target_shares: Dict[str, float]):
        combined_current = {}
        for account in self.accounts.values():
            for sym, qty in account.positions.items():
                combined_current[sym] = combined_current.get(sym, 0.0) + qty
        self.portfolio_trades = compute_portfolio_trades(combined_current, target_shares)

    def validate_trade(self, account_id: str, symbol: str, quantity: float) -> tuple[bool, str]:
        account = self.accounts[account_id]
        price = self.prices.get(symbol, 0)

        trade_info = TradeInfo(
            symbol=symbol,
            quantity=quantity,
            price=price,
            minimum_value=account.minimum_trade_value,
            current_position=account.positions.get(symbol, 0),
            account_balance=self.cash_matrix.get(account_id, 0)
        )

        return self.validation_engine.validate_trade(trade_info)

    def has_sufficient_cash(self, account_id: str, amount: float) -> bool:
        """Check if account has sufficient cash for a transaction."""
        return self.cash_matrix.get(account_id, 0) >= amount

    def adjust_cash(self, account_id: str, amount: float) -> None:
        """Adjust account cash balance."""
        if account_id not in self.cash_matrix:
            raise ValueError(f"Invalid account ID: {account_id}")
        new_balance = self.cash_matrix[account_id] + amount
        if new_balance < 0:
            raise ValueError(f"Insufficient funds in account {account_id}")
        self.cash_matrix[account_id] = new_balance


    def to_dict(self) -> Dict:
        return {
            "portfolio_trades": self.portfolio_trades,
            "prices": self.prices,
            "cash_matrix": self.cash_matrix,
            "model_only": self.model_only,
        }

    @classmethod
    def from_dict(cls, data: Dict, accounts: List[Account]) -> "PortfolioStateManager":
        instance = cls(
            accounts=accounts,
            prices=data.get("prices", {}),
            portfolio_trades=data.get("portfolio_trades", {}),
        )
        instance.cash_matrix = data.get("cash_matrix", {})
        instance.model_only = data.get("model_only", {})
        return instance


def calculate_portfolio_positions(accounts: List[Account]) -> Tuple[Dict[str, float], float]:
    """
    Calculate combined positions across all accounts and total cash.

    Args:
        accounts: List of Account objects

    Returns:
        Tuple of (combined positions dictionary, total cash)
    """
    combined_positions = {}
    total_cash = sum(acc.cash for acc in accounts)

    for acc in accounts:
        for sym, qty in acc.positions.items():
            combined_positions[sym] = combined_positions.get(sym, 0) + qty

    return combined_positions, total_cash


def calculate_portfolio_positions_from_dicts(accounts_data: List[Dict[str, Any]]) -> Tuple[Dict[str, float], float]:
    """
    Calculate combined positions across all accounts and total cash from dictionary data.

    Args:
        accounts_data: List of dictionaries, each containing 'cash' and 'positions' keys
                      where 'positions' is a dictionary of symbol-quantity pairs

    Returns:
        Tuple of (combined positions dictionary, total cash)

    Example:
        >>> accounts = [
        ...     {"cash": 1000.0, "positions": {"AAPL": 10, "MSFT": 5}},
        ...     {"cash": 500.0, "positions": {"AAPL": 5, "GOOG": 3}}
        ... ]
        >>> positions, cash = calculate_portfolio_positions_from_dicts(accounts)
        >>> print(positions)  # {"AAPL": 15, "MSFT": 5, "GOOG": 3}
        >>> print(cash)  # 1500.0
    """
    combined_positions = {}
    total_cash = sum(acc.get("cash", 0.0) for acc in accounts_data)

    for acc in accounts_data:
        for sym, qty in acc.get("positions", {}).items():
            combined_positions[sym] = combined_positions.get(sym, 0) + qty

    return combined_positions, total_cash


def calculate_target_shares(
        combined_positions: Dict[str, float],
        total_cash: float,
        prices: Dict[str, float],
        model: PortfolioModel
) -> Dict[str, float]:
    """
    Calculate target shares for each symbol based on the model and total portfolio value.

    Args:
        combined_positions: Dictionary of current positions
        total_cash: Total cash across all accounts
        prices: Dictionary of current prices
        model: Portfolio model with target weights

    Returns:
        Dictionary mapping symbols to target shares
    """
    total_value = total_cash + sum(
        qty * prices[sym] for sym, qty in combined_positions.items()
    )
    normalized_model = model.normalize()
    target_dollars = {
        sym: weight * total_value for sym, weight in normalized_model.items()
    }
    return {sym: target_dollars[sym] / prices[sym] for sym in target_dollars}


def calculate_target_shares_from_accounts(
        accounts: List[Account],
        prices: Dict[str, float],
        model: PortfolioModel
) -> Dict[str, float]:
    """
    Calculate target shares for each symbol based on the model and accounts.

    Args:
        accounts: List of Account objects
        prices: Dictionary of current prices
        model: Portfolio model with target weights

    Returns:
        Dictionary mapping symbols to target shares
    """
    # Calculate combined positions and total cash
    combined_positions = {}
    total_cash = 0

    for account in accounts:
        total_cash += account.cash
        for sym, qty in account.positions.items():
            combined_positions[sym] = combined_positions.get(sym, 0) + qty

    # Calculate total portfolio value
    total_value = total_cash + sum(
        qty * prices[sym] for sym, qty in combined_positions.items()
    )

    # Calculate target shares using normalized model weights
    normalized_model = model.normalize()
    target_dollars = {
        sym: weight * total_value for sym, weight in normalized_model.items()
    }
    return {sym: target_dollars[sym] / prices[sym] for sym in target_dollars}