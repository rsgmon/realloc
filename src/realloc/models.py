from typing import List, Optional, Dict


class PortfolioModel:
    def __init__(
        self,
        name: str,
        targets: Optional[Dict[str, float]] = None,
        enforce_long_only: bool = True,
    ):
        self.name = name
        self.enforce_long_only = enforce_long_only
        self.targets = targets if targets is not None else {}

        if self.enforce_long_only:
            for symbol, weight in self.targets.items():
                if weight < 0:
                    raise ValueError(
                        f"Model contains short weight for {symbol}, which is not allowed in long-only mode."
                    )

    def add_target(self, symbol: str, weight: float):
        if self.enforce_long_only and weight < 0:
            raise ValueError(
                f"Cannot add short weight for {symbol} in long-only model."
            )
        self.targets[symbol] = weight

    def remove_target(self, symbol: str):
        self.targets.pop(symbol, None)

    def update_target(self, symbol: str, weight: float):
        if self.enforce_long_only and weight < 0:
            raise ValueError(
                f"Cannot update to short weight for {symbol} in long-only model."
            )
        self.targets[symbol] = weight

    def get_target(self, symbol: str) -> Optional[float]:
        return self.targets.get(symbol)

    def normalize(self) -> Dict[str, float]:
        total = sum(self.targets.values())
        if total == 0:
            return self.targets
        return {symbol: weight / total for symbol, weight in self.targets.items()}

    def to_dict(self) -> Dict:
        return {"name": self.name, "targets": self.targets}

    @classmethod
    def from_dict(cls, data: Dict) -> "PortfolioModel":
        return cls(name=data.get("name", ""), targets=data.get("targets", {}))
