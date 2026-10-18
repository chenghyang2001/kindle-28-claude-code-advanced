"""驗證 merged.txt 是否符合練習一的結構化規格（獨立於 Claude 的自我回報）。

規格：./notes/ 底下 .txt（不含子目錄）依檔名排序、每檔前加「===== 檔名 =====」、UTF-8。
用法：python scripts/check_merged.py <notes 目錄> <merged.txt>
"""
import re
import sys
from pathlib import Path


def natural_key(name: str):
    """自然排序：3-idea 排在 10-reading 前面。"""
    return [int(tok) if tok.isdigit() else tok for tok in re.split(r"(\d+)", name)]


def check(notes_dir: Path, merged_path: Path) -> dict:
    """回傳各檢查項目的結果字典。"""
    if not notes_dir.is_dir():
        raise FileNotFoundError(f"找不到 notes 目錄：{notes_dir}")
    if not merged_path.is_file():
        raise FileNotFoundError(f"找不到合併檔：{merged_path}")

    raw = merged_path.read_bytes()
    try:
        text = raw.decode("utf-8")
        is_utf8 = True
    except UnicodeDecodeError:
        text = raw.decode("utf-8", errors="replace")
        is_utf8 = False

    sources = [p.name for p in notes_dir.glob("*.txt") if p.is_file()]
    headers = re.findall(r"^===== (.+?) =====$", text, flags=re.MULTILINE)

    return {
        "utf8": is_utf8,
        "no_bom": not raw.startswith(b"\xef\xbb\xbf"),
        "file_count_ok": sorted(headers) == sorted(sources),
        "excludes_subdir": "old.txt" not in headers and "舊筆記" not in text,
        "order_string_sort": headers == sorted(sources),
        "order_natural_sort": headers == sorted(sources, key=natural_key),
        "all_content_present": all(
            (notes_dir / s).read_text(encoding="utf-8").strip() in text for s in sources
        ),
        "headers": headers,
        "total_lines": len(text.splitlines()),
    }


def main():
    if len(sys.argv) != 3:
        print("用法：python check_merged.py <notes 目錄> <merged.txt>", file=sys.stderr)
        sys.exit(2)
    try:
        result = check(Path(sys.argv[1]), Path(sys.argv[2]))
    except (FileNotFoundError, OSError) as e:
        print(f"錯誤：{e}", file=sys.stderr)
        sys.exit(1)
    for key, value in result.items():
        print(f"{key:22} {value}")


if __name__ == "__main__":
    # 冒煙測試：python check_merged.py --selftest
    if sys.argv[1:] == ["--selftest"]:
        assert natural_key("3-idea.txt") < natural_key("10-reading.txt")
        assert sorted(["10-a", "3-b"]) == ["10-a", "3-b"]  # 字串排序的陷阱
        try:
            check(Path("不存在的目錄"), Path("x.txt"))
            raise AssertionError("應該拋出 FileNotFoundError")
        except FileNotFoundError:
            pass
        print("selftest OK")
    else:
        main()
