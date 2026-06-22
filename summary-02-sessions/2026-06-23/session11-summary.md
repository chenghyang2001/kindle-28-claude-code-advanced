# Session 11 — 第9章外掛安裝實戰 + User-level Hook 跨機器路徑修復

**日期**：2026-06-23
**機器**：user 家用機
**主題**：章節語音摘要、官方外掛 user-level 安裝、claude-code-setup cache 修復、hookify 停用、user-level settings.json 硬編碼路徑根治

> 註：與同日 Session 9（/chapter-audio、/next-lesson slash 指令）、Session 10（另一 console：$CLAUDE_PROJECT_DIR + batch/loop/schedule 教學）為平行 session，內容互補。

## 完成事項

### 章節語音摘要

- `第09章｜打造_Claude_Code_自動化團隊.m4a`（19 分鐘）用 ffmpeg + faster-whisper(medium) 轉成 538 行逐字稿
- 寫成繁中結構化摘要，連同逐字稿放進 `demo-ch9-plugin/`
- 踩到並記錄：ffmpeg(Win) 輸出 `/tmp/x.wav` 靜默失敗（exit 0 但檔不存在），須用實體路徑

### 官方外掛安裝（user level `~/.claude/settings.json`）

- 啟用圖片指定 4 外掛：`pr-review-toolkit`、`commit-commands`（本就啟用）、`hookify`、`claude-md-management`
- 加裝 `claude-code-setup@claude-plugins-official`
- 釐清機制：`enabledPlugins` 只翻開關，實際載入從 `cache\` 目錄

### claude-code-setup cache 修復

- 症狀：重啟後 skill 回 Unknown skill
- 根因：直接改 settings.json 啟用但 cache 目錄空的（檔案沒下載）
- 修法：從 marketplace `cp -r` 補進 cache（含 `.claude-plugin/` 隱藏目錄——bash `*` 不匹配 dotdir，要單獨複製）

### hookify 停用（import bug）

- 根因：hook 腳本 `from hookify.core` 假設 `CLAUDE_PLUGIN_ROOT` basename=`hookify`，但 cache 版面 `hookify/0.1.0/` 多一層版本號 → `No module named 'hookify'`
- 決定：停用（4 hook 全壞、改 cache 會被更新覆蓋）

### user-level settings.json 硬編碼路徑根治（最重要）

- 發現 `~/.claude/settings.json` 有 9 處寫死 `C:/Users/B00332/.claude/hooks/...`（公司機路徑經 `.claude` repo 同步來）
- 家用機觸發 `No such file` + node `loader:1451`
- 修法：改成 `"$(cygpath -w "$HOME/.claude/hooks/X")"`（與既有 enforce_writer_qa hook 同款，兩台機都能跑）

### 其他

- 建空目錄 `demo-ch10-brownfield/`（待第十章音檔）
- 手動跑 claude-code-setup 工作流產推薦報告（結論：只缺 ruff 格式化 + 擋 .venv 兩 hook）
- superpowers `run-hook.cmd` 錯誤：單引號包 `${CLAUDE_PLUGIN_ROOT}` 阻止展開 → 第三方非阻擋 bug，使用者選忽略

## 關鍵技術筆記

- ffmpeg(Win) 不吃 Git Bash `/tmp`，須實體路徑
- 外掛載入源頭：`~/.claude/plugins/cache/<marketplace>/<plugin>/<version>/`
- `$HOME` 展開為 MSYS `/c/Users/...`，node.exe 不吃，必須 `cygpath -w`
- bash glob `*` 不匹配 `.` 開頭目錄，複製外掛要補 `.claude-plugin/`

## 產出檔案

| 檔案 | 動作 |
|------|------|
| `demo-ch9-plugin/第09章-外掛程式-摘要筆記.md` | 新增 |
| `demo-ch9-plugin/ch09_transcript.txt` | 新增 |
| `demo-ch10-brownfield/` | 新增空目錄 |
| `.gitignore` | 加 hookify.*.local.md 規則 |
| `~/.claude/settings.json` | 啟用 5 外掛 + 修 9 處 B00332 路徑 |
| memory `settings-cross-machine-hardcoded-paths.md` | 新增 |
| memory `local-av-transcription.md` | 補 ffmpeg /tmp 陷阱 |

相關 commits：`922fbca`(demo-ch9)、`bd6fb92`(gitignore)；`.claude` repo `5a26622`/`cdbebef`/`351c305`/`9d851f5`

## HANDOFF（下次 session 優先處理）

### 立即行動

- [ ] 重啟兩台機器 Claude Code，確認 user-level B00332 修復 + hookify 停用生效、錯誤不再跳
- [ ] 第十章 brownfield：取得音檔後用 `/chapter-audio 10` 填滿 `demo-ch10-brownfield/`
- [ ] （選配）繼續課程：`/next-lesson 9` 進第 10 課

### 進行中（需接續）

- demo-ch10-brownfield 空目錄待內容；第10章「既有專案/brownfield」主題，正好對應 claude-code-setup 外掛用途

### 注意事項

- **兩個修復是不同檔案，不衝突**：本 session 改 user-level `~/.claude/settings.json`（9 個 gsd hook，cygpath+$HOME）；Session 10 改專案 `.claude/settings.json`（SessionStart git hook，$CLAUDE_PROJECT_DIR）。各自 repo、各自 commit
- hookify 已停用，`.claude/hookify.*.local.md` 規則檔留著無害（gitignored、停用後不讀）
- superpowers run-hook.cmd 錯誤已知、選擇忽略，非阻擋
