"""單元測試：重構後拆出的純函式 summarize_loans / format_entry，用 dict 假資料、不需 DB。"""
from datetime import date

from bookshelf.service import Entry, format_entry, summarize_loans


def row(title, due, returned=None, fine=0):
    return {"title": title, "member": "m", "due": due, "returned": returned, "fine": fine}


def test_summarize_counts():
    rows = [row("A", "2026-03-15"), row("B", "2026-03-01"), row("C", "2026-01-01", "2026-01-05", 20)]
    s = summarize_loans(rows, date(2026, 3, 10))
    assert (s.out, s.late, s.collected) == (2, 1, 20)
    assert [e.kind for e in s.entries] == ["out", "late", "returned"]


def test_format_entry_late():
    assert format_entry(Entry("late", "書", "amy", "2026-01-01", 30)) == "[逾期] 書 / amy / 到期 2026-01-01 / 預估罰金 30"
