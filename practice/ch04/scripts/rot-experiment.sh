#!/bin/bash
# 練習 01：用 claude -p + --resume 把同一個 session 撐長，觀察脈絡腐化
# 用法：bash scripts/rot-experiment.sh [--dry-run]
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
LAB="$ROOT/rot-lab"
LOG="$ROOT/logs/${ROT_LOG:-rot-run}.jsonl"
MODEL="${ROT_MODEL:-haiku}"   # 小模型較容易看到腐化，也省額度
DRY_RUN=0
[ "${1:-}" = "--dry-run" ] && DRY_RUN=1

# 題目要求：呼叫 claude -p 前清掉 CLAUDE 開頭的環境變數（避免被當成巢狀 session）
for v in $(env | grep -o '^CLAUDE[A-Za-z0-9_]*' || true); do unset "$v"; done

command -v claude >/dev/null || { echo "錯誤：找不到 claude CLI" >&2; exit 1; }
command -v jq >/dev/null || { echo "錯誤：找不到 jq" >&2; exit 1; }

cd "$LAB"
: > "$LOG"
SID=""

ask() {  # $1=回合標籤 $2=prompt
  local tag="$1" prompt="$2" out
  echo "=== [$tag] $prompt" | head -c 200; echo
  if [ "$DRY_RUN" = 1 ]; then return 0; fi
  local args=(-p "$prompt" --model "$MODEL" --output-format json
              --setting-sources project,local
              --permission-mode acceptEdits --allowedTools "Read Write Glob Grep")
  [ -n "$SID" ] && args+=(--resume "$SID")
  out="$(claude "${args[@]}" 2>&1)" || { echo "錯誤：[$tag] claude 回傳非 0：$out" >&2; exit 1; }
  SID="$(echo "$out" | jq -r '.session_id')"
  echo "$out" | jq -c --arg tag "$tag" '{tag:$tag, session_id, num_turns, cost:.total_cost_usd,
     ctx_in:((.usage.input_tokens//0)+(.usage.cache_read_input_tokens//0)+(.usage.cache_creation_input_tokens//0)),
     result}' >> "$LOG"
  echo "$out" | jq -r '.result' | head -c 600; echo
}

ask T01 "本 session 的固定決策，請記住直到最後：(1) 專案代號 ORCA-7 (2) 所有日期一律寫成 YYYY/MM/DD (3) 輸出檔一律放 out/、檔名小寫加連字號 (4) 輸出內容禁止使用 emoji (5) 每份輸出檔第一行必須是『# ORCA-7』。只回覆『已記下』。"
ask T02 "讀 data/sales.csv，算各區總額，寫成 out/sales-summary.md。"
ask T03 "讀 notes/ 下所有檔案，把待辦事項整理成 out/action-items.md，並告訴我 notes/config.md 的 port。"

# 中途偷改檔：session 不知道 config.md 已改
[ "$DRY_RUN" = 0 ] && sed -i 's/port: 8080/port: 9090/' notes/config.md

ask T04 "讀完整的 data/big-log-1.txt（全部 1800 行），統計每個 ERROR code 的次數，列表回覆。"
ask T05 "讀完整的 data/big-log-2.txt（全部 1800 行），統計每個 ERROR code 的次數，列表回覆。"
ask T06 "比較兩份 log：哪個檔的 E202 比較多？各多少？寫成 out/log-compare.md。"
ask T07 "再把 data/big-log-1.txt 前 600 行中 latency_ms 超過 800 的請求列出 req_id（最多 10 筆）。"
ask T08 "替會議 02 的每個待辦寫一段 100 字的執行建議，寫成 out/meeting-02-plan.md。"
ask T09 "不要讀任何檔案，直接憑記憶回答：notes/config.md 的 port 現在是多少？"
ask T10 "不要讀任何檔案，直接憑記憶回答：本 session 一開始定的 5 條固定決策是什麼？"
ask T11 "寫一份今天（2026-10-18）的總結 out/Final Report.md，列出今天產出的所有檔案。"
ask T12 "現在讀 notes/config.md，port 是多少？和你在 T09 的回答一樣嗎？"

# 還原被改的檔，方便重跑
[ "$DRY_RUN" = 0 ] && sed -i 's/port: 9090/port: 8080/' notes/config.md
echo "完成。session_id=$SID，紀錄在 $LOG"
