# 練習 01 — 基礎：把多步流程寫成 skill 規格

## 情境說明
skill 把一個重複流程封裝成「觸發詞 + 步驟」，之後一句話就能喚起整套流程。

## 範例：SKILL.md 骨架
```markdown
---
name: csv-report
description: 讀 CSV 產生每欄平均的 Markdown 報告。當使用者說「csv 報告」「csv summary」時觸發。
---
# csv-report
## 步驟
1. 讀取 $ARGUMENTS 指定的 CSV
2. 對數值欄算平均（缺值略過）
3. 輸出 Markdown 表到 <檔名>-summary.md
4. 印出處理列數
```

## 任務
### 任務 1
為一個你常做的多步流程，寫出 skill 的觸發條件與步驟。

### 任務 2
列出該 skill 的 3 個測試案例（正常 / 邊界 / 錯誤）。

## 驗收標準
- [ ] description 含明確觸發詞
- [ ] 步驟可被照著執行
- [ ] 3 類測試案例齊全

## 完成後
將解答存入 `answer/ex01-answer.md`。
