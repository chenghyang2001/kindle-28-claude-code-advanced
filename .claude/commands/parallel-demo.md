---
description: 平行化 worktree demo — 開 2 個 headless Claude 各自在 worktree 產檔再合併（對照《平行化》手冊 5 階段生命週期）
argument-hint: "[DEMO_ROOT，名稱須含 demo，預設 ~/wt-parallel-demo]"
allowed-tools: Bash
---

# /parallel-demo — git worktree 平行化實跑 demo

跑 `demo/parallel-worktree/parallel-worktree-demo.sh`：在「用完即焚」的臨時 repo 內開 2 個 worktree、
啟動 2 個 headless `claude -p` 平行各產一個檔案，再依序合併回主線、清理。對照《平行化：AI 開發的最大生產力倍增器》手冊。

DEMO_ROOT 參數：`$ARGUMENTS`（空 → 用預設 `~/wt-parallel-demo`）。

## 0. 前置提醒（跑之前先讓使用者知道）

- 會開 **2 個真的 `claude -p`**，走 **Max 訂閱額度（$0，不扣 API credits）**，需要一點時間（背景平行）。
- 用 `--permission-mode acceptEdits`（headless 無 TTY，Claude 自動接受寫檔）——只在此拋棄式沙盒生效。
- DEMO_ROOT 若有帶值，**名稱必須含 `demo`**，否則腳本防呆會擋（防手滑刪錯目錄）。
- **必須在 Git Bash 跑**（不是 PowerShell/cmd）；本機 `claude` 已在 PATH。

## 1. 執行

在專案根目錄用 Git Bash 跑（DEMO_ROOT 有帶就傳、沒帶就省略讓腳本用預設）：

```bash
bash "$CLAUDE_PROJECT_DIR/demo/parallel-worktree/parallel-worktree-demo.sh" $ARGUMENTS
```

- 給足 timeout（建議 ≥ 420000ms，兩軌 headless Claude 需時）。
- 腳本自己會印 Phase 0→5；若中途某軌失敗，`.log-a.txt`／`.log-b.txt` 有原始輸出，讀出來回報根因。

## 2. 驗證 + 回報

腳本跑完後，`cd` 進 `<DEMO_ROOT>/main`（預設 `~/wt-parallel-demo/main`）確認並整理給使用者：

- `ls -1`：主線最終檔案（應同時有 `greet.py` + `farewell.py`）。
- `git log --oneline --graph`：指出 **track-a 通常 fast-forward、track-b 是 3-way merge commit**（教學重點）。
- `git worktree list` 只剩 main、`git branch` 只剩預設分支（確認清理乾淨）。
- 提醒：結果留在 `<DEMO_ROOT>/main` 供翻看；**下次再跑會整包 `rm -rf` 重建**，要留先複製走。

## 3. 想改成自己的任務（順帶告知）

改腳本 Phase 3 那兩行 `exec_track ... '<prompt>'` 的中文 prompt 即可；**只要各軌動不同檔案**（避免衝突），
要 3~5 軌就複製一組 `exec_track` + `PID` + `wait` + `merge`（呼應手冊黃金法則「3–5 個是甜蜜點」）。

## 注意（本專案 CLAUDE.md）

- 每次回答前照語音播報流程（Write `skills/_answer.txt` → taskkill say_ui → start say_ui --autoplay；此三步已長期授權）。
- 這個指令是使用者「明確觸發要跑 demo」的意圖，故第 1 步可直接執行、不必再逐行等「執行」；但若使用者只想看不想跑，尊重其意願改為只解說。
