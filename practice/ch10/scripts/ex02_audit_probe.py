"""練習 02：逐項佐證 itsdangerous audit 發現（只讀 vendor，不修改）"""
import sys
import time
import tracemalloc
import zlib
from pathlib import Path

VENDOR_SRC = Path(__file__).resolve().parent.parent / "vendor" / "itsdangerous" / "src"
sys.path.insert(0, str(VENDOR_SRC))

from itsdangerous import (  # noqa: E402
    BadPayload,
    BadSignature,
    NoneAlgorithm,
    Signer,
    TimestampSigner,
    URLSafeSerializer,
    URLSafeTimedSerializer,
)
from itsdangerous.encoding import base64_encode  # noqa: E402

BOMB_SIZE = 20 * 1024 * 1024  # 20 MB 已足以看出放大效應，又不會拖垮本機


def make_bomb_token():
    """做一個『未簽章』的壓縮炸彈 token：payload 合法、簽章亂填。"""
    json_bytes = b'"' + b"a" * BOMB_SIZE + b'"'
    payload = b"." + base64_encode(zlib.compress(json_bytes, 9))
    return (payload + b".forged-signature").decode()


def measure(func):
    tracemalloc.start()
    t0 = time.perf_counter()
    outcome = func()
    elapsed = time.perf_counter() - t0
    _, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    return outcome, elapsed, peak / 1024 / 1024


def f1_zip_bomb():
    """F1（高）：loads_unsafe 會對未驗證資料做無上限 zlib 解壓。"""
    token = make_bomb_token()
    s = URLSafeSerializer("secret")

    def safe_path():
        try:
            s.loads(token)
        except BadSignature:
            return "BadSignature"

    def unsafe_path():
        ok, value = s.loads_unsafe(token)
        return f"ok={ok}, 解出 {len(value):,} 字元"

    r1, t1, m1 = measure(safe_path)
    r2, t2, m2 = measure(unsafe_path)
    print(f"F1 token 只有 {len(token):,} bytes")
    print(f"   loads()        → {r1}，{t1*1000:.1f} ms，峰值 {m1:.1f} MB")
    print(f"   loads_unsafe() → {r2}，{t2*1000:.1f} ms，峰值 {m2:.1f} MB（放大 {BOMB_SIZE // len(token)}x）")
    assert m2 > 10 * max(m1, 1), "預期 unsafe 路徑記憶體明顯放大"


class BoundedURLSafeSerializer(URLSafeSerializer):
    """F1 修補方向的可執行驗證：解壓設上限（不改 vendor，用子類別示範）。"""

    max_decompressed = 1024 * 1024  # 1 MB

    def load_payload(self, payload, *args, **kwargs):
        if payload.startswith(b"."):
            from itsdangerous.encoding import base64_decode
            d = zlib.decompressobj()
            raw = d.decompress(base64_decode(payload[1:]), self.max_decompressed)
            if d.unconsumed_tail or not d.eof:
                raise BadPayload("解壓後超過上限，拒絕處理")
            payload = base64_encode(raw)  # 交回父類別走一般（未壓縮）路徑
        return super().load_payload(payload, *args, **kwargs)


def f1_fix_demo():
    token = make_bomb_token()
    s = BoundedURLSafeSerializer("secret")
    (ok, value), elapsed, peak = measure(lambda: s.loads_unsafe(token))
    print(f"   修補後 loads_unsafe → ok={ok}, value={value!r}，{elapsed*1000:.1f} ms，峰值 {peak:.1f} MB")
    assert value is None and peak < 5
    normal = s.dumps({"msg": "x" * 2000})
    assert normal.startswith(".") and s.loads(normal) == {"msg": "x" * 2000}
    print("   修補後正常壓縮 token 仍可往返（回歸測試 OK）")


def f2_positional_salt():
    """F2（中）：TimedSerializer.loads 第 2 個位置參數是 max_age，不是 salt。"""
    plain, timed = URLSafeSerializer("k"), URLSafeTimedSerializer("k")
    assert plain.loads(plain.dumps(1, salt="ctx"), "ctx") == 1
    try:
        timed.loads(timed.dumps(1, salt="ctx"), "ctx")
    except BadSignature as e:
        print(f"F2 同樣寫法 loads(token, 'ctx')：Serializer 成功、TimedSerializer → {type(e).__name__}")
    try:
        timed.loads(timed.dumps(1), "ctx")
    except TypeError as e:
        print(f"   預設 salt 的 token 則爆未包裝的 TypeError：{e}")


def f3_weak_keys():
    """F3（中）：空字串 key 照收；空 list 到 sign 時才 IndexError。"""
    forged = Signer("").sign("admin")
    print(f"F3 Signer('') 可簽：{forged!r}（任何人都能用空 key 重算）")
    try:
        Signer([]).sign("x")
    except IndexError as e:
        print(f"   Signer([]) 建構成功，sign 時才 IndexError：{e}")


def f4_none_algorithm():
    """F4（中）：NoneAlgorithm 是公開 API，使用後任何人可偽造。"""
    s = Signer("k", algorithm=NoneAlgorithm())
    print(f"F4 NoneAlgorithm 下 unsign(b'role=admin.') → {s.unsign(b'role=admin.')!r}（零成本偽造）")


def f5_sha1_default():
    s = Signer("k")
    print(f"F5 預設 digest = {s.digest_method.__name__}，簽章長度 {len(s.get_signature('x'))} 字元（SHA1）")


def f6_default_salt():
    """F6（低）：不同用途共用預設 salt 時，token 可跨用途重放。"""
    reset_pw = URLSafeSerializer("app-key")
    unsubscribe = URLSafeSerializer("app-key")
    token = unsubscribe.dumps({"user": 42})
    print(f"F6 退訂 token 被『重設密碼』serializer 接受：{reset_pw.loads(token)}（兩者 salt={reset_pw.salt!r}）")


def f8_lazy_derivation_error():
    s = Signer("k", key_derivation="bogus")
    try:
        s.sign("x")
    except TypeError as e:
        print(f"F8 key_derivation='bogus' 建構不報錯，sign 才拋 TypeError：{e}")


def f10_clock_skew():
    class FutureSigner(TimestampSigner):
        def get_timestamp(self):
            return super().get_timestamp() + 2  # 簽章機時鐘快 2 秒

    token = FutureSigner("k").sign("v")
    try:
        TimestampSigner("k").unsign(token, max_age=3600)
    except BadSignature as e:
        print(f"F10 時鐘快 2 秒就被拒：{type(e).__name__}：{e}")


def main():
    probes = (f1_zip_bomb, f1_fix_demo, f2_positional_salt, f3_weak_keys,
              f4_none_algorithm, f5_sha1_default, f6_default_salt,
              f8_lazy_derivation_error, f10_clock_skew)
    try:
        for probe in probes:
            probe()
        print("\n全部佐證腳本執行完成")
    except AssertionError as e:
        print(f"佐證失敗：{e!r}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
