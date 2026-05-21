# Phase 3C — Optional Cleanup Report

> **Status:** complete (local; not yet committed/pushed).
> **Date:** 2026-05-21.
> **Scope:** removed 3 inert orphans identified in
> `PHASE_3C_FINAL_MERGE_REPORT §5` and
> `PHASE_3C_REMOTE_STABILIZATION_REPORT §8`. Nothing else.
> **Net change:** 3 files modified, **200 lines deleted**, 0 added.

---

## 1. Items removed

| # | Item | Location | LOC removed |
|---|------|----------|------------:|
| 1 | `tool_card.py` (entire file) | PCC root | 174 |
| 2 | `_RetiredToolRow` sentinel class + comment header | `dashboard.py:361-381` | 22 |
| 3 | `_open_detail_todos` dead method | `main_window.py:358-360` | 4 |

Total: **200 lines deleted across 3 files. Zero lines added.**

---

## 2. Verification of orphan status (Step 1)

Performed before any deletion — confirmed each item had zero remaining runtime references.

### `tool_card.py` / `ToolCard`

Grep across all PCC `*.py` files (excluding `.venv`):

```
tool_card.py:2:tool_card.py — Phoenix Command Center
tool_card.py:3:ToolCard widget displayed in the overview grid.
tool_card.py:16:class ToolCard(QFrame):
```

All 3 hits are **inside the file itself**. Zero external imports, zero string references, zero call sites. Confirmed orphan.

History: Was wired into the dashboard grid by B8 (commit `2d04c7d`), then B8 was reverted (`e94131c`) when the operator identified the wrong-design conclusion. The file persisted as dead code through the remainder of Phase 3C.

### `_RetiredToolRow`

```
dashboard.py:369:class _RetiredToolRow:
```

One hit — the class definition itself. Zero references anywhere else. Sentinel was added in B11 when `ToolRow` retired, intended to surface a clear `RuntimeError` if any stray external import tried to load it. No external import ever materialised; the sentinel never fired.

### `_open_detail_todos`

```
main_window.py:358:    def _open_detail_todos(self, name):
```

One hit — the method definition itself. The only previous caller was `Dashboard.todos_selected.connect(self._open_detail_todos)`, which was severed in B11 when `todos_selected` retired (the per-tool TODOs chip moved into the table's STATUS column workflow). The method has been dead code since B11 landed.

Also verified: zero references to `todos_selected` or `todos_clicked` signals anywhere in the codebase (they retired with the `ToolRow` class).

### Defensive cross-checks

  - Searched for string-form references (e.g. `"ToolCard"`, `"_RetiredToolRow"`, `"_open_detail_todos"`) — zero hits.
  - Searched for dynamic imports / `getattr` lookups — none found referencing these names.
  - Searched `tests/` directory — zero hits.
  - Searched commons docs — zero hits (the references in this report and prior reports are historical narrative, not code references).

All three items were genuinely dead. Safe to remove.

---

## 3. Validation results (Step 3)

| Check | Result |
|-------|--------|
| `python -m compileall -q . -x "\.venv\|commons\|build\|dist\|__pycache__"` | ✓ clean |
| `python -m pytest -q tests/` | ✓ **4 passed in 0.24s** |
| `python main.py` source-mode launch | ✓ launched (background; smoke tests already exercised MainWindow boot during the pytest run) |
| `git diff --stat` | `3 files changed, 200 deletions(-)` |
| Working tree clean (post-stage) | will be confirmed at commit time |
| Dashboard behaviour | unchanged (no code path touched any signal/handler still in use) |
| Detail panel behaviour | unchanged (`_open_detail` remains; `_open_detail_todos` was a dead wrapper around it) |
| Import resolution | clean (no module referenced `tool_card` outside itself) |

No regressions. The deletions touched code that had been unreachable since B11.

---

## 4. LOC reduction

| Metric | Pre-cleanup | Post-cleanup | Δ |
|--------|------------:|-------------:|--:|
| `dashboard.py` lines | (post-B15) | post-cleanup | −22 |
| `main_window.py` lines | (post-B15) | post-cleanup | −4 |
| `tool_card.py` lines | 174 | 0 (file deleted) | −174 |
| **Total LOC** | — | — | **−200** |

200 lines of dead code retired. The PCC source tree is now genuinely free of B8-revert / B11-retirement remnants.

---

## 5. Intentionally deferred cleanup (Step 4)

Per the brief: "If yes [cleanup temptation exists]: explicitly document it, but DO NOT implement it."

Three cleanup temptations identified, **all deferred:**

### A. ScanWorker `worker_failed` Signal — currently never emitted

`scanner.ScanWorker` exposes a `failed(str)` signal (added in B15 for sync-pill error state). The current `run()` method's `try`/`except` catches per-tool exceptions and emits `tool_scanned(..., {"status": "unknown", ...})` for them, but the outer `try` catching catastrophic worker failure does emit `failed(str)` correctly. So the signal *is* wired; it just doesn't fire in normal operation. Not dead code — defensive infrastructure. Leave.

### B. `dashboard.py` — `_short_tool_tag` and `_rgba_glow` module-level helpers

Both are module-level helpers consumed only by `ActivityRow`. Could be made `@staticmethod` on `ActivityRow` to tighten the module surface. Pure stylistic refactor; zero behavioural change. **Deferred** — out of scope for this cleanup PR. Future-PR candidate if a broader `dashboard.py` reorganisation happens.

### C. `theme.py` — `_old_C_LEGACY` aliases

PCC's `theme.py` `C` dict carries legacy alias keys (`accent`, `accent_dark`, `accent_glow`, `teal`, `teal_dark`, `btn_default`, `btn_hover`, `scrollbar`, `scrollbar_h`) that were preserved during the BrandProfile retrofit so existing inline-styled call sites kept working. Many of those call sites have since been retired (the dashboard now uses commons widgets where possible). A future audit could identify which aliases still have callers and retire the rest. **Deferred** — would touch many small files for marginal LOC savings; better as part of a future Phase 3F "complete BrandProfile cleanup" or similar.

### D. Comments referring to retired features

Several comments in `dashboard.py` / `main_window.py` reference "the retired ToolRow" or "the retired todos chip" as historical context. They're documentation, not code. Leaving them — they explain the *why* of the current shape to future readers. Not stale, just historical.

### What is NOT considered for cleanup

Per the brief's STOP CONDITIONS:
  - No surrounding architecture refactor.
  - No runtime-behaviour-changing edits.
  - No commons API touched.
  - No UX surface touched.

All four held throughout this session.

---

## 6. Confirmation

  - **No UX changes occurred.** Dashboard chrome unchanged. Sidebar unchanged. Detail panel unchanged. Status bar unchanged. Top utility band unchanged. Aggregate tiles unchanged. All visible surfaces identical to the post-Phase-3C-merge state.
  - **No architecture changes occurred.** No new ADR. No commons API change. No BrandProfile change. No new module added. The 3 deletions are pure subtractions from existing modules.
  - **No production deployment occurred.** Source-mode only. No frozen build. No installer. No GitHub Release.
  - **No tests modified.** Existing 4/4 smoke tests pass against the post-cleanup tree.
  - **No documentation modified.** Historical references in prior reports and prior code comments preserved as historical record. This cleanup report is the only new file.

---

## Local commit + push readiness

This report describes the cleanup state pre-commit. The cleanup itself is currently uncommitted in the PCC working tree:

```
$ git status
On branch main
Changes not staged for commit:
        deleted:    tool_card.py
        modified:   dashboard.py
        modified:   main_window.py

no changes added to commit (use "git add" and/or "git commit -a")
```

Recommended commit sequence (PCC main, single commit):

```
git rm tool_card.py
git add dashboard.py main_window.py
git commit -m "Cleanup: remove Phase 3C inert orphans (post-merge)" \
           -m "Removes 3 dead items: tool_card.py (B8-revert orphan), _RetiredToolRow sentinel (dashboard.py, never fired), _open_detail_todos (main_window.py, dead since B11). 200 LOC deleted. No UX change. No architecture change."
git push origin main
```

Push gated on operator approval per Phase-3C closure convention.

---

## Phase 3C verdict (post-cleanup)

**Phase 3C closure remains stable.** The cleanup removed 200 lines of dead code without changing any visible surface or any architectural decision. The tag `pcc-phase-3c-merged-v2.0.0` on commit `060d08c` continues to represent the operator-validated Phase 3C end-state; this cleanup PR (when committed) lands as a small additive consolidation on top, not a re-opening of the phase.

Phase 3D can begin from the cleanup tip whenever the operator opens its spec.

---

*End of cleanup report.*
