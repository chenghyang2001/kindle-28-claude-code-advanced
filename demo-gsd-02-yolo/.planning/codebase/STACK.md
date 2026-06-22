# Technology Stack

**Analysis Date:** 2026-06-22

## Languages

**Primary:**

- Python 3.11.9 - All application and test code

## Runtime

**Environment:**

- Python 3.11.9 (Windows Store edition, per global CLAUDE.md)

**Package Manager:**

- pip (via `python -m pip`)
- Lockfile: not present (only `requirements.txt` with unpinned `pytest`)

## Frameworks

**Core:**

- None — `app.py` uses Python standard library only (`sys`)

**Testing:**

- pytest 9.0.2 - Test runner; config file not present (no `pytest.ini` / `pyproject.toml` / `setup.cfg`)

**Linting:**

- ruff 0.15.16 - Used for linting (`.ruff_cache/` present); no `ruff.toml` or `[tool.ruff]` section detected

**Build/Dev:**

- None — no build system, no virtual environment config committed

## Key Dependencies

**Critical:**

- `pytest` (unpinned, resolves to 9.0.2 at runtime) — declared in `requirements.txt`

**Infrastructure:**

- None

## Configuration

**Environment:**

- No `.env` files present
- No environment variables required by the application

**Build:**

- No build config files (`pyproject.toml`, `setup.cfg`, `setup.py` are all absent)
- `requirements.txt` — single line: `pytest`

## Platform Requirements

**Development:**

- Python 3.11+
- `python -m pip install pytest` to install test dependency
- Run tests: `python -m pytest test_app.py`
- Run CLI: `python app.py`

**Production:**

- Not applicable — this is a learning demo / CLI tool, not deployed

---

*Stack analysis: 2026-06-22*
