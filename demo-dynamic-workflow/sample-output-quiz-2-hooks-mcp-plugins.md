# hello-dynamic-workflow 實跑產出 #2（換 3 主題）

> 2026-06-23 第二次實跑，只改 `TOPICS` 一行 → Hooks / MCP Servers / Plugins。
> Run ID：`wf_81dfac90-4dd`｜4 agent（3 出題 + 1 彙整）｜~50 秒。

---

## 題目

**第 1 題（medium）Hooks**：要在「工具實際執行**之前**」攔截並阻擋某個 Write/Edit 呼叫，應使用哪個 Hook 事件？

**第 2 題（easy）MCP Servers**：MCP Server 的主要作用是什麼？（單選 A–D）

**第 3 題（easy）Plugins**：關於 Plugins，下列何者正確？（單選 A–D）

---

## 解答

**第 1 題：PreToolUse。** 它在「工具被呼叫、尚未執行前」觸發，能檢查輸入並 block；PostToolUse 是執行後才跑（如本專案 ruff 自動整理）。本專案三-agent 鐵律就是靠 PreToolUse hook（enforce_writer_qa.py）擋 Write/Edit。

**第 2 題：B。** MCP（Model Context Protocol）是標準化接線協定；MCP Server 把外部工具/資料（GitHub、Drive、Gmail、資料庫…）包成 Claude 可呼叫的工具與資源。一句話：**Claude 對接外部工具與資料的「標準插座」**。（A 它不是推理模型；C context 壓縮是 compact；D 跨機器同步是 settings 範疇。）

**第 3 題：B。** Plugin 是「打包與分發」格式，把 slash 指令、subagent、hook、甚至 MCP server 設定集中成可分享可安裝的套件，經 marketplace 一鍵安裝即生效（不需重編譯）。本專案就裝了 pr-review-toolkit、commit-commands、hookify、claude-md-management 等官方 plugin。
