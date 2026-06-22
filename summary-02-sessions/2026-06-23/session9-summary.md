# Session 9 — 第 9 章外掛實戰：安裝官方外掛 + 自建專案自動化

**日期**：2026-06-23
**主題**：把第 9 章「官方外掛程式」從理論落地到本專案——裝官方外掛、用 hookify 寫守則、建 slash 指令

---

## 完成事項

### 1. 第 9 章語音摘要（demo-ch9-plugin）

- 用 ffmpeg + faster-whisper（medium）轉錄 `第09章｜打造_Claude_Code_自動化團隊.m4a`（19 分鐘 → 538 行 / 16k 字）
- 產出結構化摘要 `第09章-外掛程式-摘要筆記.md` + `ch09_transcript.txt`，放進 `demo-ch9-plugin/`
- 內容重點：plugin.json 五大元素（Skills/Commands/Agents/Hooks/MCP servers）、官方生態系、安裝前三大安全守則（審查碼／驗作者／控 allowedTools 權限）

### 2. 安裝 4 個官方外掛（user level `~/.claude/settings.json`）

- `pr-review-toolkit`、`commit-commands` → 本來就 enabled
- `hookify` → false 翻成 true
- `claude-md-management@claude-plugins-official` → 新增（圖片寫 `claude-md-manage` 是簡寫，實際名 `claude-md-management`）
- `.claude` repo 確認為 PRIVATE 後才 push（含密鑰）

### 3. 自建兩條 hookify 規則（`.claude/hookify.*.local.md`，git-ignored）

- `no-hardcoded-paths`：寫程式碼/設定副檔名且 content 含 `C:\Users\`/`C:/Users/` → warn。雙條件 AND，文件 .md/.txt 不觸發
- `interactive-guard`：Bash 含 `git push|git commit|git reset --hard|rm -rf` → warn（呼應互動教學第 6/7 條）
- 兩條都用 hookify 引擎做端對端實測通過

### 4. 自建兩個 slash 指令（`.claude/commands/`，已進版控）

- `/chapter-audio <章節號> [--quality]`：章節 m4a 一鍵轉摘要進 demo
- `/next-lesson <N>`：carry N→N+1 + 進互動教學模式

### 5. 文件

- CLAUDE.md 新增「本專案自動化」一節（攜帶機制段落後）

---

## 關鍵技術筆記

- **hookify 機制踩坑**：
  - `config_loader.py` 用 cwd 相對 `glob('.claude/hookify.*.local.md')` → **只讀專案層，讀不到 `~/.claude/`**
  - 簡寫 `pattern` + `event: file` 對應 `new_text` 欄位，**只抓 Edit 的 new_string，抓不到 Write 的 content** → 要用顯式 `conditions` + `field: content`（才會 `content or new_string`）
  - regex 自動 `re.IGNORECASE`
  - parser 不做跳脫處理：檔案裡要寫**雙反斜線** `C:[\\/]Users[\\/]` 才會被 Python regex 解析成 backslash-or-slash char class
  - 規則即時生效、不用重啟；slash 指令需重啟（但本 session 實測 SessionStart 有自動載入）
- **ffmpeg /tmp 坑**：Windows ffmpeg 不能用 `/tmp` 路徑（對應不到），要輸出實體路徑如 `~/Downloads`
- **faster-whisper**：1.2.1 已裝；medium CPU int8 跑 19 分鐘音檔約 20-40 分鐘（慢但準），small + beam_size=1 約 3-6 分鐘

---

## 產出檔案

| 檔案 | 說明 | 版控 |
|------|------|------|
| `demo-ch9-plugin/第09章-外掛程式-摘要筆記.md` | 第 9 章摘要 | ✅ commit 922fbca |
| `demo-ch9-plugin/ch09_transcript.txt` | 轉錄全文 | ✅ commit 922fbca |
| `.claude/commands/chapter-audio.md` | slash 指令 | ✅ commit 05930c5 |
| `.claude/commands/next-lesson.md` | slash 指令 | ✅ commit 05930c5 |
| `.claude/hookify.no-hardcoded-paths.local.md` | hookify 規則 | git-ignored |
| `.claude/hookify.interactive-guard.local.md` | hookify 規則 | git-ignored |
| `CLAUDE.md` | 新增自動化記錄 | ✅ commit 1e5118e |
| `~/.claude/settings.json` | 啟用外掛 | ✅ commit c20586c（.claude repo）|

---

## HANDOFF（下次 session 優先處理）

### 立即行動

- [ ] 重啟 Claude Code 確認 `/chapter-audio`、`/next-lesson`、hookify、claude-md-management 全部生效
- [ ] 可用 `/chapter-audio 10` 接著處理第 10 章（demo-ch10-brownfield 已存在）
- [ ] 課程進度：可用 `/next-lesson` 機制接續第 10 課（既有專案）

### 進行中（需接續）

- 17 課互動學習持續進行中。已有 demo：ch3、ch9、ch10、gsd-01/02/03、ralph-01/02
- 第 9 章已透過實戰（裝外掛 + 自建自動化）深度掌握

### 注意事項

- hookify 規則是**專案層本機檔**（git-ignored），換機器/換專案不會自動帶過去，需各自建立
- `~/.claude/settings.json` 含密鑰，只 push 到 PRIVATE 的 `.claude` repo
- 寫 hookify regex 記得：雙反斜線 + 顯式 conditions 用 `field: content` 才同時涵蓋 Write/Edit
