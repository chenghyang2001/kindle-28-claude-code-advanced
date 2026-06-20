# 練習 03 解答 — 為 legacy 函式補測試

## 核心概念：安全網（characterization test）
補測試的目的**不是判斷對錯，而是把「現在的行為」釘死記錄**。之後重構時測試仍綠 = 行為前後一致、沒改壞。

## 問題一：為什麼只補測試不改行為？照現況還是應該？
- **照「現在實際的樣子」寫**，不是「應該的樣子」。
- 比喻：翻修舊房子前先把每個角落拍照存證（醜也照原樣拍），翻修後才分得清哪些是你改的。
- 正確順序：
  1. 照現況補測試 → 行為釘住、全綠
  2. 才有底氣重構 / 修 bug（修 bug 是另一個動作：先改測試預期值、再改程式，有意識地一起改）
- 補測試時若發現明顯 bug → 先照現況寫進測試 + 註記可疑，安全網建好後再開獨立動作修。**先釘住，再修正。**

## 問題二 / 任務：三類測試（pytest 範例）

```python
import pytest
from legacy import parse_amount

def test_normal():            # happy path：正常合理輸入
    assert parse_amount("1,234.5") == 1234.5

def test_empty():             # edge case：空/零/None/極值/特殊字元
    assert parse_amount("") == 0.0

def test_invalid():           # error case：非法輸入 → 正確拋錯
    with pytest.raises(ValueError):
        parse_amount("abc")
```

| 類別 | 測什麼 |
|------|--------|
| happy path | 正常輸入 → 正確結果 |
| edge case | 空/零/None/極值/特殊字元 |
| error case | 非法輸入 → 正確拋錯 |

## 限制條件遵守
- ✅ 不改原函式行為，只補測試（先用測試釘住現況）
- ✅ 涵蓋 happy / edge / error 三類

## 關鍵收穫
- legacy 補測試＝建重構安全網，照「現況」釘住而非照「理想」。
- 釘住與修 bug 是兩個分開的動作，不可在補網時順手改行為。
