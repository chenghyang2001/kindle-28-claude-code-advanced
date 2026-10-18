"""CSV 欄位統計腳本：對數值欄位計算 count / sum / mean / median / min / max，支援分組與欄位篩選。"""
import argparse
import csv
import json
import sys
from pathlib import Path

EMPTY_GROUP = "(空)"


def read_rows(csv_path):
    """讀取 CSV，回傳 list[dict]。"""
    path = Path(csv_path)
    if not path.is_file():
        raise FileNotFoundError(f"找不到檔案：{csv_path}")
    with path.open(encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh))


def to_number(value):
    """轉成 float；空字串或非數字回傳 None（視為缺值）。"""
    if value is None or value.strip() == "":
        return None
    try:
        return float(value)
    except ValueError:
        return None


def numeric_columns(rows):
    """所有非空值都能轉數字、且至少一個非空值的欄位才算數值欄位。"""
    if not rows:
        return []
    result = []
    for col in rows[0].keys():
        values = [r[col] for r in rows if r[col] is not None and r[col].strip() != ""]
        if values and all(to_number(v) is not None for v in values):
            result.append(col)
    return result


def median(nums):
    """中位數；偶數個取中間兩數平均，空清單回傳 None。"""
    if not nums:
        return None
    ordered = sorted(nums)
    mid = len(ordered) // 2
    if len(ordered) % 2:
        return ordered[mid]
    return (ordered[mid - 1] + ordered[mid]) / 2


def column_stats(rows, column):
    """單一欄位統計，略過缺值。"""
    nums = [n for n in (to_number(r.get(column)) for r in rows) if n is not None]
    if not nums:
        return {"count": 0, "sum": 0.0, "mean": None, "median": None, "min": None, "max": None}
    return {
        "count": len(nums),
        "sum": sum(nums),
        "mean": sum(nums) / len(nums),
        "median": median(nums),
        "min": min(nums),
        "max": max(nums),
    }


def resolve_columns(rows, columns=None, exclude=None):
    """決定要統計的欄位：None → 全部數值欄位；有給則驗證存在（KeyError）且為數值（ValueError）。"""
    # 數值判定一律用全部 rows，分組時才不會因某組全缺值而判定不一致
    numeric = [c for c in numeric_columns(rows) if c != exclude]
    if columns is None:
        return numeric
    header = list(rows[0].keys()) if rows else []
    for col in columns:
        if col not in header:
            raise KeyError(f"欄位不存在：{col}")
        if col not in numeric:
            raise ValueError(f"欄位不是數值欄位：{col}")
    return list(columns)


def compute_stats(rows, columns=None):
    """回傳 {欄位: 統計 dict}；columns 可指定欄位與輸出順序。"""
    return {col: column_stats(rows, col) for col in resolve_columns(rows, columns)}


def group_rows(rows, group_by):
    """依 group_by 欄位分組；空值歸到 "(空)"，回傳依鍵排序的 dict。"""
    groups = {}
    for row in rows:
        raw = row.get(group_by)
        key = raw if raw is not None and raw.strip() != "" else EMPTY_GROUP
        groups.setdefault(key, []).append(row)
    return {key: groups[key] for key in sorted(groups)}


def compute_grouped_stats(rows, group_by, columns=None):
    """回傳 {群組值: {欄位: 統計 dict}}；group_by 不存在拋 KeyError。"""
    header = list(rows[0].keys()) if rows else []
    if group_by not in header:
        raise KeyError(f"分組欄位不存在：{group_by}")
    target_cols = resolve_columns(rows, columns, exclude=group_by)
    return {
        key: {col: column_stats(group, col) for col in target_cols}
        for key, group in group_rows(rows, group_by).items()
    }


def parse_columns(text):
    """把 "a,b" 轉成 ["a", "b"]；未提供回傳 None。"""
    if text is None:
        return None
    return [c.strip() for c in text.split(",") if c.strip() != ""]


def main(argv=None):
    parser = argparse.ArgumentParser(description="CSV 數值欄位統計")
    parser.add_argument("csv_path")
    parser.add_argument("--group-by", dest="group_by", default=None, help="分組欄位")
    parser.add_argument("--columns", default=None, help="要統計的欄位，以逗號分隔")
    args = parser.parse_args(argv)
    try:
        rows = read_rows(args.csv_path)
        columns = parse_columns(args.columns)
        if args.group_by is None:
            result = compute_stats(rows, columns)
        else:
            result = compute_grouped_stats(rows, args.group_by, columns)
    except KeyError as exc:
        # KeyError 的 str() 會多包一層引號，改取原始訊息
        print(f"錯誤：{exc.args[0] if exc.args else exc}", file=sys.stderr)
        return 1
    except (FileNotFoundError, ValueError, UnicodeDecodeError, csv.Error) as exc:
        print(f"錯誤：{exc}", file=sys.stderr)
        return 1
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
