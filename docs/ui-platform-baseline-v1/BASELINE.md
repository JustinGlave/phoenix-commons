# BASELINE.md — Phoenix UI Platform Baseline v1

> The canonical architecture snapshot for the entire Phoenix ecosystem
> as of 2026-05-16. This file is the **front door** of the baseline —
> read this first, then walk the rest of the directory by topic.
>
> Status: **architecture-stabilization output, not implementation.**

## What Phoenix UI Platform is

**Not** "shared styling utilities." This is a full **UI platform**
that the Phoenix Controls / ATS Automation desktop tool family
depends on:

| Provides | Owned by |
|----------|----------|
| Design tokens (palette, typography, spacing, radii) | `phoenix-commons` |
| Canonical QSS stylesheet                            | `phoenix-commons` |
| Reusable widget catalog (buttons, panels, tables, no-scroll family, update banner) | `phoenix-commons` |
| Path helpers (`is_frozen`, `user_data_dir`, `resource_path`) | `phoenix-commons` |
| Updater contract + reference implementation | `phoenix-commons` |
| Icon infrastructure (base set + extension API) | `phoenix-commons` (planned in Phase 2.6) |
| Per-app logo / branding | each app |
| Business logic | each app |

The repos in scope:

| Repo | Role | Today's state |
|------|------|----------------|
| `phoenix-commons` | UI platform + packaging contract provider | Source-mode operational; commons not yet consumed by production tools |
| `phoenix-command-center` | Management hub + scaffold generator + first commons consumer | Source-mode green; CI passing; frozen-exe blocked |
| `Job Tracker` (production) | Lab project tracker | Untouched; uses local theme copy |
| `Phoenix_CAD_Tool` (production) | Lab Layout Tool (BricsCAD-integrated) | Untouched; canonical theme source |
| `Phoenix-Checkout-Tool` (production) | Valve checkout | Untouched; exe-only updater |
| `ValveMasterTool` (production) | Valve master data tool | Untouched; legacy gray theme |

## Maturity at a glance

| Pillar | Source mode | Frozen exe | Production retrofit |
|--------|-------------|------------|---------------------|
| Theme + widgets        | ✅ stable | ⚠ blocked (AV) | ⏸ deferred |
| Paths + updater        | ✅ stable | ⚠ blocked (AV) | ⏸ deferred |
| Scaffold wizard        | ✅ stable | ⚠ blocked (AV) | n/a |
| Command Center hub     | ✅ stable | ⚠ blocked (AV) | n/a |
| CI smoke pipeline      | ✅ green  | n/a            | n/a |
| Packaging source       | ✅ stable | ⚠ blocked (AV) | ⏸ deferred |
| Icon infrastructure    | ⏸ planned | ⏸ planned       | ⏸ deferred |

## What's stable

- The phoenix-commons package skeleton + the lifted theme, widgets,
  paths, and updater modules (Phases 1, 2, 3, 3A).
- The Phoenix Tool wizard in Command Center with two radios
  (standalone default, commons-backed gated). Scaffolds tested
  source-mode green (Phases 5, 5A, 5B).
- The packaging source pipeline for Command Center itself —
  `build.bat`, `installer.iss`, `updater.py`, `paths.py`,
  `scripts/validate_release_zip.py`, full doc set (LICENSE,
  CHANGELOG, SECURITY, CONTRIBUTING, CODE_OF_CONDUCT, release
  checklist, build notes) — all merged to PCC `main`.
- GitHub Actions CI: `compileall` + 4 smoke tests on every push to
  PCC `main`, green as of merge `a9d9433`.
- Local git bundle backups (Phase 6C Layer 1).

## What's blocked

| Blocker | Effect | Owner |
|---------|--------|-------|
| **S1 / corporate AV** quarantines PyInstaller bootloader exes | Cannot verify any frozen-exe build end-to-end on the current developer laptop | IT / DevOps + Justin |
| Unresolved commons distribution | `phoenix-commons` has no PyPI / private-index strategy for downstream apps | Architecture |
| Production retrofit gate | All 4 production tools stay on local theme copies until pilot retrofit proves zero-risk migration | Justin |

## Strategic direction

1. **Commons is the UI platform.** No app should fork the design
   system; apps extend via **addendum**, not duplication.
2. **Frozen-exe gate must clear before any retrofit.** Source-mode
   green is necessary but not sufficient. A retrofitted production
   tool that can't ship is worse than a non-retrofitted one that
   does ship.
3. **Pilot before wave.** Phoenix Checkout + Phoenix CAD (LLT)
   together are the pilot batch — smallest visible change at the
   lowest risk. ValveMaster + Job Tracker follow after pilot review.
4. **Two updater payload contracts coexist long-term**:
   full-folder (Job Tracker, Phoenix CAD) is canonical; exe-only
   (Checkout, ValveMaster) is supported via an explicit kwarg.
5. **Commons-backed scaffolds stay non-default in the wizard** until
   frozen-exe is verified for the commons-backed variant. Source-mode
   testing is already validated.

## Why the architecture changed

The original rollout (Phases 0–6B) treated `phoenix-commons` as a
collection of helpers to be lifted from production tools and made
importable. That framing was correct for Phase 1–3, but it produced
two side-effects that this baseline addresses head-on:

| Side-effect | Baseline response |
|-------------|-------------------|
| Apps end up with **two copies** of the same primitive (local + commons), drifting separately | Formalize **single ownership** (PLATFORM_CONTRACT.md) and prohibit forks (`addendum, not fork`) |
| Commons grows without a clear scope, risking "everything ends up here" | Explicit scope rules (COMMONS_SCOPE.md): what's in, what's out |
| Migration paths assumed all 4 tools retrofit at once | Pilot-first migration strategy (MIGRATION_RULES.md) |
| Updater payload contract was implicit per-tool | Both contracts documented + a kwarg-controlled API (PACKAGING_CONTRACT.md) |
| Frozen-exe gating implicit | Single explicit blocker (BLOCKERS.md), tied to the same root cause across all phases |

## How to read the rest of this directory

| Question | File |
|----------|------|
| "What's the literal current state?" | `CURRENT_STATE.md` |
| "What phases exist and what's their status?" | `PHASES.md` |
| "Who owns what (apps vs commons)?" | `PLATFORM_CONTRACT.md` |
| "What does the updater / installer / package-data look like?" | `PACKAGING_CONTRACT.md` |
| "How do we migrate a production tool safely?" | `MIGRATION_RULES.md` |
| "What's the canonical name of X?" | `NAMING_REGISTRY.md` |
| "What does 'Phoenix design system' mean concretely?" | `DESIGN_SYSTEM.md` |
| "Should this thing go in commons?" | `COMMONS_SCOPE.md` |
| "What depends on what?" | `DEPENDENCY_GRAPH.md` |
| "Why isn't X working?" | `BLOCKERS.md` |
| "Why did we decide Y?" | `DECISIONS.md` |
| "What's left to do?" | `TODOS.md` |

## Stop conditions

This baseline is **architecture-only**. No code shipped while it was
written. No production tool source touched. No build / installer /
release / updater commands executed.

Implementation work resumes only after explicit user approval, one
phase at a time, against the criteria in `PHASES.md`.
