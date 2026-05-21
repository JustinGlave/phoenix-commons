# Phase 3C — Runtime Polish Report (Report 01)

> **Status:** complete (B5+B6+B7 landed on `phase-3c-pcc-retrofit`).
> **Branch:** PCC `phase-3c-pcc-retrofit`. Not merged to `master`.
> **Date:** 2026-05-20.
> **Scope:** operator-review fix-up after the Phase 3C retrofit foundation
> (`PHASE_3C_PCC_RETROFIT_AND_VISUAL_IMPLEMENTATION_REPORT.md`).

This report covers the two findings operator review surfaced during the
Phase 3C retrofit (B1-B4) walk-through:

  1. Console / window flashing during PCC startup as tool data loaded.
  2. PCC still felt visually "old" — the retrofit's commons styling was
     not actually showing through on the dashboard.

Both findings were addressed surgically (no architecture changes, no
async framework, no loading-system rewrite, no palette experiments).
A first conservative flagship-polish pass also landed.

---

## 1. Root cause of flashing windows

Two compounding root causes:

### 1a. Subprocess console flashing (the user-visible "windows popping up")

PCC's `ScanWorker` runs a sequence of `git` subprocesses per discovered
tool — `git rev-parse`, `git status --porcelain`, `git rev-list`,
`git log -1`, `git remote get-url origin`, etc. On the developer machine
this is ~17 git invocations spread across all configured Phoenix tools.

Every `subprocess.check_output()` / `subprocess.run()` callsite was
missing `creationflags=subprocess.CREATE_NO_WINDOW`. On Windows, Python's
`subprocess` module defaults to creating a new console (cmd.exe) for
each child process when the parent process has no console attached
(true for a PySide6 `--windowed` app). That console flashes open + closes
faster than the eye can resolve a single window — but at ~17 windows
across 4 tools, what the operator perceives is a continuous flicker of
black rectangles during the first 1-2 seconds of dashboard load.

Three modules involved:

  - `scanner.py` — `_run()` helper services every `ScanWorker` git call
    + `git_pull` / `git_push` / `git_fetch` for the detail panel.
  - `detail_panel.py` — pre-pull safety check that runs
    `git status --porcelain` to warn before pulling onto dirty tree.
  - `new_tool_wizard.py` — `_detect_commons_url` runs `git remote
    get-url origin` when the wizard opens, then `git init` / `git
    submodule add` during scaffold.

### 1b. Stylesheet double-cascade render hang (the "PCC has no new design")

The Phase 3C retrofit's `main.py` calls `apply_pcc_theme(app)` before
MainWindow is created. That function correctly chains:

  1. `phoenix_commons.theme.apply_dark_theme(app, brand=PCC_BRAND)` —
     installs commons base QSS at the application level with PCC's
     orange + teal `BrandProfile` sentinel substitutions.
  2. Appends the PCC chrome overlay (`make_qss()`) to the app
     stylesheet.

The application-level cascade is correct and sufficient.

But the pre-retrofit `MainWindow.__init__` still ran
`self.setStyleSheet(make_qss())` on line 48. Qt treats a widget-level
`setStyleSheet` as the **new cascade root** for that widget subtree —
it does not merge with the application-level cascade, it overrides it.

That had two visible consequences:

  - The full PCC stylesheet was recomputed a second time during
    MainWindow construction. Empirically (via screen recording at 2 fps
    + 10 fps frame extraction) this manifested as a ~2.5-second
    solid-black render hang before any UI snapped in.
  - The commons base styling (Phoenix navy surfaces + tokens) never
    reached MainWindow's children. Only the PCC overlay's selectors
    (`#sidebar`, `#topbar`, `#toolCard`, `#sectionHeader`, etc.) were
    visible. The operator observation "PCC doesn't have any of the
    new design elements" was literally correct — the commons cascade
    was being thrown away at MainWindow level.

The same pattern repeated on five dialog openings (Settings, NewTool,
About, Shortcuts, PushPreview) and one QMessageBox (pull-with-dirty
warning) — each `dlg.setStyleSheet(make_qss())` overrode the app-level
cascade for that dialog tree.

---

## 2. Exact fix implemented

Two commits on `phase-3c-pcc-retrofit`:

### B5 (bad7cd1) — Hide cmd.exe console flash on git subprocess calls

```python
# scanner.py / detail_panel.py / new_tool_wizard.py
_HIDE_CONSOLE = subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0
```

Applied as `creationflags=_HIDE_CONSOLE` to every `subprocess.check_output`
/ `subprocess.run` / `subprocess.Popen` call that runs `git`:

  - `scanner.py` — `_run()` helper (services ~17 ScanWorker callsites),
    `git_pull`, `git_push`, `git_fetch`.
  - `detail_panel.py` — the `git status --porcelain` dirty-check before
    pull. Editor + terminal launchers (`os.startfile`,
    `subprocess.Popen([editor, path])`) deliberately **not** modified
    — those open user-facing GUI applications that should show windows.
  - `new_tool_wizard.py` — `_detect_commons_url`'s
    `git remote get-url origin` + `_run_subprocess` helper that runs
    `git init` / `git submodule add` at scaffold time.

`CREATE_NO_WINDOW` is the standard Win32 process-creation flag for
"don't allocate a console when launching this child process." Used by
all four production Phoenix tools in their own subprocess code. Not a
signature-evasion or AV-bypass technique — it's the documented Microsoft
API for windowed-GUI apps that need to call console utilities silently.

### B6 (9fdb796) — Remove redundant widget-level setStyleSheet

Removed all 7 widget-level `setStyleSheet(make_qss())` calls:

  - `main_window.py`: 5 calls (MainWindow itself + 4 dialogs).
  - `detail_panel.py`: 2 calls (1 QMessageBox + 1 PushPreviewDialog).

Each removal replaced with a one-line comment explaining the cascade
behaviour, so a future contributor doesn't reintroduce it. Dead
`make_qss` imports cleaned up in both files (still imported into
`theme.py`'s `apply_pcc_theme`, where it is needed).

App-level cascade established in `main.py` via `apply_pcc_theme(app)`
now flows to MainWindow + every child widget + every dialog
unimpeded.

---

## 3. Startup behavior before / after

| Phase                          | Before (B4)                                                                                                                 | After (B5 + B6)                                          |
|--------------------------------|-----------------------------------------------------------------------------------------------------------------------------|----------------------------------------------------------|
| `QApplication.__init__`         | (immediate)                                                                                                                 | (immediate)                                              |
| `apply_pcc_theme(app)`         | sets app stylesheet to commons base + PCC overlay                                                                            | unchanged                                                |
| `MainWindow()` construction     | re-cascades PCC overlay a second time — ~2.5s black-frame render hang                                                       | constructs immediately, app cascade reused               |
| First `ScanWorker.run()` tick   | ~17 cmd.exe console windows flash open + closed during git probes                                                            | console flashes suppressed; scan runs silently           |
| Dashboard first paint           | commons base **invisible** — only the PCC overlay's selectors take effect, dashboard looks identical to pre-retrofit         | commons base + PCC overlay both visible; navy surfaces  |
| Dialog open (Settings, etc.)    | each dialog re-cascades PCC overlay locally; commons base invisible inside dialogs too                                       | dialogs inherit app cascade; consistent with main window |

Source-mode launch on the developer machine after B6: clean exit
(code 0), no stderr, no crashes, no perceptible startup hang.

Operator confirmation after B5 (verbatim): *"the windows popping up
are gone, looks better."*

---

## 4. Visual polish changes (first flagship pass)

Single commit, B7 (0fa40e3), three targeted edits in `theme.py`'s PCC
overlay. All within the Step 3 ALLOWED list (typography polish,
hierarchy, density tuning); none in the NOT-ALLOWED list (no redesign,
no second design system, no palette experiments).

  1. **`QLabel#pageTitle`**: `20px/700` → `22px/800` + `letter-spacing:
     -0.3px`. The "Dashboard" / "Commons" / detail-panel headings now
     read with measurably more presence on first paint. Flagship-class
     desktop apps tend toward heavier display type on top-level
     section titles; this nudges PCC in that direction without leaving
     the existing weight scale.

  2. **`QLabel#sectionHeader`**: padding `14/16/4/16` → `16/16/6/16`.
     Two pixels of breathing room above each section header
     ("NAVIGATION", "TOOLS", "RECENT ACTIVITY") and two pixels below
     before list content begins. Section headers no longer feel
     crowded against the surface above them.

  3. **`QListWidget#sidebarList::item`**: vertical padding `5px` →
     `7px`. Each sidebar nav row gets ~4px more clickable surface,
     improving Fitts'-law targeting and making the sidebar feel less
     cramped relative to the dashboard's roomier whitespace. The
     custom `SidebarToolWidget` (with its own 4px margin) still fits
     without clipping.

No palette change, no widget structure change, no new components, no
new selectors.

---

## 5. Runtime validation

  - `python -m compileall -q . -x "\.venv|commons|build|dist|__pycache__"`
    — clean (no errors).
  - `python -m pytest -q tests/` — 4 passed in 0.18s (smoke tests:
    module imports, version format, MainWindow instantiates, theme
    QSS non-empty).
  - `python main.py` source-mode launch — exit code 0, no stderr.
    Window appeared without the prior 2.5s black-frame hang; scan ran
    silently with no console flashes; dashboard rendered with commons
    base styling visible underneath the PCC overlay.

No regression observed against any prior Phase 3C smoke (B1-B4) or
prior PCC operational state (pre-retrofit).

---

## 6. Remaining UX debt (out of scope for B5-B7)

  - **First-run Settings dialog timing** — `_first_run_or_load`
    schedules `_open_settings` via `QTimer.singleShot(200ms)` to dodge
    the (former) render hang. With B6 in place the 200ms delay is no
    longer load-bearing, but the magic number remains. A follow-up
    pass should re-check whether the dialog can open synchronously
    after MainWindow.show().
  - **ScanWorker sequential model** — single `QThread` walks tools one
    at a time. With 4-6 tools in the root, this is fine; at 20+ tools
    it would matter. Out of scope per "do not redesign the loading
    system unnecessarily."
  - **No progress feedback during scan** — only a "● Scanning…" text
    indicator in the status bar. A flagship would have a progress
    chip per tool row + a global progress affordance. Deferred to a
    later UX session.
  - **`pre-pull dirty check` modal pattern** — `git status
    --porcelain` runs synchronously in the GUI thread before opening
    a QMessageBox. Fine for small repos; for a large repo it could
    micro-stutter. Out of scope.

---

## 7. Remaining visual debt (out of scope for B7)

  - **AggregateTile inline-styled typography** — the 5 stat tiles on
    the dashboard set `font-size: 28px; font-weight: 800;
    letter-spacing: -0.5px;` inline in `dashboard.py`. These cannot
    be themed via QSS, cannot share commons typography tokens, and
    cannot benefit from the B7 hierarchy polish. The fix is to add
    `#tileValue` / `#tileLabel` object names and move styling to
    `theme.py` — surgical but it touches dashboard.py, so it was
    deliberately deferred out of the polish-only pass.
  - **Status bar styled inline** — `main_window.py` lines 363-377 set
    `QStatusBar` style via concatenated f-string instead of QSS
    selectors. Same fix pattern as AggregateTile.
  - **Sidebar wordmark** — "🔥 Phoenix / Command Center" is still a
    Segoe UI emoji + two `QLabel` widgets. A flagship would have a
    proper icon graphic + custom wordmark.
  - **Emoji-as-icon usage** — `◈ ◆ 🔥 📌 📄 💾 ●` litter the dashboard
    + sidebar. These render inconsistently across Windows themes and
    don't compose with PCC's brand colour. Once
    `phoenix_commons.icons` is consumed by PCC (slated for a later
    phase), every emoji glyph should become an SVG icon with
    Phoenix-tinted fill.
  - **Spacing scale not normalized** — the codebase uses 4 / 5 / 6 /
    8 / 10 / 12 / 14 / 16 / 20 / 24 px margins and paddings
    ad-hoc. A flagship-grade pass would lock to {4, 8, 12, 16, 20,
    24, 32} only. Significant churn; deferred.
  - **Status indicator polish** — clean/dirty/unknown dots are bare
    Unicode `●` glyphs at 9px. A polish pass should consider an
    animated or glow-tinted indicator on scan-completion.

---

## 8. Recommended next implementation priorities

In rough order of operator-visible impact per unit of risk:

  1. **Operator visual review of post-B7 state.** Before any more
     code lands, run PCC source-mode, capture screenshots of
     dashboard + commons browser + detail panel + new-tool wizard,
     and identify specific surfaces that still feel "old." B5-B7
     should have closed the perceptual gap, but only direct visual
     review can confirm.
  2. **AggregateTile → QSS object names.** Move tile typography out
     of inline styles in `dashboard.py` into `#tileValue`,
     `#tileLabel`, `#tileAccent` selectors in `theme.py`. Enables
     future polish passes to retune all 5 tiles in one place.
  3. **Status bar → QSS selectors.** Same migration as above for the
     `QStatusBar` styling block.
  4. **Spacing-scale normalization.** Choose {4, 8, 12, 16, 20, 24,
     32} as the canonical px scale, audit every
     `setContentsMargins` / `setSpacing` / QSS padding callsite, and
     migrate. Should be a single PR with mechanical edits.
  5. **Phoenix-commons icon adoption.** Once PCC's retrofit consumes
     `phoenix_commons.icons`, swap the emoji glyphs (`◈ ◆ 🔥 📌 📄 💾
     ●`) for SVG icons with Phoenix-tinted fills. Coordinated with
     the icon package's `BrandProfile`-aware tinting story.
  6. **Subtle scan-completion accent moment.** When `_on_scan_done`
     fires, pulse the status indicator or briefly tint the tile
     borders with PCC accent orange. Adds a flagship "alive" feel
     without changing any persistent surface.
  7. **First-run dialog timing review.** Re-check whether the 200ms
     `QTimer.singleShot` delay is still needed; remove the magic
     number if not.

None of these are merge blockers for the current `phase-3c-pcc-retrofit`
branch.

---

## 9. Confirmation — STOP-condition compliance

  - **No architecture expansion occurred.** No new modules created. No
    new threading model. No new async framework introduced. The
    module map (`main.py`, `main_window.py`, `dashboard.py`,
    `detail_panel.py`, `scanner.py`, `theme.py`, `config.py`, etc.)
    is unchanged. The QApplication / QMainWindow / QThread structure
    is unchanged.
  - **No production deployment occurred.** All work is source-mode
    only on the `phase-3c-pcc-retrofit` branch. No installer was
    built, no `dist/` zip was created, no GitHub Release was
    published. PCC remains a source-run-only management app per its
    CLAUDE.md.
  - **No AV-bypass behaviour occurred.** `subprocess.CREATE_NO_WINDOW`
    is the documented Win32 API for suppressing console allocation on
    child processes spawned from a GUI parent. It is used by every
    one of the four production Phoenix tools (Job Tracker, Phoenix
    CAD, Phoenix Checkout, ValveMaster) in their existing,
    SentinelOne-cleared production code. It does not modify file
    signatures, bootloader content, or any other AV-relevant surface.
    The Phase 6D `FROZEN_BUILD_BASELINE.md` heuristics around S1
    quarantine are entirely orthogonal — those concern PyInstaller
    bootloader content shape, which `CREATE_NO_WINDOW` does not
    touch.
  - **No commons changes.** B5-B7 are PCC-only commits on
    `phase-3c-pcc-retrofit`. The `phoenix-commons` submodule pointer
    is unchanged. No edits to `phoenix_commons.theme`,
    `phoenix_commons.widgets`, `phoenix_commons.updater`, or any
    other commons module.
  - **No commons-doctrine drift.** The fixes are consistent with
    `MIGRATION_RULES.md` ("retrofits must preserve the app's
    surgical scope"), `RETROFIT_PLAYBOOK.md` ("favor app-level
    cascade over widget-level overrides"), and ADR-016 (the
    `BrandProfile` mechanism PCC's retrofit consumes is unaltered).

---

## Commit summary

| Commit  | Subject                                                                | Files                                                                    |
|---------|------------------------------------------------------------------------|--------------------------------------------------------------------------|
| bad7cd1 | Hide cmd.exe console flash on git subprocess calls (Phase 3C B5)        | `scanner.py`, `detail_panel.py`, `new_tool_wizard.py`                     |
| 9fdb796 | Remove redundant widget-level setStyleSheet (Phase 3C B6)               | `main_window.py`, `detail_panel.py`                                       |
| 0fa40e3 | First flagship polish pass: typography + density (Phase 3C B7)          | `theme.py`                                                                |

Branch tip: `0fa40e3` on `phase-3c-pcc-retrofit`. Not merged.

Recommended merge gate: operator visual review of post-B7 state
(priority 1 in §8) → if confirmed flagship-feeling improved, proceed
to merge `phase-3c-pcc-retrofit` → `master` per `MIGRATION_RULES`
Phase 3 merge protocol.

---

*End of report.*
