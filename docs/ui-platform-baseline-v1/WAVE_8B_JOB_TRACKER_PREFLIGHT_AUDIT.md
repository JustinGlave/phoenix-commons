# Wave 8b — Job Tracker / Project Tracking Tool Pre-Flight Audit

> **Status:** read-only audit. No source modified.
> **Target:** Job Tracker repo (display name "Project Tracking Tool", origin `JustinGlave/project-tracking-tool`).
> **Current version:** `1.8.5`.
> **Date:** 2026-05-27.

---

## 1. Repo state audit

| Item | Value |
|------|-------|
| Working dir | `C:\Users\justing\PycharmProjects\Job Tracker\` |
| Origin | `https://github.com/JustinGlave/project-tracking-tool.git` |
| Branch | `main` (clean, up to date with origin) |
| `version.py` `__version__` | `"1.8.5"` |
| Display name | `Project Tracking Tool` (per installer.iss `#define MyAppName`) |
| Exe name | `ProjectTrackingTool.exe` |
| Setup output | `ProjectTrackingToolSetup.exe` |
| Updater zip name | `ProjectTrackingTool.zip` |
| Full-install zip | `ProjectTrackingTool_FullInstall.zip` |
| Install path | `{localappdata}\ATS Inc\Project Tracking Tool` (note SPACE in path) |
| User-data path | `%APPDATA%\ATS Inc\Project Tracking Tool` |
| Main entry | `project_tracker_gui.py` (**6,404 LOC** monolith) |
| Backend | `project_tracker_backend.py` (2,317 LOC) |
| Total Python LOC | **10,934** across 10 files |
| Tests | `tests/test_regressions.py` (441 LOC) |
| build.bat | present + already includes sanity-check stage |
| installer.iss | present, **no `AppId` GUID** declared — uses AppName-based default (see § 4) |
| .spec | `ProjectTrackingTool.spec` (entry name correct — not stale) |
| requirements.txt | present (PySide6 + openpyxl + pyxlsb + reportlab) |
| requirements-dev.txt | **absent** |
| CI workflow | `.github/workflows/ci.yml` already at family-standard (windows-latest, Py3.12, py_compile + import + unittest) — more aligned than ValveMaster's was |
| Local tags | `v1.6.0`..`v1.8.5` (18 prior releases) |
| `commons/` submodule | **not yet present** |
| starter_package/ | **present** with 8 files + __pycache__ (full scaffold for spawning new tools) |
| CLAUDE.md | present + documents the 3-step Build / Inno Setup / Zips workflow |
| WIP isolation needed? | **No.** Working tree clean. |

---

## 2. Standards gap inventory

### 2.1 Visual

| Item | State | Disposition |
|------|-------|-------------|
| Phoenix dark-navy palette (System A) | aligned — `_EMBEDDED_QSS` carries `#0a0e27` / `#141829` / `#dc2626` / `#3b82f6` / `#1e3a8a` byte-matching DEFAULT_BRAND | already aligned |
| Local `phoenix_style.qss` file | present at repo root, bundled by `--add-data`, **but never read at runtime** (`apply_phoenix_theme` uses `_EMBEDDED_QSS` only) | dead bundled asset — clean-up candidate, optional B-step |
| App-specific QSS selectors (`#taskToolsButton`, etc.) | embedded in `_EMBEDDED_QSS` | must survive the retrofit (Wave 8a B8a lesson — append local QSS layer over commons baseline) |
| Object-name discipline | aligned — `secondaryButton` / `tertiaryButton` / etc. follow family pattern | already aligned |

### 2.2 Functional

| Item | State | Disposition |
|------|-------|-------------|
| User-data path under `%APPDATA%\ATS Inc\<App>` | aligned — `_app_data_path()` returns `%APPDATA%/ATS Inc/Project Tracking Tool/` | already aligned |
| Legacy data migration | `_app_data_path()` migrates from old next-to-exe location | preserved-local |
| Atomic JSON writes | aligned via backend (verified) | already aligned |
| Background work in QThread | aligned (update check thread) | already aligned |
| Excel/openpyxl integration | financials subsystem | preserved-local (domain) |
| User auth + admin role | `user_auth.py` | preserved-local (domain) |

### 2.3 Packaging / build

| Item | State | Disposition |
|------|-------|-------------|
| PyInstaller `--onedir --windowed` | aligned | already aligned |
| Inno Setup `PrivilegesRequired=lowest` | aligned | already aligned |
| Install path `{localappdata}\ATS Inc\<App>` | aligned | already aligned |
| `version.py` `__version__ = "X.Y.Z"` | aligned | already aligned |
| Updater = GitHub Releases | aligned | already aligned |
| `--noupx` flag | **missing** | needs retrofit (B-series) |
| `--collect-all phoenix_commons` | N/A pre-retrofit | add at B-series |
| Stdlib `--exclude-module` list | **missing** | needs retrofit |
| Step-0 full cleanup | implicit only (`--noconfirm`) — no explicit `rmdir build dist` | needs retrofit |
| Python 3.12 build-venv soft-warn | **missing** | needs retrofit (Decision #9 pattern) |
| commons submodule preflight in build.bat | N/A pre-retrofit | add at B-series |
| Hidden imports for openpyxl + pyxlsb | aligned (already present) | already aligned |
| `requirements-dev.txt` (pyinstaller/pytest/pytest-qt pins) | **absent** | needs retrofit |
| Updater zip layout-validation step in build.bat | aligned (PowerShell post-build check at lines 151-156) | already aligned |

### 2.4 Repository

| Item | State | Disposition |
|------|-------|-------------|
| `CHANGELOG.md` | present | already aligned |
| `CLAUDE.md` | present | already aligned (post-retrofit reconciliation needed) |
| `.github/workflows/ci.yml` | already family-standard (windows-latest, Py3.12, compileall + import + unittest) | minor addition at B-series: `submodules: recursive` + commons import smoke + `pip install -r requirements-dev.txt` |
| LICENSE | present | already aligned |
| Assets folder organization | repo-root flat (`PTT_Normal.ico`, `PTT_Transparent.png`, `phoenix_style.qss`) | already documented in `ASSET_NAMING_PROPOSAL.md` — out of Wave 8b scope (separate cleanup) |

### 2.5 Retrofit

| Item | State | Disposition |
|------|-------|-------------|
| commons submodule | absent | add at B1 |
| `phoenix_commons` consumption | none | add via B2–B5 facades |
| Monolith inline-class retrofit candidates | `PrimaryButton`, `SecondaryButton`, `TertiaryButton`, `PhoenixTable`, `UpdateBanner` — all in `project_tracker_gui.py` (lines 335, 343, 352, 361, 1709) | replace at B5 (MIGRATION_RULES § 11 pattern, identical to ValveMaster Wave 8a B5) |

---

## 3. Commons-API gap inventory

### Theme

| Local symbol | Commons equivalent | Class |
|--------------|-------------------|-------|
| `apply_phoenix_theme(app)` (line 6271) — `setStyle("Fusion") + setStyleSheet(_EMBEDDED_QSS)` | `phoenix_commons.theme.apply_dark_theme` | **C** — facade (DEFAULT_BRAND) |
| `_EMBEDDED_QSS` (line 5688, ~570 LOC inline QSS string) | commons-side `EMBEDDED_QSS` + canonical `phoenix_style.qss` package data | **C** — retire, but append local QSS overlay for app-specific selectors (Wave 8a B8a pattern) |

### Widgets

| Local symbol | Commons equivalent | Class |
|--------------|-------------------|-------|
| `PrimaryButton(QPushButton)` (line 335) | `phoenix_commons.widgets.PrimaryButton` | **C** — name-collision replace |
| `SecondaryButton(QPushButton)` (line 343) | `phoenix_commons.widgets.SecondaryButton` | **C** — name-collision replace |
| `TertiaryButton(QPushButton)` (line 352) | `phoenix_commons.widgets.TertiaryButton` | **C** — name-collision replace |
| `PhoenixTable(QTableWidget)` (line 361) | `phoenix_commons.widgets.PhoenixTable` | **C** — name-collision replace |
| `UpdateBanner(QFrame)` (line 1709) | `phoenix_commons.widgets.UpdateBanner` | **C** — name-collision replace (call-site needs signature adjust; same Wave 8a B5 pattern) |
| `ReorderableTaskTable(QTableWidget)` (line 374) | none | **A** — preserve-local (app-specific drag-reorder behavior) |
| `StatCard(QFrame)` (line 1450) | none in commons | **A** — preserve-local (functions like PCC's AggregateTile but PCC's is also local; promotion to commons needs two-consumer evidence per MIGRATION_RULES § 0) |
| `SegmentedProgressBar`, `ElidingLabel`, `_BackgroundWidget`, `_WatermarkViewport`, `ResizeHandle`, `_HeaderResizeHandle`, `_VResizeHandle` | none | **A** — all preserve-local (Job-Tracker-specific UI primitives) |

### Paths

| Local symbol | Commons equivalent | Class |
|--------------|-------------------|-------|
| `_resource_path(filename)` (line 21) | `phoenix_commons.paths.resource_path` | **C** — facade (B2 pattern from Wave 8a) |
| `_app_data_path()` (line 28) — returns `data.json` path + legacy-location migration | `phoenix_commons.paths.user_data_dir` (returns directory only — different shape) + local migration | **A** — preserve-local. `user_data_dir` is available via commons but the legacy-migration logic + return-of-specific-filename are app-specific. |
| `_backup_data_file(data_path)` (line 43) — timestamped backup with 10-file retention | none | **A** — preserve-local (Job-Tracker-specific) |

### Updater

| Local symbol | Commons equivalent | Class |
|--------------|-------------------|-------|
| `check_for_update()` (no args; reads `GITHUB_OWNER`/`GITHUB_REPO`/`__version__`) | `phoenix_commons.updater.check_for_update(owner, repo, current_version, zip_asset_name)` | **C** — facade with 4 kwargs |
| `download_and_apply(info, progress_callback)` | `phoenix_commons.updater.download_and_apply(info, exe_name, *, expected_internal=True, progress_callback=...)` | **C** — facade. **`expected_internal=True`** (commons default) per Job Tracker's full-folder payload contract |
| `UpdateInfo` dataclass | `phoenix_commons.updater.UpdateInfo` | **C** — re-export from commons |
| `UpdatePackageError` | `phoenix_commons.updater.installer.UpdatePackageError` | **C** — re-export from commons (used by `tests/test_regressions.py`) |
| `_validate_update_zip(zip_path)` (line 148) | commons `_validate_update_zip` is private | **A** — preserve-local for test-import compat |
| `_build_update_powershell_script(zip_path, install_dir, exe_path)` (line 184) | commons `_build_full_folder_powershell` is private | **A** — preserve-local for test-import compat |

**Test surface impact:** `tests/test_regressions.py` imports `UpdatePackageError`, `_build_update_powershell_script`, `_validate_update_zip` from local `updater`. Hybrid-facade pattern (same as Wave 8a B3 with `_parse_version`/`_ps_single_quote`) — local helpers preserved at module level for test compatibility.

### Gap inventory summary

| Class | Count |
|-------|-------|
| **C — Replace with commons** | ~10 symbols (5 widgets + 2 theme + 1 paths + 4 updater names) |
| **A — Preserve-local** | ~15+ widgets + 2 path helpers + 2 updater helpers + all dialogs + all domain logic |
| **B — Add to commons** | **0** — no new commons primitives needed |

Mirrors the Wave 8a / ValveMaster shape. **No new commons API work required.**

---

## 4. Preserved-local domain logic

Explicitly preserved (no commons migration considered):

- **`project_tracker_backend.py`** (2,317 LOC) — `ProjectRecord`, `ProjectTrackerBackend`, `PHOENIX_TASKS`, `parse_currency`, change-order logic, RSS export, all job/task data models
- **`project_tracker_gui.py`** — minus the 5 commons-replaceable widget classes, everything else is app-specific dialogs / widgets (~6,200 LOC preserved)
- **`financials_dashboard.py`** (405 LOC) — financial-summary UI
- **`financials_dialog.py`** (333 LOC) — financial entry/edit dialogs
- **`financials_excel.py`** (413 LOC) — openpyxl + pyxlsb integration; Excel import/export
- **`financials_models.py`** (69 LOC) — financial data structures
- **`user_auth.py`** (381 LOC) — admin/user authentication; `UserManager`, `AuthStoreError`, password hashing
- **`generate_guide.py`** (256 LOC) — help/guide generator
- **`tests/test_regressions.py`** (441 LOC) — regression baseline — must stay green across retrofit
- **`PTT_Normal.ico`, `PTT_Transparent.png`** — local brand assets (PyInstaller `--add-data` bundles; legacy "PTT_" naming preserved per `ASSET_NAMING_PROPOSAL.md` out of Wave 8b scope)
- **`phoenix_style.qss` at repo root** — currently dead asset (not loaded); to be either retired or wired up at theme retrofit per operator decision
- **`_EMBEDDED_QSS` app-specific selectors** — any selectors not present in commons QSS (e.g. `#taskToolsButton`) must be preserved via Wave 8a B8a two-layer compose pattern
- **`updater.py` private helpers** (`_validate_update_zip`, `_build_update_powershell_script`) — test-import contract
- **Excel/openpyxl/pyxlsb dependency chain** — runtime-critical; PyInstaller hidden-imports must survive build.bat hardening
- **`reportlab`** — PDF export (used by financials/RSS); runtime-critical
- **`_app_data_path` legacy migration** — backward-compat for v1.0.x installs

---

## 5. starter_package audit

| Item | State |
|------|-------|
| Directory present | ✅ `starter_package/` at repo root |
| Contents | 8 source files: `CLAUDE.md`, `app_backend.py` (3 KB), `app_gui.py` (22 KB), `build.bat`, `installer.iss`, `updater.py`, `version.py`, `gitignore.txt` + `__pycache__/` |
| External references (build/runtime/test) | **none** — no Python import, no build.bat reference, no installer.iss reference, no test reference |
| Documentation references | only `CHANGELOG.md` mentions "starter_package/ deletion planned" |
| Runtime impact of deletion | none — nothing in the deployed app depends on it |
| Build impact of deletion | none — build.bat doesn't reference it |
| Test impact of deletion | none — `tests/test_regressions.py` doesn't import it |
| Historical context | early scaffold for spawning new Phoenix tools; effectively superseded by PCC's New Tool Wizard (Phase 3F+) + the commons-backed family standard |
| Deletion gate | **operator approval required before deletion** (per MIGRATION_RULES) |
| Recommended disposition | delete in Wave 8b (Decision pending) |

Optional alternative: move to a `historical/` subfolder if operator wants a soft preservation. Operator decision.

---

## 6. Build / packaging readiness

### build.bat audit (vs FROZEN_BUILD_BASELINE)

| Requirement | Current state | Gap |
|-------------|----------------|-----|
| Python 3.12 build venv | not enforced | **LOW** — add soft-warn at retrofit |
| PyInstaller 6.20.0 pinned | no `requirements-dev.txt` | **MEDIUM** — add at retrofit |
| `--noupx` flag | ❌ missing | **HIGH** — add at retrofit |
| Stdlib `--exclude-module` list | ❌ missing | **HIGH** — add at retrofit |
| `--collect-all phoenix_commons` | N/A pre-retrofit | add at retrofit |
| Step-0 explicit cleanup | partial — `--noconfirm` deletes `dist/` per-target but no explicit `rmdir build dist` | **LOW** — add at retrofit |
| commons-submodule preflight | N/A pre-retrofit | add at retrofit |
| `--onedir --windowed` | ✅ aligned | |
| `--add-data` for ico/png/qss/pyxlsb | ✅ already present | preserve through retrofit |
| Hidden imports for openpyxl | ✅ already present | preserve |
| Sanity checks (README version + py_compile + unittest) | ✅ already present | preserve |
| Post-build artifact verification (zip layout check) | ✅ already present | preserve |
| Inno Setup path-probe with `%LOCALAPPDATA%` fallback | ✅ aligned | preserve |

**Job Tracker's build.bat is closer to FROZEN_BUILD_BASELINE than ValveMaster's was**, but still missing the four hardening flags.

### installer.iss audit

| Item | State |
|------|-------|
| `AppId` GUID | **❌ NOT DECLARED** — installer.iss has no explicit AppId. Inno Setup uses AppName-based default. |
| `DefaultDirName` | `{localappdata}\ATS Inc\Project Tracking Tool` (space in path) — aligned |
| `OutputBaseFilename` | `ProjectTrackingToolSetup` — aligned |
| `PrivilegesRequired=lowest` | aligned |
| Uninstall data-deletion prompt | already implemented (lines 64-87) |
| `SetupIconFile` | `PTT_Normal.ico` (legacy "PTT_" prefix — out of Wave 8b scope) |

**Critical AppId concern:** The 18 prior releases (v1.6.0..v1.8.5) all installed without an explicit AppId. Inno Setup's upgrade detection relies on either the explicit AppId OR (when absent) a hash of the AppName. Current users have `AppId` = hash of "Project Tracking Tool". **Adding an explicit AppId now would break upgrade detection for every existing install** — first-time upgrade users would see "Install" instead of "Upgrade" and end up with two parallel installations. **Hard stop: do NOT add an AppId during Wave 8b.** This is an inverse-stop-condition: the contract that must be preserved is the *absence* of an explicit AppId.

### .spec file

`ProjectTrackingTool.spec` — entry name `'project_tracker_gui.py'` is correct (not stale). The file is gitignored (`*.spec` in `.gitignore` by convention; needs explicit check at retrofit). build.bat uses CLI flags exclusively, so the spec is unused. Disposition: same as Wave 8a — delete at retrofit; PyInstaller regenerates fresh.

### Updater / installer contract risks

| Risk | Current state | Notes |
|------|----------------|-------|
| Updater zip = full folder (`_internal/` required) | ✅ enforced both at build.bat post-check + updater `_validate_update_zip` | preserve through retrofit (`expected_internal=True`) |
| AppId absent (AppName-hash upgrade detection) | ✅ stable for v1.6.0..v1.8.5 | **PRESERVE — do not add AppId** |
| Install path stable | ✅ `{localappdata}\ATS Inc\Project Tracking Tool` unchanged for many releases | preserve |
| User-data path stable | ✅ `%APPDATA%\ATS Inc\Project Tracking Tool` | preserve |
| Legacy data-file location migration | ✅ `_app_data_path()` handles next-to-exe legacy path | preserve |

### S1 risk

| Factor | State |
|--------|-------|
| Python 3.12 build venv | not enforced (operator could build from 3.14) |
| `--noupx` | missing |
| Stdlib excludes | missing |
| Step 0 cleanup | partial |
| Bootloader fingerprint | unverified for latest v1.8.5 build environment |

**S1 risk: MEDIUM** until retrofit hardens build.bat. Post-retrofit + Py3.12 venv: LOW.

### Hidden dependency risks

- `openpyxl` 3.1.5, `pyxlsb` 1.0.10, `reportlab` 4.4.10 — full-stack Excel + PDF surface. PyInstaller hidden-imports + `--collect-submodules=openpyxl` already present in build.bat. **Must preserve** through retrofit.
- `pywin32` — not in requirements.txt (only `pywin32-ctypes` arrives transitively via PyInstaller). If financials Excel code uses any `win32com` integration, this needs scrutiny. (Audit didn't surface a direct `win32com` import — likely safe.)

---

## 7. Visual change assessment

### Current theme system

- `_EMBEDDED_QSS` carries the full Phoenix dark-navy theme inline (~570 lines)
- Palette byte-matches DEFAULT_BRAND: BG `#0a0e27` / surface `#141829` / primary `#dc2626` / secondary `#1e3a8a` / accent `#3b82f6`
- App-specific QSS selectors present in embedded string (e.g. `#taskToolsButton` with custom `#16213d` + border `#2d5a8e`)
- 3 widget-level `setStyleSheet` carve-outs at lines 597, 3551, 3552 — minor (color/transparency overrides; same B6 invariant-respect pattern PCC/CAD/Checkout preserve)
- Local `phoenix_style.qss` at repo root **NOT currently loaded** at runtime — dead bundled asset

### Expected visible change — **LOW (≈ 0%)**

Same Phoenix-CAD profile as Wave 8a. Specific risks:

| Surface | Expected change |
|---------|------------------|
| Background / surface colours | none (byte-match) |
| Buttons | none (DEFAULT_BRAND substitution = byte-equal) |
| PhoenixTable | minor — ≤2px padding shift from commons primitive (same as ValveMaster) |
| `#taskToolsButton` styling | **AT RISK** — if commons QSS doesn't carry this selector, button reverts to red primary. Mitigation: append local QSS overlay (Wave 8a B8a two-layer compose pattern) |
| `UpdateBanner` | minor text — commons reads "Release Notes" / no 🆕 emoji (Wave 8a precedent) |
| `StatCard` (preserve-local) | no change |
| All financials dialogs | no change (preserved-local) |
| Login / user-management dialogs | no change (preserved-local) |

### Screenshot baseline needs

- Main window (project list + task table)
- Financials dashboard
- Change-order window
- Notes window
- Login dialog (post-startup)
- ManageUsers dialog (admin-only)
- An RSS table view
- UpdateBanner (post-update-check)

### Operator review needs

Light review at merge gate; explicit operator approval of any visible delta. Same Wave 8a precedent.

---

## 8. Risk classification

| Dimension | Level | Notes |
|-----------|-------|-------|
| **Visual risk** | **LOW** | ≈ 0% expected; Wave 8a B8a pattern (two-layer QSS) ports cleanly |
| **Functional risk** | **LOW** | Domain logic untouched; widget swap is name-collision-equivalent |
| **Excel / financials risk** | **LOW-MEDIUM** | `openpyxl` + `pyxlsb` hidden-imports must survive build.bat hardening; financials code path well-isolated |
| **Build risk** | **MEDIUM** | Missing hardening flags resolved at retrofit; existing build.bat is already cleaner than ValveMaster's was |
| **Packaging risk** | **MEDIUM** | **No AppId in installer.iss — must NOT be added** (would break upgrade detection for v1.6.0..v1.8.5 users) |
| **User-data risk** | **LOW** | `_app_data_path()` legacy migration preserved-local; `%APPDATA%\ATS Inc\Project Tracking Tool` stable |
| **S1 risk** | **MEDIUM** until B-series hardens build | post-B-series + 3.12 venv: LOW |
| **Commons integration risk** | **LOW** | Same monolith-inline-class pattern as Wave 8a; no new commons primitives needed |
| **starter_package deletion risk** | **LOW** | no runtime/build/test dependency; only CHANGELOG.md mentions it |
| **Test-import compat (`UpdatePackageError`, `_validate_update_zip`, `_build_update_powershell_script`)** | **LOW** | Hybrid facade preserves local symbols (Wave 8a `_parse_version`/`_ps_single_quote` precedent) |
| **Monolith size** | **MEDIUM** | `project_tracker_gui.py` at 6,404 LOC is the largest of the family; surgical diffs only |

### Likely stop conditions

- Operator adds AppId GUID to installer.iss (would break upgrade detection) — **hard stop**
- AppName change (would break upgrade detection in the same way) — **hard stop**
- Frozen-exe S1 quarantine in 5-min observation
- `tests/test_regressions.py` regresses
- Excel / financials code-path breakage (openpyxl/pyxlsb missing hidden import, reportlab not bundled)
- starter_package deletion uncovers unexpected dependency

---

## 9. Proposed retrofit sequence (B-series)

| Step | Files touched | Purpose | Expected visible change |
|------|----------------|---------|------------------------|
| **B1** | `.gitmodules`, `commons/` (new submodule), `requirements.txt`, `requirements-dev.txt` (new), `.github/workflows/ci.yml` (minor edits — `submodules: recursive` + `pip install -r requirements-dev.txt` + commons import smoke), CLAUDE.md (commons-submodule note) | Commons consumption + dev pin baseline | None |
| **B2** | new `paths.py` facade + `project_tracker_gui.py` (retire `_resource_path`; preserve `_app_data_path` + `_backup_data_file` as local) | paths facade — minimal commons consumption | None |
| **B3** | `updater.py` hybrid facade + preserved-local helpers (`_validate_update_zip`, `_build_update_powershell_script` kept for test surface; `UpdatePackageError` re-exported from commons) | `check_for_update` + `download_and_apply` delegate to commons with **`expected_internal=True`** | None |
| **B4** | `project_tracker_gui.py` — `apply_phoenix_theme` body → `apply_dark_theme(app)`; `_EMBEDDED_QSS` retired; **two-layer compose** (append repo-root `phoenix_style.qss` after commons baseline, per Wave 8a B8a lesson). If `phoenix_style.qss` is empty/stale, write the app-specific selectors that were in `_EMBEDDED_QSS` into it first | theme facade + app-specific QSS preserved | ≈ 0% |
| **B5** | `project_tracker_gui.py` — replace 5 inline `class PrimaryButton/SecondaryButton/TertiaryButton/PhoenixTable/UpdateBanner` definitions with `from phoenix_commons.widgets import …`; update `UpdateBanner(...)` call sites to commons signature | widget retrofit | ≈ 0% (minor `UpdateBanner` text delta) |
| **B6** | (no-op confirmation) — verify financials / Excel / user_auth / generate_guide / change-order subsystems untouched; confirm `openpyxl`/`pyxlsb`/`reportlab` hidden-imports intact | preserved-local audit pass | None |
| **B7** | `git rm -r starter_package/` | starter_package deletion (operator-approved) | None |
| **B8** | `build.bat` — add 3.12 soft-warn + commons preflight + Step 0 full cleanup + `--noupx` + `--collect-all=phoenix_commons` + stdlib excludes; delete stale `.spec` if present; preserve sanity checks + zip layout post-check + signing flow (if any) | build hardening | None |
| **B9** | (validation only — no commits) | source-mode validation: compileall + `unittest discover -s tests` + identity-equal × 5 widgets + offscreen theme smoke + offscreen MainWindow construction | None |
| **B10** | (build run only — artifacts gitignored) | frozen build under Python 3.12 venv; verify commons + assets bundled; verify updater zip = exe + `_internal/`; 5-min S1 observation (operator) | ≈ 0% visible (operator review) |
| **B11** | merge gate audit + `PHASE_8B_JOB_TRACKER_REPORT.md` + MIGRATION_RULES row 38 update | merge gate | (post-merge) |

Estimated effort:
- **B1–B8: 1 working session** (~3–4 hours mechanical work; matches Wave 8a B1–B6 pace)
- **B9–B11: 1 working session** (~2–3 hours validation + frozen build + merge)
- **Total: 2 working sessions** (matches Wave 8a duration)

---

## 10. Operator decisions needed

| # | Decision | Default | Approval status |
|---|----------|---------|------------------|
| 1 | Version bump or tag-skip | **tag-skip** (facade-only retrofit; `1.8.5` stays); forensic tag `job-tracker-retrofit-v1.8.5-pre` on merge commit | default-accept |
| 2 | `starter_package/` disposition | **delete in same PR** (per MIGRATION_RULES row 38; no runtime/build dependency) | **operator-must-confirm** before B7 |
| 3 | Excel / financials scope preservation | **preserve verbatim** — no migration; `openpyxl`/`pyxlsb`/`reportlab` hidden imports unchanged; financials_*.py + financials_models.py untouched | default-accept |
| 4 | Screenshot baseline location | `phoenix-commons/docs/ui-platform-baseline-v1/screenshots/wave-8b/` | default-accept |
| 5 | CI shape | existing `ci.yml` already family-standard; **minor edit only** (add `submodules: recursive` + `pip install -r requirements-dev.txt` + commons import smoke) — no parallel workflow needed (unlike ValveMaster which had a divergent `test.yml`) | default-accept |
| 6 | Python 3.12 build-venv enforcement | **soft-warn** at build.bat entry (Wave 8a Decision #9 pattern) | default-accept |
| 7 | Step 0 cleanup preference | **full cleanup** (`rmdir /s /q dist build`) per FROZEN_BUILD_BASELINE | default-accept |
| 8 | AppId GUID addition | **DO NOT ADD** — installer.iss currently has no AppId; v1.6.0..v1.8.5 users have AppName-hashed AppId; adding one now would break upgrade detection | **hard rule — no decision needed (preserve absence)** |
| 9 | `phoenix_style.qss` at repo root (currently dead — not loaded at runtime) | **wire up at B4 via two-layer compose** (Wave 8a B8a pattern). The file's contents may need to be the app-specific overlay layer (selectors not in commons). If empty/duplicate-with-`_EMBEDDED_QSS`, B4 writes the overlay layer into it before deleting `_EMBEDDED_QSS`. | **operator-must-confirm** (small risk of overlay extraction mistake) |
| 10 | `BrandProfile` | **commons `DEFAULT_BRAND`** (palette byte-matches `_EMBEDDED_QSS` tokens) | default-accept |
| 11 | WIP isolation | not needed — working tree clean | default-accept |
| 12 | Cooldown floor | doctrinal floor is **2026-06-09** (14 days after Wave 8a merge 2026-05-26); today 2026-05-27 → floor is **13 days out**. Operator may approve early-open override (Wave 8a precedent) or wait. | **operator-must-confirm** date / override stance |

**Summary:** 9 default-accept + 3 operator-must-confirm (#2 starter_package, #9 phoenix_style.qss disposition, #12 cooldown / opening date).

---

## 11. Recommendation

### **Ready after operator decisions + cooldown clearance (or explicit override).**

Job Tracker is in **better build/CI shape than ValveMaster was** at the equivalent pre-retrofit point:

| Dimension | ValveMaster pre-Wave-8a | Job Tracker pre-Wave-8b |
|-----------|--------------------------|---------------------------|
| `requirements.txt` | missing | present + pinned |
| `.github/workflows/ci.yml` (family-standard) | absent (test.yml divergent) | present + windows-latest + Py3.12 |
| build.bat sanity checks | none | present (README + py_compile + unittest) |
| Updater zip layout post-check in build.bat | none | present (PowerShell namelist check) |
| Test surface | 10 + 146 tests (validation) | 441 LOC regression tests covering auth + updater + backend |

But also has **more domain surface to preserve**:
- 10,934 total LOC vs ValveMaster's similar order
- Financials subsystem (Excel + PDF)
- User auth with admin role
- Change-order + RSS subsystems
- starter_package scaffold (slated for deletion)

### What's READY now

- ✅ Branch state clean; no WIP isolation needed
- ✅ Commons-API gap inventory complete (≈10 Class-C / 0 Class-B / 15+ Class-A — mirrors Wave 8a shape)
- ✅ Preserved-local list enumerated
- ✅ starter_package safe-to-delete confirmed (operator approval the only gate)
- ✅ B-series sequence drafted (B1–B11)
- ✅ Visual-change profile ≈ 0% (Phoenix-CAD precedent)
- ✅ Build path identified (already cleaner than ValveMaster's was)
- ✅ AppId hard-rule documented (preserve absence)
- ✅ Test-import compat strategy documented (hybrid-facade for 3 private updater helpers)

### What needs operator decisions

- ❌ Confirm `starter_package/` deletion in same PR (Decision #2)
- ❌ Confirm `phoenix_style.qss` two-layer overlay approach (Decision #9)
- ❌ Confirm cooldown stance — wait until 2026-06-09 OR explicit early-open override (Decision #12)

### What's BLOCKED until operator answers

- Wave 8b kickoff brief authoring
- Retrofit branch creation
- Any Job Tracker source modification

---

## 12. Confirmation

- **No implementation occurred.** No source-code change to Job Tracker or any other repo.
- **No app code changed.** All audit observations are read-only.
- **No commons API changed.** No new primitives, no `__all__` mutation, no test addition on commons side.
- **No `BrandProfile` changes.** Wave 8b will use commons `DEFAULT_BRAND` per default in §10.
- **No production deployment.** No installer built, no release tagged.
- **No retrofit branch created.** `phase-8b-job-tracker-retrofit` is not on the Job Tracker repo.
- **No commons submodule added to Job Tracker.** B1 task at kickoff.
- **No `build.bat` / `installer.iss` / `requirements*` / `version.py` / theme / UI / `.spec` modifications.** All preserved as observed.
- **starter_package preserved** as observed; deletion is operator-approved at B7.
- **Wave 8b remains operator-gated** to the 2026-06-09 doctrinal cooldown floor or explicit override.

---

*End of Wave 8b pre-flight audit. Awaits operator answers to Decisions #2, #9, #12 before kickoff brief authoring.*
