"""整合測試：Library（商業邏輯）＋ 真實 sqlite3（記憶體 / 暫存檔）。"""
from datetime import date

import pytest

from bookshelf import db
from bookshelf.rules import ValidationError
from bookshelf.service import Library, LibraryError
from tests.conftest import ISBN_A


def test_add_and_list(lib, conn):
    titles = [r["title"] for r in db.list_books(conn)]
    assert titles == sorted(["測試驅動開發", "重構"])


def test_add_invalid_isbn_rejected(conn):
    with pytest.raises(ValidationError):
        Library(conn).add_book("9780306406158", "壞 ISBN")


def test_borrow_sets_due_14_days(lib):
    assert lib.borrow(ISBN_A, "alice", date(2026, 1, 1)) == date(2026, 1, 15)


def test_cannot_borrow_twice(lib):
    lib.borrow(ISBN_A, "alice", date(2026, 1, 1))
    with pytest.raises(LibraryError):
        lib.borrow(ISBN_A, "bob", date(2026, 1, 2))


def test_return_late_records_fine(lib, conn):
    lib.borrow(ISBN_A, "alice", date(2026, 1, 1))
    assert lib.give_back(ISBN_A, date(2026, 1, 17)) == 10
    loan = db.all_loans(conn)[0]
    assert loan["returned"] == "2026-01-17" and loan["fine"] == 10


def test_data_persists_in_file(tmp_path):
    path = str(tmp_path / "lib.db")
    c1 = db.connect(path)
    Library(c1).add_book(ISBN_A, "持久化")
    c1.close()
    c2 = db.connect(path)
    assert db.get_book(c2, ISBN_A)["title"] == "持久化"
    c2.close()


# --- 依 coverage 缺口補的測試（service.py 第 23、25、32、43 行：錯誤路徑） ---
@pytest.mark.parametrize("action, exc", [
    (lambda lib: lib.add_book(ISBN_A, "   "), ValidationError),          # 空書名
    (lambda lib: lib.add_book(ISBN_A, "重複"), LibraryError),            # 重複新增
    (lambda lib: lib.borrow("9780131103627", "bob", date(2026, 1, 1)), LibraryError),  # 查無此書
    (lambda lib: lib.give_back(ISBN_A, date(2026, 1, 1)), LibraryError),  # 沒借就還
])
def test_service_error_paths(lib, action, exc):
    with pytest.raises(exc):
        action(lib)
