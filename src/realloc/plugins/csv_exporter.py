import csv


def export(trades: list, path: str):
    with open(path, mode="w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Account", "Symbol_Quantity"])
        for trade in trades:
            for account, sym_qty in trade.items():
                writer.writerow([account, sym_qty])
