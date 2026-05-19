# Phoenix Valve Checkout Tool — Visual Baseline

> Phase 2.7 pre-migration markdown baseline. Used as the visual
> comparison reference for the Phase 3+ retrofit PR(s) that
> swap Phoenix Checkout's local theme/widgets/updater/paths for
> their commons equivalents.
>
> Captured 2026-05-19 from `docs/production-inventory.md` + the
> commons widget catalogue. Sections marked **Inferred** require
> pixel verification at the first post-AV screenshot run.

## 1. Identity

| Field | Value |
|-------|-------|
| App name (display) | **Phoenix Valve Checkout Tool** |
| Source repo | `Phoenix-Checkout-Tool` (the lone CamelCase + hyphen repo name) |
| Exe | `PhoenixCheckoutTool.exe` |
| Install path | `{localappdata}\ATS Inc\Phoenix Valve Checkout Tool` |
| User-data path | `%APPDATA%\ATS Inc\Phoenix Valve Checkout Tool` |
| Current version | `1.7.0` |
| Updater zip | `PhoenixCheckoutTool.zip` — **exe-only payload** (no `_internal/`) |
| Build pipeline | `build.bat` → PyInstaller `--onedir --windowed` → Inno Setup → two zips |
| `expected_internal` value (for commons updater retrofit) | **`False`** — per ADR-003 / production-inventory § Critical asymmetry |

## 2. Current theme system

- **Phoenix System A** (canonical navy + red + blue) loaded from
  `phoenix_style.qss` at the repo root.
- `--add-data="phoenix_style.qss;."` bundles the file alongside
  `_internal/` under PyInstaller.
- Loaded inline in `checkout_tool_gui.py` (no separate `ui/style.py`
  module — the monolithic GUI file does it directly).
- **No embedded QSS fallback.** If the bundled QSS file is missing
  (auto-updater drift), the app renders unstyled. Phase 2.1's
  `EMBEDDED_QSS` fallback will close this gap during retrofit.

## 3. Main window

**Inferred.** Single top-level `QMainWindow` with central widget
containing the checkout workflow chrome. Dark navy bg (`#0a0e27`),
white text. Window title: `Phoenix Valve Checkout Tool`. Status
bar at bottom with version label + (post-retrofit) update banner.

Window does not appear to use a `QSplitter` — single content area.

## 4. Dashboard / home view

**Inferred.** Checkout-flow-focused — first screen presents the
checkout form rather than a dashboard. Phoenix Checkout is more
workflow tool than dashboard tool. The "home view" is effectively
the checkout entry surface.

## 5. Forms

**The dominant surface in this tool.** Checkout forms collect
valve / part / project metadata. Likely uses:

- `QLabel` + `QLineEdit` / `QComboBox` / `QSpinBox` rows
- `QComboBox` for the dropdowns (NOT `NoScrollComboBox` —
  pre-commons, the tool doesn't have the no-scroll family;
  this is a known migration item)
- `QFormLayout` or hand-rolled `QGridLayout` for label/input
  pairs
- Action buttons at the bottom: a primary "Submit" or "Generate"
  CTA + secondary "Reset" / "Cancel"

The buttons are raw `QPushButton` styled via the QSS file's
selectors. They do NOT use the Phoenix `PrimaryButton` /
`SecondaryButton` / `TertiaryButton` classes — those come in
during retrofit.

## 6. Tables / grids

**Inferred — light usage.** Checkout flow is form-driven, not
table-driven. Any tables present are likely small read-only
listings (e.g. recent checkouts, project list) using raw
`QTableWidget` — not yet `PhoenixTable`.

## 7. Dialogs

**Inferred.**

- **Confirmation dialogs** — `QMessageBox.question` for "Generate
  template?" / "Overwrite existing file?" type prompts.
- **File-picker dialogs** — `QFileDialog.getOpenFileName` /
  `getSaveFileName` for the XLSX-template output path. These
  inherit OS chrome; can't be themed.
- **Error dialogs** — `QMessageBox.critical` for "Failed to write
  template" / "Invalid input" scenarios.

The `QMessageBox` usages are forbidden by `DESIGN_SYSTEM.md`
§ Forbidden patterns ("`QMessageBox` for routine info — use the
status bar"). Routine-info dialogs are migration targets.

## 8. Update banner state

**Currently absent.** Phoenix Checkout's `updater.py` is the
light/4-constant variant — it shows an update via a `QMessageBox`
prompt, not a status-bar banner. Migration to commons gains
`UpdateBanner` (the System A banner with install/release-notes
buttons in the status bar).

## 9. Empty states

**Inferred — minimal.** The form's "no input yet" state is just
the form with empty fields. No dedicated empty-state illustration
or copy.

Post-retrofit, the empty-state convention from `PLATFORM_CONTRACT`
should apply (hint label + CTA), but Phase 2.7 doesn't see
evidence of one today.

## 10. Dense-data states

**N/A.** Phoenix Checkout doesn't render large tables / dense
data grids. Workflow is single-form, single-output.

## 11. Error / warning states

**Inferred.**

- **Validation errors** — likely `QMessageBox.warning` modal or
  inline `QLabel` red-text below the offending input. Neither
  matches commons norms yet.
- **Failed-output errors** — `QMessageBox.critical` modal. Same
  story.

Post-retrofit, the recommended pattern is **inline error labels
using the `error` semantic colour** (`#ef4444` from
`phoenix_commons.theme.tokens.ERROR`) — keeps the user in flow.

## 12. Sidebar / navigation states

**N/A.** No sidebar — single-content tool.

## 13. Known visual debt

| # | Item | Where seen | Severity |
|---|------|-----------|----------|
| 1 | Raw `QPushButton` instead of Phoenix button tiers | Throughout the form's submit / cancel actions | Medium — fixable by import swap |
| 2 | Inline `setStyleSheet("color: …")` likely present | Suspected in `checkout_tool_gui.py`'s monolithic body — need source read at retrofit time | Medium |
| 3 | No `_resource_path` helper — QSS load assumes the file is next to the exe | `checkout_tool_gui.py` | Low — replaced by commons `apply_dark_theme` |
| 4 | Monolithic 177 KB `checkout_tool_gui.py` (per production-inventory) | One file | High — refactoring risk, see § Migration sensitivity |
| 5 | No embedded QSS fallback | (gap relative to Phoenix CAD's `ui/style.py:63-829`) | Medium — auto-update without `_internal/` could leave QSS unloaded |
| 6 | `QMessageBox` for routine confirmation / status | Various | Medium — `DESIGN_SYSTEM.md` § Forbidden |
| 7 | Build pipeline lacks `py_compile` / tests / artifact validation (per inventory) | `build.bat` | Low (build) — doesn't affect runtime visual |

## 14. Known inconsistencies

| # | Item | Compared to | Notes |
|---|------|-------------|-------|
| 1 | Repo name `Phoenix-Checkout-Tool` uses CamelCase + hyphens | All other tools use lowercase-kebab-case | Cosmetic; doesn't affect runtime UI |
| 2 | Exe-only updater zip | Phoenix CAD + Job Tracker use full-folder | Functional, not visual — but the `UpdateBanner` retrofit needs the right `expected_internal=False` kwarg |
| 3 | No `requirements.txt` (per inventory) | Every other tool has one | Build-pipeline issue, not visual |

## 15. Migration sensitivity

**Headline:** monolithic-GUI extraction is the heavy lift.
Theme + widgets + updater retrofit is moderate. End-user-visible
change should be ≈ 0 because Phoenix Checkout already uses
System A.

| Surface | Sensitivity | Why |
|---------|-------------|-----|
| Theme load | Low | Already on `phoenix_style.qss`. Retrofit swaps the local loader for `phoenix_commons.theme.apply_dark_theme` — same QSS, same output. |
| Button styling | Low | Raw `QPushButton` → `PrimaryButton` / `SecondaryButton` / `TertiaryButton`. ObjectNames match QSS selectors, output identical. |
| Form layout | **High** | The 177 KB monolithic GUI file has the form logic + presentation tangled. Extraction into separate widget classes will touch hundreds of lines per form. Visual diffs need pixel-level review. |
| Update banner | Low | New surface (was `QMessageBox`); intentional visible change with sign-off. |
| Dialogs | Medium | `QMessageBox.question` / `QFileDialog` keep their OS chrome — no commons replacement planned. `QMessageBox.warning` for validation should migrate to inline error labels. |
| XLSX templates | N/A | Output-only; no visual baseline impact. |

## 16. High-risk screens

1. **Main checkout form** — biggest surface, most user-facing,
   the screen Phoenix Checkout's identity rests on. Pixel-level
   review required at retrofit PR.
2. **The 5 XLSX templates' "preview" UI** (if present) — anywhere
   the tool reflects template structure to the user.
3. **Any state that exercises `QMessageBox`** — those are
   migration candidates and will look different after the
   retrofit (inline error vs modal). Sign-off needed.

## See also

- `../README.md` — directory structure + alias map
- `../VISUAL_BASELINE_RULES.md` — capture rules + parity definition
- `../MIGRATION_VISUAL_REVIEW_CHECKLIST.md` — per-PR checklist
- `../../production-inventory.md` § Phoenix-Checkout-Tool — identity source
