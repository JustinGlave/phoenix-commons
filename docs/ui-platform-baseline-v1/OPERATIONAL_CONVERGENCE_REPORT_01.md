# OPERATIONAL_CONVERGENCE_REPORT_01.md

> Operational Convergence Phase — Report 01. Convergence audit across
> active repos. Documentation-only deliverable. Authored 2026-05-19,
> after `OPERATIONAL_HARDENING_REPORT_01.md`.
>
> **Mode:** managed rollout + operational maturity. NOT architecture
> invention. Treats existing governance (`MIGRATION_RULES.md`,
> `PLATFORM_CONTRACT.md`, `DESIGN_SYSTEM.md`, ADRs) as canonical.
>
> **Scope:** read-only audit + categorisation. No files touched in
> any tool repo. No commons code modified. Recommendations are
> low-risk normalisation only — no architecture redesign, no "while
> we're here" expansion, no new framework systems.

## 1. Scope

Audited 6 active repos for convergence on:

- CLAUDE.md presence + naming
- Repo topology
- Script / layout variance
- CI workflow naming + config
- Entrypoint file naming
- CHANGELOG format
- Operational convention drift

Repos: `phoenix-command-center`, `phoenix-commons`, `Phoenix_CAD_Tool`
(Lab Layout Tool), `Phoenix-Checkout-Tool`, `Job Tracker` (Project
Tracking Tool), `ValveMasterTool` (Phoenix Master Tool, post-v1.1.0
rename).

## 2. Findings

### 2.1 CLAUDE.md / dev-context file naming

| Repo | File | Size | Notes |
|------|------|------|-------|
| Phoenix CAD | `CLAUDE.md` | 12 KB | Renamed from `AGENTS.md` in prior hardening sprint |
| Job Tracker | `CLAUDE.md` | 2 KB | Pre-existing; concise |
| Phoenix Checkout | `DEVELOPER.md` | 14 KB | Same purpose, different filename |
| Phoenix Master Tool | `GIT_SETUP.md` | 4 KB | Different scope (Git workflow only) |
| commons | (none) | — | Missing |
| PCC | (none) | — | Missing |

Auxiliary dev docs present elsewhere: Phoenix CAD `PLAN.md` (12 KB) +
`TODO.md` (2 KB); Job Tracker `NOTES.txt` (3 KB).

**Convergence gap**: Phoenix Checkout uses `DEVELOPER.md` for what is
otherwise `CLAUDE.md` in the family.

### 2.2 Repo topology

| Tool | Topology shape |
|------|-----------------|
| PCC | `assets/`, `docs/`, `scripts/`, `tests/`, flat root for `.py` files |
| commons | `src/phoenix_commons/`, `docs/`, `tests/`, `Design Items/`, `scratch/` |
| Phoenix CAD | `ui/`, `cad/`, `blocks/`, `config/`, `jobs/`, `templates/`, `tools/`, `commons/` (submodule), `legacy/`, `docs/` |
| Phoenix Checkout | flat root + 5 `.xlsx` templates, `commons/` (submodule), `legacy/` |
| Job Tracker | flat root + `pyxlsb/`, `starter_package/`, `tests/` |
| Phoenix Master Tool | flat root + `tests/` + `phoenix_style.qss` |

Brand assets at repo root in all 4 production tools (`LLT_*`, `PTT_*`,
`green.png`, `Normal_red.ico` etc.). PCC alone uses `assets/`.

### 2.3 Script / layout variance

| Item | Status |
|------|--------|
| `build.bat` presence | 5 of 6 (commons is library — no build.bat by design) |
| `installer.iss` presence | 4 of 6 (PCC + commons unpackaged) |
| `requirements.txt` | 5 of 6 (PMT lacks one; commons uses pyproject.toml) |
| `requirements-dev.txt` | 2 of 6 (PCC, Phoenix CAD) |
| `pyproject.toml` | 1 of 6 (commons only — correct shape for a library) |
| `tests/` directory | 4 of 6 (Phoenix CAD + Phoenix Checkout lack tests/) |
| `.gitmodules` (commons submodule) | 2 of 6 (Phoenix CAD + Phoenix Checkout — the retrofitted tools) |

### 2.4 CI naming + config variance

| Repo | Filename | YAML name | Python | Runner |
|------|----------|-----------|--------|--------|
| phoenix-commons | `ci.yml` | `ci` | **3.12** ✅ | windows-latest |
| Phoenix Checkout | `ci.yml` | `CI` | **3.12** ✅ | windows-latest |
| PCC | `ci.yml` | `ci` | 3.14 ⚠ | windows-latest |
| Phoenix CAD | `ci.yml` | `CI` | 3.14 ⚠ | windows-latest |
| Job Tracker | `ci.yml` | `CI` | 3.14 ⚠ | windows-latest |
| Phoenix Master Tool | `test.yml` ⚠ | `Tests` | **3.10/3.11/3.12** matrix | **ubuntu-latest** ⚠ |

ADR-014 canonical: Python 3.12, Windows-latest. 3 repos still on 3.14
(pre-ADR drift). PMT diverges intentionally (per user direction during
the hardening sprint).

### 2.5 Entrypoint file naming

| Pattern | Tool |
|---------|------|
| `main.py` | PCC |
| `app.py` | Phoenix CAD |
| `<tool>_gui.py` | Phoenix Checkout (`checkout_tool_gui.py`), Job Tracker (`project_tracker_gui.py`) |
| `<tool>_pyside6.py` | Phoenix Master Tool (`phoenix_master_pyside6.py`) |

Four distinct patterns. Each is wired into `build.bat` (`APP_MAIN=`)
and `installer.iss` — convergence here would touch the build pipeline.

### 2.6 CHANGELOG format drift

All 6 CHANGELOGs use `# Changelog` title and `## [Unreleased]` heading.
Version section date format varies:

| Repo | Date format on first version section |
|------|--------------------------------------|
| PCC | `## [2.0.0] — 2026-05-12` ✅ ISO |
| commons | `## [0.1.0] — Phase 2 Stabilization` (no calendar date — intentional, no tag) |
| Phoenix CAD | `## [0.1.1] — 2026-05-12` ✅ ISO |
| Phoenix Checkout | `## [1.7.0] — 2025` ⚠ year only |
| Job Tracker | `## [1.8.5] — 2026-05-12` ✅ ISO |
| Phoenix Master Tool | `## [1.1.0] — 2026` ⚠ year only |

3 of 5 versioned releases use ISO YYYY-MM-DD. 2 use year-only. commons
omits date by design.

### 2.7 Operational convention drift

| Convention | Drift observed |
|------------|----------------|
| Brand assets at repo root | 4 of 4 production tools; PCC alone uses `assets/` |
| `_FullInstall.zip` manual-install asset | All 4 production tools (consistent) |
| Auto-updater zip payload | full-folder (CAD + Job Tracker) vs exe-only (Checkout + PMT) — intentional per ADR-003 |
| `legacy/` directory for pre-retrofit QSS | Phoenix CAD + Phoenix Checkout only (the 2 retrofitted) |
| Local `phoenix_style.qss` at repo root | Job Tracker + PMT (pre-retrofit tools using System A) |
| `starter_package/` (Job Tracker) | Slated for deletion in Phase 8b — known debt |

## 3. Categorisation

### 3.1 Safe immediate normalisation (low-risk; recommended in this phase)

| # | Action | Repos | Risk |
|---|--------|-------|------|
| **N1** | Update CI `python-version` from `"3.14"` → `"3.12"` to match ADR-014 | PCC, Phoenix CAD, Job Tracker | Very low. Single-line edit per workflow. Both interpreters work; ADR-014 names 3.12 as the contract. |
| **N2** | Update CI YAML `name:` header from `CI` → `ci` for consistency | Phoenix CAD, Job Tracker, Phoenix Checkout | Trivial. Cosmetic — GitHub Actions UI label only. |
| **N3** | Normalise CHANGELOG date format `2025` / `2026` → ISO `YYYY-MM-DD` on the two affected version sections | Phoenix Checkout (`[1.7.0] — 2025`), PMT (`[1.1.0] — 2026`) | Trivial. Dates available from `git tag` annotations. |
| **N4** | Author concise `CLAUDE.md` in the 4 repos missing one (commons, PCC, Phoenix Checkout, PMT) | 4 repos | Low. Net-new doc files. Phoenix Checkout's `DEVELOPER.md` stays (different scope — developer onboarding); CLAUDE.md is AI-context. Each repo's CLAUDE.md is custom content (not boilerplate). |

**N4 caveat**: each CLAUDE.md must be custom — no boilerplate. Suggest
target size matches Job Tracker's 2 KB pattern (concise), not Phoenix
CAD's 12 KB. Each one authored as a separate small commit per repo
so reviews stay independent.

### 3.2 Defer until post-PCC retrofit (Phase 3C and later)

| # | Item | Why deferred |
|---|------|--------------|
| **D1** | Entrypoint file naming convergence (`main.py` / `app.py` / `<tool>_gui.py` / `<tool>_pyside6.py`) | Touches `build.bat` `APP_MAIN=`, `installer.iss` `[Files]`, runtime imports. High-risk rename for low benefit. Each tool's existing entry name is wired through its release pipeline; convergence here is not free. |
| **D2** | Brand asset relocation to `assets/` folder in production tools | Already documented in `ASSET_NAMING_PROPOSAL.md`. Rollout is opportunistic per-tool, not a coordinated sweep. |
| **D3** | Adding `tests/` + `requirements-dev.txt` to Phoenix CAD + Phoenix Checkout | Test authoring is content work, not normalisation. CI placeholders already note "TODO when tests/ is added". |
| **D4** | Rename PMT's `test.yml` → `ci.yml` | User explicitly chose to leave PMT CI alone during the hardening sprint. PMT's `test.yml` works. |
| **D5** | Fold Job Tracker's `NOTES.txt` into `CLAUDE.md` | Distinct content scopes. Folding might lose context. Leave both. |
| **D6** | Phoenix Checkout's `DEVELOPER.md` → rename to `CLAUDE.md`? | These are different documents in spirit — DEVELOPER.md is human-onboarding-flavour; CLAUDE.md is AI-context-flavour. Keep both (author a new CLAUDE.md per N4; leave DEVELOPER.md untouched). |
| **D7** | `starter_package/` deletion in Job Tracker | Scheduled for Phase 8b retrofit per `MIGRATION_RULES.md` § Migration order. Out of scope for any standalone PR. |
| **D8** | Topology-level convergence (subsystem folders, `cad/`, `blocks/`, etc.) | Domain-specific structure; not drift. |

### 3.3 Intentionally divergent (canonical reasons — preserve as-is)

| # | Item | Reason |
|---|------|--------|
| **I1** | PMT CI uses Ubuntu matrix on 3.10/3.11/3.12 | Unit-test-focused; OS-agnostic by design. User-approved during hardening sprint. |
| **I2** | PMT CI filename is `test.yml` | User-approved decision to leave PMT CI alone. |
| **I3** | commons uses `pyproject.toml`; tools use `requirements.txt` | Library vs application shape — correct per role. |
| **I4** | commons has no `build.bat` / `installer.iss` | Library — packaging is the consuming tool's job. |
| **I5** | Phoenix CAD has `cad/`, `blocks/`, `templates/`, `jobs/`, `tools/` subsystems | Domain-specific (BricsCAD COM integration + DWG library + fixture data). |
| **I6** | Phoenix Checkout has 5 `.xlsx` templates at repo root | Bundled assets for the tool's export feature; loaded via `--add-data=` at build. |
| **I7** | Updater payload split: full-folder (CAD + Job Tracker) vs exe-only (Checkout + PMT) | ADR-003 — intentional asymmetry; preserved in commons updater API via `expected_internal` kwarg. |
| **I8** | Job Tracker + PMT have `phoenix_style.qss` at repo root | Pre-retrofit copies of System A. Will become `legacy/phoenix_style.qss.preretrofit` files when Phase 8a / 8b retrofits land. |
| **I9** | commons has no `assets/` folder | Library; no runtime assets to bundle. `Design Items/` is brand-source storage, not packaged. |
| **I10** | Different entrypoint naming patterns across tools | Reflect domain history; convergence cost > benefit (see D1). |
| **I11** | commons CHANGELOG version section lacks a calendar date | commons has no tagged releases yet (per ADR-015 — submodule SHAs are distribution); calendar dates are added when commons first tags. |

## 4. Risk assessment

All 4 recommended N1-N4 actions are documentation-grade or
single-line-config changes:

| Action | Files touched | Runtime impact | Build-pipeline impact | Rollback cost |
|--------|---------------|------------------|--------------------------|---------------|
| N1 — CI Python version | 3 × `.github/workflows/ci.yml` | None | CI only | 1 commit revert |
| N2 — CI YAML name field | 3 × `.github/workflows/ci.yml` | None | None (label only) | 1 commit revert |
| N3 — CHANGELOG date format | 2 × `CHANGELOG.md` | None | None | 1 commit revert |
| N4 — Author CLAUDE.md × 4 | 4 × new files | None | None | 1 commit revert per repo |

No retrofit branch needed. No submodule SHA bumps. No installer
changes. No release work.

**Cross-cutting risk**: zero — none of N1-N4 touch any of the contracts
named in `MIGRATION_RULES.md` § Stop conditions (AppId, install path,
user-data path, zip asset name, exe name).

## 5. Recommended next actions

In recommended execution order:

1. **N4 → CLAUDE.md authoring** (4 commits across 4 repos). One per
   repo as separate commits; concise content per the Job Tracker
   ~2 KB pattern. User approval per repo recommended given content
   is custom.
2. **N1 → CI Python version normalisation** (3 commits across 3 repos).
   PCC + Phoenix CAD + Job Tracker: `python-version: "3.14"` →
   `"3.12"` per ADR-014.
3. **N2 → CI YAML name field normalisation** (3 commits, or rolled
   into N1 commits). Cosmetic.
4. **N3 → CHANGELOG date format normalisation** (2 commits). Phoenix
   Checkout v1.7.0 → ISO date; PMT v1.1.0 → ISO date.

Items in § 3.2 (Defer) and § 3.3 (Intentional) are not action items.

**No work executed by this report.** This document inventories +
recommends; subsequent commits land the actions per user approval.

## 6. Constraints honoured

| Constraint | Status |
|------------|--------|
| No new framework systems | ✅ — convergence audit only |
| No opportunistic commons expansion | ✅ — no commons code touched |
| No runtime instrumentation | ✅ |
| No parallel governance layers | ✅ — references existing MIGRATION_RULES + DECISIONS + PLATFORM_CONTRACT |
| Consolidate existing doctrine, don't rewrite | ✅ — categorisations cite existing rules |
| Convergence over expansion | ✅ — every recommendation reduces variance |
| Small disciplined improvements over redesigns | ✅ — N1-N4 are all single-line or single-file changes |

## 7. Sign-off

| Field | Value |
|-------|-------|
| Phase | Operational Convergence — audit |
| Status | ✅ Complete (audit + report) |
| Date | 2026-05-19 |
| Repos audited | 6 |
| Findings categorised | 4 safe-immediate / 8 defer / 11 intentional |
| Recommendations | 4 low-risk normalisations (N1-N4) |
| Files touched in this audit | 0 (read-only) |
| Commons code modified | none |
| Production-tool source modified | none |
| Saved to | `phoenix-commons/docs/ui-platform-baseline-v1/OPERATIONAL_CONVERGENCE_REPORT_01.md` |
