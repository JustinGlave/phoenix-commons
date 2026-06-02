# PCC v1 — TODO Workbench V1-T6 Report (Final Polish + Integration)

> **Status:** ✅ COMPLETE — TODO Workbench MVP finished. Filter integration,
> Clear resolved, dashboard tile wiring, scan-lifecycle + nav + empty-state
> polish. 83 tests green.
> **Date:** 2026-06-02.
> **Repo:** `phoenix-command-center` · branch `pcc-v1-ground-control-fixes`.
> **Spec:** `PCC_TODO_WORKBENCH_MVP_SPEC.md` (§ 8 UI, § 9 V1-T6, § 10 MVP scope).
> **Builds on:** V1-T1..T5.
> **Recommendation:** **READY for the PCC v1 merge gate.**

---

## 1. Files changed

| File | Type | Purpose |
|------|------|---------|
| `todo_workbench.py` | modified (+~66) | Deferred/Dismissed filters + default-hide-dismissed; Clear-resolved button + action; `set_status_filter`; stale-`_shown_rows` fix |
| `dashboard.py` | modified (+~23) | `AggregateTile` opt-in `clicked`/`set_clickable`; Dashboard `open_todos_clicked`; wire the Open-TODOs tile |
| `main_window.py` | modified (+~9) | Connect `open_todos_clicked` → open Workbench filtered to Open |
| `tests/test_todo_workbench.py` | modified (+4 tests, 1 updated) | Defer/dismiss filters, Clear-resolved prune-safety |

No scanner change, no commons change, no new commons primitive, no
project-management features, no Workbench redesign, no code-comment editing.

---

## 2. Filter / defer / dismiss behaviour

Status filter set is now **8**: `All · Open · FIXME · Completed · Resolved ·
Needs review · Deferred · Dismissed`.

- **Default-hide-dismissed** — every filter **except** `Dismissed` excludes
  dismissed rows. `Dismissed` is the only view that shows them. Manual control;
  nothing is auto-pruned.
- **Deferred stays visible but muted** under all non-Dismissed views, and has
  its own `Deferred` filter. Deferred/dismissed rows render in muted text with
  their state in the row tooltip (from V1-T4).
- `Open`/`Completed` use `base_status` so moved-open / moved-completed are
  included; `Needs review` = `needs_review ∪ changed ∪ missing_file`.
- New `set_status_filter(label)` lets the dashboard tile preselect `Open`.

A latent bug was fixed along the way: `_shown_rows` (the row-index → view map
the actions use) is now cleared in `_show_empty`, so a stale view can't be acted
on after a filter (e.g. dismissing the last visible row) empties the table.

## 3. Clear resolved behaviour

A manual **"Clear resolved"** `TertiaryButton` in the filter toolbar:
- Prunes **only** `todo_state.json` overlay entries whose **current
  verification status is `resolved`** (file readable + text genuinely gone —
  this also covers dismissed-resolved, since dismissal is overlay and doesn't
  change the verified status).
- **Never** clears `open` / `completed` / `moved` / `needs_review` /
  `missing_file` entries, and **never** touches source TODOs.
- Manual only — no auto-prune. Empty case → calm "No resolved TODOs to clear."
- After pruning it re-verifies + re-renders; cleared ids are absent from both
  state and scan, so they simply disappear from the table.

## 4. Dashboard integration

The existing **"Open TODOs"** aggregate tile is now clickable → opens the TODO
Workbench filtered to `Open`:
- `AggregateTile` gained an **opt-in** `clicked` signal + `set_clickable()`
  (pointer cursor). Non-interactive tiles (every other tile, and detail-panel
  tiles) are visually + behaviourally unchanged — `mousePressEvent` only emits
  when `set_clickable(True)` was called.
- `Dashboard.open_todos_clicked` is wired from `tile_todos.clicked`; MainWindow
  routes it to `_open_workbench_open` (→ `_show_workbench` + `set_status_filter
  (Open)`). The tile's metrics/appearance and all other dashboard behaviour are
  untouched — no tile redesign.

## 5. Scan-lifecycle behaviour

- `_on_scan_done` refreshes the Workbench after every scan / Refresh All
  (wired in V1-T3) so fleet-wide counts + verification reconcile.
- After a markdown toggle (V1-T5) the row reconcile remains immediate
  (in-memory cache reconcile of the toggled TODO), and the next Refresh All
  re-scans for real — eventually consistent + correct.
- `_show_workbench` refreshes on entry (fresh data without waiting for a scan).
- Calm status-bar messages on toggle + Clear resolved (via `status_message`).

## 6. Navigation / empty-state polish

- **Ctrl+3** opens the Workbench (verified **unique** — no shortcut conflict);
  **Tools → TODO Workbench** present; sidebar row 2; nav-row mapping correct
  (tools at row 4+).
- Empty states render calmly: **no root** ("Set your Tools Root…"), **no scan**
  ("Run Refresh All…"), **no TODOs** ("No TODOs found 🎉"), **filtered to zero**
  ("No TODOs match this filter." — covers the "only deferred/dismissed, hidden
  by default" case). "All resolved" shows the resolved rows under All (then
  Clear resolved empties them).

## 7. Validation results

Canonical Python 3.12 venv (ADR-014), `QT_QPA_PLATFORM=offscreen`.

| Check | Result |
|-------|--------|
| `compileall` (repo, excl. venv/commons/build/dist) | ✅ OK |
| `pytest tests/` | ✅ **83 passed** (was 79; +4, 1 updated) |
| Dismissed hidden by default; shown under Dismissed filter | ✅ |
| Deferred visible (muted) under All; shown under Deferred filter | ✅ |
| Clear resolved prunes only resolved overlay; keeps open | ✅ |
| **Integration smoke** (offscreen MainWindow): 8-filter set; every filter switches; **dashboard Open-TODOs tile → Workbench + Open filter**; Clear-resolved calm message; **Ctrl+3 unique**; markdown toggle still flips `[ ]`→`[x]` | ✅ `T6_INTEGRATION_OK` |
| Code TODO still refused (V1-T5 test) | ✅ |
| Refresh All → Workbench refresh wired (`_on_scan_done`) | ✅ |
| Change surface = 4 modified files; `todo_state.json` git-ignored | ✅ |

Full MVP test footprint: **83** (`test_todo_state` 24, `test_todo_verify` 13,
`test_todo_workbench` 25, `test_todo_toggle` 17, + 4 prior PCC smoke).

## 8. Remaining intentional limitations

- **No PM features** — no kanban, due dates, assignees, GitHub Issues sync (out
  of scope by design).
- **Only md-checkbox is source-mutating**; code TODOs never editable.
- **Identity collisions** (identical text twice in one file) share overlay;
  toggle needs a `line_hint` to disambiguate.
- **Cross-file move** reads as resolved-here + new-there (no cross-file
  identity) — deferred to v1.1.
- **Cache reconcile, not re-scan**, for an individual toggle; fleet stats catch
  up on the next Refresh All.
- **PCC computes `todo_id`** (no scanner-side emission) — deferred to v1.1.

## 9. Recommendation

**READY for the PCC v1 merge gate.** The TODO Workbench MVP (spec § 10) is
complete: all-app table, atomic local overlay, verification engine, safe
markdown toggle, the full filter set incl. defer/dismiss, Clear resolved,
open-in-detail / open-in-VS-Code / copy-path, and dashboard tile integration —
with PM features and code-comment editing explicitly out. 83 tests green; no
scanner/commons change. No tiny fix outstanding.

## 10. Confirmation

- ✅ **No scanner contract changed** — consumes cached `_tool_data`; the toggle
  reconcile is in-memory; `todo_toggle` doesn't import the scanner.
- ✅ **No commons changes / no new commons primitive** — `AggregateTile` /
  `PhoenixTable` / `StatusBadge` / `TertiaryButton` only; the AggregateTile
  click is additive + opt-in (other tiles unchanged).
- ✅ **No code-comment editing added** — md-checkbox only, hard-blocked for code.
- ✅ **No dashboard redesign** — one tile made clickable, metrics untouched.
- ✅ **No project-management features.**
- ✅ **No release / tag / publish.**
- ✅ Clear resolved removes only verified-resolved overlay entries — never
  source, never active (open/completed/moved/needs_review) state.

### STOP conditions — none triggered

Clear-resolved deleting active overlay (no — only verified `resolved` ids) ·
dashboard tile needing redesign (no — additive opt-in click) · scanner-change
pressure (none) · source mutation beyond the md toggle (none) · Workbench
becoming PM software (no — triage only).

---

*V1-T6 complete and committed on `pcc-v1-ground-control-fixes`. The TODO
Workbench MVP is done. Next: PCC v1 merge-gate preparation.*
