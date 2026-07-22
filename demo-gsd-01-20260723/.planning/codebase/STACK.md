# Technology Stack

**Analysis Date:** 2026-07-22

## Languages

**Primary:**

- Python 3 (tested against Python 3.14.3 locally, `__pycache__` compiled as `cpython-314`) - all application code (`app.py`, `test_app.py`)

**Secondary:**

- Markdown - documentation only (`GSD-PRACTICE.md`)

## Runtime

**Environment:**

- CPython 3.14 (no version pin file such as `.python-version` or `pyproject.toml` present; version is whatever `python`/`python3` resolves to on the machine)

**Package Manager:**

- `pip` (invoked as `pip install pytest` per `GSD-PRACTICE.md`)
- Lockfile: missing (no `requirements.lock`, `Pipfile.lock`, or `poetry.lock`)

## Frameworks

**Core:**

- None - this is a plain-Python module with no web/CLI framework. `app.py` implements its own `input()`-based REPL loop in `main()`.

**Testing:**

- pytest (version unpinned in `requirements.txt`) - used for all tests in `test_app.py`
- Test artifacts observed: `.pytest_cache/`, `__pycache__/test_app.cpython-314-pytest-8.4.2.pyc` indicate pytest 8.4.2 was the last version actually run

**Build/Dev:**

- None - no bundler, linter config, or build tool detected (no `ruff.toml`, `.flake8`, `pyproject.toml`, `setup.py`, or `setup.cfg`)

## Key Dependencies

**Critical:**

- `pytest` (`requirements.txt`, unpinned version) - sole third-party dependency, required to run the test suite (`test_app.py`)

**Infrastructure:**

- None - no ORM, HTTP client, logging framework, or web server dependency exists in this codebase

## Configuration

**Environment:**

- No `.env` file, environment variable usage, or config loader present in the code
- `GSD-PRACTICE.md` instructs setting `PYTHONUTF8=1` when invoking `pytest` on Windows (`PYTHONUTF8=1 pytest test_app.py -v`), to force UTF-8 mode for the Traditional Chinese strings/output used throughout `app.py`

**Build:**

- None - no build config files exist; the project runs directly via `python app.py` / `pytest test_app.py`

## Platform Requirements

**Development:**

- Windows 10 (per project CLAUDE.md and GSD-PRACTICE.md instructions), Git Bash used as the reference shell
- Python 3.x interpreter on PATH with `pip`
- `pytest` installed via `pip install pytest`

**Production:**

- Not applicable - this is a learning/practice CLI (`demo-gsd-01-20260723`) with no deployment target. It is a "brownfield" exercise base for practicing the GSD (Get Shit Done) planning workflow, not a shipped product.

---

*Stack analysis: 2026-07-22*
