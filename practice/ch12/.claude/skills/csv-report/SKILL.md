---
name: csv-report
description: 讀 CSV 產生每個數值欄平均值的 Markdown 報告（<檔名>-summary.md）。當使用者說「csv 報告」「csv summary」「幫我統計這個 CSV」「CSV 平均」時觸發。不觸發：要畫圖表或做複雜統計分析。
argument-hint: <csv 檔案路徑>
allowed-tools: Bash(python *), Bash(PYTHONUTF8=1 python *), Read
---
# csv-report

把一個 CSV 檔整理成「每個數值欄的平均值」Markdown 報告。

## 步驟
1. 確認 $ARGUMENTS 指定的 CSV 路徑；沒給路徑就停下並提示用法 `/csv-report <csv 路徑>`。
2. 執行輔助腳本（不要自己心算平均）：
   `PYTHONUTF8=1 python .claude/skills/csv-report/scripts/csv_report.py "$ARGUMENTS"`
3. 腳本規則（給讀者參考，實作已寫在腳本內）：
   - 某欄所有非空值都能轉成數字 → 視為數值欄，算平均（四捨五入到小數 2 位）
   - 空字串、`NA`、`N/A`、`null` 視為缺值，略過不計
   - 有任何無法轉數字的值（如 `North`）→ 視為文字欄，不算平均
   - 整欄都缺值 → 平均顯示 `-`
4. 輸出 Markdown 表到與 CSV 同目錄的 `<檔名>-summary.md`。
5. 把腳本最後一行「處理列數：N」原樣回報給使用者，並附上報告檔路徑。
6. 腳本回傳非 0（檔案不存在、空檔、編碼錯誤）時，把錯誤訊息轉述給使用者，**不要**產生報告檔。
