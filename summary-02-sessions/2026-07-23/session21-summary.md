# Session 21 Summary — GSD Phase 1 規劃（demo-gsd-01-20260723）

**日期**：2026-07-23
**專案**：`demo-gsd-01-20260723`（待辦清單 CLI — 完成任務功能，GSD brownfield 練習第二輪）
**主題**：`/gsd-plan-phase 1` 完整跑通 — Pattern Mapping → Planning → Verification → 決策覆蓋閘門修訂 → commit

## 完成事項

### GSD plan-phase 工作流（Phase 1：資料結構遷移與測試安全網重建）

- 初始化查詢確認狀態：`01-CONTEXT.md` 已存在（上個 session 的 discuss-phase 產出）、無 RESEARCH/PLAN、MVP 模式由 ROADMAP `**Mode:** mvp` 生效、Walking Skeleton 閘門不觸發（brownfield，app.py 已可端到端運行）
- 研究決策：使用者選「跳過研究」（單檔 117 行純標準庫 dataclass 遷移，屬 well-understood refactor）
- **UI 閘門誤判排除**：workflow 的 grep 樣式命中 "ui" 其實是 "Req**ui**rements" 子字串——每個 phase section 都有該欄位，全部會誤觸發；依閘門本意（偵測前端工作）判定 HAS_UI=false 跳過
- 派 `gsd-pattern-mapper`（sonnet）→ 產出 `01-PATTERNS.md`，抓出最高風險點：`delete_task` 的 `name in tasks`/`tasks.remove(name)` 在元素變 `Task` 物件後**靜默失效**（不報錯但永遠 False）
- 派 `gsd-planner`（opus）→ 2 個計畫、2 個 wave（同檔改寫強制序列化）：
  - `01-01`：定義 `Task` dataclass + 遷移 add/list/_print + 元素級複製防線（TDD）
  - `01-02`：整段重寫 `delete_task` + 遷移 TestDeleteTask + 補刪除已完成任務測試 + CLI 端到端煙霧驗證
- 派 `gsd-plan-checker`（sonnet）→ **VERIFICATION PASSED**，12 維度一次過、0 修訂迭代
- **決策覆蓋閘門（#2492 translation gate）初判 FAIL（0/4）**：D-01～D-04 實質已實作但缺字面 `D-NN:` 引用 → 用 SendMessage 叫原 planner（context 還在）做針對性修訂只補引用 → 重跑閘門 4/4 PASS
- Post-planning gap 分析：7/9「未覆蓋」全是 Phase 2/3 的需求（COMP-01~04、COMPAT-03、DISP-01/02），Phase 1 的 COMPAT-01/02 均覆蓋，符合預期
- Commit `409be2a` `docs(01): create phase plan`（PLAN×2 + PATTERNS + STATE + ROADMAP）

### 關鍵設計決定（planner 產出、經 checker 確認）

- **垂直切分取代 ROADMAP 原水平切分**：原「app.py 一刀／測試一刀」會讓 01-01 收尾時測試全紅；改成「add/list 一刀、delete 一刀」後，利用 `TestDeleteTask` 四個測試「自建字串清單、不經過 add_task」的結構，讓每個 plan 收尾整個測試套件都是綠燈（MVP「每步可運作」）
- 純遷移 phase 不虛構 user story，以 CLI 端到端煙霧測試作為 MVP 可觀察行為證明
- Security 閘門（ASVS L1）：threat_model 精簡照實（本機 in-memory CLI 威脅面極小）

## 關鍵技術筆記

1. **GSD 決策覆蓋閘門是機械式比對**：`check.decision-coverage-plan` 要求計畫 `must_haves.truths`（或內文）出現字面 `D-NN:` ID，「實質覆蓋」不算數——這是可追溯性設計，讓 verify-phase 能逐項回查。planner 寫計畫時就該直接引用 ID。
2. **UI 閘門 grep 誤判**：`grep -iE "UI|…"` 會被每個 phase 的 `**Requirements**` 欄位誤觸發（"ui" 子字串）。orchestrator 要用 `grep -o` 看實際命中內容再判斷，Phase 2/3 規劃時同樣會誤中。
3. **Git Bash → node 絕對路徑地雷再現**：`node "$HOME/.claude/.../gsd-tools.cjs"` 被 MSYS 誤轉成 `C:\c\Users\...`（MODULE_NOT_FOUND），修法 `node "$(cygpath -w "$HOME/...")"`。與既有記憶「git worktree 絕對路徑地雷」同根因。
4. **SendMessage 針對性修訂省成本**：plan 修訂不必重派新 planner——用 agentId 續原 agent（context 完整），只描述 delta（補引用、不動實質），一次到位。
5. **背景等待模式**：Stop hook（quality-gate）擋收工時，用 `Bash run_in_background` + `until grep -q …; do sleep 2; done` 等背景 agent 寫檔完成，避免 foreground sleep。

## 產出檔案

| 檔案 | 說明 |
| ------ | ------ |
| `demo-gsd-01-20260723/.planning/phases/01-data-structure-migration/01-01-PLAN.md` | Wave 1：Task dataclass + add/list 遷移（TDD，含 D-01~D-04 引用） |
| `demo-gsd-01-20260723/.planning/phases/01-data-structure-migration/01-02-PLAN.md` | Wave 2：delete_task 重寫 + COMPAT-02 測試 + CLI 煙霧驗證 |
| `demo-gsd-01-20260723/.planning/phases/01-data-structure-migration/01-PATTERNS.md` | Pattern map：6 檔案分類、golden snippets、delete 靜默失效警示 |
| `demo-gsd-01-20260723/.planning/STATE.md` | 更新為 Ready to execute（2 plans） |
| `demo-gsd-01-20260723/.planning/ROADMAP.md` | Phase 1 加 wave 依賴標註 |

Commit：`409be2a` docs(01): create phase plan（本 session 收工另補 brownfield baseline commit）

## HANDOFF（下次 session 優先處理）

### 立即行動

- [ ] `/clear` 後執行 `/gsd-execute-phase 1`（2 plans：wave 1 → wave 2，皆 autonomous）
- [ ] 執行完確認 12+2 測試全綠（`PYTHONUTF8=1 pytest test_app.py -v`），走 verify/SUMMARY 流程
- [ ] Phase 2 規劃前先 `/gsd-discuss-phase 2`（complete_task 三態回傳設計有灰色地帶）

### 進行中（需接續）

- Phase 1 已規劃完成（Ready to execute），尚未執行；Phase 2/3 未規劃
- brownfield baseline（app.py + test_app.py + requirements.txt + GSD-PRACTICE.md）於本次收工 commit 入版控，執行 phase 後 diff 有對照基準

### 注意事項

- 決策覆蓋閘門要字面 `D-NN:` 引用——Phase 2/3 規劃時直接在 planner prompt 要求引用 ID，省一輪修訂
- UI 閘門 grep 對 "Requirements" 必誤判；Phase 3 有真 UI 工作（顯示層），到時是真觸發不是誤判，需 UI-SPEC 判斷
- Windows 跑 pytest/python 一律 `PYTHONUTF8=1`；node 吃 `$HOME` 路徑要 `cygpath -w`
- Phase 3 成功標準含「未設 PYTHONUTF8=1 的原生終端機印 ✓ 不炸」——執行時別忘了這條要真的在原生 cmd 驗
