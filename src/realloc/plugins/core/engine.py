from typing import Dict, List, Type, TypeVar, Tuple, Any
from .base import Plugin, TradeValidator, Exporter
from ...trades import TradeInfo

T = TypeVar('T', bound=Plugin)


class PluginEngine:
    """Manages plugin registration and execution"""

    def __init__(self):
        self.plugins: Dict[str, Plugin] = {}

    def register(self, plugin: Plugin) -> None:
        """Register a plugin"""
        self.plugins[plugin.name] = plugin

    def get_plugins_of_type(self, plugin_type: Type[T]) -> List[T]:
        """Get all test_plugins of a specific type"""
        return [p for p in self.plugins.values() if isinstance(p, plugin_type)]


class ValidationEngine:
    """Specialized engine for trade validation plugins"""

    def __init__(self):
        self.validators: List[TradeValidator] = []

    def add_validator(self, name: str, **kwargs: Any) -> None:
        """Add a validator by name"""
        validator = TradeValidator.load_validator(name, **kwargs)
        self.validators.append(validator)

    def validate_trade(self, trade_info: TradeInfo) -> Tuple[bool, str]:
        """Run all registered validators on a trade"""
        for validator in self.validators:
            is_valid, reason = validator.validate(trade_info)
            if not is_valid:
                return False, reason
        return True, ""