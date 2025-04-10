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
