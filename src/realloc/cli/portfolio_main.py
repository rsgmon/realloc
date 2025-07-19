import argparse
import json
import sys
from realloc import Account, PortfolioModel, PortfolioStateManager, compute_portfolio_trades
from realloc.plugins.core.discovery import list_plugins



def load_json(path):
    with open(path, "r") as f:
        return json.load(f)


def main():
    if len(sys.argv) > 1 and sys.argv[1] == "list-plugins":
        list_plugins()
        return
    parser = argparse.ArgumentParser(description="Portfolio Allocator CLI")
    parser.add_argument(
        "--rebalance", help="Path to input JSON with accounts, model, and prices"
    )
    parser.add_argument("--exporter", help="Optional exporter plugin name")
    parser.add_argument("--export-path", help="Where to write output file")
    args = parser.parse_args()

    if args.rebalance:
        data = load_json(args.rebalance)

        # Load model
        model = PortfolioModel("Target", data["model"])

        # Load accounts
        accounts = [Account.from_dict(acc) for acc in data["accounts"]]

        # Compute total value and targets
        prices = data["prices"]
        combined = {}
        total_cash = sum(a["cash"] for a in data["accounts"])
        for acc in data["accounts"]:
            for sym, qty in acc["positions"].items():
                combined[sym] = combined.get(sym, 0) + qty

        total_value = total_cash + sum(
            qty * prices[sym] for sym, qty in combined.items()
        )
        target_shares = {
            sym: (weight * total_value) / prices[sym]
            for sym, weight in model.normalize().items()
        }

        trades = compute_portfolio_trades(combined, target_shares, prices)
        tam = PortfolioStateManager(accounts, prices, trades)

        print("📈 Planned Trades:")
        print(json.dumps(tam.portfolio_trades, indent=2))

        print("\n📊 Final Account States:")
        for acc in accounts:
            print(
                f"{acc.account_number} => positions: {acc.positions}, cash: {tam.cash_matrix[acc.account_number]:.2f}"
            )
        if args.exporter and args.export_path:
            from realloc.plugins import load_export_plugin

            plugin = load_export_plugin(args.exporter)
            plugin.export(tam.portfolio_trades, args.export_path)


if __name__ == "__main__":
    main()
