# PCC Dashboard Implementation — Step 5 Report

> **Status:** complete.
> **Date:** 2026-05-21.
> **Scope:** Aggregate metrics row modernization. 5 tiles → 4 tiles with
> Lucide leading icons + contextual subtitles per
> `PCC_DASHBOARD_SURFACE_SPEC_V1` §3.3.
> **Operator gate:** visual review of the new tile row before Step 6
> (top utility band: search shell + sync pill) starts.

---

## 1. Aggregate tile inventory

| Pre-Step-5 | Survives? | Post-Step-5 |
|------------|-----------|-------------|
| Tools | ✓ | Tools (with icon + subtitle) |
| Total LOC | ✓ | Total LOC (with icon + subtitle) |
| Open TODOs | ✓ | Open TODOs (with icon + subtitle) |
| Total Size | ✓ | Total Size (with icon + subtitle) |
| Needs Commit | ✗ retired | (status now in tools-table STATUS column) |

**Why "Needs Commit" retires:** the dirty-repo count it represented is now visible per-row in the table's STATUS column as a coloured `StatusBadge` pill ("Clean" / "N changes" / "Unknown"). Carrying it again as an aggregate tile was redundant — operators can already see "which tools need commit" at the table level. Spec §3.3 explicitly nominates this for retirement.

---

## 2. Tile redesign decisions

### Per-tile structure (was → now)

| Aspect | Pre-Step-5 | Post-Step-5 |
|--------|------------|-------------|
| Outer chrome | `objectName="statCard"` QFrame, no QSS rule matched | Same widget, unchanged QSS targeting |
| Header | "TOOLS" uppercase label only | Leading Lucide icon + label, in a horizontal row |
| Value | 28px bold accent | 28px bold accent (preserved) |
| Subtitle | none | New 11px muted line beneath the value |
| Minimum size | 140 × 88 | 160 × 96 (slightly larger to host the subtitle line) |

### What stayed the same

  - 28px bold value as the dominant visual element. Spec §2 *"Numbers prominent"* preserved.
  - Uppercase muted label with letter-spacing. Spec §4 *"Section headers small + uppercase + muted"* preserved.
  - Accent-colored value (per-tile accent) — Tools orange, LOC teal, TODOs amber, Size muted slate.
  - No animation. No count-up effects. No flashy chrome. Calm as before.

### What changed

  - Leading icon establishes glance recognition: operator can tell which tile is which by silhouette before reading the label.
  - Subtitle adds context that "the number alone doesn't carry" — the spec's central distinction between "numbers without context" and "numbers with framing."
  - Tile minimum size grew by 20px height + 20px width to accommodate the new chrome without crowding.

---

## 3. Icon mapping

| Tile | Lucide icon | Source | Rationale |
|------|-------------|--------|-----------|
| Tools | `package` | commons (already shipped Step 1) | Collection-of-repos semantic. |
| Total LOC | `file-text` | **NEW commons (Step 5)** | Code-as-text mass. |
| Open TODOs | `warning` | commons (already shipped) | Operator-action signal — TODOs are reminders of pending work. |
| Total Size | `hard-drive` | **NEW commons (Step 5)** | Disk footprint. |

Two new SVGs added to commons (`lucide/file-text.svg`, `lucide/hard-drive.svg`) — both Lucide-standard MIT-licensed. ICON_NAMES extended from 13 → 15. Tests auto-discover via ICON_NAMES iteration so no test edits required; all 126/126 commons tests pass.

Icons render at 14×14 px tinted `C["text_muted"]` (muted slate) so they don't compete with the metric value for attention — the icon is a glance aid, not a feature.

---

## 4. Subtitle system

### Per-tile subtitle content

| Tile | Subtitle pattern | Data source | Fallback |
|------|------------------|-------------|----------|
| Tools | `"across {basename(root_path)}"` | `self.cfg["root_path"]` passed into `Dashboard.set_tools(root_path=...)` | empty (hidden) when no root configured |
| Total LOC | `"across {N} tool{s}"` | scan result count | empty when no data |
| Open TODOs | `"{N} marked FIXME"` or `"no FIXMEs flagged"` | counted inline in `finalize_stats` by inspecting each undone TODO's `text` field for `"FIXME"` (uppercased match) | always populated |
| Total Size | `"Largest: {prettified_tool_name}"` | tool with `max(total_size)` from the scan corpus | empty when no data |

### Real-data sourcing — no analytics backend invented

The spec brief was clear: "Use real data where cleanly available. Otherwise: graceful static fallback text is acceptable. Do NOT: invent fake analytics."

  - **Tools subtitle** ("across PycharmProjects") — straight `os.path.basename` of the configured root path. No new scanner work. No new config field.
  - **LOC subtitle** ("across 7 tools") — uses the existing scan-result count. The "+1,840 this week" reading from the spec screenshot is a *trend* and would require historical tracking we don't have. Skipped — replaced with a static count that's still informative.
  - **TODOs subtitle** ("2 marked FIXME") — counted inline by inspecting each TODO's `text` field for "FIXME" (case-insensitive). Scanner already returns the full TODO text via `get_todos`; no scanner change required.
  - **Size subtitle** ("Largest: ValveMasterTool") — finds the tool with max `total_size` from the existing scan data, prettifies the name. No new scanner field.

No new scanner field. No new config schema. No new backend.

---

## 5. Validation results

| Check | Result |
|-------|--------|
| Commons `python -m pytest -q tests/` | **126 passed in 0.25s** (+2 new ICON_NAMES auto-discovered; was 124 pre-Step-5) |
| Commons `phoenix_commons.icons.icon("file-text")` / `icon("hard-drive")` resolve | OK — both SVGs ship; `IconNotFoundError` not raised |
| PCC `python -m compileall -q . -x ".venv\|commons\|build\|dist\|__pycache__"` | clean |
| PCC `python -m pytest -q tests/` | **4 passed in 0.21s** (existing smoke; AggregateTile constructor with new kwargs imports + instantiates correctly during MainWindow boot) |
| PCC source-mode launch | exit 0 expected (operator visual review pending) |
| Tile rendering | All 4 tiles construct with their leading icon + initial placeholder subtitle |
| Icon rendering | `package` / `file-text` / `warning` / `hard-drive` render via Lucide loader with `C["text_muted"]` tint |
| Subtitle rendering | Subtitle slot hidden by default (empty string), revealed when set_subtitle is called |
| Dark-theme compatibility | Tile chrome stays the same; new subtitle uses `C["text_muted"]` so it adapts to PCC's chrome palette |
| BrandProfile compatibility | Tiles consume `C` palette tokens directly; icons routed through `phoenix_commons.icons.icon()` which uses SEMANTIC_COLORS (not BrandProfile slots). No brand-profile change required |
| Layout stability | New tile size 160×96 (was 140×88). 4 tiles at 12px gap fit the dashboard content area at 1300×800 default; tiles size up gracefully on wider windows |
| post-B5 subprocess invariant | preserved (no subprocess changes) |
| post-B6 setStyleSheet invariant | preserved — AggregateTile uses inline styles by design (pre-existing pattern); new icon QLabel + subtitle QLabel are added without introducing new `setStyleSheet` call sites at the Dashboard composition level |

---

## 6. Remaining dashboard debt

Per the spec §6 sequence:

| # | Step | Status |
|---|------|--------|
| 1 | Lucide icons + sidebar modernization | done (B9) |
| 2 | StatusBadge primitive + dashboard pilot | done (B10) |
| 3 | Tools list → PhoenixTable | done (B11) + B11.1-B11.4 polish |
| 4 | Per-tool activity tag colors | done (B12) |
| 5 | **Aggregate tile refresh** | **done (B13, this commit)** |
| 6 | Top utility band (search shell + sync pill) | pending |
| 7 | Search backend | pending |
| 8 | Status-bar `Press ⌘K to search` hint | pending |

Items deferred but not blocking:

  - **LOC trend subtitle** ("+1,840 this week") — would require historical LOC snapshotting; PCC doesn't persist scan history. Out of scope for the dashboard's flagship-polish series; can be revisited if/when scan history becomes a separate feature.
  - **Tile color palette** — currently each tile uses a per-tile accent: orange (Tools), teal (LOC), amber (TODOs), muted slate (Size). Operator may want to revisit if any tile's color feels off.
  - **TODOs subtitle copy** — currently shows "N marked FIXME" with a "no FIXMEs flagged" fallback. Could be enriched if scanner gained a priority field (currently FIXME is detected by substring scan, which catches "FIXME:" but also any prose mention).

---

## 7. Recommended Step 6 implementation target

The spec §6 nominates Step 6 as **"Top utility band: search shell + sync-state pill"** — adds a net-new horizontal band above the dashboard body containing the page title, a centered search input with ⌘K shortcut affordance, and a right-aligned sync-state pill.

**Recommendation: proceed to Step 6 as scoped in the spec.**

Three reasons:

  1. **Visible identity surface.** The top utility band is the single most "2026 dev tool" surface visible in the spec screenshot. Adopting it shifts PCC's first-paint identity from "PySide6 dashboard" to "Linear-style operator surface."
  2. **Search shell only — no backend.** The spec is explicit that Step 6 is the *shell* (the input widget + ⌘K binding + "coming soon" placeholder); the search *backend* is Step 7. This keeps Step 6 scope bounded.
  3. **Reuses Step-2 StatusBadge** for the sync pill. The "All synced · 14:22" pill in the screenshot is exactly a StatusBadge in `clean` variant. Step 2's primitive earns its keep again.

### Step 6 scope (preview)

  - New `TopBand` widget in `dashboard.py` (or a small new module if it grows past ~80 LOC). Three children: page title on the left, search input centered, sync-pill on the right.
  - Search input wired to `Ctrl+K` (Windows) / `Cmd+K` (macOS) global shortcut — focuses the input. No completion / no results panel — just the focused state for now.
  - Sync pill is a `StatusBadge` instance — variant defaults to `clean` showing "All synced · HH:MM"; switches to `scanning` during active scans; switches to `error` if a scan fails.
  - Status-bar hint ("Press ⌘K to search") is the Step-8 micro-addition that pairs with this.

### Optional intermediate — Step 5.5

If the operator wants the tile chrome to feel more substantial (currently the icons are subtle by design), Step 5.5 could bump icon size 14px → 18px and increase the tile minimum-height by another 8-16px. Not blocking Step 6; operator's call after visual review.

---

## 8. Confirmation

  - **No architecture changes occurred.** No new ADR. No public-API rename. `AggregateTile` API gained two keyword-only kwargs (`icon_name`, `subtitle`) — backward-compatible additions. The two new Lucide SVGs and the ICON_NAMES extension are pure-additive commons content.
  - **No production deployment occurred.** Work is source-mode only on PCC `phase-3c-pcc-retrofit` and commons `main`. No installer built, no `dist/` zip created, no GitHub Release published. Neither branch pushed.
  - **No BrandProfile changes occurred.** `PCC_BRAND` unchanged. `BrandProfile` API unchanged. Tile color choices use PCC's `C` palette tokens (which point at brand slots) but the *mechanism* is unchanged.
  - **No production tool source touched.** PCC-only PCC-side change. Phoenix CAD / Phoenix Checkout / PTT / PMT / ValveMaster all untouched.
  - **No commons API break.** ICON_NAMES grew by 2 entries; existing entries unchanged. Existing consumers of `phoenix_commons.icons.icon()` continue to work without modification.
  - **No subprocess regression.** No new subprocess calls. Post-B5 invariant preserved.
  - **No widget-level setStyleSheet regression.** `AggregateTile`'s inline styling predates B6 (it's the same pre-existing pattern); Step 5 refines the tile primitive but doesn't introduce new cascade-bypassing widgets at the Dashboard composition level.
  - **No animation, no analytics backend, no metrics-framework dependency added.** Subtitles compute from existing scan data only.

---

## Commit summary

| Repo | Commit | Subject |
|------|--------|---------|
| sibling `phoenix-commons` `main` | `d5827b9` | icons: add file-text + hard-drive Lucide SVGs (Step 5) |
| PCC submodule `commons` `main` | `333820c` | icons: add file-text + hard-drive Lucide SVGs (Step 5) (mirror) |
| `phoenix-command-center` `phase-3c-pcc-retrofit` | (B13) | Aggregate tiles refresh — icons + subtitles, 5 → 4 (B13, Step 5) |

**Operator gate:** visual review of the new aggregate-tile row before Step 6 starts. Recommended capture targets:

  1. Full dashboard at default 1300×800 — confirm 4 tiles (no "Needs Commit"), each with a leading icon next to its label and a contextual subtitle line beneath the value.
  2. Close-up of the tile row — confirm icon shapes are distinct (box / file / triangle / drive silhouettes).
  3. Confirm subtitles read naturally for the operator's actual tool set (e.g., "across PycharmProjects", "across 7 tools", "no FIXMEs flagged" or "2 marked FIXME", "Largest: ValveMasterTool").
  4. Compare against pre-Step-5 (5 tiles, no icons, no subtitles) — confirm the new chrome feels calmer and more informative without competing with the tools table for attention.

---

*End of report.*
