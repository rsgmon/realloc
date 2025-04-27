# 📈 Portfolio Allocator

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
git clone https://github.com/yourname/portmgr.git
cd portmgr
pip install -e .[dev]
```

## 🏁 Quick Start 

from core import Account, PortfolioModel, PortfolioAllocator

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

## 🗂 Project Structure

```core/
  accounts.py
  models.py
  trades.py
  selectors.py
  matrix.py
  utils.py
  allocator.py
  __init__.py
tests/
  test_core.py
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