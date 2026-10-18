"""特徵測試案例：鎖住舊模組行為，重構後必須逐筆一致。"""

CASES = [
    ({"items": [{"price": 100, "qty": 2}]}, None),
    ({"items": [{"price": 600, "qty": 2}]}, "VIP"),
    ({"items": [{"price": 1000, "qty": 1}]}, "SALE"),
    ({"items": [{"price": 999, "qty": 1}]}, "SALE"),
    ({"items": [{"price": 300, "qty": 2}], "coupon": "OFF50"}, None),
    ({"items": [{"price": 450, "qty": 1}], "coupon": "OFF50"}, None),
    ({"items": [{"price": 200, "qty": 1}], "region": "remote"}, None),
    ({"items": [{"price": 800, "qty": 2}], "region": "remote"}, "VIP"),
    ({"items": [{"price": 1100, "qty": 1}], "coupon": "OFF50"}, "SALE"),
    ({"items": []}, None),
]
