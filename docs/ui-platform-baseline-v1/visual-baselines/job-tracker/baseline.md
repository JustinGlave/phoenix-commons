# Job Tracker (source view) — Visual Baseline

> Phase 2.7 pre-migration markdown baseline. **Source / dev
> perspective** — what the repo looks like, what dev work
> touches. The end-user / installed-product perspective is in
> the sibling `ptt/baseline.md` (Project Tracking Tool is what
> `ProjectTrackingTool.exe` is called in production).
>
> Job Tracker is the **largest surface area and longest history
> in the production batch** — strongest production risk, last
> to be retrofitted per the canonical rollout plan.
>
> Captured 2026-05-19 from documented architectural patterns +
> the `starter_package/` template scaffolding.

## 1. Identity

| Field | Value |
|-------|-------|
| App name (display) | **Project Tracking Tool** (see `ptt/baseline.md`) |
| Source repo | `Job Tracker` (working-copy name; the GitHub repo is `project-tracking-tool`) |
| GitHub | `JustinGlave/project-tracking-tool` |
| Exe | `ProjectTrackingTool.exe` |
| Install path | `{localappdata}\ATS Inc\Project Tracking Tool` |
| User-data path | `%APPDATA%\ATS Inc\Project Tracking Tool` |
| Current version | `1.8.5` (the most-iterated tool in the family) |
| Updater zip | `ProjectTrackingTool.zip` — **full-folder payload** |
| Build pipeline | `build.bat` — README/version sanity + `py_compile` + `unittest discover` + PyInstaller `--onedir` + Inno Setup + two zips + updater-zip validation |
| `expected_internal` value (for commons updater retrofit) | **`True`** — already matches commons default |

## 2. Current theme system

**Phoenix System A** — `phoenix_style.qss` bundled via
`--add-data="phoenix_style.qss;."`. Same canonical QSS as Phoenix
CAD and Phoenix Checkout.

Notable difference from Phoenix CAD: **no separate `ui/style.py`
module**. The QSS file is loaded inline somewhere in
`project_tracker_gui.py` (the main GUI file). Migration will
move the load logic to `phoenix_commons.theme.apply_dark_theme`.

## 3. Main window

`QMainWindow` from `project_tracker_gui.py`. Central widget holds
the Project Tracking dashboard + various task panes.

Specific to Job Tracker:

- **Tabbed top-level navigation** (likely) — Projects, Tasks,
  Time, Reports, Settings, etc.
- **Per-tab content** — each tab gets its own dashboard / form /
  table layout
- **Status bar** with version + the existing update banner (or
  modal — see § 8)

## 4. Dashboard / home view

The "home view" is likely the **Projects tab** — listing recent
projects, status indicators, summary metrics.

Visual: dense-data dashboard with multiple `Panel`-like cards
showing different aspects (open projects, this-week's hours,
flagged items, etc.).

## 5. Forms

Forms are heavy in Job Tracker:

- **New Project** — name + client + start date + budget +
  template
- **Task entry** — title + project + assigned-to + due date +
  status
- **Time entry** — date + project + hours + notes
- **Settings** — various per-user preferences

Likely uses raw `QLineEdit` / `QComboBox` / `QDateEdit` /
`QSpinBox` etc. Pre-commons retrofit, the buttons are raw
`QPushButton` styled via QSS file selectors.

Forms span many surfaces — the biggest migration target.

## 6. Tables / grids

**Many tables.** Job Tracker is fundamentally a data-management
tool:

- **Project table** — name + client + status + dates + budget
- **Task table** — title + project + assignee + status + due
- **Time entries table** — date + project + hours + notes
- **Report tables** — billable hours by project / by assignee /
  by date range
- **Per-project drill-down** — task list with sub-tables

All read-mostly. Migration to `PhoenixTable` is per-table import
swap.

`starter_package/` (the template scaffold inside Job Tracker)
shows the canonical PhoenixTable-equivalent shape — the
production tables likely follow the same pattern but with
local copies.

## 7. Dialogs

- **New Project / New Task / Edit X dialogs** — `QDialog`
  subclasses with form layout. Modal.
- **Confirmation modals** — `QMessageBox.question` for delete
  prompts, status-change prompts.
- **Pyxlsb file pickers** — `QFileDialog` for the spreadsheet
  data import / export.
- **Error modals** — `QMessageBox.critical`.

`starter_package/` shows the canonical dialog pattern (Phoenix
`Panel` + `button_row` + `PrimaryButton` / `TertiaryButton`
combo) — the production tool may not fully match this yet, since
`starter_package/` is the template intended to be deleted after
retrofit.

## 8. Update banner state

**Present** but in the older convention — Job Tracker's
`updater.py` has the heavy/2-constant variant (per
production-inventory). Banner / dialog shape depends on the
exact `_UpdateChecker` integration in `app_gui.py` (Phase 3
lifted that into `phoenix_commons.updater.qt.UpdateCheckThread`).

The `starter_package/` template shows the modern `UpdateBanner`
shape (status bar strip with install / release-notes /
dismiss). The deployed production tool may or may not be on the
banner yet — needs verification at retrofit time.

## 9. Empty states

- **No projects yet** — empty Projects tab with hint + "Create
  project" CTA
- **No tasks for selected project** — empty task list with
  "Add task" CTA
- **No time entries for date range** — "No time recorded" copy
- **No reports configured** — "Configure first report" copy

## 10. Dense-data states

Job Tracker hits dense-data scenarios the hardest in the family:

- **Time entries table over a year** — thousands of rows
- **Tasks across all projects** — hundreds of rows
- **Detailed reports** — large pivot-like outputs

The `pyxlsb` dependency hints at heavy Excel import/export
workflows; users likely paste large spreadsheets in.

## 11. Error / warning states

- **Validation errors** on forms — likely modal `QMessageBox.warning`
- **Pyxlsb parse errors** — modal `QMessageBox.critical` with
  the file path inline
- **Path / permission errors** — `QMessageBox.critical`
- **Network / GitHub Releases errors during update check** —
  silent (logged at DEBUG per the canonical pattern)

## 12. Sidebar / navigation states

If Job Tracker has a sidebar at all, it's likely **project-list
focused** — a list of projects on the left, drilling into one
fills the right pane.

OR it may be entirely **tabbed** — top-level tabs for
Projects / Tasks / Time / Reports, no sidebar.

Implementation detail not visible from source-tree inspection
alone.

## 13. Known visual debt

| # | Item | Severity |
|---|------|----------|
| 1 | `starter_package/` scaffold inside the repo (intended for deletion post-retrofit) | Medium — needs explicit deletion in retrofit PR |
| 2 | No separate `ui/style.py` — theme load is inline in `project_tracker_gui.py` | Low — replaced by commons import |
| 3 | Inline `_app_data_path()` in `project_tracker_gui.py` (no `paths.py`) | Low — replaced by `phoenix_commons.paths.user_data_dir` |
| 4 | Hardcoded asset-name search `projecttrackingtool.zip` in updater | Low — parameterised in commons updater |
| 5 | Bundles `pyxlsb/` package via `--add-data` (per inventory) | Low — bundling concern, not visual |
| 6 | `PTT_Transparent.png` / `PTT_Normal.ico` are bundled app assets | Low — stay app-local per `ICON_POLICY.md` |

## 14. Known inconsistencies

| # | Item | Notes |
|---|------|-------|
| 1 | Working-copy dir name `Job Tracker` vs GitHub repo `project-tracking-tool` vs display name `Project Tracking Tool` vs exe `ProjectTrackingTool.exe` | Four name variants in play. `NAMING_REGISTRY.md` is the single source of truth for which is canonical where. |
| 2 | `starter_package/` template exists alongside the running production code | Migration deletion target — the template was the design seed for many later retrofits |
| 3 | Heavy/2-constant updater vs Phoenix CAD's heavy/5-constant | Functional difference; commons consolidates both into one parameterised API |

## 15. Migration sensitivity

**Headline:** Largest production-risk retrofit in the family.
Visible change should be ≈ 0 (already on System A) but the
**source-tree surface area is enormous**, so the risk of
accidentally regressing a corner-case form / table is highest.

**Retrofit order:** Job Tracker is **LAST** in the production
batch (per the original rollout plan). Phoenix CAD goes first
(lowest visible risk), then Phoenix Checkout, then ValveMaster
(intentional palette change), then Job Tracker.

| Surface | Sensitivity | Why |
|---------|-------------|-----|
| Theme load | Low | Same QSS, just imported from commons |
| `_app_data_path()` → `user_data_dir(...)` | Low | API-equivalent |
| Updater | Low (after parametrisation) | Same payload, same behaviour, parameterised owner/repo/zip-name |
| Forms | **High** | Many forms, many fields each, many button placements. Each form is an opportunity for accidental regression. |
| Tables | High | Many tables, each with custom column orderings, custom row-actions. |
| `starter_package/` deletion | Medium | Has to happen in the same PR; deletion can break imports if anything in production code references it. |
| Dialogs | Medium | Multiple `QDialog` subclasses scattered through the codebase. |
| Tabs / nav | Low | Top-level container; rarely touched in retrofits. |

## 16. High-risk screens

For Job Tracker's retrofit review:

1. **Every form dialog** — each one is its own pixel-review
   target. The volume is the risk.
2. **The Time entries table over a year** — dense data
   stress-test; confirm `PhoenixTable` defaults render
   thousands of rows without visual artifacts.
3. **The pyxlsb import path** — confirm modal-error chrome
   unchanged when an import fails.
4. **Reports view** — pivot-like aggregations; confirm
   column / row hierarchy unchanged.
5. **The update banner** — confirm it lands in the right
   status-bar position with the right copy after the swap
   from whatever-it-uses-now to commons `UpdateBanner`.
6. **`starter_package/` post-deletion** — verify no production
   import accidentally referenced the scaffold (the deletion
   should be a clean cut).

## See also

- `../ptt/baseline.md` — the deployed-product perspective
- `../README.md` — directory structure + alias map
- `../VISUAL_BASELINE_RULES.md` — capture rules
- `../MIGRATION_VISUAL_REVIEW_CHECKLIST.md` — per-PR checklist
- `../../production-inventory.md` § Job Tracker — identity source
- `../../PHASES.md` — Job Tracker retrofit slot
