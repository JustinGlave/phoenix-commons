# Wave 8b B1 — Submodule + Requirements-Dev + CI Minor Edit Report

> **Status:** B1 committed on `phase-8b-job-tracker-retrofit`.
> **Commit:** `cc7acdb`.
> **Date:** 2026-05-27.

---

## 1. Early-open override

**Operator-approved early-open override: Wave 8b implementation began before the 2026-06-09 doctrinal cooldown floor** (computed from Wave 8a's 2026-05-26 merge per MIGRATION_RULES § Frequency limits) by explicit operator instruction on 2026-05-27. No unresolved technical blockers; all 12 kickoff decisions resolved in `WAVE_8B_KICKOFF_DECISION_RECORD.md`. Recorded in B1 commit message + this report + CLAUDE.md retrofit-state section.

Wave 8c (Phoenix Checkout) cooldown floor is recomputed from **Wave 8b merge date**, not from 2026-06-09.

---

## 2. Branch state

| Item | Value |
|------|-------|
| Branch | `phase-8b-job-tracker-retrofit` (new) |
| Branched from | `main` HEAD `0eaed43` (*CI: workflow name 'CI' -> 'ci' (N2)*) |
| Branch HEAD | `cc7acdb` |
| Working tree | clean |
| Push state | local only (push at B11 merge gate) |

---

## 3. Files changed

`git show --stat cc7acdb` — 6 files, +47 / -1.

| File | Change |
|------|--------|
| `.gitmodules` | new — submodule pointer (`path = commons`, `url = https://github.com/JustinGlave/phoenix-commons`) |
| `commons` | new (gitlink) — pinned at `ff2fb40` |
| `requirements-dev.txt` | new — pyinstaller 6.20.0 + pytest 8.3.4 + pytest-qt 4.4.0 |
| `requirements.txt` | modified — appended `-e ./commons` (runtime pins preserved) |
| `.github/workflows/ci.yml` | modified — minor edit (+2 steps) |
| `CLAUDE.md` | modified — prepended retrofit-state section |

Untouched:
  - `project_tracker_gui.py` (6,404 LOC monolith — B2-B5 will surgically retrofit)
  - `project_tracker_backend.py`, `financials_*.py`, `user_auth.py`, `generate_guide.py`, `updater.py`, `build.bat`, `installer.iss`, `version.py`, `ProjectTrackingTool.spec`, `phoenix_style.qss`
  - `starter_package/` (B7 will delete per Decision #2)
  - `tests/test_regressions.py` (regression baseline)

---

## 4. Submodule state

```
$ git submodule status
 ff2fb40cb93feb6d407b358d34b4e7fdf9fdd947 commons (heads/main)
```

Pin SHA `ff2fb40` is today's commons `main` HEAD (the Wave 8b kickoff docs commit). Same submodule pattern as Wave 8a B1.

---

## 5. Requirements changes

### `requirements.txt` (modified)

Runtime pins preserved verbatim. Appended:

```
# Commons consumption (editable submodule install per ADR-015).
# Added at Wave 8b B1 (2026-05-27).
-e ./commons
```

### `requirements-dev.txt` (new)

```
pyinstaller==6.20.0
pytest==8.3.4
pytest-qt==4.4.0
```

Matches family canon (Wave 8a B1 + canonical FROZEN_BUILD_BASELINE).

---

## 6. CI changes

`.github/workflows/ci.yml` edits — minor only, 2 new steps + 1 modified checkout:

| Edit | Site |
|------|------|
| Add `with: submodules: recursive` | checkout step |
| Convert single-line install to multi-line: add `pip install -r requirements-dev.txt` after existing `pip install -r requirements.txt` | install step |
| Add new step: `phoenix_commons import smoke` (`python -c "import phoenix_commons; print(...)"`) | new step between install + py_compile |

**Preserved verbatim:** workflow name, `on:` triggers (push to main / PR), `runs-on: windows-latest`, Python 3.12 setup-python, py_compile across 10 files, version-metadata check, import-check (6 modules with GUI-platform-plugin exclusion comment preserved), regression tests via `unittest discover -s tests`.

Total steps: 6 → 8.

---

## 7. Validation results

| Check | Result |
|-------|--------|
| Working tree clean pre-branch | ✅ on `main` `0eaed43` |
| Branch created | ✅ `phase-8b-job-tracker-retrofit` |
| Submodule add | ✅ pinned at `ff2fb40` |
| Submodule status | `ff2fb40 commons (heads/main)` ✅ |
| `phoenix_commons` import (sys.path-based smoke via local `.venv`) | `phoenix_commons 0.1.0` ✅ |
| `ci.yml` YAML parse | 1 job `lint`, 8 steps ✅ |
| Post-commit tree | clean on `phase-8b-job-tracker-retrofit` ✅ |

### Deferred to B10

Full `pip install -r requirements.txt -r requirements-dev.txt` from a clean Python 3.12 venv + frozen-build cycle deferred to B10 (the brief's `pytest` / source-mode validation gate runs at B9 — also deferred to that step).

---

## 8. Issues

None blocking. Two observations:

1. **Local existing `.venv/` Python version** — Job Tracker's pre-retrofit venv is operator-managed; B10 will use a dedicated Python 3.12 venv (per Wave 8a pattern) for the canonical frozen build.

2. **Pip resolver** — the runtime stack (`PySide6==6.10.2` + `openpyxl==3.1.5` + `pyxlsb==1.0.10` + `reportlab==4.4.10`) coexisting with `-e ./commons` (which only depends on PySide6) should not conflict; full resolver validation deferred to B10's clean-venv install.

---

## 9. Confirmation

- **No app logic changed.** `project_tracker_gui.py`, backend, financials, user_auth, generate_guide untouched.
- **No UI / theme changed.** `_EMBEDDED_QSS` and all widget classes preserved; `phoenix_style.qss` untouched.
- **No updater changed.** `updater.py` body unchanged; `expected_internal=True` contract preserved.
- **No `build.bat` changed.** B8 will harden it.
- **No `installer.iss` changed.** **AppId still NOT declared per Decision #8 hard rule** (preserves AppName-hashed upgrade detection for v1.6.0..v1.8.5 users).
- **No `version.py` changed.** Stays at `1.8.5` per Decision #1 tag-skip.
- **`starter_package/` untouched.** B7 will delete per Decision #2.
- **No production deployment.** No PyInstaller invocation, no frozen exe, no installer build, no GitHub Release.

Branch HEAD: `cc7acdb`. Ready for **B2 (paths facade)**.
