"""auth.py 與 cli.py 的 pytest 測試。

涵蓋範圍：
- 各錯誤碼的觸發條件與檢查順序
- 初始狀態沒有任何帳號
- 安全性：AuthStore 內部不含註冊時使用的明碼
- CLI 的文字協定流程（以子程序實際執行 cli.py）

執行方式：在本目錄執行 `python -m pytest -q`。
"""
import subprocess
import sys
from pathlib import Path
from typing import Union

# 為什麼要手動插入路徑：pytest 的 rootdir 不一定是本目錄，
# 若從其他目錄啟動 pytest，直接 import auth 會失敗。
THIS_DIR = Path(__file__).resolve().parent
if str(THIS_DIR) not in sys.path:
    sys.path.insert(0, str(THIS_DIR))

from auth import (  # noqa: E402  必須在路徑設定之後匯入
    AuthStore,
    E_EMPTY_FIELD,
    E_USER_EXISTS,
    E_USER_NOT_FOUND,
    E_WEAK_PASSWORD,
    E_WRONG_PASSWORD,
    OK,
)

# 測試用密碼，長度 >= 8 才能通過註冊的強度檢查。
GOOD_PASSWORD = "correct-horse"
WRONG_PASSWORD = "wrong-pass"


# ---------------------------------------------------------------------------
# a. 錯誤碼觸發
# ---------------------------------------------------------------------------

def test_register_ok_and_boundary_length():
    """正常註冊回傳 OK；恰好 8 字元的密碼是合法下限。"""
    store = AuthStore()
    assert store.register("alice", GOOD_PASSWORD) == OK
    assert store.register("bob", "12345678") == OK


def test_register_empty_field_variants():
    """空字串、只有空白、None 都視為空欄位。"""
    store = AuthStore()
    assert store.register("", GOOD_PASSWORD) == E_EMPTY_FIELD
    assert store.register("   ", GOOD_PASSWORD) == E_EMPTY_FIELD
    assert store.register("alice", "") == E_EMPTY_FIELD
    assert store.register("alice", "        ") == E_EMPTY_FIELD
    assert store.register(None, GOOD_PASSWORD) == E_EMPTY_FIELD


def test_register_weak_password_boundary():
    """7 字元密碼太弱；8 字元才通過（見 test_register_ok_and_boundary_length）。"""
    store = AuthStore()
    assert store.register("alice", "1234567") == E_WEAK_PASSWORD


def test_register_user_exists_is_case_insensitive():
    """帳號大小寫不分，ALICE 與 alice 視為同一人。"""
    store = AuthStore()
    assert store.register("Alice", GOOD_PASSWORD) == OK
    assert store.register("ALICE", GOOD_PASSWORD) == E_USER_EXISTS


def test_login_user_not_found():
    """登入不存在的帳號回傳 E_USER_NOT_FOUND。"""
    store = AuthStore()
    assert store.login("nobody", GOOD_PASSWORD) == E_USER_NOT_FOUND


def test_login_wrong_password():
    """帳號存在但密碼錯誤回傳 E_WRONG_PASSWORD。"""
    store = AuthStore()
    store.register("alice", GOOD_PASSWORD)
    assert store.login("alice", WRONG_PASSWORD) == E_WRONG_PASSWORD


def test_login_ok_case_insensitive_username():
    """登入時帳號大小寫不影響結果。"""
    store = AuthStore()
    store.register("alice", GOOD_PASSWORD)
    assert store.login("ALICE", GOOD_PASSWORD) == OK


def test_empty_field_takes_precedence_over_other_checks():
    """空欄位優先於弱密碼與帳號重複檢查。"""
    store = AuthStore()
    store.register("alice", GOOD_PASSWORD)
    # 帳號為空且密碼太弱：應回傳空欄位，而不是弱密碼。
    assert store.register("", "short") == E_EMPTY_FIELD
    # 帳號為空時登入同樣回傳空欄位，不會查到帳號不存在。
    assert store.login("", GOOD_PASSWORD) == E_EMPTY_FIELD


def test_weak_password_checked_before_user_exists():
    """弱密碼檢查早於帳號重複檢查：重複帳號 + 弱密碼回傳 E_WEAK_PASSWORD。"""
    store = AuthStore()
    store.register("alice", GOOD_PASSWORD)
    assert store.register("ALICE", "short") == E_WEAK_PASSWORD


# ---------------------------------------------------------------------------
# b. 初始狀態
# ---------------------------------------------------------------------------

def test_fresh_store_has_no_accounts():
    """新建的 AuthStore 沒有任何帳號，任何登入都應回傳 E_USER_NOT_FOUND。"""
    store = AuthStore()
    assert store.login("alice", GOOD_PASSWORD) == E_USER_NOT_FOUND
    assert store._accounts == {}


# ---------------------------------------------------------------------------
# c. 安全性：內部狀態不含明碼
# ---------------------------------------------------------------------------

def _collect_leaf_values(obj, out, seen):
    """遞迴收集物件內所有 str / bytes 葉節點，用來檢查是否含有明碼。

    seen 記錄已走訪過的物件 id，避免循環參照造成無窮遞迴。
    """
    if id(obj) in seen:
        return
    seen.add(id(obj))
    if isinstance(obj, (str, bytes)):
        out.append(obj)
    elif isinstance(obj, dict):
        for key, value in obj.items():
            _collect_leaf_values(key, out, seen)
            _collect_leaf_values(value, out, seen)
    elif isinstance(obj, (list, tuple, set, frozenset)):
        for item in obj:
            _collect_leaf_values(item, out, seen)
    elif hasattr(obj, "__dict__"):
        # 自訂物件（例如 AuthStore）的屬性存在 __dict__ 裡，也要掃描。
        _collect_leaf_values(vars(obj), out, seen)


def test_store_internals_do_not_contain_plaintext_password():
    """註冊後 AuthStore 的所有屬性都不應含有明碼字串。

    掃描 str 與 bytes 兩種形式：雜湊值與 salt 是 bytes，
    若實作錯誤地把密碼存成任一形式，這裡都會抓到。
    """
    password = "super-secret-passphrase-42"
    store = AuthStore()
    assert store.register("alice", password) == OK

    leaves = []
    _collect_leaf_values(store, leaves, set())
    assert leaves, "掃描不到任何內部資料，測試本身可能失效"

    password_bytes = password.encode("utf-8")
    for leaf in leaves:
        if isinstance(leaf, str):
            assert password not in leaf
        else:
            assert password_bytes not in leaf


# ---------------------------------------------------------------------------
# d. CLI 流程（以子程序實際執行 cli.py）
# ---------------------------------------------------------------------------

def _run_cli(stdin_data: Union[str, bytes]) -> subprocess.CompletedProcess:
    """以子程序執行 cli.py，stdin 餵入指定內容，回傳完整執行結果。

    為什麼以 bytes 傳輸：text 模式會替換換行符並套用編碼，無法精確控制
    BOM 或非法 UTF-8 位元組這類輸入。str 會先以 UTF-8 編碼後再送入，
    bytes 則原樣送入。stdout / stderr 一律以 UTF-8 解碼回傳 str。

    cwd 固定為本目錄，讓 cli.py 能正確 import auth。
    timeout 避免 CLI 卡住時拖垮整個測試套件。
    """
    if isinstance(stdin_data, str):
        stdin_data = stdin_data.encode("utf-8")
    completed = subprocess.run(
        [sys.executable, "cli.py"],
        input=stdin_data,
        capture_output=True,
        cwd=str(THIS_DIR),
        timeout=60,
    )
    return subprocess.CompletedProcess(
        args=completed.args,
        returncode=completed.returncode,
        stdout=completed.stdout.decode("utf-8"),
        stderr=completed.stderr.decode("utf-8", errors="replace"),
    )


def test_cli_register_login_flow_then_quit():
    """註冊後登入成功、錯誤密碼登入失敗，依序輸出三行結果。"""
    script = (
        "register alice correct-horse\n"
        "login alice correct-horse\n"
        "login alice wrong-pass\n"
        "quit\n"
    )
    result = _run_cli(script)
    assert result.returncode == 0
    assert result.stdout.splitlines() == ["OK", "OK", "E_WRONG_PASSWORD"]


def test_cli_bad_commands_each_print_e_bad_command():
    """未知指令、段數不對、空白行，各輸出一行 E_BAD_COMMAND。"""
    script = (
        "frobnicate alice\n"   # 未知指令
        "register alice\n"     # register 缺一段
        "\n"                   # 空白行
        "quit\n"
    )
    result = _run_cli(script)
    assert result.returncode == 0
    assert result.stdout.splitlines() == ["E_BAD_COMMAND"] * 3


def test_cli_eof_without_quit_exits_cleanly():
    """沒有 quit、只有 EOF 也能正常結束，exit code 為 0。"""
    result = _run_cli("register alice correct-horse\n")
    assert result.returncode == 0
    assert result.stdout.splitlines() == ["OK"]


def test_cli_login_unknown_user_after_register():
    """註冊 alice 後登入 bob，回傳 E_USER_NOT_FOUND。"""
    script = (
        "register alice correct-horse\n"
        "login bob correct-horse\n"
        "quit\n"
    )
    result = _run_cli(script)
    assert result.returncode == 0
    assert result.stdout.splitlines() == ["OK", "E_USER_NOT_FOUND"]


def test_cli_quit_stops_reading_further_lines():
    """quit 之後的指令不會被執行，也不產生任何輸出。"""
    result = _run_cli("quit\nregister alice correct-horse\n")
    assert result.returncode == 0
    assert result.stdout == ""


def test_cli_bom_on_first_line():
    """首行帶 UTF-8 BOM（記事本存檔常見）時，指令仍被正常解析。"""
    result = _run_cli("﻿register alice correct-horse\n")
    assert result.returncode == 0
    assert result.stdout.splitlines() == ["OK"]


def test_cli_decode_error_line_continues():
    """無法解碼的行輸出 E_BAD_COMMAND，且不影響下一行的處理。"""
    result = _run_cli(b"\xff\xfe\nregister alice correct-horse\n")
    assert result.returncode == 0
    assert result.stdout.splitlines() == ["E_BAD_COMMAND", "OK"]
