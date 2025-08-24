import pytest
from pathlib import Path
from realloc.plugins.importers.allocation.allocation_csv import AllocationCSVImporter
from realloc.plugins.core.base import AllocationImporter
from realloc.models import PortfolioModel


@pytest.fixture
def importer():
    return AllocationCSVImporter()


@pytest.fixture
def sample_csv(tmp_path):
    content = '''Symbol,Target Weight
AAPL,0.4
GOOG,0.3
MSFT,0.3'''
    csv_file = tmp_path / "allocations.csv"
    csv_file.write_text(content)
    return csv_file


def test_inheritance(importer):
    assert isinstance(importer, AllocationImporter)


def test_name(importer):
    assert importer.name == "allocation_csv"


def test_supported_extensions(importer):
    assert importer.supported_extensions == ['.csv']


def test_import_portfolio_model(importer, sample_csv):
    result = importer.import_allocations(sample_csv)

    assert isinstance(result, PortfolioModel)
    assert result.name == "CSV Import"
    assert result.targets == {
        "AAPL": 0.4,
        "GOOG": 0.3,
        "MSFT": 0.3
    }


def test_import_dict(importer, sample_csv):
    result = importer.import_allocations(sample_csv, return_dict=True)

    assert isinstance(result, dict)
    assert result == {
        "AAPL": 0.4,
        "GOOG": 0.3,
        "MSFT": 0.3
    }


def test_custom_model_name(importer, sample_csv):
    result = importer.import_allocations(sample_csv, model_name="Test Model")

    assert isinstance(result, PortfolioModel)
    assert result.name == "Test Model"


def test_invalid_weight(importer, tmp_path):
    content = '''Symbol,Target Weight
AAPL,invalid'''

    csv_file = tmp_path / "allocations.csv"
    csv_file.write_text(content)

    with pytest.raises(ValueError, match="Invalid weight for AAPL"):
        importer.import_allocations(csv_file)


def test_negative_weight(importer, tmp_path):
    content = '''Symbol,Target Weight
AAPL,-0.5
GOOG,1.5'''

    csv_file = tmp_path / "allocations.csv"
    csv_file.write_text(content)

    with pytest.raises(ValueError, match="Negative weight not allowed for AAPL"):
        importer.import_allocations(csv_file)


def test_invalid_total_weight(importer, tmp_path):
    content = '''Symbol,Target Weight
AAPL,0.5
GOOG,0.2'''

    csv_file = tmp_path / "allocations.csv"
    csv_file.write_text(content)

    with pytest.raises(ValueError, match="Total allocation weight must be close to 1.0"):
        importer.import_allocations(csv_file)


def test_missing_columns(importer, tmp_path):
    content = '''Symbol
AAPL'''

    csv_file = tmp_path / "allocations.csv"
    csv_file.write_text(content)

    with pytest.raises(ValueError, match="Missing required columns"):
        importer.import_allocations(csv_file)