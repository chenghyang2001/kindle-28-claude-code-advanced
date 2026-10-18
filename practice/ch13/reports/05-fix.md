# 實作 agent 第二輪：依 debate 裁決修正
- `src/todo.py`：新增 `_parse_priority` + `DEFAULT_PRIORITY = 3`；`add()` 在寫入前驗證；`sorted_items()` 改用 `_parse_priority`；`_parse_due` 的錯誤訊息不再印原值
- `tests/test_features.py`：+8 個測試（None 存成 3、5 種壞值參數化、載入壞 priority、due 訊息不洩漏原值）
- pytest：`23 passed`（主 agent 重跑結果相同）
- 邊界驗證：`git diff --name-only` = `src/todo.py`、`tests/test_features.py` → 無越界
- 主 agent 冒煙實驗：overdue=[1]、sorted=[1, 4, 2, 3]、None→3、'1'/True/-1 都被拒絕，訊息只印型別
