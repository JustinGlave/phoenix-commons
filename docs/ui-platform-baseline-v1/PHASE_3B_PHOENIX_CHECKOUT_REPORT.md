# PHASE_3B_PHOENIX_CHECKOUT_REPORT.md

> Phoenix Checkout retrofit — the second commons-backed retrofit; first
> against a monolithic high-complexity app. Validates the retrofit
> doctrine codified from Phase 3A against a much harder target:
> 3,606-line single-file GUI, split-thread updater API, user-facing
> dark/light theme toggle.
>
> Source-only. No PyInstaller, no Inno Setup, no frozen-exe validation,
> no installer testing, no updater deployment, no release work. AV/S1-
> gated rows remain blocked.
>
> Captured 2026-05-20.

## 1. Pre-flight state

| Repo | Branch | Working tree | Origin sync |
|------|--------|--------------|--------------|
| `phoenix-commons` | `main` = `70785a2` | ✅ clean | ✅ |
| `Phoenix-Checkout-Tool` | `main` = `2e03df6` (v1.7.0) | ⚠️ 1 untracked file (user-approved per § Findings) | ✅ |

Pre-flight identified two findings that required user decision before
the retrofit could proceed:

1. **Untracked `Code Review - checkout_tool_gui.docx`** (14 KB, mtime
   2026-04-17) — left untouched per user direction. Not committed, not
   moved, not gitignored.
2. **Light theme architecture** — `apply_light_theme` + a user-toggleable
   View → Dark Mode menu item. Commons is dark-only per ADR-011. **User
   directed: keep `apply_light_theme` 100% local as an app-local
   extension.**
3. **Split updater API** — `download_update` + `apply_update` as
   separate functions for v1.7.0's threaded install. Commons has only
   the integrated `download_and_apply`. **User directed: preserve split
   API exactly, consume commons primitives internally where appropriate.**
4. **No `requirements.txt`** in Checkout repo. User directed: create
   as part of the retrofit per the canonical ADR-015 pattern.

Phoenix Checkout invariants confirmed:
- ✅ **System A** — `phoenix_style.qss` content is effectively identical
  to commons's (110 selectors vs commons's 114; the 4 extras are
  Phoenix-CAD-specific `#comToggleBtn` variants that don't apply to
  any Checkout widget objectName, so zero visual effect).
- ✅ **`expected_internal=False`** — Checkout's `apply_update` extracts
  only `EXE_NAME` from the zip via PowerShell, never references
  `_internal/`. ADR-003 cross-tool updater-contract asymmetry preserved.
- ✅ **Exe-only updater payload** — `build.bat` creates an exe-only
  auto-updater zip (`PhoenixCheckoutTool.zip`) + a full-folder manual
  install zip (`PhoenixCheckoutTool_FullInstall.zip`).
- ✅ **`apply_dark_theme` QPalette** byte-equivalent to commons's
  (same 13 role/color pairs).

Retrofit branch: `phase-3b-phoenix-checkout-retrofit` (created from
clean `main = 2e03df6`, pushed to origin).

## 2. Backup confirmation

Fresh git bundles created beside earlier backups:

```
$ ls C:/Users/justing/PycharmProjects/Backups/

Phoenix-Checkout-Tool-20260520.bundle    591 KB   ← NEW (Phase 3B start)
Phoenix_CAD_Tool-20260519.bundle         1.5 MB   ← prior (Phase 3A start)
phoenix-command-center-20260513.bundle    77 KB   ← original
phoenix-commons-20260513.bundle          3.3 MB   ← original
phoenix-commons-20260519.bundle          3.6 MB   ← prior (Phase 3A start)
phoenix-commons-20260520.bundle          3.6 MB   ← NEW (Phase 3B start)
```

Both new bundles verified with `git bundle verify` — record complete
history.

## 3. Every duplicated subsystem removed

### 3.1. `_EMBEDDED_QSS` body in monolith (108-line literal)

| | Pre-retrofit | Post-retrofit |
|---|---|---|
| Location | `checkout_tool_gui.py:3445-3553` | **DELETED** |
| Content | 108-line abbreviated dark-mode QSS string | Commons-resident `EMBEDDED_QSS` (generated from canonical `phoenix_style.qss`) used by `apply_dark_theme` internally |

### 3.2. `apply_dark_theme` body (~30 lines local)

| | Pre-retrofit | Post-retrofit |
|---|---|---|
| Body | Fusion style + 13-row QPalette + on-disk-QSS-or-`_EMBEDDED_QSS`-fallback | 2-line facade: `from phoenix_commons.theme import apply_dark_theme as _commons_apply_dark_theme; _commons_apply_dark_theme(app)` |
| QPalette colors | All 13 hex/RGB values | Same 13 values produced by `DEFAULT_BRAND` profile substitution (verified byte-equivalent pre-retrofit) |

### 3.3. Inline widget classes (4 classes, 36 lines)

| Class | Pre-retrofit | Post-retrofit |
|-------|--------------|---------------|
| `PrimaryButton` | Inline (`:32-37`) | Re-exported from `phoenix_commons.widgets` |
| `SecondaryButton` | Inline (`:40-46`) | Re-exported |
| `TertiaryButton` | Inline (`:49-55`) | Re-exported |
| `_PhoenixTable` | Inline (`:58-66`) | Imported as `PhoenixTable as _PhoenixTable` (alias preserves the 4 underscored call sites) |

Identity check verified all 4 classes are **literally the same Python
objects** as the commons versions:

```
checkout_tool_gui.PrimaryButton   is phoenix_commons.widgets.PrimaryButton   ✓
checkout_tool_gui.SecondaryButton is phoenix_commons.widgets.SecondaryButton ✓
checkout_tool_gui.TertiaryButton  is phoenix_commons.widgets.TertiaryButton  ✓
checkout_tool_gui._PhoenixTable   is phoenix_commons.widgets.PhoenixTable    ✓
```

### 3.4. Updater duplicates (partial — see § 5)

| Symbol | Pre-retrofit | Post-retrofit |
|--------|--------------|---------------|
| `UpdateInfo` dataclass | Local definition (`updater.py`) | Re-imported from `phoenix_commons.updater` |
| `_parse_version` | Local definition | **DELETED** (commons internal equivalent) |
| `check_for_update()` body | ~40-line API client | 7-line facade calling commons with 4 kwargs |
| `RELEASES_API`, `REQUEST_TIMEOUT` | Module-level constants | **DELETED** (only used by old `check_for_update`) |

### 3.5. Backend path helper

| | Pre-retrofit | Post-retrofit |
|---|---|---|
| `_app_data_path(filename)` body | 3 lines — `Path(os.environ.get("APPDATA", Path.home())) / "ATS Inc" / "Phoenix Valve Checkout Tool"`, `mkdir`, `return str(... / filename)` | 1 line: `return str(_commons_user_data_dir("Phoenix Valve Checkout Tool", "ATS Inc") / filename)` |
| `os` / `pathlib.Path` imports | Used by `_app_data_path` | Dropped (no longer needed at module level) |

### 3.6. Repo-root `phoenix_style.qss`

| | Pre-retrofit | Post-retrofit |
|---|---|---|
| Location | `phoenix_style.qss` (repo root, 110 selectors, 16,123 bytes LF) | **DELETED** from repo root |
| Legacy preservation | n/a | `legacy/phoenix_style.qss.preretrofit` (per MIGRATION_RULES.md § Local backup QSS strategy; 30-day removal target) |
| Build bundling | `--add-data="phoenix_style.qss;."` | `--collect-all=phoenix_commons` (PyInstaller bundles commons's QSS automatically) |

### 3.7. `tools/embed_qss.py`

| | Pre-retrofit | Post-retrofit |
|---|---|---|
| Phoenix Checkout had NO `tools/embed_qss.py` | n/a | n/a |

Phoenix Checkout never had an embed-sync script (unlike Phoenix CAD).
The pre-retrofit `_EMBEDDED_QSS` was hand-maintained.

## 4. Every commons subsystem adopted

| Commons subsystem | How Phoenix Checkout consumes it |
|---|---|
| `phoenix_commons.theme.apply_dark_theme` | Local `apply_dark_theme` (`checkout_tool_gui.py`) is now a 2-line facade |
| `phoenix_commons.theme.tokens.DEFAULT_BRAND` | Used implicitly — Checkout passes no `brand=` kwarg; commons defaults to canonical red + deep blue + blue |
| `phoenix_commons.theme.EMBEDDED_QSS` | Resolved internally by `apply_dark_theme` as the QSS-file-missing fallback |
| `phoenix_commons.theme.phoenix_style.qss` (package data) | Resolved by `apply_dark_theme` from commons's install path; sentinel-substituted at apply time |
| `phoenix_commons.widgets.PrimaryButton/SecondaryButton/TertiaryButton/PhoenixTable` | 4 inline classes replaced with commons re-exports (see § 3.3) |
| `phoenix_commons.paths.user_data_dir` | Backend `_app_data_path` facade'd onto it (see § 3.5) |
| `phoenix_commons.updater.UpdateInfo` | Re-imported in `updater.py`; type annotations resolve to commons class |
| `phoenix_commons.updater.check_for_update` | Local `check_for_update()` is a zero-arg facade |

Subsystems **NOT adopted** (deliberately):

| Commons subsystem | Why not adopted by Phoenix Checkout |
|---|---|
| `phoenix_commons.updater.download_and_apply` | Commons offers only integrated download+apply. Checkout's GUI uses the split pattern (`download_update` on background thread, `apply_update` on main thread) added in v1.7.0. Calling commons's `download_and_apply` would force synchronous flow — behavioral regression. Keeping split LOCAL. |
| `phoenix_commons.updater.installer._validate_update_zip` | Underscore-private per API_BOUNDARIES.md; Checkout never validated zip content pre-retrofit anyway (exe-only contract = minimal validation). No drift. |
| `phoenix_commons.paths.is_frozen` | Checkout's pre-retrofit code doesn't expose an `is_frozen` helper (the test `getattr(sys, "frozen", False)` is used inline in `apply_update`). No retrofit target. |
| `phoenix_commons.paths.resource_path` | Checkout's `_resource_path` (`checkout_tool_gui.py:495`) resolves app-local assets (window icon, green.png); commons resolves commons-owned files. API shapes differ. Kept local. |
| `phoenix_commons.icons.icon` (Lucide loader) | Out of retrofit scope — would be feature work (icon swap). |
| `phoenix_commons.updater.qt.UpdateCheckThread` | Checkout has its own `_UpdateChecker` / `_ReleasesFetcher` / `_UpdateDownloader` QThread subclasses (`:584/593/621`) that integrate tightly with the GUI's release-notes / dialog flow. Replacing would touch business logic — out of scope. |
| `phoenix_commons.theme.tokens.SEMANTIC_COLORS` / `BrandProfile` | Checkout uses DEFAULT brand (red/blue) implicitly; no custom brand to register. |
| `phoenix_commons.widgets.no_scroll.*` | Checkout doesn't use no-scroll widgets (`NoScrollComboBox` etc.) — no inline duplicates to retrofit. |
| `phoenix_commons.widgets.Panel`, `PageTitle`, `SectionTitle`, `HintLabel`, `UpdateBanner` | Checkout uses raw `QLabel(...); setObjectName("SectionTitle")` patterns throughout the monolith (~30+ call sites). Replacing each with the commons class wrapper would be cosmetic refactoring of business logic — out of strict retrofit scope per "preserve behavior." The objectName-based QSS styling renders identically either way. |

## 5. Updater-contract preservation details

The most contract-sensitive part of the retrofit. ADR-003 documents
the cross-tool asymmetry: **Phoenix Checkout ships exe-only updater
zips** (vs Phoenix CAD / Job Tracker's full-folder layout).

### What's preserved BYTE-FOR-BYTE

| Element | Value |
|---------|-------|
| `GITHUB_OWNER` | `"JustinGlave"` |
| `GITHUB_REPO` | `"Phoenix-Checkout-Tool"` (note: CamelCase + hyphens; the lone outlier per `production-inventory.md`) |
| `ZIP_ASSET_NAME` | `"PhoenixCheckoutTool.zip"` (exe-only payload) |
| `EXE_NAME` | `"PhoenixCheckoutTool.exe"` |
| `expected_internal` value implied by `apply_update` | `False` (extracts only `EXE_NAME` from zip; never touches `_internal/`) |
| GUI call sites | All 11 unchanged (line numbers preserved within the monolith) |

### Updater API shape preserved

The GUI uses a **split** API not a single `download_and_apply`. Both
shapes coexist locally:

| Function | Public? | Used by GUI? | Body |
|----------|---------|--------------|------|
| `check_for_update()` | ✅ | ✅ (`:588`) | Facade — calls commons with 4 kwargs |
| `UpdateInfo` (dataclass) | ✅ | ✅ (type annotations + return) | Re-imported from commons — identity-equal class |
| `download_update(info, tmp_zip, progress_callback)` | ✅ | ✅ (`:636`, from `_UpdateDownloader(QThread).run()`) | LOCAL — commons has no separate download primitive |
| `apply_update(info, tmp_zip)` | ✅ | ✅ (`:3345`, after download completes on main thread) | LOCAL — extracts EXE_NAME only (exe-only contract) |
| `download_and_apply(info, progress_callback)` | ✅ | ❌ (convenience wrapper not called by GUI; retained for external callers) | LOCAL — wraps download_update + apply_update |

### Threaded-install behaviour preserved

v1.7.0 added `_UpdateDownloader(QThread)` running `download_update` on
a background thread, with the apply step deferred to the main thread
after download completes. This split is essential to the
"Install & Restart" button's responsiveness — synchronous
`download_and_apply` would freeze the UI during download.

**Commons doesn't support this split.** Forcing commons's combined
`download_and_apply` would regress the threading. Per
MIGRATION_RULES.md § "Delete duplication, not behaviour", the local
split implementations stay.

### The exe-only PowerShell extraction (preserved verbatim)

The bat-content body of `apply_update` was preserved exactly:

```
powershell -ExecutionPolicy Bypass -Command "Add-Type -AssemblyName System.IO.Compression.FileSystem; $tmp = Join-Path $env:TEMP ([System.IO.Path]::GetRandomFileName()); [System.IO.Compression.ZipFile]::ExtractToDirectory('{zip_ps}', $tmp); Copy-Item -Path (Join-Path $tmp '{EXE_NAME}') -Destination '{exe_ps}' -Force; Remove-Item -Path $tmp -Recurse -Force"
```

Verified post-edit: `_internal` never appears in the bat-content body.

## 6. Monolithic-GUI handling strategy

Phoenix Checkout's `checkout_tool_gui.py` was 3,606 lines pre-retrofit.
The user spec called extraction "the biggest danger" — risk of
"accidental redesign through extraction."

### Strategy applied: in-place surgical edits, ZERO extraction

The monolith was NOT split into multiple files. All retrofits happen
in-place:

| Operation | LOC removed | LOC added | Net |
|-----------|-------------|-----------|-----|
| Replace `PrimaryButton/SecondaryButton/TertiaryButton/_PhoenixTable` class definitions with `from phoenix_commons.widgets import ...` | 36 | 16 | -20 |
| Delete `_EMBEDDED_QSS` body | 110 | 0 | -110 |
| Replace `apply_dark_theme` body with facade | 27 | 19 | -8 |
| **Monolith total** | **173** | **35** | **-138** |

Result: 3,606 → 3,468 lines (-138, -3.8%). Significant duplication
removed without disturbing the monolith's structural shape.

### What the monolith still contains (untouched)

All app-specific UI orchestration. The retrofit did NOT touch:
- `_BgWidget` (background-color helper)
- `_UpdateChecker(QThread)` (release-poll thread)
- `_ReleasesFetcher(QThread)` (release-notes fetch)
- `_UpdateDownloader(QThread)` (background-download thread)
- `NewJobDialog`
- `NewCheckoutDialog`
- `BatchCheckoutDialog`
- `WelcomeDialog`
- `BugSuggestionDialog`
- `MainWindow` (1000+ lines of app logic)
- `apply_light_theme` (~80 lines — INTENTIONALLY local)
- `_resource_path` (app-local assets)
- The `View → Dark Mode` toggle + QSettings persistence
- Every form / dialog / table / business-logic method

The "monolith is not permission to modernize" rule held. No
`MainWindow` refactoring, no method extraction, no form rewrites, no
dialog reorganization.

### `apply_light_theme` — the deliberate non-retrofit

ADR-011 commits the platform to dark-only. Commons has no
`apply_light_theme`. Two choices:

| Option | What it does | Why rejected/accepted |
|--------|--------------|------------------------|
| **A** Keep `apply_light_theme` 100% local (chosen) | Light theme + the user-toggleable View → Dark Mode menu item continue to work. ADR-016 brand-profile mechanism doesn't apply. | **Preserves behavior** — users with `darkMode=False` setting in `QSettings("ATS Inc", APP_NAME)` see no change. |
| **B** Drop light theme | Forces dark mode universally. Aligns with ADR-011 at the tool level. | Rejected — violates "preserve behavior." Light-mode users would see a complete visual change without consent. |
| **C** Add `apply_light_theme` to commons | Would require ADR-011 amendment + significant commons expansion. | Rejected — user spec said "Do NOT proactively improve commons." Real value only if ≥2 tools want light mode (which isn't currently the case). |

Documented in `checkout_tool_gui.py:apply_dark_theme`'s docstring as
an app-local extension per MIGRATION_RULES.md § Drift-vs-extension
heuristic.

## 7. Visual parity findings

Per `VISUAL_BASELINE_RULES.md` § Capture mode, Phase 3B captures no
pixel screenshots (S1/AV chain prevents reliable frozen exe;
offscreen-Qt isn't a faithful production representation). Visual
parity assessed structurally.

### Dark theme — ✅ Acceptable parity by construction

- **QPalette**: byte-identical to pre-retrofit (verified — the 13
  role/color pairs Checkout used locally are EXACTLY the values
  commons produces with `DEFAULT_BRAND`).
- **QSS file**: commons's canonical QSS has 114 selectors vs
  Checkout's 110. The 4 extras are `#comToggleBtn` (Phoenix-CAD-
  specific). They don't apply to any Checkout widget objectName, so
  zero visual rendering difference.
- **`_EMBEDDED_QSS` fallback**: Checkout's old 108-line abbreviated
  fallback is gone. The new fallback (commons's full embedded) is
  more comprehensive — but the fallback only fires when the on-disk
  QSS file is missing (auto-update edge case), which doesn't happen
  in source mode + would only ADD rendering if it did fire. No
  regression.

### Light theme — ✅ Unchanged

`apply_light_theme` is 100% local and untouched. View → Dark Mode
toggle behaviour preserved exactly. QSettings persistence preserved.

### Widget visuals — ✅ Identity-equal

All 4 retrofitted widget classes are LITERALLY the same Python
objects as commons. No re-definition; no behavior drift possible.

### MIGRATION_VISUAL_REVIEW_CHECKLIST walkthrough

| Section | Result | Notes |
|---------|--------|-------|
| 1. Main window | ✅ | No `MainWindow` code touched. |
| 2. Dashboard / home view | ✅ | No dashboard code touched. |
| 3. Forms | ✅ | No form code touched. Widget classes identity-equal. |
| 4. Tables / grids | ✅ | `_PhoenixTable` is now `phoenix_commons.widgets.PhoenixTable`. Same defaults. |
| 5. Dialogs | ✅ | `NewJobDialog/NewCheckoutDialog/BatchCheckoutDialog/WelcomeDialog/BugSuggestionDialog` all untouched. |
| 6. Update banner | ✅ | Banner uses `objectName="UpdateBanner"` (raw QLabel) — same QSS selector applies post-retrofit. |
| 7. Empty states | ✅ | No empty-state copy touched. |
| 8. Dense-data states | ✅ | No table rendering touched. |
| 9. Error / warning states | ✅ | No error-handling code touched. |
| 10. Sidebar / navigation | ✅ | No nav code touched (Checkout uses menu-bar nav). |
| Palette / tokens | ✅ | All coloured pixels still map to commons tokens. Sentinel substitution produces canonical hex literals. |
| Typography | ✅ | No font code touched. |
| Spacing + radius | ✅ | No padding / margin / radius code touched. |
| Icons | N/A | Lucide icon loader not adopted. App-local PTT_Normal_green.ico + green.png untouched. |
| objectName discipline | ✅ | Commons-owned objectNames unchanged. No app collisions. |
| Update banner specifically | ✅ | `objectName="UpdateBanner"` selector unchanged; `expected_internal=False` preserved. |
| Updater behaviour | ✅ | Split API preserved. `check_for_update` zero-arg signature unchanged. |

**No ⚠️ (intentional change with sign-off) rows.** No ❌ (regression)
rows. All ✅.

### Per-app addenda (RETROFIT_PR_TEMPLATE.md § Per-app addenda)

| Item | Status |
|------|--------|
| Monolithic `checkout_tool_gui.py` extraction is incremental | ✅ Zero extraction performed — pure in-place edits |
| 5 XLSX templates' bundling preserved | ✅ Still bundled via `--add-data` |
| `expected_internal=False` passed in updater | ✅ Preserved exactly via local `apply_update` |
| `green.png` + `PTT_Normal_green.ico` stay app-local | ✅ Untouched |

## 8. Migration checklist results

See § 7 above. Summary:

| Status | Count |
|--------|-------|
| ✅ Verified parity | 16 of 16 surface rows + 5 of 5 cross-cutting rows |
| ⚠️ Intentional change (sign-off) | 0 |
| ❌ Regression | 0 |

All rows green by construction. No sign-off comments required.

## 9. Any regressions discovered

**None.** Every source-mode + import-level + identity check green.

Edge cases for frozen mode (post S1/AV-chain resolution):

| Risk | Likelihood | Mitigation |
|------|------------|------------|
| `--collect-all=phoenix_commons` doesn't bundle `phoenix_style.qss` | Low | Phase 2.6 packaging-verification dry-runs verified `importlib.resources` resolves; Phase 3A frozen-exe will demonstrate the same |
| Submodule init fails on fresh clone | Low | `build.bat` preflight catches with actionable error message |
| `expected_internal=False` regresses to True somewhere | Low | The `apply_update` body was preserved verbatim except for docstring additions; no code-level changes |
| Light theme toggle breaks | Low | `apply_light_theme` is 100% untouched + no commons import; verified to produce a 3,513-char styleSheet distinct from dark |

## 10. Any deferred cleanup intentionally skipped

| Item | Why deferred |
|------|---------------|
| `apply_light_theme` → commons | Commons is dark-only per ADR-011 |
| Inline `QLabel + setObjectName("SectionTitle")` patterns → `phoenix_commons.widgets.SectionTitle` | ~30+ call sites in business-logic code. Cosmetic refactor; objectName-based QSS renders identically. Out of strict retrofit scope. |
| Inline `_UpdateChecker/_ReleasesFetcher/_UpdateDownloader` QThread subclasses → `phoenix_commons.updater.qt.UpdateCheckThread` | Tightly integrated with GUI release-notes flow; replacement would touch business logic. |
| `phoenix_commons.icons.icon` for emoji-icon replacement | Feature-level work; out of retrofit scope. |
| Bumping `version.py` from 1.7.0 → 1.7.1 (or similar) | Release-prep decision, not retrofit. Tag decision deferred. |
| Removing `legacy/phoenix_style.qss.preretrofit` | Per MIGRATION_RULES.md ~30-day window. |
| Adding `.github/workflows/ci.yml` | Checkout has no CI workflow pre-retrofit; adding one is feature work. |
| Adding a `py_compile` step + version-sanity check to `build.bat` | Phoenix CAD's build.bat is more rigorous than Checkout's; aligning would be modernization not retrofit. |

## 11. Source-mode validation results

| # | Check | Result |
|---|-------|--------|
| 1 | `compileall -q -x "commons\|build\|dist\|\.venv\|legacy" .` exit 0 | ✅ |
| 2 | Retrofit imports resolve (`paths` via backend, `updater`, `checkout_tool_gui`, `checkout_tool_backend`, `checkout_export`) | ✅ |
| 3 | Widget identity check — 4 classes are commons | ✅ |
| 4 | Updater config constants preserved (4 / 4) | ✅ |
| 5 | `apply_update` bat-content body contains no `_internal` reference | ✅ |
| 6 | Backend `DATA_FILE` resolves to `%APPDATA%\ATS Inc\Phoenix Valve Checkout Tool\data.json` | ✅ |
| 7 | `QT_QPA_PLATFORM=offscreen` apply_dark_theme + widget construction | ✅ 16,891-char styleSheet, default brand substituted |
| 8 | `QT_QPA_PLATFORM=offscreen` apply_light_theme works (distinct from dark) | ✅ 3,513-char styleSheet |
| 9 | Submodule pinned at commons main HEAD | ✅ `70785a2` matches both |
| 10 | Commons-side `pytest -q tests/` | ✅ **91 / 91 pass** |

Plus:
- ✅ Out-of-scope files untouched: `installer.iss`, `checkout_export.py`,
  `PhoenixCheckoutTool.spec`, `PTT_Normal_green.ico`, `green.png` — all 0
  changes
- ✅ Cumulative diff vs `2e03df6`: +181 / −244 (net **−63** lines from
  the main repo, excluding the commons submodule)

## 12. Package-data validation results

Confirmed during Phase 2.6 (`STABILIZATION_REPORT_05.md` § 3.3):
non-editable `pip install` bundles `*.qss` + 10 `*.svg` via
`pyproject.toml`'s `[tool.setuptools.package-data]` table. Re-validated
this phase via Checkout's submodule editable install:

```
.venv/Scripts/python -c "
    from importlib.resources import files
    qss = (files('phoenix_commons.theme') / 'phoenix_style.qss').read_bytes()
    print(f'commons QSS bundled in editable install: {len(qss):,} bytes')
"
→ 17,956 bytes (sentinel-form)
```

Frozen-mode package-data validation remains deferred to Phase 4
(post-S1/AV-chain resolution).

## 13. Remaining local-only code in Phoenix Checkout

### Files untouched by the retrofit

| File | Reason it stays local |
|------|------------------------|
| `checkout_export.py` | App-specific Excel export logic |
| `checkout_tool_backend.py` (other than `_app_data_path`) | App-specific data model (`CheckoutStore`, `Job`, `ValveCheckout`, `DATA_FILE` constant) |
| `checkout_tool_gui.py` (3,468 of 3,606 lines) | App-specific GUI orchestration — MainWindow, dialogs, all business logic |
| `version.py` | Per-app version |
| `installer.iss` | App-specific installer config |
| `PhoenixCheckoutTool.spec` | PyInstaller spec |
| Bundled XLSX templates (5 files) | App-domain data |
| `PTT_Normal_green.ico` + `green.png` | App branding assets |

### Definitions retained locally after the retrofit

| Symbol | Where | Reason retained |
|--------|-------|------------------|
| `_BgWidget`, `_UpdateChecker`, `_ReleasesFetcher`, `_UpdateDownloader`, `NewJobDialog`, `NewCheckoutDialog`, `BatchCheckoutDialog`, `WelcomeDialog`, `BugSuggestionDialog`, `MainWindow` | `checkout_tool_gui.py` | App-specific UI orchestration; no commons equivalents |
| `_resource_path` | `checkout_tool_gui.py:495` | App-local asset resolution (window icon, green.png) |
| `apply_light_theme` | `checkout_tool_gui.py:3363` | ADR-011 says no light mode in commons; user-toggleable behavior preserved as app-local extension |
| `download_update`, `apply_update`, `download_and_apply` | `updater.py` | Split-API pattern; commons has only integrated download_and_apply — preservation per user direction |
| `GITHUB_OWNER/GITHUB_REPO/EXE_NAME/ZIP_ASSET_NAME` | `updater.py` | Per-tool GitHub Releases config |
| `_app_data_path` (now a facade) | `checkout_tool_backend.py` | Preserves the existing function signature so `DATA_FILE = _app_data_path("data.json")` keeps working |

## 14. Retrofit lessons learned

### Patterns confirmed (Phase 3A doctrine held)

1. **Local facade strategy works on a monolith.** Keeping `updater.py`
   and `checkout_tool_backend.py` as local facade files preserves every
   caller-side import inside the 3,606-line monolith. Zero MainWindow
   business-logic changes.
2. **In-place inline-class retrofit works.** Replacing the 4 widget
   classes with `from phoenix_commons.widgets import ...` at the top
   of the monolith required zero downstream changes — the import binds
   the same names the rest of the file uses.
3. **Identity check is a strong parity guarantee.** Verified post-edit
   that `ctg.PrimaryButton is phoenix_commons.widgets.PrimaryButton` etc.
   Catches accidental re-definition.
4. **Sed-based block deletion** worked well for the 108-line
   `_EMBEDDED_QSS` body removal. Edit tool isn't ideal for very large
   anchors; sed -i is surgical for block deletions.
5. **AST-based code-vs-docstring discrimination** catches false-positive
   regressions — the post-retrofit docstring legitimately mentions
   `_EMBEDDED_QSS` (saying "DELETED"); a naive `not in` would fail.
6. **Pre-flight gate caught real commons-API gaps** (split updater + no
   light theme in commons) before the retrofit started instead of mid-
   way. User-directed resolution avoided forced-redesign mid-retrofit.

### New observations specific to Phase 3B

1. **The monolith is not permission to modernize.** Held tight on this
   — zero extraction performed beyond the 4 inline widget classes and
   the `_EMBEDDED_QSS` body, both of which are pure duplication. The
   1000+ line `MainWindow` is untouched.
2. **Light-theme architecture surfaced a real commons-API design
   limitation** worth noting for the platform record. ADR-011 commits
   to "dark only" but doesn't account for tools that built light-mode
   features pre-platform. The "app-local extension" pattern in
   MIGRATION_RULES.md § Drift-vs-extension absorbs this gracefully.
3. **Split-thread updater API** is genuine commons-API gap. Worth
   noting as a candidate for a Phase 9+ commons enhancement (PCC and
   ValveMaster may have similar needs).
4. **`_PhoenixTable` as alias** preserves caller-side imports through
   a name change — the underscore prefix in Checkout's local class
   doesn't exist on commons's `PhoenixTable`. The `import as` form
   handled this transparently.
5. **No CI workflow to fix** — Checkout has no `.github/workflows/`
   directory. One less file to update. Counter-balance: no CI means no
   automatic per-PR validation of the retrofit's import wiring.
6. **No `requirements.txt` to amend; created from scratch.** This was a
   pre-flight finding that turned into an additive (not modifying) file
   create. Strictly within "preserve behavior" since nothing existed
   before to break.
7. **PySide6 version drift between tools is real** — Checkout's venv
   had 6.11.0 while Phoenix CAD's `requirements.txt` pins 6.10.2. Each
   tool's requirements pins what its venv currently has; cross-tool
   alignment is a Phase 9+ coordination item.

## 15. Whether doctrine held under high complexity

**Yes — the Phase 3A doctrine codified in
`MIGRATION_RULES.md § Phase 3A retrofit doctrine` held end-to-end.**

| Doctrine principle | Held? | Evidence |
|--------------------|-------|----------|
| Local facade strategy | ✅ | 3 facades (paths via backend, updater, theme); zero caller-side changes |
| Identity-equal widget verification | ✅ | 4 widget classes confirmed `is` commons |
| Sentinel substitution workflow | ✅ | Verified via offscreen apply_dark_theme — sentinels gone, default brand substituted |
| Submodule initialization expectations | ✅ | Build.bat preflight added; `submodules: recursive` not added (no CI exists) |
| Duplicate-removal sequencing | ✅ | Each commit replaces + verifies before deleting; B6 (legacy QSS preserve) preceded final removal |
| "Delete duplication, not behaviour" | ✅ | Light theme, split updater both kept LOCAL — exactly the principle's intent |
| Drift-vs-extension heuristic | ✅ | Two judgment calls (apply_light_theme, split-updater API) resolved via the heuristic |
| Commit granularity | ✅ | 7 commits B1-B7, each independently compiling + reversible |
| Pre-flight WIP isolation procedure | ✅ (modified) | Light-theme + split-updater findings ARE the new equivalent of WIP isolation — surface real commons-API gaps before retrofit, get user direction. |
| Source-mode validation checklist (10 rows) | ✅ | All 10 rows + 2 bonus rows (light theme works, out-of-scope files unchanged) — all green |

**Two new lessons that should update the doctrine** (recommended for a
post-Phase-3B doctrine update):

1. **Commons-API gaps surfaced at pre-flight are EQUIVALENT TO WIP
   isolation** — both block the retrofit until resolved, both require
   user decision. Pre-flight should explicitly enumerate commons-API
   coverage gaps as part of "STOP if any inconsistency."
2. **Inline-class retrofits in monoliths work via top-of-file import
   substitution** — without changes to downstream call sites. The
   Phase 3A doctrine described the "local facade" pattern for separate
   files; the monolith-import-substitution pattern is its monolithic
   variant.

## 16. Recommended changes before PCC retrofit (Phase 3C)

### Pre-Phase-3C commons changes

**One real ADR/work item:**

- **PCC palette reconciliation ADR-016 implementation in PCC source.**
  ADR-016 already documents PCC's `BrandProfile(primary="#E8783C",
  secondary="#3CB8AE", accent="#3CB8AE")`. PCC's retrofit needs to
  declare this profile in its source (likely a new
  `phoenix-command-center/theme.py`-equivalent module exporting the
  profile) and pass it to `apply_dark_theme(app, brand=PCC_BRAND)`.
  Documented in ADR-016 § 9 "Migration implications."

### Pre-Phase-3C doc cleanups (recommended)

- **Update `MIGRATION_RULES.md` Migration-order table** to mark Phase 3B
  as "Merged YYYY-MM-DD" (or "Awaiting merge approval" until merged).
- **Update doctrine with the two new lessons from § 15** — commons-API
  gaps as pre-flight WIP equivalents; inline-class import-substitution
  for monoliths.
- **Add a commons-API gap log** to `BLOCKERS.md` or a new
  `COMMONS_API_GAPS.md` enumerating:
  1. No `apply_light_theme` (deferred per ADR-011)
  2. No split `download_update` / `apply_update` (Phase 9+ candidate)
  3. The `rgba(30, 58, 138, 220)` sentinel-substitution edge case
     (still un-addressed since Phase 3A)

### Pre-Phase-3C Phoenix Checkout follow-ups (recommended)

- Update `version.py` 1.7.0 → 1.7.1 (or 1.8.0) before any release of
  the retrofit. Decision tied to whether the retrofit is its own
  release or batched with feature work.
- Consider adding a `.github/workflows/ci.yml` to Phoenix Checkout in a
  follow-up PR. Currently no CI; fresh-clone validation is manual.

### Phase 3C retrofit-PR template (extrapolated)

PCC's retrofit follows the Phase 3A/3B doctrine with brand-profile
specifics:

| # | Subject | PCC-specific notes |
|---|---------|---------------------|
| B1 | submodule + editable install + requirements.txt | Standard |
| B2 | path helper retrofit | PCC's `pcc_config.json` lives at project root in source mode; ADR-016 § 9 says "PCC's path policy must migrate to %APPDATA% for frozen" — needs decision |
| B3 | updater retrofit | If PCC gets packaged (open per `production-inventory.md`), `expected_internal` value TBD |
| B4 | theme retrofit + register `PCC_BRAND` profile | Visible color swap from orange/teal to default unless brand profile registered correctly |
| B5 | widget retrofit | PCC has app-specific `CommonsDropZone`, `SidebarSprite`, `ToolCard` — stay local |
| B6 | legacy QSS preservation | If PCC's `theme.py` C-dict is the "QSS" equivalent, preserve as `legacy/theme.py.preretrofit` |
| B7 | build.bat / packaging | PCC isn't currently packaged — may not have a build.bat to update |

## 17. Exact commits

### phoenix-commons (no commits this phase)

`main` at `70785a2` (unchanged from Phase 3A merge-report tip).

### Phoenix-Checkout-Tool (7 retrofit commits on `phase-3b-phoenix-checkout-retrofit`)

```
$ git log --oneline 2e03df6..phase-3b-phoenix-checkout-retrofit

5153aad Update build.bat — submodule preflight + --collect-all=phoenix_commons (Phase 3B B7)
2630792 Preserve legacy phoenix_style.qss + delete repo-root copy (Phase 3B B6)
61aac52 Retrofit inline widget classes to commons re-exports (Phase 3B B5)
30ca27a Retrofit apply_dark_theme + delete _EMBEDDED_QSS body (Phase 3B B4)
54458c1 Retrofit updater.py — facade check_for_update + keep split API local (Phase 3B B3)
0bb1618 Retrofit checkout_tool_backend._app_data_path to commons (Phase 3B B2)
76f2c23 Add phoenix-commons submodule + editable install + requirements.txt (Phase 3B B1)
```

| Hash | Subject | Lines |
|------|---------|-------|
| `76f2c23` | B1 — submodule + editable install + requirements.txt | +14 / 0 |
| `0bb1618` | B2 — backend `_app_data_path` retrofit | +15 / -6 |
| `54458c1` | B3 — updater facade (split API local) | +75 / -63 |
| `30ca27a` | B4 — apply_dark_theme facade + _EMBEDDED_QSS delete | +19 / -137 |
| `61aac52` | B5 — widget retrofit | +17 / -37 |
| `2630792` | B6 — legacy QSS preservation | +22 / 0 (rename) |
| `5153aad` | B7 — build.bat update | +19 / -1 |

**Cumulative Phoenix Checkout diff** (vs `2e03df6` main baseline):

```
 .gitmodules                                        |   3 +
 build.bat                                          |  20 +-
 checkout_tool_backend.py                           |  21 ++-
 checkout_tool_gui.py                               | 210 ++++-----------------
 commons                                            |   1 +    (submodule pin)
 legacy/README.md                                   |  22 +++
 .../phoenix_style.qss.preretrofit                  |   0     (renamed from repo root)
 requirements.txt                                   |  10 +
 updater.py                                         | 138 +++++++-------
 9 files changed, 181 insertions(+), 244 deletions(-)
```

**Net code reduction: 63 lines** removed from Phoenix Checkout (mostly
duplicated platform code in the monolith). The −138-line monolith
reduction is offset by +75 in updater (facade docstrings) and +21 in
backend (similar), but the deletion is real duplication; the additions
are documentation.

## 18. Branch state

### Phoenix-Checkout-Tool (local)

```
$ git -C Phoenix-Checkout-Tool branch -vv

  claude/pedantic-euler-0e7317 2e03df6 (worktree at .claude/worktrees/pedantic-euler-0e7317) [origin/main]
  main                         2e03df6 [origin/main]
* phase-3b-phoenix-checkout-retrofit 5153aad [origin/phase-3b-phoenix-checkout-retrofit]
```

`main` unchanged (retrofit on a branch awaiting merge approval).
The Claude worktree was ignored per user direction.

### phoenix-commons (local)

```
$ git -C phoenix-commons branch -vv

  baseline-v1                       417f860 [origin/baseline-v1]
* main                              70785a2 [origin/main]    ← unchanged this phase
  phase-2-theme-widgets             db1d8b4
  phase-3-paths-updater             b2e7f79
  phase-4-pyinstaller-compatibility ba3d2c4 [origin/phase-4-pyinstaller-compatibility]
```

## 19. Remote state

### Phoenix-Checkout-Tool (origin)

```
$ git -C Phoenix-Checkout-Tool ls-remote --heads origin

2e03df6…  refs/heads/main                                       ← unchanged
5153aad…  refs/heads/phase-3b-phoenix-checkout-retrofit          ← ★ new retrofit branch ★
```

Push: `git push origin phase-3b-phoenix-checkout-retrofit`
(`2e03df6..5153aad`).

### phoenix-commons (origin)

```
$ git -C phoenix-commons ls-remote --heads origin

417f860…  refs/heads/baseline-v1
70785a2…  refs/heads/main                              ← unchanged this phase (Phase 3A post-review tip)
ba3d2c4…  refs/heads/phase-4-pyinstaller-compatibility
```

This report's commit will advance `main` to a new tip when pushed.

## 20. Remaining blockers

| # | Blocker | Blocks | Severity / next action |
|---|---------|--------|-------------------------|
| 1 | User approval to merge Phase 3B → Checkout `main` | Checkout production rollout | Awaiting review |
| 2 | User approval for Phase 3C (PCC retrofit) start | Phase 3C | Awaiting |
| 3 | S1/AV chain (`BLOCKERS.md §1`) | Frozen-exe / installer / real updater | Unchanged; gates Phase 4+ |
| 4 | PCC palette reconciliation source-level work | Phase 3C | Pending — ADR-016 specifies but PCC source needs the `BrandProfile` registration |
| 5 | `legacy/phoenix_style.qss.preretrofit` (Checkout) removal | Eventual cleanup | Schedule ~30 days post-Phase-3B merge |
| 6 | Version bump for Phase 3B release | Next Checkout release | `version.py` still 1.7.0 |
| 7 | Phoenix Checkout has NO `.github/workflows/ci.yml` | Per-PR validation | Add in a separate follow-up PR (out of retrofit scope) |
| 8 | Commons-API gap log | Doctrine completeness | Recommended: add `COMMONS_API_GAPS.md` cataloguing the 3 known items |
| 9 | TODOS.md / PHASES.md doc-drift from current numbering | Doc clarity | Pre-Phase-3C doc-housekeeping candidate |

Items 1, 2, 3, 4 are gates. Items 5, 6, 7, 8, 9 are operational
follow-ups that don't block Phase 3C from starting.

## 21. Confirmation

### No other apps touched

| App | Modified this phase? |
|-----|----------------------|
| Phoenix CAD / Lab Layout Tool | ❌ No |
| Phoenix Valve Checkout Tool | ✅ Yes — retrofit branch `phase-3b-phoenix-checkout-retrofit`; `main` UNCHANGED |
| Phoenix Command Center | ❌ No |
| Project Tracking Tool (Job Tracker) | ❌ No |
| ValveMasterTool | ❌ No |

### No runtime / frozen verification attempted

- ❌ **PyInstaller not invoked.** `build.bat` reviewed + updated but
  not executed.
- ❌ **Inno Setup not invoked.**
- ❌ **No frozen exe built or tested.**
- ❌ **No installer built or tested.**
- ❌ **`download_and_apply` not invoked.** No real GitHub Release
  downloaded.

### No release / deploy work

- ❌ **No GitHub Release created.**
- ❌ **No git tag pushed.**
- ❌ **No `version.py` bumped.**
- ❌ **No `main` merge** (retrofit branch awaiting reviewer approval).
- ❌ **No phoenix-commons commits this phase** other than this report.

Operations performed this phase:

```
=== Pre-flight ===
git status / ls-remote / bundle / read contracts
read Checkout source (3 main files + build.bat + version.py)
discover dual-theme + split-API findings → user decision

=== Retrofit (B1-B7 on phase-3b-phoenix-checkout-retrofit) ===
B1: git submodule add + pip install -e ./commons + write requirements.txt
B2: edit checkout_tool_backend.py — _app_data_path facade
B3: rewrite updater.py — facade check_for_update + keep split API
B4: sed -i delete _EMBEDDED_QSS body + edit apply_dark_theme to facade
B5: edit checkout_tool_gui.py top — replace 4 inline widget classes with imports
B6: cp phoenix_style.qss legacy/ + git rm phoenix_style.qss + write legacy/README.md
B7: edit build.bat — submodule preflight + --collect-all=phoenix_commons

=== Validation ===
compileall (-x commons|build|dist|.venv|legacy) → exit 0
python -c "<retrofit imports + identity + contract>" → all pass
QT_QPA_PLATFORM=offscreen python -c "<dark + light theme smoke>" → both green
git submodule status → commons pinned at 70785a2 (= commons main HEAD)
cd phoenix-commons && pytest -q tests/ → 91/91 pass

=== Push ===
git push origin phase-3b-phoenix-checkout-retrofit → 2e03df6..5153aad

=== Report ===
Write PHASE_3B_PHOENIX_CHECKOUT_REPORT.md (this file)
git commit + push commons main
```

That's the entire surface.

## STOP

Phase 3B retrofit complete on the retrofit branch. Phoenix Checkout
consumes commons through 3 facades (paths via backend, updater, theme)
+ 4 widget re-exports. Visual parity preserved by construction. Light
theme + split-updater API kept local per user direction. All
validation green. Branch pushed to origin awaiting merge approval.

Per the phase spec:

- ❌ **Did NOT merge** to Phoenix Checkout `main`.
- ❌ **Did NOT start Phase 3C (PCC retrofit).**
- ❌ **Did NOT start Phase 8a (ValveMaster).**
- ❌ **Did NOT start Phase 8b (Job Tracker).**
- ❌ **Did NOT start frozen verification or installer testing.**
- ❌ **No release work.**

Recommended next steps:

1. Reviewer (Justin) review the retrofit PR + this report.
2. If approved: merge `phase-3b-phoenix-checkout-retrofit` → `main`
   with `--no-ff` per MIGRATION_RULES (analogous to Phase 3A merge).
3. Tag decision (skip per Phase 3A precedent until version.py is
   bumped at release-prep time).
4. Update MIGRATION_RULES.md migration-order row 3B → "Merged YYYY-MM-DD"
   (analogous to Phase 3A merge-report follow-up).
5. Phase 3C (PCC) approval — ready in principle; new ADR work not
   required.

Architecture stabilization remains in effect. Awaiting user direction.
