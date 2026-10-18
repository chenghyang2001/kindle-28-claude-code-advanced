import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from orders import apply_discount, order_total, summarize


def test_order_total():
    order = {"items": [{"price": 100, "qty": 2}, {"price": 50, "qty": 1}]}
    assert order_total(order) == 250


def test_vip_discount():
    order = {"vip": True, "items": [{"price": 100, "qty": 1}]}
    assert apply_discount(order) == 90


def test_summarize_runs():
    orders = [{"vip": False, "items": [{"price": 10, "qty": 1}]}]
    assert summarize(orders) == (10, 10, 0)


def test_coupon_not_accumulated_across_calls():
    order = {"items": [{"price": 100, "qty": 1}], "coupon": 10}
    assert apply_discount(order) == 90
    assert apply_discount(order) == 90


def test_bulk_threshold_inclusive():
    order = {"items": [{"price": 1000, "qty": 1}]}
    assert apply_discount(order) == 950


def test_summarize_values_and_failure():
    orders = [
        {"id": "ok", "items": [{"price": 100, "qty": 1}]},
        {"id": "bad", "items": [{"price": 80, "qty": "two"}]},
    ]
    assert summarize(orders) == (100, 100, 1)


def test_summarize_empty_and_all_failed():
    assert summarize([]) == (0, None, 0)
    bad = [{"id": "bad", "items": [{"qty": 1}]}]
    assert summarize(bad) == (0, None, 1)


def test_coupon_cannot_make_total_negative():
    order = {"items": [{"price": 10, "qty": 1}], "coupon": 50}
    assert apply_discount(order) == 0


def test_summarize_non_dict_order_counts_as_failed():
    assert summarize([None]) == (0, None, 1)


def test_vip_and_bulk_stack():
    order = {"vip": True, "items": [{"price": 1200, "qty": 1}]}
    assert apply_discount(order) == 1026
