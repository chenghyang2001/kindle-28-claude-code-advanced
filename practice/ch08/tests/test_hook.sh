#!/usr/bin/env bash
# bash_audit.py 單元測試：直接餵 hook JSON，檢查 exit code 與 log
set -u
cd "$(dirname "$0")/.."
export PYTHONUTF8=1 CLAUDE_PROJECT_DIR="$PWD"
H=.claude/hooks/bash_audit.py
LOG=.claude/hooks/logs/hook.log
rm -f "$LOG"
pass=0; fail=0
check() { # 名稱 預期exit 實際exit
  if [ "$2" = "$3" ]; then echo "PASS $1 (exit=$3)"; pass=$((pass+1)); else echo "FAIL $1 預期=$2 實際=$3"; fail=$((fail+1)); fi
}
mk() { printf '{"hook_event_name":"PreToolUse","session_id":"unittest1","tool_input":{"command":"%s"}}' "$1"; }

mk "ls -la"                       | python $H 2>/dev/null; check "一般指令放行" 0 $?
mk "git push origin main --force" | python $H 2>/dev/null; check "強制push阻擋" 2 $?
mk "rm -rf /"                     | python $H 2>/dev/null; check "rm-rf根目錄阻擋" 2 $?
mk "git reset --hard HEAD~1"      | python $H 2>/dev/null; check "reset-hard阻擋" 2 $?
mk "rm -rf /" | K28_HOOK_DISABLE=1 python $H 2>/dev/null; check "kill switch放行" 0 $?
echo 'not json'                   | python $H 2>/dev/null; check "壞輸入fail-open" 0 $?
echo '{"hook_event_name":"SessionStart","session_id":"unittest1","source":"startup"}' | python $H; check "SessionStart記錄" 0 $?

echo "--- log 內容 ---"; cat "$LOG"
n=$(grep -c "rm -rf /" "$LOG"); check "kill switch 時不寫 log（rm -rf / 只出現1次）" 1 "$n"
rm -f "$LOG"
echo "結果：$pass 通過 / $fail 失敗"; [ $fail -eq 0 ]
