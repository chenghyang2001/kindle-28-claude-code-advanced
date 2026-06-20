# 練習 03 — 綜合挑戰：把重複任務做成可重用 prompt 範本

> 選配：完成前兩個練習後再挑戰

## 挑戰情境
把你最常重複的一個任務，做成一個可換輸入重用的 prompt 範本（含參數占位符），存進專案的 `.claude/commands/` 變成 slash command。

## 範例：slash command 檔（`.claude/commands/csv-summary.md`）
```markdown
# /csv-summary — 產生 CSV 欄位平均摘要

讀取 $ARGUMENTS 指定的 CSV，對所有數值欄位計算平均，
輸出為 Markdown 表到同目錄的 <檔名>-summary.md，並印出處理列數。
缺值略過；平均四捨五入到 2 位；UTF-8。
```
使用：`/csv-summary ./data/sales.csv`

## 限制條件
- 範本必須能換不同輸入重用（用 `$ARGUMENTS` 或明確占位符）
- 附一段「如何驗證輸出正確」的說明

## 完成後
將解答存入 `answer/ex03-answer.md`。
