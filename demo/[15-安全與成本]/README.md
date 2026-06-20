# [15] 安全與成本（Security and Costs）

> 所屬：Part VI — 精通　|　難度：進階　|　預估：~45 分鐘

## 學習目標
- 依任務選對 model 控制成本
- 設計安全的 permissions
- 用 hooks 與 Docker 強化安全

## 前置條件
- 完成 [08]。

## 課程結構
- `exercise-01-基礎.md`：為三種任務（格式化 / 分析 / 複雜推理）各選一個成本最划算的 model。
- `exercise-02-進階.md`：設計一組 permissions 策略：哪些自動允許、哪些必須確認。
- `exercise-03-綜合.md`：為一個會接觸 DB / API key / 使用者輸入的工作流，做一次安全 + 成本檢查表。

## 完成標準
- [ ] 閱讀本課 README
- [ ] 完成基礎練習，解答存入 `answer/ex01-answer.md`
- [ ] 完成進階練習，解答存入 `answer/ex02-answer.md`
- [ ] （選配）完成綜合挑戰，解答存入 `answer/ex03-answer.md`
- [ ] 填寫 `STEP_LOG.md`
- [ ] 執行 `/study-scaffold carry 15` 攜帶答案到下一課

## 本課重點概念
- 各 model 成本對照
- permissions 模式
- hooks 做安全護欄
- Docker 隔離執行
- prompt cache 省成本
