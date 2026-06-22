---
phase: 01-status
plan: 01
subsystem: core
tags: [python, pytest, todo-cli, dict-migration, stdlib]

# Dependency graph
requires: []
provides:
  - "task 資料結構由 str 遷移為 dict{name, done}"
  - "complete_task(tasks, name)：標記第一個相符任務 done=True（strip / idempotent / 找不到回 False）"
  - "list_pending(tasks)：回傳 done=False 任務的淺 copy（保序、空回 []）"
  - "add/list/delete 對外行為在 dict 模型下維持不變（ValueError / 防禦性 copy / True|False）"
  - "main() CLI list 顯示相容 dict（只印 name）"
affects: [02-persistence]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "純函式操作傳入 tasks，name 比對前一律 strip"
    - "錯誤處理：空輸入拋 ValueError、找不到回布林 False（不拋例外）"

key-files:
  created: []
  modified:
    - app.py
    - test_app.py

key-decisions:
  - "list_pending / list_tasks 採淺 copy（list comprehension 自然保序），元素仍為原 dict reference，符合既定封裝設計"
  - "complete_task 與 delete_task 共用 strip + 線性比對 + 只處理第一個相符者的慣例"

patterns-established:
  - "dict{name, done} 為任務的標準形態，Phase 2 持久化將直接序列化此結構"

requirements-completed: [STAT-01, STAT-02, STAT-03, STAT-04]

# Metrics
duration: 8min
completed: 2026-06-22
---

# Phase 1 Plan 01: 任務完成狀態 (Status) Summary

**把 todo-CLI 的 task 由純字串遷移為 dict{name, done}，新增 complete_task 標記完成與 list_pending 只看未完成兩個查詢能力，既有 6 測試對齊 dict 後全綠並新增 9 個 Status 測試（共 15 passed）。**

## Performance

- **Duration:** ~8 min
- **Started:** 2026-06-22T06:45:16Z
- **Completed:** 2026-06-22T06:53Z
- **Tasks:** 3 (plan) → 2 file-atomic commits
- **Files modified:** 2

## Accomplishments

- `add_task` 改存 `dict{"name": <stripped>, "done": False}`，保留 strip 與空白 ValueError。
- `delete_task` 改以 `task["name"]` 比對（strip 後），True/False 行為不變。
- 新增 `complete_task`（strip 比對、idempotent、找不到回 False、只標記第一個相符者）。
- 新增 `list_pending`（只回 done=False、維持插入順序、空/全完成回 []、淺 copy）。
- `main()` list 顯示改讀 `task['name']`，dict 任務只印名稱。
- 既有 6 測試對齊 dict 模型（不弱化原意）+ 新增 `TestCompleteTask` / `TestListPending`。

## Task Commits

Plan 的 3 個任務依檔案職責合併為 2 個原子 commit（實作 / 測試分離）：

1. **Task 1 + 2: dict 遷移 + complete_task/list_pending（app.py）** - `efca883` (feat)
2. **Task 1 + 3: 既有測試對齊 + Status 新測試（test_app.py）** - `e89de5c` (test)

**Plan metadata:** （隨本 SUMMARY 一併提交）

## Files Created/Modified

- `app.py` - dict 模型遷移、複合查詢函式（complete_task / list_pending）、main 顯示相容
- `test_app.py` - 6 既有測試對齊 dict、新增 9 個 complete/pending 測試（共 15）

## Decisions Made

- 既有測試 fixtures 全部改為 `dict{name, done}`，斷言改為驗證實際 `done` 值與插入順序（非只驗長度），維持原意不弱化。
- `complete_task` / `list_pending` 置於 `delete_task` 之後、`main` 之前，與既有純函式並列。

## Deviations from Plan

唯一偏差為 **commit 粒度**（非行為）：

- **項目：** Plan 列 3 個任務，但 app.py（Task 1 實作 + Task 2）與 test_app.py（Task 1 測試對齊 + Task 3）各為單一檔案、內容相互交織，無法在不使用互動式分段 staging（本環境不支援 `git add -p` 互動）下乾淨拆成 3 個檔內 commit。
- **處理：** 合併為 2 個原子 commit，依「實作（feat）/ 測試（test）」職責分離；實作先於測試提交，確保每個 commit 後狀態自洽（test 依賴 impl 的 import）。
- **影響：** 純提交分組差異，所有計畫行為與驗證皆完整交付，無範圍增減。

## Issues Encountered

- Git 對 app.py / test_app.py 顯示 LF→CRLF 警告（Windows 換行），僅警告不影響提交與測試。

## Verification

- `PYTHONUTF8=1 python -m pytest test_app.py -v` → **15 passed**（既有 6 對齊 + 新增 9）
- smoke：`complete_task(t,' a '), t[0]['done'], complete_task(t,'x'), list_pending names` → `True True False []`
- `add_task` 產生 `[{'name':'x','done':False}]`；`main` list 顯示 `1. 買牛奶`（只印 name）
- requirements.txt 維持只有 `pytest`（無新增依賴）

## User Setup Required

None - 純記憶體、標準庫，無外部服務配置。

## Next Phase Readiness

- dict{name, done} 結構就緒，Phase 2 持久化（`save_tasks` / `load_tasks` JSON）可直接序列化含 done 欄位。
- 無阻塞。

## Self-Check: PASSED

- FOUND: app.py
- FOUND: test_app.py
- FOUND: .planning/phases/01-status/01-01-SUMMARY.md
- FOUND commit: efca883 (feat — app.py)
- FOUND commit: e89de5c (test — test_app.py)

---
*Phase: 01-status*
*Completed: 2026-06-22*
