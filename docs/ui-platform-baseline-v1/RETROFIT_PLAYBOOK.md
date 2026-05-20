# RETROFIT_PLAYBOOK.md

> **Operator field manual for executing a single Phoenix tool retrofit
> end-to-end.** Distillation of Phase 3A (Phoenix CAD) and Phase 3B
> (Phoenix Checkout) practice into checklist form.
>
> **Status**: outline / first draft. Authored 2026-05-19 during the
> Operational Convergence Phase for later audit review.
>
> **This is NOT**:
> - a second `MIGRATION_RULES.md` (that document is the source of truth for *why*; this document is *how*)
> - a philosophy document
> - an architecture manifesto
> - a place to invent new framework systems
>
> **Cross-references** (canonical):
> - `MIGRATION_RULES.md` — retrofit doctrine; every step here cites a rule there
> - `RETROFIT_PR_TEMPLATE.md` — PR body template
> - `RELEASE_CHECKLIST.md` — post-retrofit release procedure
> - `production-inventory.md` — frozen Phase 0 baseline per tool

---

## How to use this playbook

1. Pick the next tool from `MIGRATION_RULES.md` § Migration order.
2. Walk through phases P0 → P9 in order. Each phase has a numbered
   checklist; check items as you complete them.
3. If any STOP condition triggers, halt and consult the cited rule.
4. Author the post-retrofit report when P8 completes.

A typical retrofit takes **1–2 sessions of focused work** plus a
2-week MIGRATION_RULES § Frequency-limit cooldown before the next
tool starts.

## Intentional divergence: monolith vs modular topology

**Application structure follows domain history.** The retrofit
doctrine supports both shapes equally; subsystem convergence is NOT
a platform goal. The playbook applies to either shape — only the B5
commit pattern differs.

| Shape | Example | B5 retrofit pattern |
|-------|---------|---------------------|
| **Modular** (separate platform-helper files: `paths.py`, `updater.py`, `ui/style.py`, `ui/components.py`) | Phoenix CAD / Lab Layout Tool | Whole-file facade per `MIGRATION_RULES.md § 1` |
| **Monolithic** (inline widget classes + inline theme in one large GUI module) | Phoenix Checkout (`checkout_tool_gui.py`, ~3,468 lines) | Inline-import per `MIGRATION_RULES.md § 11` |

Both shapes are valid post-retrofit. The playbook does NOT push tools
toward one shape. Decisions about future structural refactors are
out of any retrofit's scope (see Anti-patterns below).

---

## P0 — Pre-flight (all items required before opening a branch)

- [ ] Tool's working tree is clean (`git status` empty)
- [ ] Tool's `main`/`master` is up to date with origin (`git pull --ff-only`)
- [ ] Tool's pinned commons SHA noted (if already on commons) OR
      decision made on which commons SHA to pin (if new retrofit)
- [ ] **WIP isolation procedure** per MIGRATION_RULES § 9 executed if
      the tool has unfinished feature work parked on `main`
- [ ] `production-inventory.md` row for this tool read; AppId,
      install path, user-data path, zip asset name, exe name noted
      verbatim (these are the binding invariants)
- [ ] User authorisation to begin (the cooldown window from the
      previous retrofit's merge has elapsed per MIGRATION_RULES
      § Frequency limits)

## P1 — Commons-API gap inventory (per MIGRATION_RULES § 0)

- [ ] List every local platform helper file in the tool (`paths.py`,
      `updater.py`, `ui/style.py`, `ui/components.py`, inline
      widget classes in monolithic GUI files, etc.)
- [ ] Map each local symbol to its commons equivalent (`phoenix_commons.*`)
- [ ] For every gap (symbol with no commons equivalent), choose:
      - **A. Keep local** (default) — document why in retrofit report
      - **B. Add to commons** — requires evidence of ≥ 2 consumers;
        pause retrofit, land commons PR first
- [ ] **User approval required** on each Option-A/B decision before
      proceeding to P2

## P2 — Branch setup

- [ ] Branch name `phase-<id>-<tool-slug>-retrofit` off the tool's
      `main`/`master` at the clean baseline
- [ ] Branch pushed to origin with `-u` so the audit trail is durable
- [ ] No production-tool code touched yet

## P3 — Surgical commits (the B-series)

Land changes as **many small logical commits**, not one mega-commit.
Phase 3A pattern (7 commits) and Phase 3B pattern (7 + 1 regression
fix) are the canonical references.

Each commit independently passes `compileall` + the local import
smoke (P4 checklist below). Each commit message follows the form:
`<verb> <subsystem> (Phase <id> B<n>)`.

Typical commit series:

- [ ] **B1** — Add commons submodule + `requirements.txt` entry +
      `.gitmodules`
- [ ] **B2** — Retrofit one platform helper file (e.g. `paths.py`)
      to commons facade
- [ ] **B3** — Retrofit `updater.py` (preserve any tool-specific
      payload contract — exe-only vs full-folder per ADR-003)
- [ ] **B4** — Retrofit theme load (delete `_EMBEDDED_QSS` body
      after verifying commons fallback)
- [ ] **B5** — Retrofit widget definitions to commons re-exports
      (for monolithic files use § 11 inline-import pattern;
      for helper-file shapes use whole-file facade)
- [ ] **B6** — Preserve legacy QSS under `legacy/phoenix_style.qss.preretrofit`;
      delete repo-root copy
- [ ] **B7** — Update `build.bat` with submodule preflight +
      `--collect-all=phoenix_commons`
- [ ] (As-needed) **Bn** — regression-fix commits surfacing during
      validation (cf. Phase 3B B8 — the import-removal lesson)

## P4 — Per-commit verification (run after every B-commit)

- [ ] `python -m compileall -q -x "(\.venv|build|dist|commons)" .` exits 0
- [ ] `python -c "import phoenix_commons; print(phoenix_commons.__version__)"`
      succeeds (confirms submodule + editable install)
- [ ] No identity drift on retrofitted widgets (run identity check
      from P7 row 3 informally)

## P5 — Whole-file import-removal audit

**Mandatory** after any commit that removes a top-level `import X`
from a file. Catches the Phase 3B B8 class of regression
(MIGRATION_RULES § 10 row 11 corollary).

- [ ] `git grep -nE "\\bX\\." <file>` returns zero hits for the
      removed module's namespace use
- [ ] If hits exist, re-add the import in a follow-up commit (do not
      amend a previous commit; new commit per § 5 "Duplicate-removal
      sequencing")

## P6 — Source-mode launch (the retrofit gate)

Per MIGRATION_RULES § 10 row 11 — this is the gate. `compileall` and
import-only smoke are insufficient.

- [ ] Launch the tool source-mode:
      ```powershell
      $p = Start-Process -FilePath '.venv\Scripts\pythonw.exe' `
          -ArgumentList '<entry-script>.py' `
          -WorkingDirectory '<tool-root>' -PassThru
      Start-Sleep -Seconds 4
      $alive = Get-Process -Id $p.Id -ErrorAction SilentlyContinue
      ```
- [ ] Process is alive ≥ 3 seconds (4 recommended)
- [ ] `MainWindowTitle` matches the expected app title
- [ ] No exception trace on stderr / log file

## P7 — Final validation (MIGRATION_RULES § 10 — all 11 rows)

| Row | Check | Pass criterion |
|-----|-------|----------------|
| 1 | `compileall` | exit 0 |
| 2 | imports clean | no errors |
| 3 | widget identity `is commons.WidgetClass` | True |
| 4 | updater config constants preserved | match pre-retrofit values |
| 5 | `download_and_apply` source contains expected `expected_internal=` (or docstring documents exe-only contract) | match payload contract per ADR-003 |
| 6 | `<APP_CONSTANT>` paths resolve to pre-retrofit values | match exactly |
| 7 | offscreen `apply_dark_theme` + widget construction | no exceptions; styleSheet substantial; brand hexes present; no `__BRAND_*` sentinels |
| 8 | offscreen `import <entry-module>` | no exceptions |
| 9 | submodule SHA on commons main (or intentional older SHA — documented) | matches |
| 10 | commons-side `pytest -q tests/` | all pass |
| 11 | actual source-mode launch alive ≥ 3 s | PASS per P6 |

Any failing row blocks merge.

## P8 — Manual QA (operator + user)

Operator launches; user drives. Cover the tool's user-facing surface,
with extra scrutiny on any preserved-local paths surfaced in P1:

- [ ] Theme toggle (if tool has light/dark)
- [ ] Updater banner / dialog responsiveness (no UI freeze on
      check-for-updates)
- [ ] Menu actions
- [ ] Forms / input validation
- [ ] Tables (sorting, selection, hover)
- [ ] Dialogs (file pickers, confirmations, error popups)
- [ ] QSettings persistence (close + reopen)
- [ ] Visual parity vs pre-retrofit memory (spacing, hover, density)

User reports findings. Operator resolves blockers in the retrofit
branch before P9.

## P9 — Merge readiness (7-question assessment)

Answer all 7 explicitly. HIGH confidence required to merge.

1. Source-mode launch verified after all fixes? (YES / NO)
2. § 10 checklist all 11 rows green? (YES / NO)
3. User manual QA passed? (YES / NO)
4. Retrofit branch contained — no business-logic / scope drift? (YES / NO)
5. Commons contamination? (YES / NO — should be NO)
6. All B-commits pushed to origin? (YES / NO)
7. Doctrine additions reviewed + landed on commons main? (YES / NO if any new doctrine was codified)

If any answer breaks confidence → halt, fix, re-assess. Do not merge
on partial confidence.

## P10 — Merge execution

- [ ] `git checkout main`/`master` (whichever the tool uses)
- [ ] `git pull --ff-only origin <branch>`
- [ ] `git merge --no-ff phase-<id>-<tool>-retrofit -m "Retrofit <App Display Name> to commons-backed (Phase <id>)"`
- [ ] `git push origin <branch>`
- [ ] Verify remote tip matches local: `git ls-remote origin <branch>`
- [ ] **Retrofit branch preserved on origin** — do NOT delete
      (MIGRATION_RULES § Per-retrofit branch + PR convention)

## P11 — Post-merge validation

Re-run a subset of P7 on the merged `main`:

- [ ] Row 1 (`compileall`) on `main`
- [ ] Row 2 (imports + identity equality)
- [ ] Row 7 (offscreen theme smoke)
- [ ] Row 11 (actual source-mode launch on `main`)

No PyInstaller, no installer, no frozen verification (unless the
release-prep cycle explicitly authorises it — see `RELEASE_CHECKLIST.md`).

## P12 — Tag decision

Default: **SKIP** unless an explicit release version is being claimed.
Phase 3A and 3B both skipped tagging — `version.py` unchanged; existing
`vX.Y.Z` tag still points at the pre-retrofit commit; the retrofit
ships with the next normal release.

- [ ] If skipping: note in the post-retrofit report § Tag decision
- [ ] If tagging: follow `RELEASE_CHECKLIST.md` § Release execution

## P13 — Status row update

In `MIGRATION_RULES.md` § Migration order, flip the tool's row from
its current state to:

```
✅ Merged YYYY-MM-DD (merge commit `<sha>` on `<repo>:<branch>`).
Retrofit work: B1–Bn (`<first-sha>`..`<last-sha>`). Doctrine additions
in this document codified from <retrofit-report> + <post-review-report>.
Retrofit branch preserved on origin per ...
```

Commit as part of the post-review report commit.

## P14 — Author post-retrofit report

Two reports total (Phase 3A and Phase 3B precedent):

- **Retrofit execution report** (`PHASE_<id>_<TOOL>_REPORT.md`) — authored
  during retrofit work; covers pre-flight, B-commits, validation results
- **Post-review and merge report** (`PHASE_<id>_POST_REVIEW_AND_MERGE_REPORT.md`)
  — authored post-merge; covers manual QA findings, doctrine
  additions, merge readiness 7-question assessment, post-merge
  validation, tag decision, MIGRATION_RULES row flip

Both saved to `phoenix-commons/docs/ui-platform-baseline-v1/`.

## STOP conditions (any one triggers halt + user consultation)

Per `MIGRATION_RULES.md` § Stop conditions:

- Need to modify a commons-owned file mid-retrofit
- Need to change `AppId`, install path, or user-data path
- Need to change zip asset name or exe name
- Frozen-exe verification fails for a reason NOT documented in
  `BLOCKERS.md`
- A test passes on `main` but fails on the retrofit branch
- Visible-change band for the tool is exceeded (per
  `MIGRATION_RULES.md` § Screenshot baseline requirements)

## Anti-patterns (do NOT do these during a retrofit)

- ❌ "While we're here" cleanup of unrelated code
- ❌ Modernisation of business logic
- ❌ Renaming variables, files, or directories outside the retrofit's
  surgical scope
- ❌ Adding new features
- ❌ Adding new dependencies beyond `phoenix_commons` (-e ./commons)
- ❌ Extracting a monolithic file's inline classes to a new file
- ❌ Editing commons source as part of the retrofit (commons changes
  are a separate PR per MIGRATION_RULES § 0 Option B)
- ❌ Amending or force-pushing during the B-series
- ❌ Skipping the source-mode launch gate because `compileall` passed

## Templates referenced

- `RETROFIT_PR_TEMPLATE.md` — PR body
- `RELEASE_CHECKLIST.md` — release procedure (post-retrofit, when a
  version is bumped)
- `PHASE_3A_PHOENIX_CAD_REPORT.md` — retrofit-execution report template
- `PHASE_3B_POST_REVIEW_AND_MERGE_REPORT.md` — post-review report template

---

## Draft status

This outline is **the playbook's first draft**. Subsequent passes
should:

1. Flesh out the rare-but-real corner cases each tool hit (e.g.
   Phase 3B B8 — the `import os` removal regression).
2. Add tool-specific notes from `production-inventory.md` per row.
3. Cross-link every checklist item to the specific
   `MIGRATION_RULES.md` rule it derives from.

But content should NOT expand into:

- New doctrine (that goes in `MIGRATION_RULES.md`)
- Architecture rationale (that goes in ADRs)
- Library-development guidance (that goes in `CONTRIBUTING.md`)

The playbook stays a **checklist** — single-page-friendly,
operator-actionable.

| Field | Value |
|-------|-------|
| Phase | Operational Convergence — playbook outline draft |
| Status | 🔵 Outline (draft 1 of n) |
| Date | 2026-05-19 |
| Canonical source for doctrine | `MIGRATION_RULES.md` |
| Saved to | `phoenix-commons/docs/ui-platform-baseline-v1/RETROFIT_PLAYBOOK.md` |
