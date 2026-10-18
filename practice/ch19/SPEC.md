# 功能合約：csv_stats.py 新增「分組統計 + 中位數 + 欄位篩選」

> 主 session 撰寫，給兩個子代理共用的唯一依據。實作者（Agent A）只改 `csv_stats.py`；
> 測試者（Agent B）只建 `tests/test_csv_stats.py`。雙方不可修改對方的檔案，也不可改本檔。

## 1. 中位數
- `column_stats(rows, column)` 回傳的 dict 新增 `"median"` 鍵。
- 偶數個值取中間兩數平均；無有效值時 `median` 為 `None`。

## 2. 分組統計（新函式）
```python
compute_grouped_stats(rows, group_by, columns=None) -> dict
```
- 回傳 `{群組值: {欄位: 統計 dict}}`，群組值是原始字串，依字母順序排序（dict 插入順序）。
- 群組欄位值為空字串時，歸到群組 `"(空)"`。
- `group_by` 不存在於 CSV 欄位 → 拋 `KeyError`。
- 數值欄位的判定用「全部 rows」判定（不是每組各自判定），且不包含 `group_by` 本身。

## 3. 欄位篩選
- `compute_stats(rows, columns=None)` 與 `compute_grouped_stats` 都接受 `columns`（list[str] 或 None）。
- `None` → 所有數值欄位；有給 → 只輸出這些欄位，順序依傳入順序。
- 指定欄位不存在 → 拋 `KeyError`；存在但非數值欄位 → 拋 `ValueError`。

## 4. CLI
- `python csv_stats.py <csv> [--group-by COL] [--columns a,b]`
- 正常輸出 JSON 到 stdout，回傳 0。
- 檔案不存在、`KeyError`、`ValueError` → stderr 印 `錯誤：...`，回傳 1（不丟 traceback）。

## 5. 範例資料（data/sales.csv）預期值
- `units` 全體：count 9、sum 64、median 7。
- `--group-by region` 的 `North.units`：值 10,8,4,6 → count 4、sum 28、mean 7、median 7。
- `South.units`：5,7（一列缺值）→ count 2、median 6。
- `East.price`：3.5,8.0,1.3 → median 3.5。

## 6. 不變條件
- 既有函式簽名向下相容（`compute_stats(rows)` 不給 columns 仍可用）。
- 只用標準庫。
