# Phase 1: 資料結構遷移與測試安全網重建 - Context

**Gathered:** 2026-07-23
**Status:** Ready for planning

<domain>
## Phase Boundary

把 `tasks` 從裸字串 `list[str]` 換成能攜帶完成狀態的 `Task` 資料結構，改寫 `add_task` / `delete_task` / `list_tasks` 內部邏輯，並讓既有 12 個測試在新結構下全數重新變綠（驗證原始行為語意：順序、去空白、副本語意、刪除只影響第一筆同名）。本階段**不實作** `complete_task`（Phase 2）、**不動** CLI 顯示層與 ✓ 標記（Phase 3）。對應需求：COMPAT-01、COMPAT-02。

</domain>

<decisions>
## Implementation Decisions

### Task 資料結構選型

- **D-01:** 採用 `dataclass Task`，欄位 `name: str`、`done: bool = False`。理由：可變性讓 Phase 2 的 complete 直接 `.done = True`；自動 `__eq__` 讓既有測試斷言近乎機械式替換（`"買牛奶"` → `Task("買牛奶")`）；四份研究一致推薦。
- **D-02:** **不使用** `slots=True`（Python 3.14 有已知 dataclass slots 回歸，見 research STACK.md）。
- **D-03:** 型別提示全面升級為 `list[Task]`（內建泛型、不 import typing），取代既有裸 `list` 註記。

### list_tasks 複製深度

- **D-04:** 元素級複製——`list_tasks` 回傳每個 Task 的獨立副本（如 `dataclasses.replace(t)` 或等價寫法），呼叫端拿到完全獨立快照；修改回傳值中元素的 `.done` 不得污染原始 `tasks`。此決策照 ROADMAP Phase 1 成功標準 2 字面實作。

### Claude's Discretion

- **測試斷言遷移風格**：12 個既有測試改用 `Task(...)` 建構式直接比對、或輔助函式取名稱清單——planner 自行裁量，前提是驗證的行為語意不變（ROADMAP SC1）。
- **名稱查找共用設計**：`delete_task` 重寫時是否抽出 `_find` 類 helper 供 Phase 2 `complete_task` 重用——planner 自行裁量；注意既有 `name in tasks` / `tasks.remove(name)` 在 Task 物件下會靜默失效，必須整段重寫（research 認定的最高風險點）。
- **空名稱驗證位置**：維持在 `add_task` 或移入 `Task.__post_init__`——planner 自行裁量，預設維持在 `add_task`（最小改動）。

</decisions>

<canonical_refs>

## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### 研究產出（本次功能的技術決策依據）

- `.planning/research/ARCHITECTURE.md` — 5 種資料結構方案比較矩陣、ripple effect 總表（對三函式與 12 測試的具體衝擊）、10 步建置順序
- `.planning/research/PITFALLS.md` — 8 個 pitfall 含 warning signs 與 phase mapping（測試斷言耦合、別名污染、cp950 等）
- `.planning/research/STACK.md` — dataclass 選型細節、slots 回歸警告、pytest capsys 模式

### Codebase map（既有慣例約束）

- `.planning/codebase/TESTING.md` — 測試命名/組織慣例（`Test<FunctionName>` 類、inline 測資、繁中測資字串、`is True/False` 斷言風格）
- `.planning/codebase/CONVENTIONS.md` — 命名/docstring/錯誤處理慣例（Google-style 繁中 docstring、`<verb>_task(tasks, name)` 簽名形狀、bool 回傳表「找不到」）

### 規劃文件

- `.planning/REQUIREMENTS.md` — COMPAT-01/COMPAT-02 驗收語意
- `.planning/ROADMAP.md` — Phase 1 成功標準 3 條（本 CONTEXT 的 D-04 對應 SC2）

</canonical_refs>

<code_context>

## Existing Code Insights

### Reusable Assets

- `app.py` 單檔「functional core, imperative shell」結構：核心函式以 `tasks` 為第一參數、`main()` 持有唯一狀態——Task 化後此結構完全保留
- `test_app.py` 12 個測試、3 個 Test 類別：零 fixture、inline 測資、每測試獨立——遷移時維持此形狀

### Established Patterns

- 型別提示用內建型別（不 import typing）→ D-03 的 `list[Task]` 與此一致
- 「找不到」用 bool 回傳、無效輸入才 raise ValueError → delete_task 重寫時維持
- 使用者可見字串一律繁體中文、錯誤走 stderr

### Integration Points

- `delete_task` 內部 `name in tasks` / `tasks.remove(name)` 是唯一「簽名不變但內部必須整段重寫」的函式（最高風險點）
- `_print_task_list` 在本階段只需相容 Task（印 `task.name`），✓ 標記留給 Phase 3

</code_context>

<specifics>
## Specific Ideas

No specific requirements — open to standard approaches（使用者選型皆採研究推薦方案）。

</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope.

</deferred>

---

*Phase: 1-資料結構遷移與測試安全網重建*
*Context gathered: 2026-07-23*
