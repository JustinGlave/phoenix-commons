# PCC v1 — TODO Workbench V1-T5 Report

> **Status:** ✅ COMPLETE — safe markdown checkbox toggle implemented behind a
> pure, fully-guarded engine; 19 new tests; validated.
> **Date:** 2026-06-02.
> **Repo:** `phoenix-command-center` · branch `pcc-v1-ground-control-fixes`.
> **Spec:** `PCC_TODO_WORKBENCH_MVP_SPEC.md` (§ 7 safe-editing policy, § 9 V1-T5).
> **Builds on:** V1-T1/T2 (state + verify) · V1-T3 (read-only view) · V1-T4
> (actions + overlay).
> **Scope:** the **only** source-mutating action in the whole MVP — a
> single-line markdown checkbox flip. Code-comment TODOs stay hard-blocked.

---

## 1. Files changed

| File | Type | Purpose |
|------|------|---------|
| `todo_toggle.py` | **new** (~190) | Pure, guarded toggle engine — path containment, relocation, surgical flip, atomic write, post-write verify |
| `todo_workbench.py` | modified (+~50) | Context-menu "Mark done"/"Reopen" (md only; code disabled); `_act_toggle_md`; cache reconcile; `status_message` signal |
| `main_window.py` | modified (+3) | Connect `status_message` → status bar |
| `tests/test_todo_toggle.py` | **new** (17 tests) | All safety paths (pure) |
| `tests/test_todo_workbench.py` | modified (+2) | Toggle through the Workbench action; code-TODO refusal |

No scanner change, no commons change, no new commons primitive, no Workbench
redesign. `todo_toggle.py` is pure stdlib — **no Qt, no scanner import**.

---

## 2. Toggle implementation

`todo_toggle.toggle_markdown_todo(*, abs_path, app_root, todo_text, kind,
target_done, line_hint=None) -> ToggleResult` — target-based (not blind toggle),
so it's idempotent and matches the menu label ("Mark done" → `target_done=True`,
"Reopen" → `False`). Never raises; returns a `ToggleResult(ok, reason, new_done,
line_num, changed)`.

Flow: validate kind/root/path/existence → read (preserving EOLs) → relocate the
line → if already in target state, no-op success → else surgical flip → atomic
write → post-write re-read verify.

The line regex captures the structure for a surgical edit:
```
^(?P<open>\s*-\s*\[)(?P<mark>[ xX✓])(?P<close>\]\s+)(?P<text>.+)$
```
Only `mark` is replaced (`x` ↔ space); `open` (indent + `- [`), `close` (`] `),
`text`, and the line ending are reattached unchanged.

## 3. Safety checks (in order)

1. **Markdown only** — `kind != "md"` → refuse. Code-comment TODOs are never
   edited (the context menu also disables the item for them).
2. **App root known** — empty `app_root` → refuse.
3. **Path present** — empty `abs_path` → refuse.
4. **Containment** — `is_within(app_root, abs_path)` via `realpath` +
   `commonpath` (resolves `..` and symlinks, handles different-drive
   `ValueError`) → refuse if the target escapes the root.
5. **File exists** — `os.path.isfile` → refuse if missing.
6. **Confident relocation** — scan **all** lines for markdown-checkbox lines
   whose *normalized* text matches; require **exactly one**. Zero → "could not
   locate"; many → refuse "needs review", **unless** `line_hint` (1-based) points
   at exactly one of the duplicates (tie-break). `line_num` is never blindly
   trusted.
7. **Post-write verification** — re-read the file and confirm the marker flipped
   and the text is still the same TODO; failure → reported (rare anomaly).

All refusals leave the file byte-for-byte unchanged.

## 4. Atomic write behaviour

`_atomic_write` creates a temp file in the **same directory**, writes with
`newline=""` (so the exact line endings in the rebuilt content are preserved),
`flush` + `os.fsync`, then `os.replace` over the target (atomic within a
filesystem). On any `OSError` it returns False and the original file is
untouched; the temp file is always cleaned up. Never a partial write.

## 5. UI behaviour

- Context-menu item (single-row selection / right-click): **"Mark done"** for an
  unchecked row, **"Reopen (uncheck)"** for a checked row. For code TODOs the
  item is present but **disabled**: *"Mark done — markdown TODOs only"*.
- On success the Workbench reconciles the **cached** scan payload's `done`/`tag`
  for that one TODO to the confirmed file state, then re-verifies + re-renders
  (selection preserved). This is an in-memory cache reconcile to match the file
  we just wrote — **not** a scanner change; the next Refresh All re-scans for
  real. The TODO's identity (`todo_id`) is stable across the flip (md id ignores
  the tag), so the row keeps its overlay and just moves open ↔ completed.
- A calm status-bar message via the new `status_message` signal:
  *“…” marked done.* / *“…” reopened.* / *Toggle refused — <reason>.*

## 6. Tests / validation

Canonical Python 3.12 venv (ADR-014), `QT_QPA_PLATFORM=offscreen`.

| Check | Result |
|-------|--------|
| `compileall` (repo, excl. venv/commons/build/dist) | ✅ OK |
| `pytest tests/` | ✅ **79 passed** (was 60; +17 toggle-engine, +2 workbench) |
| unchecked → checked / checked → unchecked | ✅ |
| indentation / trailing text / **CRLF** line ending preserved | ✅ |
| relocates when `line_hint` wrong; normalized-text match robust | ✅ |
| already-in-state → no write | ✅ |
| no match refuses · multiple refuses · multiple + hint disambiguates | ✅ |
| **code TODO refused** · path-outside-root refused · missing-file refused · unknown-root refused | ✅ |
| atomic write leaves no temp; `is_within` helper | ✅ |
| Workbench: Mark done flips the real file + status + row reconcile | ✅ |
| Workbench: code TODO refused (file untouched) | ✅ |
| **Integration smoke** (offscreen MainWindow): toggle a temp `.md` → `- [ ]`→`- [x]`, status bar "marked done", row reconciled; reopen round-trip → `- [x]`→`- [ ]` | ✅ `T5_INTEGRATION_OK` |
| Change surface = 3 modified + 2 new; `todo_state.json` git-ignored | ✅ |

All tests operate on temp files (`tmp_path` / a temp dir); the integration smoke
created + removed its own temp repo. **No production app source was modified.**

## 7. Known limitations (by design / deferred)

- **Markdown checkboxes only** — code-comment TODOs are intentionally not
  editable, ever (hard block, per spec § 7).
- **Single-line, single-file** — no multi-toggle / bulk; the flip touches only
  the one matched line.
- **Identical-line duplicates** need a `line_hint` to act; otherwise refused
  ("needs review") rather than guessing.
- **Cache reconcile, not re-scan** — the toggled row updates from an in-memory
  reconcile to the confirmed file; fleet-wide stats (e.g. the dashboard "Open
  TODOs" tile) refresh on the next Refresh All. Eventually consistent + correct.
- **Non-md / weird checkbox glyphs** beyond `x`/`X`/`✓` aren't recognized
  (matches the scanner's `_MD_DONE`).

None required source editing beyond the single selected line, a scanner change,
or a new commons primitive.

## 8. Next step — V1-T6 (final Workbench polish)

Per spec § 9: integrate filters with defer/dismiss (hide deferred from the
default view), wire the dashboard "Open TODOs" tile to open the Workbench
filtered, **"Clear resolved"** (prune `resolved` + `dismissed` overlay entries),
and the scan-lifecycle polish — then the v1 merge-gate prep.

## 9. Confirmation

- ✅ **Code-comment TODOs are not editable** — refused by the engine *and*
  disabled in the menu.
- ✅ **Only the single selected markdown TODO line is ever written**, and only on
  files **inside the configured app root** (containment-checked).
- ✅ **No TODO lines deleted, no source logic rewritten, no mass edits, no
  installed-payload edits.**
- ✅ **Scanner contract unchanged** — `todo_toggle` doesn't import the scanner;
  the cache reconcile is in-memory only.
- ✅ **Commons unchanged / no new commons primitive.**
- ✅ **No Workbench redesign** (one context-menu item + a status signal).
- ✅ **No release / tag / publish.**

### STOP conditions — none triggered

Ambiguous relocation (handled: refuse unless exactly one / hint-disambiguated) ·
uncertain path containment (handled: `realpath`+`commonpath`, refuse on doubt) ·
code-comment editing temptation (hard-blocked) · scanner-change pressure (none) ·
corruption risk (surgical single-char flip + atomic write + post-write verify;
refusals leave the file byte-identical).

---

*V1-T5 complete and committed on `pcc-v1-ground-control-fixes`. Ready for V1-T6
(filters / Clear resolved / final Workbench polish + merge-gate prep) on operator
go-ahead.*
