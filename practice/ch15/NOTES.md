# NOTES — 第 15 章練習紀錄（2026-10-18，快速 demo 模式）

## 做了什麼

| 項目 | 檔案 |
| --- | --- |
| 範例資料 | `data/sales.csv`（6 列營收）、`data/tmp-delete-me.txt`（rm 測試用）、`.env`（假 key，已 gitignore，不入版控） |
| 練習 01 實跑腳本 | `scripts/ex01-model-cost.sh`：3 任務 × haiku/sonnet/opus 共 9 次 `claude -p --output-format json` |
| 練習 01 成本表 | `scripts/ex01-cost-table.py` → `results/ex01/cost-table.md` |
| 練習 02 權限設定 | `.claude/settings.json`（allow 5／ask 3／deny 4 條） |
| 練習 02 實測腳本 | `scripts/ex02-permission-test.sh`：5 個案例 |
| 解答 | `answer/ex01-answer.md`、`answer/ex02-answer.md` |

## 驗證結果

**練習 01**（9/9 次成功）

- 成本比例 Haiku : Sonnet : Opus ≈ **1 : 18 : 37**，三個任務都很一致。
- **Haiku 在推理題答錯**（違反「標籤全錯」的前提），Sonnet、Opus 正確 → 推理題不該為了省錢用 Haiku。
- 單次成本主要是約 2.8 萬 token 的 Claude Code 系統提示固定開銷，不是 prompt 本身。
- 9 次總花費約 0.41 美元。

**練習 02**（5/5 符合預期）

- allow：`git status`、讀 `data/sales.csv` → 放行，`permission_denials` 為空。
- deny：讀 `.env`、`curl` → 擋下。
- ask：`rm` → `-p` 模式沒有互動確認，**變成拒絕**，檔案實際沒被刪。
- 5 次總花費約 0.013 美元。

## 和題目要求的差異

1. 題目範例的 model ID 是 `claude-haiku-4-5-20251001`；實跑用別名 `haiku/sonnet/opus`，實際對應 `claude-*-5-5` 新版。所以成本數字是新版 model 的，不是題目年代的。
2. 題目只要「量級估算」，這裡改成實測（每任務 3 個 model，超過要求的 2 個）。每組只跑一次，速度數字有波動，成本比例則穩定。
3. 題目的 permissions 範例只有 allow/ask，這裡多加了 deny，並在 `-p` 下實測；ask 在 `-p` 下與 deny 行為相同，已照實記錄。
4. 所有 `claude -p` 都加 `--setting-sources project,local` 並清 `CLAUDE*` 環境變數，避免全域設定干擾；`results/` 裡的使用者家目錄路徑已換成 `~`。
5. 沒有用到外部帳號、MCP、plugin、worktree、GSD／Ralph，因此沒有需要只寫範本的部分。

## 已知沒處理的風險（快速模式，未經 QA／審查）

- 成本只跑 1 次樣本，沒有重複取平均。
- `ex01-cost-table.py` 的 `assert` 只做最小冒煙檢查。
- 權限規則用的是字串前綴比對，`Bash(curl:*)` 擋不住 `bash -c "curl ..."` 之類的變形，正式環境應搭配 sandbox 或 hook。
