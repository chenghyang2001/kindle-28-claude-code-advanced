# Session 12 — Dynamic Workflows / `/loop` / 把 workflow 包成 skill

**日期**：2026-06-23
**主題**：第 9 章外掛延伸 — 學 Dynamic Workflows、`/loop`、並把 workflow 固化成 skill（互動教學模式，全程實跑驗證）

---

## 完成事項

### 1. 環境修復（外掛）

- **修好 `/revise-claude-md`**：根因是 `claude-md-management` 在本機 `~/.claude/settings.json` 的 `enabledPlugins` 缺項（市集快取有、但未啟用）。以 `claude plugin install claude-md-management@claude-plugins-official` + `/reload-plugins` 補裝啟用。
- 啟用 `hookify@claude-code-plugins`；安裝 `claude-code-setup`（提供 `claude-automation-recommender` skill）。
- 跑 automation-recommender 分析本專案 → 唯一推薦：ruff 存檔自動 lint hook。

### 2. 新增本專案自動化

- **`.claude/settings.json` 加 PostToolUse ruff hook**：Edit/Write `.py` 後自動 `ruff check --fix` + `ruff format`（只對 .py、ruff 沒裝靜默略過、永不阻擋）。

### 3. Dynamic Workflows 教學（demo-dynamic-workflow/）

- 建完整教材：README（何時/如何/為何/替代方案 + 決策矩陣）、hello 範例腳本、STEP_LOG。
- 互動問答 Q1–Q3（情境配對 4/4 全對）。
- **實跑 4 次 Workflow**：扇出+彙整 ×2（44 萬 token/次）、3 階段交叉驗證 pipeline ×1（10 agent / 109 萬 token）、skill 觸發 ×1。
- 從 `journal.jsonl` 還原**實跑流程圖**（`last-run-graph.mmd` + `.png`，mmdc 渲染）。

### 4. `/loop` 教學

- 實跑 60 秒×3 次自動停的 self-paced loop（`loop-demo-log.md`）。
- 釐清：`CronList`/`ScheduleWakeup` 是 Claude 內部工具（非 shell/斜線指令）；self-paced = 一串 one-shot vs `/loop 1m` = 真 recurring cron。

### 5. 把 workflow 包成 skill

- 建 `.claude/skills/quiz-workflow/SKILL.md`（內嵌出題 workflow + 觸發詞 + 參數）。
- 端到端驗證：打 `quiz-workflow Hooks, MCP Servers, Plugins` → skill 觸發 → Workflow 4 agent → 回測驗卷 ✅。

---

## 關鍵技術筆記

- **Dynamic Workflows = `Workflow` 工具**（Claude 跑的 JS 多代理編排），**不是 `/slash`**。三原語：`agent()`／`parallel()`（同步牆）／`pipeline()`（無等待牆，首選）。
- **跨機器同步 `enabledPlugins` 不會自動帶過來** → 文件記「已啟用」≠ 該機真啟用（配置漂移）。
- **工具 vs 指令**：大寫駝峰（CronList／Workflow／ScheduleWakeup）= Claude 跑；小寫帶斜線（/loop /workflows /schedule）= 使用者打。
- **skill 不跑 JS**：它是「指示」，被觸發時叫主 Claude 呼叫 `Workflow`。把右上角武器降維成左下角一句話指令。
- **成本**：workflow 層數/審查員越多越貴（簡單 44 萬 → 3 階段 109 萬 token/次），依任務價值取捨。

---

## 產出檔案

| 檔案 | 動作 | commit |
|------|------|--------|
| `CLAUDE.md` | 配置漂移備註 + 外掛排錯通則 | 27d384e |
| `.claude/settings.json` | PostToolUse ruff hook | cfa444b |
| `demo-dynamic-workflow/`（README/hello/3 測驗卷/流程圖/loop-log/STEP_LOG） | 新增 | d228cea, df2135a, 7731494, 7886f7f |
| `.claude/skills/quiz-workflow/SKILL.md` | 新增 | 64060a3 |
| `doc/dynamic-workflow-lesson-summary.md` | 新增 | 7886f7f |

---

## HANDOFF（下次 session 優先處理）

### 立即行動

- [ ] （可選）繼續決策矩陣未碰的格子：`/schedule`（雲端 cron 版，需 AskUserQuestion 決定 cloud vs session）。
- [ ] （可選）把 `quiz-workflow` skill 進一步打包成可分享的 plugin（plugin.json + marketplace）。
- [ ] 回到主課程進度：第 9 章後續或 `/next-lesson` 換下一課。

### 進行中（需接續）

- 無未完成工作。本課（Dynamic Workflows / loop / 包 skill）已全部實跑驗證並 commit。

### 注意事項

- **ruff PostToolUse hook 已生效**（下個 session 起編輯 `.py` 會自動 lint，輸出 `🐍 ruff 已整理：…`）。
- workflow demo 很耗 token（單日 4 次累計 >2M），未來純展示用途跑 1 次即可，別反覆跑長版。
- `demo-dynamic-workflow/bash.exe.stackdump` 是當機暫存、已被 `.gitignore`（`*.stackdump`）擋掉，無害。
- 互動教學模式 + 每回合 say_ui 語音播報仍持續生效。
