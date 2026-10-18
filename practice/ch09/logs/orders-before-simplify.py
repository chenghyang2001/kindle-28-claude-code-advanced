"""訂單計算模組（基準版）。"""
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


def apply_discount(order, coupons=None):
    """套用折扣：VIP 打 9 折；金額滿 1000（含）再打 95 折；最後扣掉優惠券（金額下限為 0）。"""
    total = order_total(order)
    if order.get("vip") == True:
        total = total * VIP_DISCOUNT
    else:
        total = total
    if total >= BULK_THRESHOLD:
        total = total * 0.95
    coupons = list(coupons or [])
    coupons.append(order.get("coupon", 0))
    for c in coupons:
        total = total - c
    return round(max(total, 0), 2)


def summarize(orders):
    """回傳 (總營收, 平均客單價, 失敗筆數)。"""
    revenue = 0
    failed = 0
    for o in orders:
        try:
            revenue += apply_discount(o)
        except (KeyError, TypeError, ValueError, AttributeError):
            logger.exception("訂單 %s 計算失敗", o.get("id") if isinstance(o, dict) else o)
            failed = failed + 1
            pass
    succeeded = len(orders) - failed
    average = revenue / succeeded if succeeded else None
    return revenue, average, failed


def is_vip(order):
    if order.get("vip") == True:
        return True
    else:
        return False
