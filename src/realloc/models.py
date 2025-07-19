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
        """
        Normalizes target weights to sum to 1 (100%) while maintaining their relative proportions.

        This method takes the raw target weights and scales them so they sum to 1 while keeping
        their relative relationships intact. For example, targets of {A: 2, B: 2, C: 1} would
        become {A: 0.4, B: 0.4, C: 0.2}.

        Returns:
            Dict[str, float]: A dictionary mapping symbols to their normalized weights.
            If the sum of target weights is 0, returns the original targets unchanged.

        Example:
            >>> model = PortfolioModel("Example", {"AAPL": 40, "MSFT": 40, "GOOG": 20})
            >>> model.normalize()
            {'AAPL': 0.4, 'MSFT': 0.4, 'GOOG': 0.2}
        """
        total = sum(self.targets.values())
        if total == 0:
            return self.targets
        return {symbol: weight / total for symbol, weight in self.targets.items()}

    def to_dict(self) -> Dict:
        return {"name": self.name, "targets": self.targets}

    @classmethod
    def from_dict(cls, data: Dict) -> "PortfolioModel":
        return cls(name=data.get("name", ""), targets=data.get("targets", {}))
