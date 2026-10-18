# K28 第 7 章練習筆記

## 做了什麼
1. 自建「現有專案」`notestat`（Python 標準庫 CLI＋pytest 7 個測試＋`data/` 範例筆記）。
2. 練習 01：寫 5 段式 CLAUDE.md（快照：`answer/ex01-CLAUDE.md`），解答 `answer/ex01-answer.md`。
3. 練習 02：先寫臃腫版（`answer/ex02-bloated-CLAUDE.md`，63 行），再拆成 `instructions/` 4 個 @import 檔，根目錄 `CLAUDE.md` 剩 38 行。解答 `answer/ex02-answer.md`。

## 驗證結果
- `PYTHONUTF8=1 python -m pytest -q` → 7 passed
- CLAUDE.md 的 3 條指令用 awk 抽出逐行實跑，exit 全為 0；不存在路徑回 exit 2，與文件一致
- 拆檔後靜態逐行比對：missing=0
- `claude -p`（清 CLAUDE* 環境變數、haiku、禁用讀檔工具）問 4 個只在 import 檔的細節：實驗組 4/4 答對，空資料夾對照組 0/4

## 和題目要求的差異
- 題目說「為一個現有專案」：沒有現成專案，依本章補充自建 `notestat`。
- 練習 01 與 02 共用根目錄 CLAUDE.md：最終根目錄是練習 02 的模組化版；練習 01 的版本另存 `answer/ex01-CLAUDE.md`。
- 「## 本專案例外」段落原文保留，搬到 `instructions/project-exceptions.md` 並由主檔 @import（靜態比對確認一字不漏）。
- 臃腫版中「覆蓋率 85%」「MAX_FILE_BYTES」等規則是為了練習拆檔而寫的約定，程式碼尚未實作檔案大小上限與覆蓋率檢查。
- 沒用到 MCP、plugin、worktree、外部帳號，故無範本需要另外註明。
- 快速模式：未經 QA／reviewer 審查。
