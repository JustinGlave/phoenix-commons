# PCC Detail Panel Surface Spec — v1

> **Status:** product direction. Pre-implementation.
> **Date:** 2026-05-21.
> **Phase:** 3D.
> **Scope:** the PCC detail panel — its purpose, hierarchy, layout, visual feel,
> and the surfaces it composes. No code. No retrofit doctrine. No
> architectural change to commons or ADR-016. Reuses every primitive
> Phase 3C produced.
> **Inputs:** current `detail_panel.py` (784 LOC; pre-retrofit chrome), the
> Phase 3C dashboard surfaces, `PCC_DASHBOARD_SURFACE_SPEC_V1`, ADR-016,
> commons widgets (Panel, StatusBadge, PrimaryButton, SecondaryButton,
> TertiaryButton, PhoenixTable, Lucide icons), `PCC_FULL_DASHBOARD_UX_REVIEW_01`
> §3 ("What still feels old" — detail panel was the headline item).
> **Output:** this file. Operator approves the spec; implementation
> sequencing follows separately, one surface at a time.

---

## 1. Product intent

**The detail panel is the operator's per-tool operational control surface.** Not a viewer. Not a dashboard. The single screen the operator drills into to *do something with one specific tool* — pull, launch, inspect commits, triage TODOs, browse files.

The detail panel answers four operator questions, in priority:

1. **"What's the current state of this tool right now?"** — branch, last commit, sync state vs upstream, dirty files, ahead/behind.
2. **"What needs my attention?"** — open TODOs, uncommitted changes, unpushed commits.
3. **"How do I act on it?"** — pull / push / fetch / open in editor / open on GitHub / launch the tool.
4. **"What does this tool look like right now?"** — file browsing, recent commits.

Everything else is supporting chrome.

### What dominates visually

The **identity + status block** at the top. The operator hits the detail panel because they want to act on *this* tool — the tool's identity (name + branch + sync state) is the visual anchor.

### What feels secondary

The **tab-resident content** (Overview commits feed, TODOs list, Files browser, Git output). These are the deep surfaces; they need to be readable but never compete with the top status block for the operator's eye.

### What feels alive

  - Sync-state pill changing during pull/push/fetch operations
  - Git output streaming in the Git tab
  - File-viewer reflecting tree clicks
  - StatusBadge updating after a scan refreshes data

### What feels calm

Tab bar, tile row, panel chrome, back navigation. These define the workspace; they don't compete.

---

## 2. Workflow audit — what `detail_panel.py` looks like today

`detail_panel.py` is 784 lines. Five top-level classes:
  - `StatTile(QFrame)` — local-only tile widget (pre-retrofit, not `AggregateTile`).
  - `GitOpWorker(QThread)` — backend; not chrome.
  - `CommonsDropZone(QFrame)` — Files-tab affordance for dragging files into commons.
  - `SyncStatusCard(QFrame)` — Overview-tab ahead/behind/uncommitted chip cluster.
  - `TodoItem(QFrame)` — TODOs-tab per-item widget.
  - `DetailPanel(QWidget)` — the host widget.

### Current top bar (`detail_panel.py:402-437`)

```
[← Back] [Tool Name (pageTitle)] [branch badge] [status badge] [stretch]
                                                   [⬛ VS Code] [⌥ GitHub]
                                                   [▶ Run source] [▶ Launch installed]
```

  - 5 emoji-prefixed buttons in a row (Back + 4 actions). **Button soup.**
  - Branch badge: inline-styled `QLabel`, not a `StatusBadge`.
  - Status badge: inline-styled `QLabel` (separate from the dashboard's StatusBadge variant).
  - All four action buttons are raw `QPushButton` with PCC `objectName`s (`ghostBtn`, `accentBtn`) — not commons widget classes.

### Current tile row (`detail_panel.py:440-449`)

**Six tiles** in a row: Last Commit / LOC / Size / Open TODOs / Completed / Code Files.

  - Uses `StatTile` (local class), NOT the dashboard's `AggregateTile`. Different layout, no leading icons, no subtitles.
  - Six is more than the dashboard's five — and the dashboard's row already feels right at the edge.

### Current tabs (4 tabs, `detail_panel.py:452-504`)

| Tab | Contents | Issues |
|-----|----------|--------|
| **Overview** | `SyncStatusCard` (ahead/behind/uncommitted chips) + Recent Commits feed | Chip soup; commits feed not in a Panel container; inline-styled rows |
| **TODOs** | summary text + scrollable list of `TodoItem` widgets | TodoItems use emoji bullets; no Panel container |
| **Files** | QSplitter with QTreeView + FileViewer + CommonsDropZone | Functional surface; mostly fine but feels chrome-less |
| **Git** | Pull/Push/Fetch buttons + raw `QLabel` git output | Emoji-prefixed buttons; output is a stretched QLabel, no monospace container, no Panel wrapping |

### What still feels "legacy PCC" (operator's term)

  1. **Top bar button cluster** — 4 actions + Back + title + 2 badges all in one horizontal row. Visually crowded.
  2. **Emoji icons on every action button** — ⬛ ⌥ ▶ ▶ ⬇ ⬆ ↻ — half the surfaces still emoji-tagged.
  3. **`StatTile` ≠ `AggregateTile`** — chrome drift between dashboard and detail panel.
  4. **Inline-styled chips and badges** everywhere — branch badge, status badge, SyncStatusCard's three sub-chips, TodoItem markers, Recent Commits message rows.
  5. **Raw `QPushButton` everywhere** — no `PrimaryButton`/`SecondaryButton`/`TertiaryButton` consumption.
  6. **No `Panel` containers** — tab contents float in tab-pane frames without the rounded-card chrome that dashboard's TOOLS and RECENT ACTIVITY panels carry.
  7. **Git output is a raw `QLabel`** with inline-styled background — should be a monospace text surface in a Panel container.
  8. **Six aggregate tiles** — already too many; matches the operator's earlier "tiles are crowded" reaction.

### What still works well

  - The **4-tab structure** (Overview / TODOs / Files / Git) is logical. Each tab maps to a distinct operator question. Keep the structure.
  - The **Files tab's QTreeView + FileViewer + CommonsDropZone** is a domain-specific functional surface — operators drag from the tree into commons. Less "chrome-driven" than the other tabs. Probably fine to leave largely alone except for icon migration.
  - The **back-navigation** affordance (button + Escape key handling in `MainWindow`) is intuitive.
  - The **per-tool launch differentiation** (Run source vs Launch installed) is operationally correct — enabled/disabled based on what's actually present. Keep.

---

## 3. Surface inventory

Seven surfaces compose the modernized detail panel. Each gets a paragraph of intent + a priority classification.

### 3.1 Top utility band — PRIMARY

Rebuild the top bar as a single horizontal band, mirroring the dashboard's utility band rhythm:

  - **Left:** Back button (commons `TertiaryButton` or `ghostBtn` equivalent, with a `arrow-left` Lucide icon).
  - **Title block (left-of-center):** Tool name (pageTitle) + branch sub-label.
  - **Status block (center-or-trailing):** Single `StatusBadge` showing the tool's primary state (`clean` / `N changes` / `unknown` / `scanning` / `error`). Replaces both the current branch-badge `QLabel` and the status-badge `QLabel`.
  - **Right:** Action button group, restructured per §4.

The header is the operator's identity anchor. The operator should know what tool they're looking at and its current state within 200 ms of the panel painting.

### 3.2 Action button group — PRIMARY

The current top-bar 4-action cluster gets restructured into a clearer hierarchy:

| Action | Treatment | Lucide icon |
|--------|-----------|-------------|
| **Launch installed** | `PrimaryButton` (red brand-primary, dominant) | `play` (or `rocket`) |
| **Run source** | `SecondaryButton` (deep-blue, supporting) | `play-circle` (or `terminal`) |
| **Open in VS Code** | `TertiaryButton` (outline, low-emphasis) | `code` |
| **Open on GitHub** | `TertiaryButton` (outline, low-emphasis) | `external-link` (or `github`) |

When the installed exe isn't present, "Launch installed" disables (current behaviour); the SecondaryButton "Run source" remains the operator's path. The hierarchy reads as: **launch > run > inspect**.

### 3.3 Aggregate tiles row — SECONDARY

Reduce from 6 tiles to **4 tiles** (matches dashboard's tile count). Drop the "Completed" and "Code Files" tiles (low operator-value — Completed = TODOs done count, which is in the TODOs tab; Code Files = file count, which is in the Files tab).

The 4 retained tiles, with leading Lucide icons + subtitle convention matching the dashboard:

| Tile | Icon | Subtitle convention |
|------|------|---------------------|
| **Last Commit** | `clock` | branch name (e.g. "on main") |
| **LOC** | `file-text` | "across N files" |
| **Size** | `hard-drive` | total file count |
| **Open TODOs** | `warning` | "N marked FIXME" / "all clear" |

Use the **same `AggregateTile` class** that the dashboard uses (already supports `icon_name` + `subtitle` kwargs). Zero new commons primitives.

### 3.4 Overview tab — PRIMARY tab

  - **Sync-state card** (replaces `SyncStatusCard` chip soup) — single `Panel` containing 3 `StatusBadge` instances:
    - "↑ N unpushed" / "✓ in sync" (variant: `dirty` if N>0 else `clean`)
    - "↓ N behind" / "✓ up to date" (variant: `dirty` if N>0 else `clean`)
    - "N uncommitted" / "Clean tree" (variant: `dirty` if N>0 else `clean`)
  - **Recent Commits** — wrapped in a `Panel("Recent Commits")` container, each commit row is a clean message + timestamp pair (no inline-styled chrome).

### 3.5 TODOs tab — PRIMARY tab

  - **Summary row** at top: counts (open / completed / FIXME) as `StatusBadge` pills.
  - **TodoItem list** — wrap in `Panel`. Each TodoItem migrates to a leading Lucide icon (instead of emoji), tighter row chrome, and a small `StatusBadge` per item for `open` / `done` / `fixme` state.

### 3.6 Files tab — TERTIARY tab

  - Largely unchanged structurally. QTreeView + FileViewer + CommonsDropZone is a functional surface.
  - **Cosmetic only:** any emoji glyphs on the CommonsDropZone get migrated to Lucide; the splitter handle uses a more restrained QSS treatment from commons.

### 3.7 Git tab — SECONDARY tab

  - **Action button row:** Pull / Push / Fetch — migrate to `SecondaryButton` (these are supporting operations, not destructive primary actions) with Lucide icons (`arrow-down` / `arrow-up` / `refresh`).
  - **Git output area:** wrap in a `Panel("Output")` container. Replace the raw `QLabel` with a `QPlainTextEdit` (read-only) using a monospace font — Consolas / Cascadia Code. Same operational feel as a terminal-like output surface.

---

## 4. Interaction philosophy

### Action hierarchy

Three-tier:
  1. **Primary** — `PrimaryButton` red. Used once per surface for the most operator-critical action. In the detail panel: **Launch installed** at the top.
  2. **Secondary** — `SecondaryButton` deep-blue. Used for supporting operations. In the detail panel: **Run source**, **Pull**, **Push**, **Fetch**.
  3. **Tertiary** — `TertiaryButton` outline. Used for inspection / navigation. In the detail panel: **Back**, **VS Code**, **GitHub**.

Operator can identify "what's the most important thing on this surface" by glancing for the red.

### Button semantics

Per-button rule: the button's color signals the operator's commitment level.
  - Red (Primary) = "this will start something running."
  - Blue (Secondary) = "this will execute an operation against the repo."
  - Outline (Tertiary) = "this opens something or navigates away."

### Status semantics

Identical to dashboard:
  - **`clean`** — operation healthy / state is good (green).
  - **`dirty`** — uncommitted / unsaved / pending (amber).
  - **`warning`** — non-fatal warning / partial success (amber).
  - **`error`** — operation failed (red).
  - **`unknown`** — state unobservable (muted slate).
  - **`scanning`** — actively scanning (brand-accent).
  - **`syncing`** — actively syncing (brand-accent).

No new variants introduced. `StatusBadge` from Phase 3C Step 2 covers everything.

### Dense vs spacious

  - **Top utility band:** spacious — operator-anchor zone, breathing room around action buttons.
  - **Tile row:** medium-density — 4 tiles with leading icons + subtitles, matches dashboard exactly.
  - **Tab content:** dense within sections, spacious between sections. Same rhythm as dashboard's TOOLS panel.
  - **Git output:** dense (monospace, low padding) — log-feel.

### Scrolling behavior

  - Each tab's primary content scrolls vertically when overflowing.
  - The top utility band + tile row never scroll.
  - The tab bar itself never scrolls horizontally (with 4 tabs there's no risk).
  - Git output scrolls within its container (don't tie it to the tab-pane scroll).

### Navigation rhythm

  - **Tabs:** Ctrl+1..4 jumps to Overview / TODOs / Files / Git (parallel to dashboard's Ctrl+1 for Dashboard and Ctrl+2 for Commons).
  - **Back to dashboard:** Escape key (already implemented in `MainWindow._on_escape`) + the Back button.
  - **No deep nesting.** Files tab opens files in the right pane via tree-click; never opens modal dialogs.

### Keyboard affordances

| Shortcut | Action |
|----------|--------|
| `Esc` | Back to dashboard |
| `Ctrl+1` | Switch to Overview tab |
| `Ctrl+2` | Switch to TODOs tab |
| `Ctrl+3` | Switch to Files tab |
| `Ctrl+4` | Switch to Git tab |
| `Ctrl+P` | Pull (Git tab focused only) |
| `Ctrl+Shift+P` | Push (Git tab focused only) |
| `Ctrl+R` / `F5` | Refresh this tool's scan data |

Optional and deferrable; the spec calls them out as `nice-to-have` rather than mandatory.

---

## 5. Visual direction

### Inherited from Phase 3C dashboard language

Every visual decision in the detail panel maps to a decision already made on the dashboard:

| Surface treatment | Dashboard origin | Detail panel application |
|-------------------|------------------|--------------------------|
| `StatusBadge` variants + compact mode | Phase 3C Step 2 | Tool top-bar status, sync-card pills, TODO item states |
| Panel rounded-card chrome | Phase 3C B11 polish | Wraps each tab's content + Recent Commits + sync-card + Git output |
| Lucide icons (no emoji) | Phase 3C Step 1 | All buttons + tile leading icons |
| Quieter table headers (where applicable) | Phase 3C B11.1 | Not yet a detail-panel surface, but `#dashboardToolsTable` QSS carve-out pattern is reusable if a future tab adds a table |
| AggregateTile with icon + subtitle | Phase 3C Step 5 | 4-tile row at top of detail panel |
| Per-tool tag colors | Phase 3C Step 4 | Not a detail-panel surface; only relevant on the dashboard activity feed |
| `pageTitle` 22px bold | Phase 3C B7 typography | Detail panel header title |
| `sectionHeader` small-caps muted | Phase 3C B11 polish | Section labels inside tabs |

### What should NOT return from old PCC

Explicitly forbidden by this spec:

  - **Chip soup** — no inline-styled QLabel chains for status indicators. Always `StatusBadge` or a Panel-contained primitive.
  - **Noisy button clusters** — never more than 4 buttons in a row. If we need more, they go in a context menu or a popover.
  - **Inconsistent spacing** — use Phase 3C's spacing tokens (`12px` between sections inside a Panel, `16px` between Panels, `20-24px` between major regions).
  - **Emoji semantics** — no emoji on any primary surface. The Files-tab CommonsDropZone is the last hold-out and gets migrated.
  - **Scattered status indicators** — every status goes through `StatusBadge`. No bespoke colored dots, no bespoke colored text, no bespoke colored borders to convey state.
  - **Raw `QPushButton` for visible actions** — always `PrimaryButton` / `SecondaryButton` / `TertiaryButton` from commons.
  - **Inline-styled `setStyleSheet` on the panel** — preserves the B6 invariant; styling flows through commons cascade + PCC overlay only.

### Typography

  - Tool title: `#pageTitle` (22px, 800 weight, slight negative letter-spacing) — same as dashboard.
  - Section headers inside tabs: `#sectionHeader` (10px uppercase muted 700 weight) — same as dashboard.
  - Aggregate tile values: same `AggregateTile` styling (28px, 800 weight, accent-coloured).
  - Body text: 12px regular.
  - Git output: Consolas/monospace 12px in a Panel-contained `QPlainTextEdit`.

### Motion / restraint

Allowed:
  - Hover transitions on buttons (150ms ease-out, same as dashboard).
  - StatusBadge variant changes on scan completion (instant, no fade).
  - Tab switch transitions (instant — Qt default).
  - Scroll-bar appearance/disappearance.
  - Sync-pill flips during git operations.

Forbidden:
  - Tile count-up animations on data load.
  - Sliding tab content transitions.
  - Fade-ins on initial paint.
  - Loading spinners — use sync pill `scanning` variant instead.
  - "Shimmer" skeleton placeholders.

### Chrome philosophy

Chrome recedes; data leads. Tab bar, status bar, section headers, scrollbars are rendered in muted tokens. Accents (orange / teal per PCC's BrandProfile) reserved for **interactive affordances** — buttons, focus rings, status pills, active tab. If a surface uses accent colour, it should be doing something semantic.

---

## 6. Information hierarchy

### Primary

  - **Top utility band** — tool identity + current status + primary actions.
  - **Aggregate tile row** — fleet-level metrics for this one tool.

Operator's eye lands here on first paint. ~25% of vertical space.

### Secondary

  - **Active tab's primary content** — the surface the operator chose to drill into (Overview commits feed / TODOs list / Files browser / Git output).

~60% of vertical space.

### Tertiary

  - **Tab bar** — navigation, not content.
  - **Status bar (inherited from main window)** — operational confirmation.

~5% of vertical space; remainder is whitespace + Panel containers' chrome.

### Quaternary

  - **Per-row affordances** — TodoItem checkbox-style toggle, commit row hover, file-tree drag handles.

Always-available but never demanding attention.

---

## 7. Implementation sequencing

Strict order by **value-per-risk**. Each step is a separate B-series commit on `phase-3d-pcc-detail-retrofit` with operator approval before landing. Stop at any step if visual review reveals an issue.

| # | Step | Why first | Risk | Spec needed before? |
|---|------|-----------|------|---------------------|
| 1 | **Top utility band restructure** | Single biggest visual upgrade per LOC. Replaces the button-soup top bar with a Phase-3C-style band. Most "still feels old" complaint resolved in one step. | Medium | No — this spec covers it. |
| 2 | **Replace `StatTile` with `AggregateTile`** + reduce to 4 tiles + add Lucide icons + subtitles | Mechanical migration. Drops two tiles (Completed, Code Files). | Low | No. |
| 3 | **Migrate action buttons to commons `PrimaryButton` / `SecondaryButton` / `TertiaryButton`** + Lucide icons | Mechanical. Affects ~7 buttons across the panel. | Low | No. |
| 4 | **Overview tab — wrap content in Panels + modernize SyncStatusCard** | Visual coherence with dashboard. Replaces chip soup with StatusBadge cluster. | Medium | No. |
| 5 | **TODOs tab — Panel wrap + modernize TodoItem + StatusBadge per item** | Visual coherence; eliminates remaining emoji bullets. | Medium | Minor — TodoItem visual spec covered inline §3.5. |
| 6 | **Git tab — Panel wrap + monospace QPlainTextEdit output + SecondaryButton actions** | Last "raw QLabel output" surface in PCC. Replaces with a proper terminal-like surface. | Medium | No. |
| 7 | **Files tab — Lucide migration on CommonsDropZone + splitter chrome polish** | Cosmetic only; smallest surface to address. | Low | No. |
| 8 | **Keyboard shortcuts (Ctrl+1..4 tab switching, Ctrl+P pull, etc.)** | Polish; nice-to-have. | Trivial | No. |

Steps 1, 2, 3 deliver ~70% of the perceived "detail panel feels modern" upgrade. Steps 4-7 fill in the rest. Step 8 is optional.

**Recommended first cycle:** Steps 1 → 2 → 3 (one operator-approved PR per step). Each is bounded and validates independently.

### Sequencing rationale

  - **Top band first (step 1)** because it's the operator's identity anchor and the biggest "still feels old" complaint. Win the headline issue early.
  - **Tile row second (step 2)** because it sits right under the top band and the dashboard already has the `AggregateTile` API ready. Mechanical work, immediate visible parity with dashboard.
  - **Buttons third (step 3)** because they're scattered across every surface (top band, Git tab, file-tree action) and a single migration session normalises them all.
  - **Tab content last** — operator gets the dashboard-feel chrome before drilling into the deep tabs.

### Estimated session count

  - Steps 1-3: **1 session** (compact, mechanical, can be a single commit per step).
  - Steps 4-6: **1 session each** (each is a tab; deserves visual review per step).
  - Step 7: **0.5 session** (light cosmetic).
  - Step 8: **optional 0.5 session** (or skip entirely).

Total: **3-4 sessions of B-series commits** on a `phase-3d-pcc-detail-retrofit` branch + a merge cycle.

---

## 8. Explicit "what NOT to do"

  - **Do not redesign the four-tab structure.** Overview / TODOs / Files / Git is logical. Adding a fifth tab, removing one, or reordering them is out of scope.
  - **Do not invent a fifth tab type.** No "Activity" tab, no "Logs" tab, no "Builds" tab.
  - **Do not introduce a fifth status variant** (e.g. `pending`, `partial`). `StatusBadge`'s seven variants from Phase 3C cover every detail-panel state.
  - **Do not introduce a new commons primitive.** Every visual element resolves to `Panel` / `StatusBadge` / `PrimaryButton` / `SecondaryButton` / `TertiaryButton` / `AggregateTile` / Lucide icons from `phoenix_commons.icons`. If a new primitive feels needed, stop and raise it.
  - **Do not change BrandProfile.** PCC stays orange + teal. The detail panel inherits the dashboard's accent palette.
  - **Do not redesign `GitOpWorker` or `scanner.get_git_info`.** Backend stays untouched. UI consumes the same data shape it always has.
  - **Do not migrate `FileViewer`.** It's a domain widget with internal complexity (syntax highlighting, file type detection, etc.). Cosmetic Lucide migration only on its toolbar if any; structural untouched.
  - **Do not modify `CommonsDropZone`'s drag-drop semantics.** Visual chrome migration only (emoji → Lucide). The drag-target rectangle + drop-callback logic stays as-is.
  - **Do not introduce animation.** Same restraint as dashboard.
  - **Do not add a notification surface.** Status updates go through the sync pill + status bar (inherited from main window).
  - **Do not add a command palette.** ⌘K already focuses dashboard search; that's enough.
  - **Do not redesign the back-navigation.** `back_clicked` signal + Escape key handler stays.

---

## 9. Relationship to existing dashboard language

The detail panel is the **dashboard's chrome applied to a different operational surface.** Every primitive, color, icon, spacing rule, and interaction philosophy that the dashboard established carries forward.

### Shared layer (commons-level)

  - `Panel` — same rounded-card chrome wraps detail-panel sections.
  - `StatusBadge` — same 7-variant semantic system.
  - `AggregateTile` — same 4-tile row at the top.
  - `PrimaryButton` / `SecondaryButton` / `TertiaryButton` — same 3-tier action hierarchy.
  - Lucide icons — same icon vocabulary (no emoji on any primary surface).

### Shared layer (PCC-level)

  - PCC `BrandProfile` (orange + teal) — same accent colours.
  - PCC `C` palette tokens — same chrome colors (bg, surface, border, text, etc.).
  - `#pageTitle` / `#sectionHeader` QSS — same typography.

### Detail-panel-specific additions (within the shared language)

  - **Action hierarchy.** Detail panel exposes Primary (Launch installed) / Secondary (Run source / Pull / Push / Fetch) / Tertiary (Back / VS Code / GitHub) — a clearer hierarchy than the dashboard's single action surface.
  - **Tab-resident scrolling regions.** Dashboard has the single scrollable activity feed; detail panel has tab-resident scrollable surfaces. Same QScrollArea + Panel pattern, just per-tab.

### What this spec is NOT introducing

  - No new `BrandProfile` slot.
  - No new commons widget.
  - No new QSS selector keyed on a new objectName (beyond existing `#statCard`, `#Panel`, etc.).
  - No new Lucide icon (the 15 currently in commons cover everything — `play`, `code`, `external-link`, `arrow-down`, `arrow-up`, `refresh`, `clock`, `file-text`, `hard-drive`, `warning`, `git-branch`, etc. Plus existing ones already in `ICON_NAMES`).

**Wait** — the spec needs `play`, `arrow-left`, `play-circle`, `terminal`, `code`, `external-link`, `clock`. Let me cross-check against commons inventory.

### Commons icon coverage check

Currently in `ICON_NAMES`:
```
check, file-text, git-branch, hard-drive, info, layout-dashboard,
package, plus, refresh, save, search, settings, trash, warning, x
```

Detail-panel-needed icons that **don't yet exist**:
  - `play` (Run source button)
  - `arrow-left` (Back button — optional; the literal "← Back" could stay)
  - `code` (VS Code button)
  - `external-link` (GitHub button)
  - `arrow-down` (Pull button)
  - `arrow-up` (Push button)
  - `clock` (Last Commit tile leading icon)

**~7 new Lucide SVGs** would be needed to fully realize the spec. All Lucide-standard, all mechanical to add (same pattern as Step 1 / Step 5 commons icon additions in Phase 3C). This becomes the first commons addition of Phase 3D — bundled into step 3 (button migration) or as a precursor step 0.

This is a known additive scope expansion in commons — flagged here so the operator can approve before Phase 3D implementation begins.

---

## 10. Biggest risks

### A. Top utility band crowding

The current top bar already has 4 action buttons + 2 badges + title + back. Even after restructuring, fitting all of them in one band at PCC's default 1300px window is tight. Risk: the modernized band still feels crowded.

**Mitigation:** test the band at 1100px (minimum window width) early in step 1. If buttons overflow, move tertiary actions (VS Code / GitHub) into a context menu or an overflow button.

### B. Tab content height shrinkage

Adding Panel containers around each tab's content costs ~32px of vertical space (16px top + 16px bottom margins per Panel). With 4 tabs each gaining a Panel, the operator's data viewport shrinks. Risk: TODOs / Files / Git get noticeably less scrollable area.

**Mitigation:** Panel margins should be tuned per-tab — Files tab might use 8px instead of 16px since its splitter already has its own padding.

### C. Loss of `StatTile`'s 6-tile information density

Going from 6 → 4 tiles drops two pieces of information from the at-a-glance surface (Completed count + Code Files count). Risk: operator who relied on those gets a regression.

**Mitigation:** "Completed" count is derivable in the TODOs tab summary (open vs done). "Code Files" count is implicit in the Files tab tree. Spec assumes operator won't miss them at glance level; if they do, we can re-introduce one as a 5th tile (matching the dashboard's "Needs Commit" recovery in B14.1).

### D. Mismatch with dashboard "felt quality"

The dashboard is the operator's anchor; the detail panel is where they drill into. If the chrome migrations are mechanical but the *interaction feel* doesn't match dashboard polish (hover responsiveness, button affordance clarity, scroll smoothness), operators will perceive Phase 3D as "less finished" than 3C even with the same primitives.

**Mitigation:** at the end of each step, source-mode launch + drill into the detail panel + compare interaction feel head-to-head with the dashboard. If anything feels off, that's the next polish item before moving on.

### E. Architecture-creep risk: tempting "while we're in there" refactors

`detail_panel.py` is 784 lines of mostly inline-styled chrome. The temptation to refactor `SyncStatusCard` / `TodoItem` into commons widgets, restructure `_build()` into per-tab helper methods, or move `GitOpWorker` into commons updater submodule is real and present at every step. Risk: scope creep that turns 3-4 sessions into 8-10.

**Mitigation:** Each step's commit MUST stay within the surface scope. Refactors that improve maintainability but don't change visible chrome go into a separate "tech debt" phase, not Phase 3D.

### F. Commons icon-set expansion drift

Adding 7 new Lucide SVGs (`play`, `code`, `external-link`, `arrow-down`, `arrow-up`, `clock`, optionally `arrow-left`) grows the commons icon set from 15 → 22. Risk: each new icon is a tiny commit but the cumulative diff to commons becomes a small architecture decision. Operator may want to gate the SVG additions on a separate commons PR.

**Mitigation:** bundle all 7 icons in a single "icons: detail-panel additions" commons commit early in Phase 3D (call it step 0). Single commit, single approval, then the rest of Phase 3D consumes them.

---

## 11. What this spec is NOT

  - **Not an implementation plan.** §7 sequences the work; it does not specify the code.
  - **Not architecture doctrine.** ADR-016 + PLATFORM_CONTRACT + MIGRATION_RULES remain the doctrinal layer.
  - **Not a redesign mandate.** It absorbs the dashboard's existing language into the detail panel; no new design system invented.
  - **Not exhaustive.** Cosmetic micro-decisions (exact pixel paddings, exact hover-transition timings, exact tile widths) get decided per-step during implementation. This spec sets direction, not pixels.
  - **Not a contract for backend changes.** `GitOpWorker`, `scanner.get_git_info`, `_resolve_installed_exe`, `FileViewer` internals all untouched.

---

## 12. Branch + workflow conventions (carried from Phase 3C)

  - **Branch:** `phase-3d-pcc-detail-retrofit` (per MIGRATION_RULES § Per-retrofit branch + PR convention).
  - **Commit cadence:** B-series, one per step in §7. Each B-series commit gets operator visual approval before the next opens.
  - **Validation per step:** compileall + smoke tests + source-mode launch. Operator-visible polish review per step.
  - **Frozen-build validation:** before merge to `main`, run the hardened `build.bat` and observe for ~3-5 min. Same gate as Phase 3C.
  - **Merge mode:** `--no-ff` per MIGRATION_RULES.
  - **Tag on merge:** `pcc-phase-3d-merged-v<X.Y.Z>` (version bump per `version.py`; suggest 2.1.0 to mark "detail panel modernization" as a new minor).
  - **Reports per step:** mirrored under `phoenix-commons/docs/ui-platform-baseline-v1/PCC_DETAIL_PANEL_IMPLEMENTATION_STEP_NN_REPORT.md`.

---

*End of spec.*
