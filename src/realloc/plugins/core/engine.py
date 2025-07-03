from typing import Dict, List, Type, TypeVar, Tuple
from .base import Plugin, TradeValidator, Exporter, TradeInfo

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
    """Specialized engine for trade validation test_plugins"""

    def __init__(self, plugin_engine: PluginEngine):
        self.plugin_engine = plugin_engine

    def validate_trade(self, trade_info: TradeInfo) -> Tuple[bool, str]:
        """Run all registered validators on a trade"""
        validators = self.plugin_engine.get_plugins_of_type(TradeValidator)
        for validator in validators:
            is_valid, reason = validator.validate(trade_info)
            if not is_valid:
                return False, reason
        return True, ""