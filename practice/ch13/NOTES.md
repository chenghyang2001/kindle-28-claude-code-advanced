# NOTES — K28 第 13 章練習（多 agent 團隊與 agent debate）

> 快速 demo 模式（依本專案 CLAUDE.md）：主 agent 不寫業務碼，程式由實作子代理撰寫，未另跑 code-qa/code-reviewer 鐵律流程。

## 做了什麼
1. **自建小任務專案**：`src/todo.py`（JSON 保存的 todo 清單）+ `tests/test_todo.py`（3 個測試）+ 範例資料 `data/sample-todos.json`，commit 成基準線。
2. **寫合約** `contracts/CONTRACT.md`：任務定義、四個角色的讀寫邊界、Never modifies 條款、git diff 驗證方式。
3. **練習 01：真的派出三個 general-purpose 子代理**（依序執行，每一棒都驗證）
   - 研究 agent（只讀）→ 相依地圖 + 7 條風險 → `reports/01-research.md`
   - 實作 agent（只寫 src/、tests/）→ `overdue()`、`sorted_items()` + 12 個測試 → `reports/02-implementation.md`
   - 審查 agent（只讀）→ 1 條必改 + 5 條建議 → `reports/03-review.md`
4. **練習 02：在同一則訊息平行派 3 位審查者**（正確性／安全性／可維護性）辯論審查 agent 必改項目的爭議修法（方案 X：priority 不合法就靜默改成 3）→ `reports/04-debate.md`
5. **閉環**：依裁決再派實作 agent 修正 → `reports/05-fix.md`
6. 解答：`answer/ex01-answer.md`、`answer/ex02-answer.md`

## 驗證結果
| 項目 | 結果 |
| --- | --- |
| 基準線測試 | 3 passed |
| 實作第一輪 | 15 passed（主 agent 重跑相同） |
| 實作第二輪 | 23 passed（主 agent 重跑相同） |
| 研究 agent 只讀 | `git status`/`git diff`：追蹤檔無變更 ✅ |
| 實作 agent 邊界 | 兩輪的 `git diff --name-only` 都只有 src/、tests/，越界檢查「無越界」✅ |
| 審查 agent 只讀 | `git status` 為空；`.pyc` 時間戳早於審查開始 → 連被忽略的檔都沒產生 ✅ |
| 3 位辯論審查者只讀 | `git status` 只有主 agent 寫的 reports/03-review.md ✅ |
| Debate 裁決 | 反對 3 / 贊成 0 → 方案 X 打回，採方案 Y + 合議補強 |
| 冒煙實驗 | overdue=[1]、sorted=[1, 4, 2, 3]、None→3、'1'/True/-1 被拒絕且訊息不含原值 |

## 過程中值得記錄的事
- **上游錯誤被下游擋下**：研究 agent 把預期排序算成 [4, 1, 2, 3]（id1 的 due 10-15 其實比 id4 的 10-18 早）。實作 agent 照合約算出 [1, 4, 2, 3] 並主動回報衝突；主 agent 以合約為準裁決。我派工時的 prompt 也照抄了研究的錯誤值，這也被擋下了。
- **審查找到真 bug**：`priority=None` 會讓 `sorted_items()` TypeError，這是研究與實作都沒注意到的。
- **少數意見被保留**：安全性審查者指出方案 Y 在讀取端也有 DoS 風險，未達多數、不採納，但寫進紀錄列為已知風險。

## 和題目要求的差異
- 題目只要求「設計／畫出」分工與合約；本次**實際派出子代理執行並用 git diff 驗證**（依本章補充要求）。
- 練習 02 的爭議決策沒有另外虛構，而是**直接取自練習 01 審查 agent 的必改項目**，所以 debate 的結論能真正落地成程式碼修改（多一輪實作 agent）。
- 練習 02 的範例規則是「≥2 反對則打回」，本次照用，並另外記錄少數意見的處理。
- 子代理一律用 general-purpose，在 prompt 裡寫明角色與讀寫邊界（沒用全域自訂 agent 類型）。讀寫邊界是靠 prompt 約束 + 事後 git 驗證，**不是**工具層級的強制權限；若要強制，可在 `.claude/agents/` 建專案層 agent 並以 `tools:` 限制只給 Read/Grep/Glob（本次未做）。
- 未用到：MCP、plugin、git worktree、`claude -p`、GSD/Ralph（本章題目不需要）。
- `.claude/session-state.md` 是本機 SessionStart/UserPromptSubmit hook 自動產生的，不是任何子代理寫的；已加入 `.gitignore`。
- 沒有建 GitHub repo、沒有 push。
