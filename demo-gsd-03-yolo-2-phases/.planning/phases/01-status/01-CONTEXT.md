# Phase 1: 任務完成狀態 (Status) - Context

**Gathered:** 2026-06-22
**Status:** Ready for planning
**Mode:** Smart discuss (YOLO — recommended answers auto-accepted)

<domain>
## Phase Boundary

把既有 todo-CLI 的 task 從純字串升級為含完成狀態的結構，並提供「標記完成」與
「只看未完成」兩個查詢能力。範圍限定在 `app.py` 的函式層 + pytest；不改 CLI loop 指令、
不做持久化（屬 Phase 2）。

</domain>

<decisions>
## Implementation Decisions

### 資料結構與遷移

- task 以 `dict{"name": str, "done": bool}` 儲存（取代純字串）
- `add_task(tasks, name)` 新增時 `done` 預設 `False`；仍保留 strip、空字串/空白拋 `ValueError`
- `list_tasks(tasks)` 維持回傳防禦性 copy（`list(tasks)` 的淺 copy 已足夠，呼叫端不應原地改）
- `delete_task(tasks, name)` 改以 `task["name"]` 比對；仍回 `True`（刪到）/`False`（找不到）

### complete_task 行為

- `complete_task(tasks, name)`：把第一個 name 相符的 task 設 `done=True`
- 找不到 → 回 `False`（與 `delete_task` 一致，不拋例外）；標記成功 → 回 `True`
- 已完成的再標記 → 維持 `done=True` 並回 `True`（idempotent）
- 比對前對 name 做 strip，與 add/delete 的處理一致

### list_pending 行為

- `list_pending(tasks)`：回傳 `done=False` 的 task 的淺 copy list
- 維持原始插入順序
- 空清單或全部完成 → 回 `[]`

### Claude's Discretion

- 函式內部寫法、docstring 用語、測試案例命名由實作者決定（保持與既有 app.py 風格一致）

</decisions>

<code_context>

## Existing Code Insights

### Reusable Assets

- `app.py`：`add_task` / `list_tasks` / `delete_task` + `main` CLI loop（來源見 .planning/codebase/STRUCTURE.md）
- `test_app.py`：既有 6 個 pytest 測試（必須維持全綠）

### Established Patterns

- 純函式操作傳入的 `tasks` list；錯誤處理用 `ValueError`（空輸入）與布林回傳（找不到）
- `list_tasks` 回 copy 以保護封裝；name 一律先 strip
- 標準庫、無外部依賴；UTF-8

### Integration Points

- 既有 add/list/delete 需配合新的 dict 結構調整內部比對邏輯，但對外行為不變
- `main()` CLI loop 顯示任務時需相容 dict（顯示 name；done 狀態顯示為 Phase 2/後續 v2 範疇，本階段最小變更維持可列印）

</code_context>

<specifics>
## Specific Ideas

- 必須維持既有 6 個測試全綠（REQUIREMENTS STAT-04）
- task dict 欄位固定為 `name` 與 `done` 兩個（對齊 PROJECT.md Key Decisions）

</specifics>

<deferred>
## Deferred Ideas

- CLI 指令接上 complete/pending、啟動載入/退出儲存 → v2（REQUIREMENTS 已標 deferred）
- 持久化（save/load）→ Phase 2

</deferred>
