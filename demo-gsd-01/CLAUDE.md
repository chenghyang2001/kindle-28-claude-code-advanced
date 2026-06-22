<!-- GSD:project-start source:PROJECT.md -->
## Project

**Todo CLI（demo-gsd-01）**

一個用來練習 GSD 完整流程的待辦清單 CLI（純 Python，無外部框架）。目前提供新增、列出、刪除三個任務操作；本次工作要為它加上「標記任務為完成」的能力。對象是學習 GSD 流程的開發者，App 本身只是載體，流程才是重點。

**Core Value:** 使用者能對待辦清單做基本的任務管理操作，且每個操作都有對應的測試保障行為正確。

### Constraints

- **Tech stack**：純 Python 標準庫，不引入外部套件 — 維持練習單純、可攜
- **Compatibility**：不可破壞既有 add/list/delete 的行為與測試 — 既有測試必須持續全綠
- **Testing**：新功能必須附測試（happy / edge / error）— 符合專案「測試與程式碼同時生成」原則
<!-- GSD:project-end -->

<!-- GSD:stack-start source:codebase/STACK.md -->
## Technology Stack

## Languages
- Python 3.11.9 - All application logic and tests
## Runtime
- Python 3.11.9 (Windows Store edition — installed via `PythonSoftwareFoundation.Python.3.11`)
- Packages installed at user-level: `C:\Users\B00332\AppData\Local\Packages\PythonSoftwareFoundation.Python.3.11_qbz5n2kfra8p0\LocalCache\local-packages\Python311\site-packages`
- pip (bundled with Python 3.11)
- Lockfile: not present (only `requirements.txt` with a single unpinned dependency)
## Frameworks
- None — `app.py` uses Python stdlib only (`sys`)
- pytest 9.0.2 — unit test runner for `test_app.py`
- Not applicable — no build step, no transpilation, no bundler
## Key Dependencies
- `pytest` (unpinned, resolved to 9.0.2 at install time) — the only declared dependency; required to run `test_app.py`
- `colorama` — Windows terminal color support
- `iniconfig` — pytest config file parsing
- `packaging` — version comparison utilities
- `pluggy` — pytest plugin system
- `pygments` — syntax highlighting in tracebacks
- None — purely in-memory, no persistence layer
## Configuration
- No `.env` file, no environment variables required
- On Windows: prefix test runs with `PYTHONUTF8=1` to force UTF-8 output encoding (system default is cp950)
- No build config files (no `setup.py`, `pyproject.toml`, `setup.cfg`, `tox.ini`, or `pytest.ini`)
- pytest discovers tests automatically by convention (`test_app.py` in project root)
## Platform Requirements
- Python 3.11+
- pip
- Windows 10 (current environment); no platform-specific code in `app.py` itself, but `PYTHONUTF8=1` is needed on Windows due to cp950 default encoding
- Not applicable — this is a GSD workflow practice project, not a deployed application
- Entry point: `python app.py` (interactive CLI loop via `main()`)
- Test entry point: `PYTHONUTF8=1 pytest test_app.py -v` (12 test cases, all in-memory)
<!-- GSD:stack-end -->

<!-- GSD:conventions-start source:CONVENTIONS.md -->
## Conventions

## Naming Patterns
- Lowercase with no hyphens: `app.py`, `test_app.py`
- Test file named `test_<module>.py` — mirrors the source module name
- `snake_case` for all public functions: `add_task`, `list_tasks`, `delete_task`
- Private/helper functions prefixed with underscore: `_print_task_list`
- CLI entry point named `main`
- `snake_case` for all local variables: `tasks`, `raw`, `parts`, `cmd`
- Descriptive names that reflect content: `tasks`, `name`, `result`, `found`
- Basic Python built-in type hints used on function parameters: `list`, `str`, `bool`
- Return types annotated on all public functions: `-> None`, `-> list`, `-> bool`
## Code Style
- 4-space indentation throughout
- No formatter config detected (no `.flake8`, `.pylintrc`, `pyproject.toml`, or `setup.cfg`)
- Blank lines between sections within functions for readability
- No linting config detected — no enforced rules beyond manual discipline
## Import Organization
- Absolute imports only
- No `from ... import *`
- Test file imports specific names: `from app import add_task, delete_task, list_tasks`
## Error Handling
- Raise `ValueError` for invalid input at function boundary (`add_task` with empty name)
- Guard clause pattern: validate early, raise before proceeding
- CLI layer catches `ValueError` and prints to `sys.stderr`, never crashes the loop
- `EOFError` and `KeyboardInterrupt` both caught in CLI loop for graceful exit
- Functions that cannot find a resource return a sentinel value (`False`) rather than raising
## Logging
- User-facing messages via `print()`
- Error messages directed to `sys.stderr` with Chinese prefix `錯誤：`
- No structured logging — appropriate for CLI scope
## Comments
- Explain **why**, not **what**: comments justify non-obvious decisions
- Document workarounds and trade-offs explicitly
- All public functions have Google-style docstrings in Traditional Chinese
- Sections used: one-line summary, `Args:`, `Returns:`, `Raises:` (where applicable)
- Private helpers have a single-line docstring
## Function Design
- Mutation functions (`add_task`, `delete_task`) signal outcome via return value or exception — never silently succeed on bad input
- Read functions (`list_tasks`) return copies, never the internal reference
## Module Design
- No explicit `__all__` — public API is implied by naming (no underscore prefix)
- Private helpers use `_` prefix
- Module is importable without side effects; CLI only runs via direct invocation
- All user-facing strings, docstrings, and comments are in Traditional Chinese
- Code identifiers are in English (snake_case)
<!-- GSD:conventions-end -->

<!-- GSD:architecture-start source:ARCHITECTURE.md -->
## Architecture

## System Overview
```text
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
- All core functions accept the `tasks` list as their first argument — no global state, no class instance
- State lives entirely in the caller (`main()` owns the `tasks: list` variable)
- Core functions are pure-ish: `add_task` and `delete_task` mutate in place; `list_tasks` returns a copy and never mutates
- CLI layer is thin: it only parses text, calls a core function, and prints results
## Layers
- Purpose: Implement task management rules (validation, mutation, read)
- Location: `app.py:12–58`
- Contains: `add_task`, `list_tasks`, `delete_task`
- Depends on: Nothing (no imports beyond `sys`)
- Used by: CLI layer (`main`), test layer (`test_app.py`)
- Purpose: Accept user input, format output, run the interactive loop
- Location: `app.py:61–125`
- Contains: `_print_task_list`, `main`
- Depends on: Core logic layer functions
- Used by: End user via `python app.py`
- Purpose: Verify core function behaviour with isolated unit tests
- Location: `test_app.py`
- Contains: `TestAddTask`, `TestListTasks`, `TestDeleteTask` (12 test cases)
- Depends on: Core logic layer only (imports `add_task`, `list_tasks`, `delete_task`)
- Used by: pytest runner (`pytest test_app.py`)
## Data Flow
### CLI Request Path
### Test Path
- `tasks` is a plain `list[str]` created in `main()` at startup
- Lives only for the duration of the process (no persistence, no file I/O, no database)
- Each test method instantiates its own isolated list — no shared fixture state
## Key Abstractions
- Purpose: Sole data store — an ordered collection of task name strings
- Examples: passed into every core function as first argument
- Pattern: Caller owns the list; core functions operate on it by reference
- Purpose: Map user-typed commands to core function calls
- Examples: `app.py:93–121`
- Pattern: `if/elif` chain on `cmd` string; unknown commands fall through to error message
## Entry Points
- Location: `app.py:124–125` (`if __name__ == "__main__": main()`)
- Triggers: `python app.py` from the shell
- Responsibilities: Creates the `tasks` list, runs the REPL until `quit` or EOF/Ctrl-C
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
### Mutating the list returned by `list_tasks`
## Error Handling
- `add_task` raises `ValueError` for empty/whitespace-only names; `main()` catches it and prints to `sys.stderr`
- `delete_task` returns `False` (not an exception) when the task is not found; `main()` prints a "not found" message
- `main()` catches `EOFError` and `KeyboardInterrupt` from `input()` for graceful exit
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
