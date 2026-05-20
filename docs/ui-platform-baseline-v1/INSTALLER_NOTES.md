# INSTALLER_NOTES.md

> Inno Setup conventions, wizard artwork specifications, and AppId
> hygiene for Phoenix tool installers. Companion to `RELEASE_CHECKLIST.md`
> and `FROZEN_BUILD_BASELINE.md`.
>
> Documentation only — this file does not execute or modify any installer.
> The four production tools' `installer.iss` files are the source of truth
> for what's currently shipping; this document captures the conventions
> that hold across them and the gaps that future polish should close.
>
> **Build prerequisite (codified 2026-05-20)**: the upstream PyInstaller
> step that feeds Inno Setup MUST run under the frozen-build baseline —
> Python 3.12 build venv, pinned PyInstaller 6.20.0, pinned PySide6 6.10.2,
> hardened build.bat (`--noupx` + stdlib excludes). See
> `FROZEN_BUILD_BASELINE.md`. Inno Setup's job is unchanged by this
> baseline; the baseline keeps the bootloader exe alive long enough for
> Inno Setup to compress it into Setup.exe.

## Installer mechanics — Inno Setup

All four production Phoenix tools use **Inno Setup 6** (Jordan Russell
Software). The pattern:

```
build.bat
  └─→ Python 3.12 venv (frozen-build baseline)
       └─→ PyInstaller --onedir --windowed --noupx → dist\<AppName>\
            └─→ ISCC installer.iss → dist\<AppName>Setup.exe
                 └─→ powershell Compress-Archive → dist\<AppName>.zip (updater)
                      + dist\<AppName>_FullInstall.zip (manual install)
```

### Required directives (all tools)

| Directive | Value | Reason |
|-----------|-------|--------|
| `AppName` | App display name (e.g. `Lab Layout Tool`) | Shown in Add/Remove Programs and the installer titlebar. |
| `AppVersion` | `{#MyAppVersion}` from `/DMyAppVersion=` | Build.bat passes `version.py`'s value. |
| `AppPublisher` | `ATS Inc` | Consistent across all tools. **Do not vary spelling** (not "ATS Inc.", not "ATS Automation" for production tools — see Branding Asset Guide § Organization names). |
| `DefaultDirName` | `{localappdata}\ATS Inc\<App Display Name>` | User-writable so the auto-updater can replace files without admin. |
| `PrivilegesRequired` | `lowest` | Installs to LocalAppData, not Program Files. |
| `PrivilegesRequiredOverridesAllowed` | (empty or `commandline`) | Locks down the install path. |
| `OutputBaseFilename` | `<ExeName>Setup` (e.g. `LabLayoutToolSetup`) | Auto-updater + release-doc filename convention. |
| `SetupIconFile` | `<color>.ico` (e.g. `LLT_Normal.ico`) | Installer titlebar + Add/Remove Programs icon. |
| `Compression` | `lzma2/ultra` (typical) | Smaller installer downloads. |
| `SolidCompression` | `yes` | Better compression ratio for the `_internal/` Qt DLLs. |

### Recommended directives (currently inconsistent — see § "Gaps")

| Directive | Recommended value | Status |
|-----------|-------------------|--------|
| `AppId` | A unique GUID per tool, fixed for the lifetime of the tool | Only ValveMaster has one (`{{A7F3C2D1-9B4E-4F6A-8C3D-1E5B7A9F2C4D}`). The other three rely on the install-path fingerprint. |
| `WizardImageFile` | 164 × 314 BMP, Phoenix dark navy with app's color accent | **No tool has one** (ValveMaster has the directive but the value is empty). All four installers show Inno Setup's default blue/green gradient. |
| `WizardSmallImageFile` | 55 × 58 BMP, app's color logo | Same status as above — not set on any tool. |
| `VersionInfoVersion` | `{#MyAppVersion}` | Sets the file-version metadata on the Setup.exe itself. Some tools have it, some don't. |
| `VersionInfoCompany` | `ATS Inc` | Same — partial coverage. |
| `UninstallDisplayIcon` | `{app}\<ExeName>.exe` | So the uninstaller entry in Add/Remove Programs shows the app icon. Status varies. |

### Forbidden directives

| Directive | Why forbidden |
|-----------|---------------|
| `AppId` (changing) | Changing `AppId` on a tool that has shipped will orphan every existing install. New version installs alongside the old one. **Hard rule** — see MIGRATION_RULES § Stop conditions. |
| `DefaultDirName` (changing) | Same — moves the install to a new path; old install lingers. |
| `PrivilegesRequired=admin` | Forces UAC. Phoenix tools install per-user to avoid this. |

## AppId management

`AppId` is Inno Setup's stable identity for the tool — the value
Windows uses to recognise an upgrade vs a side-by-side install. The
default (no explicit `AppId`) is derived from the `AppName` and
install path, which happens to be stable for our tools because we
never change those. But the **right** practice is to set an explicit
GUID:

```
[Setup]
AppId={{A7F3C2D1-9B4E-4F6A-8C3D-1E5B7A9F2C4D}
```

(Note the **double brace** at the start — Inno Setup uses `{` for
its own constant syntax, so a literal `{` in a value is escaped as `{{`.)

### Generating a GUID for a new tool

```powershell
[guid]::NewGuid().ToString("B").ToUpper()
```

Returns e.g. `{A7F3C2D1-9B4E-4F6A-8C3D-1E5B7A9F2C4D}` — prefix with
an extra `{` when writing into `installer.iss`.

### When to set AppId for an existing tool

**Never, unless the tool has never shipped.** Setting `AppId` for the
first time on an already-deployed tool changes the identity Inno
Setup associates with the install — the next installer treats it as
a new product, leaves the old install on disk, and creates a second
entry in Add/Remove Programs.

If you want to retrofit an explicit `AppId` for the three tools that
don't have one, the only safe approach is:

1. Compute what GUID Inno Setup is currently deriving from the
   tool's `AppName` + `DefaultDirName` (Inno Setup's docs describe
   the derivation; reproduce it exactly).
2. Set that derived GUID as the explicit `AppId`.
3. Test the upgrade path from the previous shipped installer.

This is risky enough that the recommendation is: **leave the three
implicit-AppId tools alone** until they're ever rebuilt from a clean
install path.

## Wizard artwork (currently missing)

Inno Setup's wizard window shows two images by default — both are
*placeholders* the installer ships with, looking nothing like
Phoenix's brand:

- **Large image** (left side of wizard pages 1 + 2): 164 × 314 px,
  bitmap (`.bmp`, NOT png). Specified via `WizardImageFile=`.
- **Small image** (top-right of every wizard page): 55 × 58 px,
  bitmap. Specified via `WizardSmallImageFile=`.

### Specifications for Phoenix tools

| Property | Large | Small |
|----------|-------|-------|
| Dimensions | 164 × 314 px | 55 × 58 px |
| Format | 24-bit BMP (8-bit indexed also works) | 24-bit BMP |
| Background | Phoenix dark navy `#0a0e27` (solid) | Same |
| Foreground | App's color logo, centered vertically, sized so the logo's bounding box is ~70% of the smaller dimension | App's color logo, centered, filling ~70% of the 55 × 58 frame |
| Text | None on the large image; the small image is too tight for text | — |
| Bleed | None — Inno Setup centers the bitmap as-is with no scaling | — |

When commissioned: produce **four large images and four small images**,
one set per tool color (orange / green / blue / red). Store them in
each tool's `installer-assets/` folder (a new convention — see
`BRANDING_ASSET_GUIDE.md` § "Recommended folder layout"). Add to
`installer.iss`:

```
[Setup]
WizardImageFile=installer-assets\wizard.bmp
WizardSmallImageFile=installer-assets\wizard-small.bmp
```

And to `build.bat`'s PyInstaller line — these are NOT bundled into
the exe; they're only needed at Inno Setup compile time, so they
stay outside `--add-data=`.

## Code signing (currently not in scope)

None of the four production tools is currently code-signed.
Consequences:

- SmartScreen / Defender shows a "Windows protected your PC" prompt
  on first run, until the install's reputation accrues.
- Some antivirus products quarantine PyInstaller-onedir builds
  unsigned (this has happened to Phoenix CAD historically).

Signing is **out of scope** for the current operational stabilization
window — it requires:

1. A code-signing certificate (DigiCert / Sectigo, ~USD 400/year for
   an Organization Validation cert that doesn't trigger UAC; ~USD 1000+
   for an Extended Validation cert that does build reputation faster).
2. A signing rig — typically a HSM (hardware security module) or
   USB token; modern requirements rule out file-based keys.
3. Updates to `build.bat` to invoke `signtool sign /tr ... /fd SHA256
   /a dist\<App>\<ExeName>.exe` after PyInstaller and before Inno
   Setup; then again on the installer itself after ISCC.

When ready to sign:

- Decide OV vs EV (cost vs UX trade-off).
- Document the certificate's expiry + renewal contact in this file.
- Update `RELEASE_CHECKLIST.md` § "Build" with a "signed?" step.
- Verify the signed installer + exe in a clean Win10/Win11 VM.

## Tool-specific installer notes

### Job Tracker / Project Tracking Tool

- `installer.iss` includes a `[Code]` section that prompts the user
  on uninstall whether to delete `%APPDATA%\ATS Inc\Project Tracking
  Tool\`. Default: keep (so accidental uninstall during upgrade
  doesn't lose data).
- Build also bundles a `Project Tracking Tool - User Guide.pdf`
  alongside the exe. PDF lives at repo root; gitignored.

### Phoenix CAD / Lab Layout Tool

- Bundles a `blocks/` DWG library (large — several MB) via PyInstaller
  `--add-data`; consequently the installer is the biggest of the four.
- Includes a fixture-jobs directory (`jobs/*.json`) for demo content.
- `tools/embed_qss.py` runs during `build.bat` to keep the in-code
  embedded QSS fallback in sync with `phoenix_style.qss`. The
  embedded fallback only kicks in if `phoenix_style.qss` isn't in
  `_internal/` (defence in depth against a broken bundle).

### Phoenix Checkout / Phoenix Valve Checkout Tool

- Updater zip is **exe-only** (just `PhoenixCheckoutTool.exe`, no
  `_internal/`) — per ADR-003. Build.bat's zip step must NOT include
  `_internal/`. Auto-updater's `apply_update` extracts only the exe.
- Installer includes 5 styled XLSX templates
  (`checkout_template.xlsx` + 4 product-line variants); bundled via
  `--add-data`, copied to `{app}` by Inno Setup.

### ValveMaster / Valve Master Tool

- Only tool with an explicit `AppId` GUID. **Must not be changed.**
- Updater zip is **exe-only** (same as Checkout).
- Brand assets (`Normal_red.ico`, `Transparent_red.png`) are
  base64-embedded in `assets.py` — PyInstaller bundles them implicitly
  via the module scan, no `--add-data` entry. This makes the build
  slightly leaner but means the assets can't be swapped without a
  code change. Documented as a Phase 8a retrofit consideration.

## Gaps to close during future installer polish

Not in scope for the current operational-stabilization window, but
worth knowing about:

1. **Set explicit `AppId` GUIDs** for the three tools that don't
   have one (Job Tracker, Phoenix CAD, Phoenix Checkout). Requires
   matching Inno Setup's derivation algorithm; see § "AppId management"
   above. Risk: install collision if the derivation is wrong.
2. **Ship wizard artwork** for all four tools. Requires brand-design
   work + creating each tool's `installer-assets/` folder. No runtime
   risk; purely cosmetic.
3. **Add `VersionInfoCompany=ATS Inc`** to every `installer.iss`
   (some tools omit this — File Properties on the installer exe
   then shows blank "Company"). Trivial; no risk.
4. **Add `UninstallDisplayIcon={app}\<ExeName>.exe`** so the
   uninstaller in Add/Remove Programs uses the app icon, not the
   default. Trivial; no risk.
5. **Add code signing** — see § "Code signing" above for the full
   prep list.
6. **Standardize the uninstall prompt** for user-data deletion across
   all four tools (Phoenix CAD doesn't have one; the other three do).

## See also

- `RELEASE_CHECKLIST.md` — full release procedure.
- `VERSIONING_POLICY.md` — when MAJOR / MINOR / PATCH applies.
- `BRANDING_ASSET_GUIDE.md` — icon / wizard image sourcing.
- `production-inventory.md` (one level up in `docs/`) — frozen
  snapshot of each tool's installer config.
- `FROZEN_BUILD_BASELINE.md` — canonical frozen-build configuration
  that produces the bootloader Inno Setup compresses.
- `DECISIONS.md` § ADR-014 — Python 3.12 as the platform canonical
  version (build venv mandate).
- `BUILD_HARDENING_EXPERIMENT_REPORT_03.md` — empirical evidence
  that Python 3.14 bootloaders trigger S1 quarantine while 3.12
  bootloaders do not.
- `BLOCKERS.md` § 1 — S1 quarantine blocker history.
