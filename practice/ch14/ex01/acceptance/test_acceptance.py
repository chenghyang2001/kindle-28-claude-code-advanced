"""練習 01 共用驗收測試：弱／強兩個沙盒都用這一套來評分。

用法：SANDBOX=<沙盒路徑> python -m pytest -q ex01/acceptance/test_acceptance.py
介面契約取自強 prompt（auth.AuthStore + cli.py）；弱 prompt 沒有指定介面，
因此「介面對不上」本身就是弱 prompt 的代價之一。
"""
import importlib
import os
import subprocess
import sys
from pathlib import Path

import pytest

SANDBOX = os.environ.get("SANDBOX")
if not SANDBOX:
    pytest.exit("錯誤：缺少環境變數 SANDBOX（指向待測沙盒資料夾）", returncode=2)
SANDBOX_PATH = Path(SANDBOX).resolve()
sys.path.insert(0, str(SANDBOX_PATH))


@pytest.fixture
def store():
    try:
        auth = importlib.import_module("auth")
    except ImportError as exc:
        pytest.fail(f"找不到 auth 模組：{exc}")
    if not hasattr(auth, "AuthStore"):
        pytest.fail("auth 模組沒有 AuthStore 類別")
    return auth.AuthStore()


def test_register_ok(store):
    assert store.register("alice", "secret123") == "OK"


def test_login_ok(store):
    store.register("alice", "secret123")
    assert store.login("alice", "secret123") == "OK"


def test_wrong_password(store):
    store.register("alice", "secret123")
    assert store.login("alice", "WRONGpass") == "E_WRONG_PASSWORD"


def test_user_not_found(store):
    assert store.login("ghost", "secret123") == "E_USER_NOT_FOUND"


def test_duplicate_user_case_insensitive(store):
    store.register("alice", "secret123")
    assert store.register("ALICE", "another123") == "E_USER_EXISTS"


def test_weak_password(store):
    assert store.register("bob", "short") == "E_WEAK_PASSWORD"


@pytest.mark.parametrize("user,pw", [("", "secret123"), ("   ", "secret123"), ("carol", "")])
def test_empty_field(store, user, pw):
    assert store.register(user, pw) == "E_EMPTY_FIELD"


def test_no_plaintext_in_memory(store):
    store.register("alice", "Plaintext-Canary-42")
    assert "Plaintext-Canary-42" not in repr(vars(store))


def test_cli_flow():
    cli = SANDBOX_PATH / "cli.py"
    if not cli.exists():
        pytest.fail("找不到 cli.py")
    script = "register alice secret123\nlogin alice secret123\nlogin alice badpass99\nfoo\nquit\n"
    proc = subprocess.run(
        [sys.executable, str(cli)], input=script, capture_output=True,
        text=True, encoding="utf-8", timeout=20, cwd=SANDBOX_PATH,
    )
    lines = [ln.strip() for ln in proc.stdout.splitlines() if ln.strip()]
    assert proc.returncode == 0
    # v2：強 prompt 規定「每行指令印一行錯誤碼」，quit 也是指令，多印一行 OK 屬合規
    assert lines[:4] == ["OK", "OK", "E_WRONG_PASSWORD", "E_BAD_COMMAND"]
    assert lines[4:] in ([], ["OK"])
