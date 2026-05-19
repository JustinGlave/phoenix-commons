# phoenix-commons

> The **Phoenix UI Platform** — shared design system, widgets, path
> helpers, and auto-updater for the Phoenix Controls / ATS Automation
> desktop tool family. Built on PySide6.

[![license: internal-proprietary](https://img.shields.io/badge/license-internal--proprietary-red.svg)](LICENSE)

This is **not a utility grab-bag**. It is the platform contract that
every Phoenix desktop tool depends on. The architecture posture
(ownership, scope, migration rules) lives at
[`docs/ui-platform-baseline-v1/`](docs/ui-platform-baseline-v1/) —
read that directory if you need the canonical answer to any
"who owns what" question.

## What Phoenix UI Platform is

| Provides | API surface |
|----------|-------------|
| Design tokens (palette, typography, spacing, radii) | `phoenix_commons.theme` (formalised in Phase 2.1) |
| Canonical QSS stylesheet | `phoenix_commons.theme.apply_dark_theme(app)` |
| Widget catalog (`PrimaryButton`, `Panel`, `PhoenixTable`, `UpdateBanner`, `NoScroll*`, typography helpers, `button_row`) | `phoenix_commons.widgets` |
| Path helpers (`is_frozen`, `user_data_dir`, `resource_path`) | `phoenix_commons.paths` |
| GitHub-Releases auto-updater (`check_for_update`, `download_and_apply`, `UpdateInfo`, `UpdateCheckThread`) | `phoenix_commons.updater` |
| Base icon set + extension API | `phoenix_commons.icons` (planned Phase 2.6) |

## What commons owns vs what apps own

| Commons owns | Apps own |
|--------------|----------|
| Design tokens, QSS, widgets, paths, updater, icons | App logos, watermarks, splash screens |
| Public widget classes + their `objectName` strings | App-specific widgets (`CommonsDropZone`, `ToolCard`, etc.) |
| Updater code (both full-folder + exe-only payload contracts) | Per-app `OWNER`, `REPO`, `EXE_NAME`, `ZIP_ASSET_NAME` constants |
| Path resolution logic | App-specific `APP_NAME` passed to `user_data_dir` |
| The platform contract itself (this repo) | Business logic + domain models |

Full ownership map: [`docs/ui-platform-baseline-v1/PLATFORM_CONTRACT.md`](docs/ui-platform-baseline-v1/PLATFORM_CONTRACT.md).
Scope rules: [`docs/ui-platform-baseline-v1/COMMONS_SCOPE.md`](docs/ui-platform-baseline-v1/COMMONS_SCOPE.md).

## Current maturity

| Pillar | Source mode | Frozen exe | Production retrofit |
|--------|-------------|------------|---------------------|
| Theme + widgets | ✅ stable | ⚠ blocked (AV) | ⏸ deferred |
| Paths + updater | ✅ stable | ⚠ blocked (AV) | ⏸ deferred |
| Icon infrastructure | ⏸ planned (Phase 2.6) | n/a | ⏸ deferred |
| CI pipeline | ✅ green on push to `main` | n/a | n/a |
| Architecture baseline | ✅ v1 committed at `docs/ui-platform-baseline-v1/` | n/a | n/a |

The package is **source-mode operational** but the commons-backed
build pipeline has not been verified end-to-end on the current
developer laptop due to the corporate AV bootloader-quarantine
issue tracked in [`docs/ui-platform-baseline-v1/BLOCKERS.md`](docs/ui-platform-baseline-v1/BLOCKERS.md).

## Migration philosophy

**Apps extend via addendum, not fork.**

A consuming app may NEVER copy a commons primitive into its own
source tree and modify it locally. Apps extend the platform via:

- **Subclassing** commons widget classes
- **`objectName`-based QSS overrides** (cascade-aware additions,
  never replacing commons-owned selectors)
- **Composition** — combining commons primitives into app-specific
  layouts
- The documented **extension points** per category in
  `PLATFORM_CONTRACT.md`

Why: a fork drifts. Two months later the fork has different padding,
different border radius, different focus state, and the design
system fractures. Subclassing keeps the cascade intact and the
contract enforceable.

Production retrofit order is **pilot-first**:

| Wave | Tools | Phase |
|------|-------|-------|
| Pilot | Phoenix Checkout Tool + Phoenix CAD Tool (Lab Layout Tool) | 7 |
| Wave 8a | ValveMasterTool (visible gray→navy theme swap) | 8a |
| Wave 8b | Job Tracker (largest surface area) | 8b |

Full rules: [`docs/ui-platform-baseline-v1/MIGRATION_RULES.md`](docs/ui-platform-baseline-v1/MIGRATION_RULES.md).

## Current blockers

| # | Blocker | Status |
|---|---------|--------|
| 1 | S1 / corporate AV quarantines PyInstaller bootloaders | Open; gates Phases 4 / 6C / 7 / 8 |
| 2 | Frozen-exe verification | Blocked on #1 |
| 3 | Installer runtime behaviour | Blocked on #2 |
| 4 | Updater runtime behaviour | Blocked on #3 |
| 5 | Commons distribution strategy (submodule vs private PyPI vs GitHub Packages vs vendoring) | Deferred to Phase 9 |
| 6 | Commons CI was missing | ✅ Resolved (this commit set) |
| 7 | Same-disk-only backups | Open; low urgency |

Full detail: [`docs/ui-platform-baseline-v1/BLOCKERS.md`](docs/ui-platform-baseline-v1/BLOCKERS.md).

## Install (development)

```powershell
git clone https://github.com/JustinGlave/phoenix-commons.git
cd phoenix-commons

py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -e .[test]
```

Python 3.12 is the canonical platform version (see
[ADR-014](docs/ui-platform-baseline-v1/DECISIONS.md) for why). Apps
may experiment with newer versions locally; the platform CI and
contracts target 3.12.

```python
from phoenix_commons import __version__
from phoenix_commons.theme import apply_dark_theme
from phoenix_commons.widgets import PrimaryButton, Panel, PhoenixTable
from phoenix_commons.paths import is_frozen, user_data_dir, resource_path
from phoenix_commons.updater import check_for_update, download_and_apply
```

## Layout

```
phoenix-commons/
├── pyproject.toml
├── README.md / LICENSE / SECURITY.md / CODE_OF_CONDUCT.md
├── src/phoenix_commons/                 ← the installable package
│   ├── theme/                            ← apply_dark_theme + phoenix_style.qss + embedded fallback
│   ├── widgets/                          ← public widget catalog
│   ├── paths.py                          ← is_frozen / user_data_dir / resource_path
│   └── updater/                          ← client / installer / Qt-aware thread
├── tests/                                ← smoke tests (compileall + pytest in CI)
├── docs/
│   ├── ui-platform-baseline-v1/          ← canonical architecture snapshot
│   ├── rollout/                          ← Phase 1–6C rollout reports (historical)
│   ├── production-inventory.md           ← Phase 0 deliverable
│   ├── phase-1-completion-packet.md      ← Phase 1 deliverable
│   └── phase-1-report.md                 ← Phase 1 deliverable
└── .github/
    └── workflows/ci.yml                  ← Python 3.12 + compileall + pytest
```

## Versioning

Tracked in `src/phoenix_commons/_version.py`. Bumped alongside any
public-API change. Currently `0.1.0` (Phase 1 baseline).

## Development

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -e .[test]

# Smoke verification:
.\.venv\Scripts\python.exe -m compileall -q .
.\.venv\Scripts\python.exe -m pytest -q tests/
```

CI runs the same two commands on Windows / Python 3.12 on every
push to `main` and any pull request.

## License

This is **internal ATS Automation tooling** — see [`LICENSE`](LICENSE)
for the full proprietary-use language. Not open source. Do not
redistribute, publish source, or describe in public material without
written approval from ATS Automation. See [`SECURITY.md`](SECURITY.md)
for reporting security concerns through internal channels.
