import logging

import pytest
from pathlib import Path


from realloc import Trade
from realloc.cli.rebalance_json_input import is_trade_remaining, main
from realloc.plugins.core.base import Exporter



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
                "cash": 10000.0,
                "positions": {"AAPL": 10}
            },
            {
                "account_number": "ACC2",
                "label": "Account 2",
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
            patch('realloc.PortfolioStateManager') as matrix_mock, \
            patch('realloc.Account') as account_mock, \
            patch('realloc.compute_portfolio_trades') as allocate_mock, \
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


def test_main_basic_execution(input_file, mock_dependencies, caplog):
    """Test the basic execution flow of the main function."""
    caplog.set_level(logging.INFO)

    # Configure mock to return a valid account ID
    mock_dependencies['buy'].return_value = "A1"
    mock_dependencies['sell'].return_value = "A2"

    # Configure matrix mock with some trades
    mock_dependencies['matrix'].return_value.portfolio_trades = {"AAPL": 10.0}
    mock_dependencies['matrix'].return_value.cash_matrix = {"A1": 1000, "A2": 2000}
    mock_dependencies['matrix'].return_value.accounts = {
        "A1": Mock(account_number="A1", positions={"AAPL": 5}),
        "A2": Mock(account_number="A2", positions={"GOOG": 3})
    }

    with patch('sys.argv', ['rebalance_json_input.py', str(input_file)]):
        main()

    # Check for expected log messages
    log_output = "\n".join(record.message for record in caplog.records)
    assert "=== Initial Account States ===" in log_output
    assert "=== Target Portfolio (shares) ===" in log_output
    assert "=== Current Portfolio (shares) ===" in log_output


from unittest.mock import patch, MagicMock, Mock
import json

def test_main_max_iterations(input_file, mock_dependencies, caplog):
    caplog.set_level(logging.INFO)

    # Configure matrix mock to always have remaining trades
    mock_dependencies['matrix'].return_value.portfolio_trades = {"AAPL": 10.0}

    with patch('sys.argv', ['rebalance_json_input.py', str(input_file), '--iterations', '1']):
        main()

    log_output = "\n".join(record.message for record in caplog.records)
    assert "Max iterations reached" in log_output


def test_main_invalid_input_file():
    with pytest.raises(FileNotFoundError):
        with patch('sys.argv', ['rebalance_json_input.py', 'nonexistent.json']):
            main()


@pytest.mark.parametrize("bad_data,expected_error", [
    (
            {
                "accounts": [],
                "model": {"label": "Test", "targets": {}}
            },
            r"Missing required keys in input file: {'prices'}"
    ),
    (
            {
                "prices": {},
                "model": {"label": "Test", "targets": {}}
            },
            r"Missing required keys in input file: {'accounts'}"
    ),
    (
            {
                "prices": {},
                "accounts": []
            },
            r"Missing required keys in input file: {'model'}"
    ),
    (
            {
                "prices": {},
                "accounts": [],
                "model": {}  # Model missing required fields
            },
            "Model must contain 'label' and 'targets' fields"
    ),
    (
            {
                "prices": {"AAPL": -100},  # Invalid price
                "accounts": [],
                "model": {"label": "Test", "targets": {}}
            },
            "All prices must be positive numbers"
    ),
    (
            {
                "prices": "not a dict",  # Wrong type for prices
                "accounts": [],
                "model": {"label": "Test", "targets": {}}
            },
            "Prices must be a dictionary mapping symbols to prices"
    ),
    (
            {
                "prices": {},
                "accounts": "not a list",  # Wrong type for accounts
                "model": {"label": "Test", "targets": {}}
            },
            "Accounts must be a list of account objects"
    ),
    (
            {
                "prices": {},
                "accounts": [],
                "model": "not a dict"  # Wrong type for model
            },
            "Model must be a dictionary with 'label' and 'targets' fields"
    ),
])
def test_main_invalid_input_data(tmp_path: Path, bad_data: dict, expected_error: str):
    """
    Test that the main function properly validates input data and raises appropriate errors.

    Args:
        tmp_path: Pytest fixture providing temporary directory path
        bad_data: Invalid input data that should trigger an error
        expected_error: Expected error message
    """
    input_file = tmp_path / "bad_input.json"
    with open(input_file, "w") as f:
        json.dump(bad_data, f)

    with pytest.raises(ValueError, match=expected_error):
        with patch('sys.argv', ['rebalance_json_input.py', str(input_file)]):
            main()
