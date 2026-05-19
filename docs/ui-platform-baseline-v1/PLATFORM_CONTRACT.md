# PLATFORM_CONTRACT.md

> Who owns what. The single source of truth for every primitive in
> the Phoenix UI Platform. If a concept appears here it has **exactly
> one owner** — duplication is a defect.

## Core principle

**Apps extend via addendum, not fork.**

A retrofit may NEVER:

- Copy a commons primitive into the app source tree and modify it.
- Rebuild a commons primitive from scratch under a different name.
- Re-implement design tokens, widget classes, or update logic.

A retrofit MAY:

- **Subclass** a commons widget to add app-specific behaviour
  (`class JobTrackerToolbar(Panel): ...`).
- **Override** an `objectName` to apply app-local QSS rules on top
  of the commons stylesheet (cascade-aware additions only — never
  override commons-owned selectors).
- **Compose** commons primitives into app-specific layouts.
- **Extend** commons via the explicit extension points documented
  per category below.

## Ownership map

### 🎨 Theme tokens (palette, typography, spacing, radii)

| Aspect | Owner | Extension point |
|--------|-------|------------------|
| Hex values for `bg`, `surface`, `card`, `border`, `accent`, `teal`, status colours, text colours | `phoenix_commons.theme.tokens` (planned Phase 2.1) | Apps **do not** add tokens. New shared tokens go through a commons PR. |
| Font family + weight ramp | `phoenix_commons.theme.tokens` | Same — commons-owned. |
| Spacing constants (gutter, padding tiers) | `phoenix_commons.theme.tokens` | Apps use the constants; do not invent new ones inline. |
| Border-radius constants (button / card / panel / chip) | `phoenix_commons.theme.tokens` | Same. |

### 🪟 QSS (canonical stylesheet)

| Aspect | Owner |
|--------|-------|
| The Phoenix dark-navy QSS string (file + embedded fallback) | `phoenix_commons.theme` |
| `apply_dark_theme(app)` entry point | `phoenix_commons.theme.apply` |
| App-local QSS **additions** (cascade-only, never overriding commons selectors) | each app |

Apps that need an app-specific tweak append their QSS string to the
commons stylesheet, never replacing it. A future Phase 2.5 enforces
the load order via a single `commons_qss + "\n" + app_qss` pattern.

### 🧱 Widgets (component catalog)

| Aspect | Owner |
|--------|-------|
| `PrimaryButton`, `SecondaryButton`, `TertiaryButton` | commons |
| `Panel`, `PageTitle`, `PageSubtitle`, `SectionTitle`, `HintLabel` | commons |
| `PhoenixTable` | commons |
| `NoScrollComboBox`, `NoScrollSpinBox`, `NoScrollDoubleSpinBox`, `NoScrollDateEdit` | commons |
| `UpdateBanner` + `UpdateCheckThread` | commons |
| `button_row` helper | commons |
| App-specific widgets (e.g. `CommonsDropZone`, `SidebarSprite`, `SidebarToolWidget`, `ToolCard`) | each app |
| Subclasses of commons widgets (e.g. `class MyHeader(PageTitle):`) | each app |

`objectName` strings used by commons are **part of the commons public
API** — apps must not re-use them for unrelated widgets.

### 🖼 Icons

| Aspect | Owner |
|--------|-------|
| Base icon set — generic UI icons (refresh, settings, search, info, warning, error, success, chevron) | commons (planned Phase 2.6) |
| Per-app **logo** + per-app **mark / wordmark** | each app |
| Per-app status icons (e.g. Phoenix CAD's BricsCAD-specific glyphs) | each app |

Logos NEVER live in commons. The Command Center's `assets/logo.png`,
Phoenix CAD's `LLT_Transparent.png`, etc., stay app-local. Commons
provides the BASE set so apps can compose UIs without re-creating
generic chrome.

### 📁 Paths (frozen-vs-source resolution)

| Aspect | Owner |
|--------|-------|
| `is_frozen()` predicate | commons |
| `user_data_dir(app_name, org_name)` — `%APPDATA%\<org>\<app>\` resolver | commons |
| `resource_path(filename, base=None)` — `_MEIPASS`-aware resolver | commons |
| Per-app `APP_NAME` constant passed into `user_data_dir` | each app |

Apps that re-implement these helpers locally (PCC currently does)
should be migrated to commons imports in Phase 7+. Local re-implementations
are a deprecated pattern after Phase 3B is approved.

### 🔄 Updater

| Aspect | Owner |
|--------|-------|
| `check_for_update(current_version, owner, repo, zip_asset_name, timeout)` | commons |
| `download_and_apply(info, exe_name, *, expected_internal=True, progress_callback)` | commons |
| `UpdateInfo` dataclass | commons |
| `UpdateCheckThread` (Qt-aware) | commons |
| Per-app `OWNER` / `REPO` / `EXE_NAME` / `ZIP_ASSET_NAME` / `EXPECTED_INTERNAL` constants | each app |
| Per-app release notes parsing | each app (if they want app-specific UX) |

The full-folder vs exe-only contract is described in `PACKAGING_CONTRACT.md`.

### 📦 Package data (runtime resources bundled into the exe)

| Aspect | Owner |
|--------|-------|
| Bundling **commons-owned** files (`phoenix_style.qss`, icon set) | commons `pyproject.toml` + a documented `pyinstaller --collect-data phoenix_commons` (planned Phase 3C) |
| Bundling **app-owned** files (logo, watermark, sprite, screenshots) | each app's `build.bat` via `--add-data` |
| `_internal/` layout in the built exe | PyInstaller default; apps must not reorganise |

### 🏗 Runtime resources (icons / fonts / QSS / images at runtime)

| Aspect | Owner |
|--------|-------|
| Loading commons-owned resources (`apply_dark_theme(app)`, `icons.refresh()`) | commons API |
| Loading app-owned resources | app code, via `paths.resource_path("assets/...")` |

Apps NEVER directly read commons-owned files — they go through the
commons API. This decouples consumers from internal file layouts and
lets commons restructure without breaking apps.

## Forbidden patterns

| Anti-pattern | Why it's forbidden |
|--------------|---------------------|
| Hard-coded hex colour in app source (e.g. `setStyleSheet("color: #3CB8AE")`) | Bypasses the token system; theme changes drift. Use `C['teal']`. |
| App-local copy of `phoenix_style.qss` or its embedded fallback | Forks the canonical stylesheet. |
| Re-implementing `PrimaryButton` as `class FastButton(QPushButton)` | Same widget under a different name. Subclass instead. |
| Writing user data inside the install dir / `_internal/` | Wiped on every update. Use `paths.user_data_dir()`. |
| `dist\<App>.zip` missing `_internal/` when the tool ships full-folder updates | Breaks Job Tracker / Phoenix CAD updater contract. |
| App-defined `objectName` colliding with a commons-owned name | QSS cascade chaos. |

## Extension points (the "addendum" channel)

| Need | Approved extension point |
|------|--------------------------|
| App needs a button that looks like Primary but has a tiny icon prefix | `class IconButton(PrimaryButton):` in app source, set new `objectName`, append app-local QSS for that name. |
| App needs a different default panel padding | New `objectName` on the panel + app QSS override of that name only. Do not modify commons `Panel`. |
| App needs a new colour for a specific business state (e.g. "approved" green) | Use the closest existing commons token (`C['success']`) if semantically aligned. If genuinely new, propose a new commons token via PR. |
| App needs an icon commons doesn't provide | Drop it in the app's `assets/`, load via `paths.resource_path("assets/...")`. If 2+ apps need the same icon, propose adding it to commons in Phase 2.6's extension catalog. |

## Contract enforcement

| Mechanism | Owner |
|-----------|-------|
| Code review per retrofit PR | reviewer (Justin) |
| Lint rule blocking hardcoded hex in app source (planned) | future commons tooling |
| Per-retrofit safety checklist (PACKAGING_CONTRACT.md) | each retrofit PR |
| Smoke tests verifying commons API surface | each app's `tests/` |

The contract is enforced at PR-review time today. Automation is a
Phase 9 candidate.
