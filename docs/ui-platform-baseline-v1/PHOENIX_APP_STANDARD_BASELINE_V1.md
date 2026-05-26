# Phoenix App Standard Baseline — v1

> **Status:** canonical platform standard for every Phoenix app.
> **Date:** 2026-05-22.
> **Authored after:** Phase 3G merge — PCC main-app polish series closed.
> **Synthesized from:** the modernized reference set (Phoenix Command Center,
> Phoenix CAD / Lab Layout Tool, Phoenix Checkout Tool, phoenix-commons).
> **What this is:** the single-doc reference for what every Phoenix app
> must share, may customize, and must keep local. Cross-links to
> authoritative docs where they exist.
> **What this is NOT:** retrofit implementation work, ADR-class doctrine
> (those live in `DECISIONS.md` + ADR files), or per-app spec.
> **Supersedes:** none. Complements `PLATFORM_CONTRACT.md`,
> `DESIGN_SYSTEM.md`, `MIGRATION_RULES.md`, `FROZEN_BUILD_BASELINE.md`.

---

## 0. How to use this doc

This is the **one place** to look up "is X part of the Phoenix app standard?" Before opening a new retrofit, before reviewing a PR that touches platform-level concerns, before answering an operator question about "should this app behave like the others" — read this doc first.

It groups standards into 5 categories:

1. **Visual** (theme, typography, primitives, icons)
2. **Functional** (launch, settings, updater, user data, errors)
3. **Packaging/build** (Python version, PyInstaller flags, S1-safe baseline)
4. **Repository** (branch naming, build.bat, requirements, CI, releases)
5. **Retrofit** (facade doctrine, identity-equal widgets, stop conditions)

Each section starts with a one-line summary, lists mandatory items, then enumerates allowed customization. Authoritative cross-references are inline.

---

## 1. Visual standards

**Summary:** every Phoenix app uses System A dark theme + BrandProfile sentinel substitution + the commons primitive vocabulary. App-specific accents are allowed only via `BrandProfile` slot overrides per ADR-016. No emoji on chrome.

### 1.1 Theme — mandatory

  - **Dark navy "System A" palette.** Locked colour tokens (BG `#0a0e27` / SURFACE `#141829` / TEXT `#E4E4F0` / MUTED `#9090B0` / SUCCESS / WARNING / ERROR / INFO) are universal across every Phoenix app.
  - Locked tokens live in `phoenix_commons.theme.tokens` and are non-overridable per ADR-016.
  - Apps apply the theme at startup via `phoenix_commons.theme.apply_dark_theme(app, brand=<BrandProfile>)`.
  - PCC keeps its own `BrandProfile` (orange + teal) via the documented sentinel-substitution mechanism. Other apps default to commons `DEFAULT_BRAND` (red + deep blue + blue).

Authoritative: `DESIGN_SYSTEM.md` § Locked tokens, `ADR_PCC_PALETTE_RECONCILIATION.md` (ADR-016).

### 1.2 BrandProfile — three-slot mechanism

  - **3 slots, not 4.** `primary` (PrimaryButton fill, focus rings) / `secondary` (SecondaryButton fill, UpdateBanner background) / `accent` (links, status pills, brand-flavored highlights). No fourth slot accepted.
  - Canonical QSS uses `__BRAND_PRIMARY__` / `__BRAND_SECONDARY__` / `__BRAND_ACCENT__` sentinels.
  - `apply_dark_theme(app, brand=...)` substitutes at apply time.
  - Per-app BrandProfile lives in `theme.py` (or equivalent) at the app's root.
  - The only PCC-style override in production: PCC uses orange + teal-dark + teal. Other production tools use `DEFAULT_BRAND`.

Authoritative: `ADR_PCC_PALETTE_RECONCILIATION.md` (ADR-016), `DESIGN_SYSTEM.md` § BrandProfile.

### 1.3 Primitives — closed set

Every Phoenix app uses the commons primitive vocabulary. The closed set verified against `phoenix_commons.widgets.__all__` as of 2026-05-22:

| Primitive | Use |
|-----------|-----|
| `Panel` | Rounded-card chrome wrapper for sections (dashboard panels, dialog cards, detail-panel surfaces, UsageFooter) |
| `StatusBadge` | Coloured pill conveying operational state. Closed 7-variant set: `clean` / `dirty` / `error` / `warning` / `unknown` / `scanning` / `syncing`. Supports `compact=True` for dense rows |
| `PrimaryButton` | Red brand-primary; the surface's most operator-critical action. ≤1 per surface |
| `SecondaryButton` | Deep-blue brand-secondary; supporting operations (Pull/Push/Fetch, Run source, etc.) |
| `TertiaryButton` | Outline tier; navigation/inspection actions (Back, VS Code, GitHub, Rescan, Cancel, Browse) |
| `PhoenixTable` | Comparison-grid table (dashboard tools table) |
| `UpdateBanner` | Auto-update notification banner |
| `PageTitle` / `PageSubtitle` / `SectionTitle` / `HintLabel` | Typography widget classes — apps may use either these classes directly OR the `#pageTitle` / `#sectionHeader` object-name convention against the commons canonical QSS (see §1.5) |
| `phoenix_commons.widgets.no_scroll.*` | `NoScrollComboBox`, `NoScrollSpinBox`, `NoScrollDoubleSpinBox`, `NoScrollDateEdit` for scrollable forms (imported from the `no_scroll` submodule, not the `widgets` package root) |
| `button_row` helper (function) | Right-aligned action button row composition |

  - **Apps MUST use these primitives** for any chrome element they cover.
  - **Apps MUST NOT recreate them** as local QFrame/QLabel subclasses with inline `setStyleSheet`.
  - **A new primitive enters this set only via a commons PR** with documented two-consumer evidence per MIGRATION_RULES § 0 (pre-flight commons-API gap inventory).

#### App-local primitives that are NOT in commons today

Some primitives currently live in PCC (or another app) and are NOT mandatory cross-app commons primitives. They may be **promoted** to commons later only with documented two-consumer evidence:

| App-local primitive | Current owner | Notes |
|---------------------|---------------|-------|
| `AggregateTile` | PCC `dashboard.py` | Dashboard metric tile with leading Lucide icon + subtitle. Used inside PCC by the dashboard tile row (Phase 3C Step 5) and the detail-panel tile row (Phase 3D Step 2 imported it from dashboard). **PCC reference pattern**, not a mandatory cross-app commons primitive. Promotion to commons requires a second-consumer commitment per the two-consumer-evidence rule. |
| `SearchResultsPopup` | PCC `dashboard.py` | Floating result list under the Ctrl+K search input (Phase 3F). PCC-local; not a candidate for commons promotion since the search MVP itself is PCC-scoped. |

Authoritative: `COMPONENT_CONTRACT.md`, `phoenix_commons.widgets.__all__` (the runtime source of truth).

### 1.4 Icons — Lucide only

  - **No emoji on chrome.** Every primary surface (dashboard, detail panel, dialogs, buttons) renders Lucide SVG icons via `phoenix_commons.icons.icon(name, color)`.
  - **Closed icon set** in `ICON_NAMES`. New names added only via commons PR (~30 sec per icon).
  - Current `ICON_NAMES` (23 entries as of Phase 3G):
    ```
    arrow-down arrow-left arrow-up check clock code external-link
    file-text git-branch hard-drive info layout-dashboard package
    pin play plus refresh save search settings trash warning x
    ```
  - Emoji glyphs are allowed inside terminal-style output surfaces (e.g. `_git_out_set` runtime messages) but never on persistent chrome.

Authoritative: `ICON_POLICY.md`, `phoenix_commons.icons.registry`.

### 1.5 Typography — `#pageTitle` / `#sectionHeader` convention

  - **Page title:** 22px / 800-weight / negative letter-spacing (-0.3px). Set via `setObjectName("pageTitle")`. Used for: dashboard page title, detail-panel tool name, Commons Browser "Commons", Settings dialog "Settings".
  - **Section header:** 10px / 700-weight / uppercase / muted / 1.5px letter-spacing. Set via `setObjectName("sectionHeader")`. Used for: panel internal titles, table column headers (uppercase variant), UsageFooter "USED BY".
  - **Body text:** 12-13px / regular. Apps may use inline `setStyleSheet` on semantic-content labels (the B6 carve-out) for muted text colour or strikethrough.
  - **No bespoke typography.** Apps don't redefine font-family, font-size, or weight outside these conventions except for terminal-style output (Consolas / Cascadia Code monospace 10-12px).

### 1.6 Button hierarchy — 3-tier

  - **Primary tier:** `PrimaryButton` (red). The single most operator-critical action per surface. Anchors the right edge.
  - **Secondary tier:** `SecondaryButton` (deep blue / teal-dark in PCC). Supporting operations.
  - **Tertiary tier:** `TertiaryButton` (outline). Navigation + inspection.

  Operator should be able to glance at a surface and identify the primary action by colour alone.

  **Never** use raw `QPushButton` with `setObjectName("accentBtn")` / `setObjectName("ghostBtn")` for new code. Those object-name fallbacks exist for pre-retrofit code only.

### 1.7 Table / list conventions

  - **`PhoenixTable`** with `setObjectName("<appPrefix>Table")` for app-specific table tuning (e.g. quieter header treatment).
  - Columns: clear NAME / value / status pattern. STATUS columns use `StatusBadge` cell widgets, not coloured text.
  - Row hover via commons cascade; no inline hover styles.
  - **Sorting:** disabled by default unless the surface genuinely requires it (`setSortingEnabled(False)`).

### 1.8 Dialog conventions

  - **Header:** Lucide icon + `#pageTitle` text + `addStretch()`. No emoji prefix.
  - **Content:** `Panel`-wrapped cards per logical section. Tighten margins to 14/12/14/12 vs Panel's default 16/16/16/16 for denser dialogs.
  - **Buttons:** right-aligned via `addStretch()` + `TertiaryButton(Cancel)` + `PrimaryButton(Save & Apply)` (or similar action verb).
  - **Modality:** `setModal(True)` for settings, `setModal(False)` only when the operator explicitly works around the dialog (rare).
  - **Window title:** `<App Name> — <Dialog Name>` (em-dash separator).

### 1.9 Forbidden visual patterns

  - **Chip soup.** Inline-styled QLabel chains for status indicators. Use `StatusBadge`.
  - **Emoji on chrome.** Use Lucide icons.
  - **Inline `setStyleSheet` on commons primitives.** Use the canonical commons QSS + app-overlay extensions.
  - **Bespoke colour tokens.** Use `phoenix_commons.theme.tokens.SEMANTIC_COLORS` or the app's `C` dict.
  - **Animation / loading spinners.** Use `StatusBadge(variant="scanning")` instead.
  - **Command palette / mode switches / hidden shortcuts.** Operator workflow is click-driven; keyboard shortcuts are opt-in nice-to-haves.

---

## 2. Functional standards

**Summary:** apps launch via a single canonical entry point, use commons paths/updater, preserve user data across upgrades, and use `StatusBadge` for transient state feedback.

### 2.1 App entry point — mandatory

  - **`main.py`** is the single canonical entry. Constructs `QApplication`, applies theme, instantiates `MainWindow`, calls `app.exec()`.
  - **`version.py`** carries `__version__ = "X.Y.Z"` and (for shipping apps) `APP_NAME`, `APP_BUILD`, `AUTHOR`, `AUTHOR_ORG`, `AUTHOR_URL`.
  - **Build scripts read version from `version.py`.** Never hardcode version elsewhere.
  - README's current-version line + `version.py` must match before any release.

### 2.2 Settings / config behavior

  - **Schema:** JSON file under `%APPDATA%\ATS Inc\<App Name>\` (or app-specific path via `phoenix_commons.paths.user_data_dir`).
  - **Atomic writes:** temp-file-then-replace pattern (`tempfile.NamedTemporaryFile` + `os.replace`).
  - **First-run flow:** if config file missing, app shows Settings dialog before main window (PCC pattern) OR uses sensible defaults silently (other apps' choice).
  - **Settings dialog:** modal `QDialog`; returns updated `dict` via `get_config()`; caller calls `config.save(cfg)`.
  - **No automatic save.** Settings persist only on operator-confirmed Save click.

### 2.3 Updater behavior

  - **`phoenix_commons.updater`** provides `check_for_update(owner, repo, current_version, zip_asset_name)` → `UpdateInfo | None` and `download_and_apply(info, exe_name, *, expected_internal=True, progress_callback=None)`.
  - **`expected_internal=True`** is default for commons-backed builds (validates `<Exe>.exe` + `_internal/` at zip root).
  - **`expected_internal=False`** for Phoenix Checkout's exe-only payload (ADR-003).
  - **Standalone tools** may keep their own updater.py; commons-backed tools should facade.
  - **GitHub Release zip asset names are stable** — `ProjectTrackingTool.zip`, `LabLayoutTool.zip`, `PhoenixCheckoutTool.zip`, `ValveMasterTool.zip`. **Renaming them is a Stop Condition per MIGRATION_RULES.**

### 2.4 User data preservation

  - **`%APPDATA%\ATS Inc\<App Name>`** for writable user data. Never under PyInstaller `_internal/` (gets wiped on auto-update).
  - **`{localappdata}\ATS Inc\<App Name>`** for install files (read-mostly).
  - **Per-tool install + user-data paths** documented in `production-inventory.md`.
  - **Upgrades MUST preserve existing user data.** Validating this is row 11 of MIGRATION_RULES § 10 source-mode validation checklist.

### 2.5 Error / status feedback

  - **Transient operational status:** dashboard sync pill (`StatusBadge(variant="scanning"/"clean"/"error")`) or status-bar message.
  - **Per-row status:** `StatusBadge` in table cell or composed widget.
  - **Catastrophic errors:** `QMessageBox.warning` with actionable text (no traceback in operator-facing dialog; logging optional).
  - **No "..." spinners.** Use StatusBadge `scanning` variant.

### 2.6 Background work

  - **`QThread`** for long-running operations. **Never raw `threading.Thread`.**
  - **Signal-back to main thread.** Workers emit completion + error signals; main thread updates UI.
  - **Cancellation:** workers should be politely interruptible where the operator's workflow demands it (e.g. Cancel button on an in-progress scan).

### 2.7 Subprocess hygiene

  - **`subprocess.CREATE_NO_WINDOW`** on Windows for any non-GUI subprocess call (the B5 invariant established in Phase 3C polish). Otherwise the operator sees a cmd.exe flash on every git operation.
  - **Exceptions:** intentional GUI-launching subprocess (editor, GitHub URL) must NOT use `CREATE_NO_WINDOW`.

---

## 3. Packaging / build standards

**Summary:** Python 3.12 + PyInstaller 6.20 + `--noupx` + hardened stdlib excludes + commons submodule preflight + S1-safe baseline. Authoritative reference: `FROZEN_BUILD_BASELINE.md`.

### 3.1 Python version — Python 3.12

  - **Frozen builds MUST use Python 3.12.x.** Per ADR-014 + `BUILD_HARDENING_EXPERIMENT_REPORT_03.md`, 3.13/3.14 frozen builds get quarantined by S1 on the developer workstation.
  - **Source-mode work** may use 3.10-3.14.
  - **Build venv** is a separate `.venv-build/` if needed to isolate from a 3.13+ source venv.
  - Authoritative: `FROZEN_BUILD_BASELINE.md`, ADR-014.

### 3.2 PyInstaller — version + flags

  - **PyInstaller pinned to 6.20.0** in `requirements-dev.txt`.
  - **`--onedir --windowed`** mandatory (no onefile builds).
  - **`--noupx`** mandatory (UPX-compressed bootloaders increase AV false-positive rate).
  - **Stdlib excludes** required to keep the bundle lean and AV-friendly:
    ```
    --exclude-module turtle
    --exclude-module test
    --exclude-module unittest
    --exclude-module tkinter
    ... (full list in FROZEN_BUILD_BASELINE.md § stdlib excludes)
    ```
  - **`--collect-all phoenix_commons`** for commons-backed builds (ensures Lucide SVGs + QSS package data ship).
  - **Step 0 cleanup:** `rmdir /S /Q build dist` before each build (deterministic state).

  Authoritative: `FROZEN_BUILD_BASELINE.md`.

### 3.3 Commons submodule preflight

  - **`build.bat` MUST fail loudly** if `commons/src/phoenix_commons/__init__.py` is missing OR `import phoenix_commons` fails from the build venv.
  - Phoenix CAD's `build.bat` is the canonical reference for the preflight check.

### 3.4 Installer / updater zip contract

  - **Installer target:** `{localappdata}\ATS Inc\<App Name>`.
  - **Installer:** Inno Setup 6 with `PrivilegesRequired=lowest`.
  - **Output:** `<AppSlug>Setup.exe` (e.g. `LabLayoutToolSetup.exe`).
  - **Updater zip:** `<AppSlug>.zip` at the GitHub release. Contains `<Exe>.exe` at root + `_internal/` at root (validated by `download_and_apply` with `expected_internal=True`).
  - **AppId GUID:** stable per app — renaming/regenerating orphans existing installs (hard Stop Condition).

### 3.5 S1-safe baseline

  - **Bootloader fingerprint must remain in the Phoenix-family quarantine-safe zone.** Validated empirically per build via S1 observation:
    - Process kill quarantine: didn't fire (PID stays alive ≥3 min)
    - File quarantine: didn't fire (`Test-Path` returns True for the exe)
    - Bootloader content quarantine: didn't fire (exe launches)
  - **3.13/3.14 builds quarantine.** **3.12 builds with the hardened recipe don't.** Validated through Phase 6 experiments.
  - Authoritative: `BUILD_HARDENING_EXPERIMENT_REPORT_03.md`, `FROZEN_BUILD_BASELINE.md`.

### 3.6 Build / release validation

Before tagging a release, validate:

  - `compileall` clean
  - `pytest` (or per-tool smoke) green
  - Frozen build succeeds with hardened flags
  - Frozen exe launches in operator's session (5-minute observation window)
  - Installer produces the expected setup.exe
  - Installed exe launches from `{localappdata}\ATS Inc\<App Name>`
  - Updater zip validates as expected (`<Exe>.exe` + `_internal/` at root)
  - Upgrade round-trip preserves user data

---

## 4. Repository standards

**Summary:** consistent file layout, commit conventions, CI shape, and release-tagging across every Phoenix app.

### 4.1 File layout — root structure

Every Phoenix app's repository root contains:

```
<app-root>/
├── README.md                  # current version line + how-to-run section
├── CHANGELOG.md               # Keep-a-Changelog format
├── CLAUDE.md                  # per-app AI assistant context
├── requirements.txt           # pinned runtime deps + `-e ./commons` for commons-backed
├── requirements-dev.txt       # pinned PyInstaller + pytest deps
├── version.py                 # __version__ = "X.Y.Z" + APP_NAME/BUILD constants
├── main.py                    # entry point
├── theme.py                   # BrandProfile + apply_*_theme + C dict
├── paths.py                   # user_data_dir / resource_path (facades commons)
├── updater.py                 # updater facade (or full impl for standalone)
├── build.bat                  # build script
├── installer.iss              # Inno Setup script
├── phoenix_style.qss          # local backup of commons canonical QSS
├── .gitignore
├── .gitmodules                # commons-backed only
├── commons/                   # commons-backed only — git submodule
├── assets/                    # icons, sprites, logo
├── ui/                        # main_window.py + components.py + style.py (facades)
├── tests/                     # test_smoke.py at minimum
└── .github/
    ├── ISSUE_TEMPLATE/
    ├── pull_request_template.md
    └── workflows/
        └── ci.yml
```

Authoritative: `PACKAGING_CONTRACT.md`, RETROFIT_PLAYBOOK.md (when finalized).

### 4.2 Branch naming

  - **Per-retrofit:** `phase-<id>-<tool-slug>-retrofit` (e.g. `phase-3a-phoenix-cad-retrofit`).
  - **Per-PCC-modernization:** `phase-<id>-pcc-<surface>` (e.g. `phase-3g-pcc-settings-dialog`).
  - **Feature work:** `feature/<feature-slug>`.
  - **WIP isolation:** `feature/<feature-slug>` from a dirty `master`/`main`, then reset and create the retrofit branch.

Authoritative: `MIGRATION_RULES.md § Per-retrofit branch + PR convention`.

### 4.3 CI shape

  - **windows-latest runner** (PCC + every production tool is Windows-targeted).
  - **Python 3.12** via `actions/setup-python@v5` with `python-version: "3.12"`.
  - **`actions/checkout@v4` with `submodules: recursive`** for commons-backed apps (per the Phase 3D CI-fix doctrine that codified this).
  - **Split pip install:** `pip install -r requirements.txt` then `pip install -r requirements-dev.txt` as separate steps (so a failure in either is immediately visible).
  - **`import phoenix_commons` smoke check** after install for commons-backed apps.
  - **`compileall -q .`** as the first runtime check.
  - **`pytest -q tests/`** as the second.

Authoritative: PCC's `ci.yml` (commit `160270c`) is the canonical reference.

### 4.4 Commit conventions

  - **Per-retrofit step commits** (B1/B2/.../B-n or Step 1/2/.../n) — small, logical, reviewable.
  - **Merge commits use `--no-ff`** per MIGRATION_RULES.
  - **Commit message style:** subject line ≤72 chars + structured body explaining what/why/validation/invariants.
  - **HEREDOC for multiline commit messages** to preserve formatting.
  - **Never amend an already-pushed commit.** Create a new commit instead (MIGRATION_RULES § Git Safety Protocol).

### 4.5 Release / tagging convention

  - **Per-retrofit merge tags:** `<app-slug>-retrofit-vX.Y.Z` matching the post-retrofit release version (Phase 3A pattern: `lab-layout-tool-retrofit-v0.1.2-pre`).
  - **PCC modernization tags:** `pcc-phase-<id>-merged-v<X.Y.Z>` on the merge commit (`pcc-phase-3c-merged-v2.0.0` through `pcc-phase-3g-merged-v2.4.0`).
  - **Annotated tags only** (`git tag -a`). Lightweight tags don't carry the merge message.
  - **Tag the merge commit, not the cleanup commit** (mirrors Phase 3C → 3G precedent).

### 4.6 Source-mode validation (every retrofit)

The 11-row checklist in MIGRATION_RULES § 10 is mandatory before any retrofit merges:

  1. compileall exit 0
  2. import-only smoke
  3. identity-equal widget verification (`x is commons.X`)
  4. updater config constants preserved
  5. `expected_internal=<expected>` preserved per tool
  6. paths.<APP_CONSTANT> resolves to expected path
  7. apply_dark_theme + widget construction (offscreen)
  8. import entry-module (offscreen)
  9. submodule pinned to commons main (or documented intentional older SHA)
  10. commons pytest green
  11. **Actual source-mode app launch** (process alive ≥3s, MainWindowTitle correct, no stderr)

---

## 5. Retrofit standards

**Summary:** local facade strategy preserves caller imports; small commits; preserve behavior; never opportunistic modernization. Authoritative: `MIGRATION_RULES.md § Phase 3A retrofit doctrine`.

### 5.1 Local facade strategy — mandatory

Each retrofitted subsystem stays as a local file in the consuming app, with internals that delegate to commons. The local file preserves the entire caller-side import surface.

| Local file | Pre-retrofit | Post-retrofit |
|-----------|--------------|---------------|
| `paths.py` | Self-contained | Imports `is_frozen` from commons; keeps app-specific path constants |
| `updater.py` | Duplicates commons | ~100-line facade — 4 config constants + 2 wrapper functions |
| `ui/style.py` | ~800 LOC `_EMBEDDED_QSS` | ~55-line shim — `apply_dark_theme` re-export + app-local asset resolution |
| `ui/components.py` | Full widget catalog | Commons re-exports + app-specific dialogs only |

**Hybrid facade + preserved-local coexistence** allowed (Phase 3B Checkout proved this).

### 5.2 Pre-flight commons-API gap inventory

Before retrofit, audit every local symbol against commons. Present binary decision per gap:

  - **A. Keep local** (default) — behavior is intentional / app-specific
  - **B. Add to commons** — only if ≥ 2 tools will consume; speculative second consumers don't count

Document per-gap decisions in the retrofit's post-retrofit report.

### 5.3 Delete duplication, not behavior

  - If commons subtly differs from the local helper, **app KEEPS its local behavior**.
  - Cleanup of unrelated code "while we're here" is **forbidden**. A retrofit doesn't refactor business logic, doesn't rename variables, doesn't modernise idioms.

### 5.4 No opportunistic modernization

Each retrofit step has surface scope. Touching anything outside that scope is a Stop Condition.

The PCC main-app polish series (Phase 3C-3G) demonstrated this discipline by phase: each phase touched one surface; cleanup spilled into post-merge consolidation commits (not into the per-step commits).

### 5.5 Identity-equal widget verification

Required for every retrofit:

```python
assert ui.components.PrimaryButton is phoenix_commons.widgets.PrimaryButton
assert ui.components.Panel         is phoenix_commons.widgets.Panel
```

`is`, not `==`. Catches the failure mode where a retrofit re-defines a class instead of re-exporting it.

### 5.6 Screenshot baseline — visible-change band

Per tool, the allowed visible change at retrofit time:

| Tool | Acceptable visible change |
|------|---------------------------|
| Phoenix CAD | ≈ 0% (already System A) |
| Phoenix Checkout | < 5% (theme already System A) |
| ValveMaster / Phoenix Master Tool | ≈ 0% (revised 2026-05-22 per `WAVE_8A_VALVEMASTER_PREFLIGHT_AUDIT.md`; the v1.1.0 release already shipped the System A palette in `phoenix_style.qss`. Earlier "High — gray→navy swap" prediction is superseded.) |
| Job Tracker | < 5% (theme already System A) |
| PCC | High during 3C-3G modernization; near 0% during any Wave-8 retrofit |

Exceeding the band is a Stop Condition.

### 5.7 Stop conditions

A retrofit **must stop and ask** if:

  - Need to modify a commons-owned file
  - Need to change AppId GUID, zip asset name, install path, or user-data path
  - Build venv is not Python 3.12.x
  - `build.bat` is missing hardened-baseline flags
  - Frozen-exe verification fails for a reason other than the documented S1/AV pattern
  - A test that passes on `main` fails on the retrofit branch
  - Visible-change band exceeded

Authoritative: `MIGRATION_RULES.md § Stop conditions`.

---

## 6. What every app MUST share

  - Dark navy System A theme (locked tokens)
  - Commons primitives from `phoenix_commons.widgets.__all__` (Panel / StatusBadge / Primary / Secondary / TertiaryButton / PhoenixTable / UpdateBanner / PageTitle / PageSubtitle / SectionTitle / HintLabel / button_row) and `phoenix_commons.widgets.no_scroll.*` (NoScroll* family)
  - Lucide icons (no emoji on chrome)
  - `#pageTitle` / `#sectionHeader` typography
  - 3-tier button hierarchy
  - `version.py` with `__version__ = "X.Y.Z"`
  - `main.py` single canonical entry
  - Python 3.12 frozen build
  - PyInstaller 6.20 + `--noupx` + stdlib excludes
  - `subprocess.CREATE_NO_WINDOW` on Windows
  - `%APPDATA%\ATS Inc\<App Name>` user data location
  - `{localappdata}\ATS Inc\<App Name>` install location
  - Stable AppId GUID per app
  - Stable GitHub release zip asset name per app
  - `commons` submodule for commons-backed apps
  - CI with `submodules: recursive` checkout + `import phoenix_commons` smoke
  - `--no-ff` merges on retrofit branches
  - `<app-slug>-retrofit-vX.Y.Z` or `pcc-phase-<id>-merged-v<X.Y.Z>` annotated tags
  - Source-mode validation per MIGRATION_RULES § 10 (11 rows)

## 7. What every app MAY customize

  - **`BrandProfile` slots** (primary / secondary / accent) per ADR-016 — PCC is currently the only override-using app, but others may adopt their own
  - **App-specific `C` palette extension keys** (sidebar / topbar / card-hover colours when the canonical QSS doesn't cover them)
  - **App-specific section-header object names** for QSS variants (e.g. `#dashboardToolsTable`)
  - **App-local widget extensions** that subclass commons primitives and add methods (NOT override `__init__` to change colours — that's drift)
  - **Per-app spec docs** for unique surfaces (e.g. Phoenix CAD's hood-wiring page)
  - **Local helper files** (e.g. PCC's `search.py`, Phoenix CAD's `cad/` subsystem)
  - **App-specific data shapes** in `pcc_config.json` / `<app>_state.json`
  - **App-specific keyboard shortcuts** beyond the universal Ctrl+R / F5 refresh + Ctrl+, settings + Ctrl+Q quit
  - **App-specific menus** under File / Tools / Help

## 8. What every app MUST keep local

  - Path constants specific to the app (`paths.JOBS_DIR`, `paths.BLOCKS_DIR`, etc.)
  - Source-mode policy if it differs from commons default (e.g. Phoenix CAD's source-mode-uses-repo-root override)
  - App-specific dialogs (Settings, About, custom Wizards)
  - Domain-specific business logic (CAD blocks, Checkout valve forms, Job Tracker project records)
  - GitHub owner/repo/zip-asset metadata
  - Light-mode theme (if applicable — ADR-011 keeps commons dark-only; Checkout has its own light-mode toggle)
  - Threading patterns specific to the app (e.g. Checkout's split-install download/apply)

## 9. What every app MUST get from commons

  - `apply_dark_theme(app, brand=...)` + the canonical QSS + locked tokens
  - `BrandProfile` + sentinel-substitution mechanism
  - `phoenix_commons.widgets` primitives (the closed set in §1.3)
  - `phoenix_commons.icons.icon(name, color)` + Lucide SVGs
  - `phoenix_commons.paths.is_frozen` + `user_data_dir` + `resource_path` helpers
  - `phoenix_commons.updater.check_for_update` + `download_and_apply` (commons-backed apps)
  - `phoenix_commons.theme.tokens.SEMANTIC_COLORS` + `color_for_tool`

## 10. Validation gates that must pass before merge

For any retrofit / modernization merge:

  1. compileall clean (`exit 0`)
  2. pytest green (PCC: 4/4 smoke; tool-specific where present)
  3. Commons pytest green if commons was touched (currently 134 passing)
  4. Source-mode launch: process alive ≥3 sec, MainWindowTitle non-empty, no stderr
  5. Frozen build (production tools): hardened recipe + 5-minute S1 observation
  6. Visible-change band respected (per §5.6)
  7. No regressions vs production tool's last release (installed exe + user data)
  8. Identity-equal widget verification passes (`is` comparisons)
  9. Submodule pin documented (matches commons main OR intentional older SHA)
  10. MIGRATION_RULES § 10 11-row checklist all green

Authoritative: `MIGRATION_RULES.md § Source-mode validation checklist`.

---

## 11. Living standard

This doc is the **v1** baseline. Future amendments require:

  - **Visual / functional / packaging standards changes** → commons PR + ADR if the change is doctrinal.
  - **Retrofit doctrine additions** → codified into MIGRATION_RULES under the appropriate section.
  - **New primitives entering the closed set** → commons PR with documented two-consumer evidence.

Cross-references that may evolve:

  - `MIGRATION_RULES.md` — retrofit doctrine
  - `PLATFORM_CONTRACT.md` — overarching platform contract
  - `DESIGN_SYSTEM.md` — visual design system
  - `COMPONENT_CONTRACT.md` — primitive contracts
  - `ICON_POLICY.md` — icon-set rules
  - `PACKAGING_CONTRACT.md` — build/release rules
  - `FROZEN_BUILD_BASELINE.md` — frozen-build recipe
  - `VISUAL_BASELINE_RULES.md` — visual-baseline checks
  - `MIGRATION_VISUAL_REVIEW_CHECKLIST.md` — per-retrofit visual review
  - `ADR_PCC_PALETTE_RECONCILIATION.md` (ADR-016) — BrandProfile mechanism
  - `DECISIONS.md` — ADR index

---

*End of Phoenix App Standard Baseline v1. This doc is the single-point reference; everything else linked from here is the authoritative deep-dive.*
