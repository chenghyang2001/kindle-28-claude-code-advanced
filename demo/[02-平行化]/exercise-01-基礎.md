# 練習 01 — 基礎：用 git worktree 隔離兩個 session

## 情境說明
兩個 Claude session 共用同一工作目錄會搶 `.git/index.lock`、互相污染暫存區。用 worktree 讓每個 session 有自己的工作樹與 index。

## 範例指令
```bash
# 在 repo 內，從乾淨起點長出兩個隔離工作樹（兄弟目錄）
git worktree add ../myrepo-featA -b feature/a origin/main
git worktree add ../myrepo-featB -b feature/b origin/main

git worktree list          # 確認兩個工作樹各自獨立
# 在 ../myrepo-featA 改檔 -> git add -A -> git commit（碰不到 featB 的 index）

# 完工清理
git worktree remove ../myrepo-featA
git branch -d feature/a
```

## 任務
### 任務 1
在一個練習 repo 用 `git worktree add` 建立兩個兄弟目錄，各自 checkout 不同分支。

### 任務 2
在兩個工作樹同時改不同檔案、各自 `git add -A && git commit`，確認 index 不衝突、commit 不互相干擾。

### 任務 3
跑 `git worktree list` 截圖，並完整走一次 `git worktree remove` + 刪分支的清理流程。

## 驗收標準
- [ ] 兩個工作樹能同時各自 commit 而不報 index.lock
- [ ] 能說出「工作樹」與「分支」的差別
- [ ] 清理後 `git worktree list` 只剩主工作樹

## 完成後
將解答存入 `answer/ex01-answer.md`。
