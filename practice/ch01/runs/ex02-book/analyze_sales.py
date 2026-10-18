"""分析 data/sales.csv，輸出數值欄位平均值到 out/summary.md"""
import csv
import sys
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
INPUT_PATH = BASE_DIR / "data" / "sales.csv"
OUTPUT_PATH = BASE_DIR / "out" / "summary.md"
NUMERIC_COLUMNS = ["unit_price", "quantity", "total"]


def compute_averages(csv_path):
    """回傳 (各欄平均, 總列數, 含缺值列數, 各欄缺值數)"""
    sums = {col: Decimal(0) for col in NUMERIC_COLUMNS}
    counts = {col: 0 for col in NUMERIC_COLUMNS}
    missing = {col: 0 for col in NUMERIC_COLUMNS}
    row_count = 0
    rows_with_missing = 0

    with open(csv_path, encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        absent = [c for c in NUMERIC_COLUMNS if c not in (reader.fieldnames or [])]
        if absent:
            raise ValueError(f"CSV 缺少欄位：{absent}")
        for row in reader:
            row_count += 1
            has_missing = False
            for col in NUMERIC_COLUMNS:
                raw = (row[col] or "").strip()
                if raw == "":
                    missing[col] += 1
                    has_missing = True
                    continue
                # 用 Decimal 避免浮點誤差，讓四捨五入與手算一致
                sums[col] += Decimal(raw)
                counts[col] += 1
            if has_missing:
                rows_with_missing += 1

    averages = {
        col: (sums[col] / counts[col]).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        if counts[col] > 0 else None
        for col in NUMERIC_COLUMNS
    }
    return averages, row_count, rows_with_missing, missing


def render_markdown(averages):
    lines = ["| 欄位 | 平均值 |", "| --- | ---: |"]
    for col, avg in averages.items():
        lines.append(f"| {col} | {avg if avg is not None else 'N/A'} |")
    return "\n".join(lines) + "\n"


def main():
    try:
        averages, row_count, rows_with_missing, missing = compute_averages(INPUT_PATH)
    except FileNotFoundError:
        print(f"錯誤：找不到檔案 {INPUT_PATH}", file=sys.stderr)
        sys.exit(1)
    except (ValueError, ArithmeticError) as e:
        print(f"錯誤：資料格式有誤 - {e}", file=sys.stderr)
        sys.exit(1)

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(render_markdown(averages), encoding="utf-8")

    print(f"處理列數：{row_count}")
    print(f"含缺值而被跳過（至少一欄）的列數：{rows_with_missing}")
    print("各欄缺值數：" + "、".join(f"{c}={n}" for c, n in missing.items()))
    print(f"已輸出：{OUTPUT_PATH}")


if __name__ == "__main__":
    main()
