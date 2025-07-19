from dataclasses import dataclass, asdict
from typing import List, Optional, Dict, TYPE_CHECKING, Any
import math


from realloc.utils import normalize_symbol_sets

if TYPE_CHECKING:
    from .accounts import Account



@dataclass
class Trade:
    account_id: str
    symbol: str
    shares: float

    def to_dict(self) -> Dict[str, Any]:
        """Serialize the dataclass to a dictionary"""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TradeInfo':
        """Deserialize from a dictionary to create a new instance"""
        return cls(**data)


@dataclass
class TradeInfo:
    """Information about a trade for validation purposes"""
    symbol: str
    quantity: float
    price: float
    minimum_value: Optional[float] = None
    current_position: Optional[float] = None
    account_balance: Optional[float] = None



def compute_portfolio_trades(
    current_shares: Dict[str, float],
    target_shares: Dict[str, float],
    prices: Optional[Dict[str, float]] = None,
) -> Dict[str, int]:
    current_shares, target_shares = normalize_symbol_sets(current_shares, target_shares)
    return {
        symbol: int(math.floor(target_shares[symbol] - current_shares[symbol]))
        for symbol in current_shares
    }


def split_trades(
    current_shares: Dict[str, float],
    target_shares: Dict[str, float],
    prices: Optional[Dict[str, float]] = None,
) -> Dict[str, Dict[str, int]]:
    net_trades = compute_portfolio_trades(current_shares, target_shares, prices)
    buys = {s: v for s, v in net_trades.items() if v > 0}
    sells = {s: abs(v) for s, v in net_trades.items() if v < 0}
    return {"buy": buys, "sell": sells}


class ScaledPortfolio:
    def __init__(self, accounts: List["Account"], model_target: Dict[str, float]):
        self.accounts = accounts
        self.model_target = model_target

    def generate_scaled_cash_constrained_trades(
        self, prices: Dict[str, float]
    ) -> Dict[str, Dict[str, int]]:
        trades_by_account = {}
        for account in self.accounts:
            total_value = sum(
                account.positions.get(sym, 0) * prices.get(sym, 0)
                for sym in self.model_target
            )
            total_value += account.cash

            scaled_target = {
                sym: (self.model_target[sym] * total_value)
                / sum(self.model_target.values())
                for sym in self.model_target
            }

            share_targets = {
                sym: scaled_target[sym] / prices.get(sym, 1)
                for sym in self.model_target
            }

            current = account.positions
            normalized_current, normalized_target = normalize_symbol_sets(
                current, share_targets
            )
            trade_shares = compute_portfolio_trades(
                normalized_current, normalized_target, prices
            )

            final_trades = {}
            cash_used = 0.0
            for sym, qty in trade_shares.items():
                cost = qty * prices.get(sym, 0)
                if qty > 0:
                    if cash_used + cost <= account.cash:
                        final_trades[sym] = qty
                        cash_used += cost
                    else:
                        affordable_qty = int(
                            (account.cash - cash_used) // prices.get(sym, 1)
                        )
                        if affordable_qty > 0:
                            final_trades[sym] = affordable_qty
                            cash_used += affordable_qty * prices.get(sym, 1)
                else:
                    final_trades[sym] = qty

            trades_by_account[account.account_number] = final_trades

        return trades_by_account


def is_trade_remaining(trades, tolerance: float = 0.01) -> bool:
    return any(abs(qty) > tolerance for qty in trades.values())


def sell_position(current: float, target: float) -> float:
    return max(current - target, 0)


def calculate_sell_amounts(
    current_amounts: List[float], target_amounts: List[Optional[float]]
) -> List[float]:
    return [
        sell_position(c, t if t is not None else 0)
        for c, t in zip(current_amounts, target_amounts)
    ]


def buy_position(current: float, target: float) -> float:
    return max(target - current, 0)


def calculate_buy_amounts(
    current_amounts: List[float], target_amounts: List[Optional[float]]
) -> List[float]:
    return [
        buy_position(c, t if t is not None else 0)
        for c, t in zip(current_amounts, target_amounts)
    ]
