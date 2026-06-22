# Lesson 6：Ralph 獨立版（frankbria/ralph-claude-code）深度解析

> 建立日期：2026-06-22
> 對應 demo：`demo-ralph-02/`（VPS 實跑，9/9 全綠）
> 對應書章：第六章「用 Ralph 框架打造全自動開發代理人」

---

## 一、外掛版 vs 獨立版（先搞清楚這件事）

Ralph 有兩個版本，概念相同但技術架構完全不同：

| | 外掛版（ralph-wiggum） | 獨立版（frankbria/ralph-claude-code） |
|---|---|---|
| 安裝方式 | `/plugin install ralph-wiggum`（Claude Code 外掛） | `git clone` + `./install.sh`（全域 bash 指令） |
| 觸發方式 | `/ralph-loop "..."` 在 Claude Code session 內 | `ralph --monitor ...` 從終端機啟動 |
| 運作機制 | 寄生 Claude Code session，用 Stop hook 觸發下一輪 | 外部 bash 迴圈，`claude -p` headless 呼叫 |
| 背景執行 | ❌ 不行（寄生於對話視窗） | ✅ tmux detach 可離開終端 |
| 速率限制 | ❌ 無（燒多少算多少） | ✅ `--calls N`（每小時上限） |
| 斷路器 | ❌ 無（靠 `--max-iterations` backstop） | ✅ `--timeout N`（分鐘逾時） |
| 適合任務 | 短任務（< 30 分鐘） | 長任務（可過夜跑） |
| 執行環境 | Windows / Mac / Linux 都行 | Linux / WSL2 / VPS（bash + tmux 原生） |
| Scope creep 風險 | 低（短任務，方向跑不遠） | ⚠️ 高（長時間自主，規格不夠死就亂長） |

---

## 二、獨立版核心架構：外部控制迴圈

```
你的終端機（ralph 主程序）
    │
    ▼
ralph 讀取 TASKS.md（任務節點清單）
    │
    ├─► 選一個未完成節點
    │
    ▼
claude -p "讀 TASKS.md，實作 [節點]，跑測試，通過後打勾" ──► 子程序
    │                                                          │
    │                                         Claude 寫 code → npm test
    │                                         測試通過 → 修改 TASKS.md 打勾
    │                                                          │
    ◄──────────────── 子程序結束，ralph 主程序收回控制 ◄────────┘
    │
    ├─ 所有節點打勾？→ 結束（完成）
    ├─ 撞 --calls 上限？→ 下一小時繼續
    ├─ 撞 --timeout？→ 停止
    └─ 未完成 → 繼續下一輪
```

**關鍵設計**：ralph 是「外部程序」，不是 Claude 的一部分。Claude 每輪是全新的 `claude -p` 子程序，ralph 是不間斷跑在外面的指揮者。

---

## 三、三大安全護欄（防止無人值守時失控）

### 護欄 1：速率限制（Rate Limiter）—— `--calls N`

- **作用**：每小時最多允許 N 次 API 呼叫
- **防的是**：Claude 無限快速重試、一晚燒光額度
- **範例**：`ralph --calls 50` = 每小時上限 50 次，超過就休眠到下一小時

### 護欄 2：會話過期（Session Timeout）—— `--timeout N`

- **作用**：單次任務執行超過 N 分鐘就強制停止
- **防的是**：Claude 在某個子任務卡死、無限轉圈
- **範例**：`ralph --timeout 30` = 單次超過 30 分鐘就殺掉，視為失敗

### 護欄 3：斷路器（Circuit Breaker）—— 解析 stack trace

- **作用**：偵測 Claude 拋出的錯誤訊息，重複失敗超過閾值就停止整個迴圈
- **防的是**：環境壞掉（npm 裝不了、測試 framework 掛掉）但 Claude 一直重試
- **設計原則**：停下來讓人類看，比白白燒錢繼續跑更好

---

## 四、標準執行流程（SOP）

```bash
# Step 1：匯入規格（把 spec 拆成任務節點）
ralph-import api-spec.md
# → 產出 TASKS.md，每個端點 / 功能一個 [ ] 任務節點

# Step 2：初始化專案
ralph-enable
# → 寫入 .ralph-config，設好 claude -p 的工作目錄、模型等

# Step 3：乾跑（重要！0 API 呼叫）
ralph --monitor --dry-run
# → 確認流程設定正確、護欄參數合理，不花任何錢

# Step 4：真實執行（帶護欄）
ralph --monitor --calls 50 --timeout 30
# → 在 tmux 監控視窗看即時 log；可 Ctrl+B D detach 出去做別的事

# Step 5：驗收
npm test
# → 全綠 = 任務完成
```

---

## 五、tmux 監控視窗

Ralph 的 `--monitor` 模式會開一個分割 tmux 視窗，顯示：

```
┌─────────────────────────────────────────────────────────────┐
│  Ralph Monitor                                              │
│  Calls this hour: 12/50    Timeout: 18/30 min              │
│  Tasks: ████████░░  8/10 done                              │
├─────────────────────────────────────────────────────────────┤
│  [14:32:01] Starting task: getTodo                         │
│  [14:32:45] npm test: PASS (9/9)                           │
│  [14:32:45] ✅ getTodo marked complete                      │
│  [14:32:46] Starting task: updateTodo                      │
└─────────────────────────────────────────────────────────────┘
```

- **Detach（離開監控不中斷）**：`Ctrl+B D`
- **重新 attach 回來看**：`tmux attach -t ralph`

---

## 六、demo-ralph-02 實跑觀察（2026-06-22）

**任務**：在 VPS 上實作 Todo API 5 個端點（api.js），讓 api.test.js 全綠

**結果**：

- Ralph 第 1 圈即完成 5 端點實作，9/9 全綠
- 僅消耗 1 次 API 呼叫、2,379 tokens
- 但出現 **scope creep**：Ralph 自作主張多建了：
  - `server.js`（真的 Express HTTP server，規格沒要求）
  - `api.validation.test.js`（額外驗證測試）
  - `server.test.js`（HTTP 整合測試）
  - 合計 17 個測試（原規格只有 9 個）

**教訓**：規格只說「實作函式 + 測試」，但沒明確說「不要建 HTTP server」→ Ralph 自由發揮。**規格要說清楚不做什麼，不只是要做什麼。**

---

## 七、Ralph 獨立版 vs 外掛版選擇口訣

**選外掛版（ralph-wiggum），如果：**

- 任務 < 30 分鐘
- 想在 Claude Code session 內互動監督
- Windows 環境（不想裝 WSL）
- 任務夠短不需要速率限制

**選獨立版（frankbria），如果：**

- 任務可能要幾小時或過夜
- 需要在 VPS / CI / Linux 伺服器上跑
- 需要三大護欄防失控
- 想完全脫離終端（tmux detach）

---

## 八、Windows 10 的限制（踩坑紀錄）

獨立版需要 bash + tmux，Windows 原生不支援：

```
Windows 原生 → ❌ 不行
WSL2（Virtual Machine Platform）→ 需要 BIOS 開 Intel VT-x
本機卡關根因：VirtualizationFirmwareEnabled = False（BIOS VT-x 未開）
解法：進 BIOS 開 Intel Virtualization Technology
備援：走 VPS（Hostinger / 任何 Linux VPS）
```

**排查順序**：

```powershell
# 1. 確認 BIOS VT 狀態
Get-ComputerInfo | Select-Object -Property HyperV*

# 2. 確認 WSL feature 狀態
Get-WindowsOptionalFeature -Online -FeatureName VirtualMachinePlatform

# VirtualizationFirmwareEnabled = True + WSL InstallState = 1 → 能跑
# VirtualizationFirmwareEnabled = False → 進 BIOS 才能解
```

---

## 九、關鍵收穫（3 句）

1. **外部控制 = 完整自主**：ralph 是外面的指揮者，claude 是可拋棄的執行子程序，這個架構讓護欄、監控、重試完全在你的控制之下。
2. **測試是客觀裁判**：ralph 的自我評估靠 `npm test` exit code，不靠 Claude 自報「我做完了」——這是防止 Claude 騙自己的關鍵設計。
3. **規格要寫「不做什麼」**：本次 scope creep 的根因，規格的負向邊界（禁止自行擴充）和正向邊界（要做的功能）一樣重要。
