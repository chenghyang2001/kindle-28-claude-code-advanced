# 練習 01 解答：三 agent 團隊（實際派出執行）

任務專案：`src/todo.py`（JSON 檔保存的 todo 清單），新增 `overdue(today)` 與 `sorted_items()`。
合約全文：`contracts/CONTRACT.md`；各 agent 交付物：`reports/01~03`。

## 任務 1：分工與交付物（誰產出什麼給誰）

```text
                  ┌────────────── 主 agent（架構師）──────────────┐
                  │ 寫合約 → 派工 → 存交付物 → 驗證邊界 → 裁決衝突 → commit │
                  └──┬──────────────────┬──────────────────┬──────┘
          ① 派工     │        ③ 派工(帶研究結論)│        ⑤ 派工(帶 commit) │
                     ▼                  ▼                  ▼
            ┌──────────────┐   ┌──────────────┐   ┌──────────────┐
            │ 研究 agent    │   │ 實作 agent    │   │ 審查 agent    │
            │ 只讀          │   │ 只寫 src/tests│   │ 只讀          │
            └──────┬───────┘   └──────┬───────┘   └──────┬───────┘
         ② 相依地圖+風險清單   ④ 程式碼+測試+變更摘要  ⑥ 必改/建議清單
                     └──────→ reports/01 ──→ 實作讀  reports/02 ──→ 審查讀  reports/03
```

| 角色 | 輸入 | 交付物 | 交給誰 | 實際結果 |
| --- | --- | --- | --- | --- |
| 研究 agent | 合約、src、tests、data | 相依地圖 + 7 條風險 + 測試清單 | 主 agent → 存成 reports/01 → 實作 agent | ✅ 完成；但預期排序 [4,1,2,3] 算錯了 |
| 實作 agent | 合約 + reports/01 | `src/todo.py` +37 行、12 個測試 | 主 agent → commit → 審查 agent | ✅ 15 passed；照合約糾正了研究的錯誤 → [1,4,2,3] |
| 審查 agent | 合約 + reports/01、02 + HEAD | 1 條必改 + 5 條建議 + 合約符合度表 | 主 agent | ✅ 找到 priority=None 會讓 sorted_items 當掉 |
| 主 agent | 三份交付物 | 裁決、commit、交給練習 02 | — | 沒有寫任何業務程式碼 |

三個 agent 的職責不重疊：研究只產出「事前資訊」，實作只產出「程式碼」，審查只產出「事後判斷」。三者的交付物型態也不同（地圖／程式碼／清單）。

## 任務 2：合約邊界

| 角色 | 可讀 | 可寫 | 禁止 |
| --- | --- | --- | --- |
| 研究 agent | 全部 | 無 | Write/Edit、任何寫檔的 shell 指令、pytest（會產生快取） |
| 實作 agent | 全部 | `src/`、`tests/` | contracts/、reports/、data/、answer/、.claude/、CLAUDE.md；git 寫入操作 |
| 審查 agent | 全部 | 無 | 同研究 agent；只能用 `python -B -c` 做記憶體內實驗 |
| 主 agent | 全部 | reports/、contracts/、answer/、文件 | 業務程式碼（src/） |

合約的關鍵設計：
1. **寫在檔案裡**（contracts/CONTRACT.md），每個 agent 開工前都先讀；prompt 裡也重述一次讀寫邊界。
2. **可驗證**：每個 agent 回傳後，主 agent 跑 `git status --porcelain` / `git diff --name-only` 檢查。
3. **交付物由主 agent 落地**：只讀 agent 用文字回傳，由主 agent 存成 reports/，所以只讀角色連報告都不必寫。
4. **commit 只有主 agent 做**：每個階段 commit 一次，下一個 agent 就有乾淨的比對基準。

## git diff 驗證結果（實際輸出）

| 時間點 | 指令 | 輸出 | 判定 |
| --- | --- | --- | --- |
| 研究 agent 回傳後 | `git status --porcelain` + `git diff --name-only` | 只有 `?? .claude/`（hook 產生的 session-state.md，13:36 寫入，早於派工），追蹤檔無變更 | ✅ 未改檔 |
| 實作 agent 回傳後 | `git diff --name-only` + 越界 grep | `src/todo.py`、新檔 `tests/test_features.py`；越界檢查「無越界」 | ✅ 只寫 src/tests |
| 審查 agent 回傳後 | `git status --porcelain` + `git diff HEAD --name-only` | 空；`.pyc` 時間戳 13:38（審查 13:39 之後才開始）→ 連被忽略的檔都沒產生 | ✅ 未改檔 |

## 驗收
- [x] 三 agent 職責不重疊（產出物型態不同，順序依賴明確）
- [x] 有明確的讀/寫邊界（合約檔 + 每階段 git diff 驗證）

## 心得
- 「研究算錯、實作照合約糾正」正是多 agent 的價值：實作 agent 的 context 乾淨，被要求以合約為準，所以沒有盲從上游的結論。
- 主 agent 的裁決依據是**合約**，不是「誰比較有自信」。
