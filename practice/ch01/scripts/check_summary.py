"""獨立核對 summary.md 的平均值（不沿用 Claude 寫的程式，避免自己驗自己）。

用法：python scripts/check_summary.py <sales.csv> <summary.md>
"""
import csv
import re
import sys
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path

NUMERIC_COLUMNS = ["unit_price", "quantity", "total"]


def expected_means(csv_path: Path) -> dict:
    """逐欄略過空值後計算平均，四捨五入到 2 位（ROUND_HALF_UP）。"""
    with csv_path.open(encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f))
    means = {}
    for col in NUMERIC_COLUMNS:
        values = [Decimal(r[col]) for r in rows if r[col].strip() != ""]
        if not values:
            means[col] = None
            continue
        means[col] = (sum(values, Decimal(0)) / len(values)).quantize(Decimal("0.01"), ROUND_HALF_UP)
    return means


def parse_table(md_path: Path) -> dict:
    """從 Markdown 表格取出「欄位 → 平均值」。"""
    table = {}
    for line in md_path.read_text(encoding="utf-8").splitlines():
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) >= 2 and cells[0] in NUMERIC_COLUMNS:
            table[cells[0]] = Decimal(cells[1])
    return table


def is_valid_gfm_table(md_path: Path) -> bool:
    """表頭＋分隔列＋資料列欄數一致。"""
    lines = [l for l in md_path.read_text(encoding="utf-8").splitlines() if l.startswith("|")]
    if len(lines) < 3 or not re.fullmatch(r"\|(\s*:?-+:?\s*\|)+", lines[1].replace(" ", "")):
        return False
    return len({l.count("|") for l in lines}) == 1


def main():
    if len(sys.argv) != 3:
        print("用法：python check_summary.py <sales.csv> <summary.md>", file=sys.stderr)
        sys.exit(2)
    csv_path, md_path = Path(sys.argv[1]), Path(sys.argv[2])
    for p in (csv_path, md_path):
        if not p.is_file():
            print(f"錯誤：找不到檔案 {p}", file=sys.stderr)
            sys.exit(1)
    try:
        expected = expected_means(csv_path)
        actual = parse_table(md_path)
    except (OSError, ValueError, ArithmeticError) as e:
        print(f"錯誤：解析失敗 {e}", file=sys.stderr)
        sys.exit(1)
    all_ok = is_valid_gfm_table(md_path)
    print(f"GFM 表格格式：{'PASS' if all_ok else 'FAIL'}")
    for col in NUMERIC_COLUMNS:
        ok = actual.get(col) == expected[col]
        all_ok &= ok
        print(f"{col:11} 預期 {expected[col]}  實際 {actual.get(col)}  {'PASS' if ok else 'FAIL'}")
    print("OVERALL:", "PASS" if all_ok else "FAIL")
    sys.exit(0 if all_ok else 1)


if __name__ == "__main__":
    main()
