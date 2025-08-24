import csv
from collections import defaultdict
from pathlib import Path
from typing import List

from realloc import Account
from realloc.plugins.core.base import AccountImporter


class CSVAccountImporter(AccountImporter):
    """Importer plugin for account positions from CSV files"""

    @property
    def name(self) -> str:
        return "csv_account"

    @property
    def supported_extensions(self) -> List[str]:
        return ['.csv']

    def account_importer(self, path: Path) -> List[Account]:
        """
        Import account data from a CSV file

        Args:
            path: Path to the CSV file

        Returns:
            List of Account objects
        """
        # Group positions by account
        account_positions = defaultdict(dict)
        account_details = {}  # Store account label and ID

        with open(path, 'r', newline='', encoding='utf-8-sig') as csvfile:  # Changed encoding to utf-8-sig
            reader = csv.DictReader(csvfile)

            # Clean up field names to handle BOM and whitespace
            expected_fields = {'Account Label', 'Account Id', 'Symbol', 'Shares'}
            actual_fields = {field.strip() for field in reader.fieldnames or []}

            # Validate required columns
            if not expected_fields.issubset(actual_fields):
                missing = expected_fields - actual_fields
                raise ValueError(f"Missing required columns: {missing}")

            for row in reader:
                # Clean up keys and values
                row = {k.strip(): v.strip() for k, v in row.items()}

                account_id = row['Account Id']
                symbol = row['Symbol']
                # Convert shares to float, handle potential errors
                try:
                    shares = float(row['Shares'])
                except ValueError:
                    raise ValueError(f"Invalid share amount for {symbol}: {row['Shares']}")

                account_positions[account_id][symbol] = shares
                # Store account details (label and ID)
                account_details[account_id] = row['Account Label']

        # Create Account objects
        accounts = []
        for account_id, positions in account_positions.items():
            account = Account(
                label=account_details[account_id],
                account_number=account_id,
                cash=0,  # Default to 0 cash since it's not in CSV
                positions=positions
            )
            accounts.append(account)

        return accounts