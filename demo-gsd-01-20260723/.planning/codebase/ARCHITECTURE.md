<!-- refreshed: 2026-07-22 -->
# Architecture

**Analysis Date:** 2026-07-22

## System Overview

```text
┌─────────────────────────────────────────────────────────────┐
│                     Interactive CLI Loop                     │
│                  `app.py::main()` (line 65)                  │
├──────────────────┬──────────────────┬───────────────────────┤
│   add command    │   list command   │   delete command      │
│  parses "add X"  │  parses "list"   │  parses "delete X"    │
└────────┬─────────┴────────┬─────────┴──────────┬────────────┘
         │                  │                     │
         ▼                  ▼                     ▼
┌─────────────────────────────────────────────────────────────┐
│                    Core Function Layer                       │
│     `add_task()` / `list_tasks()` / `delete_task()`          │
│                  `app.py` (lines 12-53)                      │
└────────┬──────────────────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────────────────┐
│  In-memory `tasks: list` (local variable in `main()`)        │
│  No persistence — state is lost on process exit              │
└─────────────────────────────────────────────────────────────┘
```

## Component Responsibilities

| Component | Responsibility | File |
| ----------- | ---------------- | ------ |
| CLI loop (`main`) | Read stdin, dispatch to command handlers, print feedback | `app.py:65-117` |
| `add_task` | Validate and append a task name to the list | `app.py:12-24` |
| `list_tasks` | Return a shallow copy of the task list (read-only view) | `app.py:27-36` |
| `delete_task` | Remove first matching task name, report found/not-found | `app.py:39-53` |
| `_print_task_list` | Format and print a task list to stdout | `app.py:56-62` |
| Test suite | Verify core function behavior via pytest | `test_app.py` |

## Pattern Overview

**Overall:** Single-file procedural script with a functional core and an imperative CLI shell (a minimal "functional core, imperative shell" pattern).

**Key Characteristics:**

- No classes, no modules beyond the single `app.py` file — flat procedural design
- Core business logic (`add_task`, `list_tasks`, `delete_task`) is pure/near-pure: takes `tasks` list as an explicit parameter, mutates or copies it, has no hidden global state
- The CLI loop (`main`) owns the only piece of state (`tasks: list`) and is the sole caller of the core functions
- No persistence layer — this is intentionally an in-memory brownfield teaching sample (see `GSD-PRACTICE.md`)
- Designed as a base for incremental extension: the codebase deliberately omits a `complete_task` function so learners can add it via the GSD workflow

## Layers

**CLI / Presentation Layer:**

- Purpose: Read user input, parse commands, dispatch to core functions, print results/errors
- Location: `app.py:65-117` (`main()`), `app.py:56-62` (`_print_task_list`)
- Contains: `input()` loop, command parsing (`raw.split(maxsplit=1)`), `print()` calls, `try/except (EOFError, KeyboardInterrupt)`
- Depends on: Core Function Layer (calls `add_task`, `list_tasks` indirectly via `_print_task_list`, `delete_task`)
- Used by: Nothing (top-level entry point, invoked via `if __name__ == "__main__":`)

**Core Function Layer:**

- Purpose: Encapsulate task list operations (add/list/delete) with validation
- Location: `app.py:12-53`
- Contains: Three public functions operating on a `tasks: list` parameter passed explicitly (dependency injection via argument, not global state)
- Depends on: Nothing external (stdlib only — no imports besides `sys`)
- Used by: CLI layer (`main`) and the test suite (`test_app.py`)

## Data Flow

### Primary Request Path (interactive CLI)

1. User types a line at the `>` prompt; `main()` reads it via `input()` (`app.py:74`)
2. Line is split into `cmd` and optional argument via `raw.split(maxsplit=1)` (`app.py:82-83`)
3. `cmd` is matched against `add` / `list` / `delete` / `quit`; unmatched commands print an "unknown command" message (`app.py:85-113`)
4. Matched commands call the corresponding core function (`add_task`, `list_tasks` via `_print_task_list`, `delete_task`), passing the in-loop `tasks` list explicitly (`app.py:94, 100, 106`)
5. Result or error is printed back to stdout/stderr before looping to the next prompt

**State Management:**

- Single mutable `tasks: list` created at the top of `main()` (`app.py:67`)
- No global variables; no class holding state — state lives only for the duration of the process (no file/DB persistence)
- Core functions mutate the list in place (`add_task`, `delete_task`) or return a copy (`list_tasks`) — callers never get a live reference to the internal list from `list_tasks`

## Key Abstractions

**Task representation:**

- Purpose: Represents a to-do item as a plain string (name only — no `done`/`id`/metadata fields)
- Examples: `tasks: list = []` populated with strings like `"買牛奶"`
- Pattern: Flat list of strings; no wrapper class or dict. This is the key design decision a `complete_task` feature must address (e.g., switch to `dict` with a `done` flag, or use a string prefix like `[x]` — left as an open decision per `GSD-PRACTICE.md`)

**Explicit state passing:**

- Purpose: All three core functions take `tasks` as their first parameter rather than reading a module-level/global list
- Examples: `add_task(tasks, name)`, `list_tasks(tasks)`, `delete_task(tasks, name)`
- Pattern: Makes functions independently testable without needing to reset global state between tests (see `test_app.py`, each test creates its own local `tasks = []`)

## Entry Points

**`app.py` (script entry point):**

- Location: `app.py:116-117` (`if __name__ == "__main__": main()`)
- Triggers: Running `python app.py` (or `PYTHONUTF8=1 python app.py` per Windows conventions in this environment)
- Responsibilities: Starts the interactive REPL-style CLI loop

**`test_app.py` (test entry point):**

- Location: entire file, invoked via `pytest test_app.py -v`
- Triggers: Manual test runs during GSD verify-phase
- Responsibilities: Exercises `add_task`, `list_tasks`, `delete_task` with 12 test cases across `TestAddTask`, `TestListTasks`, `TestDeleteTask`

## Architectural Constraints

- **Threading:** Single-threaded, synchronous, blocking `input()` loop — no concurrency anywhere in the codebase
- **Global state:** None. The only mutable state (`tasks`) is a local variable scoped to `main()` — this is a deliberate constraint that keeps the core functions pure and testable
- **Circular imports:** Not applicable — single module, only imports `sys` from stdlib
- **Persistence:** None by design — this is an in-memory teaching sample (`GSD-PRACTICE.md` line 2: "brownfield 基底"). Any future `complete_task` implementation must decide how to represent "done" state without introducing a data store, unless a phase explicitly adds one

## Anti-Patterns

None observed. The codebase is intentionally minimal (117 lines) and does not exhibit typical anti-patterns (no god objects, no deep nesting, no duplicated logic). When extending with `complete_task`, avoid introducing a global `tasks` variable — follow the existing pattern of passing `tasks` as an explicit first parameter to preserve testability.

## Error Handling

**Strategy:** Fail-fast validation via exceptions in the core layer; the CLI layer catches and converts exceptions into user-facing messages.

**Patterns:**

- `add_task` raises `ValueError` for empty/whitespace-only names (`app.py:22-23`); `main()` catches this specific exception and prints to `stderr` (`app.py:96-97`)
- `delete_task` uses a return-value pattern (`True`/`False`) rather than exceptions for the "not found" case (`app.py:50-53`) — the CLI layer branches on the boolean to print success/failure messages (`app.py:106-110`)
- The CLI loop wraps `input()` in `try/except (EOFError, KeyboardInterrupt)` to allow graceful exit on Ctrl+D/Ctrl+C (`app.py:73-77`)

## Cross-Cutting Concerns

**Logging:** None — user-facing feedback is via `print()` to stdout, errors via `print(..., file=sys.stderr)`. No logging framework is used.

**Validation:** Minimal, scoped to `add_task` (rejects empty/whitespace name). No validation exists for `delete_task`'s input (empty string is treated as a normal, simply-not-found name).

**Authentication:** Not applicable — this is a local, single-user CLI with no auth concerns.

---

*Architecture analysis: 2026-07-22*
