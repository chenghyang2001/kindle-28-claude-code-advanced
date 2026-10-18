# 練習 01 解答 — csv-report skill

## 任務 1：觸發條件與步驟

實際檔案：`.claude/skills/csv-report/SKILL.md`（專案層，不放 `~/.claude/skills`），輔助腳本 `.claude/skills/csv-report/scripts/csv_report.py`。

```markdown
---
name: csv-report
description: 讀 CSV 產生每個數值欄平均值的 Markdown 報告（<檔名>-summary.md）。當使用者說「csv 報告」「csv summary」「幫我統計這個 CSV」「CSV 平均」時觸發。不觸發：要畫圖表或做複雜統計分析。
argument-hint: <csv 檔案路徑>
allowed-tools: Bash(python *), Bash(PYTHONUTF8=1 python *), Read
---
```

步驟：

1. 確認 `$ARGUMENTS` 給的 CSV 路徑；沒給就提示用法。
2. 跑輔助腳本算平均（不讓模型心算，結果才穩定）。
3. 規則：非空值全能轉數字 → 數值欄；`""`/`NA`/`N/A`/`null` 算缺值略過；有任何非數字值 → 文字欄；整欄缺值 → `-`。
4. 輸出 `<檔名>-summary.md` 到 CSV 同目錄。
5. 回報「處理列數：N」與報告路徑。
6. 腳本回傳非 0 → 轉述錯誤，不產生報告。

設計重點：
- **description 同時寫觸發詞與「不觸發」**：讓自動比對更準，避免搶走畫圖類需求。
- **計算交給腳本**：skill 負責流程，確定性的運算放進程式，結果才可重現、可測試。
- **allowed-tools 限縮**：只開 python 與 Read，skill 執行時不需要額外授權，也不會越權。

## 任務 2：3 個測試案例（全部用 `claude -p` 實跑）

執行腳本：`scripts/run_skill_tests.sh`（會先清掉 `CLAUDE*` 環境變數與 `ANTHROPIC_API_KEY`）。紀錄在 `answer/logs/skill-*.log`（摘要）與 `skill-*.jsonl`（完整串流）。

| # | 類型 | 輸入 | 預期 | 實際結果 |
| --- | --- | --- | --- | --- |
| 1 | 正常 | `幫我做 csv 報告：data/sales.csv`（自然語言，不打 `/`） | 自動觸發 skill；revenue 平均 1250.19、units 33；處理列數 4 | ✅ 出現 `TOOL_USE: Skill {"skill":"csv-report"}`，數值正確 |
| 2 | 邊界 | `/csv-report data/edge.csv`（空值、`N/A`、含逗號的引號欄位） | score=(88+92)/2=90、bonus=(5+7)/2=6、name 為文字欄 | ✅ 全部正確，`"Lee, Dan"` 沒有拆欄 |
| 3 | 錯誤 | `/csv-report data/missing.csv` | 回報找不到檔案，不產生 `missing-summary.md` | ✅ 腳本 exit 1，Claude 轉述錯誤，沒有產生報告檔 |

案例 1 證明 skill 會依 description 被自動載入；案例 2、3 用斜線指令直接喚起。

## 驗收標準

- [x] description 含明確觸發詞（「csv 報告」「csv summary」等）
- [x] 步驟可被照著執行（3 個案例都由 `claude -p` 照步驟跑完）
- [x] 3 類測試案例齊全且實跑
