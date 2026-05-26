# PACKAGING_CONTRACT.md

> What every Phoenix app's installer + updater MUST guarantee. The
> production tools have been shipping under these rules for years —
> this file pins them as the canonical contract so retrofits don't
> accidentally drift.

## Updater payload contracts

Two payload contracts coexist in production. **Both are valid.**
A retrofit must preserve the contract its tool currently ships under.

### Contract A — Full-folder updater (canonical, default)

```
<App>.zip
├── <ExeName>.exe          ← at zip root
└── _internal/             ← full Qt + Python runtime
    ├── ...                  (PyInstaller --onedir output)
    └── ...
```

| Property | Value |
|----------|-------|
| Used by today | Job Tracker, Phoenix CAD (LLT), Phoenix Command Center |
| `expected_internal` kwarg | `True` (default) |
| Validator | `scripts/validate_release_zip.py --require-internal` |
| Update strategy | Extract whole zip into install dir; replaces both exe and `_internal/`. |
| Strengths | Dependency-version changes between releases are handled automatically. Safe for adding/removing bundled assets. |
| Risks | Larger zip (~50 MB typical for PySide6 apps). |

### Contract B — Exe-only updater (legacy, preserved)

```
<App>.zip
└── <ExeName>.exe          ← only file
```

| Property | Value |
|----------|-------|
| Used by today | Phoenix Checkout Tool, ValveMasterTool |
| `expected_internal` kwarg | `False` |
| Validator | `scripts/validate_release_zip.py` (no `--require-internal`) |
| Update strategy | Replace just the exe; `_internal/` from the prior install stays. |
| Strengths | Tiny zips (~10 MB), fast updates. |
| Risks | Breaks if a release adds/removes/upgrades a runtime dependency — the updater silently keeps the old `_internal/`. Recovery is a full reinstall via `<App>_FullInstall.zip`. |

### When each is allowed

| Scenario | Contract |
|----------|----------|
| New Phoenix app from the wizard (any radio) | A (full-folder) — wizard templates default to this. |
| Retrofit of Job Tracker or Phoenix CAD | A — preserves existing payload. |
| Retrofit of Phoenix Checkout or ValveMaster | B — preserves existing payload. Switching to A would require a coordinated user-side full reinstall on first upgrade post-retrofit; not approved without an explicit DECISIONS entry. |
| New app that genuinely needs sub-10MB updates | B — must be a deliberate decision with documented dependency-pinning policy. |

## `_internal/` expectations

| Rule | Why |
|------|-----|
| Must contain everything PyInstaller `--onedir` produces under `dist\<ExeStem>\_internal\` | The exe at root expects this layout at runtime. |
| Must NOT contain user data | The updater wipes `_internal/` on every Contract-A update. |
| Bundled package data (commons QSS, icons) lives under `_internal/<package_path>/` | `paths.resource_path` resolves to here via `sys._MEIPASS`. |

## Installer assumptions (Inno Setup)

| Setting | Required value | Reason |
|---------|----------------|--------|
| `PrivilegesRequired` | `lowest` | Per-user install. No UAC. Auto-updater needs write access; admin install would block it. |
| Install path | `{localappdata}\ATS Inc\<App Display Name>` | All four production tools + PCC share this root. Cross-tool cohabitation matters. |
| User-data path | `{userappdata}\ATS Inc\<App Display Name>` | Separate from install dir so updates don't wipe data. |
| `AppId` | A hard-coded GUID, never changed | Windows uses it to detect upgrades. Changing it orphans every existing install. |
| `MyAppVersion` | Injected by `build.bat` from `version.py` | Single source of truth. |
| Uninstall behaviour | `[Code]` section asks before deleting user data | All 4 production tools do this; commons-backed apps inherit the pattern. |
| `OutputBaseFilename` | `<AppName-no-spaces>Setup` | Canonical installer name (`PhoenixCommandCenterSetup.exe`, `LabLayoutToolSetup.exe`, …). |

## Package-data bundling

| File class | How it's bundled |
|------------|-------------------|
| Commons-owned QSS, embedded fallback, icons | `pyproject.toml` `package-data` declaration **+** `pyinstaller --collect-data phoenix_commons` (planned Phase 3C) |
| App-owned assets (logo, watermark, sprite, screenshots) | App's `build.bat` `--add-data="<src>;<dest>"` flags. PCC bundles: `logo.png`, `logo.ico`, `watermark.png`, `ats_automation_stable_transparent.webp`. |
| Hidden imports (e.g. PySide6 submodules) | App's `build.bat` `--collect-submodules=…` flags. |

The "what does commons own vs the app" answer for any specific
asset is in `COMMONS_SCOPE.md`. The "how to load it at runtime" answer
is `paths.resource_path("...")` — always, no exceptions.

## Resource loading at runtime

| Resource | Lookup |
|----------|--------|
| Commons QSS | `phoenix_commons.theme.apply_dark_theme(app)` — never read the file directly. |
| Commons icon | `phoenix_commons.icons.<name>()` (planned Phase 2.6). |
| App-owned asset | `paths.resource_path("assets/<filename>")`. Resolves under `<app>/assets/` in source mode, `<install>/_internal/assets/` when frozen. |
| User-data file | `paths.user_data_dir(app_name, org_name) / "<filename>"`. |

## Source vs frozen-exe assumptions

| Behaviour | Source mode | Frozen exe |
|-----------|-------------|------------|
| `is_frozen()` | `False` | `True` |
| `user_data_dir(...)` | Project root (next to `main.py`) for dev convenience | `%APPDATA%\<org>\<app>\` |
| `resource_path("assets/x")` | `<project_root>/assets/x` | `<install>/_internal/assets/x` via `_MEIPASS` |
| QSS file lookup | `phoenix_commons/theme/phoenix_style.qss` from package | Same file, repackaged into `_internal/phoenix_commons/theme/` |
| Auto-updater check | Runs but `download_and_apply` raises a clear error if called (no install dir to mutate) | Runs against the live install dir |

`updater.download_and_apply` MUST guard against being called from a
source run: raising a clear `RuntimeError("source mode")` is the
required behaviour (currently implicit; will be made explicit when
PCC migrates to the commons-backed updater).

## Fallback behaviour

| If… | Then… |
|-----|-------|
| Commons QSS file is missing from package | `theme.apply_dark_theme` falls back to the embedded string in `_embedded_qss.py`. App stays themed; logs a warning. |
| Commons icon missing | `icons.<name>()` returns `QIcon()` (empty) + logs a warning. Should never happen if package-data is correct. |
| Updater can't reach GitHub | `check_for_update` returns `None`. App stays on current version. |
| Updater zip fails validation | `download_and_apply` raises `UpdatePackageError`; app shows a "couldn't update — please retry or reinstall" dialog. |
| `_MEIPASS` not set when frozen | Falls back to `Path(sys.executable).parent`. (Edge case; PyInstaller always sets it for `--onedir`.) |

## AV / S1 release gating

This is the single hardest blocker in the platform. See `BLOCKERS.md`
for the full evidence chain. Summary:

| Stage of `build.bat` | AV behaviour observed |
|----------------------|-----------------------|
| PyInstaller writes `<ExeStem>.exe` | Exe present on disk |
| Inno Setup compresses the exe into the installer | Exe still present (Inno read it successfully) |
| Compress-Archive scans dist/ for the auto-updater zip | Exe **gone** — quarantined by S1 between Inno's read and Compress's scan |
| `scripts/validate_release_zip.py` runs | Fails: exe missing from zip |
| build.bat exits non-zero | Correct behaviour — don't ship a broken zip |

Until one of the three resolution paths (IT/S1 allow-list,
Authenticode code-signing, or alternate build host) is in place, **no
release artifact produced on the current developer laptop can be
shipped.** This applies to PCC AND any future retrofit.

## Per-retrofit safety checklist

Every Phase 7/8 retrofit PR must verify, before merge:

```
installer.iss DefaultDirName unchanged       e.g. {localappdata}\ATS Inc\Lab Layout Tool
installer.iss OutputBaseFilename unchanged   e.g. LabLayoutToolSetup
installer.iss AppId GUID unchanged           the exact existing GUID
GitHub Release zip asset name unchanged      e.g. LabLayoutTool.zip
Auto-updater target exe name unchanged       e.g. LabLayoutTool.exe
User-data path unchanged                     %APPDATA%\ATS Inc\<App>
version.py __version__ format unchanged      X.Y.Z
PyInstaller --onedir output contains exe + _internal/
Updater zip contains exe (+ _internal/ if contract A)
Installed app launches from LocalAppData
Existing user data is preserved across upgrade
Upgrade from prior installed release works on a real machine
For Phoenix CAD: cad/ subsystem + BricsCAD COM untouched
For Job Tracker: starter_package/ deletion in same PR
For ValveMaster / Phoenix Master Tool: facade retrofit (≈ 0% visible change per WAVE_8A_VALVEMASTER_PREFLIGHT_AUDIT) — AppId GUID {A7F3C2D1-9B4E-4F6A-8C3D-1E5B7A9F2C4D} preserved byte-for-byte
```

A retrofit PR that fails any checklist item must not merge. The
checklist is per-tool because the values differ; see `NAMING_REGISTRY.md`
for the exact values for each tool.
