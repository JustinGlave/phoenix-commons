# PCC v1 — TODO Workbench V1-T3 Report

> **Status:** ✅ COMPLETE — read-only TODO Workbench view implemented, wired as
> a 3rd top-level view (Ctrl+3), tested (10 new tests), validated.
> **Date:** 2026-06-02.
> **Repo:** `phoenix-command-center` · branch `pcc-v1-ground-control-fixes`.
> **Spec:** `PCC_TODO_WORKBENCH_MVP_SPEC.md` (§ 8 UI, § 9 step V1-T3).
> **Builds on:** V1-T1 (`todo_state.py`) + V1-T2 (`todo_verify.py`).
> **Scope:** UI only. No source mutation, no actions, no md-toggle.

---

## 1. Files changed

| File | Type | Purpose |
|------|------|---------|
| `todo_workbench.py` | **new** (~270) | Read-only `TodoWorkbench(QWidget)` — Panel + PhoenixTable + StatusBadge + filter toolbar + empty states |
| `main_window.py` | modified (+~55) | 3rd top-level view: stack page 3, nav row 2, Ctrl+3, Tools-menu entry, scan-refresh hook, `_app_roots` helper, nav-index renumber |
| `tests/test_todo_workbench.py` | **new** (10 tests) | Construction / render / filters / empty states / state-path isolation |

No scanner, no commons, no dashboard/detail behaviour (beyond nav wiring), no
production-app source. No new commons primitive.

---

## 2. Workbench UI implementation (`todo_workbench.py`)

`TodoWorkbench(QWidget)` — a top-level view built **only** from existing
PCC/commons vocabulary:
- `Panel` container, `PhoenixTable` (commons, no-edit/no-select), `StatusBadge`
  pills, `QComboBox` filters, `QLabel` headers/empty/count — **no new
  primitive**.
- `pageTitle` object name + PCC `C` tokens for sub-labels (consistent chrome).

**Data flow** (no scanner change): `MainWindow._refresh_workbench()` passes its
cached `_tool_data` + an `{app: repo_root}` map →
`todo_verify.verify_tool_data(...)` (the pure V1-T2 engine) → `TodoView` rows →
table. The UI layer supplies `now` (`datetime.now().isoformat`) and the
file-probe (`make_fs_probe(app_roots)`); the engine stays pure.

**Persistence:** after a refresh with scan data, the Workbench writes the
engine's refreshed **bookkeeping** to the local `todo_state.json`
(`save_state`) — the V1-T1 overlay file, never repo source. This is what makes
`resolved` / `moved` / `last seen` meaningful across scans and sessions. A
write error is swallowed (a read-only view must never crash on it). Tests inject
a temp `_state_path` so a refresh never writes to the repo root.

---

## 3. Table columns

`App · Status · Priority · Tag · TODO · File · Line · Last seen · Verified`

- **Status** — a `StatusBadge` cell widget, variant mapped from the verify
  state (commons closed set only): open→`warning`, completed→`clean`,
  resolved→`unknown`, moved→`syncing`, changed→`dirty`, missing_file→`error`,
  needs_review→`dirty`. Label text spells the state out.
- **Priority** — `High`/`Normal`/`Low`/`—` from the operator overlay (read-only
  here; editing is V1-T4).
- **TODO** column stretches; **File** is interactive (220 px default); the rest
  size to contents. Full text is set as each cell's tooltip (long TODOs elide
  but hover-reveal). A moved row's TODO tooltip notes the previous line.
- **Last seen / Verified** — overlay timestamps formatted `YYYY-MM-DD HH:MM`
  (`—` when absent).
- **No Actions column** (V1-T4). Rows are display-only; `PhoenixTable` is
  no-selection / no-edit.
- Render is **bounded** at `MAX_ROWS = 1000`; the count line reports
  `N shown · M total` and any withheld overflow (never a silent truncation).

---

## 4. Filter behaviour

A simple toolbar, no fuzzy search / no index:
- **Status** combo: `All` · `Open` · `FIXME` · `Completed` · `Resolved` ·
  `Stale / Needs review`.
  - `Open` = present & `base_status==open` (includes moved-open).
  - `Completed` = present & `base_status==completed` (includes moved-completed).
  - `FIXME` = `tag=="FIXME"`.
  - `Resolved` = `status==resolved`.
  - `Stale / Needs review` = `status in {needs_review, changed, missing_file}`.
- **App** combo + **File** combo — distinct values from the current rows
  (`All apps` / `All files` defaults). Repopulated on each refresh with signals
  blocked and the prior selection preserved when still valid.

Filters compose (status ∧ app ∧ file) and re-render live on change.

---

## 5. Navigation wiring (`main_window.py`)

TODO Workbench is now the **3rd top-level view**:

| View | Stack page | Nav row | Shortcut |
|------|-----------|---------|----------|
| Dashboard | 0 | 0 | Ctrl+1 |
| Commons Browser | 1 | 1 | Ctrl+2 |
| Detail (per-tool) | 2 | (4+) | — |
| **TODO Workbench** | **3** | **2** | **Ctrl+3** |

- **Stack:** Workbench appended as page 3, so Detail stays page 2 — every
  `setCurrentIndex(2)` / detail caller is untouched.
- **Sidebar:** a `file-text`-icon nav row inserted at row 2. The "TOOLS"
  separator + per-tool rows now start at row 3 / 4+.
- **Nav-index renumber** (the only fragile part — done in one pass, all five
  sites): `_load_tools` rebuild boundary `>2`→`>3`; `_nav_changed` adds
  `row==2 → workbench` and tools at `row>=4` (`idx=row-4`); `_open_detail` nav
  row `+3`→`+4`; `_sidebar_context_menu` guard `<3`→`<4` and `row-3`→`row-4`.
- **Action + menu:** `act_workbench` (Ctrl+3) → `_show_workbench`; added to the
  **Tools** menu after Commons Browser.
- **Refresh:** `_show_workbench` refreshes on entry (fresh data without waiting
  for a scan); `_on_scan_done` refreshes after every scan (records bookkeeping +
  keeps the table current). Refresh All's discover/scan behaviour from the v1
  small-fixes is unchanged — it now also drives the Workbench.

`Ctrl+3` was verified free of conflicts (1/2/K/N/R/F5/,/Q/F1/Esc were the
existing binds).

---

## 6. Empty states

Calm, context-aware (no errors):
- **No root configured** → "Set your Tools Root in Settings to populate TODOs."
- **Root set, no scan yet** → "Run Refresh All to populate TODOs."
- **Scanned, zero TODOs** → "No TODOs found 🎉"
- **Filtered to zero** → "No TODOs match this filter."

The view starts in the "no scan yet" state on construction.

---

## 7. Validation results

Canonical Python 3.12 venv (ADR-014), `QT_QPA_PLATFORM=offscreen`.

| Check | Result |
|-------|--------|
| `py_compile` (`main_window.py`, `todo_workbench.py`) | ✅ OK |
| `compileall` (repo, excl. venv/commons/build/dist) | ✅ OK |
| `pytest tests/` (full suite) | ✅ **51 passed** in 0.44s (4 smoke + 37 state/verify + 10 workbench) |
| MainWindow constructs offscreen (≈ source-mode launch) | ✅ |
| Stack = 4 pages; page 3 is `TodoWorkbench` | ✅ |
| Nav rows: row 2 = Workbench, row 3 = "TOOLS" sep | ✅ |
| `_show_workbench` → stack 3 + nav row 2 | ✅ |
| Nav row mapping: 4→AppX, 5→AppY (offset), 3 (sep)→no-op | ✅ |
| Ctrl+3 wired + **unique** (no conflict) | ✅ |
| Tools menu contains "TODO Workbench" | ✅ |
| Table render via `_refresh_workbench` (2 rows) | ✅ |
| Filter smoke All/Open/FIXME/Completed/Resolved/Stale | ✅ (committed tests) |
| Empty states (no-root / no-scan / filtered-zero) | ✅ |
| `todo_state.json` git-ignored; no repo write from tests | ✅ |

Change surface = `main_window.py` + 2 new files. No build/venv leakage.

---

## 8. Known limitations (by design / deferred)

- **Read-only** — no row actions, no open-in-detail/VS-Code, no md-toggle
  (V1-T4 / V1-T5). `PhoenixTable` is no-selection by design here.
- **Absent rows** (resolved/missing/needs-review) show the stored normalized
  text + blank kind/tag (overlay doesn't retain raw text/kind/tag) — cosmetic;
  present rows carry full scan fields.
- **`resolved`/`moved` need prior state** — on a first-ever refresh everything
  is `open`/`completed` (present); those states populate once bookkeeping has
  been persisted across scans (now wired).
- **File filter** can grow long on big trees (still a simple combo; no search).
- **Render cap** 1000 rows (reported, never silent). Tuning deferred.

None required a scanner change or a new commons primitive.

---

## 9. Next step — V1-T4 (non-mutating actions)

Per spec § 9: add display-safe row actions that don't touch source —
open-in-detail (route to the detail TODOs tab), open-source-in-VS-Code
(`code -g file:line`), copy path, and operator overlay edits (priority / notes /
defer / dismiss → `todo_state.json`). Still **no** md-toggle (that's V1-T5, the
only source-mutating step).

---

## 10. Confirmation

- ✅ **No markdown checkbox toggle implemented** (V1-T5).
- ✅ **No source files edited** — the only write is the local `todo_state.json`
  overlay (V1-T1 file), never repo source / TODO comments.
- ✅ **No scanner contract changed** — consumes cached `_tool_data` unchanged.
- ✅ **No commons change / no new commons primitive** — Panel / PhoenixTable /
  StatusBadge / combos only.
- ✅ **No dashboard/detail behaviour change** beyond navigation integration.
- ✅ **No Actions column** — rows are display-only.
- ✅ **No release / tag / publish.**

### STOP conditions — none triggered

Scanner-contract pressure (none) · new commons primitive needed (none — closed
StatusBadge variant set sufficed) · table rendering unstable (no — 51 tests
green, render smoke clean) · Ctrl+3 conflict (none — verified unique) · scope
creep into editing/toggle/actions (held — read-only).

---

*V1-T3 complete and committed on `pcc-v1-ground-control-fixes`. Ready for V1-T4
(non-mutating actions) on operator go-ahead.*
