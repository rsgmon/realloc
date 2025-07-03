import csv

import pytest
from pathlib import Path
import json
from unittest.mock import Mock, patch
from realloc.cli.rebalance_main import is_trade_remaining, main


@pytest.fixture
def sample_input_data():
    return {
        "prices": {
            "AAPL": 150.0,
            "GOOGL": 2800.0,
        },
        "accounts": [
            {
                "account_number": "ACC1",
                "label": "Account 1",
                "targets": {"AAPL": 1.0},
                "cash": 10000.0,
                "positions": {"AAPL": 10}
            },
            {
                "account_number": "ACC2",
                "label": "Account 2",
                "targets": {"GOOGL": 1.0},
                "cash": 15000.0,
                "positions": {"GOOGL": 5}
            }
        ],
        "model": {
            "label": "Test Portfolio",
            "targets": {
                "AAPL": 0.6,
                "GOOGL": 0.4
            }
        }
    }


@pytest.fixture
def input_file(tmp_path, sample_input_data):
    input_file = tmp_path / "input.json"
    with open(input_file, "w") as f:
        json.dump(sample_input_data, f)
    return input_file


def test_is_trade_remaining():
    trades = {"AAPL": 5.0, "GOOGL": 0.001, "MSFT": -3.0}
    assert is_trade_remaining(trades) == True

    trades = {"AAPL": 0.001, "GOOGL": 0.005, "MSFT": -0.009}
    assert is_trade_remaining(trades) == False

    trades = {}
    assert is_trade_remaining(trades) == False


@pytest.fixture
def mock_dependencies():
    with patch('realloc.PortfolioModel') as model_mock, \
            patch('realloc.TradeAccountMatrix') as matrix_mock, \
            patch('realloc.Account') as account_mock, \
            patch('realloc.allocate_trades') as allocate_mock, \
            patch('realloc.select_account_for_buy_trade') as buy_mock, \
            patch('realloc.select_account_for_sell_trade') as sell_mock:
        # Configure mocks
        model_instance = model_mock.return_value
        model_instance.normalize.return_value = {"AAPL": 0.6, "GOOGL": 0.4}

        matrix_instance = matrix_mock.return_value
        matrix_instance.portfolio_trades = {"AAPL": 0}
        matrix_instance.cash_matrix = {"ACC1": 10000.0, "ACC2": 15000.0}
        matrix_instance.accounts = {
            "ACC1": account_mock.return_value,
            "ACC2": account_mock.return_value
        }

        account_instance = account_mock.return_value
        account_instance.account_number = "ACC1"
        account_instance.positions = {}
        account_instance.cash = 10000.0

        allocate_mock.return_value = {"AAPL": 0}

        yield {
            'model': model_mock,
            'matrix': matrix_mock,
            'account': account_mock,
            'allocate': allocate_mock,
            'buy': buy_mock,
            'sell': sell_mock
        }


def test_main_basic_execution(input_file, mock_dependencies, capsys):
    with patch('sys.argv', ['rebalance_main.py', str(input_file)]):
        main()

    captured = capsys.readouterr()
    assert "=== Initial Account States ===" in captured.out
    assert "=== Target Portfolio (shares) ===" in captured.out
    assert "=== Current Portfolio (shares) ===" in captured.out


from realloc.plugins.exporters.csv_exporter import CSVExporter

from unittest.mock import patch, MagicMock
import json
import csv


def test_main_with_csv_exporter(input_file, mock_dependencies, tmp_path, capsys):
    export_path = tmp_path / "output.csv"

    # Create test input data
    input_data = {
        "prices": {"VTI": 100.0, "VXUS": 50.0},
        "accounts": [
            {
                "label": "IRA Account",
                "account_number": "IRA",
                "positions": {"VTI": 10},
                "cash": 1000.0,
                "targets": {}
            },
            {
                "label": "401k Account",
                "account_number": "401k",
                "positions": {"VXUS": 20},
                "cash": 500.0,
                "targets": {}
            }
        ],
        "model": {
            "label": "Test Model",
            "targets": {"VTI": 0.6, "VXUS": 0.4}
        }
    }

    # Write input data to the input file
    with open(input_file, 'w') as f:
        json.dump(input_data, f)

    # Create a mock exporter
    mock_exporter = MagicMock()

    # Mock the Exporter class and its load_export_plugin method
    with patch('realloc.plugins.core.base.Exporter') as MockExporter:
        MockExporter.load_export_plugin.return_value = mock_exporter

        with patch('sys.argv', [
            'rebalance_main.py',
            str(input_file),
            '--exporter', 'csv',
            '--export-path', str(export_path)
        ]):
            main()

    # Verify that the exporter's export method was called
    mock_exporter.export.assert_called_once()

    # Get the trades that were passed to the export method
    account_trades = mock_exporter.export.call_args[0][0]

    # Verify the structure of account_trades
    assert isinstance(account_trades, list)
    for trade in account_trades:
        assert isinstance(trade, dict)
        # Each trade should be {account_id: {symbol: quantity}}
        assert len(trade) == 1  # One account per trade
        account_id = list(trade.keys())[0]
        assert isinstance(trade[account_id], dict)
        assert len(trade[account_id]) == 1  # One symbol per trade


def test_main_max_iterations(input_file, mock_dependencies, capsys):
    # Configure matrix mock to always have remaining trades
    mock_dependencies['matrix'].return_value.portfolio_trades = {"AAPL": 10.0}

    with patch('sys.argv', ['rebalance_main.py', str(input_file), '--iterations', '1']):
        main()

    captured = capsys.readouterr()
    assert "Max iterations reached" in captured.out


def test_main_invalid_input_file():
    with pytest.raises(FileNotFoundError):
        with patch('sys.argv', ['rebalance_main.py', 'nonexistent.json']):
            main()


@pytest.mark.parametrize("bad_data,expected_error", [
    (
            {
                "accounts": [],
                "model": {"label": "Test", "targets": {}}
            },
            "Input file must contain all required keys"  # Missing prices
    ),
    (
            {
                "prices": {},
                "model": {"label": "Test", "targets": {}}
            },
            "Input file must contain all required keys"  # Missing accounts
    ),
    (
            {
                "prices": {},
                "accounts": []
            },
            "Input file must contain all required keys"  # Missing model
    ),
    (
            {
                "prices": {},
                "accounts": [],
                "model": {}  # Model missing required fields
            },
            "Model must contain 'label' and 'targets' fields"
    ),
])
def test_main_invalid_input_data(tmp_path, bad_data, expected_error):
    input_file = tmp_path / "bad_input.json"
    with open(input_file, "w") as f:
        json.dump(bad_data, f)

    with pytest.raises(ValueError, match=expected_error):
        with patch('sys.argv', ['rebalance_main.py', str(input_file)]):
            main()