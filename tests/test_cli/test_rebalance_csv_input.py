import pytest
import logging
from pathlib import Path
from realloc.cli.rebalance_csv_input import main, process_rebalance


@pytest.fixture
def sample_accounts_csv(tmp_path):
    content = '''Account Label,Account Id,Symbol,Shares
IRA,A1,CASH,1000.50
IRA,A1,AAPL,10
IRA,A1,MSFT,5
Taxable,A2,CASH,2500.75
Taxable,A2,AAPL,15
Taxable,A2,GOOG,3'''
    csv_file = tmp_path / "accounts.csv"
    csv_file.write_text(content)
    return csv_file


@pytest.fixture
def sample_allocations_csv(tmp_path):
    content = '''Symbol,Target Weight
AAPL,0.4
MSFT,0.3
GOOG,0.3'''
    csv_file = tmp_path / "allocations.csv"
    csv_file.write_text(content)
    return csv_file


@pytest.fixture
def sample_prices_csv(tmp_path):
    content = '''Symbol,Price
AAPL,150.50
MSFT,250.75
GOOG,2750.25
CASH,1.00'''
    csv_file = tmp_path / "prices.csv"
    csv_file.write_text(content)
    return csv_file


def test_cli_successful_run(tmp_path, sample_accounts_csv, sample_allocations_csv,
                            sample_prices_csv, caplog):
    """Test successful CLI execution"""
    caplog.set_level(logging.INFO)
    args = [
        "--accounts", str(sample_accounts_csv),
        "--allocations", str(sample_allocations_csv),
        "--prices", str(sample_prices_csv)
    ]

    exit_code = main(args)
    assert exit_code == 0


def test_cli_with_export(tmp_path, sample_accounts_csv, sample_allocations_csv,
                         sample_prices_csv):
    """Test CLI execution with trade export"""
    export_path = tmp_path / "trades.csv"
    args = [
        "--accounts", str(sample_accounts_csv),
        "--allocations", str(sample_allocations_csv),
        "--prices", str(sample_prices_csv),
        "--export", str(export_path)
    ]

    exit_code = main(args)
    assert exit_code == 0
    assert export_path.exists()


def test_cli_missing_required_arg():
    """Test CLI execution with missing required argument"""
    # Using only --accounts argument, missing required --allocations and --prices
    args = ["--accounts", "accounts.csv"]
    exit_code = main(args)
    assert exit_code == 2  # Standard argparse exit code for missing args


def test_cli_with_max_iterations(tmp_path, sample_accounts_csv, sample_allocations_csv,
                                 sample_prices_csv, caplog):
    """Test CLI with custom max iterations"""
    caplog.set_level(logging.INFO)

    # Create minimal valid test data
    with open(sample_allocations_csv, 'w') as f:
        f.write('''Symbol,Target Weight
AAPL,1.0''')

    with open(sample_accounts_csv, 'w') as f:
        f.write('''Account Label,Account Id,Symbol,Shares
IRA,A1,CASH,1000.00
IRA,A1,AAPL,10.00''')

    with open(sample_prices_csv, 'w') as f:
        f.write('''Symbol,Price
AAPL,150.00
CASH,1.00''')

    exit_code = main(["--accounts", str(sample_accounts_csv),
                      "--allocations", str(sample_allocations_csv),
                      "--prices", str(sample_prices_csv),
                      "--max-iterations", "1"])

    assert exit_code == 0

