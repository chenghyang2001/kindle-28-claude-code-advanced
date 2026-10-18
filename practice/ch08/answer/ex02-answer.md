# 練習 02 解答 — 用 hook 自動化重複動作

## 任務 1：選定的重複動作與觸發時機

**重複動作**：每次讓 Claude 跑 shell 指令時，人工盯著「它剛跑了什麼、有沒有危險指令」。
**自動化成**：Bash 稽核 + 危險指令守門 hook。

| 觸發時機 | matcher | 行為 |
|---------|---------|------|
| `SessionStart` | （全部） | 寫一行 `SessionStart source=...` 到 log，用來切分每次 session |
| `PreToolUse` | `Bash` | 記錄將要執行的指令（`ALLOW`）；命中危險樣式（`rm -rf /`、`git push --force`、`git reset --hard`）則寫 `BLOCK` 並 **exit 2 阻擋**，stderr 回饋給 Claude |

- 設定：`.claude/settings.json` 的 `hooks` 區塊，指令 `python "$CLAUDE_PROJECT_DIR/.claude/hooks/bash_audit.py"`
- 腳本：`.claude/hooks/bash_audit.py`
- log：`.claude/hooks/logs/hook.log`（已加進 .gitignore）

## 任務 2：實作與測試

### 2-1 單元測試（直接餵 hook JSON）— `bash tests/test_hook.sh`
```text
PASS 一般指令放行 (exit=0)
PASS 強制push阻擋 (exit=2)
PASS rm-rf根目錄阻擋 (exit=2)
PASS reset-hard阻擋 (exit=2)
PASS kill switch放行 (exit=0)
PASS 壞輸入fail-open (exit=0)
PASS SessionStart記錄 (exit=0)
PASS kill switch 時不寫 log（rm -rf / 只出現1次） (exit=1)
結果：8 通過 / 0 失敗
```

### 2-2 端到端：真的 `claude -p --setting-sources project` 故意觸發 — `bash tests/verify_e2e.sh`
（`ccp` = 清掉 `CLAUDE*` 變數後的 `claude -p --setting-sources project`）

**正常觸發**（請 Claude 執行 `echo hook-trigger-test`）：
```text
2026-10-18 12:58:38 [e65b834a] SessionStart source=startup
2026-10-18 12:58:42 [e65b834a] PreToolUse ALLOW cmd='echo hook-trigger-test'
```
→ 順序正確：session 開始先觸發 SessionStart，Bash 執行前觸發 PreToolUse。

**危險指令阻擋**（請 Claude 執行 `git reset --hard HEAD`）：
```text
PreToolUse:Bash hook error: [...bash_audit.py]: [bash_audit] 已阻擋危險指令：git reset --hard HEAD（設 K28_HOOK_DISABLE=1 可停用此 hook）
2026-10-18 12:59:23 [07e4ea56] SessionStart source=startup
2026-10-18 12:59:28 [07e4ea56] PreToolUse BLOCK cmd='git reset --hard HEAD' pattern='\\bgit\\s+reset\\s+--hard\\b'
```

**kill switch**（`K28_HOOK_DISABLE=1 ccp ...`，請 Claude 執行 `echo killswitch-test`）：
```text
done
--- 本次新增 log（應為空）---
新增行數=0
```
→ Claude 照樣完成任務，但 hook 完全沒動作（連 SessionStart 都沒寫）。

## 延伸思考：如何設計「可關閉 / 可逃生」的 hook

1. **Kill switch 環境變數放在最前面**：`K28_HOOK_DISABLE=1` 時連 stdin 都不讀就 exit 0。單次停用只要在指令前加變數，不必改設定檔。
2. **Fail-open**：腳本自己出錯（壞 JSON、找不到檔案）一律 exit 0 並寫 `[hook-error]`。稽核型 hook 不能因為自己的 bug 把 Claude 卡死。（安全關鍵的守門 hook 可以反過來選 fail-closed，但要清楚記錄為什麼這樣選。）
3. **只有明確命中才阻擋**：只用 exit 2 擋少數高風險樣式，其餘一律放行，降低誤判。
4. **阻擋訊息要說怎麼逃生**：stderr 寫明「設 K28_HOOK_DISABLE=1 可停用」，人和 Claude 都看得到。
5. **每次觸發都留 log**：帶時間、session id、事件、決策（ALLOW/BLOCK）。除錯時看 log 就知道 hook 有沒有跑、在什麼時候跑、做了什麼決定。
6. **放在專案層、可隔離測試**：寫在 `.claude/settings.json`，用 `--setting-sources project` 單獨測，不跟全域 hook 混在一起；腳本也能直接用 JSON 單測，不必每次都開 Claude。
7. **其他層級的逃生門**：`/hooks` 選單、settings 的 `"disableAllHooks": true`、或 `--setting-sources` 排除該層設定。
