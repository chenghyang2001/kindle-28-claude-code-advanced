# Codebase Structure

**Analysis Date:** 2026-06-22

## Directory Layout

```
demo-gsd-03-yolo-2-phases/
├── app.py              # Application: 3 core functions + interactive CLI main()
├── test_app.py         # pytest tests for the 3 core functions
└── requirements.txt    # Single dependency: pytest
```

A 3-file flat project — no packages, subdirectories, or config files.

## Directory Purposes

**Project root (`demo-gsd-03-yolo-2-phases/`):**

- Purpose: Holds the entire to-do-list CLI starter.
- Contains: one application module, one test module, one requirements file.
- Key files: `app.py`, `test_app.py`, `requirements.txt`.

## Key File Locations

**Entry Points:**

- `app.py` (`main()` at line 42, guarded by `__main__` at lines 91-92): the runnable CLI.

**Core Logic:**

- `app.py` lines 10-39: the three pure functions.

**Configuration:**

- `requirements.txt`: declares `pytest` (the only dependency).

**Testing:**

- `test_app.py`: pytest suite covering the three core functions.

## Public Function Surface

All functions live in `app.py`.

| Signature | Purpose |
|-----------|---------|
| `add_task(tasks: list, name: str) -> None` | Append a stripped task name to `tasks`; raise `ValueError` if name is `None`/empty/whitespace. (`app.py:10`) |
| `list_tasks(tasks: list) -> list` | Return a shallow copy of `tasks` to protect internal storage from external mutation. (`app.py:21`) |
| `delete_task(tasks: list, name: str) -> bool` | Remove the first task matching the stripped name; return `True` if removed, `False` if not found. (`app.py:30`) |
| `main() -> None` | Interactive REPL loop dispatching `add`/`list`/`delete`/`quit`; handles EOF and Ctrl+C. (`app.py:42`) |

## Test Coverage Map

Tests in `test_app.py` are organized into one class per core function (3 classes, 6 test methods). `main()` is **not** covered (no I/O/REPL tests).

| Test class | Test method | Covers | Source |
|------------|-------------|--------|--------|
| `TestAddTask` | `test_add_happy_path` | `add_task` appends and strips whitespace (`"  買牛奶  "` → `"買牛奶"`) | `test_app.py:14` |
| `TestAddTask` | `test_add_empty_name_raises` | `add_task` raises `ValueError` for `""` and `"   "` | `test_app.py:20` |
| `TestListTasks` | `test_list_happy_path` | `list_tasks` returns matching contents | `test_app.py:32` |
| `TestListTasks` | `test_list_returns_copy` | `list_tasks` returns a copy; mutating the result does not affect the original | `test_app.py:37` |
| `TestDeleteTask` | `test_delete_happy_path` | `delete_task` removes an existing task and returns `True` | `test_app.py:48` |
| `TestDeleteTask` | `test_delete_non_existent_returns_false` | `delete_task` returns `False` and leaves the list unchanged when not found | `test_app.py:54` |

**Coverage gaps (by design — see ARCHITECTURE.md):** `main()` REPL behavior, command parsing, EOF/KeyboardInterrupt handling. No tests for completion-status or persistence (those features do not exist yet).

## Naming Conventions

**Files:**

- Lowercase with underscore: `app.py`, `test_app.py` (pytest auto-discovers `test_*.py`).

**Functions:**

- snake_case verb-noun: `add_task`, `list_tasks`, `delete_task`.

**Tests:**

- Test classes `Test<Subject>` (PascalCase); methods `test_<behavior>` (snake_case).

## Where to Add New Code

**New core function (e.g. mark-complete):**

- Implement as a pure function in `app.py` alongside the existing three, taking `tasks` as a parameter and avoiding I/O.
- Add a dispatch branch in `main()`'s `if/elif` chain.

**New tests:**

- Add a `Test<Subject>` class in `test_app.py` mirroring the existing structure (happy path + edge/error case).

**New dependency:**

- Append to `requirements.txt`.

---

*Structure analysis: 2026-06-22*
