# Lab Layout Tool (deployed product) — Visual Baseline

> Phase 2.7 pre-migration markdown baseline. **Deployed-product
> perspective** — what end users see when they launch
> `LabLayoutTool.exe` from `Start Menu → ATS Inc → Lab Layout Tool`.
> The source / dev perspective (repo structure, build pipeline,
> `cad/` subsystem) is in the sibling `phoenix-cad/baseline.md`.
>
> Captured 2026-05-19. End-user-visible surfaces only —
> dev-only chrome (build output, source-tree paths) is in the
> sibling doc.

## 1. Identity (end-user view)

| Field | Value |
|-------|-------|
| Display name (what the user sees) | **Lab Layout Tool** |
| Start Menu / Programs entry | `ATS Inc > Lab Layout Tool` |
| Exe path on disk | `%LocalAppData%\ATS Inc\Lab Layout Tool\LabLayoutTool.exe` |
| User-data folder | `%APPDATA%\ATS Inc\Lab Layout Tool\` |
| Taskbar icon | `LLT_Normal.ico` (red Phoenix mark with "LLT" wordmark) |
| Splash image | `LLT_Transparent.png` (if used) |
| Current shipped version | `0.1.1` |

## 2. Current theme (what the user sees)

**Phoenix System A** — dark navy chrome (`#0a0e27` window
background), white text, red primary CTAs (`#dc2626` filled
buttons), blue accent (`#3b82f6` for focus rings / link-like
chrome). Same palette as Job Tracker and Phoenix Checkout.

This is the **canonical reference** for what "System A" looks
like in production — the QSS file shipping with this exe is
the byte-identical source that
`phoenix_commons.theme.phoenix_style.qss` is lifted from.

## 3. Main window (end-user view)

- Title bar reads `Lab Layout Tool` (or `Lab Layout Tool — <Job Name>`
  when a job is open).
- Dark navy chrome inside Windows's dark title bar.
- Sizable; remembers last position/size between launches
  (likely via `QSettings`).
- Status bar at bottom shows current job + version label + (when
  applicable) the update banner.

## 4. Home / dashboard view

The first screen on a fresh launch is **the layout editor with
no job loaded** — empty CAD canvas plus a hint pointing at
`File → Open Job` or `File → New Job`.

Once a job is loaded, the canvas fills with the layout-editor
working surface; side panels populate with the job's layers,
block library, and tools.

## 5. Forms

Forms users encounter:

- **New Job dialog** — job name + client + date + template choice
- **Layer property editor** — colour swatch + line-type combo +
  thickness spinner
- **Block insert / properties** — block-name combo + position
  inputs
- **Export options** — output path + DWG version + viewport choices

Each form uses the standard Phoenix layout: `Panel`
container, `SectionTitle` header, label-input rows, action
buttons at the bottom (`PrimaryButton` for the affirmative
action, `TertiaryButton` for cancel/dismiss).

## 6. Tables / grids

- **Layer table** — alternating-row, no-selection, read-only
  (the standard `PhoenixTable` defaults). Click-to-edit
  inline.
- **Block library list** — DWG filenames, possibly with
  thumbnail previews.
- **Recent jobs list** — names + dates (likely on the empty
  canvas or in `File → Recent Jobs`).

## 7. Dialogs users hit

- **File pickers** — OS-native dark-titled `QFileDialog`s for
  opening jobs / saving DWG exports.
- **Confirmation modals** — `QMessageBox.question` for save-
  on-quit and overwrite prompts. These are functional but
  identified as Phoenix-design-system-forbidden (`QMessageBox`
  for routine prompts — `DESIGN_SYSTEM.md` § Forbidden).
- **About dialog** — version + license info.

## 8. Update banner

**Present today** — Phoenix CAD's `UpdateBanner` is the canonical
Phoenix version (Phase 2 lifted it into commons verbatim from
this tool).

When an update is available:

- Slim 44 px strip in the status bar
- Copy: "Update available — v<latest> is ready. You're on v<current>."
- "Release Notes" button opens a `QMessageBox` with the release-
  notes markdown rendered as text
- "Install && Restart" button triggers `download_and_apply` →
  background download → PyInstaller-helper batch + PowerShell
  → app exits → installer relaunches the new exe
- ✕ button dismisses for the session

## 9. Empty states

- **Fresh-launch / no-job-loaded** — canvas is blank with a hint
  message and prominent CTAs (Open Job / New Job).
- **Empty block library** — if the user has no blocks dir,
  hint points at the configured blocks path.
- **No-recent-jobs** — likely a clean "No recent jobs yet"
  message.

## 10. Dense-data states

Layer counts in the hundreds (complex layouts) populate the
layer table. Block libraries can be 50+ entries. Standard
Phoenix table conventions handle dense data well; the
`alternatingRowColors` + compact row height keep
hundreds-of-rows tables legible without resizing.

## 11. Error / warning states

- **CAD-import errors** — BricsCAD COM raises → modal
  `QMessageBox.critical` with the COM error message. CAD-domain
  specific; out of retrofit scope.
- **File-save errors** — modal `QMessageBox.critical` or
  status-bar transient.
- **Stale-job warnings** — inline `HintLabel`-style copy.
- **Update-failure messages** — modal `QMessageBox.warning`.

## 12. Sidebar / navigation

Top menu bar (File / View / Edit / Tools / Help) plus a tool
palette on the left side of the layout editor (likely). No
collapsible sidebar in the modern-app sense.

## 13. End-user visible debt

The end user mostly doesn't see Phoenix CAD's visual debt
because Phoenix CAD IS the canonical reference. What an
end-user sees today is the standard for what every other
Phoenix tool aspires to.

The exceptions:

- **`QMessageBox` for routine confirmations** — modal dark Qt
  dialogs that don't match the rest of the dark-navy chrome
  perfectly. Same issue across all Phoenix tools today.
- **OS file-picker chrome** — the file picker uses Windows's
  built-in styling, which contrasts with the in-app dark
  theme. Can't be fixed (Qt's `QFileDialog.AcceptOption.DontUseNativeDialog`
  would swap to a worse-looking dark Qt picker; live with the
  OS one).

## 14. Visible inconsistencies vs other Phoenix tools

Among the QSS-based tools (Phoenix CAD / Job Tracker / Phoenix
Checkout), Lab Layout Tool is the **reference** — others are
inconsistent against it, not the reverse. Specific deltas
visible to a user who alt-tabs between LLT and another tool:

| LLT | Job Tracker / PTT | Phoenix Checkout |
|-----|-------------------|------------------|
| `UpdateBanner` strip in status bar | Different placement (older convention) | Modal `QMessageBox` instead |
| `Panel` chrome on every card | Consistent | Inconsistent — some panels are raw `QWidget` |
| Layer / block tables use `PhoenixTable` | Job tables use `PhoenixTable` | Tables are rare |

PCC (Phoenix Command Center) is a separate story — different
palette entirely (orange/teal vs navy/red/blue). See
`../pcc/baseline.md`.

## 15. Migration sensitivity (end-user view)

**Zero expected user-visible change after retrofit.** This is
the cleanest production tool for the commons-backed swap.

User shouldn't notice anything different after Phase 3+
retrofit lands. Internal source-tree changes (deletion of local
widget copies in favour of commons imports) don't surface.

## 16. High-risk screens (end-user view)

For an end-user sanity check post-retrofit:

1. **Open the same job that was open pre-retrofit** — confirm
   identical canvas rendering, identical layer table content,
   identical export output.
2. **Trigger the update banner** — confirm it still appears in
   the same status-bar slot with the same copy.
3. **Open and dismiss a few `QMessageBox` dialogs** — confirm
   modal chrome unchanged.
4. **Open a DWG file picker** — confirm OS chrome unchanged
   (it's not commons-themed; should be identical).

## See also

- `../phoenix-cad/baseline.md` — the source / dev perspective
  (repo structure, build pipeline, the `cad/` exclusion rule)
- `../README.md` — directory structure + alias map
- `../VISUAL_BASELINE_RULES.md` — capture rules
- `../MIGRATION_VISUAL_REVIEW_CHECKLIST.md` — per-PR checklist
- `../../production-inventory.md` § Phoenix_CAD_Tool — identity source
