"""pricing 模組單元測試：值與型別都必須與 legacy_order.calc 一致。"""
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "tests"))

from cases import CASES  # noqa: E402
import legacy_order  # noqa: E402
import pricing  # noqa: E402

SNAPSHOT = ROOT / "tests" / "snapshot.json"

# research.md §4 額外案例：(order, tier, 期望輸出)
EXTRA_CASES = [
    ({"items": [{"price": 1000, "qty": 1}], "coupon": "OFF50"}, "VIP",
     {"subtotal": 1000, "discount": 150.0, "shipping": 60, "tax": 42, "total": 952.0}),
    ({"items": [{"price": 540, "qty": 1}], "coupon": "OFF50"}, "VIP",
     {"subtotal": 540, "discount": 54.0, "shipping": 60, "tax": 24, "total": 570.0}),
    ({"items": [{"price": 1550, "qty": 1}], "coupon": "OFF50"}, None,
     {"subtotal": 1550, "discount": 50, "shipping": 0, "tax": 75, "total": 1575}),
    ({"items": [{"price": 1000, "qty": 1}]}, "vip",
     {"subtotal": 1000, "discount": 0, "shipping": 60, "tax": 50, "total": 1110}),
    ({"items": [{"price": 10.5, "qty": 1}]}, None,
     {"subtotal": 10.5, "discount": 0, "shipping": 60, "tax": 1, "total": 71.5}),
]


def types_of(result: dict) -> dict:
    """把結果轉成 {欄位: 型別}，用來抓 int/float 漂移。"""
    return {key: type(value) for key, value in result.items()}


class TestSubtotal(unittest.TestCase):
    def test_sum_int(self):
        result = pricing.subtotal([{"price": 100, "qty": 2}, {"price": 50, "qty": 1}])
        self.assertEqual(result, 250)
        self.assertIs(type(result), int)

    def test_empty_is_int_zero(self):
        result = pricing.subtotal([])
        self.assertEqual(result, 0)
        self.assertIs(type(result), int)

    def test_float_price(self):
        result = pricing.subtotal([{"price": 10.5, "qty": 1}])
        self.assertEqual(result, 10.5)
        self.assertIs(type(result), float)

    def test_qty_zero_raises(self):
        with self.assertRaisesRegex(ValueError, "qty must be positive"):
            pricing.subtotal([{"price": 1, "qty": 0}])

    def test_qty_negative_raises(self):
        with self.assertRaises(ValueError):
            pricing.subtotal([{"price": 1, "qty": 1}, {"price": 1, "qty": -1}])

    def test_checks_qty_before_reading_later_items(self):
        # 第一筆就拋，不會讀到第二筆缺 price 的 KeyError
        with self.assertRaises(ValueError):
            pricing.subtotal([{"price": 1, "qty": 0}, {"qty": 1}])


class TestDiscount(unittest.TestCase):
    def test_vip_is_float(self):
        result = pricing.discount(1200, "VIP", None)
        self.assertEqual(result, 120.0)
        self.assertIs(type(result), float)

    def test_sale_at_threshold(self):
        result = pricing.discount(1000, "SALE", None)
        self.assertEqual(result, 100)
        self.assertIs(type(result), int)

    def test_sale_below_threshold_is_int_zero(self):
        result = pricing.discount(999, "SALE", None)
        self.assertEqual(result, 0)
        self.assertIs(type(result), int)

    def test_off50_uses_net_after_tier(self):
        self.assertEqual(pricing.discount(540, "VIP", "OFF50"), 54.0)
        self.assertEqual(pricing.discount(1000, "VIP", "OFF50"), 150.0)
        self.assertEqual(pricing.discount(1100, "SALE", "OFF50"), 150)
        self.assertIs(type(pricing.discount(1100, "SALE", "OFF50")), int)

    def test_off50_threshold(self):
        self.assertEqual(pricing.discount(500, None, "OFF50"), 50)
        self.assertEqual(pricing.discount(499, None, "OFF50"), 0)

    def test_unknown_tier_and_coupon(self):
        self.assertEqual(pricing.discount(1000, "vip", "off50"), 0)
        self.assertEqual(pricing.discount(1000, "GOLD", "XYZ"), 0)


class TestShipping(unittest.TestCase):
    def test_free_at_threshold(self):
        self.assertEqual(pricing.shipping(1500, "remote"), 0)

    def test_remote(self):
        self.assertEqual(pricing.shipping(1499.9, "remote"), 150)

    def test_standard_and_case_sensitive(self):
        self.assertEqual(pricing.shipping(100, None), 60)
        self.assertEqual(pricing.shipping(100, "REMOTE"), 60)

    def test_returns_int(self):
        for net, region in ((0, None), (100, "remote"), (2000, None)):
            self.assertIs(type(pricing.shipping(net, region)), int)


class TestTax(unittest.TestCase):
    def test_bankers_rounding(self):
        self.assertEqual(pricing.tax(50), 2)     # round(2.5) = 2
        self.assertEqual(pricing.tax(1050), 52)  # round(52.5) = 52
        self.assertEqual(pricing.tax(1350), 68)  # round(67.5) = 68

    def test_returns_int(self):
        self.assertIs(type(pricing.tax(1080.0)), int)


class TestCalculate(unittest.TestCase):
    def test_matches_snapshot(self):
        expected = json.loads(SNAPSHOT.read_text(encoding="utf-8"))
        actual = [pricing.calculate(o, t) for o, t in CASES]
        self.assertEqual(actual, expected)

    def test_matches_legacy_values_and_types(self):
        for order, tier in CASES:
            with self.subTest(order=order, tier=tier):
                legacy = legacy_order.calc(order, tier)
                new = pricing.calculate(order, tier)
                self.assertEqual(new, legacy)
                self.assertEqual(list(new), list(legacy))  # key 順序
                self.assertEqual(types_of(new), types_of(legacy))

    def test_extra_cases(self):
        for order, tier, expected in EXTRA_CASES:
            with self.subTest(order=order, tier=tier):
                new = pricing.calculate(order, tier)
                self.assertEqual(new, expected)
                self.assertEqual(types_of(new), types_of(expected))
                self.assertEqual(types_of(new), types_of(legacy_order.calc(order, tier)))

    def test_remote_case_sensitive(self):
        result = pricing.calculate({"items": [{"price": 1, "qty": 1}], "region": "REMOTE"})
        self.assertEqual(result["shipping"], 60)

    def test_empty_items_all_int(self):
        result = pricing.calculate({"items": []})
        self.assertEqual(result, {"subtotal": 0, "discount": 0, "shipping": 60,
                                  "tax": 0, "total": 60})
        self.assertTrue(all(type(v) is int for v in result.values()))

    def test_bad_qty_raises(self):
        with self.assertRaises(ValueError):
            pricing.calculate({"items": [{"price": 1, "qty": 0}]})

    def test_missing_items_raises_keyerror(self):
        with self.assertRaises(KeyError):
            pricing.calculate({})


if __name__ == "__main__":
    unittest.main()
