"""sqlite3 資料存取層（整合測試的主要對象）。"""
import sqlite3

SCHEMA = """
CREATE TABLE IF NOT EXISTS books (
    isbn  TEXT PRIMARY KEY,
    title TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS loans (
    id       INTEGER PRIMARY KEY AUTOINCREMENT,
    isbn     TEXT NOT NULL REFERENCES books(isbn),
    member   TEXT NOT NULL,
    borrowed TEXT NOT NULL,
    due      TEXT NOT NULL,
    returned TEXT,
    fine     INTEGER NOT NULL DEFAULT 0
);
"""


def connect(path: str = ":memory:") -> sqlite3.Connection:
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    conn.executescript(SCHEMA)
    return conn


def insert_book(conn, isbn: str, title: str) -> None:
    with conn:
        conn.execute("INSERT INTO books (isbn, title) VALUES (?, ?)", (isbn, title))


def get_book(conn, isbn: str):
    return conn.execute("SELECT * FROM books WHERE isbn = ?", (isbn,)).fetchone()


def list_books(conn):
    return conn.execute("SELECT * FROM books ORDER BY title").fetchall()


def open_loan(conn, isbn: str):
    """取得某本書尚未歸還的借閱紀錄（沒有則回傳 None）。"""
    return conn.execute(
        "SELECT * FROM loans WHERE isbn = ? AND returned IS NULL", (isbn,)
    ).fetchone()


def insert_loan(conn, isbn: str, member: str, borrowed: str, due: str) -> int:
    with conn:
        cur = conn.execute(
            "INSERT INTO loans (isbn, member, borrowed, due) VALUES (?, ?, ?, ?)",
            (isbn, member, borrowed, due),
        )
    return cur.lastrowid


def close_loan(conn, loan_id: int, returned: str, fine: int) -> None:
    with conn:
        conn.execute(
            "UPDATE loans SET returned = ?, fine = ? WHERE id = ?",
            (returned, fine, loan_id),
        )


def all_loans(conn):
    return conn.execute(
        "SELECT l.*, b.title FROM loans l JOIN books b ON b.isbn = l.isbn ORDER BY l.id"
    ).fetchall()
