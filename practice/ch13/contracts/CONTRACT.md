# 三 agent 合約（本任務專案）

## 任務
為 `src/todo.py` 新增兩個功能：
1. `TodoStore.overdue(today)`：回傳未完成且 `due < today` 的項目（`today` 為 `datetime.date`，`due` 為 `YYYY-MM-DD` 字串或 None）
2. `TodoStore.sorted_items()`：依「未完成優先 → priority 小者優先 → due 早者優先（None 排最後）」排序

## 角色與讀寫邊界

| 角色 | 可讀 | 可寫 | 交付物（給誰） |
| --- | --- | --- | --- |
| 研究 agent | 全部 | **無**（Never modifies any file） | 相依地圖 + 風險清單（文字回傳給主 agent） |
| 實作 agent | 全部 | **只限 `src/`、`tests/`** | 程式碼 + 單元測試 + 變更摘要（給主 agent → 審查 agent） |
| 審查 agent | 全部 | **無**（Never modifies any file） | 必改/建議清單（文字回傳給主 agent） |
| 主 agent | 全部 | `reports/`、`contracts/`、`answer/`、文件 | 派工、把回傳存到 `reports/`、整合、裁決衝突 |

## Never modifies 條款
- 研究、審查 agent：不得執行 Write / Edit / 任何會改檔的 shell 指令（含 `git` 寫入操作、`pytest --cache` 產生快取除外於 .gitignore）
- 實作 agent：不得碰 `contracts/`、`reports/`、`data/`、`answer/`、`.claude/`、`CLAUDE.md`
- 任何 agent 不得 `git commit` / `git push`（commit 由主 agent 做）

## 驗證方式
主 agent 在每個 agent 回傳後執行 `git status --porcelain` / `git diff --name-only`：
- 只讀角色回傳後：必須為空
- 實作角色回傳後：所有變更路徑必須以 `src/` 或 `tests/` 開頭
