# GSD YOLO 練習（2 個 Phase）— demo-gsd-03-yolo-2-phases

> 進階版：`demo-gsd-02-yolo`（你做過的單 phase YOLO）→ 本練習是**雙 phase**。
> 重點：看 `/gsd-autonomous` 怎麼**自動跑完 Phase 1 再自動接 Phase 2**（auto_advance）。
> 指令格式：你這台是 flat skills 版，全部用 **dash**（`/gsd-xxx`），不是冒號。

---

## 一、這次和上次差在哪？

| | demo-gsd-02-yolo（上次） | demo-gsd-03（本次） |
|---|---|---|
| Phase 數 | 1 個 | **2 個（循序）** |
| 學習重點 | 體驗 autonomous 跑一個 phase | 體驗 autonomous **連跑多 phase 不停手** |
| 關鍵機制 | discuss→plan→execute | 上述 ×2 + **auto_advance**（phase 間自動推進） |

---

## 二、為什麼這個任務會變成「2 個 phase」？

關鍵在**相依性**：Phase 2 必須建立在 Phase 1 的成果上，GSD 才會把它們排成循序兩段。

| Phase | 功能 | 為何相依 |
|---|---|---|
| **Phase 1：任務完成狀態** | task 從 `str` 改成 `dict{name, done}`，加 `complete_task(tasks, name)` + `list_pending(tasks)` | 改變了資料結構 |
| **Phase 2：存檔持久化** | 加 `save_tasks(tasks, path)` + `load_tasks(path)`（用 JSON） | **要先有 Phase 1 的 dict 結構，才能正確存下 done 狀態** |

> 如果兩個功能互不相干，GSD 可能塞進同一個 phase。
> 因為 Phase 2 依賴 Phase 1 的資料結構，GSD 會自然排成 Phase 1 → Phase 2。

---

## 三、起點 app.py（你的 brownfield base，乾淨 3 函式）

```python
add_task(tasks, name)      # 新增，空 name 拋 ValueError
list_tasks(tasks)          # 列出全部（回傳 copy）
delete_task(tasks, name)   # 刪除，回傳 True/False
# 以下都是 YOLO 要自動加的：
# Phase 1 → complete_task / list_pending（並把 task 改 dict）
# Phase 2 → save_tasks / load_tasks（JSON 持久化）
```

---

## 四、前置準備（一次性）

```bash
cd C:/Users/B00332/workspace/kindle-28-claude-code-advanced/demo-gsd-03-yolo-2-phases
pip install pytest
PYTHONUTF8=1 pytest test_app.py -v
# 預期：baseline 全綠（6 passed）
```

---

## 五、YOLO 練習步驟

### Step 1：用 YOLO 啟動法開 Claude Code

```bash
cd C:/Users/B00332/workspace/kindle-28-claude-code-advanced/demo-gsd-03-yolo-2-phases
claude --dangerously-skip-permissions
```

### Step 2：建 codebase 地圖（小專案用 fast 版即可）

```
/gsd-map-codebase
```

> 只有 2 個檔，可選 fast 模式（單 agent 快掃），不用完整四 agent。

### Step 3：建專案 roadmap — **這步是 2-phase 的關鍵**

```
/gsd-new-project
```

當它問你要做什麼，**明確描述兩個有先後關係的需求**，幫它切出 2 個 phase：

```
這是一個既有的待辦清單 CLI（目前 task 是純字串）。請分兩個階段擴充：

第一階段（任務完成狀態）：
- 把 task 從 str 改成 dict，含 name 和 done 兩個欄位
- 新增 complete_task(tasks, name)：標記完成
- 新增 list_pending(tasks)：只列出未完成

第二階段（存檔持久化，必須建立在第一階段的 dict 結構上）：
- 新增 save_tasks(tasks, path)：把任務（含 done 狀態）存成 JSON 檔
- 新增 load_tasks(path)：從 JSON 檔讀回任務

每階段都要補 pytest 測試，且不可弄壞現有 6 個測試。
```

> 看 GSD 產出的 `ROADMAP.md`：應該會看到 **Phase 1 + Phase 2 兩段**。
> 這就是 2-phase 練習的核心觀察點。

### Step 4：確認 roadmap 真的是 2 個 phase（重要檢查）

在跑 autonomous 前，先看一眼：

```
/gsd-progress
```

或直接看檔案：`.planning/ROADMAP.md`。
確認有 2 個 phase 再往下，否則 autonomous 只會跑 1 個。

### Step 5：一鍵 YOLO 跑完兩個 phase

```
/gsd-autonomous
```

接著**雙手離開鍵盤**。觀察重點：

- Phase 1 跑完（discuss→plan→execute）後，**不問你**就自動接 Phase 2
- 這個「自動接下一個」就是 `auto_advance` 的效果

> 想只跑到 Phase 1 停：`/gsd-autonomous --to 1`
> 想只跑 Phase 2：`/gsd-autonomous --only 2`

### Step 6：驗收

```bash
PYTHONUTF8=1 pytest test_app.py -v
# 預期：原 6 個 + Phase 1 + Phase 2 新增測試，全綠

grep -nE "def (complete_task|list_pending|save_tasks|load_tasks)" app.py
# 預期：4 個函式都出現

ls .planning/phases/
# 預期：看到 2 個 phase 資料夾
```

---

## 六、2-phase 專屬觀察點（練完填）

| 觀察 | 你看到什麼 |
|---|---|
| ROADMAP.md 切了幾個 phase？ | **2 個**：Phase 1 任務完成狀態（Status）→ Phase 2 存檔持久化（Persistence）|
| Phase 1 → Phase 2 之間 GSD 有停下問你嗎？ | **沒有**。Phase 1 verifier PASS 後 re-read ROADMAP，直接接 Phase 2，中間無任何提問 = `auto_advance` |
| Phase 2 的 PLAN 有沒有「依賴 Phase 1 結構」的描述？ | **有**。Phase 2 `Depends on` 明寫 `save_tasks` 要存 `done`，而 `done` 只在 Phase 1 把 task 改 `dict` 後才存在 |
| `.planning/phases/` 下有幾個資料夾？ | **2 個**：`01-status`、`02-persistence` |
| autonomous 全程你下了幾次指令？ | **0 次**（只在開跑前說一次「執行」）|

### 驗收結果（2026-06-22）

- `PYTHONUTF8=1 pytest test_app.py -v` → **19 passed**（原 6 → Phase 1 後 15 → Phase 2 後 19）
- `app.py` 新增 4 函式：`complete_task` / `list_pending` / `save_tasks` / `load_tasks`
- task 結構 `str` → `dict{name, done}`
- 每個 phase 走完整 `discuss → plan → plan_check → execute → verify`，兩個 phase verifier 皆 PASS（各 5/5）
- 設定：mode=YOLO / granularity=coarse / research=off / plan_check=on / verifier=on / model=balanced(Sonnet)

---

## 七、autonomous 的範圍控制 flag（進階）

`/gsd-autonomous` 支援這些 flag（實測自安裝的 skill）：

| Flag | 作用 |
|---|---|
| `--from N` | 從第 N 個 phase 開始跑 |
| `--to N` | 跑到第 N 個 phase 就停（不自動推進下一個） |
| `--only N` | 只跑第 N 個 phase |
| `--interactive` | discuss 階段仍問你，plan+execute 才自動背景跑 |

> 學習建議：第一次用 **無 flag**（跑完全部），體會完整 auto_advance；
> 第二次可試 `--to 1` 看「停在 phase 1」的差別。

---

## 八、驗收標準

- [ ] `ROADMAP.md` 切出 2 個 phase
- [ ] `app.py` 多了 4 個函式（complete_task / list_pending / save_tasks / load_tasks）
- [ ] task 結構從 str 改成 dict
- [ ] `PYTHONUTF8=1 pytest test_app.py -v` 全綠
- [ ] `.planning/phases/` 下有 2 個 phase 資料夾
- [ ] 你能說出 autonomous 在 Phase 1→2 之間「沒停下」就是 auto_advance

```
