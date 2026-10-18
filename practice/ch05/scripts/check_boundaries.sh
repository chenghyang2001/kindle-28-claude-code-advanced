#!/bin/bash
set -euo pipefail
# 越權檢查：比對兩個 commit 之間的變更檔，確認都在該角色允許清單內
# 用法：scripts/check_boundaries.sh <role> <base-commit> <head-commit>
role="${1:?缺 role}"; base="${2:?缺 base}"; head="${3:?缺 head}"
case "$role" in
  researcher) allow='^(docs/research\.md|signals/DONE\.md)$' ;;
  builder)    allow='^(src/pricing\.py|tests/test_pricing\.py|signals/BUILD_COMPLETE\.md)$' ;;
  reviewer)   allow='^(reviews/REVIEW\.md|signals/REVIEW_COMPLETE\.md)$' ;;
  *) echo "未知 role：$role" >&2; exit 2 ;;
esac
changed=$(git diff --name-only "$base" "$head")
echo "[$role] $base..$head 變更檔："; echo "${changed:-（無）}" | sed 's/^/  /'
bad=$(echo "$changed" | grep -Ev "$allow" | grep -v '^$' || true)
if [ -n "$bad" ]; then echo "越權！不允許的檔案：" >&2; echo "$bad" | sed 's/^/  /' >&2; exit 1; fi
echo "[$role] 邊界 OK"
