# GSD YOLO 模式練習 — demo-gsd-02-yolo

> 對照組：`demo-gsd-01`（你已做過的「互動逐步」模式）
> 本練習：同一個 todo app，改用 **YOLO（自動）模式**，體會「設好就走、喝咖啡等它跑完」。

---

## 一、先搞懂：GSD 的「速度光譜」

YOLO 不是單一指令，是把「人類 gate」一層層拿掉。由慢到快：

| 模式 | 指令 | 會為你停下嗎 | 何時用 |
|---|---|---|---|
| 互動（demo-gsd-01 做過） | `/gsd-discuss-phase` → `/gsd-plan-phase` → execute → `/gsd-verify-work`（逐個下） | ✅ 每個 phase 都停 | 需求模糊、要逐步把關 |
| **自動 / YOLO（本練習主角）** | `/gsd-autonomous` | ❌ 只在灰色決策 / 卡關才停 | 需求清楚、想一路跑完整個 milestone |
| 快速（輕量 YOLO） | `/gsd-quick "任務"` | ❌ 略過 discuss / research / verify | 單一明確小任務 |
| 極速（瑣碎） | `/gsd-fast "任務"` | ❌ 連 PLAN.md 都不寫 | 改 typo、一句話能講完的事 |
| 權限 YOLO（疊加層） | 啟動時 `claude --dangerously-skip-permissions` | ❌ 連工具授權 y/n 都不問 | 安全的本地練習環境（**嚴禁正式環境**） |

> 🔑 **真正的「喝咖啡 YOLO」= `/gsd-autonomous` + `--dangerously-skip-permissions`**
> 前者拿掉「phase gate」，後者拿掉「工具授權 gate」，兩個一起才是完全不停。

---

## 二、本練習要做什麼

你的 brownfield 起點（app.py）只有 3 個函式：`add_task` / `list_tasks` / `delete_task`。

YOLO 模式要它**自動連續加 2 個功能**（這樣才看得出 autonomous 連跑多 phase 的威力）：

1. `complete_task(tasks, name)` — 標記任務完成
2. `list_pending(tasks)` — 只列出未完成的任務

---

## 三、前置準備（一次性）

```bash
# 1. 確認 GSD 已裝（demo-gsd-01 裝過就跳過）
npx get-shit-done-cc --claude --global

# 2. 裝 pytest
cd C:/Users/B00332/workspace/kindle-28-claude-code-advanced/demo-gsd-02-yolo
pip install pytest

# 3. 跑 baseline，確認起點 6 個測試全綠
PYTHONUTF8=1 pytest test_app.py -v
# 預期：6 passed
```

---

## 四、YOLO 練習：路線 A（完整 autonomous，推薦）

這條路線最能對照你 demo-gsd-01 的逐步體驗。

### Step 1：用「YOLO 啟動法」開 Claude Code

```bash
cd C:/Users/B00332/workspace/kindle-28-claude-code-advanced/demo-gsd-02-yolo
claude --dangerously-skip-permissions
```

> `--dangerously-skip-permissions` = 之後 GSD 寫檔 / 跑測試 / commit 都不會再問你 y/n。
> ⚠️ 只在這種本地練習資料夾用。正式專案絕不要。

### Step 2：建地圖（brownfield 第一步，跟 demo-gsd-01 一樣）

```
/gsd-map-codebase
```

### Step 3：建立專案 roadmap（這步會問你幾個 setup 問題 — 正常）

```
/gsd-new-project
```

當它問你要做什麼，直接貼：

```
這是一個既有的待辦清單 CLI。請新增兩個功能：
1) complete_task(tasks, name)：標記任務為完成
2) list_pending(tasks)：只列出未完成的任務
每個功能都要有對應 pytest 測試，現有 6 個測試不可弄壞。
```

> 它會自動產出 ROADMAP.md，把上面拆成 1～2 個 phase。

### Step 4：一鍵 YOLO，跑完所有 phase

```
/gsd-autonomous
```

接著**雙手離開鍵盤**。它會自己對每個 phase 跑：discuss → plan → execute，
中間不問你（除非遇到真正的灰色決策）。這就是 YOLO。

### Step 5：驗收

```bash
PYTHONUTF8=1 pytest test_app.py -v
# 預期：原 6 個 + 新增的 complete_task / list_pending 測試，全綠
grep -nE "def (complete_task|list_pending)" app.py
# 預期：兩個函式都出現
```

---

## 五、YOLO 練習：路線 B（單任務速跑，最短路徑）

如果你只想體驗「一句話 → 它自己 plan+寫+測+commit」，用 `/gsd-quick`：

```bash
cd C:/Users/B00332/workspace/kindle-28-claude-code-advanced/demo-gsd-02-yolo
claude --dangerously-skip-permissions
```

在 session 內：

```
/gsd-map-codebase
/gsd-quick "在 app.py 新增 complete_task(tasks,name) 標記完成、list_pending(tasks) 列出未完成，各補 pytest 測試，不可弄壞現有 6 個測試"
```

`/gsd-quick` 預設略過 discuss / research / verifier，直接 plan → execute → atomic commit。
任務存在 `.planning/quick/`（不進 ROADMAP）。

---

## 六、進階：把 YOLO 設成「預設」

不想每次手動，可以改 GSD 設定讓它預設就 YOLO：

```
/gsd-config
```

對照 `.planning/config.json` 三個關鍵開關（demo-gsd-01 目前是互動值）：

| 開關 | 互動模式（demo-gsd-01） | YOLO 模式 | 意思 |
|---|---|---|---|
| `mode` | `interactive` | `autonomous` | 整體預設模式 |
| `skip_discuss` | `false` | `true` | 跳過 discuss 問答 |
| `workflow.auto_advance` | `false` | `true` | 一個 phase 完成自動接下一個 |

---

## 七、互動 vs YOLO 對照（練完心得 — 2026-06-22 實測）

> 本表是 demo-gsd-02-yolo 走完 `map-codebase → new-project → autonomous` 後的**親身數據**，不是估計值。

| 面向 | 互動（demo-gsd-01） | YOLO（demo-gsd-02-yolo 實測） |
|---|---|---|
| 我下了幾次指令 | 5+（每 phase 一次） | **3**（`/gsd-map-codebase` / `/gsd-new-project` / `/gsd-autonomous`） |
| 中途被問幾次決策 | 多次（每 phase gate） | **3**（2 個灰色決策：資料模型、行為細節 + 1 個「修不修 MF-01」） |
| 我對計劃的掌控 | 高（逐份審 PLAN.md） | 低（roadmapper / planner 自己決定，我只核可） |
| 品質防線 | 有 | **一樣有**（plan-check + verifier + code-review 照跑） |
| 適合的任務 | 需求模糊 / 要把關 | 需求清楚 / 信任它 |
| 風險 | 慢 | 跑偏較晚發現 —— 但 review 兜住了（見下） |

### 核心心得

1. **YOLO 拿掉的是「phase gate」，不是「品質 gate」。** autonomous 一路跑 discuss→plan→execute，中間不停；但 `plan-check`、`verifier`、`code-review` 仍在背後守門。真正「喝咖啡看它跑完」= `/gsd-autonomous` + `--dangerously-skip-permissions`（前者拿掉 phase gate，後者拿掉工具授權 gate）。

2. **brownfield walking-skeleton 踩坑（必記）。** Phase 1 是 `**Mode:** mvp`，GSD 的 walking-skeleton 閘門（mvp + phase 01 + 無前置 summary）會誤觸發，叫 planner 從零搭「專案+路由+DB+UI」骨架——對既有純函式 todo 完全錯誤。**手動覆寫**：派 planner 時強制 `WALKING_SKELETON=false` + 標 brownfield/no-scaffold。

3. **code-review 真的攔下一個隱藏 regression（MF-01）。** 任務從 `list[str]` 升級成 `list[dict]` 後，`list_tasks` 的 `list(tasks)` 淺複本**不再隔離**——dict 是可變的、被共享參照，呼叫端改 `done` 會偷改內部狀態，但 docstring 還保證「不會被外部竄改」。既有測試只測 list 層 `.append`，沒測 dict 欄位，所以**沒抓到**。修法：`copy.deepcopy(tasks)` + 強化測試去改 `returned[0]["done"]` 斷言內部不變。→ 這就是「自動」之下品質防線的價值。

4. **最終戰果**：`list[str]`→`list[dict]`、新增 `complete_task`/`list_pending`、測試 6→**12 全綠**、9 個 atomic commit。

---

## 八、驗收標準

- [x] `app.py` 多了 `complete_task()` 和 `list_pending()`
- [x] `test_app.py` 多了對應測試
- [x] `PYTHONUTF8=1 pytest test_app.py -v` 全綠（**12 passed**：原 6 更新 + 新 6）
- [x] 你能說出 `/gsd-autonomous` 和 `/gsd-discuss-phase` 逐步的差別
- [x] 你知道 `--dangerously-skip-permissions` 是什麼、為何只能本地用

---

## 起點 app.py 函式（你的 brownfield base）

```python
add_task(tasks, name)      # 新增，空 name 拋 ValueError
list_tasks(tasks)          # 列出全部（回傳 copy）
delete_task(tasks, name)   # 刪除，回傳 True/False
# complete_task  ← YOLO 要自動加的
# list_pending   ← YOLO 要自動加的
```
