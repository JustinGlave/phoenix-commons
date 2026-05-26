# MIGRATION_VISUAL_REVIEW_CHECKLIST.md

> Per-PR visual-review checklist applied to every Phase 3A / 3B /
> 3C / 7 / 8 retrofit. Reviewer (Justin) works top-to-bottom
> through this checklist against the PR's screenshots before
> merging.
>
> Companion to `VISUAL_BASELINE_RULES.md` (which defines what
> "acceptable parity" means) and the per-app `baseline.md` files
> (which are the comparison reference).

## How to use

1. Reviewer opens the retrofit PR's screenshots directory:
   `visual-baselines/<app>/screenshots/`.
2. For each surface where a `--phase-2.7` baseline exists,
   compare the new `--phase-<this-retrofit>` capture against
   it. (If no baseline yet — first retrofit of a surface —
   capture the new screenshot now and note "first capture" in
   the row.)
3. Tick every row as either ✅ (parity), ⚠️ (intentional change
   with sign-off note), or ❌ (regression to fix).
4. PRs with any ❌ row don't merge until resolved.
5. PRs with ⚠️ rows require explicit reviewer sign-off comment
   referencing the row + rationale.

## Per-surface checklist

### 1. Main window

- [ ] Window title text matches baseline (allowing for dynamic
      suffix like `— <Job Name>`).
- [ ] Window default size + minimum size unchanged.
- [ ] Window remembers position / state via QSettings as before.
- [ ] Dark-titled OS chrome present (Windows-level "dark mode for
      apps" assumed on).
- [ ] No light-titled fallback or unstyled splash on cold launch.
- [ ] Phoenix dark-navy background `#0a0e27` (or token-equivalent).
- [ ] Status bar present at the bottom with version label.

### 2. Dashboard / home view

- [ ] First-launch state matches baseline (empty / hint / CTA
      pattern).
- [ ] Default view on app re-launch is the documented "home"
      tab / surface.
- [ ] Dashboard density unchanged — same cards / panels visible
      without scrolling on 1920×1080.
- [ ] Card placement / order unchanged.
- [ ] No new full-screen modals interrupting the home flow.

### 3. Forms

- [ ] Every form's field order unchanged.
- [ ] Field labels match (text, casing, alignment).
- [ ] Field widths match (within ±2 px).
- [ ] Tab order matches.
- [ ] Field-level validation triggers the same visual indicator
      (border colour, error label, icon) as baseline.
- [ ] Action buttons at the bottom: same labels, same tier
      (primary / secondary / tertiary), same order.
- [ ] No raw `QPushButton` remaining — all migrated to
      `PrimaryButton` / `SecondaryButton` / `TertiaryButton`.
- [ ] No raw `QComboBox` / `QSpinBox` / `QDateEdit` inside any
      scrollable form — all migrated to the `no_scroll` family.
- [ ] Form-modal `QDialog` chrome unchanged (title bar, OK /
      Cancel placement).

### 4. Tables / grids

- [ ] Column count and order match baseline.
- [ ] Column widths match within ±5 px.
- [ ] Header text + alignment unchanged.
- [ ] Row height matches (compact Phoenix default ~36 px).
- [ ] Alternating row colours present (`alternatingRowColors=True`).
- [ ] No selection highlighting (`SelectionMode.NoSelection`).
- [ ] No focus rectangle (`FocusPolicy.NoFocus`).
- [ ] Cell text alignment unchanged (numeric right-aligned, text
      left-aligned, etc.).
- [ ] Status-indicator columns (badges, coloured chips) render
      with the same semantic colour from `theme.tokens`.
- [ ] Dense-data scenario (≥ 500 rows) still scrolls without
      visual artifacts.
- [ ] Empty-table state matches baseline (placeholder copy / CTA).

### 5. Dialogs

- [ ] Modal centring unchanged.
- [ ] Modal width unchanged (forms generally 480 px; review per
      dialog).
- [ ] `QDialog` title bar matches baseline.
- [ ] Action-row layout matches (button order, alignment,
      tier).
- [ ] `QMessageBox` usages either preserved (with sign-off if
      flagged as design-system-forbidden) OR migrated to inline
      labels (with sign-off for the visible change).
- [ ] OS-native `QFileDialog` chrome left untouched (this is
      Windows's, not Qt's, can't be styled).

### 6. Update banner

- [ ] Banner appears in the status bar (commons standard) NOT
      in a `QMessageBox` modal (legacy pattern).
- [ ] If the app was previously on the modal pattern and now
      uses the banner: **sign-off required**.
- [ ] Banner copy template: "Update available — v<latest> is
      ready. You're on v<current>."
- [ ] "Release Notes" button (132 px tertiary) opens a
      `QMessageBox` with the release-notes text.
- [ ] "Install && Restart" button (150 px primary).
- [ ] Dismiss ✕ button (40 px tertiary) hides the banner for
      the session.
- [ ] Banner height 44 px.
- [ ] Banner objectName `UpdateBanner` triggers the QSS rules.
- [ ] No emoji in banner copy (icons via the icon set, not
      Unicode).

### 7. Empty states

- [ ] Empty-state copy matches baseline (text / tone).
- [ ] CTA button present and labelled consistently.
- [ ] Empty-state hint label uses `HintLabel` (objectName
      `hint`) not raw `QLabel`.
- [ ] Empty state is visually quiet — no warning banners on a
      legitimate empty state.

### 8. Dense-data states

- [ ] Performance unchanged — large tables still scroll smoothly.
- [ ] No new wrapping / truncation in column text.
- [ ] Totals / summary rows render in the same position with
      the same emphasis (bold / colour).
- [ ] Filtered / sorted state visually indicates the active
      filter / sort.

### 9. Error / warning states

- [ ] Form validation errors render with the `error` semantic
      colour (`#ef4444` from `phoenix_commons.theme.tokens.ERROR`).
- [ ] Warning states use `WARNING` (`#f59e0b`).
- [ ] Success confirmations use `SUCCESS` (`#22c55e`).
- [ ] Info banners use `INFO` / `ACCENT`.
- [ ] No hardcoded hex literals in retrofitted code.
- [ ] Modal `QMessageBox.critical` for genuine errors retained.
- [ ] Routine info NOT in `QMessageBox` (per `DESIGN_SYSTEM.md`
      § Forbidden patterns).

### 10. Sidebar / navigation

- [ ] If the app has a sidebar: same width, same item order,
      same hover / selected state semantics.
- [ ] If the app has tabs: same tab order, same tab labels,
      same active-tab indicator (orange bar, underline,
      whatever the QSS specifies).
- [ ] Menu bar (if present): same menu order, same shortcuts.

## Cross-cutting checks

### Palette / tokens

- [ ] Every coloured pixel in the new render maps to a token in
      `phoenix_commons.theme.tokens.SEMANTIC_COLORS` (or is an
      app-local addendum colour declared in the app's QSS).
- [ ] No inline `setStyleSheet("color: #ABCDEF")` calls — all
      colours come from QSS selectors targeting `objectName`s.
- [ ] No `QPalette` mutations outside `apply_dark_theme`.

### Typography

- [ ] Font family unchanged (`Segoe UI` / system stack).
- [ ] No `QFontDatabase.addApplicationFont(...)` introduced.
- [ ] Section headers use the right typography token
      (`SectionTitle` for 12pt semibold, `PageTitle` for 14pt
      bold).
- [ ] `HintLabel` used for 9pt muted helper text — not raw
      `QLabel`.
- [ ] No inline `font-family: Consolas` (the 6 known PCC
      occurrences are tracked separately).

### Spacing + radius

- [ ] Every padding / margin value is a multiple of 4 px (per
      `DESIGN_SYSTEM.md` § Spacing scale).
- [ ] Border radii from the radius scale (4 / 6 / 8 / 10 px).
- [ ] Cards / panels have rounded corners (`radius_lg`
      minimum).
- [ ] No square-cornered cards (looks legacy).

### Icons (post-Phase-2.2)

- [ ] Icons load via `phoenix_commons.icons.icon(name, ...)` for
      generic UI chrome.
- [ ] Per-app logos / brand marks loaded via
      `phoenix_commons.paths.resource_path(...)` and live in the
      app's `assets/`.
- [ ] No emoji icons remaining in retrofitted code (`⚙️`, `🔍`,
      `💾`, `🗑️`, `⚠️`, etc. — replaced with Lucide equivalents).
- [ ] Icon recolouring uses `color="<semantic>"` (not hex
      literals, except for app-local one-offs).
- [ ] Icon sizes from the standard rungs (14 / 16 / 18 / 20 / 24
      / 28 / 32 px).

### `objectName` discipline

- [ ] No commons-owned `objectName` re-used on an unrelated
      widget (see `COMPONENT_CONTRACT.md` § Reserved `objectName`
      rules).
- [ ] App-local `objectName`s follow a clear convention
      (e.g. `App-<tool>-<role>`).

### Update banner specifically

- [ ] `UpdateBanner` constructor signature unchanged.
- [ ] `install_clicked` signal still wired to `download_and_apply`.
- [ ] `download_and_apply` called with the right
      `expected_internal` kwarg per the app:
  - Phoenix CAD / Job Tracker: `expected_internal=True`
  - Phoenix Checkout / ValveMaster: `expected_internal=False`

### Updater behaviour (functional, not just visual)

- [ ] `check_for_update` called from a `UpdateCheckThread`
      (Qt-friendly).
- [ ] `UpdateInfo` resolution path unchanged.
- [ ] Background download still progress-callbacked through to
      the UI.

## Per-app addenda

### Phoenix CAD / Lab Layout Tool

- [ ] `cad/` subsystem completely untouched.
- [ ] BricsCAD COM call surface unchanged.
- [ ] `app.py` modified ONLY at import lines.
- [ ] `LLT_Transparent.png` + `LLT_Normal.ico` stay app-local.

### Job Tracker / Project Tracking Tool

- [ ] `starter_package/` directory **deleted** in the retrofit PR.
- [ ] No production import accidentally referenced
      `starter_package/`.
- [ ] `pyxlsb` bundling preserved.
- [ ] `PTT_Transparent.png` + `PTT_Normal.ico` stay app-local.

### Phoenix Checkout

- [ ] Monolithic `checkout_tool_gui.py` extraction is incremental
      — each form/dialog migrated in its own commit within the
      retrofit PR for reviewability.
- [ ] 5 XLSX templates' bundling preserved.
- [ ] `expected_internal=False` passed in updater call.
- [ ] `green.png` + `PTT_Normal_green.ico` stay app-local.

### Phoenix Command Center (the palette outlier)

- [ ] **Decision recorded in an ADR before this PR opens:**
      Does PCC adopt the commons-canonical palette (red/blue)
      as-is, or does the commons palette get an `accent_alt`
      token to accommodate PCC's orange/teal identity?
- [ ] If commons-canonical: confirm orange `#E8783C` → red
      `#dc2626` is intentional and signed off.
- [ ] If commons-canonical: confirm teal `#3CB8AE` → blue
      `#3b82f6` is intentional and signed off.
- [ ] `SidebarSprite` widget continues to composite correctly
      over the new background colour.
- [ ] Six inline `font-family: Consolas` occurrences in PCC
      widget code addressed (per `DESIGN_SYSTEM.md` § Forbidden).

### ValveMaster / Phoenix Master Tool — Wave 8a facade retrofit

**Revised 2026-05-26 per `WAVE_8A_VALVEMASTER_PREFLIGHT_AUDIT.md`.**
The original "System B → A cutover" framing is superseded:
ValveMaster's `v1.1.0` release already shipped the canonical
System A palette in `phoenix_style.qss` (byte-match verified).
Wave 8a is therefore a **facade retrofit** (commons-backed
architecture alignment + build hardening + updater/theme/widget
facades), NOT a visible theme swap. Expected visible change
≈ 0% (Phoenix-CAD profile).

Rows below are **expected to be ✅ (parity) or, where the
retrofit introduces a Lucide-icon substitution, ⚠️ (intentional)
with sign-off**. The full "everything is intentional" framing
from the original cutover section no longer applies.

- [ ] Theme: `phoenix_style.qss` retired in favor of
      `phoenix_commons.theme.apply_dark_theme(app)` via
      `DEFAULT_BRAND` (palette tokens are byte-equal — should be
      ✅ parity, not ⚠️).
- [ ] Programmatic `QPalette` defaults removed if any local
      overrides existed; commons sentinel-substitution applies.
- [ ] `assets.py` base64-embedded brand assets remain local
      (PyInstaller bundles via module scan — preserve-local
      per pre-flight audit § preserved-local domain logic).
      Lucide substitution allowed for chrome icons where
      appropriate; valve-type domain icons remain app-local.
- [ ] Inno Setup `AppId` GUID **`{A7F3C2D1-9B4E-4F6A-8C3D-1E5B7A9F2C4D}`
      preserved byte-for-byte** — critical for Windows upgrade
      detection.
- [ ] `apply_light_theme()` removed if present (Phoenix is
      dark-only; ADR-011).
- [ ] Release note framing: **facade retrofit**, ≈ 0% visible
      change. Reference `WAVE_8A_VALVEMASTER_PREFLIGHT_AUDIT.md`
      and `WAVE_8A_IMPLEMENTATION_BRIEF.md` in the PR description.
- [ ] Light visual review at merge gate (per operator decision
      2026-05-22) — full Phase 2.7-style baseline is not required
      because the canonical palette already shipped at `v1.1.0`.
- [ ] No user-visible "the look has changed" release note. If
      anything observable did shift (e.g. a Lucide-icon swap),
      document it surgically in the changelog.

## Final sign-off

- [ ] Every checklist row resolved (✅ / ⚠️ / ❌).
- [ ] All ❌ rows fixed and re-screenshot-ed.
- [ ] All ⚠️ rows have a sign-off comment from the reviewer.
- [ ] The retrofit's screenshots committed to
      `visual-baselines/<app>/screenshots/` with the
      `--phase-<this-retrofit>` suffix.
- [ ] The `--phase-2.7` baseline screenshots retained for
      historical comparison (NOT deleted).
- [ ] Per-app `baseline.md` updated with any newly-observed
      facts (e.g. "Phoenix Checkout's main form actually
      had X — confirmed during retrofit").
- [ ] `CHANGELOG.md` entry in the retrofitted app's repo
      describes the visible changes.

## See also

- `README.md` (this dir) — structure + alias map
- `VISUAL_BASELINE_RULES.md` — naming, sizing, parity definition
- `<app>/baseline.md` — pre-migration reference per app
- `../PLATFORM_CONTRACT.md` § Widgets / Icons — ownership
- `../COMPONENT_CONTRACT.md` — extension rules
- `../ICON_POLICY.md` — naming, promotion, recolour rules
- `../DESIGN_SYSTEM.md` § Forbidden patterns — anti-patterns
  retrofits must remove
- `../DECISIONS.md` § ADR-015 — submodule transport mechanism
  (relevant to how the retrofit's `commons/` shows up)
