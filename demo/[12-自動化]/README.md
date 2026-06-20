# [12] 自動化（Automation）

> 所屬：Part V — 開發　|　難度：進階　|　預估：~50 分鐘

## 學習目標
- 用 skills 與 subagents 自動化重複任務
- 接上 CI/CD
- 認識 OpenClaw 等排程觸發

## 前置條件
- 完成 [08] 與 [09]。

## 課程結構
- `exercise-01-基礎.md`：把一個重複的多步驟流程，寫成一個 skill 的規格（觸發詞 + 步驟）。
- `exercise-02-進階.md`：設計一條 CI 流程，讓 Claude 在 PR 時自動跑 review。
- `exercise-03-綜合.md`：為一個真實重複任務，組合『skill + subagent + 排程』做出端到端自動化規格。

## 完成標準
- [ ] 閱讀本課 README
- [ ] 完成基礎練習，解答存入 `answer/ex01-answer.md`
- [ ] 完成進階練習，解答存入 `answer/ex02-answer.md`
- [ ] （選配）完成綜合挑戰，解答存入 `answer/ex03-answer.md`
- [ ] 填寫 `STEP_LOG.md`
- [ ] 執行 `/study-scaffold carry 12` 攜帶答案到下一課

## 本課重點概念
- skills 封裝流程
- subagents 分工
- CI/CD 整合
- dynamic workflows
- OpenClaw / 排程觸發
