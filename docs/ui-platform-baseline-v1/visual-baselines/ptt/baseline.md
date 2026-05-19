# Project Tracking Tool (deployed product) — Visual Baseline

> Phase 2.7 pre-migration markdown baseline. **Deployed-product
> perspective** — what end users see when they launch
> `ProjectTrackingTool.exe` from `Start Menu → ATS Inc → Project
> Tracking Tool`. The source / dev perspective (repo structure,
> `starter_package/` scaffold) is in the sibling
> `job-tracker/baseline.md`.
>
> The Project Tracking Tool is the **flagship, longest-running,
> highest-iteration** Phoenix tool (at v1.8.5). Most surfaces in
> production today are PTT surfaces.
>
> Captured 2026-05-19.

## 1. Identity (end-user view)

| Field | Value |
|-------|-------|
| Display name (what the user sees) | **Project Tracking Tool** |
| Start Menu / Programs entry | `ATS Inc > Project Tracking Tool` |
| Exe path on disk | `%LocalAppData%\ATS Inc\Project Tracking Tool\ProjectTrackingTool.exe` |
| User-data folder | `%APPDATA%\ATS Inc\Project Tracking Tool\` |
| Taskbar icon | `PTT_Normal.ico` |
| Splash / about image | `PTT_Transparent.png` (if used) |
| Current shipped version | `1.8.5` |

## 2. Current theme (what the user sees)

**Phoenix System A** — dark navy chrome (`#0a0e27`), white text,
red primary CTAs (`#dc2626`), blue accent (`#3b82f6`). Same
palette as Lab Layout Tool and Phoenix Checkout.

PTT was likely the **first tool to ship the System A QSS**, so
its visual baseline is the longest-lived in the family. Any
user looking at PTT today is looking at the historical Phoenix
look.

## 3. Main window (end-user view)

- Title bar reads `Project Tracking Tool` (possibly with a
  project name suffix when one is open).
- Dark navy chrome inside Windows's dark title bar.
- Top-level navigation: **tabs** — likely Projects / Tasks /
  Time / Reports / Settings (or similar).
- Wide-by-default to accommodate dense tables.
- Status bar at bottom with version label + (existing) update
  indicator.

## 4. Home / dashboard view

The first screen on launch is **the Projects tab** showing the
list of recent / active projects. Each project shows:

- Project name + client
- Status indicator (active / on hold / complete)
- Total hours logged
- Last-updated date

Click into a project to drill down to tasks and time entries.

## 5. Forms

Users hit forms constantly in PTT:

- **New Project** — name, client, dates, budget, template
- **New Task** — title, project, assignee, due date, status
- **New Time Entry** — date, project, hours (decimal), notes
- **Edit X** — same fields, pre-filled
- **Project settings** — per-project configuration
- **App settings** — global preferences (default project,
  preferred report format, auto-save toggle, etc.)

Each form is a modal `QDialog` with:

- Top: project / task / time-entry name field
- Middle: the field-by-field input grid
- Bottom: action buttons (Save / Cancel / Delete)

## 6. Tables / grids (the dominant surface)

PTT is **table-heavy**:

- **Projects table** — name, client, status, dates, total hours
- **Tasks table** (per project) — title, assignee, status,
  due date
- **Time entries table** — date, project, hours, notes
- **Reports tables** — pivot-like aggregations across the above

Standard Phoenix `PhoenixTable` conventions apply:
alternating-row colouring, read-only, no-selection-on-hover,
compact ~36 px row height.

Heavy users will have **thousands of time-entry rows** across
the year — the table behaviour under that load is part of PTT's
identity.

## 7. Dialogs users hit

- **New / Edit modals** — form-style `QDialog` (see § 5)
- **Confirmation dialogs** — `QMessageBox.question` for delete
  prompts, status-change confirmations
- **File pickers** — `QFileDialog` for pyxlsb import / export
- **Error dialogs** — `QMessageBox.critical` for parse failures,
  permission issues, network problems
- **About dialog** — version + license info

## 8. Update banner

PTT has the **heavy / 2-constant** updater (per
production-inventory). The user sees an update via:

- Either a modal "Update available" `QMessageBox`, OR
- An older convention of the in-app update banner — depends on
  the exact integration in `app_gui.py`

Post-retrofit (Phase 7), this becomes the canonical commons
`UpdateBanner` strip in the status bar (matching Phoenix CAD's
current behaviour).

## 9. Empty states

- **Fresh launch with no projects** — Projects tab shows hint
  + "Create your first project" CTA
- **No tasks for selected project** — task panel shows "No
  tasks yet for <project>" + Add Task CTA
- **No time entries for date range** — "No time recorded for
  selected dates"
- **No matching reports** — "Adjust filters to see results"

## 10. Dense-data states (PTT's stress test)

- **Time entries across a full year** — thousands of rows.
  Most-used users will hit this.
- **Tasks across all projects** — hundreds of rows.
- **Reports tables for the whole company** — pivot-like, with
  totals row at the bottom.

PTT's table performance / scrolling behaviour under these
loads is part of the established UX. Retrofit must preserve.

## 11. Error / warning states

- **Form validation errors** — modal `QMessageBox.warning`
  (forbidden by `DESIGN_SYSTEM.md`; migration target).
- **Pyxlsb import errors** — modal `QMessageBox.critical` with
  the offending file path.
- **Time-entry conflicts** (e.g. overlapping entries) — warning
  prompt before save.
- **Network errors on update check** — silent (logged DEBUG).
- **Disk-full / permission errors on save** — modal
  `QMessageBox.critical`.

## 12. Sidebar / navigation

PTT navigates via **top tabs**, not a left sidebar. The tab bar
is the primary nav surface; selecting a project from the
Projects table drills into a per-project view that may have its
own internal tabs.

This differs from PCC (left sidebar) and from typical modern
apps but matches the existing Phoenix tool family's pattern.

## 13. End-user visible debt

| # | Item | Severity |
|---|------|----------|
| 1 | `QMessageBox.warning` for routine form validation | Medium — design-system forbidden; migration target |
| 2 | `QMessageBox.question` for "delete project?" confirmations | Medium — same |
| 3 | Modal `QMessageBox.critical` for routine errors that could be inline | Medium — same |
| 4 | If PTT's update banner is in the older convention rather than the modern `UpdateBanner` strip — user sees a different update UX than Phoenix CAD | Medium — visible to power users who use both tools |

## 14. Visible inconsistencies vs other Phoenix tools

| PTT | Lab Layout Tool | Phoenix Checkout |
|-----|------------------|-------------------|
| **Probably-modal update prompt** (legacy) | Status-bar `UpdateBanner` strip (modern) | Modal `QMessageBox` (legacy) |
| Tab-based top-level navigation | Menu-bar + tool-palette navigation | Single-content (no tabs / no sidebar) |
| Heavy table usage | Heavy table usage (layer + block library) | Light table usage |
| Form modals via `QDialog` | Form modals via `QDialog` (same pattern) | Form lives in main window (no modal) |

## 15. Migration sensitivity (end-user view)

**Headline:** Same as `job-tracker/baseline.md` § 15 — visible
change should be ≈ 0 because PTT already runs System A. The
risk is the **enormous surface area** of the retrofit creating
opportunities for accidental visual regression on a specific
form or table.

End users should specifically verify post-retrofit:

| Surface | What to check |
|---------|---------------|
| Projects table | Same column order, same status badges, same row spacing |
| New Project dialog | Same field order, same field widths, Save / Cancel button positions |
| Time entries dense-data view | Confirm thousands of rows still render smoothly |
| Reports tables | Confirm pivot-like layout unchanged |
| Update flow | Confirm it lands in the same place (sign-off if migrating from modal to banner) |

## 16. High-risk screens

For end-user post-retrofit sanity:

1. **Reopen the same project that was open pre-retrofit** —
   confirm identical layout, identical task list, identical
   time entries summary.
2. **Create a new task** — confirm dialog chrome and tab order
   unchanged.
3. **Generate the year-end report** — confirm pivot layout
   unchanged, totals row correct.
4. **Trigger an update check** — verify banner / modal
   behaviour. If this changes shape (modal → banner), sign-off
   needed in the retrofit PR.
5. **Try the pyxlsb import** — confirm the file picker
   experience unchanged.

## See also

- `../job-tracker/baseline.md` — the source / dev perspective
- `../README.md` — directory structure + alias map
- `../VISUAL_BASELINE_RULES.md` — capture rules
- `../MIGRATION_VISUAL_REVIEW_CHECKLIST.md` — per-PR checklist
- `../../production-inventory.md` § Job Tracker — identity source
