# Phoenix Family — 4-App Final Release Promotion Plan

> **✅ EXECUTED + SUPERSEDED 2026-06-01.** This plan was carried out in full: stable tags created, drafts authored, assets uploaded, and **all 4 releases published**. Current canonical state is `PHOENIX_4_APP_RELEASE_CLOSURE_REPORT.md`. The forward-looking "no releases published / releases remain drafts" language below reflects the plan's state-at-authoring (2026-05-31) and is retained for forensic record only — it no longer describes current reality.
>
> **Status (at authoring):** plan only — no tags created, no releases published, no assets uploaded in this document.
> **Date:** 2026-05-31.
> **Scope:** promote validated RCs (`-rc1`) to final stable releases for all 4 production tools.
> **Companions:** `PHOENIX_4_APP_RC_RELEASE_PLAN.md`, `PHOENIX_4_APP_RC_VALIDATION_SUMMARY.md`, per-RC reports.

---

## 1. RC validation summary

All 4 RCs operator-validated. No blockers.

| App | RC tag | Pass date |
|-----|--------|-----------|
| Phoenix CAD / Lab Layout Tool | `v0.1.2-rc1` | 2026-05-30 |
| Phoenix Checkout Tool | `v1.7.1-rc1` | 2026-05-30 |
| ValveMaster / Phoenix Master Tool | `v1.1.1-rc1` | 2026-05-30 |
| Job Tracker / Project Tracking Tool | `v1.8.6-rc1` | 2026-05-31 |

Per-RC operator-gates detail in `PHOENIX_4_APP_RC_VALIDATION_SUMMARY.md` §§ 1-4.

---

## 2. Final stable version targets

| App | Final stable |
|-----|--------------|
| Phoenix CAD | **v0.1.2** |
| Phoenix Checkout | **v1.7.1** |
| ValveMaster / Phoenix Master Tool | **v1.1.1** |
| Job Tracker / Project Tracking Tool | **v1.8.6** |

`version.py` already contains these values in the RC commits — **no further bumps planned, no further code changes**.

---

## 3. Tag / SHA mapping

Final stable tags point at the **exact same SHA** as the matching RC tag. RC tags remain immutable per Decision #2.

| App | Repo | RC tag SHA | Final stable tag (to create) | Same SHA? |
|-----|------|------------|------------------------------|-----------|
| Phoenix CAD | `JustinGlave/lab-layout-tool` | `35a06610b0c655e9652d9540070afd37fc97f820` | `v0.1.2` | ✅ |
| Phoenix Checkout | `JustinGlave/Phoenix-Checkout-Tool` | `274b0a8f2914ba4d9123bf8a4c3afe1d03e74077` | `v1.7.1` | ✅ |
| ValveMaster | `JustinGlave/valve-master-tool` (origin remap from `phoenix-master-tool` per Inno Setup AppName rename) | `e6eefa15b89fba851b1e8acd2d94e83035c58c9a` | `v1.1.1` | ✅ |
| Job Tracker | `JustinGlave/project-tracking-tool` | `689e8ee06979b8ff737caa654f53f1c2a0928c8b` | `v1.8.6` | ✅ |

---

## 4. Artifact inventory

All 12 release-bound artifacts confirmed on local disk in each repo's `dist/`. No rebuild required.

| App | Installer | Updater zip | Full-install zip |
|-----|-----------|--------------|-------------------|
| **Phoenix CAD** | `dist\LabLayoutToolSetup.exe` (36.3 MB) | `dist\LabLayoutTool.zip` (55.6 MB, 305 entries) | `dist\LabLayoutTool_FullInstall.zip` (55.6 MB) |
| **Phoenix Checkout** | `dist\PhoenixCheckoutToolSetup.exe` | `dist\PhoenixCheckoutTool.zip` (1 entry) | `dist\PhoenixCheckoutTool_FullInstall.zip` |
| **ValveMaster / PMT** | `dist\PhoenixMasterToolSetup.exe` | `dist\PhoenixMasterTool.zip` (1 entry) | `dist\PhoenixMasterTool_FullInstall.zip` |
| **Job Tracker** | `dist\ProjectTrackingToolSetup.exe` (37.3 MB) | `dist\ProjectTrackingTool.zip` (54.8 MB, 260 entries) | `dist\ProjectTrackingTool_FullInstall.zip` (54.9 MB) |

### Classification

**GitHub Release-bound (MUST upload — 8 artifacts total):**
- Installer per app (`<App>Setup.exe`) × 4
- Updater zip per app (`<App>.zip`) × 4 — required for auto-updater to find the asset

**Operator-archive (OPTIONAL — operator's call — 4 artifacts):**
- Full-install zip per app (`<App>_FullInstall.zip`) × 4 — historically uploaded for manual users; redundant with installer for most use cases

---

## 5. Updater contract confirmation

Re-verified against actual zip layouts on 2026-05-31:

| App | Asset name (DO NOT RENAME) | Contract | Validated layout |
|-----|----------------------------|----------|-------------------|
| Phoenix CAD | `LabLayoutTool.zip` | **full-folder** (`expected_internal=True`) | 305 entries; exe at root + `_internal/*` |
| Phoenix Checkout | `PhoenixCheckoutTool.zip` | **exe-only** (`expected_internal=False`) | 1 entry: `['PhoenixCheckoutTool.exe']` |
| ValveMaster | `PhoenixMasterTool.zip` | **exe-only** (`expected_internal=False`, ADR-003) | 1 entry: `['PhoenixMasterTool.exe']` |
| Job Tracker | `ProjectTrackingTool.zip` | **full-folder** (`expected_internal=True`) | 260 entries; exe at root + `_internal/*` |

**Asset filenames must match exactly** — the per-tool `updater.py` (commons facade) looks for these specific names. Any rename breaks auto-update for existing user-base.

---

## 6. Release notes drafts

Same tone across all 4 — release-hardening + commons-backed alignment, no functional changes, S1-validated, updater contract preserved. Each draft is concise (≤ 200 words operator-facing copy).

### 6.1 Phoenix CAD / Lab Layout Tool v0.1.2

```markdown
# Lab Layout Tool v0.1.2

**Release hardening + commons-backed platform alignment. No functional changes.**

## What changed

- Build pipeline aligned with the Phoenix `FROZEN_BUILD_BASELINE`
  (Python 3.12 canonical, `--noupx`, stdlib excludes, commons preflight,
  Step 0 full cleanup).
- Theme + widgets + paths + updater now consume the `phoenix-commons`
  shared library (Phase 3A retrofit, merged 2026-05-19, `79c7003`).
- Visual change vs v0.1.1: ≈ 0% (theme-neutral facade swap).
- S1-validated frozen build under Python 3.12.

## Auto-updater compatibility

Existing v0.1.1 installations will receive this update via the in-app
banner. Updater zip is the full-folder payload (exe + `_internal/`).

## Install

- New users: download `LabLayoutToolSetup.exe` and run.
- Existing users: in-app updater will download `LabLayoutTool.zip`.

## Cross-reference

Coordinated Phoenix family RC arc — see
`phoenix-commons/docs/ui-platform-baseline-v1/PHOENIX_4_APP_FINAL_RELEASE_PROMOTION_PLAN.md`.
```

### 6.2 Phoenix Checkout Tool v1.7.1

```markdown
# Phoenix Checkout Tool v1.7.1

**Release hardening + commons-backed platform alignment + openpyxl
dependency declaration. No functional changes.**

## What changed

- Build pipeline aligned with the Phoenix `FROZEN_BUILD_BASELINE`.
- Theme + widgets + paths + updater now consume `phoenix-commons`
  (Phase 3B retrofit, merged 2026-05-19, `26a4689`).
- `openpyxl` runtime dependency now declared (PyInstaller bundle fixed
  post-hardening; existing user templates load correctly).
- Visual change vs v1.7.0: ≈ 0%.
- S1-validated frozen build under Python 3.12.

## Auto-updater compatibility

Existing v1.7.0 installations will receive this update via the in-app
banner. Updater zip is the **exe-only** payload (per ADR-003).

## Install

- New users: download `PhoenixCheckoutToolSetup.exe` and run.
- Existing users: in-app updater will download `PhoenixCheckoutTool.zip`.

## Cross-reference

Coordinated Phoenix family RC arc — see
`phoenix-commons/docs/ui-platform-baseline-v1/PHOENIX_4_APP_FINAL_RELEASE_PROMOTION_PLAN.md`.
```

### 6.3 ValveMaster / Phoenix Master Tool v1.1.1

```markdown
# Phoenix Master Tool v1.1.1

**Wave 8a commons retrofit + release hardening. No functional changes.**

## What changed

- Theme + widgets + paths + updater now consume `phoenix-commons`
  (Wave 8a retrofit, merged 2026-05-26, forensic tag
  `valvemaster-retrofit-v1.1.0-pre`).
- Build pipeline aligned with the Phoenix `FROZEN_BUILD_BASELINE`
  (Python 3.12, `--noupx`, stdlib excludes, commons preflight,
  Step 0 full cleanup).
- Decoded Fields valid/invalid color states preserved end-to-end
  (Wave 8a B8a fix — valid model segments render green, invalid
  segments render red).
- Visual change vs v1.1.0: ≈ 0%.
- S1-validated frozen build under Python 3.12.

## Auto-updater compatibility

Existing v1.1.0 installations will receive this update via the in-app
banner. Updater zip is the **exe-only** payload per ADR-003.
Inno Setup AppId `{A7F3C2D1-9B4E-4F6A-8C3D-1E5B7A9F2C4D}` preserved
for upgrade detection.

## Install

- New users: download `PhoenixMasterToolSetup.exe` and run.
- Existing users: in-app updater will download `PhoenixMasterTool.zip`.

## Cross-reference

Coordinated Phoenix family RC arc — see
`phoenix-commons/docs/ui-platform-baseline-v1/PHOENIX_4_APP_FINAL_RELEASE_PROMOTION_PLAN.md`.
```

### 6.4 Job Tracker / Project Tracking Tool v1.8.6

```markdown
# Project Tracking Tool v1.8.6

**Wave 8b commons retrofit + release hardening + `starter_package/`
removal. No functional changes.**

## What changed

- Theme + widgets + paths + updater now consume `phoenix-commons`
  (Wave 8b retrofit, merged 2026-05-28, forensic tag
  `job-tracker-retrofit-v1.8.5-pre`).
- Build pipeline aligned with the Phoenix `FROZEN_BUILD_BASELINE`
  (Python 3.12, `--noupx`, stdlib excludes, commons preflight,
  Step 0 full cleanup); existing sanity-check pipeline preserved
  (README version + py_compile + unittest discover + zip-layout
  post-verify).
- `starter_package/` historical scaffold removed (Wave 8b B7; ported
  to commons during Phase 1 of the platform rollout).
- Excel / xlsb / PDF integrations (`openpyxl`, `pyxlsb`, `reportlab`)
  preserved verbatim — pinned in `requirements.txt`, hidden imports
  intact in `build.bat`.
- Financials + auth + change-order + RSS + notes subsystems untouched.
- Visual change vs v1.8.5: ≈ 0%.
- S1-validated frozen build under Python 3.12.

## Auto-updater compatibility

Existing v1.6.0..v1.8.5 installations will receive this update via the
in-app banner. Updater zip is the **full-folder** payload
(`expected_internal=True`). Inno Setup AppName-hashed upgrade detection
preserved (no explicit AppId added, per the user-base upgrade contract).

## Install

- New users: download `ProjectTrackingToolSetup.exe` and run.
- Existing users: in-app updater will download `ProjectTrackingTool.zip`.

## Cross-reference

Coordinated Phoenix family RC arc — see
`phoenix-commons/docs/ui-platform-baseline-v1/PHOENIX_4_APP_FINAL_RELEASE_PROMOTION_PLAN.md`.
```

---

## 7. Stable tag plan (commands only — do NOT execute yet)

Per app, run from the repo's local clone. Tag points at the same SHA as the RC tag.

### Phoenix CAD
```bash
cd "C:/Users/justing/PycharmProjects/Phoenix_CAD_Tool"
git tag -a v0.1.2 35a0661 \
  -m "Lab Layout Tool v0.1.2 — release hardening + commons-backed platform alignment, no functional changes"
git push origin v0.1.2
```

### Phoenix Checkout
```bash
cd "C:/Users/justing/PycharmProjects/Phoenix-Checkout-Tool"
git tag -a v1.7.1 274b0a8 \
  -m "Phoenix Checkout Tool v1.7.1 — release hardening + commons-backed platform alignment + openpyxl dependency declared, no functional changes"
git push origin v1.7.1
```

### ValveMaster
```bash
cd "C:/Users/justing/PycharmProjects/ValveMasterTool"
git tag -a v1.1.1 e6eefa1 \
  -m "Phoenix Master Tool v1.1.1 — Wave 8a commons retrofit + release hardening, no functional changes"
git push origin v1.1.1
```

### Job Tracker
```bash
cd "C:/Users/justing/PycharmProjects/Job Tracker"
git tag -a v1.8.6 689e8ee \
  -m "Project Tracking Tool v1.8.6 — Wave 8b commons retrofit + release hardening + starter_package removal, no functional changes"
git push origin v1.8.6
```

All 4 stable tags are **separate from the `-rc1` tags** (no re-tagging in place per Decision #2).

---

## 8. GitHub Release draft plan per repo

Repeat the pattern per app. Title format: `<App Name> v<X.Y.Z>`.

### Per-app draft fields

| Field | Phoenix CAD | Phoenix Checkout | ValveMaster | Job Tracker |
|-------|-------------|-------------------|-------------|-------------|
| **Title** | `Lab Layout Tool v0.1.2` | `Phoenix Checkout Tool v1.7.1` | `Phoenix Master Tool v1.1.1` | `Project Tracking Tool v1.8.6` |
| **Target tag** | `v0.1.2` | `v1.7.1` | `v1.1.1` | `v1.8.6` |
| **Description body** | § 6.1 | § 6.2 | § 6.3 | § 6.4 |
| **Mark as latest** | yes | yes | yes | yes |
| **Pre-release** | no | no | no | no |
| **Assets to upload (required)** | `LabLayoutToolSetup.exe` + `LabLayoutTool.zip` | `PhoenixCheckoutToolSetup.exe` + `PhoenixCheckoutTool.zip` | `PhoenixMasterToolSetup.exe` + `PhoenixMasterTool.zip` | `ProjectTrackingToolSetup.exe` + `ProjectTrackingTool.zip` |
| **Assets optional (operator's choice)** | `LabLayoutTool_FullInstall.zip` | `PhoenixCheckoutTool_FullInstall.zip` | `PhoenixMasterTool_FullInstall.zip` | `ProjectTrackingTool_FullInstall.zip` |

### Verification checklist before pressing Publish (per app)

- [ ] Target tag exists on `origin` and points at the expected SHA (matches the `-rc1` tag SHA)
- [ ] Release notes body matches the approved draft from § 6
- [ ] Title matches "<App Name> v<X.Y.Z>" exactly
- [ ] Installer (`<App>Setup.exe`) uploaded and downloadable
- [ ] Updater zip (`<App>.zip`) uploaded and downloadable
- [ ] Asset filename exactly matches updater contract (case-sensitive)
- [ ] Full-install zip uploaded (if operator chose this option) — otherwise not present
- [ ] "Latest release" checkbox set
- [ ] Pre-release checkbox NOT set
- [ ] Operator has reviewed the draft and explicitly approves publication

---

## 9. Upload checklist (post-tag, pre-publish)

Steps 1-3 below are per-app; step 4 is once-after-all-4.

1. **Push stable tag** (see § 7 commands)
2. **Create GitHub Release draft** at that tag (web UI or `gh release create --draft`)
3. **Upload required assets** (installer + updater zip)
4. (Cross-cutting) **Final operator approval to publish all 4 releases** — only after every draft is reviewed

Asset upload order within each draft (CAD → Checkout → VM → JT):
1. Installer first
2. Updater zip second
3. Full-install zip third (only if operator chose to include)

---

## 10. Final operator decision / approval checklist

Each numbered item below requires an explicit operator approval. None of these have been done yet.

1. ❌ **Create 4 final stable tags** (`v0.1.2`, `v1.7.1`, `v1.1.1`, `v1.8.6`) — local first
2. ❌ **Push 4 final stable tags** to origin
3. ❌ **Create 4 GitHub Release drafts** at the 4 final tags (titles + descriptions per § 6/§ 8)
4. ❌ **Upload installer + updater zip assets** to all 4 drafts (CAD → Checkout → VM → JT order)
5. ❌ **(Optional) Upload `*_FullInstall.zip` to drafts** — operator's call per app
6. ❌ **Publish all 4 releases** — final operator approval gate; releases go live and become the "latest" downloadable releases

Until step 6, releases remain drafts and are not visible to end users.

---

## 11. Confirmation

- **No final stable tags created** — only the immutable `-rc1` tags exist.
- **No GitHub Releases published or drafted on GitHub** — drafts described in this document are pre-authoring only.
- **No assets uploaded** to GitHub or anywhere else.
- **No source code changed** since the RC commits.
- **No `version.py` changes** since the RC commits (versions already at the targeted final values).
- **No updater contract changes**.
- **No `installer.iss` changes** — AppId / install path / user-data path preserved per Decision #8 and prior per-tool conventions.
- **No production deployment.**
- **No commits, no pushes, no remote state changes** triggered by this document.

### Stop conditions — none triggered

- ✅ All 4 artifacts present per app (12 total)
- ✅ All 4 RC tags exist + point at expected SHAs
- ✅ All 4 updater zip contracts match expected (CAD full-folder, Checkout exe-only, VM exe-only, JT full-folder)
- ✅ No source-affecting uncommitted changes (only untracked dev venvs + 1 operator review doc in Checkout — none staged, none release-affecting)
- ✅ Release notes do not require any product/version-policy decision (notes are factual, no marketing language)

---

## Awaiting operator approval

Plan is ready. Next operator step: approve item 1 (create final stable tags) — or approve a different starting point per § 10.

No release publication or asset upload will happen without explicit operator approval per § 10 step.
