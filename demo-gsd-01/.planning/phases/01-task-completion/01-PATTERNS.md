# Phase 1: Task Completion - Pattern Map

**Mapped:** 2026-06-22
**Files analyzed:** 2 (app.py, test_app.py — both modified; 1 new function added)
**Analogs found:** 6 / 6

---

## File Classification

| New/Modified File | Role | Data Flow | Closest Analog | Match Quality |
|---|---|---|---|---|
| `app.py` :: `complete_task` (new) | service | CRUD (update) | `app.py` :: `delete_task` lines 42-58 | exact |
| `app.py` :: `add_task` (refactor str→dict) | service | CRUD (create) | `app.py` :: `add_task` lines 12-27 (self) | self-analog |
| `app.py` :: `list_tasks` (refactor str→dict) | service | CRUD (read) | `app.py` :: `list_tasks` lines 29-39 (self) | self-analog |
| `app.py` :: `delete_task` (refactor str→dict lookup) | service | CRUD (delete) | `app.py` :: `delete_task` lines 42-58 (self) | self-analog |
| `app.py` :: `_print_task_list` (add [x]/[ ] display) | utility | transform | `app.py` :: `_print_task_list` lines 61-68 (self) | self-analog |
| `test_app.py` (refactor + extend) | test | CRUD | `test_app.py` :: `TestDeleteTask` lines 81-109 | exact |

---

## Pattern Assignments

### `app.py` :: `complete_task` (new function, CRUD update)

**Analog:** `app.py` :: `delete_task` (lines 42-58) — identical role (find-by-name) and identical bool-return contract.

**Docstring pattern** (copy from `delete_task`, lines 43-52):

```python
def delete_task(tasks: list, name: str) -> bool:
    """從清單中刪除指定名稱的任務。

    Args:
        tasks: 現有的任務清單（就地修改）。
        name:  要刪除的任務名稱。

    Returns:
        True  — 成功刪除。
        False — 清單中不存在此名稱，不做任何修改。
    """
```

`complete_task` must follow the **same Google-style docstring structure** in Traditional Chinese, with `Args:`, `Returns:` sections, and a two-line `Returns:` block explaining True/False separately.

**Bool return + "why" comment pattern** (lines 53-58):

```python
    if name in tasks:
        tasks.remove(name)
        return True

    # 不存在就靜默回傳 False，讓呼叫端決定怎麼處理
    return False
```

`complete_task` replicates this exact bool-return shape. The `if name in tasks` lookup changes to a dict-aware scan (see Shared Patterns § Dict Lookup below), but the `return True` / `return False` positions and the "why" comment convention are identical.

**In-place mutation pattern** (contrast: `add_task` line 26):

```python
    tasks.append(name.strip())
```

`delete_task` calls `tasks.remove(name)` (line 54). `complete_task` must mutate the found dict in-place: `task["done"] = True`. All three functions receive `tasks` as the first parameter and mutate it directly — no return of the list, no copy.

**Idempotent / no-op pattern** (D-04 decision):
`complete_task` returns `True` even when the task is already `done=True`. The "why" comment should explain: already-completed is a no-op, not an error — consistent with the codebase's pattern of "silent sentinel, let caller decide."

---

### `app.py` :: `add_task` (refactor, CRUD create)

**Analog:** `app.py` :: `add_task` lines 12-27 (self — minimal change).

**Guard clause pattern** (lines 22-24 — copy verbatim, no change needed):

```python
    # 空名稱沒有意義，早點拋錯比讓垃圾資料留在清單裡好
    if not name or not name.strip():
        raise ValueError(f"任務名稱不可為空字串：{name!r}")
```

This guard is **unchanged**. It runs before the append, exactly as now.

**Append line** (line 26 — the only line that changes):

```python
    # before (str model):
    tasks.append(name.strip())

    # after (dict model):
    tasks.append({"name": name.strip(), "done": False})
```

`done` defaults to `False` (D-01, Claude's Discretion). No other logic changes.

**Docstring** (lines 12-24): signature becomes `add_task(tasks: list, name: str) -> None` — unchanged. Only the `Args: tasks` description should note `list[dict]` if desired, but the return annotation stays `-> None`.

---

### `app.py` :: `list_tasks` (refactor, CRUD read)

**Analog:** `app.py` :: `list_tasks` lines 29-39 (self — zero logic change).

**Copy pattern** (lines 37-39 — copy verbatim):

```python
    # 回傳 copy 而非原 list，防止外部意外修改內部狀態
    return list(tasks)
```

`list(tasks)` produces a **shallow copy** of the list. After the refactor, each element is a dict; the shallow copy means the caller gets a new list but the dict objects inside are shared. Per D-05, `list_tasks` is not responsible for deep-copying the dicts — it only prevents list-level mutation. The comment and the one-liner are kept as-is.

---

### `app.py` :: `delete_task` (refactor, CRUD delete)

**Analog:** `app.py` :: `delete_task` lines 42-58 (self — lookup logic changes, contract identical).

**Before (str lookup, lines 53-58):**

```python
    if name in tasks:
        tasks.remove(name)
        return True

    # 不存在就靜默回傳 False，讓呼叫端決定怎麼處理
    return False
```

**After (dict lookup — new inner pattern to adopt):**
The `name in tasks` check no longer works once tasks are dicts. Replace with a linear scan:

```python
    for task in tasks:
        if task["name"] == name:
            tasks.remove(task)
            return True

    # 不存在就靜默回傳 False，讓呼叫端決定怎麼處理
    return False
```

`tasks.remove(task)` removes by object identity (the found dict), which is correct. The "why" comment on `return False` is kept verbatim.

---

### `app.py` :: `_print_task_list` (refactor, transform/display)

**Analog:** `app.py` :: `_print_task_list` lines 61-68 (self — loop body changes, structure identical).

**Before (str items, lines 65-68):**

```python
    for idx, task in enumerate(tasks, start=1):
        print(f"  {idx}. {task}")
```

**After (dict items, [x]/[ ] prefix per D-06):**

```python
    for idx, task in enumerate(tasks, start=1):
        marker = "[x]" if task["done"] else "[ ]"
        print(f"  {idx}. {marker} {task['name']}")
```

The `if not tasks:` guard (lines 63-65) is **unchanged**:

```python
    if not tasks:
        print("（目前沒有任何待辦任務）")
        return
```

---

### `test_app.py` (refactor + extend)

**Analog:** `test_app.py` :: `TestDeleteTask` lines 81-109 — same class-based structure, same pytest conventions, same True/False assertion style. `TestCompleteTask` mirrors this class directly.

**Module docstring + import pattern** (lines 1-11 — update import line):

```python
"""
test_app.py — app.py 的 pytest 測試套件。

涵蓋 add_task / list_tasks / delete_task / complete_task 四個函式的：
  - happy path（正常流程）
  - edge / error case（邊界與錯誤路徑）
"""

import pytest

from app import add_task, complete_task, delete_task, list_tasks
```

Add `complete_task` to the import list (alphabetical order within the import).

**Test class + method docstring pattern** (lines 81-109 — copy structure for TestCompleteTask):

```python
class TestDeleteTask:
    """測試 delete_task 函式。"""

    def test_delete_existing_task_returns_true(self):
        """刪除存在的任務應回傳 True 並移除該項目。"""
        tasks = ["報告", "開會"]
        result = delete_task(tasks, "報告")
        assert result is True
        assert tasks == ["開會"]

    def test_delete_nonexistent_task_returns_false(self):
        """刪除不存在的任務名稱應回傳 False，清單不變。"""
        tasks = ["現有任務"]
        result = delete_task(tasks, "不存在的任務")
        assert result is False
        assert tasks == ["現有任務"], "清單不應被修改"
```

`TestCompleteTask` follows the same shape:

- One method per behaviour (happy path, not-found returns False, idempotent/no-op returns True)
- `assert result is True` / `assert result is False` — use `is`, not `==`
- After-state assertion on `tasks` to prove mutation (or no mutation)
- Method docstring in Traditional Chinese explaining the expected behaviour

**Dict assertion style** (refactored existing tests):
After the refactor, existing assertions like `assert tasks == ["買牛奶"]` become dict-based. Copy this style:

```python
    # direct dict comparison — clearest form
    assert tasks == [{"name": "買牛奶", "done": False}]

    # or field access when only one field matters
    assert tasks[0]["name"] == "買牛奶"
    assert tasks[0]["done"] is False
```

Use the **direct dict comparison** form (`assert tasks == [{"name": ..., "done": ...}]`) for simplicity and readability, consistent with the existing `assert tasks == ["買牛奶"]` style.

---

## Shared Patterns

### Docstring Convention

**Source:** `app.py` lines 12-27, 29-39, 42-58
**Apply to:** `complete_task` (new), all refactored functions

```python
def example_task(tasks: list, name: str) -> bool:
    """一行摘要，說明函式做什麼。

    Args:
        tasks: 現有的任務清單（就地修改）。
        name:  目標任務名稱。

    Returns:
        True  — 操作成功。
        False — 找不到該名稱，不做任何修改。
    """
```

Rules: Google-style, Traditional Chinese, `Args:` + `Returns:` (+ `Raises:` only if function raises). Two-line `Returns:` block for bool functions.

### Bool Return Sentinel Pattern

**Source:** `app.py` lines 53-58
**Apply to:** `complete_task` (new), `delete_task` (refactored lookup)

```python
    # ... find logic ...
    return True

    # 不存在就靜默回傳 False，讓呼叫端決定怎麼處理
    return False
```

Rule: never raise when the item is simply not found; return `False` and let the caller decide. The "why" comment on the final `return False` is part of the pattern.

### Dict Lookup Pattern (new, replacing `in` operator)

**Source:** adapted from `delete_task` lines 53-55
**Apply to:** `delete_task` (refactored), `complete_task` (new)

```python
    for task in tasks:
        if task["name"] == name:
            # ... mutate or remove task ...
            return True
    return False
```

Rule: iterate with a `for` loop; compare `task["name"]`; act on the found dict object; `return True` inside the loop; `return False` after the loop.

### "Why" Inline Comment Style

**Source:** `app.py` lines 22-23, 38, 57
**Apply to:** all new and refactored functions

```python
# 空名稱沒有意義，早點拋錯比讓垃圾資料留在清單裡好
# 回傳 copy 而非原 list，防止外部意外修改內部狀態
# 不存在就靜默回傳 False，讓呼叫端決定怎麼處理
```

Rule: comments explain **why** a decision was made, not **what** the code does. New code follows the same pattern.

### Guard Clause (ValueError)

**Source:** `app.py` lines 22-24
**Apply to:** `add_task` (unchanged guard — keep verbatim)

```python
    if not name or not name.strip():
        raise ValueError(f"任務名稱不可為空字串：{name!r}")
```

Rule: validate at function entry, raise before any mutation, include the invalid value in the error message with `!r`.

---

## No Analog Found

None. All files have direct in-project analogs.

---

## Metadata

**Analog search scope:** `app.py` (125 lines), `test_app.py` (109 lines), `.planning/codebase/CONVENTIONS.md`
**Files scanned:** 3 source files + CONTEXT.md
**Pattern extraction date:** 2026-06-22
