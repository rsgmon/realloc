import pytest
import sys

from realloc.cli.portfolio_main import main


@pytest.fixture
def reset_sys_argv():
    old_argv = sys.argv.copy()
    yield
    sys.argv = old_argv


def test_main_help(reset_sys_argv, capsys):
    sys.argv = ["portfolio-cli", "--help"]
    with pytest.raises(SystemExit) as e:
        main()
    captured = capsys.readouterr()
    assert "usage" in captured.out.lower()
    assert e.value.code == 0  # 0 for normal help exit


def test_main_invalid_json_file(reset_sys_argv, tmp_path):
    bad_json = tmp_path / "bad.json"
    bad_json.write_text("{not: valid json}")

    sys.argv = ["portfolio-cli", str(bad_json)]
    with pytest.raises(SystemExit) as e:
        main()
    assert e.value.code != 0
