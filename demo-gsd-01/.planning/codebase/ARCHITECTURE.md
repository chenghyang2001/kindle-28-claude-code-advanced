<!-- refreshed: 2026-06-22 -->
# Architecture

**Analysis Date:** 2026-06-22

## System Overview

```text
┌─────────────────────────────────────────────────────────────┐
│                   CLI Entry Point                           │
│   `app.py:main()`  — interactive REPL loop                  │
└────────────────────────┬────────────────────────────────────┘
                         │ parses user input
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                  Core Business Logic                        │
│   add_task()  `app.py:12`                                   │
│   list_tasks() `app.py:29`                                  │
│   delete_task() `app.py:42`                                 │
└────────────────────────┬────────────────────────────────────┘
                         │ mutates / reads
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                  In-Memory State                            │
│   `tasks: list`  — plain Python list, no persistence        │
└─────────────────────────────────────────────────────────────┘
```

## Component Responsibilities

| Component | Responsibility | File |
|-----------|----------------|------|
| `add_task` | Validate and append a task name to the list | `app.py:12` |
| `list_tasks` | Return a shallow copy of the task list | `app.py:29` |
| `delete_task` | Remove the first matching task name; return success flag | `app.py:42` |
| `_print_task_list` | Format and print the task list to stdout | `app.py:61` |
| `main` | Interactive REPL — parse commands, dispatch to core functions | `app.py:71` |
| `TestAddTask` | pytest class covering add_task happy + edge + error paths | `test_app.py:18` |
| `TestListTasks` | pytest class covering list_tasks return-copy behaviour | `test_app.py:57` |
| `TestDeleteTask` | pytest class covering delete_task True/False return + list mutation | `test_app.py:81` |

## Pattern Overview

**Overall:** Procedural single-module with pass-by-reference state

**Key Characteristics:**

- All core functions accept the `tasks` list as their first argument — no global state, no class instance
- State lives entirely in the caller (`main()` owns the `tasks: list` variable)
- Core functions are pure-ish: `add_task` and `delete_task` mutate in place; `list_tasks` returns a copy and never mutates
- CLI layer is thin: it only parses text, calls a core function, and prints results

## Layers

**Core Logic Layer:**

- Purpose: Implement task management rules (validation, mutation, read)
- Location: `app.py:12–58`
- Contains: `add_task`, `list_tasks`, `delete_task`
- Depends on: Nothing (no imports beyond `sys`)
- Used by: CLI layer (`main`), test layer (`test_app.py`)

**Presentation / CLI Layer:**

- Purpose: Accept user input, format output, run the interactive loop
- Location: `app.py:61–125`
- Contains: `_print_task_list`, `main`
- Depends on: Core logic layer functions
- Used by: End user via `python app.py`

**Test Layer:**

- Purpose: Verify core function behaviour with isolated unit tests
- Location: `test_app.py`
- Contains: `TestAddTask`, `TestListTasks`, `TestDeleteTask` (12 test cases)
- Depends on: Core logic layer only (imports `add_task`, `list_tasks`, `delete_task`)
- Used by: pytest runner (`pytest test_app.py`)

## Data Flow

### CLI Request Path

1. User types a command line at the prompt (`> add 買牛奶`) (`app.py:81`)
2. `main()` strips and splits the input into `cmd` + optional argument (`app.py:90–91`)
3. Dispatch branch (if/elif) calls the appropriate core function (`app.py:93–121`)
4. Core function mutates or reads `tasks` in place (`app.py:12–58`)
5. `main()` prints success/error message or calls `_print_task_list` (`app.py:103–118`)

### Test Path

1. pytest discovers `TestAddTask`, `TestListTasks`, `TestDeleteTask` in `test_app.py`
2. Each test method creates a fresh `tasks = []` locally — no shared state between tests
3. Imports and calls core functions directly, asserts return values and list state

**State Management:**

- `tasks` is a plain `list[str]` created in `main()` at startup
- Lives only for the duration of the process (no persistence, no file I/O, no database)
- Each test method instantiates its own isolated list — no shared fixture state

## Key Abstractions

**Task list (`tasks: list`):**

- Purpose: Sole data store — an ordered collection of task name strings
- Examples: passed into every core function as first argument
- Pattern: Caller owns the list; core functions operate on it by reference

**Command dispatch in `main()`:**

- Purpose: Map user-typed commands to core function calls
- Examples: `app.py:93–121`
- Pattern: `if/elif` chain on `cmd` string; unknown commands fall through to error message

## Entry Points

**Interactive CLI:**

- Location: `app.py:124–125` (`if __name__ == "__main__": main()`)
- Triggers: `python app.py` from the shell
- Responsibilities: Creates the `tasks` list, runs the REPL until `quit` or EOF/Ctrl-C

**Test runner:**

- Location: `test_app.py` (top-level, discovered by pytest)
- Triggers: `pytest test_app.py` or `PYTHONUTF8=1 pytest test_app.py -v`
- Responsibilities: Exercises all three core functions with 12 parameterised test cases

## Architectural Constraints

- **Threading:** Single-threaded; no concurrency, no async, no worker threads
- **Global state:** None — `tasks` list is local to `main()`; `sys` import used only for `sys.stderr`
- **Circular imports:** None (two files; `test_app.py` imports from `app.py`, never the reverse)
- **Persistence:** None — all state is lost when the process exits
- **Python version:** CPython 3.11 (confirmed by `__pycache__/app.cpython-311.pyc`)

## Anti-Patterns

### Extending `main()` to add a new command

**What happens:** Developer adds a new `elif cmd == "complete":` block directly inside `main()`'s dispatch chain without adding the corresponding core function and tests first.
**Why it's wrong:** Bypasses the core-logic / CLI separation; the new behaviour becomes untestable without running the full REPL loop.
**Do this instead:** Add the core function (e.g. `complete_task`) to `app.py:12–58`, add its tests to `test_app.py`, then wire the dispatch in `main()` — matching the pattern of `add_task`/`delete_task`.

### Mutating the list returned by `list_tasks`

**What happens:** Caller does `tasks = list_tasks(tasks); tasks.append(...)` expecting to change the real list.
**Why it's wrong:** `list_tasks` deliberately returns a copy (`return list(tasks)`) — mutations to the copy are silently discarded.
**Do this instead:** Call `add_task(tasks, name)` or `delete_task(tasks, name)` to mutate the canonical list directly.

## Error Handling

**Strategy:** Guard-clause validation in core functions; user-visible error messages in CLI layer

**Patterns:**

- `add_task` raises `ValueError` for empty/whitespace-only names; `main()` catches it and prints to `sys.stderr`
- `delete_task` returns `False` (not an exception) when the task is not found; `main()` prints a "not found" message
- `main()` catches `EOFError` and `KeyboardInterrupt` from `input()` for graceful exit

## Cross-Cutting Concerns

**Logging:** No logging framework — `print()` for user messages, `print(..., file=sys.stderr)` for errors
**Validation:** Input validated at the core-function boundary (`add_task` checks `name.strip()`)
**Authentication:** Not applicable (local CLI, no users)

---

*Architecture analysis: 2026-06-22*
