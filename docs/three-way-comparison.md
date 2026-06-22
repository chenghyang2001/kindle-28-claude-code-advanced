# 三方比較：GSD vs Ralph 獨立版 vs Anthropic autonomous-coding

> 建立日期：2026-06-22
> 對應課程：第五課（GSD）、第六課（Ralph 獨立版）、Anthropic 官方 quickstart 演練
> 核心問題：都能「給規格 → 自動完成任務」，差在哪？

---

## 一、一句話定位

| 框架 | 一句話定位 |
|---|---|
| **GSD** | 結構化「**專案方法論**」：從模糊想法到交付，全程有多階段品質關卡，**人在每個關卡把關** |
| **Ralph 獨立版** | 輕量「**自主執行引擎**」：給清楚規格 + 測試，無人值守跑到全綠，**人只設邊界不介入** |
| **Anthropic autonomous-coding** | 最小「**AI 工廠示範**」：Python SDK 程式化驅動 Claude，Initializer 建測試清單，Coding Agent 逐一完成，**全自動直到全綠** |

核心差異一句話：**GSD = 大腦（想清楚再做）；Ralph = 引擎（埋頭把苦工做完）；Anthropic = 工廠流水線（有套 Python harness 撐著自動跑）**

---

## 二、完整逐維度比較表

| 維度 | GSD | Ralph 獨立版 | Anthropic autonomous-coding |
|---|---|---|---|
| **核心理念** | 慢即是快：先討論再計劃再執行 | 放手跑：目標清楚就全權交出去 | 自動工廠：Python 腳本不間斷驅動 Claude |
| **驅動機制** | Claude Code Skills（`/gsd:xxx` 互動指令） | 外部 bash 迴圈（`claude -p` headless 子程序） | Python 腳本呼叫 Claude Agent SDK（程式化迴圈） |
| **進入方式** | Claude Code session 內打 `/gsd:new-project` | 終端機 `ralph --monitor --calls 50 --timeout 30` | 終端機 `python autonomous_agent_demo.py` |
| **人類角色** | 決策者 / 審查者（逐階段 gate） | 邊界守門員（設好護欄就離開，事後驗收） | 觀察者（看 log，必要時 Ctrl+C） |
| **自動化程度** | 半自動（多階段，每段要你確認） | 全自動（fire-and-forget，可過夜） | 全自動（Python 腳本自動接續 session） |
| **Phase 結構** | 4 個明確 phase：Discuss → Plan → Execute → Verify | 單一迴圈：read → execute → test → repeat | 2 種 agent：Initializer (S1) + Coding Agent (S2+) |
| **Discuss 階段** | ✅ AI 反問你問題，逼出清楚需求 | ❌ 無（你自己先寫好規格） | ❌ 無（直接讀 app_spec.txt） |
| **起點需要什麼** | 模糊想法也行（Discuss 幫你問清楚） | 清楚規格 + 可自動驗證的測試 | 清楚的 app_spec.txt + 可驗證的功能行為 |
| **規格格式** | 由 Discuss 問答動態產生 PLAN.md | `ralph-import spec.md` → TASKS.md 任務節點 | 靜態 app_spec.txt → Initializer 生成 feature_list.json |
| **計劃細緻度** | 極細：改哪些檔、順序、補哪些測試、行數 | 中：任務節點清單（功能描述層級） | 粗：feature 行為描述 + 驗證步驟（不指定實作） |
| **狀態容器** | `.planning/` 資料夾（PROJECT / REQUIREMENTS / ROADMAP / STATE / PLAN） | TASKS.md（任務節點 + 打勾進度） | feature_list.json + claude-progress.txt + git |
| **狀態注入方式** | `.planning/` 被自動讀入新 session system prompt | Claude 每輪讀 TASKS.md + 上輪打勾狀態 | coding_prompt.md 指示 agent 自己 `cat` 各狀態檔 |
| **完成信號** | 測試全綠 + 人審查通過 Verify | `npm test` exit 0 / 所有 [ ] 變 [x] | feature_list.json 所有 `passes: true` |
| **失敗處理** | Verify 失敗 → 回 Plan 重寫修復計劃 → 新 Execute | 本輪失敗 → 下一輪繼續（斷路器計次，超閾值停） | 發現 bug → 標 `passes: false` → 同 session 修 |
| **Verify 機制** | 獨立 phase：引導手動驗證 + 自動診斷 | `npm test` exit code（客觀裁判） | 每 session 開頭跑舊功能 + Puppeteer UI 截圖 |
| **並行執行** | ✅ 多個 sub-agent 並行跑獨立任務 | ❌ 串行（單一迴圈） | ❌ 串行（session 間順序執行） |
| **既有專案分析** | ✅ `map-codebase`：並行 Explorer Agents 各查一面向 | ❌ 從規格出發，不分析既有 codebase | ❌ greenfield only |
| **背景執行** | ❌ 需在 Claude Code session 內 | ✅ tmux detach 可完全離開終端 | ✅ Python 腳本可背景跑（nohup / screen） |
| **速率限制護欄** | ❌ 依賴 Max 訂閱限制 | ✅ `--calls N`（每小時上限） | ❌ 無（依賴 API key 層級限制） |
| **逾時護欄** | ❌ 無明確逾時 | ✅ `--timeout N`（分鐘） | ❌ 無（靠 `--max-iterations`） |
| **Scope creep 風險** | 低（人審 PLAN.md 把關） | ⚠️ 高（長時間自主，規格不夠死就亂長） | ⚠️ 中（Initializer 生清單後不能改，但 impl 可能過度） |
| **安全模型** | 繼承 Claude Code permission（互動確認） | 靠護欄（rate / timeout / 斷路器） | `security.py` bash 白名單（OS 層硬封鎖） |
| **執行環境** | Windows / Mac / Linux（Claude Code） | Linux / WSL2 / VPS（bash + tmux） | 任何有 Python 的環境（但 Puppeteer 驗證需要 headless 瀏覽器） |
| **成本特性** | 人控節奏，按階段花 | 可能長時間連續燒，護欄是唯一煞車 | Python 腳本持續呼叫 SDK，需設 max-iterations |
| **PR / branch 機制** | ✅ `/gsd:pr-branch` 建 PR | ❌ 無（靠 git commit） | ❌ 無（自動 git commit 但無 PR 機制） |
| **典型輸出** | 有設計、有驗證紀錄的完整專案 | 「測試全綠」的一批程式碼 | 「feature_list 全 pass」的完整 web app |

---

## 三、任務路由表（我有這種任務 → 用哪個）

| # | 任務類型 | 推薦 | 理由 |
|---|---|---|---|
| 1 | 需求模糊，想先釐清再開發 | **GSD** | Discuss 階段能逼出清楚需求 |
| 2 | 規格清楚，想全自動過夜跑完 | **Ralph** | fire-and-forget，有護欄 |
| 3 | 從零建新 web app，功能多且複雜 | **Anthropic** | Initializer 自動拆 200 功能，Coding Agent 逐一做 |
| 4 | 改既有大型 codebase，需分析舊架構 | **GSD** | `map-codebase` 並行探索，再 Plan |
| 5 | 照 api-spec 實作 N 個端點，今晚跑完 | **Ralph** | 規格明確可測試，適合無人值守 |
| 6 | 修 CI 裡一批紅燈測試 | **Ralph** | 目標明確，exit code 是客觀裁判 |
| 7 | 需要架構設計決策，多方案權衡 | **GSD** | Discuss + Plan gate，人參與決策 |
| 8 | 全自動、最小人工介入的 MVP 原型 | **Anthropic** | Python 腳本跑完就有可執行 app |
| 9 | 需要 code review / security audit | **GSD** | 內建多個 reviewer agent |
| 10 | 清 100 個 lint error 或技術債 | **Ralph** | 重複、可驗證的機械任務 |
| 11 | 想用 Puppeteer 驗 UI 行為 | **Anthropic** | coding_prompt.md 內建 Puppeteer 流程 |
| 12 | Windows 環境（不想裝 WSL） | **GSD** 或 **Anthropic** | Ralph 獨立版需要 bash + tmux |

---

## 四、三角定位圖（文字版）

```
              人類主導程度
              ↑
              │
              │  GSD ●
              │   （人審查每個計劃）
              │
              │
              │         Anthropic ●
              │         （人只看 log）
              │
              │  Ralph ●
              │  （人設邊界後離開）
              └────────────────────────→
              規格需要清晰度
              低←────────────────→高

換個維度：

            無人值守能力
            ↑
  Ralph ●   │         Anthropic ●
  （可過夜）│         （Python 腳本跑）
            │
            │    GSD ●
            │    （需互動）
            └────────────────────────→
            任務結構複雜度
            單純←──────────────→複雜
```

---

## 五、最佳組合策略

三個工具**不是競爭關係**，而是可以串接的工具鏈：

```
模糊需求
    │
    ▼
【GSD Discuss + Plan】
  → 把需求問清楚
  → 產出清晰的 spec / PLAN.md
    │
    ├─► 執行段機械、重複、可測試 → 【Ralph 獨立版】無人值守跑完
    │
    ├─► 要建完整 web app greenfield → 【Anthropic autonomous-coding】factory 模式
    │
    └─► 需要架構決策 / 品質 gate → 【GSD Execute + Verify】繼續走 GSD
```

**GSD 負責「想清楚」，Ralph / Anthropic 負責「做完」。**

---

## 六、選擇口訣（30 秒決策）

**選 GSD，如果：**

- 需求模糊，需要先問清楚
- 任務跨多階段、有架構決策
- 需要人逐階段把關品質
- 有既有 codebase 需要先分析

**選 Ralph 獨立版，如果：**

- 規格清楚，測試已寫好
- 任務機械、重複、可自動驗證
- 想無人值守（過夜 / CI / VPS）
- 有 Linux 環境或願意用 VPS

**選 Anthropic autonomous-coding，如果：**

- Greenfield 新 app，功能清單已知
- 想要 Puppeteer UI 驗證內建
- 想用 Python 程式化控制 Claude Agent SDK
- 追求最小 harness、了解底層機制

---

## 七、各自最大弱點

| 框架 | 最大弱點 |
|---|---|
| **GSD** | 對小任務殺雞用牛刀；流程步驟多，不熟練前上手成本高 |
| **Ralph 獨立版** | Scope creep 風險高（規格不夠死就亂長）；Windows 原生不能跑 |
| **Anthropic autonomous-coding** | 無 Discuss 階段（需求模糊就直接跑會跑偏）；Initializer 第一輪要 10-20 分鐘 |
