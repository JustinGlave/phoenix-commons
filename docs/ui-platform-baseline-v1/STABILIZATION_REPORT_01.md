# STABILIZATION_REPORT_01.md

> First UI-Platform-stabilization deliverable. Merges the v1 baseline
> into `main`, adds governance + CI + smoke tests + ADR-014.
>
> Source-only, no migrations, no production-tool work, no builds.
>
> Captured 2026-05-16.

## 1. Status

**Passed.** All 6 user-spec steps completed, source-mode verification
green, three logical commits on `main`, pushed to origin. Architecture
stabilization remains in effect — no Phase 2.1 implementation started.

## 2. Merge commit

| Field | Value |
|-------|-------|
| Merge commit hash | `65966a4997934d39e0f70cd1902f954db52a07f1` (short `65966a4`) |
| Strategy | `ort` (Git default), `--no-ff` |
| Branches | `baseline-v1` (kept) → `main` |
| Files brought in | 14 baseline + report files under `docs/ui-platform-baseline-v1/`, plus the `phase-6c-frozen-exe-dogfood-plan.md`, `phase-6c-backup-report.md`, and earlier rollout history that was on `baseline-v1` but not on `main` |
| Pushed | `4049f7c..65966a4 main -> main` |

`baseline-v1` is **not deleted** per the spec.

## 3. Governance files added

| File | Lines | Role |
|------|-------|------|
| `LICENSE` | 78 | Internal-proprietary ATS license. Mirrors PCC. Phoenix-family apps explicitly authorised to embed + redistribute as part of their compiled binaries. |
| `SECURITY.md` | 91 | Internal reporting policy. Updater / paths / theme-loader called out as priority surfaces. Coordinates fix propagation to consuming apps via the Phase 7+ retrofit chain. |
| `CODE_OF_CONDUCT.md` | 66 | Contributor Covenant v2.1 adaptation, same shape as PCC's. |
| `README.md` | 161 (replaces previous 56-line "Phase 1 skeleton") | Reframes commons as the UI Platform; tables ownership; lists maturity / blockers / migration philosophy; cross-links to `docs/ui-platform-baseline-v1/`. |

All four authored with the same internal-proprietary posture
established in PCC.

## 4. CI workflow summary

**Path:** `.github/workflows/ci.yml`

| Property | Value |
|----------|-------|
| Trigger | `push` to `main`, any `pull_request` |
| Runner | `windows-latest` |
| Python | `3.12` (per ADR-014) |
| Install | `pip install -e .[test]` — editable install + pytest + pytest-qt |
| Step 1 | `python -m compileall -q .` |
| Step 2 | `pytest -q tests/` with `QT_QPA_PLATFORM=offscreen` |
| PyInstaller / Inno Setup / release publish | **Not present** — phoenix-commons is a library, packaging belongs to consuming apps |

The workflow is intentionally narrow. Closes `BLOCKERS.md §6` ("No CI
on phoenix-commons yet").

## 5. Smoke-test summary

**Files:** `tests/conftest.py` (new), `tests/test_smoke.py` (extended).

Existing tests preserved (8 tests covering Phase 1 package skeleton +
Phase 2 theme/widget API surface). Four new tests added:

| Test | Verifies |
|------|----------|
| `test_make_qss_non_empty` | Both the package-data `phoenix_style.qss` file AND the embedded fallback string are substantial (>5,000 chars each). Catches catastrophic truncation. |
| `test_component_instantiation` (qtbot) | All 10 public widgets construct under offscreen Qt without raising: `PrimaryButton`, `SecondaryButton`, `TertiaryButton`, `Panel`, `PageTitle`, `PageSubtitle`, `SectionTitle`, `HintLabel`, `PhoenixTable`, `UpdateBanner`. `UpdateBanner` requires `(current_version, latest_version)` positional args. |
| `test_no_scroll_instantiation` (qtbot) | The 4 `NoScroll*` widget family classes construct. |
| `test_canonical_token_names_present_in_qss` | The Phoenix System A canonical hex values (`#0a0e27`, `#dc2626`) appear in the QSS. Guards against accidental palette regression (e.g. someone copying ValveMaster's legacy gray "System B" colours). Will be upgraded to a direct `from phoenix_commons.theme.tokens import C` check when Phase 2.1 lands. |

`tests/conftest.py` sets `QT_QPA_PLATFORM=offscreen` at module-load
time so pytest-qt initialises Qt in headless mode. CI also sets the
env var at the job level — defensive double-set.

`pyproject.toml` `optional-dependencies.test` now includes
`pytest-qt>=4.4` so `qtbot` fixture is available.

## 6. Smoke-test output

```
$ python -m pip install -e .[test]
Successfully installed phoenix-commons-0.1.0

$ python -m compileall -q .
(exit 0)

$ QT_QPA_PLATFORM=offscreen python -m pytest -q tests/
.....................................                                    [100%]
37 passed in 0.15s
```

37 tests pass. Breakdown:

- **test_smoke.py** — 12 (8 pre-existing + 4 new)
- **test_paths.py** — pre-existing tests for `is_frozen` / `user_data_dir` / `resource_path`
- **test_updater.py** — pre-existing tests for `check_for_update` / `download_and_apply` / validator helpers

Runtime: 0.15 s. Suite stays well within the "lightweight + fast"
target.

## 7. ADR-014 summary

**Title:** Canonical platform Python version = 3.12

**Status:** Finalized.

**Decision:** The Phoenix UI Platform's canonical Python version is
**3.12**, enforced through:
- CI `setup-python` with `python-version: "3.12"` on Windows-latest
- Consuming-app build venvs (Phase 7+ retrofits)
- Production tools' `build.bat` pinning `py -3.12 -m venv .venv`

`pyproject.toml` keeps `requires-python = ">=3.10"` as a developer-
convenience floor; the *contract target* is 3.12.

**Rationale (5 factors):**

1. PyInstaller maturity on 3.12 wheels
2. PySide6 6.10.x validated on 3.12
3. GitHub Actions `setup-python@v5` first-tier support for 3.12
4. Production-tool deployments already pin 3.12
5. S1/AV signature was characterised against 3.12-based bootloaders

**Consequences:**
- App developers may experimentally use newer Python locally; commits
  must NOT introduce 3.13+ only syntax / stdlib.
- PCC currently uses 3.14 on Justin's laptop; its packaging pipeline
  must move to 3.12 before Phase 7 retrofits start. **This is a new
  open item** — added to §11 below.
- 3.14 only enters the platform contract when an explicit superseding
  ADR replaces this one.

Full text: `docs/ui-platform-baseline-v1/DECISIONS.md` § ADR-014.

## 8. Commits (in order)

```
$ git log --oneline -5

263aab3 Add ADR-014 — canonical platform Python version = 3.12       ← step 4
d7ca1a4 Add governance files + Python-3.12 CI + smoke tests           ← steps 2 + 3
65966a4 Merge Phoenix UI Platform Baseline v1                          ← step 1
417f860 Add remote bootstrap report — phoenix-commons connected to private GitHub
788757c Add baseline generation report — meta-document for the v1 baseline
```

Three logical commits per the user spec:

| # | Commit | Hash | What |
|---|--------|------|------|
| 1 | Baseline merge | `65966a4` | `--no-ff` merge of `baseline-v1` |
| 2 | Governance + CI | `d7ca1a4` | LICENSE, SECURITY.md, CODE_OF_CONDUCT.md, README.md, .github/workflows/ci.yml, tests/conftest.py + extended test_smoke.py, pyproject.toml test-extras |
| 3 | ADR-014 | `263aab3` | Canonical Python 3.12 ADR appended to DECISIONS.md |

## 9. Branch state — local

```
$ git branch -vv

* main                              263aab3 [origin/main] Add ADR-014 — canonical platform Python version = 3.12
  baseline-v1                       417f860 [origin/baseline-v1] Add remote bootstrap report …
  phase-2-theme-widgets             db1d8b4 Add Phase 2 report …
  phase-3-paths-updater             b2e7f79 Add Phase 3A report …
  phase-4-pyinstaller-compatibility ba3d2c4 [origin/phase-4-pyinstaller-compatibility] Phase 6C backup report …
```

| Branch | Tip | Tracks origin |
|--------|-----|---------------|
| `main` | `263aab3` | ✓ |
| `baseline-v1` | `417f860` (unchanged this turn) | ✓ |
| `phase-4-pyinstaller-compatibility` | `ba3d2c4` (unchanged this turn) | ✓ |
| `phase-2-theme-widgets`, `phase-3-paths-updater` | local-only ancestor refs (reachable through `phase-4-*`) | — |

## 10. Remote state — origin

```
$ git ls-remote --heads origin

788757c…  refs/heads/baseline-v1                          ← unchanged this turn
263aab3…  refs/heads/main                                 ← updated (3 new commits)
ba3d2c4…  refs/heads/phase-4-pyinstaller-compatibility    ← unchanged this turn
```

Push command run: `git push origin main` (`65966a4..263aab3`).

## 11. Blockers discovered / surfaced

| # | Blocker | Type | Status |
|---|---------|------|--------|
| Pre-existing #6 ("No CI on phoenix-commons") | Infrastructure | **✅ Resolved** by this stabilization (workflow added at `.github/workflows/ci.yml`). |
| **New** — PCC's local Python is 3.14, conflicts with ADR-014's 3.12 contract target | Coordination | **Open.** PCC's `build.bat` venv + `requirements.txt` need a 3.12 retarget before Phase 7. Tracked in `TODOS.md` "before migrations" (to be added in a future commit) and ADR-014's "Consequences" row. |
| Other 6 blockers from BLOCKERS.md | unchanged | All still in effect. AV chain (1-4), commons distribution (5), same-disk backups (7) all unchanged by this stabilization. |

The S1/AV chain blocker (BLOCKERS.md §1) remains the single gating
issue for all frozen-exe phases. Today's work is fully AV-independent.

## 12. Confirmation — no migrations / builds / retrofits occurred

- ❌ **No app code modified** (zero edits to PCC, Job Tracker,
  Phoenix CAD, Phoenix Checkout, ValveMaster source).
- ❌ **No commons source code modified** (zero edits under
  `src/phoenix_commons/`).
- ❌ **No `build.bat` / PyInstaller / Inno Setup / updater
  download/apply / `gh release`** invocations.
- ❌ **No rollout phases started.**
- ❌ **No migrations started.**
- ❌ **No retrofits started.**
- ❌ **No icon-infrastructure / packaging-implementation /
  build-verification / AV-workaround work attempted.**
- ❌ **Phase 2.1 (token formalization) NOT started.**

Operations performed this turn:

```
git checkout main
git merge --no-ff baseline-v1 -m "Merge Phoenix UI Platform Baseline v1"
git push origin main
(Write) LICENSE / SECURITY.md / CODE_OF_CONDUCT.md / README.md
(Write) .github/workflows/ci.yml / tests/conftest.py
(Edit)  tests/test_smoke.py / pyproject.toml /
        docs/ui-platform-baseline-v1/DECISIONS.md
python -m pip install -e .[test]
python -m compileall -q .
QT_QPA_PLATFORM=offscreen python -m pytest -q tests/
git add … && git commit … (×2 logical commits)
git push origin main
(Write) docs/ui-platform-baseline-v1/STABILIZATION_REPORT_01.md
```

That's the entire surface.

## 13. STOP

Architecture stabilization remains in effect. Phase 2.1 (token
formalization) is the next logical implementation phase but is **not
approved** for execution. No code change resumes without explicit
phase approval per `BASELINE.md` stop conditions.

Awaiting user direction.
