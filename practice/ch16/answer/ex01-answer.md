# 練習 01 解答 — 個人指令小抄（基礎）

> 環境：Claude Code 2.1.302，Windows 10 + Git Bash。完整小抄見 `../CHEATSHEET.md`。

## 任務 1：最常用的 10 個指令／快捷鍵

| # | 指令 / 按鍵 | 用途 | 本版核對 |
| --- | --- | --- | --- |
| 1 | `/clear` | 換任務時清空脈絡，避免舊對話污染 | ✅ 在 slash 清單 |
| 2 | `/compact` | 脈絡快滿但任務沒做完時壓縮續跑（可附保留指示） | ✅ |
| 3 | `/init` | 新專案產生 CLAUDE.md 草稿 | ✅ |
| 4 | `claude -c` | 接續本目錄最近一次對話 | ✅ `--help` 有 `-c, --continue` |
| 5 | `claude -r` | 從清單挑舊 session 接續 | ✅ `-r, --resume [value]` |
| 6 | `claude -p "..."` | 非互動跑一次、印完即走（腳本／管線用） | ✅ 已實跑，回傳 `完成` |
| 7 | `claude mcp list` | 檢查 MCP server 有沒有連上 | ✅ 子指令存在 |
| 8 | `Esc` | 中斷目前生成（方向錯就停） | 按鍵，無法用 help 核對 |
| 9 | `↑` | 帶回上一個輸入，改一下再送 | 按鍵 |
| 10 | `Shift+Tab` | 切換權限模式（一般 / 自動接受 / plan） | 按鍵；對應 flag `--permission-mode` ✅ |

## 任務 2：3 個待刻意練習的項目

| 項目 | 為什麼不熟 | 練習方式 |
| --- | --- | --- |
| `/context` | 習慣憑感覺 `/compact`，沒先看用量 | 每次想 compact 前先 `/context`，超過約 60% 再壓 |
| `claude -w <name>` | 平行任務仍在同一個工作目錄開兩個 session，會搶 git index | 下次有兩個獨立任務就各開一個 worktree |
| `claude --bg` + `claude agents` / `attach` | 長任務都在前景等 | 把跑測試、批次處理這類長任務丟背景，用 `claude logs <id>` 看進度 |

## 驗收

- [x] 至少 10 條，含用途（10 條）
- [x] 標出 3 個待熟練項
- 額外：所有 CLI 指令都經 `check_cheatsheet.py` 對照 `--help` 核對（60 項 0 FAIL）。
