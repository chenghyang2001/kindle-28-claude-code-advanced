# 練習 03 — 綜合挑戰：為 legacy 函式補測試

> 選配：完成前兩個練習後再挑戰

## 挑戰情境
挑一段沒有測試的 legacy 函式，在「不改它行為」的前提下補上測試，當作未來重構的安全網。

## 範例：三類測試（pytest）
```python
import pytest
from legacy import parse_amount

def test_normal():            # happy path
    assert parse_amount("1,234.5") == 1234.5

def test_empty():             # edge case
    assert parse_amount("") == 0.0

def test_invalid():           # error case
    with pytest.raises(ValueError):
        parse_amount("abc")
```

## 限制條件
- 測試需涵蓋 happy / edge / error 三類
- 不可修改原函式行為，只補測試（先用測試把現況「釘住」）

## 完成後
將解答存入 `answer/ex03-answer.md`。
