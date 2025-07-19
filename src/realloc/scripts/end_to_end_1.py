from realloc import *

from typing import Dict

from realloc import Trade

# (existing classes/functions here...)

# --- Rebalance Simulation Block ---
if __name__ == "__main__":
    prices = {"AAPL": 100, "GOOG": 100, "MSFT": 100, "IBM": 34.56}

    accounts = [
        Account("Account A", "A", 99, {"AAPL": 10, "IBM": 5000}, {}),
        Account("Account B", "B", 80000, {"GOOG": 4, "MSFT": 5}, {}),
        Account("Account C", "C", 0, {"AAPL": 50}, {}),
    ]

    model = PortfolioModel("Balanced", {"AAPL": 0.5, "GOOG": 0.4, "MSFT": 0.1})

    print("=== Initial Account States ===")
    for acc in accounts:
        print(f"{acc.account_number}: positions={acc.positions}, cash={acc.cash}")

    combined_positions = {}
    total_cash = 0
    for acc in accounts:
        total_cash += acc.cash
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
    trades = compute_portfolio_trades(current_shares, target_shares, prices)

    print("=== Target Portfolio (shares) ===")
    print(target_shares)
    print("=== Current Portfolio (shares) ===")
    print(current_shares)
    print("=== Required Trades ===")
    print(trades)
    print()

    tam = PortfolioStateManager(accounts, prices, trades)

    def is_trade_remaining(trades: Dict[str, int], tolerance: float = 0.01) -> bool:
        return any(abs(qty) > tolerance for qty in trades.values())

    max_iterations = 10
    iteration = 0

    while is_trade_remaining(tam.portfolio_trades) and iteration < max_iterations:
        sorted_trades = sorted(
            tam.portfolio_trades.items(), key=lambda item: (item[1] > 0, abs(item[1]))
        )
        # print(f"sorted trades {sorted_trades}")
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
            print(f"Selected Account_id: {account_id}")
            print(f"\n🔍 Evaluating trade for {symbol}: {qty} ({direction})")
            print(f"Remaining qty needed: {qty_remaining}")
            print("📊 Account states:")
            for acc in tam.accounts.values():
                holding = acc.positions.get(symbol, 0)
                cash = tam.cash_matrix[acc.account_number]
                can_afford = int(cash // prices[symbol])
                print(
                    f"Account {acc.account_number} | Holds: {holding} | Cash: {cash:.2f} | Can afford: {can_afford} {symbol}"
                )

            account = tam.accounts[account_id]
            if direction == "buy":
                max_affordable = int(tam.cash_matrix[account_id] // prices[symbol])
                qty_to_trade = min(qty_remaining, max_affordable)
            else:
                qty_to_trade = min(qty_remaining, int(account.positions.get(symbol, 0)))

            if qty_to_trade == 0:
                break
            single_trade = Trade(account_id, symbol, qty_to_trade if direction == "buy" else -qty_to_trade)

            print(
                f"🟢 Executing {direction} of {qty_to_trade} {symbol} in account {account_id}"
            )
            tam.update([single_trade])

            tam.update_portfolio_trades(target_shares)
            print(
                f"Is Trade Remaining: {is_trade_remaining(tam.portfolio_trades, tolerance=0.1)}"
            )
            break  # Re-evaluate trades after each execution
        iteration += 1

    if iteration >= max_iterations:
        print(
            "⚠️ Maximum iterations reached. Possible infinite loop or unresolvable trade drift."
        )

    print("\n=== Final Account States ===")
    for acc in accounts:
        print(
            f"{acc.account_number}: positions={acc.positions}, cash={tam.cash_matrix[acc.account_number]:.2f}"
        )
