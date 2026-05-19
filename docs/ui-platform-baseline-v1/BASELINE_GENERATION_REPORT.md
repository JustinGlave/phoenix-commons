# BASELINE_GENERATION_REPORT.md

> Meta-document. How the v1 baseline was derived, what changed from
> prior rollout assumptions, and what still needs a human decision.
>
> **Not a rollout narrative.** Tables-first, architecture-focused.

## 1. Files created

13 contract files + this generation report, in
`phoenix-commons/docs/ui-platform-baseline-v1/`. All authored in a
single sitting on branch `baseline-v1`, commit `3f16d46`.

| File | Lines | Role |
|------|-------|------|
| `BASELINE.md`            | 130 | Front door + reading guide |
| `CURRENT_STATE.md`       | 207 | Verified/assumed/blocked/deferred state across repos + CI |
| `PHASES.md`              | 222 | Revised ladder (0/1/2/2.1–2.7/3/3A/3B/3C/4/5/6/6A/6B/6C/7/8/9) |
| `PLATFORM_CONTRACT.md`   | 155 | Single ownership + extension points |
| `PACKAGING_CONTRACT.md`  | 165 | Updater contracts A/B, installer/package-data rules, AV gating |
| `MIGRATION_RULES.md`     | 139 | Pilot-first (Checkout + Phoenix CAD), rollback, drift heuristic |
| `NAMING_REGISTRY.md`     | 159 | Canonical names for every external-facing identifier |
| `DESIGN_SYSTEM.md`       | 221 | System A palette, type ramp, spacing, radii, forbidden patterns |
| `COMMONS_SCOPE.md`       | 147 | Belongs/never/app-local + decision matrix |
| `DEPENDENCY_GRAPH.md`    | 220 | Coupling map + blast-radius cheat-sheet |
| `BLOCKERS.md`            | 161 | 7 active blockers with impact/mitigation/owner/next action |
| `DECISIONS.md`           | 227 | ADR log — 9 finalized, 4 deferred, 5 rejected |
| `TODOS.md`               |  84 | Actionable backlog bucketed by horizon |
| `BASELINE_GENERATION_REPORT.md` | (this file) | Meta — how the baseline was derived |

Total: 2,237 + this file. No source code touched. No commons or app
code modified.

## 2. Existing docs referenced

| Source | Used for |
|--------|----------|
| `phoenix-commons/docs/production-inventory.md` (Phase 0) | Per-tool identity table in `NAMING_REGISTRY.md`; updater-contract A/B asymmetry confirmation |
| `phoenix-commons/docs/rollout/phase-1-report.md`, `phase-1a-report.md` | Commons skeleton + housekeeping facts in `CURRENT_STATE.md` |
| `…/phase-2-report.md`, `phase-3-report.md`, `phase-3a-report.md` | Theme + widgets + paths + updater lift status |
| `…/phase-4-report.md`, `phase-4b-local-report.md` | AV blocker evidence (2 of 3 reproductions) for `BLOCKERS.md §1` |
| `…/phase-4c-command-center-init-report.md` | PCC git-repo origin story |
| `…/phase-5*.md` (5, 5A, 5B, blocked-preflight) | Wizard radios + scaffold + UX gap fix; commons-backed gating decision (ADR-007) |
| `…/phase-6-standalone-dogfood-report.md` | AV blocker 3rd reproduction; full evidence chain for `BLOCKERS.md §1` |
| `…/phase-6a-build-template-fix-report.md` | Validator helper extraction (ADR-009) |
| `…/phase-6b-command-center-merge-report.md` | PCC `main` merge state |
| `…/phase-6c-frozen-exe-dogfood-plan.md` | Phase 6C entry conditions in `PHASES.md` and `BLOCKERS.md §2` |
| `…/phase-6c-backup-report.md` | Backup-strategy state in `BLOCKERS.md §7` |
| `phoenix-command-center/docs/known-issues.md` | Canonical S1/AV documentation, cross-linked from `BLOCKERS.md §1` |
| `phoenix-command-center/docs/build_notes.md` | Build pipeline diagram + asset bundling rules in `PACKAGING_CONTRACT.md` and `DEPENDENCY_GRAPH.md` |
| `phoenix-command-center/docs/release_checklist.md` | Release-gate items in `PACKAGING_CONTRACT.md` "Per-retrofit safety checklist" |
| `phoenix-command-center/docs/branding-packaging-report.md`, `build-notes-clarification-report.md` | PCC packaging state in `CURRENT_STATE.md` |
| `phoenix-command-center/LICENSE` | Internal-proprietary clause (ADR-006) |
| Conversation context (Phase 5→6B turns + GUI polish + smoke-test fix) | Cross-checked claims against live decisions; reconciled with what's on `main` today |

## 3. Obsolete assumptions identified

Items from the original unified rollout plan that no longer reflect
intent or reality. Each is replaced by a baseline file's canonical
position.

| Obsolete assumption | Replacement |
|---------------------|-------------|
| Sequential retrofit order (CAD → Checkout → ValveMaster → Job Tracker) | Pilot-of-two: Checkout + Phoenix CAD together. Then 8a (ValveMaster), 8b (Job Tracker). (`MIGRATION_RULES.md`, ADR-004) |
| Commons framed as "shared helpers lifted from production tools" | Commons IS the UI platform: tokens, QSS, widgets, paths, updater, icons, resources. (`BASELINE.md`, `PLATFORM_CONTRACT.md`, ADR-001) |
| Original unified plan's Phase 4 ladder ended at "PyInstaller compatibility verification (gate)" | AV blocker reframes 4 + 6 + 6C + 7 + 8 as a single chain off one root cause. (`BLOCKERS.md` dependency graph) |
| Plan B (vendoring) was a Plan-A-failure fallback | Plan B is now one of three legitimate options in the commons distribution decision (ADR-010); still deferred |
| Commons-backed wizard radio "becomes default once Phase 4 passes" | Specifically: stays non-default until **Phase 6C** (end-to-end frozen-exe, not just PyInstaller compat) passes. (ADR-007) |
| Implicit single updater payload contract | Both contracts (full-folder + exe-only) are first-class and coexist long-term, switched by `expected_internal` kwarg. (ADR-003, `PACKAGING_CONTRACT.md`) |
| ValveMaster's `#1c1c1c` gray palette was "lower priority but acceptable" | "System B" is deprecated; System A is the only sanctioned design system. ValveMaster gets retrofitted in 8a with an explicit visible-change release note. (ADR-005, `DESIGN_SYSTEM.md`) |
| Apps "may copy commons primitives if the local need is unique" | Apps NEVER fork. Only extend via subclass / `objectName` override / composition. (ADR-002, `PLATFORM_CONTRACT.md`) |
| Phase 7 was a single phase covering all 4 retrofits | Split into Phase 7 (pilot batch) + Phase 8a + Phase 8b. (`PHASES.md`) |
| Original ladder had no slots for token / widget API / resource provider / icon infrastructure phases | New sub-phases 2.1, 2.2, 2.5, 2.6, 2.7, 3B, 3C inserted. (`PHASES.md`) |

## 4. Contradictions reconciled

Where prior docs disagreed with newer decisions, the newer position
became canonical and the older one is preserved as historical.

| Topic | Earlier position | Reconciled position |
|-------|------------------|---------------------|
| Updater payload contract | Phase 0 inventory documented both shapes; the original unified plan defaulted everything to full-folder | Both shapes are valid; commons API exposes the choice. (ADR-003) |
| Wizard default radio | Phase 5 plan implied commons-backed would become default "soon" | Stays non-default until Phase 6C clears, not just Phase 4. (ADR-007) |
| ValveMaster retrofit priority | "Lower priority" in original plan | High-visibility theme change; Phase 8a comes first in the wave specifically to get the brand-consistency win once it's safe to ship. (ADR-005) |
| Phase ordering when AV blocker emerged | Phase 6 was supposed to lead directly to Phase 7 retrofits | AV inserts a hard gate (Phase 6C) between 6 and 7. All retrofits deferred. (`BLOCKERS.md §1`) |
| "Commons should publish to PyPI" | Original plan assumed open distribution | License is now internal-proprietary; public PyPI rejected. Private hosting or submodule. (ADR-006, ADR-010) |
| PCC's flat layout vs wizard's `ui/` subdir layout | Plan implied PCC would migrate to the canonical `ui/` layout | Cosmetic-only; Phase 9 stewardship work, not blocking anything. (`TODOS.md` "Future") |

## 5. Newly introduced canonical decisions

The 9 finalized ADRs in `DECISIONS.md`:

| ADR | Decision | First introduced |
|-----|----------|------------------|
| 001 | Commons is a UI platform, not a helper grab-bag | Architecture pivot at this baseline |
| 002 | Apps extend via addendum, not fork | This baseline (codifies prior implicit norm) |
| 003 | Two updater payload contracts coexist permanently | Phase 0 finding, formalized here |
| 004 | Pilot batch = Checkout + Phoenix CAD | This baseline (replaces sequential plan) |
| 005 | System A is the only design system; System B (ValveMaster gray) is deprecated | Phase 0 finding, formalized here |
| 006 | Internal-proprietary license; not open source | PCC branding/packaging work (2026-05-15) |
| 007 | Commons-backed wizard radio stays non-default until Phase 6C clears | Phase 5 implementation |
| 008 | Sentinel-substitution templates (`__TOKEN__`), not f-string formatting | Phase 5 implementation |
| 009 | Release-zip validator out of inline PowerShell into Python helper | Phase 6A |

## 6. Deferred / unresolved decisions

ADRs 010-013 — explicitly postponed with documented trigger
conditions for re-evaluation.

| ADR | Topic | Trigger to revisit |
|-----|-------|--------------------|
| 010 | Commons distribution strategy (submodule / private PyPI / GitHub Packages / Plan B vendoring) | Phase 8 retrofit kickoff |
| 011 | Light-mode palette | Explicit production-user feedback |
| 012 | Automated lint enforcement for design-system drift | After Phase 8 — if drift is observed |
| 013 | Telemetry / usage metrics | User base grows beyond ATS internal use |

## 7. Biggest architectural risks

| Rank | Risk | Mitigation status |
|------|------|-------------------|
| 1 | AV/S1 gate is open with no committed resolution path. Blocks all frozen-exe phases (4, 6C, 7, 8). | Documented; 3 paths identified; no ETA. Owner: IT/DevOps + Justin. |
| 2 | Commons distribution unresolved. Phase 8 makes "every tool has a submodule" operationally painful at scale. | Deferred to Phase 9 unless retrofit forces. ADR-010. |
| 3 | No CI on phoenix-commons yet. Every retrofit becomes the first integration test of commons. | Low-effort to add; listed in TODOs "immediate". |
| 4 | PCC's `pcc_config.json` lives at project-root — a frozen install would lose state on update. | Phase 3B addresses; not yet approved. |
| 5 | Same-disk backups. Whole-disk failure / laptop loss destroys both repos + bundle. PCC is on GitHub; phoenix-commons is local-only. | Push commons to a private GitHub repo (low-effort); listed in TODOs "immediate". |

## 8. Biggest architectural improvements

| Rank | Improvement | Effect |
|------|-------------|--------|
| 1 | Single ownership per primitive + "addendum, not fork" formalized | Eliminates drift surface that was building up across 4 production tools |
| 2 | Both updater contracts first-class via `expected_internal` kwarg | No risky migration of deployed installer formats ever needed |
| 3 | Pilot-of-two retrofit strategy | Stress-tests the contract at N=2 before high-visibility / high-surface retrofits |
| 4 | AV/S1 collapsed to one root blocker with one resolution chain | Clarifies that fixing one environmental issue unblocks 4 downstream phases |
| 5 | Commons scope made finite (decision matrix with worked examples) | Prevents "everything ends up in commons" creep |
| 6 | Phase ladder revised with 2.x and 3.x sub-phases | Every future increment has a precise gate |
| 7 | Naming registry exists | Every external-facing identifier has one canonical home |
| 8 | Design system pinned (System A only; System B deprecated) | Brand consistency restored across the tool family post-Phase-8a |

## 9. Recommended next approved implementation phase

| Scenario | Recommended next phase |
|----------|------------------------|
| **AV gate clears within the next 1–4 weeks** | Phase 6C (frozen-exe dogfood). Unblocks Phase 7 immediately. Highest leverage. |
| **AV gate stays open indefinitely** | (a) Add CI to phoenix-commons (TODOs "immediate"). (b) Phase 3B (PCC config-path migration). Both are AV-independent platform-prep work. |
| **Architecture wants more prep regardless** | Phase 2.1 (token formalization) — locks the public token API so retrofits can rely on it. AV-independent. |
| **Strategic priority is brand polish before any release** | Replace placeholder PCC logo / installer wizard BMPs (TODOs "before releases"). Cosmetic but visible. |

No phase will start without explicit user approval per `BASELINE.md`
stop conditions.

## 10. Recommended freeze points before migrations

Phase 7 (pilot retrofit) cannot start until all of these freeze:

| Freeze point | What "frozen" means | Phase that delivers it |
|--------------|---------------------|------------------------|
| Token public API | `phoenix_commons.theme.tokens` module exists with `__all__` enumerated; key names locked | Phase 2.1 |
| Widget public API | `phoenix_commons.widgets.__all__` enumerated; constructor kwargs frozen; private modules underscore-prefixed | Phase 2.2 |
| Runtime resource API | `apply_dark_theme(app)` is the only sanctioned QSS-loading path; resource-file paths are internal | Phase 2.5 |
| Production-tool AppId GUIDs registered | All 4 GUIDs copied into `NAMING_REGISTRY.md` from each `installer.iss` | Pre-Phase-7 prep |
| Per-tool updater contract documented | `expected_internal` value per tool committed to `NAMING_REGISTRY.md` | Already done (✓) |
| AV gate cleared | One of the 3 resolution paths landed; Phase 6C green | Phase 6C |
| Commons CI green | `phoenix-commons` has a working `.github/workflows/ci.yml` | TODOs "before migrations" |
| Pilot-readiness checklist signed off | Final architectural review on commons API surface | New checklist (per TODOs "before migrations") |

A retrofit PR that starts before any of the above is frozen is
**out of order** and should be rejected at review.

## 11. Remaining blockers

7 active. See `BLOCKERS.md` for full detail. Summary:

| # | Blocker | Type | Gates |
|---|---------|------|-------|
| 1 | S1/AV bootloader quarantine | Environmental | Frozen-exe verification (chain blocker for 2/3/4) |
| 2 | Frozen-exe verification | Implementation (blocked on #1) | Installer + updater runtime verification |
| 3 | Installer runtime behaviour | Implementation (blocked on #2) | PCC v2.0.0 release |
| 4 | Updater runtime behaviour | Implementation (blocked on #3) | Stable releases at scale |
| 5 | Commons distribution strategy | Architecture decision | Phase 8 at scale; deferred to Phase 9 |
| 6 | Commons CI missing | Infrastructure | Phase 7 confidence (no automated guardrail) |
| 7 | Same-disk backups | Operational | Disaster recovery for phoenix-commons |

Resolution dependencies: 1 → 2 → 3 → 4 is one chain. 5, 6, 7 are
independent and resolvable today.

## 12. What still needs human decisions

Decisions the architecture baseline can't make on its own —
require Justin (or IT / DevOps as noted):

| Question | Owner | When it becomes urgent |
|----------|-------|-------------------------|
| Which AV resolution path do we take? (IT/S1 allow-list / Authenticode signing / alternate build host) | IT/DevOps + Justin | Already urgent — gates all frozen-exe phases |
| When do we attempt Phase 6C? | Justin | Immediately after AV gate clears |
| Do we add CI to phoenix-commons before or after pushing to GitHub? | Justin | Before Phase 7 |
| What's the commons distribution strategy? (ADR-010) | Justin + Architecture | Phase 8 kickoff |
| When is PCC ready to release v2.0.0 as an installer? | Justin | After Phase 6C green + replacement of placeholder branding |
| Do we want PCC's `pcc_config.json` migration to AppData (Phase 3B) to happen before or after the first installer release? | Justin | Decision needed before any frozen-build install — config drift between source-run and frozen-run is a real risk |
| Should we wire `assets/watermark.png` into the PCC UI now or defer to a later polish phase? | Justin | Low priority; cosmetic |
| Are the 4 production AppId GUIDs OK to copy as-is from each `installer.iss` into `NAMING_REGISTRY.md`? | Justin | Phase 7 prep |
| Do we ever delete the merged feature branches on origin? (`feature-command-center-gui-polish`, `feature-command-center-branding-packaging`, `fix-ci-smoke-tests`, `packaging-command-center`) | Justin | Anytime; cosmetic |
| Does the baseline itself get pushed to GitHub (when phoenix-commons has a remote), or stay local? | Justin | When phoenix-commons gets a remote |

Each decision is also reflected in `BLOCKERS.md` (if blocking) or
`TODOS.md` (if actionable but not blocking) or `DECISIONS.md`
"Deferred" (if explicitly postponed).

---

## Generation method

For transparency / reproducibility of this baseline:

| Aspect | Method |
|--------|--------|
| Source material | All files listed in §2 above |
| Authoring sequence | BASELINE → CURRENT_STATE → PHASES → PLATFORM_CONTRACT → PACKAGING_CONTRACT → MIGRATION_RULES → NAMING_REGISTRY → DESIGN_SYSTEM → COMMONS_SCOPE → DEPENDENCY_GRAPH → BLOCKERS → DECISIONS → TODOS (linear; each subsequent file referenced earlier ones) |
| Style discipline | Tables heavily; minimal prose; sections labeled; cross-references between files explicit |
| Verification | Each claim in `CURRENT_STATE.md` tagged Verified / Assumed / Blocked / Deferred so future readers know what they can rely on |
| Branch | `baseline-v1` off the prior commons HEAD (`ba3d2c4`) |
| Commit | `3f16d46` — single commit, 13 files + 2,237 lines |
| Push state | Not pushed (phoenix-commons has no remote yet — see BLOCKERS.md §7) |
| Implementation work performed | None. Architecture stabilization only. |
