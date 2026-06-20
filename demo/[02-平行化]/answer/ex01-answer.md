# 練習 01 解答 — 用 git worktree 隔離兩個 session

> 以互動問答（Q1～Q5）方式完成，含實跑驗證。

## 核心問題：兩個 session 待在同一資料夾為什麼會打架（Q1）

| 層級 | 衝突 | 原因 |
|------|------|------|
| 1 工作目錄 | 互相覆蓋檔案 | 兩 session 看到磁碟同一份檔案 |
| 2 index 暫存區 | 誤抓對方 WIP | 整個資料夾只有一個 git index，`git add -A` 會掃到別人做一半的東西 |
| 3 index.lock | commit 報錯 | git 動 index 時建 `.git/index.lock`，兩操作同時來 → `Unable to create '.git/index.lock'` |

> 比喻：兩個廚師擠同一塊砧板——食材混、刀搶、誰也做不好。

## worktree 怎麼解決（Q2）

`git worktree` 給每個 session **一塊自己的砧板**：獨立工作目錄 + 獨立 index + 獨立 index.lock，
但**共用同一個 `.git` 歷史資料庫**（同一個冰箱）。比 `git clone` 輕——不必把歷史再抄一份。

## 開 worktree 的指令（Q3）

```bash
git worktree add ../myrepo-featA -b feature/a origin/main
```
| 部分 | 意思 |
|------|------|
| `git worktree add` | 開一塊新砧板（新工作目錄） |
| `../myrepo-featA` | 開在隔壁資料夾（`..` 上一層），不塞進現有 repo |
| `-b feature/a` | 順手建一條新分支 feature/a |
| `origin/main` | 從遠端乾淨的 main 長出（避免沾本地 WIP）；前面通常先 `git fetch origin` |

## 實跑驗證：兩 worktree 各自 commit 不撞鎖（Q4）

實際建 main + 兩個 worktree，兩邊各改不同檔、各自 commit：

```
$ git worktree add ../myrepo-featA -b feature/a
$ git worktree add ../myrepo-featB -b feature/b
$ git commit -m "featA: 加 a.txt"   → [feature/a 6b21bba]  成功 ✅
$ git commit -m "featB: 加 b.txt"   → [feature/b 69db907]  成功 ✅
$ git worktree list
  .../myrepo         [main]
  .../myrepo-featA   [feature/a]
  .../myrepo-featB   [feature/b]
```
- 兩邊 commit **都成功、無 index.lock 錯誤**（各有各的 index）。
- featA 目錄只有 `a.txt`、featB 只有 `b.txt`——**工作目錄互相隔離**。

## 收尾紀律（Q5）

```bash
git worktree remove ../myrepo-featA   # 1. 收砧板（有未 commit 改動會被擋，硬拆才 --force）
git branch -d feature/a               # 2. 砍分支（worktree remove 不會自動刪分支！）
git worktree list                     # 3. 確認只剩該留的
# 若手動刪了 worktree 資料夾，補：git worktree prune  清幽靈登記
```

**最關鍵的觀念**：worktree（砧板/工作目錄）與 branch（分支）是**兩回事**。
`worktree remove` 只收工作目錄，分支不會自動消失，要 `branch -d` 另外砍——**兩步分開做**。

## 一句話總結
平行 session 不打架的根本原因＝**各有各的工作目錄與 index**；用完記得「收砧板 + 砍分支」兩步收尾。
