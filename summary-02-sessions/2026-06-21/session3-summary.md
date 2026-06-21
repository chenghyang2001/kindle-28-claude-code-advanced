# Session 3 Summary — GSD（Get Shit Done）安裝與實戰學習

**日期**：2026-06-21
**主題**：從 Kindle 影片認識 GSD → 全域安裝 → 手把手用 GSD 做一個計算機 Hello World

> 本 session 未碰 Kindle 課程主線（第 15 課仍未完成），全程在學習與實作 GSD 框架。

## 完成事項

### 1. GSD 影片研究（第 05 章）

- 用 `~/Downloads/ffmpeg/bin/ffmpeg` 抽出 `第05章｜擊敗上下文腐化：精通_GSD_框架.mp4`（460 秒）音訊
- 用 `faster_whisper`（small / int8 / zh）轉錄成 `~/Downloads/gsd_transcript.txt`（216 行、含時間戳）
- 釐清 GSD 定義：**Get Shit Done**，作者 TÂCHES（影片誤稱 Glitter Cowboy），對抗「上下文腐化」的工作流；核心＝隔離 + markdown 外接記憶 + 四階段循環（討論/規劃/執行/驗證）+ 多代理

### 2. 安裝 GSD（全域）

- `npx -y get-shit-done-cc --claude --global` → **v1.42.3**，裝進 `~/.claude`
- 裝了 67 個 `gsd-*` skills + agents + hooks，`gsd-sdk` link 到 `%APPDATA%\npm\gsd-sdk.cmd`
- 確認 GSD 官方支援多工具（Claude/Codex/Gemini/Cursor…）；本機只裝 Claude 版（未裝 Codex 版，使用者明確不要）

### 3. 手把手實作 GSD 計算機（在獨立 repo）

- 新 repo `~/workspace/gsd-hello-calculator`
- 走完完整 GSD 流程：`/gsd-new-project`（Interactive/Coarse/Sequential/git Yes、Research No/PlanCheck No/Verifier Yes、Vertical MVP、跳過 UI-SPEC）→ `/gsd-plan-phase 1` → `/gsd-execute-phase 1` → `approved`
- 產出 `index.html`（純 HTML+JS 計算機，textContent 防 XSS、除零/非數字錯誤處理），機器驗證 10/10
- 我額外寫了 `GSD-學習筆記.md`（操作小抄 + 概念總複習）到該 repo

## 關鍵技術筆記

- **GSD 指令在本機是連字號**：文件寫 `/gsd:xxx`，本機要打 `/gsd-xxx`（冒號→連字號）
- **兩個 slash 指令不能同一行**：`/clear` 是 CLI 內建、立刻清空、不吃後綴；要分兩次 Enter。且 `/clear` 對 execute 是「建議非必須」（executor 是獨立乾淨子代理）
- **本機可做影音轉錄**：`~/Downloads/ffmpeg/bin/ffmpeg` + `faster_whisper`（已安裝）可把 mp4 → 文字；Read 工具不能讀影音
- `~/.claude` 不是 git repo（session 收工無第二個 git push 對象）

## 產出檔案

| 檔案 | 說明 | repo |
|------|------|------|
| `summary-02-sessions/2026-06-21/session3-summary.md` | 本摘要 | kindle-28 |
| `~/workspace/gsd-hello-calculator/index.html` | GSD 做出的計算機 | gsd-hello-calculator |
| `~/workspace/gsd-hello-calculator/GSD-學習筆記.md` | GSD 操作小抄 + 概念複習 | gsd-hello-calculator |
| `~/Downloads/gsd_transcript.txt` | 第 05 章影片逐字稿 | （Downloads，非 repo） |
| `~/.claude/skills/gsd-*`（67 個）+ agents + hooks | GSD 全域安裝 | （非 git） |

## HANDOFF（下次 session 優先處理）

### 立即行動

- [ ] 回到 Kindle 主線：第 15 課「安全與成本」仍未完成——`demo/[15-安全與成本]/answer/ex01-answer.md` 已寫（ex01），但 **ex02（權限/prompt cache）、ex03（綜合 checklist）尚未做**
- [ ] 第 15 課完成後跑 `/study-scaffold carry 15` 帶到第 16 課
- [ ] （選配）若要把 GSD 計算機 repo 推上 GitHub，需先建 remote（目前無 remote）

### 進行中（需接續）

- Kindle 課程進度：第 1~14 課完成；**第 15 課僅 ex01 完成**（互動教學模式：一次一題、要語音播報、未經同意不跑指令）
- GSD 學習：已跑完一輪完整流程，使用者已具備獨立操作能力；延伸練習（加 phase / `/gsd-autonomous` / `/gsd-debug`）尚未玩

### 注意事項

- 第 15 課要回到「互動式教學模式」：一次一題、停下等答、使用者說「你回答」才給解、每次回答用 `say_ui.exe` 語音播報、未經同意不執行指令（語音三步例外）
- GSD 計算機是**獨立 repo + 獨立 Claude session**（在 `~/workspace/gsd-hello-calculator`），不要跟 kindle repo 混
- 影音轉錄是本機可用能力，未來遇到 mp4/m4a 問題可直接 ffmpeg + faster_whisper
