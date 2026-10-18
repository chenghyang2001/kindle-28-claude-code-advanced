"""使用者登入系統的核心邏輯（不含 CLI 互動）。

密碼以 PBKDF2-HMAC-SHA256 加鹽雜湊後儲存，絕不保存明文。
使用者資料以 JSON 檔保存，寫入時採用「暫存檔 + 原子替換」避免半寫入損毀。
"""

import hashlib
import hmac
import json
import os
import re
import secrets
import tempfile
from pathlib import Path

DEFAULT_ITERATIONS = 600_000
USERNAME_PATTERN = re.compile(r"^[A-Za-z0-9_]{3,32}$")
MIN_PASSWORD_LENGTH = 8

# 用於「使用者不存在」時仍執行一次雜湊，避免透過回應時間推斷帳號是否存在
_DUMMY_HASH_SALT = b"\x00" * 16


class AuthError(Exception):
    """登入系統的業務錯誤，訊息可直接顯示給使用者。"""


def hash_password(password: str, iterations: int = DEFAULT_ITERATIONS, salt: bytes | None = None) -> str:
    """回傳格式為 `pbkdf2_sha256$迭代次數$鹽(hex)$雜湊(hex)` 的字串。"""
    if salt is None:
        salt = secrets.token_bytes(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, iterations)
    return f"pbkdf2_sha256${iterations}${salt.hex()}${digest.hex()}"


def verify_password(password: str, stored: str) -> bool:
    """以常數時間比較密碼是否符合已儲存的雜湊。"""
    try:
        algorithm, iterations, salt_hex, digest_hex = stored.split("$")
        if algorithm != "pbkdf2_sha256":
            return False
        digest = hashlib.pbkdf2_hmac(
            "sha256", password.encode("utf-8"), bytes.fromhex(salt_hex), int(iterations)
        )
    except ValueError:
        return False
    return hmac.compare_digest(digest.hex(), digest_hex)


def validate_username(username: str) -> None:
    if not USERNAME_PATTERN.fullmatch(username):
        raise AuthError("帳號只能包含英文字母、數字與底線，長度 3 到 32 字元。")


def validate_password(password: str) -> None:
    if len(password) < MIN_PASSWORD_LENGTH:
        raise AuthError(f"密碼長度至少需要 {MIN_PASSWORD_LENGTH} 個字元。")


class UserStore:
    """以 JSON 檔保存使用者帳號。帳號比對不分大小寫。"""

    def __init__(self, path: str | os.PathLike, iterations: int = DEFAULT_ITERATIONS):
        self.path = Path(path)
        self.iterations = iterations

    def _load(self) -> dict:
        if not self.path.exists():
            return {}
        with self.path.open(encoding="utf-8") as f:
            return json.load(f)

    def _save(self, data: dict) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        fd, tmp_name = tempfile.mkstemp(dir=self.path.parent, suffix=".tmp")
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            os.replace(tmp_name, self.path)
        except BaseException:
            if os.path.exists(tmp_name):
                os.remove(tmp_name)
            raise

    def register(self, username: str, password: str) -> None:
        validate_username(username)
        validate_password(password)
        data = self._load()
        key = username.lower()
        if key in data:
            raise AuthError("此帳號已被註冊。")
        data[key] = {
            "username": username,
            "password_hash": hash_password(password, self.iterations),
        }
        self._save(data)

    def authenticate(self, username: str, password: str) -> bool:
        record = self._load().get(username.lower())
        if record is None:
            # 不論帳號是否存在都要花費相近時間
            hash_password(password, self.iterations, salt=_DUMMY_HASH_SALT)
            return False
        return verify_password(password, record["password_hash"])

    def change_password(self, username: str, old_password: str, new_password: str) -> None:
        if not self.authenticate(username, old_password):
            raise AuthError("舊密碼不正確。")
        validate_password(new_password)
        data = self._load()
        data[username.lower()]["password_hash"] = hash_password(new_password, self.iterations)
        self._save(data)

    def exists(self, username: str) -> bool:
        return username.lower() in self._load()
