# realloc

[//]: # ([![Build Status]&#40;https://github.com/rsgmon/realloc/actions/workflows/ci.yml/badge.svg&#41;]&#40;https://github.com/rsgmon/realloc/actions&#41;)

[//]: # ([![Python Versions]&#40;https://img.shields.io/pypi/pyversions/realloc&#41;]&#40;https://www.python.org/&#41;)

[//]: # ([![License]&#40;https://img.shields.io/github/license/rsgmon/realloc&#41;]&#40;LICENSE&#41;)

[//]: # ([![Coverage]&#40;https://img.shields.io/badge/Coverage-84%25-brightgreen&#41;]&#40;htmlcov/index.html&#41;)

---


A modular Python library for managing and rebalancing multi-account investment portfolios.

It handles account-aware trade allocation, portfolio-level targets, and execution constraints across multiple real-world accounts.

---

## 🚀 Features

- Allocate trades across multiple accounts
- Enforce constraints (e.g. no negative positions, long-only models)
- Simulate rebalancing with real-time cash and price updates
- Split trades into buys and sells
- Fully tested with `pytest`
- Clean, modular, extensible API

---

## 📦 Installation

Clone the repo and install in editable mode:

```bash
git clone https://github.com/yourname/realloc.git
cd realloc
pip install -e .[dev]
```

## 🏁 Quick Start 

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

### 📄 `rebalance-cli` 
This is a ready-made script that demonstrates a full re-balance (not just a slice re-balance) of realloc. 

Input Format

To use `rebalance-cli`, you must provide a JSON file with:

- `prices`: { symbol → float }
- `accounts`: list of account dictionaries
- `model`: portfolio model with `name` and `targets`

📂 Example:
```json
{
  "prices": { "AAPL": 100, "GOOG": 100 },
  "accounts": [
    { "label": "A", "account_number": "1", "cash": 1000, "positions": { "AAPL": 5 }, "targets": {} }
  ],
  "model": {
    "name": "Balanced",
    "targets": { "AAPL": 0.6, "GOOG": 0.4 }
  }
}


## 🗂 Project Structure

```
src/
  realloc/
    plugins/
      base.py
      csv_exporter.py
      loader.py
    cli/
      reblance-cli
      portfolio-cli
    accounts.py
    models.py
    trades.py
    selectors.py
    matrix.py
    utils.py
    allocator.py
    __init__.py
  tests/
    test_realloc.py
  Dockerfile
  Makefile
  README.md
  setup.py
```

## 📄 License

MIT License.

## 🙌 Contributing

Pull requests welcome!
Please open an issue or contact first if proposing large changes.