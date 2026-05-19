# MIGRATION_RULES.md

> The rules of safe migration. Every Phase 7 + Phase 8 retrofit
> follows this document. Anything not explicitly permitted here is
> forbidden.

## Migration order

| Wave | Tools | Reason |
|------|-------|--------|
| **Pilot (Phase 7)** | Phoenix Checkout Tool **+** Phoenix CAD Tool (LLT) | Lowest combined risk: Phoenix CAD is already on System A so visible change ≈ 0; Phoenix Checkout has the simpler updater contract. Two tools at once is intentional — proves the migration scales beyond N=1. |
| **Wave (Phase 8a)** | ValveMasterTool | Has the visible gray→navy theme swap. Land alongside an explicit release note. |
| **Wave (Phase 8b)** | Job Tracker | Largest surface area + most production usage. Goes last. `starter_package/` deletion happens in the same PR. |

The original rollout plan listed CAD → Checkout → ValveMaster → Job
Tracker (sequential). This baseline changes that to a **pilot batch
of two** for the reasons above.

## Pilot migration policy

The pilot batch is allowed extra ceremony that single retrofits don't
need:

1. **No migration starts until BOTH pilot tools are ready.** Don't
   half-pilot — that defeats the "prove it scales" goal.
2. **Pilot retrofits ship as separate PRs**, one per tool, both
   open simultaneously. Reviewer compares them side-by-side.
3. **A pilot review report** is written (analogous to a phase report)
   summarising what worked, what was harder than expected, and any
   contract changes that should ripple to commons before Wave 8.
4. **Pilot review report must be accepted** before Wave 8 starts.

## Rollback policy

| Failure during retrofit | Action |
|--------------------------|--------|
| Compileall or pytest fails on the retrofit branch | Fix on the branch; do not merge. |
| Frozen-exe build fails in a way that AV explains | Mark Partial; consult `BLOCKERS.md`. |
| Installed exe fails to launch | Revert the retrofit branch; investigate; re-attempt as a new PR. |
| User-data loss reproduced on upgrade | **Hard stop.** Revert immediately. Patch `paths.user_data_dir` or migration code; do not retry until cause confirmed. |
| Theme regression discovered post-merge | Hotfix release with the legacy QSS dropped back in as app-local file; retrofit re-attempted later. |

A retrofit PR is **always revertable as a single git revert**. This
is non-negotiable. If a retrofit needs more than one commit, squash
them in the PR before merge.

## Screenshot baseline requirements

Each retrofit PR includes **before + after** screenshots of:

- The app's main window (centered, default size).
- Any dialog the retrofit visibly affects (Settings, About, etc.).
- A representative data view (Job Tracker's job list; Phoenix
  CAD's hood-wiring page; etc.).

Screenshots taken at the deployed version's last release vs the
retrofit branch's head, on the same monitor / DPI / OS theme.

Visible-change goal:

| Tool | Acceptable visible change |
|------|---------------------------|
| Phoenix CAD | ≈ 0% (already on System A; widget refactor only) |
| Phoenix Checkout | < 5% (theme already System A; widget swap may shift padding 1–2 px) |
| ValveMaster | High — explicit gray→navy theme swap. Document loudly. |
| Job Tracker | < 5% (theme already System A; refactor primarily code-side) |

If the visible change exceeds the band for a tool that's supposed to
be invisible, the retrofit isn't ready to merge.

## Local backup QSS strategy

Every retrofit lands the canonical commons QSS via
`apply_dark_theme()`. Before merging:

1. The tool's existing `phoenix_style.qss` (or programmatic palette
   in ValveMaster's case) gets copied to
   `<app>/legacy/phoenix_style.qss.preretrofit`.
2. That file is **not** loaded at runtime. It exists as a known-good
   fallback if a critical theme regression is discovered post-merge.
3. The file is removed in a follow-up PR ~30 days after the retrofit
   ships if no regression surfaces.

The phrase "local backup QSS" specifically refers to this preservation
pattern. Not to be confused with the git bundle backups in Phase 6C.

## Drift-vs-extension heuristic

The hardest judgment call during retrofit: is this app-specific code
**extending** commons (allowed) or **drifting from** it (forbidden)?

| Symptom | Drift or extension? |
|---------|---------------------|
| App-local class subclasses a commons widget and adds a method | **Extension** ✓ |
| App-local class subclasses commons widget and **overrides** its `__init__` to change colours | **Drift** ✗ — recolour via QSS object-name override instead. |
| App copies the commons QSS string + edits 2 selectors | **Drift** ✗ — append app-local QSS lines after commons QSS. |
| App invents a new colour token because the closest commons token "isn't quite right" | Likely **drift** — propose the new token as a commons PR first. If only one app needs it, keep it strictly app-local with a comment explaining why. |
| App imports `phoenix_commons.theme.tokens.C` and uses `C['accent']` | **Extension** ✓ — using the public API. |
| App imports `phoenix_commons.theme._embedded_qss` (private module) | **Drift** ✗ — bypassing the public API. Lint should catch this in Phase 9. |

When in doubt, ask: "if I had to delete this app and reinstall it
fresh, would I need to keep this snippet around to recreate the same
look?" If yes → commons. If no → app-local extension.

## Stop conditions

A retrofit **must stop and ask** if any of these surface during the
PR:

| Stop condition | Reason |
|----------------|--------|
| Need to modify a commons-owned file | Triggers a separate commons PR first. Retrofit waits. |
| Need to change the `AppId` GUID | Hard rule — would orphan existing installs. Justin must approve. |
| Need to change `<App>.zip` asset name | Breaks the auto-updater for users still on the prior version. Justin must approve. |
| Need to change install path or user-data path | Same — breaks upgrades. Justin must approve. |
| Frozen-exe verification fails for a reason **other than** the documented S1/AV pattern | New blocker. Document in `BLOCKERS.md` before continuing. |
| A test that passes on `main` fails on the retrofit branch | Fix in the retrofit before merge; do not merge a regression. |
| The visible-change band for the tool is exceeded | Re-scope the retrofit. |

## Per-retrofit branch + PR convention

| Item | Convention |
|------|------------|
| Branch name | `retrofit-<tool-slug>` — e.g. `retrofit-phoenix-checkout`, `retrofit-phoenix-cad`, `retrofit-valvemaster`, `retrofit-job-tracker`. |
| PR title | `Retrofit <App Display Name> to commons-backed` |
| PR body | Per-retrofit safety checklist (PACKAGING_CONTRACT.md §9) filled in. Plus screenshot table. Plus a "what changed in commons during this retrofit" section (often empty). |
| Merge strategy | `--no-ff`. Preserve the retrofit branch on origin until the pilot review (Phase 7) or wave review (Phase 8) approves it for deletion. |
| Tag | `<app-slug>-retrofit-vX.Y.Z` matching the post-retrofit release. |

## Frequency limits

| Wave | Cadence rule |
|------|---------------|
| Pilot (Phase 7) | Both tools merged within 2 weeks of each other. |
| Wave 8a (ValveMaster) | At least 2 weeks **after** the pilot's last merge. |
| Wave 8b (Job Tracker) | At least 2 weeks after Wave 8a. |

Spacing exists so production-user incident reports can surface before
the next retrofit lands.
