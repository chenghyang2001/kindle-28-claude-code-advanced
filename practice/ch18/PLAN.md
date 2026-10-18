# PLAN：待辦清單 CLI（todo.py）

> 計畫模式三段式：目標 → 步驟 → 驗收。先定介面合約，讓「核心邏輯」與「測試」兩個子代理能平行開工。

## 一、目標

做一個單檔 Python 待辦清單 CLI，支援 `add`／`list`／`done`，資料以 JSON 存檔。

### 介面合約（兩個子代理都必須遵守）

檔案：`todo.py`（專案根目錄），只用標準庫。

```python
DEFAULT_DB = "todo.json"   # 可用環境變數 TODO_DB 覆寫

def load_tasks(path) -> list[dict]      # 檔案不存在 → []；JSON 壞掉 → raise ValueError
def save_tasks(path, tasks) -> None     # UTF-8、ensure_ascii=False、indent=2
def add_task(path, title) -> dict       # 去頭尾空白；空字串 → raise ValueError；回傳新任務
def list_tasks(path) -> list[dict]      # 依 id 排序
def mark_done(path, task_id) -> dict    # 找不到 id → raise KeyError；已完成再標記不報錯
def main(argv=None) -> int              # CLI 入口，回傳 exit code
```

任務格式：`{"id": int, "title": str, "done": bool}`，id 從 1 起，取「現有最大 id + 1」。

CLI 行為：

| 指令 | 成功輸出（stdout） | exit |
| --- | --- | --- |
| `add <title...>` | `已新增 #<id>：<title>` | 0 |
| `list` | 每行 `[ ] #1 買牛奶` 或 `[x] #2 寫報告`；沒任務印 `（沒有待辦事項）` | 0 |
| `done <id>` | `已完成 #<id>：<title>` | 0 |
| 錯誤（空標題、id 不存在、id 非數字、JSON 壞掉） | 錯誤訊息印到 stderr | 1 |
| 參數錯誤／未知指令 | argparse 預設行為 | 2 |

全域選項：`--db <path>` 指定存檔路徑（優先於 `TODO_DB`）。

## 二、步驟

1. 寫本 PLAN.md，初始 commit（worktree 需要至少一個 commit）。
2. 在 `./wt/` 開兩個 worktree：`wt/core`（分支 `feat/core`）、`wt/tests`（分支 `feat/tests`），`wt/` 加進 `.gitignore`。
3. 平行派兩個子代理：
   - A：在 `wt/core` 寫 `todo.py`，commit。
   - B：在 `wt/tests` 寫 `tests/test_todo.py`（只依合約，不看實作），commit。
4. 回主線 merge 兩個分支，跑 `pytest`，修到全過。
5. 派 review 子代理審查，依 must-fix 修正，再跑 `pytest`。
6. 寫 NOTES.md（耗時、書上章節技巧、與題目差異）。
7. 移除 worktree、刪暫時分支，`git add` + `commit`（不 push）。

## 三、驗收

- [x] `python -m pytest -q` 全過
- [x] `python todo.py add 買牛奶` → `list` → `done 1` → `list` 手動流程正確
- [x] 中文標題存進 JSON 不變成 `\uXXXX`
- [x] 錯誤情境 exit code 為 1，訊息在 stderr
- [x] `git worktree list` 只剩主工作樹，`feat/*` 分支已刪
- [x] `wt/` 在 `.gitignore` 內，未被 commit
