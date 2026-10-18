"""關卡 3：比對 simplify 前後版本對同一批輸入的輸出是否完全一致。"""
import importlib.util
import logging
import sys

logging.disable(logging.CRITICAL)


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def run(fn, *args):
    try:
        return ("ok", fn(*args))
    except Exception as e:  # 比對腳本需要記錄例外型別本身
        return ("raise", type(e).__name__)


before = load("before", sys.argv[1])
after = load("after", sys.argv[2])
it = lambda p, q=1: {"price": p, "qty": q}
cases = [
    {"items": [it(100)]}, {"vip": True, "items": [it(100)]},
    {"vip": 1, "items": [it(100)]}, {"vip": "yes", "items": [it(100)]},
    {"vip": False, "items": [it(1000)]}, {"vip": True, "items": [it(1200)]},
    {"items": [it(10)], "coupon": 50}, {"items": [it(100)], "coupon": 10},
    {"items": [it(80, "two")]}, {"items": [{"qty": 1}]}, {"items": []},
]
diffs = 0
for c in cases:
    for fn in ("apply_discount", "is_vip"):
        b, a = run(getattr(before, fn), c), run(getattr(after, fn), c)
        if b != a:
            diffs += 1
            print("DIFF", fn, c, b, "->", a)
    b, a = run(before.apply_discount, c, [5, 5]), run(after.apply_discount, c, [5, 5])
    if b != a:
        diffs += 1
        print("DIFF apply_discount+coupons", c, b, "->", a)
for batch in ([], [None], cases, load("d", "src/orders.py").load_orders("data/orders.json")):
    b, a = run(before.summarize, batch), run(after.summarize, batch)
    if b != a:
        diffs += 1
        print("DIFF summarize", b, "->", a)
print(f"比對 {len(cases)} 筆輸入 × 3 種呼叫 + 4 批 summarize，差異 {diffs} 處")
sys.exit(1 if diffs else 0)
