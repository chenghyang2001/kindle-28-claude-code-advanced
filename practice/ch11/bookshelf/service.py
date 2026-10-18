"""商業邏輯：借書、還書、報表（串接 rules 與 db）。"""
from dataclasses import dataclass, field
from datetime import date, timedelta

from . import db
from .rules import ValidationError, calc_fine, is_valid_isbn, normalize_isbn

LOAN_DAYS = 14


class LibraryError(Exception):
    """商業規則違反（例如重複借出）。"""


class Library:
    def __init__(self, conn):
        self.conn = conn

    def add_book(self, raw_isbn: str, title: str) -> str:
        isbn = normalize_isbn(raw_isbn)
        if not is_valid_isbn(isbn):
            raise ValidationError(f"ISBN 檢查碼錯誤：{raw_isbn}")
        if not title or not title.strip():
            raise ValidationError("書名不可為空")
        if db.get_book(self.conn, isbn) is not None:
            raise LibraryError(f"書已存在：{isbn}")
        db.insert_book(self.conn, isbn, title.strip())
        return isbn

    def borrow(self, raw_isbn: str, member: str, today: date) -> date:
        isbn = normalize_isbn(raw_isbn)
        if db.get_book(self.conn, isbn) is None:
            raise LibraryError(f"查無此書：{isbn}")
        if db.open_loan(self.conn, isbn) is not None:
            raise LibraryError(f"已被借出：{isbn}")
        due = today + timedelta(days=LOAN_DAYS)
        db.insert_loan(self.conn, isbn, member, today.isoformat(), due.isoformat())
        return due

    def give_back(self, raw_isbn: str, today: date) -> int:
        isbn = normalize_isbn(raw_isbn)
        loan = db.open_loan(self.conn, isbn)
        if loan is None:
            raise LibraryError(f"此書沒有借出紀錄：{isbn}")
        fine = calc_fine(date.fromisoformat(loan["due"]), today)
        db.close_loan(self.conn, loan["id"], today.isoformat(), fine)
        return fine

    def report(self, today: date) -> str:
        s = summarize_loans(db.all_loans(self.conn), today)
        header = f"=== 借閱報表 {today.isoformat()} ==="
        footer = f"借出中：{s.out}，逾期：{s.late}，已收罰金：{s.collected}"
        return "\n".join([header, *map(format_entry, s.entries), footer])


@dataclass
class Entry:
    kind: str       # "out" 借出中 / "late" 逾期 / "returned" 已還且有罰金
    title: str
    member: str
    due: str
    fine: int = 0


@dataclass
class Summary:
    entries: list = field(default_factory=list)
    out: int = 0
    late: int = 0
    collected: int = 0


def format_entry(e: Entry) -> str:
    """單筆報表列的文字格式。"""
    if e.kind == "late":
        return f"[逾期] {e.title} / {e.member} / 到期 {e.due} / 預估罰金 {e.fine}"
    if e.kind == "out":
        return f"[借出] {e.title} / {e.member} / 到期 {e.due}"
    return f"[已還] {e.title} / {e.member} / 罰金 {e.fine}"


def summarize_loans(rows, today: date) -> Summary:
    """純計算：把借閱紀錄分類並統計，不處理任何文字格式。"""
    s = Summary()
    for r in rows:
        if r["returned"] is not None:
            s.collected += r["fine"]
            if r["fine"] > 0:   # 準時歸還的不列在報表上（保留原行為）
                s.entries.append(Entry("returned", r["title"], r["member"], r["due"], r["fine"]))
            continue
        s.out += 1
        due = date.fromisoformat(r["due"])
        if today > due:
            s.late += 1
            s.entries.append(Entry("late", r["title"], r["member"], r["due"], calc_fine(due, today)))
        else:
            s.entries.append(Entry("out", r["title"], r["member"], r["due"]))
    return s
