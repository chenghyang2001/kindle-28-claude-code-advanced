# 練習 02 — 進階：設計 CI 自動 review

## 情境說明
把 Claude 接進 CI，PR 時自動跑審查，人類只看它整理好的重點。

## 範例：GitHub Actions（概念骨架）
```yaml
name: claude-review
on: pull_request
jobs:
  review:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Run Claude review
        env:
          ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}  # 機密用 Secrets，不寫死
        run: |
          # 取 diff 餵給 Claude，輸出審查到 PR comment
          ./scripts/claude_review.sh
```

## 任務
### 任務 1
畫出「PR 觸發 → 取 diff → Claude 審查 → 回貼 comment」的流程。

### 任務 2
說明敏感值（API key）如何安全注入（Secrets，而非寫進 yml）。

## 延伸思考
什麼任務適合 subagent、什麼適合 skill、什麼適合 CI？三者界線在哪？

## 完成後
將解答存入 `answer/ex02-answer.md`。
