# Session 16 摘要：GSD → VPS → Ralph 自主執行 demo（todo-cli）

**日期**：2026-07-02
**對應課程**：`[05-GSD 框架]` + `[06-Ralph 自主迴圈]` 綜合實戰
**產出 repo**：<https://github.com/chenghyang2001/gsd-ralph-todo>

## 完成事項

### 規劃（本機 GSD）

- 互動選定 App：`todo-cli`（Python stdlib、4 命令 add/list/done/rm、JSON 持久化、pytest 當唯一完工判準）
- `/gsd-new-project` → PROJECT.md + roadmap（1 phase，10/10 需求對應）
- `/gsd-plan-phase 1` → `01-01-PLAN.md`（add+list）、`01-02-PLAN.md`（done+rm）、`SKELETON.md`（架構契約），採 TDD（測試先行）

### 交接與執行（VPS Ralph standalone）

- 建 public GitHub repo + push（VPS clone 免認證）
- VPS 探勘：claude 2.1.146 / python3.12 / `~/ralph-claude-code`（frankbria v0.11.5）皆現成
- 驗 auth：`ANTHROPIC_API_KEY` 未設 → 走 Max、$0；`claude -p` 實測回 OK
- `install.sh` 裝 ralph 全域指令 → `ralph-enable-ci` 搭 `.ralph/` → 客製 PROMPT/fix_plan/specs（翻自 GSD PLAN）+ 修 `.ralphrc` ALLOWED_TOOLS + 裝 pytest
- `tmux` detached 啟動 Ralph 自主迴圈 → **4 loop / 3 API call / 12,641 tokens → pytest 11 passed，exit_reason: plan_complete**

### 交付（全自動）

- 重點文件 `docs/DEMO-GSD-RALPH-VPS.md`（完整 walkthrough）已 commit+push
- Gmail 寄至 <chenghyang2001@gmail.com>（含附件，ID `19f1f981d560ac37`）
- NotebookLM notebook `191d45c1…` 建立、加來源、觸發語音（task `e45a8889…`）+ 簡報（task `1b6c4932…`）

## 關鍵技術筆記

- **GSD↔Ralph 解耦**：`PLAN.md` 是唯一介面 → 跳過 `/gsd-execute-phase`，改用 VPS Ralph 當執行器；接合縫本質是「階層 PLAN → 扁平 fix_plan + PROMPT（含退出規則）」的格式翻譯
- **3b-2A 權限坑**：`.ralphrc` 的 `ALLOWED_TOOLS` 是 Node 預設，Python 專案必加 `Bash(python3 *)/Bash(pytest *)/Bash(pip *)`，否則 Ralph 按不了自己的 pytest 計分板
- **GSD 冒號 vs 連字號**：官方 plugin 用 `gsd:xxx`，本機是全域 skills 用 `gsd-xxx`（SKILL.md 硬編碼 31 處提示不一致，非顯示 bug）
- **detached 用 tmux**（`ssh 'cmd &'` 回 255）；ralph 在 `~/.local/bin` 非互動 SSH 要自己 `export PATH`
- **notebooklm CLI 這版**：`create --json` 的 id 巢狀在 `notebook.id`；`source add -n ""` 空值會加到當前 context 而非新 notebook → 要帶明確 NB id，`source list` 確認 ready 才 generate
- **auth 警告可能是舊的**：session 啟動報 NotebookLM-py MISSING，實測 `notebooklm list` 其實通

## 產出檔案

| 檔案 | repo | 說明 |
| ------ | ------ | ------ |
| `todo.py` / `test_todo.py` | gsd-ralph-todo | Ralph 自主產出（11 tests 綠） |
| `.planning/**` | gsd-ralph-todo | GSD 規劃產物（PLAN/SKELETON/ROADMAP） |
| `.ralph/**` + `.ralphrc` | gsd-ralph-todo | Ralph 執行設定（客製） |
| `docs/DEMO-GSD-RALPH-VPS.md` | gsd-ralph-todo | 完整 walkthrough 重點文件 |
| `doc/gsd-ralph-vps-demo-summary.md` | kindle-28（`60b0c21`） | 課程 session 摘要 |
| `memory/gsd-ralph-vps-pipeline.md` | ~/.claude | 可重現流水線 + 踩坑 memory |

## HANDOFF（下次 session 優先處理）

### 立即行動

- [ ] 開 notebook `191d45c1…` 確認語音（`e45a8889…`）+ 簡報（`1b6c4932…`）已生成完成，需要的話下載備份 / 上 VPS 播放清單
- [ ] 若要示範完整教學價值，可把 `gsd-ralph-todo` 的 demo 併進課程 `demo/[06-Ralph 自主迴圈]/` 當範例
- [ ] （選配）修 GSD SKILL.md 的冒號→連字號 31 處硬編碼提示（本次選 B 未改）

### 進行中（需接續）

- NotebookLM 語音/簡報在 NLM 後台生成中（觸發完成、尚未下載驗證）

### 注意事項

- VPS 上 `~/gsd-ralph-todo` 已是完整成品；`~/ralph-claude-code` 是 Ralph 本體（勿刪）
- Ralph 走 Claude Max（`ANTHROPIC_API_KEY` 保持未設）；若哪天變扣 API credits，先查是否誤設 env
- notebooklm CLI 生成前務必確認 source `Status=ready`，否則 `GENERATION_FAILED`
