<!-- GSD:project-start source:PROJECT.md -->
## Project

**PROJECT: 待辦清單 CLI（任務狀態 + 持久化擴充）**

一個既有的極簡待辦清單 CLI（brownfield）。目前用 in-memory `list` 儲存純字串 task，
提供 add / list / delete 三個核心函式。本專案分兩個有先後關係的階段擴充它：
先讓任務有「完成狀態」，再讓任務能「存檔持久化」。

**Core Value:** 讓使用者不只記下待辦，還能**標記完成**並在**重開程式後保留**任務與完成狀態。
（這一個能力鏈是整個專案要驗證的重點。）
<!-- GSD:project-end -->

<!-- GSD:stack-start source:codebase/STACK.md -->
## Technology Stack

## Languages
- Python 3 - Entire application (`app.py`) and test suite (`test_app.py`). Uses modern type-hint syntax (`list`, `str`, `-> None`, `-> bool`) in function signatures.
- Not applicable (single-language project)
## Runtime
- CPython 3 (standard interpreter). No version pin file (`.python-version`, `runtime.txt`, `pyproject.toml`) detected.
- Standard library only for the application — sole import is `import sys` (`app.py:7`).
- pip (implied by `requirements.txt`)
- Lockfile: missing (no `requirements.lock`, `Pipfile.lock`, or `poetry.lock`)
## Frameworks
- None. The application is plain Python using only the standard library.
- pytest - Test runner and assertion framework. Imported in `test_app.py:6` (`import pytest`) and declared in `requirements.txt`. Uses `pytest.raises` for exception assertions and plain `assert` for value checks.
- None detected (no build step, no bundler, no linter config files present)
## Key Dependencies
- pytest (unpinned) - The only declared dependency in `requirements.txt`. Required for the test suite; not needed to run the app itself.
- None
## Configuration
- No environment variables consumed. No `.env`, config files, or settings module.
- No build configuration files.
## How It Runs
## Encoding / UTF-8 Notes
- Source files and tests contain Traditional Chinese string literals (e.g. `"買牛奶"`, `"task 名稱不可為空白"`). Files must be read/written as UTF-8.
- On Windows (system default cp950), prefix Python invocations with `PYTHONUTF8=1` to avoid encoding errors when the CLI prints or reads Chinese text, e.g. `PYTHONUTF8=1 python app.py`.
- Error messages are written to `sys.stderr` (`app.py:71`); normal output goes to stdout.
## Platform Requirements
- Python 3 + pip. Install test dependency with `pip install -r requirements.txt`.
- Not applicable. This is a local CLI learning starter with no deployment target.
<!-- GSD:stack-end -->

<!-- GSD:conventions-start source:CONVENTIONS.md -->
## Conventions

Conventions not yet established. Will populate as patterns emerge during development.
<!-- GSD:conventions-end -->

<!-- GSD:architecture-start source:ARCHITECTURE.md -->
## Architecture

## System Overview
```text
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
- Pure core functions take the data store (`tasks` list) as an explicit parameter — no global state, no hidden singletons.
- All user interaction (input/print/stderr) is confined to `main()`. The three core functions never touch I/O, which makes them directly unit-testable.
- The data model is a deliberately primitive `list[str]` — a task is just its name string, with no wrapper object or status field.
## Layers
- Purpose: Drive the interactive session, parse commands, format and print results/errors.
- Location: `main()` in `app.py:42-89`.
- Contains: REPL `while True` loop, command parsing (`raw.split(maxsplit=1)`), dispatch `if/elif` chain, exception handling.
- Depends on: the three core functions, `sys.stderr`, builtin `input`/`print`.
- Used by: the `__main__` guard (`app.py:91-92`).
- Purpose: Implement task operations on a supplied list.
- Location: `add_task` / `list_tasks` / `delete_task` in `app.py:10-39`.
- Contains: validation, mutation, copy-on-read logic.
- Depends on: nothing but the passed-in `list` argument.
- Used by: `main()` and the pytest suite.
- Purpose: Hold the tasks for the duration of one process run.
- Location: local variable `tasks` in `main()` (`app.py:44`).
- Note: In-memory only — no file, no database, no persistence between runs.
## Data Flow
### Primary Request Path (e.g. `add 買牛奶`)
### List Flow (`list`)
### Delete Flow (`delete <名稱>`)
- A single local `list[str]` in `main()`. State exists only while the process runs and is discarded on exit.
## Key Abstractions
- Purpose: Represents a to-do item.
- Current form: a plain `str` (the trimmed task name). No object, no ID, no completion flag.
- Examples: `app.py:18` (`tasks.append(name.strip())`).
## Entry Points
- Location: `if __name__ == "__main__": main()` (`app.py:91-92`).
- Triggers: `python app.py`.
- Responsibilities: start the REPL and own the task list.
## Error Handling
- `add_task` raises `ValueError` for `None`, empty, or whitespace-only names (`app.py:16-17`); `main()` catches it and reports to `sys.stderr` (`app.py:70-71`).
- `delete_task` does **not** raise when a task is missing — it returns `False`, letting the caller decide (`app.py:33`, `app.py:39`).
- `list_tasks` returns a shallow copy so external mutation cannot corrupt the internal store (`app.py:27`) — a defensive-copy / encapsulation guard.
- `main()` traps `EOFError` (piped input end → clean break, `app.py:52-55`) and `KeyboardInterrupt` (Ctrl+C → `已中斷`, `app.py:87-88`).
## Cross-Cutting Concerns
## Deliberately Minimal Brownfield Starter
- **Completion status** — tasks are bare strings with no done/pending flag. No `complete`/`done` command exists.
- **Persistence** — the list lives only in RAM; nothing is saved to disk or a database between runs.
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
