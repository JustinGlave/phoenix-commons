# PCC Dashboard Implementation — Step 6 Report

> **Status:** complete.
> **Date:** 2026-05-21.
> **Scope:** Top utility band — page title, centered search shell
> (no backend), right-aligned sync-state pill. Per
> `PCC_DASHBOARD_SURFACE_SPEC_V1` §3.2 + §6.
> **Operator gate:** visual review of the new top band + Ctrl+K
> focus behavior before Step 7 (search backend) starts.

---

## 1. Utility-band architecture

Single horizontal band above the dashboard body. Three regions:

```
+----------------------------------------------------------------------------+
| Dashboard              [🔍 Search tools, commits, TODOs…] [Ctrl+K]   ● Scanning… |
+----------------------------------------------------------------------------+
| TOOLS / aggregate tile row                                                 |
| TOOLS panel  |  RECENT ACTIVITY panel                                      |
+----------------------------------------------------------------------------+
| status bar: N tools discovered · Last scan: HH:MM:SS                       |
+----------------------------------------------------------------------------+
```

| Region | Widget | Sizing | Purpose |
|--------|--------|--------|---------|
| Left | `QLabel#pageTitle` "Dashboard" | natural | Identifies the current page |
| Center | `QFrame#searchFrame` containing leading icon + `QLineEdit#dashboardSearch` + `QLabel#searchShortcutChip` | 380-540 px (min/max), 34 px tall, sandwiched between two `addStretch(1)`s so it drifts to the middle | Operator's command surface; ⌘K focuses it |
| Right | `StatusBadge` (sync pill) | natural | Primary scan-status indicator |

Composition lives in `Dashboard._build_top_band()`. The band sits as the first child of the dashboard's main `QVBoxLayout`, before the aggregate-tile row.

### Why a band and not a Panel

The Panel container is meant for *content* regions (tools section, activity feed). The utility band is *chrome* — operator-action affordances. Wrapping it in another Panel would visually nest two cards above the tile row, fighting the spec's "calm, restrained chrome" direction. Inline band layout with no border keeps the surface lighter than the dashboard body.

---

## 2. Search-shell implementation

### Widget composition (`Dashboard._build_search_frame`)

  - `QFrame#searchFrame` — the visual unit. Surface-tinted background, 1px border, 8px radius. Hover state lightens the border via QSS `:hover` selector.
  - Inside the frame (horizontal layout, 10/0/6/0 margins, 8 px spacing):
    1. Leading `QLabel` with a tinted `search` Lucide icon at 14×14 px.
    2. `QLineEdit#dashboardSearch` — borderless (`setFrame(False)`), transparent background, 13px text, info-blue selection. Placeholder: `"Search tools, commits, TODOs…"`. `returnPressed` connected to `_on_search_submit`.
    3. Trailing `QLabel#searchShortcutChip` rendering `"Ctrl+K"` in a small monospaced-feeling chip (1px border, btn_default background, 10px font-weight 600).

### Submission path

`returnPressed` → `Dashboard._on_search_submit()` → emits `search_submitted` signal with the trimmed query → `MainWindow._on_search_submitted(query)` → `statusBar().showMessage(f'Search: "{query}" — backend coming in Step 7', 5000)`.

Empty submissions are dropped before the signal fires (`if text:`), so accidental Enter presses don't surface noise.

### Explicit non-goals (Step 6)

  - No results panel.
  - No indexing.
  - No fuzzy matching.
  - No completion / autosuggest.
  - No keyboard navigation through results.
  - No command-palette execution.

Every one of those is Step 7 work and intentionally absent here.

---

## 3. Sync-pill implementation

A `phoenix_commons.widgets.StatusBadge` (the Step-2 primitive) in the right slot of the band. Public API on Dashboard:

```python
dashboard.set_sync_state(variant, label=None)
```

| Variant | Default label | Visual |
|---------|--------------|--------|
| `scanning` | `"Scanning…"` | brand-accent pill |
| `clean` | `"All synced · HH:MM"` (local time) | green pill |
| `error` | `"Scan failed"` | red pill |

`label=None` lets the helper compute the canonical text; passing an explicit string overrides it (used internally where the timestamp logic differs).

### Lifecycle wiring

| Event | Code path | Pill state |
|-------|-----------|------------|
| Dashboard constructed | `_build_top_band()` initial state | `scanning` ("Scanning…") |
| `MainWindow._start_scan()` invoked | `dashboard.set_sync_state("scanning")` | `scanning` |
| Scan completes successfully | `MainWindow._on_scan_done()` → `dashboard.finalize_stats(...)` (which calls `set_sync_state("clean")` at end) | `clean` ("All synced · HH:MM") |
| Scan errors out | (deferred — no current `ScanWorker` error callback) | n/a |

The "scan failed" path is exposed via the API but not currently triggered — `scanner.ScanWorker` doesn't emit a failure signal yet. Wiring it up requires a separate scanner-reliability pass; flagged as deferred in §7.

---

## 4. Keyboard-shortcut behavior

### Single binding, cross-platform

```python
self.act_focus_search = self._make_action(
    "Focus Search", "Ctrl+K", self._focus_dashboard_search
)
```

Qt translates `Ctrl` → `Cmd` on macOS automatically when the action is materialised via `QKeySequence("Ctrl+K")`. One binding covers both platforms.

### Handler

```python
def _focus_dashboard_search(self) -> None:
    if self.stack.currentIndex() != 0:
        self._show_dashboard()
    self.dashboard.focus_search()
```

The shortcut works from any page of the QStackedWidget — if the operator is on the Commons page or a Detail page, the handler switches back to the Dashboard first, then sets focus. Selects all existing text so a repeated press reliably resets the input.

### Affordance

The `Ctrl+K` chip beside the input is purely a visual hint — non-interactive QLabel. Tooltip: `"Press Ctrl+K (Cmd+K on macOS) to focus"`.

No command-palette UI. No `:` modal. No fancy overlay. Per the spec's "Raycast / Linear utility restraint, NOT: Notion AI / Arc Browser theatrics" rule.

---

## 5. Status coordination changes

### `MainWindow.status_scan` retired

Pre-Step-6 the status bar had a permanent right-aligned `QLabel` (`status_scan`) that showed `"● Scanning…"` text in PCC accent during scans. Now retired:

  - `_build_statusbar()` no longer creates the `status_scan` widget.
  - `_start_scan()` no longer calls `status_scan.setText(...)` — it calls `dashboard.set_sync_state("scanning")` instead.
  - `_on_scan_done()` no longer clears the status — `dashboard.finalize_stats()` flips the pill to `clean · HH:MM` itself.
  - `_start_commons_scan()` / `_on_commons_scanned()` no longer touch `status_scan` — the Commons page has its own scan indicator via `CommonsBrowser.set_scanning`.

### What the status bar still shows

  - `status_info` (full-width left): `"N tools discovered · Last scan: HH:MM:SS"`. Slow-changing, infrastructural.

Per spec §3.6: the status bar is now quieter / infrastructural; the sync pill in the utility band is the primary scan-status surface.

### What didn't change

  - The `Press ⌘K to search` right-aligned status-bar hint from the spec screenshot is spec **Step 8** — explicitly deferred to keep Step 6 scope bounded. Adding it now would conflate two surfaces; the operator may want to validate the band's overall feel before introducing the duplicate affordance.

---

## 6. Validation results

| Check | Result |
|-------|--------|
| Commons `python -m pytest -q tests/` | **126 passed** (no commons additions in this step) |
| PCC `python -m compileall -q .` | clean |
| PCC `python -m pytest -q tests/` | **4 passed** (smoke; MainWindow boot exercises Dashboard → top band → search frame end-to-end) |
| PCC source-mode launch | exit 0, 0 stderr (operator visual review pending) |
| Search input rendering | `QFrame#searchFrame` paints with surface bg + 1px border + 8px radius via PCC QSS overlay; QLineEdit transparent inside the frame |
| `Ctrl+K` focus behavior | `act_focus_search` installed on MainWindow via `addAction`; `_focus_dashboard_search` switches page + calls `dashboard.focus_search()` |
| Sync-pill state transitions | initial `scanning` → `clean · HH:MM` on scan completion (verified by reading `_on_scan_done` ↔ `finalize_stats` ↔ `set_sync_state` call graph) |
| BrandProfile compatibility | search chrome consumes PCC's `C` palette tokens (surface, border, btn_default, info, text); StatusBadge variants use commons sentinel substitution (scanning uses BRAND_ACCENT) |
| Layout stability | top band uses fixed 34 px height for the search frame, min/max width 380-540 px; page title + sync pill take natural sizes — no overflow, no layout thrashing at narrow window widths |
| post-B5 subprocess invariant | preserved (no subprocess changes) |
| post-B6 setStyleSheet invariant | preserved — new chrome flows through commons cascade via the new QSS overlay block (added to theme.py's existing overlay), not widget-level setStyleSheet |
| No startup regression | startup time unchanged; sync pill displays "Scanning…" briefly during the initial scan then settles to "All synced · HH:MM" |
| No notification surface added | spec rule respected — no toast, no banner, no autodismiss |

---

## 7. Remaining dashboard debt

Per the spec §6 sequence:

| # | Step | Status |
|---|------|--------|
| 1 | Lucide icons + sidebar modernization | done (B9) |
| 2 | StatusBadge primitive + dashboard pilot | done (B10) |
| 3 | Tools list → PhoenixTable | done (B11 + polish) |
| 4 | Per-tool activity tag colors | done (B12) |
| 5 | Aggregate tile refresh | done (B13) |
| 6 | **Top utility band — search shell + sync pill** | **done (B14, this commit)** |
| 7 | Search backend | pending |
| 8 | Status-bar `Press ⌘K to search` hint | pending |

### Items deferred but not blocking

  - **Sync-pill error state wiring.** API exposed (`set_sync_state("error")`) but no scan-fail callback in `ScanWorker` triggers it. Needs a separate scanner-reliability pass.
  - **Step-8 status-bar hint** ("Press ⌘K to search" right-aligned). Trivial single-line addition; deliberately deferred so the operator can validate band feel first.

---

## 8. Recommended Step 7 implementation target

The spec §6 nominates Step 7 as **"Search backend"** — replace the Step-6 shell's "coming soon" placeholder with a real search across tool names, recent commit messages, and open TODOs.

**Recommendation: proceed to Step 7 as scoped in the spec.**

Three reasons:

  1. **Shell is ready.** The QLineEdit + Ctrl+K + Enter wiring all work. Step 7 plugs a backend into the existing signal without touching the UI surface.
  2. **Corpus is already cached.** `Dashboard._tool_data` holds the full scan result (tool names, recent commits, TODOs). Search can read it directly — no scanner change required.
  3. **Result UI fits inside the existing widget tree.** A simple QListWidget popup attached to the QLineEdit (or a results panel that appears below the band) keeps scope bounded; the operator can decide popup vs panel during spec review.

### Step 7 scope (preview)

  - New `SearchCorpus` helper class (probably in a new `search.py` module) that indexes the cached `_tool_data` lazily on first query.
  - Match across three axes: tool names (exact + substring), recent commit messages (substring), TODO text (substring). Each result carries `(label, kind, target)` so the result click can route to the right surface (open detail tab / TODO position / commit context).
  - Result list — either inline below the search frame (small popup) or expanded view in the dashboard body during search. Spec doesn't pre-specify; needs a small Step-7 design call.
  - Empty-input state: when query is empty, no results panel — band stays in its idle look.
  - Performance: re-rank on every keystroke for ~20-50 result corpus is fine; nothing fancy needed.

### Optional precursor — Step 6.5

Add the status-bar `Press ⌘K to search` hint (the small Step-8 addition) before Step 7 if the operator wants the chrome complete first. One-line addition to `_build_statusbar()`. Not blocking; flagged for operator preference.

---

## 9. Confirmation

  - **No architecture changes occurred.** No new ADR. No public-API rename. No commons module added or removed. The new chrome is PCC-only (theme.py overlay + dashboard.py extensions); no commons additions in this step.
  - **No production deployment occurred.** Work is source-mode only on PCC `phase-3c-pcc-retrofit`. No installer built, no `dist/` zip created, no GitHub Release published. Branch not pushed.
  - **No BrandProfile changes occurred.** `PCC_BRAND` unchanged. `BrandProfile` API unchanged. Search chrome consumes PCC's `C` palette tokens; sync pill uses StatusBadge variants from Step 2 (which themselves use commons sentinel substitution — brand-accent for scanning, locked tokens for clean/error/etc.).
  - **No production tool source touched.** PCC-only PCC-side change. Phoenix CAD / Phoenix Checkout / PTT / PMT / ValveMaster all unmodified.
  - **No commons changes.** B14 consumes commons primitives (Panel + StatusBadge + icons) without modifying them. No commons commit.
  - **No subprocess regression.** No new subprocess calls. Post-B5 invariant preserved.
  - **No widget-level setStyleSheet regression.** New chrome lives in PCC's theme.py QSS overlay (existing inline-styled file pattern); B6's invariant of "no setStyleSheet calls outside theme.py" is preserved.
  - **No animation, no command palette, no notification system, no search indexing, no search backend.** Each one explicitly out of scope per the spec brief.

---

## Commit summary

| Repo | Commit | Subject |
|------|--------|---------|
| `phoenix-command-center` `phase-3c-pcc-retrofit` | (B14) | Top utility band — search shell + sync pill (B14, Step 6) |

(No commons commit for this step — Step 6 consumes existing primitives only.)

**Operator gate:** visual review of the new utility band before Step 7 starts. Recommended capture targets:

  1. Full dashboard at default 1300×800 — confirm the band sits above the aggregate-tile row with the page title left, search shell centered, sync pill right.
  2. Search input focused (Ctrl+K) — confirm the input gains focus and any existing text is selected.
  3. Sync-pill state transitions — confirm the pill flips from "Scanning…" → "All synced · HH:MM" when the scan completes.
  4. Status bar — confirm the prior "● Scanning…" indicator is gone; status bar shows only `N tools discovered · Last scan: HH:MM:SS`.
  5. Type a query + press Enter — confirm the status-bar "coming soon" message appears for ~5 seconds.

---

*End of report.*
