from realloc.plugins.core.base import Exporter
import csv
from typing import Dict, List


class CSVExporter(Exporter):
    def __init__(self, path: str):
        self.path = path

    @property
    def name(self) -> str:
        return "csv"

    def export(self, trades: List[Dict]) -> None:
        with open(self.path, mode="w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["Account", "Symbol", "Shares"])
            for trade in trades:
                writer.writerow([
                    trade['account'],
                    trade['symbol'],
                    trade['shares']
                ])