import argparse
import json
from core import (
    Account,
    PortfolioModel,
    TradeAccountMatrix,
    allocate_trades,
    select_account_for_buy_trade,
    select_account_for_sell_trade,
)


def is_trade_remaining(trades, tolerance: float = 0.01) -> bool:
    return any(abs(qty) > tolerance for qty in trades.values())


def main():
    parser = argparse.ArgumentParser(
        description="Run full rebalance using TradeAccountMatrix"
    )
    parser.add_argument(
        "input_file", help="Path to input JSON file (accounts, model, prices)"
    )
    parser.add_argument(
        "--iterations", type=int, default=10, help="Path to output JSON file"
    )
    parser.add_argument("--exporter", help="Optional exporter plugin name")
    parser.add_argument("--export-path", help="Where to write output file")
    args = parser.parse_args()

    with open(args.input_file, "r") as f:
        data = json.load(f)

    prices = data["prices"]
    accounts = [Account(**acc) for acc in data["accounts"]]
    model = PortfolioModel(**data["model"])

    print("=== Initial Account States ===")
    for acc in accounts:
        print(f"{acc.account_number}: positions={acc.positions}, cash={acc.cash}")

    combined_positions = {}
    total_cash = sum(acc.cash for acc in accounts)
    for acc in accounts:
        for sym, qty in acc.positions.items():
            combined_positions[sym] = combined_positions.get(sym, 0) + qty

    total_value = total_cash + sum(
        qty * prices[sym] for sym, qty in combined_positions.items()
    )
    normalized_model = model.normalize()
    target_dollars = {
        sym: weight * total_value for sym, weight in normalized_model.items()
    }
    target_shares = {sym: target_dollars[sym] / prices[sym] for sym in target_dollars}

    current_shares = combined_positions
    trades = allocate_trades(current_shares, target_shares, prices)

    print("=== Target Portfolio (shares) ===")
    print(target_shares)
    print("=== Current Portfolio (shares) ===")
    print(current_shares)
    print("=== Required Trades ===")
    print(trades)
    print()

    tam = TradeAccountMatrix(accounts, prices, trades)

    max_iterations = args.iterations
    iteration = 0
    account_trades = []
    while is_trade_remaining(tam.portfolio_trades) and iteration < max_iterations:
        sorted_trades = sorted(
            tam.portfolio_trades.items(), key=lambda item: (item[1] > 0, abs(item[1]))
        )

        for symbol, qty in sorted_trades:
            if abs(qty) < 0.1:
                continue
            direction = "buy" if qty > 0 else "sell"
            qty_remaining = abs(qty)

            if direction == "buy":
                account_id = select_account_for_buy_trade(
                    symbol,
                    qty_remaining,
                    list(tam.accounts.values()),
                    prices,
                    tam.cash_matrix,
                )
            else:
                account_id = select_account_for_sell_trade(
                    symbol, qty_remaining, list(tam.accounts.values())
                )

            if account_id is None:
                print(f"⚠️ Cannot find account to {direction} {qty_remaining} {symbol}")
                break

            account = tam.accounts[account_id]
            if direction == "buy":
                max_affordable = int(tam.cash_matrix[account_id] // prices[symbol])
                qty_to_trade = min(qty_remaining, max_affordable)
            else:
                qty_to_trade = min(qty_remaining, int(account.positions.get(symbol, 0)))

            if qty_to_trade == 0:
                break

            single_trade = {
                account_id: {
                    symbol: qty_to_trade if direction == "buy" else -qty_to_trade
                }
            }
            account_trades.append(single_trade)
            print(
                f"🟢 Executing {direction} of {qty_to_trade} {symbol} in account {account_id}"
            )
            tam.update(single_trade)
            tam.update_portfolio_trades(target_shares)
            break  # Re-evaluate after each trade

        iteration += 1

    if iteration >= max_iterations:
        print("⚠️ Max iterations reached. Some trades may be unresolved.")

    print("\n=== Final Account States ===")
    for acc in accounts:
        print(
            f"{acc.account_number}: positions={acc.positions}, cash={tam.cash_matrix[acc.account_number]:.2f}"
        )
    if args.exporter and args.export_path:
        from core.plugins.loader import load_export_plugin

        plugin = load_export_plugin(args.exporter)
        plugin.export(account_trades, args.export_path)
