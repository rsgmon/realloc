from typing import List, Optional, Dict
import math

class Account:
    def __init__(
        self,
        label: str,
        account_number: str,
        cash: float,
        positions: Dict[str, float],
        targets: Dict[str, float]
    ):
        self.label = label
        self.account_number = account_number
        self.cash = cash
        self.positions = positions
        self.targets = targets

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
            "targets": self.targets
        }

    @classmethod
    def from_dict(cls, data: Dict) -> 'Account':
        return cls(
            label=data.get("label", ""),
            account_number=data.get("account_number", ""),
            cash=data.get("cash", 0.0),
            positions=data.get("positions", {}),
            targets=data.get("targets", {})
        )

class TradeAccountMatrix:
    def __init__(
        self,
        accounts: List[Account],
        portfolio_trades: Dict[str, int],
        prices: Dict[str, float],
    ):
        self.accounts = {a.account_number: a for a in accounts}
        self.portfolio_trades = portfolio_trades.copy()
        self.prices = prices.copy()
        self.account_trades: Dict[str, Dict[str, int]] = {a.account_number: {} for a in accounts}
        self.cash_matrix: Dict[str, float] = {a.account_number: a.cash for a in accounts}
        self.share_trades: Dict[str, int] = portfolio_trades.copy()
        self.model_only: Dict[str, int] = {
            sym: qty for sym, qty in portfolio_trades.items()
            if not any(sym in a.positions for a in accounts)
        }

    def update(self):
        for account_number, trades in self.account_trades.items():
            account = self.accounts[account_number]
            for symbol, qty in trades.items():
                # Update holdings
                account.positions[symbol] = account.positions.get(symbol, 0) + qty

                # Update cash
                trade_value = qty * self.prices.get(symbol, 0)
                self.cash_matrix[account_number] -= trade_value

                # Update portfolio trade state
                self.share_trades[symbol] = self.share_trades.get(symbol, 0) - qty

        # Remove zeroed-out trades
        self.share_trades = {k: v for k, v in self.share_trades.items() if v != 0}
        for account_number in self.account_trades:
            self.account_trades[account_number] = {
                k: v for k, v in self.account_trades[account_number].items() if v != 0
            }

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
    return {'buy': buys, 'sell': sells'}
