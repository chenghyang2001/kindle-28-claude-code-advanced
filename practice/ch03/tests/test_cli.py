"""cfgcli 既有指令的測試。"""
import pytest

from cfgcli.cli import main


@pytest.fixture(autouse=True)
def isolated_home(tmp_path, monkeypatch):
    monkeypatch.setenv("CFGCLI_HOME", str(tmp_path))
    return tmp_path


def test_set_then_get(capsys):
    assert main(["set", "theme", "dark"]) == 0
    capsys.readouterr()
    assert main(["get", "theme"]) == 0
    assert capsys.readouterr().out.strip() == "dark"


def test_get_missing_key_returns_error(capsys):
    assert main(["get", "nope"]) == 1
    assert "找不到" in capsys.readouterr().err


def test_list_sorted(capsys):
    main(["set", "b", "2"])
    main(["set", "a", "1"])
    capsys.readouterr()
    main(["list"])
    assert capsys.readouterr().out.splitlines() == ["a=1", "b=2"]
