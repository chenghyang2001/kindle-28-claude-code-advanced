# Pitfalls Research

**Domain:** 為既有「純字串 in-memory 待辦清單 CLI」新增 complete_task（完成狀態）功能
**Researched:** 2026-07-23
**Confidence:** HIGH（多數結論直接來自閱讀 `app.py` / `test_app.py` / `PROJECT.md` 實際程式碼與測試斷言，非泛用臆測）

## Critical Pitfalls

### Pitfall 1: 資料結構變更打破既有字串斷言測試

**What goes wrong:**
`tasks` 目前是 `list[str]`，12 個既有測試大量直接斷言 `tasks == ["買牛奶"]`、`tasks == ["任務A", "任務B"]` 這種「整個清單等於一串純字串」的寫法（見 `test_app.py` 的 `TestAddTask` / `TestDeleteTask`）。一旦把 `tasks` 改成 `list[dict]`、`list[Task]`（dataclass）或雙清單/tuple 等任何能攜帶「完成狀態」的結構，這些既有斷言會**全部**變成型別不符而失敗，即使底層行為完全正確。

**Why it happens:**
新增 completion 狀態時開發者容易「先把資料結構改好，再回頭修測試」，忽略了 PROJECT.md 明確要求「既有 12 個測試必須繼續通過（允許因資料結構變更而調整斷言，但行為語意不可變）」。若不先設計「測試要斷言什麼」，很容易在遷移過程中把測試改到只驗證新結構的表面形狀，卻悄悄弱化了原本驗證的行為（例如「回傳副本」「去頭尾空白」「只刪除第一筆符合的」）。

**How to avoid:**

- 遷移測試斷言時，優先改成「透過既有函式介面查詢行為」而非直接比較內部資料結構。例如改用 helper `task_names(tasks)`（抽取所有名稱）或 `is_task_completed(tasks, name)` 之類的存取函式，讓測試不需要知道底層是 dict 還是 dataclass。
- 若仍要斷言完整清單，至少要有一個「golden shape」共識（例如都用 `{"name": ..., "completed": ...}` 的 dict），並在 PR/plan 文件中明確記下這個決定，讓所有新舊測試共用同一種比較方式。
- 逐一走過 12 個既有測試，確認每個測試修改後仍然驗證原本要驗證的**行為**，而不是被動地把 `"買牛奶"` 換成 `{"name": "買牛奶", "completed": False}` 就交差。

**Warning signs:**

- `pytest` 一次性冒出大量（非個位數）失敗，且失敗訊息都是型別不符（`AssertionError: [{'name': ...}] != ['買牛奶']`）而非邏輯錯誤。
- 修改測試時發現「只要把預期值換個型態就綠燈」，卻沒有人重新檢查這個測試原本在防呆什麼。

**Phase to address:**
資料結構設計 / 測試遷移階段（應在實作 `complete_task` 之前，先完成資料結構決策與既有測試的斷言遷移）。

---

### Pitfall 2: 依名稱操作 + 重複任務名稱的完成歧義

**What goes wrong:**
既有 `delete_task` 用 `tasks.remove(name)`，其語意是「只刪除第一個符合的項目」（`test_delete_only_first_occurrence` 已經驗證此行為：清單 `["任務A", "任務A"]` 呼叫一次 delete 後只剩一個 `"任務A"`）。`complete_task` 若沿用同一套「依名稱定位」介面（PROJECT.md 明確要求風格與 delete 一致），在有重複名稱任務時，使用者完全無法指定「完成哪一個」，只能盲猜是第一筆還是全部都變成已完成。這是本次功能新增最容易被忽略的邊界案例，因為既有系統從未強制名稱唯一。

**Why it happens:**
既有系統把「依名稱操作」設計成隱含假設「名稱通常唯一」，但從未真正驗證或強制唯一性（`add_task` 沒有查重）。開發者在新增 complete 功能時容易照抄 delete 的實作模式（找第一個符合的），卻沒意識到「刪除」是破壞性的一次性操作、影響有限，而「完成狀態」是持續存在於清單上的可見標記，重複名稱下的歧義會長期反覆出現在每次 `list` 顯示中，且如果實作成「符合名稱的全部標記完成」還會產生跟 delete 不一致的語意（一個是「只動第一個」、一個是「全部都動」）。

**How to avoid:**

- 明確決定並記錄 `complete_task` 對重複名稱的行為：建議與 `delete_task` 保持一致（只影響第一個符合、且未完成的項目），並在函式 docstring 與測試中明確寫出這個決定。
- 新增至少一個測試案例：清單中有兩筆同名任務，一筆已完成、一筆未完成，呼叫 `complete_task` 應該影響哪一筆（建議：優先影響第一個「未完成」的，讓已完成的維持原狀，避免「已經完成過」的提示邏輯打架）。
- 在 PITFALLS 對應的 plan 階段就把「重複名稱歧義」列為明確的驗收條件，而不是留到程式寫完才發現。

**Warning signs:**

- 測試只涵蓋「清單中恰好一筆」的情境，從未出現兩筆同名任務的測試案例。
- 手動測試時對同名任務呼叫 `complete`，結果與直覺不符（例如兩筆都被標記，或標記了「錯的」那一筆）。

**Phase to address:**
`complete_task` 核心邏輯實作階段（應與資料結構設計同一階段決策，因為歧義處理方式會影響資料結構要不要引入唯一 id）。

---

### Pitfall 3: Windows cp950 主控台印出 ✓ Unicode 字元觸發 UnicodeEncodeError

**What goes wrong:**
`_print_task_list` 目前只印純中文字串（cp950 可涵蓋的 Big5 範圍字元），一旦新增已完成任務要印出 `✓`（U+2713，checkmark），這個字元不在 cp950 編碼表內。若使用者直接用系統預設編碼（未設定 `PYTHONUTF8=1`）在 Windows 主控台執行 `python app.py`，`print()` 寫入 stdout 時會拋出 `UnicodeEncodeError: 'cp950' codec can't encode character '✓'`，導致 CLI 直接崩潰，而不是「顯示不出來但至少不當機」。

**Why it happens:**
開發者通常在已設定 `PYTHONUTF8=1` 或 UTF-8 終端機（如 VS Code 內建終端、Git Bash）的環境下開發與測試，看不到這個問題；但 CLAUDE.md / PROJECT.md 都明確標註「Windows 環境執行 Python 需 `PYTHONUTF8=1`（cp950 陷阱）」，代表此專案的目標執行環境包含未設定此環境變數的原生 `cmd.exe` / PowerShell 主控台。純中文字元恰好在 cp950 範圍內能矇混過關，但 `✓`、`✗`、emoji 等符號不在傳統中文編碼表內，是最容易被忽略的一類字元。

**How to avoid:**

- 在 README / CLAUDE.md 既有的 `PYTHONUTF8=1` 提醒之外，把「新增 ✓ 顯示」明確視為需要重新驗證編碼相容性的變更點。
- 撰寫一個手動或自動化的煙霧測試：在**不設定** `PYTHONUTF8=1` 的情況下模擬呼叫 `_print_task_list`（或直接呼叫並捕捉 `UnicodeEncodeError`），確認至少不會讓整個 CLI 崩潰退出；若無法保證環境一定有 UTF-8，考慮加上 `try/except UnicodeEncodeError` 的防禦性輸出（退化為 `[done]` 純 ASCII 標記）。
- 若能力範圍內，直接在 `main()` 開頭呼叫 `sys.stdout.reconfigure(encoding="utf-8", errors="replace")`（Python 3.7+ 可用），讓輸出即使在 cp950 主控台也不會整個當機，僅是顯示異常字元。

**Warning signs:**

- 開發過程中的測試全數在 pytest（不經過真實終端機 stdout 編碼）或 UTF-8 終端機下執行，從未在原生 Windows `cmd.exe` 手動跑過 `python app.py` 並輸入 `list`。
- Code review 時看到 `print(f"✓ {task}")` 這類字面量卻沒有任何編碼防禦或測試涵蓋。

**Phase to address:**
CLI 顯示層整合階段（`list` 指令輸出格式修改時），建議在該階段的驗收條件中明列「需在未設 PYTHONUTF8 的 Windows 原生終端機手動驗證一次」。

---

### Pitfall 4: complete 與 delete 語意混淆（使用者操作與程式邏輯雙重風險）

**What goes wrong:**
`delete` 是破壞性、不可逆的移除操作；`complete` 是非破壞性、可查看歷史的狀態標記（任務留在清單上）。兩者共用「依名稱操作」的相同 CLI 介面模式（`complete <名稱>` / `delete <名稱>`），容易在兩個層次上被混淆：(1) **使用者操作層**——打錯指令把想完成的任務誤刪，或反過來以為完成了但其實刪除了；(2) **實作層**——開發者複製貼上 `delete_task` 的程式碼改寫 `complete_task` 時，遺漏了兩者本質不同（remove vs mutate-in-place-and-keep），例如誤把 `complete_task` 寫成「找到後 remove 再重新 append 一個已完成版本」，導致清單順序被打亂（`test_add_multiple_tasks_preserves_order` 這類「順序守恆」的隱性契約被破壞）。

**Why it happens:**
PROJECT.md 明確要求 complete 的 CLI 風格要跟 delete 一致，這是刻意的設計決策（降低使用者學習成本），但「介面一致」不等於「實作邏輯可以照抄」。開發者在追求程式碼一致性時，容易把 `delete_task` 的 `if name in tasks: tasks.remove(name); return True` 模式機械式套用到 `complete_task`，卻忘記 complete 不該讓任務消失。

**How to avoid:**

- 明確在函式 docstring 寫清楚「complete_task 不會移除任務，只會修改其完成狀態旗標，清單長度與順序維持不變」，並用測試斷言清單長度、順序在 complete 前後一致。
- CLI 層的指令說明文字（`print("指令：add ... | list | delete ... | quit")`）要同步更新為包含 `complete`，且措辭上明確用「標記完成」而非「完成」這種可能被誤解為「移除」的字眼，降低使用者誤觸風險。
- 新增測試：對同一份清單先 `complete_task` 再 `list_tasks`，斷言清單長度不變、原順序不變、目標任務的完成狀態變更、其餘任務不受影響。

**Warning signs:**

- `complete_task` 的實作中出現 `tasks.remove(...)` 或重新建立清單（`tasks = [...]`）等會改變順序或造成任務消失的程式碼。
- 手動測試 `complete` 後執行 `list`，任務數量減少或順序跟 `add` 時不同。

**Phase to address:**
`complete_task` 核心邏輯實作階段；CLI 指令說明文字（help text）應在同一階段一併更新，避免上線後才發現使用者困惑。

---

### Pitfall 5: 範圍蔓延——undo / toggle / 持久化悄悄溜進來

**What goes wrong:**
PROJECT.md 的 Out of Scope 明確排除「取消完成（undo/uncomplete）」「依編號操作」「持久化」。但這類功能在實作 `complete_task` 時「順手就能加」的誘惑很高：例如為了處理「已完成任務再次 complete」的情境，開發者可能會想「不如順便做成 toggle（再次 complete 就變回未完成）」；或者測試時想手動重跑驗證，順手加了個簡單的存檔功能「方便除錯」。這些看似合理的小擴充會讓 diff 變大、審查變難，也違反使用者已經明確做出的範圍決策（PROJECT.md Key Decisions 表格記載「v1 不做 undo，重複 complete 僅提示」、「toggle 語意容易誤觸」）。

**Why it happens:**
「已經在改這個函式了，順便多做一點」是常見的开发心理慣性，尤其當「重複 complete 要怎麼處理」這個問題的最直覺答案就是 toggle。但 PROJECT.md 已經明確記錄「toggle 語意容易誤觸」是刻意排除 toggle 的理由——這代表本次已經討論過這個選項並否決，實作階段不應該重新引入。

**How to avoid:**

- 實作前重讀 PROJECT.md 的 Out of Scope 段落，把它當作跟 Active Requirements 同等重要的「不做清單」。
- `complete_task` 對「已完成任務再次呼叫」的正確行為是：回報「已經完成過」、**不拋錯、不改變狀態**（PROJECT.md Active 需求已明文規定），任何會讓狀態變動的實作（包含 toggle）都是偏離規格。
- Code review 時專門檢查：函式簽名是否新增了 Out of Scope 提到的參數（如 `task_id`、`persist=True`）；CLI 是否新增了 Out of Scope 提到的指令（如 `undo`）。

**Warning signs:**

- `complete_task` 的函式簽名或回傳值出現「切換」語意（例如回傳目前完成狀態的布林值並在每次呼叫時反轉），而非單純「標記為完成」。
- 出現任何檔案讀寫（`open(..., "w")`）程式碼，即使宣稱只是「除錯用」。
- CLI 指令清單新增了 PROJECT.md 未提及的指令字。

**Phase to address:**
需求確認 / plan 階段的驗收條件應把「未新增 Out of Scope 項目」列為明確檢查點；code review 階段再次核對。

---

### Pitfall 6: 測試斷言耦合「顯示表示法」而非「行為狀態」

**What goes wrong:**
`list` 顯示已完成任務要帶 ✓ 標記是 UI 層的呈現需求，但如果測試直接斷言 `_print_task_list` 或 `list` 指令的**輸出字串**（例如斷言 `capsys.readouterr().out == "  1. 買牛奶 ✓\n"`），日後只要調整顯示格式（例如把 ✓ 換成 `[x]`、調整縮排、加上編號對齊），就會連帶打壞一堆測試，即使底層「哪個任務完成了」的邏輯完全沒變。這種測試把「資料層的完成狀態」和「顯示層的呈現方式」耦合在一起，違反了既有測試風格（`list_tasks` 的測試都是斷言回傳值而非 print 輸出）。

**Why it happens:**
✓ 顯示是這次功能唯一「看得到」的部分，開發者很自然會想「寫個測試確保畫面有打勾」，於是直接對 `capsys` 捕捉的字串做斷言，卻沒有先把「完成狀態是否正確」和「畫面呈現是否正確」拆成兩層分別測試。

**How to avoid:**

- 沿用既有測試風格：核心函式（`complete_task`、`list_tasks`）的測試斷言「資料狀態」（例如某任務的 `completed` 欄位為 `True`），不涉及 print 輸出。
- 若需要驗證 ✓ 顯示邏輯，把它獨立成一個可測試的純函式（例如 `format_task_line(task) -> str`），對這個小函式做少量、專門的顯示格式測試，而不是對整個 `main()` loop 或 `_print_task_list` 做端對端字串比對。
- 只在少量（1-2 個）整合測試中驗證「畫面上确实出现 ✓」，避免每個行為測試都重複斷言顯示字串。

**Warning signs:**

- 測試檔案中出現大量 `capsys.readouterr().out == "固定字串"` 的斷言，且這些斷言涵蓋的是本應只測資料邏輯的函式。
- 只是調整顯示縮排或符號，就導致原本測「completed 狀態」的測試也跟著失敗。

**Phase to address:**
測試撰寫階段（`complete_task` 完成後、CLI 顯示整合前），建議在 plan 文件中明確分開「資料邏輯測試」與「顯示格式測試」兩類驗收標準。

---

### Pitfall 7: `list_tasks` 淺複製在資料結構改為可變物件後產生別名共享的靜默 bug

**What goes wrong:**
既有 `list_tasks` 用 `return list(tasks)`（淺複製），這在 `tasks: list[str]` 時完全安全，因為字串是不可變（immutable）物件——`test_list_tasks_returns_copy` 驗證的是「對回傳清單 `append`，不影響原清單」，這個測試在字串時代永遠會過。但一旦資料結構改成 `list[dict]` 或 `list[Task]`（dataclass，預設可變），淺複製只複製了「清單容器」本身，清單裡的每個元素仍然是**同一個物件參照**。如果呼叫端拿到 `list_tasks()` 的回傳值後修改某個任務的 `completed` 欄位（例如 `result[0]["completed"] = True` 或 `result[0].completed = True`），會直接污染原始的 `tasks`，而既有測試完全不會抓到這個 regression，因為它只測了「加一筆」不會影響原清單，沒測「改一筆已存在項目的欄位」會不會外洩。

**Why it happens:**
這是 Python 淺複製（shallow copy）的經典陷阱，字串的不可變性長期掩蓋了這個問題，資料結構遷移時如果沒有重新檢視 `list_tasks` 的複製語意，這個 bug 會在改資料結構的當下被引入卻不會被既有測試發現（既有測試綠燈 ≠ 沒有這個 bug）。

**How to avoid:**

- 資料結構一旦改為 dict 或 dataclass，`list_tasks` 需要改成深複製（`copy.deepcopy(tasks)`）或至少對每個元素做淺複製（例如 `[dict(t) for t in tasks]` 或 `[dataclasses.replace(t) for t in tasks]`），視乎「完成狀態」是否為巢狀結構決定要多深。
- 新增一個明確測試「防禦別名污染」：從 `list_tasks` 拿到回傳值後，修改回傳值中某個任務的欄位（而非新增/刪除元素），斷言原始 `tasks` 不受影響。這個測試在字串時代不需要，但改資料結構後必須補上。

**Warning signs:**

- Code review 時發現 `list_tasks` 的實作沒有跟著資料結構變更而調整複製深度。
- 手動測試流程：`list` 一次拿到清單、修改該清單裡某個項目的欄位、再 `list` 一次，發現原始資料被意外改動。

**Phase to address:**
資料結構設計階段（決定新結構後，`list_tasks` 的複製語意必須重新審視，屬於「連鎖影響既有函式」的一部分）。

---

### Pitfall 8: 對已完成任務重複 complete 的冪等性處理容易做錯

**What goes wrong:**
PROJECT.md 明確要求「對已完成的任務再次 complete 時，回報『已經完成過』（不報錯、不改變狀態）」。這聽起來簡單，但常見的錯誤實作方式包括：(a) 用跟 `delete_task` 一樣的布林回傳值（`True`/`False`）代表「成功/找不到」，卻沒有第三種狀態表示「找到了但已經是完成狀態」，導致 CLI 層無法區分「任務不存在」和「任務已完成」兩種情況並給出不同訊息；(b) 誤把「已完成」視為錯誤而拋出例外（跟 `add_task` 對空字串拋 `ValueError` 的模式搞混），導致 CLI 需要額外的 `try/except` 分支，且與規格「不報錯」矛盾；(c) 用「找到就無條件設為 True」的寫法，雖然結果上沒有問題（狀態确实没变化，因为本来就是 True），但如果未來 completed 帶有「完成時間戳記」等衍生欄位，這種無條件覆寫會不小心更新時間戳記，違反「不改變狀態」的字面意思。

**Why it happens:**
既有的兩個「操作型」函式（`add_task` 用例外、`delete_task` 用布林值）建立了兩種不同的錯誤回報慣例，`complete_task` 需要表達三種結果（成功完成 / 找不到 / 已完成過），比既有函式的二元結果更複雜，開發者若不先想清楚回傳值設計，很容易套用其中一種既有模式硬塞進三態情境裡。

**How to avoid:**

- 明確設計 `complete_task` 的回傳值以區分三種狀態，例如回傳一個列舉/字串常數（`"completed"` / `"not_found"` / `"already_completed"`）或用兩個獨立的布林/回傳碼，讓 CLI 層可以分別印出「已標記完成」「找不到任務」「已經完成過」三種不同訊息，而不是只能判斷 True/False 兩種。
- 撰寫測試明確涵蓋三態：(1) 對未完成任務 complete → 狀態變更且回傳「成功」；(2) 對不存在任務 complete → 回傳「找不到」且清單不變；(3) 對已完成任務再次 complete → 回傳「已完成過」且清單完全不變（包含任何衍生欄位都不能被覆寫）。
- 若日後新增「完成時間」等欄位，第 3 種情境的測試要特別斷言該欄位沒有被覆寫，而不是只斷言 `completed` 仍是 `True`。

**Warning signs:**

- `complete_task` 的回傳型別是單純的布林值，CLI 層無法用它區分「找不到」與「已完成過」兩種截然不同的使用者訊息。
- 測試只涵蓋「complete 一次成功」與「complete 不存在的任務」，缺少「對已完成任務再次 complete」的測試案例。

**Phase to address:**
`complete_task` 核心邏輯實作階段，應與 Pitfall 2（重複名稱歧義）一併設計，因為兩者都牽涉到「找到符合名稱的項目後要如何篩選/回應」。

---

## Technical Debt Patterns

| Shortcut | Immediate Benefit | Long-term Cost | When Acceptable |
| ---------- | ------------------- | ----------------- | ------------------ |
| 用 `dict`（如 `{"name": ..., "completed": ...}`）取代 dataclass 儲存任務 | 不需定義新型別、改動最小 | 沒有型別檢查與屬性存取提示，容易打錯 key（如 `"complete"` vs `"completed"`）且 IDE 無法提示 | 僅限本次極簡學習用練習；若專案要繼續擴充欄位（優先級、到期日）應盡早換成 dataclass |
| `complete_task` 直接用線性掃描 `for t in tasks: if t["name"] == name` | 實作快、跟 `delete_task` 風格一致 | 名稱重複時行為不確定（見 Pitfall 2）；任務量大時是 O(n) | 目前規模（in-memory、學習用途）可接受；若未來要支援大量任務或依 id 查找，應引入索引或改用 id 為主鍵 |
| 顯示層 `✓`/未顯示 直接寫死在 `_print_task_list` 字串組裝中 | 改動範圍小 | 顯示格式與資料邏輯耦合，未來要支援其他呈現方式（如 JSON 輸出）需要重新拆分 | 可接受，只要抽出獨立的 `format_task_line` 函式降低未來拆分成本 |

## UX Pitfalls

| Pitfall | User Impact | Better Approach |
| --------- | ------------- | ------------------ |
| `complete` 與 `delete` 指令名稱都用「依名稱」且輸出訊息措辭相近（如都印「已完成：X」「已刪除：X」） | 使用者快速輸入時容易誤觸錯誤指令且不易察覺後果差異（delete 不可逆） | 訊息措辭刻意區分（例如「已標記完成：X（清單中保留）」vs「已刪除：X（無法復原）」），必要時可在 delete 前追加確認語句 |
| 對已完成任務重複 `complete` 只印一行提示、無明顯視覺差異 | 使用者可能誤以為指令沒反應而重複嘗試 | 提示文字明確說明目前狀態（例如「X 已經是完成狀態，無需重複標記」） |
| `list` 顯示 ✓ 但未顯示「總計 N 筆，M 筆已完成」等摘要 | 任務多時使用者難以一眼掌握完成進度 | 可在 `_print_task_list` 底部加一行簡短摘要（屬於低風險的小增量，非 Out of Scope） |

## "Looks Done But Isn't" Checklist

- [ ] **complete_task 對重複名稱的行為**：不能只用「清單裡剛好沒有重複名稱」的測試資料驗收，必須專門測過重複名稱情境（Pitfall 2）。
- [ ] **✓ 顯示的編碼相容性**：不能只在 UTF-8 終端機/pytest 下驗證過，必須確認在未設 `PYTHONUTF8=1` 的原生 Windows 主控台不會 `UnicodeEncodeError` 崩潰（Pitfall 3）。
- [ ] **既有 12 個測試綠燈**：不能只看 `pytest` 全綠就結案，要抽查每個被修改的斷言是否仍驗證原本的行為契約（順序、去空白、副本語意），而非被動改型別交差（Pitfall 1）。
- [ ] **list_tasks 回傳值的隔離性**：不能只驗證「新增/刪除不影響原清單」，還要驗證「修改回傳清單中既有項目的欄位」不會污染原始資料（Pitfall 7）。
- [ ] **對已完成任務重複 complete**：不能只驗證「不報錯」，還要驗證清單狀態（包含任何衍生欄位）完全沒有變化（Pitfall 8）。
- [ ] **Out of Scope 沒有被悄悄實作**：檢查最終 diff 沒有出現 undo/toggle/持久化/依編號操作相關程式碼（Pitfall 5）。

## Recovery Strategies

| Pitfall | Recovery Cost | Recovery Steps |
| --------- | ---------------- | ----------------- |
| 資料結構變更打破既有測試（Pitfall 1） | LOW | 逐一檢視失敗測試，改為透過函式行為斷言而非直接比較內部結構；不需重寫邏輯，只需調整斷言方式 |
| 重複名稱歧義（Pitfall 2） | MEDIUM | 若已上線發現歧義，需要額外討論是否要引入唯一 id（可能牽動 delete_task 介面），屬於範圍變更，建議先與使用者確認是否接受名稱唯一的新約束 |
| cp950 UnicodeEncodeError（Pitfall 3） | LOW | 加上 `sys.stdout.reconfigure(encoding="utf-8", errors="replace")` 或改用 ASCII 替代符號（如 `[x]`），屬於小範圍修補 |
| list_tasks 別名污染（Pitfall 7） | LOW | 改 `list_tasks` 為深複製或逐元素複製，補上對應測試即可，不影響其他函式 |
| 冪等性處理錯誤（Pitfall 8） | MEDIUM | 需要重新設計 `complete_task` 回傳值型別，可能牽動呼叫端（CLI 層）的判斷邏輯，建議連同 CLI 訊息一起修正並補測試 |

## Pitfall-to-Phase Mapping

| Pitfall | Prevention Phase | Verification |
| --------- | -------------------- | ---------------- |
| Pitfall 1（既有測試斷言耦合資料結構） | 資料結構設計 / 測試遷移階段 | 12 個既有測試全數通過，且逐一確認修改後仍驗證原始行為契約而非僅型別相符 |
| Pitfall 2（重複名稱完成歧義） | complete_task 核心邏輯實作階段 | 新增涵蓋「兩筆同名任務（一完成一未完成）」的測試案例並通過 |
| Pitfall 3（cp950 Unicode 崩潰） | CLI 顯示層整合階段 | 在未設 PYTHONUTF8=1 的原生 Windows 終端機手動執行一次 `list` 顯示已完成任務，確認不崩潰 |
| Pitfall 4（complete/delete 語意混淆） | complete_task 核心邏輯實作階段 | 測試斷言 complete 前後清單長度、順序不變；CLI 說明文字更新為「標記完成」措辭 |
| Pitfall 5（範圍蔓延） | 需求確認 / plan 階段 + code review | 最終 diff 檢查無 undo/toggle/持久化/依編號操作相關程式碼 |
| Pitfall 6（測試斷言耦合顯示表示法） | 測試撰寫階段 | 資料邏輯測試（completed 欄位）與顯示格式測試（✓ 字元）分開撰寫，各自獨立驗證 |
| Pitfall 7（list_tasks 別名污染） | 資料結構設計階段 | 新增「修改回傳清單中既有項目欄位不影響原始資料」的測試並通過 |
| Pitfall 8（冪等性處理錯誤） | complete_task 核心邏輯實作階段 | 涵蓋成功/找不到/已完成過三態的測試皆通過，且已完成過情境斷言清單完全無變化 |

## Sources

- `app.py`（本專案現有原始碼，2026-07-23 讀取）— `add_task` / `list_tasks` / `delete_task` / `_print_task_list` / `main` 的實際實作與既有慣例（例外 vs 布林回傳、依名稱操作、只動第一筆符合項）。
- `test_app.py`（本專案現有測試套件，12 個測試）— 既有斷言風格（直接比較 `tasks == [...]`、`list_tasks` 副本驗證、`delete` 只刪第一筆的既有驗證）。
- `.planning/PROJECT.md`（2026-07-23）— Active/Out of Scope 需求、Key Decisions、Constraints（PYTHONUTF8、既有測試相容性要求）。
- Python 官方文件（`copy` 模組淺複製 vs 深複製語意；`str.encode` 編碼錯誤處理）— 一般 Python 語言行為知識，屬於 MEDIUM confidence 的背景知識，非本次額外檢索驗證，但與程式碼觀察一致。

---
*Pitfalls research for: Python in-memory todo CLI — 新增 completion 狀態的資料結構遷移*
*Researched: 2026-07-23*
