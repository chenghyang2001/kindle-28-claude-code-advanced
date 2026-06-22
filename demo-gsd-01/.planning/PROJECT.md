# Todo CLI（demo-gsd-01）

## What This Is

一個用來練習 GSD 完整流程的待辦清單 CLI（純 Python，無外部框架）。目前提供新增、列出、刪除三個任務操作；本次工作要為它加上「標記任務為完成」的能力。對象是學習 GSD 流程的開發者，App 本身只是載體，流程才是重點。

## Core Value

使用者能對待辦清單做基本的任務管理操作，且每個操作都有對應的測試保障行為正確。

## Requirements

### Validated

<!-- 既有程式碼已實作並有測試保障，視為已驗證 -->

- ✓ 新增任務 `add_task(tasks, name)`（空 name 拋 ValueError）— existing
- ✓ 列出任務 `list_tasks(tasks)`（回傳 copy）— existing
- ✓ 刪除任務 `delete_task(tasks, name)`（回傳 True/False）— existing

### Active

<!-- 本次工作要建構的新需求 -->

- [ ] 標記任務為完成 `complete_task(name)`

### Out of Scope

<!-- 明確邊界，避免 scope creep -->

- 優先順序 / 截止日期 / 標籤等進階欄位 — 超出本練習範圍，屬未來 phase
- 持久化儲存（檔案 / DB）— 練習聚焦記憶體內資料結構與流程
- CLI 互動介面 / 參數解析 — 既有程式以函式為單位，維持一致

## Context

- 技術環境：Python（Windows Store 版），測試用 pytest，執行需 `PYTHONUTF8=1`
- 既有架構：函式式設計，task 以資料結構存於記憶體，每個函式皆有對應測試
- codebase 地圖已於 `/gsd:map-codebase` 產出，存於 `.planning/codebase/`（7 份報告）
- 既有測試 baseline：`PYTHONUTF8=1 pytest test_app.py -v` → 12 passed

## Constraints

- **Tech stack**：純 Python 標準庫，不引入外部套件 — 維持練習單純、可攜
- **Compatibility**：不可破壞既有 add/list/delete 的行為與測試 — 既有測試必須持續全綠
- **Testing**：新功能必須附測試（happy / edge / error）— 符合專案「測試與程式碼同時生成」原則

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| 用 GSD 完整流程新增 complete_task | 練習 GSD 各 phase 的指令與協作模式 | — Pending |
| complete_task 的標記方式留待 discuss-phase 決定 | 屬實作層 gray area，new-project 不鎖死 | — Pending |

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
