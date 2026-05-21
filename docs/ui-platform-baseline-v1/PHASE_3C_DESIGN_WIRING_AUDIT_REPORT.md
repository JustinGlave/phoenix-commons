# Phase 3C — Design Wiring Audit Report

> **Status:** complete (audit only, no source changes landed).
> **Date:** 2026-05-20.
> **Branch audited:** PCC `phase-3c-pcc-retrofit` at tip `0fa40e3`.
> **Scope:** answer "why does the running app still look like the old
> PCC UI when the intended new design exists in the files?"
> Audit only — no new design invented, no polish, no subjective tweaks.

---

## TL;DR

The intended richer PCC dashboard design **exists in `tool_card.py`** as a
`ToolCard` widget (270×215 card with stats + four action buttons:
VS Code, GitHub, Pull, Launch). It has **never been imported by any code
on any branch in this repo's history**, since the initial commit. The
running dashboard instead uses an inline `ToolRow` class (a flat
horizontal list row) defined locally in `dashboard.py`. A stale
`QGridLayout` import in `dashboard.py` (also never used) suggests the
original intent was a grid of `ToolCard`s and the wiring was never
landed.

The commons widget library (`phoenix_commons.widgets`) is fully
available via the Phase 3C editable install but is **not imported by
any PCC running-code module**. PCC's retrofit was theme-only.

No stale caches, no wrong-branch confusion, no QSS override after
Phase 3C B6, no version mismatch. The cascade is correctly wired and
commons base styling IS being applied — it just provides the
QMainWindow/QWidget/QMenuBar/QPushButton baseline, not the
dashboard-grid layout the operator review screenshot shows.

---

## 1. Where the intended new design currently lives

Three orphan-or-near-orphan locations identified:

### 1a. `tool_card.py` — the prime candidate

Path: `C:\Users\justing\PycharmProjects\phoenix-command-center\tool_card.py`

```python
class ToolCard(QFrame):
    """A card widget representing a single tool/repo. Emits signals for
    all actions and for selection."""
    selected    = Signal(str)   # tool name
    act_vscode  = Signal(str)   # tool path
    act_github  = Signal(str)   # github url
    act_pull    = Signal(str)   # tool path
    act_launch  = Signal(str)   # tool path

    # Fixed 270×215 card.
    # Header: badge + name + status dot
    # Stats: ⏱ commit, 📄 LOC, 💾 size, 📌 TODOs
    # Action buttons: VS Code, GitHub, Pull, Launch (accent-coloured)
```

This is a **PCC-local** widget (not commons). It defines the richer
card-based representation an operator would recognise as "the intended
design." Its `update_stats(data)` consumes `last_commit`, `branch`,
`loc`, `total_size`, `todo_count`, `status` — which are exactly the
fields `scanner.py` produces.

### 1b. `commons/Design Items/Phoenix_Tool_Design_V1/` — design reference

Six files (all in the `phoenix-commons` submodule, not PCC source):

```
CLAUDE_STARTER_PROMPT.txt
INTEGRATION_GUIDE.md
phoenix_design_system.md
phoenix_implementation.py     ← example PySide6 widgets
phoenix_mockups.html          ← HTML mockups
phoenix_style.qss             ← canonical QSS
```

`phoenix_implementation.py` defines reference widgets (`PrimaryButton`,
`PhoenixMainWindow`, `FormInput`, `DataTable`, `PageTitle`, etc.) and
three example tool windows (`ModelDecoderWindow`, `ProjectManagerWindow`,
`CheckoutWindow`). **These are templates for individual Phoenix TOOLS,
not for the PCC management hub.** The mockup HTML shows the same — a
tool with File/Edit/View/Tools/Help menubar + form inputs + action
buttons, not a sidebar-and-tile-grid management dashboard.

This content has been codified into `phoenix_commons.widgets/theme` (the
runtime package) — those reference files are now historical pre-package
artifacts.

### 1c. `phoenix_commons.widgets` — codified design system

Path: `C:\...\commons\src\phoenix_commons\widgets\__init__.py`

Public API (verified by reading `__init__.py`):

```
PrimaryButton, SecondaryButton, TertiaryButton
PageTitle, PageSubtitle, SectionTitle, HintLabel
Panel
PhoenixTable
UpdateBanner
button_row
NoScrollComboBox, NoScrollSpinBox, NoScrollDoubleSpinBox, NoScrollDateEdit
```

Fully installed via Phase 3C's editable install (verified —
`python -c "import phoenix_commons; print(phoenix_commons.__file__)"`
resolves to `commons/src/phoenix_commons/__init__.py`, version 0.1.0).

---

## 2. Whether it is wired into the running app

| Location | Imported by PCC running code? |
|----------|-------------------------------|
| `tool_card.py` (`ToolCard`) | **NO** — zero imports anywhere in history |
| `commons/Design Items/Phoenix_Tool_Design_V1/*.py` | **NO** — design reference, not runtime |
| `phoenix_commons.widgets.PrimaryButton` etc. | **NO** — no PCC code imports |
| `phoenix_commons.theme.apply_dark_theme` | **YES** — via `theme.py:35` |
| `phoenix_commons.theme.tokens.BrandProfile` | **YES** — via `theme.py:36` |
| `phoenix_commons.paths.*` | **NO** — PCC uses its own `paths.py` |
| `phoenix_commons.updater.*` | **NO** — PCC has no updater (source-run only) |
| `phoenix_commons.icons.*` | **NO** |

Evidence (grep against `*.py` excluding `.venv`):

```
PCC imports from phoenix_commons:
  theme.py:35  from phoenix_commons.theme import apply_dark_theme as _commons_apply_dark_theme
  theme.py:36  from phoenix_commons.theme.tokens import BrandProfile

PCC imports from tool_card:
  (none)

PCC imports from commons/Design Items:
  (none)
```

`phoenix_tool_templates.py` references `phoenix_commons.widgets`
extensively, but that's the **scaffolding template for new tools the
wizard generates** — it isn't PCC's own running code path.

---

## 3. What code path the running app actually uses

Verified by reading `main.py`, `main_window.py`, `dashboard.py`,
`sidebar_tool_widget.py`, `detail_panel.py`, `theme.py`, plus
recent commits B1–B7 on `phase-3c-pcc-retrofit`.

```
main.py
  └── QApplication
        ├── apply_pcc_theme(app)             ← theme.py:113
        │     ├── phoenix_commons.theme.apply_dark_theme(app, brand=PCC_BRAND)
        │     │     └── installs commons base QSS + sentinel brand
        │     │         substitution at APP LEVEL
        │     └── append make_qss() overlay (PCC chrome)
        └── MainWindow()
              ├── sidebar (QFrame#sidebar)
              │     ├── logo  (Segoe UI emoji 🔥 + 2 QLabels)
              │     ├── nav QListWidget (Dashboard / Commons / TOOLS)
              │     │     └── SidebarToolWidget per tool   ← sidebar_tool_widget.py
              │     ├── SidebarSprite (animated WebP)
              │     └── 3 action buttons (✦ New Tool / ↻ Refresh / ⚙ Settings)
              └── content QStackedWidget
                    ├── [0] Dashboard()                    ← dashboard.py
                    │         ├── AggregateTile × 5 (inline-styled)
                    │         ├── Left: VBoxLayout of inline ToolRow ← THIS is
                    │         │      the "old-looking" list
                    │         └── Right: VBoxLayout of ActivityRow
                    ├── [1] CommonsBrowser()               ← commons_browser.py
                    └── [2] DetailPanel()                  ← detail_panel.py
```

No `ToolCard` reachable from any node in that tree. No
`phoenix_commons.widgets.*` reachable either. The dashboard's `ToolRow`
is defined inline as a `dashboard.py:51` class (compact horizontal
row: badge + name + 📌 chip + ● dot + ›).

The app **is** on `phase-3c-pcc-retrofit` at `0fa40e3` (B7). The B6
removal of widget-level `setStyleSheet` calls **is** in place, so
commons cascade IS reaching the widget tree. But commons selectors
target QMainWindow/QWidget/QPushButton baselines + `#title /
#sectionTitle / #hint / #secondaryButton / #tertiaryButton` —
none of which PCC's custom widgets use. PCC's overlay uses its own
disjoint vocabulary: `#pageTitle / #sectionHeader / #accentBtn /
#ghostBtn / #toolCard / #statCard / #cardTitle / #cardStat / #sidebar
/ #topbar / #sidebarList / ...`.

So commons styling is "applied" but doesn't visibly affect PCC's
dashboard widgets because the selectors don't overlap.

---

## 4. Why the visual result still looks old

Three independent layers all contribute:

### 4a. The richer card design was never wired (the primary reason)

`tool_card.py:ToolCard` has existed since the initial commit (`3d84cc9`
"Initial commit — Command Center baseline before Phase 5"). Searching
the git history across all branches with
`git log --all -S "ToolCard" -S "from tool_card" -S "import tool_card"`
returns **only** the initial-commit definition. Nothing has ever
imported it. The dashboard has used inline `ToolRow` from day one.

### 4b. `dashboard.py` carries a stale `QGridLayout` import

`dashboard.py:8`:
```python
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QScrollArea,
    QPushButton, QSizePolicy, QGridLayout
)
```

`QGridLayout` is imported but never instantiated. The only layouts
actually used are `QVBoxLayout` and `QHBoxLayout`. The vestigial import
strongly suggests an earlier intent: a **grid of `ToolCard`s** (which
is what a `QGridLayout` is for — tile grids of fixed-size widgets) that
was either never built or was reverted before being committed.

### 4c. Commons widget library is not consumed for any PCC surface

`phoenix_commons.widgets.PrimaryButton`, `Panel`, `PhoenixTable`,
`PageTitle` etc. are all available via `pip install -e ./commons` (Phase
3C B1) but PCC's running modules use raw Qt widgets with PCC-specific
object names. Phase 3C's retrofit was THEME-ONLY (commit B2 was
`theme.py` only; B3 wired `apply_pcc_theme(app)` in main.py; no commit
swapped any widget instantiation). The retrofit report
(PHASE_3C_PCC_RETROFIT_AND_VISUAL_IMPLEMENTATION_REPORT) is explicit
about this scope.

### 4d. App-level cascade IS working — this is NOT the reason

Verified post-B6: `phoenix_commons.theme.apply_dark_theme(app,
brand=PCC_BRAND)` runs first in `apply_pcc_theme()`, then the PCC
overlay is appended via `app.setStyleSheet(base + overlay)`. No
widget-level `setStyleSheet(make_qss())` calls remain to override the
cascade for any subtree. The commons base IS visible — it provides
QMainWindow background, QMenuBar styling, QMenu styling, base button
colours, line-edit/combo-box/spinbox styling, scrollbar styling,
QToolTip styling.

The reason it doesn't "look new" is that the commons base styles
applied things PCC's dashboard surface barely uses (no QMenu in the
content area, no QSpinBox / QComboBox / QTableWidget on the dashboard,
no `#title` / `#sectionTitle` / `#hint`-named labels). PCC's dashboard
content surface is composed entirely of `QFrame`s with PCC's chrome
selectors (`#toolCard`, `#statCard`, `#pageTitle`) — which only the PCC
overlay styles.

---

## 5. Minimal surgical fix plan

This fix is **NOT clearly low-risk** (per the audit's stop condition,
flagged for operator approval before landing).

### Fix plan: wire `ToolCard` into the dashboard grid

```
dashboard.py:
  1. Add `from tool_card import ToolCard` at the top.
  2. Remove the inline `ToolRow` class definition (lines 51–177).
  3. In Dashboard._build():
     - Replace `self.list_layout = QVBoxLayout(self.list_container)`
       with `self.list_layout = QGridLayout(self.list_container)`
     - Set grid spacing + margins to match the intended card grid.
  4. In Dashboard.set_tools():
     - For each tool, instantiate `ToolCard(name=t["name"],
       path=t["path"], github_url=tc.get("github_url",""),
       is_commons=is_c)` instead of `ToolRow(...)`.
     - Place into the grid via `self.list_layout.addWidget(card, row,
       col)` with a column-count derived from the column width
       (~3 columns at 1300×800 default; 2 if narrower).
     - Connect `ToolCard.selected` → `self.tool_selected` (same as
       current `ToolRow.clicked` wiring).
     - Connect `ToolCard.act_vscode / act_github / act_pull /
       act_launch` to new dashboard signals
       (`vscode_requested(str path)`, `github_requested(str url)`,
       `pull_requested(str path)`, `launch_requested(str path)`).
  5. In Dashboard.update_tool():
     - Same — `_rows[name].update_stats(data)` already works because
       `ToolCard.update_stats` accepts the same shape (just with
       additional keys it knows how to render).

main_window.py:
  6. In _open_detail (or wherever the dashboard tool_selected is
     handled), add slots for the new dashboard signals that delegate
     to the existing action helpers in detail_panel (the action
     wiring already exists; we just need to route from the dashboard
     to the same handlers, instead of forcing the user to drill into
     the detail panel first).
```

That's the surgical version. No new design invented; the design
already exists in `tool_card.py`. No commons widgets touched. No new
QSS rules. No layout-engine swap beyond `VBoxLayout → GridLayout`
inside the existing scrollable left column.

### What this fix does NOT do

  - Does NOT migrate any widget to `phoenix_commons.widgets.*`. That
    is a separate, larger retrofit phase (Phase 3D candidate). Out of
    scope here.
  - Does NOT touch the sidebar — `SidebarToolWidget` continues to
    show the compact per-tool row in the sidebar nav list. Only the
    dashboard's left-column tool list changes.
  - Does NOT change the right-column activity feed (still uses
    `ActivityRow`).
  - Does NOT change the aggregate stat tiles at the top of the
    dashboard.
  - Does NOT change the detail panel, settings dialog, or wizard.

---

## 6. Files that need to change

| File | Change |
|------|--------|
| `dashboard.py` | Import `ToolCard`; remove inline `ToolRow` class; switch `list_layout` to `QGridLayout`; instantiate `ToolCard` in `set_tools`; add four signal forwards for the four action buttons. |
| `main_window.py` | Add slot wiring for the four new dashboard action signals → existing handlers (open-in-vscode / open-in-browser / git-pull / launch). The handlers exist (detail_panel + scanner already implement them); only the routing is new. |
| `tool_card.py` | No change — already correct. |
| `theme.py` | No change. |
| `main.py` | No change. |

That's the entire surgical change set. Two files modified, ~80 lines
of code touched.

---

## 7. Risks

In rough order of severity:

  1. **Grid-vs-list reflow on narrow viewports.** `ToolCard` is a
     fixed 270×215. At PCC's minimum window size (1100×700), the
     left column of the dashboard is ~3/10 of the content area =
     ~324px wide. That fits exactly one card per row. The current
     `ToolRow` shrinks to fit (`setSizePolicy(QSizePolicy.Ignored,
     QSizePolicy.Preferred)` + `setMinimumWidth(0)`). The new card
     layout will either need to be 1-column at narrow widths or use
     a responsive column-count calculation in
     `Dashboard.resizeEvent()`. Either approach works; the latter is
     ~20 more lines.
  2. **`ToolCard.act_launch` semantics drift.** `ToolCard` emits a
     bare `path` on launch, but PCC's existing tool-launch logic
     (in `detail_panel`) uses a per-tool `launch_cmd` from
     `pcc_config.json`. The fix needs to look up the launch_cmd in
     the dashboard action handler, same way `detail_panel` already
     does. Same pattern, but new code in `main_window`.
  3. **Per-card data freshness.** `ToolCard.update_stats(data)` is
     called by `dashboard.update_tool(name, data)` — same flow as
     `ToolRow` today. Low risk; the data shape already matches.
  4. **Visual densification.** With 4–6 production tools + commons,
     the grid will show 4–6 cards. At ~290×235 effective footprint
     (card + grid gap), that's ~3 cards across in the default 1300px
     window. Visually denser than the current 6-line flat list. This
     IS the intended design, but worth confirming with the operator
     before landing — the audit explicitly does NOT invent a new
     design, but the change IS visible.
  5. **Status dot animation regression.** Both `ToolRow` and
     `ToolCard` show a status dot that updates colour from the scan.
     Same code path — no regression expected.
  6. **Sidebar nav still shows compact rows.** `SidebarToolWidget`
     unchanged, so clicking a sidebar tool entry still works.
     Dashboard cards add a second click target for the same action.
     Both should route through the same `_open_detail` path. Low
     risk if signals are correctly wired.
  7. **`tool_card.py` button styling.** `ToolCard._mini_btn` uses
     inline styles for its action buttons. These will render as-is
     without picking up either commons or PCC overlay styles for
     buttons. Visually consistent with the rest of the card, but
     diverges from the PCC overlay's `#ghostBtn`/`#accentBtn`
     palette. Out of scope for the wiring fix — separate cleanup
     task if desired.

None of these risks are merge blockers. All are mitigable in code.

---

## 8. Confirmation — no new design invented

  - **`ToolCard` already exists** in `tool_card.py` (initial commit,
    `3d84cc9`). The fix wires the pre-existing widget into the
    pre-existing dashboard. No new component class is proposed.
  - **`QGridLayout` already imported** in `dashboard.py:8`. The fix
    uses the existing import. No new layout engine is proposed.
  - **No new QSS rules** are proposed. `ToolCard` already self-styles
    via inline QSS in `tool_card.py:66-77` + `_mini_btn` + the
    PCC overlay's `#toolCard` and `#cardTitle`/`#cardStat`
    selectors (all of which already exist in `theme.py`'s overlay).
  - **No subjective visual tweaks.** No spacing changes, no
    typography changes, no palette experiments. The polish pass B7
    is not extended.
  - **No second design system.** Commons widget library
    (`phoenix_commons.widgets`) is NOT swapped in. That's a separate
    retrofit phase (3D candidate).
  - **No commons changes.** No edits to `phoenix-commons` package
    or its QSS.

---

## STOP

Per the audit spec stop condition ("Stop after the audit unless the
fix is clearly mechanical and low-risk"): this fix is **mechanical**
(import + signal wiring + layout swap) but **not low-risk** (Risk 1
and Risk 4 in §7 are visible operator-facing changes). The audit is
complete; the fix plan is documented in §5–§7; **awaiting operator
approval before landing**.

If approved, the fix lands as a single commit `B8 — Wire ToolCard
into dashboard grid (Phase 3C)` on `phase-3c-pcc-retrofit`. Pre-flight:
the existing smoke tests (`test_module_imports`, `test_version_format`,
`test_main_window_instantiates`, `test_apply_dark_theme_does_not_raise`)
will continue to pass. New ad-hoc verification: visual confirmation
that the dashboard now shows a grid of cards instead of a list of
rows, with each card's four action buttons (VS Code / GitHub / Pull /
Launch) wired to the same handlers `detail_panel` already provides.

---

*End of report.*
