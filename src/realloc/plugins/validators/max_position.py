from realloc.plugins.core.base import TradeValidator
from realloc.trades import TradeInfo


class MaxPositionValidator(TradeValidator):
    def __init__(self, max_position: float):
        self.max_position = max_position

    @property
    def name(self) -> str:
        return "max_position"

    def validate(self, trade: TradeInfo) -> tuple[bool, str]:
        # For missing current_position, treat as valid (per test requirement)
        if trade.current_position is None:
            return True, ""

        new_position = trade.current_position + trade.quantity
        if abs(new_position) <= self.max_position:
            return True, ""

        return False, f"Would exceed max position of {self.max_position}"