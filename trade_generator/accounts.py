from typing import List, Optional, Dict

from trades import allocate_trades, split_trades

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