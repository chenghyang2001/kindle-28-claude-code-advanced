# [04] 脈絡管理（Context Management）

> 所屬：Part II — 生產力　|　難度：進階　|　預估：~40 分鐘

## 學習目標
- 辨識 context rot 並即時處置
- 維持 context hygiene
- 監控 context 用量

## 前置條件
- 完成 [01]。

## 課程結構
- `exercise-01-基礎.md`：刻意把一個 session 撐長，觀察 Claude 開始忘記早期決定的徵兆。
- `exercise-02-進階.md`：設計一份『壓縮時必留清單』：哪些資訊（ID、路徑、決策）壓縮後一定要保留。
- `exercise-03-綜合.md`：為一個跨多次對話的任務，建立『脈絡接續』機制（摘要 + 關鍵 ID 落檔）。

## 完成標準
- [ ] 閱讀本課 README
- [ ] 完成基礎練習，解答存入 `answer/ex01-answer.md`
- [ ] 完成進階練習，解答存入 `answer/ex02-answer.md`
- [ ] （選配）完成綜合挑戰，解答存入 `answer/ex03-answer.md`
- [ ] 填寫 `STEP_LOG.md`
- [ ] 執行 `/study-scaffold carry 4` 攜帶答案到下一課

## 本課重點概念
- context rot（脈絡腐化）
- context hygiene
- 何時該 /clear 或 /compact
- 壓縮要保留的關鍵資訊
- 脈絡監控
