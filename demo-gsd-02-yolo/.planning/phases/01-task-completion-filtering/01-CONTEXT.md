# Phase 1: Task Completion & Filtering - Context

**Gathered:** 2026-06-22
**Status:** Ready for planning

<domain>
## Phase Boundary

在既有 `app.py`（待辦清單 CLI）上新增 `complete_task(tasks, name)` 與 `list_pending(tasks)` 兩個函式，並補對應 pytest 測試。為支援「完成」狀態，將任務的記憶體表示從 `list[str]` 升級為 `list[dict]`，既有 `add_task` / `list_tasks` / `delete_task` 與其 6 個測試一併同步調整且維持全綠。不串接 REPL（v2）。

</domain>

<decisions>
## Implementation Decisions

### 資料模型

- 完成狀態以 **dict 模型**儲存：每個任務為 `{"name": str, "done": bool}`，新增時 `done=False`
- 既有 `add_task` / `list_tasks` / `delete_task` 同步改為 dict 版；既有 6 個測試一併更新並保持全綠（= demo-gsd-01 做法）
- `list_pending(tasks)` 回傳「未完成任務的 name 字串清單」（便利視圖）
- `complete_task` 找不到任務時回傳 `False`（與 `delete_task` 一致，不拋錯）

### 行為細節

- 重複 `complete_task` 同一已完成任務 → idempotent，回傳 `True`
- 已完成任務仍可被 `delete_task` 刪除（delete 照 name 比對、不分完成狀態）
- `complete_task` 回傳 `True`/`False`（found / not-found）
- 既有 `list_tasks` 測試斷言更新為比對 name（例：`[t["name"] for t in list_tasks(tasks)] == [...]`）

</decisions>

<code_context>

## Existing Code Insights

### Reusable Assets

- `app.py`：既有 `add_task(tasks, name)`、`list_tasks(tasks)`、`delete_task(tasks, name)`、`main()` REPL
- `test_app.py`：既有 6 個 class-based pytest 測試（TestAddTask / TestListTasks / TestDeleteTask）
- `.planning/codebase/`：7 份地圖（CONVENTIONS / TESTING / STRUCTURE 可參考 dict 重構與測試慣例）

### Established Patterns

- 繁體中文 docstring、type hints、4-space 縮排、純標準庫
- pytest class-based 測試；執行：`PYTHONUTF8=1 pytest test_app.py -v`
- `add_task` 對空白 name 拋 `ValueError`（去前後空白後判斷）

### Integration Points

- 改動集中於 `app.py` 函式層 + `test_app.py`
- `main()` REPL 新增 complete/pending 指令屬 v2（本次不做）

</code_context>

<specifics>
## Specific Ideas

對照 demo-gsd-01 已驗證的 dict 模型做法（recent commit「重構 test_app.py 為 dict 模型並新增 TestCompleteTask」）。保持 in-memory、無持久化。

</specifics>

<deferred>
## Deferred Ideas

- REPL-01：`main()` REPL 新增 `complete` / `pending` 指令串接新函式（v2，超出本 phase 範圍）

</deferred>
