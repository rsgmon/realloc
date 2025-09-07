from datetime import datetime
import csv
from pathlib import Path
from typing import Dict, List

from realloc.plugins.core.base import PriceImporter


class PricesCSVImporter(PriceImporter):
    """CSV implementation of price importer plugin"""

    @property
    def name(self) -> str:
        return "price_csv"

    @property
    def supported_extensions(self) -> List[str]:
        return ['.csv']

    def import_prices(self, path: Path, date: datetime = None) -> Dict[str, float]:
        """
        Import price data from a CSV file

        Args:
            path: Path to the CSV file
            date: Optional date for historical prices. If None, uses most recent price.

        Returns:
            Dict mapping symbols to their prices
        """
        prices = {}

        with open(path, 'r', newline='', encoding='utf-8-sig') as csvfile:
            reader = csv.DictReader(csvfile)

            # Validate required columns
            expected_fields = {'Symbol', 'Price'}
            if date:
                expected_fields.add('Date')

            actual_fields = {field.strip() for field in reader.fieldnames or []}

            if not expected_fields.issubset(actual_fields):
                missing = expected_fields - actual_fields
                raise ValueError(f"Missing required columns: {missing}")

            # Process rows
            for row in reader:
                row = {k.strip(): v.strip() for k, v in row.items()}

                # Skip rows not matching the requested date
                if date and row.get('Date'):
                    row_date = datetime.strptime(row['Date'], '%Y-%m-%d')
                    if row_date.date() != date.date():
                        continue

                symbol = row['Symbol']
                try:
                    price = float(row['Price'])
                except ValueError:
                    raise ValueError(f"Invalid price for {symbol}: {row['Price']}")

                if price <= 0:
                    raise ValueError(f"Price must be positive for {symbol}: {price}")

                prices[symbol] = price

        if not prices:
            raise ValueError("No valid prices found in CSV file")

        return prices