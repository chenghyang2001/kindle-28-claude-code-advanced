# Requirements: 極簡待辦清單 CLI（demo-gsd-02-yolo）

**Defined:** 2026-06-22
**Core Value:** 使用者能可靠管理待辦任務（含新增完成／篩選未完成），且不破壞既有 6 個通過測試。

## v1 Requirements

初始範圍。每項對應 roadmap phase。

### Task Completion

- [ ] **TASK-01**: 使用者能透過 `complete_task(tasks, name)` 把指定任務標記為完成
- [ ] **TASK-02**: 使用者能透過 `list_pending(tasks)` 只取得尚未完成的任務

### Testing

- [ ] **TEST-01**: `complete_task` 有對應 pytest 測試（正常 + 找不到任務的錯誤/邊界）
- [ ] **TEST-02**: `list_pending` 有對應 pytest 測試（含全部未完成 / 部分完成）
- [ ] **TEST-03**: 既有 6 個測試維持全綠（回歸防線）

## v2 Requirements

延後，追蹤但不在本次 roadmap。

### REPL

- **REPL-01**: `main()` 互動式 REPL 新增 `complete` / `pending` 指令串接新函式

## Out of Scope

明確排除，避免範圍蔓延。

| Feature | Reason |
|---------|--------|
| 持久化（檔案／DB） | 此 demo 刻意維持 in-memory，聚焦學習 GSD 流程 |
| 引入新第三方依賴 | 保持標準庫 + pytest 極簡 |
| 修改既有 add/list/delete 行為 | 既有 6 測試是回歸防線，不動既有行為 |

## Traceability

各 phase 涵蓋哪些需求，roadmap 建立時填入。

| Requirement | Phase | Status |
|-------------|-------|--------|
| TASK-01 | TBD | Pending |
| TASK-02 | TBD | Pending |
| TEST-01 | TBD | Pending |
| TEST-02 | TBD | Pending |
| TEST-03 | TBD | Pending |

**Coverage:**

- v1 requirements: 5 total
- Mapped to phases: 0（待 roadmap）
- Unmapped: 5 ⚠️（roadmap 後應為 0）

---
*Requirements defined: 2026-06-22*
*Last updated: 2026-06-22 after initial definition*
