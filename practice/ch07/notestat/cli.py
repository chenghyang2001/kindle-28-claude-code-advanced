"""命令列入口：python -m notestat <檔案或資料夾>"""
import argparse
import json
import sys
from pathlib import Path

from notestat.core import summarize


def collect_files(target: Path) -> list[Path]:
    """單檔直接回傳；資料夾則遞迴找 *.md 並排序（輸出穩定，方便比對）。"""
    if target.is_file():
        return [target]
    if target.is_dir():
        return sorted(target.rglob("*.md"))
    raise FileNotFoundError(f"找不到路徑：{target}")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="notestat", description="統計 Markdown 筆記")
    parser.add_argument("target", help="檔案或資料夾")
    parser.add_argument("--json", action="store_true", help="以 JSON 輸出")
    args = parser.parse_args(argv)

    try:
        files = collect_files(Path(args.target))
    except FileNotFoundError as err:
        print(f"錯誤：{err}", file=sys.stderr)
        return 2

    results = {}
    for path in files:
        try:
            results[path.as_posix()] = summarize(path.read_text(encoding="utf-8"))
        except UnicodeDecodeError:
            print(f"警告：{path} 不是 UTF-8，已略過", file=sys.stderr)

    if args.json:
        print(json.dumps(results, ensure_ascii=False, indent=2))
    else:
        for name, stat in results.items():
            print(f"{name}\tlines={stat['lines']}\twords={stat['words']}\theadings={stat['headings']}")
        total_words = sum(s["words"] for s in results.values())
        print(f"TOTAL\tfiles={len(results)}\twords={total_words}")
    return 0
