"""Characterization test（特徵測試）：在重構 Library.report() 之前，
把「現在的實際輸出」逐字釘住。這裡不判斷輸出對不對，只保證重構後輸出完全一樣。"""
from datetime import date

import pytest

from bookshelf import db
from bookshelf.service import Library

EXPECTED = (
    "=== 借閱報表 2026-03-10 ===\n"
    "[借出] 測試驅動開發 / alice / 到期 2026-03-15\n"
    "[逾期] 重構 / bob / 到期 2026-03-06 / 預估罰金 20\n"
    "[逾期] C 程式語言 / carol / 到期 2025-12-15 / 預估罰金 200\n"
    "[已還] 整潔程式碼 / dave / 罰金 15\n"
    "借出中：3，逾期：2，已收罰金：15"
)


@pytest.fixture
def scenario():
    """涵蓋 report 的每條分支：未逾期、逾期、逾期封頂、已還有罰金、已還無罰金。"""
    conn = db.connect()
    lib = Library(conn)
    for isbn, title in [
        ("9780306406157", "測試驅動開發"), ("9781861972712", "重構"),
        ("9780131103627", "C 程式語言"), ("080442957X", "整潔程式碼"),
        ("9780201633610", "設計模式"),
    ]:
        lib.add_book(isbn, title)
    lib.borrow("9780306406157", "alice", date(2026, 3, 1))
    lib.borrow("9781861972712", "bob", date(2026, 2, 20))
    lib.borrow("9780131103627", "carol", date(2025, 12, 1))
    lib.borrow("080442957X", "dave", date(2026, 1, 1))
    lib.give_back("080442957X", date(2026, 1, 18))
    lib.borrow("9780201633610", "erin", date(2026, 1, 1))
    lib.give_back("9780201633610", date(2026, 1, 10))
    yield lib
    conn.close()


def test_report_golden_master(scenario):
    assert scenario.report(date(2026, 3, 10)) == EXPECTED


def test_report_empty_library():
    lib = Library(db.connect())
    assert lib.report(date(2026, 1, 1)) == (
        "=== 借閱報表 2026-01-01 ===\n借出中：0，逾期：0，已收罰金：0"
    )


def test_report_due_today_is_not_late(scenario):
    # 邊界：到期日當天不算逾期（today > due 才算）
    text = scenario.report(date(2026, 3, 15))
    assert "[借出] 測試驅動開發 / alice / 到期 2026-03-15" in text
