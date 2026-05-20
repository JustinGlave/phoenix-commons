# CLAUDE_NORMALIZATION_REPORT_01.md

> Operational Convergence Phase — CLAUDE.md normalization deliverable.
> Authored 2026-05-19.
>
> **Scope:** add concise, repo-specific `CLAUDE.md` to the 4 active
> repos that lacked one. No commons / runtime / installer code touched.

## 1. Action summary

| Repo | File | Size | Commit |
|------|------|------|--------|
| phoenix-commons | `CLAUDE.md` | 2,379 bytes | `6f40031` |
| phoenix-command-center | `CLAUDE.md` | 2,725 bytes | `253e31e` |
| Phoenix-Checkout-Tool | `CLAUDE.md` + `.gitignore` un-ignore | 3,099 bytes | `784e171` |
| ValveMasterTool (Phoenix Master Tool repo) | `CLAUDE.md` | 3,429 bytes | `12bc8dc` |

Pre-existing tracked `CLAUDE.md` files (untouched):

| Repo | File | Status |
|------|------|--------|
| Phoenix_CAD_Tool | `CLAUDE.md` (12 KB; renamed from `AGENTS.md` in prior Hardening Sprint) | Untouched |
| Job Tracker | `CLAUDE.md` (2 KB; pre-existing) | Untouched |

## 2. Content discipline

All four new files follow the refinements specified in the
Convergence-Phase mandate:

| Requirement | Status |
|-------------|--------|
| Custom per repo (no copy/paste boilerplate) | ✅ Each file authored from scratch with repo-specific content |
| Operational context only | ✅ Purpose / entrypoints / retrofit state / CI / do-not-change items |
| References canonical governance docs rather than duplicating them | ✅ Each links to `docs/ui-platform-baseline-v1/` artifacts (commons-side) and sibling docs (per repo) |
| Concise (~1-3 KB target) | ✅ Range 2.4-3.4 KB; PMT slightly over due to v1.1.0 rename history |
| Preserves repo-specific realities + intentional divergences | ✅ PMT's Ubuntu CI divergence + Checkout's monolithic-file preservation + PCC's palette divergence all called out |
| No long philosophy sections | ✅ |
| No platform history / generalised governance restatement | ✅ |
| No speculative future architecture | ✅ |

## 3. Non-trivial finding: Phoenix Checkout `.gitignore`

The pre-existing `.gitignore` in `Phoenix-Checkout-Tool` explicitly
listed `CLAUDE.md` among ignored paths (alongside `.claude/` and
`memory/`). This blocked `git add CLAUDE.md` on first attempt.

The previous policy treated `CLAUDE.md` as a per-developer scratch
file. The Operational Convergence Phase standardises `CLAUDE.md` as
a tracked repo-orientation document. Resolution:

- Removed the `CLAUDE.md` line from `.gitignore` in the same commit
  as the new file (`784e171`).
- `.claude/` and `memory/` directories remain ignored — those are
  per-developer runtime state, not orientation docs.

Commit message documents both changes so the change is auditable.

## 4. Intentional non-uniformities preserved

Per convergence-phase doctrine ("preserve repo-specific realities
and intentional divergences"):

| Aspect | Variation | Reason |
|--------|-----------|--------|
| File size | 2.4 KB (commons) to 3.4 KB (PMT) | PMT's higher operational complexity (recent rename, AppId GUID preservation, base64 assets); PCC's deferred Phase 3C scope notes; Checkout's subsystem source-of-truth map | 
| `CLAUDE.md` companion files | Checkout has `DEVELOPER.md` (14 KB, kept separately); PMT has `GIT_SETUP.md` (4 KB, kept separately); Job Tracker has `NOTES.txt` (3 KB, kept separately); CAD has `PLAN.md` + `TODO.md` | Each tool's pre-existing dev docs serve distinct purposes (human-onboarding-depth, git-workflow specifics, etc.). CLAUDE.md is the AI-context layer; the others are not duplicated into it. |
| Retrofit state language | CAD + Checkout are "commons-backed"; PCC + PMT + Job Tracker are "not yet retrofitted" | Reflects actual Phase 3A / 3B merge state vs Phase 3C / 8a / 8b pending state |

## 5. Risk assessment

| Risk category | Outcome |
|---------------|---------|
| Runtime behaviour change | None — `CLAUDE.md` is not imported by any code |
| Build pipeline impact | None — not referenced by `build.bat`, `installer.iss`, or PyInstaller |
| Updater contract impact | None — file ships with source, not with binary |
| User-data path impact | None |
| Commons API surface impact | None — commons CLAUDE.md is repo-root doc, not in `src/phoenix_commons/` package |

All 4 changes are pure documentation additions. Rollback cost: 1
commit revert per repo if needed.

## 6. Deferred items

- **CONTRIBUTING.md update in PCC** to fix the stale "MIT License"
  reference and Python 3.14 mention. Flagged in
  `OPERATIONAL_HARDENING_REPORT_01.md § 9` item 2. Not in this
  report's scope.
- **CLAUDE.md content review by user** — recommended before Phase 3C
  begins so any per-repo content corrections land before retrofit
  work depends on the file.

## 7. Exact commits

```
6f40031  phoenix-commons        Add CLAUDE.md (Operational Convergence — CLAUDE.md normalization)
253e31e  phoenix-command-center  Add CLAUDE.md (Operational Convergence — CLAUDE.md normalization)
784e171  Phoenix-Checkout-Tool   Add CLAUDE.md + un-ignore filename (Operational Convergence — CLAUDE.md normalization)
12bc8dc  ValveMasterTool         Add CLAUDE.md (Operational Convergence — CLAUDE.md normalization)
```

## 8. Confirmation

| Item | Status |
|------|--------|
| No retrofit work | ✅ |
| No runtime / frozen work | ✅ |
| No commons API changes | ✅ |
| No production behaviour changes | ✅ |
| Build pipelines untouched | ✅ |
| Installer scripts untouched | ✅ |
| Repo-specific realities preserved | ✅ |
| Intentional divergences documented in-file | ✅ |

| Field | Value |
|-------|-------|
| Phase | Operational Convergence — CLAUDE.md normalization |
| Status | ✅ Complete |
| Date | 2026-05-19 |
| Repos touched | 4 |
| Commits landed | 4 |
| Saved to | `phoenix-commons/docs/ui-platform-baseline-v1/CLAUDE_NORMALIZATION_REPORT_01.md` |
