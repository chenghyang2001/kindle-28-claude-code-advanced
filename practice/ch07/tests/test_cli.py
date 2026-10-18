"""CLI 整合測試：真的讀 data/ 目錄。"""
from pathlib import Path

from notestat.cli import main

DATA_DIR = Path(__file__).resolve().parent.parent / "data"


def test_cli_dir(capsys):
    assert main([str(DATA_DIR)]) == 0
    out = capsys.readouterr().out
    assert "TOTAL\tfiles=2" in out


def test_cli_missing_path(capsys):
    assert main(["no-such-path"]) == 2
    assert "找不到路徑" in capsys.readouterr().err
