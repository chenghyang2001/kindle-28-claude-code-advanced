"""export 子指令測試（happy / edge / integration / error）。"""
import json

import pytest

from cfgcli.cli import main
from cfgcli.store import config_path


@pytest.fixture(autouse=True)
def isolated_home(tmp_path, monkeypatch):
    monkeypatch.setenv("CFGCLI_HOME", str(tmp_path))
    return tmp_path


def test_export_stdout_is_valid_json(capsys):
    main(["set", "theme", "dark"])
    main(["set", "lang", "en"])
    capsys.readouterr()
    assert main(["export"]) == 0
    assert json.loads(capsys.readouterr().out) == {"theme": "dark", "lang": "en"}


def test_export_empty_config(capsys):
    assert main(["export"]) == 0
    assert capsys.readouterr().out.strip() == "{}"


def test_export_keeps_chinese(capsys):
    main(["set", "名稱", "測試"])
    capsys.readouterr()
    main(["export"])
    out = capsys.readouterr().out
    assert "測試" in out and "\\u" not in out


def test_export_to_file(tmp_path, capsys):
    main(["set", "theme", "dark"])
    target = tmp_path / "out" / "x.json"
    target.parent.mkdir()
    assert main(["export", "-o", str(target)]) == 0
    assert json.loads(target.read_text(encoding="utf-8")) == {"theme": "dark"}
    assert "已匯出" in capsys.readouterr().out


def test_export_corrupt_config_returns_error(capsys):
    path = config_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("{not json", encoding="utf-8")
    assert main(["export"]) == 2
    assert "錯誤" in capsys.readouterr().err
