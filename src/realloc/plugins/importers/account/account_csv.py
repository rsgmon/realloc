from collections import defaultdict
import csv
from pathlib import Path
from typing import List, Dict, Union

from realloc.accounts import Account
from realloc.plugins.core.base import AccountImporter


class CSVAccountImporter(AccountImporter):
    """Importer plugin for account positions from CSV files"""

    CASH_SYMBOL = "CASH"

    @property
    def name(self) -> str:
        return "csv_account"

    @property
    def supported_extensions(self) -> List[str]:
        return ['.csv']

    def account_importer(self, path: Path, return_dicts: bool = False) -> Union[List[Account], List[Dict]]:
        """Import account data from a CSV file. Requires a CASH position for each account."""
        account_positions = defaultdict(dict)
        account_details = {}  # Store account label and ID
        account_has_cash = set()  # Track which accounts have CASH position
        all_accounts = set()  # Track all accounts regardless of positions

        with open(path, 'r', newline='', encoding='utf-8-sig') as csvfile:
            reader = csv.DictReader(csvfile)

            # Clean up field names to handle BOM and whitespace
            expected_fields = {'Account Label', 'Account Id', 'Symbol', 'Shares'}
            actual_fields = {field.strip() for field in reader.fieldnames or []}

            # Validate required columns
            if not expected_fields.issubset(actual_fields):
                missing = expected_fields - actual_fields
                raise ValueError(f"Missing required columns: {missing}")

            for row in reader:
                row = {k.strip(): v.strip() for k, v in row.items()}
                account_id = row['Account Id']
                symbol = row['Symbol']

                # Track all accounts encountered
                all_accounts.add(account_id)

                try:
                    shares = float(row['Shares'])
                except ValueError:
                    raise ValueError(f"Invalid share amount for {symbol}: {row['Shares']}")

                if symbol == self.CASH_SYMBOL:
                    account_has_cash.add(account_id)
                else:
                    account_positions[account_id][symbol] = shares

                account_details[account_id] = row['Account Label']

        # Validate CASH positions
        accounts_without_cash = all_accounts - account_has_cash
        if accounts_without_cash:
            raise ValueError(
                f"The following accounts are missing required CASH position: {', '.join(accounts_without_cash)}"
            )

        # Create accounts list, now including those with only CASH
        accounts = []
        for account_id in all_accounts:
            account_data = {
                "label": account_details[account_id],
                "account_number": account_id,
                "cash": next(
                    float(row['Shares'])
                    for row in csv.DictReader(open(path))
                    if row['Account Id'].strip() == account_id and row['Symbol'].strip() == self.CASH_SYMBOL
                ),
                "positions": account_positions.get(account_id, {}),
                "enforce_no_negative_positions": False
            }

            if return_dicts:
                accounts.append(account_data)
            else:
                accounts.append(Account(**account_data))

        return accounts