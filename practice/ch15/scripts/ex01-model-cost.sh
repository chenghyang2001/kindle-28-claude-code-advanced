#!/bin/bash
# 練習 01：同一任務用不同 model 實跑 claude -p，記錄 total_cost_usd 與 duration
set -euo pipefail

# 清掉 CLAUDE 開頭的環境變數，避免繼承外層 session 設定
for var_name in $(env | grep -o '^CLAUDE[A-Za-z0-9_]*' || true); do unset "$var_name"; done

repo_root="$(cd "$(dirname "$0")/.." && pwd)"
out_dir="$repo_root/results/ex01"
mkdir -p "$out_dir"
cd "$repo_root"

# 三種任務：prompt 刻意短，以節省額度
prompt_format='把這行轉成 JSON 物件，只輸出 JSON：name=Amy age=30 city=Taipei'
prompt_analysis="以下 CSV 各區營收趨勢為何？用兩句話回答。$(cat data/sales.csv)"
prompt_reasoning='三個盒子分別標示「蘋果」「橘子」「混合」，標籤全部貼錯。只能從一個盒子拿一顆水果看，如何確定全部正確標籤？用 3 句內說明。'

run_one() {
  local task_name="$1" model_name="$2" prompt_text="$3"
  local out_file="$out_dir/${task_name}-${model_name}.json"
  echo "執行 $task_name / $model_name ..." >&2
  if ! claude -p "$prompt_text" --model "$model_name" --output-format json \
       --setting-sources project,local < /dev/null > "$out_file"; then
    echo "錯誤：$task_name / $model_name 執行失敗" >&2
  fi
}

for model_name in haiku sonnet opus; do
  run_one format "$model_name" "$prompt_format"
  run_one analysis "$model_name" "$prompt_analysis"
  run_one reasoning "$model_name" "$prompt_reasoning"
done
echo "完成，結果在 $out_dir" >&2
