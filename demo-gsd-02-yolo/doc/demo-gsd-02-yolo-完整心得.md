# GSD YOLO 模式完整實戰心得 — demo-gsd-02-yolo

**日期**：2026-06-22
**主題**：用 GSD（Get-Shit-Done）的 YOLO / autonomous 模式，在既有（brownfield）Python todo CLI 上自動新增功能，並對照 demo-gsd-01 的互動逐步模式。
**一句話**：YOLO 拿掉的是「phase gate（每階段停下來問你）」，**不是「品質 gate」**——plan-check、verifier、code-review 仍在背後守門，而且真的攔下了一個 bug。

---

## 0. 起點與目標

- **起點（brownfield base）**：`app.py` 是一個極簡 in-memory todo CLI，只有 3 個函式：
  - `add_task(tasks, name)`：新增任務（空白名稱拋 `ValueError`）
  - `list_tasks(tasks)`：列出全部（回傳 copy）
  - `delete_task(tasks, name)`：刪除（回傳 `True`/`False`）
  - 任務以 `list[str]` 純字串存放，無「完成」概念。`test_app.py` 有 6 個通過的 pytest 測試。
- **目標**：用 YOLO 自動新增 2 個功能：
  - `complete_task(tasks, name)`：標記任務完成
  - `list_pending(tasks)`：只列出未完成任務
  - 各補 pytest 測試，且**既有 6 個測試不可弄壞**（回歸防線）。

---

## 1. GSD 的「速度光譜」

YOLO 不是單一指令，而是把「人類 gate」一層層拿掉：

| 模式 | 指令 | 會停下嗎 | 何時用 |
|---|---|---|---|
| 互動 | `discuss-phase` → `plan-phase` → execute → `verify-work`（逐個下） | ✅ 每 phase 停 | 需求模糊、要逐步把關 |
| **自動 / YOLO** | `/gsd-autonomous` | ❌ 只在灰色決策/卡關停 | 需求清楚、想一路跑完 |
| 快速 | `/gsd-quick "任務"` | ❌ 略過 discuss/research/verify | 單一明確小任務 |
| 極速 | `/gsd-fast "任務"` | ❌ 連 PLAN.md 都不寫 | 改 typo |
| 權限 YOLO（疊加層） | 啟動時 `claude --dangerously-skip-permissions` | ❌ 連工具授權 y/n 都不問 | **僅限本機安全練習環境** |

> 🔑 真正的「喝咖啡 YOLO」= `/gsd-autonomous` + `--dangerously-skip-permissions`。前者拿掉 phase gate，後者拿掉工具授權 gate，兩個一起才完全不停。

---

## 2. brownfield GSD 完整流程順序

```
map-codebase → new-project → (discuss → plan → execute → review → verify) → 里程碑收尾
                                └──────────── /gsd-autonomous 自動串完 ────────────┘
```

本次只下了 **3 個指令**：`/gsd-map-codebase`、`/gsd-new-project`、`/gsd-autonomous`。

### 2.1 `/gsd-map-codebase`（建地圖）

- 派 **4 個平行 `gsd-codebase-mapper` agent**，產出 7 份文件：STACK / INTEGRATIONS / ARCHITECTURE / STRUCTURE / CONVENTIONS / TESTING / CONCERNS（共 878 行）。
- **教訓**：對只有 2 個原始碼檔的小專案，完整版 7 份文件其實偏重（skill 自己也建議 `<5 檔可略過` 或用 `--fast`）。但完整跑一次能體會「該用哪個力道的工具」。

### 2.2 `/gsd-new-project`（開 roadmap）

長 workflow：init → brownfield 偵測（已有地圖，自動跳過）→ 提問 → `PROJECT.md` → config → research 決策 → `REQUIREMENTS.md` → 結構模式 → roadmap。

- **config 選擇**：mode=**YOLO**、granularity=**coarse**、parallel、git=yes；research=**No**（2 函式不需領域研究）、plan-check=yes、verifier=yes、模型=balanced。
- **諷刺點**：YOLO 練習的 `new-project` 反而要「深度提問」——因為 **mode=yolo 影響的是後面的自動核可，不是這一刻的需求釐清**。真正不問的是稍後的 autonomous。
- **brownfield 規則**：既有 3 函式 + 6 測試列為 `Validated`，新 2 函式列為 `Active`。
- roadmapper 很聰明：粒度粗 + 任務小 + 5 個緊密需求 → **只開 1 個 phase**，不硬拆。

### 2.3 `/gsd-autonomous`（一鍵跑完 Phase 1）

對 Phase 1 自動跑 discuss → plan → execute → review → verify。

---

## 3. autonomous 內部：3 個被問到的決策

YOLO 全程只停下來問了 3 次（全部是「真正需要人決定」的事）：

### 決策 1 — 資料模型（Grey Area 1/2，最關鍵）

`task` 目前是 `list[str]`，要加「完成」狀態有兩條路：

- **A. dict 模型**（選這個）：`list[dict]`，每個 task = `{"name": str, "done": bool}`。正規、可擴充；但既有 `add/list/delete` 與 6 測試要一起改成 dict 並保持綠。
- B. 字串標記：保持 `list[str]`，complete 用標記改字串。既有測試零改動，但 hacky。

> 因為函式簽名固定為 `complete_task(tasks, name)` 與 `list_pending(tasks)`，完成狀態**必須存在 `tasks` 內**——這就排除了「另開一個 set」的選項，逼出 dict vs 字串標記的抉擇。

### 決策 2 — 行為細節（Grey Area 2/2）

- 重複 `complete` 已完成任務 → **idempotent，回 `True`**
- 已完成任務**仍可被 `delete`**（delete 照 name、不分狀態）
- `complete_task` 回 `True`/`False`（found/not-found，與 `delete_task` 一致）
- `list_pending` 回**未完成任務的 name 字串清單**
- 既有 `list_tasks` 測試斷言改為比對 name

### 決策 3 — 要不要修 code-review 抓到的 MF-01（見第 5 節）

---

## 4. 踩坑：brownfield walking-skeleton 誤觸發（必記）

**現象**：Phase 1 是 `**Mode:** mvp`。GSD 的 walking-skeleton 閘門條件是 `MVP_MODE=true` **且** `phase==01` **且** 無前置 summary——全部成立 → `WALKING_SKELETON=true`，會叫 planner 產出 `SKELETON.md`、從零搭「專案 + 路由 + 一次真實 DB 讀寫 + 一次真實 UI 互動 + dev 部署」。

**問題**：這對既有的**純函式 in-memory todo**完全錯誤——沒有 DB、沒有 UI、沒有 web，`app.py` 已經存在。

**手動覆寫（解法）**：不要讓 plan-phase 的自動 orchestration 把 `WALKING_SKELETON=true` 烤進 planner prompt。改為**直接派 `gsd-planner`**，明確標：

- `WALKING_SKELETON = false`
- 「這是 BROWNFIELD，`app.py`/`test_app.py` 已存在，就地修改，不要 scaffold、不要 SKELETON.md」

結果：planner 正確產出 1 份 PLAN（2 tasks），**無 SKELETON.md**。

> 教訓：GSD 官方文件 / 子代理慣例用冒號指令（`/gsd:xxx`），但本機是 flat-skills 安裝，指令是**連字號**（`/gsd-xxx`）。walking-skeleton 是 brownfield 的已知地雷，plan 階段要盯。

---

## 5. 品質防線真的兜住了：MF-01 隱藏 regression

execute 後測試 11 passed、verifier 也判 `passed`（6/6 must-have）。但 **code-review（對抗式審查）抓到一個真 bug**：

**MF-01 — `list_tasks` 淺複本隔離破損**

- 原本 task 是 `str` 時，`list_tasks` 回 `list(tasks)` 就完全隔離（字串不可變）。
- 改 **dict 後，`list(tasks)` 只複製外層清單，內部 dict 仍是同一參照** → 呼叫端改回傳值的 `done` 會**偷改內部狀態**：

  ```python
  returned = list_tasks(tasks)
  returned[0]["done"] = True   # 靜默竄改內部
  assert tasks[0]["done"]      # True —— 內部狀態被汙染
  ```

- docstring 還保證「避免呼叫端在外部直接竄改內部狀態」——**契約破了**。
- 既有 `test_list_returns_copy` 只測 list 層 `.append`，**沒測 dict 欄位**，所以這個 bug 溜過了 executor + verifier。

**修法（派 `gsd-code-fixer`）**：

1. `list_tasks` 改 `return copy.deepcopy(tasks)`，回復隔離契約。
2. 強化 `test_list_returns_copy`：`returned[0]["done"] = True` 後斷言 `tasks[0]["done"]` 不變——讓這個 bug 以後不會再溜。
3. 補 `test_list_pending_empty`（`list_pending([]) == []`）。
→ 測試 11 → **12 passed**。

**被正確拒絕的 review 誤報**：reviewer 提「complete/pending 沒接進 `main()` REPL」——但那是我們**刻意 deferred 到 v2**（REPL-01），不是 bug。

> 這節是整個練習的精華：**「自動」不等於「沒人把關」**。autonomous 拿掉了「每階段停下來等你」，但 plan-check、verifier、code-review 照跑，還真的攔下一個 dict 重構引進的隱藏 regression。

---

## 6. 互動 vs YOLO 對照（親身數據）

| 面向 | 互動（demo-gsd-01） | YOLO（demo-gsd-02-yolo） |
|---|---|---|
| 下了幾次指令 | 5+（每 phase 一次） | **3** |
| 中途被問幾次決策 | 多次（每 phase gate） | **3**（2 灰色決策 + 1 修不修） |
| 對計劃的掌控 | 高（逐份審） | 低（agent 自己決定、我只核可） |
| 品質防線 | 有 | **一樣有** |
| 適合的任務 | 需求模糊 / 要把關 | 需求清楚 / 信任它 |
| 風險 | 慢 | 跑偏較晚發現（但 review 兜住） |

---

## 7. 最終戰果

- `app.py`：`list[str]` → `list[dict]`；新增 `complete_task` / `list_pending`；`list_tasks` 改 `deepcopy`。
- `test_app.py`：6 測試更新為 dict + 新增 `TestCompleteTask`（3）+ `TestListPending`（3，含空清單）= **12 passed**。
- **9 個 atomic commit**：map → PROJECT → config → REQUIREMENTS → roadmap → CONTEXT → plan → execute(×3) → fix → 收尾。
- 全程語言鐵律繁中、commit message 繁中。
- 里程碑收尾（audit → complete → cleanup）**刻意停下不跑**，保留所有 planning artifact 供回看。

---

## 8. 五個帶得走的結論

1. **YOLO 拿掉 phase gate，不拿掉品質 gate。** 想完全不停還要疊 `--dangerously-skip-permissions`（僅限本機）。
2. **brownfield + mvp + phase 01 = walking-skeleton 地雷**，plan 階段要手動覆寫成 no-skeleton。
3. **資料模型升級（str→dict）會悄悄破壞淺複本隔離**——可變物件的 `list()` 不是深複本。
4. **對抗式 code-review 的價值在於抓 verifier/executor 漏掉的隱藏 bug**，不要因為「測試全綠」就跳過。
5. **工具力道要配任務大小**：2 函式的小專案，完整版 map-codebase / opus planner 都偏重，`--fast` / sonnet 就夠。
