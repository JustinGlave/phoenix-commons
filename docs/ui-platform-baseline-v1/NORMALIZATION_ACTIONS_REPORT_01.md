# NORMALIZATION_ACTIONS_REPORT_01.md

> Operational Convergence Phase — N1/N2/N3 normalization execution
> report. Authored 2026-05-19. Companion to
> `OPERATIONAL_CONVERGENCE_REPORT_01.md` (which recommended these
> actions) and `CLAUDE_NORMALIZATION_REPORT_01.md` (CLAUDE.md work
> from the same sprint).
>
> **Scope:** apply safe-immediate normalisations N1 (CI Python 3.12
> per ADR-014), N2 (CI workflow `name:` lowercase), N3 (CHANGELOG
> ISO date format). No runtime / build-pipeline / installer / commons
> code touched.

## 1. Actions executed

### N1 — CI Python `3.14` → `3.12` (ADR-014 enforcement)

| Repo | Commit | Notes |
|------|--------|-------|
| phoenix-command-center | `cd3012b` + `ca52a53` (follow-up step-name fix) | Active build-smoke step's value + display name; commented-out PyInstaller block left untouched (dormant, out of N1 scope per "no opportunistic edits") |
| Phoenix_CAD_Tool | `d65e7e2` | Single-line value edit; step name was already version-agnostic |
| Job Tracker | `5317cf2` | Single-line value edit |

3 repos × 1 logical change = 3 commits (plus 1 follow-up step-name
fix in PCC where the step display name still showed "3.14" after
the value was changed).

phoenix-commons + Phoenix-Checkout-Tool were already on 3.12; no
N1 action needed. Phoenix Master Tool's `test.yml` uses Python
matrix `3.10/3.11/3.12` (intentional divergence — see § 3).

### N2 — CI workflow `name:` field `CI` → `ci`

| Repo | Commit | Notes |
|------|--------|-------|
| Phoenix_CAD_Tool | `fb383af` | YAML header `name: ci` |
| Phoenix-Checkout-Tool | `d4a318e` | Same |
| Job Tracker | `0eaed43` | Same |

3 repos × 1 logical change = 3 commits.

phoenix-commons + PCC were already lowercase `ci`. Phoenix Master
Tool's workflow is `name: Tests` (intentional divergence).

### N3 — CHANGELOG version section date → ISO `YYYY-MM-DD`

| Repo | Commit | Date source | Old | New |
|------|--------|-------------|-----|-----|
| Phoenix-Checkout-Tool | `700f565` | `git log -1 v1.7.0` author date | `[1.7.0] — 2025` | `[1.7.0] — 2026-05-04` |
| ValveMasterTool (Phoenix Master Tool) | `21ba5df` | `git log -1 v1.1.0` author date | `[1.1.0] — 2026` | `[1.1.0] — 2026-05-10` |

phoenix-commons uses `[0.1.0] — Phase 2 Stabilization` (intentional —
no calendar date because no tagged release yet per ADR-015).
PCC, Phoenix CAD, Job Tracker were already on ISO format.

## 2. Commit cadence

User constraint: "one logical commit per normalization category".
Implementation: each `(category × repo)` pair landed as its own
commit. Per-repo combined commits would have bundled N1 + N2 in the
same `.yml` file edit, but the strict per-category-per-repo approach
preserves a finer-grained revert path.

8 normalisation commits + 1 follow-up step-name fix = 9 commits.

```
PCC      cd3012b  CI: Python 3.14 -> 3.12 (N1)
PCC      ca52a53  CI: step name 'Set up Python 3.14' -> '3.12' (N1 follow-up)
CAD      d65e7e2  CI: Python 3.14 -> 3.12 (N1)
CAD      fb383af  CI: workflow name 'CI' -> 'ci' (N2)
Checkout d4a318e  CI: workflow name 'CI' -> 'ci' (N2)
JT       5317cf2  CI: Python 3.14 -> 3.12 (N1)
JT       0eaed43  CI: workflow name 'CI' -> 'ci' (N2)
Checkout 700f565  CHANGELOG: ISO date for v1.7.0 (N3)
PMT      21ba5df  CHANGELOG: ISO date for v1.1.0 (N3)
```

## 3. Intentional divergences preserved

| Repo | Item | Reason |
|------|------|--------|
| Phoenix Master Tool | CI filename `test.yml` (not `ci.yml`) | User-approved during Hardening Sprint |
| Phoenix Master Tool | CI runner `ubuntu-latest` (not `windows-latest`) | Matches pre-rename test framework; unit-test-focused; OS-agnostic by design |
| Phoenix Master Tool | CI Python matrix `3.10/3.11/3.12` (not pinned 3.12) | Matrix coverage for the parts-list backend; same convergence-phase decision to leave PMT CI alone |
| Phoenix Master Tool | CI workflow `name: Tests` (not `ci`) | Same — preserved |
| phoenix-commons | CHANGELOG version section `[0.1.0] — Phase 2 Stabilization` (no calendar date) | No tagged release yet per ADR-015 — submodule SHAs are distribution; calendar date appears when commons first tags |

## 4. PCC follow-up edit context

PCC's N1 commit (`cd3012b`) updated only the `python-version: "3.14"`
value on the active build-smoke job. The setup-python step's display
name (`- name: Set up Python 3.14`) still showed 3.14 after the value
was changed, making CI logs misleading.

Resolution: a single follow-up commit (`ca52a53`) updated the step
name to `- name: Set up Python 3.12`. Logical same-category — the
step display name describes the Python version being set up; both
edits belong to N1's normalisation intent.

Could have been amended into `cd3012b`, but the project's commit
discipline ("prefer new commit over amend") + the fact that
`cd3012b` was already pushed argued for a separate follow-up.

Anti-pattern check: the commented-out PyInstaller-smoke block at
PCC `.github/workflows/ci.yml` lines 42-59 still contains
`python-version: "3.14"` inside the comment. Left untouched —
dormant; out of N1 scope per the convergence-phase mandate against
"opportunistic edits".

## 5. Risk assessment

| Action | Files touched | Runtime impact | Build-pipeline impact | Rollback cost |
|--------|---------------|------------------|--------------------------|---------------|
| N1 × 3 | 3 `.github/workflows/ci.yml` files | None | CI only | 1 commit revert each |
| N2 × 3 | 3 `.github/workflows/ci.yml` files | None | None (UI label only) | 1 commit revert each |
| N3 × 2 | 2 `CHANGELOG.md` files | None | None | 1 commit revert each |
| PCC follow-up | 1 `.github/workflows/ci.yml` | None | None | 1 commit revert |

All actions are CI-config or documentation. No `installer.iss`,
`build.bat`, `version.py`, or production source code modified.

## 6. Verification

Static verification each commit's YAML continues to load. No live
CI run triggered by this report — actual CI execution will surface
on the next push to each repo's branch (already covered by the
N1/N2 commits themselves).

| Repo | CI workflow YAML loads | python-version per ADR-014 | name lowercase per convergence |
|------|-------------------------|-------------------------------|--------------------------------|
| phoenix-commons | ✅ | ✅ (was already) | ✅ (was already) |
| phoenix-command-center | ✅ | ✅ (N1) | ✅ (was already) |
| Phoenix_CAD_Tool | ✅ | ✅ (N1) | ✅ (N2) |
| Phoenix-Checkout-Tool | ✅ | ✅ (was already) | ✅ (N2) |
| Job Tracker | ✅ | ✅ (N1) | ✅ (N2) |
| Phoenix Master Tool | ✅ | (intentional matrix) | (intentional `Tests`) |

## 7. Deferred items

None blocking. Convergence audit's deferred set (D1-D8 from
`OPERATIONAL_CONVERGENCE_REPORT_01.md § 3.2`) remains deferred:

- D1 entrypoint naming convergence (touches build pipeline — out of scope)
- D2 brand asset relocation (covered by `ASSET_NAMING_PROPOSAL.md`)
- D3 add tests/ + requirements-dev.txt to CAD + Checkout (content work, not normalisation)
- D4 rename PMT `test.yml` → `ci.yml` (user-approved intentional)
- D5 fold Job Tracker `NOTES.txt` into CLAUDE.md (distinct scopes — keep both)
- D6 Phoenix Checkout `DEVELOPER.md` rename (kept separately per CLAUDE_NORMALIZATION_REPORT § 4)
- D7 `starter_package/` deletion (scheduled for Phase 8b)
- D8 topology subsystem convergence (domain-specific structures)

## 8. Confirmation

| Item | Status |
|------|--------|
| No retrofit work | ✅ |
| No runtime / frozen work | ✅ |
| No commons API changes | ✅ |
| No production behaviour changes | ✅ |
| Build pipelines untouched | ✅ |
| Installer scripts untouched | ✅ |
| One logical commit per normalisation category (× repo) | ✅ — 9 commits in total |
| Intentional divergences preserved + documented | ✅ |

| Field | Value |
|-------|-------|
| Phase | Operational Convergence — N1/N2/N3 normalisation |
| Status | ✅ Complete |
| Date | 2026-05-19 |
| Repos touched | 5 (PCC + Phoenix CAD + Phoenix Checkout + Job Tracker + PMT) |
| Commits landed | 9 |
| Saved to | `phoenix-commons/docs/ui-platform-baseline-v1/NORMALIZATION_ACTIONS_REPORT_01.md` |
