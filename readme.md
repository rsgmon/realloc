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
- Fully tested with `pytest`
- Clean, modular, extensible API
- Includes plugin architecture allowing for custom exporters, validators, and rebalancers.

---

## Installation

Clone the repo and install in editable mode:

```bash
git clone https://github.com/yourname/realloc.git
cd realloc
pip install -e .[dev]
```

## Quick Start 

```
from realloc import Account, PortfolioModel, PortfolioAllocator
```

### Define accounts

Accounts must always have a label, account number, Cash balance, and positions

```
accounts = [
    Account("IRA", "A1", 1000, {"AAPL": 5}, {}),
    Account("Taxable", "A2", 2000, {"GOOG": 3}, {})
]
```

### Define a portfolio level target model
```
model = PortfolioModel("Balanced", {"AAPL": 0.5, "GOOG": 0.5})
```
### Define prices
```
prices = {"AAPL": 100, "GOOG": 200}
```

The next step is to calculate portfolio level trades. For that we've provided three functions:

```
from realloc.portfolio import calculate_portfolio_positions, calculate_target_shares
from realloc.trades import compute_portfolio_trades

portfolio_positions = calculate_portfolio_positions(accounts)
target_shares = calculate_target_shares(portfolio_positions[0], portfolio_positions[1], prices, model)
portfolio_trade = compute_portfolio_trades(portfolio_positions[0], target_shares)
```

`PortfolioStateManager`, while not required will help you manage the state of everything while calculating trades. You can roll your own but why?

```
from realloc.portfolio import PortfolioStateManager
portfolio_state = PortfolioStateManager(accounts, prices, portfolio_trade)
```

Now you're ready to try to rebalance. For this quick start we have a basic but tested built-in rebalancer. It's in plugins but you can import directly.

```
from realloc.plugins.rebalancers.default_rebalancer import DefaultRebalancer

rebalancer = DefaultRebalancer()
rebalancer.execute_rebalance(portfolio_state, target_shares, 10)
```

BOOM! Trades. They're not tax-aware, and no constraints like "Don't buy stock DVL" are in place. But that's actually more common than you'd think. So if you're not concerned about taxes or constraints, you'll probably be ok.

But how do I get the trades into a format, so I don't have to hand input. Ah, we have a plugin for exporting. Ours is basic, but you can build a broker-specific one.

```
from realloc.plugins.exporters import csv_exporters
```

But wait, there's more! 

### `rebalance-cli` 
This is a ready-made script that demonstrates a full re-balance (not just a slice re-balance) of realloc. 

Input Format

To use `rebalance-cli`, you must provide a JSON file with:

- `prices`: { symbol → float }
- `accounts`: list of "account" dictionaries
- `model`: `Portfolio` model with `name` and `targets`

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

Ok now what? This is where we try to allow you to take control. Do not get us wrong! We have built ready-made objects to do the work. 

However, if you professionally rebalanced portfolios, you will know there is an art to it and there is not always one answer. But, that topic is for another day.

The api is meant to allow you to do everything from just running our premade scripts to interacting with low level details functions and classes.
```

# Several Plugin Types are available
### 1. Rebalancer PluginsCustomize how trades are allocated across accounts:
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

## Command Line Tools

After installing realloc, the following CLI commands are available:

- `rebalance-cli-json`: Rebalance portfolio using JSON input format
- `rebalance-cli-csv`: Rebalance portfolio using CSV input format
- `partial-rebalance-cli`: Perform partial portfolio rebalancing
- `list-plugins`: Display all available plugins in the system


### Using Plugins with CLI
The `rebalance-cli` supports plugins through command-line arguments:
```
#bash
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