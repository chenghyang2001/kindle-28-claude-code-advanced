#!/bin/bash
# ccwt / ccwt_done：一行開好（收掉）隔離 worktree
# 用法：source scripts/ccwt.sh 後
#   ccwt <task>       從預設分支長出 ./wt/<task>，分支 feature/<task>，並 cd 進去
#   ccwt_done <task>  移除 ./wt/<task> 並刪除 feature/<task>
# 本專案層版本：不寫進 ~/.bashrc；要常駐可在自己的 shell 設定裡 source 這支檔案。

# 決定乾淨起點：有遠端就 fetch 後用 origin/<預設分支>；沒遠端就用本地 main/master 分支
# 刻意不用 HEAD——HEAD 可能停在 WIP 分支上
_ccwt_base() {
  if git remote get-url origin >/dev/null 2>&1; then
    git fetch -q origin || { echo "錯誤：git fetch origin 失敗" >&2; return 1; }
    local def
    def="$(git symbolic-ref --short refs/remotes/origin/HEAD 2>/dev/null)" \
      || def="origin/$(git remote show origin | sed -n 's/.*HEAD branch: //p')"
    [ "$def" = "origin/" ] && { echo "錯誤：抓不到 origin 預設分支" >&2; return 1; }
    echo "$def"; return 0
  fi
  local b
  for b in main master; do
    git show-ref --verify -q "refs/heads/$b" && { echo "$b"; return 0; }
  done
  echo "錯誤：沒有 origin，也找不到本地 main/master" >&2; return 1
}

# 主工作樹根目錄（就算在某個 worktree 裡執行，也會回到主 repo 底下的 wt/）
_ccwt_root() {
  local common
  common="$(git rev-parse --path-format=absolute --git-common-dir 2>/dev/null)" || return 1
  # 刻意保留 git 回傳的原生格式（Windows 上是 C:/...）：若環境設了 MSYS_NO_PATHCONV=1，
  # 把 /c/... 交給 Windows 版 git 會被誤建到 C:\c\... 底下（實際踩過）
  dirname "$common"
}

# 目前目錄，格式與 _ccwt_root 一致（Git Bash 用 pwd -W 取得 C:/...，其他平台用 pwd）
_ccwt_pwd() { pwd -W 2>/dev/null || pwd; }

ccwt() {
  local task="${1:-}"
  [ -n "$task" ] || { echo "用法：ccwt <task>" >&2; return 2; }
  git check-ref-format --branch "feature/$task" >/dev/null 2>&1 \
    || { echo "錯誤：task 名稱不合法：$task" >&2; return 2; }
  local root; root="$(_ccwt_root)" || { echo "錯誤：目前不在 git repo 內" >&2; return 1; }
  local dir="$root/wt/$task" branch="feature/$task" base
  [ -e "$dir" ] && { echo "錯誤：$dir 已存在" >&2; return 1; }
  git show-ref --verify -q "refs/heads/$branch" && { echo "錯誤：分支 $branch 已存在" >&2; return 1; }
  base="$(_ccwt_base)" || return 1
  git worktree add -q "$dir" -b "$branch" "$base" || { echo "錯誤：worktree add 失敗" >&2; return 1; }
  cd "$dir" || return 1
  echo "已進入隔離工作樹：$dir（分支 $branch，起點 $base @ $(git rev-parse --short "$base")）"
}

ccwt_done() {
  local task="${1:-}"
  [ -n "$task" ] || { echo "用法：ccwt_done <task>" >&2; return 2; }
  local root; root="$(_ccwt_root)" || { echo "錯誤：目前不在 git repo 內" >&2; return 1; }
  case "$(_ccwt_pwd)" in "$root/wt/$task"*) cd "$root" || return 1 ;; esac
  git -C "$root" worktree remove "$root/wt/$task" || return 1   # 有未提交變更會被擋，避免誤刪 WIP
  git -C "$root" branch -d "feature/$task" 2>/dev/null \
    || { echo "提醒：feature/$task 尚未合併，已保留；確定不要可執行 git branch -D feature/$task"; }
  echo "已清理 wt/$task"
}
