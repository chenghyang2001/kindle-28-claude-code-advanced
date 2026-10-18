"""共用 fixture：每個測試拿到獨立的記憶體 DB，避免共享狀態。"""
import pytest

from bookshelf import db
from bookshelf.service import Library

ISBN_A = "9780306406157"
ISBN_B = "9781861972712"


@pytest.fixture
def conn():
    c = db.connect(":memory:")
    yield c
    c.close()


@pytest.fixture
def lib(conn):
    library = Library(conn)
    library.add_book(ISBN_A, "測試驅動開發")
    library.add_book(ISBN_B, "重構")
    return library
