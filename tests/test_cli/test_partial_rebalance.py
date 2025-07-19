import subprocess
import json
import tempfile
import os
import pytest


@pytest.fixture
def partial_input_json():
    data = {
        "prices": {"AAPL": 100, "MSFT": 200, "GOOG": 150},
        "accounts": [
            {
                "label": "Test A",
                "account_number": "A",
                "cash": 0,
                "positions": {"MSFT": 5},

            },
            {
                "label": "Test B",
                "account_number": "B",
                "cash": 500,
                "positions": {"GOOG": 3},

            },
        ],
        "model": {"name": "Simple", "targets": {"AAPL": 0.5, "GOOG": 0.3, "MSFT": 0.2}},
    }
    with tempfile.NamedTemporaryFile("w+", suffix=".json", delete=False) as f:
        json.dump(data, f)
        f.flush()
        yield f.name
    os.remove(f.name)


def test_partial_rebalance_cli_runs(partial_input_json):
    result = subprocess.run(
        [
            "partial-rebalance-cli",
            partial_input_json,
            "--sell-symbol",
            "MSFT",
            "--buy-symbol",
            "AAPL",
        ],
        capture_output=True,
        text=True,
    )

    # Check that it ran successfully
    assert result.returncode == 0
    assert "Final Account States" in result.stdout
    assert "Sold" in result.stdout or "Bought" in result.stdout


def test_partial_rebalance_cli_handles_no_trades(partial_input_json):
    result = subprocess.run(
        [
            "partial-rebalance-cli",
            partial_input_json,
            "--sell-symbol",
            "NFLX",
            "--buy-symbol",
            "TSLA",
        ],
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0
    assert "No relevant trades found" in result.stdout
