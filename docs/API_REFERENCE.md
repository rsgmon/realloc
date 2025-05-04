# 📚 API Reference: realloc

This document describes the main classes, functions, and interfaces provided by the `realloc` library.

---

## ✨ Core Classes

### `Account`
Manages a single investment account's state.

**Attributes:**
- `label: str`
- `account_number: str`
- `cash: float`
- `positions: Dict[str, float]`
- `targets: Dict[str, float]`
- `enforce_no_negative_positions: bool`

**Key Methods:**
- `to_dict()`
- `from_dict(data: Dict)`

---

### `PortfolioModel`
Defines a target portfolio allocation by symbol.

**Attributes:**
- `name: str`
- `targets: Dict[str, float]`
- `enforce_long_only: bool`

**Key Methods:**
- `normalize()`
- `add_target(symbol: str, weight: float)`
- `update_target(symbol: str, weight: float)`
- `remove_target(symbol: str)`

---

## PortfolioAllocator
High-level API for portfolio-wide trade allocation.

### Initialization:
```
PortfolioAllocator(accounts, model, prices, selector=None)
```

### `Key Methods`:

```
rebalance() -> Dict[str, int]
compute_portfolio_trades()
get_cash_matrix()
get_account_positions()
portfolio_trades (property)
```

---

## TradeAccountMatrix
Internal state manager for accounts during rebalance.

### Key Methods:

```
update(trades: Dict[str, Dict[str, int]])
update_portfolio_trades(target_shares: Dict[str, float])
to_dict()
from_dict(data: Dict, accounts: List[Account])
```

---

## TaxAwareSelector
Smart selector that prefers taxable accounts for sells.

### Initialization:

`TaxAwareSelector(tax_deferred_accounts: List[str])`

### Key Methods:

```
select_account_for_sell_trade(symbol, amount, accounts)
select_account_for_buy_trade(symbol, amount, accounts, prices, cash_matrix)
```

---

## 🛠 Core Utility Functions

```
allocate_trades(current_shares, target_shares, prices=None)
split_trades(current_shares, target_shares, prices=None)
normalize_symbol_sets(current_shares, target_shares)
calculate_sell_amounts(current_amounts, target_amounts)
calculate_buy_amounts(current_amounts, target_amounts)
```

---

## 📦 Additional Modules

- selectors.py: Trade selection strategies
- utils.py: Symbol normalization helpers
- matrix.py: TradeAccountMatrix internals
- trades.py: Allocation calculation logic

## 📚 Notes

All cash calculations assume integer share rounding (no fractional shares).
Negative positions are only allowed if enforce_no_negative_positions=False.
Tax-aware logic is optional and can be injected at runtime.
