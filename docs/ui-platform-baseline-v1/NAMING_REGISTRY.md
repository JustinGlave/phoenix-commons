# NAMING_REGISTRY.md

> Canonical names. Single source of truth for every identifier that
> survives outside this repo (installer names, GitHub asset names,
> object names, branch conventions, etc.). Changing any value in
> this file is a contract-breaking change.

## Per-tool identity table

| pcc_config key | Display name (Inno `AppName`) | Exe | Installer | Updater zip asset | Install path | User-data path | GitHub repo | AppId GUID | Updater contract |
|---|---|---|---|---|---|---|---|---|---|
| `Job Tracker` | `Project Tracking Tool` | `ProjectTrackingTool.exe` | `ProjectTrackingToolSetup.exe` | `ProjectTrackingTool.zip` | `{localappdata}\ATS Inc\Project Tracking Tool` | `%APPDATA%\ATS Inc\Project Tracking Tool` | `JustinGlave/project-tracking-tool` | (existing — verify before retrofit) | **A** full-folder |
| `Phoenix_CAD_Tool` | `Lab Layout Tool` | `LabLayoutTool.exe` | `LabLayoutToolSetup.exe` | `LabLayoutTool.zip` | `{localappdata}\ATS Inc\Lab Layout Tool` | `%APPDATA%\ATS Inc\Lab Layout Tool` | `JustinGlave/lab-layout-tool` | (existing — verify) | **A** full-folder |
| `Phoenix-Checkout-Tool` | `Phoenix Valve Checkout Tool` | `PhoenixCheckoutTool.exe` | `PhoenixCheckoutToolSetup.exe` | `PhoenixCheckoutTool.zip` | `{localappdata}\ATS Inc\Phoenix Valve Checkout Tool` | `%APPDATA%\ATS Inc\Phoenix Valve Checkout Tool` | `JustinGlave/Phoenix-Checkout-Tool` | (existing — verify) | **B** exe-only |
| `ValveMasterTool` | `ValveMasterTool` (display = exe name) | `ValveMasterTool.exe` | `ValveMasterToolSetup.exe` | `ValveMasterTool.zip` | `{localappdata}\ATS Inc\ValveMasterTool` | `%APPDATA%\ATS Inc\ValveMasterTool` | `JustinGlave/valve-master-tool` | `{{A7F3C2D1-9B4E-4F6A-8C3D-1E5B7A9F2C4D}` | **B** exe-only |
| `phoenix-command-center` | `Phoenix Command Center` | `PhoenixCommandCenter.exe` | `PhoenixCommandCenterSetup.exe` | `PhoenixCommandCenter.zip` | `{localappdata}\ATS Inc\Phoenix Command Center` | `%APPDATA%\ATS Inc\Phoenix Command Center` | `JustinGlave/phoenix_command_center` | `{B6E4A1F2-3D5C-4B7A-9E1F-8C2D5A7B9E4F}` | **A** full-folder |

The four production AppId GUIDs other than ValveMaster's are baked
into each tool's `installer.iss` and are non-public-facing; the
retrofit must verify (read-only) and copy them verbatim. Do not
regenerate. ValveMaster's is recorded here because the Phase 0
inventory captured it; the others should be added to this row
during pilot prep.

## Commons-owned object names

| objectName | Used by widget | Used by app QSS |
|------------|----------------|------------------|
| `accentBtn`        | `PrimaryButton` and PCC's `New Tool` button | Orange accent fill. |
| `ghostBtn`         | `SecondaryButton`, `TertiaryButton` | Gray ghost. |
| `appTitle`         | (deprecated; use `pageTitle`) | n/a |
| `accentTitle`      | PCC's `Phoenix` sidebar word | Phoenix orange. |
| `pageTitle`        | `PageTitle` | Large heading. |
| `sectionHeader`    | section labels (sidebar `NAVIGATION` / `TOOLS`) | Small uppercase muted. |
| `statValue`        | `AggregateTile` numeric value | Large bold. |
| `statLabel`        | `AggregateTile` text label | Small uppercase muted. |
| `statCard`         | `AggregateTile` outer frame | Card background + border. |
| `cardTitle`        | `Panel` heading | Bold panel title. |
| `cardStat`         | `Panel` numeric inset | Body weight in card colour. |
| `commitMsg` / `commitWhen` | activity-row text in PCC dashboard | Body / muted. |
| `sidebar`          | the sidebar QFrame | Sidebar background + right border. |
| `topbar`           | the logo strip at top of sidebar | Slightly darker than sidebar. |
| `sidebarList`      | `QListWidget` for nav items | Nav-list QSS rules. |
| `sidebarSprite`    | PCC's animated sprite frame | Transparent. |

App-local `objectName` strings must NOT collide with this set.
If an app needs a similar look but different rules, use a
distinct name (e.g. `appHeader` for app-specific headers vs
`pageTitle` for the canonical one).

## Commons-owned token names

Will be formalized in Phase 2.1. Working set today:

```
C['bg']           #18181F
C['surface']      #21212E
C['sidebar']      #1C1C2A
C['card']         #27273A
C['card_hover']   #2E2E42
C['card_sel']     #32324A
C['border']       #34344A
C['border_hi']    #4A4A68

C['accent']       #E8783C   ← Phoenix orange
C['accent_dark']  #C05E28
C['accent_glow']  rgba(232, 120, 60, 0.18)
C['teal']         #3CB8AE
C['teal_dark']    #2A8880

C['text']         #E4E4F0
C['text_sub']     #9090B0
C['text_muted']   #58587A
C['text_inv']     #18181F

C['success']      #4EC47A
C['warning']      #F0A030
C['error']        #E84848

C['btn_default']  #2E2E42
C['btn_hover']    #3A3A52
C['scrollbar']    #2E2E42
C['scrollbar_h']  #4A4A68
```

Naming rules:

| Rule | Example |
|------|---------|
| Background / surface tokens are descriptive of role | `bg`, `surface`, `sidebar`, `card`, not `dark1` / `dark2` |
| Text tokens are descriptive of contrast | `text`, `text_sub`, `text_muted`, `text_inv` |
| Status tokens are semantic | `success`, `warning`, `error` (never `green`, `orange`, `red`) |
| Variant suffixes use `_hover`, `_dark`, `_glow`, `_sel`, `_hi` (descending tier) | `card_hover`, `border_hi` |
| Brand colours stay branded | `accent` = Phoenix orange; `teal` = Phoenix teal |

## Branch naming

| Branch class | Convention | Examples |
|--------------|------------|----------|
| Long-running rollout (historical) | `phase-<n>-<topic>` | `phase-4-pyinstaller-compatibility` |
| Architecture baseline / docs | `baseline-<vN>` or `docs-<topic>` | `baseline-v1` (this branch) |
| Feature work in an app | `feature-<topic>` | `feature-command-center-gui-polish` |
| Packaging / branding work in an app | `feature-<app>-branding-packaging` | `feature-command-center-branding-packaging` |
| CI / smoke / infrastructure fixes | `fix-ci-<topic>` or `fix-<topic>` | `fix-ci-smoke-tests` |
| Production retrofit | `retrofit-<tool-slug>` | `retrofit-phoenix-checkout`, `retrofit-job-tracker` |
| Bug fix on a release | `hotfix-<topic>` | `hotfix-updater-zip-validation` |

Branches are kept on origin after merge for audit until explicitly
deleted. Deletion is fine once the work is at least one release-cycle
old.

## Release naming

| Release class | Tag pattern | Asset names |
|---------------|-------------|-------------|
| Phoenix Command Center | `pcc-vX.Y.Z` or `vX.Y.Z` | `PhoenixCommandCenterSetup.exe`, `PhoenixCommandCenter.zip`, `PhoenixCommandCenter_FullInstall.zip` |
| Job Tracker | `vX.Y.Z` | `ProjectTrackingToolSetup.exe`, `ProjectTrackingTool.zip`, `ProjectTrackingTool_FullInstall.zip` |
| Phoenix CAD (Lab Layout Tool) | `vX.Y.Z` | `LabLayoutToolSetup.exe`, `LabLayoutTool.zip`, `LabLayoutTool_FullInstall.zip` |
| Phoenix Checkout Tool | `vX.Y.Z` | `PhoenixCheckoutToolSetup.exe`, `PhoenixCheckoutTool.zip`, `PhoenixCheckoutTool_FullInstall.zip` |
| ValveMasterTool | `vX.Y.Z` | `ValveMasterToolSetup.exe`, `ValveMasterTool.zip`, `ValveMasterTool_FullInstall.zip` |
| phoenix-commons | `commons-vX.Y.Z` | (none — package only; no installer) |

Three-digit semver (`X.Y.Z`). No `v` prefix inside `version.py`'s
`APP_VERSION` constant; the tag MAY include it. The updater
normalises both.

## Package naming

| Python package | PyPI name (if/when published) | Top-level import |
|----------------|--------------------------------|------------------|
| `phoenix-commons` | `phoenix-commons` (claimed; not yet published) | `phoenix_commons` |
| `phoenix-command-center` | not published — installed as exe | `phoenix_command_center` is not a package; flat-layout app |
| (production tools) | not published — installed as exe | n/a |

## File naming conventions

| File class | Convention |
|------------|------------|
| Phase rollout reports | `docs/rollout/phase-<n>-<topic>-report.md` |
| Architecture baselines | `docs/<topic>-baseline-v<N>/...` |
| Build automation | `build.bat`, `installer.iss` at repo root |
| Smoke tests | `tests/test_smoke.py` plus `tests/conftest.py` |
| Per-feature integration tests | `tests/test_<feature>.py` |
| Helper scripts | `scripts/<verb>_<noun>.py` (e.g. `validate_release_zip.py`) |
| Assets | `assets/<filename>` — never bare repo-root assets |

## What's NOT in this registry

This file pins names that survive outside the repo. Internal symbols
(function names, variable names, etc.) are not contract-bound and
can change without listing here. The line is:

| Internal (no entry needed) | External (must be in this file) |
|----------------------------|---------------------------------|
| Python function / method names | Installer name, exe name, zip asset name |
| Internal helper class names | Widget public class names (`PrimaryButton`, etc.) |
| Local variable names | Token dict keys (`C['accent']`, etc.) |
| Internal CSS class names | `objectName` strings |
| Test names | Branch / tag naming conventions |
