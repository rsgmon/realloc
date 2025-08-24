import argparse
import json
import sys
from realloc import (
    Account,
    PortfolioModel,
    Trade,
    PortfolioStateManager,
    compute_portfolio_trades,
    select_account_for_buy_trade,
    select_account_for_sell_trade,
)
from realloc.plugins.core.discovery import list_plugins


def main():
    if len(sys.argv) > 1 and sys.argv[1] == "list-plugins":
        list_plugins()
        return
    parser = argparse.ArgumentParser(
        description="Perform partial rebalance for two symbols using model targets"
    )
    parser.add_argument("input_file", help="Path to input JSON file")
    parser.add_argument("--sell-symbol", required=True, help="Symbol to sell")
    parser.add_argument("--buy-symbol", required=True, help="Symbol to buy")
    parser.add_argument("--exporter", help="Optional exporter plugin name")
    parser.add_argument("--export-path", help="Where to write output file")

    args = parser.parse_args()

    # Load input
    with open(args.input_file, "r") as f:
        data = json.load(f)

    prices = data["prices"]
    accounts = [Account(**acc) for acc in data["accounts"]]
    model = PortfolioModel(**data["model"])

    tam = PortfolioStateManager(accounts, prices)

    # Step 1: Compute current portfolio holdings
    combined_positions = {}
    total_cash = sum(acc.cash for acc in accounts)
    for acc in accounts:
        for sym, qty in acc.positions.items():
            combined_positions[sym] = combined_positions.get(sym, 0) + qty

    # Step 2: Compute model-based target trades
    total_value = total_cash + sum(
        qty * prices[sym] for sym, qty in combined_positions.items()
    )
    normalized = model.normalize()
    target_dollars = {sym: weight * total_value for sym, weight in normalized.items()}
    target_shares = {sym: target_dollars[sym] / prices[sym] for sym in target_dollars}
    all_trades = compute_portfolio_trades(combined_positions, target_shares, prices)

    # Step 3: Extract only the two symbols
    buy_symbol = args.buy_symbol
    sell_symbol = args.sell_symbol
    trades = {
        k: all_trades[k]
        for k in [buy_symbol, sell_symbol]
        if k in all_trades and abs(all_trades[k]) >= 1
    }

    if not trades:
        print("⚠️ No relevant trades found for specified symbols.")
        return

    print(f"🎯 Target trades from model:")
    for sym in trades:
        print(f" - {sym}: {trades[sym]} shares")

    # Step 4: Execute sell first
    if sell_symbol in trades and trades[sell_symbol] < 0:
        qty_remaining = abs(trades[sell_symbol])
        for _ in range(10):
            account_id = select_account_for_sell_trade(
                sell_symbol, qty_remaining, list(tam.accounts.values())
            )
            if not account_id:
                print(f"⚠️ Could not find account to sell {qty_remaining} {sell_symbol}")
                break
            acc = tam.accounts[account_id]
            sell_qty = min(qty_remaining, acc.positions.get(sell_symbol, 0))
            single_trade = Trade(account_id, sell_symbol, sell_qty)
            tam.update([single_trade])
            print(f"✅ Sold {sell_qty} of {sell_symbol} from {account_id}")
            qty_remaining -= sell_qty
            if qty_remaining <= 0:
                break

    # Step 5: Attempt to buy
    qty_remaining = trades.get(buy_symbol, 0)
    price = prices[buy_symbol]
    for _ in range(10):
        account_id = select_account_for_buy_trade(
            buy_symbol,
            qty_remaining,
            list(tam.accounts.values()),
            prices,
            tam.cash_matrix,
        )
        if not account_id:
            break
        max_affordable = int(tam.cash_matrix[account_id] // price)
        if max_affordable == 0:
            break
        buy_qty = min(max_affordable, qty_remaining)
        single_trade = Trade(account_id, buy_symbol, buy_qty)
        tam.update([single_trade])
        print(f"✅ Bought {buy_qty} of {buy_symbol} in {account_id}")
        qty_remaining -= buy_qty
        if qty_remaining <= 0:
            break

    # Step 6: Raise cash if buy incomplete
    if qty_remaining > 0:
        print(
            f"⚠️ Not enough cash to complete buy. Raising funds via overweight symbols..."
        )
        combined = {}
        for acc in tam.accounts.values():
            for sym, qty in acc.positions.items():
                combined[sym] = combined.get(sym, 0) + qty

        total_value = sum(qty * prices[sym] for sym, qty in combined.items()) + sum(
            tam.cash_matrix.values()
        )
        target_dollars = {
            sym: normalized.get(sym, 0) * total_value for sym in normalized
        }
        actual_dollars = {sym: combined.get(sym, 0) * prices[sym] for sym in combined}

        overweight = {
            sym: actual_dollars[sym] - target_dollars.get(sym, 0)
            for sym in actual_dollars
            if actual_dollars[sym] > target_dollars.get(sym, 0)
        }

        sorted_ow = sorted(overweight.items(), key=lambda x: x[1], reverse=True)
        for sym, _ in sorted_ow:
            for acc in tam.accounts.values():
                holding = acc.positions.get(sym, 0)
                if holding == 0:
                    continue
                qty_to_sell = min(
                    holding, int((qty_remaining * price) // prices[sym]) + 1
                )
                single_trade = Trade(acc.account_number, sym, -qty_to_sell)
                tam.update([single_trade])
                print(
                    f"💸 Sold {qty_to_sell} of overweight {sym} from {acc.account_number}"
                )
                break

            # Reattempt buy
            account_id = select_account_for_buy_trade(
                buy_symbol,
                qty_remaining,
                list(tam.accounts.values()),
                prices,
                tam.cash_matrix,
            )
            if account_id:
                max_affordable = int(tam.cash_matrix[account_id] // price)
                if max_affordable:
                    buy_qty = min(max_affordable, qty_remaining)
                    single_trade = Trade(account_id, buy_symbol, buy_qty)
                    tam.update([single_trade])
                    print(f"🔁 Bought {buy_qty} of {buy_symbol} in {account_id}")
                    qty_remaining -= buy_qty
                    if qty_remaining <= 0:
                        break

    print("\n=== Final Account States ===")
    for acc in tam.accounts.values():
        print(
            f"{acc.account_number}: positions={acc.positions}, cash={tam.cash_matrix[acc.account_number]:.2f}"
        )
    if args.exporter and args.export_path:
        from realloc.plugins import load_export_plugin

        plugin = load_export_plugin(args.exporter)
        plugin.export(tam.portfolio_trades, args.export_path)
