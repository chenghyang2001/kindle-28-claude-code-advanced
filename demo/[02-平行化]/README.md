# [02] 平行化（Parallelization）

> 所屬：Part II — 生產力　|　難度：進階　|　預估：~45 分鐘

## 學習目標
- 用 git worktree 隔離平行 session
- 設定常用 alias 加速
- 同時跑多個 Claude 而不互相污染

## 前置條件
- 完成 [01]，且本機有一個 git repo 可練習。

## 課程結構
- `exercise-01-基礎.md`：在一個 repo 上開兩個 worktree，模擬兩個 Claude session 同時工作互不干擾。
- `exercise-02-進階.md`：把『開一個隔離 worktree + 切到該目錄 + 起 Claude』的流程包成一個 shell alias / function。
- `exercise-03-綜合.md`：設計一個『雙 session 隔離』的個人慣例：何時用 worktree、何時直接在主線、完工如何收尾。

## 完成標準
- [ ] 閱讀本課 README
- [ ] 完成基礎練習，解答存入 `answer/ex01-answer.md`
- [ ] 完成進階練習，解答存入 `answer/ex02-answer.md`
- [ ] （選配）完成綜合挑戰，解答存入 `answer/ex03-answer.md`
- [ ] 填寫 `STEP_LOG.md`
- [ ] 執行 `/study-scaffold carry 2` 攜帶答案到下一課

## 本課重點概念
- git worktree 隔離
- 工作樹 vs 分支
- 平行 session 不共用 index
- 避免 .git/index.lock 衝突
- alias 倍增生產力
