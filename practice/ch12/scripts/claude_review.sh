#!/bin/bash
# 取 git diff 餵給 claude -p 做 code review。
# 本機：預設乾跑，審查結果寫到 review.md（用訂閱登入，不用 API key）。
# CI ：GITHUB_ACTIONS=true 且加 --post 時，用 gh 把結果貼成 PR comment。
#
# 用法：scripts/claude_review.sh [--base <ref>] [--out <檔案>] [--post]
#   --base  比對基準，預設 HEAD（本機看未 commit 的改動）；CI 傳 origin/<base 分支>
#   --out   審查結果輸出檔，預設 review.md
#   --post  貼回 PR comment（只在 CI 生效，需要 GH_TOKEN 與 PR_NUMBER）
set -euo pipefail

BASE_REF="HEAD"
OUT_FILE="review.md"
DO_POST=0
MAX_DIFF_BYTES=100000   # diff 太大會吃光 context，超過就截斷並註明

while [ $# -gt 0 ]; do
  case "$1" in
    --base) BASE_REF="${2:?--base 需要參數}"; shift 2 ;;
    --out)  OUT_FILE="${2:?--out 需要參數}"; shift 2 ;;
    --post) DO_POST=1; shift ;;
    -h|--help) sed -n '2,10p' "$0"; exit 0 ;;
    *) echo "錯誤：未知參數 $1" >&2; exit 2 ;;
  esac
done

command -v claude >/dev/null || { echo "錯誤：找不到 claude CLI" >&2; exit 1; }
git rev-parse --git-dir >/dev/null 2>&1 || { echo "錯誤：不在 git repo 內" >&2; exit 1; }

IS_CI="${GITHUB_ACTIONS:-false}"
if [ "$IS_CI" = "true" ]; then
  # CI 沒有互動登入，只能靠 Secrets 注入的 API key
  [ -n "${ANTHROPIC_API_KEY:-}" ] || { echo "錯誤：CI 缺少 ANTHROPIC_API_KEY（請設 GitHub Secrets）" >&2; exit 1; }
else
  # 本機一律走訂閱登入，避免誤扣 API Credits
  if [ -n "${ANTHROPIC_API_KEY:-}" ]; then
    echo "警告：本機偵測到 ANTHROPIC_API_KEY，已在本程序內移除，改用訂閱登入" >&2
    unset ANTHROPIC_API_KEY
  fi
fi

# 從另一個 Claude session 內呼叫時，清掉 CLAUDE* 變數讓子程序當成獨立 session
for v in $(env | grep -oE '^CLAUDE[A-Z_]*' || true); do unset "$v"; done

DIFF="$(git diff "$BASE_REF" -- . ':(exclude)answer/logs' || { echo "錯誤：git diff $BASE_REF 失敗" >&2; exit 1; })"
if [ -z "$DIFF" ]; then
  echo "沒有變更可審查（base=$BASE_REF）"
  exit 0
fi
if [ "${#DIFF}" -gt "$MAX_DIFF_BYTES" ]; then
  DIFF="${DIFF:0:$MAX_DIFF_BYTES}
...（diff 超過 ${MAX_DIFF_BYTES} 字元，以下截斷）"
fi

PROMPT='你是嚴格的 code reviewer。stdin 是一份 git diff。請只根據 diff 用繁體中文輸出 Markdown：
## 摘要（1~2 句）
## 🔴 必改（bug、安全漏洞、機密外洩；附檔名:行號與修正建議）
## 🟡 建議
## 🟢 做得好的地方
沒有項目的段落寫「無」。不要改檔、不要執行指令。'

echo "審查中（base=$BASE_REF，diff ${#DIFF} 字元）..." >&2
# --tools "" 不給任何工具：審查只需要讀 diff，避免被 diff 內容 prompt injection 誘導執行指令
# --setting-sources + disableAllHooks：不載入使用者層 hook，否則像 Stop hook 會劫持最後輸出
if ! printf '%s' "$DIFF" | claude -p "$PROMPT" --tools "" --output-format text     --setting-sources project,local --settings '{"disableAllHooks":true}' > "$OUT_FILE"; then
  echo "錯誤：claude -p 執行失敗" >&2
  exit 1
fi
[ -s "$OUT_FILE" ] || { echo "錯誤：審查結果為空" >&2; exit 1; }
echo "審查結果已寫入 $OUT_FILE" >&2

if [ "$DO_POST" -eq 1 ]; then
  if [ "$IS_CI" != "true" ]; then
    echo "乾跑模式：非 CI 環境，不貼 PR comment" >&2
  else
    : "${PR_NUMBER:?錯誤：缺少 PR_NUMBER}"
    gh pr comment "$PR_NUMBER" --body-file "$OUT_FILE" || { echo "錯誤：貼 PR comment 失敗" >&2; exit 1; }
  fi
fi
