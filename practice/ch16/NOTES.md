# NOTES — K28 第 16 章練習（快速 demo 模式）

## 做了什麼

| 檔案 | 內容 |
| --- | --- |
| `CHEATSHEET.md` | 小抄本體：四大類（session / 檔案 / 自動化 / 外掛 MCP），每條附常用 flag，⭐ 前 10、🎯 待練 3 個 |
| `answer/ex01-answer.md` | 練習 01：10 個常用指令 + 3 個待熟練 |
| `answer/ex02-answer.md` | 練習 02：flag 補齊、分類、alias 延伸思考 |
| `check_cheatsheet.py` | 自動核對小抄：flag 對 `--help`、子指令對 Usage 行、斜線指令對本版清單 |
| `aliases.sh` | 延伸思考的 alias（`cc_p`、`cc_json`、`cc_wt`、`ccc`、`ccplan`、`ccsafe`） |
| `help-snapshots/` | 本版 help 快照、init 事件（斜線清單 229 個）、核對報告、實跑紀錄 |

## 驗證結果

- `check_cheatsheet.py --selftest`：PASS（假 flag / 假斜線指令都被抓出，`--` 之後的 MCP 參數有略過）。
- `check_cheatsheet.py`：60 項 0 FAIL → `help-snapshots/check-report.txt`。
- `claude mcp add/get/remove --scope project`：實跑成功，測完已移除，`.mcp.json` 也刪除 → `help-snapshots/live-run.txt`。
- `claude -p --output-format json`：回傳 success（haiku、`--max-budget-usd 0.05`、執行前清掉 `CLAUDE*` 環境變數）。
- `aliases.sh`：`bash -n` 語法 OK、`source` 後 3 個函式 + 3 個 alias 皆載入、空參數回 exit 1、`cc_p` 實跑回 `alias OK` → `help-snapshots/alias-test.txt`。

## 和題目要求的差異 / 發現

1. **`claude config` 子指令本版不存在**：`claude config --help` 印的是主 help（被當成 prompt）。小抄標 ⚠，改指 `/config` 或 `--settings`。
2. **斜線指令清單來源**：本版沒有 `--list-commands` 之類 flag，改從 `claude -p --output-format stream-json --verbose` 的 init 事件取 `slash_commands`（229 個，含本機 skills）。
   `/resume`、`/memory`、`/plugin` 不在該清單——它們是互動 TUI 專用指令，小抄標〔TUI〕，未能用自動方式證明存在。
3. 題目範例的 `/code-review`、`/plugin`、`--resume`、`--model`、`mcp list` 均存在；`/ultrareview` 在清單中但 help 說明它是 `claude ultrareview` 的舊別名，且為計費雲端功能，**未實跑**。
4. 按鍵（`Esc`、`↑`、`Shift+Tab`）無法用 help 核對，依使用經驗列入。
5. `claude plugin install` 預設 scope 是 **user**，小抄特別標出要加 `--scope project`；本練習沒有實際安裝外掛（沒有需要的外掛，只核對 flag）。
6. `claude --bg`、`claude -w` 只核對 flag 存在，未實跑（會建背景 session / worktree，對小抄練習非必要）。
7. 踩坑：Windows 上 Python `subprocess.run(["claude", ...])` 找不到 npm 的 `claude.CMD`，需先 `shutil.which("claude")`；`timeout` 不能直接包 shell 函式。

> 快速模式：未經 QA／code-reviewer 審查。
