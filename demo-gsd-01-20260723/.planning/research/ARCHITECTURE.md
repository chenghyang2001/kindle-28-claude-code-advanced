# Architecture Research

**Domain:** 單檔 Python in-memory 待辦清單 CLI（functional core / imperative shell）— 新增「完成任務」功能的資料結構遷移
**Researched:** 2026-07-23
**Confidence:** HIGH（純 Python 語言語意分析 + 既有 codebase 直接檢視，無需外部函式庫佐證）

## 現況摘要（來自 `.planning/codebase/ARCHITECTURE.md` 與 `app.py`）

- 單檔 `app.py`，`tasks: list[str]` 是唯一狀態，存活於 `main()` 的區域變數。
- 三個核心函式一律以 `tasks` 為第一參數（顯式傳遞，非全域變數）：
  - `add_task(tasks: list, name: str) -> None`（就地 `append`，驗證空字串拋 `ValueError`）
  - `list_tasks(tasks: list) -> list`（回傳淺複製，不洩漏內部參照）
  - `delete_task(tasks: list, name: str) -> bool`（`name in tasks` 判斷存在、`tasks.remove(name)` 就地刪除第一筆符合者）
- `_print_task_list(tasks: list) -> None` 直接 `print(f"  {idx}. {task}")`，`task` 目前就是字串本身。
- 既有 12 個 pytest 測試全部以「字串等值比較」斷言（如 `assert tasks == ["買牛奶"]`），這是本次遷移最大的相容性壓力來源。
- 核心語意張力：**純字串無法攜帶「已完成」旗標**，這是本次功能唯一無法迴避的資料結構決策點。

## 五種方案比較

| 方案 | `tasks` 型別 | complete 語意 | 對既有三函式的衝擊 | 對 12 個既有測試的衝擊 | 判定 |
| --- | --- | --- | --- | --- | --- |
| (a) list of dict | `list[dict]` | 找到 dict、設 `d["done"] = True` | `add_task` 內部改為 append dict；`delete_task` 的 `name in tasks` / `tasks.remove(name)` 必須改寫為以 `t["name"]` 比對 | 全部 12 個斷言要從 `"買牛奶"` 改成 `{"name": "買牛奶", "done": False}` | 可行，但可讀性與型別安全皆遜於 dataclass |
| (b) dataclass `Task` | `list[Task]` | 找到 `Task`、`.done = True`（就地變動屬性） | 同上：`add_task` append `Task(...)`；`delete_task` 內部比對邏輯必須改寫 | 12 個斷言改成 `Task("買牛奶")`（`done` 有預設值 `False`，靠 dataclass 自動產生的 `__eq__` 幾乎是機械式替換） | **推薦** |
| (c) `NamedTuple` `Task` | `list[Task]`（元素不可變） | 找到 index，`tasks[i] = tasks[i]._replace(done=True)` | 同 (b)，但 complete 操作無法直接 `.done = True`，需改走替換整個 tuple 的寫法 | 斷言可寫成 `Task("買牛奶")`（NamedTuple 也支援位置/具名建構與 `__eq__`），但「不可變元素＋外部用替換」與既有「串列本身可變、直接就地修改」的風格不一致 | 可行，但對教學示範而言引入不必要的心智負擔 |
| (d) 平行 `completed: set[str]`（依名稱） | `list[str]` **完全不變** | `name` 加入 `completed` 集合，`list_tasks`/render 時查表 | **零衝擊**：`add_task` / `list_tasks` / `delete_task` 簽名與內部邏輯完全不用改 | **零衝擊**：12 個既有測試原封不動全綠 | **表面最省事，但有正確性缺陷（見下）** |
| (e) 字串前綴標記（如 `"[x] 買牛奶"`） | `list[str]`（內容語意改變） | 找到字串、替換為加前綴版本 | `delete_task` 的精確比對 `name in tasks` 會找不到已完成任務（因為清單裡實際存的是 `"[x] 買牛奶"` 而非 `"買牛奶"`），**必須修改 `delete_task`** | 表面上型別仍是 `list[str]`，未完成任務的斷言不變，但這只是假象——一旦任務完成後被刪除的路徑就壞了 | **淘汰**：直接違反 PROJECT.md 明訂的「delete_task 本次不動」限制 |

### 為何 (d) 平行 completed-set 看似最省事，實際上有語意漏洞

`test_delete_only_first_occurrence` 這個既有測試已經證明**重複名稱的任務是被支援的合法情境**（`tasks = ["任務A", "任務A"]`）。如果完成狀態改用「依名稱」的集合來記錄，一旦使用者有兩筆同名任務、只完成其中一筆，`completed` 集合裡記的是名稱字串本身，**無法區分是哪一個實例完成**——結果會讓兩筆同名任務同時被畫上 ✓，即使使用者只 complete 了一筆。這是與既有測試證明的行為（支援重複名稱）直接衝突的正確性缺陷，不是次要瑕疵。另外，`delete_task` 刪除某個同名任務後，`completed` 集合裡的殘留名稱不會同步清除，長期會累積成 stale 狀態（危害較小，但屬於「兩份狀態互相脫節」的架構味道）。

### 為何字串前綴 hack 直接淘汰

PROJECT.md Out of Scope 明訂「修改 delete 行為 — delete_task 已存在且有測試,本次不動」。前綴 hack 一旦任務被標記完成，字串內容就變成 `"[x] 買牛奶"`，但 `delete_task` 目前用精確字串比對（`name in tasks`），使用者輸入 `delete 買牛奶` 會比對失敗、回報「找不到任務」——即使任務明明還在清單上。要修就必須讓 `delete_task` 也懂得剝離標記再比對，這正是「不動 delete_task」這條限制明確禁止的路。此外這個方案把「顯示格式」與「資料模型」混為一談，是需要事後用字串解析取狀態的反樣式（anti-pattern），不建議採用。

## 推薦方案：`dataclass Task`

```python
from dataclasses import dataclass

@dataclass
class Task:
    name: str
    done: bool = False
```

**為何選這個而非 dict／NamedTuple：**

1. **與既有「functional core, imperative shell」風格一致**：`Task` 是純值物件，`tasks` 依然是扁平串列（只是元素從 `str` 換成 `Task`），三個核心函式繼續維持「接收 `tasks` 作為第一參數、就地變動或回傳複製」的既有模式，不需要引入 class 持有狀態、不需要全域變數。
2. **測試遷移幾乎是機械式替換**：dataclass 自動產生的 `__eq__` 會逐欄位比較，且 `done` 有預設值 `False`，所以既有斷言 `assert tasks == ["買牛奶"]` 只需要改成 `assert tasks == [Task("買牛奶")]`——這是一次全域「字串常值換成建構式呼叫」的機械改法，不需要重新設計斷言邏輯。這比 dict 版本的 `{"name": "買牛奶", "done": False}` 更精簡、比 NamedTuple 更貼近「這是一個有名字的物件」的直覺。
3. **屬性存取比 dict 鍵值更安全**：`task.name` / `task.done` 打錯字會被大多數編輯器/型別檢查器抓到；`task["nam"]`（dict 誤植鍵名）在執行前不會被發現，教學情境下更容易讓學習者踩坑。
4. **complete_task 的變動語意與既有風格一致**：`add_task`／`delete_task` 目前都是「就地變動傳入的串列」，dataclass 預設可變（非 `frozen`），`complete_task` 可以直接 `matched_task.done = True` 做屬性層級的就地變動，語意上與既有的「就地修改」慣例一致。NamedTuple 因為不可變，必須改成「找 index、用 `_replace()` 產生新物件、寫回原位置」，這種「元素不可變但容器可變」的混合心智模型，對這個刻意保持極簡的教學專案來說是不必要的複雜度。
5. **零第三方依賴**：`dataclasses` 是標準庫，符合 PROJECT.md 「無框架、無第三方依賴，維持極簡」的限制。

**已知取捨（誠實揭露）：**

- `list_tasks` 的淺複製（`list(tasks)`）在字串時代是完全安全的（字串不可變，複製後兩邊互不影響）。改成 `list[Task]` 後，淺複製的串列雖然是新物件，但**串列裡的 `Task` 實例仍是同一個參照**——如果呼叫端拿到 `list_tasks()` 的回傳值後去改 `result[0].done = True`，會連帶改到 `main()` 內部真正的 `tasks`。現有 12 個測試沒有任何一個做這種操作（`test_list_tasks_returns_copy` 只測試 `append` 到複製出來的串列，不涉及改動元素屬性），所以既有測試仍會全�oreo green，但這是新引入的、值得在 code review 時留意的細節，非本次必須解決但應該記錄在案。
- dataclass 預設 `__repr__` 會印出 `Task(name='買牛奶', done=False)`，比原始字串略長，若未來要在錯誤訊息中直接印出任務物件（如 `f"找不到任務：{name!r}"`，注意這裡印的是使用者輸入的 `name` 字串而非 `Task`，所以不受影響），需要留意呼叫端印的是 `.name` 屬性還是整個物件。

## Ripple Effect 總表（對既有元件的具體衝擊）

| 元件 | 現況 | 遷移後 | 衝擊等級 |
| --- | --- | --- | --- |
| `add_task(tasks, name)` | `tasks.append(name.strip())` | `tasks.append(Task(name=name.strip()))` | 低：簽名不變，僅內部一行改動；驗證邏輯（空字串拋錯）完全不動 |
| `list_tasks(tasks)` | `return list(tasks)` | 不變（仍是 `return list(tasks)`），但語意上變成複製「Task 參照的淺層串列」 | 極低：程式碼零改動，僅需在文件註記淺複製的新限制（見上） |
| `delete_task(tasks, name)` | `if name in tasks: tasks.remove(name); return True` | 必須改寫為依 `.name` 屬性尋找、移除對應 `Task` 物件（例：`next((t for t in tasks if t.name == name), None)` 後 `tasks.remove(t)`） | **高**：這是唯一一個「簽名不變、但內部邏輯必須整段重寫」的既有函式——原本的 `in` / `remove` 是靠字串直接相等比較，換成 `Task` 物件後這兩個運算子都會失效（`name in tasks` 恆為 `False`，因為找不到與裸字串相等的 `Task`），若遺漏這步會讓 `delete_task` 徹底失靈且不會立刻報錯 |
| `_print_task_list(tasks)` | `print(f"  {idx}. {task}")` | `print(f"  {idx}. {'✓ ' if task.done else '  '}{task.name}")`（或等效格式） | 中：純呈現層改動，不影響資料，但需要新增測試/手動驗證輸出格式含 ✓ |
| `complete_task(tasks, name)`（新函式） | 不存在 | 依名稱找 `Task`：不存在回報「找不到」、已完成回報「已經完成過」、否則設 `.done = True` 並回報成功——**三種結果無法用單一 `bool` 表達**，建議回傳字串狀態碼或簡單的三態（例如 `"completed"` / `"not_found"` / `"already_done"`），CLI 層再依此印對應訊息 | 新增：需要與 `delete_task` 的「回傳 bool」慣例不同的回傳型態設計，這是本次唯一真正的新 API 設計決策 |
| `main()` CLI dispatch | 支援 `add` / `list` / `delete` / `quit` | 新增 `elif cmd == "complete":` 分支，解析 `complete <名稱>`，依 `complete_task` 三態回傳印出對應訊息 | 中：純新增分支，不動既有分支 |
| 12 個既有 pytest 斷言 | `assert tasks == ["買牛奶"]` 等字串等值比較 | 改為 `assert tasks == [Task("買牛奶")]`（靠 dataclass 自動 `__eq__` + `done` 預設值，幾乎是機械式替換） | 中：**全部 12 個測試都要動**，但屬於「調整斷言、不改變行為語意」的允許範圍（PROJECT.md Constraints 明訂） |

## 建議建置順序（Build Order）

依相依關係排序，每一步完成後應可獨立驗證：

1. **定義 `Task` dataclass**（`name: str`, `done: bool = False`）——這是所有後續步驟的基礎，必須最先完成。
2. **改寫 `add_task` 內部邏輯**，改為 append `Task` 實例而非裸字串。此時既有測試會立即全部變紅（型別不符），這是預期中的過渡狀態。
3. **改寫 `delete_task` 內部比對邏輯**，改用 `.name` 屬性尋找與移除對應的 `Task` 物件。這一步是整個遷移中風險最高的部分，因為 `in` / `remove` 這兩個既有運算子換了資料型別後會靜默失效（不拋例外、只是永遠回傳 `False`／找不到），務必搭配步驟 6 的測試立即驗證。
4. **確認 `list_tasks` 行為**（程式碼可能零改動，但要跑一次既有測試確認淺複製語意仍成立）。
5. **改寫 `_print_task_list`**，讀取 `.name` / `.done` 並加上 ✓ 標記。
6. **同步遷移全部 12 個既有測試斷言**（字串常值 → `Task(...)` 建構式）——這一步必須緊接在步驟 2-3 之後完成，目的是讓既有測試套件重新變綠，在新增任何功能程式碼之前先確保回歸安全網完整，避免新舊改動疊加導致除錯困難。
7. **實作 `complete_task(tasks, name)` 新函式**，依賴步驟 1 的 `Task.done` 欄位；決定三態回傳設計（找不到／已完成過／成功）。
8. **在 `main()` CLI dispatch 新增 `complete` 指令分支**，依賴步驟 7 的回傳值印出對應訊息。
9. **新增 `TestCompleteTask` 測試類別**（延續既有 `TestAddTask`/`TestListTasks`/`TestDeleteTask` 的分類風格），至少涵蓋：成功完成、找不到任務、對已完成任務再次 complete、（建議額外納入）對重複名稱任務呼叫 complete 的行為。
10. **互動式 REPL 手動驗證**：跑 `python app.py`（Windows 記得 `PYTHONUTF8=1`），實際輸入 `add` → `complete` → `list` 確認 ✓ 顯示正確、`delete` 仍正常運作。

## 未解的邊界案例（留待 roadmap / plan-phase 決定）

PROJECT.md 目前只規範「對已完成的任務再次 complete 時回報已經完成過」，但**沒有明確定義重複名稱任務與 complete 的交互行為**：若清單上有兩筆同名任務、其中一筆已完成，使用者再次 `complete <該名稱>` 時，應該：

- (i) 依照 `delete_task` 現有的「只動第一筆符合者」慣例，找到第一筆**尚未完成**的同名任務完成之，還是
- (ii) 只要名稱存在且該名稱的第一筆符合項目已完成，就直接回報「已經完成過」（即使還有另一筆同名任務尚未完成）？

這個決策會影響 `complete_task` 內部的搜尋邏輯（是否要跳過已完成的、找下一個同名的），建議在 plan-phase 明確拍板，並補一則測試案例固化行為，避免實作時隨意假設。

## 元件邊界圖（遷移後）

```
┌─────────────────────────────────────────────────────────────┐
│                     Interactive CLI Loop                     │
│                  `app.py::main()`                             │
├──────────────┬──────────────┬──────────────┬────────────────┤
│  add command │ list command │ delete cmd   │ complete cmd（新）│
└──────┬───────┴──────┬───────┴──────┬───────┴────────┬───────┘
       ▼               ▼              ▼                 ▼
┌─────────────────────────────────────────────────────────────┐
│                    Core Function Layer                        │
│  add_task()  /  list_tasks()  /  delete_task()  /             │
│              complete_task()（新，依賴 Task.done）              │
└──────┬──────────────────────────────────────────────────────┘
       ▼
┌─────────────────────────────────────────────────────────────┐
│         In-memory `tasks: list[Task]`（main() 區域變數）        │
│         Task(name: str, done: bool = False) —— dataclass       │
│         No persistence — state 在 process 結束後消失            │
└─────────────────────────────────────────────────────────────┘
```

**通訊邊界不變**：CLI 層仍是唯一持有 `tasks` 狀態的地方、唯一呼叫核心函式的地方；核心函式之間彼此不互相呼叫（`complete_task` 不會呼叫 `delete_task` 或 `add_task`）；`Task` 是純資料物件，不含任何行為方法（no methods），保持與既有「無 class 持有狀態」精神一致——`Task` 只是取代 `str` 作為串列元素型別，不是引入物件導向的狀態容器。

## Anti-Patterns to Avoid

### Anti-Pattern 1：把「已完成」狀態存在字串格式裡（選項 e）

**What people do:** 用前綴／後綴標記（如 `"[x] "` 或 `" (done)"`）把狀態編碼進顯示字串本身。
**Why it's wrong:** 資料模型與呈現格式混為一談；任何需要依原始名稱做精確比對的既有邏輯（本例即 `delete_task`）會因為字串內容被動態改寫而比對失敗，且這類 bug 通常是「找不到任務」這種容易被誤判成別的原因（使用者輸入錯誤）的靜默失敗，難以除錯。
**Instead:** 用結構化型別（dataclass／dict／NamedTuple）把「名稱」與「狀態」拆成獨立欄位，顯示邏輯只在 `_print_task_list` 這個單一呈現層組字串，資料層本身不含格式標記。

### Anti-Pattern 2：用名稱字串當唯一鍵值來關聯狀態（選項 d 的陷阱）

**What people do:** 為了避免改動既有函式簽名，另開一個「依名稱查狀態」的平行資料結構（如 `completed: set[str]`）。
**Why it's wrong:** 當系統已經明確支援重複名稱（本例 `test_delete_only_first_occurrence` 證實），依名稱查詢的平行狀態無法區分同名的不同實例，會導致「完成其中一筆卻連帶影響另一筆」的正確性錯誤；此外兩份狀態（`tasks` 與 `completed`）分開存在，天生就有互相脫節（desync）的風險，例如刪除任務後另一份狀態沒有同步清理。
**Instead:** 讓「done」狀態直接附著在任務本身的資料結構上（如 `Task.done`），使狀態與其擁有者物理上綁定，天然避免多實例混淆與雙重狀態脫節的問題。

## Sources

- 直接檢視本專案既有原始碼：`app.py`、`test_app.py`、`.planning/codebase/ARCHITECTURE.md`、`.planning/PROJECT.md`（2026-07-23）
- Python 標準庫語意（`dataclasses`、`typing.NamedTuple`、`list`/`set` 就地變動與淺複製行為）為 CPython 官方文件記載之穩定語言特性，不受版本波動影響，故標記 HIGH confidence，無需額外外部查證。

---
*Architecture research for: Python in-memory todo CLI — completion-state migration*
*Researched: 2026-07-23*
