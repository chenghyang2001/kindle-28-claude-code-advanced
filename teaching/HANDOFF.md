# K28 演練交接

## 原機器結果

先前在 `demo/` 依書做過學習課程（17 課），各課解答在 `demo/[NN-…]/answer/`、過程在 `STEP_LOG.md`；另有 `demo-gsd-*`、`demo-ralph-*` 等實驗資料夾。快速模式的差異以「和 demo 原解答／題目要求的差異」記錄。

## 快速模式進度表

| 章 | 完成日 | 實際耗時 | 和原解答／題目要求的差異 |
| --- | --- | --- | --- |
| 01 | 2026-10-18 | 9 分 | claude -p 非互動量不到反問次數，改記指令次數＋假設數；CSV 用自建模擬資料；範例資料洩漏提示讓模糊版偏好 |
| 02 | 2026-10-18 | 6 分 | worktree 改建在資料夾內 ./wt/（非 ../ 兄弟）；無遠端改用本地 master；bashrc 不動改 scripts/ccwt.sh；MSYS 路徑坑誤建 C:\c\…\k28-ch02-practice 空目錄待手動刪 |
| 03 | 2026-10-18 | 10 分 | EnterPlanMode 實跑，核准選 BYPASS 確認回 bypass；設定改 settings.local.json；無 pre-setup 對照放 scratchpad 避免吃上層 CLAUDE.md；全域 ~/.claude/plans 3 檔已複製到 answer 後刪除；C:\tmp\tmp.fIP5SDubc1 待手動刪 |
| 04 | 2026-10-18 | 12 分 | 用 claude -p --resume＋haiku 12 回合模擬長 session（非互動聊天）；run1 被 CLAUDE.md 答案污染重跑 run2；教練實下 /compact 驗證 3 項全保留 |
| 05 | 2026-10-18 | 9 分 | gate 寫成可執行腳本實跑＋反向測試；真派 Researcher/Builder/Reviewer 三子代理＋信號檔，src 越權 0；未跑 /gsd-* 指令（手寫 PHASES.md）；指揮者改了型別註記與 2 行整合 |
| 06 | 2026-10-18 | 7 分 | 未用 Ralph 本體，改 bash＋claude -p（haiku）迴圈；MAX 10→6；紅燈停／無進展停各故意觸發一次（EXIT 2/3）；修正無進展輪也 commit 的 bug |
| 07 | 2026-10-18 | 4 分 | 自建 notestat 當現有專案；@import 以 claude -p 實測 4/4（對照組 0/4）；ex01 版另存 answer/；例外段落搬進 import 檔 |
| 08 | 2026-10-18 | 6 分 | isolated 開窗跳「外部 CLAUDE.md import」選 No 維持隔離；hook／alias 全改專案層（env.sh、.claude/settings.json、$CLAUDE_PROJECT_DIR）；model 用 sonnet 非 opus；hook e2e＋kill switch 實測 |
