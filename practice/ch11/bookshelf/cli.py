"""命令列入口（端對端測試的對象）：python -m bookshelf.cli --db x.db <指令>。"""
import argparse
import sys
from datetime import date

from . import db
from .rules import ValidationError, parse_date
from .service import Library, LibraryError


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="bookshelf", description="書籍借閱管理")
    p.add_argument("--db", default="bookshelf.db", help="sqlite 檔案路徑")
    sub = p.add_subparsers(dest="cmd", required=True)
    a = sub.add_parser("add")
    a.add_argument("isbn")
    a.add_argument("title")
    b = sub.add_parser("borrow")
    b.add_argument("isbn")
    b.add_argument("member")
    b.add_argument("--date", default=None)
    r = sub.add_parser("return")
    r.add_argument("isbn")
    r.add_argument("--date", default=None)
    sub.add_parser("list")
    rp = sub.add_parser("report")
    rp.add_argument("--date", default=None)
    return p


def _day(text):
    return parse_date(text) if text else date.today()


def main(argv=None) -> int:
    args = build_parser().parse_args(argv)
    conn = db.connect(args.db)
    lib = Library(conn)
    try:
        if args.cmd == "add":
            print(f"已新增：{lib.add_book(args.isbn, args.title)}")
        elif args.cmd == "borrow":
            print(f"借出成功，到期日 {lib.borrow(args.isbn, args.member, _day(args.date))}")
        elif args.cmd == "return":
            print(f"歸還成功，罰金 {lib.give_back(args.isbn, _day(args.date))} 元")
        elif args.cmd == "list":
            for row in db.list_books(conn):
                print(f"{row['isbn']}  {row['title']}")
        elif args.cmd == "report":
            print(lib.report(_day(args.date)))
        return 0
    except (ValidationError, LibraryError) as exc:
        print(f"錯誤：{exc}", file=sys.stderr)
        return 1
    finally:
        conn.close()


if __name__ == "__main__":
    sys.exit(main())
