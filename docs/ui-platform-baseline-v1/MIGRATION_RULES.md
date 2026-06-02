# MIGRATION_RULES.md

> The rules of safe migration. Every retrofit (Phase 3A, 3B, 3C, 8a,
> 8b) follows this document. Anything not explicitly permitted here
> is forbidden.
>
> Updated 2026-05-19 with codified doctrine from the Phase 3A
> Phoenix CAD pilot (`PHASE_3A_PHOENIX_CAD_REPORT.md`,
> `PHASE_3A_POST_REVIEW_REPORT.md`). The retrofit-doctrine section
> below is the canonical "how to do a retrofit" reference.
>
> Updated 2026-05-19 with four additions codified from the Phase 3B
> Phoenix Checkout retrofit (`PHASE_3B_PHOENIX_CHECKOUT_REPORT.md`,
> `PHASE_3B_POST_REVIEW_AND_MERGE_REPORT.md`):
>
> - § 0. Pre-flight commons-API gap inventory (new explicit step)
> - § 1. Local facade strategy — *hybrid facade + preserved-local
>   coexistence in the same file* (refinement)
> - § 10. Source-mode validation checklist — row 8 strengthened; new
>   row 11 (actual app launch + main-window construction)
> - § 11. Monolith inline-class retrofit pattern (new section)

## Migration order

Actual ordering (Phase 3A pilot proved single-tool retrofits scale —
the original "two tools at once" framing was relaxed):

| Phase | Tool | Branch name | Status |
|-------|------|-------------|--------|
| **3A** | Phoenix CAD Tool (Lab Layout Tool) | `phase-3a-phoenix-cad-retrofit` | ✅ Merged 2026-05-19 (merge commit `79c7003` on `lab-layout-tool:master`). Retrofit branch preserved on origin per MIGRATION_RULES § Per-retrofit branch + PR convention. |
| **3B** | Phoenix Checkout Tool | `phase-3b-phoenix-checkout-retrofit` | ✅ Merged 2026-05-19 (merge commit `26a4689` on `Phoenix-Checkout-Tool:main`). Retrofit work: B1–B7 (`76f2c23`..`5153aad`) + regression fix B8 (`80dace8`). Doctrine additions in this document codified from `PHASE_3B_PHOENIX_CHECKOUT_REPORT.md` + `PHASE_3B_POST_REVIEW_AND_MERGE_REPORT.md`. Retrofit branch preserved on origin per MIGRATION_RULES § Per-retrofit branch + PR convention. Tag intentionally skipped — `version.py` unchanged at 1.7.0; `v1.7.0` already exists at pre-retrofit commit; no new release version claimed by this merge. |
| **3C** | Phoenix Command Center | `phase-3c-pcc-retrofit` | ✅ Merged 2026-05-21 (merge commit `058a67a` on `phoenix_command_center:main`, post-merge submodule consolidation `060d08c`). Retrofit work: B1–B15 across 23 commits delivering the dashboard modernization (Lucide icons + StatusBadge + tools table + per-tool activity colors + aggregate tile refresh + top utility band). Tag `pcc-phase-3c-merged-v2.0.0` on the merge commit. Retrofit branch preserved on origin per MIGRATION_RULES § Per-retrofit branch + PR convention. PCC keeps orange + teal `BrandProfile` per ADR-016. Reports under this directory: `PCC_DASHBOARD_SURFACE_SPEC_V1`, `PCC_DASHBOARD_IMPLEMENTATION_STEP_01_REPORT` through `STEP_06_REPORT`, `PCC_FULL_DASHBOARD_UX_REVIEW_01`, `PCC_PHASE_3C_FINAL_POLISH_AND_BUILD_VALIDATION_REPORT`, `PHASE_3C_FINAL_MERGE_GATE_REPORT`, `PHASE_3C_FINAL_MERGE_REPORT`, `PHASE_3C_REMOTE_STABILIZATION_REPORT`. |
| **3D** | Phoenix Command Center — Detail Panel | `phase-3d-pcc-detail-retrofit` | ✅ Merged 2026-05-22 (merge commit `2196082` on `phoenix_command_center:main`, post-merge cleanup + submodule consolidation `d466202`). Retrofit work: Steps 1, 2, 4, 5, 6, 7 across 6 commits (`03fdfa3`..`390df84`) delivering the detail-panel modernization (top utility band restructure + AggregateTile migration + Overview / TODOs / Git / Files tab Panel-wrap + Lucide cohesion). Step 3 folded into Steps 1+6; Step 8 (keyboard shortcuts) deferred indefinitely per spec §7. Tag `pcc-phase-3d-merged-v2.1.0` on the merge commit. Retrofit branch preserved on origin per MIGRATION_RULES § Per-retrofit branch + PR convention. PCC keeps orange + teal `BrandProfile` per ADR-016. Reports under this directory: `PCC_DETAIL_PANEL_SURFACE_SPEC_V1`, `PCC_DETAIL_PANEL_IMPLEMENTATION_STEP_01/02/04/05/06/07_REPORT`, `PHASE_3D_FINAL_MERGE_GATE_REPORT`, `PHASE_3D_FINAL_MERGE_REPORT`. |
| **3E** | Phoenix Command Center — Commons Browser | `phase-3e-pcc-commons-browser-retrofit` | ✅ Merged 2026-05-22 (merge commit `6f0380c` on `phoenix_command_center:main`, post-merge submodule consolidation `829c513`). Retrofit work: Steps 1, 2, 3 across 3 commits (`d0434b3`..`d74e0bd`) delivering the Commons Browser modernization (summary chip row `_Chip` → `StatusBadge` / `UsageFooter` → `Panel` + Lucide + `StatusBadge` composition / tree+viewer cohesion pass: redundant splitter inline-QSS retired + Rescan → `TertiaryButton` + header spacing + dead imports removed). Step 4 = closure gate. Tag `pcc-phase-3e-merged-v2.2.0` on the merge commit. Retrofit branch preserved on origin per MIGRATION_RULES § Per-retrofit branch + PR convention. PCC keeps orange + teal `BrandProfile` per ADR-016. Cleanest closure of 3C/3D/3E — Step 3 retired all dead-code items inline; post-merge consolidation is a pure submodule-bump (7 docs-only commits). No scanner / FileViewer / tree / QFileSystemModel / search-backend / Wave-8a work occurred. Reports under this directory: `PCC_PHASE_3E_CANDIDATE_AUDIT_REPORT`, `PCC_COMMONS_BROWSER_SURFACE_SPEC_V1`, `PCC_COMMONS_BROWSER_IMPLEMENTATION_STEP_01/02/03_REPORT`, `PHASE_3E_FINAL_MERGE_GATE_REPORT`, `PHASE_3E_FINAL_MERGE_REPORT`. |
| **3F** | Phoenix Command Center — Search MVP | `phase-3f-pcc-search-mvp` | ✅ Merged 2026-05-22 (merge commit `a6e8f02` on `phoenix_command_center:main`). Single-commit additive phase (`19ec360`) replacing the dashboard's Ctrl+K placeholder with real bounded search over already-cached tool / TODO / commit / path data. New `search.py` module (~230 LOC pure-Python, no Qt; `SearchResult` dataclass + `build_corpus` + `search` helpers). `Dashboard` gains 3 new signals (`search_query_changed`, `search_submitted` [extended], `search_result_chosen`) plus a `SearchResultsPopup(QFrame)` lazily constructed under the search input. `main_window.py` wires live-update + Enter-dispatch + result-routing; the "backend coming in Step 7" placeholder string is retired. Closed result-kind set (`tool` / `todo` / `commit`) routes via existing `_open_detail(name, tab_index=...)` (tool/commit → Overview tab 0, todo → TODOs tab 1). Tag `pcc-phase-3f-merged-v2.3.0` on the merge commit. Retrofit branch preserved on origin per MIGRATION_RULES § Per-retrofit branch + PR convention. **Cleanest closure of the 3C/3D/3E/3F series** — zero dead code at gate, zero submodule lag, no post-merge consolidation commit needed. No scanner contract change. No commons changes (no new primitives, no new icons). No persistent index, no fuzzy library, no command palette, no search history, no commons file content search. PCC keeps orange + teal `BrandProfile` per ADR-016. Operator visual review passed on the operator's interactive desktop. Reports under this directory: `PCC_SEARCH_BACKEND_MVP_REPORT`, `PHASE_3F_FINAL_MERGE_GATE_REPORT`, `PHASE_3F_FINAL_MERGE_REPORT`. |
| **3G** | Phoenix Command Center — Settings Dialog | `phase-3g-pcc-settings-dialog` | ✅ Merged 2026-05-22 (merge commit `3a13eed` on `phoenix_command_center:main`). Single-commit/+140/-83 single-file phase (`7c5e8ab`) bringing `settings_dialog.py` onto the Phase 3C/3D/3E/3F unified vocabulary. Gear emoji (U+2699) retired; Lucide `settings` icon + `#pageTitle` typography. 3 General-tab inline-styled QFrame cards → commons `Panel` via `_make_general_card(title, description)` helper. `ToolRow` now extends commons `Panel` (mirrors Phase 3D `SyncStatusCard` pattern). Save → `PrimaryButton`; Cancel → `TertiaryButton`; Browse → `TertiaryButton` (0 raw `QPushButton` remaining). Tag `pcc-phase-3g-merged-v2.4.0` on the merge commit. Retrofit branch preserved on origin per MIGRATION_RULES § Per-retrofit branch + PR convention. **Smallest closure of the 3C–3G series** — 1 commit, 1 file, zero dead code at gate, zero submodule lag, no post-merge consolidation needed. No schema change. No persistence change. No `config.py` change. No `main_window.py` integration change. No commons changes (no new primitives, no new icons — `settings` pre-existing since Phase 2.2). PCC keeps orange + teal `BrandProfile` per ADR-016. **Phase 3G closes the PCC main-app polish series.** Operator direction post-3G: pause further PCC polish; begin platform-wide standards baseline before Wave 8a. Reports under this directory: `PCC_SETTINGS_DIALOG_MODERNIZATION_REPORT`, `PHASE_3G_FINAL_MERGE_REPORT`, plus the new `PHOENIX_APP_STANDARD_BASELINE_V1`, `APP_ALIGNMENT_CHECKLIST`, `APP_STANDARDIZATION_READINESS_MATRIX`. |
| **8a** | ValveMasterTool / Phoenix Master Tool | `phase-8a-valvemaster-retrofit` | ✅ Merged 2026-05-26 (merge commit `631dbe8` on `phoenix-master-tool:main`). Retrofit work: B1–B8a across 7 commits (`46012a6`..`2fa160e`) delivering commons submodule + requirements + family `ci.yml` + paths facade + updater hybrid facade + theme facade + 5-widget retrofit + build.bat hardening + `_EMBEDDED_QSS` retirement + post-B8 Decoded Fields visual fix (app-specific QSS layer restored). Forensic tag `valvemaster-retrofit-v1.1.0-pre` on the merge commit (Decision #1 tag-skip baseline + forensic rollback marker; version.py unchanged at 1.1.0; not a release tag). Retrofit branch preserved on origin per § Per-retrofit branch + PR convention. **Operator-approved early-open override:** Wave 8a opened on 2026-05-26 (before the 2026-06-02 doctrinal cooldown floor) by explicit operator instruction; recorded in B1 commit + every B-step report. ADR-003 exe-only payload contract preserved (updater zip = `['PhoenixMasterTool.exe']`). AppId `{A7F3C2D1-9B4E-4F6A-8C3D-1E5B7A9F2C4D}` + install path `{localappdata}\ATS Inc\PhoenixMasterTool` + user-data path + zip-asset name + exe name all preserved byte-for-byte. No production deployment occurred *at the retrofit merge itself*; the coordinated 4-app release subsequently published **`v1.1.1`** on 2026-06-01 (stable tag `v1.1.1` at the same SHA as `v1.1.1-rc1`; GitHub Release live with `PhoenixMasterToolSetup.exe` + `PhoenixMasterTool.zip` — see `PHOENIX_4_APP_RELEASE_CLOSURE_REPORT`). Reports under this directory: `WAVE_8A_VALVEMASTER_PREFLIGHT_AUDIT`, `WAVE_8A_KICKOFF_DECISION_RECORD`, `WAVE_8A_IMPLEMENTATION_BRIEF`, `WAVE_8A_B1`..`WAVE_8A_B9_MERGE_GATE_REPORT`, `PHASE_8A_VALVEMASTER_REPORT`. |
| **8b** | Job Tracker (Project Tracking Tool) | `phase-8b-job-tracker-retrofit` | ✅ Merged 2026-05-28 (merge commit `6a0d60b` on `project-tracking-tool:main`). Retrofit work: B1–B10 across 6 commits (`cc7acdb`..`d7212cc`) delivering commons submodule + `requirements-dev.txt` + ci.yml minor edit + paths facade + updater hybrid facade (`expected_internal=True` full-folder payload per ADR-003) + theme facade + 5-widget retrofit + `_EMBEDDED_QSS` retirement (~116 LOC) + repo-root `phoenix_style.qss` rewritten from stale Checkout-leftover to Job-Tracker app-specific overlay (two-layer compose per Wave 8a B8a pattern) + `starter_package/` deletion (8 files) + build.bat hardening (`--noupx`, `--collect-all=phoenix_commons`, 8× stdlib excludes, 3.12 soft-warn, commons preflight, Step 0 full cleanup). Net source diff: **-2011 LOC** (largest single retrofit reduction in the family — driven by `_EMBEDDED_QSS` + starter_package + retired widget classes). Forensic tag `job-tracker-retrofit-v1.8.5-pre` on the merge commit. **Operator-approved early-open override:** Wave 8b opened 2026-05-27 (before the 2026-06-09 doctrinal cooldown floor computed from Wave 8a's 2026-05-26 merge) by explicit operator instruction; recorded in B1 commit + every B-step report. `version.py` unchanged at `1.8.5` (Decision #1 tag-skip). **`AppId` still NOT declared in installer.iss per Decision #8 hard rule** (preserves AppName-hashed upgrade detection for the v1.6.0..v1.8.5 user base — adding one would have stranded existing installs). Full-folder payload contract preserved: updater zip = exe + `_internal/*` (260 entries, ADR-003 + `expected_internal=True`). Excel / PDF runtime stack preserved: `openpyxl==3.1.5` / `pyxlsb==1.0.10` / `reportlab==4.4.10` pins + hidden imports intact; functionally proven via B10 frozen exe loading 57 records from .xlsb. Domain logic (`project_tracker_backend.py`, financials_*.py × 4, `user_auth.py`, `generate_guide.py`) confirmed 0-diff vs main at B6 audit. Test surface (`tests/test_regressions.py` 441 LOC) preserved with hybrid-facade re-exports for `UpdatePackageError` + preserved-local `_validate_update_zip` / `_build_update_powershell_script`. Operator B10 interactive validation: 5-min S1 observation passed (no quarantine), visual pass (≈ 0% change), 29/29 regression tests green. Retrofit branch preserved on origin per § Per-retrofit branch + PR convention. No production deployment occurred *at the retrofit merge itself*; the coordinated 4-app release subsequently published **`v1.8.6`** on 2026-06-01 (stable tag `v1.8.6` at the same SHA as `v1.8.6-rc1`; GitHub Release live with `ProjectTrackingToolSetup.exe` + `ProjectTrackingTool.zip` full-folder payload — see `PHOENIX_4_APP_RELEASE_CLOSURE_REPORT`). Reports under this directory: `WAVE_8B_JOB_TRACKER_PREFLIGHT_AUDIT`, `WAVE_8B_KICKOFF_DECISION_RECORD`, `WAVE_8B_IMPLEMENTATION_BRIEF`, `WAVE_8B_KICKOFF_READY_REPORT`, `WAVE_8B_B1`/`B2`/`B3`/`B4_B5`/`B6_B7`/`B8_B9`/`B10`/`B11_MERGE_GATE_REPORT`, `PHASE_8B_JOB_TRACKER_REPORT` (closure). |

The Phase 3A pilot deliberately retrofitted **one tool** rather than
two, against the earlier "pilot batch of two" framing. Rationale,
documented retrospectively in `PHASE_3A_PHOENIX_CAD_REPORT.md`:

- Phoenix CAD is the source of the canonical commons widgets — its
  retrofit is the lowest-risk possible first move; doing it alone
  surfaces the retrofit workflow without confounding it with a
  second tool's specifics.
- Phoenix Checkout's monolithic `checkout_tool_gui.py` (177 KB,
  per `production-inventory.md`) is the heavier lift; benefits from
  applying Phoenix CAD's proven facade pattern after Phase 3A merges.

## Pilot migration policy

Phase 3A served as the pilot. Phase 3B (Phoenix Checkout) and beyond
are no longer "pilot batch" — they're single-tool retrofits applying
the **Phase 3A retrofit doctrine** (next section). Each retrofit:

1. Branches from the tool's `master`/`main` at a clean baseline.
2. Lands as its own PR with the canonical retrofit-PR structure
   (see `RETROFIT_PR_TEMPLATE.md`).
3. Includes its own post-retrofit report — `PHASE_<id>_<tool>_REPORT.md`
   in this directory, structured per `PHASE_3A_PHOENIX_CAD_REPORT.md`.
4. Does not start until the previous retrofit has either merged OR
   been explicitly cleared not to block.

## Phase 3A retrofit doctrine — the canonical pattern

This section codifies what worked in the Phase 3A Phoenix CAD pilot.
Every subsequent retrofit (3B onward) follows this pattern unless an
explicit deviation is approved.

### 0. Pre-flight commons-API gap inventory

*Added 2026-05-19 from the Phase 3B Phoenix Checkout retrofit.*

Before opening the retrofit branch, audit the tool's existing platform
helpers against the commons public API and produce an explicit gap
inventory. The product is a table of every locally-defined symbol that
the retrofit could plausibly replace, paired with the commons symbol it
would map to (or `—` if no commons equivalent exists).

For every gap (local symbol with no clean commons equivalent), present
a binary decision to the user **before retrofit work starts**:

| Option | Meaning |
|--------|---------|
| **A. Keep local** | The behaviour is intentional or app-specific. Retrofit treats the symbol as preserved-local (see § 1 below). No commons changes. |
| **B. Add to commons** | The behaviour is genuinely generic and a future second consumer is realistic. Retrofit pauses while a commons PR adds the symbol; then proceeds. |

Choose Option A by default. Option B requires evidence that ≥ 2 tools
will consume the symbol (one current + one credibly anticipated).
A speculative second consumer is not evidence.

Document the decision per gap in the retrofit's post-retrofit report.
Phase 3B's two gaps:

| Local symbol | Commons equivalent? | Decision | Rationale |
|--------------|---------------------|----------|-----------|
| `apply_light_theme` (Checkout `checkout_tool_gui.py`) | No — commons is dark-only per ADR-011. | **A. Keep local** | Light mode is a user-facing toggle (View → Dark Mode + QSettings persistence). Removing it would break behaviour. ADR-011 explicitly excludes light mode from commons; this is settled doctrine. |
| Split `download_update` + `apply_update` (Checkout `updater.py`) | No — commons exposes only combined `download_and_apply`. | **A. Keep local** | Checkout v1.7.0's threaded-install behaviour depends on the split (download in background thread, apply on main thread). Combining would re-introduce the v1.6.x UI-freeze regression. Future commons PR could add the split — flagged in Phase 3B report as a candidate, not blocking. |

This step would have caught the false-start in earlier sessions where
"retrofit `updater.py` to commons" was discussed without inventorying
which functions in `updater.py` had commons equivalents. The inventory
forces the question.

### 1. Local facade strategy

Each retrofitted subsystem stays as a **local file** in the consuming
app, with internals that delegate to commons. The local file
preserves the entire caller-side import surface, so no business-logic
file (e.g. `app.py`, `main_window.py`, domain modules) needs editing.

Concrete shapes observed in Phoenix CAD:

| Local file | Pre-retrofit | Post-retrofit |
|-----------|--------------|---------------|
| `paths.py` | Self-contained — `is_frozen` + path constants + helpers | Imports `is_frozen` from commons; keeps app-specific path constants and source-mode policy locally |
| `updater.py` | ~350 lines duplicating commons | ~100-line facade — 4 config constants + 2 wrapper functions |
| `ui/style.py` | ~800 lines with hand-maintained `_EMBEDDED_QSS` | ~55-line shim — `apply_dark_theme` re-export + `_resource_path` for app-local assets |
| `ui/components.py` | ~640 lines with full widget catalog | ~460 lines — commons re-exports + app-specific dialogs only |

Why local facades over direct commons imports at every call site:

- Caller-side imports (e.g. `from ui.style import apply_dark_theme`)
  don't change — business-logic files stay untouched.
- App-specific configuration (GitHub owner/repo, app-local asset
  paths, source-mode policy) lives where it belongs (in the app).
- The retrofit PR's diff is concentrated in the platform-helper
  files; reviewers can audit ~5 small files instead of every call site.

**Hybrid facade + preserved-local coexistence** *(added 2026-05-19,
Phase 3B Checkout)*. A single local file MAY contain both
commons-facaded functions AND preserved-local functions side by side.
The Phase 3A Phoenix CAD pattern made every retrofitted file a
whole-file facade; Phase 3B Phoenix Checkout proved that intra-file
hybrids are equally valid and sometimes required:

| File | Facaded symbols (delegate to commons) | Preserved-local symbols (keep app behaviour) |
|------|---------------------------------------|-----------------------------------------------|
| `updater.py` (Checkout) | `check_for_update` (4-kwarg call to `phoenix_commons.updater.check_for_update`); `UpdateInfo` (re-import for type identity) | `download_update`, `apply_update`, `download_and_apply` — split-install threaded behaviour from v1.7.0; exe-only payload extraction (`expected_internal=False` semantics per ADR-003) |
| `checkout_tool_gui.py` theme region (Checkout) | `apply_dark_theme` (facade calling `phoenix_commons.theme.apply_dark_theme`) | `apply_light_theme` (~30 lines; ADR-011 keeps light mode out of commons) |

Rules for hybrid files:

1. Every preserved-local symbol carries an inline docstring note
   citing **why** it's local (ADR reference, behavioural contract,
   threading requirement, etc.).
2. The retrofit's pre-flight gap inventory (§ 0) must explicitly
   list each preserved-local symbol with its Option-A decision.
3. The post-retrofit report's file-by-file diff narrative calls out
   the hybrid structure so future retrofits / audits don't mistake
   it for incomplete retrofit work.

### 2. Identity-equal widget verification

For every commons widget the retrofit adopts, a smoke-test assert:

```python
ui.components.PrimaryButton  is  phoenix_commons.widgets.PrimaryButton  # True
ui.components.Panel          is  phoenix_commons.widgets.Panel          # True
```

`is` (not `==`) — the local re-export must be the **same Python class
object** as the commons class. This catches the failure mode where a
retrofit accidentally re-defines a class instead of re-exporting it.
Pre-Phase-3B / 3C / 8 retrofits include this check in their post-
retrofit validation step.

### 3. Sentinel substitution workflow (BrandProfile)

The canonical QSS (`phoenix_commons/theme/phoenix_style.qss`) carries
three sentinel tokens for the brand-profile slots:
`__BRAND_PRIMARY__`, `__BRAND_SECONDARY__`, `__BRAND_ACCENT__`.

`apply_dark_theme(app, brand=None)` substitutes them at apply time
against the active `BrandProfile`. Apps that pass no `brand=` kwarg
get `DEFAULT_BRAND` (commons canonical red + deep blue + blue).

Per ADR-016, locked tokens (BG, SURFACE, TEXT, MUTED, status colours)
stay as literal hex in the QSS — they're universal across every
Phoenix tool.

Tooling consequences:

- **Editing the canonical QSS** (under commons) is the only way to
  change locked tokens. Apps cannot override at runtime.
- **Adding a fourth brand slot** requires a new ADR superseding
  ADR-016 — the closed slot list is intentional.
- **A rare edge case**: one `rgba(30, 58, 138, 220)` literal at QSS
  line 665 (UpdateBanner background) is SECONDARY in rgba form. Not
  cleanly sentinelizable in the current pipeline; brand-override apps
  see one surface render in canonical SECONDARY. Acceptable; flagged
  for PCC retrofit consideration.

### 4. Submodule initialization expectations

Every retrofitted app inherits a `commons/` git submodule per
ADR-015. Three operational requirements:

1. **`requirements.txt` includes `-e ./commons`.**
2. **`build.bat` preflights the submodule** — fails loudly with an
   actionable error if `commons/src/phoenix_commons/__init__.py` is
   missing or `import phoenix_commons` fails from the venv.
3. **CI checks out submodules recursively.** `actions/checkout` step
   uses `with: submodules: recursive`. CI also runs `python -c "import
   phoenix_commons; print(phoenix_commons.__version__)"` as a smoke
   check that the install resolved.

Fresh-clone procedure for any retrofitted tool:

```bash
git clone <tool-repo>
cd <tool-repo>
git submodule update --init --recursive
.venv/Scripts/pip install -r requirements.txt
```

### 5. Duplicate-removal sequencing

Delete locally-defined platform code **only after the replacement
path is proven green**. The Phase 3A sequence:

1. Add commons submodule + editable install. ✅ Verify
   `import phoenix_commons` works.
2. Retrofit one subsystem (e.g. `paths.py` → facade). ✅ Verify
   imports + behaviour preserved.
3. Move to next subsystem. ✅ Verify.
4. ... etc.
5. Only at the end — once every subsystem is on commons — delete
   anything that was just commons-duplicate (the `_EMBEDDED_QSS`
   body, the heavy updater implementation, the `tools/embed_qss.py`
   helper, etc.).

Never delete and replace in the same commit. Always: replace,
verify, then delete-with-evidence.

### 6. "Delete duplication, not behaviour"

Two failure modes the doctrine forbids:

- **Behavioral regression for the sake of consumption.** If commons's
  API does subtly different things than the local helper (e.g.
  Phoenix CAD's `_resolve_user_data` returns repo root in source
  mode; commons's `user_data_dir` always returns `%APPDATA%`), the
  app KEEPS its local behaviour. The retrofit consumes only what
  cleanly matches.
- **Cleanup of unrelated code "while we're here."** A retrofit
  doesn't refactor business logic, doesn't rename variables, doesn't
  modernise idioms. Purely: remove platform-duplicate code, replace
  with commons calls, preserve behaviour.

### 7. Drift-vs-extension heuristic

(Section below — already canonical, cross-referenced from this
doctrine section.)

For Phase 3A's specific judgment calls:

| Local code | Drift or extension? | Why |
|------------|---------------------|-----|
| `paths._resolve_user_data` — source-mode → repo root | **Extension** | Phoenix CAD's intentional source-mode policy; differs from commons's default; uses commons primitive (`is_frozen`) |
| `paths.JOBS_DIR` / `BLOCKS_DIR` / etc. | **Extension** | App-local path constants composing on commons |
| `ui.style._resource_path` for `LLT_Normal.ico` | **Extension** | App-local asset resolution; commons resources go through commons API |
| `WelcomeDialog` / `PreferencesDialog` / `JobBrowserDialog` | **Extension** | App-specific UX composing commons primitives |
| Anywhere business logic touches color hex directly | **Drift** | Use tokens; if not available, propose a commons PR |
| Hand-maintained QSS in an app | **Drift** | Use commons's canonical QSS |

### 8. Commit granularity expectations

Retrofit PRs use **many small logical commits**, not one giant
mono-commit. The Phase 3A pattern was 7 commits:

| # | What | Phoenix CAD example |
|---|------|---------------------|
| B1 | Submodule + editable install + `requirements.txt` | `6770cee` |
| B2 | Retrofit one platform helper (paths) | `b4fd625` |
| B3 | Retrofit another (updater) | `461687f` |
| B4 | Retrofit theme load | `ed1de8d` |
| B5 | Retrofit widgets | `dd53be2` |
| B6 | Preserve legacy QSS + delete repo-root | `7f08ad6` |
| B7 | Update `build.bat` + delete `embed_qss` | `2b040fc` |

Plus commons-side enabling work as separate commits in `phoenix-commons`
(Phase 3A had 3 — BrandProfile mechanism / sentinel substitution / doc
update).

Each commit independently passes `compileall` + `pytest` (commons-side)
+ source-mode smoke (tool-side). PR review can bisect.

### 9. Pre-flight WIP isolation procedure

If a tool's working tree has unfinished feature work when a retrofit
is approved, the retrofit blocks until the WIP is isolated. Phase 3A's
exact procedure (user-approved Option 3):

1. `git checkout -b feature/<feature-slug>` from the dirty `master`.
2. Stage + commit the WIP files with an honest "WIP: park <feature>
   before retrofit" message.
3. `git push -u origin feature/<feature-slug>` — WIP is now safe on
   remote.
4. `git checkout master` (or `main`).
5. `git reset --hard origin/master` (DESTRUCTIVE — requires user
   approval).
6. `git checkout -b phase-<id>-<tool>-retrofit` — the actual retrofit
   branch.
7. `git push -u origin phase-<id>-<tool>-retrofit`.

After the retrofit lands, the feature branch is resumed normally —
either rebased onto the post-retrofit `master`, or merged separately.

### 10. Source-mode validation checklist

Every retrofit's final-validation step exercises (minimum):

| # | Check | Pass criterion |
|---|-------|----------------|
| 1 | `compileall -q -x "commons\|build\|dist\|\.venv" .` | Exit 0 |
| 2 | `python -c "import paths, updater, ui.style, ui.components, ui.<other>"` | No errors |
| 3 | `ui.components.<WidgetClass> is phoenix_commons.widgets.<WidgetClass>` | True (identity check) |
| 4 | Updater config constants preserved | Match pre-retrofit values |
| 5 | `inspect.getsource(updater.download_and_apply)` contains the expected `expected_internal=<True/False>` | Match tool's payload contract |
| 6 | `paths.<APP_CONSTANT>` resolves to the expected path | Match pre-retrofit value |
| 7 | `QT_QPA_PLATFORM=offscreen` apply_dark_theme + widget construction | No exceptions; styleSheet substantial; default-brand hex present; sentinels absent |
| 8 | `QT_QPA_PLATFORM=offscreen python -c "import <entry-module>"` (e.g. `import app`, `import checkout_tool_gui`) | No exceptions on top-level module load. **Note**: this only exercises module-load code paths. It does NOT catch undefined-name bugs that live inside function bodies executed later (Python resolves names lazily at runtime). See row 11. |
| 9 | `git -C commons rev-parse HEAD == git -C <commons-parent> rev-parse main` | Submodule pinned to commons main HEAD (or an intentional older SHA — document if so) |
| 10 | Commons-side `pytest -q tests/` | All tests pass (no regressions from retrofit-enabling commons changes) |
| 11 | **Actual source-mode app launch** — `python <entry-script>.py`, then verify the main window exists and the process is alive ≥ 3 seconds | Process alive; `MainWindowTitle` is the expected app title; no crash traceback on stderr |

Any failing row = retrofit blocks merge.

**Row 8 vs row 11 — why both are required.** *Added 2026-05-19 from
Phase 3B Phoenix Checkout regression B8 (`80dace8`).*

The Phase 3B B2 retrofit (`0bb1618`) removed `import os` from
`checkout_tool_backend.py` because the retrofitted function
(`_app_data_path`) no longer used it. The PR passed `compileall` AND
the row-8 import-only smoke. The regression — `CheckoutStore._load()`
crashing with `NameError: name 'os' is not defined` at
`os.path.exists(DATA_FILE)` — only surfaced when an actual `MainWindow()`
instance constructed and called `self._store = CheckoutStore()` in
its `__init__`.

The lesson: any business logic that runs only after `app.exec_()` —
which is most of what an application actually does — is invisible to
import-only smoke. Row 11 forces an actual end-to-end source-mode
launch. Cost: ~5 seconds per retrofit. Benefit: catches an entire
class of regression that no static check can.

**Recommended row 11 implementation** (on Windows + PowerShell):

```powershell
$p = Start-Process -FilePath '.venv\Scripts\pythonw.exe' `
    -ArgumentList '<entry-script>.py' `
    -WorkingDirectory '<tool-root>' -PassThru
Start-Sleep -Seconds 4
$alive = Get-Process -Id $p.Id -ErrorAction SilentlyContinue
if ($alive) { "PASS PID=$($p.Id) Title='$($alive.MainWindowTitle)'" } else { "FAIL exited" }
```

**Whole-file import-removal audit rule** (corollary). When a retrofit
removes a top-level `import X` from a file because the retrofitted
function no longer needs `X`, audit EVERY remaining use of `X` in the
file — not just the function being retrofitted. Python's lazy name
resolution means `compileall` will not catch the regression.
Concretely: `grep -nE "\\bX\\." <file>` and confirm zero hits before
removing the import.

### 11. Monolith inline-class retrofit pattern

*Added 2026-05-19 from the Phase 3B Phoenix Checkout retrofit.*

Some tools (Phoenix Checkout's `checkout_tool_gui.py`, 3,468 lines)
don't have a clean platform-helper file structure — their widget
classes are defined **inline at the top of a monolithic GUI module**,
not in a separate `ui/components.py`. The Phase 3A facade pattern
(swap whole platform-helper files for facades) doesn't apply.

The Phase 3B Checkout B5 commit (`61aac52`) proved the surgical
pattern for this case:

**Recipe.** Replace the inline `class WidgetName(QPushButton)` / etc.
definitions with a single `from phoenix_commons.widgets import ...`
statement. Leave every caller site in the same file ENTIRELY
untouched. If the local name had a different identifier than the
commons one (e.g. Checkout's `_PhoenixTable` vs commons's
`PhoenixTable`), use an import alias: `from phoenix_commons.widgets
import PhoenixTable as _PhoenixTable`.

**Phase 3B B5 example.** Before retrofit (lines 30–60 of
`checkout_tool_gui.py`):

```python
class PrimaryButton(QPushButton):
    def __init__(self, text: str, parent=None):
        super().__init__(text, parent)
        self.setMinimumHeight(36)
        self.setCursor(Qt.CursorShape.PointingHandCursor)

class SecondaryButton(QPushButton):
    ...

class TertiaryButton(QPushButton):
    ...

class _PhoenixTable(QTableWidget):
    ...
```

After retrofit:

```python
from phoenix_commons.widgets import (
    PrimaryButton,
    SecondaryButton,
    TertiaryButton,
    PhoenixTable as _PhoenixTable,
)
```

Caller sites elsewhere in the 3,468-line file (`PrimaryButton("Save")`,
`_PhoenixTable(0, 5)`, etc.) are **byte-identical** before and after.
The diff is concentrated entirely in the import block.

**Verification.** Identity-equality check per § 2 still applies and is
the gate:

```python
import checkout_tool_gui as g
import phoenix_commons.widgets as cw
assert g.PrimaryButton    is cw.PrimaryButton
assert g.SecondaryButton  is cw.SecondaryButton
assert g.TertiaryButton   is cw.TertiaryButton
assert g._PhoenixTable    is cw.PhoenixTable
```

All five Phase 3B Checkout assertions held True post-B5 (B5 verified
in `PHASE_3B_PHOENIX_CHECKOUT_REPORT.md`).

**Scope discipline.** The monolithic file is NOT permission to also:

- Extract the inline classes to a new `ui/components.py` "while we're
  here". The point of the inline-import pattern is to retrofit with
  minimum diff. Extracting to a new file is its own future refactor;
  it is OUT of the retrofit's scope.
- Modernise any business logic in the monolith. Forms, tables,
  dialogs, menu construction, QSettings persistence — all untouched.
- Refactor the file's organisation (move methods between classes,
  split a class into two, etc.). The retrofit edits exactly two
  regions: the inline widget definitions, and the theme function (if
  the theme is also inline). Everything else is a no-op.

The Phase 3B Checkout retrofit produced a 2-hunk diff in
`checkout_tool_gui.py` (widget region + theme region). Anything else
is a scope violation that should trigger a stop-and-ask per the
Stop conditions section.

## Rollback policy

| Failure during retrofit | Action |
|--------------------------|--------|
| Compileall or pytest fails on the retrofit branch | Fix on the branch; do not merge. |
| Frozen-exe build fails in a way that AV explains | Mark Partial; consult `BLOCKERS.md`. |
| Installed exe fails to launch | Revert the retrofit branch; investigate; re-attempt as a new PR. |
| User-data loss reproduced on upgrade | **Hard stop.** Revert immediately. Patch `paths.user_data_dir` or migration code; do not retry until cause confirmed. |
| Theme regression discovered post-merge | Hotfix release with the legacy QSS dropped back in as app-local file; retrofit re-attempted later. |

A merged retrofit is **always revertable as a single
`git revert -m 1 <merge-sha>`** against the `--no-ff` merge commit
produced by § Per-retrofit branch + PR convention. This is
non-negotiable.

The small-commit history within the retrofit branch (the B1–Bn
commits described in § 8) is **preserved** on origin for forensic
inspection — rollback acts on the merge commit, not on the
individual retrofit commits. This means the retrofit branch's
internal commits are NOT squashed before merge; the `--no-ff`
strategy keeps both fine-grained bisect history AND single-revert
rollback simultaneously.

## Screenshot baseline requirements

Each retrofit PR includes **before + after** screenshots of:

- The app's main window (centered, default size).
- Any dialog the retrofit visibly affects (Settings, About, etc.).
- A representative data view (Job Tracker's job list; Phoenix
  CAD's hood-wiring page; etc.).

Screenshots taken at the deployed version's last release vs the
retrofit branch's head, on the same monitor / DPI / OS theme.

Visible-change goal:

| Tool | Acceptable visible change |
|------|---------------------------|
| Phoenix CAD | ≈ 0% (already on System A; widget refactor only) |
| Phoenix Checkout | < 5% (theme already System A; widget swap may shift padding 1–2 px) |
| ValveMaster / Phoenix Master Tool | **≈ 0% (revised)** — the v1.1.0 release already shipped the System A palette in `phoenix_style.qss` (canonical BG `#0a0e27` / surface `#141829` / DEFAULT_BRAND palette). Wave 8a is a facade retrofit, not a visible theme swap. See `WAVE_8A_VALVEMASTER_PREFLIGHT_AUDIT.md` for the byte-match verification. |
| Job Tracker | < 5% (theme already System A; refactor primarily code-side) |

If the visible change exceeds the band for a tool that's supposed to
be invisible, the retrofit isn't ready to merge.

## Local backup QSS strategy

Every retrofit lands the canonical commons QSS via
`apply_dark_theme()`. Before merging:

1. The tool's existing `phoenix_style.qss` (or programmatic palette
   in ValveMaster's case) gets copied to
   `<app>/legacy/phoenix_style.qss.preretrofit`.
2. That file is **not** loaded at runtime. It exists as a known-good
   fallback if a critical theme regression is discovered post-merge.
3. The file is removed in a follow-up PR ~30 days after the retrofit
   ships if no regression surfaces.

The phrase "local backup QSS" specifically refers to this preservation
pattern. Not to be confused with the git bundle backups in Phase 6C.

## Drift-vs-extension heuristic

The hardest judgment call during retrofit: is this app-specific code
**extending** commons (allowed) or **drifting from** it (forbidden)?

| Symptom | Drift or extension? |
|---------|---------------------|
| App-local class subclasses a commons widget and adds a method | **Extension** ✓ |
| App-local class subclasses commons widget and **overrides** its `__init__` to change colours | **Drift** ✗ — recolour via QSS object-name override instead. |
| App copies the commons QSS string + edits 2 selectors | **Drift** ✗ — append app-local QSS lines after commons QSS. |
| App invents a new colour token because the closest commons token "isn't quite right" | Likely **drift** — propose the new token as a commons PR first. If only one app needs it, keep it strictly app-local with a comment explaining why. |
| App imports `phoenix_commons.theme.tokens.C` and uses `C['accent']` | **Extension** ✓ — using the public API. |
| App imports `phoenix_commons.theme._embedded_qss` (private module) | **Drift** ✗ — bypassing the public API. Lint should catch this in Phase 9. |

When in doubt, ask: "if I had to delete this app and reinstall it
fresh, would I need to keep this snippet around to recreate the same
look?" If yes → commons. If no → app-local extension.

## Stop conditions

A retrofit **must stop and ask** if any of these surface during the
PR:

| Stop condition | Reason |
|----------------|--------|
| Need to modify a commons-owned file | Triggers a separate commons PR first. Retrofit waits. |
| Need to change the `AppId` GUID | Hard rule — would orphan existing installs. Justin must approve. |
| Need to change `<App>.zip` asset name | Breaks the auto-updater for users still on the prior version. Justin must approve. |
| Need to change install path or user-data path | Same — breaks upgrades. Justin must approve. |
| Build venv is not Python 3.12.x | Per `FROZEN_BUILD_BASELINE.md` + ADR-014 empirical validation (`BUILD_HARDENING_EXPERIMENT_REPORT_03.md`), frozen builds on 3.13/3.14 are quarantined by S1 on the developer workstation. Source-mode work continues to allow 3.10–3.14. The retrofit's frozen-build step MUST use a 3.12 venv. |
| `build.bat` is missing the hardened-baseline flags (`--noupx`, stdlib `--exclude-module` list, Step 0 cleanup) | Per `FROZEN_BUILD_BASELINE.md`. The hardening is mandatory for explainability + reproducibility; production tool retrofits should adopt the same flags as the wizard's template default. |
| Frozen-exe verification fails for a reason **other than** the documented S1/AV pattern | New blocker. Document in `BLOCKERS.md` before continuing. |
| A test that passes on `main` fails on the retrofit branch | Fix in the retrofit before merge; do not merge a regression. |
| The visible-change band for the tool is exceeded | Re-scope the retrofit. |

## Per-retrofit branch + PR convention

| Item | Convention | Phase 3A example |
|------|------------|-------------------|
| Branch name | `phase-<phase-id>-<tool-slug>-retrofit` | `phase-3a-phoenix-cad-retrofit` |
| PR title | `Retrofit <App Display Name> to commons-backed (Phase <id>)` | `Retrofit Lab Layout Tool to commons-backed (Phase 3A)` |
| PR body | Use `RETROFIT_PR_TEMPLATE.md`. Plus a "what changed in commons during this retrofit" section (may be empty for later retrofits — commons API is now stable). |
| Merge strategy | `--no-ff`. Preserve the retrofit branch on origin until the post-review report (this doc / equivalent) explicitly clears it for deletion. |
| Tag | `<app-slug>-retrofit-vX.Y.Z` matching the post-retrofit release. |

The earlier `retrofit-<tool-slug>` convention has been superseded by
`phase-<id>-<tool>-retrofit` — phase-prefixed names make the ordering
explicit in `git branch` output and match the directory naming the
post-retrofit reports use.

## Frequency limits

| Wave | Cadence rule |
|------|---------------|
| Pilot (Phase 7) | Both tools merged within 2 weeks of each other. |
| Wave 8a (ValveMaster) | At least 2 weeks **after** the pilot's last merge. |
| Wave 8b (Job Tracker) | At least 2 weeks after Wave 8a. |

Spacing exists so production-user incident reports can surface before
the next retrofit lands.
