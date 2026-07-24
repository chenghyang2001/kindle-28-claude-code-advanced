# Session 22 — 開源資源探勘系列 + book-viz-pack 雙書實戰 + NLM 雙層 auth 修復

**日期**：2026-07-24
**機器**：NB00547
**主題**：課程圖片查證 → 食譜庫改造示範 → 兩本 Kindle 書視覺化 → NotebookLM auth 全線修復

---

## 完成事項

### A. 開源資源探勘系列（3 份文件 + 3 封 Gmail）

1. **課程圖片 5 個開源資源查證**：GitHub 即時查星數與活躍度，發現圖片有三個問題——等級落差被視覺抹平（50.7k/29.8k vs 幾百星）、`claude-starter-kit` 未標 owner（205 個同名 repo，最高僅 331⭐）、遺漏 `VoltAgent/awesome-claude-code-subagents`（23.6k⭐）。產出 `doc/claude-code-opensource-resources.md`。
2. **claude-code-templates 指令目錄探勘**：展開 25 個分類（原誤報 24，已更正）中的 5 個相關分類共 58 個指令。挑出值得撈的 3 個：`git-bisect-helper`、`add-mutation-testing`、`gemini-review`。命中率約 5%，印證「挑著撈」原則。產出 `doc/claude-code-templates-commands-catalog.md`。
3. **awesome-claude-code 深入探勘**：零基礎介紹 awesome list 文化，實測 README 含 25 分類 225 個專案。展開 Memory & Context Persistence（9 個）與 Multi-Agent Orchestration（僅 2 個）對照本機方案，結論：檔案式三層記憶不換，但吸收 Selvedge「記 why」與 roampal「壞建議降權」兩個概念。產出 `doc/awesome-claude-code-deep-dive.md`。

### B. 食譜庫改造實戰（抽象原則 → 可執行示範）

從 `davila7/claude-code-templates` 撈 `documentation/troubleshooting-guide.md`（280 行、K8s/值班升級矩陣導向），瘦身改造成 `.claude/commands/pitfall-guide.md`（~40 行，資料來源改為本專案 STEP_LOG + git log，輸出改「症狀/根因/解法/預防」四段式，全繁中）。系統確認註冊生效後實跑 `/pitfall-guide --all`，產出 `docs/pitfall-guide.md`（12 個坑分 5 類）。

### C. book-viz-pack 雙書實戰（2 本 × 5 圖 + PPTX）

| 書 | notebook ID | 產出 |
| --- | --- | --- |
| Kindle 34《Agentic Spec-Driven Development》(Anatoly Volkhover, 13 章) | `c3c1718c-5423-4020-a8b1-baf2b4467c1f` | `mermaid/agentic-sdd/` 5 圖 + 後追加第 6 張對映圖 = 6 頁 PPTX |
| Kindle 33《Claude Code for CTOs》(Javier Rayón, 22 章) | `2d65f31c-c4ad-438c-914a-a1d1836865db` | `mermaid/claude-code-ctos/` 5 圖 + 5 頁 PPTX |

兩本的素材都因本機 NLM auth 過期而改派 @小雲 走 VPS `notebooklm ask` 抽取（章節核心概念 + 方法論架構 + 10 術語關係），素材品質反而優於直接抽 PDF。

### D. build_pptx.py 升級（三 agent 鐵律，medium 複雜度）

使用者要求 PPTX 每頁加圖表名稱標題。走 code-writer → code-qa（不派 reviewer，使用者決定）：

- 新增 `_title_from_stem()`：`1-心智圖` → 「1. 心智圖」，無數字前綴則用原 stem
- 新增頂部標題文字框（0.7 吋帶、26pt 粗體 #333333 置中、**paragraph.font 與 run.font 雙層設定**）
- 圖片改置標題帶以下（IMAGE_TOP_IN = 1.0 吋）等比例縮放
- QA VERDICT: **OVERALL PASS**（V1-V5 全過，3 test case：5 頁標題順序正確且圖不重疊 / `cover.png` 無前綴不崩潰 + 空目錄繁中報錯 exit 1 / 正式產物重生驗證）
- 影響範圍是 skill 層，之後每本書的合輯自動帶頁標題

### E. Kindle 34 × GSD 深度對照分析

實查本機 `.planning/` 產物結構與 67 個 gsd skill，做出 10 個概念的對映表：

- ✅ 對得上（5）：Bootstrap / Durable Rules / Polygraph / Devil's Advocate / Course Correction
- ⚠️ 張力（2）：SOT（GSD 的 PLAN.md 是一次性施工圖非活文件）/ Intake Log（GSD 結構化整理 vs 書堅持逐字）
- 🔴 缺口（3）：**Dry Run**（GSD 的 plan-checker 審計畫，非壓測規格）、**Glossary**（grep 67 skill 零命中）、**Artifact 不可直編**
- 結論：最該補的是 Glossary（成本最低、對自造術語密集的本環境效益最大），可放 `~/.claude/instructions/` 全專案共用
- 對映表已做成第 6 張圖進 PPTX

### F. NotebookLM 雙層 auth 全線修復

| 通路 | auth 檔 | 修復方式 | 結果 |
| --- | --- | --- | --- |
| CLI | `~/.notebooklm/storage_state.json` | 使用者跑 `bash ~/.claude/scripts/nlm-login.sh` | ✅ 15:09 更新，實測通過 |
| MCP | `~/.notebooklm-mcp/auth.json` | 使用者跑 `npx -y notebooklm-mcp-server auth` | ✅ 16:38 更新（15 cookies），但執行中的 server 需重啟才生效 |

### G. 其他

- AI 短影音工具研究（Dr Julie 風格 Shorts 的 A/B/C 三路線：Captions 後製 / Argil 數位分身 / Sora2+n8n 純生成），寄自己 + 太太信箱
- SDD 資源盤點：awesome-claude-code 搜 spec-driven **命中 0**（連 GitHub Spec Kit 都沒收錄，策展死角實證）；真正的 SDD 資源在 claude-code-templates 的 `project-management` 分類（PAC 五件套 + create-prd/prp/jtbd）
- `~/.claude` repo 補提交：`xlsx-to-dialable` 腳本（444 行）、`.gitignore` 補 `.ruff_cache/`、settings.json、三個專案 MEMORY.md

---

## 關鍵技術筆記

1. **NLM 雙層 auth 各自獨立，修一邊不會修另一邊**：`nlm-login.sh` 只寫 CLI 的 playwright storage_state；MCP 要另跑 `npx -y notebooklm-mcp-server auth`。MCP 的啟動設定在 `~/.claude.json` 的 `mcpServers`（`npx -y notebooklm-mcp-server start`）。
2. **MCP auth 寫檔成功 ≠ 立即生效**：長駐 stdio server 行程仍持舊 cookie，`refresh_auth` 回報「已重載」但實際呼叫仍 expired，需 `/mcp` 重連或新 session 才撿到。
3. **互動式 OAuth 不能用 `run_in_background`**：detached 執行會讓 Chromium 一開就被關（`browserContext.newPage: Target page... has been closed`）。必須前景執行且**使用者要在螢幕前完成登入**。
4. **`page.goto` 30 秒 timeout 可能是暫時性**：首次冷啟失敗，快取轉熱後第二次就過了頁面載入階段。判別網路是否真的不通要另外測（實測 notebooklm.google.com HTTP 200 / 0.5s）。
5. **VPS 版 notebooklm CLI 結構與本機不同**：頂層是 `notebooklm list`（**沒有** `notebook` 子指令），且有本機沒驗證過的 `ask` / `configure` / `history` chat 指令。非互動式 SSH 不載入 `~/.profile`，要用絕對路徑 `/home/claude/.local/bin/notebooklm`。
6. **NLM 下載的章節 PPTX 是圖片型**：python-pptx 抽不到文字（13 檔只抽到 195 字元，全是檔名）。要拿章節內容得走 `ask`。
7. **build_pptx.py 路徑必須 cygpath -w**：直接餵 MSYS 路徑（`/c/Users/...`）Python 會找不到目錄。
8. **`~$*` 是 Office 開檔鎖定檔**：PowerPoint 開著時會出現在 git status，已補進專案 `.gitignore`。

---

## 產出檔案

| 檔案 | 說明 | commit |
| --- | --- | --- |
| `doc/claude-code-opensource-resources.md` | 5 個開源資源查證與採用建議 | `5bef3ea` |
| `.claude/commands/pitfall-guide.md` | 食譜庫改造產物（slash command） | `5bef3ea` |
| `docs/pitfall-guide.md` | 全專案踩坑指南（12 坑 5 類） | `5bef3ea` |
| `doc/claude-code-templates-commands-catalog.md` | 5 分類 58 指令目錄 + 挑選建議 | `99c00b0` |
| `doc/awesome-claude-code-deep-dive.md` | awesome list 介紹 + 兩分類對照 | `a08208d` |
| `doc/ai-shorts-video-tools-research.md` | AI 短影音工具三路線 | `a8d3fad` |
| `mermaid/agentic-sdd/`（mmd×6 + png×6 + pptx） | Kindle 34 視覺包 | `a8d3fad` / `ecd1371` |
| `mermaid/claude-code-ctos/`（mmd×5 + png×5 + pptx） | Kindle 33 視覺包 | `6a3241b` |
| `.gitignore`（補 `~$*`） | Office 鎖定檔排除 | `ecd1371` |
| `~/.claude/skills/book-viz-pack/scripts/build_pptx.py` | 頁標題功能（+73 −13） | `9010f79`（**`~/.claude` repo**） |
| `~/.claude/skills/xlsx-to-dialable/scripts/xlsx_to_dialable.py` | 撥號清單轉換（444 行） | `1674ccf`（**`~/.claude` repo**） |

> 上表前 9 列的 commit 屬 `kindle-28-claude-code-advanced` 專案 repo，最後 2 列屬 `~/.claude` repo，`git show <hash>` 要在對應目錄執行。

---

## HANDOFF（下次 session 優先處理）

### 立即行動

- [ ] **驗證 MCP NotebookLM 是否已生效**：本 session 結束時 `~/.notebooklm-mcp/auth.json` 已更新（16:38、15 cookies）但執行中的 server 仍持舊 cookie。操作步驟：①先 `/mcp` 重連（或直接開新 session，server 會重啟）②呼叫 `mcp__notebooklm__notebook_list` 實測。若仍失敗則 auth.json 格式或 server 版本（v3.0.7）有其他問題——此時直接改用 CLI（已確認正常），不必卡在 MCP。
- [ ] **補 `~/.claude/skills/xlsx-to-dialable/SKILL.md`**：該目錄目前只有 `scripts/`，缺 SKILL.md 就沒有 description 與觸發詞，Claude Code 不會當 skill 載入，等於只是一支要手動呼叫的獨立腳本。
- [ ] **（可選）建立 GLOSSARY.md 補 GSD 缺口**：本 session 分析出 GSD 三大缺口中 Glossary 最值得補、成本最低。建議放 `~/.claude/instructions/glossary.md` 讓全專案共用，定義自造術語（小核/小雲/小腦、鐵律、三 agent、閉環、Session 等），格式用「定義 + 明確排除的反義」。

### 進行中（需接續）

- **book-viz-pack 的 SKILL.md 抽取表待補兩條**：①NotebookLM URL 作為輸入來源（本 session 用了兩次但 SKILL.md 未定義此型別，目前靠臨場判斷走 VPS ask）②NLM 下載的章節 PPTX 是圖片型、python-pptx 抽不到字。
- **NotebookLM 兩筆殘留 error source 未清**：Kindle 34 的 `ch13.pdf`（ID 前綴 `6a7b9067`）與 Kindle 33 的 `ch12.pdf`（ID 前綴 `4a71fd68`）各有一筆上傳失敗殘骸。刪除是破壞性操作，本 session 未動，等使用者指示。

### 注意事項

- **`demo-sdd-spec-kit` 待辦刻意不排程**：使用者本 session 明確表示「不要順手把過期的 demo-sdd-spec-kit 排回來跑，keep it the way it is now」。記憶裡那筆提醒維持原狀，不要主動觸發。
- **三 agent 鐵律的 reviewer 決策權在使用者**：本 session medium 複雜度改動，使用者選擇不派 code-reviewer，Writer→QA 兩段就收工，結果 QA PASS。下次同類改動仍要問，不要自行預設。
- **互動式 OAuth 一律讓使用者用 `!` 前綴自己跑**（且提醒 `!` 前不能有空格），不要用 `run_in_background`——detached 會殺掉瀏覽器。
- **usage 已達 Week 64%**（session 結束時），跨到 07-25 09:00 才重置，下個 session 注意成本。
