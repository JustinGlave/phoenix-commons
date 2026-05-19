# Phoenix CAD Tool (source view) — Visual Baseline

> Phase 2.7 pre-migration markdown baseline. **Source / dev
> perspective** — what the repo looks like and what surfaces
> dev work touches. The end-user / installed-product
> perspective is in the sibling `llt/baseline.md` (Lab Layout
> Tool is what `LabLayoutTool.exe` is called in production).
>
> Phoenix CAD is also the **canonical source of the Phoenix
> widget catalog** — `phoenix_style.qss` lives at the repo
> root, and every widget in `phoenix_commons.widgets` was
> lifted verbatim from `Phoenix_CAD_Tool/ui/components.py`.
> The retrofit therefore mostly removes local copies; visible
> change at the user level should be ≈ 0.
>
> Captured 2026-05-19 from documented architectural patterns.

## 1. Identity

| Field | Value |
|-------|-------|
| App name (display) | **Lab Layout Tool** (see `llt/baseline.md`) |
| Source repo | `Phoenix_CAD_Tool` (the local working-copy name on Justin's machine; the GitHub repo is `lab-layout-tool`) |
| GitHub | `JustinGlave/lab-layout-tool` |
| Exe | `LabLayoutTool.exe` |
| Install path | `{localappdata}\ATS Inc\Lab Layout Tool` |
| User-data path | `%APPDATA%\ATS Inc\Lab Layout Tool` |
| Current version | `0.1.1` |
| Updater zip | `LabLayoutTool.zip` — **full-folder payload** (exe + `_internal/`) |
| Build pipeline | `build.bat` → pre-flight + `py_compile` + `embed_qss.py` sync + PyInstaller `--onedir` + Inno Setup + two zips + zip validation |
| `expected_internal` value (for commons updater retrofit) | **`True`** — already matches commons default |

## 2. Current theme system

**Phoenix System A (canonical, navy + red + blue).** Phoenix CAD is
where the canonical theme lives.

- `phoenix_style.qss` at the repo root — the **canonical** QSS
  file Phase 2.1 lifted into `phoenix_commons/theme/phoenix_style.qss`
  byte-for-byte.
- `ui/style.py:21-58` — `apply_dark_theme(app)` (the function
  Phase 2.1 lifted into `phoenix_commons.theme.apply`).
- `ui/style.py:63-829` — `_EMBEDDED_QSS` hand-maintained string
  (the predecessor to the Phase 2.1 generated `embedded_qss.py`
  in commons). Phoenix CAD's local copy is still hand-maintained
  pre-retrofit.
- `tools/embed_qss.py` — Phoenix CAD's build-time script that
  copies `phoenix_style.qss` into the embedded fallback string
  before PyInstaller runs. (The commons equivalent is
  `phoenix_commons.theme.generate_embedded_qss`, landed in Phase 2.1.)

## 3. Main window

`QMainWindow` from `app.py`. Central widget contains the Phoenix
CAD layout-editor canvas + side controls. Status bar at the
bottom with version label + (existing) update banner.

Notable:

- The `cad/` subsystem (BricsCAD COM integration via `pythoncom`
  / `win32com.client`) is **out of retrofit scope.** The retrofit
  PR touches only theme/widgets/updater/paths.
- `app.py` orchestrates the UI; modify only at import sites
  during the retrofit (per `PLATFORM_CONTRACT.md`).

## 4. Dashboard / home view

The "home view" is the layout editor's main canvas — a
`QGraphicsView` (likely) hosting the CAD drawing surface plus
side panels for layer controls, dimension tools, and the
current-job indicator.

The canvas itself is mostly app-specific (CAD-domain rendering),
not commons-relevant. The **side panels and toolbar** are where
commons widgets dominate.

## 5. Forms

Form-style surfaces include:

- **Layer property editors** — name + colour + line-type + thickness inputs
- **Block library browser** — DWG file list + preview pane
- **Job metadata editor** — project name + client + date inputs
- **Export options** — output path + DWG version + viewport choices

Likely uses:

- `Panel` (the commons widget — already in this codebase pre-commons)
- `SecondaryButton` / `TertiaryButton` for the cancel / dismiss actions
- `NoScrollComboBox` / `NoScrollSpinBox` for the dropdown / numeric inputs

All of those classes exist locally in `ui/components.py` at the lines
Phase 2 lifted into commons. After retrofit, they import from
`phoenix_commons.widgets` instead — semantics identical.

## 6. Tables / grids

- **Block library table** — DWG file listing (PhoenixTable equivalent
  in local source).
- **Layer table in the layer-editor panel** — likely a `QTableWidget`
  with the standard Phoenix table conventions (read-only,
  no-selection, alternating rows).
- **Job list** — recent-jobs panel listing past sessions.

All read-only or near-read-only. Retrofit swap to `PhoenixTable`
is a one-line import change per surface.

## 7. Dialogs

- **DWG file picker** — `QFileDialog` (OS chrome, can't be themed)
- **Save-job dialog** — `QFileDialog` saving JSON fixtures
- **About / version dialog** — likely `QMessageBox.about`
- **Confirmation dialogs** — `QMessageBox.question` for save-prompts
- **Update-available dialog** — see § 8

## 8. Update banner state

**Already present.** Phoenix CAD's `ui/components.py:206-263` is
the `UpdateBanner` source that Phase 2 lifted into commons. It's
the canonical version.

Banner lives in the status bar via
`status_bar.addPermanentWidget(banner, 1)`. Visual:

- Slim 44 px tall strip
- `#UpdateBanner` objectName triggers QSS styling
- "Update available — vX.Y.Z is ready. You're on vA.B.C." copy
- "Release Notes" tertiary button (132 px)
- "Install && Restart" primary button (150 px)
- Dismiss ✕ tertiary button (40 px)

Retrofit is mostly a no-op — same widget, just imported from
commons instead of locally.

## 9. Empty states

- **No-job-loaded state** — likely a hint message in the canvas
  area ("Open a job from File → Open or create a new one")
- **Empty block library** — hint pointing at the blocks/ source dir

These are app-specific copy — retrofit doesn't change them.

## 10. Dense-data states

The layer table and block library can carry tens-to-hundreds of
entries. Standard Phoenix `PhoenixTable` defaults (alternating
rows, compact 36 px row height — inferred from QSS) handle dense
data well today.

## 11. Error / warning states

- **CAD-import errors** — likely modal `QMessageBox.critical`
  with the BricsCAD COM error message. CAD-specific; out of
  retrofit scope.
- **File-save errors** — `QMessageBox.critical` or status-bar
  message.
- **Stale-job warning** — inline label in the job panel.

## 12. Sidebar / navigation states

Phoenix CAD's sidebar (if it has one) is layer-editor / tool-
palette focused. Most navigation is via the main canvas + the
top menu bar (File / View / Edit / Tools / Help).

## 13. Known visual debt

| # | Item | Severity |
|---|------|----------|
| 1 | Hand-maintained `_EMBEDDED_QSS` in `ui/style.py:63-829` (driftable against the QSS file) | Medium — solved by commons generated fallback |
| 2 | Local `paths.py` with hardcoded `ORG_NAME / APP_NAME` | Low — replaced by `phoenix_commons.paths.user_data_dir(app_name, org_name=...)` |
| 3 | Local copies of every widget class (`ui/components.py`) | Low — replaced by `phoenix_commons.widgets` imports |
| 4 | `tools/embed_qss.py` is a one-off build script | Low — superseded by `phoenix_commons.theme.generate_embedded_qss` |
| 5 | `LLT_Transparent.png` / `LLT_Normal.ico` are bundled assets — confirm they stay app-local | Low — per `ICON_POLICY.md` logos NEVER move to commons |

## 14. Known inconsistencies

| # | Item | Notes |
|---|------|-------|
| 1 | Local working-copy directory name `Phoenix_CAD_Tool` differs from the GitHub repo name `lab-layout-tool` AND the deployed product name `Lab Layout Tool` | Three names for one tool. Cross-referenced in `NAMING_REGISTRY.md`. |
| 2 | The widget catalog Phase 2 lifted into commons is **byte-identical** to `ui/components.py` (per the verbatim-port policy) | No inconsistency; this is the canonical source. |

## 15. Migration sensitivity

**Headline:** Lowest-risk retrofit in the production batch.
Visible change should be 0. Source-tree change is large
(deleting hundreds of lines of local copies in favour of imports)
but functionally equivalent.

| Surface | Sensitivity | Why |
|---------|-------------|-----|
| `apply_dark_theme` call | Zero | Same QSS, same QPalette. Migration is `from ui.style import apply_dark_theme` → `from phoenix_commons.theme import apply_dark_theme`. |
| Widget instantiation | Zero | All Phoenix-CAD-defined widgets are byte-identical to commons. Migration is per-import-line. |
| `_EMBEDDED_QSS` reference | Zero | Local copy deletion + import from `phoenix_commons.theme.embedded_qss`. Generated by `generate_embedded_qss` — drift-proof. |
| `paths.py` helpers | Low | Refactor from hardcoded constants to `user_data_dir("Lab Layout Tool", "ATS Inc")`. |
| `updater.py` | Low | Already uses the heavy/5-constant pattern; migration is to commons's `check_for_update` + `download_and_apply(..., expected_internal=True)` (default). |
| `cad/` subsystem | **OUT OF SCOPE** | Per `PLATFORM_CONTRACT.md`. BricsCAD COM is untouched. |
| `app.py` orchestration | Zero | Only the import lines change. |

## 16. High-risk screens

Honestly, **none.** Phoenix CAD is the canonical source — there's
nothing the retrofit changes about how anything looks. The
review checklist still gets applied for due-diligence, but every
row should resolve "matches baseline" trivially.

Top monitor surfaces (low risk, applied for paranoia):

1. **Layout-editor canvas** — verify CAD rendering unchanged
   (the canvas itself is `cad/`-owned and out of scope, so it
   really shouldn't change).
2. **Layer / block side panels** — confirm Panel chrome
   unchanged after the import swap.
3. **Status bar + update banner** — verify the banner still
   anchors at the bottom-right with the same copy template.

## See also

- `../llt/baseline.md` — the deployed-product perspective
- `../README.md` — alias map + directory structure
- `../VISUAL_BASELINE_RULES.md` — capture rules
- `../MIGRATION_VISUAL_REVIEW_CHECKLIST.md` — per-PR checklist
- `../../production-inventory.md` § Phoenix_CAD_Tool — identity source
- `../../PLATFORM_CONTRACT.md` § Widgets — `cad/` scope-exclusion rule
