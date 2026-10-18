#!/bin/bash
# 在乾淨沙盒用 claude -p（haiku）跑一個 prompt，結果複製回 ex01/runs/<名稱>/
# 用法：bash ex01/run_sandbox.sh <weak|strong> [global|clean]
#   global：沿用使用者全域設定（會載入 ~/.claude/CLAUDE.md）
#   clean ：--setting-sources project,local，不載入全域 CLAUDE.md／hooks
set -euo pipefail

name="${1:?用法：run_sandbox.sh <weak|strong> [global|clean]}"
mode="${2:-global}"
extra=()
case "$mode" in
  global) ;;
  clean) extra=(--setting-sources project,local) ;;
  *) echo "錯誤：mode 只能是 global 或 clean"; exit 1 ;;
esac
here="$(cd "$(dirname "$0")" && pwd)"
prompt_file="$here/prompts/$name.txt"
[ -f "$prompt_file" ] || { echo "錯誤：找不到 $prompt_file"; exit 1; }

# 沙盒放在系統暫存區，避開本專案 CLAUDE.md 的影響
sandbox="$(mktemp -d "${TMPDIR:-/tmp}/k28-ex01-$name-$mode-XXXX")"
out="$here/runs/$name-$mode"
rm -rf "$out" && mkdir -p "$out"

# 清掉 CLAUDE 開頭環境變數，避免子程序被當成本 session 的 child
clean_env=()
for v in $(env | grep -o '^CLAUDE[A-Za-z0-9_]*' || true); do clean_env+=(-u "$v"); done

start=$(date +%s)
(cd "$sandbox" && env "${clean_env[@]}" DISABLE_WRITER_QA_HOOK=1 \
  claude -p "$(cat "$prompt_file")" --model haiku \
  --dangerously-skip-permissions --output-format text "${extra[@]}") \
  > "$out/claude-output.txt" 2>&1 || echo "警告：claude -p 回傳非 0" >> "$out/claude-output.txt"
echo "耗時秒數：$(( $(date +%s) - start ))" > "$out/meta.txt"
echo "沙盒：$sandbox" >> "$out/meta.txt"

# 複製產出（排除快取）
mkdir -p "$out/src"
cp -r "$sandbox"/. "$out/src/"
find "$out/src" -type d \( -name __pycache__ -o -name .pytest_cache \) -prune -exec rm -rf {} +
(cd "$out/src" && find . -type f | sort) > "$out/files.txt"
echo "完成：$out"
