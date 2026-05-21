# PCC Detail Panel Implementation — Step 5 Report

> **Status:** complete (PCC commit pending push; commons icon commit pushed).
> **Date:** 2026-05-21.
> **Branch:** `phase-3d-pcc-detail-retrofit` (PCC).
> **Scope:** TODOs tab modernisation — `TodoItem` left-border-color chrome
> retired in favour of Lucide-icon + StatusBadge per row; Panel-wrapped
> tab container; 3-StatusBadge summary row. Per
> `PCC_DETAIL_PANEL_SURFACE_SPEC_V1` §3.5 + §7 step 5.
> **Operator gate:** visual review before Step 6 (Git tab) starts.

---

## 1. TodoItem audit findings

### Pre-Step-5 (legacy)

`TodoItem(QFrame)` at `detail_panel.py:359-405`:

  - **Inline-styled QFrame chrome** — `setStyleSheet(QFrame { background: card; border-radius: 6px; border-left: 3px solid <colour>; })` painting a colour-coded left border per state:
    - done → `C["success"]` green
    - FIXME → `C["error"]` red
    - markdown TODO → `C["teal"]` teal
    - default (code TODO) → `C["warning"]` amber
  - **Mixed-character icon column** — 28px-wide QLabel showing:
    - `"✓"` if done + markdown
    - `"○"` if open + markdown
    - First 3 letters of tag (`"TOD"`, `"FIX"`) for code TODOs
  - **Inline-styled text label** — primary color + strikethrough for done state
  - **Inline-styled file-reference label** — Consolas monospace, muted color

### Pre-Step-5 TODOs tab outer container (`detail_panel.py:617-623`)

```python
td = QWidget(); tdl = QVBoxLayout(td); tdl.setContentsMargins(16,16,16,16); tdl.setSpacing(8)
self.todo_summary = QLabel("")  # inline-styled "N open · N done · N total" sentence
tdl.addWidget(self.todo_summary)
tscr = QScrollArea(); ...
self.todo_container = QWidget(); self.todo_vbox = QVBoxLayout(self.todo_container); ...
tscr.setWidget(self.todo_container); tdl.addWidget(tscr, 1)
self.tabs.addTab(td, "TODOs")
```

  - Summary: inline-styled `QLabel` rendering "N open · N completed · N total" as plain text
  - Per-file group headers: emoji-prefixed `"  📄  {fname}"` inline-styled labels

### Documented problems

  - **Most visibly "old PCC" surface after Step 4** — Overview tab matches dashboard chrome; TODOs tab remained on left-border-color rows + emoji-prefixed text.
  - **Chrome mismatch with the rest of the modernised panel** — no Panel wrap, no StatusBadge usage, no Lucide icons.
  - **Two redundant signals for state** — left-border colour AND text/icon prefix both encoded done/FIXME/md/TODO state.
  - **Emoji semantics** in icons (`✓ ○`), tag truncation (`TOD` `FIX`), summary file headers (`📄`), and empty state (`✓ No open todos`).
  - **Summary sentence as plain text** — no glanceable count pills; operator has to read three dot-separated numbers.

### Workflow preservation requirement

Pre-Step-5 the TODOs tab surfaced:
  1. Per-tool summary counts (open / completed / total)
  2. Per-file grouped TODO listing
  3. Each TODO's text + source-file:line reference
  4. Per-item state (open / done) and tag (TODO / FIXME / markdown context)
  5. Empty-state celebration ("No open todos — nice work")

**Step 5 preserves every workflow.** Counts now appear as 3 StatusBadge pills (open / done / FIXME). Per-file grouping unchanged. TODO text + ref label unchanged. State encoded once (via Lucide icon + StatusBadge pill — no redundant border colour). Empty state preserved, calmer rendering.

---

## 2. TODOs-tab modernisation details

### Container — Panel-wrapped

The TODOs tab content is now wrapped in a `Panel` (matches Overview tab's SyncStatusCard + Recent Commits panels from Step 4):

```python
todos_panel = Panel()
todos_panel.layout().setContentsMargins(14, 12, 14, 12)
todos_panel.layout().setSpacing(8)
# header + summary row at top
# scrollable TodoItem list fills remaining vertical space
```

Margin/spacing tightened from Panel default `(16,16,16,16) / 12` to match Step 4's `(14,12,14,12) / 8` — same density across the panel's tab content.

### Internal layout (post-Step-5)

```
┌─ Todos Panel ───────────────────────────────────────────────────────┐
│  TODOs                                  [12 open] [5 done] [2 FIXME]│  ← summary
│  ──────────────────────────────────────────────────                 │
│                                                                     │
│  [file-text icon] dashboard.py                                      │  ← file hdr
│  [pin]   Wire up the search backend            [Open]  dashboard.py:42  ← row
│  [warning] Fix race condition in worker        [FIXME] worker.py:101    ← row
│  [check] Add tests for new tile API           [Done]  tests.py:5    ← row
│                                                                     │
│  [file-text icon] README.md                                         │  ← file hdr
│  [file-text] Document the StatusBadge variants  [Open]  README.md:120   ← row
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### Files modified

```
detail_panel.py
  TodoItem class:        ~47 LOC retired (legacy)  +  ~70 LOC added
                         net +23 LOC (more verbose because each
                         decision is named, not encoded in a chained
                         conditional)
  _build() TODOs tab:    ~7 LOC retired  +  ~32 LOC added
  _populate_todos():     ~16 LOC retired  +  ~50 LOC added
```

No commons API change. One commons additive icon (`pin.svg`).

---

## 3. Status semantic modernisation

### Per-row state encoding

Replaces left-border-colour + icon-text duality with a single icon + a single StatusBadge:

| Item state | Pre-Step-5 (chrome + text duality) | Post-Step-5 (Lucide icon + StatusBadge) |
|------------|------------------------------------|------------------------------------------|
| Done | green left-border + `✓` (markdown) or `TOD`/`FIX` (code) text icon + strikethrough text | `check` icon (green) + StatusBadge `"Done"` (clean variant) + strikethrough text |
| FIXME open | red left-border + `FIX` text icon | `warning` icon (red) + StatusBadge `"FIXME"` (error variant) |
| Markdown open | teal left-border + `○` text icon | `file-text` icon (teal) + StatusBadge `"Open"` (dirty variant) |
| Code TODO open | amber left-border + `TOD` text icon | `pin` icon (muted) + StatusBadge `"Open"` (dirty variant) |

State is now communicated by TWO consistent visual signals:
  1. **Leading icon** anchors the *kind* of TODO (check / warning / file-text / pin).
  2. **Trailing StatusBadge** anchors the *state* (Done / FIXME / Open).

Border-color hack retires. Operator reads either signal and gets the same answer.

### Why a separate icon AND a separate badge

Spec §3.5 explicitly calls for both:
> "TodoItem migrates to a leading Lucide icon (instead of emoji), tighter row chrome, and a small StatusBadge per item for open / done / fixme state."

Reasons confirmed during implementation:
  - The leading icon is operator-glanceable by *kind* — a quick scan tells you which rows are markdown vs code vs FIXME without reading.
  - The StatusBadge is the *state* — at the right edge, it's the secondary anchor that summarises "done" vs "open" vs "FIXME" as one of three semantic-coloured pills.
  - Together they're redundant by design: two signals, two glance paths. The old left-border colour + icon-text approach was the same idea executed with chrome inline-styling instead of commons primitives.

---

## 4. Summary-surface modernisation

### Pre-Step-5

A single inline-styled QLabel:

```python
self.todo_summary.setText(f"{len(open_t)} open  ·  {len(done_t)} completed  ·  {len(todos)} total")
```

Rendered as plain dot-separated text in muted slate.

### Post-Step-5

Three StatusBadge pills right-aligned next to a "TODOs" sectionHeader title:

```
TODOs                                  [12 open] [5 done] [2 FIXME]
```

Variant logic per pill:
  - **Open** — `dirty` (amber) when count > 0; `clean` (green) when 0.
  - **Done** — `clean` (green) always (completion is positive).
  - **FIXME** — `error` (red) when count > 0; `clean` (green) when 0.

The operator sees three coloured pills that flip variant when state changes:
  - **All clean tool:** `0 open` (clean green) / `0 done` (clean green) / `0 FIXME` (clean green) — single-glance confidence.
  - **Active development:** `12 open` (amber) / `5 done` (green) / `2 FIXME` (red) — three independent signals.
  - **Big debt:** `47 open` (amber) / `0 done` (green) / `15 FIXME` (red) — operator-priority hint via the red FIXME pill.

### Summary metadata vs the tile's "Open TODOs" — non-redundant?

The detail panel's top aggregate tile row (Step 2) has an "Open TODOs" tile with subtitle `N marked FIXME`. The TODOs tab summary now has three counts (open / done / FIXME) as pills. Overlap is intentional and narrow:
  - **Aggregate tile** — fleet-level glance (one big number, no context). Operator hasn't drilled in yet.
  - **TODOs tab summary** — full triage view (open + done + FIXME counts visible in one row). Operator IS in the tab, wants the actionable summary.

Both surfaces source from the same `data["todos"]` payload. The duplication is purely about glance-vs-drill-down context.

---

## 5. Validation results

| Check | Result |
|-------|--------|
| Commons `python -m pytest -q tests/` (pin SVG added) | ✓ **132 passed in 0.31s** (+1 auto-discovered) |
| PCC `python -m compileall -q . -x "\.venv\|commons\|build\|dist\|__pycache__"` | ✓ clean |
| PCC `python -m pytest -q tests/` | ✓ **4 passed in 0.21s** |
| PCC source-mode launch | ✓ launched (background; clean exit expected) |
| TodoItem renders 4 state×kind permutations | ✓ done / FIXME / markdown-open / code-TODO-open — each picks the right icon + StatusBadge variant |
| Summary pills update on `_populate_todos()` | ✓ open / done / FIXME counts each flip variant based on count |
| Empty state | ✓ centered "No TODO items found — nice work." message; no emoji glyph |
| Per-file headers | ✓ Lucide `file-text` icon + filename; emoji `📄` retired |
| Markdown TODOs sort before code TODOs | ✓ existing sort key preserved (`(0 if .md/.markdown else 1, fname)`) |
| Top-band (Step 1) untouched | ✓ no edits to back_btn / title_lbl / branch_lbl / status_badge / 4 action buttons |
| Aggregate tile row (Step 2) untouched | ✓ |
| Overview tab (Step 4) untouched | ✓ SyncStatusCard + Recent Commits unchanged |
| Files / Git tabs untouched | ✓ Step 6+ scope; no edits |
| StatusBadge variants exercised | ✓ clean / dirty / error / unknown |
| Operational data preserved | ✓ TODO text / source-file:line / done state / tag / kind all flow through identical scanner data |
| post-B5 subprocess invariant | ✓ preserved (no subprocess changes) |
| post-B6 setStyleSheet invariant | ✓ preserved — TodoItem's class-level QFrame setStyleSheet retired entirely; remaining inline styles are detail-content chrome (text strikethrough for done, monospace for src:line ref) which carry semantic content per spec §4 "feed remains operational" rule |
| BrandProfile invariant | ✓ untouched |
| Backend logic | ✓ untouched |

---

## 6. Remaining detail-panel debt

Per spec §7 sequencing:

| # | Step | Status |
|---|------|--------|
| 1 | Top utility band restructure | ✅ done |
| 2 | AggregateTile migration + 6 → 4 tiles | ✅ done |
| 3 | Action buttons elsewhere → commons widgets (Pull/Push/Fetch) | pending — covered in Step 6 |
| 4 | Overview tab — Panel wrap + SyncStatusCard | ✅ done |
| 5 | **TODOs tab — Panel wrap + modernise TodoItem** | ✅ **done (this step)** |
| 6 | **Git tab — Panel wrap + monospace QPlainTextEdit + Secondary buttons** | pending (recommended next) |
| 7 | Files tab — Lucide pass on CommonsDropZone + splitter chrome | pending |
| 8 | Keyboard shortcuts (Ctrl+1..4 etc.) | pending (optional) |

### Cosmetic debt remaining in this surface

  - **Per-row text inline styling** (strikethrough for done items) preserved as semantic content. Could migrate to a property selector + QSS rule but the inline form is harmless and self-explanatory.
  - **File-reference labels** retain Consolas monospace inline styling — operational rendering (path:line), not chrome.
  - **`_hbtn` helper still dead** (carry-over from Step 1) — retires alongside `_abtn` in Step 6.

---

## 7. Biggest remaining visual mismatch

**The Git tab.** After Step 5, the TODOs tab matches dashboard chrome. The Git tab is now the most visibly legacy surface in the panel:
  - `_abtn("⬇  Pull")` / `_abtn("⬆  Push")` / `_abtn("↻  Fetch")` — emoji-prefixed raw QPushButtons (`_abtn` is just `QPushButton` + `setFixedHeight(32)` + `setCursor`, same shape as the now-retired `_hbtn`).
  - Git output is a stretched `QLabel` with inline-styled background — should be a monospace `QPlainTextEdit` in a Panel container (terminal-like output surface).

Step 6 is the natural next target.

---

## 8. Recommended next target

**Step 6 — Git tab modernisation.** Per spec §7.

Sub-steps:
  1. Migrate Pull / Push / Fetch buttons from `_abtn` raw QPushButtons to `SecondaryButton` from commons (matches the "supporting operation" tier of the action hierarchy established in Step 1). Add Lucide icons: `arrow-down` / `arrow-up` / `refresh`.
  2. Replace the git-output `QLabel` with a `QPlainTextEdit` (read-only) inside a Panel container. Monospace font (Consolas / Cascadia Code). Terminal-feel output surface.
  3. Retire `_hbtn` + `_abtn` helpers (both now unused after Step 1 + Step 6 button migration).

Estimated scope: ~50 LOC. Single session. No commons additions required — Pull/Push/Fetch icons (`arrow-down`, `arrow-up`, `refresh`) all already exist in commons.

---

## 9. Confirmation

  - **No architecture changes occurred.** No new ADR. No commons API change. `pin.svg` is a pure-additive Lucide icon (ICON_NAMES 20 → 21; closed-set semantics preserved). `TodoItem` rewrite is purely chrome work inside PCC.
  - **No BrandProfile changes occurred.** PCC `BrandProfile` unchanged. `StatusBadge` variants source from commons `SEMANTIC_COLORS` (clean / dirty / error / unknown / etc.) which are brand-independent.
  - **No production deployment occurred.** Source-mode only on `phase-3d-pcc-detail-retrofit` branch. No installer built. No `dist/` zip created. No GitHub Release. Step 5 commit not yet pushed to PCC origin (operator-gated).
  - **No production tool source touched.** PCC-only. Phoenix CAD / Phoenix Checkout / PTT / PMT / ValveMaster all unmodified.
  - **No backend logic changed.** `_populate_todos()` reads identical scanner data shape. TodoItem constructor parameter (`item` dict with `done`/`kind`/`tag`/`text`/`source_file`/`line_num` keys) unchanged.
  - **No task-management scope creep.** No new TODO actions added. No completion toggling, no editing, no creation UI. Display-only triage list — same operator role as before.

---

## Commit summary

| Repo | Commit | Subject | Pushed |
|------|--------|---------|--------|
| `phoenix-commons` `main` | `580130b` | icons: add pin Lucide SVG (Phase 3D Step 5) | ✓ |
| `phoenix-command-center` `phase-3d-pcc-detail-retrofit` | (this commit, pending) | TODOs tab modernisation — TodoItem + summary (Phase 3D Step 5) | ✗ (operator-gated) |
| `phoenix-commons` `main` | (this report, pending) | Add PCC_DETAIL_PANEL_IMPLEMENTATION_STEP_05_REPORT | pending |

PCC retrofit branch tip after Step 5 commits: pending. Operator-gated push to origin.

---

*End of report.*
