# NOTES — Kindle 28 第 12 章練習

快速 demo 模式（依專案 CLAUDE.md），未經 code-writer／QA／reviewer 流程。

## 做了什麼

| 練習 | 產出 |
| --- | --- |
| 01 | `.claude/skills/csv-report/SKILL.md`（專案層 skill）＋ `scripts/csv_report.py` 輔助腳本；測試資料 `data/sales.csv`、`data/edge.csv`；測試腳本 `scripts/run_skill_tests.sh`；解答 `answer/ex01-answer.md` |
| 02 | `.github/workflows/claude-review.yml`（範本）＋ `scripts/claude_review.sh`；示範審查對象 `demo/discount.py`；解答 `answer/ex02-answer.md` |

## 驗證結果

- **練習 01**：`claude -p` 實跑 3 個案例，全部通過（紀錄在 `answer/logs/skill-*.log`）
  - 正常：用自然語言「幫我做 csv 報告」就自動觸發 `Skill(csv-report)`，平均值正確
  - 邊界：空值、`N/A`、含逗號的引號欄位都處理正確
  - 錯誤：檔案不存在時回報錯誤、沒有產生報告檔
- **練習 02**：`scripts/claude_review.sh` 本機乾跑成功（未設 `ANTHROPIC_API_KEY`，用訂閱登入）
  - 刻意埋的 4 個問題全部被列為 🔴 必改（`answer/logs/review-dryrun.md`）
  - 另測：空 diff → 印「沒有變更」exit 0；未知參數 → exit 2；`bash -n` 與 YAML 解析通過
  - 乾跑後已把 `demo/discount.py` 還原成乾淨版本，有問題的改動保留在 `answer/logs/review-input.diff`

## 過程中遇到的問題

1. **`claude -p` 的 stderr 警告混進 JSON 串流**（"no stdin data received"）→ 加 `< /dev/null`、stderr 另存。
2. **使用者全域 Stop hook 劫持審查輸出**：第一次乾跑時，子 session 結束時被「Uncommitted changes detected」hook 擋下，最後輸出變成回應 hook 的文字，不是審查結果。
   - `--bare` 可跳過 hook，但它不讀 OAuth、強制要 API key，不符合「本機用訂閱登入」的要求
   - 改用 `--setting-sources project,local --settings '{"disableAllHooks":true}'` 解決
   - 該 hook 還在專案內產生 `.claude/session-state.md`，已刪除並加進 `.gitignore`
3. **平均值格式不一致**（`33.0` vs `1250.19`）：skill 測試時子 session 主動指出，已改成固定兩位小數。`answer/logs/skill-*.log` 是修改前跑的，所以紀錄中仍顯示 `33.0`、`90.0`；修改後直接執行腳本確認輸出為 `33.00`。

## 和題目要求的差異

- 練習 01 範例的 skill 名稱沿用 `csv-report`（題目要「你常做的流程」，這裡選題目範例延伸，加上輔助腳本、缺值規則與錯誤處理）。
- 練習 02 的 workflow **只是範本**：沒有 push、沒有建 GitHub repo、沒有設 Secrets，所以 `gh pr comment` 那段沒有實際執行（本機加 `--post` 只會印「乾跑模式」）。
- 練習 02 本機乾跑是審查「未 commit 的改動」（`git diff HEAD`），CI 上則傳 `--base origin/<base 分支>`。
- 全程沒有修改 `~/.claude/` 底下任何檔案；沒有用到 MCP、plugin、worktree、GSD／Ralph。
