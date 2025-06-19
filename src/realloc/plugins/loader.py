import sys
import importlib.metadata
from realloc.plugins.base import ExportPlugin


def load_export_plugin(name: str):
    try:
        entry_points = importlib.metadata.entry_points()
        if hasattr(entry_points, "select"):  # Python 3.10+
            matches = entry_points.select(group="realloc.plugins", name=name)
        else:  # <3.10 fallback
            matches = entry_points.get("realloc.plugins", [])
            matches = [ep for ep in matches if ep.name == name]
        if not matches:
            raise ValueError(f"No export plugin named '{name}' found.")
        return matches[0].load()
    except Exception as e:
        raise RuntimeError(f"Failed to load plugin '{name}': {e}")
