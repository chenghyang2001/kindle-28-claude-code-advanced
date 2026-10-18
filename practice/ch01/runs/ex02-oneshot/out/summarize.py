"""計算 data/sales.csv 數值欄平均，輸出 out/summary.md（快速 demo 模式）"""
import csv
import sys
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
CSV_PATH = BASE_DIR / "data" / "sales.csv"
OUT_PATH = BASE_DIR / "out" / "summary.md"
NUMERIC_COLS = ["unit_price", "quantity", "total"]
TWO_PLACES = Decimal("0.01")


def parse_cell(raw, col, line_no):
    """空字串/空白視為缺值；非數字也當缺值但要警告列號"""
    text = (raw or "").strip()
    if not text:
        return None
    try:
        return Decimal(text)
    except InvalidOperation:
        print(f"警告：第 {line_no} 列 {col} 非數字「{text}」，視為缺值", file=sys.stderr)
        return None


def collect(csv_path):
    values = {c: [] for c in NUMERIC_COLS}
    skipped = {c: 0 for c in NUMERIC_COLS}
    row_count = rows_with_missing = 0
    with open(csv_path, encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        missing_cols = [c for c in NUMERIC_COLS if c not in (reader.fieldnames or [])]
        if missing_cols:
            raise ValueError(f"CSV 缺少欄位：{missing_cols}")
        # 表頭是第 1 列，資料從第 2 列起算（檔案行號）
        for line_no, row in enumerate(reader, start=2):
            row_count += 1
            has_missing = False
            for col in NUMERIC_COLS:
                num = parse_cell(row.get(col), col, line_no)
                if num is None:
                    skipped[col] += 1
                    has_missing = True
                else:
                    values[col].append(num)
            rows_with_missing += has_missing
    return values, skipped, row_count, rows_with_missing


def render_markdown(values):
    lines = ["# sales.csv 數值欄平均", "", "| 欄位 | 平均值 | 有效筆數 |", "|---|---:|---:|"]
    for col in NUMERIC_COLS:
        nums = values[col]
        avg = (sum(nums, Decimal(0)) / len(nums)).quantize(TWO_PLACES, ROUND_HALF_UP) if nums else "N/A"
        lines.append(f"| {col} | {avg} | {len(nums)} |")
    return "\n".join(lines) + "\n"


def main():
    try:
        values, skipped, row_count, rows_with_missing = collect(CSV_PATH)
        OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
        OUT_PATH.write_text(render_markdown(values), encoding="utf-8", newline="\n")
    except (OSError, ValueError, csv.Error) as e:
        print(f"錯誤：{e}", file=sys.stderr)
        sys.exit(1)
    print(f"處理資料列：{row_count}")
    print(f"含缺值的列：{rows_with_missing}")
    print("各欄略過數：" + ", ".join(f"{c}={skipped[c]}" for c in NUMERIC_COLS))


if __name__ == "__main__":
    main()
