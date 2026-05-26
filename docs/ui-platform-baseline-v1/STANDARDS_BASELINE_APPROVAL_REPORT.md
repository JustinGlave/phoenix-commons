# Standards Baseline Approval Report

> **Status:** consistency audit complete; baseline approved with minimal corrections applied.
> **Date:** 2026-05-22.
> **Companion to:** `PHOENIX_APP_STANDARD_BASELINE_V1.md`, `APP_ALIGNMENT_CHECKLIST.md`,
> `APP_STANDARDIZATION_READINESS_MATRIX.md`, `MIGRATION_RULES.md`.
> **Purpose:** audit the new standards docs against actual implemented platform reality,
> apply minimal corrections, and certify the baseline is ready to drive Wave 8a pre-flight.

---

## 1. Docs reviewed

  - `PHOENIX_APP_STANDARD_BASELINE_V1.md` (5-category canonical standard)
  - `APP_ALIGNMENT_CHECKLIST.md` (12-section retrofit checklist A-L + anti-checklist)
  - `APP_STANDARDIZATION_READINESS_MATRIX.md` (per-app readiness for ValveMaster / Job Tracker / Screenshot_Tool)
  - `MIGRATION_RULES.md` (retrofit doctrine; Phase 3G row added)
  - Phase 3C through Phase 3G implementation + merge reports (cross-checked for cited claims)

### Verification method

  - **Runtime inspection** of `phoenix_commons.widgets.__all__`, `phoenix_commons.widgets.no_scroll`, `phoenix_commons.icons.registry.ICON_NAMES`, `phoenix_commons.theme.tokens`, `phoenix_commons.paths`, `phoenix_commons.updater` against the doc's claims.
  - **Filesystem inspection** of remaining-app folders (ValveMaster, Job Tracker, Screenshot_Tool) for `MIGRATION_RULES § 0` pre-flight readiness.
  - **Cross-doc reference check** for contradictions, premature requirements, mismatched phase ordering, and incorrect "mandatory" language.

---

## 2. Issues found

### Issue 1 — `AggregateTile` mislabeled as commons primitive (HIGH severity)

  - **Where:** `PHOENIX_APP_STANDARD_BASELINE_V1.md` §1.3 (closed-set table) + §6 (what every app MUST share).
  - **Claim:** AggregateTile is a commons primitive every Phoenix app must use.
  - **Reality:** `AggregateTile` is defined in PCC's `dashboard.py` (PCC-local). Verified absent from `phoenix_commons.widgets.__all__`:
    ```
    __all__ = ['PrimaryButton', 'SecondaryButton', 'TertiaryButton',
               'PageTitle', 'PageSubtitle', 'SectionTitle', 'HintLabel',
               'Panel', 'PhoenixTable', 'StatusBadge', 'UpdateBanner',
               'button_row']
    ```
  - **Impact if not corrected:** Wave 8a pre-flight gap inventory would force a `AggregateTile`-not-in-commons stop-condition mid-retrofit. ValveMaster doesn't have aggregate tiles; Job Tracker may or may not — neither needs AggregateTile to align with the baseline, but the doc was implying otherwise.
  - **Why it matters:** the operator brief explicitly forbade "terms that imply commons ownership when the primitive is app-local."

### Issue 2 — Missing typography widget classes in §1.3 enumeration (LOW severity)

  - **Where:** `PHOENIX_APP_STANDARD_BASELINE_V1.md` §1.3.
  - **Gap:** the table omitted `PageTitle` / `PageSubtitle` / `SectionTitle` / `HintLabel`, which ARE in `phoenix_commons.widgets.__all__`.
  - **Impact:** doc was incomplete but not contradictory — the `#pageTitle` / `#sectionHeader` object-name convention covered the use cases. Apps could still derive correctly. Adding the classes to the enumeration provides full accuracy.

### Issue 3 — `SearchResultsPopup` location ambiguous (FYI only — not an error)

  - **Where:** `PHOENIX_APP_STANDARD_BASELINE_V1.md` does not list `SearchResultsPopup`.
  - **Reality:** `SearchResultsPopup` is PCC-local in `dashboard.py` (Phase 3F).
  - **Impact:** none — baseline doc correctly omitted it. Worth documenting explicitly so future readers understand its scope.

### Issue 4 — Cross-doc consistency: clean (no error)

Verified the checklist + readiness matrix do NOT propagate the AggregateTile mislabel:

  - `APP_ALIGNMENT_CHECKLIST.md` section B (Visual standards): no AggregateTile mention. ✓
  - `APP_STANDARDIZATION_READINESS_MATRIX.md`: no AggregateTile mention. ✓
  - `MIGRATION_RULES.md`: no AggregateTile mention in the Phase 3G row or anywhere else.

So the correction is isolated to the baseline doc.

### Issue 5 — MIGRATION_RULES compatibility: clean (no conflict)

Cross-checked the new standards baseline against MIGRATION_RULES doctrine:

| MIGRATION_RULES item | Standards baseline section | Conflict? |
|----------------------|----------------------------|-----------|
| § 0 Pre-flight commons-API gap inventory | §5.2 | ✓ Mirrored, no conflict |
| § 1 Local facade strategy | §5.1 | ✓ Mirrored, no conflict |
| § 2 Identity-equal widget verification | §5.5 | ✓ Mirrored, no conflict |
| § 3 Sentinel substitution workflow | §1.2 BrandProfile | ✓ Mirrored, no conflict |
| § 4 Submodule init expectations | §4.3 CI shape | ✓ Mirrored, no conflict |
| § 5 Duplicate-removal sequencing | §5.3 | ✓ Mirrored, no conflict |
| § 6 Delete duplication, not behaviour | §5.3 | ✓ Mirrored, no conflict |
| § 7 Drift-vs-extension heuristic | §5.4 | ✓ Mirrored, no conflict |
| § 8 Commit granularity | §4.4 | ✓ Mirrored, no conflict |
| § 9 WIP isolation procedure | A.1 (checklist) | ✓ Mirrored, no conflict |
| § 10 Source-mode validation checklist (11 rows) | §10 + checklist G | ✓ Mirrored, no conflict |
| § 11 Monolith inline-class retrofit pattern | (referenced by Wave 8b row) | ✓ Mirrored, no conflict |
| § Stop conditions | §5.7 | ✓ Mirrored, no conflict |
| § Frequency limits | §A.1 (checklist) + matrix cooldown | ✓ Mirrored, no conflict |
| § Per-retrofit branch + PR convention | §4.2 + checklist E/F | ✓ Mirrored, no conflict |
| § Drift-vs-extension heuristic | §5.4 | ✓ Mirrored, no conflict |
| § Rollback policy | (referenced via single-revert callouts) | ✓ Mirrored, no conflict |

**Conclusion:** the standards baseline + checklist + readiness matrix synthesize MIGRATION_RULES doctrine without introducing new doctrine or contradicting existing rules. **MIGRATION_RULES retains primacy** where any future conflict surfaces.

### Issue 6 — Checklist accuracy review: passes (no error)

Every checklist item is:
  - **Required** (MUSTs are MUSTs)
  - **Testable** (each has a clear pass criterion)
  - **Not aspirational** (no references to non-existent primitives)
  - **Conditionally qualified** where applicable (e.g. `commons-backed apps` qualifier on submodule items, `production tools only` qualifier on frozen-build section H)

No restructuring needed to introduce MUST/SHOULD/MAY tiers — inline qualifiers already provide the conditionality.

### Issue 7 — Readiness matrix language review: passes (no error)

Verified the matrix:
  - Doesn't imply any implementation work has started
  - Cooldown date (2026-06-02) is factual and explicit (14 days after Phase 3B's 2026-05-19 merge)
  - Phase ordering matches MIGRATION_RULES § Migration order (8a → 8b)
  - Screenshot_Tool correctly classified as TBD / unscheduled
  - Blocker lists are scoped (operator approval, cooldown clear, pre-flight gap inventory, WIP isolation)
  - § 8 "Open questions for operator" surfaces 5 pre-Wave-8a decisions without making them

No corrections needed to the matrix.

---

## 3. Corrections made

### Correction 1 — `PHOENIX_APP_STANDARD_BASELINE_V1.md §1.3`

**Before:**
  - Table row: `AggregateTile | Dashboard metric tile with leading Lucide icon + subtitle`
  - "Apps MUST use these primitives" applied across all table rows

**After:**
  - `AggregateTile` row **removed** from the closed-set table.
  - **New subsection added** below the table: "App-local primitives that are NOT in commons today" — explicitly classifies AggregateTile (and SearchResultsPopup) as PCC-local reference patterns, with the two-consumer-evidence promotion path called out.
  - Closed-set table updated with the typography widget classes (`PageTitle` / `PageSubtitle` / `SectionTitle` / `HintLabel`) which were missing from the enumeration but ARE in commons `__all__`.
  - The `no_scroll` family row clarified to indicate it's imported from the `widgets.no_scroll` submodule (not the `widgets` package root).

### Correction 2 — `PHOENIX_APP_STANDARD_BASELINE_V1.md §6`

**Before:**
> Commons primitives (Panel / StatusBadge / Primary / Secondary / TertiaryButton / PhoenixTable / UpdateBanner / **AggregateTile** / no_scroll family)

**After:**
> Commons primitives from `phoenix_commons.widgets.__all__` (Panel / StatusBadge / Primary / Secondary / TertiaryButton / PhoenixTable / UpdateBanner / **PageTitle / PageSubtitle / SectionTitle / HintLabel / button_row**) and `phoenix_commons.widgets.no_scroll.*` (NoScroll* family)

Cites `__all__` as the runtime source of truth.

### What was NOT changed

Per the operator brief's "Do NOT rewrite the standards docs stylistically":

  - No prose rewrites of correct material.
  - No new sections added beyond the §1.3 sub-section needed to reclassify AggregateTile.
  - No new ADR / no new doctrine.
  - No promotion of AggregateTile to commons (explicit non-goal in the brief).
  - No changes to the checklist (already accurate).
  - No changes to the readiness matrix (already accurate).
  - No changes to MIGRATION_RULES (Phase 3G row already correct; no doctrine conflicts).

### Diff scope

  - Single file modified: `PHOENIX_APP_STANDARD_BASELINE_V1.md`
  - Two edits: §1.3 (closed-set table + new sub-section) and §6 (must-share enumeration)
  - This file appended: `STANDARDS_BASELINE_APPROVAL_REPORT.md` (new)
  - No PCC source-code changes
  - No commons API changes
  - No BrandProfile changes
  - No app code touched

---

## 4. Remaining open questions

These are surfaced from the readiness matrix § 8 + this audit. They do NOT block standards approval — they're the operator-decision questions that need answers BEFORE Wave 8a opens.

### From the readiness matrix

  1. **Wave 8a target version.** Does ValveMaster bump `version.py` as part of the retrofit, or follow the Phase 3B tag-skip pattern?
  2. **Wave 8a screenshot baseline.** Where to keep before/after screenshots for the high-visible-change theme swap?
  3. **Wave 8b Excel scope.** Does retrofit preserve the financials subsystem as preserved-local (hybrid facade), or does it warrant its own surface-spec doc?
  4. **Screenshot_Tool inclusion.** Skip permanently, defer until 8b closes, or add to `production-inventory.md` now?
  5. **Wave 8 cadence frequency.** MIGRATION_RULES § Frequency limits sets a 14-day floor; operator may want a longer interval.

### From this audit

  6. **AggregateTile promotion path.** Will ValveMaster or Job Tracker actually adopt aggregate tiles? If yes, that's the second-consumer evidence for promotion. If no, AggregateTile stays PCC-local indefinitely.
  7. **Search V2 scope decision.** Standards baseline §10.Recommended Next of the PCC search MVP report explicitly defers fuzzy / persistent / commons-file-content search. Operator confirms this stays deferred indefinitely (i.e. don't open it as a Phase 3H).

None of these questions require code changes to resolve. Each is an operator decision that can be answered in the corresponding phase-kickoff brief.

---

## 5. Final standardization readiness verdict

### **APPROVED with corrections applied.**

The standards baseline trio (`PHOENIX_APP_STANDARD_BASELINE_V1.md` + `APP_ALIGNMENT_CHECKLIST.md` + `APP_STANDARDIZATION_READINESS_MATRIX.md`) is internally consistent, factually correct, MIGRATION_RULES-compatible, and ready to drive Wave 8a pre-flight after operator approval.

### Audit summary

| Audit dimension | Result |
|------------------|--------|
| Commons primitive enumeration accuracy | ✓ Corrected (AggregateTile reclassified; typography classes added) |
| Checklist item accuracy | ✓ Passes — every item testable, none aspirational |
| Readiness matrix accuracy | ✓ Passes — cooldown / phase order / blockers all factual |
| MIGRATION_RULES compatibility | ✓ No conflicts — standards synthesize doctrine without inventing new doctrine |
| Premature requirements | ✓ None — all "MUSTs" are achievable with existing commons API |
| App-local mislabels | ✓ Caught + corrected (AggregateTile); no others found |
| Phase ordering | ✓ Matches MIGRATION_RULES § Migration order (3A → 3B → 3C-3G → 8a → 8b) |
| Cooldown language | ✓ Factual (2026-06-02, explicit derivation) |
| Wave 8a kickoff readiness | ✓ Standards docs do not block; operator approval + 5 open-question answers are the gate |

### What was NOT audited

  - **Individual ValveMaster / Job Tracker / Screenshot_Tool code inspection** — that's the per-retrofit pre-flight gap inventory (MIGRATION_RULES § 0), not this audit's scope.
  - **commons internal implementation details** — only the public `__all__` surface was verified.
  - **Frozen-build recipe correctness** — `FROZEN_BUILD_BASELINE.md` remains authoritative; this audit only verified the baseline doc cites it correctly.

---

## 6. Wave 8a pre-flight readiness

Per Wave 8a's pre-flight requirements in `APP_STANDARDIZATION_READINESS_MATRIX.md § 6`:

| Pre-flight requirement | Status |
|------------------------|--------|
| Operator approval to open the phase | **Pending** (operator's decision) |
| Doctrinal cooldown floor cleared (2026-06-02) | **~11 days from today (2026-05-22)** |
| Pre-flight commons-API gap inventory (MIGRATION_RULES § 0) | **Pending** — happens at Wave 8a kickoff |
| WIP isolation if needed (MIGRATION_RULES § 9) | **Pending** — TBD at kickoff |
| Branch created from `main` at clean baseline | **Pending** — happens at kickoff |
| Branch name follows `phase-8a-valvemaster-retrofit` convention | **Documented** |
| Operator visual-change-band approval for grey→navy swap | **Pending** — happens at kickoff |

**Wave 8a pre-flight CAN begin** after the operator decides to open the phase (no earlier than the 2026-06-02 cooldown floor, but realistically when the operator is ready). The standards baseline + checklist + readiness matrix together provide everything the pre-flight needs to execute consistently.

---

## 7. Recommended next action

  1. **Operator reviews this approval report.**
  2. **Operator answers the 5 open questions in §4** (or defers them to Wave 8a kickoff).
  3. **Operator decides Wave 8a kickoff date** (any time on or after 2026-06-02).
  4. **At Wave 8a kickoff:** author the Wave 8a brief using `APP_ALIGNMENT_CHECKLIST.md` as the structural template and `MIGRATION_RULES § Phase 3A retrofit doctrine` as the implementation template.

No standards-doc edits are blocking. No code changes are needed. No additional ADRs are required.

---

## 8. Confirmation

  - **No implementation occurred.** No PCC source-code changes. No ValveMaster / Job Tracker / Screenshot_Tool / Phoenix CAD / Phoenix Checkout source-code changes.
  - **No app code changed.** All edits are doc-only.
  - **No commons API changed.** No additions to `phoenix_commons.widgets.__all__`. No new icons. No new modules. AggregateTile remains PCC-local; no promotion attempted.
  - **No BrandProfile changes occurred.** PCC orange + teal per ADR-016; other apps use commons `DEFAULT_BRAND`.
  - **No production deployment occurred.** No installer built; no frozen build; no release tagged in this audit.
  - **No Wave 8a work began.** Wave 8a remains operator-gated to the 2026-06-02 doctrinal cooldown floor.
  - **No Wave 8b work began.** Wave 8b stays gated behind Wave 8a's merge + a fresh 14-day cooldown.
  - **No new PCC polish opened.** New Tool Wizard / About / Shortcuts / Push Preview / Search V2 all remain deferred per Phase 3G closure direction.
  - **No new doctrine introduced.** MIGRATION_RULES retains primacy; standards baseline synthesizes existing doctrine without adding to it.

---

*End of Standards Baseline Approval Report. Baseline approved. Wave 8a kickoff awaits operator direction.*
