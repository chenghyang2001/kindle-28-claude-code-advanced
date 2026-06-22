# Technology Stack

**Analysis Date:** 2026-06-22

## Languages

**Primary:**

- Python 3.11.9 - All application logic and tests

## Runtime

**Environment:**

- Python 3.11.9 (Windows Store edition — installed via `PythonSoftwareFoundation.Python.3.11`)
- Packages installed at user-level: `C:\Users\B00332\AppData\Local\Packages\PythonSoftwareFoundation.Python.3.11_qbz5n2kfra8p0\LocalCache\local-packages\Python311\site-packages`

**Package Manager:**

- pip (bundled with Python 3.11)
- Lockfile: not present (only `requirements.txt` with a single unpinned dependency)

## Frameworks

**Core:**

- None — `app.py` uses Python stdlib only (`sys`)

**Testing:**

- pytest 9.0.2 — unit test runner for `test_app.py`

**Build/Dev:**

- Not applicable — no build step, no transpilation, no bundler

## Key Dependencies

**Critical:**

- `pytest` (unpinned, resolved to 9.0.2 at install time) — the only declared dependency; required to run `test_app.py`

**Transitive (pytest):**

- `colorama` — Windows terminal color support
- `iniconfig` — pytest config file parsing
- `packaging` — version comparison utilities
- `pluggy` — pytest plugin system
- `pygments` — syntax highlighting in tracebacks

**Infrastructure:**

- None — purely in-memory, no persistence layer

## Configuration

**Environment:**

- No `.env` file, no environment variables required
- On Windows: prefix test runs with `PYTHONUTF8=1` to force UTF-8 output encoding (system default is cp950)

**Build:**

- No build config files (no `setup.py`, `pyproject.toml`, `setup.cfg`, `tox.ini`, or `pytest.ini`)
- pytest discovers tests automatically by convention (`test_app.py` in project root)

## Platform Requirements

**Development:**

- Python 3.11+
- pip
- Windows 10 (current environment); no platform-specific code in `app.py` itself, but `PYTHONUTF8=1` is needed on Windows due to cp950 default encoding

**Production:**

- Not applicable — this is a GSD workflow practice project, not a deployed application
- Entry point: `python app.py` (interactive CLI loop via `main()`)
- Test entry point: `PYTHONUTF8=1 pytest test_app.py -v` (12 test cases, all in-memory)

---

*Stack analysis: 2026-06-22*
