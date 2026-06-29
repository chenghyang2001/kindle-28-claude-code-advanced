# Session 15 — GSD 練習新目錄建立 + SDD 轉錄合併

**日期**：2026-06-30
**專案**：kindle-28-claude-code-advanced

---

## 完成事項

### 1. GSD 練習新目錄 `demo-gsd-01-20260630` 建立完成

- **決策**：原 `demo-gsd-01/`（已完成 complete_task 練習）完全保留不動，另建日期目錄以隔離新一輪練習
- 使用 **code-writer → code-qa 兩步鐵律**（中等複雜度，3 test case，不派 reviewer）
- code-writer 產出 Writer Manifest（含 SHA256）
- code-qa 5 層驗證全 PASS：V1 存在、V2 hash 匹配、V3 語法、V4 動態執行、V5 ruff lint
- `PYTHONUTF8=1 pytest test_app.py -v` → **12 passed**

### 2. 基底檔案規格

- `app.py`（117 行）：`add_task` / `list_tasks` / `delete_task` 三函式，tasks 存 `list[str]`，**無 complete_task**
- `test_app.py`（66 行）：TestAddTask(5) + TestListTasks(3) + TestDeleteTask(4) = 12 tests
- SHA256 驗證：app.py `5123839d...`、test_app.py `44ea5ab7...`

### 3. SDD 音頻轉錄（背景任務，共多輪嘗試）

- 原始音頻：18.2 分鐘，繁中語音，內容為 SDD vs Vibe Coding 對比分析
- 最終採用分段策略：part0~3 各自轉錄（字數 1427/1425/1624/1010）
- 合併 4 段 → `demo-gsd-01-20260630/doc/sdd-transcript.md`（14602 bytes）

### 4. 非程式碼檔案複製

- `GSD-PRACTICE.md` 從 `demo-gsd-01/` 複製
- `requirements.txt` 從 `demo-gsd-01/` 複製

---

## 關鍵技術筆記

- **GSD brownfield 起點設計**：tasks 刻意保留 `list[str]` 而非 dict，讓 discuss-phase 的「資料結構選擇」成為真實的灰色地帶，學習者才有東西討論
- **原始 app.py 從未 commit 過**：上次 GSD 練習的第一個 commit（3261a00）就已含 complete_task，所以無法用 git checkout 還原——只能手動重建基底
- **中等複雜度鐵律應用**：2 個 .py 檔，各 50-150 行，走 code-writer + QA（3 test case），無 reviewer——減少等待時間且足夠驗證
- **TTS say_ui.exe 失敗**：exit code 1，原因未排查（非關鍵，GSD 練習不依賴 TTS）

---

## 產出檔案

| 檔案 | 說明 |
|---|---|
| `demo-gsd-01-20260630/app.py` | 3 函式 brownfield 基底（117 行） |
| `demo-gsd-01-20260630/test_app.py` | 12 個 baseline 測試（66 行） |
| `demo-gsd-01-20260630/requirements.txt` | pytest 依賴 |
| `demo-gsd-01-20260630/GSD-PRACTICE.md` | GSD 流程練習指引 |
| `demo-gsd-01-20260630/doc/sdd-transcript.md` | SDD 音頻轉錄合併（14602 bytes） |

---

## HANDOFF（下次 session 優先處理）

### 立即行動

- [ ] 在 `demo-gsd-01-20260630/` 目錄開 `claude`，執行 `/gsd-map-codebase` 開始 GSD 流程第一階段
- [ ] 修復 `skills/dist/say_ui.exe` TTS 失敗問題（exit code 1）
- [ ] 考慮把 `sdd-transcript.md` 送進 NotebookLM 生成語音摘要（18 分鐘 SDD 內容）

### 進行中（需接續）

- GSD 練習新目錄已就緒，但 6 個 GSD 階段尚未開始：`/gsd-map-codebase` → `/gsd-new-project` → `/gsd-discuss-phase` → `/gsd-plan-phase` → `/gsd-execute-phase` → `/gsd-verify-phase`
- 目標：在新目錄用 GSD 完整流程新增 `complete_task` 函式

### 注意事項

- `demo-gsd-01/` 完全未動（上次已完成的版本），新練習在 `demo-gsd-01-20260630/` 進行
- GSD 練習需要在**新的 Claude Code session** 中執行（`cd demo-gsd-01-20260630 && claude`），不是在這個 session
- SDD 轉錄內容涵蓋：Vibe Coding 風險 / SDD vs GSD vs ROVE / BMAD / Git Worktree 隔離 / agents.md 跨工具標準 / Tessa 激進觀點
