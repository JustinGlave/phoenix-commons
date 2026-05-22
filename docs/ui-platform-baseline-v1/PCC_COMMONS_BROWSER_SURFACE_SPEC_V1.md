# PCC Commons Browser Surface Spec — v1

> **Status:** product direction. Pre-implementation.
> **Date:** 2026-05-22.
> **Phase:** 3E.
> **Scope:** the PCC Commons Browser — its purpose, hierarchy, layout,
> visual feel, and the surfaces it composes. No code. No retrofit doctrine.
> No architectural change to commons or ADR-016. Reuses every primitive
> Phase 3C + 3D produced.
> **Inputs:** current `commons_browser.py` (240 LOC; pre-retrofit chrome),
> the Phase 3C dashboard + Phase 3D detail-panel surfaces,
> `PCC_DASHBOARD_SURFACE_SPEC_V1`, `PCC_DETAIL_PANEL_SURFACE_SPEC_V1`,
> ADR-016, commons widgets (Panel, StatusBadge, PrimaryButton,
> SecondaryButton, TertiaryButton, PhoenixTable, Lucide icons),
> `PCC_PHASE_3E_CANDIDATE_AUDIT_REPORT` (selection rationale).
> **Output:** this file. Operator approves the spec; implementation
> sequencing follows separately, one surface at a time.

---

## 1. Product intent

**The Commons Browser is PCC's cross-tool dependency inspection surface.** Not a file explorer. Not a search interface. Not a dependency graph. The single screen the operator drills into to answer one structural question: *"For this file in `phoenix-commons`, which tools actually consume it?"*

The Commons Browser answers three operator questions, in priority:

1. **"What's in commons?"** — the file tree at a glance: structure, names, sizes.
2. **"Is this file orphaned, or is it actively used?"** — the per-file usage state (which tools reference it).
3. **"What does this commons file actually contain?"** — file content preview, identical to detail-panel file inspection.

Everything else is supporting chrome.

### What dominates visually

The **tree + viewer body**. The operator's eye lands on the file tree (left) and the viewer (right). These are the workspace; everything else recedes.

### What feels secondary

The **header chip row** — small at-a-glance aggregate counts (files / referenced / orphans / total size). Visible at first paint; doesn't compete with the tree/viewer for attention.

### What feels alive

  - **Summary chips updating** when a scan completes
  - **Usage footer flipping** between placeholder / "ORPHAN" / "Used by N tool(s)" as the operator clicks files
  - **Status label** transient ("Scanning usage across tools…" during a refresh)
  - **Rescan button** enable/disable around an in-flight scan

### What feels calm

  - Page title, divider, splitter handle, scrollbars
  - Background panels around the tree and viewer
  - The empty state ("Select a file to see which tools reference it.")

### What the operator decides from this surface

  - "Is this commons file still used? If not, can it be retired?"
  - "Which tools would I need to coordinate with if I changed this file?"
  - "Is the commons folder structure healthy, or is it accumulating cruft?"
  - "What does the canonical implementation actually look like?" (read-only inspection)

The Commons Browser is **not** where the operator edits commons — that flow goes through the Files tab of the *commons-itself* detail panel (or external editor via the Files tab's drag-out). The Commons Browser is purely a *read + audit* surface.

---

## 2. Workflow audit — what `commons_browser.py` looks like today

`commons_browser.py` is 240 lines. Three top-level classes:

  - `_Chip(QLabel)` — inline-styled summary chip widget (local-only; not the commons `StatusBadge`).
  - `UsageFooter(QFrame)` — bottom-of-viewer surface showing which tools reference the selected file.
  - `CommonsBrowser(QWidget)` — the host page widget.

### Current top region (`commons_browser.py:119-148`)

```
[Commons (pageTitle)] [status_lbl (transient)]     [stretch] [Rescan]

[— files] [— referenced] [— orphans] [—]
```

  - Header row: `#pageTitle` + transient status label + Lucide-iconed Rescan button (Phase 3C Step 1 already migrated)
  - Below: 4 `_Chip` inline-styled QLabel summary chips (files / referenced / orphans / total size)
  - The chips use bespoke inline `setStyleSheet` — none of them are `StatusBadge`s

### Current body (`commons_browser.py:151-182`)

```
┌─ QSplitter (Horizontal, handleWidth=2) ───────────────────────┐
│ ┌─ QTreeView ────┐ ┌─ FileViewer ───────────────┐             │
│ │ commons/       │ │ <preview of selected file> │             │
│ │ ├─ docs/       │ │                            │             │
│ │ ├─ src/        │ │                            │             │
│ │ │  └─ ...      │ │                            │             │
│ │ └─ tests/      │ │                            │             │
│ └────────────────┘ └────────────────────────────┘             │
│                    ┌─ UsageFooter ──────────────┐             │
│                    │ USED BY                    │             │
│                    │ [◈ Tool A] [◈ Tool B] …    │             │
│                    └────────────────────────────┘             │
└───────────────────────────────────────────────────────────────┘
```

  - QSplitter handle: inline `setStyleSheet` (line 153) — identical to the line Phase 3D's post-merge cleanup removed from the detail panel because the theme.py overlay already covers it globally.
  - QTreeView + QFileSystemModel — same pattern as detail-panel Files tab.
  - FileViewer — shared widget; spec §8 forbids redesign (same constraint as Phase 3D Files tab).
  - UsageFooter — bottom-of-right-pane QFrame with `◇` orphan / `◈` user-chip glyphs.

### Current usage footer (`commons_browser.py:41-99`)

```
USED BY
◈ Phoenix Cad  ◈ Job Tracker  ◈ Valvemaster
```

— OR, for an unused file —

```
USED BY
◇  ORPHAN — not referenced by any tool
```

— OR, before a file is selected —

```
USED BY
Select a file to see which tools reference it.
```

  - `UsageFooter` is a raw QFrame with inline-styled card chrome (line 43-45).
  - Section header: hand-styled QLabel "USED BY" with `text_muted` + uppercase letter-spacing — semantically identical to `#sectionHeader` (which the theme.py overlay already styles).
  - Per-tool chip: inline-styled QLabel with `◈` emoji prefix + accent colour + accent_glow background.
  - Orphan chip: inline-styled QLabel with `◇` emoji prefix + warning colour + warning-tinted background.
  - Placeholder: italic muted QLabel.

### What still feels "legacy PCC"

  1. **`_Chip` summary chips** — bespoke inline-styled QLabel where `StatusBadge` (compact variant) now exists across PCC.
  2. **`◇` / `◈` emoji glyphs on chrome** — last remaining emoji on a primary PCC surface. Dashboard + detail panel both Lucide-only.
  3. **`UsageFooter` inline-styled card chrome** — should be a `Panel` with an internal `#sectionHeader` + a horizontal flow of `StatusBadge` pills.
  4. **Inline `QSplitter::handle` stylesheet** — redundant; theme.py overlay already covers it (the exact same fix Phase 3D landed in detail panel).
  5. **No `Panel` containers** around any region — tree, viewer, footer, summary row all sit bare.
  6. **Header chip-row alignment** — chips are tightly packed left of a horizontal stretch; no consistent spacing with the page title.

### What works well — preserve

  - **The pageTitle + Rescan-button header layout** — clear identity anchor + single right-aligned action.
  - **The two-pane QSplitter body** — tree (left, narrow) + viewer+footer (right, wide). Operationally correct.
  - **The QFileSystemModel + QTreeView coupling** — identical to detail-panel Files tab; the operator's mental model carries.
  - **The `_on_tree_clicked` flow** — single click loads file in viewer + shows users in footer. Calm, fast.
  - **The empty-state pattern** — placeholder text in the UsageFooter when no file is selected.
  - **The error-state pattern** — `_set_empty_state(message)` resets tree + viewer + chips when commons path is missing/invalid.
  - **The `set_scanning(True)` indicator** — transient status label + disabled Rescan button. Calm; non-spammy.
  - **The Lucide Rescan icon** — Phase 3C Step 1 already on it.

### What must remain structurally unchanged

  - 4 summary chips (files / referenced / orphans / total size)
  - QSplitter orientation (horizontal) + tree-on-left/viewer-on-right
  - QTreeView column hidden config (cols 1, 2, 3 hidden — same as detail panel)
  - QFileSystemModel filter (`AllDirs | Files | NoDotAndDotDot`)
  - FileViewer integration
  - `refresh_requested` signal contract
  - Empty + error state messages

### What is purely chrome debt

  - `_Chip` class itself — replaceable by `StatusBadge`(compact) or by an `AggregateTile`-strip
  - `UsageFooter` inline-styled QFrame — replaceable by `Panel` + `StatusBadge` row
  - `◇` / `◈` emoji glyphs — replaceable by Lucide `package` (used) + `warning` (orphan)
  - Inline `QSplitter::handle` stylesheet — redundant with theme.py overlay

---

## 3. Surface inventory

Six surfaces compose the modernized Commons Browser. Each gets a paragraph of intent + a priority classification.

### 3.1 Page header — SECONDARY

`#pageTitle` "Commons" + transient status label (right of title) + right-aligned `TertiaryButton`/`SecondaryButton` "Rescan" with Lucide `refresh` icon.

  - **Left:** `#pageTitle` "Commons"
  - **After title, left-of-center:** muted status label (e.g. "Scanning usage across tools…") — currently a QLabel with inline styling. Modernise to read as a calm sub-label, same style as detail panel's branch sub-label (`text_muted` 13px 500-weight).
  - **Right:** Rescan button — should match the detail panel's tier convention. Rescan is a *supporting operation* (it re-runs the heavy scan), not a destructive primary action — `SecondaryButton` is the right tier. (Alternative: `TertiaryButton` if the operator finds Secondary too prominent for a page-header action — operator review will decide.)

The header is the operator's identity anchor. Should match the dashboard's top-utility-band rhythm: `pageTitle` left, action right, calm.

### 3.2 Summary chip row — SECONDARY

Replace 4 `_Chip` inline-styled chips with 4 `StatusBadge` compact pills (the same primitive Phase 3D used for sync-card pills + TODO summary pills).

| Pill | Label | Variant | Source |
|------|-------|---------|--------|
| files | "N files" | `unknown` (neutral) | `len(usage)` |
| referenced | "N referenced" | `clean` (positive) | count where `users` non-empty |
| orphans | "N orphans" | `dirty` if >0 else `clean` | count where `users` empty |
| size | format_size(total_size) | `unknown` (neutral) | `sum(v["size"] for v in usage.values())` |

Variant flips:
  - `files`/`size`: always `unknown` (neutral muted) — these are reference counts, not states.
  - `referenced`: always `clean` (green) — positive metric.
  - `orphans`: `dirty` (amber) when >0; `clean` (green) when 0 (visible "all healthy" signal).

The "files" + "size" pills could optionally be rendered as plain `QLabel`-style metric strips instead of StatusBadges; default to StatusBadge for visual consistency with the rest of PCC. Operator review can flip these in Step 1.

### 3.3 Tree pane — SECONDARY

Largely unchanged structurally. QFileSystemModel + QTreeView + column hidden config preserved.

Visual change:
  - Optionally wrap the tree in a `Panel` container with a small "FILES" section header — but **caution**: per spec §8 of Phase 3D, Panel wrapping a tree can crowd it. The detail-panel Files tab deliberately did NOT Panel-wrap the tree.
  - **Default decision:** do NOT Panel-wrap the tree. Match the detail-panel Files-tab decision. Tree sits bare on the splitter pane.

### 3.4 Viewer pane — TERTIARY

Largely unchanged. FileViewer is a domain widget — spec §8 forbids redesign (same constraint as Phase 3D Files tab).

Cosmetic only:
  - Remove inline `QSplitter::handle` stylesheet (theme.py overlay covers it).
  - Optionally tighten the right-pane vertical spacing between FileViewer and UsageFooter.

### 3.5 Usage footer — PRIMARY

The single most modernization-worthy surface. Replace `UsageFooter`'s inline-styled QFrame chrome with:

  - **`Panel` container** with internal `#sectionHeader` ("USED BY")
  - **Per-state body composition:**
    - Empty (no file selected): muted italic placeholder QLabel (preserved)
    - Orphan (file selected, no users): single `StatusBadge` with `warning` variant + Lucide `warning` icon + text "Not referenced by any tool"
    - Used (file selected, ≥1 user): horizontal flow of `StatusBadge` pills with `clean` variant, one per tool, prefixed by Lucide `package` icon

Each StatusBadge displays the tool's pretty name (already computed via `name.replace("-", " ").replace("_", " ").title()`).

If a tool's name is too long for compact StatusBadge mode, fall back to non-compact StatusBadge with the same variant. Operator review will validate visual density at Step 2.

### 3.6 Splitter chrome — TERTIARY

Already correct. Just remove the inline `setStyleSheet` call (theme.py overlay already styles `QSplitter::handle`).

---

## 4. Interaction philosophy

### Workflow preservation

  - **Single-click on file in tree** → loads file in viewer + updates UsageFooter
  - **Single-click on folder in tree** → expands/collapses (Qt default)
  - **Rescan click** → emits `refresh_requested` signal; main window kicks off scan; commons browser shows "Scanning…" + disables Rescan; on completion main window calls `set_usage(usage)` + `set_scanning(False)`
  - **Set commons path** → main window calls `set_commons_path(path)`; if invalid, browser enters empty state
  - **Empty state** → all chips show "—", tree shows nothing, viewer clears, footer placeholder explains the empty cause

Every interaction is preserved. **No new interactions introduced** by this spec.

### Forbidden interactions

  - No search box. Search backend is its own future phase.
  - No filtering controls (file type filter, used-vs-orphan filter, etc.).
  - No multi-select.
  - No drag-and-drop in or out of the Commons Browser tree.
  - No right-click context menu on tree items.
  - No inline file edit.
  - No directory traversal beyond the commons folder.
  - No animations on chip variant flips (instant — same as dashboard StatusBadge updates).

### Splitter behavior

  - Default split sizes: `[320, 720]` (preserve current `setSizes`).
  - Handle width: 2px (preserve).
  - Operator can drag the handle freely (Qt default).
  - No collapse-to-zero handles.

### Empty + error states

Three distinct states, all preserved:

| State | Trigger | Surface |
|-------|---------|---------|
| **No commons path configured** | `set_commons_path("")` or path doesn't exist | Tree shows nothing; viewer clears; footer shows placeholder text explaining the cause |
| **Path valid, no scan yet** | After `set_commons_path(valid)` before `set_usage` is called | Tree populated; viewer clears; footer shows "Select a file to see which tools reference it." (preserved) |
| **Path valid, scan running** | `set_scanning(True)` | Status label shows "Scanning usage across tools…"; Rescan button disabled |

Each transitions cleanly without flashing or layout jumps. (B6 invariant respected — no widget-level setStyleSheet on commons primitives.)

### Dense vs spacious

  - **Header zone:** spacious — matches detail panel + dashboard rhythm
  - **Summary chip row:** medium-density (4 StatusBadges + horizontal stretch)
  - **Tree:** dense (default QTreeView)
  - **Viewer:** depends on file content (FileViewer's own concern)
  - **UsageFooter:** medium-density (Panel chrome + StatusBadge row)

### Scrolling

  - Tree scrolls vertically on overflow (QTreeView default).
  - Viewer scrolls per its own internal logic (FileViewer concern; unchanged).
  - UsageFooter does NOT scroll — if a file has >10 users, the StatusBadge row will wrap or truncate. **Decision deferred to Step 2 implementation**; default is to allow horizontal scroll inside the Panel via a QScrollArea.

### Navigation rhythm

  - Page reached via sidebar nav (Commons item) — unchanged.
  - `Ctrl+2` jumps to Commons (per current keyboard shortcuts in `about_dialog.py:140`) — preserved.
  - No `Back` button (Commons Browser is a peer page in the QStackedWidget, not a drilldown).

---

## 5. Visual direction

### Inherited from Phase 3C dashboard + Phase 3D detail-panel language

Every visual decision maps to a decision already made on the dashboard or detail panel:

| Surface treatment | Origin | Commons Browser application |
|-------------------|--------|------------------------------|
| `StatusBadge` 7-variant + compact mode | Phase 3C Step 2 | Summary chip row + UsageFooter per-tool pills |
| `Panel` rounded-card chrome | Phase 3C B11 polish | UsageFooter container |
| Lucide icons (no emoji) | Phase 3C Step 1 | UsageFooter per-tool + orphan icons |
| Per-tool tag colors | Phase 3C Step 4 | UsageFooter per-tool StatusBadges could optionally inherit tag colors (operator review in Step 2) |
| `pageTitle` 22px 800 | Phase 3C B7 typography | Page header (preserved) |
| `sectionHeader` 10px uppercase muted | Phase 3C B11 polish | Inside UsageFooter Panel |
| `SecondaryButton`/`TertiaryButton` | Phase 3D Steps 1+6 | Rescan button |
| `QSplitter::handle` global QSS | Phase 3D post-merge cleanup | Splitter chrome (no inline stylesheet) |
| Property-selector QSS pattern | Phase 3D Step 6 (`outputState`) | Not needed for Commons Browser (no terminal-style output surface) |

### What should NOT return from old PCC

Explicitly forbidden by this spec:

  - **Chip soup** — no inline-styled QLabel chains for status indicators. Always `StatusBadge`.
  - **Emoji glyphs on chrome** — no `◇` / `◈` / `✓` / `⚠` / any emoji on chips, badges, or section headers. Lucide only.
  - **Inline-styled QFrame cards** — `Panel` is the canonical card chrome.
  - **Bespoke `_Chip`-style local classes** — use commons primitives.
  - **Inline `setStyleSheet` on commons primitives** — preserves the B6 invariant established in Phase 3C/3D.
  - **Raw `QPushButton` for action buttons** — `SecondaryButton` / `TertiaryButton` from commons.
  - **Bespoke section headers** — `#sectionHeader` object name + theme.py QSS.

### Typography

  - Page title: `#pageTitle` (22px, 800 weight) — same as dashboard + detail panel.
  - Section headers inside Panels: `#sectionHeader` (10px uppercase muted 700 weight).
  - Body text: 12px regular.
  - File path / metadata sub-labels: 11-12px muted slate.
  - Per-tool StatusBadge labels: StatusBadge default typography (no override).

### Motion / restraint

**Allowed:**
  - Hover transitions on buttons (150ms ease-out, same as dashboard).
  - StatusBadge variant flips on scan completion (instant, no fade).
  - Tree expand/collapse (Qt default).

**Forbidden:**
  - Animated count-up on chip values when scan completes.
  - Slide-in transitions on UsageFooter state changes.
  - Fade-ins on file selection.
  - Loading spinners — use the existing transient status label instead.
  - Shimmer skeletons.

### Chrome philosophy

Chrome recedes; data leads. Page title, section header, scrollbars, splitter handle, and tree branches all rendered in muted tokens. Accents (orange / teal per PCC's BrandProfile) reserved for **interactive affordances** — Rescan button, focus rings, status pills indicating non-zero counts.

---

## 6. Information hierarchy

### Primary

  - **Tree + viewer body** — operator's primary inspection workspace.
  - **UsageFooter** — the *answer* to the operator's question. After they click a file, this is what they actually came to see.

~70% of vertical space.

### Secondary

  - **Page header** — identity + rescan action.
  - **Summary chip row** — at-a-glance fleet-level commons metrics.

~20% of vertical space.

### Tertiary

  - **Splitter handle** — chrome, not content.
  - **Status sub-label** — transient.
  - **Empty-state placeholder text** — calm, informational.

~10% of vertical space; remainder is whitespace + Panel chrome.

### Quaternary

  - **Tree branch indicators** (Qt default)
  - **Scrollbars** (Qt default styled muted via PCC overlay)

Always-available but never demanding attention.

---

## 7. Implementation sequencing

Strict order by **value-per-risk**. Each step is a separate commit on `phase-3e-pcc-commons-browser-retrofit` with operator approval before landing. Stop at any step if visual review reveals an issue.

| # | Step | Why first | Risk | Spec needed before? |
|---|------|-----------|------|---------------------|
| 1 | **Summary chip row modernization** — `_Chip` → `StatusBadge` (compact) | Highest-visibility, smallest-LOC step. Replaces the most-jarring inline-styled chips with the Phase 3C/3D vocabulary. | Low | No — this spec covers it. |
| 2 | **UsageFooter modernization** — Panel wrap + StatusBadge per-tool/orphan + Lucide icons | The single most operator-visible chrome win. Replaces `◇`/`◈` emoji chips with proper StatusBadge pills inside a Panel. | Low-Med | No. |
| 3 | **Tree/viewer/page cohesion pass** — splitter inline-QSS cleanup + Rescan button tier migration to `SecondaryButton`/`TertiaryButton` + final spacing/typography polish | Mechanical. Mirrors Phase 3D Steps 6 + 7. | Low | No. |
| 4 | **Validation + merge gate** — compileall + pytest + offscreen smoke + operator review + merge-gate report authoring | Closure of the phase per Phase 3D pattern. | n/a | No. |

Steps 1, 2, 3 deliver ~95% of the perceived "Commons Browser feels modern" upgrade. Step 4 is the closure gate (mirrors Phase 3D's gate-report + merge sequence).

**Estimated session count:** 1-2 sessions total.

  - Steps 1 + 2 + 3 could fit in a single session if each step's diff stays bounded (≤50 LOC).
  - Step 4 (gate + merge + cleanup) is its own session.

### Sequencing rationale

  - **Summary chip row first (Step 1)** because it's the most-visible header surface; lands the cohesion win at the top of the page where the operator's eye lands first.
  - **UsageFooter second (Step 2)** because it's the largest visual delta and the operator-question-answering surface — modernizing it after the chip row means the page reads coherently top-to-bottom.
  - **Cohesion pass third (Step 3)** because by then the local primitives are all migrated; remaining work is mop-up.
  - **Validation last (Step 4)** because the established Phase 3C/3D pattern places the merge gate at the end with a comprehensive report.

### What about post-merge cleanup?

Like Phase 3D, expect a small post-merge cleanup commit on `main` (1-3 dead-import or redundant-stylesheet items) mirroring the `d466202` precedent.

---

## 8. Explicit "what NOT to do"

  - **Do not redesign the two-pane layout.** Tree-on-left / viewer-on-right with a horizontal QSplitter is operationally correct. Reorienting to vertical, three panes, or tabs is out of scope.
  - **Do not invent a search box.** Search across commons files is a separate Phase 3F+ candidate per the candidate audit. It does not belong in Phase 3E.
  - **Do not introduce a filter UI.** No file-type filter, no used-vs-orphan filter, no sort-by-size dropdown.
  - **Do not redesign `FileViewer`.** It's a shared domain widget (the same one detail-panel Files tab uses). Spec §8 of the Phase 3D detail-panel spec already forbids it; that constraint carries.
  - **Do not redesign `scanner.scan_commons_usage`.** The usage data shape (`{rel_path: {"size": int, "users": [tool_name, ...]}}`) is a stable contract. Spec §6 documents it for preservation.
  - **Do not introduce a new commons primitive.** Every visual element resolves to `Panel` / `StatusBadge` / `SecondaryButton` / `TertiaryButton` / Lucide icons from `phoenix_commons.icons`. If a new primitive feels needed, stop and raise it.
  - **Do not change BrandProfile.** PCC stays orange + teal per ADR-016.
  - **Do not introduce new commons icons.** The icon set after Phase 3D (`arrow-down`, `arrow-left`, `arrow-up`, `check`, `clock`, `code`, `external-link`, `file-text`, `git-branch`, `hard-drive`, `info`, `layout-dashboard`, `package`, `pin`, `play`, `plus`, `refresh`, `save`, `search`, `settings`, `trash`, `warning`, `x`) covers everything Commons Browser needs. If a clear semantic gap surfaces, raise it as a separate commons PR before the implementation step.
  - **Do not add animation.** Same restraint as dashboard + detail panel.
  - **Do not redesign tree navigation.** Single-click selects, double-click expands (Qt default). No keyboard navigation overrides. No context menus.
  - **Do not turn Commons Browser into an IDE.** No syntax highlighting beyond what FileViewer already provides. No inline editing. No file operations (rename, delete, copy).
  - **Do not turn Commons Browser into a dependency graph.** No node-edge visualization. No call-graph inspection. The usage footer is the only dependency surface; it stays simple (list of tool names).
  - **Do not modernize Settings / Wizard / About in this phase.** Each is a candidate for a separate future small phase. Phase 3E is *Commons Browser only*.
  - **Do not preempt Wave 8a.** Wave 8a is operator-gated and has a doctrinal cooldown floor of 2026-06-02. Phase 3E may ship before that date; it does not affect the Wave 8a clock.
  - **Do not modify `commons_browser.py`'s public API.** `set_commons_path` / `set_scanning` / `set_usage` / `refresh_requested` signal must all remain identical signatures. The main window calls them at specific lifecycle points; changing the API would force corresponding changes in `main_window.py` outside this phase's scope.

---

## 9. Relationship to existing dashboard + detail-panel language

The Commons Browser is **the dashboard + detail panel's chrome applied to an inspection surface.** Every primitive, color, icon, spacing rule, and interaction philosophy carries forward.

### Shared layer (commons-level)

  - `Panel` — same rounded-card chrome wraps the UsageFooter.
  - `StatusBadge` — same 7-variant semantic system for summary chips + per-tool pills.
  - `SecondaryButton` / `TertiaryButton` — same 3-tier action hierarchy (Rescan = Secondary or Tertiary; operator review).
  - Lucide icons — same icon vocabulary (no emoji on any primary surface).

### Shared layer (PCC-level)

  - PCC `BrandProfile` (orange + teal) — same accent colours.
  - PCC `C` palette tokens — same chrome colors (bg, surface, border, text, etc.).
  - `#pageTitle` / `#sectionHeader` QSS — same typography.
  - `QSplitter::handle` overlay — covers the splitter chrome globally (no per-page inline QSS).

### Commons-Browser-specific (within the shared language)

  - **No new tier.** Header / chip row / tree / viewer / footer all map to existing tiers.
  - **Same QFileSystemModel + QTreeView + FileViewer pattern as detail-panel Files tab.**
  - **UsageFooter Panel + StatusBadge composition** is a new arrangement of existing primitives, not a new primitive.

### What this spec is NOT introducing

  - No new `BrandProfile` slot.
  - No new commons widget.
  - No new QSS selector keyed on a new objectName.
  - No new Lucide icon (the 23 currently in `ICON_NAMES` cover everything — `package` for users, `warning` for orphans, `refresh` for rescan, plus existing typography).

---

## 10. Biggest risks

### A. Over-panelization

Wrapping every region (header, chips, tree, viewer, footer) in `Panel` chrome would shrink the operator's data viewport noticeably. The detail panel learned this lesson on the Files tab (didn't Panel-wrap the tree). Risk: the Commons Browser ends up feeling boxed-in rather than calm.

**Mitigation:** Default to Panel-wrapping ONLY the UsageFooter (and possibly the summary chip row if the operator wants visual consistency with the dashboard's tile row). Tree and viewer sit bare on the splitter, matching the detail-panel Files-tab pattern.

### B. Scanner / usage-data shape drift

If the spec or implementation accidentally proposes a richer usage data shape (e.g. line numbers, last-import-date, dependency-direction), the scanner becomes feature work — out of scope. Risk: scope creep into scanner backend.

**Mitigation:** §6 below explicitly documents the existing shape as immutable for Phase 3E. Any usage-data enrichment is a separate future phase.

### C. FileViewer coupling

The Commons Browser uses FileViewer identically to the detail-panel Files tab. If anything in Phase 3E touches FileViewer, it would re-open the Phase 3D `do NOT` list. Risk: small scope creep that touches FileViewer's preview rendering.

**Mitigation:** Phase 3E spec §8 forbids FileViewer modification. Implementation steps must NOT touch `file_viewer.py`.

### D. Search backend scope creep

While modernizing the Commons Browser, the operator may want "while you're in there, let's also add search across commons files." Risk: Phase 3E expands into search backend work.

**Mitigation:** Spec §8 forbids search backend work. Search is a deferred Phase 3F+ candidate per the candidate audit.

### E. Wave 8a scheduling conflict

Wave 8a (ValveMaster) has a doctrinal cooldown floor of 2026-06-02. If Phase 3E is still mid-flight on that date, parallel-work pressure could compromise either. Risk: Phase 3E drags past 2026-06-02 and conflicts with Wave 8a opening.

**Mitigation:** Phase 3E is small (3-4 commits over 1-2 sessions). Should fit comfortably inside the 11-day window before 2026-06-02. If it doesn't, Wave 8a is the higher doctrinal priority and Phase 3E pauses to let Wave 8a open first.

### F. "One more PCC polish" fatigue

The operator has back-to-back closed Phase 3C and 3D. Phase 3E could feel like the retrofit cadence never stops. Risk: operator perceives diminishing returns and pulls the plug mid-phase.

**Mitigation:** Frame Phase 3E explicitly as the *final* PCC main-app surface modernization. Settings / Wizard / About / Push Preview can be sub-phases later with no doctrinal commitment to do them.

### G. UsageFooter tool-list overflow

If a commons file has many tool consumers (e.g. 10+), the StatusBadge row will overflow horizontally. Risk: layout breaks or chips get cut off.

**Mitigation:** Default plan is to allow horizontal scroll inside the UsageFooter Panel via a `QScrollArea` (matching the detail-panel Files-tab tree-pane pattern). Operator review in Step 2 validates the threshold.

---

## 11. What this spec is NOT

  - **Not an implementation plan.** §7 sequences the work; it does not specify the code.
  - **Not architecture doctrine.** ADR-016 + PLATFORM_CONTRACT + MIGRATION_RULES remain the doctrinal layer.
  - **Not a redesign mandate.** It absorbs the dashboard + detail-panel existing language into the Commons Browser; no new design system invented.
  - **Not exhaustive.** Cosmetic micro-decisions (exact pixel paddings, exact StatusBadge widths, exact horizontal-scroll thresholds for the usage footer) get decided per-step during implementation. This spec sets direction, not pixels.
  - **Not a contract for scanner changes.** `scanner.scan_commons_usage`, the usage data shape, the tool corpus building logic — all untouched.
  - **Not a contract for FileViewer changes.** Spec §8 of the Phase 3D detail-panel spec forbids FileViewer redesign; that constraint carries.
  - **Not search backend work.** Search backend is a deferred Phase 3F+ candidate.

---

## 12. Branch + workflow conventions (carried from Phase 3C + 3D)

  - **Branch:** `phase-3e-pcc-commons-browser-retrofit` (per MIGRATION_RULES § Per-retrofit branch + PR convention).
  - **Commit cadence:** one commit per step in §7. Each commit gets operator visual approval before the next opens.
  - **Validation per step:** compileall + smoke tests + offscreen DetailPanel/CommonsBrowser construction smoke. Operator-visible polish review per step.
  - **Frozen-build validation:** N/A — PCC is unpackaged per `CLAUDE.md`. Source-mode validation only.
  - **Merge mode:** `--no-ff` per MIGRATION_RULES.
  - **Tag on merge:** `pcc-phase-3e-merged-v2.2.0` (matches Phase 3C/3D `v2.X.0` minor-bump convention).
  - **Reports per step:** mirrored under `phoenix-commons/docs/ui-platform-baseline-v1/PCC_COMMONS_BROWSER_IMPLEMENTATION_STEP_NN_REPORT.md`.
  - **Final closure:** `PHASE_3E_FINAL_MERGE_GATE_REPORT.md` + `PHASE_3E_FINAL_MERGE_REPORT.md` mirroring the Phase 3D closure pattern.

---

## Confirmation

  - **No implementation occurred.** This is the surface spec only. No PCC source files edited. No commons source files edited. No commits to PCC or commons except this spec file.
  - **No architecture changes occurred.** No new ADR. No commons API change. No new commons widget. No new commons icon. `BrandProfile` unchanged. ADR-014 / ADR-015 / ADR-016 all hold.
  - **No production deployment occurred.** PCC remains unpackaged. No installer. No `dist/` artifact. No GitHub Release.
  - **No production tool source touched.** Phoenix CAD / Phoenix Checkout / Project Tracking Tool / ValveMaster all unmodified.
  - **No Phase 3E implementation has begun.** Implementation steps follow operator approval of this spec.
  - **No Wave 8a work has begun.** Wave 8a remains operator-gated (cooldown floor 2026-06-02).
  - **No search backend work has begun.** Search backend remains a deferred Phase 3F+ candidate.
  - **No Settings / Wizard / About work has begun.** Each remains a future candidate for separate sub-phases.

---

*End of spec. Phase 3E direction: Commons Browser modernization. Awaiting operator approval before Step 1 implementation begins.*
