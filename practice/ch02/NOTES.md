# NOTES — K28 第 2 章練習（git worktree）

快速 demo 模式：主 Claude 直接寫檔，沒有經過 code-writer / QA / reviewer 三 agent 流程。

## 做了什麼

| 檔案 | 說明 |
|---|---|
| `scripts/ex01-demo.sh` | 練習 01 一鍵執行：建 `wt/featA`、`wt/featB` → 兩邊同時 commit 各 20 次 → 對照組（同一工作樹兩個行程同時 commit）→ 清理 |
| `scripts/ccwt.sh` | 練習 02：`ccwt <task>` / `ccwt_done <task>` function |
| `tests/test-ccwt.sh` | `ccwt` 測試：16 項（正常流程、錯誤案例、清理、題目範例） |
| `logs/ex01-output.txt`、`logs/ex02-test-output.txt` | 實際執行輸出 |
| `answer/ex01-answer.md`、`answer/ex02-answer.md` | 解答 |
| `.gitignore` | 排除 `wt/` 和當機殘留檔 |

## 驗證結果

- 練習 01：`bash scripts/ex01-demo.sh` 結束碼 0
  - 兩個工作樹同時各 commit 20 次，`index.lock` 錯誤 **0 次**；兩個分支各自只多了自己的檔案
  - 對照組（同一工作樹）`index.lock` 錯誤 **1 次**，重現了題目情境說明的問題（鎖的競爭跟時機有關，每次跑的次數會不同）
  - 清理後 `git worktree list` 只剩主工作樹，分支只剩 `master`
- 練習 02：`bash tests/test-ccwt.sh` → **PASS=16 FAIL=0**
- 兩支腳本都過 `bash -n` 語法檢查；沒有跑 shellcheck（本機沒裝）

## 和題目要求的差異

1. **worktree 位置**：題目用 `../myrepo-featA` 兄弟目錄；依你的補充改成本資料夾的 `./wt/featA`、`./wt/featB`，`wt/` 已加進 `.gitignore`。
2. **起點**：題目用 `origin/main`；本 repo 沒有遠端，所以用本地 `master`。為了有起點，先做了一個初始 commit（`ff61225`）。
3. **`~/.bashrc`**：沒動全域設定，function 放在 `scripts/ccwt.sh`，要用的時候自己 `source`。
4. **截圖**：`git worktree list` 用文字輸出（`logs/ex01-output.txt` 和解答內）代替圖片。
5. **origin 那條路徑沒實測**：`ccwt` 有「有遠端就 fetch + 用 `origin/<預設分支>`」的程式，但本 repo 沒遠端，只實測了本地 master 那條路徑。
6. **分支刪除**：題目範例用 `git branch -d`；練習分支有 commit 但沒有合併，`-d` 會被拒絕，所以 ex01 用 `-D`。`ccwt_done` 則刻意用 `-d`，沒合併就保留分支。

## 踩到的坑（重要）

- **`MSYS_NO_PATHCONV=1` + Windows 版 git**：這台機器的環境設了這個變數，Git Bash 的 `/c/Users/...` 路徑會原樣傳給 git，git 把它當成 `C:\c\Users\...`。第一次嘗試和 `ccwt` 初版因此把目錄誤建到了 **`C:\c\Users\user\workspace\k28-ch02-practice\`**（裡面是 `sandbox/`、`wt/`，都是本 session 的殘留，沒有其他用途）。
  - 已修正：`ccwt` 改用 git 自己回傳的 `C:/...` 路徑，比對目錄時用 `pwd -W`。
  - **殘留目錄沒刪**：刪除資料夾外目錄的指令被權限擋下。請手動刪 `C:\c\Users\user\workspace\k28-ch02-practice`。只刪這一個子目錄，`C:\c` 底下其他東西是別的 session 留下的，我沒碰。
- 在 `$(...)` 或 pipe 裡呼叫 `ccwt`，`cd` 會發生在子 shell，不會回到外層——要直接呼叫。

## 已知沒處理的風險（快速模式）

- 沒有在 Linux/macOS 實測（`pwd -W` 不存在時會改用 `pwd`，理論上可以用）。
- `ccwt` 不會檢查 `wt/` 有沒有在 `.gitignore` 裡；在別的 repo 用要自己加。
