"""單元測試：rules.py 純函式，不碰 DB、不碰檔案，毫秒級。"""
from datetime import date

import pytest

from bookshelf.rules import ValidationError, calc_fine, is_valid_isbn, normalize_isbn, parse_date


@pytest.mark.parametrize("raw", ["978-0-306-40615-7", "9780306406157", "0-306-40615-2"])
def test_valid_isbn(raw):
    assert is_valid_isbn(raw)


@pytest.mark.parametrize("raw", ["9780306406158", "12345", "", "97803064061AB"])
def test_invalid_isbn(raw):
    assert not is_valid_isbn(raw)


def test_normalize_strips_dash_and_space():
    assert normalize_isbn(" 978-0306 406157 ") == "9780306406157"


def test_normalize_none_raises():
    with pytest.raises(ValidationError):
        normalize_isbn(None)


def test_parse_date_ok():
    assert parse_date("2026-10-18") == date(2026, 10, 18)


def test_parse_date_bad():
    with pytest.raises(ValidationError):
        parse_date("2026/10/18")


def test_fine_on_time_is_zero():
    assert calc_fine(date(2026, 1, 10), date(2026, 1, 10)) == 0


def test_fine_three_days_late():
    assert calc_fine(date(2026, 1, 10), date(2026, 1, 13)) == 15


# --- 依 coverage 缺口補的測試（rules.py 第 24 行：ISBN-10 非法字元分支） ---
@pytest.mark.parametrize("raw, expected", [("080442957X", True), ("08044295XX", False), ("1234X67890", False)])
def test_isbn10_check_digit_x_and_bad_chars(raw, expected):
    assert is_valid_isbn(raw) is expected


# coverage 盲點：calc_fine 的上限是用 min() 實作，不是 if 分支，
# 所以就算沒測過上限，branch coverage 仍顯示 100%。這個測試是靠「讀規格」補的。
def test_fine_capped_at_200():
    assert calc_fine(date(2026, 1, 1), date(2026, 6, 1)) == 200
