#!/usr/bin/env bash
# 端到端驗證：用真的 claude -p（只吃本專案設定）觸發 hook，檢查 log
# 用法：bash tests/verify_e2e.sh [model|hook|kill|block|all]
set -u
cd "$(dirname "$0")/.."
shopt -s expand_aliases
source ./env.sh >/dev/null
LOG=.claude/hooks/logs/hook.log
mkdir -p .claude/hooks/logs; touch "$LOG"
OUT=tests/out; mkdir -p "$OUT"

# 只顯示本次執行新增的 log 行
mark() { wc -l < "$LOG"; }
since() { tail -n +"$(( $1 + 1 ))" "$LOG"; }

run_model() {
  echo "=== [ex01] model 預設 + permissions allowlist ==="
  ccj "用 Bash 工具執行 git status --short，然後只回覆指令輸出的行數（一個數字）。" > "$OUT/model.json"
  jq -r '"result=\(.result)\nmodels=\(.modelUsage|keys|join(","))\npermission_denials=\(.permission_denials|length)\ncost_usd=\(.total_cost_usd)"' "$OUT/model.json"
}

run_hook() {
  echo "=== [ex02] hook 觸發時機 ==="
  m=$(mark)
  ccp "用 Bash 工具執行 echo hook-trigger-test，然後只回覆 done。"
  echo "--- 本次新增 log ---"; since "$m"
}

run_kill() {
  echo "=== [ex02] kill switch K28_HOOK_DISABLE=1 ==="
  m=$(mark)
  K28_HOOK_DISABLE=1 ccp "用 Bash 工具執行 echo killswitch-test，然後只回覆 done。"
  echo "--- 本次新增 log（應為空）---"; since "$m"; echo "新增行數=$(( $(mark) - m ))"
}

run_block() {
  echo "=== [ex02] 危險指令阻擋 ==="
  m=$(mark)
  # 這是 hook 測試：沒有任何 commit，且非 allowlist，即使 hook 失效也會被權限擋下
  ccp "這是 hook 測試。請用 Bash 工具執行一次：git reset --hard HEAD 。不論成功或失敗都不要重試，只回覆你看到的錯誤訊息。"
  echo "--- 本次新增 log ---"; since "$m"
}

case "${1:-all}" in
  model) run_model ;; hook) run_hook ;; kill) run_kill ;; block) run_block ;;
  all) run_model; run_hook; run_kill; run_block ;;
esac
