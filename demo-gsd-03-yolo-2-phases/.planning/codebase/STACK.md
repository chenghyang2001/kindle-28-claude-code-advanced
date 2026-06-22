# Technology Stack

**Analysis Date:** 2026-06-22

## Languages

**Primary:**

- Python 3 - Entire application (`app.py`) and test suite (`test_app.py`). Uses modern type-hint syntax (`list`, `str`, `-> None`, `-> bool`) in function signatures.

**Secondary:**

- Not applicable (single-language project)

## Runtime

**Environment:**

- CPython 3 (standard interpreter). No version pin file (`.python-version`, `runtime.txt`, `pyproject.toml`) detected.
- Standard library only for the application — sole import is `import sys` (`app.py:7`).

**Package Manager:**

- pip (implied by `requirements.txt`)
- Lockfile: missing (no `requirements.lock`, `Pipfile.lock`, or `poetry.lock`)

## Frameworks

**Core:**

- None. The application is plain Python using only the standard library.

**Testing:**

- pytest - Test runner and assertion framework. Imported in `test_app.py:6` (`import pytest`) and declared in `requirements.txt`. Uses `pytest.raises` for exception assertions and plain `assert` for value checks.

**Build/Dev:**

- None detected (no build step, no bundler, no linter config files present)

## Key Dependencies

**Critical:**

- pytest (unpinned) - The only declared dependency in `requirements.txt`. Required for the test suite; not needed to run the app itself.

**Infrastructure:**

- None

## Configuration

**Environment:**

- No environment variables consumed. No `.env`, config files, or settings module.

**Build:**

- No build configuration files.

## How It Runs

**Run the application:**

```bash
python app.py
```

Launches the interactive CLI loop (`main()`), guarded by `if __name__ == "__main__":` (`app.py:91-92`). Supported REPL commands: `add <名稱>`, `list`, `delete <名稱>`, `quit`. The loop also exits cleanly on EOF (piped input ends) and `Ctrl+C` (KeyboardInterrupt).

**Run the tests:**

```bash
pytest test_app.py
```

or simply `pytest` from the project root.

## Encoding / UTF-8 Notes

- Source files and tests contain Traditional Chinese string literals (e.g. `"買牛奶"`, `"task 名稱不可為空白"`). Files must be read/written as UTF-8.
- On Windows (system default cp950), prefix Python invocations with `PYTHONUTF8=1` to avoid encoding errors when the CLI prints or reads Chinese text, e.g. `PYTHONUTF8=1 python app.py`.
- Error messages are written to `sys.stderr` (`app.py:71`); normal output goes to stdout.

## Platform Requirements

**Development:**

- Python 3 + pip. Install test dependency with `pip install -r requirements.txt`.

**Production:**

- Not applicable. This is a local CLI learning starter with no deployment target.

---

*Stack analysis: 2026-06-22*
