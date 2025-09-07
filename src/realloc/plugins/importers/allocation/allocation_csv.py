from pathlib import Path
import csv
from typing import Dict, List, Union

from realloc.models import PortfolioModel
from realloc.plugins.core.base import AllocationImporter


class AllocationCSVImporter(AllocationImporter):
    """CSV implementation of allocation importer plugin"""

    @property
    def name(self) -> str:
        return "allocation_csv"

    @property
    def supported_extensions(self) -> List[str]:
        return ['.csv']

    def import_allocations(
        self, 
        path: Path, 
        return_dict: bool = False,
        model_name: str = "CSV Import"
    ) -> Union[PortfolioModel, Dict[str, float]]:
        """
        Import target allocation data from a CSV file

        Args:
            path: Path to the CSV file
            return_dict: If True, returns dictionary instead of PortfolioModel object
            model_name: Name to use for the PortfolioModel if created

        Returns:
            Either a PortfolioModel object or dict mapping symbols to their target allocation weights
        """
        allocations = {}

        with open(path, 'r', newline='', encoding='utf-8-sig') as csvfile:
            reader = csv.DictReader(csvfile)

            # Validate required columns
            expected_fields = {'Symbol', 'Target Weight'}
            actual_fields = {field.strip() for field in reader.fieldnames or []}

            if not expected_fields.issubset(actual_fields):
                missing = expected_fields - actual_fields
                raise ValueError(f"Missing required columns: {missing}")

            # Process rows
            total_weight = 0.0
            for row in reader:
                row = {k.strip(): v.strip() for k, v in row.items()}
                symbol = row['Symbol']

                try:
                    weight = float(row['Target Weight'])
                except ValueError:
                    raise ValueError(f"Invalid weight for {symbol}: {row['Target Weight']}")

                if weight < 0:
                    raise ValueError(f"Negative weight not allowed for {symbol}: {weight}")

                allocations[symbol] = weight
                total_weight += weight

            # Validate total weight
            if not 0.99 <= total_weight <= 1.01:  # Allow small rounding differences
                raise ValueError(f"Total allocation weight must be close to 1.0 (got {total_weight})")

        return allocations if return_dict else PortfolioModel(model_name, allocations)