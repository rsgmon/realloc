import pytest
from datetime import datetime
from pathlib import Path
from realloc.plugins.importers.prices.prices_csv import PriceCSVImporter
from realloc.plugins.core.base import PriceImporter


@pytest.fixture
def importer():
    return PriceCSVImporter()


def test_inheritance(importer):
    assert isinstance(importer, PriceImporter)


@pytest.fixture
def sample_csv(tmp_path):
    content = '''Symbol,Price,Date
AAPL,150.50,2025-08-24
GOOG,2750.25,2025-08-24
MSFT,305.75,2025-08-24'''
    csv_file = tmp_path / "prices.csv"
    csv_file.write_text(content)
    return csv_file


def test_name(importer):
    assert importer.name == "price_csv"


def test_supported_extensions(importer):
    assert importer.supported_extensions == ['.csv']


def test_basic_import(importer, sample_csv):
    prices = importer.import_prices(sample_csv)

    assert len(prices) == 3
    assert prices['AAPL'] == 150.50
    assert prices['GOOG'] == 2750.25
    assert prices['MSFT'] == 305.75


def test_import_with_date(importer, tmp_path):
    content = '''Symbol,Price,Date
AAPL,150.50,2025-08-24
AAPL,151.50,2025-08-23
GOOG,2750.25,2025-08-24'''

    csv_file = tmp_path / "prices.csv"
    csv_file.write_text(content)

    prices = importer.import_prices(csv_file, date=datetime(2025, 8, 24))
    assert prices['AAPL'] == 150.50
    assert len(prices) == 2


def test_invalid_price(importer, tmp_path):
    content = '''Symbol,Price
AAPL,invalid'''

    csv_file = tmp_path / "prices.csv"
    csv_file.write_text(content)

    with pytest.raises(ValueError, match="Invalid price for AAPL"):
        importer.import_prices(csv_file)


def test_negative_price(importer, tmp_path):
    content = '''Symbol,Price
AAPL,-150.50'''

    csv_file = tmp_path / "prices.csv"
    csv_file.write_text(content)

    with pytest.raises(ValueError, match="Price must be positive for AAPL"):
        importer.import_prices(csv_file)


def test_empty_result(importer, tmp_path):
    content = '''Symbol,Price,Date
AAPL,150.50,2025-08-24'''

    csv_file = tmp_path / "prices.csv"
    csv_file.write_text(content)

    with pytest.raises(ValueError, match="No valid prices found in CSV file"):
        importer.import_prices(csv_file, date=datetime(2024, 1, 1))


def test_missing_columns(importer, tmp_path):
    content = '''Symbol
AAPL'''

    csv_file = tmp_path / "prices.csv"
    csv_file.write_text(content)

    with pytest.raises(ValueError, match="Missing required columns"):
        importer.import_prices(csv_file)


def test_missing_date_column(importer, tmp_path):
    content = '''Symbol,Price
AAPL,150.50'''

    csv_file = tmp_path / "prices.csv"
    csv_file.write_text(content)

    with pytest.raises(ValueError, match="Missing required columns"):
        importer.import_prices(csv_file, date=datetime(2025, 8, 24))