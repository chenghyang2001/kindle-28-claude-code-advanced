# Phase 1: 資料結構遷移與測試安全網重建 - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-07-23
**Phase:** 1-資料結構遷移與測試安全網重建
**Areas discussed:** Task 資料結構選型, list_tasks 複製深度

---

## Task 資料結構選型

### Q1: 任務要用什麼資料結構攜帶完成狀態？

| Option | Description | Selected |
| -------- | ------------- | ---------- |
| dataclass Task（推薦） | Task(name, done=False)；自動 **eq** 讓測試遷移近乎機械式替換，可變性讓 complete 直接 .done=True；四份研究一致推薦 | ✓ |
| dict | {"name":..., "done":...}；零 import，但斷言冗長、沒有型別保障、key 打錯字不會報錯 | |
| NamedTuple | 不可變，complete 要用 index+_replace 寫回，對教學專案心智負擔偏高（研究不推薦） | |
| You decide | 交給 Claude 依研究建議裁量（會選 dataclass） | |

**User's choice:** dataclass Task（推薦）

### Q2: 換成 Task 後，函式簽名的型別提示要升級嗎？（現況是裸 tasks: list）

| Option | Description | Selected |
| -------- | ------------- | ---------- |
| 升級 list[Task]（推薦） | 更精確、IDE/reviewer 友善；Python 3.14 內建泛型免 import，與既有「用內建型、不 import typing」風格一致 | ✓ |
| 維持裸 list | 最小 diff，完全貼既有風格；但新人看簽名看不出元素型別 | |
| You decide | 交給 Claude 裁量 | |

**User's choice:** 升級 list[Task]（推薦）

---

## list_tasks 複製深度

### Q1: list_tasks 的複製語意要做到哪個程度？

| Option | Description | Selected |
| -------- | ------------- | ---------- |
| 元素級複製（推薦） | 回傳每個 Task 的獨立副本（dataclasses.replace）；呼叫端拿到完全獨立快照，符合 SC2 字面，教學上最不易踩到隱形別名 bug | ✓ |
| 維持淺複製 | 保留 list(tasks)；最小改動，但 Task 實例共享參照，需同步把 ROADMAP 成功標準 2 改寬（只保證增刪不污染） | |
| You decide | 交給 Claude 裁量（會選元素級複製） | |

**User's choice:** 元素級複製（推薦）

---

## Claude's Discretion

- 測試斷言遷移風格（Task(...) 建構式直接比對 vs 輔助函式取名稱清單）— 使用者未選入討論
- 名稱查找共用設計（是否抽 _find helper 供 Phase 2 重用）— 使用者未選入討論
- 空名稱驗證位置（add_task vs Task.**post_init**）— 預設維持 add_task

## Deferred Ideas

None — discussion stayed within phase scope.
