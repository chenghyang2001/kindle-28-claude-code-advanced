# Session 1 Summary — 第七課收尾 + 第八課（環境配置）基礎與進階

## 日期

2026-06-20

## 完成事項

### 第七課 精通 CLAUDE.md（收尾）

- 進階三題：拆分依據（主題／變動頻率／重用範圍）、實際把 10 條混雜規則拆 4 子檔、模組化 4 代價（過度拆分／衝突無仲裁／**context 不會省**／間接層遮蔽）。
- 綜合 capstone：把本專案臃腫根 CLAUDE.md（7 段）模組化成 `answer/modular-demo/`（薄主檔 + `interactive-teaching.md` + `voice-playback.md`），**不動正在驅動 session 的真實根檔**。
- commit `a298e78`。

### 第八課 環境配置（基礎）

- 學 settings.json 三層級（個人 local > 專案 > 全域）+ 金鑰鐵律（永不入 settings）。
- 盤點本機 `~/.claude`，列 5 可優化點，**實修 2 個真問題**：
  - #1 安全：全域 settings 明文 `GOOGLE_DOCS_CLIENT_ID/SECRET` → `setx` 成 OS 環境變數後從 settings 刪。
  - #2 Bug：3 條 env 路徑被存成**字面 JSON 跳脫序列**（``/`\t`）→ 解析出控制字元 → 認證檔找不到（AUTH CHECK MISSING 元兇之一）。
- 卡關突破：byte / text 取代都「0 處」，繞到語意層用 `json.loads` + `chr(92)` 重新賦值再 `json.dumps` 寫回，一次成功且結構完整無副作用。
- commit `523f73d`。

### 第八課 環境配置（進階）

- 寫 **SessionStart hook**：開專案自動印學習進度。
- 新建 `.claude/settings.json`（專案層），指令 `git log -1 --format="📚 學習進度：%s (%h)"`。
- 驗證：V1 JSON 合法 ✅、V2 實跑 git 輸出 `📚 學習進度：完成第八課…(523f73d)` ✅。
- 解答 `demo/[08-環境配置]/answer/ex02-answer.md` + STEP_LOG 進階打 ✅（本次 session 末尾才寫，隨收工 commit）。

## 關鍵技術筆記

- **hook 選事件法**：問「我要這件事在什麼時間點自動發生」→ 對到事件名，不是背。SessionStart=開場、UserPromptSubmit=送訊息、PreToolUse=工具前守門、PostToolUse=工具後、Stop=收尾、PreCompact=壓縮前。
- **settings 三層級優先序**：個人 local > 專案 > 全域（越窄越優先）；金鑰永遠走 OS 環境變數/.env。
- **JSON 跳脫層 bug**：檔案存「字面跳脫序列」時，byte/text 比對都對不上，要繞到 json 語意層用 `chr(92)` 賦值。
- **專案層 hook 安全機制**：第一次載入會問「是否信任本專案 hook」，按允許才生效。

## 產出檔案

| 檔案 | 動作 |
|------|------|
| `.claude/settings.json` | 新建（SessionStart hook） |
| `demo/[08-環境配置]/answer/ex02-answer.md` | 新建（進階解答） |
| `demo/[08-環境配置]/STEP_LOG.md` | 更新（進階 ✅） |
| `~/.claude/settings.json` | 修改（移密鑰 + 修 3 路徑跳脫，已於基礎時 commit 範疇外操作） |

## HANDOFF（下次 session 優先處理）

### 立即行動

- [ ] 第八課**綜合**：設計完整環境配置（terminal + alias + 1 hook + 1 MCP + model 預設），或視情況略過。
- [ ] 安全善後：到 Google Cloud Console **rotate** 舊的 `GOOGLE_DOCS_CLIENT_SECRET`（曾出現在 log），rotate 後 `setx` 更新。
- [ ] 刪 `~/.claude/settings.json.bak`（含舊明文 secret）——destructive，需明確「執行」同意。

### 進行中（需接續）

- 第八課進階已完成，綜合題尚未開始。第 9～17 課全未開始（9-官方外掛 / 10-既有專案 / 11-大規模 / 12-自動化 / 13-Agent 編排 / 14-進階技巧 / 15-安全與成本 / 16-快速參考 / 17-資源）。

### 注意事項

- **互動教學模式鐵律**：一次一題、等回答；未經「執行」不可跑任何指令；唯一例外＝每回合語音播報（taskkill 舊 + start 新 `say_ui.exe --autoplay` + Write `_answer.txt`），已長期授權。
- 全域 settings 的 path 修復需**重開 session** 才生效；本 session 內 AUTH CHECK 仍可能顯示 MISSING（YouTube/Google Docs token 是 OAuth 未跑過，與路徑無關）。
- 新增的專案層 hook 下次開 session 會跳「信任本專案 hook」確認，按允許。
