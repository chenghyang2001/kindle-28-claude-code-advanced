"""git bisect run 用的判定腳本（放在 repo 外，保證每個 commit 用同一份測試）。

exit 0 = good、exit 1 = bad、exit 125 = 此 commit 無法測（bisect 會跳過）。
用法（在 bisect-demo 內）：git bisect run python ../check_cart.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path.cwd()))

try:
    import cart
except ImportError as exc:
    print(f"SKIP：無法 import cart（{exc}）")
    sys.exit(125)

if not hasattr(cart, "total"):
    # total 在 c5 才出現，之前的 commit 沒有被測功能，視為 good
    print("GOOD：尚無 total 功能")
    sys.exit(0)

# 回歸案例：剛好 1000 元應免運
cases = [
    ([(500, 2)], False, 1000),   # 邊界：剛好 1000 → 免運
    ([(100, 1)], False, 160),    # 未滿 → 加 60
    ([(2000, 1)], True, 1800),   # 會員九折後 1800 → 免運
]
failed = []
for items, is_member, expected in cases:
    actual = cart.total(items, is_member)
    if actual != expected:
        failed.append(f"total({items}, member={is_member}) = {actual}，預期 {expected}")

if failed:
    print("BAD：" + "；".join(failed))
    sys.exit(1)
print("GOOD：3 個案例全過")
sys.exit(0)
