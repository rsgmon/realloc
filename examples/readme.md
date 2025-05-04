# 📚 Portfolio Allocator Examples

This folder contains ready-to-run examples demonstrating how to use `realloc` to allocate and rebalance portfolios.

Each example highlights a different real-world use case.

---

## ✨ Examples Included

| File | Purpose |
|-----|---------|
| `basic_rebalance.ipynb` | Intro example: two accounts, two symbols, simple rebalance |
| `multi_account_rebalance.ipynb` | Simulates multiple accounts and cash-constrained rebalancing |
| `tax_aware_rebalance.ipynb` | Demonstrates tax-aware selling using `TaxAwareSelector` |
| `stress_test_rebalance.py` | Stress test: 100 accounts, 200 symbols, massive rebalancing |

---

## 🏁 How to Run

If you are using Jupyter notebooks:

```bash
cd examples/
jupyter notebook
```

Or run the stress test script directly:
`python examples/stress_test_rebalance.py`

Make sure you've installed all dependencies with:
`pip install -e .[dev]`