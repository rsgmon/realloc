# 🧠 Design Principles — realloc

This document explains the key architectural and design choices behind the `realloc` library.

Following these principles ensures the system remains modular, extensible, and reliable for real-world portfolio management.

---

## ✨ 1. Modularity First

- Each realloc component (`Account`, `PortfolioModel`, `PortfolioAllocator`, etc.) has a **single responsibility**.
- Business logic is separated cleanly from orchestration.
- Users can swap pieces (e.g., tax-aware selectors) without rewriting the realloc.

✅ Easy to extend  
✅ Easy to test  
✅ Easy to replace parts without breaking others

---

## 🔁 2. Stateless realloc Functions

- realloc functions (like `allocate_trades`, `split_trades`) are **pure functions** wherever possible.
- No hidden mutation or implicit side-effects.
- Classes like `PortfolioStateManager` explicitly manage portfolio/account state transitions.

✅ Predictable behavior  
✅ Safer concurrency in future versions  
✅ Easier to reason about and debug

---

## 🧩 3. Account-Aware, Portfolio-Level Thinking

- All trade allocation is performed **at the portfolio level**, not account-by-account.
- Individual accounts are updated based on global targets.
- Cash balances and constraints are respected dynamically.

✅ Realistic modeling of actual wealth management workflows

---

## 💵 4. Cash and Constraints are First-Class Citizens

- Each `Account` tracks `cash` independently.
- Rebalancing honors available cash, rounding issues, and prevents overspending.
- Enforcement of rules (e.g., no negative positions) happens at the account level.

✅ Handles real-world frictions  
✅ Safer trading simulations

---

## 🔥 5. Tax Awareness as a Pluggable Concern

- Tax-sensitive behaviors (e.g., selling from taxable first) are injected via **Selector Strategies** (`TaxAwareSelector`).
- The realloc allocator is tax-agnostic by default.

✅ Allows flexibility for future tax rules (harvesting, wash sale detection, etc.)

---

## 🛠 6. Transparent State Transitions

- No hidden changes: rebalancing **explicitly updates** the `PortfolioStateManager`.
- Users can inspect:
  - Planned portfolio trades
  - Updated cash positions
  - Updated security holdings

✅ Full auditability for users and developers

---

## 📈 7. Performance and Scalability

- Algorithms use efficient data structures (dicts, lists) and minimal dependencies.
- Designed to handle:
  - 100s of accounts
  - 1000s of securities
  - Millions of dollars under management

✅ Ready for real-world scale

---

## 🚀 8. Developer-Friendly and Extensible

- Consistent type hints across the project
- Minimal external dependencies (easier for users to install)
- Clear examples and CLI support included
- Tests written using `pytest` with high coverage

✅ Easy for new contributors to understand and improve
✅ Easy for users to automate workflows

---

# 📚 Summary

`realloc` is built to be:

- Modular
- Transparent
- Scalable
- Tax- and constraint-aware
- Developer-first

All contributions should aim to respect and extend these core principles.

---
