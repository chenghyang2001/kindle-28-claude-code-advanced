# Coding Conventions

**Analysis Date:** 2026-06-22

## Naming Patterns

**Files:**

- Lowercase with no hyphens: `app.py`, `test_app.py`
- Test file named `test_<module>.py` — mirrors the source module name

**Functions:**

- `snake_case` for all public functions: `add_task`, `list_tasks`, `delete_task`
- Private/helper functions prefixed with underscore: `_print_task_list`
- CLI entry point named `main`

**Variables:**

- `snake_case` for all local variables: `tasks`, `raw`, `parts`, `cmd`
- Descriptive names that reflect content: `tasks`, `name`, `result`, `found`

**Types:**

- Basic Python built-in type hints used on function parameters: `list`, `str`, `bool`
- Return types annotated on all public functions: `-> None`, `-> list`, `-> bool`

## Code Style

**Formatting:**

- 4-space indentation throughout
- No formatter config detected (no `.flake8`, `.pylintrc`, `pyproject.toml`, or `setup.cfg`)
- Blank lines between sections within functions for readability

**Linting:**

- No linting config detected — no enforced rules beyond manual discipline

## Import Organization

**Order:**

1. Standard library (`import sys`)
2. Third-party (none in this project)
3. Local modules

**Pattern:**

- Absolute imports only
- No `from ... import *`
- Test file imports specific names: `from app import add_task, delete_task, list_tasks`

## Error Handling

**Patterns:**

- Raise `ValueError` for invalid input at function boundary (`add_task` with empty name)
- Guard clause pattern: validate early, raise before proceeding
- CLI layer catches `ValueError` and prints to `sys.stderr`, never crashes the loop
- `EOFError` and `KeyboardInterrupt` both caught in CLI loop for graceful exit
- Functions that cannot find a resource return a sentinel value (`False`) rather than raising

```python
# Guard clause — validate early, explain why
if not name or not name.strip():
    raise ValueError(f"任務名稱不可為空字串：{name!r}")
```

```python
# CLI error boundary — catch domain errors, print to stderr
try:
    add_task(tasks, parts[1])
except ValueError as exc:
    print(f"錯誤：{exc}", file=sys.stderr)
```

## Logging

**Framework:** `print()` / `sys.stderr` (no logging framework)

**Patterns:**

- User-facing messages via `print()`
- Error messages directed to `sys.stderr` with Chinese prefix `錯誤：`
- No structured logging — appropriate for CLI scope

## Comments

**When to Comment:**

- Explain **why**, not **what**: comments justify non-obvious decisions
- Document workarounds and trade-offs explicitly

**Examples from codebase:**

```python
# 空名稱沒有意義，早點拋錯比讓垃圾資料留在清單裡好
# 回傳 copy 而非原 list，防止外部意外修改內部狀態
# 不存在就靜默回傳 False，讓呼叫端決定怎麼處理
# 管道輸入結尾或使用者 Ctrl-C，優雅退出
```

**Docstrings:**

- All public functions have Google-style docstrings in Traditional Chinese
- Sections used: one-line summary, `Args:`, `Returns:`, `Raises:` (where applicable)
- Private helpers have a single-line docstring

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

## Function Design

**Size:** Functions are short (< 20 lines each) and single-purpose

**Parameters:** Functions receive the shared state (`tasks: list`) as an explicit parameter — no global state

**Return Values:**

- Mutation functions (`add_task`, `delete_task`) signal outcome via return value or exception — never silently succeed on bad input
- Read functions (`list_tasks`) return copies, never the internal reference

## Module Design

**Exports:**

- No explicit `__all__` — public API is implied by naming (no underscore prefix)
- Private helpers use `_` prefix

**Entry Point:**

```python
if __name__ == "__main__":
    main()
```

- Module is importable without side effects; CLI only runs via direct invocation

**Language:**

- All user-facing strings, docstrings, and comments are in Traditional Chinese
- Code identifiers are in English (snake_case)

---

*Convention analysis: 2026-06-22*
