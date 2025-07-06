import importlib.metadata
from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional, Tuple


class Plugin(ABC):
    """Base class for all test_plugins"""
    @property
    @abstractmethod
    def name(self) -> str:
        """Unique name identifying this plugin"""
        pass


class Exporter(Plugin):
    """Base class for data export test_plugins"""
    @abstractmethod
    def export(self, data: dict) -> None:
        pass

    @staticmethod
    def load_export_plugin(name: str, path: Path) -> 'Exporter':
        """
        Load an export plugin by name.

        Args:
            name: The name of the plugin to load
            path: Path to the export file

        Returns:
            An instance of the loaded plugin

        Raises:
            ValueError: If no plugin with the given name is found
            RuntimeError: If the plugin fails to load
        """
        try:
            entry_points = importlib.metadata.entry_points()

            # Handle different entry_points return types across Python versions
            if hasattr(entry_points, "select"):  # Python 3.10+
                matches = list(entry_points.select(group="realloc.plugins", name=name))
            else:  # Earlier Python versions
                matches = [
                    ep for ep in entry_points.get("realloc.plugins", [])
                    if ep.name == name
                ]

            if not matches:
                # Debug info
                available = []
                if hasattr(entry_points, "select"):
                    available = [ep.name for ep in entry_points.select(group="realloc.plugins")]
                else:
                    available = [ep.name for ep in entry_points.get("realloc.plugins", [])]

                raise ValueError(
                    f"No export plugin named '{name}' found. "
                    f"Available plugins: {list(set(available))}"  # Using set to remove duplicates
                )

            plugin_class = matches[0].load()
            if not isinstance(plugin_class, type) or not issubclass(plugin_class, Exporter):
                raise ValueError(
                    f"Plugin '{name}' is not a valid Exporter. "
                    f"Got {type(plugin_class)}"
                )

            return plugin_class(path=path)

        except Exception as e:
            if isinstance(e, ValueError):
                raise
            raise RuntimeError(f"Failed to load plugin '{name}': {e}")


@dataclass
class TradeInfo:
    """Container for all trade-related information needed for validators"""
    symbol: str
    quantity: float
    price: float
    minimum_value: float = 0
    account_balance: Optional[float] = None
    current_position: Optional[float] = None


class TradeValidator(Plugin):
    """Base class for trade validation test_plugins"""

    @abstractmethod
    def validate(self, trade: TradeInfo) -> Tuple[bool, str]:
        """Validate a trade based on specific criteria.

        Args:
            trade: TradeInfo object containing all trade details

        Returns:
            tuple[bool, str]: (is_valid, reason_if_invalid)
        """
        pass

