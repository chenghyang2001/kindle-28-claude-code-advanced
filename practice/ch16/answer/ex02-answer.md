# 練習 02 解答 — 補上 flags 與分類（進階）

> 完整分類小抄：`../CHEATSHEET.md`（四大類 + 每條常用 flag）。本檔是重點摘要與驗證紀錄。

## 任務 1 + 2：分類後的小抄（含常用 flag）

### 檔案操作

| 指令 | 常用 flag |
| --- | --- |
| `/init` | — |
| `claude --add-dir ../shared` | 可多個目錄 |
| `claude -w feature-x` | `--tmux` |
| `/config` | ⚠ `claude config` 子指令**本版不存在**（舊版才有），改用 `/config` 或 `--settings <file>` |

### Session 控制

| 指令 | 常用 flag |
| --- | --- |
| `claude -c` | `--fork-session` |
| `claude -r` | `-r <id>`、`--from-pr 123` |
| `claude --model sonnet` | `--fallback-model haiku`、`--effort high` |
| `claude -n "名稱"` | 對應互動中的 `/rename` |
| `/clear`、`/compact`、`/context` | `/compact <保留指示>` |

### 自動化

| 指令 | 常用 flag |
| --- | --- |
| `claude -p "..."` | `--output-format text/json/stream-json`（stream-json 要加 `--verbose`） |
| 預算與安全 | `--max-budget-usd 0.5`、`--allowedTools "Read,Grep"`、`--disallowedTools "Bash"` |
| 結構化 | `--json-schema '{...}'`、`--no-session-persistence` |
| 背景 | `claude --bg` → `claude agents` / `attach` / `logs` / `stop` |
| 斜線 | `/code-review high`、`/loop 5m /code-review` |

### 外掛 / MCP

| 指令 | 常用 flag |
| --- | --- |
| `claude mcp add` | `--scope project`、`--transport http`、`-e KEY=v`、`-H "Header: v"` |
| `claude mcp list` / `get` / `remove` | `remove --scope project` |
| `claude plugin install` | `--scope project`（預設是 user！）、`-y` |
| `claude plugin list` / `details` | `details` 會列 token 成本 |
| 排錯 | `--safe-mode`、`--bare` |

## 實際驗證

1. **flag 自動核對**：`PYTHONUTF8=1 python check_cheatsheet.py` → 60 項（flag + 子指令 + 斜線指令）0 FAIL，報告存 `help-snapshots/check-report.txt`。
   `--selftest` 用假 flag `--no-such-flag`、假指令 `/no-such-cmd` 驗證腳本真的抓得到錯。
2. **MCP（project scope，測完移除）**：`claude mcp add --scope project demo-echo -- node -e ...` → `.mcp.json` 出現設定、`claude mcp get` 顯示「Pending approval」→ `claude mcp remove --scope project demo-echo` 移除。紀錄：`help-snapshots/live-run.txt`。
3. **`claude -p --output-format json`**：實跑回傳 `{'subtype': 'success', 'result': '完成', 'num_turns': 1}`。

## 延伸思考：哪些值得設 alias？

實作在 `../aliases.sh`（`source ./aliases.sh` 測試通過，未改 `~/.bashrc`）。

**值得設（打字長、參數固定、高頻）**

| alias | 展開 | 理由 |
| --- | --- | --- |
| `cc_p "..."` | `claude -p "..." --output-format text --no-session-persistence` | 每次都要打 3 個 flag，最值得縮 |
| `cc_json "..." [USD]` | 加 `--output-format json --max-budget-usd` | 腳本用，預算上限不能忘 → 用 alias 強制帶上 |
| `cc_wt <name>` | `claude -w <name>` | 本身短，但強制必填名稱，避免匿名 worktree |
| `ccplan` / `ccsafe` | `--permission-mode plan` / `--safe-mode` | flag 長、拼錯就啟動錯模式 |

**不值得設（過度工程）**

- `/clear`、`/compact`、`/init` 等斜線指令：本來就有 Tab 補全，alias 也做不到（是 TUI 內指令）。
- `claude -c`、`claude -r`：已經只有 2 個字元的 flag，alias（`ccc`）只省 3 個字，還多一層要記；我保留 `ccc` 只是示範，實務上可刪。
- `claude mcp add ...`：每次參數都不同，alias 包不住，反而遮住 `--scope` 這種該看清楚的選項。

原則：**alias 用來「固定安全預設」**（預算、不留紀錄、scope），不是用來省幾個字元。
