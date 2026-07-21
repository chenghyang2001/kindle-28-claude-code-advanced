# Session 17 摘要（2026-07-22）

> 編號註記：`summary-02-sessions/` 既有檔停在 session16；記憶索引的非正式計數曾提及 S18（worktree-skill-subagent-binding）、S19（git-for-windows-abspath）。本檔按 **summary 檔序列**編為 17，涵蓋本次連續 session 的兩大主題（worktree 平行化收尾 + book-viz-pack 新 skill）。

## 主題

1. **Git Worktree 平行化**（前半，/compact 前）
2. **book-viz-pack 新 skill**：一本書 → 固定 5 圖 + PPTX 合輯（後半）

---

## 完成事項

### A. Git Worktree 平行化（承接《平行化》PDF）

- 建 `demo/parallel-worktree/parallel-worktree-demo.sh`：2 軌 headless `claude -p` 各建 worktree 產檔 → 合併 → 清理，對照手冊 5 階段生命週期。走三代理人 + 4 輪 QA，實跑 EXIT_CODE=0（track-a fast-forward、track-b 3-way merge 驗證）。commit `072f07a`。
- 包成 `/parallel-demo` slash command（薄包裝）。commit `6e1a590`。
- 寫 `doc/worktree-parallel-playbook.md`：demo→真實 8 改點、合併決策、混合執行模式、劇本 A/B、護欄、工具對照、選型決策樹。commit `4e11647`。
- QA 抓到 2 個 Git for Windows 真實環境雷（見記憶 `git-for-windows-worktree-abspath-gotcha`）。

### B. book-viz-pack skill（本次核心）

- 需求：讀 Kindle 書 → 快速視覺化理解，固定產 5 張繁中圖（心智/學習流程/架構分層/能力堆疊/概念關係）+ PPTX 合輯。
- 探勘先行：發現 golden sample（`mermaid/*.mmd` 手動 4 圖）+ `mmd-gen` skill + 工具鏈（mmdc 11.14 / python-pptx 1.0.2）全在 → 決定複用不重造。
- 3 個設計岔路（AskUserQuestion）：獨立新 skill / 每本書一專案資料夾 / 架構圖+堆疊圖都要（→ 5 圖）。
- 直寫 7 份 `.md`（SKILL + 5 生圖契約 + style-guide，逃生門）。
- `build_pptx.py` 走三代理人：**code-writer（127 行）→ code-qa（PASS 3/3）→ code-reviewer（APPROVED, 0 MUST_FIX）**；reviewer 提的 dpi 註解已小修豁免修正。
- 端對端驗收：用 golden-sample 重用技巧（4 圖已對應契約 1/2/4/5，只補生第 3 張架構分層圖）→ render 5 圖 → build pptx（5 頁）→ 目視驗證新第 3 張 CJK 無方塊。
- 提交：skill 本體 `~/.claude` commit `bc20eb1`；驗收產出本專案 commit `d8add5b`。
- 記憶：新建 `book-viz-pack-skill.md` + MEMORY.md 索引行。

---

## 關鍵技術筆記

- **mmdc CJK 雷**：render 必帶 `-p "$HOME/workspace/mermaid/puppeteer-config.json"`（本機 Edge 渲染），否則繁中 edge label 變空心方塊；`-s 2` 提解析度。
- **block-beta vs architecture-beta**：mmdc 11.14 下 `architecture-beta` render 失敗，堆疊/架構一律 `block-beta`（換行用 `\n` 非 `<br/>`）。
- **golden-sample 重用技巧**：既有手動 4 圖常對應新契約 1/2/4/5，只需補第 3 張即可湊滿 5 張跑完整 pipeline，省重讀整本 PDF。
- **三代理人價值再驗證**：QA 造 3 種長寬比 PNG 反推 EMU 比例，證等比例縮放 + natural sort 在極端形狀都對——純靜態 review 看不出。

---

## 產出檔案

| 檔案 | 動作 | commit |
| ------ | ------ | -------- |
| `~/.claude/skills/book-viz-pack/`（7 .md + build_pptx.py） | 新增 | `bc20eb1` |
| `mermaid/claude-code-advanced/`（5 mmd + 5 png + 圖表合輯.pptx） | 新增 | `d8add5b` |
| `memory/book-viz-pack-skill.md` + MEMORY.md 索引 | 新增 | 本機記憶（不進版控） |
| （前半）`demo/parallel-worktree/`、`/parallel-demo`、`doc/worktree-parallel-playbook.md` | 新增 | `072f07a`/`6e1a590`/`4e11647` |

---

## HANDOFF（下次 session 優先處理）

### 立即行動

- [ ] （可選）拿下一本 Kindle 書實測 `book-viz-pack` 完整觸發：丟 PDF/摘要 + 「幫我把這本書畫五張圖」→ 驗證 Phase 0 抽文字 + 5 圖全新生成路徑（本次驗收用了 golden 重用，尚未跑過「純新書從零抽取」的完整路徑）。
- [ ] （可選）把 session 編號與記憶非正式計數（S18/S19）對齊，避免未來混淆。

### 進行中（需接續）

- 無未完成工作。book-viz-pack 已建置、實測、版控、記憶留存，狀態 = 完成可用。

### 注意事項

- `book-viz-pack` 尚未在「純新書（無 golden 圖）」跑過完整 Phase 0→4；第一次對全新書觸發時留意 Phase 0 抽文字品質與 block-beta（第 4 圖）render 是否穩。
- `say_ui.exe` TTS 本 session 正常（互動教學語音播報全程可用），與 MEMORY.md 記的「2026-06-30 exit code 1 失敗」不同機／不同時，暫不覆蓋該記錄。
