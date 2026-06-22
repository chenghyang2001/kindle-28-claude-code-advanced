# 極簡待辦清單 CLI（demo-gsd-02-yolo）

## What This Is

一個用 Python 標準庫寫的極簡待辦清單 CLI，任務以純字串存放於記憶體 list。本次工作是在既有基礎上，以 GSD YOLO（autonomous）模式自動新增「標記完成」與「列出未完成」兩個功能，作為對照 demo-gsd-01 互動逐步模式的學習練習。

## Core Value

使用者能可靠地管理待辦任務（新增／列出／刪除，並新增完成／篩選未完成），且**不破壞既有的 6 個通過測試**。

## Requirements

### Validated

<!-- 既有程式碼已實作並依賴，來自 .planning/codebase/ 地圖。 -->

- ✓ `add_task(tasks, name)` — 新增任務，空白名稱拋 `ValueError` — existing
- ✓ `list_tasks(tasks)` — 回傳任務清單淺層複本 — existing
- ✓ `delete_task(tasks, name)` — 刪除任務，回傳 True/False — existing
- ✓ `main()` 互動式 REPL（add / list / delete / quit） — existing
- ✓ `test_app.py` 6 個 pytest 測試全綠 — existing

### Active

<!-- 本次要建的新範圍。 -->

- [ ] `complete_task(tasks, name)` — 標記指定任務為完成
- [ ] `list_pending(tasks)` — 只列出尚未完成的任務
- [ ] 為上述兩個新函式各補對應 pytest 測試

### Out of Scope

- 持久化（檔案／DB） — 此 demo 刻意維持 in-memory，聚焦學習 GSD 流程
- 修改或破壞既有 6 個測試 — 必須保持全綠（回歸防線）
- CLI REPL 加新指令（complete / pending） — v1 先做函式層，REPL 串接非本次必要

## Context

- **Brownfield 起點**：`app.py` 目前只有 3 個核心函式，任務以 `list[str]` 純字串存放，無「完成」概念。
- **學習脈絡**：本資料夾是 GSD YOLO 模式練習（對照組 demo-gsd-01 走互動逐步）。完整步驟見 `YOLO-PRACTICE.md`。
- **codebase 地圖**：`.planning/codebase/` 有 7 份（由 `/gsd-map-codebase` 完整版產出），可供規劃參考。
- **資料模型未決**：要加「已完成」狀態，但 task 目前是純字串——需在實作時選定表示法（見 Key Decisions）。

## Constraints

- **Tech stack**: Python 3.x 標準庫 + pytest + ruff — 不引入額外依賴，保持極簡
- **Compatibility**: 既有 6 個測試不可弄壞 — 這是回歸防線
- **Scope**: demo／學習用，刻意維持最小可行 — 避免過度工程

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| 「已完成」狀態如何表示（task 目前是 `list[str]` 純字串） | 加完成狀態需選資料模型：改 `list[dict]`、另維護 completed set、或命名約定 | — Pending（留給規劃／執行時決定） |
| 採 GSD YOLO（autonomous）模式 | 需求清楚、信任自動跑完多 phase，作為對照學習 | — Pending |

## Evolution

This document evolves at phase transitions and milestone boundaries.

**After each phase transition** (via `/gsd-transition`):

1. Requirements invalidated? → Move to Out of Scope with reason
2. Requirements validated? → Move to Validated with phase reference
3. New requirements emerged? → Add to Active
4. Decisions to log? → Add to Key Decisions
5. "What This Is" still accurate? → Update if drifted

**After each milestone** (via `/gsd:complete-milestone`):

1. Full review of all sections
2. Core Value check — still the right priority?
3. Audit Out of Scope — reasons still valid?
4. Update Context with current state

---
*Last updated: 2026-06-22 after initialization*
