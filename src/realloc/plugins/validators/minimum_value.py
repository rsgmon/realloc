from ..core.base import TradeValidator
from ...trades import TradeInfo


class MinimumValueValidator(TradeValidator):
    @property
    def name(self) -> str:
        return "minimum_value_validator"

    def validate(self, trade: TradeInfo) -> tuple[bool, str]:
        if trade.quantity == 0:
            return False, "Zero quantity trade"

        if trade.minimum_value == 0:
            return True, ""

        trade_value = abs(trade.quantity * trade.price)
        if trade_value < trade.minimum_value:
            return False, f"Trade value ${trade_value:.2f} below minimum ${trade.minimum_value:.2f}"

        return True, ""