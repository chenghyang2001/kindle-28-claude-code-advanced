# 練習 02 解答 — 把開隔離 worktree 包成 function

> 程式：`scripts/ccwt.sh`　測試：`bash tests/test-ccwt.sh`（輸出：`logs/ex02-test-output.txt`）
> 依限制：不寫進全域 `~/.bashrc`，改成專案內檔案，用 `source scripts/ccwt.sh` 載入。

## 任務 1：我的 function

命名規則：

- 分支：`feature/<task>`
- 目錄：`<主 repo>/wt/<task>`（依補充要求放在本資料夾內，不用 `../` 兄弟目錄）
- 起點：有 `origin` → `git fetch` 後用 `origin/<預設分支>`；沒有遠端 → 本地 `main`，找不到再用 `master`。**不用 HEAD。**

```bash
source scripts/ccwt.sh
ccwt login-fix        # 建立 wt/login-fix（分支 feature/login-fix）並 cd 進去
# ...在這裡起 claude、改檔、commit...
ccwt_done login-fix   # 回主目錄、移除工作樹；分支已合併才刪，沒合併就保留並提醒
```

和題目範例相比多加的部分：

| 加強 | 理由 |
|---|---|
| 沒給 task、或名稱不是合法分支名（`git check-ref-format`）→ 結束碼 2 | 避免建出奇怪的分支 |
| 目錄或分支已存在就拒絕 | 不覆蓋別人的工作 |
| 沒有遠端時改用本地 main/master；`origin/HEAD` 沒設定時改問 `git remote show origin` | 題目範例在這兩種情況下會直接失敗 |
| 在任何附屬工作樹裡執行，目錄都會算到**主 repo** 的 `wt/` 下 | 避免 `wt/a/wt/b` 這種一層層巢狀 |
| 傳給 git 的路徑用 git 回傳的 `C:/...` 格式 | 這台機器有設 `MSYS_NO_PATHCONV=1`，把 `/c/...` 傳給 Windows 版 git 會被建到 `C:\c\...`（實際踩到） |
| `ccwt_done`：有未提交變更就拒絕刪除；分支用 `-d`（未合併會保留） | 收尾時不誤刪成果 |

## 任務 2：證明是從乾淨起點長出

測試做法：先做一個「髒」的環境——工作樹 `wt/wip` 在 `feature/wip` 分支上，多一個沒合併的 commit（`wip-commit.txt`），還有一個沒 commit 的檔案（`wip-dirty.txt`）。**在這個髒環境裡**執行 `ccwt clean-start`：

```
HEAD = 1bdc3bb（master = ff61225），另有未追蹤檔 wip-dirty.txt
已進入隔離工作樹：.../wt/clean-start（分支 feature/clean-start，起點 master @ ff61225）
  ✅ 起點 = master，不是 WIP 的 HEAD
  ✅ 沒帶到 WIP 的 commit 檔
  ✅ 沒帶到未提交的髒檔
  ✅ 工作樹乾淨
...
結果：PASS=16 FAIL=0
```

16 項全部通過：正常流程 7 項、錯誤案例 3 項、`ccwt_done` 清理 3 項、題目範例 `login-fix` 全流程 3 項。

> 本 repo 沒有遠端，所以實測的是「本地 master」這條路徑；`origin/<預設分支>` 那條路徑只有程式，沒有實測（見 NOTES.md）。

## 延伸思考：為什麼從 `origin/<預設分支>` 起，而不是本地 HEAD？

`git worktree add -b X` 不給起點時用的是**目前的 HEAD**。HEAD 很可能是髒的：

1. **夾帶別人的半成品**：HEAD 可能停在另一個功能分支上，或本地 main 有還沒 push 的實驗 commit。新任務的分支會繼承這些 commit，PR 裡就混進無關的改動，review 看不懂，也沒辦法單獨合併或回滾。
2. **基底過舊**：本地 main 很久沒 pull，新分支一開始就落後遠端，合併時容易衝突，也可能是在已經修好的 bug 上繼續開發。
3. **結果無法重現**：每個人的本地 HEAD 都不同，「在我這裡可以跑」常常是因為多帶了某些本地 commit。從 `origin/<預設分支>` 起，大家的起點一樣，CI 跑的也是這個。
4. **多 session 情境更明顯**：另一個 session 可能正在主目錄改檔或切分支，HEAD 隨時會變。用固定的遠端 ref 當起點就不受影響。

另外：工作目錄裡沒 commit 的改動本來就不會被帶進新工作樹，**帶進去的是 commit**。所以危險的是「HEAD 指向哪個 commit」，這也是為什麼測試要特別做一個「有未合併 commit 的 WIP 分支」來驗證。
