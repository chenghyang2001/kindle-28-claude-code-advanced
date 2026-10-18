"""練習 01：用小實驗驗證對 itsdangerous 的 5 個疑點（只讀 vendor，不修改）"""
import base64
import hashlib
import hmac
import sys
from pathlib import Path

# 直接從 vendor 原始碼匯入，確保驗證的是我們讀的那份程式碼
VENDOR_SRC = Path(__file__).resolve().parent.parent / "vendor" / "itsdangerous" / "src"
sys.path.insert(0, str(VENDOR_SRC))

from itsdangerous import (  # noqa: E402
    BadSignature,
    BadTimeSignature,
    SignatureExpired,
    Signer,
    TimestampSigner,
    URLSafeTimedSerializer,
)
from itsdangerous.encoding import base64_decode, bytes_to_int  # noqa: E402


def q1_key_rotation():
    """Q1：多把 key 時，簽章用哪把？驗證用哪幾把？"""
    old = Signer("old-key")
    rotated = Signer(["old-key", "new-key"])
    token_old = old.sign("hello")
    assert rotated.unsign(token_old) == b"hello", "舊 token 應仍可驗證"
    assert rotated.sign("hello") == Signer("new-key").sign("hello"), "新簽章應用最後一把"
    print("Q1 OK：sign 用最後一把 key；unsign 逐把（由新到舊）嘗試，舊 token 仍有效")


def q2_manual_signature():
    """Q2：預設 django-concat 推導 + HMAC-SHA1，能否手算出同一個簽章？"""
    key, salt, value = b"secret", b"itsdangerous.Signer", b"hello"
    derived = hashlib.sha1(salt + b"signer" + key).digest()
    mac = hmac.new(derived, value, hashlib.sha1).digest()
    manual = base64.urlsafe_b64encode(mac).rstrip(b"=")
    lib = Signer(key).get_signature(value)
    assert manual == lib, (manual, lib)
    print(f"Q2 OK：手算簽章 {manual.decode()} == 函式庫結果（20 bytes SHA1 → 27 字元）")


def q3_token_anatomy():
    """Q3：URLSafeTimedSerializer 的 token 長什麼樣？開頭的 '.' 代表什麼？"""
    s = URLSafeTimedSerializer("secret")
    small = s.dumps({"id": 1})
    big = s.dumps({"text": "a" * 500})
    payload, ts, sig = small.rsplit(".", 2)
    ts_int = bytes_to_int(base64_decode(ts))
    print(f"Q3 小 token = {small}")
    print(f"   payload={payload} → {base64_decode(payload)!r}, ts={ts}→{ts_int}, sig={sig}")
    assert not small.startswith("."), "小資料壓縮不划算，不應壓縮"
    assert big.startswith("."), "大資料應壓縮，以 '.' 標記"
    print(f"   大 token 開頭為 '.'（zlib 壓縮旗標），長度 {len(big)}（原 JSON 約 513 字）")


def q4_expired_stops_fallback():
    """Q4：過期與簽章錯誤是不同例外嗎？過期時還會嘗試其他 key 嗎？"""
    class PastSigner(TimestampSigner):
        def get_timestamp(self):  # 模擬 100 秒前簽的
            return super().get_timestamp() - 100

    token = PastSigner("k").sign("v")
    try:
        TimestampSigner("k").unsign(token, max_age=10)
    except SignatureExpired as e:
        print(f"Q4 OK：過期 → SignatureExpired（{e}），date_signed={e.date_signed}")
    try:
        TimestampSigner("wrong").unsign(token, max_age=10)
    except SignatureExpired:
        raise AssertionError("錯的 key 不該被判為過期")
    except BadTimeSignature as e:
        print(f"   錯 key → BadTimeSignature（{type(e).__name__}），不是過期")


def q5_separator_in_payload():
    """Q5：payload 自己含 '.' 時，切割會不會出錯？"""
    s = Signer("k")
    signed = s.sign(b"a.b.c")
    assert s.unsign(signed) == b"a.b.c"
    try:
        Signer("k", sep="a")
    except ValueError as e:
        print(f"Q5 OK：unsign 用 rsplit(sep, 1) 只切最後一段；sep 若在 base64 字母表內會被拒：{e}")


def main():
    try:
        for probe in (q1_key_rotation, q2_manual_signature, q3_token_anatomy,
                      q4_expired_stops_fallback, q5_separator_in_payload):
            probe()
        print("\n全部 5 題驗證通過")
    except (AssertionError, BadSignature) as e:
        print(f"驗證失敗：{e!r}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
