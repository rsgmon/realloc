import pytest

from pathlib import Path

from realloc.plugins.core.base import TradeValidator
from realloc.trades import TradeInfo
from realloc.plugins.core.engine import PluginEngine, ValidationEngine
from realloc.plugins.core.base import Exporter
from realloc.plugins.exporters.csv_exporter import CSVExporter


class SimpleValidator(TradeValidator):
    @property
    def name(self) -> str:
        return "simple_validator"

    def validate(self, trade: TradeInfo) -> tuple[bool, str]:
        return True, ""


class RejectingValidator(TradeValidator):
    @property
    def name(self) -> str:
        return "rejecting_validator"

    def validate(self, trade: TradeInfo) -> tuple[bool, str]:
        return False, "Always reject"


def test_validation_engine_fails_on_first_rejection(basic_trade):
    validation = ValidationEngine()
    validation.validators.append(SimpleValidator())  # Add directly to validators list
    validation.validators.append(RejectingValidator())

    is_valid, reason = validation.validate_trade(basic_trade)
    assert not is_valid
    assert reason == "Always reject"


def test_validation_engine_passes_valid_trade(basic_trade):
    validation = ValidationEngine()
    validation.validators.append(SimpleValidator())  # Add directly to validators list

    is_valid, reason = validation.validate_trade(basic_trade)
    assert is_valid
    assert reason == ""


def test_validation_engine_with_no_validators(basic_trade):
    validation = ValidationEngine()

    is_valid, reason = validation.validate_trade(basic_trade)
    assert is_valid
    assert reason == ""



def test_load_export_plugin_success(tmp_path):
    test_path = tmp_path / "test.csv"
    plugin = Exporter.load_exporter("csv", path=test_path)
    assert isinstance(plugin, CSVExporter)


def test_load_export_plugin_nonexistent():
    with pytest.raises(ValueError) as exc_info:
        Exporter.load_exporter("nonexistent", path=Path("dummy.csv"))
    assert "No plugin named 'nonexistent' found" in str(exc_info.value)


def test_load_export_plugin_invalid(monkeypatch):
    def mock_entry_points():
        class MockEntryPoint:
            def __init__(self):
                self.name = "invalid"

            def load(self):
                return type("InvalidPlugin", (), {})

        class MockEntryPoints(dict):
            def select(self, group, name):
                if name == "invalid":
                    return [MockEntryPoint()]
                return []

            def get(self, group, default=None):
                if group == "realloc.plugins":
                    return [MockEntryPoint()]
                return default or []

        return MockEntryPoints()

    import importlib.metadata
    monkeypatch.setattr(importlib.metadata, 'entry_points', mock_entry_points)

    with pytest.raises(ValueError) as exc_info:
        Exporter.load_exporter("invalid", path=Path("dummy.csv"))
    assert "Plugin 'invalid' is not a valid Exporter" in str(exc_info.value)
