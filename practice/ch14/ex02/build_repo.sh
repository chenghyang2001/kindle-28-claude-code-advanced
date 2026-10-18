#!/bin/bash
# 建立 bisect 演練用 repo：10 個 commit，第 6 個 commit 偷偷埋 bug
# 用法：bash ex02/build_repo.sh [目標資料夾，預設 ex02/bisect-demo]
set -euo pipefail

here="$(cd "$(dirname "$0")" && pwd)"
repo="${1:-$here/bisect-demo}"
rm -rf "$repo" && mkdir -p "$repo" && cd "$repo"
git init -q -b main
git config user.name "bisect-demo"
git config user.email "bisect-demo@example.invalid"

commit() { git add -A && git commit -q -m "$1"; }

# c1：購物車小計
cat > cart.py <<'EOF'
"""購物車計價模組"""


def subtotal(items):
    """items: [(單價, 數量), ...]"""
    return sum(price * qty for price, qty in items)
EOF
commit "c1 新增購物車小計 subtotal"

# c2：README
printf '# cart\n\n購物車計價小工具。\n' > README.md
commit "c2 新增 README"

# c3：會員折扣
cat >> cart.py <<'EOF'


def member_discount(amount, is_member):
    """會員打 9 折"""
    return round(amount * 0.9, 2) if is_member else amount
EOF
commit "c3 新增會員九折 member_discount"

# c4：運費
cat >> cart.py <<'EOF'


FREE_SHIPPING_THRESHOLD = 1000
SHIPPING_FEE = 60


def shipping(amount):
    """滿 1000 免運，否則 60 元"""
    return 0 if amount >= FREE_SHIPPING_THRESHOLD else SHIPPING_FEE
EOF
commit "c4 新增運費規則 shipping"

# c5：總價
cat >> cart.py <<'EOF'


def total(items, is_member=False):
    """總價 = 折扣後小計 + 運費"""
    discounted = member_discount(subtotal(items), is_member)
    return discounted + shipping(discounted)
EOF
commit "c5 新增總價 total"

# c6：（兇手）「重構」運費判斷，把 >= 改成 >，剛好 1000 元時誤收運費
sed -i 's/return 0 if amount >= FREE_SHIPPING_THRESHOLD else SHIPPING_FEE/return SHIPPING_FEE if amount <= FREE_SHIPPING_THRESHOLD else 0/' cart.py
commit "c6 重構 shipping 判斷式寫法"

# c7：README 補充
printf '\n## 規則\n- 會員九折\n- 滿 1000 免運\n' >> README.md
commit "c7 README 補充計價規則"

# c8：格式化金額
cat >> cart.py <<'EOF'


def format_price(amount):
    """格式化成 NT$ 1,234"""
    return f"NT$ {amount:,.0f}"
EOF
commit "c8 新增金額格式化 format_price"

# c9：CLI 入口
cat > main.py <<'EOF'
"""示範入口"""
from cart import format_price, total

if __name__ == "__main__":
    print(format_price(total([(500, 2)])))
EOF
commit "c9 新增 main.py 示範入口"

# c10：版本號
echo '__version__ = "1.0.0"' > version.py
commit "c10 新增版本號 1.0.0"

git log --oneline
