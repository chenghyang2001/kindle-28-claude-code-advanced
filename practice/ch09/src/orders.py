"""訂單計算模組：單筆金額、折扣與營收摘要。"""
import json
import logging

logger = logging.getLogger(__name__)


def load_orders(path):
    """從 JSON 檔讀取訂單清單。"""
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def order_total(order):
    """計算單筆訂單金額：sum(單價 × 數量)。"""
    return sum(item["price"] * item["qty"] for item in order["items"])


VIP_DISCOUNT = 0.9
BULK_THRESHOLD = 1000  # 滿 1000（含）打 95 折
BULK_DISCOUNT = 0.95


def apply_discount(order, coupons=None):
    """套用折扣：VIP 打 9 折；金額滿 1000（含）再打 95 折；最後扣掉優惠券（金額下限為 0）。"""
    total = order_total(order)
    if is_vip(order):
        total *= VIP_DISCOUNT
    if total >= BULK_THRESHOLD:
        total *= BULK_DISCOUNT
    for c in [*(coupons or []), order.get("coupon", 0)]:
        total -= c
    return round(max(total, 0), 2)


def summarize(orders):
    """回傳 (總營收, 平均客單價, 失敗筆數)；沒有成功筆數時平均為 None。"""
    revenue = 0
    succeeded = 0
    failed = 0
    for o in orders:
        try:
            revenue += apply_discount(o)
            succeeded += 1
        except (KeyError, TypeError, ValueError, AttributeError):
            logger.exception("訂單計算失敗：%r", o)
            failed += 1
    average = revenue / succeeded if succeeded else None
    return revenue, average, failed


def is_vip(order):
    """vip 欄位 == True 才算 VIP（刻意保留 ==：1 算、"yes" 不算）。"""
    return order.get("vip") == True  # noqa: E712
