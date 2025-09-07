import pytest
from pathlib import Path
from realloc.plugins.importers.account.account_csv import CSVAccountImporter
from realloc.accounts import Account


@pytest.fixture
def importer():
    return CSVAccountImporter()


@pytest.fixture
def sample_csv(tmp_path):
    content = '''Account Label,Account Id,Symbol,Shares
IRA,E123,CASH,1000.50
IRA,E123,AAA,45
IRA,E123,BBB,6.6
Taxable,T456,CASH,2500.75
Taxable,T456,AAA,10
Taxable,T456,DDD,25'''
    csv_file = tmp_path / "accounts.csv"
    csv_file.write_text(content)
    return csv_file


def test_name(importer):
    assert importer.name == "csv_account"


def test_supported_extensions(importer):
    assert importer.supported_extensions == ['.csv']


def test_importer_objects(importer, sample_csv):
    accounts = importer.account_importer(sample_csv)

    assert len(accounts) == 2
    assert all(isinstance(acc, Account) for acc in accounts)

    # Check IRA account
    ira = next(acc for acc in accounts if acc.label == "IRA")
    assert ira.account_number == "E123"
    assert ira.cash == 1000.50
    assert ira.positions["AAA"] == 45
    assert ira.positions["BBB"] == 6.6
    assert "CASH" not in ira.positions

    # Check Taxable account
    taxable = next(acc for acc in accounts if acc.label == "Taxable")
    assert taxable.account_number == "T456"
    assert taxable.cash == 2500.75
    assert taxable.positions["AAA"] == 10
    assert taxable.positions["DDD"] == 25
    assert "CASH" not in taxable.positions


def test_missing_cash(importer, tmp_path):
    content = '''Account Label,Account Id,Symbol,Shares
IRA,E123,AAA,45'''

    csv_file = tmp_path / "accounts.csv"
    csv_file.write_text(content)

    with pytest.raises(ValueError, match="missing required CASH position"):
        importer.account_importer(csv_file)


def test_invalid_shares(importer, tmp_path):
    content = '''Account Label,Account Id,Symbol,Shares
IRA,E123,CASH,invalid'''

    csv_file = tmp_path / "accounts.csv"
    csv_file.write_text(content)

    with pytest.raises(ValueError, match="Invalid share amount for CASH"):
        importer.account_importer(csv_file)


def test_missing_columns(importer, tmp_path):
    content = '''Account Label,Symbol,Shares
IRA,CASH,1000.50'''

    csv_file = tmp_path / "accounts.csv"
    csv_file.write_text(content)

    with pytest.raises(ValueError, match="Missing required columns"):
        importer.account_importer(csv_file)