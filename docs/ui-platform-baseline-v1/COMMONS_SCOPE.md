# COMMONS_SCOPE.md

> What belongs in `phoenix-commons`, what doesn't, what stays
> app-local. Hard scope. Used to evaluate every PR that would add to
> commons.

## Belongs in commons

| Category | Examples | Rationale |
|----------|----------|-----------|
| Design tokens | `C['accent']`, font family, spacing scale, radii | Single source of truth for the design system |
| Canonical QSS | `phoenix_style.qss` + embedded fallback | Drives every Phoenix app's chrome |
| Theme apply entry point | `apply_dark_theme(app)` | One way to install the theme |
| Reusable widgets | `PrimaryButton`, `Panel`, `PhoenixTable`, `UpdateBanner`, `NoScroll*` family, typography helpers | Used by 2+ apps with identical behaviour |
| Path helpers | `is_frozen`, `user_data_dir`, `resource_path` | Same logic every app needs |
| Updater client | `check_for_update`, `download_and_apply`, `UpdateInfo`, `UpdateCheckThread` | Same GitHub-Releases pattern every app uses |
| Base icon set | refresh, settings, search, info, warning, error, success, chevron (Phase 2.6) | Generic UI chrome shared across apps |
| Release-zip validator | `scripts/validate_release_zip.py` template | Shipped with every wizard scaffold; same logic across apps |
| Build-pipeline templates | Standalone + commons-backed scaffold templates in PCC's wizard | These ARE the contract for new apps |

**Rule of thumb:** if **two or more shipping apps** would use it
verbatim, it belongs in commons.

## Never belongs in commons

| Category | Examples | Rationale |
|----------|----------|-----------|
| App logos | PCC's `logo.png`, Phoenix CAD's `LLT_Transparent.png`, Job Tracker's `PTT_Normal.png` | Brand identity is per-app. Commons is the platform, not the brand. |
| App-specific business logic | Job Tracker's `RotatingFileHandler` config, Phoenix CAD's BricsCAD COM bridge, Phoenix Checkout's Excel sheet templates | Domain-specific code stays with its domain |
| App-specific widgets | `CommonsDropZone`, `SidebarSprite`, `ToolCard`, `ValveTypeBadge` | Used by one app only |
| App config files | `pcc_config.json` schema, Job Tracker's job-list JSON shape | App-internal data structures |
| Per-app GitHub URLs / repo metadata | constants like `GITHUB_OWNER`, `GITHUB_REPO`, `EXE_NAME`, `ZIP_ASSET_NAME` | App identity, passed in as kwargs to commons APIs |
| Test fixtures for an app's business logic | Phoenix CAD's `jobs/*.json` fixtures, Job Tracker's `tests/test_excel_parsing.py` | App-internal correctness |
| Bundled XLSX / DWG / domain-format files | Phoenix Checkout's 5 styled XLSX templates, Phoenix CAD's `blocks/*.dwg` library | App data, not platform code |
| Programmatic palettes from legacy apps | ValveMaster's `apply_dark_theme()` with the gray palette | "System B" is being phased out; not lifted into commons |
| Secrets / API keys / credentials | n/a (Phoenix apps don't currently have any) | Even if they did, they wouldn't go in commons |

**Rule of thumb:** if an app's name, business domain, or
deployment-specific identity is in the value, it stays app-local.

## Stays app-local (but follows commons conventions)

| Category | Why it stays local | What commons provides anyway |
|----------|--------------------|-------------------------------|
| App's `main.py` | Entry point is app-specific | The conventions in DESIGN_SYSTEM / PLATFORM_CONTRACT |
| App's `version.py` | App version is app-specific | The X.Y.Z format convention |
| App's `build.bat` | Bundling app assets is per-app | A canonical template (in PCC wizard) the app starts from |
| App's `installer.iss` | AppId GUID, install path, asset list are per-app | A canonical template |
| App's `requirements.txt` | App's runtime deps include PySide6 + (eventually) `-e ./commons` | Pinning conventions |
| App's `.github/workflows/ci.yml` | Job names, secrets, asset uploads per-app | CI workflow template |
| App's `tests/` | Tests cover app-specific behaviour | A smoke-test template the wizard scaffolds |

## Decision matrix

Use this when in doubt whether a thing belongs in commons:

| Question | If YES | If NO |
|----------|--------|-------|
| Does 2+ Phoenix apps use this verbatim? | Candidate for commons | Stays app-local |
| Does it encode the app's identity, domain, or branding? | App-local only | Continue checking |
| Does it bind to a specific GitHub repo / asset name / install path? | App-local; pass as kwarg into a commons helper if needed | Continue checking |
| Does it depend on app-specific files at runtime? | App-local (commons doesn't know about app files) | Continue checking |
| Is its public API stable, or still evolving fast? | Stable → commons; unstable → keep in one app until it settles | n/a |
| Could a future Phoenix app reasonably want it? | Commons | App-local |

## Examples worked through

### "Phoenix CAD has a 'rotating file handler' for logs — should it go in commons?"

| Check | Answer |
|-------|--------|
| 2+ apps use verbatim? | Yes — Job Tracker has a similar one. |
| Encodes app identity? | No — purely a logging helper. |
| Binds to app-specific names? | The file path does, but that's a kwarg. |
| App-specific runtime deps? | No. |
| API stable? | Yes — this pattern is well-understood. |

→ **Candidate for commons.** Goes into `phoenix_commons.logging` or
similar in a future phase (not currently planned; would need a
two-app-needs ratio observed first).

### "Job Tracker bundles `pyxlsb` for Excel parsing — should commons own it?"

| Check | Answer |
|-------|--------|
| 2+ apps use verbatim? | No — Phoenix Checkout uses `openpyxl` differently. |
| Encodes app identity? | No, but very domain-specific. |
| Binds to app names? | No, but binds to app data shapes. |

→ **App-local.** Commons stays out of Excel parsing entirely.

### "ValveMaster's `Normal_red.ico` — should it migrate to a commons icon library?"

| Check | Answer |
|-------|--------|
| 2+ apps use verbatim? | No. It's ValveMaster-specific branding. |
| Encodes app identity? | **Yes** — the red colour is part of ValveMaster's mark. |

→ **App-local.** Commons icon library only has generic chrome icons
(refresh, settings, etc.), never app marks.

### "The 'NoScrollComboBox' pattern — should it be in commons?"

| Check | Answer |
|-------|--------|
| 2+ apps use verbatim? | Yes — Phoenix CAD, Job Tracker, and future tools all need scroll-wheel-safe combos. |
| Encodes app identity? | No. |
| Binds to app names? | No. |
| Stable API? | Yes — `QComboBox` subclass with `wheelEvent` overridden. |

→ **Already in commons** as `phoenix_commons.widgets.no_scroll`. ✓

### "PCC's `phoenix_tool_templates.py` (the wizard scaffolder) — does this belong in commons?"

| Check | Answer |
|-------|--------|
| 2+ apps use verbatim? | No. Only PCC uses it. |
| Encodes app identity? | No, but it's PCC's core feature. |
| Stable API? | Yes (Phase 5/5A/5B). |

→ **App-local in PCC.** PCC IS the management hub; the wizard is its
business logic. Other Phoenix apps don't scaffold things.

## Anti-scope (the things commons is NOT)

- Not a kitchen sink of utility functions. If a function isn't
  visibly tied to the UI platform or the packaging contract, it
  doesn't belong here.
- Not a place for app-internal abstractions that "feel reusable but
  aren't actually reused yet."
- Not a versioning escape hatch — every commons release affects all
  apps simultaneously, so the bar for adding/changing things is
  high.
- Not a Python utility library (no `collections.OrderedDict`-style
  helpers).
- Not a Qt extension library (no `QStandardItemModel` subclasses
  unless 2+ apps need them).

## Scope review cadence

`COMMONS_SCOPE.md` is reviewed at the start of every phase that
proposes a commons change. If a phase wants to add something to
commons, the PR description must include the decision-matrix answers
above. If the matrix says "app-local," the PR is rejected.

The author of each Phase 7+ retrofit PR also reviews this file before
opening the PR.
