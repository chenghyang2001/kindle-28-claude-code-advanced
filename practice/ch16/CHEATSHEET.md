# Claude Code 個人小抄（v2.1.302 實測版）

> 核對方式：`check_cheatsheet.py` 自動把本檔每個 `claude ...` 範例的 flag 拿去比對 `claude --help` / `claude <子指令> --help`，
> 斜線指令比對 `claude -p --output-format stream-json --verbose` 的 init 事件 `slash_commands` 清單。
> 標記：⭐ = 最常用前 10　🎯 = 待刻意練習　⚠ = 本版不存在／需注意　〔TUI〕= 互動模式專用（不在 -p 清單）

## 1. Session 控制

| 指令 / 按鍵 | 用途 | 常用 flag / 變化 |
| --- | --- | --- |
| ⭐ `/clear` | 清空脈絡重來 | — |
| ⭐ `/compact` | 壓縮脈絡續跑 | `/compact 保留 API 設計決策`（附保留指示） |
| ⭐ `claude -c` | 接續本目錄最近一次對話 | `claude -c --fork-session`（另開新 session ID） |
| ⭐ `claude -r` | 挑選並接續舊 session | `claude -r <id>`、`claude -r "關鍵字"`、`claude --from-pr 123` |
| `/resume` 〔TUI〕 | 互動中切換 session | — |
| `/rename` | 幫 session 取名 | 啟動時：`claude -n "ch16-練習"` |
| 🎯 `/context` | 看脈絡用量（決定要不要 compact） | — |
| `/model` | 切模型 | 啟動時：`claude --model sonnet`、`--fallback-model haiku` |
| `/effort` | 調思考強度 | 啟動時：`claude --effort high` |
| ⭐ `Esc` | 中斷目前生成 | `Esc Esc`：回到先前訊息改寫（rewind） |
| ⭐ `↑` | 帶回上一個輸入 | — |
| `Shift+Tab` | 切換權限模式（含 plan） | 啟動時：`claude --permission-mode plan` |

## 2. 檔案 / 專案操作

| 指令 | 用途 | 常用 flag / 變化 |
| --- | --- | --- |
| ⭐ `/init` | 產生 CLAUDE.md 草稿 | — |
| `@路徑` | 把檔案塞進脈絡 | `@src/` 整個目錄 |
| `claude --add-dir ../shared` | 允許存取額外目錄 | 可多個：`--add-dir a b` |
| 🎯 `claude -w feature-x` | 為 session 建 git worktree 隔離 | `claude -w feature-x --tmux`（需 tmux） |
| `/memory` 〔TUI〕 | 編輯 CLAUDE.md / 記憶 | `#` 開頭快速記一條 |
| `/config` | 設定面板 | ⚠ `claude config` 子指令本版**不存在**，改用 `/config` 或 `--settings` |

## 3. 自動化 / 非互動

| 指令 | 用途 | 常用 flag / 變化 |
| --- | --- | --- |
| ⭐ `claude -p "..."` | 非互動、印完即走 | `claude -p "摘要" --output-format json` |
| 串流 | 給程式吃 | `claude -p "..." --output-format stream-json --verbose` |
| 限額 | 防爆預算 | `claude -p "..." --max-budget-usd 0.5` |
| 限工具 | 只准特定工具 | `claude -p "..." --allowedTools "Read,Grep"`、`--disallowedTools "Bash"` |
| 結構化輸出 | 要求 JSON Schema | `claude -p "..." --json-schema '{"type":"object"}'` |
| 不留紀錄 | 一次性 | `claude -p "..." --no-session-persistence` |
| 追加系統提示 | 改人設 | `claude -p "..." --append-system-prompt "只用繁中"` |
| 🎯 `claude --bg` | 背景跑 session | `claude agents` 列出、`claude attach <id>`、`claude logs <id>`、`claude stop <id>` |
| `/code-review` | 審查 diff | `/code-review high`、`/code-review --fix` |
| `/loop` | 週期執行 | `/loop 5m /code-review` |
| `claude ultrareview` | 雲端多 agent 審查（計費） | `/ultrareview` 為舊別名 |

## 4. 外掛 / MCP

| 指令 | 用途 | 常用 flag / 變化 |
| --- | --- | --- |
| ⭐ `claude mcp list` | 列出 MCP server | `claude mcp get <name>` |
| `claude mcp add` | 新增 MCP | `claude mcp add --scope project --transport http demo https://example.com/mcp` |
| `claude mcp add`（stdio） | 帶環境變數 | `claude mcp add --scope project -e KEY=v demo -- npx some-server` |
| `claude mcp remove` | 移除 | `claude mcp remove --scope project demo` |
| `/mcp` | 互動中看 MCP 狀態 | — |
| `/plugin` 〔TUI〕 | 外掛管理介面 | — |
| `claude plugin install` | 安裝外掛 | `claude plugin install foo@market --scope project` |
| `claude plugin list` | 已安裝外掛 | `claude plugin details <name>`（看 token 成本） |
| `/reload-plugins` | 不重啟重新載入外掛 | — |
| 除錯設定 | 全部客製關掉 | `claude --safe-mode`、`claude --bare` |

## 待刻意練習（3 個）🎯

1. `/context` —— 習慣「看數字再決定 compact」，而非憑感覺。
2. `claude -w <name>` —— 平行任務用 worktree 隔離，避免兩個 session 搶同一份工作樹。
3. `claude --bg` + `claude agents / attach` —— 長任務丟背景，前景繼續做事。
