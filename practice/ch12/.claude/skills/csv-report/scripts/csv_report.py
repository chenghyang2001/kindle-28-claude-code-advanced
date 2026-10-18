"""csv-report skill 的輔助腳本：計算 CSV 各數值欄平均，輸出 Markdown 報告。"""
import csv
import sys
from pathlib import Path

MISSING = {"", "na", "n/a", "null", "none"}


def to_number(text):
    """能轉數字就回傳 float，缺值回傳 None，非數字丟 ValueError。"""
    if text.strip().lower() in MISSING:
        return None
    return float(text)


def summarize(rows, headers):
    """回傳 [(欄名, 型別, 有效筆數, 平均或 None)]。"""
    stats = []
    for col in headers:
        values, is_numeric = [], True
        for row in rows:
            try:
                num = to_number(row.get(col) or "")
            except ValueError:
                is_numeric = False
                break
            if num is not None:
                values.append(num)
        if not is_numeric:
            stats.append((col, "文字", None, None))
        else:
            avg = round(sum(values) / len(values), 2) if values else None
            stats.append((col, "數值", len(values), avg))
    return stats


def render(csv_path, stats, row_count):
    lines = [f"# {csv_path.name} 摘要", "", f"處理列數：{row_count}", "",
             "| 欄位 | 型別 | 有效筆數 | 平均 |", "| --- | --- | ---: | ---: |"]
    for col, kind, count, avg in stats:
        lines.append(f"| {col} | {kind} | {'-' if count is None else count} | "
                     f"{'-' if avg is None else f'{avg:.2f}'} |")
    return "\n".join(lines) + "\n"


def main():
    if len(sys.argv) != 2:
        print("錯誤：用法 csv_report.py <csv 路徑>", file=sys.stderr)
        sys.exit(2)
    csv_path = Path(sys.argv[1])
    try:
        with csv_path.open(encoding="utf-8-sig", newline="") as f:
            reader = csv.DictReader(f)
            rows = list(reader)
            headers = reader.fieldnames
    except FileNotFoundError:
        print(f"錯誤：找不到檔案 {csv_path}", file=sys.stderr)
        sys.exit(1)
    except UnicodeDecodeError as e:
        print(f"錯誤：{csv_path} 不是 UTF-8 編碼（{e}）", file=sys.stderr)
        sys.exit(1)
    if not headers:
        print(f"錯誤：{csv_path} 是空檔，沒有標題列", file=sys.stderr)
        sys.exit(1)
    out_path = csv_path.with_name(f"{csv_path.stem}-summary.md")
    out_path.write_text(render(csv_path, summarize(rows, headers), len(rows)), encoding="utf-8")
    print(f"報告：{out_path}")
    print(f"處理列數：{len(rows)}")


if __name__ == "__main__":
    main()
