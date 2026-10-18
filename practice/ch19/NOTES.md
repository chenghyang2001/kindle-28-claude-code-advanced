# NOTES：K28 第 19 章演練紀錄（2026-10-18）

## 做了什麼

1. **ORCHESTRATION.md**：把「從副駕駛到指揮官」整理成決策表，4 種模式（單一 session／git worktree 平行／子代理／GSD・Ralph 自主迴圈），每列附判斷條件、典型例子、風險與降低風險的做法，另附快速判斷流程圖與「切、約、派、驗」四件事。
2. **基線**（主 session 自建，題目要求）：`csv_stats.py`（數值欄位 count/sum/mean/min/max）＋ `data/sales.csv`（10 列、含 1 個缺值）。
3. **合約**：主 session 寫 `SPEC.md`，定義新功能（中位數、`compute_grouped_stats` 分組統計、`columns` 欄位篩選、CLI `--group-by`/`--columns`）、錯誤行為、範例資料預期值，以及「誰只准改哪個檔」。
4. **指揮 2 個子代理（同時派出）**：
   - Agent A（實作者）：只改 `csv_stats.py`。
   - Agent B（測試者）：只建 `tests/test_csv_stats.py`、`tests/conftest.py`，依合約寫測試，不看實作。
   - 兩者檔案不重疊，所以用子代理而非 worktree（對照決策表）。
5. **整合驗收**（主 session）：自己跑 pytest 與 CLI，不採信子代理自述；檢查 `git status` 確認兩代理沒越界。

## 主 session 做了／沒做的事

| 主 session 有做 | 主 session 沒做 |
| --- | --- |
| 基線腳本＋範例 CSV（題目指定「自己先建」） | 新功能的業務碼（全由 Agent A 寫） |
| SPEC.md 合約、派工單 | 測試碼（全由 Agent B 寫） |
| 跑 pytest／CLI 驗收、`.gitignore`、文件、commit | 修改子代理產出 |

## 驗證結果

- `PYTHONUTF8=1 python -m pytest tests -q` → **27 passed in 0.07s**（主 session 親自執行）。
- 測試涵蓋：中位數 4、範例資料預期值 2、分組統計 6、欄位篩選 8、向下相容 1、CLI 6（含 3 參數化）。
- CLI 冒煙：`--group-by region --columns units` 輸出正確 JSON；檔案不存在 → `錯誤：找不到檔案：nope.csv`、回傳 1。
- 兩代理都只改了被分配的檔案（`git status` 確認）；一次整合就全綠，沒有退回重做。

## 兩個代理的解讀差異（合約沒寫清楚的地方）

- 群組值「只有空白」：A 也歸到 `"(空)"`；B 只測空字串，沒測全空白 → 合約缺口，下次應寫清楚。
- `columns` 中放 `group_by` 欄位：A 拋 `ValueError`；B 沒測。
- 數字一律輸出 float（`64.0`）：B 用 `pytest.approx` 比對，所以不受影響。

## 和題目要求的差異

- **沒有實際跑 git worktree 平行與 GSD／Ralph 迴圈**：題目只要求「主 session 指揮 2 個子代理」實作一次，另兩種模式僅寫在決策表中。
- **子代理在同一個工作目錄**（未用 worktree 隔離）：因兩者檔案不重疊，依決策表判斷不需要；這也是本次刻意示範的判斷。
- **兩代理同時跑**：B 跑測試時 A 已改完，所以 B 回報「27 passed」；理想的「先紅後綠」沒有被觀察到。
- **快速 demo 模式**：依專案 CLAUDE.md 豁免三 agent 鐵律，未經獨立 QA／code-reviewer 審查。
- 依限制：未建 GitHub repo、未 push、未部署，未修改全域 `~/.claude/`。
