#!/bin/bash
# 用 claude -p 觸發 csv-report skill 跑 3 個測試案例，輸出存 answer/logs/
set -uo pipefail
cd "$(dirname "$0")/.."
# 清掉 CLAUDE 開頭的環境變數，避免子程序被當成父 session 的延伸
for v in $(env | grep -oE '^CLAUDE[A-Z_]*'); do unset "$v"; done
unset ANTHROPIC_API_KEY
run_case() {
  local name="$1" prompt="$2"
  echo "=== $name：$prompt" > "answer/logs/skill-$name.log"
  claude -p "$prompt" --output-format stream-json --verbose \
    --allowedTools "Skill" "Bash(PYTHONUTF8=1 python *)" "Bash(python *)" "Read" \
    < /dev/null > "answer/logs/skill-$name.jsonl" 2> "answer/logs/skill-$name.stderr"
  echo "exit=$?" >> "answer/logs/skill-$name.log"
  # 擷取：是否呼叫了 Skill 工具、最終回覆
  jq -R -r 'fromjson? | select(.type=="assistant") | .message.content[]? | select(.type=="tool_use") | "TOOL_USE: \(.name) \(.input|tostring)"' \
    "answer/logs/skill-$name.jsonl" >> "answer/logs/skill-$name.log" 2>/dev/null
  jq -R -r 'fromjson? | select(.type=="result") | "RESULT: \(.result)"' "answer/logs/skill-$name.jsonl" >> "answer/logs/skill-$name.log" 2>/dev/null
  cat "answer/logs/skill-$name.log"; echo
}
run_case normal "幫我做 csv 報告：data/sales.csv"
run_case edge   "/csv-report data/edge.csv"
run_case error  "/csv-report data/missing.csv"
