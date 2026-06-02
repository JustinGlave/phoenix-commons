# Phoenix Master Tool — Tests Workflow Failure Report

> **Status:** ✅ FIXED. Tests workflow green across all 3 matrix legs; family `ci` workflow remained green.
> **Date:** 2026-06-02.
> **Repo:** `JustinGlave/phoenix-master-tool`.
> **Scope:** CI-only single-file fix.

---

## 1. Failed run identified

| Run | Workflow | Trigger | Result | Duration |
|-----|----------|---------|--------|----------|
| `26799986306` | **Tests** | push (`gitignore: ignore .venv…` commit `2fa78ec`) | ❌ failure | 9s |
| (also failed) | Tests | v1.1.1 commit `e6eefa1` (`26704711936`) | ❌ failure | 10s |
| (first failure) | Tests | Wave 8a merge `631dbe8` (`26495876875`) | ❌ failure | 10s |

**Failure onset:** the Tests workflow was green through 2026-05-20 (`CHANGELOG: ISO date…`, pre-retrofit) and started failing at the **Wave 8a merge** (2026-05-27) — the first commit where `updater.py` began importing `phoenix_commons`. The fast ~10s failures (vs the previously-green ~10s passes) are a setup/import failure, not a slow test failure.

The family **`ci`** workflow (windows-latest, added at Wave 8a B1 with `submodules: recursive` + `pip install -r requirements.txt`) was **green** the whole time — it already initializes the submodule and installs commons. Only the preserved legacy `Tests` workflow (ubuntu matrix) was failing.

---

## 2. Root cause

First real error line (identical across all 3 matrix legs):

```
ERROR: test_updater (unittest.loader._FailedTest.test_updater)
ImportError: Failed to import test module: test_updater
ModuleNotFoundError: No module named 'phoenix_commons'
FAILED (errors=1)
##[error]Process completed with exit code 1.
```

Chain:
- `tests/test_updater.py` imports `from updater import _parse_version, _ps_single_quote`
- `updater.py` (post-Wave-8a-B3 hybrid facade) imports `from phoenix_commons.updater import …`
- The legacy `Tests` workflow checked out with `submodules: false` (confirmed in the run log) and ran `python -m unittest discover` with **no dependency install and no submodule** → `phoenix_commons` not importable
- `test_validation.py` tests passed; only `test_updater` failed → confirms a setup/import failure, **not** a real test-logic regression

This is exactly the predicted cause: the old `test.yml` predates the commons submodule and was never updated to initialize it.

---

## 3. Files changed

| File | Change |
|------|--------|
| `.github/workflows/test.yml` | +9 lines (CI-only) |

**No source, no `version.py`, no `requirements*`, no `installer.iss`, no `updater.py`, no tags, no releases touched.**

---

## 4. Exact fix

Two minimal additions to `test.yml` — and **only** `test.yml`:

1. **Checkout the submodule:**
   ```yaml
   - uses: actions/checkout@v4
     with:
       submodules: recursive
   ```

2. **Expose commons on PYTHONPATH for the unittest step:**
   ```yaml
   - name: Run validation + updater unit tests
     run: python -m unittest discover -s tests -v
     env:
       PYTHONPATH: commons/src
   ```

### Why `PYTHONPATH` rather than `pip install`

- `phoenix_commons/__init__.py` is the lightweight Phase-1 skeleton (exports only `__version__` — no eager widget/theme import).
- `phoenix_commons.updater.__init__` imports only `.client` + `.installer`, both pure stdlib (urllib / json / zipfile / subprocess) — **no PySide6 at import time**.
- `test_updater` only imports `_parse_version` / `_ps_single_quote` from `updater`.
- Therefore the import chain needs no PySide6. `PYTHONPATH=commons/src` makes `phoenix_commons` importable for the src-layout package **without** installing the heavy PySide6 stack.
- commons declares `PySide6>=6.5` as a hard dependency, so `pip install -e ./commons` would pull PySide6 on all 3 matrix legs — defeating the lightweight cross-version intent of this workflow. `PYTHONPATH` keeps each leg at ~6–10s.

The Python **3.10/3.11/3.12 matrix was preserved** — the logs proved a setup issue, not a version-support problem, so no matrix change was warranted.

Commit: `a0085eb` — *CI: initialize commons submodule in Tests workflow* (pushed to `main`).

---

## 5. Rerun result

Push of `a0085eb` triggered both workflows:

| Workflow | Run | Result | Detail |
|----------|-----|--------|--------|
| **Tests** | `26802837703` | ✅ **success** (13s) | `unittest (Python 3.10)` ✅ 6s · `unittest (Python 3.11)` ✅ 9s · `unittest (Python 3.12)` ✅ 10s |
| **ci** (family) | `26802837678` | ✅ **success** | remained green (windows-latest, Py3.12, commons import smoke + compileall + pytest) |

All 3 previously-failing matrix legs now pass. The family CI workflow stayed green. No new failures introduced.

---

## 6. Confirmation

- **No source changed** — only `.github/workflows/test.yml`.
- **No `version.py` changed** — still `1.1.1`.
- **No release assets changed** — the `v1.1.1` GitHub Release + its 2 assets untouched.
- **No tags changed** — `v1.1.1`, `v1.1.1-rc1`, `valvemaster-retrofit-v1.1.0-pre` all intact at their SHAs.
- **No GitHub Releases edited.**
- **No updater contract / installer / AppId / install-path change.**
- **No rebuild.**
- **No PCC work started.**

### Note on the other 3 family repos

This same legacy-`test.yml`-vs-submodule gap could exist in any tool that (a) kept a pre-retrofit `test.yml` and (b) has tests importing `phoenix_commons`:

- **Job Tracker** — has a single family `ci.yml` only (no legacy `test.yml`); its CI initializes submodules — **not affected**.
- **Phoenix CAD / Phoenix Checkout** — their CI history was green through the release; if either carries a legacy ubuntu `test.yml` with commons-importing tests, the same one-line `submodules: recursive` (+ `PYTHONPATH`) fix would apply. **Not failing today** (no failure email); flagged here only as a watch item, not an action.

---

## Verdict

**Tests workflow failure resolved with the smallest possible CI-only change.** Root cause was the predicted missing-submodule/commons-import in the preserved legacy `test.yml`; fixed by adding `submodules: recursive` + `PYTHONPATH=commons/src`. Both workflows green. No source, release, tag, or contract impact.
