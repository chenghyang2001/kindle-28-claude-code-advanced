# Project Research Summary

**Project:** 待辦清單 CLI — 新增「完成任務」(complete_task) 功能
**Domain:** 純 Python 標準庫、單檔 in-memory CLI（functional core / imperative shell）
**Researched:** 2026-07-23
**Confidence:** HIGH

## Executive Summary

這是一個刻意保持極簡的單檔 Python 待辦清單 CLI（`app.py` + `test_app.py`，12 個既有 pytest 測試），本次任務是加入「完成任務」狀態。四份研究一致指向同一個核心結論：**這不是新增子系統,而是一次「資料結構遷移」**——`tasks: list[str]` 必須換成能同時攜帶名稱與完成狀態的結構，而業界（todo.txt、Taskwarrior、Ultralist）在這類功能上的做法高度收斂，PROJECT.md 既有決策（依名稱操作、✓ 留在清單上、不做 undo、重複 complete 給友善訊息）也完全落在這些工具的 table stakes 範圍內，不需要另尋方向。

推薦做法是零外部依賴、全部使用 Python 標準庫：用 `dataclass Task(name: str, done: bool = False)` 取代裸字串,搭配既有的「函式接收 tasks 作為第一參數、就地變動或回傳複製」風格,不需要 `attrs`/`pydantic`/`colorama` 等任何第三方套件。真正的風險不在「要選什麼工具」，而在遷移過程中的邊界案例與既有契約的隱性破壞：(1) 12 個既有測試的字串斷言全部要跟著資料結構機械式改寫，稍有不慎會把測試改到只驗證型別而非行為；(2) `delete_task` 目前用 `name in tasks`／`tasks.remove(name)` 做精確字串比對，換成物件後這兩個運算子會靜默失效，必須整段重寫且是本次風險最高的環節；(3) 既有系統從未強制名稱唯一，`complete_task` 面對重複名稱任務時的行為必須明確定義並補測試，否則會出現「完成一筆卻連帶影響另一筆同名任務」的正確性錯誤；(4) Windows cp950 終端機印出 `✓`（U+2713）會拋 `UnicodeEncodeError`，需要延續專案既有 `PYTHONUTF8=1` 慣例並在未設定時手動驗證一次。

風險緩解策略清楚：先定案資料結構（dataclass Task,不用 dict/NamedTuple/雙 list/字串前綴 hack）→ 先遷移既有測試讓回歸安全網變綠 → 再實作 `complete_task` 新邏輯 → 最後整合 CLI 顯示層。整個功能範圍已被 PROJECT.md 的 Out of Scope 清楚圈定（不做 undo/toggle/持久化/依編號操作），最大的紀律風險是「順手多做一點」的範圍蔓延,需要在 code review 階段主動核對。

## Key Findings

### Recommended Stack

不需要新增任何依賴。`requirements.txt` 維持只有 `pytest` 一行。核心決策是用 Python 3.14 內建的 `dataclasses` 定義 `Task` 資料結構，取代目前的裸字串；`pytest` + `capsys` fixture 延續既有測試風格，`capsys` 捕捉的是 Python 內部字串（非真實終端機輸出），所以測試本身不受 Windows cp950 編碼影響。

**Core technologies:**

- Python `dataclasses`（stdlib）: 定義 `Task(name: str, done: bool = False)` — 自動產生 `__init__`/`__eq__`/`__repr__`，讓既有測試斷言可機械式改寫（`"買牛奶"` → `Task("買牛奶")`），且預設可變、可直接 `.done = True` 就地修改，貼合既有 functional core 風格
- `pytest`（既有）: 延續測試框架 — `capsys` fixture 驗證 CLI 印出 `✓` 的行為，不需額外測試工具
- `PYTHONUTF8=1`（環境變數，非套件）: 讓 `print("✓")` 在 Windows cp950 終端機不崩潰 — 專案 `GSD-PRACTICE.md` 已建立此慣例，延續即可

**明確不要用：** `attrs`/`pydantic`（驗證/序列化用不到，過度設計）、`colorama`（純文字 `✓` 已足夠，且增加 Windows 相容性風險）、`dataclass(slots=True)`（Python 3.14 有已知 regression，CPython issue #135228/#142214）。

### Expected Features

**Must have (table stakes)：**

- `complete <名稱>` 標記任務完成 — 所有主流待辦 CLI（todo.txt `do`、Taskwarrior `done`、Ultralist `complete`）都有對應動詞指令
- `list` 顯示 ✓ 標記且已完成任務不消失 — 比照 todo.txt/Ultralist「所見即所有」模型（非 Taskwarrior 的預設隱藏模型）
- 對不存在任務 complete 時回報「找不到任務」— 與既有 `delete_task` 錯誤處理風格一致
- `delete_task` 對已完成任務仍要能刪除 — PROJECT.md 未明文但屬隱含子案例，建議在需求定義時明確補上驗收準則
- 既有 12 個測試維持綠燈 + 新增對應測試 — 相容性硬要求

**Should have（本專案架構下的差異化選擇）：**

- 重複 complete 給友善訊息而非報錯/靜默 — 因採「名稱定址 + 完成任務仍可見」模型，此情境比多數工具更常態發生，友善處理是加分項
- complete 是單向冪等（非 toggle）— 降低誤觸風險，PROJECT.md 已明確排除 toggle

**Defer (v2+)：** `uncomplete` 取消完成、`list --pending`/`list --done` 過濾檢視、完成時間戳記、持久化、依編號操作。這些都在 PROJECT.md Out of Scope 範圍內，本次不應投入設計成本。

### Architecture Approach

現況是單檔 `app.py`，`tasks: list[str]` 是唯一狀態，三個核心函式（`add_task`/`list_tasks`/`delete_task`）以 `tasks` 為第一參數顯式傳遞。五種資料結構方案比較後，**推薦 `dataclass Task`**：與現有 dict/NamedTuple/平行 completed-set/字串前綴 hack 相比，dataclass 在「測試遷移成本」「型別安全」「與既有就地變動風格一致性」三方面表現最佳；平行 completed-set 表面最省事但有正確性缺陷（無法區分重複名稱的不同實例，違反既有測試已證實的「支援重複名稱」行為），字串前綴 hack 會違反 PROJECT.md「不動 delete_task」的明文限制，兩者都應淘汰。

**Major components:**

1. **`Task` dataclass**（新）— 純值物件，只有 `name`/`done` 兩欄位，無方法（no methods），保持「無 class 持有狀態」的既有精神
2. **Core Function Layer**（`add_task`/`list_tasks`/`delete_task`/`complete_task`）— `delete_task` 是唯一一個「簽名不變、但內部比對邏輯必須整段重寫」的既有函式（`in`/`remove` 換成物件後會靜默失效）；`complete_task` 是新函式，需要三態回傳設計（成功/找不到/已完成過），無法用單一 bool 表達
3. **CLI dispatch layer**（`main()`）— 新增 `complete` 指令分支，依三態回傳印出對應訊息；顯示層 `_print_task_list` 讀取 `.name`/`.done` 加上 ✓ 標記

建議建置順序：定義 Task → 改寫 add_task → 改寫 delete_task（風險最高）→ 確認 list_tasks 淺複製語意 → 改寫顯示層 → **先遷移既有 12 個測試斷言使其重新變綠** → 實作 complete_task → CLI dispatch 整合 → 新增 complete 測試 → 手動 REPL 驗證。

### Critical Pitfalls

1. **既有測試斷言耦合資料結構** — 12 個測試目前直接比較 `tasks == ["買牛奶"]`，遷移時容易「換型別就交差」而弱化原本驗證的行為契約（順序、去空白、副本語意）。應逐一確認修改後仍驗證原始行為，而非只是型別相符。
2. **依名稱操作 + 重複任務名稱的完成歧義** — 既有系統從未強制名稱唯一（`test_delete_only_first_occurrence` 已證實支援重複名稱），`complete_task` 必須明確決定並測試「兩筆同名、一完成一未完成」時的行為（建議與 delete 一致：只影響第一個未完成的）。
3. **Windows cp950 印出 ✓ 觸發 UnicodeEncodeError** — 純中文字元恰好在 cp950 範圍內矇混過關，但 `✓` 不在傳統中文編碼表內；必須在未設 `PYTHONUTF8=1` 的原生 Windows 終端機手動驗證一次，不能只靠 pytest/UTF-8 終端機驗證。
4. **complete 與 delete 語意混淆** — 複製貼上 `delete_task` 邏輯改寫 `complete_task` 容易誤用 `remove` 造成任務消失或順序打亂；需明確測試 complete 前後清單長度與順序不變。
5. **list_tasks 淺複製產生別名共享 bug** — 字串不可變時淺複製完全安全，換成可變的 dataclass 後，複製出的清單裡元素仍是同一參照，修改回傳值的欄位會污染原始資料；既有測試不會抓到，需新增專門測試。
6. **範圍蔓延（undo/toggle/持久化）** — PROJECT.md 已明確排除，但「已完成任務再次 complete」的處理最直覺答案就是 toggle，實作時容易順手引入，需在 code review 專門核對。

## Implications for Roadmap

Based on research, suggested phase structure:

### Phase 1: 資料結構遷移與測試安全網重建

**Rationale:** 這是所有後續工作的硬性前置依賴（ARCHITECTURE.md 與 FEATURES.md 都指出：純字串無法攜帶完成狀態），且遷移期間既有測試會暫時全數變紅，必須獨立成一個階段先讓回歸安全網恢復綠燈，才能安全疊加新功能。
**Delivers:** `Task` dataclass 定義；`add_task`/`delete_task`/`list_tasks` 改寫完成；12 個既有測試斷言遷移為 `Task(...)` 建構式且全數通過
**Addresses:** FEATURES.md「既有 12 個測試維持綠燈」table stakes；「delete 對完成狀態一視同仁」隱含需求
**Avoids:** Pitfall 1（測試斷言耦合資料結構）、Pitfall 7（list_tasks 別名污染）；`delete_task` 內部比對邏輯重寫時需搭配即時測試驗證（風險最高環節）

### Phase 2: complete_task 核心邏輯與冪等性設計

**Rationale:** 資料結構到位後，才能實作真正的新行為；此階段的回傳值設計（三態：成功/找不到/已完成過）與重複名稱歧義處理是本次唯一的新 API 設計決策，需在同一階段一併拍板。
**Delivers:** `complete_task(tasks, name)` 函式，含三態回傳設計；涵蓋成功/找不到/已完成過/重複名稱四類情境的新測試
**Uses:** STACK.md 的 dataclass `Task`；ARCHITECTURE.md 建議的三態回傳（非布林值）
**Implements:** Core Function Layer 中的新函式，遵循「就地變動、不引入 remove/append」原則

### Phase 3: CLI 整合與顯示層 / 跨平台驗證

**Rationale:** 顯示層是唯一「使用者看得見」的部分，且涉及 Windows cp950 編碼這個獨立風險面向，適合放在資料邏輯穩定之後、作為最後整合與驗收階段。
**Delivers:** `_print_task_list` 加上 ✓ 標記；`main()` CLI dispatch 新增 `complete` 指令分支與 help text 更新；未設 `PYTHONUTF8=1` 的原生 Windows 終端機手動驗證通過

### Phase Ordering Rationale

- 資料結構決策（Phase 1）在 FEATURES.md 與 ARCHITECTURE.md 中都被標記為「一切的前提」，必須最先完成且獨立驗證，避免新舊改動疊加導致除錯困難
- Phase 1 刻意把「既有測試遷移」與「新功能實作」分開，是 PITFALLS.md Pitfall 1 的直接對策：先確保回歸安全網完整，再新增功能程式碼
- Phase 3 把「顯示格式」與「資料邏輯」分開驗收，對應 PITFALLS.md Pitfall 6（測試不應耦合顯示表示法），也讓 cp950 這個跨平台風險有獨立的驗收檢查點

### Research Flags

Phases likely needing deeper research during planning:

- **無** — 本次功能範圍小且四份研究已涵蓋主要技術決策（資料結構選型、回傳值設計、編碼陷阱），三個 phase 都屬於標準 Python stdlib 模式，不需要額外的 `--research-phase` 深挖

Phases with standard patterns (skip research-phase):

- **Phase 1：** dataclass 語法與 pytest 斷言遷移是穩定的 Python 語言特性，四份研究已提供具體程式碼範例
- **Phase 2：** 三態回傳設計已有明確建議（字串常數或列舉），非新穎技術問題
- **Phase 3：** `PYTHONUTF8=1` 與 `sys.stdout.reconfigure` 是專案既有已驗證慣例的延伸

## Confidence Assessment

| Area | Confidence | Notes |
| ------ | ------------ | ------- |
| Stack | HIGH | 純 stdlib 語法，官方文件（pytest capsys、Python 3.14 dataclasses 預設行為）直接驗證；pytest 9.x 版本相容性為 MEDIUM（未逐條核對 changelog）但不影響核心結論 |
| Features | MEDIUM | 基於 todo.txt/Taskwarrior/Ultralist 的 WebSearch 摘要比對，多數為官方文件確認（HIGH），少數（dstask）僅供脈絡參考（LOW），整體判為 MEDIUM |
| Architecture | HIGH | 直接檢視本專案既有原始碼與測試，搭配 Python 語言穩定語意（淺複製、dataclass `__eq__`），無需外部佐證 |
| Pitfalls | HIGH | 多數結論直接來自閱讀 `app.py`/`test_app.py`/`PROJECT.md` 實際程式碼與既有測試斷言，非泛用臆測 |

**Overall confidence:** HIGH

### Gaps to Address

- **重複名稱任務與 complete 的交互行為未定案**：ARCHITECTURE.md 明確指出 PROJECT.md 只規範「對已完成任務再次 complete」，但沒定義「兩筆同名、一完成一未完成」時應該影響哪一筆。建議在 plan-phase 明確拍板（建議：找第一個尚未完成的同名任務），並補一則測試固化行為。
- **`delete_task` 對已完成任務的行為未在 PROJECT.md 明文記載**：FEATURES.md 指出這是隱含需求，建議在需求定義階段補上明確的驗收準則（delete 對任何完成狀態的任務一視同仁）。
- **是否要加 `sys.stdout.reconfigure` 防禦碼**：STACK.md 與 PITFALLS.md 都提出這是可選項（多一行防禦碼 vs. 維持「靠慣例、不加額外程式碼」的極簡風格），屬於 plan-phase 的取捨，非必須立即決定。

## Sources

### Primary (HIGH confidence)

- [pytest 官方文件 — capsys fixture](https://docs.pytest.org/en/stable/how-to/capture-stdout-stderr.html) — `readouterr()` API 與文字/位元組行為
- [Taskwarrior — Done Command 官方文件](https://taskwarrior.org/docs/commands/done/) — `done` 指令行為
- [Taskwarrior — Filters 官方文件](https://taskwarrior.org/docs/filter/) — `list` 報表預設過濾規則
- 本專案既有原始碼：`app.py`、`test_app.py`、`.planning/codebase/ARCHITECTURE.md`、`.planning/PROJECT.md`

### Secondary (MEDIUM confidence)

- WebSearch: pytest 最新版本（9.1.1，2026-06-19）— PyPI release tracking，未逐一核對官方 changelog 全文
- WebSearch: Python 3.14 dataclasses 預設行為與 `slots=True` regression — GitHub issue（cpython#135228、#142214）為社群回報，與官方文件描述一致
- [Todo.Txt format (GitHub)](https://github.com/todotxt/todo.txt) — 完成標記語法
- [Ultralist — Showing tasks 官方文件](https://ultralist.io/docs/cli/showing_tasks/) — `[x]` 完成標記顯示方式

### Tertiary (LOW confidence)

- [dstask (GitHub, naggie/dstask)](https://github.com/naggie/dstask) — 僅供 Taskwarrior 替代方案的背景脈絡參考，未深入查證完成行為細節

---
*Research completed: 2026-07-23*
*Ready for roadmap: yes*
