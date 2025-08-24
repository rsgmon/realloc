# src/realloc/plugins/core/discovery.py
from typing import Dict, List
from importlib.metadata import entry_points


def get_plugin_list() -> Dict[str, List[str]]:
    plugins = {"exporters": [], "validators": [], "rebalancers": []}

    discovered_plugins = entry_points().get('realloc.plugins', [])
    print("DEBUG - All discovered plugins:")
    for plugin in discovered_plugins:
        print(f"  {plugin.name}: {plugin.value}")

    for plugin in discovered_plugins:
        class_name = plugin.value.split(':')[1]
        if class_name.endswith('Exporter'):
            plugins["exporters"].append(plugin.name)
        elif class_name.endswith('Validator'):
            plugins["validators"].append(plugin.name)
        elif class_name.endswith('Rebalancer'):
            plugins["rebalancers"].append(plugin.name)

    return plugins


def get_plugin(name: str):
    plugins = entry_points().get('realloc.plugins', [])
    for plugin in plugins:
        if plugin.name == name:
            return plugin.load()
    raise ValueError(f"Plugin {name} not found")



def list_plugins() -> None:
    """Print all available realloc plugins to stdout"""
    plugins = get_plugin_list()

    print("Available realloc plugins:")

    if plugins["exporters"]:
        print("\nExporters:")
        for plugin in plugins["exporters"]:
            print(f"  - {plugin}")

    if plugins["validators"]:
        print("\nValidators:")
        for plugin in plugins["validators"]:
            print(f"  - {plugin}")

    if plugins["rebalancers"]:
        print("\nRebalancers:")
        for plugin in plugins["rebalancers"]:
            print(f"  - {plugin}")