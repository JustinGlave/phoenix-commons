# PCC v1 — TODO Workbench V1-T1 + V1-T2 Report

> **Status:** ✅ COMPLETE — state model + verification engine implemented,
> tested (37 new tests), validated. **No UI** (V1-T3 next).
> **Date:** 2026-06-02.
> **Repo:** `phoenix-command-center` · branch `pcc-v1-ground-control-fixes`.
> **Spec:** `PCC_TODO_WORKBENCH_MVP_SPEC.md` (A1 full MVP, approved).
> **Scope:** logic foundation only — V1-T1 (`todo_state.py`) + V1-T2 (`todo_verify.py`).

---

## 1. Files changed

| File | Type | LOC | Purpose |
|------|------|-----|---------|
| `todo_state.py` | **new** | ~230 | Identity (`todo_id`/`normalize`) + operator-overlay model + atomic persistence |
| `todo_verify.py` | **new** | ~290 | Pure verification engine (scan ⋈ overlay → states) + input-shaping helpers |
| `tests/test_todo_state.py` | **new** | 24 tests | Identity stability + persistence resilience |
| `tests/test_todo_verify.py` | **new** | 13 tests | All verification-state transitions + purity |
| `.gitignore` | modified | +5 | Ignore machine-specific `todo_state.json` |

No Qt, no scanner, no dashboard/detail, no commons, no production-app source
touched. Both new modules are **pure stdlib** (`todo_state` imports only the
pure-stdlib `paths` helper; `todo_verify` imports only `todo_state` + stdlib).

---

## 2. `todo_state.py` — implementation

### Identity
- `normalize_todo_text(text)` — lower-case, collapse internal whitespace, strip
  leading/trailing whitespace + trailing sentence punctuation. Idempotent.
  Aliased as `normalize` (spec pseudocode name).
- `normalize_source_file(path)` — forward-slash, collapse `//`, strip edge
  slashes (case preserved; scanner already emits repo-relative forward-slashed
  paths).
- `todo_id(app, source_file, text, kind, tag)` — see § 3.

### Operator overlay model
- `TodoRecord` (dataclass) — overlay (`priority`, `notes`, `deferred`,
  `dismissed`, `operator_status`) + verification bookkeeping (`app`,
  `first_seen`, `last_seen`, `last_verified`, `last_known_file`,
  `last_known_line`, `last_text`). `from_dict` **forward-fills** missing keys,
  **ignores** unknown keys, and **coerces** bad values (out-of-vocabulary
  `priority` → `None`; non-str notes → `""`; str line → int). `app` was added
  beyond spec § 5's listed fields because the § 6 cross-check procedure already
  references `rec.app` (needed for absent-id attribution + file probing).
- `TodoState` (dataclass) — `{schema, todos: {todo_id: TodoRecord}}` with
  `record()` (get-or-create), `copy()` (deep copy via dict round-trip), and
  defensive `from_dict` (non-dict → empty; bad schema → default; non-dict
  `todos` → `{}`).

### Persistence
- `default_state_path()` → `paths.user_data_dir() / "todo_state.json"` — the
  canonical PCC user-data dir (project root in source mode = **beside
  `pcc_config.json`** per spec § 5; `%APPDATA%\ATS Inc\Phoenix Command Center`
  when frozen, which **survives auto-updates**). This is the prompt's "PCC
  user-data location".
- `save_state` — **atomic**: `tempfile.mkstemp` sibling → write → `flush` →
  `os.fsync` → `os.replace`. Temp file cleaned up on any error path. A crash
  mid-write can never corrupt live operator notes.
- `load_state` — defensive: `FileNotFoundError` / `OSError` / `ValueError`
  (incl. `JSONDecodeError`) → empty `TodoState()`. Never raises into the caller.

**Source of truth = the files.** This module stores operator overlay +
bookkeeping only; completion (`done`) is always re-derived from the scan, never
read back from state.

---

## 3. `todo_id` strategy

```
md   :  sha1( app ␟ norm_file ␟ "md"   ␟ norm_text )[:16]
code :  sha1( app ␟ norm_file ␟ "code" ␟ TAG ␟ norm_text )[:16]
```
(`␟` = ASCII unit separator `\x1f`, which can't appear in TODO text.)

| Property | Behaviour | Why |
|----------|-----------|-----|
| **No `line_num`** | id is identical regardless of line | a moved TODO keeps its id → reconciled silently as `moved`, not lost+new |
| **md excludes tag** | `[ ]`(TODO) and `[x]`(DONE) → same id | toggling completion tracks the *same* item, not a new "DONE" row |
| **code includes tag** | `# TODO x` ≠ `# FIXME x` | a TODO and a FIXME are genuinely different debt |
| **Normalized text** | whitespace/case/trailing-punct insensitive | cosmetic edits don't fork identity |
| **Includes app + file** | same text in two files/apps → distinct | correct cross-app attribution |

Signature order follows the **V1-T1 brief** `(app, source_file, text, kind,
tag)` (the spec § 4 pseudocode listed `(app, source_file, kind, tag, text)` —
same inputs, brief order used). Computed entirely **in PCC** — no scanner
change.

**Known collision (accepted, spec § 4):** two identical TODO lines in the *same*
file → same id (shared overlay). Rare; occurrence-ordinal disambiguation
deferred to v1.1.

---

## 4. `todo_verify.py` — engine behaviour

`verify(scan_todos, state, now, *, probe=None, similarity_threshold=0.8)
-> VerifyResult(rows, state)`.

**Purity contract:** no Qt · no clock (caller passes `now`) · no disk I/O ·
input `state` never mutated (returns an updated **copy**) · filesystem access
**injected** via `probe`.

### State decision table

| Situation | `status` | Notes |
|-----------|----------|-------|
| present, `done=False` | `open` | `base_status=open` |
| present, `done=True` | `completed` | `base_status=completed` |
| present, line changed (same text) | `moved` | `base_status` = underlying open/completed; `moved=True`, `previous_line` set, bookkeeping line updated. `moved/open` ≡ `(moved, base=open)`; `moved/completed` ≡ `(moved, base=completed)` |
| absent, probe `ok`, no similar text | `resolved` | only assertion of resolution, and only on a **readable** file with genuine absence |
| absent, probe `ok`, similar text in same file (ratio ≥ 0.8) | `changed` | TODO was edited → flagged for review, not silently resolved |
| absent, probe `missing` | `missing_file` | file gone |
| absent, probe `unreadable` | `needs_review` | transient/locked file |
| absent, **no probe / `unknown`** | `needs_review` | **safety default — never `resolved`** |

The absent-id classification enforces the spec § 6 safety rule: a transiently
unreadable, missing, or unprobeable file is **never** auto-flipped to
`resolved` (which would hide real debt). Resolution is asserted only on a
readable file with the text genuinely absent.

### Helpers
- `flatten_tool_data(tool_data)` — flattens `{app: {"todos":[…]}}` (PCC's
  `_tool_data` shape) to a flat ScanTodo list, **authoritatively** injecting
  `app` from the container key; tolerates non-dict/odd shapes.
- `make_fs_probe({app: root})` — builds a real-FS probe (`ok`/`missing`/
  `unreadable`/`unknown`) for the UI layer; an unmapped app → `unknown`.
- `verify_tool_data(tool_data, state, now, *, app_roots=None)` — ergonomic
  wrapper that shapes inputs then calls the pure `verify`.
- `_similar` — stdlib `difflib.SequenceMatcher` ratio (no new dependency).

`TodoView` (presented row) = scan fields + `todo_id` + `status`/`base_status`/
`present`/`moved`/`previous_line` + overlay fields (priority/notes/deferred/
dismissed/operator_status/first_seen/last_seen/last_verified). Assembled fresh
each pass — the scan drives presence, the overlay decorates.

---

## 5. Test coverage (37 tests)

**`test_todo_state.py` (24):** normalize collapses ws/case · strips trailing
punct (keeps internal) · idempotent · empty/punct-only/None · `normalize` alias
· `todo_id` 16-char hex · **line-independent** · stable across ws/punct ·
**changes on text change** · **md ignores tag** · **code distinguishes
TODO/FIXME** · distinguishes file/app · record forward-fill + coercion + garbage
· **missing file → empty** · **atomic roundtrip** · no temp left behind ·
**corrupt file → empty** · non-dict todos ignored · copy independence.

**`test_todo_verify.py` (13):** **open** · **completed** · first-sighting
bookkeeping · **moved** (line) · **moved/completed** · **md-toggle keeps
identity (not a new resolved row)** · **resolved** (file ok + gone) ·
**missing_file** · **unreadable → needs_review** · **no-probe → needs_review
(never resolved)** · **changed** (similar text in file) · **verify doesn't
mutate input state** · overlay carried onto rows · **FIXME tag preserved +
distinct id** · flatten injects app + tolerates junk · `make_fs_probe`
ok/missing/unknown.

Every state in the brief's "minimum v1 logic" plus the full 7-state set is
exercised, including the two safety-critical negatives (never auto-resolve an
unreadable/unknown file; md-toggle never spawns a phantom resolved row).

---

## 6. Validation results

All with the canonical Python 3.12 venv (ADR-014), `QT_QPA_PLATFORM=offscreen`.

| Check | Result |
|-------|--------|
| `py_compile` (4 new files) | ✅ OK |
| `compileall` (repo, excl. venv/commons/build/dist) | ✅ OK |
| Import smoke: `python -c "import todo_state, todo_verify; print('todo foundation OK')"` | ✅ `todo foundation OK` |
| `pytest tests/test_todo_state.py tests/test_todo_verify.py` | ✅ **37 passed** in 0.08s |
| `pytest tests/` (full suite — incl. 4 prior smoke) | ✅ **41 passed** in 0.35s |
| `git check-ignore todo_state.json` | ✅ ignored (no operator state leaks) |
| Change surface = 4 new + `.gitignore` only | ✅ |

No GUI launch was needed — the foundation is Qt-free and imports cleanly.

---

## 7. Known limitations (by design / deferred)

- **Identity collision** — identical text twice in one file shares one id +
  overlay (spec § 4; ordinal disambiguation → v1.1).
- **Cross-file move** — moving a TODO between files reads as resolved-here +
  new-there (no cross-file identity; spec § 10).
- **Absent-row text** — resolved/missing rows display the stored *normalized*
  `last_text` (raw pre-normalization text isn't retained); kind/tag are blank
  on absent rows (not stored in the overlay). Cosmetic only; present rows carry
  full scan fields.
- **`changed` precision** — `difflib` ratio ≥ 0.8 is a heuristic; ambiguous
  edits surface as `changed`/needs-review for the operator to judge (never
  auto-resolved). Tunable via `similarity_threshold`.
- **Probe is caller-supplied** — the engine stays pure; real file existence is
  resolved by the UI layer (V1-T6) via `make_fs_probe(app_roots)`. Without a
  probe, absent ids are conservatively `needs_review`.

None of these required a scanner change or risked making local state the source
of truth.

---

## 8. Next step — V1-T3 (read-only Workbench UI)

Per spec § 9, V1-T3 builds the **read-only** Workbench view:
- new `todo_workbench.py` — commons `PhoenixTable` columns (App · Status ·
  Priority · Tag · Text · File · Line · Last seen · Verified), `StatusBadge`
  per verify state, filter toolbar (All/Open/FIXME/Completed/Resolved/Stale/by
  app/by file).
- view-model join: flatten `_tool_data` → `verify_tool_data(...)` → rows.
- `main_window.py` nav wiring as a 3rd top-level view (**Ctrl+3** + Tools-menu
  entry — deferred to V1-T3 per operator decision; not added here).
- read-only first: no actions, no md toggle (those are V1-T4 / V1-T5).

---

## 9. Confirmation

- ✅ **No UI implemented** — logic + tests only.
- ✅ **No scanner contract changed** — consumes the existing `get_todos`
  payload (`text/done/source_file/line_num/kind/tag`) unchanged.
- ✅ **No production app source changed** — work is entirely within PCC.
- ✅ **No markdown checkbox toggle implemented** — V1-T5, not started; no
  source-mutating code exists in this foundation.
- ✅ **No code-comment rewriting** — none.
- ✅ **No commons primitive added / commons architecture changed.**
- ✅ **No dashboard / detail-panel change.**
- ✅ **No Ctrl+3 / nav change yet** (V1-T3).
- ✅ **No release / tag / publish.**
- ✅ Local state stores operator overlay only; **files remain source of truth**.

### STOP conditions — none triggered

Scanner-contract pressure (none — payload sufficient) · `todo_id` stable without
line number (✅ achieved + tested) · local state becoming source of truth (no —
overlay only) · verification needing source rewrites (no — pure read + injected
probe) · scope creep into UI (held — no UI) · tests can't cover transitions (no
— all 7 states + safety negatives covered).

---

*V1-T1 + V1-T2 complete and committed on `pcc-v1-ground-control-fixes`. Ready
for V1-T3 (read-only TODO Workbench UI) on operator go-ahead.*
