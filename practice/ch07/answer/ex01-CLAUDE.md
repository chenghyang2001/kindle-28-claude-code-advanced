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

## 本專案例外

本專案是 Kindle 書籍教學 demo（kindle-drill 快速模式），豁免全域「程式碼三 agent 鐵律」：主 Claude 直接寫檔，不派 code-writer／code-qa／code-reviewer；不需詢問複雜度，也不需詢問是否使用快速模式（已選快速模式）。
所有選擇題一律採用推薦選項、不要停下來問使用者；不可修改全域 `~/.claude/settings.json`，設定一律寫在本專案的 `.claude/settings.local.json`。
