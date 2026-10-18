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
| 09 | 2026-10-18 | 8 分 | pr-review-toolkit --scope project 裝→review-pr→simplify→移除；installed_plugins 自動回原狀、marketplaces 時間戳由教練還原；全域 cache 殘留 pr-review-toolkit 目錄未刪；以 claude plugin 指令代替 /plugin |
| 10 | 2026-10-18 | 7 分 | onboard itsdangerous（vendor/ 只讀，--depth 1 看不到歷史）；追問改自問自答 5 題附腳本實證；/init 草稿放 answer 不寫進 vendor；audit 10 項（高1中3低6） |
| 11 | 2026-10-18 | 7 分 | 題目只要規劃，實際做完三層測試＋coverage 76→81→96%＋3 步重構各一 commit；模組 277 行略超；cli list 錯誤路徑只手動驗證 |
| 12 | 2026-10-18 | 9 分 | skill 建專案層 .claude/skills，claude -p 自然語言觸發 3 案例過；CI yml 只寫範本不 push、不設 Secrets，gh pr comment 未實跑；review 腳本本機乾跑抓到 4/4 埋點 |
| 13 | 2026-10-18 | 8 分 | 題目只要設計，實派研究/實作/審查三子代理＋git diff 驗邊界；辯論題取自審查必改項，3 審查者平行投票後再派修正閉環；邊界靠 prompt 約束非工具強制 |
| 14 | 2026-10-18 | 22 分 | 登入縮成 CLI 模擬（pbkdf2、無 JWT）；弱/強 prompt 各在全域與 --setting-sources 乾淨沙盒跑，強 11/11、弱 0/11；git bisect run 3 步抓到兇手；強×全域耗時僅知 >600 秒 |
