# 練習 01 解答：寫一份精煉 CLAUDE.md

## 「現有專案」
自建 `notestat`：統計 Markdown 筆記字數／行數／標題數的 Python CLI（只用標準庫）＋ pytest 7 個測試。
- 程式：`notestat/core.py`、`notestat/cli.py`、`notestat/__main__.py`
- 測試：`tests/test_core.py`（正常／邊界／錯誤）、`tests/test_cli.py`（讀 `data/` 的整合測試）
- 範例資料：`data/ch07-memo.md`、`data/todo.md`

## 任務 1＋2：5 段式 CLAUDE.md
完整內容見 `answer/ex01-CLAUDE.md`（練習 01 階段的根目錄 CLAUDE.md 快照；之後練習 02 把根目錄版本模組化）。

| 段落 | 填了什麼「真實」內容 |
| --- | --- |
| 專案概述 | 工具用途＋中文逐字、英文以空白切詞的計數規則 |
| 架構 | 實際目錄樹，並註明 `data/` 必須剛好 2 個 .md（測試依賴） |
| 技術堆疊 | Python ≥3.10（本機 3.14.3）、只用標準庫、pytest 8 設定位置 |
| 執行方式 | 3 條可直接複製的指令＋結束碼＋為什麼要 `PYTHONUTF8=1` |
| 重要架構決策 | core/cli 分離、不用 jieba、資料夾結果排序輸出（3 條「為什麼」） |

## 驗證：指令真的複製貼上跑過
用 awk 把 CLAUDE.md 內 ```bash 區塊抽出來逐行執行：

```text
$ PYTHONUTF8=1 python -m pytest -q
7 passed in 0.03s                      [exit=0]
$ PYTHONUTF8=1 python -m notestat data/
data/ch07-memo.md  lines=5  words=33  headings=3
data/todo.md       lines=3  words=12  headings=1
TOTAL  files=2  words=45               [exit=0]
$ PYTHONUTF8=1 python -m notestat data/todo.md --json
{"data/todo.md": {"lines": 3, "words": 12, "headings": 1}}   [exit=0]
$ PYTHONUTF8=1 python -m notestat nope
錯誤：找不到路徑：nope                   [exit=2]（與文件寫的結束碼一致）
```

## 驗收
- [x] 5 段齊全
- [x] 執行指令可直接複製跑（上方實跑結果）
- [x] 至少 1 條「為什麼這樣設計」的決策（共 3 條）
