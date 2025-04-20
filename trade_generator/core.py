from typing import List, Optional, Dict
import math

class Account:
    def __init__(
        self,
        label: str,
        account_number: str,
        cash: float,
        positions: Dict[str, float],
        targets: Dict[str, float],
        enforce_no_negative_positions: bool = False
    ):
        self.label = label
        self.account_number = account_number
        self.cash = cash
        self.positions = positions
        self.targets = targets
        self.enforce_no_negative_positions = enforce_no_negative_positions

        if self.enforce_no_negative_positions:
            for symbol, amount in self.positions.items():
                if amount < 0:
                    raise ValueError(f"Negative position for {symbol} not allowed in account {account_number}")

    def allocate(self, prices: Optional[Dict[str, float]] = None) -> Dict[str, int]:
        return allocate_trades(self.positions, self.targets, prices)

    def split_allocation(self, prices: Optional[Dict[str, float]] = None) -> Dict[str, Dict[str, int]]:
        return split_trades(self.positions, self.targets, prices)

    def to_dict(self) -> Dict:
        return {
            "label": self.label,
            "account_number": self.account_number,
            "cash": self.cash,
            "positions": self.positions,
            "targets": self.targets,
            "enforce_no_negative_positions": self.enforce_no_negative_positions
        }

    @classmethod
    def from_dict(cls, data: Dict) -> 'Account':
        return cls(
            label=data.get("label", ""),
            account_number=data.get("account_number", ""),
            cash=data.get("cash", 0.0),
            positions=data.get("positions", {}),
            targets=data.get("targets", {}),
            enforce_no_negative_positions=data.get("enforce_no_negative_positions", False)
        )

class PortfolioModel:
    def __init__(self, name: str, targets: Optional[Dict[str, float]] = None, enforce_long_only: bool = True):
        self.name = name
        self.enforce_long_only = enforce_long_only
        self.targets = targets if targets is not None else {}

        if self.enforce_long_only:
            for symbol, weight in self.targets.items():
                if weight < 0:
                    raise ValueError(f"Model contains short weight for {symbol}, which is not allowed in long-only mode.")

    def add_target(self, symbol: str, weight: float):
        if self.enforce_long_only and weight < 0:
            raise ValueError(f"Cannot add short weight for {symbol} in long-only model.")
        self.targets[symbol] = weight

    def remove_target(self, symbol: str):
        self.targets.pop(symbol, None)

    def update_target(self, symbol: str, weight: float):
        if self.enforce_long_only and weight < 0:
            raise ValueError(f"Cannot update to short weight for {symbol} in long-only model.")
        self.targets[symbol] = weight

    def get_target(self, symbol: str) -> Optional[float]:
        return self.targets.get(symbol)

    def normalize(self) -> Dict[str, float]:
        total = sum(self.targets.values())
        if total == 0:
            return self.targets
        return {symbol: weight / total for symbol, weight in self.targets.items()}

    def to_dict(self) -> Dict:
        return {
            "name": self.name,
            "targets": self.targets
        }

    @classmethod
    def from_dict(cls, data: Dict) -> 'PortfolioModel':
        return cls(
            name=data.get("name", ""),
            targets=data.get("targets", {})
        )

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

class ScaledPortfolio:
    def __init__(self, accounts: List[Account], model_target: Dict[str, float]):
        self.accounts = accounts
        self.model_target = model_target

    def generate_scaled_cash_constrained_trades(self, prices: Dict[str, float]) -> Dict[str, Dict[str, int]]:
        trades_by_account = {}
        for account in self.accounts:
            total_value = sum(account.positions.get(sym, 0) * prices.get(sym, 0) for sym in self.model_target)
            total_value += account.cash

            scaled_target = {
                sym: (self.model_target[sym] * total_value) / sum(self.model_target.values())
                for sym in self.model_target
            }

            share_targets = {
                sym: scaled_target[sym] / prices.get(sym, 1)
                for sym in self.model_target
            }

            current = account.positions
            normalized_current, normalized_target = normalize_symbol_sets(current, share_targets)
            trade_shares = allocate_trades(normalized_current, normalized_target, prices)

            final_trades = {}
            cash_used = 0.0
            for sym, qty in trade_shares.items():
                cost = qty * prices.get(sym, 0)
                if qty > 0:
                    if cash_used + cost <= account.cash:
                        final_trades[sym] = qty
                        cash_used += cost
                    else:
                        affordable_qty = int((account.cash - cash_used) // prices.get(sym, 1))
                        if affordable_qty > 0:
                            final_trades[sym] = affordable_qty
                            cash_used += affordable_qty * prices.get(sym, 1)
                else:
                    final_trades[sym] = qty

            trades_by_account[account.account_number] = final_trades

        return trades_by_account

def sell_position(current: float, target: float) -> float:
    return max(current - target, 0)

def calculate_sell_amounts(current_amounts: List[float], target_amounts: List[Optional[float]]) -> List[float]:
    return [sell_position(c, t if t is not None else 0) for c, t in zip(current_amounts, target_amounts)]

def buy_position(current: float, target: float) -> float:
    return max(target - current, 0)

def calculate_buy_amounts(current_amounts: List[float], target_amounts: List[Optional[float]]) -> List[float]:
    return [buy_position(c, t if t is not None else 0) for c, t in zip(current_amounts, target_amounts)]

def normalize_symbol_sets(
    current_shares: Dict[str, float],
    target_shares: Dict[str, float]
) -> (Dict[str, float], Dict[str, float]):
    all_symbols = set(current_shares.keys()) | set(target_shares.keys())
    return (
        {symbol: current_shares.get(symbol, 0.0) for symbol in all_symbols},
        {symbol: target_shares.get(symbol, 0.0) for symbol in all_symbols}
    )

def allocate_trades(
    current_shares: Dict[str, float],
    target_shares: Dict[str, float],
    prices: Optional[Dict[str, float]] = None
) -> Dict[str, int]:
    current_shares, target_shares = normalize_symbol_sets(current_shares, target_shares)
    return {
        symbol: int(math.floor(target_shares[symbol] - current_shares[symbol]))
        for symbol in current_shares
    }

def split_trades(
    current_shares: Dict[str, float],
    target_shares: Dict[str, float],
    prices: Optional[Dict[str, float]] = None
) -> Dict[str, Dict[str, int]]:
    net_trades = allocate_trades(current_shares, target_shares, prices)
    buys = {s: v for s, v in net_trades.items() if v > 0}
    sells = {s: abs(v) for s, v in net_trades.items() if v < 0}
    return {'buy': buys, 'sell': sells}


def select_account_for_buy_trade(
    symbol: str,
    trade_amount: int,
    accounts: List[Account],
    prices: Dict[str, float]
) -> Optional[str]:
    """
    Select the most appropriate account for a given buy trade.

    Priority:
    1. Accounts that already hold the symbol.
    2. Among them, the one with the largest position.
    3. If none can fulfill the full trade, choose the one that can fulfill the largest partial.
    4. If no accounts hold the symbol, choose the one with enough cash.
    """
    candidates = [a for a in accounts if symbol in a.positions]
    if candidates:
        candidates.sort(key=lambda a: a.positions.get(symbol, 0), reverse=True)
        for account in candidates:
            max_possible = int(account.cash // prices[symbol])
            if trade_amount <= max_possible:
                return account.account_number

        # If none can fulfill the full trade, return the one that can do the most
        partial_candidates = [(a, int(a.cash // prices[symbol])) for a in candidates if int(a.cash // prices[symbol]) > 0]
        if partial_candidates:
            best = max(partial_candidates, key=lambda x: x[1])
            return best[0].account_number

    # Fallback to any account with enough cash
    cash_candidates = [(a, int(a.cash // prices[symbol])) for a in accounts if int(a.cash // prices[symbol]) > 0]
    if cash_candidates:
        best = max(cash_candidates, key=lambda x: x[1])
        return best[0].account_number

    return None


def select_account_for_sell_trade(
    symbol: str,
    trade_amount: int,
    accounts: List[Account]
) -> Optional[str]:
    """
    Select the most appropriate account for a given sell trade.

    Priority:
    1. Accounts that already hold the symbol.
    2. Among them, the one with the largest position.
    3. Return the first one that can fulfill the full sell.
    4. If none can do it fully, choose the one that can do the largest partial.
    """
    candidates = [a for a in accounts if symbol in a.positions and a.positions[symbol] > 0]
    if not candidates:
        return None

    candidates.sort(key=lambda a: a.positions.get(symbol, 0), reverse=True)
    for account in candidates:
        if account.positions[symbol] >= trade_amount:
            return account.account_number

    # Fallback to the one with the largest position
    return candidates[0].account_number if candidates else None
