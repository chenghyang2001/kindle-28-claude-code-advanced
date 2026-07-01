# Session 摘要：GSD → VPS → Ralph 自主執行 demo（todo-cli）

**日期**：2026-07-02 ｜ 對應課程：`[05-GSD 框架]` + `[06-Ralph 自主迴圈]` 綜合實戰
**產出 repo**：<https://github.com/chenghyang2001/gsd-ralph-todo>

## 一句話

在本機用 **GSD** 把需求壓成可執行 `PLAN.md`，push 上 GitHub，在 **VPS** 用 **Ralph standalone**（frankbria/ralph-claude-code）無人值守迴圈蓋到 **pytest 11 passed**——全程走 Claude Max、**$0**。

## 成果數字

- Ralph：**4 loop / 3 API call / 12,641 tokens** → `exit_reason: plan_complete`
- 測試：**11 passed in 0.73s**
- App：`todo.py`（Python stdlib only，4 命令 add/list/done/rm，JSON 持久化）+ `test_todo.py`（subprocess + tmp_path 隔離）

## 流水線（可重現）

1. **本機 GSD**：`/gsd-new-project`（→ PROJECT + roadmap，1 phase，10/10 需求）→ `/gsd-plan-phase 1`（→ 01-01/01-02-PLAN.md + SKELETON.md，TDD 規劃）
2. **交接 VPS**：public repo `git push` → VPS `git clone`（免認證）→ 驗 auth（`ANTHROPIC_API_KEY` 未設走 Max、`claude -p` 實測 OK）
3. **Ralph**：`install.sh` → `ralph-enable-ci` 搭 `.ralph/` 骨架 → 客製 PROMPT/fix_plan/specs（翻自 GSD PLAN）+ 修 `.ralphrc` ALLOWED_TOOLS → `tmux` detached 跑到 pytest 綠自停

## 關鍵重點（踩過的坑）

- **GSD↔Ralph 接合縫 = 格式翻譯**：GSD 階層 `PLAN.md` → Ralph 扁平勾選 `fix_plan.md` + `PROMPT.md`（含退出規則）。跳過 `/gsd-execute-phase`，把施工圖交給 Ralph。
- **3b-2A（必修）**：`.ralphrc` 的 `ALLOWED_TOOLS` 是 Node 預設（`Bash(npm *)`、`Bash(pytest)` 無參數）；Python 專案要精準加 `Bash(python3 *)/Bash(pytest *)/Bash(pip *)`，否則 Ralph 按不了自己的計分板（權限 vs 能力矛盾）。
- **auth 先綠燈**：Ralph 每輪呼叫 `claude`，`API_KEY` 保持未設 → Max、$0。
- **detached 用 tmux**，不要 `ssh 'cmd &'`（channel 收不乾淨回 255）。
- **`.md`/config 用本機 Write + scp**，別在 `ssh '...'` 塞 heredoc（引號/CJK 地獄）。
- **GSD 指令冒號 vs 連字號**：官方 plugin 用 `gsd:xxx`，本機是全域 skills 用 `gsd-xxx`（SKILL.md 硬編碼 31 處提示不一致，非顯示 bug）。
- **規格越小 Ralph 越準**：Ralph 內建反 scope-creep 護欄（測試 ≤20%、Implementation > Docs > Tests）。
- **TDD 是 Ralph 的計分板**：測試先行讓「完工」= pytest 紅→綠的客觀訊號。

## 交付

- 重點文件：`gsd-ralph-todo/docs/DEMO-GSD-RALPH-VPS.md`（完整 walkthrough）
- Gmail：已寄 <chenghyang2001@gmail.com>（含附件）
- NotebookLM：notebook `191d45c1…`（語音 + 簡報生成中）
