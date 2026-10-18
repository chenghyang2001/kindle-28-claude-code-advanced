"""端對端測試：用子程序真的執行 `python -m bookshelf.cli`，走過完整使用者流程。"""
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def run_cli(db_path, *args):
    env = {**os.environ, "PYTHONUTF8": "1", "PYTHONIOENCODING": "utf-8"}
    return subprocess.run(
        [sys.executable, "-m", "bookshelf.cli", "--db", str(db_path), *args],
        cwd=ROOT, capture_output=True, text=True, encoding="utf-8", env=env, timeout=30,
    )


def test_full_loan_flow(tmp_path):
    dbf = tmp_path / "e2e.db"
    assert run_cli(dbf, "add", "978-0-306-40615-7", "測試驅動開發").returncode == 0
    r = run_cli(dbf, "borrow", "9780306406157", "alice", "--date", "2026-01-01")
    assert "2026-01-15" in r.stdout
    r = run_cli(dbf, "return", "9780306406157", "--date", "2026-01-20")
    assert "罰金 25 元" in r.stdout
    r = run_cli(dbf, "list")
    assert "測試驅動開發" in r.stdout
