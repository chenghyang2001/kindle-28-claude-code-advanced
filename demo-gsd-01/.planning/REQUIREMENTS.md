# Requirements: Todo CLI（demo-gsd-01）

**Defined:** 2026-06-22
**Core Value:** 使用者能對待辦清單做基本的任務管理操作，且每個操作都有對應的測試保障行為正確。

## v1 Requirements

本次工作要交付的需求。每條對應 roadmap phase。

### Task Completion

- [ ] **COMP-01**: 使用者可用名稱把既有任務標記為完成
- [ ] **COMP-02**: 標記不存在的任務時，回傳清楚的失敗訊號且不讓程式崩潰
- [ ] **COMP-03**: 列出任務時，已完成的任務可與未完成的區分

## v2 Requirements

延後到未來，追蹤但不在本次 roadmap。

### Task Completion

- **COMP-04**: 使用者可取消完成 / 重開一個已完成的任務

## Out of Scope

明確排除，避免 scope creep。

| Feature | Reason |
|---------|--------|
| 持久化儲存（檔案 / DB） | 練習聚焦記憶體內資料結構與流程 |
| 優先順序 / 截止日期 / 標籤 | 超出本練習範圍，屬未來里程碑 |
| CLI 參數介面 / argparse | 既有程式以函式為單位，維持一致 |

## Traceability

哪些 phase 涵蓋哪些需求。roadmap 建立時填入。

| Requirement | Phase | Status |
|-------------|-------|--------|
| COMP-01 | Phase 1 | Pending |
| COMP-02 | Phase 1 | Pending |
| COMP-03 | Phase 1 | Pending |

**Coverage:**

- v1 requirements: 3 total
- Mapped to phases: 3
- Unmapped: 0 ✓

---
*Requirements defined: 2026-06-22*
*Last updated: 2026-06-22 after roadmap creation (traceability filled)*
