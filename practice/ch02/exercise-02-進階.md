# 練習 02 — 進階：把開隔離 worktree 包成 alias

## 情境說明
每次手動 `worktree add` + `cd` + 起 Claude 很煩。把它包成一個 shell function，一行開好乾淨起點的工作樹。

## 範例：bash function（放進 ~/.bashrc）
```bash
# ccwt <task>：從 origin 預設分支長出乾淨 worktree 並進入
ccwt() {
  local task="$1"
  local repo; repo="$(basename "$(git rev-parse --show-toplevel)")"
  local dir="../${repo}-${task}"
  git fetch origin
  git worktree add "$dir" -b "feature/${task}" "origin/$(git symbolic-ref --short refs/remotes/origin/HEAD | sed 's@^origin/@@')"
  cd "$dir" || return 1
  echo "已進入隔離工作樹：$dir（分支 feature/${task}）"
  # 接著就可以在這裡起 claude
}
```
使用：`ccwt login-fix`

## 任務
### 任務 1
寫出你自己的 alias / function（含分支命名規則，例如 `feature/<task>`）。

### 任務 2
測試它能從乾淨起點（`origin/main` fetch 後）長出工作樹，而非從髒掉的本地 HEAD。

## 延伸思考
為何要從 `origin/<預設分支>` 起、而不是本地 HEAD？髒起點會帶來什麼問題？

## 完成後
將解答存入 `answer/ex02-answer.md`。
