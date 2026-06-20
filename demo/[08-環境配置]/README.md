# [08] 環境配置（Configuration）

> 所屬：Part IV — 配置　|　難度：進階　|　預估：~50 分鐘

## 學習目標
- 打造理想的終端與 CLI 環境
- 設定 hooks 自動化行為
- 接上 MCP 並選對 model

## 前置條件
- 完成 [01]。

## 課程結構
- `exercise-01-基礎.md`：盤點你目前的 Claude Code 環境，列出可優化的設定項（terminal、alias、CLI flag）。
- `exercise-02-進階.md`：寫一個 hook（如 SessionStart 或 PreToolUse）來自動化一個重複動作。
- `exercise-03-綜合.md`：為自己設計一套完整環境配置：terminal + alias + 1 個 hook + 1 個 MCP + model 預設。

## 完成標準
- [ ] 閱讀本課 README
- [ ] 完成基礎練習，解答存入 `answer/ex01-answer.md`
- [ ] 完成進階練習，解答存入 `answer/ex02-answer.md`
- [ ] （選配）完成綜合挑戰，解答存入 `answer/ex03-answer.md`
- [ ] 填寫 `STEP_LOG.md`
- [ ] 執行 `/study-scaffold carry 8` 攜帶答案到下一課

## 本課重點概念
- terminal / Chrome 整合
- CLI flags
- hooks（PreToolUse/SessionStart 等）
- MCP server 串接
- model 選擇
