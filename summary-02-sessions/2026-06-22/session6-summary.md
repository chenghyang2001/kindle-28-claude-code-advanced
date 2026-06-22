# Session 6 — GSD YOLO 模式完整實戰（demo-gsd-02-yolo）+ NotebookLM studio

**日期**：2026-06-22
**機器**：NB00547
**主題**：用 GSD autonomous（YOLO）模式在既有 brownfield Python todo CLI 上自動加功能；對照 demo-gsd-01 互動模式；產出心得文件 + NotebookLM studio。

---

## 完成事項

### GSD brownfield YOLO 全流程（demo-gsd-02-yolo）

- **`/gsd-map-codebase`**：完整版派 4 個平行 `gsd-codebase-mapper`，產出 7 份文件（STACK/INTEGRATIONS/ARCHITECTURE/STRUCTURE/CONVENTIONS/TESTING/CONCERNS，共 878 行）。對 2 檔小專案偏重，但完整體驗。
- **`/gsd-new-project`**：走完 init→brownfield 偵測→PROJECT.md→config(YOLO/coarse/parallel, research=No, plan-check+verifier=yes, balanced)→REQUIREMENTS.md(5 個 v1)→roadmap(1 phase)。roadmapper 正確只開 1 phase。
- **`/gsd-autonomous`**：對 Phase 1 自動跑 smart-discuss→plan→execute→review→fix→verify。
  - 灰色決策（3 次停下）：① 資料模型選 dict（`list[dict]` {"name","done"}）② 行為細節（complete idempotent 回 True、已完成可 delete、list_pending 回 name 字串）③ 修不修 MF-01。

### 關鍵踩坑與品質防線

- **walking-skeleton 誤觸發（已存 memory）**：Phase 1 是 `**Mode:** mvp` + phase 01 + 無前置 summary → `WALKING_SKELETON=true`，會叫 planner 從零搭專案/DB/UI 骨架。**手動覆寫**：直接派 `gsd-planner` 標 `WALKING_SKELETON=false` + brownfield no-scaffold。結果無 SKELETON.md。
- **code-review 抓到真 bug（MF-01）**：`list[str]`→`list[dict]` 後，`list_tasks` 的 `list(tasks)` 淺複本不再隔離（dict 是共享參照），呼叫端可偷改內部 `done`，但 docstring 仍保證隔離。既有測試只測 list 層 `.append` 沒抓到。修法：`copy.deepcopy` + 強化測試。

### 最終戰果（程式）

- `app.py`：dict 模型 + `complete_task` + `list_pending` + `list_tasks` 改 deepcopy
- `test_app.py`：6 測試更新 dict + `TestCompleteTask`(3) + `TestListPending`(3 含空清單) = **12 passed**

### 文件 + NotebookLM

- `YOLO-PRACTICE.md` §七 填入互動 vs YOLO 親身對照表 + §八 驗收勾選
- `doc/demo-gsd-02-yolo-完整心得.md`：完整實戰心得（NLM 來源）
- NotebookLM notebook `eb5759cf-…` + source `562a8f22-…`，觸發 audio/video/slide-deck 三 studio（pending，**不 polling**）

### 規則沉澱

- 新 memory：**NLM studio 不 polling**（trigger 完即繼續）

---

## 關鍵技術筆記

- GSD 本機是 **flat-skills 安裝 → 指令用連字號** `/gsd-xxx`（非冒號 `/gsd:xxx`，那是 plugin 命名空間）
- planner/executor/verifier/code-fixer/code-reviewer 皆 GSD 專用 subagent；本次刻意用 sonnet 取代 init 給的 opus planner（trivial 任務省成本）
- NotebookLM CLI verbs：`notebooklm create` / `source add` / `generate audio|video|slide-deck`；語言 `zh_Hant`；--json 取 task_id
- NLM 雙層 auth（MCP+CLI）同時過期 → `! notebooklm login` 互動重登（順帶同步 VPS）

---

## 產出檔案

| 檔案 | 動作 |
|---|---|
| `demo-gsd-02-yolo/.planning/codebase/*.md`（7 份）| 新增（map-codebase）|
| `demo-gsd-02-yolo/.planning/PROJECT.md / config.json / REQUIREMENTS.md / ROADMAP.md / STATE.md` | 新增（new-project）|
| `demo-gsd-02-yolo/.planning/phases/01-…/01-CONTEXT/PLAN/SUMMARY/VERIFICATION/REVIEW.md` | 新增（autonomous）|
| `demo-gsd-02-yolo/app.py`、`test_app.py` | 修改（dict 模型 + 2 新函式 + deepcopy fix，12 tests）|
| `demo-gsd-02-yolo/CLAUDE.md` | 新增（GSD 疊加層）|
| `demo-gsd-02-yolo/YOLO-PRACTICE.md` | 修改（§七心得 + §八驗收）|
| `demo-gsd-02-yolo/doc/demo-gsd-02-yolo-完整心得.md` | 新增（NLM 來源）|
| `~/.claude/projects/…/memory/nlm-studio-no-polling.md` + MEMORY.md | 新增記憶 |

**Commits（本 session）**：`7f84611`→`7acfcef`（map→roadmap→context→plan→exec→fix→收尾→docs），約 11 個 atomic commit。

---

## HANDOFF（下次 session 優先處理）

### 立即行動

- [ ] 進 NotebookLM 確認 3 個 studio（audio `370e10df…` / video `bac3b8ed…` / slide `f9d43daa…`）是否生成完成；失敗則重 trigger
- [ ] 若要看 GSD 里程碑收尾完整流程：再下 `/gsd-autonomous`（會偵測 phase 全完成 → 直接進 audit→complete→cleanup）

### 進行中（需接續）

- demo-gsd-02-yolo 的 GSD milestone v1.0 **刻意未收尾**（保留 planning artifact 供回看）。Phase 1 已 complete + verified；v2 deferred 項：REPL-01（`complete`/`pending` 指令接進 `main()`）。

### 注意事項

- brownfield + mvp + phase 01 = walking-skeleton 地雷，plan 階段務必手動覆寫 `WALKING_SKELETON=false`（見 memory [[gsd-walking-skeleton-brownfield-gotcha]]）
- 本專案 CLAUDE.md 有「每回合語音播報 + 互動教學一次一問 + 未經同意不執行指令」鐵律，下次續做仍適用
- NLM studio 生成**不要 polling**（見 memory nlm-studio-no-polling）
