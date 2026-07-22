<!-- GSD:project-start source:PROJECT.md -->
## Project

**待辦清單 CLI — 完成任務功能（demo-gsd-01-20260723）**

一個極簡的 in-memory 待辦清單 CLI（單檔 `app.py`，Python 3.14，pytest 測試），目前支援 add / list / delete / quit 四個指令。這次要在這個既有基底上新增第 4 個核心功能：**完成任務（complete_task）**，讓使用者能把任務標記為已完成並在清單上看到打勾標記。

**Core Value:** 使用者能標記任務完成、並在清單上一眼看到哪些做完了（✓）——完成狀態必須正確保存與呈現，不能跟刪除混為一談。

### Constraints

- **Tech stack**: Python 3 標準庫 + pytest — 既有專案無框架、無第三方依賴，維持極簡
- **Compatibility**: 既有 12 個測試必須繼續通過（允許因資料結構變更而調整斷言，但行為語意不可變）
- **編碼**: Windows 環境執行 Python 需 `PYTHONUTF8=1`（cp950 陷阱）
- **Conventions**: 繁體中文 docstring/註解、snake_case、依名稱操作的 CLI 介面風格
<!-- GSD:project-end -->

<!-- GSD:stack-start source:codebase/STACK.md -->
## Technology Stack

## Languages
- Python 3 (tested against Python 3.14.3 locally, `__pycache__` compiled as `cpython-314`) - all application code (`app.py`, `test_app.py`)
- Markdown - documentation only (`GSD-PRACTICE.md`)
## Runtime
- CPython 3.14 (no version pin file such as `.python-version` or `pyproject.toml` present; version is whatever `python`/`python3` resolves to on the machine)
- `pip` (invoked as `pip install pytest` per `GSD-PRACTICE.md`)
- Lockfile: missing (no `requirements.lock`, `Pipfile.lock`, or `poetry.lock`)
## Frameworks
- None - this is a plain-Python module with no web/CLI framework. `app.py` implements its own `input()`-based REPL loop in `main()`.
- pytest (version unpinned in `requirements.txt`) - used for all tests in `test_app.py`
- Test artifacts observed: `.pytest_cache/`, `__pycache__/test_app.cpython-314-pytest-8.4.2.pyc` indicate pytest 8.4.2 was the last version actually run
- None - no bundler, linter config, or build tool detected (no `ruff.toml`, `.flake8`, `pyproject.toml`, `setup.py`, or `setup.cfg`)
## Key Dependencies
- `pytest` (`requirements.txt`, unpinned version) - sole third-party dependency, required to run the test suite (`test_app.py`)
- None - no ORM, HTTP client, logging framework, or web server dependency exists in this codebase
## Configuration
- No `.env` file, environment variable usage, or config loader present in the code
- `GSD-PRACTICE.md` instructs setting `PYTHONUTF8=1` when invoking `pytest` on Windows (`PYTHONUTF8=1 pytest test_app.py -v`), to force UTF-8 mode for the Traditional Chinese strings/output used throughout `app.py`
- None - no build config files exist; the project runs directly via `python app.py` / `pytest test_app.py`
## Platform Requirements
- Windows 10 (per project CLAUDE.md and GSD-PRACTICE.md instructions), Git Bash used as the reference shell
- Python 3.x interpreter on PATH with `pip`
- `pytest` installed via `pip install pytest`
- Not applicable - this is a learning/practice CLI (`demo-gsd-01-20260723`) with no deployment target. It is a "brownfield" exercise base for practicing the GSD (Get Shit Done) planning workflow, not a shipped product.
<!-- GSD:stack-end -->

<!-- GSD:conventions-start source:CONVENTIONS.md -->
## Conventions

## Naming Patterns
- Single-word, lowercase module names: `app.py` (implementation), `test_app.py` (tests — `test_` prefix + module name, flat layout, not nested in a `tests/` directory).
- `snake_case` for all functions: `add_task`, `list_tasks`, `delete_task`, `main` (`app.py:12,27,39,65`).
- Private/internal helper functions prefixed with a single leading underscore: `_print_task_list` (`app.py:56`). Use this prefix for any new helper not part of the public module API.
- Function names are verbs describing the action performed on `tasks`: `add_task`, `delete_task`, `list_tasks`. A new `complete_task(tasks, name)` function should follow the same `<verb>_task(tasks, name)` signature shape.
- `snake_case` throughout: `tasks`, `name`, `raw`, `parts`, `cmd`, `found`, `idx`, `task`.
- Loop unpacking uses descriptive names, not single letters: `for idx, task in enumerate(tasks, start=1)` (`app.py:61`).
- Exception variables are named `exc` (`app.py:96`), not `e`.
- No custom classes or dataclasses exist yet. Domain data is represented as a plain `list` of `str` (each task is just a name string). Any change to a richer task representation (e.g. dict with `done` flag) is a structural decision to be made explicitly during `/gsd:discuss-phase` / `/gsd:plan-phase`, not assumed.
- Type hints are used on all function signatures using built-in generics: `tasks: list`, `name: str`, `-> None`, `-> list`, `-> bool` (`app.py:12,27,39`). No `typing.List`/`Optional` imports are used — prefer bare `list`/built-ins consistent with the existing style (this codebase targets Python 3.14, per `python --version` in the dev environment).
## Code Style
- No formatter config file present (no `pyproject.toml`, `.ruff.toml`, `black` config). Existing code is hand-formatted but consistent: 4-space indentation, blank line between top-level functions, no trailing whitespace.
- Line length is kept short and readable; no long lines observed (max ~90 chars in docstrings).
- No `.flake8`, `ruff.toml`, or lint config present in this practice repo. (Note: the parent project `CLAUDE.md` mentions a PostToolUse hook that runs `ruff check --fix + format` on `.py` edits when `ruff` is installed locally — this may apply at the editor/session level even though no config file lives in this repo.)
- If adding lint config for new code, match project-wide conventions: 4-space indent, snake_case, docstrings on every public function.
## Import Organization
- None. This is a single flat-file module with no package structure or path aliasing.
## Error Handling
- Domain validation errors raise built-in exceptions with a descriptive, formatted message: `raise ValueError(f"任務名稱不可為空字串：{name!r}")` (`app.py:23`). Use `!r` repr formatting when embedding the offending value in the message.
- Library/pure functions (`add_task`, `list_tasks`, `delete_task`) raise exceptions rather than printing — they are silent about I/O and only communicate failure via return value (`delete_task` returns `bool`) or exception (`add_task` raises `ValueError`).
- The CLI layer (`main()`) is the only place that catches exceptions and prints user-facing errors: `except ValueError as exc: print(f"錯誤：{exc}", file=sys.stderr)` (`app.py:96-97`). Errors are printed to `stderr`, not `stdout`.
- Keyboard/EOF interrupts are caught explicitly at the input loop boundary: `except (EOFError, KeyboardInterrupt):` (`app.py:75`) — always tuple multiple exception types together when they share the same handling.
- No bare `except:` clauses anywhere in the codebase — always catch specific exception types (this matches the global `code-quality.md` instruction to never use bare `except`).
- When adding `complete_task(tasks, name)`, follow existing conventions: return `bool` (True if found/marked, False if not found) to mirror `delete_task`, OR raise a specific exception only if the operation is genuinely invalid (not merely "not found" — "not found" should be a return value, as in `delete_task`).
## Logging
- Success/info messages print to `stdout` via plain `print()`.
- Error messages print to `stderr` via `print(..., file=sys.stderr)` (`app.py:97`).
- User-facing strings are all in Traditional Chinese (繁體中文), per project-wide convention. Any new user-facing string must also be in Traditional Chinese, matching e.g. `"已新增：{...}"`, `"錯誤：{...}"`, `"找不到任務：{...}"`.
## Comments
- Every function has a full docstring, even trivial ones. New functions must include a docstring with `Args:` and `Returns:`/`Raises:` sections following the existing Google-style format (see below).
- Inline comments are sparse and only used for a single "helper function" clarifier (`app.py:57`); logic is otherwise considered self-explanatory through naming.
- N/A (Python project). Docstring style is Google-style with Traditional Chinese prose:
- Module-level docstring at the top of `app.py` explains the module's purpose and its role as a "brownfield" learning base (`app.py:1-7`). Keep this pattern when the module's purpose changes (e.g. note when `complete_task` is added).
## Function Design
- Mutating functions that report success/failure return `bool` (`delete_task` → `True`/`False`), not `None` and not exceptions, when "not found" is an expected, non-exceptional outcome.
- Functions that must reject invalid input outright (e.g., empty name) raise `ValueError` instead of returning a sentinel.
- Functions returning collections return **copies**, not references, to avoid callers mutating internal state accidentally: `list_tasks` returns `list(tasks)` (`app.py:36`), a shallow copy.
## Module Design
<!-- GSD:conventions-end -->

<!-- GSD:architecture-start source:ARCHITECTURE.md -->
## Architecture

## System Overview
```text
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
- No classes, no modules beyond the single `app.py` file — flat procedural design
- Core business logic (`add_task`, `list_tasks`, `delete_task`) is pure/near-pure: takes `tasks` list as an explicit parameter, mutates or copies it, has no hidden global state
- The CLI loop (`main`) owns the only piece of state (`tasks: list`) and is the sole caller of the core functions
- No persistence layer — this is intentionally an in-memory brownfield teaching sample (see `GSD-PRACTICE.md`)
- Designed as a base for incremental extension: the codebase deliberately omits a `complete_task` function so learners can add it via the GSD workflow
## Layers
- Purpose: Read user input, parse commands, dispatch to core functions, print results/errors
- Location: `app.py:65-117` (`main()`), `app.py:56-62` (`_print_task_list`)
- Contains: `input()` loop, command parsing (`raw.split(maxsplit=1)`), `print()` calls, `try/except (EOFError, KeyboardInterrupt)`
- Depends on: Core Function Layer (calls `add_task`, `list_tasks` indirectly via `_print_task_list`, `delete_task`)
- Used by: Nothing (top-level entry point, invoked via `if __name__ == "__main__":`)
- Purpose: Encapsulate task list operations (add/list/delete) with validation
- Location: `app.py:12-53`
- Contains: Three public functions operating on a `tasks: list` parameter passed explicitly (dependency injection via argument, not global state)
- Depends on: Nothing external (stdlib only — no imports besides `sys`)
- Used by: CLI layer (`main`) and the test suite (`test_app.py`)
## Data Flow
### Primary Request Path (interactive CLI)
- Single mutable `tasks: list` created at the top of `main()` (`app.py:67`)
- No global variables; no class holding state — state lives only for the duration of the process (no file/DB persistence)
- Core functions mutate the list in place (`add_task`, `delete_task`) or return a copy (`list_tasks`) — callers never get a live reference to the internal list from `list_tasks`
## Key Abstractions
- Purpose: Represents a to-do item as a plain string (name only — no `done`/`id`/metadata fields)
- Examples: `tasks: list = []` populated with strings like `"買牛奶"`
- Pattern: Flat list of strings; no wrapper class or dict. This is the key design decision a `complete_task` feature must address (e.g., switch to `dict` with a `done` flag, or use a string prefix like `[x]` — left as an open decision per `GSD-PRACTICE.md`)
- Purpose: All three core functions take `tasks` as their first parameter rather than reading a module-level/global list
- Examples: `add_task(tasks, name)`, `list_tasks(tasks)`, `delete_task(tasks, name)`
- Pattern: Makes functions independently testable without needing to reset global state between tests (see `test_app.py`, each test creates its own local `tasks = []`)
## Entry Points
- Location: `app.py:116-117` (`if __name__ == "__main__": main()`)
- Triggers: Running `python app.py` (or `PYTHONUTF8=1 python app.py` per Windows conventions in this environment)
- Responsibilities: Starts the interactive REPL-style CLI loop
- Location: entire file, invoked via `pytest test_app.py -v`
- Triggers: Manual test runs during GSD verify-phase
- Responsibilities: Exercises `add_task`, `list_tasks`, `delete_task` with 12 test cases across `TestAddTask`, `TestListTasks`, `TestDeleteTask`
## Architectural Constraints
- **Threading:** Single-threaded, synchronous, blocking `input()` loop — no concurrency anywhere in the codebase
- **Global state:** None. The only mutable state (`tasks`) is a local variable scoped to `main()` — this is a deliberate constraint that keeps the core functions pure and testable
- **Circular imports:** Not applicable — single module, only imports `sys` from stdlib
- **Persistence:** None by design — this is an in-memory teaching sample (`GSD-PRACTICE.md` line 2: "brownfield 基底"). Any future `complete_task` implementation must decide how to represent "done" state without introducing a data store, unless a phase explicitly adds one
## Anti-Patterns
## Error Handling
- `add_task` raises `ValueError` for empty/whitespace-only names (`app.py:22-23`); `main()` catches this specific exception and prints to `stderr` (`app.py:96-97`)
- `delete_task` uses a return-value pattern (`True`/`False`) rather than exceptions for the "not found" case (`app.py:50-53`) — the CLI layer branches on the boolean to print success/failure messages (`app.py:106-110`)
- The CLI loop wraps `input()` in `try/except (EOFError, KeyboardInterrupt)` to allow graceful exit on Ctrl+D/Ctrl+C (`app.py:73-77`)
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
