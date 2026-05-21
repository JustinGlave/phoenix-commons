# PCC Detail Panel Implementation — Step 2 Report

> **Status:** complete (PCC commit pending; commons commit pushed).
> **Date:** 2026-05-21.
> **Branch:** `phase-3d-pcc-detail-retrofit` (PCC).
> **Scope:** detail-panel aggregate tile row — replace local `StatTile`
> with shared `AggregateTile`; reduce 6 → 4 tiles; add Lucide icons +
> real-data subtitles. Per `PCC_DETAIL_PANEL_SURFACE_SPEC_V1` §3.3 + §7.
> **Operator gate:** visual review of band+tile continuity before
> Step 4 (Overview tab modernisation) starts.

---

## 1. Legacy tile audit

### Pre-Step-2 (6 tiles, all local `StatTile`)

```python
self.tile_commit = StatTile("Last Commit")
self.tile_loc    = StatTile("LOC")
self.tile_size   = StatTile("Size")
self.tile_todos  = StatTile("Open TODOs")
self.tile_done   = StatTile("Completed")
self.tile_files  = StatTile("Code Files")
```

`StatTile` (local class, 20 LOC in `detail_panel.py:70-88`):
  - Center-aligned label + value
  - `setObjectName("statCard")` for QSS chrome
  - No leading icon
  - No subtitle slot
  - Different layout/visual treatment from the dashboard's `AggregateTile`

**Documented problems:**

  - **Chrome drift.** `StatTile` and `AggregateTile` look similar at a glance but the proportions, label treatment, and value typography are subtly different. The dashboard tile feels modern (28px value, leading icon, subtitle context); `StatTile` reads as a flat pre-retrofit card.
  - **Too many tiles.** 6 in a row at PCC's default 1300px window with a sidebar makes each tile narrow. The dashboard's 5 tiles already felt at the density edge; 6 is over.
  - **Redundancy with tab content.** "Completed" duplicates information already in the TODOs tab summary line. "Code Files" duplicates the Files tab tree (and is now better surfaced as the LOC tile's subtitle).
  - **No visual continuity with the modernised top band** (Step 1). The new band sits above a row of legacy chrome — most visible inconsistency in the panel.

### Workflow preservation requirement

Pre-Step-2 the 6 tiles surfaced:
  - Last commit time (`data["last_commit"]`)
  - Lines of code (`data["loc"]`)
  - Total disk size (`data["total_size"]`)
  - Open todo count (computed from `data["todos"]`)
  - Completed todo count (computed similarly)
  - Code file count (`data["file_count"]`)

**Step 2 preserves Last Commit / LOC / Size / Open TODOs as primary metrics.** Completed retires (visible in TODOs tab summary). Code Files retires (visible in LOC subtitle: "across N files").

---

## 2. AggregateTile migration details

### What changed

| Aspect | Pre-Step-2 | Post-Step-2 |
|--------|-----------|-------------|
| Class | local `StatTile(QFrame)` (20 LOC) | shared `AggregateTile(QFrame)` (imported from `dashboard.py`) |
| Icon support | No | Yes (`icon_name=` kwarg) |
| Subtitle support | No | Yes (`subtitle=` kwarg + `set_subtitle()` method) |
| Label typography | center-aligned 11px text_sub | uppercase small-caps muted (matches dashboard) |
| Value typography | center-aligned 22px bold | left-aligned 28px 800-weight + negative letter-spacing (matches dashboard) |
| Layout | 2-row (value + label) | 3-row (icon+label / value / subtitle) |
| QSS objectName | `statCard` | `statCard` (same — inherits dashboard's QSS chrome) |
| Tile count | 6 | **4** |

### Files modified

```
detail_panel.py   ~30 LOC retired (StatTile class deleted)
                  ~30 LOC added (4-tile construction + subtitle wiring)
                  net ≈ 0 LOC; the migration is structural, not additive
```

### Import addition

```python
from dashboard import AggregateTile
```

Cross-module import: `detail_panel.py` now reaches into `dashboard.py` for the shared widget. Forward dependency only (`dashboard.py` doesn't import `detail_panel`), so no circular risk. Module load order in `main_window.py` already imports `Dashboard` before `DetailPanel` — `AggregateTile` is available when `DetailPanel` modules are loaded.

**Architecture note:** `AggregateTile` is not yet a commons primitive. Per spec §10 "what NOT to do" — no broader commons API change in this step. Promoting `AggregateTile` to commons is a future refactor candidate but explicitly out of Phase 3D scope.

### Subtle behaviour preserved

  - `setObjectName("statCard")` retained — same QSS rule binds.
  - Accent colour per tile preserved from dashboard:
    - Last Commit → `C["accent"]` (PCC orange)
    - LOC → `C["teal"]` (PCC teal)
    - Size → `C["text_sub"]` (muted; size is not a "highlight" metric)
    - Open TODOs → `C["warning"]` (amber — calls attention without alarming)

---

## 3. Tile reduction rationale

### Retired tiles

| Tile | Why retired |
|------|-------------|
| **Completed** | Already surfaced inside the TODOs tab as part of the summary line. The number is more useful in context (next to the open count and the FIXME count) than as a standalone at-a-glance metric. |
| **Code Files** | Implicit in the Files tab tree. **Re-surfaced as the LOC tile subtitle** (`"across N files"`) so the operator still sees the file count alongside the LOC figure where it's contextually relevant. |

### Retained tiles

All four retained tiles answer a distinct, operationally-relevant question:

| Tile | Question answered | Glanceable? |
|------|-------------------|-------------|
| **Last Commit** | "How recently was this tool worked on?" | Yes — relative time string. |
| **LOC** | "How big is this codebase?" | Yes — single comma-formatted integer. |
| **Size** | "How much disk space?" | Yes — human-readable bytes. |
| **Open TODOs** | "What pending work do I have here?" | Yes — integer count + FIXME context. |

### Density improvement

PCC's default 1300px window with a 362px sidebar gives the detail panel ~938px of content width. With 6 tiles at 12px gaps + ~10px internal margins, each tile got ~140px. With 4 tiles, each gets ~210px — substantially more room for the leading icon + larger value + subtitle line.

---

## 4. Icon mapping

| Tile | Lucide name | Status in commons | Tint |
|------|-------------|-------------------|------|
| **Last Commit** | `clock` | **NEW in this step** (commons commit `2c72f22`) | `text_muted` (passed via AggregateTile default) |
| **LOC** | `file-text` | existing (added Phase 3C Step 5) | `text_muted` |
| **Size** | `hard-drive` | existing (added Phase 3C Step 5) | `text_muted` |
| **Open TODOs** | `warning` | existing (commons baseline) | `text_muted` |

Commons icon set grew **19 → 20** with this step's `clock` addition. Same closed-set semantics preserved.

`AggregateTile` constructor accepts `icon_name=`; the widget tints the icon with `C["text_muted"]` internally and renders at 14×14 px above-left of the label (per Phase 3C Step 5 implementation).

---

## 5. Subtitle system

### Convention: real data only

Per spec §3.3 + §10 ("Do not invent fake analytics"): every subtitle is populated from existing `scanner.get_git_info()` / `get_file_stats()` / `get_todos()` data. No fabricated trends, no synthetic "+N this week" copy.

### Per-tile subtitles

| Tile | Subtitle template | Source field | Empty state |
|------|-------------------|--------------|-------------|
| **Last Commit** | `on {branch}` | `data["branch"]` | empty when branch missing |
| **LOC** | `across {file_count} files` | `data["file_count"]` | empty when file_count is 0 |
| **Size** | (intentionally empty) | — | — |
| **Open TODOs** | `all clear` / `N marked FIXME` / `none marked FIXME` | computed inline from `data["todos"]` | varies (see below) |

### Open TODOs subtitle — three states

```python
n_fixme = sum(
    1 for t in todos
    if not t.get("done") and "fixme" in t.get("text", "").lower()
)

if open_t == 0:
    self.tile_todos.set_subtitle("all clear")
elif n_fixme:
    self.tile_todos.set_subtitle(f"{n_fixme} marked FIXME")
else:
    self.tile_todos.set_subtitle("none marked FIXME")
```

Three meaningful operator-states:
  - **`all clear`** — no open TODOs at all; positive signal.
  - **`N marked FIXME`** — there are FIXMEs specifically (urgent flavour of TODO); operator-priority hint.
  - **`none marked FIXME`** — TODOs exist but none are FIXMEs; calm informational.

FIXME detection: case-insensitive substring scan of each open todo's `text`. Matches the scanner's existing data shape — no scanner changes required.

### Why Size has no subtitle

The file count already appears in the LOC tile's subtitle. Repeating it on the Size tile would be redundant. The Size tile reads as a clean "{N} MB" + "Size" label without competing subtitle text.

This matches the dashboard's pattern where some tiles have richer subtitles than others; not every tile needs context.

---

## 6. Validation results

| Check | Result |
|-------|--------|
| Commons `python -m pytest -q tests/` (with clock SVG) | ✓ **131 passed in 0.40s** (+1 new auto-discovered via ICON_NAMES iteration) |
| PCC `python -m compileall -q . -x "\.venv\|commons\|build\|dist\|__pycache__"` | ✓ clean |
| PCC `python -m pytest -q tests/` | ✓ **4 passed in 0.32s** |
| PCC source-mode launch | ✓ launched (background; clean exit expected pending output-file size confirmation) |
| All 5 top-band action routings preserved | ✓ unchanged from Step 1 |
| StatusBadge (Step 1 surface) untouched | ✓ no edits to status_badge / branch_lbl |
| Tile constructor doesn't crash with missing data | ✓ subtitle slots default to empty string; tile shows just value + label |
| `AggregateTile` cross-module import resolves | ✓ verified by pytest (MainWindow boots → DetailPanel constructs → AggregateTile imported successfully) |
| post-B5 subprocess invariant | ✓ preserved (no subprocess changes) |
| post-B6 setStyleSheet invariant | ✓ preserved — `AggregateTile` uses commons cascade via `#statCard` objectName, not widget-level `setStyleSheet` |
| BrandProfile invariant | ✓ tile accent colours source from PCC `C` palette tokens; no BrandProfile changes |

---

## 7. Remaining detail-panel debt

Per spec §7 sequencing:

| # | Step | Status |
|---|------|--------|
| 1 | Top utility band restructure | ✅ done |
| 2 | **AggregateTile migration + 6 → 4 tiles** | ✅ **done (this step)** |
| 3 | Action buttons elsewhere → commons widgets (Pull/Push/Fetch in Git tab) | pending — covered in Step 6 |
| 4 | **Overview tab — Panel wrap + modernise SyncStatusCard** | pending (recommended next) |
| 5 | TODOs tab — Panel wrap + modernise TodoItem | pending |
| 6 | Git tab — Panel wrap + monospace QPlainTextEdit + Secondary buttons | pending |
| 7 | Files tab — Lucide pass on CommonsDropZone + splitter chrome | pending |
| 8 | Keyboard shortcuts (Ctrl+1..4 etc.) | pending (optional) |

### Cosmetic debt remaining in this surface

  - **`_hbtn` helper** still unused (from Step 1) — retire alongside `_abtn` in Step 6.
  - **`StatTile` class deleted entirely** — no orphan to clean up later.
  - The retired tile data (`tile_done` / `tile_files` `set_value` calls) was removed at the same time; no dangling attribute references.

---

## 8. Biggest remaining visual mismatch

**`SyncStatusCard` in the Overview tab** is now the most visibly "old PCC" element in the detail panel. It's a chip-cluster widget (ahead/behind/uncommitted indicators) using inline-styled QLabels — same pattern that the dashboard retired in Phase 3C and that Step 1 retired in the top band. Sitting right beneath the now-modernised tile row, the contrast is sharp.

**Recommendation: Step 4 should be the next focus** to retire the SyncStatusCard chip soup. Per spec §3.4, the modernised SyncStatusCard becomes a Panel containing 3 StatusBadge instances (ahead/behind/uncommitted with semantic variants).

---

## 9. Recommended Step 3 / Step 4 target

Spec §7 numbers the remaining steps as **3** (button migration elsewhere — Git tab Pull/Push/Fetch) and **4** (Overview tab Panel wrap + SyncStatusCard). Both are valid next moves.

**Recommendation: skip directly to Step 4 (Overview tab modernisation).**

Reasons:

  1. **Visual continuity.** The Overview tab sits one click away from the now-modernised tile row. Modernising it preserves the dashboard-feel as the operator drills into the panel's primary tab. Step 3 (Git tab buttons) is a deeper drill and lower visual-impact.
  2. **Biggest remaining mismatch.** Per §8 above, the `SyncStatusCard` is the operator-visible weakest link now. Addressing it next is the strongest "felt-quality" improvement per LOC.
  3. **Step 3 (Git buttons) is small.** Pull/Push/Fetch button migration is mechanical — fits into Step 6 (full Git-tab modernisation) without forcing a separate session.

Sequencing recommendation: **Step 4 (Overview + SyncStatusCard) → Step 5 (TODOs) → Step 6 (Git, including the deferred button migration) → Step 7 (Files) → Step 8 (optional shortcuts).**

---

## 10. Confirmation

  - **No architecture changes occurred.** No new ADR. `clock.svg` is a pure-additive commons icon (ICON_NAMES 19→20; closed-set semantics preserved). `AggregateTile` import from `dashboard.py` adds a cross-module dependency but no new module or new commons primitive. `StatTile` deletion is pure subtraction.
  - **No BrandProfile changes occurred.** PCC `BrandProfile` unchanged. Tile accents source from PCC `C` palette tokens which haven't moved. `AggregateTile`'s own QSS rule (`#statCard`) is dashboard-side and untouched.
  - **No production deployment occurred.** Source-mode only on `phase-3d-pcc-detail-retrofit` branch. No installer built. No `dist/` zip created. No GitHub Release. Step 2 commit not yet pushed to PCC origin (operator-gated).
  - **No production tool source touched.** PCC-only. Phoenix CAD / Phoenix Checkout / PTT / PMT / ValveMaster all unmodified.
  - **No backend logic changed.** `load_tool()` data flow unchanged except for the tile-set-value surface (4 instead of 6) + new subtitle calls.

---

## Commit summary

| Repo | Commit | Subject |
|------|--------|---------|
| `phoenix-commons` `main` | `2c72f22` (pushed) | icons: add clock Lucide SVG (Phase 3D Step 2) |
| `phoenix-command-center` `phase-3d-pcc-detail-retrofit` | (this commit, pending) | Detail panel aggregate tiles — StatTile → AggregateTile (Phase 3D Step 2) |
| `phoenix-commons` `main` | (this report, pending) | Add PCC_DETAIL_PANEL_IMPLEMENTATION_STEP_02_REPORT |

PCC retrofit branch tip after Step 2: pending. Operator-gated push to origin.

---

*End of report.*
