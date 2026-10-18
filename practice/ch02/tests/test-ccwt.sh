#!/bin/bash
# ccwt 測試：證明它從乾淨起點（本地 master）長出，而非髒掉的 HEAD
set -uo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
winpwd() { pwd -W 2>/dev/null || pwd; }   # 統一路徑格式再比對
cd "$ROOT"
# shellcheck source=../scripts/ccwt.sh
source scripts/ccwt.sh
PASS=0; FAIL=0
check() { if eval "$2"; then echo "  ✅ $1"; PASS=$((PASS+1)); else echo "  ❌ $1"; FAIL=$((FAIL+1)); fi; }
cleanup() {
  cd "$ROOT"
  for t in wip clean-start login-fix; do git worktree remove --force "wt/$t" 2>/dev/null; done
  git branch -D feature/wip feature/clean-start feature/login-fix 2>/dev/null
  git worktree prune
}
cleanup >/dev/null 2>&1
MASTER_SHA="$(git rev-parse master)"

echo "[準備] 做一個『髒』的工作環境：WIP 分支 + 未推的 commit + 未提交的變更"
git worktree add -q wt/wip -b feature/wip master
cd wt/wip
echo "半成品" > wip-commit.txt && git add . && git commit -qm "WIP：還沒完成" 
echo "未存檔的改動" > wip-dirty.txt
echo "  HEAD = $(git rev-parse --short HEAD)（master = ${MASTER_SHA:0:7}），另有未追蹤檔 wip-dirty.txt"

echo "[測試 1] 在髒環境裡執行 ccwt clean-start（happy path）"
ccwt clean-start > "$ROOT/logs/.ccwt.out" 2>&1; RC=$?   # 不能用 $(...)：子 shell 裡的 cd 不會生效
echo "  $(cat "$ROOT/logs/.ccwt.out")"; rm -f "$ROOT/logs/.ccwt.out"
check "結束碼為 0" "[ $RC -eq 0 ]"
check "已 cd 進 wt/clean-start" "[ \"\$(winpwd)\" = \"\$(cd $ROOT/wt/clean-start && winpwd)\" ]"
check "分支為 feature/clean-start" "[ \"\$(git branch --show-current)\" = feature/clean-start ]"
check "起點 = master，不是 WIP 的 HEAD" "[ \"\$(git rev-parse HEAD)\" = \"$MASTER_SHA\" ]"
check "沒帶到 WIP 的 commit 檔" "[ ! -e wip-commit.txt ]"
check "沒帶到未提交的髒檔" "[ ! -e wip-dirty.txt ]"
check "工作樹乾淨" "[ -z \"\$(git status --porcelain)\" ]"

echo "[測試 2] 錯誤案例"
cd "$ROOT"
ccwt >/dev/null 2>&1; check "沒給 task → 結束碼 2" "[ $? -eq 2 ]"
ccwt 'bad..name' >/dev/null 2>&1; check "不合法分支名 → 結束碼 2" "[ $? -eq 2 ]"
ccwt clean-start >/dev/null 2>&1; check "目錄已存在 → 拒絕" "[ $? -ne 0 ]"

echo "[測試 3] ccwt_done 清理（含：有未提交變更時會擋下）"
echo x > wt/clean-start/tmp.txt
ccwt_done clean-start >/dev/null 2>&1; check "有髒檔時拒絕刪除" "[ -d wt/clean-start ]"
rm wt/clean-start/tmp.txt
ccwt_done clean-start >/dev/null; check "乾淨時移除目錄" "[ ! -e wt/clean-start ]"
check "已合併(無新 commit)的分支被刪除" "! git show-ref -q --verify refs/heads/feature/clean-start"

echo "[測試 4] 題目範例：ccwt login-fix → 改檔 commit → ccwt_done"
ccwt login-fix >/dev/null && echo fix > fix.txt && git add -A && git commit -qm "修 login"
ccwt_done login-fix   # 不接 pipe，讓 cd 回主目錄在本 shell 生效
check "未合併分支被保留（避免誤刪工作成果）" "git show-ref -q --verify refs/heads/feature/login-fix"

cleanup >/dev/null 2>&1
check "ccwt_done 後回到主目錄" "[ \"\$(winpwd)\" = \"\$(cd $ROOT && winpwd)\" ]"
check "最後只剩主工作樹" "[ \$(git worktree list | wc -l) -eq 1 ]"
echo "結果：PASS=$PASS FAIL=$FAIL"
[ $FAIL -eq 0 ]
