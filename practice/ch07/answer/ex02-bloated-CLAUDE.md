# notestat

## 專案概述
`notestat` 是統計 Markdown 筆記（字數／行數／標題數）的 Python CLI 小工具，用來追蹤 Kindle 學習筆記的累積量。中文逐字計算、英文以空白切詞。

## 架構
```text
notestat/
├── core.py      # 純函式統計邏輯（不碰檔案系統）
├── cli.py       # argparse 入口：收檔、讀檔、輸出
└── __main__.py  # python -m notestat
tests/           # pytest：test_core（單元）、test_cli（讀 data/ 的整合測試）
data/            # 範例筆記，test_cli 依賴「剛好 2 個 .md」
```

## 技術堆疊
- Python ≥ 3.10（本機 3.14.3），只用標準庫
- pytest 8.x（設定在 `pyproject.toml`，`pythonpath = ["."]`，免安裝套件即可測）

## 執行方式
```bash
PYTHONUTF8=1 python -m pytest -q
PYTHONUTF8=1 python -m notestat data/
PYTHONUTF8=1 python -m notestat data/todo.md --json
```
- 結束碼：0 成功、2 路徑不存在
- Windows 一定要加 `PYTHONUTF8=1`，否則 cp950 會讓中文輸出變亂碼

## 重要架構決策
- **core 與 cli 分離**：統計邏輯是純函式，測試不需建暫存檔；I/O 錯誤（找不到檔、非 UTF-8）只在 cli 處理。
- **不用 `jieba` 分詞**：筆記統計只需要「量」不需要「詞義」，逐字計 CJK 足夠，且維持零依賴。
- **資料夾結果排序輸出**：`rglob` 順序依檔案系統而異，排序後輸出才能穩定比對。

## 程式碼風格（很長，以下全部寫在主檔）
- 命名一律 snake_case，常數全大寫；布林變數用 is_/has_ 開頭。
- 每個函式不超過 30 行，巢狀不超過 3 層，超過就提取子函式。
- 註解寫「為什麼」不寫「做什麼」，註解與 docstring 一律繁體中文。
- 讀寫檔一律 `encoding="utf-8"`，不依賴系統預設（Windows 是 cp950）。
- 不用裸 `except:`；I/O 錯誤只在 cli.py 處理，core.py 只丟 ValueError。
- 新增 CLI 參數時，help 文字要用繁體中文，且 README 與本檔「執行方式」同步更新。
- 單一輸入檔大小上限 2 MB（MAX_FILE_BYTES = 2_097_152），超過要印警告並略過。
- 輸出欄位順序固定為 lines → words → headings，不可調換（下游試算表依賴欄位位置）。

## 測試規則（很長，以下全部寫在主檔）
- 每個新函式至少 3 個測試：正常、邊界（空字串／None）、錯誤。
- 測試檔命名 `tests/test_<模組>.py`，一個模組一個測試檔。
- data/ 裡的範例筆記只能新增在 `data/extra/` 子資料夾，避免破壞 test_cli「剛好 2 個 .md」的假設。
- 覆蓋率目標 85%，低於 85% 不得合併。
- 不在測試裡用 `time.sleep`；需要時間的地方注入假時鐘。
- 跑全部測試的指令：`PYTHONUTF8=1 python -m pytest -q`；只跑單一檔：`PYTHONUTF8=1 python -m pytest tests/test_core.py -q`。

## Git 工作流（很長，以下全部寫在主檔）
- commit message 使用繁體中文，格式「動詞 + 簡短說明」，動詞限：新增／修復／重構／更新／移除。
- 本專案 commit 前綴固定為 `[notestat]`，例：`[notestat] 新增 --json 輸出`。
- 功能分支命名 `feat/<簡短英文>`，修 bug 用 `fix/<簡短英文>`。
- 不 force push、不 `--no-verify`、不 amend 已推送的 commit。
- 發版時 tag 格式 `ns-v<主>.<次>.<修>`，例如 `ns-v0.1.0`。
- 本練習 repo 不建 GitHub repo、不 push。

## 本專案例外

本專案是 Kindle 書籍教學 demo（kindle-drill 快速模式），豁免全域「程式碼三 agent 鐵律」：主 Claude 直接寫檔，不派 code-writer／code-qa／code-reviewer；不需詢問複雜度，也不需詢問是否使用快速模式（已選快速模式）。
所有選擇題一律採用推薦選項、不要停下來問使用者；不可修改全域 `~/.claude/settings.json`，設定一律寫在本專案的 `.claude/settings.local.json`。
