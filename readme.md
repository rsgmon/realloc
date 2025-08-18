# realloc

[//]: # ([![Build Status]&#40;https://github.com/rsgmon/realloc/actions/workflows/ci.yml/badge.svg&#41;]&#40;https://github.com/rsgmon/realloc/actions&#41;)

[//]: # ([![Python Versions]&#40;https://img.shields.io/pypi/pyversions/realloc&#41;]&#40;https://www.python.org/&#41;)

[//]: # ([![License]&#40;https://img.shields.io/github/license/rsgmon/realloc&#41;]&#40;LICENSE&#41;)

[//]: # ([![Coverage]&#40;https://img.shields.io/badge/Coverage-84%25-brightgreen&#41;]&#40;htmlcov/index.html&#41;)

---

A modular Python library for managing and rebalancing multi-account investment portfolios.

It handles account-aware trade allocation, portfolio-level targets, and execution constraints across multiple real-world accounts.

---

## Features

- Allocate trades across multiple accounts
- Enforce constraints (e.g. no negative positions, long-only models)
- Simulate rebalancing with real-time cash and price updates
- Split trades into buys and sells
- Fully tested with `pytest`
- Clean, modular, extensible API

---

## Installation

Clone the repo and install in editable mode:

```bash
git clone https://github.com/yourname/realloc.git
cd realloc
pip install -e .[dev]
```

## Quick Start 

from realloc import Account, PortfolioModel, PortfolioAllocator

### Define accounts
accounts = [
    Account("IRA", "A1", 1000, {"AAPL": 5}, {}),
    Account("Taxable", "A2", 2000, {"GOOG": 3}, {})
]

### Define target model
model = PortfolioModel("Balanced", {"AAPL": 0.5, "GOOG": 0.5})

### Define prices
prices = {"AAPL": 100, "GOOG": 200}

### Allocate trades
allocator = PortfolioAllocator(accounts, model, prices)
trades = allocator.rebalance()

print(trades)

### `rebalance-cli` 
This is a ready-made script that demonstrates a full re-balance (not just a slice re-balance) of realloc. 

Input Format

To use `rebalance-cli`, you must provide a JSON file with:

- `prices`: { symbol → float }
- `accounts`: list of account dictionaries
- `model`: portfolio model with `name` and `targets`

Example:
```json
{
  "prices": { "AAPL": 100, "GOOG": 100 },
  "accounts": [
    { "label": "A", "account_number": "1", "cash": 1000, "positions": { "AAPL": 5 } }
  ],
  "model": {
    "label": "Balanced",
    "targets": { "AAPL": 0.6, "GOOG": 0.4 }
  }
}
```

# Several Plugin Types are available
### 1. Rebalancer Plugins
Customize how trades are allocated across accounts:
```
from realloc import PortfolioModel, Account, PortfolioStateManager from realloc.plugins.core.base import RebalancerPlugin
```
#### Use the default rebalancer
```
rebalancer = RebalancerPlugin.load_rebalancer("default")
```

#### Execute rebalance using the plugin
```
trades = rebalancer.execute_rebalance( tam=PortfolioStateManager(...), target_shares={"F":100, "HPQ":50}
```


### 2. Export Plugins
Format trades for different brokers:

```
from realloc.plugins.core.base import Exporter
```
### Export trades to CSV
```
exporter = Exporter.load_exporter("csv", path="trades.csv") exporter.export(trades)
```


### 3. Validator Plugins
Add custom trade validation rules:
```
from realloc.plugins.core.base import TradeValidator
# Validate minimum trade value
validator = TradeValidator.load_validator("minimum_value", min_value=100) is_valid, message = validator.validate(trade)
``` 

### Using Plugins with CLI
The `rebalance-cli` supports plugins through command-line arguments:
```
bash
# List available plugins
list-plugins
# Use an exporter plugin
rebalance-cli input.json --exporter csv --export-path trades.csv
``` 

### Available Plugins
- **Rebalancers**:
  - `default`: Standard rebalancing algorithm
- **Exporters**:
  - `csv`: Export trades to CSV format
- **Validators**:
  - `max_position`: Enforce maximum position sizes
  - `minimum_value`: Enforce minimum trade values
```

## 📄 License

MIT License.

## 🙌 Contributing

Pull requests welcome!
Please open an issue or contact first if proposing large changes.