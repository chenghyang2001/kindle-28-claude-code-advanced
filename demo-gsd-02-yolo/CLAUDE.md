<!-- GSD:project-start source:PROJECT.md -->
## Project

**極簡待辦清單 CLI（demo-gsd-02-yolo）**

一個用 Python 標準庫寫的極簡待辦清單 CLI，任務以純字串存放於記憶體 list。本次工作是在既有基礎上，以 GSD YOLO（autonomous）模式自動新增「標記完成」與「列出未完成」兩個功能，作為對照 demo-gsd-01 互動逐步模式的學習練習。

**Core Value:** 使用者能可靠地管理待辦任務（新增／列出／刪除，並新增完成／篩選未完成），且**不破壞既有的 6 個通過測試**。

### Constraints

- **Tech stack**: Python 3.x 標準庫 + pytest + ruff — 不引入額外依賴，保持極簡
- **Compatibility**: 既有 6 個測試不可弄壞 — 這是回歸防線
- **Scope**: demo／學習用，刻意維持最小可行 — 避免過度工程
<!-- GSD:project-end -->

<!-- GSD:stack-start source:codebase/STACK.md -->
## Technology Stack

## Languages
- Python 3.11.9 - All application and test code
## Runtime
- Python 3.11.9 (Windows Store edition, per global CLAUDE.md)
- pip (via `python -m pip`)
- Lockfile: not present (only `requirements.txt` with unpinned `pytest`)
## Frameworks
- None — `app.py` uses Python standard library only (`sys`)
- pytest 9.0.2 - Test runner; config file not present (no `pytest.ini` / `pyproject.toml` / `setup.cfg`)
- ruff 0.15.16 - Used for linting (`.ruff_cache/` present); no `ruff.toml` or `[tool.ruff]` section detected
- None — no build system, no virtual environment config committed
## Key Dependencies
- `pytest` (unpinned, resolves to 9.0.2 at runtime) — declared in `requirements.txt`
- None
## Configuration
- No `.env` files present
- No environment variables required by the application
- No build config files (`pyproject.toml`, `setup.cfg`, `setup.py` are all absent)
- `requirements.txt` — single line: `pytest`
## Platform Requirements
- Python 3.11+
- `python -m pip install pytest` to install test dependency
- Run tests: `python -m pytest test_app.py`
- Run CLI: `python app.py`
- Not applicable — this is a learning demo / CLI tool, not deployed
<!-- GSD:stack-end -->

<!-- GSD:conventions-start source:CONVENTIONS.md -->
## Conventions

## Naming Patterns
- `snake_case.py` — e.g., `app.py`, `test_app.py`
- Test files prefixed with `test_` to match pytest discovery rules
- `snake_case` verb-noun pattern: `add_task`, `list_tasks`, `delete_task`, `main`
- `snake_case` with descriptive names: `cleaned`, `current`, `command`
- Local loop variables: `index`, `task`
- Type-annotated where meaningful: `tasks: list = []`
- Built-in type annotations used directly: `list`, `str`, `bool`, `None`
- No custom type aliases or dataclasses — tasks are plain `str` in a `list`
## Code Style
- 4-space indentation throughout
- Ruff is present (`.ruff_cache/0.15.16/`) — no `pyproject.toml` or `ruff.toml` config file committed, so default Ruff rules apply
- No trailing whitespace observed
- Ruff (version 0.15.16 cache present) — enforced during development, no config file in repo
- No `.flake8`, `.pylintrc`, or `setup.cfg` present
## Import Organization
- None — flat single-module structure, direct imports
## Error Handling
- Functions raise typed exceptions (`ValueError`) for invalid input; callers catch and convert to user-visible messages
- `list.remove` `ValueError` is caught internally in `delete_task` and converted to a `bool` return value — no exception leaks to caller
- `main()` catches `EOFError` and `KeyboardInterrupt` from `input()` for graceful CLI exit
- Error messages printed to `sys.stderr` via `print(..., file=sys.stderr)`
- Do not use bare `except:` — all caught exceptions are named specifically
## Logging
- Normal output → `print(...)` to stdout
- Error/warning output → `print(..., file=sys.stderr)`
- No `logging` module used (appropriate for a CLI demo of this scale)
## Comments
- Comments explain *why*, not *what*: e.g., `# 先 strip 再判斷，避免「   」這類純空白被當成有效任務` (explains intent behind strip-before-check)
- Exception-handling branches include a one-line rationale comment: `# list.remove 找不到元素會拋 ValueError，這裡轉成 False 回報`
- `main()` catch block comment explains user-experience intent
- Module-level docstring: present in both `app.py` and `test_app.py`
- Function-level Google-style docstrings: all public functions have `Args:` / `Returns:` / `Raises:` sections
- Language: Traditional Chinese (繁體中文) for all docstrings and inline comments
- Test class docstrings: one-line Chinese description of what is under test
## Function Design
- Mutating functions return `None` (`add_task`)
- Read-only functions return a new copy (`list_tasks`)
- Boolean success/failure pattern for destructive operations (`delete_task` returns `bool`)
## Module Design
<!-- GSD:conventions-end -->

<!-- GSD:architecture-start source:ARCHITECTURE.md -->
## Architecture

## System Overview
```text
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
- All logic lives in one file (`app.py`); no modules, packages, or imports beyond stdlib `sys`
- State (`tasks: list`) is a plain Python list scoped to `main()`; functions receive it as a parameter (no global state)
- Functions do not own state — they mutate or read the list passed to them, making them easy to unit-test in isolation
## Layers
- Purpose: Human-readable input/output
- Location: `app.py:61–100` (the `main()` function)
- Contains: REPL loop, `input()` prompts, `print()` output, error messages to stderr
- Depends on: Core logic functions
- Used by: End user via `python app.py`
- Purpose: Data manipulation — add, read, delete tasks
- Location: `app.py:12–58`
- Contains: `add_task()`, `list_tasks()`, `delete_task()`
- Depends on: Nothing (no imports)
- Used by: `main()` and test suite
- Purpose: Holds all tasks for the session
- Location: `tasks: list` variable inside `main()` (`app.py:63`)
- Lifetime: Process lifetime; lost on exit (no persistence)
## Data Flow
### Add Task
### List Tasks
### Delete Task
- Single `tasks: list[str]` variable, passed explicitly to every function. No module-level globals, no class instances.
## Key Abstractions
- Purpose: A single todo item
- Representation: Plain `str` (no class, no ID field)
- Stored in: `list[str]` passed through function arguments
- Purpose: Dispatches user input to the correct core function
- Location: `app.py:65–96` (`while True` inside `main()`)
- Pattern: `if/elif` command dispatch on lowercased stripped input
## Entry Points
- Location: `app.py:99–100` (`if __name__ == "__main__": main()`)
- Triggers: `python app.py` from the command line
- Responsibilities: Creates the initial `tasks` list, runs the REPL until `quit` or EOF/Ctrl+C
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
### Do Not Use `list.remove()` Return Value as a Truth Test
## Error Handling
- `add_task()` raises `ValueError` for blank names; `main()` catches it and prints to stderr (`app.py:77–81`)
- `delete_task()` catches `ValueError` from `list.remove()` internally and returns `False` (`app.py:53–58`)
- `main()` catches `EOFError`/`KeyboardInterrupt` from `input()` for graceful Ctrl+D / Ctrl+C exit (`app.py:68–71`)
## Cross-Cutting Concerns
<!-- GSD:architecture-end -->

<!-- GSD:skills-start source:skills/ -->
## Project Skills

No project skills found. Add skills to any of: `.claude/skills/`, `.agents/skills/`, `.cursor/skills/`, `.github/skills/`, or `.codex/skills/` with a `SKILL.md` index file.
<!-- GSD:skills-end -->

<!-- GSD:workflow-start source:GSD defaults -->
## GSD Workflow Enforcement

Before using Edit, Write, or other file-changing tools, start work through a GSD command so planning artifacts and execution context stay in sync.

Use these entry points:
- `/gsd-quick` for small fixes, doc updates, and ad-hoc tasks
- `/gsd-debug` for investigation and bug fixing
- `/gsd-execute-phase` for planned phase work

Do not make direct repo edits outside a GSD workflow unless the user explicitly asks to bypass it.
<!-- GSD:workflow-end -->



<!-- GSD:profile-start -->
## Developer Profile

> Profile not yet configured. Run `/gsd-profile-user` to generate your developer profile.
> This section is managed by `generate-claude-profile` -- do not edit manually.
<!-- GSD:profile-end -->
