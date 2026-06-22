<!-- refreshed: 2026-06-22 -->
# Architecture

**Analysis Date:** 2026-06-22

## System Overview

```text
┌──────────────────────────────────────────────────────────┐
│                  CLI Entry Point                          │
│         `app.py` — main() REPL loop                      │
└──────────────────┬───────────────────────────────────────┘
                   │ calls
                   ▼
┌──────────────────────────────────────────────────────────┐
│              Core Business Logic                         │
│  add_task()   list_tasks()   delete_task()               │
│                  `app.py`                                │
└──────────────────┬───────────────────────────────────────┘
                   │ operates on
                   ▼
┌──────────────────────────────────────────────────────────┐
│              In-Memory State                             │
│  tasks: list[str]  (local variable inside main())        │
└──────────────────────────────────────────────────────────┘
```

## Component Responsibilities

| Component | Responsibility | File |
|-----------|----------------|------|
| `main()` | REPL loop — reads stdin, dispatches to core functions, formats stdout | `app.py:61` |
| `add_task()` | Validates and appends a task string to the shared list | `app.py:12` |
| `list_tasks()` | Returns a shallow copy of the task list | `app.py:29` |
| `delete_task()` | Removes first matching task; returns bool success | `app.py:43` |
| `TestAddTask` | pytest tests for add_task | `test_app.py:12` |
| `TestListTasks` | pytest tests for list_tasks | `test_app.py:29` |
| `TestDeleteTask` | pytest tests for delete_task | `test_app.py:45` |

## Pattern Overview

**Overall:** Single-module procedural CLI with in-memory state.

**Key Characteristics:**

- All logic lives in one file (`app.py`); no modules, packages, or imports beyond stdlib `sys`
- State (`tasks: list`) is a plain Python list scoped to `main()`; functions receive it as a parameter (no global state)
- Functions do not own state — they mutate or read the list passed to them, making them easy to unit-test in isolation

## Layers

**Presentation Layer:**

- Purpose: Human-readable input/output
- Location: `app.py:61–100` (the `main()` function)
- Contains: REPL loop, `input()` prompts, `print()` output, error messages to stderr
- Depends on: Core logic functions
- Used by: End user via `python app.py`

**Core Logic Layer:**

- Purpose: Data manipulation — add, read, delete tasks
- Location: `app.py:12–58`
- Contains: `add_task()`, `list_tasks()`, `delete_task()`
- Depends on: Nothing (no imports)
- Used by: `main()` and test suite

**State:**

- Purpose: Holds all tasks for the session
- Location: `tasks: list` variable inside `main()` (`app.py:63`)
- Lifetime: Process lifetime; lost on exit (no persistence)

## Data Flow

### Add Task

1. User types `add` at the prompt → `main()` reads command (`app.py:67`)
2. `main()` prompts for task name → reads `name` from stdin (`app.py:76`)
3. `add_task(tasks, name)` strips whitespace, validates non-empty, appends to `tasks` (`app.py:23–26`)
4. `main()` prints confirmation or error to stdout/stderr (`app.py:79–81`)

### List Tasks

1. User types `list` → `main()` calls `list_tasks(tasks)` (`app.py:83`)
2. `list_tasks()` returns a shallow copy (`app.py:40`)
3. `main()` iterates and prints each task (`app.py:87–88`)

### Delete Task

1. User types `delete` → `main()` prompts for name (`app.py:90`)
2. `delete_task(tasks, name)` calls `list.remove()`; returns `True` on success, `False` if not found (`app.py:53–58`)
3. `main()` prints result (`app.py:91–94`)

**State Management:**

- Single `tasks: list[str]` variable, passed explicitly to every function. No module-level globals, no class instances.

## Key Abstractions

**Task:**

- Purpose: A single todo item
- Representation: Plain `str` (no class, no ID field)
- Stored in: `list[str]` passed through function arguments

**REPL Loop:**

- Purpose: Dispatches user input to the correct core function
- Location: `app.py:65–96` (`while True` inside `main()`)
- Pattern: `if/elif` command dispatch on lowercased stripped input

## Entry Points

**CLI Entry Point:**

- Location: `app.py:99–100` (`if __name__ == "__main__": main()`)
- Triggers: `python app.py` from the command line
- Responsibilities: Creates the initial `tasks` list, runs the REPL until `quit` or EOF/Ctrl+C

**Test Entry Point:**

- Location: `test_app.py`
- Triggers: `pytest` (no `main` guard needed; pytest discovers classes)
- Responsibilities: Exercises `add_task`, `list_tasks`, `delete_task` in isolation with fresh `list` per test

## Architectural Constraints

- **Threading:** Single-threaded; blocking `input()` calls — no concurrency
- **Global state:** None — `tasks` is always a local variable passed as a parameter
- **Persistence:** None — all data is lost when the process exits
- **Circular imports:** Not applicable (single module)

## Anti-Patterns

### Do Not Access `tasks` Directly from Outside `main()`

**What happens:** In some scripts, tests reach into a global `tasks` variable.
**Why it's wrong:** This module has no global `tasks`; functions accept it as a parameter to stay testable.
**Do this instead:** Pass a fresh `list` to each function in tests, exactly as `test_app.py` does (`test_app.py:17`, `test_app.py:34`).

### Do Not Use `list.remove()` Return Value as a Truth Test

**What happens:** `list.remove()` returns `None`, not a bool.
**Why it's wrong:** A caller checking its return value gets `None`, which is always falsy.
**Do this instead:** Use `delete_task()` (`app.py:43`), which catches the `ValueError` and returns an explicit `bool`.

## Error Handling

**Strategy:** Validate at the boundary; convert exceptions to user-visible messages in `main()`.

**Patterns:**

- `add_task()` raises `ValueError` for blank names; `main()` catches it and prints to stderr (`app.py:77–81`)
- `delete_task()` catches `ValueError` from `list.remove()` internally and returns `False` (`app.py:53–58`)
- `main()` catches `EOFError`/`KeyboardInterrupt` from `input()` for graceful Ctrl+D / Ctrl+C exit (`app.py:68–71`)

## Cross-Cutting Concerns

**Logging:** None — output goes to `print()` / `sys.stderr`
**Validation:** Input strip + empty-check in `add_task()` (`app.py:23–25`)
**Authentication:** Not applicable

---

*Architecture analysis: 2026-06-22*
