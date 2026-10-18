# 實作 agent 交付物摘要
- 改動：`src/todo.py`（+37 行：`_parse_due` 共用解析、`overdue(today)`、`sorted_items()`）
- 新增：`tests/test_features.py`（12 個測試：happy 3、edge 7、error 2）
- pytest：`15 passed in 0.10s`（主 agent 另行重跑，結果相同）
- 讀寫邊界驗證：`git diff --name-only` 只有 `src/todo.py`；新檔只有 `tests/test_features.py` → 無越界

## 衝突與主 agent 裁決
- 衝突：研究 agent 預期 `sorted_items` 順序是 [4, 1, 2, 3]，實作 agent 照合約算出 [1, 4, 2, 3]。
- 事實：id1、id4 都是 priority 1 且未完成，id1 的 due 是 2026-10-15，早於 id4 的 2026-10-18。
- 裁決：**以合約為準 → [1, 4, 2, 3]**。研究 agent 的預期值算錯了，這次錯誤在進入程式碼之前就被實作 agent 擋下。
- 教訓：交付物之間的事實要以合約為唯一依據；下游 agent 被要求「照合約做」時，可以揭露上游的錯誤。
