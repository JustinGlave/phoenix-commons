# Wave 8a B1 — Submodule + Requirements + CI Baseline Report

> **Status:** B1 committed on `phase-8a-valvemaster-retrofit`.
> **Commit:** `46012a6f607b4041aa8a20e5746f89130e111da5` (short `46012a6`).
> **Date:** 2026-05-26.
> **Target:** ValveMasterTool / Phoenix Master Tool.
> **Brief:** `WAVE_8A_IMPLEMENTATION_BRIEF.md` § 2 (B1 spec).

---

## 0. Operator-approved early-open override

**Operator-approved early-open override: Wave 8a implementation began before the 2026-06-02 cooldown floor by explicit operator instruction.**

Context:
  - Doctrinal cooldown floor was **2026-06-02** (14 days after Phase 3B's 2026-05-19 merge per `MIGRATION_RULES.md § Frequency limits`).
  - Today is **2026-05-26** — 7 days before the floor.
  - Decision #12 (approved 2026-05-22 in `WAVE_8A_KICKOFF_DECISION_RECORD.md` § 12) stated: *"No implementation before 2026-06-02."*
  - Operator issued explicit override 2026-05-26: *"I am explicitly overriding the Wave 8a cooldown floor today. There are no unresolved technical blockers or unanswered kickoff decisions. All 12 Wave 8a decisions are resolved. The implementation brief is complete. Repos are clean. I want to proceed now rather than wait until 2026-06-02."*
  - Pre-override safety check: agent stopped first, surfaced the calendar / decision-record contradiction, and required explicit override before proceeding. Operator confirmed.

Implication for downstream sequencing:
  - Wave 8b (Job Tracker / Project Tracking Tool) cooldown floor is still **14 days after Wave 8a merge** per MIGRATION_RULES § Frequency limits — the early-open of Wave 8a does NOT compress Wave 8b's cooldown. Wave 8b floor is computed from the **Wave 8a merge date**, not from 2026-06-02.
  - This override is recorded in the B1 commit message + here + in the future closure report.

---

## 1. Branch state

| Item | Value |
|------|-------|
| Branch | `phase-8a-valvemaster-retrofit` |
| Branched from | `main` HEAD `21ba5df` (*CHANGELOG: ISO date for v1.1.0 (N3 — Operational Convergence)*) |
| Branch HEAD | `46012a6` |
| Working tree | clean |
| Push state | local only (push of retrofit branch to origin happens at B9 merge gate per the canonical retrofit pattern; intermediate B-step pushes optional) |

---

## 2. Files added / modified

`git show --stat 46012a6` reports 6 files, +119 / -19 lines.

| File | Change | Purpose |
|------|--------|---------|
| `.gitmodules` | new | Submodule pointer (path `commons`, url `https://github.com/JustinGlave/phoenix-commons`) |
| `commons` | new (gitlink) | Submodule entry; SHA `d21d0fd0` (commons `main`) |
| `requirements.txt` | new | Runtime pins: PySide6 / PySide6_Addons / PySide6_Essentials / shiboken6 + `-e ./commons` |
| `requirements-dev.txt` | new | Dev/test pins: pyinstaller / pytest / pytest-qt |
| `.github/workflows/ci.yml` | new | Family-standard CI: windows / Py3.12 / commons-backed |
| `CLAUDE.md` | modified | Reconciled stale "requirements.txt was added during 2026-05-19 sprint" claim; retrofit-state section updated; CI section now documents both workflows |

Files **unchanged** (verified by absence from `git show --stat`):
  - `phoenix_master_pyside6.py` (main GUI module, ~3000+ LOC)
  - `phoenix_master_backend.py` (169 KB domain logic)
  - `inventory.py` (SharePoint-synced parts catalog)
  - `assets.py` (base64-embedded brand PNGs)
  - `phoenix_style.qss` (System A canonical palette)
  - `updater.py` (ADR-003 exe-only payload + legacy-name resolution)
  - `build.bat` (B6 will harden — not touched in B1)
  - `installer.iss` (AppId GUID `{A7F3C2D1-9B4E-4F6A-8C3D-1E5B7A9F2C4D}` preserved; not touched)
  - `version.py` (stays at `1.1.0`; Decision #1 tag-skip)
  - `ValveMasterTool.spec` (B6 will delete — not touched in B1)
  - `.github/workflows/test.yml` (preserved per Decision #3)
  - `tests/test_updater.py` + `tests/test_validation.py` (regression baseline — untouched)

---

## 3. Submodule state

```
$ git submodule status
 d21d0fd0fe8e1bb68b403845f14c2bfa70bc165f commons (heads/main)
```

```
$ cat .gitmodules
[submodule "commons"]
        path = commons
        url = https://github.com/JustinGlave/phoenix-commons
```

| Property | Value |
|----------|-------|
| Path | `commons/` |
| URL | `https://github.com/JustinGlave/phoenix-commons` |
| Pin SHA | `d21d0fd0` — *"Add Wave 8a implementation brief push report"* (today's commons `main` HEAD) |
| Branch tracked | `main` (no specific branch directive; submodules follow recorded SHA by default) |
| Initial status flag | none — initialised + populated by the `git submodule add` command |
| Working tree of submodule | clean, on `main` |

---

## 4. Requirements contents

### `requirements.txt`

```
PySide6==6.10.2
PySide6_Addons==6.10.2
PySide6_Essentials==6.10.2
shiboken6==6.10.2

# Commons consumption (editable submodule install per ADR-015).
-e ./commons
```

Plus header comments referencing the Phoenix Tools Unified Standard + Decision #2.

### `requirements-dev.txt`

```
pyinstaller==6.20.0
pytest==8.3.4
pytest-qt==4.4.0
```

Plus header comments referencing FROZEN_BUILD_BASELINE + Decision #2.

### Pinning rationale

All four runtime pins (`6.10.2`) match the family canon (Phoenix CAD / Phoenix Checkout / PCC). `pyinstaller==6.20.0` matches the FROZEN_BUILD_BASELINE pin proven S1-safe in the Phase 6 build-hardening experiments. `pytest-qt==4.4.0` allows pytest to drive Qt-aware tests via the `qtbot` fixture (B7 source-mode validation will exercise this).

---

## 5. CI shape

Two parallel workflows on the retrofit branch tip:

### `.github/workflows/test.yml` — **PRESERVED** (Decision #3)

| Property | Value |
|----------|-------|
| Name | `Tests` |
| OS | ubuntu-latest |
| Python | matrix 3.10 / 3.11 / 3.12 |
| Test runner | `python -m unittest discover -s tests -v` |
| Self-test | `run_baseline_debug_benchmark` |
| Triggers | push to main, PR to main, workflow_dispatch |
| Touched in B1 | ❌ no — preserved byte-for-byte per documented operator preference |

### `.github/workflows/ci.yml` — **NEW** (Decision #3)

| Property | Value |
|----------|-------|
| Name | `ci` |
| OS | windows-latest |
| Python | 3.12 |
| Submodules | `recursive` |
| Steps | 6 — Checkout / Set up Python / Install reqs+dev / `import phoenix_commons` smoke / `compileall` / `pytest` |
| Triggers | push to `main` or `phase-8a-valvemaster-retrofit`, PR to main, workflow_dispatch |
| Cache | pip |

Both workflows must pass on the retrofit branch tip before B9 merge.

### YAML sanity

```
$ python -c "import yaml; data=yaml.safe_load(open('.github/workflows/ci.yml','r',encoding='utf-8').read()); ..."
ci.yml YAML parse OK
  name: ci
  jobs: ['ci']
  steps: 6

$ python -c "import yaml; data=yaml.safe_load(open('.github/workflows/test.yml','r',encoding='utf-8').read()); ..."
test.yml YAML parse OK
  name: Tests
  jobs: ['unittest']
```

Both files syntactically valid. (Pyyaml emits a known cosmetic quirk for top-level `on:` parsing as boolean `True` — this is harmless and GitHub Actions handles it correctly. No fix needed.)

---

## 6. Validation results

| Check | Command | Result |
|-------|---------|--------|
| Working tree pre-staged | `git status` | clean on `main` before branch creation ✅ |
| Branch creation | `git checkout -b phase-8a-valvemaster-retrofit` | succeeded ✅ |
| Submodule add | `git submodule add https://github.com/JustinGlave/phoenix-commons commons` | succeeded; pinned at d21d0fd0 ✅ |
| Submodule status | `git submodule status` | `d21d0fd0 commons (heads/main)` ✅ |
| `compileall` | `python -m compileall -q .` | exit 0, no output (clean) ✅ |
| `phoenix_commons` import smoke (sys.path-based) | `python -c "import sys; sys.path.insert(0, 'commons/src'); import phoenix_commons; print(phoenix_commons.__version__)"` | `phoenix_commons 0.1.0` ✅ |
| `ci.yml` YAML parse | pyyaml `safe_load` | 1 job (`ci`), 6 steps ✅ |
| `test.yml` YAML parse | pyyaml `safe_load` | 1 job (`unittest`) ✅ |
| Final tree state | `git status` after commit | clean on `phase-8a-valvemaster-retrofit` ✅ |

### Deferred to B7 source-mode validation

  - `pip install -r requirements.txt -r requirements-dev.txt` (full -e ./commons editable install). The existing `.venv/` is Python 3.14 (per CLAUDE.md / pre-flight audit); the canonical build venv is 3.12. B7 will run the full pip install + pytest cycle from a fresh 3.12 venv. The B1 brief's *"pytest if dependencies are available"* hedge confirms this is the intended deferral.
  - `pytest -q tests/` (full test run). Deferred for the same reason.

---

## 7. Issues / observations

### None blocking. Three notes for the record:

1. **`pip install pyyaml`** transient install in the existing `.venv/` (used to parse the YAML for validation). pyyaml is NOT in `requirements.txt` or `requirements-dev.txt` — it remains a venv-only artifact for ad-hoc dev tooling. No source files reference it.

2. **`.venv/` is Python 3.14**, not the canonical 3.12. Per Decision #9 (default-accept: soft-warn at build.bat entry), B6 will add a soft-warn check. B7 source-mode validation should be run from a fresh 3.12 venv (operator action).

3. **`commons` submodule pinned at today's `d21d0fd0` commit** — this is the latest commons `main` (the WAVE_8A_IMPLEMENTATION_BRIEF_PUSH_REPORT.md commit). Subsequent B-steps consume from this pin. If commons advances during the retrofit, the pin can be bumped at any time via `cd commons && git pull && cd .. && git add commons && git commit`. No bump is required for B1-B9 success.

---

## 8. Confirmation

  - **No app logic changed.** Zero edits to `phoenix_master_pyside6.py`, `phoenix_master_backend.py`, `inventory.py`, `assets.py`, or any dialog module.
  - **No UI changed.** No widget code touched. No layout change. No QSS edit.
  - **No theme changed.** `phoenix_style.qss` unchanged. `_EMBEDDED_QSS` constant unchanged (will retire at B4).
  - **No updater changed.** `updater.py` unchanged. ADR-003 exe-only payload contract preserved (`expected_internal=False` semantics will be embedded at B3).
  - **No `build.bat` changed.** B6 will harden it (`--noupx` + stdlib excludes + `--collect-all phoenix_commons` + Step 0 full cleanup + commons preflight + soft-warn for non-3.12 venv).
  - **No `installer.iss` changed.** AppId GUID `{A7F3C2D1-9B4E-4F6A-8C3D-1E5B7A9F2C4D}` preserved byte-for-byte. `DefaultDirName={localappdata}\ATS Inc\PhoenixMasterTool` preserved.
  - **No `version.py` changed.** Stays at `__version__ = "1.1.0"`. Decision #1 — tag-skip (no version bump for facade-only retrofit).
  - **No `ValveMasterTool.spec` deleted yet.** B6 will delete it (dead-code; build.bat uses CLI flags exclusively).
  - **No production deployment.** No `pyinstaller` invocation. No frozen exe. No installer build. No GitHub Release. No tag pushed.
  - **No B2-B9 work.** Scope held strictly to B1 — submodule + requirements + CI baseline + CLAUDE.md reconcile.

---

## 9. Next step — B2: `paths.py` facade

When the operator signals B2 kickoff, execute per `WAVE_8A_IMPLEMENTATION_BRIEF.md` § 2 (B2):

| Item | Value |
|------|-------|
| Files to touch | `paths.py` (new, ≈ 8 lines re-exporting from `phoenix_commons.paths`) · `phoenix_master_pyside6.py` (1 import replacement at the previous `_resource_path` site) |
| Purpose | Smallest possible facade; proves submodule consumption end-to-end |
| Stop conditions | `_resource_path` is called from a site the audit missed; path behavior shifts |
| Expected visible change | None |

B2 should follow immediately after B1 in a single working session (mechanical surgical work).

---

## 10. End condition

  - ✅ B1 committed (`46012a6`) on `phase-8a-valvemaster-retrofit`
  - ✅ Branch ready for B2
  - ✅ Working tree clean
  - ✅ Operator-approved early-open override recorded
  - ❌ No paths facade (B2)
  - ❌ No updater facade (B3)
  - ❌ No theme facade (B4)
  - ❌ No widget retrofit (B5)
  - ❌ No build hardening (B6)
  - ❌ No source-mode validation run (B7)
  - ❌ No frozen build (B8)
  - ❌ No merge (B9)

---

*End of Wave 8a B1 report. Branch `phase-8a-valvemaster-retrofit` HEAD: `46012a6`. Ready for B2 on operator signal.*
