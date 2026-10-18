"""核心統計邏輯（純函式，不碰檔案系統，方便測試）。"""
import re

# 中文沒有空白分詞，所以 CJK 字元逐字計算，其餘以空白切詞
CJK_PATTERN = re.compile(r"[一-鿿]")
HEADING_PATTERN = re.compile(r"^#{1,6}\s+\S", re.MULTILINE)


def count_words(text: str) -> int:
    """回傳字數：CJK 每字算 1，其餘以空白切出的詞算 1。"""
    if text is None:
        raise ValueError("text 不可為 None")
    cjk_count = len(CJK_PATTERN.findall(text))
    non_cjk_text = CJK_PATTERN.sub(" ", text)
    return cjk_count + len(non_cjk_text.split())


def count_headings(text: str) -> int:
    """回傳 Markdown 標題（# ~ ######）數量。"""
    return len(HEADING_PATTERN.findall(text))


def summarize(text: str) -> dict:
    """彙總一份筆記的統計結果。"""
    return {
        "lines": len(text.splitlines()),
        "words": count_words(text),
        "headings": count_headings(text),
    }
