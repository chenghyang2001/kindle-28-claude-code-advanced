# 練習 02 解答：為重複任務設計安全自主迴圈

> 實作：`ralph-demo/ralph.sh`＋`ralph-demo/PROMPT.md`；實跑紀錄：`ralph-demo/logs/`。
> 迴圈本體是 bash＋`claude -p --model haiku`（沒有安裝 Ralph，也不裝外掛版）。

## 任務 1：選定的重複任務與每輪輸入／輸出

**重複任務**：「照 TASK.md 清單，一次實作一個小函式並補上 pytest 測試」。新增工具函式、補測試、改小 bug 這類工作每週都會重複，清單式又容易驗證，很適合交給迴圈。

| | 內容 | 誰負責 |
| --- | --- | --- |
| **輸入** | `TASK.md`（`- [ ]` 清單）＋`PROMPT.md`（固定規則）＋目前的 `src/`、`tests/` | 人準備 TASK.md；迴圈每輪餵同一份 PROMPT |
| **Claude 這輪做的事** | 只挑「第一個」`- [ ]` → 寫實作到 `src/` → 寫新測試檔 → 該項改 `- [x]` | `claude -p`（只開 Read/Write/Edit/Glob/Grep，禁 Bash） |
| **輸出（產物）** | 變動的程式檔與測試檔、TASK.md 打勾 | Claude |
| **輸出（迴圈判定）** | pytest 結果、未完成項數量（前後比）、git checkpoint commit、結束碼 0/2/3/4 | 迴圈自己算，不聽 Claude 說的話 |

重點：**驗證由迴圈做，不由 Claude 自報**。Claude 被禁止執行指令，也就無法自己宣稱「測過了」。

## 任務 2：護欄（4 道，全部實測過）

| # | 護欄 | 實作 | 擋掉的失敗 | 實測證據 |
| --- | --- | --- | --- | --- |
| 1 | 迭代硬上限 | `MAX=6`，`for i in $(seq 1 "$MAX")`，跑滿回結束碼 4 | 失控空轉、無限燒額度；任務太大永遠做不完 | 正常情境 4 輪就收斂，沒有撞到上限 |
| 2 | 每輪 pytest，紅燈即停 | `python -m pytest -q` 失敗 → 不 commit、保留現場、回結束碼 2 | 越改越糟：壞程式被當成進度繼續疊加 | `logs/run-red.log`：第 1 輪紅燈 → EXIT=2 |
| 3 | 每輪 git commit 檢查點 | 綠燈後 `git commit -- .`（只 commit 工作目錄） | 改壞後回不去；看不出每輪做了什麼 | `git log`：基線＋第 1～4 輪共 5 個 commit |
| 4 | 連續 2 輪無進展即停 | 未完成項數沒下降 → `stall+1`，達 2 回結束碼 3 | Claude 卡住、反覆嘗試同一件不可能的事 | `logs/run-stall-v2.log`：2 輪無進展 → EXIT=3 |
| 加 | 時間上限 | 單輪 `timeout 300 claude -p`；整體 `timeout 1800 bash ralph.sh` | 單次呼叫掛死、整個迴圈卡住 | 腳本內建 |
| 加 | 權限收斂 | `--allowedTools Read,Write,Edit,Glob,Grep`、`--disallowedTools Bash` | Claude 跑危險指令、自己跑巢狀迴圈 | 腳本內建 |

### 實跑結果

| 情境 | 設計 | 結果 |
| --- | --- | --- |
| 正常 | 4 個函式（slugify / is_palindrome / word_count / fizzbuzz） | 第 4 輪收斂，EXIT=0，12 passed |
| 紅燈 | 既有測試互相矛盾（`is_even(2)` 同時要 True 和 False） | 第 1 輪 pytest 紅 → 停，EXIT=2，未 commit |
| 無進展 | 項目需要不存在的 API 金鑰 | 連續 2 輪未完成數不變 → 停，EXIT=3 |

## 延伸思考：最危險的失敗模式是什麼？

**最危險的是「假進展」**：迴圈以為有進展，實際上越改越糟，或是在做無意義的變動。它比失控空轉更危險，因為空轉頂多燒錢，假進展會留下看起來像完成的壞成果。

本次實作就踩到一個例子：第一版用「有沒有檔案變動」判斷，結果迴圈自己的 log 檔與 `__pycache__` 每輪都在變，無進展的輪次也被 commit 了（`logs/stall-v1-gitlog.txt` 有 3 個 commit）。修正後（`.git/info/exclude` 排除迴圈自身檔案）無進展輪不再 commit（`logs/stall-v2-gitlog.txt` 只有基線）。

設計時就該堵住，做法：

1. **進展用外部可驗證的指標量**：看「未完成項數有沒有下降＋測試是否綠」，不看 Claude 怎麼說，也不看「檔案有沒有變」。
2. **測試是閘門，不是參考**：紅燈直接停；並禁止修改既有測試（PROMPT 規則 3），否則 Claude 可能靠刪測試讓燈變綠。更嚴格的做法是迴圈比對 `tests/` 既有檔的 hash，被改就停（本次只寫在 PROMPT，列為待加強）。
3. **每輪只做一項＋每輪 commit**：壞掉的範圍限縮在一輪，可用 `git reset` 回到上一個檢查點。
4. **迴圈自己的副產物不得計入進展**：log、快取、時間戳要排除在進展判斷與 commit 之外。
5. **權限最小化**：禁 Bash，Claude 就不能自己跑 `ralph`／迴圈指令造成巢狀無限迴圈，也不能跑破壞性指令。
