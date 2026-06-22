# Phase 1: Task Completion - Context

**Gathered:** 2026-06-22
**Status:** Ready for planning

<domain>
## Phase Boundary

讓使用者把既有任務標記為完成，並在列出任務時區分完成 / 未完成狀態。涵蓋 COMP-01 / COMP-02 / COMP-03。不含取消完成、優先順序、持久化（屬其他 phase / out of scope）。

</domain>

<decisions>
## Implementation Decisions

### 完成狀態的資料表示（核心）

- **D-01:** `tasks` 從 `list[str]` 改為 `list[dict]`，每筆為 `{"name": str, "done": bool}`。這是最乾淨、最符合 `complete_task(tasks, name)` 簽名的模型。
- **D-02:** 此決定為**小型重構**：既有 `add_task` / `delete_task` / `list_tasks` / `_print_task_list` 與既有 12 個測試都必須同步更新為 dict 模型，最終整套測試保持全綠。使用者已明確知悉並接受此範圍。

### complete_task 行為

- **D-03:** `complete_task(tasks, name)` 找不到該 name → 回傳 `False`（仿照 `delete_task` 的 bool 慣例，保持 API 一致；不拋錯）。
- **D-04:** 重複完成已完成的任務 → no-op，回傳 `True`（冪等；不報錯）。成功標記（含本來就已完成）一律回 `True`。

### 列表呈現

- **D-05:** `list_tasks(tasks)` 維持回傳資料本身（現在是 dict 的 copy），不負責格式化。
- **D-06:** 完成狀態的視覺標記由顯示層 `_print_task_list` 負責：已完成顯示 `[x] name`，未完成顯示 `[ ] name`。

### Claude's Discretion

- `add_task` 新增的 dict 其 `done` 預設為 `False`（標準作法，未特別討論）。
- 既有測試的具體改寫方式（斷言改成比對 dict 或 name 欄位）交由 plan/execute 決定，只要最終全綠。

</decisions>

<canonical_refs>

## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### 需求與路線圖

- `.planning/REQUIREMENTS.md` — COMP-01/02/03 定義與驗收方向
- `.planning/ROADMAP.md` §Phase 1 — phase 目標與 4 條成功標準

### 既有程式碼（brownfield 基準）

- `app.py` — 既有 `add_task` / `list_tasks` / `delete_task` / `_print_task_list` / `main` 實作，是本次重構的對象
- `test_app.py` — 既有 12 個測試，需同步更新為 dict 模型
- `.planning/codebase/ARCHITECTURE.md` — 既有函式式架構與資料流
- `.planning/codebase/CONVENTIONS.md` — 程式風格 / docstring / 錯誤處理慣例（新函式須遵循）
- `.planning/codebase/TESTING.md` — 既有測試結構與慣例

</canonical_refs>

<code_context>

## Existing Code Insights

### Reusable Assets

- `delete_task(tasks, name)`：找名稱 + 回 bool 的 pattern，`complete_task` 可沿用同樣的查找 + bool 回傳風格
- `_print_task_list(tasks)`：既有的顯示層輔助函式，是加上 `[x]`/`[ ]` 標記的唯一改點
- `add_task` 的空名稱 `ValueError` 防呆 pattern：新函式與重構需維持一致的防禦風格

### Established Patterns

- 函式式、就地修改 `tasks`（add/delete 直接改傳入的 list）
- `list_tasks` 回傳 copy 而非原 list（避免外部誤改內部狀態）— 改 dict 後仍應回傳 copy
- 繁體中文 docstring + 「為什麼」註解風格

### Integration Points

- `main()` 互動 loop 目前用 add/list/delete 三指令；本次只做函式層 + 顯示層，**不要求**新增 `complete` CLI 指令（CLI 介面屬 out of scope），但 `_print_task_list` 改動會反映在 `list` 指令輸出

</code_context>

<specifics>
## Specific Ideas

- 完成標記格式採 `[x]` / `[ ]` 前綴（討論時的具體共識，對應 COMP-03 成功標準範例）

</specifics>

<deferred>
## Deferred Ideas

- **COMP-04 取消完成 / 重開任務**：v2 需求，本 phase 不做（REQUIREMENTS.md v2 已記錄）
- 持久化、優先順序、`complete` CLI 指令：out of scope（PROJECT.md / REQUIREMENTS.md 已記錄）

</deferred>

---

*Phase: 1-Task Completion*
*Context gathered: 2026-06-22*
