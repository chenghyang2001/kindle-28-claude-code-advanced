# 練習 02 解答 — 把開隔離 worktree 包成 alias/function

> 以互動問答（Q1～Q2）方式完成。

## Q1：該用 alias 還是 function？→ **function**

需求是「吃一個參數（任務名），把它塞進**分支名**和**目錄名兩個位置**，還要 `cd` 進去」。

| | alias | function |
|---|---|---|
| 接參數塞中間 | ❌（參數只能黏在尾巴） | ✅ 用 `$1` 想塞哪塞哪 |
| 多行邏輯 | ❌ | ✅ |
| cd 改目錄 | ⚠️ 難 | ✅ |

- **alias 只是文字代換**：`alias gco='git checkout'` → `gco main` 變 `git checkout main`，參數只能接最後。
- 我們要 `feature/login-fix` 和 `../myrepo-login-fix`，同一個 `login-fix` 要塞兩個位置 → 非 function 不可。

> 記法：「只是換個短名字」用 alias；「要吃參數、跑一段邏輯」用 function。

## Q2：步驟順序 → **B → C → A → D**

```
B. git fetch origin      先更新遠端，起點才乾淨
C. git worktree add ...   開砧板 + 新分支
A. cd 進新目錄
D. 印訊息回報
```

## 交付物：ccwt function

放進 `~/.bashrc`，用法 `ccwt login-fix`：

```bash
# ccwt <task>：從乾淨的 origin 預設分支長出隔離 worktree 並進入
ccwt() {
  local task="$1"                                        # 抓參數，例如 login-fix
  local repo
  repo="$(basename "$(git rev-parse --show-toplevel)")"  # 取得目前 repo 名
  local dir="../${repo}-${task}"                         # 組出目錄名 ../myrepo-login-fix

  git fetch origin                                       # B：更新遠端
  git worktree add "$dir" -b "feature/${task}" origin/main  # C：開砧板+新分支
  cd "$dir" || return 1                                  # A：進新目錄，失敗中止
  echo "已進入隔離工作樹：$dir（分支 feature/${task}）"    # D：回報
}
```

逐行重點：
- `local`：變數只活在函式內，不污染外部環境。
- `git rev-parse --show-toplevel` + `basename`：抓出 repo 根目錄名。
- `$task` 同時用於分支名與目錄名 ← 這就是 alias 辦不到、必須用 function 的原因。
- `cd "$dir" || return 1`：cd 失敗就中止，避免在錯的目錄亂跑。
- 安裝：貼進 `~/.bashrc` → `source ~/.bashrc`（或開新終端）。

## 已知限制
- 寫死了 `origin/main`。若預設分支是 `master` 或其他名稱要改；進階做法可用 `git symbolic-ref` 自動偵測預設分支。

## 一句話總結
「吃參數 + 跑邏輯 + cd」就該用 function，不是 alias；同一個任務名塞進分支與目錄兩處，是這題的關鍵。
