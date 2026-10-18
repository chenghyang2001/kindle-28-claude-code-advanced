"""CLI 登入模擬的帳號儲存與驗證邏輯（僅使用標準庫，資料只存在記憶體中）。"""

import hashlib
import hmac
import os

MIN_PASSWORD_LENGTH = 8
PBKDF2_ITERATIONS = 200_000
SALT_BYTES = 16


class AuthStore:
    """記憶體內的帳號表。鍵為正規化後的帳號名稱（不分大小寫）。

    記憶體中不保存明碼，只保存每個帳號的隨機 salt 與 PBKDF2-HMAC-SHA256 雜湊值。
    """

    def __init__(self):
        # 帳號表：正規化帳號 -> {"salt": bytes, "digest": bytes}；初始為空
        self._users = {}

    @staticmethod
    def _key(username):
        """將帳號正規化為比對用的鍵（去除前後空白並轉小寫）。"""
        return username.strip().casefold()

    @staticmethod
    def _is_blank(value):
        """判斷欄位是否為空字串或只有空白。"""
        return value.strip() == ""

    @staticmethod
    def _hash(password, salt):
        """以 PBKDF2-HMAC-SHA256 計算密碼雜湊。"""
        return hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, PBKDF2_ITERATIONS)

    def register(self, username, password):
        """註冊帳號，回傳錯誤碼字串。"""
        if self._is_blank(username) or self._is_blank(password):
            return "E_EMPTY_FIELD"
        if len(password) < MIN_PASSWORD_LENGTH:
            return "E_WEAK_PASSWORD"
        key = self._key(username)
        if key in self._users:
            return "E_USER_EXISTS"
        salt = os.urandom(SALT_BYTES)
        self._users[key] = {"salt": salt, "digest": self._hash(password, salt)}
        return "OK"

    def login(self, username, password):
        """登入驗證，回傳錯誤碼字串。"""
        if self._is_blank(username) or self._is_blank(password):
            return "E_EMPTY_FIELD"
        record = self._users.get(self._key(username))
        if record is None:
            return "E_USER_NOT_FOUND"
        digest = self._hash(password, record["salt"])
        # 使用常數時間比對，避免透過時間差推測雜湊內容
        if not hmac.compare_digest(digest, record["digest"]):
            return "E_WRONG_PASSWORD"
        return "OK"
