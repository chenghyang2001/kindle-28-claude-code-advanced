# Feature Research

**Domain:** 待辦清單 CLI（in-memory、互動式 REPL）— 完成任務功能
**Researched:** 2026-07-23
**Confidence:** MEDIUM

> 本研究聚焦「任務完成（complete）」這個功能面向，對照 todo.txt / todo.txt-cli、Taskwarrior、Ultralist、dstask 等主流 CLI 待辦工具的實際做法，找出 table stakes、差異化空間、以及該刻意排除的功能。PROJECT.md 已有明確決策（依名稱完成、✓ 留在清單上、v1 不做 undo、重複 complete 給友善訊息），本文件驗證這些決策是否符合生態系慣例，並補充決策時未覆蓋的邊界情境。

## Feature Landscape

### Table Stakes (Users Expect These)

使用者一旦看到「完成」這個概念存在，就會預期以下行為存在，缺了會覺得功能不完整或不一致。

| Feature | Why Expected | Complexity | Notes |
| --------- | -------------- | ------------ | ------- |
| 用一個明確指令標記任務為完成（如 `complete <名稱>`） | 所有主流待辦 CLI（todo.txt `do`、Taskwarrior `done`、Ultralist `complete`）都有對應動詞指令；使用者已從 `add`/`delete` 建立「動詞 + 目標」的心智模型 | LOW | 專案已決定依名稱指定，與既有 `delete <名稱>` 介面一致，符合 todo.txt-cli 的慣例（也是依描述比對，非強制數字 ID） |
| 清單上要看得出哪些任務已完成（視覺標記） | todo.txt 用 `x` 前綴、Taskwarrior 用狀態欄位、Ultralist 用 `[x]`；沒有標記使用者無法信任「完成」真的生效 | LOW | 專案決定用 ✓ 標記於 `list` 輸出，符合此慣例；純文字終端機常見做法，不需要顏色或特殊字元集也能達成 |
| 完成後任務預設**不會消失**（除非明確要求隱藏/歸檔） | todo.txt 與 Ultralist 都是「完成後仍留在檔案/清單中」，只是視覺上標記，這樣使用者才能看到「今天做了什麼」帶來的成就感 | LOW | 專案決定「留在清單上打勾」與 todo.txt/Ultralist 一致；**與 Taskwarrior 相反**（Taskwarrior 的 `list`/`next` 報表預設 `status:pending`，完成後會從預設視圖消失，要用 `task all` 或 `task completed` 才看得到）— 本專案選擇的是「所見即所有」的簡單模型，適合單檔學習型 CLI |
| 對不存在的任務名稱 complete 時要有清楚錯誤訊息 | 與 `delete_task` 找不到任務時的行為一致；使用者已建立「操作不存在的任務會被告知」的預期 | LOW | 專案已決定沿用「找不到任務」訊息風格，維持介面一致性 |
| 完成與刪除是兩個獨立概念，不可混用語意 | 所有工具都嚴格區分「完成」（狀態改變）與「刪除」（資料移除）；混為一談會讓使用者無法區分「做完了」跟「不要了」 | LOW | 專案 Core Value 明確指出「完成狀態必須正確保存與呈現，不能跟刪除混為一談」，與生態系慣例完全一致 |
| `delete` 對已完成的任務仍然要能刪除 | Taskwarrior、todo.txt、Ultralist 皆允許刪除已完成項目（例如清掉舊的已完成任務）；沒有理由因為任務完成就鎖死不能刪 | LOW | PROJECT.md 未明文提及此互動，屬於「complete 與 delete 的互動」這個 Active 需求項目下的隱含子案例，**建議在需求定義階段明確寫下**：`delete_task` 不應檢查完成狀態，對已完成任務一樣可刪除 |

### Differentiators (Competitive Advantage)

本專案是極簡學習型 in-memory CLI，差異化空間本來就小；以下是「在既有決策範圍內，值得刻意做好、能提升體驗」的項目，而非競爭產品意義下的差異化。

| Feature | Value Proposition | Complexity | Notes |
| --------- | ------------------- | ------------ | ------- |
| 重複 complete 給友善訊息而非報錯或靜默 | 多數成熟工具在這個邊界情境上其實處理得不優雅：Taskwarrior 因為完成後任務會從可定址的 ID 空間消失，反而**迴避**了這個問題（你幾乎不會對著已完成任務再下一次 `done`）；本專案選擇「依名稱、且完成任務仍可見」的模型，代表「使用者對著已完成任務再次 complete」是常態情境而非邊角案例，友善訊息（而非例外/報錯）是比多數工具更貼心的處理 | LOW | 這是本專案架構選擇（名稱定址 + 完成任務可見）自然帶來的體驗機會，值得在測試中明確覆蓋此情境 |
| 完成操作是「單向冪等」（idempotent，不改變已完成狀態、不報錯） | 對照「toggle 語意」（再按一次變回未完成）容易讓使用者誤觸；本專案明確選擇非 toggle，降低誤操作風險，是刻意的簡化設計，值得在文件/说明中说明原因 | LOW | 與 PROJECT.md Key Decisions 一致：「toggle 語意容易誤觸」 |
| 一致的「依名稱」定址模型貫穿 add / delete / complete | 多數工具（Taskwarrior、dstask）用數字 ID 或 UUID 定址，學習曲線較高；本專案全程用名稱字串，對初學者/單檔學習專案更直覺 | LOW | 已是既有架構決策的延伸，非新功能，但值得在 FEATURES 層面確認一致性：`complete_task` 的名稱比對規則（大小寫、去頭尾空白）應與 `delete_task` 完全一致，否則會出現「delete 找得到但 complete 找不到」的不一致 bug |

### Anti-Features (Commonly Requested, Often Problematic)

以下是待辦 CLI 生態系中常見、但主流工具也提醒要謹慎（或本專案已明確排除）的功能。

| Feature | Why Requested | Why Problematic | Alternative |
| --------- | --------------- | ------------------ | ------------- |
| 取消完成 / undo（uncomplete） | 使用者難免手滑點錯任務；todo.txt 使用者常見做法是手動刪掉 `x` 前綴，Taskwarrior 也無原生 `undone` 指令（需 `modify status:pending`），可見即使成熟工具也不把它當作一級功能 | 需要額外指令 + 額外狀態轉換路徑 + 測試覆蓋；在「單向完成」模型下引入 undo，會讓「重複 complete 給友善訊息」這條規則的角色變模糊（使用者可能預期 undo 而非再次 complete） | v1 明確排除（PROJECT.md 已決定）；未來若要做，建議獨立指令 `uncomplete <名稱>`，不要讓 `complete` 本身變成 toggle |
| 依編號操作（`complete 2`） | 數字比打完整名稱快，Taskwarrior/dstask 都用短數字 ID 提升操作效率 | 編號會隨清單增刪而變動（尤其是完成任務不移除、清單會越來越長），容易誤刪/誤完成到錯的任務；且會與現有 `delete <名稱>` 的定址方式不一致，增加雙軌介面的維護與學習成本 | 維持「依名稱」單一定址模型（已決策）；若未來清單很長導致名稱比對不便，可考慮之後加上「模糊搜尋/前綴比對」而非引入編號 |
| 過濾檢視（只看未完成 / 只看已完成） | Taskwarrior 預設就是「只顯示 pending」，是使用者很自然會問「那我可以只看沒做完的嗎」 | 需要新增指令或 `list` 的參數（如 `list --done` / `list --pending`），會擴大本次範圍（本次目標是让完成状态「可見」，不是做检视过滤器） | 不在本次範圍；`list` 維持顯示全部（帶 ✓ 標記），過濾功能留待未來里程碑視需求評估 |
| 完成時間戳記（completion date/timestamp） | todo.txt 標準格式本身內建完成日期（`x YYYY-MM-DD ...`），是相對常見的附加資訊 | 需要任務資料結構額外攜帶日期欄位、格式化輸出、時區/測試斷言的額外複雜度，超出本次「完成任務」核心範圍 | 不在本次範圍；PROJECT.md Out of Scope 已排除「優先級、到期日、分類等進階欄位」，時間戳記屬同一類延伸欄位，比照排除 |
| 持久化 / 跨重啟保存完成狀態 | 使用者自然會問「完成後關掉程式再開，還記得嗎」 | 現有系統是 in-memory，加持久化涉及檔案格式、序列化、錯誤處理，是完全不同量級的工作 | PROJECT.md Out of Scope 已明確排除，維持既有 in-memory 邊界 |
| 彩色終端輸出 / 進度條等視覺增強 | 讓 ✓ 更醒目、更有成就感 | 需要額外套件（如 `colorama`）或 ANSI escape 處理，違反「Python 3 標準庫 + pytest，維持極簡」的既有技術約束；且 Windows 終端機對 ANSI 支援不一致，會引入跨平台顯示風險 | 用純文字 ✓ 符號即可（已決策），不需顏色 |

## Feature Dependencies

```
資料結構支援「完成狀態」(str → dict/dataclass/其他)
    └──requires──> complete_task(tasks, 名稱) 函式
                       └──requires──> list 顯示 ✓ 標記
                       └──requires──> 重複 complete 的友善訊息（需先能讀出目前完成狀態）

complete_task 的名稱比對規則
    └──must-match──> delete_task 既有的名稱比對規則（大小寫/去頭尾空白一致）

delete_task（既有）
    ──unaffected-by──> 任務完成狀態（刪除不應檢查是否已完成）

12 個既有測試（斷言 tasks == ["買牛奶"] 這類字串比較）
    ──impacted-by──> 資料結構變更（str → dict 等）
                       └──requires──> 既有測試斷言方式同步調整（行為語意不可變，但斷言寫法要跟著資料結構改）
```

### Dependency Notes

- **資料結構變更是一切的前提**：`complete_task` 無法在純 `list[str]` 上實作（字串本身無法攜帶完成狀態），PROJECT.md 已標記為「核心設計決策，留待 discuss-phase / plan-phase 決定」。這是本次功能唯一的硬性前置依賴，順序上必須先定案資料結構，才能實作 `complete_task` 與 `list` 的 ✓ 顯示。
- **`complete_task` 與 `delete_task` 的比對規則必須一致**：若 `delete_task` 對名稱做了大小寫不敏感或去頭尾空白處理，`complete_task` 也要比照，否則會出現「同一個任務，delete 找得到、complete 找不到」的不一致體驗，這是本研究發現、PROJECT.md 未明文覆蓋的隱性依賴，建議在需求定義階段補上一條驗收準則。
- **重複 complete 的友善訊息，依賴「先能讀出目前完成狀態」**：這代表資料結構除了要能「設定」完成狀態，也要能「查詢」，兩者是同一個資料結構決策的一體兩面，不會是分開的工作項。
- **`delete_task` 不受完成狀態影響（衝突排除）**：這不是真正的功能衝突，而是要明確排除「complete 過的任務被 delete 特殊處理」這種誤讀 — 需求定義時應明寫「delete 對任何完成狀態的任務都一視同仁」，避免實作時誤加不必要的檢查。

## MVP Definition

### Launch With (v1)

PROJECT.md Active 需求已完整定義 v1 範圍，本研究確認以下都是必要項、且都在生態系的 table stakes 範圍內：

- [ ] `complete <名稱>` 標記任務完成 — table stakes，且介面風格需與 `delete` 一致
- [ ] `list` 顯示 ✓ 標記、已完成任務不從清單消失 — table stakes（todo.txt/Ultralist 模型）
- [ ] 對不存在任務 complete 時回報「找不到任務」— table stakes，與既有 delete 錯誤處理一致
- [ ] 重複 complete 已完成任務給友善訊息（不報錯、不改狀態）— 本專案架構下的合理選擇，且是本次的差異化亮點之一
- [ ] 既有 12 個測試維持綠燈 + complete 功能有對應新測試 — 相容性硬要求

### Add After Validation (v1.x)

不在本次 Active 範圍，但屬於「完成」概念自然的下一步延伸，待 v1 驗證「使用者真的需要用完成功能」後再評估：

- [ ] `uncomplete <名稱>`（取消完成，獨立指令而非 toggle）— 觸發時機：使用者反覆手滑誤完成、明確要求「復原」
- [ ] `list --pending` / `list --done` 過濾檢視 — 觸發時機：清單累積到一定長度、已完成項目開始造成視覺干擾

### Future Consideration (v2+)

延後到產品方向更明確後再考慮，目前不應投入設計成本：

- [ ] 完成時間戳記（何時完成）— 為何延後：需要額外欄位與格式化，且目前沒有「檢視完成歷史」的需求驅動
- [ ] 持久化（存檔/資料庫）— 為何延後：整個專案目前是 in-memory 學習範疇，持久化屬於完全不同的架構層級
- [ ] 依編號操作 — 為何延後：與既有「依名稱」介面衝突，除非未來證明名稱定址在大清單下體驗不佳，否則不應引入雙軌定址

## Feature Prioritization Matrix

| Feature | User Value | Implementation Cost | Priority |
| --------- | ------------ | --------------------- | ---------- |
| `complete <名稱>` 指令 | HIGH | MEDIUM（依賴資料結構變更） | P1 |
| `list` 顯示 ✓ 標記、完成項不移除 | HIGH | LOW（一旦資料結構到位） | P1 |
| 找不到任務的錯誤訊息 | MEDIUM | LOW | P1 |
| 重複 complete 友善訊息 | MEDIUM | LOW | P1 |
| 既有測試相容性調整 | HIGH（不做會回歸） | MEDIUM | P1 |
| `uncomplete` 取消完成 | MEDIUM | MEDIUM | P3（v1.x 之後） |
| 過濾檢視（pending/done） | LOW-MEDIUM | MEDIUM | P3 |
| 完成時間戳記 | LOW | MEDIUM | P3 |
| 持久化 | LOW（超出目前範疇） | HIGH | P3（v2+，且需重新評估專案定位） |

**Priority key:**

- P1: Must have for launch（本次里程碑必做）
- P2: Should have, add when possible（本次未觸及，暫無 P2 項目）
- P3: Nice to have, future consideration

## Competitor Feature Analysis

| Feature | todo.txt / todo.txt-cli | Taskwarrior | 本專案做法 |
| --------- | -------------------------- | ------------- | ------------ |
| 標記完成方式 | `x` 前綴（可選附完成日期，ISO 8601） | `task <id/filter> done`，狀態欄位 pending→completed | `complete <名稱>`，用內部完成旗標（非前綴字串），與既有 delete 介面一致 |
| 完成後清單顯示 | 預設仍在檔案中，多數前端（含 `ls`）會顯示已完成項目，除非另外歸檔到 done.txt | 預設 `list`/`next` 報表**隱藏**已完成任務（`status:pending` 過濾），要 `task all`/`task completed` 才看得到 | 完全比照 todo.txt 模型：`list` 顯示全部、✓ 標記已完成，不隱藏（使用者明確要求「一眼看到哪些做完了」） |
| 重複標記完成 | 手動編輯文字檔，重複加 `x` 前綴無意義也不太可能發生（人工編輯情境） | 因完成後任務從可定址 ID 空間移除，「對同一 ID 重複 done」情境實務上很少發生 | 因採「名稱 + 完成項可見」模型，此情境會常態發生，故明確設計「友善訊息、不報錯、不改狀態」 |
| 取消完成 | 需手動刪除 `x` 前綴（無原生指令） | 無原生 `undone`，需 `task <id> modify status:pending` | v1 不支援（決策一致：兩個工具都不把 undo 當一級功能） |
| 定址方式 | 依整行文字內容比對（部分關鍵字比對） | 數字 ID（短期）或 UUID（長期穩定） | 依名稱完整比對，與既有 `add`/`delete` 一致 |
| 刪除已完成任務 | 可以，直接刪除該行文字 | 可以，`task <id> delete` 不檢查完成狀態 | 應比照可以（PROJECT.md 未明文但應在需求中補上此驗收準則） |

## Sources

- [Todo.Txt format (GitHub, todotxt/todo.txt)](https://github.com/todotxt/todo.txt) — 完成標記語法（`x` 前綴 + ISO 8601 完成日期），MEDIUM confidence（WebSearch 摘要，未逐字查證官方 repo 全文）
- [Complete Todo.txt Syntax Guide (todotxt.in)](https://todotxt.in/blog/todo-txt-syntax-guide) — 補充完整語法範例
- [Taskwarrior — Done Command 官方文件](https://taskwarrior.org/docs/commands/done/) — `done` 指令行為
- [Taskwarrior — Filters 官方文件](https://taskwarrior.org/docs/filter/) — `list` 報表預設 `status:pending` 過濾規則說明，HIGH confidence（官方文件直接陳述）
- [Taskwarrior — List Report 官方文件](https://taskwarrior.org/docs/commands/list/)
- [Ultralist — Showing tasks 官方文件](https://ultralist.io/docs/cli/showing_tasks/) — `[x]` 完成標記顯示方式，MEDIUM confidence
- [dstask (GitHub, naggie/dstask)](https://github.com/naggie/dstask) — 作為 Taskwarrior 替代方案的背景認識，未深入查證完成行為細節，LOW confidence，僅供脈絡參考
- `.planning/PROJECT.md`（本專案）— 既有決策與 Out of Scope 範圍，作為比對基準

---
*Feature research for: 待辦清單 CLI 完成任務功能*
*Researched: 2026-07-23*
