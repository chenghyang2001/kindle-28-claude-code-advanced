#!/bin/bash
# Ralph 式自主迴圈（bash + claude -p），附四道護欄：
#   1. 迭代硬上限 MAX（預設 6）
#   2. 每輪跑 pytest，紅燈立刻停（不 commit、保留現場）
#   3. 每輪綠燈就 git commit 一個檢查點（可回滾）
#   4. 連續 STALL_LIMIT 輪（預設 2）未完成任何項目即停（防空轉）
# 用法：timeout 1200 bash ralph.sh <工作目錄>
# 結束碼：0=收斂  2=測試紅燈  3=無進展  4=達上限  1=使用錯誤
set -euo pipefail

WORKDIR="${1:?用法：bash ralph.sh <工作目錄>}"
MAX="${MAX:-6}"
STALL_LIMIT="${STALL_LIMIT:-2}"
CALL_TIMEOUT="${CALL_TIMEOUT:-300}"   # 單次 claude -p 最多跑幾秒
MODEL="${MODEL:-haiku}"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROMPT_FILE="$SCRIPT_DIR/PROMPT.md"

[ -d "$WORKDIR" ] || { echo "錯誤：找不到工作目錄 $WORKDIR" >&2; exit 1; }
[ -f "$WORKDIR/TASK.md" ] || { echo "錯誤：$WORKDIR 缺 TASK.md" >&2; exit 1; }
[ -f "$PROMPT_FILE" ] || { echo "錯誤：缺 $PROMPT_FILE" >&2; exit 1; }
cd "$WORKDIR"
git rev-parse --is-inside-work-tree >/dev/null 2>&1 || { echo "錯誤：$WORKDIR 不在 git repo 內" >&2; exit 1; }

# 子 claude 不可繼承本 session 的 CLAUDE* 變數，否則會被當成巢狀 session
for v in $(compgen -e | grep '^CLAUDE' || true); do unset "$v"; done
# 子 claude 不吃使用者全域 hooks（寫檔攔截 hook 會擋住自動寫 .py）
export DISABLE_WRITER_QA_HOOK=1 PYTHONUTF8=1 PYTHONDONTWRITEBYTECODE=1
# 迴圈自己的 log 與 pycache 不算「進展」，不可進檢查點（首版踩過：無進展輪也被 commit）
EXCLUDE_FILE="$(git rev-parse --git-path info/exclude)"
grep -qx '.ralph-\*' "$EXCLUDE_FILE" 2>/dev/null || printf '.ralph-*\n__pycache__/\n' >> "$EXCLUDE_FILE"

log() { echo "[ralph $(date +%H:%M:%S)] $*"; }
unchecked() { grep -c '^- \[ \]' TASK.md || true; }

# 只 commit 工作目錄內的檔案（pathspec "."），不碰 repo 其他地方
checkpoint() {
  git add -A -- .
  if git diff --cached --quiet -- .; then
    log "本輪無檔案變動，跳過 commit"
  else
    git commit -q -m "$1" -- . && log "已 commit 檢查點：$(git rev-parse --short HEAD)"
  fi
}

run_tests() {
  local rc=0
  python -m pytest -q >".ralph-pytest.log" 2>&1 || rc=$?
  # rc=5 代表「沒有收集到任何測試」，視為綠燈（第 0 輪還沒有測試）
  [ "$rc" -eq 0 ] || [ "$rc" -eq 5 ]
}

checkpoint "ralph: 基線（第 0 輪）"
stall=0
for i in $(seq 1 "$MAX"); do
  before=$(unchecked)
  if [ "$before" -eq 0 ]; then log "TASK.md 已無未完成項目，收斂"; exit 0; fi
  log "第 $i/$MAX 輪開始，未完成 $before 項"

  rc=0
  timeout "$CALL_TIMEOUT" claude -p "$(cat "$PROMPT_FILE")" \
    --model "$MODEL" \
    --setting-sources project,local \
    --permission-mode acceptEdits \
    --allowedTools "Read,Write,Edit,Glob,Grep" \
    --disallowedTools "Bash" \
    >".ralph-round-$i.log" 2>&1 || rc=$?
  [ "$rc" -eq 0 ] || log "警告：claude -p 結束碼 $rc（124=逾時），交給後續護欄判斷"
  log "claude 回覆：$(tail -c 300 ".ralph-round-$i.log" | tr '\n' ' ')"

  # 護欄 2：紅燈即停，不 commit，保留現場給人看
  if ! run_tests; then
    log "🔴 第 $i 輪 pytest 紅燈，停止迴圈（未 commit，現場保留）"
    tail -n 15 .ralph-pytest.log
    exit 2
  fi
  log "🟢 pytest：$(tail -n 1 .ralph-pytest.log)"

  # 護欄 3：綠燈就留檢查點
  checkpoint "ralph: 第 $i 輪檢查點"

  after=$(unchecked)
  if [ "$after" -eq 0 ]; then log "✅ 全部完成於第 $i 輪"; exit 0; fi

  # 護欄 4：未完成數沒有下降就算無進展
  if [ "$after" -lt "$before" ]; then
    stall=0
  else
    stall=$((stall + 1))
    log "⚠️ 本輪無進展（連續 $stall/$STALL_LIMIT 輪）"
    if [ "$stall" -ge "$STALL_LIMIT" ]; then
      log "⛔ 連續 $STALL_LIMIT 輪無進展，停止迴圈"
      exit 3
    fi
  fi
done

# 護欄 1：硬上限
log "⛔ 已達迭代上限 $MAX 輪仍未收斂，停止"
exit 4
