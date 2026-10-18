"""auth.py 的單元測試。使用較低的迭代次數以加快測試速度。"""

import json
import tempfile
import unittest
from pathlib import Path

from auth import (
    AuthError,
    UserStore,
    hash_password,
    verify_password,
)

TEST_ITERATIONS = 1_000


class PasswordHashTest(unittest.TestCase):
    def test_正確密碼可通過驗證(self):
        stored = hash_password("correct-horse", TEST_ITERATIONS)
        self.assertTrue(verify_password("correct-horse", stored))

    def test_錯誤密碼無法通過驗證(self):
        stored = hash_password("correct-horse", TEST_ITERATIONS)
        self.assertFalse(verify_password("wrong-password", stored))

    def test_同一密碼每次雜湊結果不同(self):
        a = hash_password("same-password", TEST_ITERATIONS)
        b = hash_password("same-password", TEST_ITERATIONS)
        self.assertNotEqual(a, b)

    def test_雜湊內容不含明文(self):
        stored = hash_password("plain-secret-123", TEST_ITERATIONS)
        self.assertNotIn("plain-secret-123", stored)

    def test_損毀的雜湊字串不會拋出例外(self):
        self.assertFalse(verify_password("anything", "not-a-valid-hash"))
        self.assertFalse(verify_password("anything", "md5$1$00$00"))


class UserStoreTest(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.path = Path(self._tmp.name) / "users.json"
        self.store = UserStore(self.path, iterations=TEST_ITERATIONS)

    def tearDown(self):
        self._tmp.cleanup()

    def test_註冊後可以登入(self):
        self.store.register("alice", "password123")
        self.assertTrue(self.store.authenticate("alice", "password123"))

    def test_密碼錯誤無法登入(self):
        self.store.register("alice", "password123")
        self.assertFalse(self.store.authenticate("alice", "bad-password"))

    def test_不存在的帳號無法登入(self):
        self.assertFalse(self.store.authenticate("ghost", "password123"))

    def test_重複註冊會失敗_且不分大小寫(self):
        self.store.register("alice", "password123")
        with self.assertRaisesRegex(AuthError, "已被註冊"):
            self.store.register("ALICE", "another-pass")

    def test_帳號格式不合法會被拒絕(self):
        for bad in ["ab", "has space", "中文帳號", "a" * 33, "bad-dash"]:
            with self.subTest(username=bad), self.assertRaises(AuthError):
                self.store.register(bad, "password123")

    def test_密碼太短會被拒絕(self):
        with self.assertRaisesRegex(AuthError, "至少"):
            self.store.register("alice", "short")

    def test_變更密碼需要正確的舊密碼(self):
        self.store.register("alice", "password123")
        with self.assertRaisesRegex(AuthError, "舊密碼"):
            self.store.change_password("alice", "wrong-old", "new-password")
        self.assertTrue(self.store.authenticate("alice", "password123"))

    def test_變更密碼後舊密碼失效_新密碼生效(self):
        self.store.register("alice", "password123")
        self.store.change_password("alice", "password123", "new-password")
        self.assertFalse(self.store.authenticate("alice", "password123"))
        self.assertTrue(self.store.authenticate("alice", "new-password"))

    def test_資料檔中不含明文密碼(self):
        self.store.register("alice", "password123")
        raw = self.path.read_text(encoding="utf-8")
        self.assertNotIn("password123", raw)
        self.assertEqual(json.loads(raw)["alice"]["username"], "alice")

    def test_資料檔不存在時可正常查詢(self):
        self.assertFalse(self.store.exists("alice"))
        self.assertFalse(self.store.authenticate("alice", "password123"))


if __name__ == "__main__":
    unittest.main()
