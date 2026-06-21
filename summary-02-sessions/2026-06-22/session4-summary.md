# Session 4 Summary — 第六章 Ralph 框架互動教學 + 雙 demo 實戰

**日期**：2026-06-22
**主題**：《Claude Code Advanced》第六章「用 Ralph 框架打造全自動開發代理人」互動式語音教學，外掛版 + 獨立版雙實戰演練，GSD vs Ralph 比較。

---

## 完成事項

### 1. m4a 語音轉錄 + 摘要

- 用本機 faster-whisper（base 模型）轉錄 `第06章｜用Ralph框架打造全自動開發代理人.m4a`（36MB），產出 489 句逐字稿 `~/Downloads/ralph_ch06_transcript.txt`
- 還原同音錯字（Rough→Ralph、城市嘛→程式碼、TMAX→tmux、繪畫脫離→會話脫離、Frank Bryan→Frank Bria）後做繁中摘要

### 2. 第六章互動式語音教學（8 題問答，全程 say_ui 語音播報）

- 第1題：工程師 = AI 保母 / 走走停停的指令消耗戰
- 第2題：適合任務 = 目標明確 + 過程機械化
- 第3題：Ralph vs 官方 Loop 差別 = 完全的外部控制權（非黑盒子）
- 第4題：自我評估 = 靠 npm test 的 exit code（客觀裁判）
- 第5題：外掛版只能跑短任務（無速率限制 / 寄生對話框 / 無窮迴圈燒錢）
- 第6題：獨立版 = headless `-p` 模式 + tmux 脫離(detach)
- 第7題：三大安全防護 = 速率限制(存檔休眠) / 斷路器(解析 stack trace) / 會話過期
- 第8題：15 端點實戰流程（import → 任務節點 → monitor → 過夜跑）

### 3. demo-ralph-01（外掛版練習，本機）

- 確認官方真有 `ralph-wiggum` 外掛（`/plugin install ralph-wiggum`，指令 `/ralph-loop`）
- 建計算機練習：calc.js(空殼) + calc.test.js(7 紅燈) + TASKS.md + package.json
- 兩個 .js 走 code-writer→code-qa 鐵律，QA PASS
- 使用者實跑 ralph-loop，calc.js 5 函式全綠（commit 7ec3d1b）

### 4. demo-ralph-02（獨立版演練，VPS）

- 釐清獨立版 = `frankbria/ralph-claude-code`（bash+tmux 原生，Windows 不能原生跑）
- 本機 WSL2 卡關：BIOS VT-x 未開（VirtualizationFirmwareEnabled=False），改走 VPS
- 派 @小雲 在 VPS 備好環境：node20/tmux/jq/git/claude CLI 全齊、Ralph 裝好、demo-ralph-02 staged、dry-run 通過（0 API call）
- 使用者在 VPS 重新登入 claude（Max 訂閱）後實跑 `ralph --monitor --calls 50 --timeout 30`
- **Ralph 第 1 圈即完成 5 端點實作，api.test.js 9/9 全綠（僅 1 次 API 呼叫、2379 tokens）**
- 觀察到 scope creep：Ralph 自己多建 server.js(真 HTTP server) + api.validation.test.js + server.test.js（共 17 測試）
- 主 Claude SSH 啟動 server.js + curl 實測每個端點 → JSON 行為全符合規格（含 400/404）

### 5. GSD vs Ralph 比較

- 產出 `docs/gsd-vs-ralph-comparison.md`（逐維度表 + 10 項任務路由 + 選邊口訣）
- 核心：GSD=大腦（結構化方法論、品質 gate、人 in-the-loop）；Ralph=引擎（自主迴圈、明確苦工無人值守）
- 用 mcp__gmail__send_email 寄到 <chenghyang2001@gmail.com>（含附件，Message ID 19eec30570c4d975）

---

## 關鍵技術筆記

- **Ralph 兩版本**：外掛版=`ralph-wiggum`（官方，寄生對話 session via Stop hook，短任務）；獨立版=`frankbria/ralph-claude-code`（bash+tmux，無人值守，三大護欄）
- **WSL2 開不了的根因排查順序**：先查 `VirtualizationFirmwareEnabled`(BIOS VT)、再查 VMP/WSL optional feature InstallState（1=啟用/2=停用）。本機卡在 BIOS VT-x=False，純韌體層、只能使用者進 BIOS 開
- **VPS claude auth**：`~/.claude/.credentials.json` 的 OAuth token 會過期，需互動 `/login`（Max 訂閱），且 `ANTHROPIC_API_KEY` 必須 NOT_SET（鐵律，否則改走 API 計費）
- **Ralph `--calls` 是每小時上限（rate limit）不是總迴圈數**；測試綠了不會自動停，靠完成暗號 / `--timeout` 收斂
- **Ralph scope creep 是真的**：規格/邊界不夠死，它會自己加戲（本次多建整個 HTTP server）

## 產出檔案

| 檔案 | 說明 |
|---|---|
| `~/Downloads/ralph_ch06_transcript.txt` | m4a 489 句逐字稿（非 repo） |
| `demo-ralph-01/{calc.js,calc.test.js,TASKS.md,package.json}` | 外掛版計算機練習（已 commit 7ec3d1b） |
| `demo-ralph-02/{api.js,api.test.js,api-spec.md,package.json,RUN.md}` | 獨立版 Todo API 演練（本機 staged；VPS `~/demo-ralph-02` 有實跑成果） |
| `docs/gsd-vs-ralph-comparison.md` | GSD vs Ralph 詳細比較（已寄 Gmail） |

---

## HANDOFF（下次 session 優先處理）

### 立即行動

- [ ] 第六章已上完（8 題）；若繼續課程，下一步是 study-scaffold 的第七課（或使用者指定章節）
- [ ] demo-ralph-02 本機版可選擇性實跑驗證（本機無法跑 Ralph 獨立版，但 `npm install && npm test` 可看紅燈起點）
- [ ] 若要常用 WSL2/Ralph 獨立版於本機，需先進 BIOS 開 Intel VT-x（i7-6700）

### 進行中（需接續）

- VPS `~/demo-ralph-02` 有 Ralph 全自動產出的完整 Todo API（含 server.js），測試 17 全綠，已驗證；如不再需要可請 @小雲 清理
- 本機 demo-ralph-02 未跑過 npm install（無 node_modules）

### 注意事項

- 互動教學模式 + 每次回答 say_ui 語音播報仍生效（CLAUDE.md 明文授權自動執行 taskkill+start+寫_answer.txt）
- Ralph 獨立版在 Windows 原生跑不了，必走 WSL2（需 BIOS VT）或 VPS
- demo-ralph-01/.claude/ 為 untracked（ralph-enable 產物），收工時注意是否要納入或忽略
