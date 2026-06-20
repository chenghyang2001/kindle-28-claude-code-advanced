# 練習 01 解答 — 環境盤點並優化（基礎）

> 真實盤點本機 `~/.claude` 環境，找出可優化點並**實際修掉 2 個真問題**。

## 〇、先備知識：settings.json 三層級（最常考）

| 層級 | 路徑 | 用途 | 進版控？ | 優先序 |
|------|------|------|---------|--------|
| 全域 | `~/.claude/settings.json` | 所有專案通用 | — | 低 |
| 專案 | `<repo>/.claude/settings.json` | 團隊共用 | ✅ | 中 |
| 個人覆寫 | `<repo>/.claude/settings.local.json` | 本機專屬 | ❌ | 高（蓋前兩者） |

**金鑰鐵律**：API 金鑰**永不**放任一 settings 檔 → 走 OS 環境變數或 `.env`（+`.gitignore`）。
- 會被 commit 外洩（進 git 歷史清不掉）。
- 設 `ANTHROPIC_API_KEY` 會讓 Claude Code 改用 API 計費、繞過 Max 訂閱 → 燒錢。

## 一、盤點結果：5 個可優化點

| # | 等級 | 發現 | 處置 |
|---|------|------|------|
| 1 | 🔴 安全 | 全域 `settings.json` 的 `env` 明文寫死 `GOOGLE_DOCS_CLIENT_ID/SECRET` | ✅ 已修（見下） |
| 2 | 🔴 Bug | 3 條 env 路徑被存成字面 JSON 跳脫 ``/`\t`，解析出控制字元 → 認證檔找不到 | ✅ 已修（見下） |
| 3 | 🟡 | 本專案無專案層 `.claude/settings.json` | 可加：把常用指令進 `allow`、跨機共用 |
| 4 | 🟢 | `model` 已全域設 `claude-opus-4-8` | 保留 |
| 5 | 🟡 | `permissions.allow` 34 條 + `defaultMode: auto` | 定期檢視收斂、清掉沒用條目 |

## 二、實際套用（修了 2 個真問題，任務 2「至少套用 2 個」達標）

### 修 #2：路徑控制字元 bug
- 病因：`env` 值被存成字面 JSON 跳脫序列——``（原意 `\auth`）解析成響鈴、`\t`（原意 `\token`）解析成 Tab，使路徑變成 `…mcp␇uth.json`、`…comment⇥oken.json`，認證檔當然找不到。
- **這正是每次開 session AUTH CHECK 報 NotebookLM / YouTube / Google Docs 三個 MISSING 的元兇之一**（路徑壞掉那部分）。
- 修法（踩坑後的正解）：byte/text 取代都對不上（檔案存的是字面跳脫非真控制字元）→ 改用 `json` 載入 + `chr(92)` 重新賦值再寫回：
  ```python
  d = json.loads(p.read_text("utf-8"))
  bs = chr(92)
  d["env"]["NOTEBOOKLM_MCP_AUTH"]   = f"%USERPROFILE%{bs}.notebooklm-mcp{bs}auth.json"
  d["env"]["YOUTUBE_COMMENT_TOKEN"] = f"%USERPROFILE%{bs}.config{bs}youtube-comment{bs}token.json"
  d["env"]["GOOGLE_DOCS_MCP_TOKEN"] = f"%USERPROFILE%{bs}.config{bs}google-docs-mcp{bs}token.json"
  ```
- 驗證：`NOTEBOOKLM_MCP_AUTH` 指向的 `auth.json` 存在=True（路徑修正成功）。youtube/docs 的 token 仍不存在，是**OAuth 未跑過**（另一件事，與路徑無關）。

### 修 #1：明文密鑰移出 settings
```bash
setx GOOGLE_DOCS_CLIENT_ID "...apps.googleusercontent.com"
setx GOOGLE_DOCS_CLIENT_SECRET "<值>"     # 存成永久 OS 環境變數
# 再從 settings.json env 刪除這兩個鍵 → Claude Code 從 OS 繼承
```
- 驗證：settings 中兩密鑰鍵**已清除**；Claude Code 改由 OS 環境變數取得。

### 安全善後 checklist
- [ ] 重開 session 讓 env 變更生效。
- [ ] 刪除 `settings.json.bak`（含舊明文 secret）或妥善保管。
- [ ] 到 Google Cloud **rotate** 這組 client secret（曾出現在 log）。

## 三、結構完整性驗證（修改無副作用）
- 頂層鍵一致；`permissions.allow` 34 條未掉、`deny` 16 條；6 個 hook 事件（PreCompact/PreToolUse/Stop/PostToolUse/UserPromptSubmit/SessionStart）皆在；`model` 仍 opus-4-8；`env` 由 12→10（少掉 2 個密鑰）。

## 驗收
- [x] 5 個優化點具體可執行
- [x] 至少 2 個已套用並驗證（修 #1 密鑰 + #2 路徑，皆有驗證輸出）
- [x] 先備份（`settings.json.bak`）再改，並驗證 JSON 合法 + 結構完整
