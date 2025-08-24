import argparse
import json
import logging
import sys
from pathlib import Path
from typing import Dict, List, Any

from realloc import (
    Account,
    PortfolioModel,
    Trade,
    PortfolioStateManager,
    is_trade_remaining,
)
from realloc.plugins.core.discovery import list_plugins
from realloc.plugins.core.base import Exporter
from realloc.portfolio import calculate_portfolio_positions, calculate_target_shares, compute_portfolio_trades
from realloc.selectors import select_account_for_buy_trade, select_account_for_sell_trade

# Constants
MIN_TRADE_QTY = 0.1
DEFAULT_MAX_ITERATIONS = 10

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def load_and_validate_input(input_file: Path) -> Dict[str, Any]:
    """
    Load and validate the input JSON file containing accounts, model, and prices.

    Args:
        input_file: Path to the JSON input file

    Returns:
        Dict containing validated data

    Raises:
        ValueError: If input data is invalid or missing required fields
    """
    with open(input_file) as f:
        data = json.load(f)

    required_keys = ["prices", "accounts", "model"]
    if missing := set(required_keys) - set(data.keys()):
        raise ValueError(f"Missing required keys in input file: {missing}")

    if not isinstance(data["prices"], dict):
        raise ValueError("Prices must be a dictionary mapping symbols to prices")

    if not all(isinstance(p, (int, float)) and p > 0 for p in data["prices"].values()):
        raise ValueError("All prices must be positive numbers")

    if not isinstance(data["accounts"], list):
        raise ValueError("Accounts must be a list of account objects")

    if not isinstance(data["model"], dict):
        raise ValueError("Model must be a dictionary with 'label' and 'targets' fields")

    if "label" not in data["model"] or "targets" not in data["model"]:
        raise ValueError("Model must contain 'label' and 'targets' fields")

    return data


def execute_rebalance(
        tam: PortfolioStateManager,
        target_shares: Dict[str, float],
        max_iterations: int
) -> List[Trade]:
    """
    Execute the rebalancing trades across accounts.

    Args:
        tam: Trade Account Matrix instance
        target_shares: Dictionary of target shares per symbol
        max_iterations: Maximum number of iterations to attempt

    Returns:
        List of executed trades
    """
    iteration = 0
    account_trades = []

    while is_trade_remaining(tam.portfolio_trades) and iteration < max_iterations:
        sorted_trades = sorted(
            tam.portfolio_trades.items(),
            key=lambda item: (item[1] > 0, abs(item[1]))
        )

        for symbol, qty in sorted_trades:
            if abs(qty) < MIN_TRADE_QTY:
                continue

            direction = "buy" if qty > 0 else "sell"
            qty_remaining = abs(qty)

            # Select account for trade
            account_id = (
                select_account_for_buy_trade(
                    symbol,
                    qty_remaining,
                    list(tam.accounts.values()),
                    tam.prices,
                    tam.cash_matrix,
                )
                if direction == "buy"
                else select_account_for_sell_trade(
                    symbol, qty_remaining, list(tam.accounts.values())
                )
            )

            if account_id is None:
                logger.warning(f"Cannot find account to {direction} {qty_remaining} {symbol}")
                break

            # Calculate trade quantity
            account = tam.accounts[account_id]
            if direction == "buy":
                max_affordable = int(tam.cash_matrix[account_id] // tam.prices[symbol])
                qty_to_trade = min(qty_remaining, max_affordable)
            else:
                qty_to_trade = min(qty_remaining, int(account.positions.get(symbol, 0)))

            if qty_to_trade == 0:
                break

            # Execute trade
            trade_qty = qty_to_trade if direction == "buy" else -qty_to_trade
            single_trade = Trade(account_id, symbol, trade_qty)
            account_trades.append(single_trade)

            logger.info(
                f"Executing {direction} of {qty_to_trade} {symbol} in account {account_id}"
            )

            tam.update([single_trade])
            tam.update_portfolio_trades(target_shares)
            break  # Re-evaluate after each trade

        iteration += 1

    if iteration >= max_iterations:
        logger.warning("Max iterations reached. Some trades may be unresolved.")

    return account_trades


def main():
    """
    Main entry point for the rebalance script.
    Demonstrates portfolio rebalancing across multiple accounts using the realloc library.
    """
    if len(sys.argv) > 1 and sys.argv[1] == "list-plugins":
        list_plugins()
        return

    parser = argparse.ArgumentParser(
        description="Run full rebalance using PortfolioStateManager"
    )
    parser.add_argument(
        "input_file",
        type=Path,
        help="Path to input JSON file (accounts, model, prices)"
    )
    parser.add_argument(
        "--iterations",
        type=int,
        default=DEFAULT_MAX_ITERATIONS,
        help="Maximum number of rebalancing iterations"
    )
    parser.add_argument("--exporter", help="Optional exporter plugin name")
    parser.add_argument("--export-path", type=Path, help="Where to write output file")
    args = parser.parse_args()

    # Load and validate input data
    data = load_and_validate_input(args.input_file)

    # Initialize objects
    prices = data["prices"]
    accounts = [Account(**acc) for acc in data["accounts"]]
    model = PortfolioModel(data["model"]["label"], data["model"]["targets"])

    # Log initial state
    logger.info("=== Initial Account States ===")
    for acc in accounts:
        logger.info(f"{acc.account_number}: positions={acc.positions}, cash={acc.cash}")

    # Calculate target portfolio
    combined_positions, total_cash = calculate_portfolio_positions(accounts)
    target_shares = calculate_target_shares(combined_positions, total_cash, prices, model)
    portfolio_level_trades = compute_portfolio_trades(combined_positions, target_shares, prices)

    # Log target state
    logger.info("=== Target Portfolio (shares) ===")
    logger.info(target_shares)
    logger.info("=== Current Portfolio (shares) ===")
    logger.info(combined_positions)
    logger.info("=== Required Trades ===")
    logger.info(portfolio_level_trades)

    # Execute rebalance
    tam = PortfolioStateManager(accounts, prices, portfolio_level_trades)
    account_trades = execute_rebalance(tam, target_shares, args.iterations)

    # Log final state
    logger.info("\n=== Final Account States ===")
    for acc in accounts:
        logger.info(
            f"{acc.account_number}: positions={acc.positions}, "
            f"cash={tam.cash_matrix[acc.account_number]:.2f}"
        )

    # Export results if requested
    if args.exporter and args.export_path:
        plugin = Exporter.load_export_plugin(args.exporter, args.export_path)
        plugin.export(account_trades)

    return [trade.to_dict() for trade in account_trades]


if __name__ == "__main__":
    main()