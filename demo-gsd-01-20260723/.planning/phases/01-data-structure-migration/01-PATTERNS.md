# Phase 1: 資料結構遷移與測試安全網重建 - Pattern Map

**Mapped:** 2026-07-23
**Files analyzed:** 2（`app.py` 修改、`test_app.py` 修改；無新檔案）
**Analogs found:** 2 / 2（皆為「自我參照」型分析——本 phase 是單檔 brownfield 專案，沒有第二個同角色檔案可借鏡，因此每個函式最強的分析對象就是它自己的現況實作）

## 重要說明：為何本 phase 沒有外部分析對象

`app.py` 是全專案唯一的實作檔案（117 行、無其他模組、無其他 controller/service/model 檔案），`test_app.py` 是唯一測試檔案。這次 phase 不是「建新檔案」，而是「原地改寫既有函式的內部邏輯與型別」。因此本 PATTERNS.md 的每個「Analog」欄位指向的是**同一個函式修改前的現況版本**（app.py 目前這版）或**研究文件推薦的黃金寫法**（當現況完全沒有可抄的既有 dataclass 用法時）。這與一般「跨檔案抄襲既有 controller 寫法」的情境不同，但角色分類與資料流分類方式相同，Planner 依然可以照抄下方的具體程式碼片段與行號。

## File Classification

| New/Modified File | Role | Data Flow | Closest Analog | Match Quality |
| --- | --- | --- | --- | --- |
| `app.py` — 新增 `Task` dataclass | model | CRUD（資料定義，無 I/O） | 無既有 codebase 用法；分析對象為 `.planning/research/STACK.md` 建議寫法 | no-analog（採研究推薦寫法） |
| `app.py::add_task` | service/utility | CRUD（create） | `app.py:12-24`（同函式現況實作） | self-analog（就地改寫） |
| `app.py::list_tasks` | service/utility | CRUD（read，含複製語意） | `app.py:27-36`（同函式現況實作） | self-analog（複製深度需升級） |
| `app.py::delete_task` | service/utility | CRUD（delete） | `app.py:39-53`（同函式現況實作） | self-analog（內部邏輯須整段重寫，風險最高） |
| `app.py::_print_task_list` | utility（presentation helper） | transform | `app.py:56-62`（同函式現況實作） | self-analog（僅需相容 `.name`，本 phase 不加 ✓） |
| `test_app.py`（3 個 Test 類別、12 個測試） | test | CRUD 驗證 | `test_app.py:1-67`（同檔現況全文） | self-analog（斷言字面值機械式替換） |

## Pattern Assignments

### `app.py` — 新增 `Task` dataclass（model，本 phase 的地基）

**Analog：** 無既有 codebase 用法（`.planning/codebase/CONVENTIONS.md` 明確指出「No custom classes or dataclasses exist yet」）。改採 `.planning/research/STACK.md` 與 `.planning/research/ARCHITECTURE.md` 一致推薦的寫法。

**imports 慣例**（比照 `app.py:9` 既有 `import sys` 的單行 stdlib import 風格，新增一行）：

```python
import sys
from dataclasses import dataclass
```

**核心 dataclass 定義**（研究文件建議位置：`import` 區塊之後、`add_task` 之前）：

```python
@dataclass
class Task:
    """一筆待辦任務：名稱與完成狀態。"""
    name: str
    done: bool = False
```

**必須遵守的取捨（D-01/D-02，來自 STACK.md）：**

- **不要**加 `slots=True`（Python 3.14 已知 regression，見 STACK.md 第 74 行、cpython#135228 / #142214）。
- **不要**加 `frozen=True`（Phase 2 `complete_task` 需要 `matched_task.done = True` 就地變動）。
- 保留預設可變 dataclass + 自動生成的 `__eq__`，讓 12 個既有測試能機械式改成 `Task("買牛奶")` 建構式比對。
- docstring 延續全專案 Google-style + 繁體中文慣例（見下方「共用模式」）。

---

### `app.py::add_task`（service/utility，CRUD-create）

**Analog：** 同函式現況（`app.py:12-24`）

**現況實作（改寫前）：**

```python
def add_task(tasks: list, name: str) -> None:
    """新增一筆待辦任務到 tasks 清單中。

    Args:
        tasks: 現有的任務清單（就地修改）。
        name:  任務名稱字串。

    Raises:
        ValueError: 若 name 為空字串，拒絕新增。
    """
    if not name or not name.strip():
        raise ValueError(f"任務名稱不可為空字串：{name!r}")
    tasks.append(name.strip())
```

**需要改寫的唯一一行**（依 ARCHITECTURE.md Ripple Effect 表：衝擊等級「低」，簽名不變）：

- `tasks.append(name.strip())` → `tasks.append(Task(name=name.strip()))`
- 型別提示同步升級：`tasks: list` → `tasks: list[Task]`（D-03，內建泛型、不 import typing）
- 驗證邏輯（空字串拋 `ValueError`、`!r` 格式化訊息）**完全不動**——這是既有的錯誤處理慣例，必須保留。

---

### `app.py::list_tasks`（service/utility，CRUD-read，複製語意）

**Analog：** 同函式現況（`app.py:27-36`）

**現況實作（改寫前）：**

```python
def list_tasks(tasks: list) -> list:
    """回傳目前任務清單的副本，不影響原始資料。

    Args:
        tasks: 現有的任務清單。

    Returns:
        list: tasks 的淺複製。
    """
    return list(tasks)
```

**D-04 要求的變更（元素級複製，避免 Pitfall 7 別名污染）：**

- 舊寫法 `return list(tasks)` 只複製容器、不複製元素——`Task` 是可變物件，呼叫端改 `result[0].done = True` 會直接污染原始 `tasks`（PITFALLS.md 第 154-174 行，Pitfall 7）。
- 依 D-04 與 ARCHITECTURE.md 建議，改為逐元素複製，例如：

```python
from dataclasses import replace

def list_tasks(tasks: list[Task]) -> list[Task]:
    """回傳目前任務清單的獨立副本，修改回傳值不影響原始資料。

    Args:
        tasks: 現有的任務清單。

    Returns:
        list[Task]: 每個 Task 元素皆為獨立副本的清單快照。
    """
    return [replace(t) for t in tasks]
```

- docstring 措辭需更新，明確寫出「元素也是獨立副本」（呼應既有慣例「每個公開函式皆有完整 docstring」）。
- 型別提示同步升級為 `list[Task]`（D-03）。

---

### `app.py::delete_task`（service/utility，CRUD-delete，**風險最高**）

**Analog：** 同函式現況（`app.py:39-53`）

**現況實作（改寫前）：**

```python
def delete_task(tasks: list, name: str) -> bool:
    """從清單中刪除指定名稱的任務。

    Args:
        tasks: 現有的任務清單（就地修改）。
        name:  要刪除的任務名稱。

    Returns:
        True  — 成功刪除。
        False — 清單中不存在此名稱。
    """
    if name in tasks:
        tasks.remove(name)
        return True
    return False
```

**必須整段重寫的原因（ARCHITECTURE.md Ripple Effect 表 + PITFALLS.md Pitfall 觀察）：**
`name in tasks` 與 `tasks.remove(name)` 依賴「字串直接相等比較」；換成 `Task` 物件後這兩個運算子會**靜默失效**（`name in tasks` 恆為 `False`，不拋例外），是本 phase 唯一「簽名不變、內部邏輯必須整段重寫」的函式。

**建議寫法（維持既有 bool 回傳慣例、維持「只刪除第一筆符合者」語意，呼應 `test_delete_only_first_occurrence`）：**

```python
def delete_task(tasks: list[Task], name: str) -> bool:
    """從清單中刪除指定名稱的任務（僅移除第一筆符合者）。

    Args:
        tasks: 現有的任務清單（就地修改）。
        name:  要刪除的任務名稱。

    Returns:
        True  — 成功刪除。
        False — 清單中不存在此名稱。
    """
    for t in tasks:
        if t.name == name:
            tasks.remove(t)
            return True
    return False
```

- 回傳型別維持 `bool`（不引入例外），與 `.planning/codebase/CONVENTIONS.md` 「Mutating functions that report success/failure return bool」慣例一致。
- 型別提示同步升級為 `list[Task]`（D-03）。
- **不要**用 `tasks[:] = [t for t in tasks if t.name != name]` 這類「全部符合者一起刪」的寫法——會破壞既有「只刪第一筆」的語意契約（`test_delete_only_first_occurrence` 會抓到）。

---

### `app.py::_print_task_list`（presentation helper，本 phase 僅需相容 `.name`）

**Analog：** 同函式現況（`app.py:56-62`）

**現況實作（改寫前）：**

```python
def _print_task_list(tasks: list) -> None:
    """輔助函式：把任務清單格式化輸出到 stdout。"""
    if not tasks:
        print("（目前沒有任何待辦任務）")
        return
    for idx, task in enumerate(tasks, start=1):
        print(f"  {idx}. {task}")
```

**本 phase 範圍內的最小改動**（CONTEXT.md code_context 明確界定：「本階段只需相容 Task（印 `task.name`），✓ 標記留給 Phase 3」）：

- 唯一需要改的一行：`print(f"  {idx}. {task}")` → `print(f"  {idx}. {task.name}")`
- **不要**在本 phase 加上 `✓`/`done` 顯示邏輯——那是 Phase 3 的範圍，本 phase 加了就是 scope creep（呼應 PITFALLS.md Pitfall 5「範圍蔓延」的精神，雖然該 pitfall 講的是 complete_task，但同樣原則適用：只做這個 phase 明訂的事）。
- 型別提示同步升級為 `list[Task]`（D-03）。

---

### `test_app.py`（test，12 個既有測試機械式遷移）

**Analog：** 同檔現況全文（`test_app.py:1-67`）

**imports 需新增 `Task`**（現況 `test_app.py:1-3`）：

```python
"""demo-gsd-01-20260630 — 基底測試套件（12 個測試，字串型態）"""
import pytest
from app import add_task, list_tasks, delete_task
```

→ 改為：

```python
"""demo-gsd-01-20260723 — 基底測試套件（12 個測試，Task dataclass 型態）"""
import pytest
from app import add_task, list_tasks, delete_task, Task
```

（module docstring 也應更新，反映測試資料已從字串改為 `Task`；沿用既有「檔案開頭有一行說明」慣例。）

**機械式替換範例 1 — TestAddTask 類別**（現況 `test_app.py:7-10`，字串斷言）：

```python
def test_add_single_task_happy_path(self):
    tasks = []
    add_task(tasks, "買牛奶")
    assert tasks == ["買牛奶"]
```

→ 遷移後：

```python
def test_add_single_task_happy_path(self):
    tasks = []
    add_task(tasks, "買牛奶")
    assert tasks == [Task("買牛奶")]
```

（`done` 欄位有預設值 `False`，靠 dataclass 自動 `__eq__` 逐欄位比對，`Task("買牛奶")` 等同 `Task("買牛奶", done=False)`——ARCHITECTURE.md 第 50 行明確驗證此點。）

**機械式替換範例 2 — TestListTasks 類別，需額外補強別名污染防線**（現況 `test_app.py:35-39`）：

```python
def test_list_tasks_returns_copy(self):
    tasks = ["任務A"]
    result = list_tasks(tasks)
    result.append("任務B")
    assert tasks == ["任務A"]
```

→ 遷移後（保留原斷言 + 依 PITFALLS.md Pitfall 7 建議補一個「修改回傳值中既有元素欄位」的防線）：

```python
def test_list_tasks_returns_copy(self):
    tasks = [Task("任務A")]
    result = list_tasks(tasks)
    result.append(Task("任務B"))
    assert tasks == [Task("任務A")]

def test_list_tasks_element_mutation_does_not_leak(self):
    tasks = [Task("任務A")]
    result = list_tasks(tasks)
    result[0].done = True
    assert tasks[0].done is False
```

（第二個測試是否納入本 phase 屬於 planner 裁量範圍，但 PITFALLS.md 明確指出這是「既有測試綠燈≠沒有這個 bug」的已知缺口，建議一併補上以完整驗證 D-04。）

**機械式替換範例 3 — TestDeleteTask 類別（含 bool 回傳斷言慣例）**（現況 `test_app.py:50-53`）：

```python
def test_delete_existing_task_returns_true(self):
    tasks = ["任務A"]
    assert delete_task(tasks, "任務A") is True
    assert tasks == []
```

→ 遷移後：

```python
def test_delete_existing_task_returns_true(self):
    tasks = [Task("任務A")]
    assert delete_task(tasks, "任務A") is True
    assert tasks == []
```

（`delete_task` 的參數 `name` 本身仍是純字串——只有 `tasks` 清單元素換成 `Task`，呼叫端傳入的 `name` 引數不變，這是遷移時容易搞混的一點：不要把 `delete_task(tasks, Task("任務A"))` 這種寫法帶進來，函式簽名 `delete_task(tasks, name: str)` 沒有變。）

**測試類別/命名結構維持不變**（`.planning/codebase/TESTING.md` 慣例）：

- 沿用 `TestAddTask` / `TestListTasks` / `TestDeleteTask` 三個既有類別，本 phase 不新增 `TestCompleteTask`（那是 Phase 2 範圍）。
- 測試方法命名維持 `test_<情境>_<預期結果>` 格式，不必因為型別改變而重新命名（例如 `test_add_single_task_happy_path` 名稱不變，只改內部斷言）。
- 沿用「每個測試方法自建本地 `tasks` 變數、零 fixture」的慣例（見 TESTING.md 第 81 行）。

## Shared Patterns

### 型別提示升級（D-03）

**Source:** `app.py` 現況每個函式簽名（`tasks: list` → `list[Task]`）
**Apply to:** `add_task`、`list_tasks`、`delete_task`、`_print_task_list` 四個函式簽名

```python
# 現況（改前）
def add_task(tasks: list, name: str) -> None: ...
def list_tasks(tasks: list) -> list: ...
def delete_task(tasks: list, name: str) -> bool: ...
def _print_task_list(tasks: list) -> None: ...

# 遷移後
def add_task(tasks: list[Task], name: str) -> None: ...
def list_tasks(tasks: list[Task]) -> list[Task]: ...
def delete_task(tasks: list[Task], name: str) -> bool: ...
def _print_task_list(tasks: list[Task]) -> None: ...
```

不 import `typing`，延續內建泛型慣例（`.planning/codebase/CONVENTIONS.md` 第 26 行）。

### 錯誤處理慣例（不因本 phase 改變）

**Source:** `app.py:22-23`（`add_task` 的 `ValueError`）、`app.py:96-97`（`main()` 的 `except ValueError`）
**Apply to:** `add_task` 保持不變；本 phase 不改 `main()` 的 CLI dispatch 邏輯

```python
if not name or not name.strip():
    raise ValueError(f"任務名稱不可為空字串：{name!r}")
```

「找不到」用 bool 回傳（`delete_task`）、「無效輸入」才 raise（`add_task`）的二分慣例，Phase 1 完全延續，不新增第三種回傳型態（第三態留給 Phase 2 的 `complete_task`）。

### Docstring 慣例（Google-style + 繁體中文）

**Source:** `.planning/codebase/CONVENTIONS.md` 第 84-98 行
**Apply to:** `Task` dataclass 與所有被修改的函式

```python
def delete_task(tasks: list, name: str) -> bool:
    """從清單中刪除指定名稱的任務。

    Args:
        tasks: 現有的任務清單（就地修改）。
        name:  要刪除的任務名稱。

    Returns:
        True  — 成功刪除。
        False — 清單中不存在此名稱。
    """
```

每個公開函式（含新的 `Task` dataclass）都要有完整繁體中文 docstring，即使簡短。

### 別名污染防線（D-04 對應的 Pitfall 7 防禦）

**Source:** `.planning/research/PITFALLS.md` 第 154-174 行
**Apply to:** `list_tasks` 的實作與其測試

```python
from dataclasses import replace
return [replace(t) for t in tasks]
```

不可只用 `list(tasks)`（僅複製容器，元素仍是同一參照）。

## No Analog Found

| File/Pattern | Role | Data Flow | Reason |
|---|---|---|---|
| `Task` dataclass 定義本身 | model | N/A（純資料定義） | codebase 中從無任何 class/dataclass 先例（`.planning/codebase/CONVENTIONS.md` 明確記載），改採 `.planning/research/STACK.md` 第 63-75 行與 `.planning/research/ARCHITECTURE.md` 第 38-45 行的推薦寫法作為本 phase 的「權威範本」 |

## Metadata

**Analog search scope:** 專案根目錄僅 `app.py` / `test_app.py` 兩個程式碼檔案（單檔 brownfield 專案，無 `src/`、無其他模組目錄）；已確認無其他 `.py` 檔案存在。
**Files scanned:** `app.py`（117 行，全讀）、`test_app.py`（67 行，全讀）、`.planning/phases/01-data-structure-migration/01-CONTEXT.md`、`.planning/research/ARCHITECTURE.md`、`.planning/research/PITFALLS.md`、`.planning/research/STACK.md`、`.planning/codebase/CONVENTIONS.md`、`.planning/codebase/TESTING.md`
**Pattern extraction date:** 2026-07-23
