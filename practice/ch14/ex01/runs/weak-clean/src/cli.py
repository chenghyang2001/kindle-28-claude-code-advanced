"""使用者登入系統的命令列介面。

用法：
    python cli.py                    # 互動選單
    python cli.py --db 路徑/users.json
環境變數 USER_DB 也可指定資料檔路徑（預設為使用者家目錄下的 .login_cli_users.json）。
"""

import argparse
import getpass
import os
import sys
from pathlib import Path

from auth import AuthError, UserStore

DEFAULT_DB = Path.home() / ".login_cli_users.json"


def read_password(prompt: str) -> str:
    # getpass 不會在終端機回顯密碼
    return getpass.getpass(prompt)


def do_register(store: UserStore) -> None:
    username = input("設定帳號：").strip()
    password = read_password("設定密碼：")
    if password != read_password("再次輸入密碼："):
        raise AuthError("兩次輸入的密碼不一致。")
    store.register(username, password)
    print(f"註冊成功，歡迎 {username}！")


def do_change_password(store: UserStore, username: str) -> None:
    old = read_password("目前密碼：")
    new = read_password("新密碼：")
    if new != read_password("再次輸入新密碼："):
        raise AuthError("兩次輸入的新密碼不一致。")
    store.change_password(username, old, new)
    print("密碼已更新。")


def logged_in_menu(store: UserStore, username: str) -> None:
    while True:
        print(f"\n[{username}] 1) 變更密碼  2) 登出")
        choice = input("請選擇：").strip()
        if choice == "1":
            try:
                do_change_password(store, username)
            except AuthError as e:
                print(f"錯誤：{e}")
        elif choice == "2":
            print("已登出。")
            return
        else:
            print("無效的選項。")


def do_login(store: UserStore) -> str | None:
    username = input("帳號：").strip()
    password = read_password("密碼：")
    if store.authenticate(username, password):
        print(f"登入成功，歡迎回來 {username}！")
        return username
    print("帳號或密碼錯誤。")
    return None


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="CLI 使用者登入系統")
    parser.add_argument("--db", default=os.environ.get("USER_DB", str(DEFAULT_DB)), help="使用者資料檔路徑")
    args = parser.parse_args(argv)
    store = UserStore(args.db)

    try:
        while True:
            print("\n=== 使用者登入系統 ===")
            print("1) 註冊  2) 登入  0) 離開")
            choice = input("請選擇：").strip()
            try:
                if choice == "1":
                    do_register(store)
                elif choice == "2":
                    user = do_login(store)
                    if user:
                        logged_in_menu(store, user)
                elif choice == "0":
                    print("再見！")
                    return 0
                else:
                    print("無效的選項。")
            except AuthError as e:
                print(f"錯誤：{e}")
    except (KeyboardInterrupt, EOFError):
        print("\n已中斷離開。")
        return 130


if __name__ == "__main__":
    sys.exit(main())
