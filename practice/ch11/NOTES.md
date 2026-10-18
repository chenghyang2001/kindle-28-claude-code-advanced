# NOTES — K28 第 11 章練習（測試金字塔 + 安全重構）

快速模式（依專案 CLAUDE.md）：主 Claude 直接寫檔，未經三 agent QA／審查。

## 做了什麼

1. **自建中型模組 `bookshelf/`**（書籍借閱管理）
   - 檔案：`rules.py`、`db.py`、`service.py`、`cli.py`
   - 資料庫用 sqlite3 標準庫，SQL 全部是參數化查詢
   - CLI 入口是 `python -m bookshelf.cli`，作為 E2E 測試的對象
2. **建立 `.venv`**，在裡面安裝 pytest 9.1.1、pytest-cov 7.1.0（coverage 7.16.2）。沒有安裝到全域。
3. **練習 01**
   - 三層測試：`tests/unit`、`tests/integration`、`tests/e2e`（E2E 用子程序真的跑 CLI）
   - 產出 coverage 報告，找出 5 個缺口（其中 1 個是 coverage 看不到的盲點）
   - 補測試後重跑，比較覆蓋率變化
4. **練習 02**
   - 替 `Library.report()` 寫 characterization test，並做突變檢查確認它有效
   - 分 3 小步重構，每步跑綠燈後 commit
5. 解答在 `answer/ex01-answer.md`、`answer/ex02-answer.md`；三份 coverage 報告在 `reports/`

## 驗證結果（都是實際執行的輸出）

| 時間點 | 測試數 | 總覆蓋率 | 備註 |
| --- | --- | --- | --- |
| baseline | 20 passed | 76% | `service.py` 50%，`report()` 沒測過 |
| 補缺口後 | 28 passed | 81% | `rules.py` 100%，`service.py` 60% |
| characterization 後 | 31 passed | 96% | `service.py` 100% |
| 重構 3 步完成 | 33 passed | 96% | 同一份 golden master 全程通過 |

- 各層執行時間：單元 0.04s、整合 0.07s、E2E 0.69s
- 突變檢查：把 200 改成 199，golden master 測試 FAILED；還原後恢復全綠
- CLI 手動 demo（用 `$TEMP` 底下的暫存 DB，跑完已刪除）：
  - add、borrow、return、report、list 輸出都正確
  - 壞 ISBN 和重複借出時印出「錯誤：…」，exit code 是 1

git 紀錄（每個綠燈一個 commit）：

```text
afa208e 新增 bookshelf 模組與三層測試（coverage baseline 76%）
71571cc 新增依 coverage 缺口補的測試（76% → 81%）
7c8bebb 新增 report() 的 characterization test（重構前釘住行為）
5151cb8 重構 report 步驟 1：罰金改用 calc_fine，移除重複的魔術數字
2728113 重構 report 步驟 2：抽出 summarize_loans 分離計算與排版
0277ea8 重構 report 步驟 3：抽出 format_entry 改用 f-string，並為純函式補單元測試
```

## 和題目要求的差異

- 題目只要求「規劃」和「說明」；這次實際寫了模組、測試、coverage 報告和重構 commit。
- 模組重構後是 277 行（含註解和 docstring），比指定的 150–250 行稍多，原因是重構拆出了 dataclass 和函式。重構前約 250 行。
- 有一個缺口沒有補自動測試：`cli.py` 的 `list` 指令和錯誤 exit code（剩下的 4% 未覆蓋）。這部分只用手動 CLI demo 驗證過。
- 這一章不需要外部帳號或 token，也沒有用到 MCP、plugin、worktree、`claude -p`，所以沒有需要只寫範本的部分。
- 測試資料是在 fixture 裡用程式建立的（記憶體 DB 或 `tmp_path`），沒有另外建 `data/` 目錄。

## 已知風險（快速模式未處理）

- 日期預設是 `date.today()`，CLI 不帶 `--date` 時結果會隨執行日期改變。測試都有明確指定日期。
- 沒有做並發控制，例如兩個程序同時借同一本書。
