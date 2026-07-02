# Session 17 摘要：GSD→VPS→Ralph 第三次演練「全 VPS 自主（run A）」+ 自我通知

> 日期：2026-07-03 ｜ 題目：morse-cli（摩斯電碼 encode/decode）｜ 模式：全 VPS headless 自主
> 前兩次：todo-cli（S15/16 前）、expense-cli（S16）——皆本機互動跑 GSD。本次首度把 **GSD 規劃也搬上 VPS headless 跑**。

## 這次要驗證什麼

同一條 GSD→Ralph 流水線，第三次換題材（**刻意選無狀態純演算法**：摩斯電碼 encode/decode，對照前兩次都有 JSON 存檔的 todo/expense，看接合縫會不會更薄）。**最大差異：走「A 路 = 全 VPS 自主」**——不只 Ralph，連 GSD 規劃都用 `claude -p` headless 無互動在 VPS 上跑；使用者離線後由 VPS 自己寄 Telegram + Gmail 回報結果。

## 關鍵決策：A vs B

使用者問「能不能純下命令讓 VPS 自己跑完 GSD」。回答：**GSD 預設是互動式**（靠 AskUserQuestion 在灰色決策點問人，這正是前兩次計畫緊的原因）。兩條路：

- **A（本次選）**：headless `claude -p` 叫 GSD 自主決策、禁用問問題。品質換速度。
- **B**：VPS 開 tmux 互動 session 保留人拍板。保品質但非一氣呵成。

使用者要「驗證流程 + 最快看結果」→ 選 A。

## 執行軌跡

1. **勘查 VPS**：`claude` 2.1.146 ✓、Max $0 ✓、`ralph`/`pytest` ✓，但 **GSD 完全沒裝**（走 A 最大變數）。
2. **裝 GSD**（踩坑）：GSD 真身是 npm 套件 `get-shit-done-cc` v1.42.3，完整 footprint = 67 skills + 33 agents + `~/.claude/get-shit-done/`（3.5M workflows）+ `gsd-sdk` CLI + hooks。**只 scp skills+agents 不夠**（漏 get-shit-done/ 與 gsd-sdk）。正解：`npm install -g get-shit-done-cc` → `get-shit-done-cc --global --claude`（installer 一次擺對）。
3. **spec 上 VPS**：本機寫 `REQUIREMENTS.md`（8 邊界案例；末段明講「目標=Linux、不加 Windows/cp950」——把上次跨平台編碼坑的教訓寫進驗收）→ scp。
4. **headless GSD**：`claude -p "<完全自主、禁 AskUserQuestion、灰色地帶自己用 REQUIREMENTS 決定>" --dangerously-skip-permissions --verbose` 丟 tmux。**成功**——GSD 跑完 new-project（單階段 roadmap）+ plan-phase（2-task TDD PLAN，含精確 Morse `<format_contract>`，且把我的平台約束吃進 constraints），EXIT=0，6 個 GSD 繁中 commit。中途 log 只有 START（headless buffer 到結束）→ 看 `.planning/` 檔案數 + commit 數判進度。
5. **接合縫翻譯**：GSD PLAN → Ralph 大腦檔（`.ralph/PROMPT.md`/`fix_plan.md`/`AGENT.md`，本機 Write .md + scp）；`.ralphrc` cp 前作 expense + sed 改名。
6. **自我通知 runner**：一支 `ralph-run-notify.sh` 串 ralph-enable-ci → 覆蓋大腦檔 → `ralph --verbose` → 驗 pytest → git commit + `gh repo create --public --push` → 寄 TG（`notify.py`）+ Gmail（inline smtplib）。丟 tmux，本機不輪詢。

## 踩到的坑（重要）

- **`ralph --dry-run` 是無限模擬迴圈、永不返回**：放進無人值守 runner 當 sanity step → 整個腳本靜默假死在 dry-run，`ralph --verbose` 永不觸發，使用者會空等一封永不來的信。**修法：移除 dry-run**（它只適合互動時人工 Ctrl-C）。抓到全靠交棒前的健康檢查（呼應「先自己驗證再告知」）。
- **成本安全**：`~/.env_vars` 可能藏 `ANTHROPIC_API_KEY`。做法：Ralph 本體跑乾淨環境 + `unset ANTHROPIC_API_KEY`；憑證只在寄信的**隔離 subshell** 內 source，永不外洩到 Ralph（確保全程 Max $0）。

## 交棒狀態（使用者離線）

- GSD 規劃：**完成**（PLAN.md，2 TDD task，8 邊界案例）。
- Ralph 自主執行：**進行中**（tmux `morse`，Loop #1 起跑，實作 test_morse.py → morse.py）。
- **完成後 VPS 自寄 TG + Gmail**：成功報 pytest+repo 連結，失敗報錯誤位置 + log 末段。
- repo：`chenghyang2001/gsd-ralph-morse`（Ralph 完成後自動 push public）。

## 帶走的重點

1. **GSD 可 headless 全自主跑**：只要 prompt 明講「無人、禁 AskUserQuestion、自主決策」，`claude -p` 能把 GSD 規劃跑完不卡——但品質退回 AI 自己猜（A 路的代價）。
2. **裝框架用官方 installer，別手搬**：scp 拼湊會漏相依（get-shit-done/ + gsd-sdk），npm 一鍵才完整。
3. **無人值守腳本嚴禁「永不返回」步驟**：dry-run 這種模擬迴圈是靜默假死元兇。
4. **自我通知 = 離線交棒的正解**：runner 自寄比派 sub-agent 輪詢穩（後者長輪詢會 timeout 被砍）。
5. 把上次教訓寫進這次 spec（平台講死）→ 這次不會再踩跨平台編碼坑。

> 詳見記憶檔 [[gsd-on-vps-headless]] 與 [[gsd-ralph-vps-pipeline]]。
