# K28 演練交接

## 原機器結果

先前在 `demo/` 依書做過學習課程（17 課），各課解答在 `demo/[NN-…]/answer/`、過程在 `STEP_LOG.md`；另有 `demo-gsd-*`、`demo-ralph-*` 等實驗資料夾。快速模式的差異以「和 demo 原解答／題目要求的差異」記錄。

## 快速模式進度表

| 章 | 完成日 | 實際耗時 | 和原解答／題目要求的差異 |
| --- | --- | --- | --- |
| 01 | 2026-10-18 | 9 分 | claude -p 非互動量不到反問次數，改記指令次數＋假設數；CSV 用自建模擬資料；範例資料洩漏提示讓模糊版偏好 |
| 02 | 2026-10-18 | 6 分 | worktree 改建在資料夾內 ./wt/（非 ../ 兄弟）；無遠端改用本地 master；bashrc 不動改 scripts/ccwt.sh；MSYS 路徑坑誤建 C:\c\…\k28-ch02-practice 空目錄待手動刪 |
| 03 | 2026-10-18 | 10 分 | EnterPlanMode 實跑，核准選 BYPASS 確認回 bypass；設定改 settings.local.json；無 pre-setup 對照放 scratchpad 避免吃上層 CLAUDE.md；全域 ~/.claude/plans 3 檔已複製到 answer 後刪除；C:\tmp\tmp.fIP5SDubc1 待手動刪 |
