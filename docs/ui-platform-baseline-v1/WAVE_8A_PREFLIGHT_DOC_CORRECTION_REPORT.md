# Wave 8a — Pre-flight Doc Correction Report

> **Status:** doc corrections complete + decision record authored.
> **Date:** 2026-05-22.
> **Triggered by:** `WAVE_8A_VALVEMASTER_PREFLIGHT_AUDIT.md` finding that
> ValveMaster's `phoenix_style.qss` is already byte-match canonical System A
> (the audit deflated the readiness matrix's "HIGH visible change" prediction
> to ≈ 0%).
> **Scope:** correct outdated "System B → A visible-theme swap" language
> in active Wave 8a planning docs; create operator decision record;
> publish closure report. No source-code changes.

---

## 1. Docs corrected

### Active Wave 8a planning docs (corrections applied)

| Doc | Site | Before | After |
|-----|------|--------|-------|
| `MIGRATION_RULES.md` § Migration order (Wave 8a row) | line 37 | "Not started — System B → A visible-theme swap. Operator-gated; …" | "Not started — **commons-backed architecture alignment + build hardening + updater/theme/widget facades**. … Expected visible change ≈ 0% (Phoenix-CAD profile). …" |
| `MIGRATION_RULES.md` § Screenshot baseline requirements (visible-change band table) | line 499 | "ValveMaster | High — explicit gray→navy theme swap. Document loudly." | "ValveMaster / Phoenix Master Tool | **≈ 0% (revised)** — the v1.1.0 release already shipped the System A palette …" |
| `APP_STANDARDIZATION_READINESS_MATRIX.md` § 1 Visual drift row | line 58 | "HIGH — System B grey palette (`#1c1c1c`-family). …" | "**LOW** — **revised after pre-flight audit (2026-05-22).** v1.1.0 already shipped the System A palette in `phoenix_style.qss` (byte-match canonical). …" |
| `APP_STANDARDIZATION_READINESS_MATRIX.md` § 1 Expected retrofit risk + Visible-change band rows | lines 63-64 | "MEDIUM-HIGH — visible theme swap (grey → navy) is the largest single visible change …" and "HIGH (per MIGRATION_RULES Screenshot baseline) — explicit gray→navy theme swap. Document loudly in the release note." | "**LOW-MEDIUM (revised)** — facade-only retrofit …" and "**LOW ≈ 0% (revised, Phoenix-CAD profile)** — …" |
| `APP_STANDARDIZATION_READINESS_MATRIX.md` § 6 Pre-flight requirements (row 7) | line 188 | "Operator visual-change-band approval (especially for Wave 8a's grey→navy swap)." | "Operator visual-change-band approval. (Wave 8a: ≈ 0% expected per the pre-flight audit's byte-match verification of `phoenix_style.qss`. Light review only.)" |
| `PHOENIX_APP_STANDARD_BASELINE_V1.md` § 5.6 Screenshot baseline (ValveMaster row) | line 414 | "ValveMaster | High — explicit gray→navy theme swap" | "ValveMaster / Phoenix Master Tool | ≈ 0% (revised 2026-05-22 per `WAVE_8A_VALVEMASTER_PREFLIGHT_AUDIT.md`; …)" |
| `STANDARDS_BASELINE_APPROVAL_REPORT.md` § 6 Wave 8a pre-flight readiness | line 225 | "Operator visual-change-band approval for grey→navy swap | **Pending** — happens at kickoff" | "Operator visual-change-band approval (≈ 0% expected per `WAVE_8A_VALVEMASTER_PREFLIGHT_AUDIT.md`) | **Pending** — light review at kickoff" |

**Total corrected:** 7 sites across 4 doc files.

### Docs NOT modified (intentional — historical record)

These docs reference the outdated "System B → A" language but are NOT corrected because they document state-as-of-the-time-of-authoring:

  - `ADR_PCC_PALETTE_RECONCILIATION.md` — ADR-016; historical doctrine context
  - `DECISIONS.md` — ADR index; ADR-005 (and others) document the ORIGINAL decision rationale
  - `BASELINE_GENERATION_REPORT.md` — Phase 0 historical report
  - `DESIGN_SYSTEM.md` (lines 76, 242) — design system doc; current language is forward-tense ("will" / "is being phased out") which is still accurate (the formalization happens via Wave 8a retrofit)
  - `COMMONS_SCOPE.md` — Phase 2.x scope document
  - `PHASES.md` (line 209) — historical roadmap
  - `OPERATIONAL_STABILIZATION_REPORT_01.md` — historical phase report
  - `PHASE_3B_POST_REVIEW_AND_MERGE_REPORT.md` — historical merge report
  - `PHASE_3D_FINAL_MERGE_REPORT.md` — historical merge report
  - `PHASE_3E_FINAL_MERGE_REPORT.md` — historical merge report
  - `PHASE_3F_FINAL_MERGE_GATE_REPORT.md` — historical merge-gate report
  - `PCC_DASHBOARD_SURFACE_SPEC_V1.md` — references the historical ValveMaster palette in context
  - `PHOENIX_ROLLOUT_SUPERSEDED_NOTICE.md` — superseded by definition; preserved as-is

The rule applied: **active Wave 8a planning docs get corrected; historical records stay intact.** This keeps the doctrinal record honest (the original decisions were made on the original information) while ensuring future planning consumes accurate current state.

---

## 2. Outdated language removed

Specific phrases retired from active Wave 8a planning docs:

  - "System B → A visible-theme swap" → "commons-backed architecture alignment + build hardening + updater/theme/widget facades"
  - "HIGH visible change" / "High — explicit gray→navy theme swap" → "≈ 0%" / "Phoenix-CAD profile" / "LOW (revised)"
  - "Wave 8a's grey→navy swap" → "Wave 8a (≈ 0% expected, light review only)"
  - "MEDIUM-HIGH retrofit risk (visible theme swap is the largest single change)" → "LOW-MEDIUM (facade-only retrofit)"

The corrections preserve cross-references — every revised entry cites `WAVE_8A_VALVEMASTER_PREFLIGHT_AUDIT.md` as the verification source.

---

## 3. Decisions recorded

`WAVE_8A_KICKOFF_DECISION_RECORD.md` (new) captures all 12 operator-decision items from the audit's § 9. Each carries:

  - the decision question
  - the audit's default recommendation
  - operator-approval status (`default-accept` or `operator-must-confirm`)
  - the implementation implication

### Summary of operator-action status

  - **9 decisions can default-accept silently** (audit defaults are conservative + reversible)
  - **3 decisions require explicit operator confirmation** before Wave 8a opens:
      - #2 `requirements.txt` discrepancy — why is it missing?
      - #3 CI shape — preserve `test.yml` and add `ci.yml`, or merge into one workflow?
      - #12 Wave 8a opening date — operator picks a specific date on or after 2026-06-02

The default recommendations represent the audit's professional judgment of what minimizes risk while honoring documented operator preferences (e.g. preserving the ubuntu-matrix CI workflow per CLAUDE.md's "intentional divergence" note).

---

## 4. Remaining operator approvals

Before Wave 8a opens:

  1. **Acknowledge the 6 doc corrections** in §1 (or amend if any wording is wrong)
  2. **Answer the 3 `operator-must-confirm` decisions** in §3 (or accept defaults explicitly)
  3. **Pick the Wave 8a opening date** (on or after 2026-06-02)

Once these three items are settled, the Wave 8a kickoff brief can be authored and execution can begin.

---

## 5. Final kickoff readiness

### **Verdict: B — Ready after operator answers 3 specific decisions.**

Per the operator brief's verdict options:

  - **A. Ready for Wave 8a kickoff after cooldown/operator approval** — close, but 3 decisions need explicit answers
  - **B. Ready after operator answers specific decisions** ← **selected**
  - **C. Not ready** — no; all blocking standards-doc issues are resolved

The audit + corrections + decision record together provide everything the kickoff brief needs. The remaining gating items are 3 operator decisions, all surfaced explicitly in `WAVE_8A_KICKOFF_DECISION_RECORD.md`.

### What's READY

  - ✅ Outdated "System B → A" language corrected in 7 active planning sites
  - ✅ Historical record preserved (12 historical doc references not modified — they document state-as-of-then)
  - ✅ Decision record published with 12 defaults
  - ✅ Cross-doc references consistent (all corrections cite `WAVE_8A_VALVEMASTER_PREFLIGHT_AUDIT.md` as source)
  - ✅ Pre-flight audit (`WAVE_8A_VALVEMASTER_PREFLIGHT_AUDIT.md`) is authoritative for visual-change-band assessment
  - ✅ Cooldown floor language remains factual (2026-06-02; 11 days from today)
  - ✅ B1-B9 retrofit sequence drafted in the audit
  - ✅ 10 Class-C / 0 Class-B / 15+ Class-A commons-API gap inventory complete
  - ✅ Preserved-local domain logic explicitly listed

### What's BLOCKED until operator answers

  - ❌ Wave 8a kickoff brief authoring (depends on 3 `operator-must-confirm` decisions)
  - ❌ Retrofit branch creation
  - ❌ Any ValveMaster source modification
  - ❌ Commons submodule addition to ValveMaster

---

## 6. Confirmation

  - **No implementation occurred.** No PCC, ValveMaster, Job Tracker, Phoenix CAD, Phoenix Checkout, or commons source-code change.
  - **No app code changed.** All edits are doc-only in `phoenix-commons/docs/ui-platform-baseline-v1/`.
  - **No commons API changed.** No new primitives, no new icons, no `__all__` modifications.
  - **No BrandProfile changed.** Defaults in the decision record have ValveMaster using commons `DEFAULT_BRAND`; nothing has been altered yet.
  - **No production deployment occurred.** No installer built, no frozen build, no release tagged.
  - **No retrofit branch created.** Wave 8a's `phase-8a-valvemaster-retrofit` branch awaits operator kickoff approval + the 2026-06-02 cooldown floor.
  - **No commons submodule added to ValveMaster.** B1 task at retrofit kickoff.
  - **No build.bat / installer.iss / requirements / version.py / theme / UI / `.spec` modifications.** All preserved as observed in the pre-flight audit.
  - **Historical doc records intact.** The 12 unchanged doc files keep their original phrasing — the doctrinal record honors what was true at the time of authoring.

---

## Commit summary

Files modified in this session (all docs-only, all in `phoenix-commons/`):

  - `docs/ui-platform-baseline-v1/MIGRATION_RULES.md` (2 sites corrected)
  - `docs/ui-platform-baseline-v1/APP_STANDARDIZATION_READINESS_MATRIX.md` (3 sites corrected)
  - `docs/ui-platform-baseline-v1/PHOENIX_APP_STANDARD_BASELINE_V1.md` (1 site corrected)
  - `docs/ui-platform-baseline-v1/STANDARDS_BASELINE_APPROVAL_REPORT.md` (1 site corrected)
  - `docs/ui-platform-baseline-v1/WAVE_8A_KICKOFF_DECISION_RECORD.md` (NEW)
  - `docs/ui-platform-baseline-v1/WAVE_8A_PREFLIGHT_DOC_CORRECTION_REPORT.md` (NEW — this file)

Total: 4 files modified + 2 new files. Zero source-code touch.

---

*End of Wave 8a pre-flight doc correction report. Awaits operator answers to 3 decisions before Wave 8a opens.*
