# 本課總結：Dynamic Workflows / `/loop` / 把 workflow 包成 skill（2026-06-23）

## 起點

看《Mastering Claude Code Plugins》簡報 + 決策矩陣（Skills｜/loop & /schedule｜Subagents｜Dynamic Workflows）後，想學「動態工作流」。

## 順手修掉的環境問題

- **`/revise-claude-md` 跑不出來**：`claude-md-management` 在本機 `enabledPlugins` 缺項（市集快取有但沒啟用）。修法：`claude plugin install claude-md-management@claude-plugins-official` + `/reload-plugins`。教訓：**跨機器同步時 `enabledPlugins` 不會自動帶過來**。
- 啟用 `hookify`、安裝 `claude-code-setup`（automation-recommender）。
- 新增本專案 **ruff 存檔自動 lint hook**（PostToolUse on `.py`）。

## 主課（全部實跑驗證）

1. **Dynamic Workflows** = Claude 跑的 JS 多代理編排（`Workflow` 工具），**不是 `/slash`**。三原語：`agent()`／`parallel()`（有同步牆）／`pipeline()`（無等待牆，首選）。
   - 跑了 4 次：扇出+彙整 ×2、3 階段交叉驗證 ×1、skill 觸發 ×1。
   - 從 `journal.jsonl` 還原出**實跑流程圖**（`last-run-graph.png`）。
2. **`/loop`**（矩陣左上）：60 秒×3 次自動停的 self-paced loop。停止條件必須寫在 prompt 裡。self-paced = 一串 one-shot；`/loop 1m` = 真 recurring cron。`CronList` 等是**內部工具非指令**。
3. **把 workflow 包成 skill**：`.claude/skills/quiz-workflow/SKILL.md`。skill 不跑 JS、是「指示」→ 叫主 Claude 呼叫 `Workflow`。效果＝右上角武器降維成左下角一句話指令。端到端驗證通過。

## 產出檔案

- `demo-dynamic-workflow/`：README、hello 範例、3 份測驗卷產出、流程圖（mmd+png）、loop-demo-log、STEP_LOG
- `.claude/skills/quiz-workflow/SKILL.md`
- `.claude/settings.json`：新增 PostToolUse ruff hook
- `CLAUDE.md`：配置漂移備註 + 外掛排錯通則

## 成本實感

4 次 workflow：簡單版 ~44 萬 token/次、3 階段版 ~109 萬/次。**層數/審查員越多越貴 → 依任務價值取捨**。

## 帶走三句

1. Dynamic Workflow = Claude 跑的多代理 JS 編排，不是斜線指令。
2. 「1 個 → 很多個」= subagent 升級 workflow 的分界線。
3. 大寫駝峰工具（CronList/ScheduleWakeup/Workflow）= Claude 跑；小寫帶斜線（/loop /workflows /schedule）= 你打。
