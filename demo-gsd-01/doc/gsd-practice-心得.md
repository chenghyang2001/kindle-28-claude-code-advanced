# GSD 練習心得（demo-gsd-01）

> 一次走完 GSD 完整流程，為既有 todo CLI 新增 `complete_task` 的學習重點。
> 日期：2026-06-22

## 一句話總結

GSD 的價值不是「幫你寫程式」，而是用**文件鏈 + 乾淨 context**逼出清楚規格、固化決策、抗 context rot。

## 5 個關鍵收穫

1. **流程順序不能跳**：`map-codebase → new-project → discuss → plan → execute → verify`。
   `discuss/plan/execute` 都掛在 ROADMAP 上，沒有 `new-project` 先建 roadmap，後面全部卡住（`phase_found: false`）。

2. **每階段產出一層決策、下游只讀必要文件**：
   PROJECT（為什麼）→ REQUIREMENTS（要什麼，可測）→ ROADMAP（切哪些 phase）→ CONTEXT（這 phase 怎麼做）→ PLAN（逐檔逐測試）。
   execute 只吃 PLAN，不必重讀討論——這就是抗 context rot 的核心。

3. **discuss 只問「怎麼做」，不問「要不要做」**：
   `complete_task` 的資料結構（`list[str]` → `list[dict]`）這種 gray area 在 discuss 鎖定，planner 不會再亂猜。
   選 dict 模型 = 把「加一個函式」變成「小型重構」（既有 4 函式 + 12 測試都要改）——決策的代價要講清楚。

4. **工具有 heuristic，人要攔截**：
   GSD 的 walking-skeleton gate 在 brownfield 會誤判（只看 MVP+phase01+零summary，不看程式碼是否真 greenfield）。
   orchestrator 的價值就在這種地方手動覆寫。

5. **verify 不信「我做完了」**：
   plan-checker 事前驗（發現成功標準 #3 無 runnable test → 補 capsys 測試）、verifier 事後 goal-backward 驗（逐條對照程式碼 + 跑測試當裁判）。
   客觀測試（17 passed）才是裁判，不是代理的口頭宣稱。

## 成果

- `app.py`：dict 模型 + `complete_task`（found/idempotent→True, not-found→False 不崩）+ `[x]`/`[ ]` 顯示
- `test_app.py`：12 既有改 dict + `TestCompleteTask` + `TestPrintTaskList`
- `PYTHONUTF8=1 pytest test_app.py -v` → **17 passed**
- 6 個 `.planning/` 文件鏈 + Phase 1 VERIFICATION：PASSED 4/4
