"""notestat.core 測試：正常、邊界、錯誤三類。"""
import pytest

from notestat.core import count_headings, count_words, summarize


def test_count_words_mixed():
    assert count_words("今天學 Claude Code") == 5  # 今天學=3 + Claude + Code


def test_count_words_empty():
    assert count_words("") == 0


def test_count_words_none_raises():
    with pytest.raises(ValueError):
        count_words(None)


def test_count_headings_ignores_hashtag():
    text = "# 標題\n## 小節\n#hashtag 不是標題\n"
    assert count_headings(text) == 2


def test_summarize():
    assert summarize("# A\nhello world\n") == {"lines": 2, "words": 4, "headings": 1}
