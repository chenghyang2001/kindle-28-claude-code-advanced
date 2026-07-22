# 待辦清單 CLI — 完成任務功能（demo-gsd-01-20260723）

## What This Is

一個極簡的 in-memory 待辦清單 CLI（單檔 `app.py`，Python 3.14，pytest 測試），目前支援 add / list / delete / quit 四個指令。這次要在這個既有基底上新增第 4 個核心功能：**完成任務（complete_task）**，讓使用者能把任務標記為已完成並在清單上看到打勾標記。

## Core Value

使用者能標記任務完成、並在清單上一眼看到哪些做完了（✓）——完成狀態必須正確保存與呈現，不能跟刪除混為一談。

## Requirements

### Validated

- ✓ 使用者可用 `add <名稱>` 新增任務（空白名稱會被拒絕、自動去頭尾空白）— existing
- ✓ 使用者可用 `list` 檢視目前所有任務（回傳副本、不污染原始資料）— existing
- ✓ 使用者可用 `delete <名稱>` 依名稱刪除任務（不存在時回報找不到）— existing
- ✓ 互動式 CLI loop（未知指令提示、EOF/Ctrl+C 優雅退出）— existing
- ✓ pytest 測試套件覆蓋三個核心函式（12 個測試）— existing

### Active

- [ ] 使用者可用 `complete <名稱>` 把指定任務標記為已完成（介面風格與 delete 一致）
- [ ] `list` 顯示完成狀態：已完成任務帶 ✓ 標記、留在清單上（不消失）
- [ ] 對不存在的任務 complete 時，回報「找不到任務」
- [ ] 對已完成的任務再次 complete 時，回報「已經完成過」（不報錯、不改變狀態）
- [ ] 既有 12 個測試全數維持綠燈，且 complete 功能有對應的新測試

### Out of Scope

- 取消完成（undo / uncomplete）— 使用者明確決定 v1 不做，重複 complete 僅提示
- 依編號操作（complete 2 / delete 2）— 維持與既有 delete 一致的「依名稱」介面，避免混用兩套定位方式
- 修改 delete 行為 — delete_task 已存在且有測試，本次不動
- 持久化（存檔/資料庫）— 既有系統即為 in-memory，本次不擴大範圍
- 任務優先級、到期日、分類等進階欄位 — 非本次目標

## Context

- **Brownfield 基底**：`.planning/codebase/` 已有完整 codebase map（2026-07-22）。單檔程序式設計、「functional core, imperative shell」模式：核心函式接收 `tasks` 參數、`main()` 持有唯一狀態。
- **關鍵技術張力**：目前任務是純字串 `list[str]`，字串無法攜帶「已完成」狀態 → complete 功能勢必要動資料結構（候選：dict、dataclass、雙清單、tuple……）。這是本專案的核心設計決策，留待 discuss-phase / plan-phase 決定。
- **既有測試以字串型態斷言**（如 `assert tasks == ["買牛奶"]`），資料結構一旦改變，12 個既有測試的斷言方式如何維持綠燈是重要的相容性考量。
- 學習用專案：目的是完整走一遍 GSD brownfield 流程（questioning → requirements → roadmap → plan → execute）。

## Constraints

- **Tech stack**: Python 3 標準庫 + pytest — 既有專案無框架、無第三方依賴，維持極簡
- **Compatibility**: 既有 12 個測試必須繼續通過（允許因資料結構變更而調整斷言，但行為語意不可變）
- **編碼**: Windows 環境執行 Python 需 `PYTHONUTF8=1`（cp950 陷阱）
- **Conventions**: 繁體中文 docstring/註解、snake_case、依名稱操作的 CLI 介面風格

## Key Decisions

| Decision | Rationale | Outcome |
| ---------- | ----------- | --------- |
| complete 依名稱指定（不用編號） | 與既有 delete 介面一致，不混用兩套定位方式 | — Pending |
| 已完成任務留在清單上打勾（不移除） | 使用者要看得到成就感；與 delete 語意區隔 | — Pending |
| v1 不做 undo，重複 complete 僅提示 | 控制範圍；toggle 語意容易誤觸 | — Pending |
| 任務資料結構如何改（str → ?） | 字串無法攜帶完成狀態，必須改 | — Pending（留待 discuss/plan-phase） |

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
*Last updated: 2026-07-23 after initialization*
