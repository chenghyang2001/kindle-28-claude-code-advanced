#!/bin/bash
# 練習 01：在本 repo 的 ./wt/ 下建兩個 worktree，平行 commit，再完整清理
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
BASE="master"                      # 無遠端，以本地 master 取代 origin/main
LOG="$ROOT/logs/ex01-output.txt"
TMP="$ROOT/wt/_logs"
cd "$ROOT"
mkdir -p "$ROOT/logs" "$TMP"
exec > >(tee "$LOG") 2>&1

# 前次中斷殘留：先清掉（只動本練習建立的分支/目錄）
for b in feature/a feature/b race; do
  git worktree remove --force "wt/${b##*/}" 2>/dev/null || true
  git branch -D "$b" 2>/dev/null || true
done
git worktree prune

echo "=== 任務 1：建兩個 worktree（./wt/featA、./wt/featB），各自不同分支 ==="
git worktree add wt/featA -b feature/a "$BASE"
git worktree add wt/featB -b feature/b "$BASE"
git worktree list

echo
echo "=== 任務 2：兩個工作樹『同時』各改不同檔案並 commit（背景平行各 20 次）==="
commit_loop() {  # $1=目錄 $2=檔名 $3=次數
  cd "$1"
  for i in $(seq 1 "$3"); do
    echo "line $i" >> "$2"
    git add -A && git commit -qm "改 $2 第 $i 次" || { echo "FAIL in $1 第 $i 次"; return 1; }
  done
}
commit_loop "$ROOT/wt/featA" a.txt 20 > "$TMP/a.log" 2>&1 & PID_A=$!
commit_loop "$ROOT/wt/featB" b.txt 20 > "$TMP/b.log" 2>&1 & PID_B=$!
RC_A=0; wait $PID_A || RC_A=$?
RC_B=0; wait $PID_B || RC_B=$?
echo "featA 結束碼=$RC_A，featB 結束碼=$RC_B"
LOCKS=$(cat "$TMP/a.log" "$TMP/b.log" | grep -c "index.lock" || true)
if [ "$RC_A" -eq 0 ] && [ "$RC_B" -eq 0 ] && [ "$LOCKS" -eq 0 ]; then
  echo "✅ 40 次平行 commit，index.lock 錯誤 0 次"
else
  echo "❌ 失敗：index.lock 錯誤 $LOCKS 次"; cat "$TMP/a.log" "$TMP/b.log"; exit 1
fi

echo "--- 每個工作樹的 index 檔各自獨立 ---"
for d in . wt/featA wt/featB; do
  printf '%-10s -> %s\n' "$d" "$(git -C "$d" rev-parse --git-path index)"
done
echo "--- commit 互不干擾：各分支只多了自己的檔案 ---"
for b in feature/a feature/b; do
  echo "$b：比 $BASE 多 $(git rev-list --count "$BASE..$b") 個 commit，新增檔案 = $(git diff --name-only "$BASE" "$b" | tr '\n' ' ')"
done
echo "主工作樹 $BASE 仍在：$(git log -1 --format='%h %s' "$BASE")"

echo
echo "=== 對照組：同一個工作樹裡兩個行程同時 commit ==="
git worktree add -q wt/race -b race "$BASE"
race_loop() { cd "$ROOT/wt/race"; for i in $(seq 1 30); do echo "$1 $i" >> "$1.txt"; git add -A; git commit -qm "$1 $i"; done; }
race_loop p1 > "$TMP/p1.log" 2>&1 & P1=$!
race_loop p2 > "$TMP/p2.log" 2>&1 & P2=$!
wait $P1 || true; wait $P2 || true
RACE_LOCKS=$(cat "$TMP/p1.log" "$TMP/p2.log" | grep -c "index.lock" || true)
echo "同一工作樹平行 commit：index.lock 錯誤 $RACE_LOCKS 次"
cat "$TMP/p1.log" "$TMP/p2.log" | grep -m1 "index.lock" || echo "（本次碰巧沒撞到，鎖競爭有時序性）"

echo
echo "=== 任務 3：清理 ==="
echo "--- 清理前 git worktree list ---"
git worktree list
git worktree remove wt/featA
git worktree remove --force wt/race     # 對照組可能留下半途的暫存變更
git worktree remove wt/featB
git branch -D feature/a feature/b race  # 未合併所以用 -D；已合併的分支用 -d
git worktree prune
rm -rf "$TMP"
echo "--- 清理後 git worktree list ---"
git worktree list
COUNT=$(git worktree list | wc -l)
[ "$COUNT" -eq 1 ] && echo "✅ 只剩主工作樹" || { echo "❌ 還剩 $COUNT 個工作樹"; exit 1; }
echo "剩餘分支：$(git branch --format='%(refname:short)' | tr '\n' ' ')"
