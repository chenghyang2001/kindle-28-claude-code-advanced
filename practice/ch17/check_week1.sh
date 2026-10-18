#!/bin/bash
# 練習 02：第 1 週目標自動驗收（環境配置 + 平行化套進日常工作流）
# 用法：
#   bash check_week1.sh            實際檢查（全部唯讀，不改任何檔案）
#   bash check_week1.sh --dry-run  只列出會檢查什麼，不執行
# 結束碼：0 = 全部達成；1 = 有未達成項目
set -euo pipefail

REPO_DIR="$(cd "$(dirname "$0")" && pwd)"
DRY_RUN=0
[ "${1:-}" = "--dry-run" ] && DRY_RUN=1

pass_count=0
fail_count=0

# 執行一項檢查：$1 說明，$2 要執行的指令字串
run_check() {
  local desc="$1" cmd="$2"
  if [ "$DRY_RUN" -eq 1 ]; then
    echo "[DRY] $desc"
    echo "      指令：$cmd"
    return 0
  fi
  if (cd "$REPO_DIR" && eval "$cmd") >/dev/null 2>&1; then
    echo "[PASS] $desc"
    pass_count=$((pass_count + 1))
  else
    echo "[FAIL] $desc"
    fail_count=$((fail_count + 1))
  fi
}

echo "第 1 週驗收：$REPO_DIR"
echo "----------------------------------------"

# 1. 專案層設定存在且是合法 JSON、含 permissions.allow（環境配置）
run_check "專案層 .claude/settings.local.json 合法且有 permissions.allow" \
  "PYTHONUTF8=1 python -c \"import json,sys; d=json.load(open('.claude/settings.local.json',encoding='utf-8')); sys.exit(0 if d.get('permissions',{}).get('allow') else 1)\""

# 2. 專案 CLAUDE.md 至少 5 行（有實際寫規則，不是空檔）
run_check "CLAUDE.md 至少 5 行" \
  "[ -f CLAUDE.md ] && [ \$(wc -l < CLAUDE.md) -ge 5 ]"

# 3. 至少同時存在 2 個 worktree（主目錄 + 1 個平行工作區）
run_check "git worktree 至少 2 個（實際用過平行化）" \
  "[ \$(git worktree list | wc -l) -ge 2 ]"

# 4. 學習日誌至少 3 天有記錄（每天實際用上，不是只讀過）
run_check "learning-log/week1.md 至少 3 筆日期記錄" \
  "[ \$(grep -cE '^- [0-9]{4}-[0-9]{2}-[0-9]{2}' learning-log/week1.md) -ge 3 ]"

echo "----------------------------------------"
if [ "$DRY_RUN" -eq 1 ]; then
  echo "乾跑模式：未執行任何檢查"
  exit 0
fi
echo "結果：PASS $pass_count / FAIL $fail_count"
if [ "$fail_count" -gt 0 ]; then
  echo "第 1 週目標：未達成"
  exit 1
fi
echo "第 1 週目標：達成"
