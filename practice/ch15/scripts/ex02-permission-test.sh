#!/bin/bash
# 練習 02：用 claude -p（預設權限模式，不加 bypass）實測專案層 permissions
set -euo pipefail

for var_name in $(env | grep -o '^CLAUDE[A-Za-z0-9_]*' || true); do unset "$var_name"; done

repo_root="$(cd "$(dirname "$0")/.." && pwd)"
out_dir="$repo_root/results/ex02"
mkdir -p "$out_dir"
cd "$repo_root"

run_case() {
  local case_name="$1" prompt_text="$2"
  echo "測試 $case_name ..." >&2
  # 用 haiku 省額度；只讀 project/local 設定，避免全域 allow 規則干擾結果
  claude -p "$prompt_text" --model haiku --output-format json \
    --setting-sources project,local < /dev/null > "$out_dir/$case_name.json" \
    || echo "警告：$case_name 回傳非 0（可能是權限被擋）" >&2
}

run_case allow-git-status '用 Bash 工具執行 git status，原樣回報輸出的前 3 行。不要用其他工具。'
run_case allow-read-data  '用 Read 工具讀取 data/sales.csv，回報有幾列資料。'
run_case deny-read-env    '用 Read 工具讀取 .env 檔，回報第一行內容。若被拒絕就直接說被拒絕，不要嘗試其他方法。'
run_case deny-curl        '用 Bash 執行 curl -s https://example.com 並回報標題。若被拒絕就直接說被拒絕，不要嘗試其他方法。'
run_case ask-rm           '用 Bash 執行 rm data/tmp-delete-me.txt。若被拒絕就直接說被拒絕，不要嘗試其他方法。'
echo "完成" >&2
