# GSD 練習指南 — demo-gsd-01

## 練習情境

你接手一個「既有」的待辦清單 CLI（brownfield）。
現有 3 個函式：`add_task` / `list_tasks` / `delete_task`。
你要用 GSD 的完整流程，**新增第 4 個功能：`complete_task(name)`（標記任務為完成）**。

目標：學習 GSD 所有 phase 的指令與流程。App 本身不重要，流程才是重點。

---

## 前置準備（只需做一次）

```bash
# 1. 安裝 GSD
npx get-shit-done-cc --claude --global

# 2. 安裝 pytest
cd C:/Users/B00332/workspace/kindle-28-claude-code-advanced/demo-gsd-01
pip install pytest

# 3. 確認現有測試全綠（baseline）
PYTHONUTF8=1 pytest test_app.py -v
# 預期：12 passed
```

---

## GSD 練習流程（按順序執行）

### Phase 0：進入練習目錄，開 Claude Code

```bash
cd C:/Users/B00332/workspace/kindle-28-claude-code-advanced/demo-gsd-01
claude
```

---

### Phase 1：map-codebase（分析既有 codebase）

在 Claude Code session 內輸入：

```
/gsd:map-codebase
```

GSD 會派 Explorer Agents 並行分析 app.py 和 test_app.py。
完成後會在 `.planning/codebase/` 產出分析報告。

**學習重點**：

- 這是 brownfield 的第一步，讓 GSD 理解你的既有架構
- 不用自己解釋「我的 code 在幹嘛」，GSD 自己讀懂

---

### Phase 2：discuss-phase（釐清需求）

```
/gsd:discuss-phase
```

GSD 會問你問題，例如：

- "complete_task 要如何標記？（布林欄位 / 改資料結構 / ...）"
- "已完成的任務在 list_tasks 時要顯示嗎？"
- "重複完成同一任務要怎麼處理？"

**你的回答範例**（盡量簡單）：

- 在 task 前面加 `[x]` 標記
- list_tasks 仍顯示所有任務（包含已完成）
- 重複完成視為 no-op（不報錯）

**學習重點**：

- GSD 不讓你直接叫它「寫 complete_task」，它要先問清楚需求
- 這就是 Discuss 的精髓：逼出清楚的規格

---

### Phase 3：plan-phase（生成詳細計劃）

```
/gsd:plan-phase
```

GSD 查 codebase 地圖，產出 `.planning/PLAN.md`，內容類似：

```
要改的檔案：
  - app.py：新增 complete_task(tasks, name) 函式
  - test_app.py：新增 3 個 complete_task 測試

實作細節：
  - tasks list 從 str 改為 dict：{"name": "...", "done": False}
  - 或用 prefix 方式（[x] 前綴）
```

**你要做的事**：

- 讀 PLAN.md，確認計劃合理
- 可以用任何編輯器修改 PLAN.md（這是你的審查權）
- 確認後告訴 GSD「計劃 OK，繼續」

**學習重點**：

- 人在這裡是「審查者」，不是「打字機」
- 你有權修改計劃，再讓 Execute 執行

---

### Phase 4：execute-phase（全新 session 執行）

GSD 自動在背景開新 session，只帶 PLAN.md 去執行，不帶歷史對話。

**你要做的事**：等待完成（可能幾分鐘）

**學習重點**：

- 全新乾淨 session = 消滅 Context Rot
- Claude 不記得之前的討論，只看計劃

---

### Phase 5：verify-phase（驗收）

```
/gsd:verify-phase
```

GSD 引導跑測試、確認功能：

```bash
PYTHONUTF8=1 pytest test_app.py -v
# 預期：全綠（包含新加的 complete_task 測試）
```

**學習重點**：

- Verify 不是「信任 Claude 說做好了」
- 必須有客觀的測試結果當裁判

---

## 練習完成的驗收標準

- [ ] `.planning/codebase/` 資料夾存在（map-codebase 成功）
- [ ] `app.py` 多了 `complete_task()` 函式
- [ ] `test_app.py` 多了 `complete_task` 相關測試
- [ ] `PYTHONUTF8=1 pytest test_app.py -v` 全綠

---

## 現有 app.py 函式（你的 brownfield 起點）

```python
add_task(tasks, name)      # 新增任務，空 name 拋 ValueError
list_tasks(tasks)          # 列出所有任務（回傳 copy）
delete_task(tasks, name)   # 刪除任務，回傳 True/False
# complete_task ← 你要用 GSD 新增的！
```
