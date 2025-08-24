from pathlib import Path
from datetime import datetime
import logging

from realloc.plugins.importers.account.account_csv import CSVAccountImporter
from realloc.plugins.importers.allocation.allocation_csv import AllocationCSVImporter
from realloc.plugins.importers.prices.prices_csv import PricesCSVImporter
from realloc.plugins.rebalancers.default_rebalancer import DefaultRebalancer
from realloc.portfolio import (
    PortfolioStateManager,
    calculate_portfolio_positions,
    calculate_target_shares,
    compute_portfolio_trades
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def main():
    # Initialize importers
    account_importer = CSVAccountImporter()
    allocation_importer = AllocationCSVImporter()
    price_importer = PricesCSVImporter()
    rebalancer = DefaultRebalancer()

    # Import data from CSV files
    accounts = account_importer.account_importer(Path("../../sample_positions.csv"))
    model = allocation_importer.import_allocations(
        Path("../../sample_allocations.csv"),
        model_name="Portfolio Model"
    )
    prices = price_importer.import_prices(Path("../../sample_prices.csv"))

    # Calculate portfolio-level information
    combined_positions, total_cash = calculate_portfolio_positions(accounts)
    target_shares = calculate_target_shares(
        combined_positions=combined_positions,
        total_cash=total_cash,
        prices=prices,
        model=model
    )

    # Calculate portfolio-level trades
    portfolio_trades = compute_portfolio_trades(
        current_shares=combined_positions,
        target_shares=target_shares,
        prices=prices
    )

    # Initialize portfolio state manager with the portfolio-level trades
    psm = PortfolioStateManager(
        accounts=accounts,
        prices=prices,
        portfolio_trades=portfolio_trades
    )

    # Execute rebalancing
    trades = rebalancer.execute_rebalance(
        tam=psm,
        target_shares=target_shares,
        max_iterations=100
    )

    # Print results
    print("\n=== Initial State ===")
    total_value = total_cash + sum(
        shares * prices[symbol]
        for symbol, shares in combined_positions.items()
    )
    print(f"Total Portfolio Value: ${total_value:,.2f}")
    print(f"Total Cash: ${total_cash:,.2f}")

    print("\nCurrent Positions:")
    for symbol, shares in combined_positions.items():
        current_value = shares * prices[symbol]
        current_weight = current_value / total_value
        print(f"{symbol}: {shares:.2f} shares (${current_value:,.2f}, {current_weight:.1%})")

    print("\n=== Target Allocations ===")
    normalized_weights = model.normalize()
    for symbol, weight in normalized_weights.items():
        target_value = weight * total_value
        print(f"{symbol}: {weight:.1%} (${target_value:,.2f})")

    print("\n=== Portfolio Level Trades Required ===")
    for symbol, quantity in portfolio_trades.items():
        value = abs(quantity * prices[symbol])
        print(f"{symbol}: {quantity:+.2f} shares (${value:,.2f})")

    print("\n=== Account Level Trades to Execute ===")
    trades_by_account = {}
    for trade in trades:
        if trade.account_id not in trades_by_account:
            trades_by_account[trade.account_id] = []
        trades_by_account[trade.account_id].append(trade)

    for account_id, account_trades in trades_by_account.items():
        account = next(acc for acc in accounts if acc.account_number == account_id)
        print(f"\nAccount: {account.label} ({account_id})")
        total_buys = 0
        total_sells = 0
        for trade in account_trades:
            action = "BUY" if trade.shares > 0 else "SELL"
            value = abs(trade.shares * prices[trade.symbol])
            if trade.shares > 0:
                total_buys += value
            else:
                total_sells += value
            print(f"  {action} {abs(trade.shares):.2f} {trade.symbol} (${value:,.2f})")
        print(f"  Total Buys: ${total_buys:,.2f}")
        print(f"  Total Sells: ${total_sells:,.2f}")

    print("\n=== Final State ===")
    for account in accounts:
        print(f"\nAccount: {account.label} ({account.account_number})")
        print(f"Cash: ${psm.cash_matrix[account.account_number]:,.2f}")
        print("Positions:")
        account_value = psm.cash_matrix[account.account_number]
        for symbol, shares in account.positions.items():
            value = shares * prices[symbol]
            account_value += value
            print(f"  {symbol}: {shares:.2f} shares (${value:,.2f})")
        print(f"Total Account Value: ${account_value:,.2f}")


if __name__ == "__main__":
    main()