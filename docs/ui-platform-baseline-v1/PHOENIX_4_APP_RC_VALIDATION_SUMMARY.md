# Phoenix Family — 4-App RC Validation Summary

> **Status:** all 4 RCs operator-validated. Ready for GitHub Release drafting (Decision #5: assets upload only after all 4 baked) and/or final stable tag promotion (Decision #2: separate annotated tags at same SHA).
> **Date:** 2026-05-31.
> **Companions:** `PHOENIX_4_APP_RC_RELEASE_PLAN.md`, `PHOENIX_4_APP_RC_KICKOFF_READY.md`, per-RC reports in `WAVE_RC_*.md`.

---

## 1. Phoenix CAD / Lab Layout Tool — v0.1.2-rc1

**✅ PASSED 2026-05-30** (`WAVE_RC_CAD_v0.1.2_RC1_REPORT.md` § 8).

| Gate | Result |
|------|--------|
| Install from `LabLayoutToolSetup.exe` | ✅ |
| Launch installed `LabLayoutTool.exe` | ✅ |
| 5-min S1 observation | ✅ no quarantine, no kill/relaunch |
| Visual review | ✅ |
| Main window opens | ✅ |
| Parts catalog loads | ✅ |
| Layout canvas renders | ✅ |
| BricsCAD integration buttons visible | ✅ |

---

## 2. Phoenix Checkout Tool — v1.7.1-rc1

**✅ PASSED 2026-05-30** (`WAVE_RC_CHECKOUT_v1.7.1_RC1_REPORT.md`).

| Gate | Result |
|------|--------|
| Install from `PhoenixCheckoutToolSetup.exe` | ✅ |
| Launch installed `PhoenixCheckoutTool.exe` | ✅ |
| 5-min S1 observation | ✅ no quarantine, no kill/relaunch |
| Visual review | ✅ |
| Checkout form renders | ✅ |
| xlsx template load (openpyxl end-to-end) | ✅ |

---

## 3. ValveMaster / Phoenix Master Tool — v1.1.1-rc1

**✅ PASSED 2026-05-30** (`WAVE_RC_VM_v1.1.1_RC1_REPORT.md` § 11).

| Gate | Result |
|------|--------|
| Install from `PhoenixMasterToolSetup.exe` | ✅ |
| Launch installed `PhoenixMasterTool.exe` | ✅ |
| 5-min S1 observation | ✅ no quarantine, no kill/relaunch |
| Visual review | ✅ |
| Decoded Fields valid/invalid coloring | ✅ Wave 8a B8a fix preserved end-to-end |
| Main validation workflow | ✅ normal |

---

## 4. Job Tracker / Project Tracking Tool — v1.8.6-rc1

**✅ PASSED 2026-05-31** (`WAVE_RC_JOB_TRACKER_v1.8.6_RC1_REPORT.md` § 9).

| Gate | Result |
|------|--------|
| Install from `ProjectTrackingToolSetup.exe` | ✅ |
| Launch installed `ProjectTrackingTool.exe` | ✅ |
| 5-min S1 observation | ✅ no quarantine, no kill/relaunch |
| Visual review | ✅ |
| Main project list opens | ✅ |
| Financials / auth surfaces | ✅ no obvious launch-time regression |
| openpyxl / pyxlsb / reportlab packaging | ✅ no missing-dependency errors |

---

## 5. Artifact inventory

All 4 RCs produced 4 artifacts each. Total: 16 artifacts; 8 are GitHub-Release-bound (installer + updater zip per app); 8 are operator-archive only (full-install zip + raw exe folder per app — full-install zips are operator's choice to ship or not).

| App | Frozen exe folder | Installer | Updater zip | Full-install zip |
|-----|---------------------|-----------|--------------|-------------------|
| **Phoenix CAD** | `dist\LabLayoutTool\LabLayoutTool.exe` (2.20 MB) | `dist\LabLayoutToolSetup.exe` (36.3 MB) | `dist\LabLayoutTool.zip` (55.6 MB) | `dist\LabLayoutTool_FullInstall.zip` (55.6 MB) |
| **Phoenix Checkout** | `dist\PhoenixCheckoutTool\PhoenixCheckoutTool.exe` | `dist\PhoenixCheckoutToolSetup.exe` | `dist\PhoenixCheckoutTool.zip` (exe-only) | `dist\PhoenixCheckoutTool_FullInstall.zip` |
| **ValveMaster / PMT** | `dist\PhoenixMasterTool\PhoenixMasterTool.exe` | `dist\PhoenixMasterToolSetup.exe` | `dist\PhoenixMasterTool.zip` (exe-only) | `dist\PhoenixMasterTool_FullInstall.zip` |
| **Job Tracker** | `dist\ProjectTrackingTool\ProjectTrackingTool.exe` (~3 MB) | `dist\ProjectTrackingToolSetup.exe` (37.3 MB) | `dist\ProjectTrackingTool.zip` (54.8 MB) | `dist\ProjectTrackingTool_FullInstall.zip` (54.9 MB) |

All artifacts exist only in local `dist/` directories. **No uploads to GitHub or any other location have occurred.**

---

## 6. Updater zip contract per app

| App | Contract | Validation |
|-----|----------|------------|
| **Phoenix CAD** | **full-folder** (305 entries: exe + `_internal/*` at root) | matches `expected_internal=True` commons default; matches Phase 3A precedent |
| **Phoenix Checkout** | **exe-only** (1 entry: `['PhoenixCheckoutTool.exe']`) | matches `expected_internal=False` per commons facade override; preserves Phase 3B's exe-only contract |
| **ValveMaster / PMT** | **exe-only** (1 entry: `['PhoenixMasterTool.exe']`) | matches `expected_internal=False` per ADR-003; preserves the v1.1.0 user-base updater contract |
| **Job Tracker** | **full-folder** (260 entries: exe + `_internal/*` at root) | matches `expected_internal=True` commons default; preserves the pre-retrofit full-folder contract for v1.6.0..v1.8.5 user base |

All 4 contracts intact. No drift across the retrofit + hardening + RC build path.

---

## 7. Tags / RC branches per app

| App | RC branch | RC tag | Tag SHA | Mainline HEAD |
|-----|-----------|--------|---------|----------------|
| **Phoenix CAD** | `release/v0.1.2-rc1` | `v0.1.2-rc1` | `35a0661` | `master` @ `35a0661` |
| **Phoenix Checkout** | `release/v1.7.1-rc1` | `v1.7.1-rc1` | `274b0a8` | `main` @ `274b0a8` |
| **ValveMaster / PMT** | `release/v1.1.1-rc1` | `v1.1.1-rc1` | `e6eefa1` | `main` @ `e6eefa1` |
| **Job Tracker** | `release/v1.8.6-rc1` | `v1.8.6-rc1` | `689e8ee` | `main` @ `689e8ee` |

All RC branches + tags pushed to origin. All tags are **immutable forensic markers** per Decision #2 — do not re-tag in place.

Forensic retrofit tags preserved (separate from RC tags):
- `lab-layout-tool-retrofit-v0.1.2-pre` (Phase 3A merge)
- `phoenix-checkout-tool-retrofit-v1.7.0-pre` (Phase 3B merge, if it exists — confirm before drafting release notes)
- `valvemaster-retrofit-v1.1.0-pre` @ Wave 8a merge
- `job-tracker-retrofit-v1.8.5-pre` @ Wave 8b merge

---

## 8. Remaining blockers

**None.** All 4 RCs are operator-validated.

Status: the 4-app coordinated release sequence has cleared all technical gates. The remaining work is release-distribution + tag-promotion only — no further code changes, no further builds.

---

## 9. Recommended next step

The plan permits two parallel paths; operator chooses ordering.

### Path A — GitHub Release drafts first (recommended)

**Why first:** Drafts are revisable; tags are not. Drafting forces a final review of the release-notes wording across all 4 apps before any irreversible tag-promotion or asset-upload happens. Decision #5 allows draft authoring early; asset upload waits until all 4 are drafted.

Steps:
1. Author 4 GitHub Release drafts (one per app) using the description template in `PHOENIX_4_APP_RC_RELEASE_PLAN.md` § 8
2. Operator reviews + edits drafts as needed
3. Operator approval gate → proceed to Path B (final tags) + asset upload
4. Final operator approval to publish each draft

### Path B — Final stable tags

When operator approves promotion (likely after draft authoring + review):
- `v0.1.2` annotated tag at `35a0661` (separate tag, NOT renaming `-rc1`)
- `v1.7.1` annotated tag at `274b0a8`
- `v1.1.1` annotated tag at `e6eefa1`
- `v1.8.6` annotated tag at `689e8ee`

Push all 4. The `-rc1` tags stay as forensic record per Decision #2.

### Path C — Asset upload

After Paths A + B clear:
- Upload installer (`<App>Setup.exe`) + updater zip (`<App>.zip`) to each GitHub Release draft
- Final operator approval to publish each draft → 4 releases go live

---

## 10. Confirmation

- **No GitHub Release published.** No drafts authored on GitHub yet.
- **No assets uploaded** to GitHub or anywhere else.
- **No final stable tags created** (only `-rc1` immutable tags exist).
- **No production deployment.**
- **No version.py bumps** beyond the RC version-bump commits (`v0.1.2` / `v1.7.1` / `v1.1.1` / `v1.8.6` are stamped in `version.py` per app, on the RC commits — these are the version values that will ship as the final stable versions per Decision #1; no further bumps planned).
- **No CHANGELOG edits** since the RC commits.
- **No domain logic, financials, auth, theme, widget, updater contract, AppId, install path, or user-data path changes** since the original retrofit merges (Wave 8a / 8b / Phase 3A / 3B / release-hardening branches).

---

## Awaiting operator direction

Choose execution path:

1. **Author 4 GitHub Release drafts now** (recommended — most reviewable artifact next; revisable)
2. **Create final stable tags now** (commits the version names but tags are immutable post-push; less reviewable than drafts)
3. **Both in parallel** — draft on GitHub + tag locally before pushing tags
4. **Hold** — bake additional time before any release-distribution work

Whichever path you pick, no asset upload happens until you explicitly approve the publish step.
