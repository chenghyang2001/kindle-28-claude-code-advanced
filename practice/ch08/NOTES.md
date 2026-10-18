# NOTES — 第 8 章練習紀錄

## 做了什麼

| 檔案 | 用途 |
|------|------|
| `env.sh` | 練習 01：shell 優化（UTF-8、alias `cc/ccc/ccr/ccp/ccj`、`claude_clean` 清 `CLAUDE*` 變數）。`source ./env.sh` 後生效 |
| `.claude/settings.json` | 練習 01：`model: sonnet`、`permissions.allow`；練習 02：`SessionStart` + `PreToolUse(Bash)` hooks |
| `.claude/hooks/bash_audit.py` | 練習 02：Bash 稽核 + 危險指令守門，支援 kill switch `K28_HOOK_DISABLE=1`，出錯時 fail-open |
| `tests/test_hook.sh` | hook 單元測試（8 個案例） |
| `tests/verify_e2e.sh` | 用真的 `claude -p --setting-sources project` 做端到端驗證（model / hook / kill / block） |
| `answer/ex01-answer.md`、`answer/ex02-answer.md` | 解答 |
| `.gitignore` | 排除 `settings.local.json`、hook log、測試輸出 |

## 驗證結果
- env.sh：5 個 alias 都生效；Python stdout 編碼為 utf-8；`claude_clean` 子環境的 `CLAUDE*` 變數從 11 個降到 0 個。
- model 預設：`claude -p` 沒加 `--model`，JSON 的 `modelUsage` 顯示 `claude-sonnet-5-5`。
- 權限 allowlist：沒加 `--allowedTools` 也能跑 `git status`，`permission_denials=0`。
- hook 單元測試：8/8 通過。
- hook 端到端：log 依序出現 `SessionStart` → `PreToolUse ALLOW echo hook-trigger-test`；`git reset --hard HEAD` 被 BLOCK（exit 2）；設 `K28_HOOK_DISABLE=1` 後新增 log 為 0 行。
- 4 次 `claude -p` 呼叫中，有記錄的 model 驗證那次花費約 0.054 USD。

## 和題目要求的差異
1. **全域改成專案層**：題目範例用 `~/.claude/settings.json`、`~/.claude/hooks/`；這裡改成本專案 `.claude/settings.json` 與 `./.claude/hooks/`，指令路徑用 `$CLAUDE_PROJECT_DIR`。alias 沒改 `~/.bashrc`，改寫成 `env.sh`。
2. **設定檔位置**：本專案 CLAUDE.md 原本寫「設定寫在 settings.local.json」，但這次任務指示明確要求寫在 `.claude/settings.json`，所以照任務指示做。
3. **model**：題目範例是 `claude-opus-4-8`；預設改用 `sonnet` alias（解析為 `claude-sonnet-5-5`），因為練習 demo 用不到最貴的模型。
4. **任務 2 只要求 2 個**，實際 5 個都套用並驗證。
5. **status line** 只列為想法，沒有執行 `/statusline`（任務禁止）。

## 過程中的發現
- **hook 會即時套用到正在跑的 session**：寫好 `.claude/settings.json` 之後，本 Claude session 自己的 Bash 呼叫馬上就經過這個 hook。兩次測試指令因為字串裡有 `git push --force`、`git reset --hard`（只是測資）而被擋下。改用 Write 工具建測試檔、把危險字串放在檔案裡就解決了。這也顯示：比對整串指令字串的守門 hook 會誤擋 heredoc 或測資，這是它的限制。
- **Git Bash 路徑陷阱**：Git Bash 的 `$PWD` 是 `/c/Users/...`，傳給 Windows Python 會被解讀成 `C:\c\Users\...`，第一次單測的 log 因此寫到錯的位置。修正方式是腳本改用 `Path(__file__)` 推算專案根目錄，不依賴 `CLAUDE_PROJECT_DIR` 的格式。錯寫的目錄已刪除。
- 這個 hook 會留在專案裡（屬於練習成果）。之後在本資料夾開 Claude 都會記錄 Bash 指令；要暫停就設 `K28_HOOK_DISABLE=1`。
