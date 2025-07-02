``` markdown
# Plugin Development Guide

## Overview
Realloc's plugin system allows you to create custom exporters for rebalancing data. This guide walks you through creating, testing, and distributing a realloc export plugin.

## Quick Start

### 1. Set Up Your Project
Create a new project with this structure:
```
text realloc-your-plugin/ ├── pyproject.toml ├── src/ │ └── realloc_your_plugin/ │ ├── **init**.py │ └── exporter.py ├── tests/ │ └── test_exporter.py └── README.md
``` 

### 2. Configure Project Files

`pyproject.toml`:
```
toml [project] name = "realloc-your-plugin" version = "0.1.0" description = "Your realloc exporter plugin" dependencies = [ 
[project.entry-points."realloc.plugins"] your_plugin = "realloc_your_plugin.exporter:YourExporter"
latex_unknown_tag
``` 

### 3. Implement Your Exporter
In `src/realloc_your_plugin/exporter.py`:
```
python from realloc.plugins.base import ExportPlugin
class YourExporter(ExportPlugin): def export(self, trades: dict, output_path: str) -> None: """ Export the rebalancing trades data to the specified output path.
    Args:
        trades: Dictionary containing the rebalancing trades data
        output_path: Path where the exported data should be saved
    """
    # Your export logic here
    pass
``` 

## Plugin Interface Reference

### ExportPlugin Base Class
Your plugin must inherit from `ExportPlugin` and implement the `export` method:

```python
def export(self, trades: dict, output_path: str) -> None:
    """
    Args:
        trades: Dictionary containing the rebalancing trades
        output_path: Path where the exported data should be saved
    """
```
```
### Entry Points
Plugins are discovered through the entry point group. The entry point name is what users will use with the `--exporter` flag in the CLI. `realloc.plugins`
## Testing Your Plugin
Create tests in `tests/test_exporter.py`:
``` python
def test_your_exporter(tmp_path):
    exporter = YourExporter()
    trades = {
        "account1": {
            "buys": {"AAPL": 5},
            "sells": {"GOOG": 2}
        }
    }
    output_path = tmp_path / "output.txt"
    exporter.export(trades, str(output_path))
    assert output_path.exists()
```
## Using Your Plugin
### Local Development
Install your plugin in development mode:
``` bash
pip install -e .
```
### Usage
Once installed, use your plugin with:
``` bash
rebalance-cli --exporter your_plugin input.json
```
## Best Practices
1. **Plugin Naming**
    - Use descriptive names that indicate the export format
    - Prefix package with `realloc-` (e.g., `realloc-csvplus`)
    - Use underscores in package/module names (e.g., `realloc_csvplus`)

2. **Error Handling**
    - Handle file I/O errors gracefully
    - Provide meaningful error messages
    - Validate input data before processing

3. **Documentation**
    - Document the format of your export
    - Include example usage in your README
    - Add type hints to your methods

## Common Issues and Solutions
1. **Plugin Not Found**
    - Verify your entry point name matches the CLI argument
    - Check that your package is installed in the correct environment
    - Ensure your entry point is correct `pyproject.toml`

2. **Import Errors**
    - Make sure realloc is installed
    - Check your package structure matches your entry point

3. **File Permission Issues**
    - Handle file permission errors gracefully
    - Document any special requirements for output paths

## Distribution
1. Create a GitHub repository:
``` bash
git init
git add .
git commit -m "Initial plugin implementation"
git remote add origin https://github.com/yourusername/realloc-your-plugin.git
git push -u origin main
```
1. Publish to PyPI:
``` bash
python -m build
python -m twine upload dist/*
```
## Example Plugins
You can look at these plugins for reference:
- Built-in CSV exporter in realloc's source code
- [realloc-csvplus](https://github.com/yourusername/realloc-csvplus) - Enhanced CSV export with metadata
