# PCC v1 — TODO Workbench V1-T4 Report

> **Status:** ✅ COMPLETE — non-mutating row actions + operator-overlay editing
> implemented, tested (9 new tests), validated.
> **Date:** 2026-06-02.
> **Repo:** `phoenix-command-center` · branch `pcc-v1-ground-control-fixes`.
> **Spec:** `PCC_TODO_WORKBENCH_MVP_SPEC.md` (§ 7 allowed actions, § 9 step V1-T4).
> **Builds on:** V1-T1/T2 (state + verify) · V1-T3 (read-only view).
> **Scope:** triage actions only. **No markdown toggle** (V1-T5). **No source
> file is ever written.**

---

## 1. Files changed

| File | Type | Purpose |
|------|------|---------|
| `todo_workbench.py` | modified (+~150) | Selection + context menu + double-click; 7 actions; overlay edit + re-render |
| `main_window.py` | modified (+~25) | Wire `open_in_detail`/`open_in_editor` signals; `_open_todo_in_editor` launcher |
| `tests/test_todo_workbench.py` | modified (+9 tests) | priority/note/defer/dismiss/copy/abs-path/routing/immutability |

No scanner, no commons, no new commons primitive, no dashboard/detail behaviour
change (only the two new signal connections), no Workbench redesign.

---

## 2. Actions implemented

Surfaced via **single-row selection + right-click context menu + double-click**
(no per-row Actions column — keeps the table uncluttered; `PhoenixTable` opted
into `SingleSelection`/`SelectRows` on this instance, not a commons change). The
Status-column badge cells are `WA_TransparentForMouseEvents` so clicks there
still select the row.

| Action | Mechanism | Mutates |
|--------|-----------|---------|
| **Open in detail** | double-click or menu → `open_in_detail(app)` signal → MainWindow routes to the detail panel's TODOs tab (index 1) | nothing |
| **Open source in VS Code** | menu → `open_in_editor(abs_path, line)` signal → `code -g <path>:<line>` (launch-only) | nothing (never edits) |
| **Copy path** | menu → clipboard ← `"<abs-or-rel path>:<line>"` | clipboard only |
| **Set priority** | menu submenu High / Normal / Low / Clear | `todo_state.json` overlay |
| **Add / edit note** | menu → `QInputDialog.getMultiLineText` | `todo_state.json` overlay |
| **Defer / Undefer** | menu (label flips on current state) | `todo_state.json` overlay |
| **Dismiss / Restore** | menu (label flips on current state) | `todo_state.json` overlay |

Each action is a discrete `_act_*` method taking an explicit `TodoView`, so all
are unit-testable without driving the menu.

---

## 3. Overlay-edit behaviour

`_update_overlay(todo_id, **fields)`:
1. `todo_state.load_state(state_path)` — re-reads current overlay (so a
   concurrent bookkeeping write isn't clobbered),
2. `state.record(todo_id)` (get-or-create), `setattr` the changed field(s),
3. `todo_state.save_state(...)` — atomic temp-then-`os.replace` (V1-T1),
4. `_rerender_after_overlay()` — re-verify from the **cached scan payload**
   (no scanner trigger, no payload mutation) and re-render, **preserving the
   selected `todo_id`**.

Edits cover `priority` / `notes` / `deferred` / `dismissed` only — pure operator
metadata. **Source-of-truth rule preserved:** presence + completion still come
from the files via the verify engine each render; the overlay never asserts a
completion. Deferred/dismissed rows render **muted** (text-muted foreground)
with their state in the row tooltip, and the menu labels flip
(Defer↔Undefer, Dismiss↔Restore) — visible feedback without changing filters
(filter/prune behaviour is V1-T6).

---

## 4. Routing behaviour

Decoupled via Qt signals (same pattern as `Dashboard.tool_selected`), wired in
`MainWindow.__init__`:
- `workbench.open_in_detail` → `lambda name: self._open_detail(name, tab_index=1)`
  — opens the app's detail panel on the **TODOs tab**.
- `workbench.open_in_editor` → `self._open_todo_in_editor(path, line)` — launches
  the configured editor (`cfg.editor_cmd`, default `code`) with `-g
  <path>:<line>` for goto, falling back to opening the file when no line. Mirrors
  `detail_panel`'s VS Code launch (`shell=(os.name=="nt")`). **Launch-only — the
  file is never modified.** The Workbench resolves the absolute path itself
  (`app_roots[app] / source_file`) and the menu item disables when it can't.

---

## 5. Tests / validation

Canonical Python 3.12 venv (ADR-014), `QT_QPA_PLATFORM=offscreen`.

| Check | Result |
|-------|--------|
| `compileall` (repo, excl. venv/commons/build/dist) | ✅ OK |
| `pytest tests/` | ✅ **60 passed** (was 51; +9 T4), no warnings |
| Set priority writes overlay + reflects + Clear | ✅ |
| Add/edit note writes overlay | ✅ |
| Defer/undefer toggle | ✅ |
| Dismiss/restore toggle | ✅ |
| Copy path → `…:line` string | ✅ |
| Abs-path resolution (`app_root / source_file`) | ✅ |
| `open_in_detail` emits app name | ✅ |
| `open_in_editor` emits abs path + line | ✅ |
| Overlay edit does **not** mutate the scan payload | ✅ |
| **Integration smoke** (offscreen MainWindow): open-in-detail → `_open_detail(app, tab 1)`; open-in-editor → `code -g <path>:12`; priority persisted to state; scan payload untouched | ✅ `T4_INTEGRATION_OK` |
| Change surface = 3 modified files; `todo_state.json` git-ignored | ✅ |

Tests inject a temp `_state_path`, so overlay writes never touch the repo root.

---

## 6. Known limitations (by design / deferred)

- **No source-mutating action** in T4 — the markdown checkbox toggle is V1-T5
  (the only source-mutating step in the whole MVP).
- **Defer/Dismiss are flags + visual muting only** — they don't yet hide rows or
  prune; filter integration + "Clear resolved" is V1-T6.
- **VS Code `-g` goto** assumes a `code`/`cursor`-style editor (both support
  `-g file:line`); other editors get the file opened without the line. Best-
  effort, launch-only.
- **Context-menu discoverability** — actions live on right-click + double-click
  (no always-visible Actions column, to avoid cluttering/redesigning the table);
  the sub-header hints "Double-click to open · right-click for actions".
- **Note dialog** is a plain multi-line input (no rich text) — sufficient for
  triage notes.

None required source editing, a scanner change, or a new commons primitive.

---

## 7. Next step — V1-T5 (safe markdown checkbox toggle)

The **only** source-mutating action in the MVP. Per spec § 7: re-locate the line
by id+text (not blind `line_num`), assert it still matches
`_MD_OPEN`/`_MD_DONE`, flip **only** the single checkbox char (preserve
indentation/trailing text/line ending), atomic write, immediate re-scan to
confirm, and bail with an error toast if any assertion fails — and only ever on
files under the operator's configured root, never installed payloads. Code-
comment TODOs stay hard-blocked.

---

## 8. Confirmation

- ✅ **No source files edited** — overlay edits write only `todo_state.json`;
  open-in-editor is launch-only; copy is clipboard-only.
- ✅ **No markdown checkbox toggle implemented** (V1-T5).
- ✅ **No code-comment rewriting.**
- ✅ **No scanner contract changed** — consumes cached `_tool_data`; overlay edit
  re-verifies without triggering or mutating the scan.
- ✅ **No commons change / no new commons primitive.**
- ✅ **No dashboard/detail behaviour change** beyond the two signal connections.
- ✅ **No Workbench redesign** (selection + context menu added to the T3 table).
- ✅ **No release / tag / publish.**
- ✅ Local overlay never acts as source of truth — presence/completion stay
  file-derived each render.

### STOP conditions — none triggered

Source editing needed (no — overlay/clipboard/launch only) · scanner change
needed (no) · VS Code routing unsafe (no — `-g` launch, never edits) · overlay
acting as source of truth (no — verify still derives status from files) · action
UI becoming a PM system (no — triage metadata only, no kanban/dates/assignees).

---

*V1-T4 complete and committed on `pcc-v1-ground-control-fixes`. Ready for V1-T5
(safe markdown checkbox toggle) on operator go-ahead.*
