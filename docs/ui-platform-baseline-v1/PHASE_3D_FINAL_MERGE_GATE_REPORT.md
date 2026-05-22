# Phase 3D — Final Merge Gate Report

> **Status:** merge-gate audit complete. Prepared, not executed.
> **Date:** 2026-05-21.
> **Branch:** `phase-3d-pcc-detail-retrofit`. HEAD: `390df84` (Step 7).
> **Target:** `main` (PCC's default branch).
> **What this is:** holistic Phase 3D review + cohesion audit + merge
> readiness audit + ready-to-execute merge plan.
> **What this is NOT:** the merge itself. The merge is not executed in
> this session per the brief's "Do NOT merge yet unless explicitly
> instructed."

---

## 1. Full detail-panel assessment

Holistic review of the modernised detail panel against
`PCC_DETAIL_PANEL_SURFACE_SPEC_V1` §1-9 (product intent + workflow
audit + surface inventory + interaction philosophy + visual direction).

### 1.1 Top utility band — PRIMARY ✅

Restructured per spec §3.1 + §3.2.

| Zone | Composition | Status |
|------|-------------|--------|
| LEFT — back | `TertiaryButton("Back")` + `arrow-left` Lucide (14×14, text_muted) | ✅ |
| LEFT — identity | `#pageTitle` 22px 800-weight QLabel + muted `· on <branch>` sub-label | ✅ |
| CENTER — status | Single `StatusBadge` (compact), variant flips clean/dirty/unknown | ✅ |
| RIGHT — actions | `TertiaryButton VS Code` → `TertiaryButton GitHub` → `SecondaryButton Run source` → `PrimaryButton Launch installed` | ✅ |

Action hierarchy reads correctly left-to-right: inspection → operate → launch. Primary anchors the right edge per spec §4. All button labels are clean strings; all icons are Lucide; no emoji glyphs on chrome.

### 1.2 Aggregate tiles row — SECONDARY ✅

Reduced 6 → 4 tiles per spec §3.3. Uses dashboard's `AggregateTile` (imported from `dashboard.py`).

| Tile | Icon | Subtitle convention |
|------|------|---------------------|
| Last Commit | `clock` | `on <branch>` |
| LOC | `file-text` | `across N files` |
| Size | `hard-drive` | (blank — file count is in LOC tile already) |
| Open TODOs | `warning` | `all clear` / `N marked FIXME` / `none marked FIXME` |

Same `AggregateTile` instance the dashboard uses → zero chrome drift between the two surfaces. Accent colours match dashboard palette per Phase 3C Step 5.

### 1.3 Overview tab — PRIMARY tab ✅

Per spec §3.4 + Step 4 report.

  - `SyncStatusCard` now extends `Panel` (not bare `QFrame`). Internal layout: section header + 3 `StatusBadge` pills (ahead / behind / dirty) on a single row + a calm `status_lbl` sentence + retained UNPUSHED COMMITS + UNCOMMITTED FILES detail rows (operational data preserved).
  - Recent Commits — wrapped in `Panel`. Internal QScrollArea is `NoFrame` (avoids double-border inside Panel chrome). Per-commit row preserves the calm `#card`-background frame chrome (semantic data card, not chrome).

### 1.4 TODOs tab — PRIMARY tab ✅

Per spec §3.5 + Step 5 report.

  - Summary row: 3 `StatusBadge` count pills (`N open` / `N done` / `N FIXME`). `N open` flips to `dirty` variant when >0; `N FIXME` flips to `error` variant when >0.
  - Panel wraps the per-file TodoItem list. QScrollArea NoFrame (same Panel-internal convention as Overview's commits feed).
  - `TodoItem` row: `[Lucide icon] [text body] [StatusBadge state pill] [src:line ref]`. Icon kind reflects state — `check` (done, green) / `warning` (FIXME, red) / `file-text` (md, teal) / `pin` (code TODO, muted).
  - Per-file header — `file-text` Lucide icon + filename in `#sectionHeader` muted-700.

### 1.5 Files tab — TERTIARY tab ✅

Per spec §3.6 + Step 7 report — **lightweight only**, as called for.

  - `CommonsDropZone` modernised: `[arrow-up Lucide icon] [Drag a file here…]` composition (idle, teal) flipping to `[check Lucide icon] [Copied: …]` (success, green) on drop. Dashed-border drop-affordance chrome preserved (semantic).
  - QSplitter, QTreeView, FileViewer, drag/drop wiring all preserved per spec §8 ("Do NOT redesign FileViewer / drag-drop / splitter").

### 1.6 Git tab — SECONDARY tab ✅

Per spec §3.7 + Step 6 report.

  - Actions panel: `Panel`-wrapped, internal section header + 3 `SecondaryButton`s (Pull / Push / Fetch) with `arrow-down` / `arrow-up` / `refresh` Lucide icons.
  - Output panel: `Panel`-wrapped, internal section header + `QPlainTextEdit#gitOutput` (Consolas 10pt, read-only). Per-message colour state via `outputState` dynamic property + PCC theme.py QSS selector (idle/running/success/error). `_git_out_set()` helper centralises 6 prior inline-styled call sites.

### 1.7 Spacing rhythm

| Region | Spacing |
|--------|---------|
| Top-band → tile row | 12px |
| Tile row → tab bar | 12px |
| Tab content outer margins | 16/16/16/16 (each tab's QWidget) |
| Panel internal margins | 14/12/14/12 (denser than dashboard's 16/16/16/16 — appropriate for the detail panel's denser content) |
| Panel internal section header → content | 8px |
| Between Panels in same tab | 12px (Git tab: actions panel + output panel) |

Spacing converges with the dashboard's Phase 3C-tuned rhythm. No tab feels crowded, none feels sparse.

### 1.8 Semantic consistency

Cross-panel semantics audit — every state surface uses the same variant vocabulary:

| Semantic | Used on | Variant |
|----------|---------|---------|
| Repository clean | Top-band `status_badge`, sync `badge_dirty` (when n=0) | `clean` |
| N uncommitted | Top-band `status_badge` (when n>0), sync `badge_dirty` (when n>0) | `dirty` |
| Ahead of upstream | Sync `badge_ahead` (when ahead>0) | `dirty` |
| Behind upstream | Sync `badge_behind` (when behind>0) | `dirty` |
| No upstream | Sync `badge_ahead`/`badge_behind` (when has_upstream=False) | `unknown` |
| TODO open | TodoItem state pill | `dirty` |
| TODO done | TodoItem state pill | `clean` |
| TODO FIXME (open) | TodoItem state pill, Summary `N FIXME` (when n>0) | `error` |
| Repository unknown / not git | Top-band `status_badge`, Sync card "Not a git repository." | `unknown` |
| Git op success | `git_out outputState` | `success` |
| Git op failure | `git_out outputState` | `error` |

Variant set is the same 7 from Phase 3C Step 2. **No new variants introduced** per spec §8.

### 1.9 Operational readability

  - Tool identity is visible within ~200ms of panel paint (title + branch + status badge all on the top band).
  - "What needs attention" is visible in two places — the Open TODOs tile (top) AND the TODOs tab's summary pills (drill).
  - "How do I act on it" reads top-to-bottom in priority: top-band actions → Git tab actions (Pull/Push/Fetch).
  - Git output retains its terminal-feel for operator log inspection. Property-selector QSS colours the text per state without disturbing the calm Panel container.
  - File browser remains a domain-specific workspace surface (intentionally not over-panelised).

### 1.10 Dashboard / detail continuity

Cross-surface chrome audit between Phase 3C dashboard and Phase 3D detail panel:

| Primitive | Dashboard usage | Detail panel usage | Continuity |
|-----------|-----------------|--------------------|------------|
| `Panel` rounded-card | TOOLS + RECENT ACTIVITY panels | Overview SyncStatusCard + Recent Commits + TODOs list + Git actions + Git output | ✅ identical chrome |
| `StatusBadge` 7-variant | TOOLS table STATUS column | Top-band status + Overview sync triplet + TODOs summary triplet + per-TodoItem state pill | ✅ identical chrome |
| `AggregateTile` | 5 dashboard tiles | 4 detail-panel tiles (same primitive, fewer instances) | ✅ identical chrome |
| `PrimaryButton` red | (none — dashboard has no primary action surface) | Launch installed (top-band right anchor) | ✅ tier-correct |
| `SecondaryButton` deep-blue | (none on dashboard) | Run source / Pull / Push / Fetch | ✅ tier-correct |
| `TertiaryButton` outline | (none on dashboard) | Back / VS Code / GitHub | ✅ tier-correct |
| Lucide icons | Sidebar + tile leading + table-cell + activity feed | Top-band actions + tile leading + Git-tab actions + TodoItem leading + CommonsDropZone | ✅ no emoji on chrome anywhere |
| `#pageTitle` 22px 800 | Dashboard "Phoenix Command Center" + per-page title | Detail panel tool name | ✅ identical typography |
| `#sectionHeader` 10px uppercase muted | TOOLS / RECENT ACTIVITY section headers | SYNC STATUS / RECENT COMMITS / TODOs / GIT ACTIONS / OUTPUT / per-file TODO headers | ✅ identical typography |

**Verdict:** No material visual mismatch between dashboard and detail panel. The Phase 3C primitives carried forward without drift.

---

## 2. Surface completion audit

Cross-check against `PCC_DETAIL_PANEL_SURFACE_SPEC_V1` §7 sequencing.

### 2.1 What shipped

| # | Step | Branch commit | Status |
|---|------|---------------|--------|
| 1 | Top utility band restructure | `03fdfa3` | ✅ shipped |
| 2 | AggregateTile migration + 6 → 4 tiles | `30a9333` | ✅ shipped |
| 3 | Action buttons → commons widgets | (folded into Step 1 + Step 6) | ✅ shipped — no separate commit needed |
| 4 | Overview tab — Panel wrap + SyncStatusCard modernisation | `25c4154` | ✅ shipped |
| 5 | TODOs tab — Panel wrap + modernise TodoItem | `50d5142` | ✅ shipped |
| 6 | Git tab — Panel wrap + monospace output + SecondaryButton actions | `83fada8` | ✅ shipped |
| 7 | Files tab — Lucide migration on CommonsDropZone | `390df84` | ✅ shipped |
| 8 | Keyboard shortcuts (Ctrl+1..4 etc.) | (not implemented) | ⚪ **intentionally deferred** |

**7 of 8 spec steps shipped.** Step 3 (action button migration) was a cross-cutting concern that ended up folded into Steps 1 and 6, not a separate commit — documented in the Step 6 report's commit-summary table.

### 2.2 What's intentionally deferred

Step 8 (Ctrl+1..4 tab navigation + Ctrl+P pull + Ctrl+Shift+P push + Ctrl+R refresh) per spec §4 "Optional and deferrable; the spec calls them out as nice-to-have rather than mandatory."

Recommendation per Step 7 report §6: **defer indefinitely.** Tabs are explicit; the operator uses click navigation fluidly; shortcuts would add complexity without measurable workflow benefit. Reopening Step 8 in a future polish phase remains an option but is not on the Phase 3D closure path.

### 2.3 What should remain deferred / out of scope

Per spec §8 "Explicit what NOT to do" — the following items are out of Phase 3D scope and should remain so:

  - No fifth tab, no tab reordering, no tab removal.
  - No fifth StatusBadge variant.
  - No new commons primitive.
  - No BrandProfile change (PCC stays orange + teal per ADR-016).
  - No `GitOpWorker` / `scanner.get_git_info` redesign.
  - No `FileViewer` internal redesign.
  - No `CommonsDropZone` drag-drop semantics redesign (visual chrome only).
  - No animation.
  - No notification surface.
  - No command palette (Ctrl+K stays a dashboard search anchor).
  - No back-navigation redesign.
  - No `PushPreviewDialog` chrome work (preserved as-is).
  - No file-tree workflow redesign (column visibility / sorting / context menus).

All preserved.

### 2.4 Reports landed in commons

Per spec §12 "Reports per step":

| Step | Report file | Commit |
|------|-------------|--------|
| 1 | `PCC_DETAIL_PANEL_IMPLEMENTATION_STEP_01_REPORT.md` | (in commons main) |
| 2 | `PCC_DETAIL_PANEL_IMPLEMENTATION_STEP_02_REPORT.md` | `cc7d34c` |
| 3 | (folded into Step 1 + Step 6 reports) | — |
| 4 | `PCC_DETAIL_PANEL_IMPLEMENTATION_STEP_04_REPORT.md` | `d1eae2f` |
| 5 | `PCC_DETAIL_PANEL_IMPLEMENTATION_STEP_05_REPORT.md` | `7f1618d` |
| 6 | `PCC_DETAIL_PANEL_IMPLEMENTATION_STEP_06_REPORT.md` | `a514d8e` |
| 7 | `PCC_DETAIL_PANEL_IMPLEMENTATION_STEP_07_REPORT.md` | `21238f0` |

Plus supporting commons commits for icon additions:

| Commit | What |
|--------|------|
| `2c72f22` | icons: add clock Lucide SVG (Phase 3D Step 2) |
| `580130b` | icons: add pin Lucide SVG (Phase 3D Step 5) |
| `0fb6a0e` | icons: add arrow-down + arrow-up Lucide SVGs (Phase 3D Step 6) |

ICON_NAMES grew from 17 (post-Phase-3C) to 23 (post-Phase-3D additions). Closed-set semantics preserved.

---

## 3. Validation results

### 3.1 Static checks

| Check | Result |
|-------|--------|
| PCC `python -m compileall -q . -x "\.venv\|commons\|build\|dist\|__pycache__"` | ✓ clean (exit 0) |
| PCC `python -m pytest -q tests/` | ✓ **4 passed in 0.22s** |
| Commons `python -m pytest -q tests/` | ✓ **134 passed in 0.42s** (the 6 additions: `arrow-down`, `arrow-up`, `clock`, `pin`, and the 2 existing-from-3C icon enumerations) |
| PCC working tree clean | ✓ `git status --short` returns empty |
| Commons working tree clean | ✓ `git status --short` returns empty |

### 3.2 Runtime smoke (offscreen)

End-to-end construction smoke exercised every Phase 3D surface:

```
MainWindow title    : Phoenix Command Center
DetailPanel tabs    : ['Overview', 'TODOs', 'Files', 'Git']

-- Top utility band (Step 1) --
  back_btn          : TertiaryButton
  status_badge      : StatusBadge
  vs_btn            : TertiaryButton
  gh_btn            : TertiaryButton
  run_source_btn    : SecondaryButton
  launch_installed  : PrimaryButton

-- AggregateTile row (Step 2) --
  tile_commit/loc/size/todos : AggregateTile × 4

-- Overview tab (Step 4) --
  sync_card         : SyncStatusCard (Panel-derived)
  badge_ahead/behind/dirty : StatusBadge × 3

-- TODOs tab (Step 5) --
  summary_open/done/fixme : StatusBadge × 3

-- Git tab (Step 6) --
  pull_btn/push_btn/fetch_btn : SecondaryButton × 3
  git_out            : QPlainTextEdit / outputState=idle
  → state flips OK   : running → success → error (property-selector dance)

-- Files tab (Step 7) --
  drop_zone          : CommonsDropZone
  drop_zone.hint_icon: QLabel (Lucide arrow-up idle)
  drop_zone.hint     : 'Drag a file here to copy to commons'
  tree               : QTreeView
  file_viewer        : FileViewer
```

`load_tool()` with synthetic data:
  - `status_badge.text() == "3 changes"` (dirty variant correctly chosen)
  - `summary_open.text() == "2 open"` (2 of 3 todos not-done)
  - `git_out` populates with synthesised sync sentence on initial render

All surfaces construct cleanly. All state flips work end-to-end. No runtime regressions surfaced.

### 3.3 Action routing preservation

| Action | Pre-Phase-3D handler | Post-Phase-3D handler | Status |
|--------|----------------------|------------------------|--------|
| Back | `back_clicked.emit()` | unchanged | ✅ |
| VS Code | `_open_vscode()` | unchanged | ✅ |
| GitHub | `_open_github()` | unchanged | ✅ |
| Run source | `_run_source()` | unchanged | ✅ |
| Launch installed | `_launch_installed()` | unchanged | ✅ |
| Pull / Push / Fetch | `_run_git(op)` → `GitOpWorker` | unchanged | ✅ |
| Tree click | `_on_tree_clicked(index)` → `FileViewer.load_file()` | unchanged | ✅ |
| Drop file | `CommonsDropZone.dropEvent` → `shutil.copy2` + `file_received` signal | unchanged (visual only) | ✅ |
| Push preview cancel | `PushPreviewDialog.exec()` cancel path | unchanged | ✅ |
| Pull-with-dirty warn | `QMessageBox` cancel path | unchanged | ✅ |

**Zero action-routing regressions.** Backend logic (`GitOpWorker`, `scanner.git_pull/push/fetch`, `scanner.get_push_preview`, `_resolve_installed_exe`) was not touched in any Phase 3D step.

### 3.4 Invariant preservation

| Invariant | Status |
|-----------|--------|
| **B5** — subprocess CREATE_NO_WINDOW on Windows git ops | ✅ preserved (`_HIDE_CONSOLE` flag on the porcelain check; `GitOpWorker.run` calls `git_pull`/`git_push`/`git_fetch` from scanner which carry the same flag) |
| **B6** — no widget-level `setStyleSheet` on commons primitives | ✅ preserved (only `CommonsDropZone` retains inline styles; documented carve-out for affordance-defining chrome) |
| **BrandProfile** (orange + teal per ADR-016) | ✅ untouched (`PCC_BRAND` in theme.py unchanged) |
| **Locked colour tokens** per ADR-016 (bg, surface, text, status colours) | ✅ untouched |
| **PCC overlay extension model** (object names commons doesn't carry) | ✅ preserved (new `#gitOutput` rule is an extension, not a duplication) |
| **Commons API stability** | ✅ preserved (no API change; only icon additions to a closed set) |

---

## 4. Remaining intentional debt

### 4.1 Step 8 — Keyboard shortcuts (deferred indefinitely)

Spec §7 step 8 + spec §4 "Optional and deferrable." Recommendation: **leave deferred.** Reopening this is a future polish decision, not a Phase 3D closure prerequisite.

### 4.2 Cleanup-eligible items (NOT merge blockers)

The Phase 3D modernization left a small number of cleanup-eligible items in `detail_panel.py` that mirror exactly the Phase 3C precedent (Phase 3C closed with merge `058a67a` → post-merge cleanup commit `a1b45d3` "remove Phase 3C inert orphans"). Identified items:

| # | Item | Location | Status |
|---|------|----------|--------|
| 1 | Dead helper `_sec(text)` function | `detail_panel.py:65-68` | Used pre-Step-4; retired in Step 4 without removing the definition |
| 2 | Dead import `QPushButton` | `detail_panel.py:12` | All buttons now come from commons widgets |
| 3 | Dead import `QMimeData`, `QUrl`, `QModelIndex` | `detail_panel.py:17` | No remaining references in file |
| 4 | Dead import `QCursor` | `detail_panel.py:18` | Was used by retired `_hbtn`/`_abtn` helpers |
| 5 | Dead import `STATUS_COLOR` | `detail_panel.py:29` (from theme) | Was used by pre-Step-4 chip cluster; `StatusBadge` variant strings replaced it |
| 6 | Redundant inline `QSplitter::handle` stylesheet | `detail_panel.py:701` | `theme.py` overlay (lines 601-607) already styles `QSplitter::handle` globally; the inline does the same thing |
| 7 | Submodule pin lag | PCC `commons/` at `0fb6a0e`, commons `main` at `21238f0` | 2 docs-only commits (Step 6 + Step 7 reports) |

**None of these block merge.** They're cosmetic; `compileall` and `pytest` both pass with them present; offscreen smoke runs end-to-end.

Cleanup expected cost: **1 small commit** removing items 1-6 (10-15 LOC delta) + **1 submodule bump commit** for item 7. Both are bounded surgical operations.

### 4.3 Phase-3D-specific items intentionally NOT cleaned up

  - **Operationally-semantic inline chrome** — preserved per B6 carve-out documented in Step 4-7 reports:
      - `CommonsDropZone` dashed border (drop-affordance signal)
      - Recent-commits per-row `#card` background frame (calm content card)
      - Sync-card detail rows per-status colour codes (`?`, `D`, `A`, `R`, `M`)
      - TodoItem strikethrough on done (semantic affordance)
      - Branch sub-label muted-colour inline style
      - Various `text_sub`/`text_muted` inline label colours (semantic content text colour, not chrome)
  - **`load_tool()` runtime status-sentence emoji glyphs** (`📝 ⬆ ⬇ ✓ ⚠`) — these sit INSIDE the QPlainTextEdit terminal output surface, not on chrome. Per Step 7 report §4 — terminal-style output is a calm surface for whatever the runtime decides to print.

---

## 5. Merge readiness determination

### 5.1 Verdict: **A — Merge-ready as-is.**

The Phase 3D retrofit branch (`phase-3d-pcc-detail-retrofit` HEAD `390df84`) is merge-ready immediately. All Phase 3D steps shipped, all reports landed, all validation green, all invariants preserved.

The 6 dead-import / dead-helper items + the submodule lag (§4.2) are not merge blockers — they're optional follow-on cleanups that mirror Phase 3C's `a1b45d3` precedent and would land best as a single small post-merge consolidation commit on `main` (same pattern as Phase 3C's `060d08c` + `a1b45d3` post-merge cleanup pair).

### 5.2 Why not B

"Merge-ready after tiny cleanup" (Option B) would mean landing the cleanup as a commit on the retrofit branch before merge. That's also viable, but Phase 3C established the cleaner convention: keep the retrofit branch's per-step commits semantically focused (each step does its work, nothing more), then consolidate inert orphans in a separate post-merge commit. Mirroring that convention keeps the Phase 3D history bisect-friendly and the merge atomic.

### 5.3 Why not C

No blockers identified. No major visual mismatch. No runtime instability. No layout instability. No action-routing regressions. No semantic inconsistencies. Scope is stable (no creep into Step 8, no Phase 3E creep).

---

## 6. Exact merge execution plan

Mirrors the Phase 3C closure sequence (per `PHASE_3C_FINAL_MERGE_REPORT.md` + MIGRATION_RULES § Per-retrofit branch + PR convention).

### 6.1 Sequence — PCC repo (`phoenix-command-center`)

```powershell
# 1. Confirm pre-merge state
Set-Location C:\Users\justing\PycharmProjects\phoenix-command-center
git status --short                                 # → empty
git branch --show-current                          # → phase-3d-pcc-detail-retrofit
git log main..phase-3d-pcc-detail-retrofit --oneline  # → the 6 step commits

# 2. Push retrofit branch to origin (currently local-only)
git push -u origin phase-3d-pcc-detail-retrofit

# 3. Checkout main + verify
git checkout main
git status --short                                 # → empty
git log -1 --oneline                               # → a1b45d3 cleanup or whatever main currently tips

# 4. Merge --no-ff with explicit merge message
git merge --no-ff phase-3d-pcc-detail-retrofit -m "Merge Phase 3D — PCC detail panel modernization

Phase 3D landed the detail-panel modernization in 6 commits on
phase-3d-pcc-detail-retrofit (off main at a1b45d3):

  03fdfa3 Step 1 — Top utility band restructure
  30a9333 Step 2 — Detail panel aggregate tiles (StatTile → AggregateTile)
  25c4154 Step 4 — Overview tab modernisation (SyncStatusCard + Recent Commits)
  50d5142 Step 5 — TODOs tab modernisation (TodoItem + summary)
  83fada8 Step 6 — Git tab modernisation (buttons + terminal output)
  390df84 Step 7 — Files tab cohesion pass (CommonsDropZone Lucide)

Step 3 (action button migration) was folded into Steps 1 + 6.
Step 8 (keyboard shortcuts) deferred indefinitely per spec §7.

Spec: phoenix-commons/docs/ui-platform-baseline-v1/PCC_DETAIL_PANEL_SURFACE_SPEC_V1.md
Per-step reports: PCC_DETAIL_PANEL_IMPLEMENTATION_STEP_{01,02,04,05,06,07}_REPORT.md
Closure: PHASE_3D_FINAL_MERGE_GATE_REPORT.md
"

# 5. Verify merge commit shape
git log -1                                          # → merge commit with both parents
git log --merges -1                                 # → same; confirms --no-ff worked
```

### 6.2 Post-merge consolidation commit (optional but recommended — mirrors Phase 3C `060d08c` + `a1b45d3`)

```powershell
# Single commit removing the §4.2 cleanup-eligible items + bumping submodule
git -C commons fetch origin
git -C commons checkout main
git -C commons reset --hard origin/main          # → 21238f0 commons main HEAD

# Then in PCC, remove dead items (one editor session, ~15 LOC delta):
#   - delete _sec() function (detail_panel.py:65-68)
#   - remove QPushButton from line 12 imports
#   - remove QMimeData, QUrl, QModelIndex from line 17 imports
#   - remove QCursor from line 18 imports
#   - remove STATUS_COLOR from line 29 import
#   - remove inline QSplitter::handle setStyleSheet at detail_panel.py:701
#     (theme.py overlay already styles it)

git add commons detail_panel.py
git commit -m "Cleanup: remove Phase 3D inert orphans + bump commons (post-merge)

- Drop _sec() helper (retired in Step 4)
- Drop dead imports (QPushButton, QMimeData, QUrl, QModelIndex,
  QCursor, STATUS_COLOR)
- Drop redundant inline QSplitter::handle stylesheet — theme.py
  overlay already styles it
- Bump commons submodule: 0fb6a0e → 21238f0 (Step 6 + Step 7
  report files; no commons source change)

Mirrors Phase 3C's post-merge cleanup pattern (a1b45d3).
"
```

### 6.3 Tag

```powershell
git tag pcc-phase-3d-merged-v2.1.0 HEAD~1     # tag on the merge commit, not the cleanup commit
# (if no cleanup commit: git tag pcc-phase-3d-merged-v2.1.0 HEAD)
```

**Tag rationale:** Phase 3C tagged `pcc-phase-3c-merged-v2.0.0` on the merge commit. PCC is unpackaged (no version.py-driven release), so the tag is purely operational/forensic. `v2.1.0` claims "detail panel modernization" as a new minor (since `v2.0.0` claimed "dashboard modernization"). Tag stays on the `--no-ff` merge commit per Phase 3C precedent so a single `git revert -m 1 <tag>` could roll back the whole phase if needed.

### 6.4 Push

```powershell
git push origin main
git push origin pcc-phase-3d-merged-v2.1.0
# Retrofit branch already pushed in step 2.6.1
```

### 6.5 Governance — MIGRATION_RULES status row

Add the Phase 3D row to `MIGRATION_RULES.md` § Migration order (between 3C and 8a). Template (mirrors Phase 3C's row):

```markdown
| **3D** | Phoenix Command Center — Detail Panel | `phase-3d-pcc-detail-retrofit` | ✅ Merged 2026-05-21 (merge commit `<sha>` on `phoenix-command-center:main`, post-merge consolidation `<sha>`). Retrofit work: Steps 1, 2, 4, 5, 6, 7 across 6 commits delivering the detail-panel modernization (top utility band + AggregateTile migration + Overview / TODOs / Git / Files tab Panel-wrap + Lucide cohesion). Step 3 folded into Steps 1+6; Step 8 deferred indefinitely. Tag `pcc-phase-3d-merged-v2.1.0` on the merge commit. Retrofit branch preserved on origin per MIGRATION_RULES § Per-retrofit branch + PR convention. PCC keeps orange + teal `BrandProfile` per ADR-016. Reports under this directory: `PCC_DETAIL_PANEL_SURFACE_SPEC_V1`, `PCC_DETAIL_PANEL_IMPLEMENTATION_STEP_01/02/04/05/06/07_REPORT`, `PHASE_3D_FINAL_MERGE_GATE_REPORT`, `PHASE_3D_FINAL_MERGE_REPORT`. |
```

This row, plus a small commit in commons adding it, closes the governance loop. The commit message:

```
Update MIGRATION_RULES — Phase 3D PCC detail-panel merged

Add Phase 3D row to § Migration order table. Mirrors Phase 3C row
format. Phase 3D shipped 6 of 8 spec steps (Step 3 folded into
Steps 1+6, Step 8 deferred indefinitely).
```

### 6.6 Pre-merge frozen-build check — N/A for PCC

Per `CLAUDE.md`: PCC is unpackaged (no installer, no auto-updater, source-run only). The Phase 3C frozen-build observation step does not apply to Phase 3D since the underlying tool is the same. Source-mode validation (§3.2 above) is the only runtime gate.

### 6.7 Rollback path (single command, if needed)

```powershell
git revert -m 1 <merge-sha>
```

The `--no-ff` merge commit preserves the entire Phase 3D commit history as a side branch; reverting the merge commit cleanly drops the phase without losing forensic detail.

---

## 7. Recommended Phase 3E timing

### 7.1 Phase 3D does not automatically schedule Wave 8a

Per MIGRATION_RULES § Frequency limits:

| Wave | Cadence rule |
|------|--------------|
| Wave 8a (ValveMaster) | At least 2 weeks **after** the prior other-tool retrofit's merge. |
| Wave 8b (Job Tracker) | At least 2 weeks after Wave 8a's merge. |

**Phase 3D's merge does not start Wave 8a.** Wave 8a remains **operator-gated**. The doctrine sets a *cooldown floor*; it does not authorise the next retrofit on its own.

Cooldown floor for Wave 8a, measured from the prior other-tool retrofit's merge:

  - Phase 3B (Phoenix Checkout) merged **2026-05-19** per MIGRATION_RULES § Migration order.
  - Doctrinal cooldown = 14 days.
  - Earliest doctrinal date for Wave 8a to open = **2026-06-02**.
  - Today is 2026-05-22; the cooldown floor is therefore **~11 days out**, not past.

Phase 3D is a PCC-side modernization (same tool as Phase 3C). Per the doctrine's "other-tool" framing, Phase 3D's merge does **not** reset the Wave-8a clock — but it also does **not** advance it. The 14-day floor still attaches to Phase 3B's date.

### 7.2 Phase 3E — none scheduled

Phase 3D's spec scope was the **detail panel**. With it shipped + closed, future PCC-side polish candidates exist (Commons Browser modernization, Settings dialog, New Tool Wizard, About dialog) but **none are scheduled.** Each would be opened only on explicit operator decision.

### 7.3 Recommendation

  - **Immediate:** execute the §6 merge plan on operator approval.
  - **Wave 8a:** remains operator-gated. The doctrinal cooldown floor (≥ 2026-06-02) gives the earliest defensible open date; opening on or after that date is the operator's call.
  - **Phase 3E:** not scheduled. Opening is the operator's call.
  - **No new architecture changes scheduled.** Commons API is stable; BrandProfile is stable; ADR-016 + ADR-014 + ADR-015 all hold.

---

## 8. Confirmation

  - **No implementation work occurred in this closure session.** All Phase 3D source changes landed in the 6 step commits before this gate report. This session only audited + validated + wrote the gate report.
  - **No architecture changes occurred.** No new ADR. No commons API change. No new commons widget. `BrandProfile` unchanged. ADR-016 / ADR-014 / ADR-015 all hold.
  - **No production deployment occurred.** PCC is unpackaged; no installer was built; no `dist/` artifact; no GitHub Release. The 6 retrofit commits live on the local `phase-3d-pcc-detail-retrofit` branch (not yet pushed to origin — that's the first step of the §6 merge plan).
  - **No production tool source touched.** Phoenix CAD / Phoenix Checkout / Project Tracking Tool / ValveMaster all unmodified throughout Phase 3D.
  - **No Phase 3E work was done.** Phase 3D scope was the detail panel; closure preparation does not expand scope.
  - **No new commons icons added in this session.** Step 7 used existing `arrow-up` + `check`. Commons main HEAD is `21238f0` (Step 7 report only).

---

## Appendix — Phase 3D commit graph

```
phase-3d-pcc-detail-retrofit:
  390df84 Files tab cohesion pass — CommonsDropZone Lucide (Phase 3D Step 7)
  83fada8 Git tab modernisation — buttons + terminal output (Phase 3D Step 6)
  50d5142 TODOs tab modernisation — TodoItem + summary (Phase 3D Step 5)
  25c4154 Overview tab — SyncStatusCard + Recent Commits modernised (Phase 3D Step 4)
  30a9333 Detail panel aggregate tiles — StatTile → AggregateTile (Phase 3D Step 2)
  03fdfa3 Detail panel top utility band restructure (Phase 3D Step 1)
  a1b45d3 ← branch base (Phase 3C cleanup commit on main)

main:                                       commons (sibling) main:
  a1b45d3 (Phase 3C cleanup)                 21238f0 Add PCC_DETAIL_PANEL_..._STEP_07_REPORT
  060d08c (post-3C submodule consolidate)    a514d8e Add PCC_DETAIL_PANEL_..._STEP_06_REPORT
  058a67a (merge Phase 3C)                   0fb6a0e icons: add arrow-down + arrow-up
  e4eb528 (Phase 3C tip B15)                 7f1618d Add PCC_DETAIL_PANEL_..._STEP_05_REPORT
                                             580130b icons: add pin
                                             d1eae2f Add PCC_DETAIL_PANEL_..._STEP_04_REPORT
                                             cc7d34c Add PCC_DETAIL_PANEL_..._STEP_02_REPORT
                                             2c72f22 icons: add clock
```

Net change vs `a1b45d3`:
  - `commons` submodule pointer: +1 line (lag 2 docs commits)
  - `detail_panel.py`: +786 / −204 (the modernization deltas)
  - `theme.py`: +20 (`#gitOutput` QSS rule)
  - Total: 3 files touched on the PCC side.

---

*End of report. Phase 3D is merge-ready. Merge execution pending operator approval per §6.*
