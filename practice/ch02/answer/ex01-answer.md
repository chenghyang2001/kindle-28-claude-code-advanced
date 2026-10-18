# 練習 01 解答 — 用 git worktree 隔離兩個 session

> 執行腳本：`bash scripts/ex01-demo.sh`（完整輸出：`logs/ex01-output.txt`）
> 依補充要求：worktree 建在本資料夾 `./wt/featA`、`./wt/featB`（`wt/` 已加進 `.gitignore`），起點用本地 `master`（本 repo 沒有遠端，取代 `origin/main`）。

## 任務 1：建兩個工作樹，各自不同分支

```bash
git worktree add wt/featA -b feature/a master
git worktree add wt/featB -b feature/b master
git worktree list
```

實際輸出：

```
~/workspace/k28-ch02-practice           ff61225 [master]
~/workspace/k28-ch02-practice/wt/featA  ff61225 [feature/a]
~/workspace/k28-ch02-practice/wt/featB  ff61225 [feature/b]
```

## 任務 2：兩邊同時改不同檔並 commit

兩個背景行程**同時**跑，各在自己的工作樹 `echo >> 檔案 && git add -A && git commit` 20 次：

```
featA 結束碼=0，featB 結束碼=0
✅ 40 次平行 commit，index.lock 錯誤 0 次
--- 每個工作樹的 index 檔各自獨立 ---
.          -> .git/index
wt/featA   -> .../.git/worktrees/featA/index
wt/featB   -> .../.git/worktrees/featB/index
--- commit 互不干擾 ---
feature/a：比 master 多 20 個 commit，新增檔案 = a.txt
feature/b：比 master 多 20 個 commit，新增檔案 = b.txt
```

**對照組**（同一個工作樹裡兩個行程同時 commit，各 30 次）：

```
同一工作樹平行 commit：index.lock 錯誤 1 次
fatal: Unable to create '.../.git/worktrees/race/index.lock': File exists.
```

這就是情境說明的問題：共用工作目錄 = 共用同一個 index，會搶 `index.lock`；而且 `git add -A` 會把另一個行程寫到一半的檔案一起收進去（對照組的 commit 內容會混雜 p1/p2 的檔案）。

## 任務 3：`git worktree list` 與清理

清理前（「截圖」以文字輸出代替）：

```
~/workspace/k28-ch02-practice           ff61225 [master]
~/workspace/k28-ch02-practice/wt/featA  67c9156 [feature/a]
~/workspace/k28-ch02-practice/wt/featB  dff2b84 [feature/b]
~/workspace/k28-ch02-practice/wt/race   cc47317 [race]
```

清理：

```bash
git worktree remove wt/featA
git worktree remove wt/featB
git branch -D feature/a feature/b   # 練習分支沒有合併，所以用 -D；合併過的用 -d
git worktree prune
git worktree list
```

清理後：

```
~/workspace/k28-ch02-practice  ff61225 [master]
```

## 驗收

- [x] 兩個工作樹同時各自 commit，40 次都沒有報 `index.lock`（對照組有 1 次）
- [x] 工作樹與分支的差別（見下方）
- [x] 清理後 `git worktree list` 只剩主工作樹

## 「工作樹」與「分支」的差別

| | 分支（branch） | 工作樹（worktree） |
|---|---|---|
| 本質 | 指向某個 commit 的**指標**（`refs/heads/xxx`），只是一個名字 | 磁碟上一個**實體資料夾** + 它自己的 `HEAD` 和 `index` |
| 存在哪 | `.git` 裡的一個 ref | 一個目錄（附屬工作樹的狀態存在 `.git/worktrees/<名字>/`） |
| 數量關係 | 一個 repo 可以有很多分支 | 每個工作樹同一時間只 checkout 一個分支；**同一個分支不能同時被兩個工作樹 checkout** |
| 解決什麼 | 版本歷史分叉 | 「同時」在多個分支工作，不用 stash / 切換，也不搶 index |
| 刪除 | `git branch -d` 刪的是指標，檔案不受影響 | `git worktree remove` 刪的是資料夾，分支還在 |

重點：只開分支不能解決兩個 session 互相干擾的問題，因為兩個 session 還是共用同一個資料夾和同一個 index；要多個工作樹才行。所有工作樹共用同一個 object 資料庫，所以不會像 clone 兩份那樣佔雙倍空間，commit 也會立刻在其他工作樹看到。
