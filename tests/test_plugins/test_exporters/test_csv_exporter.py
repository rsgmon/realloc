import pytest
import csv
import os

from realloc import Trade
from realloc.plugins.exporters.csv_exporter import CSVExporter


@pytest.fixture
def sample_data():
    return [
        {
            'account_id': 'account1',
            'symbol': 'AAPL',
            'shares': 100
        },
        {
            'account_id': 'account2',
            'symbol': 'MSFT',
            'shares': -50
        }
    ]


@pytest.fixture
def temp_csv_path(tmp_path):
    return str(tmp_path / "test_export.csv")


def test_csv_exporter_name():
    exporter = CSVExporter("dummy.csv")
    assert exporter.name == "csv"


def test_csv_export_creates_file(temp_csv_path, sample_data):
    exporter = CSVExporter(temp_csv_path)
    exporter.export([Trade.from_dict(single_trade) for single_trade in sample_data])
    assert os.path.exists(temp_csv_path)


def test_csv_export_content(temp_csv_path, sample_data):
    exporter = CSVExporter(temp_csv_path)
    exporter.export([Trade.from_dict(single_trade) for single_trade in sample_data])

    with open(temp_csv_path, 'r', newline='') as f:
        reader = csv.reader(f)
        rows = list(reader)

    assert rows[0] == ["Account", "Symbol", "Shares"]
    assert sorted(rows[1:]) == [
        ["account1", "AAPL", "100"],
        ["account2", "MSFT", "-50"]
    ]


def test_csv_export_empty_data(temp_csv_path):
    exporter = CSVExporter(temp_csv_path)
    exporter.export([])

    with open(temp_csv_path, 'r', newline='') as f:
        reader = csv.reader(f)
        rows = list(reader)

    assert rows[0] == ["Account", "Symbol", "Shares"]
    assert len(rows) == 1


def test_csv_exporter_invalid_path(tmp_path):
    invalid_path = str(tmp_path / "nonexistent" / "test.csv")
    exporter = CSVExporter(invalid_path)

    with pytest.raises(FileNotFoundError):
        exporter.export([{'account': 'account1', 'symbol': 'AAPL', 'shares': 100}])