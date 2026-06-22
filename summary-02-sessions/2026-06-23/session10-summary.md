# Session 10 — 修復硬編碼路徑 + 教學 /batch /loop /schedule 三指令

**日期**：2026-06-23
**機器**：DESKTOP-FFSFP66
**主題**：去硬編碼路徑（settings.json hook）＋ 互動式講解三個時間/規模型 slash 指令（含語音 TTS）

---

## 完成事項

### 1. 修復 settings.json hook 硬編碼路徑（唯一程式碼改動）

- SessionStart hook 原本寫死 `git -C "C:/Users/user/workspace/kindle-28-claude-code-advanced"`，在公司機（B00332）會失效。
- 改用 Claude Code hook 內建變數 `$CLAUDE_PROJECT_DIR` → 跨機器可攜、零硬編碼。
- 已驗證新寫法可正常輸出學習進度，commit `010b7f2` 並 push 到 main。

### 2. `/batch` 實戰 + scope-first 教訓

- 透過 `/batch 把專案內所有硬編碼 C:\Users\ 路徑改成 %USERPROFILE% / Path.home()` 觸發。
- **先掃描再動手**：grep 找到 13 個命中，分類後只有 1 個（settings.json）是會壞跨機器的真路徑；其餘 12 個是「文件在描述該 pattern 字串」（CLAUDE.md / session9-summary / 踩坑紀錄）、GSD 自動生成的歷史練習/規劃/分析產物（demo-gsd-*，CONCERNS.md 甚至是「回報」此違規）、以及 ch8 練習解答檔。
- 用 AskUserQuestion 讓使用者選範圍 → 選「只修 settings.json」。判定 `/batch` 並行 worktree+PR 編排對此情境是殺雞用牛刀（本 repo 直接 commit main、無 PR workflow、實質單檔）。

### 3. 互動式教學三個指令（每次回答都用 say_ui.exe 語音朗讀）

- **`/batch`**：一次改很多檔案（空間大量）→ 研究範圍 → 切 5–30 獨立單元 → 多 worktree 背景分身 → 各自測試+發 PR。鐵則：先掃描分類，確認真有「大量又獨立」才用。
- **`/loop`**：同一件事每隔一段時間自己重複（時間反覆）。兩種：固定間隔 `/loop 5m /x`、自我定速 `/loop`（本 session 開頭實際示範過：醒來→檢查→沒事→排 30 分後再看→使用者喊停結束）。關鍵限制：綁本機對話視窗，關窗/關機就停。
- **`/schedule`**：指定未來時間在雲端自動跑（排程，關機照跑）。定期重複 or 一次性。
- **三方決策圖**：Q1 改很多檔案？→ batch；否則 Q2 電腦會一直開著？→ 開著=loop、關機也要跑=schedule。

### 4. schedule + batch / schedule + loop 組合釐清

- 關鍵觀念：`/schedule` 是「引擎＋鬧鐘」（雲端＋時間），batch/loop 是「任務的形狀」，把形狀寫進排程任務裡。
- **schedule+batch**：定時雲端做大量平行維護（依賴升級、補缺檔），各自發 PR。caveat：雲端 headless，batch 的互動詢問步驟不可用 → prompt 要寫「自主執行、不要問、直接發 PR」。
- **schedule+loop**：`/schedule` 本身就是雲端版 loop，不會在 schedule 裡再打 loop（多餘）；組合＝用排程定時做 loop 式巡檢推進。
- **誠實 caveat**：雲端 schedule 連不到本機檔案/NUC/內網 DB → 需連內部資源者改用 NUC/VPS cron（呼應 tech-stack 既有規則）。

---

## 關鍵技術筆記

- Claude Code hook command 用正斜線路徑代表走 sh/Git Bash 解析，`%VAR%`（cmd.exe 語法）不會展開；可攜變數要用 `$CLAUDE_PROJECT_DIR`（指本專案根，比 `Path.home()` 更精準）。
- `/batch` 反模式：單檔/少量改動不該開並行編排（本 repo 無 PR workflow，直接 commit main）。
- `/loop`（本機 session-bound）vs `/schedule`（雲端常駐）的分水嶺＝「電腦要不要開著」；兩者是取代關係不是疊加。
- 語音 TTS 流程穩定：Write `skills/_answer.txt` → taskkill say_ui.exe → start `skills/dist/say_ui.exe --autoplay`，每回合關舊開新。

---

## 產出檔案

| 檔案 | 動作 | 說明 |
|------|------|------|
| `.claude/settings.json` | 修改 | hook 路徑改 `$CLAUDE_PROJECT_DIR`（commit 010b7f2，已 push）|
| `skills/_answer.txt` | 多次覆蓋 | 語音朗讀內容（batch/loop/schedule 各章節，本機暫存非版控重點）|
| `summary-02-sessions/2026-06-23/session10-summary.md` | 新增 | 本收工 summary |

---

## HANDOFF（下次 session 優先處理）

### 立即行動

- [ ] （選配）若想實作雲端排程：把「每週一掃 demo 章節缺 STEP_LOG.md 就補並發 PR」建成 `/schedule`——但須先確認本 repo 是否要啟用 PR workflow（目前是直接 commit main）。
- [ ] 繼續第 10 章課程：本專案是 17 課學習計畫，目前學到第 9 章外掛實戰 + 額外補了三指令教學，可用 `/next-lesson 9` 進第 10 課。

### 進行中（需接續）

- 三指令（batch/loop/schedule）教學已完成全部講解，使用者最後問題已答；無未完成的程式碼工作。工作樹乾淨。

### 注意事項

- `/batch` 在此 repo 多為過度工具——除非真有「大量又獨立」的多檔改動，否則直接改+commit main。
- 雲端 `/schedule` 碰不到本機/NUC/內網資源；那類排程一律走 NUC/VPS cron。
- 語音 TTS 教學模式：互動教學下每次回答前要寫 `_answer.txt` + 關舊開新 say_ui.exe（已長期授權，唯一免徵詢例外）。
