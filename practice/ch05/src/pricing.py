"""pricing：legacy_order.calc 的重構版。

對外行為（含每個欄位的 int/float 型別）必須與 legacy_order.calc 完全一致，
以 tests/snapshot.json 為準。常數刻意保留舊版的數值型別（int 不寫成 float），
否則 discount/total 的型別會漂移（120 == 120.0 會騙過 assertEqual）。
"""

# 會員等級
TIER_VIP = "VIP"
TIER_SALE = "SALE"
VIP_DISCOUNT_RATE = 0.1
SALE_THRESHOLD = 1000
SALE_DISCOUNT = 100

# 優惠券：門檻看「小計 − 前述 tier 折扣」
COUPON_OFF50 = "OFF50"
OFF50_THRESHOLD = 500
OFF50_DISCOUNT = 50

# 運費：用淨額判斷（已扣 OFF50），所以 OFF50 可能讓訂單剛好達免運
FREE_SHIPPING_THRESHOLD = 1500
FREE_SHIPPING_FEE = 0
REGION_REMOTE = "remote"
REMOTE_SHIPPING_FEE = 150
STANDARD_SHIPPING_FEE = 60

# 稅：用內建 round（銀行家捨入），與舊版一致
TAX_RATE = 0.05

NO_DISCOUNT = 0
QTY_ERROR_MESSAGE = "qty must be positive"


def subtotal(items: list[dict]) -> int | float:
    """計算小計 Σ price × qty。

    從 int 0 起算，全 int 價格時回傳 int；price 為 float 時回傳 float。
    逐筆檢查，遇到 qty ≤ 0 立即拋 ValueError（不先讀後面項目）。
    缺 price / qty key 時拋 KeyError（維持舊行為）。
    """
    total = 0
    for item in items:
        if item["qty"] <= 0:
            raise ValueError(QTY_ERROR_MESSAGE)
        total = total + item["price"] * item["qty"]
    return total


def discount(subtotal: int | float, tier: str | None, coupon: str | None) -> int | float:
    """依 tier 與 coupon 計算折扣總額。

    - VIP：subtotal × 10%（float）
    - SALE：subtotal ≥ 1000 時折 100（int），未達維持 int 0
    - OFF50：（subtotal − 前述折扣）≥ 500 時再折 50
    未知 tier / coupon 視為無折扣；大小寫敏感。
    """
    amount = NO_DISCOUNT
    if tier == TIER_VIP:
        amount = subtotal * VIP_DISCOUNT_RATE
    elif tier == TIER_SALE:
        if subtotal >= SALE_THRESHOLD:
            amount = SALE_DISCOUNT
    if coupon == COUPON_OFF50:
        if subtotal - amount >= OFF50_THRESHOLD:
            amount = amount + OFF50_DISCOUNT
    return amount


def shipping(net: float, region: str | None) -> int:
    """依淨額與地區計算運費：淨額 ≥ 1500 免運，否則 remote 150、其他 60。"""
    if net >= FREE_SHIPPING_THRESHOLD:
        return FREE_SHIPPING_FEE
    if region == REGION_REMOTE:
        return REMOTE_SHIPPING_FEE
    return STANDARD_SHIPPING_FEE


def tax(net: float) -> int:
    """淨額 5% 稅，用內建 round（銀行家捨入），回傳 int。"""
    return round(net * TAX_RATE)


def calculate(order: dict, tier: str | None = None) -> dict:
    """組合以上函式，回傳與 legacy_order.calc 相同的 dict。

    key 順序：subtotal → discount → shipping → tax → total；
    coupon / region 用 order.get（缺 key 視為 None），items 缺 key 拋 KeyError。
    """
    sub = subtotal(order["items"])
    disc = discount(sub, tier, order.get("coupon"))
    net = sub - disc
    ship = shipping(net, order.get("region"))
    tax_amount = tax(net)
    return {"subtotal": sub, "discount": disc, "shipping": ship, "tax": tax_amount,
            "total": net + ship + tax_amount}
