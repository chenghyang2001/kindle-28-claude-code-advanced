# PROJECT: 待辦清單 CLI（任務狀態 + 持久化擴充）

## What This Is

一個既有的極簡待辦清單 CLI（brownfield）。目前用 in-memory `list` 儲存純字串 task，
提供 add / list / delete 三個核心函式。本專案分兩個有先後關係的階段擴充它：
先讓任務有「完成狀態」，再讓任務能「存檔持久化」。

## Core Value

讓使用者不只記下待辦，還能**標記完成**並在**重開程式後保留**任務與完成狀態。
（這一個能力鏈是整個專案要驗證的重點。）

## Context

- 起點程式：`app.py`（3 函式：`add_task` / `list_tasks` / `delete_task` + `main` CLI loop）
- 既有測試：`test_app.py`（6 個測試，全綠）
- 技術：Python 3 標準庫；測試用 pytest；無外部框架/DB
- 程式碼地圖：`.planning/codebase/`（STACK / ARCHITECTURE / STRUCTURE）

## Requirements

### Validated（既有，從程式碼地圖推得）

- ✓ 新增任務（空字串拋 ValueError、存入前 strip）— existing
- ✓ 列出任務（回傳淺層 copy 保護封裝）— existing
- ✓ 刪除任務（成功 True / 找不到 False，不拋例外）— existing
- ✓ 互動式 CLI loop（add/list/delete/quit，EOF 優雅退出）— existing

### Active（本次新增，分兩階段）

- [ ] task 由 `str` 改為 `dict{name, done}`
- [ ] `complete_task(tasks, name)`：標記完成
- [ ] `list_pending(tasks)`：只列未完成
- [ ] `save_tasks(tasks, path)`：含 done 狀態存成 JSON
- [ ] `load_tasks(path)`：從 JSON 讀回任務
- [ ] 每階段補 pytest 測試，且不破壞既有 6 個測試

### Out of Scope

- 多使用者 / 帳號 — 單機單人工具，不需要
- 資料庫（SQLite/Postgres）— JSON 檔已足夠，避免過度工程
- Web / GUI 介面 — 維持 CLI
- 任務截止日 / 優先級 / 標籤 — 本里程碑不擴充

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| task `str` → `dict{name, done}` | 沒有 done 欄位就無法標記完成；也是持久化能存狀態的前提 | — Pending |
| 持久化用 JSON（非 DB） | 標準庫即可、純文字可讀、符合小工具定位 | — Pending |
| 切成 Phase 1（狀態）→ Phase 2（持久化）兩段 | Phase 2 的 `save_tasks` 要存 `done`，必須先有 Phase 1 的 dict 結構（相依） | — Pending |

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
