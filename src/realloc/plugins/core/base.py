from abc import ABC, abstractmethod
import importlib.metadata
from typing import TypeVar, Type, Any, List, TYPE_CHECKING, Dict

if TYPE_CHECKING:
    from ...trades import Trade


T = TypeVar('T', bound='Plugin')


class Plugin(ABC):
    """Base class for all plugins"""

    @property
    @abstractmethod
    def name(self) -> str:
        """Unique name identifying this plugin"""
        pass

    @classmethod
    def load_plugin(cls: Type[T], name: str, **kwargs: Any) -> T:
        """
        Generic plugin loader for any plugin type.

        Args:
            name: Name of the plugin to load
            **kwargs: Configuration parameters for the plugin

        Returns:
            Instantiated plugin

        Raises:
            ValueError: If plugin not found or invalid
        """
        try:
            entry_points = importlib.metadata.entry_points()

            # Handle different entry_points return types across Python versions
            if hasattr(entry_points, "select"):
                matches = list(entry_points.select(group="realloc.plugins", name=name))
            else:
                matches = [
                    ep for ep in entry_points.get("realloc.plugins", [])
                    if ep.name == name
                ]

            if not matches:
                raise ValueError(f"No plugin named '{name}' found")

            plugin_class = matches[0].load()
            if not isinstance(plugin_class, type) or not issubclass(plugin_class, cls):
                raise ValueError(
                    f"Plugin '{name}' is not a valid {cls.__name__}. "
                    f"Got {type(plugin_class)}"
                )

            return plugin_class(**kwargs)

        except Exception as e:
            if isinstance(e, ValueError):
                raise
            raise RuntimeError(f"Failed to load plugin '{name}': {e}")


class TradeValidator(Plugin):
    @abstractmethod
    def validate(self, trade: [dict]) -> tuple[bool, str]:
        pass

    @classmethod
    def load_validator(cls, name: str, **kwargs: Any) -> 'TradeValidator':
        """Convenience method for loading validator plugins"""
        return cls.load_plugin(name, **kwargs)

class Exporter(Plugin):
    @abstractmethod
    def export(self, trades: List['Trade']) -> None:
        pass

    @classmethod
    def load_exporter(cls, name: str, **kwargs: Any) -> 'Exporter':
        """Convenience method for loading exporter plugins"""
        return cls.load_plugin(name, **kwargs)


class RebalancerPlugin(Plugin):
    """Base class for rebalancing plugins"""

    @abstractmethod
    def execute_rebalance(
            self,
            tam: "PortfolioStateManager",
            target_shares: Dict[str, float],
            max_iterations: int
    ) -> List["Trade"]:
        """
        Execute the rebalancing trades across accounts.

        Args:
            tam: Trade Account Matrix instance
            target_shares: Dictionary of target shares per symbol
            max_iterations: Maximum number of iterations to attempt

        Returns:
            List of executed trades
        """
        pass

    @classmethod
    def load_rebalancer(cls, name: str, **kwargs: Any) -> 'RebalancerPlugin':
        """Convenience method for loading rebalancer plugins"""
        return cls.load_plugin(name, **kwargs)