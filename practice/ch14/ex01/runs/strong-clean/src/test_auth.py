"""auth.py 與 cli.py 的 pytest 測試，涵蓋全部錯誤碼與 CLI 流程。"""

import io
import subprocess
import sys
from pathlib import Path

import pytest

import cli
from auth import AuthStore

PASSWORD = "password1"
PROJECT_DIR = Path(__file__).resolve().parent


@pytest.fixture
def store():
    return AuthStore()


@pytest.fixture
def registered(store):
    assert store.register("bob", PASSWORD) == "OK"
    return store


def run_cli(input_text):
    """以函式方式執行 cli.main，回傳 (exit code, 輸出行列表)。"""
    stdout = io.StringIO()
    code = cli.main(stdin=io.StringIO(input_text), stdout=stdout)
    return code, stdout.getvalue().splitlines()


# ---------- 步驟 1：資料結構 ----------

def test_new_store_has_no_users(store):
    assert store._users == {}


# ---------- 步驟 2：註冊／登入錯誤碼 ----------

@pytest.mark.parametrize("username, password", [
    ("", PASSWORD),
    ("   ", PASSWORD),
    ("bob", ""),
    ("bob", "        "),
    ("", ""),
])
def test_register_empty_field(store, username, password):
    assert store.register(username, password) == "E_EMPTY_FIELD"


@pytest.mark.parametrize("username, password", [
    ("", PASSWORD),
    ("bob", "  "),
])
def test_login_empty_field(registered, username, password):
    assert registered.login(username, password) == "E_EMPTY_FIELD"


def test_empty_field_checked_before_weak_password(store):
    assert store.register("", "short") == "E_EMPTY_FIELD"


def test_register_weak_password(store):
    assert store.register("bob", "1234567") == "E_WEAK_PASSWORD"
    assert "bob" not in store._users


def test_register_minimum_length_ok(store):
    assert store.register("bob", "12345678") == "OK"


def test_register_user_exists(registered):
    assert registered.register("bob", "another-pass") == "E_USER_EXISTS"


def test_register_user_exists_case_insensitive(registered):
    assert registered.register("BOB", PASSWORD) == "E_USER_EXISTS"
    assert registered.register("Bob", PASSWORD) == "E_USER_EXISTS"


def test_login_ok(registered):
    assert registered.login("bob", PASSWORD) == "OK"


def test_login_username_case_insensitive(registered):
    assert registered.login("BOB", PASSWORD) == "OK"


def test_login_user_not_found(store):
    assert store.login("nobody", PASSWORD) == "E_USER_NOT_FOUND"


def test_login_wrong_password(registered):
    assert registered.login("bob", "wrong-pass") == "E_WRONG_PASSWORD"


# ---------- 步驟 3：密碼安全 ----------

def test_no_plaintext_password_in_store(registered):
    """掃描 AuthStore 內部所有屬性（遞迴），不應出現明碼字串。"""
    secret = PASSWORD.encode()

    def iter_values(obj, seen):
        if id(obj) in seen:
            return
        seen.add(id(obj))
        yield obj
        if isinstance(obj, dict):
            for key, value in obj.items():
                yield from iter_values(key, seen)
                yield from iter_values(value, seen)
        elif isinstance(obj, (list, tuple, set)):
            for item in obj:
                yield from iter_values(item, seen)
        elif hasattr(obj, "__dict__"):
            yield from iter_values(vars(obj), seen)

    for value in iter_values(registered, set()):
        if isinstance(value, str):
            assert PASSWORD not in value
        elif isinstance(value, bytes):
            assert secret not in value


def test_same_password_gets_different_salt_and_digest(store):
    store.register("alice", PASSWORD)
    store.register("carol", PASSWORD)
    alice, carol = store._users["alice"], store._users["carol"]
    assert alice["salt"] != carol["salt"]
    assert alice["digest"] != carol["digest"]
    assert len(alice["salt"]) == 16


# ---------- 步驟 4：CLI 與整體流程 ----------

def test_cli_register_login_flow():
    code, lines = run_cli(
        f"register alice {PASSWORD}\n"
        f"login alice {PASSWORD}\n"
        "login alice wrong-pass\n"
        "quit\n"
    )
    assert code == 0
    assert lines == ["OK", "OK", "E_WRONG_PASSWORD", "OK"]


def test_cli_user_not_found_and_weak_password():
    _, lines = run_cli("login ghost password1\nregister bob short\n")
    assert lines == ["E_USER_NOT_FOUND", "E_WEAK_PASSWORD"]


def test_cli_user_exists():
    _, lines = run_cli(f"register bob {PASSWORD}\nregister BOB {PASSWORD}\n")
    assert lines == ["OK", "E_USER_EXISTS"]


@pytest.mark.parametrize("line", [
    "foo",
    "register onlyuser",
    "register a b c",
    "login",
    "login a",
    "REGISTER a password1",
    "",
])
def test_cli_bad_command(line):
    _, lines = run_cli(line + "\n")
    assert lines == ["E_BAD_COMMAND"]


def test_cli_ignores_lines_after_quit():
    _, lines = run_cli("quit\nregister bob password1\n")
    assert lines == ["OK"]


def test_cli_eof_without_quit_exits_zero():
    code, lines = run_cli(f"register bob {PASSWORD}\n")
    assert code == 0
    assert lines == ["OK"]


def test_cli_subprocess_stdin_one_code_per_line():
    """以子程序實際執行 cli.py，驗證 stdin 每行輸出一個錯誤碼。"""
    result = subprocess.run(
        [sys.executable, str(PROJECT_DIR / "cli.py")],
        input=f"register alice {PASSWORD}\nlogin alice nope1234\nlogin zed x\nquit\n",
        capture_output=True,
        text=True,
        encoding="utf-8",
        cwd=PROJECT_DIR,
    )
    assert result.returncode == 0
    assert result.stdout.splitlines() == ["OK", "E_WRONG_PASSWORD", "E_USER_NOT_FOUND", "OK"]
