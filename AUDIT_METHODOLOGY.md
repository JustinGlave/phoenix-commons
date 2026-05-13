# Code Audit Methodology — Verify Before Claiming

A reusable process for auditing a desktop / file-backed application for real bugs. Designed for use with an AI coding assistant; lessons baked in from a failed first-pass audit where multiple agents reported "confirmed" bugs that didn't match the code.

---

## Rule 0 — Trust no claim without a code reference you have personally read

The most important rule. AI audit tools hallucinate line numbers, repeat generic anti-patterns that don't apply, and label fabricated findings as "verified." Every finding must have:

- **File path** that exists in the repo (verify with Glob or directory listing).
- **Line number range** where the code actually lives (verify with Read or Grep).
- **The actual code that triggers the bug**, quoted or paraphrased from what you read.
- **A concrete failure mode** — what happens to the user, what data is wrong, what crashes.

If you can't write all four, it's not a finding. Re-verify or discard.

---

## Phase A — Scope and budget

Before any tool reads a single line:

1. **List the modules.** Count files and lines. Decide which are in scope. (Typical: main UI, main backend, auth, updater, persistence layer, any external-format parser.) Note files you're skipping and why.
2. **Set a finding cap.** ~15–20 verified bugs is the target for an app this size. More than that and you're listing nitpicks; fewer and you're under-searching. The cap forces prioritization.
3. **Define severity.**
   - **Critical**: silent data corruption, security bypass, can lose user work.
   - **High**: visible incorrect data, role bypass, crashes in the common path.
   - **Medium**: edge-case crash, performance under load, recoverable wrong-state.
   - **Low / known-limitation**: theoretical, requires unusual conditions, documented elsewhere.

---

## Phase B — High-yield categories (work through these in order)

Each category has a specific search pattern and a specific failure to look for. Don't go top-to-bottom in code; go category-to-category.

### B1. Persistence atomicity

The single highest-yield area for a file-backed app. **Read each save function fully.** Look for:

- **Temp file + atomic rename?** `tempfile.mkstemp` then `Path.replace` (or `os.replace`) is correct on Windows/Linux. A bare `open(path, "w")` is **not atomic** — partial writes corrupt the file.
- **Retry on `PermissionError` for cloud-sync locks?** OneDrive/Dropbox/iCloud briefly lock files; without retry, saves fail randomly.
- **`fsync` before rename?** Best-practice for crash safety. Often omitted; only mark as a real finding if the app's threat model includes power loss.
- **Cache mutation before save.** If `_load` returns the same dict each time and callers mutate it, then `_save` raises — the in-memory cache is now out of sync with disk. Subsequent reads will return uncommitted changes. Look for `return self._cache` or `return data` that's a reference to a shared field.
- **Multi-step writes that should be one save.** If function A saves, function B saves, and a crash between them leaves state inconsistent — that's non-atomic. `reset_password` calling `change_password` then a second `_save` is a textbook example.

### B2. Auth, session, and password

- **Password hashing**: bcrypt, scrypt, argon2, or PBKDF2 — none of `sha256(password)`, `md5`, no salt. Look up current OWASP iteration count (changes every couple years).
- **Comparison**: `secrets.compare_digest` or `hmac.compare_digest`, not `==`. (Timing attacks on local files are mostly theoretical, but the cost of fixing it is zero.)
- **Remember-me tokens**: stored as **hashes**, not the plaintext token. Both must agree to authenticate.
- **Session expiry**: stored with timezone or as UTC; naive local time changes meaning when the clock changes.
- **Password change must invalidate sessions.** Verify the call chain: `change_password → clear_session_token`.
- **Forced-password-change must not be cancelable.** Trace the call site: does the caller check the return value or just call `.exec()` and continue?
- **`users.json` co-located with shared data?** If both files live on a shared OneDrive folder, role-based access is effectively trust-based. Document as a known limitation.
- **First-run path.** What happens if `users.json` doesn't exist? Some apps fall open to "admin"; that's fine *only* if no other users exist. Check what happens after a user *deletes* `users.json` — does the next run still grant admin?

### B3. Auto-updater

This is the most security-sensitive surface in a desktop app.

- **Version comparison**: tuple-of-ints works for `1.2.3` but breaks on `1.2.3a`, `1.2.3.dev0`, etc. Test edge cases on paper.
- **Unparseable tag handling**: if `parse("garbage")` returns `(0,)`, comparisons either always-update or never-update. Both are bad.
- **Download integrity**: HTTPS provides authenticity for the URL, but a hash or signature check is defense-in-depth. Without one, anyone who can compromise the release host can ship malware.
- **Zip-slip**: when extracting, every entry's resolved path must stay inside the destination. Don't rely on `Expand-Archive` or `extractall`; iterate `namelist()` and reject `..` or absolute paths.
- **Partial downloads**: does an interrupted download leave a half-file behind? Does the next run resume or re-download from scratch?
- **Restart race**: if the new exe replaces the running one, the OS may or may not let you. On Windows, the typical pattern is a tiny .bat/.ps1 that waits for the parent PID to exit, then copies — verify that PID-wait isn't vulnerable to PID reuse.
- **Cleanup on failure**: temp zip, staging dir, batch script — are all deleted if extraction fails midway?

### B4. External-format parsers (Excel, CSV, JSON imports)

The hardest to audit because the bugs only fire on malformed inputs.

- **Hardcoded cell addresses or column indices.** If the template ever changes, the import silently reads garbage. Look for `sheet["H3"]`, `vals[7]`, `row[3].value` without a header-search fallback.
- **No file-type validation.** Does the function trust the file extension and try to parse anyway? A user can pick a totally unrelated `.xlsx` and the parser will return whatever happens to be in those cells.
- **Type coercion crashes.** `int(cell)` or `float(cell)` on a cell that contains a string. Wrap with `try/except` and decide whether to skip the row or abort the import.
- **Length checks.** `vals[col_index]` without `if len(vals) > col_index`. Trailing empty columns make this an IndexError.
- **Sheet-detection fragility.** "Find the sheet whose row 8 col 1 says 'Job Number'" — what if it's row 7? What if the workbook has whitespace before "Job"?

### B5. GUI state machine (Qt / PySide6 / tk / wx)

- **Signal-connection leaks.** A method that calls `widget.signal.connect(handler)` and is itself called more than once will connect N times. Each event fires the handler N times. Look for connect calls inside `_reload`, `_refresh`, `_init_xxx` that are *also* called from `__init__`. Either disconnect first or guard with a "connected" flag.
- **Stale `current_X` after reload.** If `_on_data_changed` replaces the backend but doesn't reset `current_project_id`, the UI keeps trying to display the old ID even if it was deleted. Compare the file-watcher path to the manual-reload path — they should clear state identically.
- **Lambda variable capture in loops.** `for x in items: btn.connect(lambda: do(x))` captures `x` by reference; all lambdas see the last value. Use `lambda x=x: do(x)` or `functools.partial`.
- **Dialog kept alive only by `.exec()`.** Modal dialogs that aren't stored in a variable can be GC'd before they return. Usually safe with `.exec()` because it blocks, but worth flagging when in doubt.
- **Repopulate during edit.** If a background thread or timer fires `populate_table` while the user is editing a cell, their edit is lost. Look for `_populating` flags or `blockSignals` calls.
- **Bulk operations doing N saves.** `for task in tasks: backend.update_task(task.id, ...)` rewrites the JSON file N times. For 30 tasks that's 30 sequential disk writes — the UI freezes. Look for the pattern and propose a single-save batch method.

### B6. Role-based access

- **Backend enforces nothing.** If the only role check is in the GUI, document this as the trust model — don't pretend it's enforced.
- **GUI checks are complete?** Every action button needs a role check (either hidden or explicit guard). Easy to miss one. Grep for `self.backend.delete_` and `self.backend.create_` calls and verify each has a guarding `if self._current_user_view_only(): return`.
- **First-run admin trap.** Confirm what happens if a user with file access deletes `users.json`. If the answer is "they get admin next launch," that needs to be in the threat model docs, not just emergent behavior.

### B7. Logs, backups, and growing-without-bound data

- **Activity logs / audit logs**: any rotation, cap, or age-out? If not, document as Medium and propose a FIFO cap.
- **Backup rotation**: keep-N logic correct? Off-by-one easy. (`backups[:-10]` keeps the last 10; `backups[:-N]` deletes oldest. Verify.)
- **Backup-before-restore?** Critical operation must pre-back-up the live file so a bad restore can be undone manually.
- **Backup failures swallowed?** `except OSError: pass` on backup creation means users have no idea backups have been failing for weeks. Always log + surface.

### B8. Concurrency model

If multiple processes can hit the same file (shared OneDrive folder, multi-user app):

- **No file locks?** Two simultaneous saves can lose updates. For a tiny team this is acceptable; document it.
- **Last-write-wins** is the only behavior; the app doesn't merge changes.
- **File-watcher debounce**: how long? Too short = thrashing on rapid sync events. Too long = stale UI.

---

## Phase C — Verification protocol

For each candidate finding from Phase B:

1. **Open the file and read the function in full.** Not a 5-line excerpt. The full function, plus the function that calls it, plus the function it calls.
2. **Trace the failure path.** "If X is the bug, then under condition Y the user sees Z." Write Y and Z down. If you can't, it's not a finding.
3. **Verify the line number.** Use Grep with a distinctive pattern from the code you just read; the line number it returns is the authoritative one.
4. **Check the version history if available.** `git log -p path/to/file` for the section often reveals that the "bug" was fixed last month or that the comment explaining it is in the commit message.
5. **Look for the existing protection.** Before claiming "no validation," grep for `except`, `validate`, `check`, `if not` near the candidate site. The fix may already be there one frame up the stack.
6. **Distinguish bug from limitation.** A single-user JSON-backed app has known limitations (no concurrency, no role enforcement at storage). Those aren't bugs; they're the trust model. Call them out, but in a separate section.

---

## Phase D — Output format

Findings table, one row per verified bug:

| # | Severity | File:Lines | Title | Failure mode | Fix sketch |
|---|----------|------------|-------|--------------|------------|
| 1 | High | `backend.py:1735-1755` | Activity log unbounded | After ~1 year of normal use, JSON load time noticeable; eventually GBs | FIFO cap at 50k entries on every write |

End with three sections:

- **Verified bugs** (the table above)
- **Known limitations** (architectural choices that look like bugs but are intentional)
- **Findings that turned out to be false** (briefly — so the next auditor doesn't re-investigate)

---

## Anti-patterns to avoid in your own audit prompts

When delegating audit work to an AI sub-agent, these prompts give bad output:

- ❌ "Find bugs in this file." — Returns generic Python anti-patterns regardless of the code.
- ❌ "Are there any security issues?" — Returns OWASP top-10 reasoning unconnected from the actual code.
- ❌ "Verify each of these claims." — Agents will report "confirmed" without actually verifying.
- ❌ "Look for race conditions." — Without context, every signal/slot looks racy.

Good prompts:

- ✅ "Read [specific functions]. For each, identify what happens when [specific failure mode]. Give me file:line for each finding."
- ✅ "Find all call sites of `backend.delete_*`. For each, does a role check guard the call? Quote the guard or note its absence."
- ✅ "Grep for `setStyleSheet(` and list each call site. For each, is the style also defined in the QSS? Quote both."

The pattern: **specific code locations + specific failure modes + verbatim quotes**. Vague questions get vague answers.

---

## Quick checklist for the next project

Before declaring an audit complete, you should be able to answer "yes" to all of:

- [ ] I read each save function end-to-end and confirmed it's atomic (temp + rename) and retries on lock.
- [ ] I traced the auth flow from login → session → password-change → session-clear and confirmed each step.
- [ ] I read the updater end-to-end including version parse, download, validate, extract, restart.
- [ ] For every external-format import, I identified the columns/cells/keys assumed and whether they're validated.
- [ ] I grepped for `connect(` and confirmed no signal connection happens in a method called more than once without first disconnecting.
- [ ] I grepped for every `backend.delete_*` and `backend.create_*` call and confirmed a role check guards it.
- [ ] I confirmed activity/audit logs have a cap or rotation policy.
- [ ] I confirmed backups have rotation, pre-backup-before-restore, and surface failures.
- [ ] I checked what happens when the user database is deleted.
- [ ] Every finding in my report has a file:line I personally read.

If any of those are "no," go back to that category before publishing.
