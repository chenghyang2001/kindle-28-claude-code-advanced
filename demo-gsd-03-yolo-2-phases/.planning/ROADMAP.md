# ROADMAP — 待辦清單 CLI 擴充（v1）

> Brownfield 擴充既有 todo-CLI（`app.py`：`add_task` / `list_tasks` / `delete_task` on `list[str]`）。
> 兩個有先後關係的能力群：**任務完成狀態（先）→ 存檔持久化（後）**。
> 持久化必須在完成狀態之後，因為 `save_tasks` 要持久化 `done` 欄位，而 `done` 只有在
> Phase 1 把 task 從 `str` 改成 `dict{name, done}` 之後才存在 → 嚴格循序兩階段。

**Granularity:** coarse
**Mode:** mvp (Vertical MVP — 每個階段交付一條端到端的使用者能力)
**Coverage:** 7/7 requirements mapped

## Phases

- [x] **Phase 1: 任務完成狀態 (Status)** — task 改為 `dict{name, done}`，加 `complete_task` / `list_pending`，既有行為不變 (completed 2026-06-22)
- [x] **Phase 2: 存檔持久化 (Persistence)** — `save_tasks` / `load_tasks` 以 JSON 存讀任務（含 done），round-trip 一致 (completed 2026-06-22)

## Phase Details

### Phase 1: 任務完成狀態 (Status)

**Goal**: 使用者能標記任務完成，並只檢視尚未完成的任務
**Mode**: mvp
**Depends on**: Nothing（直接擴充既有 brownfield `app.py`）
**Requirements**: STAT-01, STAT-02, STAT-03, STAT-04
**Success Criteria** (what must be TRUE):

  1. task 改以 `dict{name, done}` 儲存後，既有 `add_task` / `list_tasks` / `delete_task` 的對外行為不變（空字串仍拋 `ValueError`、`list_tasks` 仍回防禦性 copy、刪除仍回 `True`/`False`）
  2. 使用者可呼叫 `complete_task(tasks, name)` 把指定任務的 `done` 標記為 `True`
  3. 使用者可呼叫 `list_pending(tasks)` 只取得 `done=False` 的任務
  4. 既有 6 個 pytest 測試維持全綠
  5. 新增涵蓋 `complete_task` / `list_pending` 的 pytest 測試（含 happy / edge / error 案例）
**Plans**: 1 plan

Plans:

- [x] 01-01-PLAN.md — task 遷移為 dict{name, done}、新增 complete_task / list_pending、既有 6 測試對齊 + 新增 Status 測試

### Phase 2: 存檔持久化 (Persistence)

**Goal**: 使用者重開程式後仍保留任務與其完成狀態
**Mode**: mvp
**Depends on**: Phase 1 — `save_tasks` 要持久化每個任務的 `done` 欄位，而 `done` 只有在 Phase 1 把 task 從 `str` 升級為 `dict{name, done}` 之後才存在；故本階段直接建立在 Phase 1 的 dict 資料結構之上
**Requirements**: PERS-01, PERS-02, PERS-03
**Success Criteria** (what must be TRUE):

  1. 使用者可呼叫 `save_tasks(tasks, path)` 把任務（含 `done` 狀態）寫成 JSON 檔
  2. 使用者可呼叫 `load_tasks(path)` 從 JSON 檔讀回任務，正確還原 `name` 與 `done`
  3. 存檔 → 讀回的 round-trip 後，任務清單（含 `done`）與原始資料完全一致
  4. 既有測試（原始 6 個 + Phase 1 新增的 Status 測試）維持全綠
  5. 新增涵蓋 `save_tasks` / `load_tasks` 的 pytest 測試（含 happy / edge / error，如空清單、檔案不存在）
**Plans**: 1 plan

Plans:

- [x] 02-01-PLAN.md — 新增 save_tasks / load_tasks（stdlib json、UTF-8、缺檔回 []、壞 JSON 外拋）+ Persistence round-trip / 空清單 / 缺檔測試

## Progress

| Phase | Plans Complete | Status | Completed |
|-------|----------------|--------|-----------|
| 1. 任務完成狀態 (Status) | 1/1 | Complete   | 2026-06-22 |
| 2. 存檔持久化 (Persistence) | 1/1 | Complete   | 2026-06-22 |
