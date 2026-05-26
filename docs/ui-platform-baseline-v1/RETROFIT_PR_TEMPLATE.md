# RETROFIT_PR_TEMPLATE.md

> Canonical PR-body structure for every Phoenix tool retrofit
> (Phase 3B onward). Codified from the Phase 3A Phoenix CAD pilot
> (`PHASE_3A_PHOENIX_CAD_REPORT.md` is the worked example). Apply
> this template to every retrofit PR; deviations require a rationale
> in the PR description.
>
> Anchored doctrine: `MIGRATION_RULES.md` § Phase 3A retrofit doctrine.

## How to use

1. Copy this template into the retrofit PR body when opening it.
2. Fill every section. **Do not delete sections** — write `N/A`
   with a rationale if a section doesn't apply.
3. Reviewer (Justin) walks the document top-to-bottom before
   approving.
4. Update the document in-PR as new findings surface during
   review; the merged PR body becomes part of the retrofit's
   permanent record.

After merge, the same content is expanded into the post-retrofit
report at `docs/ui-platform-baseline-v1/PHASE_<id>_<tool>_REPORT.md`.

---

# PR title

`Retrofit <App Display Name> to commons-backed (Phase <id>)`

Examples:
- `Retrofit Phoenix Valve Checkout Tool to commons-backed (Phase 3B)`
- `Retrofit Phoenix Command Center to commons-backed (Phase 3C)`
- `Retrofit ValveMasterTool to commons-backed (Phase 8a)`
- `Retrofit Project Tracking Tool to commons-backed (Phase 8b)`

---

# PR body — fill in below

## Summary

One paragraph: which tool, what changes, what's the visible impact.
For tools already on System A (Phoenix CAD, Phoenix Checkout,
ValveMaster / Phoenix Master Tool — see WAVE_8A_VALVEMASTER_PREFLIGHT_AUDIT
for the byte-match verification), the visible impact is "≈ 0%". For
any future tool not yet on System A, document the visible delta
explicitly and capture before/after screenshots.

## Pre-flight state

- [ ] Both `phoenix-commons` and `<tool>` repos confirmed clean +
      pushed to origin BEFORE retrofit work began.
- [ ] Working tree of `<tool>` clean before the retrofit branch
      was created.
- [ ] If any uncommitted WIP existed, it was isolated to a
      `feature/<feature-slug>` branch first (per
      `MIGRATION_RULES.md` § Pre-flight WIP isolation procedure).
- [ ] Fresh git bundles for both repos created beside earlier
      backups (`.../Backups/<repo>-YYYYMMDD.bundle`).
- [ ] Contracts re-read: `PLATFORM_CONTRACT.md`,
      `COMPONENT_CONTRACT.md`, `API_BOUNDARIES.md`,
      `MIGRATION_RULES.md` (especially the Phase 3A doctrine
      section), `VISUAL_BASELINE_RULES.md`,
      `MIGRATION_VISUAL_REVIEW_CHECKLIST.md`, `ADR-016`.
- [ ] Tool-specific `visual-baselines/<app>/baseline.md` re-read.
- [ ] Tool confirmed remains: System A (or pre-retrofit System B
      for ValveMaster); correct `expected_internal` value; correct
      updater payload contract.

## Duplicated subsystems removed

List every locally-duplicated platform subsystem this PR removes.
For each, show the LOC delta and the corresponding commons
subsystem now consumed.

| Local subsystem | LOC before | LOC after | Replaced by |
|----------------|------------|-----------|--------------|
| `paths.py` | ___ | ___ | `phoenix_commons.paths.is_frozen` (+ app-specific path constants retained) |
| `updater.py` | ___ | ___ | `phoenix_commons.updater.check_for_update` + `phoenix_commons.updater.download_and_apply` (+ tool's GitHub-config constants retained) |
| `ui/style.py` | ___ | ___ | `phoenix_commons.theme.apply_dark_theme` (+ app-local `_resource_path` retained where needed) |
| `ui/components.py` | ___ | ___ | `phoenix_commons.widgets.*` + `phoenix_commons.widgets.no_scroll.*` re-exports (+ app-specific dialogs retained) |
| `phoenix_style.qss` (repo root) | (deleted) | n/a | Commons's `phoenix_commons/theme/phoenix_style.qss` resolved via `--collect-all=phoenix_commons` |
| `tools/embed_qss.py` (or equivalent) | (deleted) | n/a | `phoenix_commons.theme.generate_embedded_qss` |
| Other (specify) | ___ | ___ | ___ |

## Commons subsystems adopted

For every commons subsystem consumed, document the consumption
shape. If the tool **deliberately did NOT adopt** a commons subsystem
that another tool consumed, document the rationale in the next
section.

| Commons subsystem | How this tool consumes it |
|-------------------|----------------------------|
| `phoenix_commons.theme.apply_dark_theme` | ___ |
| `phoenix_commons.theme.tokens.BrandProfile` / `DEFAULT_BRAND` | This tool uses ___ profile (default / custom). If custom: paste the `BrandProfile(...)` literal. |
| `phoenix_commons.theme.EMBEDDED_QSS` | ___ |
| `phoenix_commons.widgets.*` | ___ widgets re-exported via local `ui/components.py` (list any subset) |
| `phoenix_commons.widgets.no_scroll.*` | ___ |
| `phoenix_commons.paths.is_frozen` | ___ |
| `phoenix_commons.paths.user_data_dir` | ✅ adopted / ❌ deliberately not adopted (rationale: ___) |
| `phoenix_commons.paths.resource_path` | ✅ adopted / ❌ deliberately not adopted (rationale: ___) |
| `phoenix_commons.updater.*` | `expected_internal=___` (True for full-folder, False for exe-only per ADR-003) |
| `phoenix_commons.updater.installer.UpdatePackageError` | ___ |
| `phoenix_commons.icons.icon` (Lucide loader) | ✅ adopted / ❌ deliberately deferred (rationale: ___) |
| `phoenix_commons.updater.qt.UpdateCheckThread` | ✅ adopted / ❌ deliberately not adopted (rationale: ___) |
| Other | ___ |

## Deliberately deferred adoptions

Commons subsystems that this retrofit deliberately did NOT adopt,
with rationale per `MIGRATION_RULES.md` § "Delete duplication, not
behaviour."

| Commons API | Reason not adopted in this retrofit |
|-------------|---------------------------------------|
| ___ | ___ |

## Visual parity review

Reference: `MIGRATION_VISUAL_REVIEW_CHECKLIST.md`. Walk every row;
mark ✅ Verified parity, ⚠️ Intentional change with sign-off note,
or ❌ Regression (BLOCKS MERGE).

### Per-surface (10 sections)

| Section | Status | Notes |
|---------|--------|-------|
| 1. Main window | ___ | ___ |
| 2. Dashboard / home view | ___ | ___ |
| 3. Forms | ___ | ___ |
| 4. Tables / grids | ___ | ___ |
| 5. Dialogs | ___ | ___ |
| 6. Update banner | ___ | ___ |
| 7. Empty states | ___ | ___ |
| 8. Dense-data states | ___ | ___ |
| 9. Error / warning states | ___ | ___ |
| 10. Sidebar / navigation | ___ | ___ |

### Cross-cutting

| Check | Status | Notes |
|-------|--------|-------|
| Palette / tokens (every coloured pixel from `SEMANTIC_COLORS`) | ___ | ___ |
| Typography (no font swap; no inline Consolas) | ___ | ___ |
| Spacing + radius (multiples of 4 px; rounded cards) | ___ | ___ |
| Icons (commons icon set or stay-local logos per ICON_POLICY) | ___ | ___ |
| `objectName` discipline (no reserved-name reuse) | ___ | ___ |
| Updater (signal wiring, `expected_internal` kwarg) | ___ | ___ |

### Per-app addenda

(Copy from `MIGRATION_VISUAL_REVIEW_CHECKLIST.md` § Per-app addenda
for the tool being retrofitted.)

- [ ] (Phoenix CAD only) `cad/` subsystem untouched
- [ ] (Phoenix CAD only) BricsCAD COM unchanged
- [ ] (Phoenix CAD only) `app.py` modified only at import lines
- [ ] (Job Tracker only) `starter_package/` deleted in this PR
- [ ] (Phoenix Checkout only) `expected_internal=False` passed in updater call
- [ ] (PCC only) `BrandProfile(...)` registered with the documented PCC values
- [ ] (ValveMaster only) Inno Setup AppId GUID **preserved byte-for-byte**
- [ ] (ValveMaster only) `apply_light_theme()` removed (Phoenix is dark-only)
- [ ] (ValveMaster only) Release-note copy explicit about visible change

## Migration checklist sign-off

- [ ] Every row resolved (✅ / ⚠️ / ❌).
- [ ] No ❌ rows remain.
- [ ] Every ⚠️ row has reviewer sign-off comment.
- [ ] Screenshots committed under `visual-baselines/<app>/screenshots/`
      (`--phase-<id>` suffix; `--phase-2.7` baselines retained for
      historical comparison; OR explicit rationale for deferring
      screenshot capture in this PR with follow-up plan).

## Package-data validation

Source-mode evidence that commons's package data (QSS + SVGs) is
reachable through the editable submodule install.

- [ ] `.venv/Scripts/python -c "from importlib.resources import files;
      print((files('phoenix_commons.theme') / 'phoenix_style.qss').read_text(encoding='utf-8')[:80])"`
      prints the QSS preamble (not a `FileNotFoundError`).
- [ ] `.venv/Scripts/python -c "from importlib.resources import files;
      print(sorted(p.name for p in files('phoenix_commons.icons.lucide').iterdir() if p.name.endswith('.svg')))"`
      lists ≥ 10 SVGs.
- [ ] `pyproject.toml` of commons confirmed unchanged (commons API
      didn't shift mid-retrofit).

Frozen-mode package-data validation is **blocked** by the S1/AV
chain (`BLOCKERS.md §1`) — see "Blocked runtime rows" section.

## Source-mode validation

Reference: `MIGRATION_RULES.md` § Source-mode validation checklist
(10 rows). Pass criterion: every row green.

| # | Check | Result |
|---|-------|--------|
| 1 | `compileall -q -x "commons\|build\|dist\|\.venv" .` exit 0 | ___ |
| 2 | All retrofit imports resolve (`paths`, `updater`, `ui.style`, `ui.components`, `ui.<other>`) | ___ |
| 3 | Widget identity checks: `ui.components.<Class> is phoenix_commons.widgets.<Class>` | ___ |
| 4 | Updater config constants preserved | ___ |
| 5 | `inspect.getsource(updater.download_and_apply)` contains the expected `expected_internal=___` | ___ |
| 6 | Path constants resolve to expected values | ___ |
| 7 | `QT_QPA_PLATFORM=offscreen` apply_dark_theme + widget construction smoke | ___ |
| 8 | `QT_QPA_PLATFORM=offscreen python -c "import <app-entry>"` | ___ |
| 9 | Submodule pinned to expected commons SHA (commons main HEAD, or intentional older SHA documented) | ___ |
| 10 | `cd commons && pytest -q tests/` all green | ___ |

## Blocked runtime rows (S1/AV-gated)

These are **NOT validated** by this retrofit — they require the
S1/AV bootloader-quarantine chain to clear first (`BLOCKERS.md §1`).
Listed here so reviewers don't expect them.

- [ ] PyInstaller frozen-exe build
- [ ] Inno Setup installer creation
- [ ] Installed-copy launch test
- [ ] Auto-updater end-to-end with a real GitHub Release
- [ ] User-data persistence across upgrade

These rows unblock when the S1/AV chain clears, at which point
Phase 4 frozen-exe verification reruns against this retrofit's
output.

## Deferred cleanup

Items intentionally NOT addressed by this retrofit, with rationale.

| Item | Why deferred |
|------|---------------|
| Removal of `legacy/phoenix_style.qss.preretrofit` | Per `MIGRATION_RULES.md` § Local backup QSS strategy — ~30-day safety window |
| Other (specify) | ___ |

## Screenshots

If captured (S1/AV permitting and the user wants pixel baselines
now): list path of each screenshot + a 1-line description.

- [ ] `visual-baselines/<app>/screenshots/main-window--phase-<id>.png`
- [ ] `visual-baselines/<app>/screenshots/forms--phase-<id>.png`
- [ ] (etc per `VISUAL_BASELINE_RULES.md` § File naming)

If deferred: rationale + follow-up commitment.

## Rollback notes

If this retrofit needs to be reverted post-merge:

| Failure | Rollback action |
|---------|-----------------|
| Theme regression | `git revert -m 1 <merge-sha>`. Legacy `legacy/phoenix_style.qss.preretrofit` available as the known-good QSS fallback. |
| Updater regression | Same revert. The pre-retrofit `updater.py` is preserved in git history. |
| Submodule install fails on a deploy machine | Local fallback: `pip install -e ./vendor/phoenix_commons` after running `refresh_commons.bat` (Plan B per ADR-015). |
| Frozen-exe build fails post-S1/AV-clear | Mark Partial; consult `BLOCKERS.md`. |
| User-data loss reproduced on upgrade | **Hard stop.** Revert immediately. Patch `paths.user_data_dir` (or local equivalent) before re-attempting. |

Confirm:

- [ ] Pre-retrofit baseline is recoverable via the git bundles at
      `Backups/<repo>-YYYYMMDD.bundle`.
- [ ] Retrofit branch will be preserved on origin for ≥30 days
      after the post-merge release.
- [ ] `master` (or `main`) has the pre-retrofit state until merge,
      so emergency rollback is `git reset --hard <pre-merge-master>`.

## Cross-references

- `commons/docs/ui-platform-baseline-v1/MIGRATION_RULES.md` § Phase 3A retrofit doctrine
- `commons/docs/ui-platform-baseline-v1/MIGRATION_VISUAL_REVIEW_CHECKLIST.md`
- `commons/docs/ui-platform-baseline-v1/ADR_PCC_PALETTE_RECONCILIATION.md` (ADR-016)
- `commons/docs/ui-platform-baseline-v1/visual-baselines/<app>/baseline.md`
- `commons/docs/production-inventory.md` § <App>
- Previous retrofit's post-retrofit report (for pattern reference):
  `commons/docs/ui-platform-baseline-v1/PHASE_3A_PHOENIX_CAD_REPORT.md`
  (the worked example for everything in this template)
- `BLOCKERS.md` (active blockers context — S1/AV chain in particular)

## After merge

- [ ] Capture the merge SHA. Tag the post-retrofit state as
      `<app-slug>-retrofit-vX.Y.Z`.
- [ ] Write `PHASE_<id>_<TOOL>_REPORT.md` in commons's
      `docs/ui-platform-baseline-v1/` — same structure as
      `PHASE_3A_PHOENIX_CAD_REPORT.md` (20 sections).
- [ ] Mark this retrofit's row in `MIGRATION_RULES.md` § Migration
      order as "Landed YYYY-MM-DD."
- [ ] If commons-side changes landed for this retrofit, push them
      to `phoenix-commons:main` (and refresh the submodule pin in
      every other Phoenix tool when their next retrofit / release
      lands — coordinate carefully).
