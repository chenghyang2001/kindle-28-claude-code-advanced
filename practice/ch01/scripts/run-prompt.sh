#!/bin/bash
# 在獨立沙盒跑一次 claude -p，量化回合數／成本／耗時
# 用法：scripts/run-prompt.sh <run 名稱> <prompt 檔> [fixture 子目錄...]
# 例：  scripts/run-prompt.sh ex01-vague prompts/ex01-vague.txt notes
set -euo pipefail

if [ $# -lt 2 ]; then
  echo "用法：$0 <run 名稱> <prompt 檔> [fixture 子目錄...]" >&2
  exit 1
fi

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
RUN_NAME="$1"; PROMPT_FILE="$2"; shift 2
RUN_DIR="$ROOT/runs/$RUN_NAME"

[ -f "$PROMPT_FILE" ] || { echo "錯誤：找不到 prompt 檔 $PROMPT_FILE" >&2; exit 1; }

# 每次重建沙盒，避免上一輪產物影響判斷
rm -rf "$RUN_DIR"
mkdir -p "$RUN_DIR"
for sub in "$@"; do
  cp -r "$ROOT/fixtures/$sub" "$RUN_DIR/" || { echo "錯誤：複製 fixtures/$sub 失敗" >&2; exit 1; }
done

# 題目要求：呼叫 claude -p 前清掉所有 CLAUDE 開頭的環境變數（避免被當成子 session）
UNSET_ARGS=()
while IFS= read -r name; do
  UNSET_ARGS+=(-u "$name")
done < <(env | grep -o '^CLAUDE[A-Za-z0-9_]*' || true)

cd "$RUN_DIR"
env "${UNSET_ARGS[@]}" claude -p "$(cat "$ROOT/$PROMPT_FILE")" \
  --output-format json \
  --allowedTools "Bash Read Write Edit Glob Grep" \
  > "$RUN_DIR/_result.json" 2> "$RUN_DIR/_stderr.log" \
  || { echo "錯誤：claude -p 執行失敗，見 $RUN_DIR/_stderr.log" >&2; exit 1; }

echo "完成：$RUN_DIR/_result.json"
