# Phoenix Tools — Production Inventory

> **Phase 0 deliverable** of the Phoenix Tools Unified Standard. Frozen snapshot of every shipping tool's identity, paths, build pipeline, and updater behaviour. Used to gate every future retrofit: the values in this file are the contract the retrofit must preserve.
>
> Read-only audit, no source-code changes were made to any production tool while compiling this. Re-generate this document before any retrofit PR and diff against this version to confirm nothing the deployed installers depend on has drifted.
>
> Captured 2026-05-13.

## Summary

| Tool                     | Display name                 | Exe                          | Install path                                            | Version |
|--------------------------|------------------------------|------------------------------|----------------------------------------------------------|---------|
| Job Tracker              | Project Tracking Tool        | `ProjectTrackingTool.exe`    | `{localappdata}\ATS Inc\Project Tracking Tool`           | 1.8.5   |
| Phoenix_CAD_Tool         | Lab Layout Tool              | `LabLayoutTool.exe`          | `{localappdata}\ATS Inc\Lab Layout Tool`                 | 0.1.1   |
| Phoenix-Checkout-Tool    | Phoenix Valve Checkout Tool  | `PhoenixCheckoutTool.exe`    | `{localappdata}\ATS Inc\Phoenix Valve Checkout Tool`     | 1.7.0   |
| ValveMasterTool          | ValveMasterTool              | `ValveMasterTool.exe`        | `{localappdata}\ATS Inc\ValveMasterTool`                 | 1.0.9   |
| phoenix-command-center   | Phoenix Command Center       | (source-run, not packaged)   | n/a                                                       | 2.0.0   |

---

## Job Tracker

| Field | Value |
|---|---|
| App name (display) | Project Tracking Tool |
| Exe name | `ProjectTrackingTool.exe` |
| GitHub owner | `JustinGlave` |
| GitHub repo | `project-tracking-tool` |
| Release zip asset (updater) | `ProjectTrackingTool.zip` — **full PyInstaller folder** (exe + `_internal/`) |
| Release zip asset (manual) | `ProjectTrackingTool_FullInstall.zip` |
| Installer output | `dist\ProjectTrackingToolSetup.exe` |
| Install path | `{localappdata}\ATS Inc\Project Tracking Tool` |
| User-data path | `%APPDATA%\ATS Inc\Project Tracking Tool` |
| Current version | `1.8.5` (`version.py`) |
| Build command | `build.bat` — runs README/version sanity check, `py_compile`, `unittest discover`, PyInstaller `--onedir`, Inno Setup, both zips, validates updater zip contains exe + `_internal/` |
| Updater style | **Heavy / 2-constant.** Hardcoded `GITHUB_OWNER` + `GITHUB_REPO` only. Validates `_internal/` exists in zip. Uses separate PowerShell script + batch wrapper. Hardcoded asset-name search `projecttrackingtool.zip` (case-insensitive) with fallback for any non-"fullinstall" zip. |
| Updater payload contract | Full-folder replacement (exe + `_internal/`) |
| Canonical theme source | `phoenix_style.qss` (file at repo root, bundled via `--add-data="phoenix_style.qss;."`) — System A (Phoenix dark navy) |
| Path helper | Inline `_app_data_path()` in `project_tracker_gui.py` (no separate `paths.py`); also `_setup_logging()` with `RotatingFileHandler` to AppData |
| Notable extra build inputs | Bundles `pyxlsb/` package, `PTT_Transparent.png`, `PTT_Normal.ico`, `openpyxl` (hidden import + collect-submodules) |
| Evidence files checked | `installer.iss`, `build.bat`, `updater.py`, `version.py`, `requirements.txt`, `starter_package/CLAUDE.md` (for design-system docs), `starter_package/updater.py` (cleaner template variant), `starter_package/app_gui.py` (template entrypoint), `starter_package/build.bat` (template build) |
| Unknowns / needs verification | (a) Whether the production deploy on user laptops has the exact `1.8.5` artifact or a hotfix beyond that — only `version.py` was read, not a deployed exe's metadata. (b) `tests/` directory contents not enumerated; `unittest discover -s tests` is run by build.bat but the test count and coverage are unknown. (c) Whether `Financials mod/` is shipped in the released installer (it's `.gitignore`d but the build pipeline isn't checked). |

---

## Phoenix_CAD_Tool

| Field | Value |
|---|---|
| App name (display) | Lab Layout Tool |
| Exe name | `LabLayoutTool.exe` |
| GitHub owner | `JustinGlave` |
| GitHub repo | `lab-layout-tool` |
| Release zip asset (updater) | `LabLayoutTool.zip` — **full PyInstaller folder** (exe + `_internal/`) |
| Release zip asset (manual) | `LabLayoutTool_FullInstall.zip` |
| Installer output | `dist\LabLayoutToolSetup.exe` |
| Install path | `{localappdata}\ATS Inc\Lab Layout Tool` |
| User-data path | `%APPDATA%\ATS Inc\Lab Layout Tool` |
| Current version | `0.1.1` (`version.py`) |
| Build command | `build.bat` — pre-flight verifies PyInstaller in `.venv`, reads version via Python, README/version sanity check, `py_compile` (across `app.py` + `ui/*` + `cad/*` + `updater.py`), runs `tools/embed_qss.py` to sync embedded QSS fallback, PyInstaller `--onedir`, Inno Setup, both zips, validates updater zip contains exe + `_internal/` |
| Updater style | **Heavy / 5-constant.** `GITHUB_OWNER`, `GITHUB_REPO`, `EXE_NAME`, `APP_DIR_NAME`, `ZIP_ASSET_NAME` as module-level constants (plus `APP_DISPLAY_NAME`, `USER_AGENT`). Validates `_internal/` exists in zip. Mirrors the project-tracking-tool full-folder replacement pattern. |
| Updater payload contract | Full-folder replacement (exe + `_internal/`) |
| Canonical theme source | `phoenix_style.qss` + embedded fallback in `ui/style.py:63-829`. `ui/style.py:30-58` `apply_dark_theme()` is the canonical loader. System A. |
| Path helper | `paths.py` — `is_frozen()`, `USER_DATA_DIR`, `PROJECT_ROOT`, `JOBS_DIR`, `OUTPUT_DIR`, `LAST_GEN_LOG`, `FIXTURES_DIR`, `TEMPLATES_DIR`, `BLOCKS_DIR`, `CONFIG_PATH`. Hardcoded `ORG_NAME = "ATS Inc"`, `APP_NAME = "Lab Layout Tool"` |
| Notable extra build inputs | Bundles `config/`, `blocks/` (DWG library), `templates/`, `jobs/*.json` fixtures, `LLT_Normal.ico`, `LLT_Transparent.png`; hidden imports `win32com`, `win32com.client`, `pythoncom` (for BricsCAD COM) |
| Evidence files checked | `installer.iss`, `build.bat`, `updater.py` (header), `version.py`, `paths.py`, `ui/style.py`, `ui/components.py`, `requirements.txt`, `requirements-dev.txt` (pinned `pyinstaller==6.20.0`) |
| Unknowns / needs verification | (a) Full contents of `cad/` subsystem and BricsCAD COM call surface — out of retrofit scope per the canonical plan, so left unread on purpose. (b) `tools/embed_qss.py` mechanics — assumed to copy `phoenix_style.qss` into the embedded fallback string but not inspected. (c) `LLT_Normal.ico` vs `Normal_red.ico` icon naming (CAD uses LLT prefix; ValveMaster uses Normal_red); confirm no shared asset cross-contamination. |

---

## Phoenix-Checkout-Tool

| Field | Value |
|---|---|
| App name (display) | Phoenix Valve Checkout Tool |
| Exe name | `PhoenixCheckoutTool.exe` |
| GitHub owner | `JustinGlave` |
| GitHub repo | `Phoenix-Checkout-Tool` (note: capitalised, hyphen-separated — diverges from the kebab-case repo naming on the other tools) |
| Release zip asset (updater) | `PhoenixCheckoutTool.zip` — **EXE-ONLY** (just `PhoenixCheckoutTool.exe`, no `_internal/`) ⚠ |
| Release zip asset (manual) | `PhoenixCheckoutTool_FullInstall.zip` |
| Installer output | `dist\PhoenixCheckoutToolSetup.exe` |
| Install path | `{localappdata}\ATS Inc\Phoenix Valve Checkout Tool` |
| User-data path | `%APPDATA%\ATS Inc\Phoenix Valve Checkout Tool` |
| Current version | `1.7.0` (`version.py`) |
| Build command | `build.bat` — no README/version sanity check, no `py_compile`, no tests. PyInstaller `--onedir`, Inno Setup, exe-only zip + full-folder zip. No artifact verification step. |
| Updater style | **Light / 4-constant** (the "starter_package" pattern). `GITHUB_OWNER`, `GITHUB_REPO`, `ZIP_ASSET_NAME`, `EXE_NAME` as module-level constants. Inline PowerShell embedded in `.bat`. **No `_internal/` validation** — only checks that the asset name matches. |
| Updater payload contract | EXE-only replacement (zip contains just the .exe; `_internal/` is not refreshed by the updater) |
| Canonical theme source | `phoenix_style.qss` (file at repo root, bundled via `--add-data="phoenix_style.qss;."`); loaded inline in `checkout_tool_gui.py`. System A. |
| Path helper | Inline `_app_data_path()` in `checkout_tool_backend.py` — returns `%APPDATA%\ATS Inc\Phoenix Valve Checkout Tool\<filename>`; persists `data.json` there. No separate `paths.py`. |
| Notable extra build inputs | Bundles 5 styled XLSX templates (`checkout_template.xlsx`, `template_gex.xlsx`, `template_mav.xlsx`, `template_cscp_fh.xlsx`, `template_pbc_room.xlsx`); `green.png`, `PTT_Normal_green.ico` |
| Evidence files checked | `installer.iss`, `build.bat`, `updater.py`, `version.py`. **Not read in this phase:** the 177 KB monolithic `checkout_tool_gui.py` (already surveyed previously) and `checkout_tool_backend.py`. |
| Unknowns / needs verification | (a) **Mismatch between this tool's exe-only updater zip and the commons-backed updater's default `expected_internal=True`** — see "Critical asymmetry" below. Retrofit must reconcile this. (b) Absence of any `requirements.txt` is consistent across surveys but unverified for production CI. (c) Whether `dist\PhoenixCheckoutTool.zip` exe-only updaters actually work in the field — historical user reports unknown. (d) Build.bat lacks the artifact-validation step that Job Tracker and Phoenix CAD include; whether production users have ever received a corrupt zip is unknown. |

---

## ValveMasterTool

| Field | Value |
|---|---|
| App name (display) | ValveMasterTool (display name = exe name; no separate human-friendly form) |
| Exe name | `ValveMasterTool.exe` |
| GitHub owner | `JustinGlave` |
| GitHub repo | `valve-master-tool` |
| Release zip asset (updater) | `ValveMasterTool.zip` — **EXE-ONLY** (just `ValveMasterTool.exe`, no `_internal/`) ⚠ |
| Release zip asset (manual) | `ValveMasterTool_FullInstall.zip` |
| Installer output | `dist\ValveMasterToolSetup.exe` |
| Install path | `{localappdata}\ATS Inc\ValveMasterTool` |
| User-data path | `%APPDATA%\ATS Inc\ValveMasterTool` |
| Current version | `1.0.9` (`version.py`) |
| Build command | `build.bat` — reads version via Python, cleans `dist/`, PyInstaller `--onedir`, Inno Setup (Inno is required, not optional), exe-only zip + full-folder zip. No tests, no README check. |
| Updater style | **Light / 3-constant.** `GITHUB_OWNER`, `GITHUB_REPO`, `EXE_NAME` as module-level constants; ZIP asset name is hardcoded inside the search expression (`name.lower() == "valvemastertool.zip"`). Has a `HEADERS` dict. No `_internal/` validation. |
| Updater payload contract | EXE-only replacement |
| Canonical theme source | **Programmatic `QPalette`** (no QSS file). `apply_light_theme()` and `apply_dark_theme()` inline in `valve_master_pyside6.py`. **System B (older `#1c1c1c` dark grey, `#487cff` blue accent) — diverges from the canonical Phoenix dark navy.** |
| Path helper | None visible at the module level; uses `QSettings` for theme preference + window geometry. Installer creates `%APPDATA%\ATS Inc\ValveMasterTool\` (defined in `installer.iss` via `MyAppDataDir`) but the running tool itself does not have a documented JSON-config helper. |
| Notable extra build inputs | Only `version.py` is bundled via `--add-data`. Assets (`Normal_red.ico`, `Transparent_red.png`) are base64-embedded inside `assets.py` — bundled implicitly via PyInstaller's module scan. |
| Inno Setup AppId | `{{A7F3C2D1-9B4E-4F6A-8C3D-1E5B7A9F2C4D}` — **unique GUID, the only tool with one.** Critical for Windows upgrade detection; **must not be changed on retrofit.** |
| Evidence files checked | `installer.iss`, `build.bat`, `updater.py` (header), `version.py`. **Not read in this phase:** `valve_master_pyside6.py` body, `valve_master_backend.py`, `assets.py`. |
| Unknowns / needs verification | (a) Same `expected_internal` mismatch as Phoenix Checkout — exe-only updater payload is incompatible with the commons default. (b) Whether the tool persists any state to disk beyond `QSettings` (e.g., parsed model history) — not visible in the read files. (c) The exact `assets.py` size (large) is known via survey but the impact on PyInstaller build time/exe size is unmeasured. (d) Whether the gray→navy theme retrofit will require any per-widget tweaks or just a theme swap. |

---

## phoenix-command-center

| Field | Value |
|---|---|
| App name (display) | Phoenix Command Center |
| Exe name | n/a — not packaged. Source-run via `python main.py`. |
| GitHub owner | `JustinGlave` (per audit data; not directly verified in this phase) |
| GitHub repo | `phoenix-command-center` (assumed by convention) |
| Release zip asset | n/a |
| Installer output | n/a |
| Install path | n/a |
| User-data path | `pcc_config.json` (stored alongside `main.py` at project root in source-run mode) |
| Current version | `2.0.0` (`version.py`) |
| Build command | n/a — no `build.bat` |
| Updater style | n/a — no `updater.py` |
| Canonical theme source | `theme.py` (Python QSS generator using a `C` dict — different shape from `phoenix_style.qss` file). Used inside the app only. |
| Path helper | n/a — config stored at project root in dev mode |
| Notable | This is the management/scaffolding app, NOT a deployed production tool. Will gain the wizard changes in Phase 5. Eventually a candidate for the same packaging pipeline, but out of scope for the current standard rollout. |
| Evidence files checked | `version.py`; the rest of this repo's structure is already well-known to the operator from earlier sessions. |
| Unknowns / needs verification | (a) Whether `phoenix-command-center` will ever ship as a packaged installer; if so, it inherits the same standard. (b) Whether `pcc_config.json` should migrate to `%APPDATA%\ATS Inc\Phoenix Command Center\` when (if) it gets packaged. |

---

## Critical asymmetry to plan around

**Two distinct updater payload contracts coexist in production.** The four deployed tools split 2/2:

| Tool | Updater zip payload | Validates `_internal/`? |
|------|----------------------|--------------------------|
| Job Tracker | full folder (exe + `_internal/`) | ✓ in both build.bat and updater.py |
| Phoenix CAD Tool | full folder (exe + `_internal/`) | ✓ in both build.bat and updater.py |
| Phoenix Checkout Tool | **exe only** | ✗ |
| ValveMasterTool | **exe only** | ✗ |

Implications for the future commons-backed updater (Phase 3):

- The plan's `download_and_apply(info, exe_name, *, expected_internal=True)` default is correct for the full-folder pattern (Job Tracker + Phoenix CAD) but would break the exe-only pattern (Phoenix Checkout + ValveMaster) if retrofitted directly.
- Two paths forward for the per-tool retrofits, decide per tool:
  1. Pass `expected_internal=False` when porting Phoenix Checkout or ValveMaster — preserves the current exe-only payload contract; users keep getting exe-only updates. Lower risk for the retrofit itself.
  2. Upgrade Phoenix Checkout and ValveMaster's build.bat to ship full-folder updater zips, then pass `expected_internal=True`. More robust long-term (dependency changes between versions are handled) but changes the deployed payload contract — requires explicit user-visible release notes and a tested first-time upgrade.

Recommendation: handle this decision **inside each tool's retrofit PR**, not in the commons API. The commons API is correct as designed; the call site picks the right kwarg for the tool's deployed history.

---

## Conventions confirmed across all four production tools

These are the invariants the commons retrofit must preserve byte-for-byte:

- **Publisher namespace:** `ATS Inc` everywhere (folder names, installer `AppPublisher`, etc.).
- **Install root:** `{localappdata}\ATS Inc\<App Display Name>` (no admin, user-writable so the auto-updater can replace files).
- **User-data root:** `%APPDATA%\ATS Inc\<App Display Name>` (separate from install root so auto-updates don't wipe data).
- **Privilege model:** `PrivilegesRequired=lowest`, `PrivilegesRequiredOverridesAllowed=` (empty or `commandline`).
- **Build pattern:** PyInstaller `--onedir --windowed` → Inno Setup `.iss` (version injected via `/DMyAppVersion=...`) → two zips (updater + full install).
- **Version source:** `version.py` with `__version__ = "X.Y.Z"`; build.bat reads it.
- **Uninstall behaviour:** Inno Setup `[Code]` section prompts the user whether to delete `%APPDATA%\ATS Inc\<App Display Name>\` on uninstall (Job Tracker / Phoenix CAD / Phoenix Checkout / ValveMaster all have this).
- **Updater entry point:** `updater.py` with `check_for_update()` and `download_and_apply()`; called from a background thread.
- **Theme bundling (3 of 4):** `phoenix_style.qss` bundled via `--add-data="phoenix_style.qss;."`. ValveMaster is the lone holdout (programmatic palette).

## Per-tool divergences worth highlighting

- **Job Tracker** and **Phoenix CAD** include CI/sanity checks (`py_compile`, README version match, tests, post-build zip validation). Phoenix Checkout and ValveMaster build.bat files are leaner and skip these.
- **ValveMasterTool** is the only tool with an explicit Inno Setup `AppId` GUID and an inline `MyAppDataDir` constant in its `.iss`.
- **Phoenix Checkout** is the only tool where `MyAppVersion` has a hardcoded fallback default (`1.0.0`) in `installer.iss` — others fail the build if the variable isn't passed.
- **Phoenix Checkout** repo name (`Phoenix-Checkout-Tool`) is the only one using CamelCase + hyphens; the other three use lowercase-kebab-case (`project-tracking-tool`, `lab-layout-tool`, `valve-master-tool`).
- **Job Tracker** uniquely runs `unittest discover -s tests` during build (the others have no tests or skip them in build).
- **Phoenix CAD** uniquely runs `tools\embed_qss.py` during build to keep the embedded-QSS fallback in sync with the canonical QSS file.

---

## Open items beyond the inventory rows

Captured here so they don't get lost during Phase 1+:

1. **Auto-updater zip payload contract** — per-tool decision needed during Phase 7 retrofit (see Critical asymmetry above).
2. **Phoenix Checkout** lacks `requirements.txt`; one will be added during its retrofit. Production CI behaviour without a requirements file is unverified.
3. **ValveMasterTool's `AppId` GUID** must be preserved across retrofit. Document the GUID in this inventory so the value is auditable.
4. **No tool currently has a CI workflow file (`ci.yml`)** — survey says Job Tracker and Phoenix CAD have `.github/workflows/` directories, but this Phase 0 read did not enumerate them. Worth re-checking before Phase 5 templates the wizard's `.github/workflows/ci.yml`.
5. **Job Tracker's `starter_package/`** is documented for deprecation in the canonical plan; this inventory's `Notable` row mentions it so that intent is visible during retrofit.
6. **No git operations were performed** while compiling this inventory (no `git status`, `git log`, no branch creation). Future retrofit PRs must each create their own branch as Phase 1 of that retrofit.

---

## File-write summary for Phase 0

| File created | Path |
|---|---|
| `production-inventory.md` (this file) | `C:\Users\justing\PycharmProjects\phoenix-commons\docs\production-inventory.md` |

| File modified | (none) |
|---|---|
| Production tool source | **None.** Read-only access to `installer.iss`, `build.bat`, `updater.py`, `version.py`, and the relevant theme/path entries only. |
