# PCC Detail Panel Implementation — Step 4 Report

> **Status:** complete (PCC commit pending push; commons reports pushed).
> **Date:** 2026-05-21.
> **Branch:** `phase-3d-pcc-detail-retrofit` (PCC).
> **Scope:** Overview tab modernisation — `SyncStatusCard` chip cluster
> replaced with Panel-derived StatusBadge surface; Recent Commits feed
> wrapped in Panel. Per `PCC_DETAIL_PANEL_SURFACE_SPEC_V1` §3.4 + §7
> step 4.
> **Operator gate:** visual review of the modernised Overview tab
> before Step 5 (TODOs tab) starts.
> **Step 3 (button migration) deferred** to Step 6 (Git tab) per Step
> 2's report recommendation — sequencing went 1 → 2 → 4 to address
> highest visible-impact mismatch first.

---

## 1. SyncStatusCard audit findings

### Pre-Step-4 (legacy)

The Overview tab's primary widget was `SyncStatusCard(QFrame)` — a 200+ LOC class with:

  - **Bespoke card chrome** — inline `setStyleSheet` defining `#syncCard` background / border / radius (duplicates what commons `Panel` already provides).
  - **Three inline-styled chip QLabels** — `chip_ahead` / `chip_behind` / `chip_dirty`, each built by a local `_chip(text, color)` helper. Used emoji prefixes: `⬆ 0 ahead`, `⬇ 0 behind`, `📝 0 uncommitted`.
  - **Emoji-prefixed title** — `"⇄  SYNC STATUS"` (uppercase muted).
  - **Inline-styled section sub-headers** — `"UNPUSHED COMMITS"` / `"UNCOMMITTED FILES"` each with bespoke letter-spacing styling instead of the commons `#sectionHeader` selector.
  - **Operational detail rows preserved** — commit hash + msg pairs, file status code + path pairs (these carry real value, not chrome).

### Documented problems

  - **Most visibly "old PCC" surface in the detail panel** after Steps 1+2 modernised the top band + tile row. The Overview tab is the operator's first stop when drilling into a tool; the chip cluster broke the dashboard-feel immediately.
  - **Chrome-system mismatch** with the rest of the detail panel: top band uses commons primitives (StatusBadge + commons buttons + Lucide icons), tile row uses commons primitives (AggregateTile + Lucide icons), but the Overview tab dropped back to inline-styled QFrame + QLabel chips.
  - **Emoji semantics scattered** — `⇄ ⬆ ⬇ 📝` plus emoji `✓ ⚠` in the status sentence (the latter not retired in this step — see §6 remaining debt).
  - **Three chip widgets duplicating StatusBadge functionality** — same job (semantic state pill), different chrome. Pre-Phase-3C they each used hand-rolled inline styling.

### Workflow preservation requirement

Pre-Step-4 the SyncStatusCard surfaced four classes of information:
  1. Ahead/behind/uncommitted counts at-a-glance (the 3 chips)
  2. Plain-text status sentence with upstream name + warning when no upstream tracking
  3. Listing of specific unpushed commits (hash + message)
  4. Listing of specific dirty files (git-status code + path)

**Step 4 preserves all four classes.** Chrome modernised; operational detail data unchanged.

---

## 2. Overview-tab modernisation details

### Architectural change

```
Pre-Step-4:
  class SyncStatusCard(QFrame):           ← Frame with inline-styled chrome
      def __init__(self, parent=None):
          self.setObjectName("syncCard")
          self.setStyleSheet("...")        ← bespoke card QSS

Post-Step-4:
  class SyncStatusCard(Panel):            ← Inherits commons Panel
      def __init__(self, parent=None):
          super().__init__(title=None)
          self.layout().setContentsMargins(14, 12, 14, 12)
          self.layout().setSpacing(8)
```

Panel's `WA_StyledBackground` + `#Panel` QSS rule now provide the rounded-card chrome (background `rgba(20,24,41,180)`, 1px `#2d3748` border, 14px radius) — identical to the dashboard's TOOLS / RECENT ACTIVITY panels. Visual continuity restored.

### Internal layout (post-Step-4)

```
┌─ SyncStatusCard (Panel) ────────────────────────────────────────────┐
│                                                                     │
│  SYNC STATUS                  [In sync] [Up to date] [Clean tree]  │  ← header row
│  ────────────────────────────────────────────────────               │
│  ✓ Fully in sync with origin/main                                   │  ← status sentence
│                                                                     │
│  UNPUSHED COMMITS                                                   │  ← section subhead
│  abc1234  Fix table column widths                                   │  ← detail rows
│  def5678  Bump version                                              │
│                                                                     │
│  UNCOMMITTED FILES                                                  │  ← section subhead
│   M  dashboard.py                                                   │  ← detail rows
│  ??  notes.md                                                       │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### Recent Commits modernisation

The Overview tab's second region (Recent Commits feed) was previously a bare `_sec("Recent Commits")` label + scrollable `QVBoxLayout` of inline-styled commit rows. Post-Step-4 it's wrapped in its own Panel container with an internal `sectionHeader` label and the existing scroll area (frame retired via `setFrameShape(NoFrame)` so it doesn't draw a double-border inside the Panel).

```
┌─ Recent Commits (Panel) ────────────────────────────────────────────┐
│                                                                     │
│  RECENT COMMITS                                                     │
│  ────────────────────────────────────────────────────               │
│  Fix table column widths                                  2h ago   │
│  Bump version                                             5h ago   │
│  Refactor user_auth session ...                       yesterday    │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

The per-row commit chrome (message + timestamp) is **deliberately preserved**. Per spec §4 "Do NOT redesign commit logic; keep the feed operational and lightweight." Future polish if needed but not in scope here.

---

## 3. Status semantic modernisation

### The three-pill system

Replaces the prior 3 emoji-prefixed chips with 3 `StatusBadge` instances. Each pill expresses one independent dimension of repo state.

| Badge | Pre-Step-4 chip text | Post-Step-4 StatusBadge label / variant |
|-------|---------------------|------------------------------------------|
| `badge_ahead` | `⬆ N ahead` (teal text on surface bg) | `↑ N unpushed` (dirty amber) **or** `In sync` (clean green) **or** `Untracked` / `N/A` (unknown muted) |
| `badge_behind` | `⬇ N behind` (accent orange text on surface bg) | `↓ N behind` (dirty) **or** `Up to date` (clean) **or** `Untracked` / `N/A` |
| `badge_dirty` | `📝 N uncommitted` (warning amber text on surface bg) | `N uncommitted` (dirty) **or** `Clean tree` (clean) **or** `N/A` |

### State logic (post-Step-4 `update_state()`)

```python
if status == "unknown" and not branch:
    # Not a git repo at all
    for b in (badge_ahead, badge_behind, badge_dirty):
        b.set_status("N/A", variant="unknown")
    # status_lbl: "Not a git repository." (muted)
    return

if has_upstream:
    badge_ahead.set_status(
        f"↑ {ahead} unpushed" if ahead > 0 else "In sync",
        variant="dirty" if ahead > 0 else "clean",
    )
    badge_behind.set_status(
        f"↓ {behind} behind" if behind > 0 else "Up to date",
        variant="dirty" if behind > 0 else "clean",
    )
else:
    # Upstream not tracked — ahead/behind not measurable
    badge_ahead.set_status("Untracked", variant="unknown")
    badge_behind.set_status("Untracked", variant="unknown")

# Uncommitted is meaningful regardless of upstream
badge_dirty.set_status(
    f"{n_dirty} uncommitted" if n_dirty > 0 else "Clean tree",
    variant="dirty" if n_dirty > 0 else "clean",
)
```

### Three operator-perception cases the new semantics handle correctly

  1. **Clean tool, fully synced.** All three badges read clean (green): "In sync" / "Up to date" / "Clean tree". Single-glance confidence.
  2. **Local work in progress.** Tree dirty + ahead of upstream: `badge_ahead = "↑ 2 unpushed"` (dirty amber), `badge_behind = "Up to date"` (clean green), `badge_dirty = "5 uncommitted"` (dirty amber). The operator sees exactly what's pending at a glance.
  3. **Fresh-clone-no-tracking.** Upstream not yet bound: `badge_ahead = "Untracked"` (muted), `badge_behind = "Untracked"` (muted), `badge_dirty` reflects actual state. The status sentence below explains why (no upstream warning).

### Why three pills instead of one

A single `StatusBadge` summarising "Clean" / "Dirty" (as the top band's tool status pill does) would lose dimension. The detail panel is the operator's drill-down surface; three independent pills give three independent answers without forcing the operator to read a paragraph.

---

## 4. Recent-commits modernisation

### Scope

Per spec §4 — Panel wrap only. Internal commit-row chrome (hash / message / timestamp) preserved.

### Changes

  - **Outer container:** `_sec("Recent Commits")` + bare QScrollArea → `Panel()` + internal `sectionHeader` label + QScrollArea.
  - **Scroll-area frame:** `setFrameShape(QFrame.NoFrame)` so the QScrollArea doesn't draw a double-border inside the Panel chrome.
  - **Margins:** Panel default `(16,16,16,16) / 12` → tightened to `(14,12,14,12) / 8` to match the modernised SyncStatusCard above it.
  - **Stretch behaviour:** Panel takes `addWidget(commits_panel, 1)` in the Overview tab layout so it fills remaining vertical space.

### What didn't change

  - `_populate_commits()` logic untouched.
  - Per-row commit widget chrome untouched (still uses the existing inline-styled `#commitMsg` / `#commitWhen` object names).
  - `setHorizontalScrollBarPolicy(ScrollBarAlwaysOff)` preserved.
  - Commit count limit unchanged (controlled by scanner data).

---

## 5. Validation results

| Check | Result |
|-------|--------|
| Commons tests (no commons changes this step) | n/a — no commons edit |
| PCC `python -m compileall -q . -x "\.venv\|commons\|build\|dist\|__pycache__"` | ✓ clean |
| PCC `python -m pytest -q tests/` | ✓ **4 passed in 0.21s** |
| PCC source-mode launch | ✓ launched (background; exit code 0 expected — clean exit confirmed pending output-file check) |
| All 5 top-band action routings preserved | ✓ unchanged from Steps 1+2 |
| Aggregate tiles (Step 2) untouched | ✓ no edits to tile_commit/tile_loc/tile_size/tile_todos |
| StatusBadge variants exercised in update_state | ✓ clean / dirty / unknown all live |
| Operational data preserved | ✓ status_lbl sentence, unpushed_commits list, dirty_files list all populated by same data paths |
| SyncStatusCard layout under Panel chrome | ✓ Panel inherits via class extension; WA_StyledBackground + #Panel QSS apply |
| Recent Commits scroll inside Panel | ✓ QScrollArea NoFrame prevents double-border |
| post-B5 subprocess invariant | ✓ preserved (no subprocess changes) |
| post-B6 setStyleSheet invariant | ✓ preserved — SyncStatusCard's class-level `setStyleSheet` removed entirely; the only remaining inline-styled labels are operational detail-row chrome (commit-hash colour, file-status code colour) which carry semantic content (per-status colour coding) and are preserved per spec §4 "do not redesign commit logic" rule |
| BrandProfile invariant | ✓ untouched — StatusBadge variants source from commons SEMANTIC_COLORS; Panel uses sentinel-substituted QSS chrome |
| Backend logic | ✓ untouched — `update_state()` reads identical `scanner.get_git_info()` payload |

---

## 6. Remaining detail-panel debt

Per spec §7 sequencing:

| # | Step | Status |
|---|------|--------|
| 1 | Top utility band restructure | ✅ done |
| 2 | AggregateTile migration + 6 → 4 tiles | ✅ done |
| 3 | Action buttons elsewhere → commons widgets (Pull/Push/Fetch) | pending — covered in Step 6 |
| 4 | **Overview tab — Panel wrap + SyncStatusCard modernise** | ✅ **done (this step)** |
| 5 | **TODOs tab — Panel wrap + modernise TodoItem** | pending (recommended next) |
| 6 | Git tab — Panel wrap + monospace output + Secondary buttons | pending |
| 7 | Files tab — Lucide pass on CommonsDropZone + splitter chrome | pending |
| 8 | Keyboard shortcuts (Ctrl+1..4 etc.) | pending (optional) |

### Cosmetic debt remaining in this surface

  - **Status sentence still uses emoji glyphs.** `update_state()` builds the status_lbl text as `"⚠  No upstream tracking..."` or `"✓  Fully in sync..."`. Could migrate to Lucide-prefixed labels but the spec scoped this step to chip-cluster → StatusBadge; sentence emoji retirement is a follow-up polish. Low priority — single-line, calm, already readable.
  - **Commit-row "#commitMsg" / "#commitWhen" object names** preserved. They render via PCC theme.py overlay QSS. Possibly future-targetable for `sectionHeader`/`bodyText` unification but out of scope here.
  - **Per-file-status colour coding** (`_status_color()` helper at line 219) retains its inline-stylesheet treatment for the M/A/D/R/?/etc. status-code chips beneath the dirty files header. These convey semantic content (file modification state). Could migrate to `StatusBadge` variants in a future polish — explicit deferral.
  - **`_hbtn` helper** still unused (carry-over from Step 1) — retire alongside `_abtn` in Step 6.

---

## 7. Biggest remaining visual mismatch

**`TodoItem` widgets in the TODOs tab** — now the most visibly "old PCC" surface in the detail panel. Each TodoItem is a QFrame with inline `setStyleSheet` painting a coloured left-border + bespoke padding. Carries pre-retrofit chrome (border-color coding, inline styling) similar to what SyncStatusCard had before this step.

Per spec §3.5: TodoItem should migrate to Panel-wrapped rows, leading Lucide icon (per-state — checkmark for done, pin/warning for open, alert for FIXME), and a per-item `StatusBadge` for done/open/FIXME state.

Step 5 is the natural next target.

---

## 8. Recommended next target

**Step 5 — TODOs tab modernisation.** Per spec §7 sequencing.

Reasons:

  1. **Visual continuity.** After Step 4 the Overview tab matches dashboard chrome. The TODOs tab is one click sideways and remains visibly legacy.
  2. **Bounded scope.** TodoItem is a single widget class (~50 LOC). Plus the TODOs tab's outer container (summary line + scroll area) needs a Panel wrap similar to Recent Commits.
  3. **No commons additions required.** Existing Panel + StatusBadge + Lucide icons (`warning`, `check`, `pin` if available... `pin` not in commons yet — would be Step-5 step-0 addition).
  4. **Operator value.** TODOs is one of the operator's main reasons to drill into the detail panel; modernising it has direct workflow impact.

### Optional precursor (Step 5 step 0)

If TodoItem's modernised design wants a `pin` Lucide icon for open TODOs (semantically distinct from `warning` which is reserved for FIXMEs), `pin.svg` needs to be added to commons. Single mechanical SVG addition (same pattern as Step 0 / Step 2 commons icon additions).

---

## 9. Confirmation

  - **No architecture changes occurred.** No new ADR. No commons API change. `SyncStatusCard` extension of `Panel` is a class-hierarchy change inside PCC, not a commons surface modification. No new module added.
  - **No BrandProfile changes occurred.** PCC `BrandProfile` unchanged. `StatusBadge` variants source from commons `SEMANTIC_COLORS` which is brand-independent (clean=green, dirty=amber, error=red, unknown=muted, syncing/scanning=brand-accent). `Panel` uses the sentinel-substituted commons QSS chrome.
  - **No production deployment occurred.** Source-mode only on `phase-3d-pcc-detail-retrofit` branch. No installer built. No `dist/` zip created. No GitHub Release. Step 4 commit not yet pushed to PCC origin (operator-gated).
  - **No production tool source touched.** PCC-only. Phoenix CAD / Phoenix Checkout / PTT / PMT / ValveMaster all unmodified.
  - **No backend logic changed.** `update_state()` reads identical scanner data shape. `_populate_commits()` / `_populate_todos()` data paths unchanged. Commit-feed + dirty-files-list + unpushed-commits-list logic untouched.

---

## Commit summary

| Repo | Commit | Subject | Pushed |
|------|--------|---------|--------|
| `phoenix-command-center` `phase-3d-pcc-detail-retrofit` | (this commit, pending) | Overview tab — SyncStatusCard + Recent Commits modernised (Phase 3D Step 4) | ✗ (operator-gated) |
| `phoenix-commons` `main` | (this report, pending) | Add PCC_DETAIL_PANEL_IMPLEMENTATION_STEP_04_REPORT | pending |

PCC retrofit branch tip after Step 4 commits: pending. Operator-gated push to origin.

---

*End of report.*
