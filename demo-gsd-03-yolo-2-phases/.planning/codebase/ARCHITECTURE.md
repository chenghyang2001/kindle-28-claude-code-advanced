<!-- refreshed: 2026-06-22 -->
# Architecture

**Analysis Date:** 2026-06-22

## System Overview

```text
┌─────────────────────────────────────────────────────────────┐
│                     I/O / Presentation                       │
│                     `app.py` main()                          │
│   stdin REPL loop · stdout printing · stderr errors          │
│   command parsing (add / list / delete / quit)               │
└───────────────────────────┬─────────────────────────────────┘
                            │ calls
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                   Pure Logic (core functions)                │
│   `app.py`  add_task() · list_tasks() · delete_task()        │
│   No printing, no input — operate on a passed-in list        │
└───────────────────────────┬─────────────────────────────────┘
                            │ mutates / reads
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                   Data Model (in-memory)                     │
│   tasks: list[str]   (created in main(), lives in RAM only)  │
└─────────────────────────────────────────────────────────────┘
```

## Component Responsibilities

| Component | Responsibility | File |
|-----------|----------------|------|
| `main()` | Interactive REPL: read line, parse command + arg, dispatch to core functions, format output, handle EOF/Ctrl+C | `app.py:42` |
| `add_task()` | Validate and append a task name to the list | `app.py:10` |
| `list_tasks()` | Return a defensive shallow copy of the list | `app.py:21` |
| `delete_task()` | Remove the first matching task, report success boolean | `app.py:30` |
| `tasks` (`list[str]`) | In-memory store of task names | `app.py:44` |

## Pattern Overview

**Overall:** Single-module script with a clean separation between **pure logic functions** and a thin **I/O driver** (`main()`).

**Key Characteristics:**

- Pure core functions take the data store (`tasks` list) as an explicit parameter — no global state, no hidden singletons.
- All user interaction (input/print/stderr) is confined to `main()`. The three core functions never touch I/O, which makes them directly unit-testable.
- The data model is a deliberately primitive `list[str]` — a task is just its name string, with no wrapper object or status field.

## Layers

**I/O / Presentation layer:**

- Purpose: Drive the interactive session, parse commands, format and print results/errors.
- Location: `main()` in `app.py:42-89`.
- Contains: REPL `while True` loop, command parsing (`raw.split(maxsplit=1)`), dispatch `if/elif` chain, exception handling.
- Depends on: the three core functions, `sys.stderr`, builtin `input`/`print`.
- Used by: the `__main__` guard (`app.py:91-92`).

**Pure logic layer:**

- Purpose: Implement task operations on a supplied list.
- Location: `add_task` / `list_tasks` / `delete_task` in `app.py:10-39`.
- Contains: validation, mutation, copy-on-read logic.
- Depends on: nothing but the passed-in `list` argument.
- Used by: `main()` and the pytest suite.

**Data layer:**

- Purpose: Hold the tasks for the duration of one process run.
- Location: local variable `tasks` in `main()` (`app.py:44`).
- Note: In-memory only — no file, no database, no persistence between runs.

## Data Flow

### Primary Request Path (e.g. `add 買牛奶`)

1. User types `add 買牛奶`; loop reads and strips it (`app.py:51`).
2. Parsed into `action="add"`, `arg="買牛奶"` (`app.py:59-61`).
3. Dispatch branch calls `add_task(tasks, arg)` (`app.py:68`).
4. `add_task` strips the name, validates non-empty, appends to `tasks` (`app.py:16-18`).
5. `main()` prints confirmation `已新增：...` (`app.py:69`); on empty name catches `ValueError` and prints to stderr (`app.py:70-71`).

### List Flow (`list`)

1. `main()` calls `list_tasks(tasks)` → receives a copy (`app.py:73`).
2. If empty, prints `（清單為空）`; otherwise enumerates `1. <task>` per line (`app.py:74-78`).

### Delete Flow (`delete <名稱>`)

1. `main()` calls `delete_task(tasks, arg)` (`app.py:80`).
2. `delete_task` strips the target and removes the first match, returning `True`/`False` (`app.py:35-39`).
3. `main()` prints `已刪除：...` or `找不到：...` accordingly (`app.py:81-83`).

**State Management:**

- A single local `list[str]` in `main()`. State exists only while the process runs and is discarded on exit.

## Key Abstractions

**Task:**

- Purpose: Represents a to-do item.
- Current form: a plain `str` (the trimmed task name). No object, no ID, no completion flag.
- Examples: `app.py:18` (`tasks.append(name.strip())`).

## Entry Points

**CLI:**

- Location: `if __name__ == "__main__": main()` (`app.py:91-92`).
- Triggers: `python app.py`.
- Responsibilities: start the REPL and own the task list.

## Error Handling

**Strategy:** Fail-validated at the boundary, tolerant on lookups.

**Patterns:**

- `add_task` raises `ValueError` for `None`, empty, or whitespace-only names (`app.py:16-17`); `main()` catches it and reports to `sys.stderr` (`app.py:70-71`).
- `delete_task` does **not** raise when a task is missing — it returns `False`, letting the caller decide (`app.py:33`, `app.py:39`).
- `list_tasks` returns a shallow copy so external mutation cannot corrupt the internal store (`app.py:27`) — a defensive-copy / encapsulation guard.
- `main()` traps `EOFError` (piped input end → clean break, `app.py:52-55`) and `KeyboardInterrupt` (Ctrl+C → `已中斷`, `app.py:87-88`).

## Cross-Cutting Concerns

**Logging:** None — uses `print` to stdout and `sys.stderr` for the single error path.
**Validation:** Name non-emptiness enforced in `add_task` only; all names are stripped before storage so `delete` comparisons match reliably.
**Authentication:** Not applicable.

## Deliberately Minimal Brownfield Starter

This module is an **intentional minimal starting point** for a GSD YOLO 2-phase exercise (see the module docstring, `app.py:1-6`). Two capabilities are **intentionally absent** and reserved as future extensions:

- **Completion status** — tasks are bare strings with no done/pending flag. No `complete`/`done` command exists.
- **Persistence** — the list lives only in RAM; nothing is saved to disk or a database between runs.

The docstring explicitly instructs not to implement these yet, because they are meant to be added later via two GSD-driven phases. Treat their absence as by-design, not as a defect.

---

*Architecture analysis: 2026-06-22*
