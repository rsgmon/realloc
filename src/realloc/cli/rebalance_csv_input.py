#!/usr/bin/env python3

import argparse
import logging
from pathlib import Path
from typing import List, Optional

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
from realloc.trades import Trade

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def process_rebalance(
    accounts_path: Path,
    allocations_path: Path,
    prices_path: Path,
    max_iterations: int = 100
) -> List[Trade]:
    """
    Process rebalancing using CSV input files.

    Args:
        accounts_path: Path to accounts CSV file
        allocations_path: Path to allocations CSV file
        prices_path: Path to prices CSV file
        max_iterations: Maximum number of rebalancing iterations

    Returns:
        List of trades to execute

    Raises:
        FileNotFoundError: If any input file is missing
        ValueError: If input data is invalid
    """
    # Validate input files exist
    for path in [accounts_path, allocations_path, prices_path]:
        if not path.exists():
            raise FileNotFoundError(f"Input file not found: {path}")

    # Initialize importers
    account_importer = CSVAccountImporter()
    allocation_importer = AllocationCSVImporter()
    price_importer = PricesCSVImporter()
    rebalancer = DefaultRebalancer()

    # Import data
    accounts = account_importer.account_importer(accounts_path)
    model = allocation_importer.import_allocations(
        allocations_path,
        model_name="CSV Portfolio Model"
    )
    prices = price_importer.import_prices(prices_path)

    # Calculate portfolio-level information
    combined_positions, total_cash = calculate_portfolio_positions(accounts)
    target_shares = calculate_target_shares(
        model=model,
        combined_positions=combined_positions,
        total_cash=total_cash,
        prices=prices
    )

    # Calculate portfolio-level trades
    portfolio_trades = compute_portfolio_trades(
        current_shares=combined_positions,
        target_shares=target_shares,
        prices=prices
    )

    # Initialize portfolio state manager and execute rebalance
    psm = PortfolioStateManager(
        accounts=accounts,
        prices=prices,
        portfolio_trades=portfolio_trades
    )

    return rebalancer.execute_rebalance(
        tam=psm,
        target_shares=target_shares,
        max_iterations=max_iterations
    )


def main(args: Optional[List[str]] = None) -> int:
    """
    Main entry point for the CSV rebalance CLI.

    Args:
        args: Command line arguments (optional)

    Returns:
        Exit code (0 for success, non-zero for error)
    """
    parser = argparse.ArgumentParser(
        description="Rebalance portfolio using CSV input files"
    )
    parser.add_argument(
        "--accounts",
        type=Path,
        required=True,
        help="Path to accounts CSV file"
    )
    parser.add_argument(
        "--allocations",
        type=Path,
        required=True,
        help="Path to allocations CSV file"
    )
    parser.add_argument(
        "--prices",
        type=Path,
        required=True,
        help="Path to prices CSV file"
    )
    parser.add_argument(
        "--export",
        type=Path,
        help="Optional path to export trades CSV"
    )
    parser.add_argument(
        "--max-iterations",
        type=int,
        default=100,
        help="Maximum number of rebalancing iterations"
    )

    try:
        parsed_args = parser.parse_args(args)
    except SystemExit as e:
        return e.code

    try:
        trades = process_rebalance(
            parsed_args.accounts,
            parsed_args.allocations,
            parsed_args.prices,
            parsed_args.max_iterations
        )

        # Print results
        print("\nTrades to Execute:")
        if not trades:
            print("No trades required.")
            return 0

        trades_by_account = {}
        for trade in trades:
            if trade.account_id not in trades_by_account:
                trades_by_account[trade.account_id] = []
            trades_by_account[trade.account_id].append(trade)

        for account_id, account_trades in trades_by_account.items():
            print(f"\nAccount: {account_id}")
            for trade in account_trades:
                if trade.symbol == "CASH":
                    continue
                action = "BUY" if trade.shares > 0 else "SELL"
                print(f"  {action} {abs(trade.shares):.2f} {trade.symbol}")

        # Export trades if requested
        if parsed_args.export:
            from realloc.plugins.exporters.csv_exporter import CSVExporter
            exporter = CSVExporter(str(parsed_args.export))
            exporter.export(trades)
            print(f"\nTrades exported to: {parsed_args.export}")

        return 0

    except FileNotFoundError as e:
        logger.error(f"File not found: {e}")
        return 1
    except ValueError as e:
        logger.error(f"Invalid input: {e}")
        return 1
    except Exception as e:
        logger.error(f"Error: {e}")
        return 1

if __name__ == "__main__":
    exit(main())