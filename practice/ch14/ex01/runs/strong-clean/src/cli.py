"""CLI 登入模擬：從 stdin 逐行讀取指令，每行指令輸出一行錯誤碼。

支援的指令：
    register <username> <password>
    login <username> <password>
    quit

參數數量不對、未知指令或空行輸出 E_BAD_COMMAND；讀到 EOF 或 quit 時結束，exit code 為 0。
"""

import sys

from auth import AuthStore


def main(stdin=None, stdout=None):
    """逐行處理 stdin 指令並將錯誤碼寫入 stdout，回傳 exit code。"""
    stdin = sys.stdin if stdin is None else stdin
    stdout = sys.stdout if stdout is None else stdout
    store = AuthStore()

    for line in stdin:
        parts = line.split()
        command = parts[0] if parts else ""

        if command == "quit":
            # quit 也輸出一行 OK，維持「每行指令一行輸出」的規則
            print("OK", file=stdout, flush=True)
            break
        if command in ("register", "login") and len(parts) == 3:
            _, username, password = parts
            handler = store.register if command == "register" else store.login
            print(handler(username, password), file=stdout, flush=True)
        else:
            print("E_BAD_COMMAND", file=stdout, flush=True)

    return 0


if __name__ == "__main__":
    sys.exit(main())
