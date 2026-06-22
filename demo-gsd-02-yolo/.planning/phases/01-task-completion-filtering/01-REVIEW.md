---
phase: 01-task-completion-filtering
reviewed: 2026-06-22T06:30:00Z
depth: deep
files_reviewed: 2
files_reviewed_list:
  - demo-gsd-02-yolo/app.py
  - demo-gsd-02-yolo/test_app.py
findings:
  must_fix: 1
  nice_to_have: 4
  total: 5
status: CHANGES_REQUESTED
---

# Phase 01: Code Review Report

**Reviewed:** 2026-06-22
**Depth:** deep (cross-file — commits b8e2078 + d4e2150)
**Files Reviewed:** 2 (app.py, test_app.py)
**Overall Verdict:** CHANGES_REQUESTED

---

## Summary

Reviewed the dict-model refactor of `app.py` and the accompanying test file `test_app.py`.
The dict migration itself is correct — the old `list.remove(str)` pattern is gone, replaced by a clean `for/enumerate + pop` loop.
`complete_task` is correctly idempotent. `list_pending` returns new name strings, not shared references, so no mutation risk there.

One MUST_FIX: `list_tasks` returns a shallow copy that explicitly promises full state isolation in its docstring, but the promise is broken — dict elements are shared references. The accompanying test exercises list-level isolation only and silently passes despite the contract violation.

Four NICE_TO_HAVE items follow.

---

## MUST_FIX

### MF-01: `list_tasks` shallow copy does not deliver the documented isolation guarantee

**File:** `app.py:28-39` / `test_app.py:37-42`

**Issue:**
`list(tasks)` creates a new list object but the dict elements inside are shared references. The docstring explicitly states "回傳 copy 而非內部 reference，**避免呼叫端在外部直接竄改內部狀態**" — but this is false. Any caller who mutates a field on a returned dict silently corrupts the canonical task list:

```python
returned = list_tasks(tasks)
returned[0]["done"] = True   # mutates the original — confirmed by live test
assert tasks[0]["done"]      # True — internal state has been corrupted
```

The test `test_list_returns_copy` tests the wrong isolation level: it appends a new element to the returned list and checks `len(tasks) == 1`. That passes because list-level isolation is fine. But it does NOT test dict-element mutation, so the contract violation is invisible to the test suite.

**Fix (option A — deep copy, fulfil the docstring promise):**

```python
import copy

def list_tasks(tasks: list) -> list:
    return copy.deepcopy(tasks)
```

**Fix (option B — weaken the docstring to match reality):**

```python
def list_tasks(tasks: list) -> list:
    """回傳任務清單的淺層複本。

    保護外部對清單結構的修改（append / remove），但回傳的
    dict 元素與內部清單共享參考，請勿對其欄位做修改。
    """
    return list(tasks)
```

**Fix the test** (regardless of which option is chosen, the test should match intent):

```python
def test_list_returns_copy_dict_isolation(self):
    """竄改回傳元素的欄位不應影響內部清單。"""
    tasks = [{"name": "a", "done": False}]
    returned = list_tasks(tasks)
    returned[0]["done"] = True      # 嘗試污染
    assert tasks[0]["done"] is False  # 若 deepcopy 則通過；若 shallow copy 則此行揭露 bug
```

---

## NICE_TO_HAVE

### NT-01: `complete_task` docstring missing "first match only" caveat for duplicate names

**File:** `app.py:59-75`

**Issue:**
`delete_task` explicitly documents "刪除**第一個**符合名稱的任務", but `complete_task` has no equivalent note. When two tasks share the same name (one pending, one done), `complete_task` only completes the first matching task — leaving the second unchanged. This is the correct design but it is undocumented, inconsistent with the care taken in `delete_task`.

Confirmed:

```python
tasks = [{"name": "a", "done": False}, {"name": "a", "done": False}]
complete_task(tasks, "a")
# tasks == [{"name": "a", "done": True}, {"name": "a", "done": False}]
```

**Fix:** Add one line to the docstring:

```
若清單中有同名的多個任務，只標記第一個符合的任務（與 delete_task 一致）。
```

---

### NT-02: `add_task(tasks, None)` raises `AttributeError`, not `ValueError`

**File:** `app.py:11-25`

**Issue:**
The docstring's `Raises` section lists only `ValueError: 當 name 去除前後空白後為空`. But passing `None` causes `None.strip()` to raise `AttributeError: 'NoneType' object has no attribute 'strip'` — a different, undocumented exception type.

Confirmed:

```python
add_task([], None)  # raises AttributeError, not ValueError
```

**Fix:** Add a type guard before `strip()`:

```python
if not isinstance(name, str):
    raise ValueError(f"任務名稱必須是字串，收到 {type(name).__name__}")
cleaned = name.strip()
```

Or extend the Raises docstring to document `AttributeError` for non-string input. The type guard is cleaner.

---

### NT-03: `complete_task` and `list_pending` are not wired into `main()`

**File:** `app.py:90-129`

**Issue:**
`main()` only supports `add / list / delete / quit`. The two newly implemented functions (`complete_task`, `list_pending`) have no CLI entry points, making them unreachable from the running program. The docstring for `main()` accurately reflects this ("支援 add / list / delete / quit 四指令"), but it means Phase 1's deliverables cannot be exercised end-to-end via the CLI.

This is acceptable if the intent was library-layer functions only (unit-tested), but worth noting as a gap for a demo where you'd want to see the feature work live.

**Fix:** Add two command branches (example):

```python
elif command == "complete":
    name = input("要完成的任務名稱：").strip()
    if complete_task(tasks, name):
        print(f"已完成：{name}")
    else:
        print(f"找不到任務：{name}", file=sys.stderr)
elif command == "pending":
    pending = list_pending(tasks)
    if not pending:
        print("（沒有待辦任務）")
    else:
        for index, task_name in enumerate(pending, start=1):
            print(f"{index}. {task_name}")
```

---

### NT-04: `TestListPending` missing empty-list test case

**File:** `test_app.py:83-94`

**Issue:**
`TestListPending` covers "全部未完成" and "部分完成" but not the empty list edge case. `list_pending([])` should return `[]` — this is trivially correct in the implementation, but the test suite's own comment ("happy path、邊界與冪等性") implies edge cases are intended to be covered.

**Fix:** Add one test:

```python
def test_list_pending_empty_tasks(self):
    """空清單應回傳空清單。"""
    assert list_pending([]) == []
```

---

## Checklist Against Specific Questions

| 問題 | 結果 |
|------|------|
| `delete_task` dict model 正確？ | 正確 — `for/enumerate + pop` 取代舊 `.remove(str)` |
| `complete_task` 冪等？ | 正確 — 已完成再次呼叫仍回傳 True |
| `list_pending` 有無 alias 或 mutate 內部狀態？ | 安全 — 回傳新建的 `list[str]`，與內部 dict 無共享參考 |
| docstring / type hint 與 dict model 一致？ | 大致一致，但 `list_tasks` 的隔離保證聲明超過實作（見 MF-01） |
| 靜默失敗？ | `add_task(None)` 引發非文件化的 `AttributeError`（見 NT-02） |
| 重複名稱 / 大小寫敏感 | 一致地 first-match；大小寫敏感，行為合理但 `complete_task` 未文件化 |

---

_Reviewed: 2026-06-22_
_Reviewer: Claude (adversarial code-reviewer)_
_Depth: deep_
