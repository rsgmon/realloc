# Stress Test: 100 Accounts, 200 Symbols
import random
from realloc import Account, PortfolioModel, PortfolioAllocator

# Generate random symbols
symbols = [f"SYM{i:03d}" for i in range(200)]

# Generate random prices between $10 and $500
prices = {sym: random.uniform(10, 500) for sym in symbols}

# Generate random accounts
accounts = []
for i in range(100):
    label = f"Account-{i+1}"
    account_number = f"A{i+1}"
    cash = random.uniform(1000, 10000)

    # Randomly assign 10-30 positions per account
    positions = {}
    for sym in random.sample(symbols, random.randint(10, 30)):
        positions[sym] = random.randint(1, 100)

    accounts.append(Account(label, account_number, cash, positions, {}))

# Create a target model (even weights across all symbols)
model = PortfolioModel(
    "Massive Diversified Portfolio",
    {sym: 1/len(symbols) for sym in symbols}
)

# Create allocator
allocator = PortfolioAllocator(accounts, model, prices)

# Run rebalance
print("Running massive rebalance...")
portfolio_trades = allocator.rebalance()

# Output stats
print("\n--- Rebalance Summary ---")
print(f"Number of symbols in model: {len(model.targets)}")
print(f"Number of portfolio trades planned: {len(portfolio_trades)}")
print(f"Number of accounts rebalanced: {len(accounts)}")
