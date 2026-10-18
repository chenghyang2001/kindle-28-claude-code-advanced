# NOTES — K28 第 6 章練習（Ralph 自主迴圈）

## 做了什麼

| 項目 | 檔案 |
| --- | --- |
| 練習 01 解答（狀態流 mermaid＋文字圖、停止條件表） | `answer/ex01-answer.md` |
| 練習 02 解答（每輪輸入/輸出、4 道護欄、延伸思考） | `answer/ex02-answer.md` |
| 自主迴圈腳本（bash＋`claude -p --model haiku`） | `ralph-demo/ralph.sh` |
| 每輪固定提示詞 | `ralph-demo/PROMPT.md` |
| 三個情境範本（正常／紅燈／無進展） | `ralph-demo/templates/{main,red,stall}/` |
| 正常情境實際產物（4 個函式＋12 個測試） | `ralph-demo/work-main/` |
| 全部執行紀錄 | `ralph-demo/logs/` |

## 驗證結果（都實際跑過）

- `bash -n`、`shellcheck ralph.sh`：通過。
- **正常情境**：`timeout 1800 bash ralph.sh work-main` → 第 4 輪收斂，EXIT=0。TASK.md 4 項全打勾；之後獨立重跑 `pytest` 得 12 passed。git log 有「基線＋第 1～4 輪」共 5 個檢查點 commit。
- **紅燈停**（故意失敗）：既有測試互相矛盾 → 第 1 輪 pytest 紅 → 立即停止、未 commit，EXIT=2（`logs/run-red.log`）。Haiku 自己也看出測試矛盾而沒有改檔。
- **無進展停**（故意失敗）：任務需要不存在的 `PAYMENT_API_KEY` → 連續 2 輪未完成數不變 → 停止，EXIT=3（`logs/run-stall.log`、修正後重跑 `logs/run-stall-v2.log`）。
- 護欄參數：MAX=6、單輪 timeout 300 秒、整體外層 `timeout`、STALL_LIMIT=2。迴圈內沒有任何 `ralph`／`--dry-run` 指令，Claude 也被禁用 Bash。
- 子 `claude -p` 啟動前先 `unset` 所有 `CLAUDE*` 環境變數，並用 `--setting-sources project,local` 避開全域 hooks。

## 過程中發現並修正的問題

- 第一版每輪把迴圈自己的 `.ralph-*.log` 與 `__pycache__` 也 commit 進去，導致**無進展的輪次也有 commit**（`logs/stall-v1-gitlog.txt`）。修正：腳本寫入 `.git/info/exclude`＋`PYTHONDONTWRITEBYTECODE=1`，重跑後無進展輪會顯示「跳過 commit」（`logs/stall-v2-gitlog.txt` 只剩基線）。
- 主 repo 已誤 commit 的快取與 log 改成取消追蹤，並新增 `.gitignore`；前 5 個 checkpoint commit 保留原樣作為迴圈的實際紀錄，不改寫歷史。正常情境是用修正**前**的腳本跑的；修正只影響「commit 哪些檔」，不影響收斂判斷。

## 和題目要求的差異

- **沒有用 Ralph 本體**：未安裝，也照指示不裝外掛版，改用書中 bash＋`claude -p` 的骨架並加上護欄。
- 題目骨架的 `MAX=10` 改成 6（依本章補充要求），收斂判斷由 `grep -q '\[ \]'` 改成數 `^- \[ \]` 的行數，用來同時判斷「無進展」。
- 紅燈情境的紅燈來自預先放好的矛盾測試，不是 Claude 自己寫壞；這是為了讓失敗情境可以穩定重現。
- 「禁止修改既有測試」目前只寫在提示詞裡，迴圈沒有用 hash 強制檢查（已在 ex02 列為待加強）。
- 兩個失敗情境在 scratchpad 的臨時 git repo 執行，以免污染本 repo 的歷史；執行紀錄已複製到 `ralph-demo/logs/`。
- 沒有建 GitHub repo、沒有 push（依指示）。
