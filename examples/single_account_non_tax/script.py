import csv
from pathlib import Path
from realloc import Account, PortfolioStateManager, compute_portfolio_trades
from realloc.portfolio import calculate_portfolio_positions, calculate_target_shares
from realloc.plugins.rebalancers.default_rebalancer import DefaultRebalancer
from realloc.plugins.importers.prices.prices_csv import PricesCSVImporter
from realloc.plugins.importers.account.account_csv import CSVAccountImporter
from realloc.plugins.importers.allocation.allocation_csv import AllocationCSVImporter

# Setup paths
example_dir = Path(__file__).parent
input_dir = example_dir / "input"
output_dir = example_dir / "output"
output_dir.mkdir(exist_ok=True)

# Initialize importers
prices_importer = PricesCSVImporter()
account_importer = CSVAccountImporter()
allocation_importer = AllocationCSVImporter()

# Import data using the importers
accounts = account_importer.account_importer(input_dir / "positions.csv")
prices = prices_importer.import_prices(input_dir / "prices.csv")
model = allocation_importer.import_allocations(input_dir / "target_allocation.csv")

# Calculate current portfolio positions
current_portfolio, total_cash = calculate_portfolio_positions(accounts)

# Calculate target shares using calculate_target_shares
target_shares = calculate_target_shares(current_portfolio, total_cash, prices, model)

# Calculate portfolio-level trades
portfolio_trades = compute_portfolio_trades(current_portfolio, target_shares)

# Initialize portfolio manager and rebalancer
portfolio_manager = PortfolioStateManager(accounts, prices, portfolio_trades)
rebalancer = DefaultRebalancer()

# Generate account-level trades
trades = rebalancer.execute_rebalance(portfolio_manager, target_shares, max_iterations=100)
print(trades)
# Save trades
with open(output_dir / "trades.csv", 'w', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=['account_id', 'symbol', 'quantity'])
    writer.writeheader()
    for trade in trades:
        writer.writerow({
            'account_id': trade.account_id,
            'symbol': trade.symbol,
            'quantity': trade.shares
        })

print("Rebalancing completed successfully! Check output/trades.csv for the trades.")