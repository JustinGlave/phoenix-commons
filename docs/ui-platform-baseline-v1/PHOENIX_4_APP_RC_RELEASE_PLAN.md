# Phoenix Family — 4-App RC Release Plan

> **Status:** plan only — no RC builds, no tags, no GitHub Releases, no asset uploads in this document.
> **Date:** 2026-05-29.
> **Scope:** coordinated release-candidate workflow for all 4 deployed production tools.
> **Companions:** `PHOENIX_FAMILY_RELEASE_READINESS_AUDIT.md`, `CAD_CHECKOUT_RELEASE_HARDENING_REPORT.md`, `CAD_CHECKOUT_OPERATOR_VALIDATION_STEP.md`.

---

## 1. Final readiness status

| App | Current version | Hardening / Retrofit | Operator validation | Release-ready? |
|-----|------------------|----------------------|---------------------|----------------|
| **Phoenix CAD / Lab Layout Tool** | `0.1.1` (`master` HEAD `fb383af` merged; hardening on `release-hardening/cad-rc-readiness` @ `38cb3a5`) | Phase 3A merged 2026-05-19 (`79c7003`); release-hardening 2026-05-29 (`38cb3a5`) | ✅ PASSED 2026-05-29 (5-min S1 + visual) | ✅ **YES** |
| **Phoenix Checkout Tool** | `1.7.0` (`main` HEAD `700f565` merged; hardening on `release-hardening/checkout-rc-readiness` @ `9b638cb`) | Phase 3B merged 2026-05-19 (`26a4689`); release-hardening 2026-05-29 (`4da0c47` + `9b638cb` openpyxl fix) | ✅ PASSED 2026-05-29 (5-min S1 + visual); ⏳ xlsx template-load sub-check pending (non-blocking) | ✅ **YES** |
| **ValveMaster / Phoenix Master Tool** | `1.1.0` (`main` HEAD `631dbe8`, Wave 8a merge) | Wave 8a merged 2026-05-26 with full build hardening | ✅ PASSED 2026-05-26 (Wave 8a B8a operator visual + 5-min S1) | ✅ **YES** |
| **Job Tracker / Project Tracking Tool** | `1.8.5` (`main` HEAD `6a0d60b`, Wave 8b merge) | Wave 8b merged 2026-05-28 with full build hardening | ✅ PASSED 2026-05-28 (Wave 8b B10 operator visual + 5-min S1) | ✅ **YES** |

**Verdict:** all 4 production tools are operator-validated release-ready.

---

## 2. Proposed RC version numbers

Two-school decision applies: treat the hardening/retrofit work as patch-bump-worthy, OR keep version steady. The four tools are mid-stream at different version points, so the cleanest pattern is **patch bump** (operator can also override to skip).

| App | Current | Proposed RC | Rationale |
|-----|---------|-------------|-----------|
| Phoenix CAD | `0.1.1` | **`v0.1.2-rc1`** | First post-retrofit + first post-hardening release; patch bump signals "same functional state, build hardened" |
| Phoenix Checkout | `1.7.0` | **`v1.7.1-rc1`** | Same logic; patch bump |
| ValveMaster | `1.1.0` | **`v1.1.1-rc1`** | Same logic; patch bump |
| Job Tracker | `1.8.5` | **`v1.8.6-rc1`** | Same logic; patch bump |

`version.py` updates are operator-discretion. If you'd rather hold versions steady (RC the existing v0.1.1 / v1.7.0 / v1.1.0 / v1.8.5 as "v0.1.1-rc1" etc.), that's defensible — but mixing some-bumped-some-steady is messier than coordinated patch bumps across all 4.

---

## 3. Release branch names

For each app, a dedicated RC branch off the operator-validated state:

| App | Source branch | RC branch (to create) | Source HEAD |
|-----|---------------|-----------------------|-------------|
| Phoenix CAD | `release-hardening/cad-rc-readiness` | `release/v0.1.2-rc1` | `38cb3a5` |
| Phoenix Checkout | `release-hardening/checkout-rc-readiness` | `release/v1.7.1-rc1` | `9b638cb` |
| ValveMaster | `main` (Wave 8a already merged) | `release/v1.1.1-rc1` | `631dbe8` |
| Job Tracker | `main` (Wave 8b already merged) | `release/v1.8.6-rc1` | `6a0d60b` |

CAD + Checkout RC branches start from the hardening branches (which haven't been merged to mainline yet); ValveMaster + Job Tracker RC branches start from mainline (their hardening is already merged).

Alternative: merge CAD + Checkout hardening branches to mainline FIRST, then create RC branches from the post-merge `master`/`main`. That makes the mainline state match the RC state. **Recommended path** — see § 4.

---

## 4. Build order

Recommended order: **CAD → Checkout → ValveMaster → Job Tracker.**

Rationale: CAD + Checkout need mainline merges before RC; doing them first keeps the four-tool merge state consistent. ValveMaster + Job Tracker are already merged so their RC steps are shorter.

### Step-by-step

#### 1. CAD — merge hardening + bump version + RC

```
# in Phoenix_CAD_Tool repo
git checkout master
git pull origin master
git merge --no-ff release-hardening/cad-rc-readiness \
  -m "Merge release-hardening — build.bat aligned with FROZEN_BUILD_BASELINE"
# Bump version.py: __version__ = "0.1.2"
# Update README "Current Version: v0.1.2"
# Update CHANGELOG.md with v0.1.2 entry (build hardening, no functional changes)
git add version.py README.md CHANGELOG.md
git commit -m "v0.1.2 — release hardening, no functional changes"
git push origin master

# Create RC branch + RC tag
git checkout -b release/v0.1.2-rc1
git push origin release/v0.1.2-rc1
git tag -a v0.1.2-rc1 -m "Phoenix CAD v0.1.2 RC1 — release hardening"
git push origin v0.1.2-rc1

# Build
.\build.bat
# Verify artifacts present, updater zip contract = full-folder
```

#### 2. Checkout — merge hardening + bump version + RC

```
# in Phoenix-Checkout-Tool repo
git checkout main
git pull origin main
git merge --no-ff release-hardening/checkout-rc-readiness \
  -m "Merge release-hardening — build.bat hardened + openpyxl declared"
# Bump version.py: __version__ = "1.7.1"
# Update README + CHANGELOG.md
git add version.py README.md CHANGELOG.md
git commit -m "v1.7.1 — release hardening + openpyxl dep declared"
git push origin main

git checkout -b release/v1.7.1-rc1
git push origin release/v1.7.1-rc1
git tag -a v1.7.1-rc1 -m "Phoenix Checkout v1.7.1 RC1 — release hardening"
git push origin v1.7.1-rc1

.\build.bat
# Verify: updater zip contract = exe-only
```

#### 3. ValveMaster — bump version + RC (hardening already merged)

```
# in ValveMasterTool repo
git checkout main
git pull origin main
# Bump version.py: __version__ = "1.1.1"
# Update README + CHANGELOG.md
git add version.py README.md CHANGELOG.md
git commit -m "v1.1.1 — Wave 8a retrofit + hardening (commons-backed)"
git push origin main

git checkout -b release/v1.1.1-rc1
git push origin release/v1.1.1-rc1
git tag -a v1.1.1-rc1 -m "ValveMaster v1.1.1 RC1 — Wave 8a retrofit"
git push origin v1.1.1-rc1

.\build.bat
# Verify: updater zip contract = exe-only (ADR-003)
```

#### 4. Job Tracker — bump version + RC (hardening already merged)

```
# in Job Tracker repo
git checkout main
git pull origin main
# Bump version.py: __version__ = "1.8.6"
# Update README + CHANGELOG.md
git add version.py README.md CHANGELOG.md
git commit -m "v1.8.6 — Wave 8b retrofit + hardening (commons-backed)"
git push origin main

git checkout -b release/v1.8.6-rc1
git push origin release/v1.8.6-rc1
git tag -a v1.8.6-rc1 -m "Job Tracker v1.8.6 RC1 — Wave 8b retrofit"
git push origin v1.8.6-rc1

.\build.bat
# Verify: updater zip contract = full-folder (expected_internal=True)
```

---

## 5. Validation checklist per app

Every RC build must pass these gates before the RC tag is considered baked:

### Common (all 4 apps)

- [ ] Source-mode `compileall` clean
- [ ] Tests pass (where applicable — CAD + Checkout have no test dir; ValveMaster has 156 tests; Job Tracker has 29)
- [ ] `.venv` is Python 3.12.x (canonical per ADR-014)
- [ ] `build.bat` runs end-to-end without error
- [ ] All 4 build artifacts produced (`<App>.exe` + `_internal/`, `<App>Setup.exe`, `<App>.zip`, `<App>_FullInstall.zip`)
- [ ] Frozen exe launches without traceback (offscreen smoke or interactive)
- [ ] Installer (`<App>Setup.exe`) installs cleanly to `{localappdata}\ATS Inc\<App>`
- [ ] Installed exe launches
- [ ] 5-min idle interactive S1 observation — no quarantine, no kill / relaunch
- [ ] Visual review — ≈ 0% change vs the prior released version
- [ ] User-data path preserved (`%APPDATA%\ATS Inc\<App>`)
- [ ] Upgrade smoke: install from prior release → install RC over the top → user data + settings preserved

### Per-app specifics

#### Phoenix CAD
- [ ] BricsCAD integration buttons render (don't need active COM session — just UI presence)
- [ ] Layout canvas renders
- [ ] Parts catalog loads
- [ ] Updater zip contract: full-folder (exe + `_internal/*` at root)

#### Phoenix Checkout
- [ ] Open one of the 5 xlsx templates (`checkout_template`, `template_gex`, `template_mav`, `template_cscp_fh`, `template_pbc_room`) — end-to-end openpyxl validation per the post-hardening fix
- [ ] Export a small checkout sheet to xlsx (writes path via `openpyxl.cell._writer` — second openpyxl validation)
- [ ] Tag preview / status renders
- [ ] Updater zip contract: **exe-only** (1 entry)

#### ValveMaster
- [ ] Valve decode flow works (model number → decoded fields rendering)
- [ ] Decoded Fields color-state correctness (valid = green, invalid = red — Wave 8a B8a fix)
- [ ] Inventory / parts list dialog opens
- [ ] CFM calculator opens
- [ ] Updater zip contract: **exe-only** (ADR-003, 1 entry)
- [ ] AppId GUID `{A7F3C2D1-9B4E-4F6A-8C3D-1E5B7A9F2C4D}` preserved (Inno Setup upgrade detection)

#### Job Tracker
- [ ] Login dialog opens; admin auth works
- [ ] Project list + task table renders
- [ ] Financials dashboard opens (xlsb load via pyxlsb — runtime-critical)
- [ ] Notes window + change-order window open
- [ ] RSS export functional
- [ ] Updater zip contract: full-folder (`expected_internal=True`)
- [ ] AppId absent in installer.iss (preserves AppName-hashed upgrade detection)

---

## 6. Artifact list per app

Each build produces 4 artifacts. Operator uploads only the 2 GitHub-Release artifacts (installer + updater zip); the full-install zip is operator-archive only.

| App | Exe folder | Installer | Updater zip (GH Release) | Full-install zip (operator archive) |
|-----|------------|-----------|---------------------------|--------------------------------------|
| Phoenix CAD | `dist\LabLayoutTool\` | `dist\LabLayoutToolSetup.exe` | `dist\LabLayoutTool.zip` (full-folder) | `dist\LabLayoutTool_FullInstall.zip` |
| Phoenix Checkout | `dist\PhoenixCheckoutTool\` | `dist\PhoenixCheckoutToolSetup.exe` | `dist\PhoenixCheckoutTool.zip` (exe-only) | `dist\PhoenixCheckoutTool_FullInstall.zip` |
| ValveMaster | `dist\PhoenixMasterTool\` | `dist\PhoenixMasterToolSetup.exe` | `dist\PhoenixMasterTool.zip` (exe-only, ADR-003) | `dist\PhoenixMasterTool_FullInstall.zip` |
| Job Tracker | `dist\ProjectTrackingTool\` | `dist\ProjectTrackingToolSetup.exe` | `dist\ProjectTrackingTool.zip` (full-folder) | `dist\ProjectTrackingTool_FullInstall.zip` |

---

## 7. Tag plan

| App | RC tag | Final tag (post-bake) | Tag commit |
|-----|--------|-----------------------|------------|
| Phoenix CAD | `v0.1.2-rc1` | `v0.1.2` | merge commit of release-hardening into master (annotated tag, same SHA gets re-tagged from `-rc1` to final after bake) |
| Phoenix Checkout | `v1.7.1-rc1` | `v1.7.1` | merge commit of release-hardening into main |
| ValveMaster | `v1.1.1-rc1` | `v1.1.1` | version-bump commit on main |
| Job Tracker | `v1.8.6-rc1` | `v1.8.6` | version-bump commit on main |

**Tag promotion** (RC → final) options:
- (a) **Re-tag in place** — delete the `-rc1` tag and re-create as the final at the same SHA. Cleanest history; tag list shows only the final.
- (b) **Keep both tags** — `-rc1` becomes a forensic record; final is a fresh annotated tag at the same SHA. More history but easier to point at "this exact RC was promoted to release."

Recommend **(b)** — keeps the RC tag as forensic evidence.

---

## 8. GitHub Release draft plan

For each app, after RC bake passes:

### Draft a GitHub Release per app (NOT publish yet)

| Field | Value |
|-------|-------|
| Tag | `v0.1.2` / `v1.7.1` / `v1.1.1` / `v1.8.6` |
| Title | `<App> v<X.Y.Z>` |
| Description | CHANGELOG.md excerpt for this version + retrofit/hardening summary + link back to commons docs |
| Mark as latest | yes (per repo) |
| Assets (uploaded) | `<App>Setup.exe` + `<App>.zip` |
| Pre-release | NO (set only if more bake needed) |

### Release description template (per app)

```markdown
# <App Name> v<X.Y.Z>

## Highlights

- **Commons-backed**: <App> is now part of the Phoenix UI Platform shared library (`phoenix_commons`). Theme, widgets, paths, and updater are sourced from the family canon.
- **Build hardened**: PyInstaller pipeline now uses `--noupx` + stdlib excludes + canonical Python 3.12 venv (per FROZEN_BUILD_BASELINE / ADR-014). S1-safe profile.
- **Operator-visible change**: ≈ 0% (facade retrofit only — no UI redesign, no feature change).

## Updater compatibility

This release uses the <full-folder | exe-only> updater payload contract. Existing v<prior> installations will receive the update via the in-app banner.

## Install

- New users: download `<App>Setup.exe` and run.
- Existing users: the in-app updater will download `<App>.zip` and self-replace.

## What changed

<CHANGELOG excerpt for this version>

## Cross-reference

This release is part of the Phoenix family coordinated RC arc 2026-05-29 — see `phoenix-commons/docs/ui-platform-baseline-v1/PHOENIX_4_APP_RC_RELEASE_PLAN.md`.
```

### Asset upload order per app

1. Upload `<App>Setup.exe` first (installer)
2. Upload `<App>.zip` second (updater)
3. Verify both assets are downloadable from the release page
4. Publish (or keep as draft until operator clicks "Publish")

---

## 9. Explicit stop conditions

Halt the release at any of these:

### Per-app blockers

- **CAD**: BricsCAD COM integration regressed in installed exe
- **CAD**: visual change > 5% vs deployed v0.1.1
- **Checkout**: xlsx template load fails in installed exe (validates the openpyxl fix end-to-end)
- **Checkout**: exe-only updater zip layout drifts (must be 1 entry, `['PhoenixCheckoutTool.exe']`)
- **ValveMaster**: Decoded Fields color states regress
- **ValveMaster**: AppId `{A7F3C2D1-...}` differs from prior installer
- **Job Tracker**: financials dashboard or xlsb load fails
- **Job Tracker**: AppId accidentally added to installer.iss (would break upgrade detection)

### Cross-cutting blockers

- S1 quarantine during any 5-min idle observation
- Updater zip contract changes for ANY tool (must match prior expected shape)
- AppId / install path / user-data path drift for ANY tool
- Upgrade smoke fails (user data lost on RC install over prior version)
- Any frozen exe fails to launch
- pip resolver can't satisfy pinned reqs in fresh 3.12 venv

If any blocker fires: **STOP, do not publish, do not upload assets, surface to operator for triage.**

---

## 10. Confirmation

- **No production deployment occurred** during this planning session.
- **No GitHub Release published** (no draft authored yet either).
- **No updater assets uploaded.**
- **No RC tags created.**
- **No RC branches created.**
- **No version.py bumps applied.**
- **No CHANGELOG entries authored** (will happen at the version-bump commit per app).
- **No installer / updater contract changes.**

This document is the plan only. Execution requires operator approval per step.

---

## Operator decisions — APPROVED 2026-05-29

| # | Decision | Resolution |
|---|----------|------------|
| 1 | Version-bump policy | ✅ **APPROVED — patch-bump all 4.** CAD → `v0.1.2-rc1`, Checkout → `v1.7.1-rc1`, ValveMaster → `v1.1.1-rc1`, Job Tracker → `v1.8.6-rc1` |
| 2 | Tag-promotion policy | ✅ **APPROVED — keep `-rc1` tags immutable as forensic markers.** Do NOT re-tag in place. If RC passes bake, create final stable tags as separate annotated tags at the same merge-commit SHA. |
| 3 | Bake window | ✅ **APPROVED — 1-day minimum per RC.** Operator may extend by discretion if issues appear. |
| 4 | Build order | ✅ **APPROVED — CAD → Checkout → ValveMaster → Job Tracker.** |
| 5 | Asset upload trigger | ✅ **APPROVED — wait until all 4 RC builds pass before uploading release assets.** Draft release notes may be prepared earlier; no GitHub Release asset upload until the full 4-app RC set is validated. |

All 5 decisions resolved. RC execution unblocked.

### Execution ordering reminder (Decision #4 + Decision #5 combined)

```
For tool in [CAD, Checkout, ValveMaster, Job Tracker]:
    1. Merge hardening branch to mainline (CAD + Checkout only — VM + JT already merged)
    2. Bump version.py + README + CHANGELOG (this commit becomes the RC HEAD)
    3. Create release/v<X.Y.Z>-rc1 branch
    4. Create annotated `v<X.Y.Z>-rc1` tag on that commit
    5. Push branch + tag
    6. Build artifacts (`build.bat`)
    7. Operator interactive validation (5-min S1 + visual; xlsx round-trip for Checkout; upgrade smoke from prior install)
    8. Minimum 1-day bake (Decision #3)

After ALL 4 RCs pass bake (Decision #5):
    9. Draft GitHub Release per tool (description + version metadata; assets NOT uploaded yet)
    10. Upload installer + updater zip to each draft (in CAD → Checkout → VM → JT order)
    11. Final operator approval to publish each release
    12. Create final stable tags (`v0.1.2`, `v1.7.1`, `v1.1.1`, `v1.8.6`) — separate annotated tags at the same SHA as the `-rc1` tags (Decision #2)
```

---

*End of Phoenix 4-app RC release plan. All 5 decisions resolved 2026-05-29. RC execution awaits operator kickoff signal.*
