# K28 快速演練課表

依據：本 repo 的 `demo/`（依書建好的 17 課練習題，每課 exercise-01 基礎／02 進階／03 綜合）。
快速模式只做 **exercise-01 基礎＋exercise-02 進階**，綜合挑戰略過。書共 19 章，第 18、19 章沒有 demo，提示詞見下方。

每段提示詞前面都要加：「全自動執行：不要問我任何問題、不要用選擇題，所有選擇一律採用你的推薦，直接做完並回報」。

## 每章通用流程（第 01–17 章，教練執行）

1. 開練習視窗前，教練把 drill.json 的 `demo_dir` 底下 `exercise-01-基礎.md`、`exercise-02-進階.md` 複製到練習資料夾（**不要**複製 `answer/`、`starter/`、`STEP_LOG.md`、`notes/`、`out/`）。
2. 對練習視窗送：

   > 照 exercise-01-基礎.md 和 exercise-02-進階.md 依序完成。能動手的部分一律真的建檔並實際執行驗證（跑程式、跑測試、印出結果），不要只寫文字說明；需要外部帳號／token／付費服務的部分只寫範本並註明。解答存到 answer/ex01-answer.md、answer/ex02-answer.md。最後寫 NOTES.md：做了什麼、驗證結果、和題目要求的差異。完成後 git add＋commit。

3. 讀 NOTES.md，用 3–5 行回報，更新 HANDOFF 進度表。

## 第 18 章 百倍效率開發實戰（k28-ch18-practice）

> 用本書技巧從零做一個小型「待辦清單 CLI」（Python，含 add／list／done／JSON 存檔）：先寫 PLAN.md（計畫模式三段式：目標、步驟、驗收），再在練習資料夾內開兩個 git worktree 由兩個子代理平行實作「核心邏輯」與「測試」，合併後 pytest 全過，最後用一個 review 子代理審查並修正。NOTES.md 記錄每一步耗時與用到書上哪一章的技巧。

## 第 19 章 高階編排思維（k28-ch19-practice）

> 寫 ORCHESTRATION.md：把「從副駕駛到指揮官」的思維整理成決策表（何時單一 session、何時 worktree 平行、何時子代理、何時 GSD／Ralph 自主迴圈），每列附判斷條件與風險。再挑一個小任務（為一個 CSV 統計腳本加功能＋測試）實際用「主 session 指揮 2 個子代理」完成一次，記錄結果。

## 共通限制（每章都適用）

- **絕不執行** `/logout`、`/login`、`/upgrade`、`/install-github-app`、`/statusline`、`/doctor`，也不要修改全域 `~/.claude/` 底下任何檔案。題目寫到全域設定的地方，一律改成專案層（`./.claude/`、`./CLAUDE.md`、`.mcp.json`）。
- `claude mcp add`、`claude plugin install` 一律 `--scope project`（或 `local`）；測完移除，並比對全域 settings 與 plugins 目錄沒有殘留。
- git worktree 只在練習資料夾自己的 repo 裡建，不碰其他 repo。
- 不建立 GitHub repo、不 push、不部署。需要第三方 token 的只寫設定範本。
- GSD／Ralph 等外部框架：已安裝就用，沒安裝就只做題目的設計部分並註明，不安裝到全域。
- 練習中要用 `claude -p` 時先清 `CLAUDE*` 環境變數（避免巢狀限制）。
