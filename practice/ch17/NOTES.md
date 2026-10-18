# NOTES — 第 17 章練習紀錄（2026-10-18，快速 demo 模式）

## 做了什麼

| 檔案 | 用途 |
| ------ | ------ |
| `check_sources.py` | 練習 01：用標準庫 urllib 檢查 5 個學習來源的 HTTP 狀態與最近更新日期；`--selftest` 測錯誤處理 |
| `sources-check.txt` | `check_sources.py` 的執行結果 |
| `check_week1.sh` | 練習 02：第 1 週目標的自動驗收（4 項檢查，支援 `--dry-run`，全部唯讀） |
| `learning-log/week1.md` | 第 1 週學習日誌的範例資料（給驗收腳本檢查用） |
| `.claude/settings.local.json` | 專案層設定範例（含 `permissions.allow`），被全域 gitignore 排除，不入版控 |
| `.gitignore` | 排除 `.worktrees/`、`__pycache__/`、`*.stackdump` |
| `answer/ex01-answer.md` | 練習 01 解答：5 個來源＋理由、最高優先＝CHANGELOG.md、提醒設計 |
| `answer/ex02-answer.md` | 練習 02 解答：4 週路徑（每週附驗收指令）、第 1 週綁定目標、延伸思考 |

## 驗證結果

- `python check_sources.py`：**5/5 可連線**（皆 HTTP 200）。抓到 CHANGELOG 最新版本 2.1.302（2026-10-16）、Releases v2.1.302、Issues 最近更新 2026-10-18。
- `python check_sources.py --selftest`：不存在的網域記為 `[FAIL] 連線失敗`，腳本照常跑完（exit 0），錯誤處理正常。
- `bash -n check_week1.sh`：語法通過。
- `bash check_week1.sh --dry-run`：列出 4 項檢查，exit 0。
- `bash check_week1.sh`（準備前）：PASS 1 / FAIL 3，exit 1 → 能正確抓出未達成。
- `bash check_week1.sh`（建好範例資料＋在 repo 內建 `.worktrees/week1-demo` 後）：PASS 4 / FAIL 0，exit 0。測完已移除 worktree 與 `demo/week1` 分支，所以現在再跑第 3 項會是 FAIL（屬預期）。

## 和題目要求的差異

1. **官方文件與 Engineering Blog 抓不到更新日期**：兩站都沒有 `Last-Modified` header，腳本如實寫「未提供」，沒有去爬 HTML 猜日期。
2. **社群來源（Discord / Reddit）沒放進核心 5 個**：不易用腳本穩定檢查，列為備選。
3. **提醒只寫設計**：依限制沒有建立 cron、schtasks、/schedule、/loop 或任何提醒。
4. **第 2～4 週的驗收指令只寫出來，沒有實際跑**：那些週要的檔案（hook、skill、GSD 專案、踩坑紀錄）還不存在；只有第 1 週有完整的自動驗收腳本並實測。
5. **GSD 只出現在第 3 週的規劃中**：本練習沒有實際用 GSD 跑專案。
6. **`.claude/settings.local.json` 不入版控**：全域 gitignore 會排除它（本機設定本來就不該 commit），所以 clone 這個 repo 後第 1 項驗收會 FAIL，需自己建立。
7. 依快速 demo 模式，沒有走 writer → QA → reviewer 流程，只做冒煙測試。
8. 沒有建 GitHub repo、沒有 push。
