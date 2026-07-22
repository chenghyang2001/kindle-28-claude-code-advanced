# Roadmap: 待辦清單 CLI — 完成任務功能

## Overview

現有的極簡待辦清單 CLI（單檔 `app.py`）只支援 add / list / delete，任務資料是裸字串 `list[str]`，無法攜帶「已完成」狀態。本次里程碑分三個階段交付「完成任務」功能：先把資料結構換成能攜帶完成狀態的 `Task`，並讓既有 12 個測試在新結構下重新變綠（回歸安全網）；接著實作 `complete_task` 的核心邏輯與冪等性設計（成功/找不到/重複三態）；最後把完成狀態呈現在 `list` 顯示層與 CLI 互動迴圈，並驗證 Windows 原生終端機印出 ✓ 不會出錯。三階段依序推進、互為前置依賴，走完即完整交付 Core Value：使用者能標記任務完成、並在清單上一眼看到哪些做完了。

## Phases

**Phase Numbering:**

- Integer phases (1, 2, 3): Planned milestone work
- Decimal phases (2.1, 2.2): Urgent insertions (marked with INSERTED)

Decimal phases appear between their surrounding integers in numeric order.

- [ ] **Phase 1: 資料結構遷移與測試安全網重建** - 把 `tasks` 從裸字串換成 `Task` 資料結構，既有 12 個測試在新結構下全數變回綠燈
- [ ] **Phase 2: complete_task 核心邏輯與冪等性設計** - 新增 `complete_task` 函式，定案成功/找不到/已完成過三態回傳與名稱比對規則
- [ ] **Phase 3: CLI 整合與顯示層 / 跨平台驗證** - `list` 顯示 ✓ 標記、CLI 新增 `complete` 指令分支，並驗證 Windows 原生終端機不因 ✓ 字元出錯

## Phase Details

### Phase 1: 資料結構遷移與測試安全網重建

**Goal**: 建立 `Task` 資料結構取代裸字串，讓「完成狀態」有地方存放；既有 `add_task`/`delete_task`/`list_tasks` 改寫完成後，12 個既有測試的斷言遷移為 `Task(...)` 建構式並全數通過，且驗證的仍是原始行為語意（順序、去空白、副本語意），而不只是型別相符
**Mode:** mvp
**Depends on**: Nothing (first phase)
**Requirements**: COMPAT-01, COMPAT-02
**Success Criteria** (what must be TRUE):

  1. 既有 12 個測試在資料結構改為 `Task` 後全數通過（斷言改為 `Task(...)` 建構式，但驗證的行為語意——新增去空白、清單順序、刪除只影響第一筆同名——維持不變）
  2. `list_tasks` 回傳的清單是安全複製：修改回傳值中的元素（含其 `.done` 欄位）不會污染 `main()` 持有的原始 `tasks`
  3. `delete_task` 能刪除任意完成狀態（已完成或未完成）的任務，刪除行為不因任務是否標記完成而不同
**Plans**: TBD

Plans:

- [ ] 01-01: 定義 `Task` dataclass，改寫 `add_task`/`delete_task`/`list_tasks` 內部邏輯與淺複製語意
- [ ] 01-02: 遷移既有 12 個測試斷言為 `Task(...)` 建構式，補上 `delete_task` 對已完成任務的驗證，確認全數綠燈

### Phase 2: complete_task 核心邏輯與冪等性設計

**Goal**: 在 `Task` 資料結構到位後，新增 `complete_task(tasks, name)` 函式，定案並實作「成功完成 / 找不到任務 / 已完成過」三態回傳設計，比對規則與 `delete_task` 完全一致（去頭尾空白、依名稱定位、重複名稱時只影響第一個尚未完成的同名任務）
**Mode:** mvp
**Depends on**: Phase 1
**Requirements**: COMP-01, COMP-02, COMP-03, COMP-04, COMPAT-03
**Success Criteria** (what must be TRUE):

  1. 使用者對存在且未完成的任務呼叫 `complete_task` 後，該任務的 `.done` 變為 `True`，清單其餘任務與順序不受影響
  2. 使用者對不存在的任務呼叫 `complete_task` 時，得到明確可辨識的「找不到任務」回傳結果，任務清單完全不變
  3. 使用者對已完成的任務再次呼叫 `complete_task` 時，得到「已經完成過」的回傳結果，狀態不改變（單向冪等，不 toggle）
  4. `complete_task` 的名稱比對規則（去頭尾空白）與 `delete_task` 完全一致，同一個名稱字串在兩個函式中定位到同一筆任務；面對重複名稱任務時只影響第一個尚未完成的同名任務
  5. 新增至少涵蓋成功完成、找不到任務、重複 complete 三種情境的測試，全數通過
**Plans**: TBD

Plans:

- [ ] 02-01: 實作 `complete_task` 三態回傳邏輯與重複名稱歧義處理
- [ ] 02-02: 補齊 complete 三種情境（成功/找不到/重複）的新測試

### Phase 3: CLI 整合與顯示層 / 跨平台驗證

**Goal**: 把完成狀態呈現給使用者——`list` 顯示層加上 ✓ 標記、`main()` CLI 互動迴圈新增 `complete <名稱>` 指令分支並印出對應訊息，同時驗證未設定 `PYTHONUTF8=1` 的原生 Windows 終端機執行時不因 ✓ 字元拋出 `UnicodeEncodeError`
**Mode:** mvp
**Depends on**: Phase 2
**Requirements**: DISP-01, DISP-02
**Success Criteria** (what must be TRUE):

  1. 使用者執行 `list` 時，已完成任務帶 ✓ 標記、未完成任務不帶，一眼可辨識
  2. 已完成任務留在清單顯示中不消失，完成與刪除語意在畫面上清楚區分
  3. 使用者在 CLI 互動迴圈中輸入 `complete <名稱>` 能觸發對應指令分支，並依三態結果印出對應訊息（成功/找不到/已完成過）
  4. 在未設定 `PYTHONUTF8=1` 的原生 Windows 終端機執行 `list` 時，✓ 字元正常印出而不拋出 `UnicodeEncodeError`
**Plans**: TBD

Plans:

- [ ] 03-01: `_print_task_list` 加上 ✓ 標記、`main()` 新增 `complete` 指令分支與 help text 更新
- [ ] 03-02: 手動驗證未設 `PYTHONUTF8=1` 的原生 Windows 終端機執行結果

## Progress

**Execution Order:**
Phases execute in numeric order: 1 → 2 → 3

| Phase | Plans Complete | Status | Completed |
| ------- | ---------------- | -------- | ----------- |
| 1. 資料結構遷移與測試安全網重建 | 0/2 | Not started | - |
| 2. complete_task 核心邏輯與冪等性設計 | 0/2 | Not started | - |
| 3. CLI 整合與顯示層 / 跨平台驗證 | 0/2 | Not started | - |
