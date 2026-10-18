# NOTES — K28 第 3 章練習（Plan Mode／pre-setup）

## 做了什麼

| 練習 | 產出 | 解答 |
| --- | --- | --- |
| 01 基礎 | 自建 `cfgcli`（Python CLI：set/get/list，JSON 設定檔）→ 用 `EnterPlanMode` 進入計畫模式 → 寫計畫 v1 → 審查改成 v2（4 步修改，含刪掉 1 個越界步驟）→ 用 `ExitPlanMode` 送審核准 → 實作 `export` 子指令＋5 個測試 | `answer/ex01-answer.md` |
| 02 進階 | 在本專案 `./CLAUDE.md` 加專案簡報（目錄/慣用指令/慣例/雷區）、`.claude/settings.local.json`、`.claude/commands/test.md`；用 `claude -p --permission-mode plan` 對同一任務（加 `import`）在「有 pre-setup」與「乾淨副本」各跑一次並比較 | `answer/ex02-answer.md`、`answer/ex02-plans/` |

## 驗證結果

- `PYTHONUTF8=1 python -m pytest -v`：**8 passed**（既有 3＋export 5）
- 手動：`set 名稱 測試` → `export` 輸出中文原文 JSON；`export -o <Windows 路徑>` 寫檔成功
- `claude -p "/test"`：自訂指令可用，回報「8 個測試全部通過」
- 兩次 `claude -p --permission-mode plan` 都 exit 0，且都**沒有修改專案檔案**（`git status` 確認）

## 與題目要求的差異

1. **設定檔名**：題目範例是 `.claude/settings.json`，本專案 CLAUDE.md 規定設定寫在 `.claude/settings.local.json`，照專案規定做；並依慣例加進 `.gitignore`（內容完整寫在 ex02 解答中）。
2. **乾淨對照組位置**：使用者建議「在乾淨的子資料夾跑」。但 Claude Code 會往上層目錄載入 CLAUDE.md，放在本 repo 的子資料夾會吃到本專案的 CLAUDE.md，對照就不乾淨了。所以改放 session scratchpad（`git archive` 匯出 `cfgcli/`＋`tests/`）。
3. **計畫檔位置**：計畫模式（包含 `claude -p --permission-mode plan`）會把計畫檔寫在全域 `~/.claude/plans/`（`wiggly-humming-sky.md`、`cli-import-snug-russell.md`、`cli-import-frolicking-peach.md`），這是 Claude Code 內建行為、不是我手動改的全域設定。已把內容複製到 `answer/`，原檔沒有刪除。
4. **練習 01 的「核准」**：全自動模式下，`ExitPlanMode` 由系統直接核准；「審查」是我自己對 v1 做的（v1/v2 都記錄在解答裡）。
5. **對照組樣本數**：各只跑 1 次，結論是方向性的。

## 已知副作用／未處理

- 練習 01 手動測試時，Git Bash 的 `/tmp/...` 路徑被 Windows Python 解讀成 `C:\tmp\tmp.fIP5SDubc1\`，留下 `config.json`、`out.json` 兩個小測試檔。刪除指令被權限擋下，**檔案仍在**，可手動刪除整個 `C:\tmp\tmp.fIP5SDubc1`。
- 子 session 的 hook 產生了 `.claude/session-state.md`，已加入 `.gitignore`。
- 全域 Stop hook（未 commit 提醒）會蓋掉 `claude -p` 的最終輸出；之後先 commit 再跑對照即可避免。
- 快速 demo 模式：程式碼未經 QA／reviewer agent 審查。

## 沒用到的限制項

沒有用到 MCP、plugin、worktree、GSD/Ralph，也沒有建 GitHub repo、push 或部署。
