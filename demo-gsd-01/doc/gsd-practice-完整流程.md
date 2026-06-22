# GSD 完整流程實錄 — demo-gsd-01「為既有 todo CLI 新增 complete_task」

> 本文件鉅細靡遺記錄 2026-06-22 一次完整的 GSD（Get Shit Done）流程演練：
> 從分析既有 brownfield 程式碼，到用 GSD 六大階段新增 `complete_task` 功能並驗收通過。
> 目的是讓沒看過這次操作的人，也能完整理解 GSD 每個階段「做了什麼、為什麼、產出什麼」。

---

## 0. 背景與目標

- **專案**：`demo-gsd-01`，一個極簡的 in-memory 待辦清單 CLI（純 Python，無外部框架）。
- **既有程式碼（brownfield 起點）**：`app.py` 提供三個函式
  - `add_task(tasks, name)`：新增任務（空名稱拋 `ValueError`）
  - `list_tasks(tasks)`：回傳清單 copy
  - `delete_task(tasks, name)`：刪除，回 `True`/`False`
  - 另有 `_print_task_list` 顯示輔助函式、`main()` 互動 loop
  - `test_app.py`：12 個既有測試，baseline 全綠
- **目標**：用 GSD **完整流程**新增第 4 個函式 `complete_task(name)`（標記任務完成）。
- **重點**：App 本身不重要，**學 GSD 流程**才是重點。
- **協作模式**：互動教學 —— 每一步先貼指令/說明、等使用者確認再執行；每次回答用 `say_ui.exe` 語音播報。

---

## 1. GSD 是什麼（為什麼要這套流程）

GSD 是一套「規格驅動 + 多代理 + 乾淨 context」的開發工作流。它的核心信念：

- **LLM 的敵人是 context rot**：對話越長，模型越容易遺忘決策、產生幻覺。
- **解法 = 文件鏈**：把每個階段的決策固化成 `.planning/` 下的 markdown，下游階段只讀必要文件，並在**全新 context** 執行。
- **解法 = 多代理分工**：探索、規劃、執行、驗證各由獨立 context 的 subagent 負責，互不污染。

文件鏈層次（由抽象到具體）：

```
PROJECT.md      為什麼做、做什麼（專案脈絡）
REQUIREMENTS.md 要達成什麼（可測試的需求 + REQ-ID）
ROADMAP.md      切成哪些 phase（含成功標準）
CONTEXT.md      這個 phase 怎麼做（鎖定的實作決策）
PLAN.md         逐檔改動 + 逐測試（可執行的原子任務）
SUMMARY.md      執行後做了什麼
VERIFICATION.md 驗收：成功標準真的達成了嗎
```

---

## 2. 完整階段流程（本次實際走法）

> 正規 brownfield 順序：`map-codebase → new-project → discuss-phase → plan-phase → execute-phase → verify-phase`。
> 練習指南原本漏列 `new-project`，實作時補回。

### 階段 1：`/gsd:map-codebase` — 分析既有程式碼

- **做法**：平行派出 **4 個 `gsd-codebase-mapper` 子代理**（背景、各自獨立 context），分頭分析不同面向。
- **產出**：`.planning/codebase/` 下 7 份報告，共 958 行：
  - `STACK.md`（技術堆疊）、`INTEGRATIONS.md`（外部整合）
  - `ARCHITECTURE.md`（架構）、`STRUCTURE.md`（目錄結構）
  - `CONVENTIONS.md`（程式慣例）、`TESTING.md`（測試）
  - `CONCERNS.md`（技術債 / 隱憂）
- **設計亮點**：orchestrator 只收「檔案路徑 + 行數」，**不讀報告內文**，context 幾乎不被撐大。
- **收尾**：密鑰掃描（乾淨）→ commit `docs: map existing codebase`。

### 階段 2：`/gsd:new-project` — 建立專案骨架與路線圖

> **關鍵學習**：`discuss/plan/execute` 都需要 ROADMAP。沒有 `new-project` 先建 roadmap，
> `discuss-phase` 會回 `phase_found: false` 直接結束。這是練習指南漏列、實作時攔截補回的一步。

子流程：

1. **提問（QUESTIONING）**：確認需求 = 新增 `complete_task` 標記完成。
2. **寫 `PROJECT.md`**（brownfield）：
   - Validated（既有、已驗證）= add/list/delete
   - Active（待做）= complete_task
   - Out of Scope = 持久化 / 優先順序 / CLI 參數介面
3. **設定 `config.json`**：
   - Mode=Interactive、Granularity=Coarse、Execution=Parallel、Git=Yes
   - Research=No、Plan Check=Yes、Verifier=Yes、Models=Balanced
   - PR body sections=（全不選）
4. **研究決策**：跳過（todo CLI 是熟悉領域，無生態可研究）。
5. **定義 `REQUIREMENTS.md`**（v1，3 條，都 user-centric + 可測試）：
   - `COMP-01`：使用者可用名稱把既有任務標記為完成
   - `COMP-02`：標記不存在的任務 → 回清楚失敗訊號且不崩潰
   - `COMP-03`：列出任務時，已完成可與未完成區分
   - v2：`COMP-04` 取消完成 / 重開（延後）
6. **結構模式**：Vertical MVP（每 phase 端到端交付）。
7. **產 `ROADMAP.md`**：派 `gsd-roadmapper` 子代理。Coarse 顆粒度 + 3 條同類需求 → **切成 1 個 phase**（Task Completion），覆蓋率 3/3。
8. **收尾**：產生 `demo-gsd-01/CLAUDE.md`（GSD 指引）→ commit。

### 階段 3：`/gsd:discuss-phase 1` — 釐清實作決策（gray areas）

> discuss 只問「**怎麼做**」，不問「要不要做」（後者由 roadmap 鎖定）。

- **scout codebase**：發現 `tasks` 目前是 `list[str]`，add/list/delete 全依賴它、12 測試也餵字串 → 資料結構是最關鍵 gray area。
- **討論的 4 個 gray areas 與決策**：
  - **D-01/D-02 資料表示**：`list[str]` → `list[dict]` `{"name", "done"}`。最乾淨、最符合 `complete_task(tasks, name)` 簽名。**代價**：既有 4 函式 + 12 測試都要同步改（小型重構），最終仍須全綠。使用者在被明確告知代價後仍選 dict。
  - **D-03 找不到任務**：回 `False`（仿 `delete_task` 慣例，不拋錯）。
  - **D-04 重複完成**：no-op、回 `True`（冪等）。
  - **D-05/D-06 顯示**：`list_tasks` 回傳資料 copy；由顯示層 `_print_task_list` 加 `[x]`/`[ ]` 標記。
- **產出**：`01-CONTEXT.md`（決策合約）+ `01-DISCUSSION-LOG.md`（稽核軌跡）→ commit。
- **作用**：下游 planner/executor 讀 CONTEXT 即知決策，不會再亂猜資料結構。

### 階段 4：`/gsd:plan-phase 1` — 產出可執行計劃

依序派 3 個代理（有資料依賴，非平行）：

1. **`gsd-pattern-mapper`（sonnet）** → `01-PATTERNS.md`：
   把 `complete_task` 對應到既有 `delete_task`（同樣 find-by-name + bool 回傳 pattern），並標出 4 個重構點的 before/after。
2. **`gsd-planner`（opus）** → `01-task-completion-01-PLAN.md`：
   - **關鍵攔截**：ROADMAP 標了 `Mode: mvp`，GSD 的 **walking-skeleton gate** 因「MVP + phase01 + 零 summary」而**誤觸發**。但這是 brownfield（程式碼早就在），不需要搭骨架。orchestrator 在 planner prompt 明確指示「brownfield 函式擴充，不要產 SKELETON.md」→ planner 正確抑制。
   - 產出 1 plan / 2 tasks：Task1（改 app.py：dict 遷移 + complete_task + 顯示標記）、Task2（改 test_app.py：12 測試改 dict + 新增 TestCompleteTask）。含 `<threat_model>`（純記憶體 CLI、攻擊面極小）。
3. **`gsd-plan-checker`（sonnet）** → 驗證 PASS（0 blockers, 1 warning）：
   - **warning**：成功標準 #3（`[x]`/`[ ]` 顯示）只靠程式碼檢查、無 runnable test。
   - **修正**：orchestrator 直接編輯 PLAN，在 Task2 加入 `TestPrintTaskList`（capsys 測試），讓 4 條成功標準全部有自動化驗證 → warning 關閉。

- **收尾**：commit `docs(01): plan task completion phase`。

### 階段 5：`/gsd:execute-phase 1` — 實際寫程式

- **簡化決策**：execute-phase 預設用 git worktree 把每個 plan 平行隔離。但**只有 1 個 plan**，worktree 隔離是純 overhead（且 Windows 巢狀目錄下 merge 機制風險高）→ 改讓 executor 走 **sequential 主工作樹模式**。
- **鐵律相容性**：使用者有「程式碼檔案三 agent 鐵律」（code-writer→qa→reviewer），但該鐵律**明文豁免 subagent context 內寫檔**（避免遞迴）。GSD 的 `gsd-executor` 正是在 subagent context 寫檔 → 相容、不衝突。
- **`gsd-executor`（sonnet）** 實作：
  - 3 個原子化 commit：
    - `3261a00` app.py → dict 模型 + complete_task
    - `1a15df4` test_app.py dict 重構 + TestCompleteTask + TestPrintTaskList
    - `e0b304a` SUMMARY + STATE + ROADMAP + REQUIREMENTS
- **獨立驗證**：orchestrator **自己再跑一次** `PYTHONUTF8=1 pytest test_app.py -v` → **17 passed**（不只信代理自述）。

### 階段 6：`/gsd:verify-phase`（goal-backward 驗收）

- 派 **`gsd-verifier`（sonnet）**：不是只數測試，而是從 4 條成功標準**反推**，逐條在程式碼找對應實作 + 證據，再跑測試當裁判。
- **結果：PASSED 4/4**
  - SC-1 complete_task 標記完成：`app.py:73-77` + test PASS
  - SC-2 找不到 → False 不崩：`app.py:79-80` + test PASS
  - SC-3 `[x]`/`[ ]` 區分：`app.py:90-91` + capsys test PASS
  - SC-4 全套綠：`17 passed, exit 0`
  - 額外：dict 遷移完成、無殘留字串斷言、`main()` 無多餘指令、零技術債標記。
- **產出**：`01-VERIFICATION.md` → commit `docs(01): verify phase 1 (passed 4/4)`。

---

## 3. 最終成果

| 項目 | 結果 |
|---|---|
| `app.py` | dict 模型 + `complete_task`（found/idempotent→True、not-found→False 不崩）+ `[x]`/`[ ]` 顯示 |
| `test_app.py` | 12 既有改 dict + `TestCompleteTask`(4) + `TestPrintTaskList`(1) |
| 測試 | `PYTHONUTF8=1 pytest test_app.py -v` → **17 passed** |
| 文件鏈 | PROJECT / REQUIREMENTS / ROADMAP / CONTEXT / PLAN / SUMMARY / VERIFICATION + 7 份 codebase 地圖 |
| 驗收 | Phase 1 VERIFICATION **PASSED 4/4** |

### commit 軌跡（節錄）

```
6a05ade docs(01): verify phase 1 (passed 4/4)
e0b304a docs(01-task-completion-01): 完成 Phase 1 Plan 01 執行記錄
1a15df4 feat: 重構 test_app.py 為 dict 模型 + TestCompleteTask + TestPrintTaskList
3261a00 feat: app.py 遷移 dict 模型 + complete_task
347fc1e docs(01): plan task completion phase
480031e docs(01): capture phase context
345c3fa docs: create roadmap (1 phase)
bb09c81 docs: define v1 requirements
46d7178 chore: add project config
951a245 docs: initialize project
e035b64 docs: map existing codebase
```

---

## 4. 此次演練的關鍵學習（踩坑 / 攔截）

1. **`new-project` 不可略過**（brownfield 也要）：沒有 ROADMAP，所有 phase 指令 `phase_found: false`。
2. **walking-skeleton gate 在 brownfield 誤判**：只看 MVP+phase01+零summary，不看程式碼是否真 greenfield。orchestrator 須在 planner prompt 手動覆寫，否則會被叫去搭莫名的 scaffold。
3. **顆粒度真的影響 phase 切法**：Coarse + 同類需求 → roadmapper 自然切 1 phase，不會硬拆。
4. **資料結構決策的「隱藏範圍」**：選 `list[dict]` = 把「加函式」變「小重構」，連帶改既有 4 函式 + 12 測試。決策時要把代價講清楚。
5. **plan-checker 的價值在 goal-backward**：抓到「成功標準 #3 無 runnable test」這種缺口，事前補比事後便宜。
6. **單一 plan 不需要 worktree**：worktree 隔離是為了多 plan 平行；單 plan 用 sequential 主工作樹更穩。
7. **三 agent 寫碼鐵律與 GSD executor 相容**：鐵律豁免 subagent context 內寫檔，GSD executor 正落在豁免內。
8. **「先自己驗證再回報」**：executor 自稱全綠，orchestrator 仍獨立跑 pytest 確認，再交給 verifier goal-backward 複驗。

---

*文件產生日期：2026-06-22 ｜ 專案：demo-gsd-01 ｜ 流程：GSD 完整六階段*
