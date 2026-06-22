# Phase 1: Task Completion - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-06-22
**Phase:** 1-Task Completion
**Areas discussed:** 完成狀態的資料表示, 找不到任務的回傳, 列表如何呈現完成, 重複完成同一任務

---

## 完成狀態的資料表示

| Option | Description | Selected |
|--------|-------------|----------|
| list[dict] | 每筆 = {name, done}。最乾淨、最符合 complete_task(tasks,name)；代價：add/list/delete + 12 測試要同步改 | ✓ |
| 平行 set | tasks 維持 list[str]，另用 completed set 記完成。既有函式零改動，但呼叫端多管一個資料 | |
| [x] 前綴 | complete_task 把字串改成 '[x] name'。侵入最小，但完成後用原名 delete 會找不到（hacky） | |

**User's choice:** list[dict]
**Notes:** 使用者在被明確告知「這是一次小型重構、既有 12 測試要改」後仍選擇 dict，取其模型乾淨。

---

## 找不到任務的回傳

| Option | Description | Selected |
|--------|-------------|----------|
| 回 False | 仿照 delete_task 的慣例，保持 API 一致 | ✓ |
| 拋 ValueError | 仿 add_task 空名拋錯的慣例，強迫呼叫端處理 | |

**User's choice:** 回 False
**Notes:** 與既有 delete_task 一致性優先。

---

## 列表如何呈現完成

| Option | Description | Selected |
|--------|-------------|----------|
| 顯示層加 [x] | list_tasks 回傳原資料，_print_task_list 等顯示層負責加 [x]/[ ] 標記 | ✓ |
| list_tasks 回傳帶狀態 | list_tasks 直接回傳帶完成狀態的資料 | |

**User's choice:** 顯示層加 [x]（list_tasks 仍回傳資料 copy；標記由_print_task_list 處理）

---

## 重複完成同一任務

| Option | Description | Selected |
|--------|-------------|----------|
| no-op 回 True | 已完成再完成視為成功、不報錯（冪等） | ✓ |
| no-op 但回 False | 未改變狀態 → 回 False | |
| 拋錯 | 重複完成視為錯誤用法 | |

**User's choice:** no-op 回 True

---

## Claude's Discretion

- `add_task` 新增 dict 的 `done` 預設為 `False`
- 既有測試的具體改寫方式（斷言比對 dict / name 欄位）交由 plan/execute 決定，只要最終全綠

## Deferred Ideas

- COMP-04 取消完成 / 重開任務（v2）
- 持久化、優先順序、`complete` CLI 指令（out of scope）
