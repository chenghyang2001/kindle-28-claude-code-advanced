---
phase: 01-task-completion-filtering
plan: 01
subsystem: core-functions
tags: [dict-refactor, complete_task, list_pending, pytest]
dependency_graph:
  requires: []
  provides: [complete_task, list_pending, dict-model]
  affects: [app.py, test_app.py]
tech_stack:
  added: []
  patterns: [list[dict]-task-model, idempotent-complete, name-only-pending]
key_files:
  modified:
    - app.py
    - test_app.py
decisions:
  - "dict 模型（{name: str, done: bool}）取代 list[str]，既有 3 個函式同步更新"
  - "complete_task 採冪等設計：已完成任務再次呼叫仍回傳 True"
  - "list_pending 回傳 name 字串清單（非 dict），方便呼叫端直接使用"
  - "REPL 不串接 complete/pending 指令（v2 deferred per CONTEXT.md）"
metrics:
  duration: "< 5 minutes"
  completed: "2026-06-22"
  tasks_completed: 2
  files_changed: 2
---

# Phase 1 Plan 1: Refactor app.py to Dict Model + add complete_task/list_pending Summary

## One-liner

將 app.py 的任務模型從 `list[str]` 重構為 `list[dict]`，新增 `complete_task`（冪等標記完成）與 `list_pending`（回傳未完成名稱清單），並將 test_app.py 更新為 dict 斷言 + 補齊 5 個新測試，共 11 個測試全綠。

## What Was Built

### Task 1: Refactor app.py to dict model and add complete_task / list_pending

- `add_task`：`tasks.append` 改為 `{"name": cleaned, "done": False}`
- `list_tasks`：實作不變，docstring 更新
- `delete_task`：`try/except remove` 替換為 for-loop 比對 `task["name"]`，支援任何 done 狀態的刪除
- `complete_task`（新）：找到 name → `done=True`，回傳 True；冪等（已完成也回 True）；找不到回 False
- `list_pending`（新）：list comprehension，只回傳 `done=False` 任務的 name 字串
- `main()` list 分支：`{task}` 改為 `{task['name']}`

### Task 2: Update test_app.py

- import 補上 `complete_task`、`list_pending`（字母順序）
- 既有 6 個測試全部更新為 dict 斷言
- `TestCompleteTask`（3 tests）：happy path、not found、idempotent
- `TestListPending`（2 tests）：all pending、some done

## Test Results

```
11 passed in 0.06s
TestAddTask::test_add_happy_path           PASSED
TestAddTask::test_add_empty_name_raises    PASSED
TestListTasks::test_list_happy_path        PASSED
TestListTasks::test_list_returns_copy      PASSED
TestDeleteTask::test_delete_happy_path     PASSED
TestDeleteTask::test_delete_non_existent_returns_false  PASSED
TestCompleteTask::test_complete_happy_path PASSED
TestCompleteTask::test_complete_not_found_returns_false PASSED
TestCompleteTask::test_complete_idempotent PASSED
TestListPending::test_list_pending_all_pending  PASSED
TestListPending::test_list_pending_some_done    PASSED
```

## Commits

| Task | Commit | Message |
|------|--------|---------|
| 1 | b8e2078 | 重構 app.py 為 dict 模型並新增 complete_task / list_pending |
| 2 | d4e2150 | 更新 test_app.py 為 dict 模型並新增 TestCompleteTask + TestListPending |

## Deviations from Plan

None — plan executed exactly as written.

## Requirements Coverage

| Req ID | Description | Status |
|--------|-------------|--------|
| TASK-01 | complete_task 函式 | DONE |
| TASK-02 | list_pending 函式 | DONE |
| TEST-01 | TestCompleteTask 3 tests | DONE |
| TEST-02 | TestListPending 2 tests | DONE |
| TEST-03 | 既有 6 個測試更新並維持全綠 | DONE |

## Known Stubs

None.

## Threat Flags

None — pure in-memory Python CLI, no network/auth/file I/O surface introduced.

## Self-Check: PASSED

- app.py exists: FOUND
- test_app.py exists: FOUND
- Commit b8e2078 exists: FOUND
- Commit d4e2150 exists: FOUND
- 11 tests passed: VERIFIED
