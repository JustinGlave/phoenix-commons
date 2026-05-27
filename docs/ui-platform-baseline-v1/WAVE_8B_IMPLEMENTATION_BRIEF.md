# Wave 8b — Implementation Brief

> **Status:** execution-ready. Awaits explicit operator B1 approval.
> **Target:** Job Tracker / Project Tracking Tool, branch `phase-8b-job-tracker-retrofit` (to be created at B1).
> **Date:** 2026-05-27.
> **Companions:** `WAVE_8B_JOB_TRACKER_PREFLIGHT_AUDIT.md`, `WAVE_8B_KICKOFF_DECISION_RECORD.md`.

---

## Cross-cutting invariants (apply to every B step)

- **DO NOT add AppId GUID** to `installer.iss` (hard stop)
- **AppName "Project Tracking Tool"** byte-equal
- Install path `{localappdata}\ATS Inc\Project Tracking Tool` byte-equal
- User-data path `%APPDATA%\ATS Inc\Project Tracking Tool` byte-equal
- Updater zip name `ProjectTrackingTool.zip` byte-equal
- Updater exe name `ProjectTrackingTool.exe` byte-equal
- `version.py` `__version__ = "1.8.5"` unchanged
- Full-folder payload contract (`expected_internal=True`)
- `tests/test_regressions.py` stays green throughout
- Domain logic (`project_tracker_backend.py`, `financials_*.py`, `user_auth.py`, `generate_guide.py`) untouched
- `openpyxl` / `pyxlsb` / `reportlab` hidden imports preserved
- Early-open override recorded (Decision #12)

---

## B1 — Commons submodule + requirements-dev + CI minor edit

| | |
|---|---|
| Files touched | `.gitmodules` (new), `commons/` (new submodule), `requirements-dev.txt` (new), `.github/workflows/ci.yml` (minor edit), `CLAUDE.md` (commons-submodule note + early-open override) |
| Purpose | Establish commons consumption + dev pin baseline + family-CI alignment |
| Concrete actions | 1. `git checkout -b phase-8b-job-tracker-retrofit`. 2. `git submodule add https://github.com/JustinGlave/phoenix-commons commons`. 3. Write `requirements-dev.txt`: `pyinstaller==6.20.0` / `pytest==8.3.4` / `pytest-qt==4.4.0`. 4. Append `-e ./commons` to `requirements.txt`. 5. Edit `ci.yml`: add `with: submodules: recursive` on checkout step + `pip install -r requirements-dev.txt` + `import phoenix_commons` smoke step. 6. Update `CLAUDE.md` to document commons submodule + early-open override. |
| Validation | `import phoenix_commons` from venv; `git submodule status` shows pin; `ci.yml` YAML parses |
| Stop conditions | Submodule add fails; pip resolver conflict (openpyxl/pyxlsb vs commons); ci.yml YAML invalid |
| Expected visible change | None |

---

## B2 — paths / resource facade

| | |
|---|---|
| Files touched | `paths.py` (new) + `project_tracker_gui.py` (replace `_resource_path` with `from paths import resource_path`) |
| Purpose | Smallest commons-consumption code step (Wave 8a B2 pattern) |
| Concrete actions | 1. Create `paths.py`: re-export `is_frozen`/`user_data_dir`/`resource_path` from `phoenix_commons.paths`; wrap `resource_path` to bind `_TOOL_ROOT = Path(__file__).resolve().parent` per Wave 8a B2 precedent. 2. In `project_tracker_gui.py`: remove inline `_resource_path` (line 21); add `from paths import resource_path`. 3. **PRESERVE** `_app_data_path` (line 28) and `_backup_data_file` (line 43) verbatim — both are app-specific. |
| Validation | `compileall` clean; `from paths import resource_path; resource_path('phoenix_style.qss')` returns the repo-root path; `_app_data_path()` + `_backup_data_file()` still resolvable from `project_tracker_gui`; `tests/test_regressions.py` green |
| Stop conditions | Grep finds `_resource_path` call sites outside `project_tracker_gui.py` |
| Expected visible change | None |

---

## B3 — Updater hybrid facade (`expected_internal=True`)

| | |
|---|---|
| Files touched | `updater.py` (facade body + preserved-local helpers) |
| Purpose | Delegate `check_for_update` + `download_and_apply` to commons with full-folder payload contract; preserve test-import surface |
| Concrete actions | 1. Import from commons: `UpdateInfo`, `UpdatePackageError` (re-export), `check_for_update as _commons_check_for_update`, `download_and_apply as _commons_download_and_apply`. 2. Rewrite local `check_for_update()` as a facade calling commons with `owner="JustinGlave"`, `repo="project-tracking-tool"`, `current_version=__version__`, `zip_asset_name="ProjectTrackingTool.zip"`. 3. Rewrite local `download_and_apply(info, progress_callback)` as a facade calling commons with `exe_name="ProjectTrackingTool.exe"`, `expected_internal=True`, `progress_callback=progress_callback`. 4. **PRESERVE local** `_validate_update_zip` (line 148) + `_build_update_powershell_script` (line 184) — both consumed by `tests/test_regressions.py`. Same Wave 8a B3 hybrid pattern. |
| Validation | `compileall` clean; `updater.UpdateInfo is phoenix_commons.updater.UpdateInfo`; `updater.UpdatePackageError is phoenix_commons.updater.installer.UpdatePackageError`; `tests/test_regressions.py` 100% green; import smoke clean |
| Stop conditions | `tests/test_regressions.py` regresses; `expected_internal` defaults to anything but `True`; symbol `UpdatePackageError` / `_validate_update_zip` / `_build_update_powershell_script` not importable from local `updater` |
| Expected visible change | None |

---

## B4 — Theme facade + two-layer QSS compose

| | |
|---|---|
| Files touched | `project_tracker_gui.py` (replace `apply_phoenix_theme` body, retire `_EMBEDDED_QSS`); possibly write into `phoenix_style.qss` if it's empty/stale |
| Purpose | Commons baseline + app-specific overlay (Wave 8a B8a pattern — Decision #9 explicit) |
| Concrete actions | 1. `from phoenix_commons.theme import apply_dark_theme`. 2. Audit `phoenix_style.qss` (repo root) — if empty or just commons-duplicates, extract app-specific selectors from `_EMBEDDED_QSS` (selectors NOT present in commons QSS, e.g. `#taskToolsButton`) and write them into `phoenix_style.qss` as the overlay layer. 3. Rewrite `apply_phoenix_theme(app)` body to: `apply_dark_theme(app)` + `try: app.setStyleSheet(app.styleSheet() + "\n" + open(resource_path("phoenix_style.qss")).read()) except OSError: pass`. 4. Delete `_EMBEDDED_QSS` constant body (~570 LOC). |
| Validation | `compileall` clean; offscreen theme smoke: merged QSS length substantial (>30k chars), all DEFAULT_BRAND tokens present, sentinels absent, app-specific selectors (e.g. `#taskToolsButton`) present; `tests/test_regressions.py` green |
| Stop conditions | App-specific selector extraction misses a critical selector (visual regression risk); operator visual review flags any palette drift |
| Expected visible change | ≈ 0% (DEFAULT_BRAND palette byte-matches `_EMBEDDED_QSS` tokens; app-specific selectors carried through overlay) |

---

## B5 — Widget retrofit (monolith inline-class pattern)

| | |
|---|---|
| Files touched | `project_tracker_gui.py` only |
| Purpose | Replace 5 inline widget classes with commons imports (Wave 8a B5 pattern) |
| Concrete actions | 1. Add `from phoenix_commons.widgets import PrimaryButton, SecondaryButton, TertiaryButton, PhoenixTable, UpdateBanner` near top of file. 2. Delete inline class definitions: `PrimaryButton` (line 335), `SecondaryButton` (line 343), `TertiaryButton` (line 352), `PhoenixTable` (line 361), `UpdateBanner` (line 1709). 3. Update `UpdateBanner(...)` call sites to commons signature: `UpdateBanner(info.current_version, info.latest_version, info.release_notes, parent)`. 4. **PRESERVE** all other widgets: `ReorderableTaskTable`, `StatCard`, `SegmentedProgressBar`, `ElidingLabel`, `_BackgroundWidget`, `_WatermarkViewport`, `ResizeHandle`, `_HeaderResizeHandle`, `_VResizeHandle`, all dialogs. |
| Validation | identity-equal × 5: `project_tracker_gui.PrimaryButton is phoenix_commons.widgets.PrimaryButton` (and 4 others); offscreen MainWindow construction clean; `tests/test_regressions.py` green |
| Stop conditions | Any of the 5 widgets has a behavior gap; call-site signature update breaks any caller (grep for all `UpdateBanner(` sites) |
| Expected visible change | ≈ 0% (minor `UpdateBanner` text delta: "Release Notes" vs old wording; 🆕 emoji dropped — Wave 8a precedent) |

---

## B6 — Preserved-local no-op audit

| | |
|---|---|
| Files touched | None (audit only — no commits unless something needs fixing) |
| Purpose | Confirm financials / auth / domain subsystems untouched |
| Concrete actions | 1. Grep verify `financials_dashboard.py`, `financials_dialog.py`, `financials_excel.py`, `financials_models.py`, `user_auth.py`, `project_tracker_backend.py`, `generate_guide.py` show in `git status` as **unmodified**. 2. Confirm `openpyxl` / `pyxlsb` / `reportlab` still in `requirements.txt`. 3. Confirm `--hidden-import=openpyxl` / `--hidden-import=openpyxl.cell._writer` / `--collect-submodules=openpyxl` / `--hidden-import=pyxlsb` still in `build.bat`. 4. Confirm `--add-data="pyxlsb;pyxlsb"` still in `build.bat`. |
| Validation | All checks above pass |
| Stop conditions | Any preserved-local file shows as modified; any hidden-import flag is missing |
| Expected visible change | None |

---

## B7 — starter_package deletion

| | |
|---|---|
| Files touched | `starter_package/` removed (8 source files + `__pycache__/`); `CHANGELOG.md` note retired |
| Purpose | Per Decision #2 — operator-approved deletion at B7 |
| Concrete actions | 1. `git rm -r starter_package/`. 2. Edit `CHANGELOG.md`: retire the "starter_package/ deletion planned" forward-looking note; replace with closed retrospective note tied to Wave 8b. |
| Validation | `git status` shows deletion + CHANGELOG edit; grep across repo confirms zero remaining references to `starter_package` (except CHANGELOG retrospective); `compileall` + `tests/test_regressions.py` still green |
| Stop conditions | Grep surfaces a runtime/build/test reference to `starter_package` that the audit missed |
| Expected visible change | None |

---

## B8 — build.bat hardening

| | |
|---|---|
| Files touched | `build.bat`; possibly stale `ProjectTrackingTool.spec` (deletion if untracked); `CLAUDE.md` (Python 3.12 canonical note) |
| Purpose | Apply FROZEN_BUILD_BASELINE harden flags while preserving existing sanity checks + zip-layout post-check + signing flow |
| Concrete actions | 1. Add Python 3.12 soft-warn near top of build.bat (FROZEN_BUILD_BASELINE pattern). 2. Add commons preflight: `python -c "import phoenix_commons"` with clear error message on failure. 3. Convert implicit cleanup to **explicit Step 0**: `rmdir /s /q dist build 2>nul` before PyInstaller invocation. 4. Add to PyInstaller flags: `--noupx`, `--collect-all=phoenix_commons`, stdlib `--exclude-module={tkinter,_tkinter,tcl,tk,lib2to3,idlelib,turtle,turtledemo}`. 5. **PRESERVE** verbatim: existing sanity checks (README version + py_compile + unittest), `--hidden-import=openpyxl/pyxlsb`, `--collect-submodules=openpyxl`, `--add-data` for ico/png/qss/pyxlsb, post-build zip layout verify, Inno Setup compilation, full-install zip generation, Inno Setup path probes, signing hooks (if any). 6. Delete stale `ProjectTrackingTool.spec` from disk if present (gitignored anyway). |
| Validation | `build.bat` syntactically valid; soft-warn fires from non-3.12 venv; preflight passes from initialized commons venv |
| Stop conditions | Existing sanity checks accidentally removed; signing flow disrupted; openpyxl/pyxlsb/reportlab hidden imports accidentally dropped |
| Expected visible change | None (frozen-exe behavior validated at B10) |

---

## B9 — Source-mode validation

| | |
|---|---|
| Files touched | None (validation only) |
| Purpose | Confirm B1–B8 changes hold in source mode |
| Concrete actions | 1. `python -m compileall -q . -x "(commons/|.venv|build|dist)"` clean. 2. `python -m unittest discover -s tests` — all 441-LOC regressions green. 3. Identity check: 5 widgets `is` commons.widgets. 4. `from updater import UpdateInfo, UpdatePackageError, _validate_update_zip, _build_update_powershell_script` — all importable. 5. `UpdateInfo is phoenix_commons.updater.UpdateInfo`. 6. `UpdatePackageError is phoenix_commons.updater.installer.UpdatePackageError`. 7. Offscreen theme smoke: merged QSS length, brand tokens present, sentinels absent, app-specific selectors present. 8. Offscreen MainWindow construction (the actual `MainWindow` class — find canonical entry-point) — title contains `"Project Tracking Tool"`, geometry non-zero. |
| Validation | All 8 gates green |
| Stop conditions | Any single gate fails |
| Expected visible change | None |

---

## B10 — Frozen build + S1 observation

| | |
|---|---|
| Files touched | None (artifacts gitignored) |
| Purpose | Frozen-build validation under Python 3.12 venv + operator visual + S1 confirmation |
| Concrete actions | 1. Operator activates Python 3.12 build venv (create `.venv312` if needed). 2. `pip install -r requirements.txt -r requirements-dev.txt`. 3. Run `build.bat`. 4. Verify artifacts: `dist\ProjectTrackingTool\ProjectTrackingTool.exe`, `_internal\`, `dist\ProjectTrackingToolSetup.exe`, `dist\ProjectTrackingTool.zip` (contains exe + `_internal/`), `dist\ProjectTrackingTool_FullInstall.zip`. 5. Verify commons bundle at `dist\ProjectTrackingTool\_internal\phoenix_commons\` (theme/widgets/updater/icons/paths). 6. Verify `phoenix_style.qss` overlay bundled. 7. Operator visual review on interactive desktop: launch `ProjectTrackingTool.exe`, confirm theme/buttons/tables/dialogs render correctly, confirm financials/auth/RSS/change-order subsystems work, confirm UpdateBanner (if simulated). 8. 5-min idle S1 observation. |
| Validation | Build succeeds; updater zip layout passes commons `_validate_update_zip`; operator visual pass; no S1 quarantine |
| Stop conditions | Build fails; commons not bundled; updater zip layout wrong (missing `_internal/`); operator visual surfaces regression; S1 quarantine |
| Expected visible change | ≈ 0% (operator visual gate) |

---

## B11 — Merge gate

| | |
|---|---|
| Files touched | `MIGRATION_RULES.md` row 38 (commons) + `PHASE_8B_JOB_TRACKER_REPORT.md` (commons) |
| Purpose | Merge `phase-8b-job-tracker-retrofit` → `main`; tag; update governance |
| Concrete actions | 1. Final pre-merge check (working tree clean, retrofit HEAD known, main no drift). 2. `git checkout main && git merge --no-ff phase-8b-job-tracker-retrofit -m "Merge Wave 8b — Job Tracker / Project Tracking Tool commons retrofit"`. 3. Post-merge validation (compileall + tests + AppId-absent + version + paths). 4. `git tag -a job-tracker-retrofit-v1.8.5-pre <merge-sha> -m "Wave 8b commons retrofit complete. version.py unchanged at 1.8.5. Forensic rollback marker only; not a release tag."`. 5. Push main + tag + retrofit branch. 6. Update `MIGRATION_RULES.md` row 38 status to ✅ Merged. 7. Author `PHASE_8B_JOB_TRACKER_REPORT.md` (11-section closure per Wave 8a precedent). 8. Push commons. |
| Validation | All gates green; remote pushes succeed; tag at merge commit |
| Stop conditions | Merge conflicts; post-merge validation fails; push rejects |
| Expected visible change | None (post-merge state matches pre-merge B10 frozen build) |

---

## Session estimate

- **B1–B8: 1 working session** (mechanical + surgical; ~3–4 hours)
- **B9–B11: 1 working session** (validation + frozen build + merge; ~2–3 hours)
- **Total: 2 working sessions** (matches Wave 8a duration)

---

## Operator manual actions during retrofit

| When | Action |
|------|--------|
| Pre-B1 | Activate Python 3.12 venv (or let B1 use existing `.venv`; canonical venv setup at B10) |
| During B1–B8 | Review each commit diff before approving next step |
| B10 | Launch frozen exe on interactive desktop, walk through theme/buttons/tables/financials/auth/RSS/change-order, observe S1 for 5 min, confirm operator visual pass |
| B11 | Approve merge + tag |

---

*End of Wave 8b implementation brief. Awaits explicit operator B1 approval.*
