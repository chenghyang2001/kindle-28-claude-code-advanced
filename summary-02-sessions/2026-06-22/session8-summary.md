# Session 8 — GSD 與 git worktree 的關係釐清 + /code-session 實作

**日期**：2026-06-22
**專案**：kindle-28-claude-code-advanced（接續 Session 7）
**模式**：互動式教學（一次一問、未經同意不執行、每回合 say_ui 語音播報）

## 完成事項

### 概念釐清：GSD 與 git 隔離的分工

- 回答使用者「用 GSD 要不要自己建 worktree」：**GSD 不建 worktree、不主動切分支**。
- GSD 會做的 git：沒 repo 時 `git init`、每個產物/任務**自動原子 commit**；偵測 nested subdir 時不另 init、commit 到外層 repo（Session 7 已實證）。
- GSD 的 `config.json` 有 `git.branching_strategy`（預設 `none` = 直接 commit 當前分支），可設 per-phase/milestone 分支模板，但**分支 ≠ worktree**。
- 結論：**隔離是使用者責任（自己開 worktree）、commit 是 GSD 責任**；兩者可疊加（在 worktree 內跑 GSD）。

### 實作：用 /code-session 開隔離 worktree

- 跑 `/code-session gsd-wt-trial`：從 repo 根 `git rev-parse --show-toplevel` 推導，`fetch origin main` 後 `git worktree add` 建立。
- 產物：兄弟目錄 `kindle-28-claude-code-advanced-gsd-wt-trial/` + 分支 `feature/gsd-wt-trial`（起點 056fcae，乾淨）。
- 用 `git-bash.exe --cd=<WT>` 在該目錄開新 Git Bash 視窗（成功）。
- 引導：使用者在新視窗 `claude` 啟動 → 跑 GSD，commit 全落 `feature/gsd-wt-trial`，不碰 `main`。

## 關鍵技術筆記

- **GSD git 哲學**：「在你給的目錄/分支就地工作」，管 commit 不管隔離。
- **/code-session 流程**：分支 `feature/<task>`、兄弟目錄 `<repo>-<task>`、從 `origin/<default>` 長出乾淨起點；短命，完工 merge/PR 後 `worktree remove` + `branch -d`。
- **開窗指令**：`cmd.exe /c start "" "C:\Program Files\Git\git-bash.exe" --cd="<WT windows path>"` 可在指定目錄開 Git Bash（open-wt-bash skill 只開在當前 cwd，要指定目錄得自己帶 --cd）。
- 兩個 worktree 共用一個 `.git`、各自獨立 index → 兩 session 同時 commit 不搶 `.git/index.lock`。

## 產出檔案

| 檔案 / 產物 | 說明 |
|---|---|
| `kindle-28-claude-code-advanced-gsd-wt-trial/`（兄弟目錄）| 新 worktree，分支 `feature/gsd-wt-trial` |
| `summary-02-sessions/2026-06-22/session8-summary.md` | 本檔 |

## HANDOFF（下次 session 優先處理）

### 立即行動

- [ ] 若 `feature/gsd-wt-trial` worktree 已玩完：merge 回 main 或直接 `git worktree remove` + `git branch -d feature/gsd-wt-trial`（worktree 不刪會佔磁碟）
- [ ] 若要繼續 GSD 練習，可在該 worktree 內跑 `/gsd-new-project` 體驗「隔離 + 自動 commit」疊加

### 進行中（需接續）

- `feature/gsd-wt-trial` worktree 已建立但尚未在其中跑任何 GSD（使用者在另一視窗操作，本 main session 看不到其進度）。

### 注意事項

- worktree 是磁碟目錄，不主動清會一直存在；清理指令見上。
- 互動教學 + 每回合 say_ui 語音播報仍生效（CLAUDE.md），下次續課照舊。
- 本 session 為 Session 7 收工後的延伸對話（同日同 repo）。
