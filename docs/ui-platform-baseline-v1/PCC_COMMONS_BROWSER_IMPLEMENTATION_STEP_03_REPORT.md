# PCC Commons Browser Implementation — Step 3 Report

> **Status:** complete (PCC commit on retrofit branch, pending operator
> review + push).
> **Date:** 2026-05-22.
> **Branch:** `phase-3e-pcc-commons-browser-retrofit` (PCC).
> **Scope:** Final cohesion pass — Rescan button → `TertiaryButton`,
> redundant inline `QSplitter::handle` QSS retired, header spacing
> tightened to match detail-panel rhythm, dead imports removed.
> Per `PCC_COMMONS_BROWSER_SURFACE_SPEC_V1` §3.1 + §3.6 + §7 step 3.
> **Operator gate:** visual review before Phase 3E merge-gate
> preparation opens.

---

## 1. Final audit findings

### Post-Step-2 state surveyed

After Steps 1 + 2 landed, `commons_browser.py` carried these remaining
chrome-debt items:

| Line | Issue | Severity |
|------|-------|----------|
| 185-189 | Rescan as raw `QPushButton#ghostBtn` instead of commons primitive | medium — visible button tier |
| 218 | Inline `QSplitter::handle` `setStyleSheet` redundant with theme.py overlay | low — chrome duplication |
| 12 | `QSizePolicy` import unused | trivial — dead import |
| 15 | `QCursor` import used only for setting hand cursor on the soon-retired rescan QPushButton | trivial — dead after Rescan migration |
| 10 | `QPushButton` import used only for the rescan QPushButton | trivial — dead after Rescan migration |
| 176-182 | No spacing between `pageTitle` and `status_lbl` in the header `QHBoxLayout` | minor — tightness when status populates |
| 181 | `status_lbl` inline stylesheet (`f"color: {C['text_muted']}; font-size: 11px;"`) | preserved — semantic content text, B6 carve-out |

### Items intentionally NOT classified as debt

  - **`status_lbl` inline stylesheet** — semantic content text colour (operational transient label), not chrome. Same B6 carve-out the detail panel uses for muted info labels (sync-card status sentence, dirty-file count text, etc.). Per spec §4 the status label stays a calm QLabel — NOT promoted to a StatusBadge.
  - **`UsageFooter` placeholder QLabel inline stylesheet** (line 152, set in `show_placeholder`) — same B6 carve-out for semantic content text. Already documented in Step 2 report.
  - **Root layout margins/spacing** (`24, 20, 24, 20` margins + `14` spacing on line 172-173) — matches Phase 3C dashboard rhythm; left unchanged.
  - **chip_row `setSpacing(8)`** — matches dashboard convention; left unchanged.
  - **QSplitter default sizes `[320, 720]`** — operationally correct (tree-narrow / viewer-wide); left unchanged.
  - **`setHandleWidth(2)`** — Phoenix convention for narrow splitter handles; left unchanged.

### Items deferred to closure phase (Step 4)

  - **Submodule pin** — currently lags 2 commons commits behind (Step 2 + Step 3 reports). Closure-phase post-merge consolidation will bump per the Phase 3D precedent.

---

## 2. Splitter chrome cleanup details

### Removed

```python
spl.setStyleSheet(f"QSplitter::handle {{ background: {C['border']}; }}")
```

### Why redundant

PCC `theme.py` overlay at lines 601-607 already provides:

```css
QSplitter::handle {
    background: border;
}
QSplitter::handle:hover {
    background: border_hi;
}
```

The inline rule was strictly redundant — and *missing* the hover state. After removal, the splitter handle reads cleaner (subtle hover transition on the handle now works correctly).

### Mirrors Phase 3D precedent

Phase 3D's post-merge consolidation commit (`d466202`, "Cleanup: remove Phase 3D inert orphans + bump commons (post-merge)") landed the same one-line removal for the detail-panel Files-tab splitter. This step mirrors that pattern.

### Preserved unchanged

| Attribute | Value |
|-----------|-------|
| Orientation | `Qt.Horizontal` |
| Handle width | `2` |
| Default sizes | `[320, 720]` (tree-narrow / viewer-wide) |
| Tree pane (left) | `QTreeView` + `QFileSystemModel` |
| Right pane | `FileViewer` + `UsageFooter` stacked |
| Drag-handle interaction | Qt default (preserved) |

---

## 3. Rescan button migration details

### Before

```python
self.refresh_btn = QPushButton("  Rescan")
self.refresh_btn.setObjectName("ghostBtn")
self.refresh_btn.setIcon(icon("refresh", color=C['text_sub']))
self.refresh_btn.setIconSize(QSize(14, 14))
self.refresh_btn.setCursor(QCursor(Qt.PointingHandCursor))
self.refresh_btn.clicked.connect(self.refresh_requested)
```

  - Raw `QPushButton` with PCC-specific `ghostBtn` object name (which theme.py overlay styles as outline-ghost via lines 323-335).
  - Manual `setCursor(QCursor(Qt.PointingHandCursor))` because the raw QPushButton doesn't set a hand cursor by default.
  - 6-line construction (5 LOC + connect).

### After

```python
self.refresh_btn = TertiaryButton("Rescan")
self.refresh_btn.setIcon(icon("refresh", color=C['text_sub']))
self.refresh_btn.setIconSize(QSize(14, 14))
self.refresh_btn.clicked.connect(self.refresh_requested)
```

  - Commons `TertiaryButton` — outline-tier button matching the detail panel's "Back" / "VS Code" / "GitHub" actions (Phase 3D Step 1).
  - Internal cursor handling — `TertiaryButton` sets its own hand cursor; no manual `setCursor` needed.
  - 4-line construction (3 LOC + connect). 2 LOC retired.

### Tier rationale

Per spec §3.1 + the candidate-audit ranking, Rescan is:

  - **NOT primary** — it's not the page's most-important action (the page's primary purpose is *inspection*, not *triggering scans*).
  - **NOT secondary** — it's not a destructive or critical operation (Pull / Push / Fetch on the detail panel are SecondaryButton because they MUTATE the remote).
  - **TERTIARY** — it's a supporting page-level action (re-run the scan) that the operator opt-in clicks when they want fresh data.

Matches the detail-panel pattern: outline-tier buttons are for navigation + inspection actions.

### Lucide icon preserved

`icon("refresh", color=C['text_sub'])` — unchanged from Phase 3C Step 1. No new icons added.

### refresh_requested signal contract preserved

```python
class CommonsBrowser(QWidget):
    refresh_requested = Signal()
    ...
    self.refresh_btn.clicked.connect(self.refresh_requested)
```

`main_window.py` calls `self.commons.refresh_requested.connect(self._on_commons_refresh)` — integration is unchanged because the signal is on `CommonsBrowser`, not on the button. Click → signal → main window → scanner kickoff flow works identically.

---

## 4. Header / status alignment decisions

### Spacing addition

Added `hdr.addSpacing(8)` between `pageTitle` and `status_lbl`. Justification:

  - Pre-Step-3: title and status label sat side-by-side with no gap, looking cramped when status populates ("Scanning usage across tools…" would touch the title's right edge).
  - Detail panel's Phase 3D Step 1 uses `addSpacing(4)` between the title and the branch sub-label (which is 13px text).
  - Commons Browser's status label is 11px text — slightly smaller. 8px gap provides equivalent visual breathing room at the smaller size.

This is the only spacing change in the whole step.

### Status label semantics

Per spec §4 — left as a calm muted `QLabel`:

```python
self.status_lbl = QLabel("")
self.status_lbl.setStyleSheet(
    f"color: {C['text_muted']}; font-size: 11px;"
)
```

  - **Not promoted to StatusBadge.** StatusBadge would over-decorate a transient single-line operational message. The label appears only during scans (~1-3 seconds total) and clears.
  - **Inline stylesheet retained** — B6 carve-out for semantic content text colour. The colour conveys "muted/transient/informational" (operational text), not chrome.
  - **No icon prefix.** A Lucide icon would suggest persistent state; the label is ephemeral.

### What was considered but rejected

  - **StatusBadge with `scanning` variant during scans.** Considered. Rejected because (a) the existing implementation already disables the Rescan button during scans — that's the operator-facing "scanning happening" signal, and (b) StatusBadge `scanning` variant is brand-accent (orange in PCC) and would compete with the page title for attention.
  - **Spinner icon next to the status label.** Considered. Rejected per spec §5 "no animations / no spinners — use sync pill variant instead." (And we chose not to use a pill, so no spinner either.)
  - **Larger gap between title and status (e.g. 16px).** Tested mentally. Rejected — would look like the status label belongs to the rescan-action cluster on the right rather than to the title on the left.

---

## 5. Spacing / cohesion changes

### Single targeted change

Only one spacing change landed in Step 3: the `hdr.addSpacing(8)` between page title and status label. (Documented in §4 above.)

### Things considered but NOT changed

| Attribute | Current value | Considered | Verdict |
|-----------|----------------|------------|---------|
| Root margins | `24, 20, 24, 20` | tighten to detail-panel's `20, 16, 20, 16`? | Keep — Commons Browser is a peer page (not a drilldown), wider margins read calmer |
| Root spacing | `14` | tighten to `12` to match detail panel exactly? | Keep — 14 between distinct top-level regions reads as appropriately spacious |
| chip_row spacing | `8` | tighten to `6`? | Keep — matches dashboard chip row convention |
| Header → chip_row gap | implicit (root spacing 14) | add explicit `addSpacing`? | Keep — root layout spacing handles it |
| chip_row → splitter gap | implicit (root spacing 14) | add explicit `addSpacing`? | Keep — root layout spacing handles it |
| QSplitter handle width | `2` | wider for easier dragging? | Keep — Phoenix convention; matches detail panel Files-tab |
| Right-pane spacing (FileViewer → UsageFooter) | `8` | tighten? | Keep — matches Phase 3D Files tab |

### Net spacing delta

Single addition: `hdr.addSpacing(8)`. Nothing else moved.

---

## 6. Validation results

| Check | Result |
|-------|--------|
| PCC `python -m compileall -q . -x "\.venv\|commons\|build\|dist\|__pycache__"` | ✓ clean (exit 0) |
| PCC `python -m pytest -q tests/` | ✓ **4 passed in 0.78s** |
| Offscreen smoke — Rescan is `TertiaryButton` (not raw QPushButton) | ✓ |
| Offscreen smoke — Rescan click fires `refresh_requested` signal | ✓ (1 fire registered) |
| Offscreen smoke — QSplitter inline `setStyleSheet` retired | ✓ (`styleSheet()` returns `""`) |
| Offscreen smoke — QSplitter `handleWidth` still 2 | ✓ |
| Offscreen smoke — dead imports removed (`QSizePolicy`, `QCursor`, `QPushButton`) | ✓ (none in source) |
| Offscreen smoke — `#ghostBtn` object name gone | ✓ |
| Offscreen smoke — Step 1 chip row preserved (4× StatusBadge) | ✓ |
| Offscreen smoke — Step 2 UsageFooter preserved (Panel + UsageFooter inheritance) | ✓ |
| Offscreen smoke — `set_usage` end-to-end (orphan variant flip) | ✓ |
| Offscreen smoke — `set_scanning` flow (status text + rescan enable/disable) | ✓ |
| Offscreen smoke — empty state reset | ✓ |
| Lucide `refresh` icon preserved | ✓ |
| `refresh_requested` signal contract unchanged | ✓ |
| `main_window.py` integration | ✓ no caller-side changes needed |
| `scanner.scan_commons_usage` integration | ✓ untouched |
| FileViewer | ✓ untouched |
| QTreeView + QFileSystemModel | ✓ untouched |
| QSplitter (orientation, sizes, handle width) | ✓ untouched |
| B5 invariant (subprocess CREATE_NO_WINDOW) | ✓ preserved (no subprocess calls touched) |
| B6 invariant (no widget-level setStyleSheet on commons primitives) | ✓ preserved — the only inline stylesheets remaining are the two B6 carve-outs (status_lbl and UsageFooter placeholder) for semantic content text |
| BrandProfile invariant | ✓ untouched. TertiaryButton consumes commons sentinel substitution — brand-independent outline tier |
| Theme.py | ✓ untouched (no new QSS rules required) |
| Diff scope | 1 file (`commons_browser.py`); +28 / −10 |

---

## 7. Remaining Commons Browser debt

Per spec §7 sequencing:

| # | Step | Status |
|---|------|--------|
| 1 | Summary chip row — `_Chip` → `StatusBadge` | ✅ done (`d0434b3`) |
| 2 | UsageFooter modernization — Panel + StatusBadge + Lucide | ✅ done (`77e5b45`) |
| 3 | **Tree/viewer/page cohesion pass — splitter + Rescan tier + spacing** | ✅ **done (this step, `d74e0bd`)** |
| 4 | Closure gate + merge | pending |

### Cosmetic debt remaining

  - **None on the Commons Browser surface.** All three implementation steps are complete.
  - **Submodule pin lag** (`commons` directory points at `91bbd45` from before Phase 3E reports; commons `main` is now at `6268800` + the upcoming Step 3 report commit). Closure-phase post-merge consolidation will bump per the Phase 3D `d466202` precedent.

### Inline `setStyleSheet` final count

After Step 3:

| Line | Call site | Status |
|------|-----------|--------|
| 169 (UsageFooter `show_placeholder`) | `lbl.setStyleSheet(f"color: ...muted... italic;")` | **B6 carve-out** — semantic content text colour |
| 199 (CommonsBrowser header `status_lbl`) | `self.status_lbl.setStyleSheet(f"color: ...muted; font-size: 11px;")` | **B6 carve-out** — semantic content text colour |

Both are the documented carve-outs for muted-content text colour (same pattern detail-panel uses for sync-card status sentences, dirty-file count labels, branch sub-labels, etc.). **No chrome-level inline stylesheets remain in the file.**

---

## 8. Phase 3E completion assessment

### What shipped across Steps 1–3

| Surface | Pre-Phase-3E | Post-Phase-3E |
|---------|---------------|----------------|
| Summary chip row | 4× local `_Chip(QLabel)` inline-styled | 4× `StatusBadge` compact pills (with semantic variant flips) |
| `_Chip` class | 20 LOC bespoke widget | retired entirely |
| UsageFooter container | Inline-styled `QFrame` | Commons `Panel` subclass |
| UsageFooter "USED BY" header | Hand-styled letter-spacing QLabel | `#sectionHeader` QLabel |
| UsageFooter per-tool chip | `◈ Tool Name` emoji-glyph inline pill | `[package Lucide]` + `StatusBadge(clean)` composed widget |
| UsageFooter orphan chip | `◇ ORPHAN — not referenced…` emoji-glyph inline pill | `[warning Lucide]` + `StatusBadge(warning, "Not referenced by any tool")` composed widget |
| UsageFooter overflow | None — pills would overflow horizontally | `QScrollArea` inside Panel handles overflow gracefully (10-pill stress-tested) |
| Rescan button | Raw `QPushButton#ghostBtn` + manual cursor | Commons `TertiaryButton` (matches detail-panel hierarchy) |
| Splitter chrome | Inline `setStyleSheet` redundant with overlay | Inline rule retired — theme.py overlay covers it globally + adds hover state |
| Header spacing | Title + status label flush together | `addSpacing(8)` between them (matches detail-panel pattern) |
| Dead imports | `QPushButton`, `QSizePolicy`, `QCursor` | All removed |
| Total `setStyleSheet` count | 12 (Step 0 baseline) | 2 (both B6 carve-outs for semantic content text) |
| Total file LOC | 240 (pre-Phase-3E) | 320 (+80 LOC, mostly comments documenting B6 carve-outs + per-state rationale) |

### Spec §7 sequencing — complete

  - Step 1 ✅
  - Step 2 ✅
  - Step 3 ✅
  - Step 4 (closure gate + merge) — operator-gated, pending

### Visible operator-facing changes

  1. **Orphan chip color flip** — orphans badge now flips green when count is 0 (Step 1).
  2. **UsageFooter chrome cohesion** — same Panel + StatusBadge vocabulary the dashboard and detail panel use (Step 2).
  3. **Many-users overflow handled gracefully** — no layout breakage with 10+ tool consumers (Step 2).
  4. **Rescan button tier alignment** — outline ghost button now reads as proper Tertiary tier in the page-action hierarchy (Step 3).
  5. **Header breathing room** — 8px gap between title and transient status label (Step 3).

### Invariants preserved

  - **B5** — subprocess CREATE_NO_WINDOW: no subprocess calls touched in this phase.
  - **B6** — no widget-level setStyleSheet on commons primitives: preserved across all 3 steps. The 2 remaining inline stylesheets are B6 carve-outs (semantic content text colour).
  - **BrandProfile** — orange + teal per ADR-016: untouched.
  - **Commons API stability** — no API change. No new primitives. No new icons.
  - **Scanner contract** — `scan_commons_usage` output shape unchanged.
  - **FileViewer** — untouched.
  - **QTreeView + QFileSystemModel** — untouched.
  - **`refresh_requested` signal** — unchanged.
  - **`main_window.py` integration** — unchanged.

---

## 9. Recommended merge-gate next step

**Phase 3E Step 4 — Closure gate.** Per spec §7 + §12.

Sub-steps (mirrors the Phase 3D closure pattern):

  1. **Holistic Commons Browser review** — exercise all states (empty / no path / placeholder / orphan / single user / multi-user / many-user) end-to-end, validate cohesion with dashboard + detail panel.
  2. **Surface completion audit** — confirm spec §7 1-3 shipped; confirm spec §8 forbidden items not done.
  3. **Runtime / stability validation** — compileall + pytest + source-mode launch sanity.
  4. **Merge readiness audit** — working tree clean, no dead imports, no abandoned helpers, no commons drift.
  5. **Merge recommendation** — A/B/C verdict.
  6. **Exact merge execution plan** — branch push + `--no-ff` merge + post-merge consolidation (submodule bump + any cleanup-eligible items) + tag (`pcc-phase-3e-merged-v2.2.0`) + push + MIGRATION_RULES governance row.
  7. **Phase 3F timing recommendation** — what (if anything) opens next.
  8. **Confirmation block** — no architecture changes, no BrandProfile changes, no production deployment, no scanner / Wave 8a / search backend work.

Output: `PHASE_3E_FINAL_MERGE_GATE_REPORT.md` under
`phoenix-commons/docs/ui-platform-baseline-v1/`.

Estimated effort: 1 session, mostly audit + report authoring; no
source changes expected unless a regression surfaces during the
review.

---

## 10. Confirmation

  - **No architecture changes occurred.** No new ADR. No commons API change. No new commons widget. `TertiaryButton` was already in the commons public API since Phase 3C. `Panel` and `StatusBadge` likewise. `BrandProfile` unchanged. ADR-014 / ADR-015 / ADR-016 all hold.
  - **No BrandProfile changes occurred.** PCC `BrandProfile` (orange + teal) unchanged. `TertiaryButton` consumes commons sentinel substitution — brand-independent outline tier.
  - **No production deployment occurred.** Source-mode only on `phase-3e-pcc-commons-browser-retrofit` branch. PCC is unpackaged. No installer built. No `dist/` artifact. No GitHub Release. Step 3 commit not yet pushed to PCC origin (operator-gated).
  - **No scanner changes occurred.** `scanner.scan_commons_usage` output shape, tool corpus building, keys/extensions heuristics — all unchanged.
  - **No search backend work occurred.** Search backend remains a deferred Phase 3F+ candidate per the candidate audit.
  - **No Wave 8a work occurred.** Wave 8a remains operator-gated (cooldown floor 2026-06-02).
  - **No production tool source touched.** Phoenix CAD / Phoenix Checkout / PTT / ValveMaster all unmodified.
  - **No tree / FileViewer / QFileSystemModel work occurred.** Workflow preserved verbatim.
  - **No Settings / Wizard / About / Push Preview work occurred.** Each remains a separate deferred candidate.
  - **No new commons primitives or icons added.** All primitives used were pre-existing post-Phase-3D.

---

## Commit summary

| Repo | Commit | Subject | Pushed |
|------|--------|---------|--------|
| `phoenix-command-center` `phase-3e-pcc-commons-browser-retrofit` | `d74e0bd` | Commons Browser cohesion pass — splitter + Rescan + spacing (Phase 3E Step 3) | pending (operator-gated) |
| `phoenix-commons` `main` | (this report, pending) | Add PCC_COMMONS_BROWSER_IMPLEMENTATION_STEP_03_REPORT | pending |

PCC retrofit branch tip after Step 3: `d74e0bd` (3 commits ahead of
`160270c` = post-Phase-3D CI-fix tip on `main`).

No commons source change in Step 3 — only this report file is added.

---

*End of report. Phase 3E implementation = complete. Step 4 (closure
gate) opens on operator approval.*
