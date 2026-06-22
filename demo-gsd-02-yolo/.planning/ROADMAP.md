# Roadmap: 極簡待辦清單 CLI（demo-gsd-02-yolo）

## Overview

在既有的 3 函式 brownfield CLI 上，新增「標記完成」與「列出未完成」兩個功能，
同步補齊 pytest 測試，並確保原有 6 個測試維持全綠。
所有工作構成單一連貫交付，以 GSD YOLO 模式一次執行完畢。

## Phases

- [ ] **Phase 1: Task Completion & Filtering** - 新增 complete_task / list_pending 函式 + 測試，確保全部測試通過

## Phase Details

### Phase 1: Task Completion & Filtering

**Goal**: app.py 支援任務完成狀態追蹤，新函式有完整測試覆蓋，且既有 6 個測試維持全綠
**Mode:** mvp
**Depends on**: Nothing (brownfield base already exists)
**Requirements**: TASK-01, TASK-02, TEST-01, TEST-02, TEST-03
**Success Criteria** (what must be TRUE):

  1. `complete_task(tasks, name)` 能將指定任務標記為完成，呼叫後任務狀態可被後續查詢反映
  2. `list_pending(tasks)` 只回傳尚未完成的任務，已完成任務不出現在回傳清單中
  3. `complete_task` 有 pytest 測試，涵蓋正常標記（found）與任務不存在（not found）兩個案例
  4. `list_pending` 有 pytest 測試，涵蓋「全部未完成」與「部分已完成」兩個場景
  5. 既有 6 個測試（TestAddTask、TestListTasks、TestDeleteTask）在 `PYTHONUTF8=1 pytest` 下全部通過（回歸防線）
**Plans**: 1 plan

Plans:

- [ ] 01-01-PLAN.md — refactor app.py to dict model + add complete_task/list_pending + update all tests (11 total)

## Progress

| Phase | Plans Complete | Status | Completed |
|-------|----------------|--------|-----------|
| 1. Task Completion & Filtering | 0/1 | Not started | - |
