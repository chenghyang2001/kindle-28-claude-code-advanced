"""帳號註冊與登入模組（純記憶體版，僅使用 Python 標準庫）。

示範「安全地儲存與比對密碼」的最小實作：
- 帳號表只存在記憶體 dict 中，程式結束即消失（不寫檔、不接資料庫）。
- 密碼以 PBKDF2-HMAC-SHA256 雜湊，每個帳號使用獨立的隨機 salt。
- 註冊與登入回傳字串錯誤碼（如 "OK"、"E_EMPTY_FIELD"），呼叫端直接比對即可。
"""
import hashlib
import hmac
import os
import sys
import threading
import unicodedata

# PBKDF2 迭代次數：次數越高，攻擊者拿到雜湊後離線暴力破解的成本越大。
# 600,000 是 OWASP 對 PBKDF2-HMAC-SHA256 的建議下限；每次雜湊約需數百毫秒，
# 這是刻意的：單次登入對使用者仍可接受，但大量猜測就會變得很昂貴。
PBKDF2_ITERATIONS = 600_000

# 密碼最短長度：過短的密碼即使雜湊也容易被字典攻擊猜中。
MIN_PASSWORD_LENGTH = 8

# 每個帳號獨立的 salt 長度。相同密碼會得到不同雜湊，
# 讓攻擊者無法用預先算好的彩虹表一次對應整批帳號。
SALT_BYTES = 16

# 回傳錯誤碼：集中定義，避免在多處手打字串而拼錯。
OK = "OK"
E_EMPTY_FIELD = "E_EMPTY_FIELD"
E_WEAK_PASSWORD = "E_WEAK_PASSWORD"
E_USER_EXISTS = "E_USER_EXISTS"
E_USER_NOT_FOUND = "E_USER_NOT_FOUND"
E_WRONG_PASSWORD = "E_WRONG_PASSWORD"


def _is_blank(value) -> bool:
    """判斷欄位是否視為空。

    非字串（None、數字等）一律當成空欄位，避免呼叫端傳錯型別時例外直接冒出。
    只含空白的字串也視為空，因為「全是空白」對使用者沒有意義。
    """
    return not isinstance(value, str) or not value.strip()


def _is_encodable(value: str) -> bool:
    """判斷字串能否以 UTF-8 編碼。

    lone surrogate（例如 "\\ud800"）在 Python 中是合法的 str，但無法編成 UTF-8，
    若直接送進雜湊會拋出 UnicodeEncodeError。無法編碼的輸入視為無效欄位，
    規格未另定錯誤碼，因此沿用 E_EMPTY_FIELD。
    """
    try:
        value.encode("utf-8")
    except UnicodeEncodeError:
        return False
    return True


def _normalize_username(username: str) -> str:
    """把帳號轉成儲存用的 key。

    流程：strip → NFKC → 移除 Cf 類字元 → strip → casefold。
    先做 NFKC 正規化，讓全形字（如 "ＡＬＩＣＥ"）與組合字元（如帶變音符號的字母，
    兩種寫法）被視為同一個字元，避免同一人註冊成多個帳號。
    再移除格式字元（Cf），最後做 casefold 而非 lower，因為 casefold 對 Unicode 的
    大小寫折疊更徹底（例如德文 ß 會對應到 ss）。先 strip 是為了避免前後多打的空白造成重複帳號。
    """
    text = unicodedata.normalize("NFKC", username.strip())
    # 移除 Unicode 類別 Cf（格式字元）：零寬空白 U+200B、零寬不斷空白 U+FEFF、
    # 字詞連接符 U+2060 等。這些字元看不見，且 NFKC 與 strip 都不會去掉它們；
    # 若保留，"​alice" 與 "alice" 會變成兩個帳號，看起來卻完全相同（視覺上的重複帳號）。
    text = "".join(ch for ch in text if unicodedata.category(ch) != "Cf")
    # 移除 Cf 後可能露出新的前後空白（例如 " ​ alice"），所以要再 strip 一次。
    return text.strip().casefold()


def _hash_password(password: str, salt: bytes) -> bytes:
    """以 PBKDF2-HMAC-SHA256 計算密碼雜湊。

    password 先編成 UTF-8 bytes，確保中文或其他非 ASCII 密碼在不同機器上結果一致。
    """
    return hashlib.pbkdf2_hmac(
        "sha256", password.encode("utf-8"), salt, PBKDF2_ITERATIONS
    )


def _make_record(password: str) -> dict:
    """為新密碼建立儲存紀錄，只含 salt 與雜湊，不含明碼。"""
    salt = os.urandom(SALT_BYTES)
    return {"salt": salt, "hash": _hash_password(password, salt)}


# 登入時序用的假資料：帳號不存在時仍要跑一次雜湊，讓回應時間與「帳號存在」相近。
# 這裡使用固定的假 salt 與假密碼，且與任何真實帳號無關，不是明碼帳號的 record。
# 在模組載入時預先算好，避免每次登入失敗都重複計算。
_DUMMY_SALT = bytes(SALT_BYTES)
_DUMMY_HASH = _hash_password("dummy-password-for-timing-only", _DUMMY_SALT)


class AuthStore:
    """記憶體內的帳號表。"""

    def __init__(self) -> None:
        # key 為正規化後的帳號，value 為 {"salt": bytes, "hash": bytes}。
        # 刻意不保存明碼，也不保存使用者原始大小寫的帳號字串。
        self._accounts: dict = {}
        # 保護 _accounts 的讀寫。只鎖短暫的字典操作，慢的雜湊運算一律放在鎖外，
        # 否則同一時間只能有一個人登入，其他執行緒全部排隊。
        self._lock = threading.Lock()

    def register(self, username: str, password: str) -> str:
        """註冊新帳號，回傳錯誤碼。

        檢查順序有意義：先檢查空欄位（含正規化後為空）、編碼與密碼強度，最後才查帳號是否重複，
        讓回傳的錯誤碼反映最基本的輸入問題。
        """
        if _is_blank(username) or _is_blank(password):
            return E_EMPTY_FIELD
        if not (_is_encodable(username) and _is_encodable(password)):
            return E_EMPTY_FIELD
        key = _normalize_username(username)
        # 正規化後為空（例如帳號只含零寬字元）等同空欄位，不可註冊看不見的帳號。
        if not key:
            return E_EMPTY_FIELD
        if len(password) < MIN_PASSWORD_LENGTH:
            return E_WEAK_PASSWORD
        # 雜湊很慢，放在鎖外計算；代價是重複帳號時會白算一次，但不會阻塞其他執行緒。
        record = _make_record(password)
        # 「檢查是否存在」與「寫入」必須在同一把鎖內完成，否則兩個執行緒
        # 可能同時通過檢查、都寫入，讓 E_USER_EXISTS 被競態繞過。
        with self._lock:
            if key in self._accounts:
                return E_USER_EXISTS
            self._accounts[key] = record
        return OK

    def login(self, username: str, password: str) -> str:
        """驗證帳號與密碼，回傳錯誤碼。

        比對用 hmac.compare_digest 做常數時間比較，
        一般的 == 會在遇到第一個不同位元時提早返回，攻擊者可藉由回應時間推測雜湊內容。
        """
        if _is_blank(username) or _is_blank(password):
            return E_EMPTY_FIELD
        if not (_is_encodable(username) and _is_encodable(password)):
            return E_EMPTY_FIELD
        key = _normalize_username(username)
        # 正規化後為空同樣視為空欄位。這個提早返回不取決於帳號是否存在，
        # 因此不會成為帳號枚舉的線索，也不影響下方的假雜湊時序保護。
        if not key:
            return E_EMPTY_FIELD
        # 只在鎖內讀取 record（一次字典查詢），雜湊比對在鎖外進行。
        with self._lock:
            record = self._accounts.get(key)
        if record is None:
            # 帳號不存在時也跑一次雜湊與常數時間比較，再回傳。
            # 否則「不存在」會比「存在但密碼錯」快很多，攻擊者可藉由回應時間枚舉帳號。
            # 比對結果刻意忽略，這裡只為了消耗相同的運算時間。
            dummy_candidate = _hash_password(password, _DUMMY_SALT)
            hmac.compare_digest(dummy_candidate, _DUMMY_HASH)
            return E_USER_NOT_FOUND
        candidate = _hash_password(password, record["salt"])
        if not hmac.compare_digest(candidate, record["hash"]):
            return E_WRONG_PASSWORD
        return OK


if __name__ == "__main__":
    # 冒煙測試：走過註冊與登入的主要路徑，只印錯誤碼，不印任何密碼內容。
    try:
        store = AuthStore()
        print("註冊 Alice:", store.register("Alice", "correct-horse"))
        print("登入 ALICE（正確密碼，大小寫不同）:", store.login("ALICE", "correct-horse"))
        print("登入 alice（錯誤密碼）:", store.login("alice", "wrong-pass"))
    except Exception as exc:
        print(f"錯誤：{exc}", file=sys.stderr)
        sys.exit(1)
