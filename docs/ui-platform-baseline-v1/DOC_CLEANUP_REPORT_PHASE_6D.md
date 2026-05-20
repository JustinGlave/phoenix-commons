# DOC_CLEANUP_REPORT_PHASE_6D.md

> Small documentation-cleanup pass following the Phase 6D baseline
> integration. Three issues fixed; doctrine meaning preserved.
> No runtime / build / release work. Authored 2026-05-20.

## Scope

| Item | Status |
|------|--------|
| Fix duplicate `## Rollback policy` heading in MIGRATION_RULES.md | ✅ Fixed |
| Clarify merge-strategy tension in MIGRATION_RULES.md | ✅ Fixed |
| Re-check cross-references across 5 doctrine docs | ✅ Audited; one gap fixed |
| Confirm hardened-baseline language consistency | ✅ Verified; consistent via canonical-reference delegation |
| Brief cleanup report (this file) | ✅ |

## Files changed

| File | Change | Commit |
|------|--------|--------|
| `MIGRATION_RULES.md` | Removed duplicate `## Rollback policy` heading; reworded the rollback-single-revert claim to align with `--no-ff` merge policy; removed contradictory squash-before-merge sentence | `0444bb6` |
| `INSTALLER_NOTES.md` | Added cross-references to `ADR-014`, `FROZEN_BUILD_BASELINE.md`, `BUILD_HARDENING_EXPERIMENT_REPORT_03.md`, `BLOCKERS.md § 1` in § See also | `0444bb6` |
| `DOC_CLEANUP_REPORT_PHASE_6D.md` | (this report) | follow-up commit |

Two files, one fix commit, one report commit.

## Exact issues fixed

### 1. Duplicate `## Rollback policy` heading

**Before** (MIGRATION_RULES.md lines 454-456):

```
## Rollback policy

## Rollback policy

| Failure during retrofit | Action |
...
```

Two identical level-2 headers immediately adjacent, with an empty
blank section between them.

**After**: single `## Rollback policy` header.

Root cause: likely a copy-paste artifact from an earlier draft.
No body content was lost (only the empty duplicate heading was
removed).

### 2. Merge-strategy contradiction

The doc carried two implicit policies that contradicted each other:

| Section | Text (before fix) | Implied policy |
|---------|--------------------|-----------------|
| § Rollback policy line 466-468 | "A retrofit PR is always revertable as a single git revert. ... If a retrofit needs more than one commit, squash them in the PR before merge." | Squash-before-merge |
| § Per-retrofit branch + PR convention | "Merge strategy `--no-ff`. Preserve the retrofit branch on origin until the post-review report explicitly clears it for deletion." | `--no-ff` + branch preservation |

These contradict — `--no-ff` preserves multiple commits, squashing
collapses them into one.

**Established practice** (the source of truth) was unambiguous:
- Phase 3A merged 7 B-series commits with `--no-ff`. None squashed.
  Branch `phase-3a-phoenix-cad-retrofit` still on origin.
- Phase 3B merged 7 + 1 regression-fix commits with `--no-ff`. None
  squashed. Branch `phase-3b-phoenix-checkout-retrofit` still on origin.
- The "always revertable as a single revert" property was honored by
  using `git revert -m 1 <merge-sha>` against the merge commit itself,
  not by squashing.

**Resolution**: § Rollback policy rewritten to make this explicit.
- The `--no-ff` merge policy is now stated directly in § Rollback policy
  (it was previously only in § Per-retrofit branch + PR convention).
- The contradictory "squash them in the PR before merge" sentence is
  removed.
- The new text says: single-revert means `git revert -m 1 <merge-sha>`;
  small-commit history is preserved on origin for forensic inspection.

**Doctrine meaning**: unchanged. The `--no-ff` policy + small-commit
preservation was already the established practice. The squash sentence
was the orphan claim. Removing it resolves the tension without
changing what tools or operators are expected to do.

### 3. INSTALLER_NOTES.md missing cross-references

INSTALLER_NOTES.md had 0 mentions of `ADR-014` and 0 mentions of
`BUILD_HARDENING_EXPERIMENT_REPORT_03.md`. As a doctrine doc immediately
downstream of the frozen-build baseline (Inno Setup compresses the
PyInstaller bootloader; the bootloader's survival is what FROZEN_BUILD_BASELINE.md
governs), it should reference its upstream authorities.

**Fix**: added 4 entries to § See also:
- `FROZEN_BUILD_BASELINE.md` (canonical baseline)
- `DECISIONS.md § ADR-014` (Python 3.12 mandate)
- `BUILD_HARDENING_EXPERIMENT_REPORT_03.md` (empirical evidence)
- `BLOCKERS.md § 1` (S1 quarantine history)

No content drift — purely additive cross-references.

## Cross-reference matrix (post-cleanup)

| Doc | References FROZEN_BUILD_BASELINE.md | References ADR-014 | References EXPERIMENT_REPORT_03 |
|-----|--------------------------------------|---------------------|----------------------------------|
| FROZEN_BUILD_BASELINE.md | ✓ (self) | 4 | 4 |
| DECISIONS.md (ADR-014) | 3 | (defines) | 2 |
| RELEASE_CHECKLIST.md | 2 | 1 | 1 |
| INSTALLER_NOTES.md | 2 (was 2; now consistent) | **1 (was 0)** | **1 (was 0)** |
| MIGRATION_RULES.md | 2 | 1 | 1 |

All 5 docs now reference the canonical baseline + ADR + isolation
report at least once.

## Hardened baseline language consistency

Audited the following canonical strings across all 5 docs:

| Token | FROZEN_BUILD_BASELINE | DECISIONS | RELEASE_CHECKLIST | INSTALLER_NOTES | MIGRATION_RULES |
|-------|------------------------|------------|---------------------|-----------------|------------------|
| `Python 3.12` | 10 | 1 | 1 | 2 | 1 |
| `pyinstaller==6.20.0` | 1 | 0 | 1 | 0 | 0 |
| `PySide6==6.10.2` | 1 | 0 | 1 | 0 | 0 |
| `--noupx` | 4 | 0 | 1 | 2 | 1 |
| Stdlib excludes (`tkinter` etc.) | 4 | 0 | 0 | 0 | 0 |
| Step 0 cleanup (`rmdir`) | 1 | 0 | 0 | 0 | 0 |

The pattern is intentional and correct:
- **`FROZEN_BUILD_BASELINE.md`** carries the full canonical baseline definition.
- **`DECISIONS.md § ADR-014`** establishes the Python-version mandate
  and delegates implementation details to the baseline doc (correct
  — ADRs should not restate operational specifics).
- **`RELEASE_CHECKLIST.md`** carries the pinned-version verification
  checks (the operator needs concrete strings to grep `requirements.txt`
  / `requirements-dev.txt` against during pre-release).
- **`INSTALLER_NOTES.md`** mentions `--noupx` and Python 3.12 in
  context of how they feed Inno Setup, but delegates the canonical
  definition to FROZEN_BUILD_BASELINE.md.
- **`MIGRATION_RULES.md § Stop conditions`** mentions the baseline
  by reference (new stop conditions for build-venv-not-3.12 and
  build.bat-missing-hardening); delegates specifics to baseline doc.

No drift. Each doc cites the canonical source rather than duplicating
the content — which is the right delegation pattern. If the baseline
ever changes, only FROZEN_BUILD_BASELINE.md + the wizard template
need to update; the other 4 docs continue to work via reference.

## Whether any doctrine meaning changed

**No.** All three fixes are documentation-cleanup work:

| Change | Doctrine impact |
|--------|------------------|
| Duplicate heading removed | None — empty duplicate, no body content lost |
| `--no-ff` policy made explicit in Rollback section | None — codifies established practice; resolves ambiguity without inventing new behavior |
| "Squash them before merge" sentence removed | None — the sentence contradicted established practice and was the orphan; established practice prevails |
| INSTALLER_NOTES cross-refs added | None — additive only |

The merge-strategy policy is unchanged from what Phase 3A + 3B actually
executed: `--no-ff` + branch preservation + small-commit B-series.
Rollback unchanged: `git revert -m 1 <merge-sha>` against the merge
commit.

## Confirmation

| Item | Status |
|------|--------|
| No production tool source modified | ✅ |
| No production tool .venvs modified | ✅ |
| No production tool build scripts modified | ✅ |
| No installer execution | ✅ |
| No PyInstaller invocation | ✅ |
| No releases published | ✅ |
| No Phase 6C work resumed | ✅ — this is doc cleanup only |
| No new doctrine invented | ✅ — fixes consolidate existing doctrine |
| No runtime code modified | ✅ |
| No wizard template modified | ✅ — Phase 6D's template work landed in commit `9f1f3ea`; this cleanup is doc-only |
| Established practice preserved | ✅ — Phase 3A + 3B `--no-ff` history is now explicitly the documented policy |

## Recommendation on Phase 6C resumption

**Yes — Phase 6C can now resume safely** (subject to explicit user
authorisation to enter the resumption work).

The Phase 6D readiness assessment in
`BUILD_HARDENING_BASELINE_INTEGRATION_REPORT.md § 9` already concluded
that the build-half (steps 1–4 of the Phase 6C plan) is unblocked.
This cleanup pass does not change that assessment — it tightens the
doctrine but does not affect the empirical baseline.

Operationally, the docs are now:
- internally consistent (no contradictions),
- cross-referenced (each downstream doc points at the upstream baseline + ADR + isolation report),
- aligned with established practice (`--no-ff` + B-series + branch preservation).

Recommended next step (when authorised): Phase 6C-A — run a fresh
source-build dogfood under the canonical hardened baseline on a
throwaway scaffold to verify the wizard's emitted hardening works
end-to-end through the build pipeline. This is the lightest-risk
restart point and re-confirms the baseline under fresh conditions
before any installer or deploy work proceeds.

**This cleanup report does NOT itself resume Phase 6C.** It signs off
on the doc state.

## Sign-off

| Field | Value |
|-------|-------|
| Phase | Phase 6D doc cleanup |
| Status | ✅ Complete |
| Date | 2026-05-20 |
| Files changed | 2 in commons (MIGRATION_RULES.md, INSTALLER_NOTES.md) |
| Commits | 1 fix commit (`0444bb6`) + this report commit |
| Doctrine meaning changed | **No** — cleanup only |
| Production-tool source / venvs / build scripts modified | None |
| Runtime work | None |
| Phase 6C resumption | **Recommended when authorised**; not initiated by this cleanup |
| Saved to | `phoenix-commons/docs/ui-platform-baseline-v1/DOC_CLEANUP_REPORT_PHASE_6D.md` |
