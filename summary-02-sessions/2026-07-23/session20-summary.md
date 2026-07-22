# Session 20 Summary — GSD demo 重做（雙 instance 協作）+ GSD→VPS→Ralph 第四輪

**日期**：2026-07-23
**模式**：雙 Claude instance 協作（另一個 instance 跑 GSD 六階段；本 instance 當監工 + VPS 部署）

## 完成事項

### 1. 《Defeating_Context_Rot.pdf》解讀（12 頁圖解簡報）

- 讀完全部 12 頁（PyMuPDF 轉 PNG 逐頁視覺解讀；系統宣稱 73 頁實為 12 頁）
- 內容 = demo-gsd-01 上一輪（6/23 完成版）的完整實戰回顧：GSD 六階段 + 3 次人類攔截 + 5 條黃金鐵律
- 三個攔截點成為本輪重做的對照 checklist：① 漏 new-project 會 `phase_found: false` 卡死 ② Walking-Skeleton 誤判 ③ Plan 漏 capsys UI 測試

### 2. demo-gsd-01 第三輪重做環境建置

- 依目錄隔離慣例建 `demo-gsd-01-20260723/`（從 6/30 乾淨起點複製 4 檔）
- baseline 驗證 `12 passed`；修掉 GSD-PRACTICE.md 兩處 `C:/Users/B00332` 硬編碼路徑
- 使用者在另一個 Claude instance 跑 GSD，本 instance 用 Monitor 工具全程盯檔案落地並語音導航

### 3. 另一 instance 的 GSD 進度（本 instance 監工紀錄）

- map-codebase：7 份報告（`.planning/codebase/`）✅
- new-project：PROJECT.md → research → REQUIREMENTS.md → ROADMAP.md（**3 phases**，上輪只 1 phase）✅ — 攔截點 1 這輪正確避開
- discuss-phase：`01-CONTEXT.md`（97 行決策合約：Task dataclass、不用 slots=True（Py3.14 回歸）、`list[Task]`、元素級複製）✅
- plan-phase：`01-01-PLAN.md`（dataclass + add/list 遷移）+ `01-02-PLAN.md`（delete_task 重寫，最高風險隔離）✅ — 攔截點 2/3 均未複發
- 決策差異對照：上輪 `list[dict]` → 本輪 `Task` dataclass；上輪重複 complete no-op → 本輪回報「已經完成過」

### 4. GSD→VPS→Ralph 第四輪（Phase 1 執行外包給 Ralph）

- 開獨立 repo **`chenghyang2001/gsd-ralph-complete-task`**（照 7/2 todo-cli / 7/3 expense-cli SOP）
- 格式翻譯：GSD 01-01/01-02-PLAN → `.ralph/fix_plan.md` 4 任務 + `.ralph/PROMPT.md`（done-gate = `python3 -m pytest test_app.py -q` **14 passed** + fix_plan 全勾）
- 防 scope creep 硬約束：只做 Phase 1、禁 complete_task、禁 ✓ 顯示、禁改繁中文案
- VPS 部署踩 2 坑均解：① OAuth token 過期 → scp 本機 `~/.claude/.credentials.json`（活到 10:42 含 refresh）救回 ② Ralph integrity check 缺 `.ralph/AGENT.md` → `ralph-enable-ci` 補骨架（客製檔未被覆蓋）
- Ralph 於 tmux `ralph-ct` 跑起（收工時 loop 3、Max $0）
- **完成通知已搬上 VPS 自我通知**：`~/ralph-notify.sh` 於 tmux `ralph-notify` 輪詢 status.json，終態時自打 Telegram + LINE（token 在 `~/.ralph-notify-env` chmod 600）

## 關鍵技術筆記

- **ssh 傳參陷阱**：`ssh host 'cmd' arg1 arg2` 的 args 會被串接進遠端命令字串（不是傳給 cmd 當 $1）——token 這樣傳會漏到遠端命令列且檔案內容為空。正解：本機 `printf ... | ssh 'cat > file'` stdin 管道
- **VPS OAuth 救援 SOP**：本機 `.credentials.json` 未過期時直接 scp 到 VPS `~/.claude/` + chmod 600，`claude -p` 立即復活（免互動 /login）
- **Monitor 工具紀律**：`sleep 45` 連鎖會被 harness 擋；持續盯檔案落地用 `Monitor` + until-loop；會重複觸發的條件要加 `seen` flag 防洗版
- worktree 平行判斷三問（本輪 01-01→01-02 有依賴邊 + 同檔 → Sequential 正解，PDF p9 同款決策）

## 產出檔案

| 檔案 | 說明 |
| ------ | ------ |
| `demo-gsd-01-20260723/`（4 檔 + `.planning/` 由另一 instance 產出） | 第三輪 GSD 練習環境（baseline 12 passed） |
| `~/workspace/gsd-ralph-complete-task/`（獨立 repo，已 push） | Ralph 執行包：app/test/.planning/.ralph（specs 5 檔 + fix_plan + PROMPT + .ralphrc） |
| VPS `~/gsd-ralph-complete-task/` | Ralph 執行現場（tmux ralph-ct） |
| VPS `~/ralph-notify.sh` + `~/.ralph-notify-env` | 完成自我通知 watcher（tmux ralph-notify） |

## HANDOFF（下次 session 優先處理）

### 立即行動

- [ ] 把 Ralph 產出同步回 `demo-gsd-01-20260723/`（從本機 `~/workspace/gsd-ralph-complete-task` 覆蓋 app.py/test_app.py + 補 `01-01/01-02-SUMMARY.md`），讓另一 instance 能接續 `/gsd:verify-phase` 走完 Phase 1 驗收
- [ ] Phase 2（complete_task 三態）與 Phase 3（CLI ✓ 顯示 + Windows cp950 驗證）尚未開始——繼續在另一 instance 走 discuss→plan→execute→verify，或再外包 Ralph
- [ ] （可選）清 VPS token 檔：`ssh claude@187.127.109.145 'rm ~/.ralph-notify-env'`

### 進行中（需接續）

- ✅ **VPS Ralph 已於收工前完成**：5 loops、`exit_reason=completion_signals`、pytest **14 passed**、fix_plan 4 任務全勾、4 個 commit 已 pull 回本機並 push 上 GitHub（`b8f7e48`）；TG + LINE 通知已由 VPS watcher 自動發送（watcher 已自收）
- 另一 Claude instance 停在 plan-phase 完成、execute 未跑（execute 已由 Ralph 代跑完畢，**勿在該 instance 重複跑 `/gsd:execute-phase`**，直接同步產出後走 verify）

### 注意事項

- demo-gsd-01-20260723 的 GSD 產出 commit 在主 repo（`kindle-28-claude-code-advanced`）；Ralph 的程式碼 commit 在獨立 repo `gsd-ralph-complete-task`——**兩邊 app.py 會分岔**，合併方向：Ralph repo → demo 目錄（以 Ralph 產出為準）
- VPS credentials 是本機副本（2026-07-23 10:42 過期但含 refresh token 可自續）；若再 401 → 重 scp 本機 `.credentials.json` 即可
- `.ralph-notify-env` 含 TG/LINE token（chmod 600），任務結束後可考慮 `ssh ... 'rm ~/.ralph-notify-env'` 清掉
- 上一輪 PDF 的 3 攔截點本輪全數未複發（GSD 框架升級 + research 層生效）——這是本輪最大的學習驗證點，可寫進期末比較文件
