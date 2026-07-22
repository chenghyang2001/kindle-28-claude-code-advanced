# External Integrations

**Analysis Date:** 2026-07-22

## APIs & External Services

**None detected.**

- This codebase (`app.py`, `test_app.py`) contains no HTTP client calls, no SDK imports, and no references to any external API. It is a fully self-contained, in-memory command-line to-do list used as a GSD (Get Shit Done) practice exercise (see `GSD-PRACTICE.md`).

## Data Storage

**Databases:**

- None. Task data lives only in a Python `list` held in the `tasks` local variable inside `main()` (`app.py:67`). There is no persistence layer - all data is lost when the process exits.

**File Storage:**

- Local filesystem only, and only incidentally: `.pytest_cache/` and `__pycache__/` are tool-generated artifacts, not application data storage.

**Caching:**

- None.

## Authentication & Identity

**Auth Provider:**

- None - the CLI has no concept of users, sessions, or authentication. `main()` in `app.py` runs an anonymous, single-user, single-process REPL loop.

## Monitoring & Observability

**Error Tracking:**

- None. Errors are surfaced via `print(..., file=sys.stderr)` in `app.py` (e.g. line 97 for `ValueError` on empty task name) - no external error tracking service (e.g. Sentry) is integrated.

**Logs:**

- None - no logging framework (`logging` module, structured logging, etc.) is used. All output goes to stdout/stderr via `print()`.

## CI/CD & Deployment

**Hosting:**

- None - not a deployed application.

**CI Pipeline:**

- None detected - no `.github/workflows/`, no other CI config files found in this project directory.

## Environment Configuration

**Required env vars:**

- None required by the application code itself.
- `PYTHONUTF8=1` is a recommended (not required-by-code) environment variable documented in `GSD-PRACTICE.md` for correctly running `pytest test_app.py -v` with UTF-8/Traditional Chinese output on Windows.

**Secrets location:**

- Not applicable - no secrets, API keys, or credentials are used anywhere in this codebase.

## Webhooks & Callbacks

**Incoming:**

- None.

**Outgoing:**

- None.

---

*Integration audit: 2026-07-22*
