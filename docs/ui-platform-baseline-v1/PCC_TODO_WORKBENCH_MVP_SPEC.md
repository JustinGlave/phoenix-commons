# PCC v1 — TODO Workbench MVP Spec + Integration Plan

> **Status:** spec / planning only. No implementation.
> **Date:** 2026-06-02.
> **Repo:** `phoenix-command-center` (`main` @ `3a13eed`).
> **Supersedes scope of:** the PCC v1 small-fixes prompt is paused; this adds a TODO Workbench as a v1 requirement on top of the § 11 sequence in `PCC_V1_GROUND_CONTROL_RELEASE_READINESS_AUDIT.md`.
> **Recommendation:** include a **bounded MVP** in PCC v1 before RC (§ 12).

---

## 1. Current TODO capability audit

PCC already extracts + surfaces TODOs; the Workbench is a new *management* layer over existing data — not new parsing.

### Scanner payload (`scanner.get_todos`, `scanner.py:292`)

Per-TODO dict, already produced + cached per app by `ScanWorker` (`scanner.py:456` → `data["todos"]`):

| Field | Type | Meaning |
|-------|------|---------|
| `text` | str | TODO body (md checkbox text, or code-comment text after the tag) |
| `done` | bool | md `[x]` → True; md `[ ]` and all code comments → False |
| `source_file` | str | repo-relative, forward-slashed (`scanner.py:304`) |
| `line_num` | int | 1-based line |
| `kind` | str | `'md'` or `'code'` |
| `tag` | str | `TODO` / `DONE` (md) · `TODO`/`FIXME`/`HACK`/`XXX` (code) |

Regexes (`scanner.py:15`):
- `_MD_OPEN = ^\s*-\s*\[\s\]\s+(.+)$` → open checkbox
- `_MD_DONE = ^\s*-\s*\[[xX✓]\]\s+(.+)$` → checked checkbox
- `_CODE_TAG = #\s*(TODO|FIXME|HACK|XXX)[:\s]+(.+)` over `.py/.js/.ts/.jsx/.tsx`
- Skips `_SKIP_DIRS` (`.venv`, `__pycache__`, `dist`, `build`, `node_modules`, …)

### Existing consuming surfaces

| Surface | Behavior | File |
|---------|----------|------|
| Dashboard aggregate | "Open TODOs" tile sums fleet-wide (fast stat-walk substring count + per-tool list) | `dashboard.py:599`; `scanner.py:283` |
| Detail TODOs tab | `TodoItem` widgets, open/done/FIXME summary badges, per-file grouping | `detail_panel.py:391, 648` |
| Search MVP | each TODO → searchable row (kind `"todo"`, top-50/tool), routes to detail `tab_index=1` | `search.py:114` |

**Reuse verdict:** the payload (`text/done/source_file/line_num/kind/tag`) is **sufficient for the Workbench**. Stable identity + verification + operator metadata are all derivable in PCC. **No scanner-contract change required** (honors the strict constraint). The Workbench consumes the same `_tool_data[app]["todos"]` already cached on every scan.

---

## 2. Proposed TODO Workbench — product intent

A bounded cross-app TODO **management** surface: PCC as Ground Control for TODO debt across the whole family. It lets the operator:

1. see every TODO across all discovered apps in one table
2. filter by app / status / tag / FIXME
3. open a TODO in the app detail view
4. open the TODO's source file in VS Code at the line
5. attach operator metadata (priority / notes / deferred) **without touching source**
6. cross-check after each scan whether each TODO is still present / completed / resolved / moved / changed
7. safely toggle **markdown checkbox** TODOs done/reopened
8. never perform unsafe code-comment rewrites

**Explicitly NOT** (strict constraints): not a PM system, no kanban, no due dates/assignees, no GitHub Issues sync, no code-comment auto-editing in v1, no scanner-contract or commons-architecture change.

**Source of truth = the files.** The repos' markdown checkboxes and code comments are authoritative for *presence + completion*. PCC's local state only ever stores *operator overlay metadata* (priority/notes/defer) + *verification bookkeeping* — it never asserts a completion the file doesn't show.

---

## 3. Data model

### 3.1 Scan-derived TODO record (in-memory, per scan — unchanged from scanner)

```
ScanTodo = {
  app: str,            # discovered tool name (added by Workbench from the tool key)
  text: str,
  done: bool,
  source_file: str,    # repo-relative, forward-slashed
  line_num: int,
  kind: "md" | "code",
  tag: str,            # TODO/DONE/FIXME/HACK/XXX
}
```
`app` is injected by the Workbench when it flattens `_tool_data` (`{app: {"todos":[…]}}`) into one list; the scanner already keys todos per tool.

### 3.2 Workbench view-model row (in-memory, presented)

```
TodoRow = ScanTodo + {
  todo_id: str,            # stable id (§ 4)
  status: VerifyState,     # computed (§ 6)
  priority: "low"|"normal"|"high" | None,   # from local state
  notes: str,              # from local state
  deferred: bool,          # from local state
  first_seen: iso8601,     # from local state
  last_seen: iso8601,      # from local state
  last_verified: iso8601,  # from local state
}
```

The view-model is **assembled fresh each render** by joining the latest scan's `ScanTodo` list with `todo_state.json` on `todo_id`. The scan list drives presence; local state drives overlay.

---

## 4. Stable TODO identity strategy

Line numbers move; text is the stable anchor. Define:

```
def todo_id(app, source_file, kind, tag, text) -> str:
    norm = normalize(text)          # lower(), collapse internal whitespace, strip trailing . , ; :
    if kind == "md":
        key = f"{app}\x1f{source_file}\x1fmd\x1f{norm}"      # NOT tag — [ ]↔[x] keeps same id
    else:  # code
        key = f"{app}\x1f{source_file}\x1fcode\x1f{tag}\x1f{norm}"  # FIXME vs TODO are distinct items
    return sha1(key.encode()).hexdigest()[:16]
```

Design points:
- **Excludes `line_num`** → survives line moves (a moved TODO keeps its id → "Moved" reconciles silently, § 6).
- **md excludes the TODO/DONE tag** → toggling `[ ]`↔`[x]` preserves the id, so the item is tracked across completion rather than appearing as a new "DONE" row.
- **code includes the tag** → a `TODO` and a `FIXME` with the same text in the same file are genuinely different debt items.
- **Includes `source_file`** → the same text in two files are distinct (moving a TODO between files registers as resolved-here + new-there; acceptable for MVP, flagged § 11).
- **Collision case:** two identical TODO lines in the *same* file → same id. Rare; MVP treats them as one tracked item (operator metadata shared). A future refinement could append an occurrence ordinal; deferred (§ 10).

`todo_id` is computed **in PCC** (no scanner change).

---

## 5. Local PCC state file design

New file `todo_state.json` beside `pcc_config.json` (same dir; same load/forward-fill pattern as `config.py`, **but with atomic temp-file-then-replace** per the PCC persistence standard).

```jsonc
{
  "schema": 1,
  "todos": {
    "<todo_id>": {
      "priority": "high",            // operator overlay; null/absent = normal
      "notes": "blocking the v1 cut",
      "deferred": false,             // operator hid it from the default Open view
      "dismissed": false,            // operator acknowledged a 'resolved' / cleared it
      "operator_status": "in_review",// optional operator label, free of source truth
      "first_seen": "2026-06-02T...",
      "last_seen":  "2026-06-02T...",// last scan that still found this id
      "last_verified": "2026-06-02T...",
      "last_known_file": "main.py",  // for move/rename detection
      "last_known_line": 99,
      "last_text": "wire updater"    // for 'changed' detection
    }
  }
}
```

Rules:
- **Source-of-truth completion is NOT stored here.** Whether a TODO is *done* comes from the file (md `[x]`), re-derived each scan. `todo_state.json` stores only operator overlay + verification bookkeeping.
- `operator_status` is advisory (e.g. "in_review", "wontfix-pending") and never overrides the file-derived status.
- Entries are **pruned** when an id has been `resolved` + `dismissed` for N scans (configurable; default keep-forever in MVP, see § 10 "Clear resolved").
- Atomic write: write `todo_state.json.tmp` → `os.replace`. Never partial-write (a corrupt state file must never lose operator notes).
- Load is defensive: unknown ids ignored, missing keys forward-filled, parse failure → empty overlay (never crash the Workbench).

---

## 6. Cross-check algorithm (verification states)

Run after a scan (or on "Verify"). Compare the fresh `ScanTodo` set (authoritative) against `todo_state.json` records.

### States

| State | Condition |
|-------|-----------|
| **Open / still present** | id found this scan, `done == False` |
| **Completed** | id found this scan, `done == True` (md `[x]`) |
| **Moved** | id found, but `line_num` differs from `last_known_line` (same text/file) → reconcile: update line, status = underlying open/completed |
| **Changed** | not found by id, but a TODO exists in the same file whose normalized text is *similar* (≥ threshold, e.g. token-set ratio ≥ 0.8) → flag "Needs review" (text edited) |
| **Resolved / no longer found** | id was seen before, not found this scan, file readable, no similar match |
| **Missing file** | id's `last_known_file` no longer exists in the repo |
| **Needs review** | ambiguous: file unreadable this scan, or multiple similar candidates, or a "Changed" match |

### Procedure (per app, after scan)

```
fresh = { todo_id(t): t for t in scan_todos(app) }
state = load_todo_state().todos
for id, t in fresh.items():
    rec = state.get(id) or new_record(first_seen=now)
    rec.last_seen = now; rec.last_verified = now
    rec.status = "completed" if t.done else "open"
    if rec.last_known_line and rec.last_known_line != t.line_num and rec.last_text == norm(t.text):
        rec.status = "moved→" + rec.status      # silent line reconcile
    rec.last_known_file, rec.last_known_line, rec.last_text = t.source_file, t.line_num, norm(t.text)
for id, rec in state.items() not in fresh and rec.app == app:
    if not file_exists(rec.last_known_file):      rec.status = "missing_file"
    elif similar_todo_in_file(rec):               rec.status = "needs_review"  # Changed
    elif file_unreadable(rec.last_known_file):     rec.status = "needs_review"
    else:                                          rec.status = "resolved"
save_todo_state_atomic(state)
```

**Safety:** a temporarily-unreadable or transiently-missing file must **never** silently flip an item to "resolved" (which could hide real debt) — it goes to "needs_review" / "missing_file". Resolution is only asserted when the file is readable and the text genuinely absent.

---

## 7. Safe editing policy

### Allowed in v1

| Action | Safety mechanism |
|--------|------------------|
| Toggle md checkbox `[ ]`↔`[x]` | (a) re-locate the line by id+text (not blind line_num); (b) assert the line still matches `_MD_OPEN`/`_MD_DONE`; (c) flip **only** the single checkbox char, preserving indentation + trailing text + line ending; (d) atomic write of the file; (e) immediate re-scan of that file to confirm the toggle landed; (f) bail with an error toast if any assertion fails — never best-effort |
| Open source in editor | `subprocess` `editor_cmd` (config `editor_cmd`, default `code`) with `file:line` (`code -g path:line`) |
| Copy file path | clipboard only |
| Add/edit local notes, priority, defer, dismiss | `todo_state.json` only — never touches source |

### NOT allowed in v1 (hard stops)

- Automatically editing / rewriting **code** comments (`# TODO …`)
- Deleting any TODO line (md or code)
- Rewriting source logic
- Mass / multi-file edits in one action
- Any write outside the single targeted md line during a toggle

The md-toggle is the **only** source-mutating action in the MVP, it is single-line + reversible + verified, and it operates only on files in the operator's own configured root (never on installed/exe payloads).

---

## 8. UI surface proposal

A new top-level view — **TODO Workbench** — as the 3rd primary nav alongside Dashboard (Ctrl+1) and Commons Browser (Ctrl+2). Proposed **Ctrl+3** + Tools-menu entry. Built on the commons `PhoenixTable` + existing Panel/StatusBadge/button vocabulary (no new widgets, no redesign).

### Table columns

| App · Status · Priority · Tag · TODO text · File · Line · Last seen · Verified · Actions |

- **Status** = `StatusBadge` variant per § 6 state (open=warning, completed=clean/green, resolved=muted, needs_review=amber, missing_file=error).
- **Actions** = compact icon buttons: Open-in-detail · Open-in-VS-Code · Toggle-done (md only; disabled for code) · Defer · Note.

### Filters (toolbar)

All · Open · FIXME · Completed · Resolved · Stale (seen-before-not-now / needs_review) · By app (dropdown) · By file (dropdown) · free-text filter box (reuse search ranking).

### Actions (toolbar / context)

- **Verify selected** / **Verify all** — run § 6 cross-check
- **Open in detail** — routes to detail panel TODOs tab (`tab_index=1`) for that app
- **Open source in VS Code** — `code -g file:line`
- **Mark markdown done / reopen** — § 7 safe toggle (md rows only)
- **Defer** / **Add note** — local overlay
- **Clear resolved** — prune `resolved`+`dismissed` rows from `todo_state.json`

### Empty / first-run states

- No root configured → reuse the dashboard's "set Tools Root" affordance.
- App with zero TODOs → "No TODO debt 🎉" row group, not an error.

---

## 9. Implementation sequence

Bounded MVP, after the § 11 small-fixes of the readiness audit (V1-1..V1-5), as a dedicated phase **V1-T**:

| Step | Work | Files | Risk |
|------|------|-------|------|
| **V1-T1** | `todo_state.py` — atomic load/save + forward-fill (model on `config.py`); `todo_id()` + `normalize()` helpers | new `todo_state.py` | low |
| **V1-T2** | Verification engine — § 6 cross-check; pure function over (scan todos, state) → rows; unit-tested | new `todo_verify.py` (+ `tests/test_todo_verify.py`) | low (pure logic) |
| **V1-T3** | Workbench view — `PhoenixTable` columns + filters + view-model join; read-only first | new `todo_workbench.py`, `main_window.py` nav wire | medium |
| **V1-T4** | Actions (non-mutating) — open-in-detail, open-in-VS-Code, copy path, defer/note/priority → state | `todo_workbench.py` | low |
| **V1-T5** | Safe md toggle — § 7 mechanism + re-scan verify + failure toast | `todo_workbench.py` (+ `tests/test_md_toggle.py`) | medium (only source-mutating step; test hard) |
| **V1-T6** | Integration — dashboard "Open TODOs" tile → open Workbench filtered; scan-lifecycle hook to refresh rows; "Clear resolved" | `main_window.py`, `dashboard.py` | low |
| **V1-T7** | Validation — compileall + new unit tests + offscreen smoke + operator interactive review | — | — |

Estimated ~1 working session for V1-T1..V1-T2 (logic + tests), ~1 session for V1-T3..V1-T7 (UI + integration + validate). Adds ~1–2 sessions on top of the small-fixes phase.

---

## 10. v1 MUST-have vs deferred

### MUST for PCC v1 (bounded MVP)

- All-app TODO table (flatten `_tool_data` todos)
- Local `todo_state.json` (atomic) — operator overlay only
- Verify / cross-check engine (§ 6 states)
- Markdown checkbox safe toggle (§ 7)
- Open in detail + open source in VS Code
- Filters: All / Open / FIXME / Completed / Resolved / Stale / by app / by file
- Local priority / notes / defer

### MAY defer to v1.1+

- Export TODO-debt report (CSV/markdown)
- Bulk note / bulk priority editing
- Fuzzy TODO search beyond the substring filter
- GitHub Issues sync
- AI TODO summaries / clustering
- **Code-comment auto-edit** (kept hard-blocked in v1)
- Occurrence-ordinal disambiguation for identical-text collisions (§ 4)
- Cross-file move detection (same text, different file → currently resolved-here + new-there)
- Scanner-side `todo_id` emission (PCC computes it in v1)

---

## 11. Risks & stop conditions

| Risk | Mitigation / Stop |
|------|-------------------|
| md toggle corrupts a file | single-line flip + pattern assertion + atomic write + post-toggle re-scan; **STOP** + error toast if the line no longer matches the expected `_MD_OPEN`/`_MD_DONE` shape |
| False "Resolved" hides real debt | unreadable/missing file → `needs_review`/`missing_file`, never `resolved`; resolution asserted only on readable-file + genuine-absence |
| Identity collision (same text twice in a file) | shared overlay in MVP (acceptable, low-frequency); ordinal disambiguation deferred (§ 10) |
| Editing a file the scanner is mid-reading (QThread race) | toggle only on the main thread, between scans; block toggle while a scan is in-flight |
| Operator edits source outside PCC during a session | next Verify reconciles; local state is overlay, file always wins |
| Performance on huge TODO sets | reuse the search MVP's bounding (cap rows rendered; the join is O(todos)); no full re-parse — consume cached scan payload |
| Scope creep into PM/kanban | hard constraint; spec explicitly excludes (§ 2) |
| **Scanner-contract pressure** | none expected — if verification "needs" a scanner change, **STOP** and re-evaluate (constraint: don't change scanner contracts unless absolutely required) |
| **Touching production app source** | the md toggle writes only to repos under the operator's configured root (dev working copies), never to installed payloads or via the scanner; if a target path resolves outside the configured root, **STOP** |

---

## 12. Recommendation

### **A — include a bounded MVP in PCC v1 before RC.**

The operator has made cross-app TODO management a v1 requirement, and the foundation is already present (scanner payload, detail TODO tab, search routing) — so the Workbench is an *additive management layer*, not new infrastructure, and needs **no scanner-contract or commons change**. The MVP boundary in § 10 keeps it tight: read + verify + md-toggle + filters + local overlay, with PM-system features and code-comment editing explicitly out.

**Caveats for the operator (§ 13 decisions):**
- This is the **largest single v1 workitem** — ~1–2 sessions on top of the small-fixes phase, and it sequences *after* V1-1..V1-5 (don't block the updater-UI/version-policy fixes on it).
- The only source-mutating capability (md checkbox toggle) carries the only real risk; if the operator prefers a **read-only v1 Workbench** (view + verify + open-in-editor + local overlay, *no* in-app toggle), that removes the highest-risk piece and still delivers "Ground Control for TODO debt." That's the recommended fallback if v1 timeline is tight.

**Decision split:**
- **A1 (recommended):** full bounded MVP incl. safe md-toggle in v1.
- **A2 (lower-risk):** read-only Workbench in v1 (verify + open + overlay); md-toggle to v1.1.
- **B:** defer the entire Workbench to v1.1 (only if the operator wants the 4 small fixes + updater UI shipped fastest).

---

## 13. Operator decisions needed

1. **Include in v1?** A1 (full MVP w/ md-toggle) · A2 (read-only Workbench, toggle→v1.1) · B (defer all to v1.1). *Recommend A1, fall back to A2 if timeline-sensitive.*
2. **Nav placement** — Ctrl+3 top-level view (recommended) vs a tab within an existing view.
3. **"Clear resolved" retention** — keep resolved overlay forever vs auto-prune after N scans.
4. **Sequencing** — confirm Workbench runs **after** the audit's V1-1..V1-5 small fixes (so updater-UI + version policy aren't blocked).

---

## Confirmation

- **No implementation performed** — spec only.
- **No source code changed** in PCC, commons, or any app.
- **No scanner contract changed** (the existing `get_todos` payload is sufficient).
- **No commons architecture change.**
- **No build, no release, no publish.**

*PCC TODO Workbench MVP spec complete. Awaiting operator decisions (§ 13) before implementation; the paused PCC v1 small-fixes prompt resumes once scope is confirmed.*
