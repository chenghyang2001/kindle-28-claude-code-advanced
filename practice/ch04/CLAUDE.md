

## 本專案例外

本專案是 Kindle 書籍教學 demo（kindle-drill 快速模式），豁免全域「程式碼三 agent 鐵律」：主 Claude 直接寫檔，不派 code-writer／code-qa／code-reviewer；不需詢問複雜度，也不需詢問是否使用快速模式（已選快速模式）。
所有選擇題一律採用推薦選項、不要停下來問使用者；不可修改全域 `~/.claude/settings.json`，設定一律寫在本專案的 `.claude/settings.local.json`。

## Compact Instructions（壓縮必留清單，練習 02）

執行 `/compact`（手動或自動）時，以下資訊**一律保留原文**，不可改寫或省略：

1. **進行中任務的當前步驟 + 下一步**：目前在 k28 第 4 章練習，ex01／ex02 做到哪、下一步是什麼。
2. **關鍵 ID**：實驗用的 claude -p session_id（見 `logs/rot-run.jsonl`）、最新 git commit hash、背景 task ID。
3. **已修改／新建的檔案路徑**（相對於專案根目錄）：`answer/ex01-answer.md`、`answer/ex02-answer.md`、`NOTES.md`、`scripts/rot-experiment.sh`、`rot-lab/`、`logs/`，以及已 staged 未 commit 的檔案。
4. **重要決策與使用者偏好**：全程繁體中文；快速 demo 模式；全自動不提問；不 push、不改全域 `~/.claude/`；`claude -p` 前先清 `CLAUDE*` 環境變數；實驗模型用 haiku。
5. **實驗的關鍵數字**：ground truth（數值記在 `NOTES.md`，此處不寫，避免實驗 session 讀 CLAUDE.md 時被洩題）與各回合腐化症狀結論。
6. **等待中的背景任務**：task ID、預期完成時間、完成後要做的事。
7. **未解決的錯誤**：完整錯誤訊息一行摘要＋已嘗試的解法。

壓縮後的第一則回覆，必須先用下列範本自我摘要再繼續：

```
## 本 Session 目前狀態（壓縮後接續）
- 任務：…
- 進度：…（已完成 / 進行中）
- 關鍵 ID：…
- 待辦：…
```
