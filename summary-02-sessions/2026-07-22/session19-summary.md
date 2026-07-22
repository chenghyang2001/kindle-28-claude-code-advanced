# Session 19 Summary — theme-factory 10 主題 PPTX + addwii 留言 + bt-mic-switch 排查

**日期**：2026-07-21 ~ 2026-07-22
**機器**：B00332 公司機（hostname NB00547）
**主題**：theme-factory skill 實戰（10 主題套色 PPTX + 實體列印）、addwii Shorts 留言、藍牙 HFP 麥克風深度排查

## 完成事項

### 1. theme-factory skill 實戰：圖表合輯 × 10 主題

- 開啟並解讀 `theme-showcase.pdf`（10 主題型錄：色盤 hex + 字型配對 + 適用場景）
- 以 `mermaid/claude-code-advanced-圖表合輯.pptx`（5 頁：標題頁 + 4 張 Mermaid 圖）為底，用 python-pptx 為 **10 個主題各生成一份套色 PPTX** 到新資料夾 `theme-showcase/`
- 套色策略：投影片背景色 + 第一文字框當標題（header 字型+粗體+標題色）+ 其餘文字框當副標（body 字型+accent 色），配色角色比照 showcase PDF 每頁呈現
- 自我驗證：抽驗深色（02 sunset-boulevard）與淺色（09 botanical-garden）各一份，背景/標題色/字型/粗體全 PASS
- 檔名二次加工：10 份全部加上中文風格描述（如 `圖表合輯-01-ocean-depths-海洋專業風.pptx`），三段式命名 = 編號（對照 PDF 頁序）+ 英文主題 ID + 中文風格

### 2. 實體列印（KONICA）

- 用 PowerPoint COM（`PrintOptions.ActivePrinter`）把 `04-modern-minimalist-極簡灰階` 送 KONICA MINOLTA 黑白列印成功，佇列清空確認送達
- 巧合最佳配對：黑白印表機 × 灰階主題（10 主題中唯一不損失彩色對比的）

### 3. addwii-yt-comment（互動模式）

- Shorts `lsBqwFdIa1U`（讓空氣，回歸藝術般的純淨！#加我科技智能空氣清淨機）
- 依 learnings 直接走 WebFetch fallback（不試 transcript），取得標題後生成 3 候選，使用者選 2 號
- ✅ 按讚（none → like）+ 留言「智能清淨守護全家呼吸」發布成功（comment_id `UgwG7r5zfihMpnPAky14AaABAg`）

### 4. bt-mic-switch 深度排查（if-K200P）

- 症狀：藍牙已連線但錄音清單無 Hands-Free 裝置（skill exit 1）
- 診斷：AudioEndpoint 全 Unknown、MMDevices Capture DeviceState=4/8（not present/unplugged，非停用）→ HFP 鏈路根本沒建立
- 程式面 4 招全數無效：pnputil 重啟 Hands-Free AG 裝置（3010）→ 重啟 Audiosrv+AudioEndpointBuilder → 重啟 Intel SST 藍牙音訊裝置（exit 0 仍無效）→ 重啟藍牙無線電卡（3010）
- **最終解：耳機關機再開**（skill 疑難排解的標準解），重跑腳本一次命中切換成功
- 結論已寫入 `~/.claude/context/learnings.md` 的 `## bt-mic-switch` section（症狀→捷徑 + 提權技術備忘）

### 5. 版控

- commit `8b03fe4`：theme-showcase 10 份 PPTX 進版控並 push

## 關鍵技術筆記

- **python-pptx 文字樣式雙層設定**：`paragraph.font` 與 `run.font` 都要設——只設 run 漏空 run 段落、只設段落蓋不過既有 run 直接格式
- **PPTX 指定印表機列印**：PowerPoint COM `PrintOptions.ActivePrinter` 只影響該簡報，不動系統預設印表機；中文檔名/印表機名在 Git Bash→PowerShell 會 cp950 亂碼 → 用萬用字元（`*04-modern*`、`KONICA*`）解析避開傳中文
- **HFP 排查決策樹**（新 learnings）：「已連線但無 Hands-Free 錄音裝置」→ 先看 MMDevices DeviceState（4/8=鏈路沒建、2=被停用）→ 4/8 就直接請使用者關開耳機，程式面重啟驅動/服務/無線電全是白工
- **pnputil 提權含 `&` 的 InstanceId**：寫 `C:\tmp\*.txt` + `Start-Process -Verb RunAs` + `iex (Get-Content -Raw)`，避開多層引號轉義
- **中文系統 Intel SST 裝置名**：「適用於 Bluetooth® 音訊的 Intel® 智慧型音效技術」，英文 `'*Smart Sound*'` 過濾不會命中
- **shell cwd 持久性陷阱**：Bash 工具的 `cd` 跨呼叫持續，後續相對路徑 git 操作會炸（`pathspec did not match`）→ 重要操作前 cd 回 repo 根

## 產出檔案

| 檔案 | 說明 |
| ------ | ------ |
| `theme-showcase/圖表合輯-01~10-*-*.pptx`（10 份） | 10 主題套色版圖表合輯，三段式檔名 |
| `~/.claude/context/learnings.md`（更新） | bt-mic-switch section 加 2 條（HFP 排查捷徑 + 提權備忘） |
| commit `8b03fe4` | theme-showcase 進版控 |

## HANDOFF（下次 session 優先處理）

### 立即行動

- [ ] **重跑 YouTube Comment OAuth**：session 中段 auth check 已報 EXPIRED（HTTP 400）→ `python ~/.claude/skills/addwii-yt-comment/scripts/auth_youtube.py`（瀏覽器互動，需使用者操作）
- [ ] **NotebookLM auth 續命**：已 122 小時即將過期 → `bash ~/.claude/scripts/nlm-login.sh`
- [ ] Google Docs auto-refresh 持續 HTTP 400，需排查 google-docs MCP 認證

### 進行中（需接續）

- 無未完成的主線任務；theme-showcase 與列印皆已收尾
- 系統有兩個 pnputil 3010（裝置重啟待重開機完成）：if-K200P Hands-Free AG 裝置 + Intel 藍牙無線電卡——不影響日常使用，下次重開機自然清掉

### 注意事項

- bt-mic-switch 遇「已連線但無 Hands-Free」症狀：**直接請使用者關開耳機（10 秒）**，不要再走驅動/服務重啟排查（本次實證 4 招全無效，詳 learnings）
- 切到 HFP 後播放音質變悶是藍牙先天限制；不需收音時重連耳機恢復 A2DP
- telegram 語音轉錄缺 faster-whisper（`python -m pip install faster-whisper`），有用到再裝
