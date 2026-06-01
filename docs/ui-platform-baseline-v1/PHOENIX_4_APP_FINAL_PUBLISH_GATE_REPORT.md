# Phoenix Family — 4-App Final Publish Gate Report

> **Status:** all 4 drafts verified publish-ready. **Awaiting explicit operator publish approval.**
> **Date:** 2026-06-01.
> **Companions:** `PHOENIX_4_APP_FINAL_RELEASE_DRAFTS_REPORT.md`, `PHOENIX_4_APP_SOURCE_BLOAT_AUDIT.md`.

---

## 1. Source-bloat audit result

Per `PHOENIX_4_APP_SOURCE_BLOAT_AUDIT.md` (pushed earlier today as `492fb51`):

- ✅ **No `dist/`** tracked in any of the 4 repos
- ✅ **No `build/`** tracked
- ✅ **No `_internal/`** tracked
- ✅ **No `.venv/` / `.venv312/` / `.venv314-bak/`** tracked
- ✅ **No `site-packages/`** tracked
- ✅ **No `*.pyc` / `__pycache__`** tracked
- ✅ Total tracked source across 4 repos: 189 files, ~33,000 `.py` LOC, ~64,000 total tracked LOC
- ⚠ `.gitignore` venv-suffix gap exists in 3 of 4 repos — **deferred to post-release housekeeping** per operator direction; **does not block publication**

**Release publication is not bloat-blocked.**

---

## 2. Final draft verification table

All 4 draft releases verified via `gh release view` against expected metadata:

| Dimension | Phoenix CAD | Phoenix Checkout | ValveMaster | Job Tracker |
|-----------|-------------|-------------------|-------------|-------------|
| Repo | `JustinGlave/lab-layout-tool` | `JustinGlave/Phoenix-Checkout-Tool` | `JustinGlave/phoenix-master-tool` | `JustinGlave/project-tracking-tool` |
| Tag (stable) | `v0.1.2` | `v1.7.1` | `v1.1.1` | `v1.8.6` |
| Tag SHA | `35a0661` | `274b0a8` | `e6eefa1` | `689e8ee` |
| Title (expected) | `Lab Layout Tool v0.1.2` | `Phoenix Checkout Tool v1.7.1` | `Phoenix Master Tool v1.1.1` | `Project Tracking Tool v1.8.6` |
| Title (actual) | ✅ matches | ✅ matches | ✅ matches | ✅ matches |
| `version.py` matches tag | ✅ `0.1.2` | ✅ `1.7.1` | ✅ `1.1.1` | ✅ `1.8.6` |
| `draft` | ✅ true | ✅ true | ✅ true | ✅ true |
| `prerelease` | ✅ false | ✅ false | ✅ false | ✅ false |
| `publishedAt` | ✅ null | ✅ null | ✅ null | ✅ null |
| Asset count | ✅ 2 | ✅ 2 | ✅ 2 | ✅ 2 |
| Uncommitted source changes | ✅ none | ✅ none | ✅ none | ✅ none |
| Staged source changes | ✅ none | ✅ none | ✅ none | ✅ none |

Every column green across every app.

---

## 3. Asset verification table

| App | Installer | Installer size | Updater zip | Updater zip size |
|-----|-----------|----------------|--------------|--------------------|
| Phoenix CAD | `LabLayoutToolSetup.exe` | 38,016,778 B (36.3 MB) | `LabLayoutTool.zip` | 58,264,923 B (55.6 MB) |
| Phoenix Checkout | `PhoenixCheckoutToolSetup.exe` | 41,381,486 B (39.5 MB) | `PhoenixCheckoutTool.zip` | 4,593,289 B (4.4 MB) |
| ValveMaster | `PhoenixMasterToolSetup.exe` | 33,828,432 B (32.3 MB) | `PhoenixMasterTool.zip` | 2,044,232 B (1.9 MB) |
| Job Tracker | `ProjectTrackingToolSetup.exe` | 39,108,336 B (37.3 MB) | `ProjectTrackingTool.zip` | 57,508,860 B (54.8 MB) |

| Check | Result |
|-------|--------|
| Asset count per draft = 2 (installer + updater zip) | ✅ |
| No `*_FullInstall.zip` attached anywhere | ✅ |
| Asset filenames byte-exact match `updater.py` `ZIP_ASSET_NAME` constants | ✅ |
| All 8 assets present and downloadable | ✅ |

---

## 4. Updater contract confirmation

Re-verified at every step from RC build through draft upload. Final state:

| App | Contract | Validated layout | Auto-updater code-path |
|-----|----------|-------------------|--------------------------|
| Phoenix CAD | **full-folder** | 305 entries (exe + `_internal/*` at zip root) | commons `download_and_apply(info, exe_name="LabLayoutTool.exe", expected_internal=True)` |
| Phoenix Checkout | **exe-only** | 1 entry (`['PhoenixCheckoutTool.exe']`) | commons `download_and_apply(info, exe_name="PhoenixCheckoutTool.exe", expected_internal=False)` |
| ValveMaster | **exe-only** (ADR-003) | 1 entry (`['PhoenixMasterTool.exe']`) | commons `download_and_apply(info, exe_name="PhoenixMasterTool.exe", expected_internal=False)` |
| Job Tracker | **full-folder** | 260 entries (exe + `_internal/*` at zip root) | commons `download_and_apply(info, exe_name="ProjectTrackingTool.exe", expected_internal=True)` |

No drift since RC build. No drift since draft upload. Existing v<previous> installations will receive the correct payload via the in-app updater on publication.

---

## 5. Release notes verification

Each draft's release-notes body matches the template authored in `PHOENIX_4_APP_FINAL_RELEASE_PROMOTION_PLAN.md` § 6 and reaffirmed in `PHOENIX_4_APP_FINAL_RELEASE_DRAFTS_REPORT.md` § 6.

| Element | Per-draft state |
|---------|------------------|
| Title heading (`# <App Name> v<X.Y.Z>`) | ✅ |
| Subheading: "What changed" | ✅ |
| Subheading: "Auto-updater compatibility" | ✅ |
| Subheading: "Install" | ✅ |
| Subheading: "Cross-reference" link to commons promotion-plan doc | ✅ |
| Per-app callout: retrofit phase (Phase 3A / 3B / Wave 8a / Wave 8b) | ✅ |
| Per-app callout: visible-change band ("≈ 0%") | ✅ |
| Per-app callout: updater payload contract | ✅ |
| Per-app callout: S1-validated frozen build under Python 3.12 | ✅ |
| Tone factual; no overstated features | ✅ |

---

## 6. Remaining risks

**No release-blocking risks.** Three observations:

1. **`.gitignore` venv gap** in 3 of 4 repos — **deferred per operator direction**, not a publish blocker. The gap is "could-bite-later" not "is-biting-now": no venvs are actually in git history. Optional 1-line fix per repo, post-release.

2. **Operator interactive S1 was completed on each tool at RC build time** (CAD 2026-05-30, Checkout 2026-05-30, VM 2026-05-30, JT 2026-05-31). Between RC build + draft upload + this gate, no code or build artifact has changed — the validated artifacts are byte-for-byte what will publish. **No new S1 exposure.**

3. **Updater code-path will exercise on first published-release install** — the existing in-app updater logic in each tool was sized against pre-retrofit zip names + contracts (preserved across retrofit). On publish, an end-user click of "Install & Restart" should pull the correct zip and apply per its per-tool contract. **Not validated end-to-end on a live release** (only on the v0.1.1 → v0.1.2 / v1.7.0 → v1.7.1 / v1.1.0 → v1.1.1 / v1.8.5 → v1.8.6 upgrade smoke at operator validation time). This is the first publication of any retrofit work; first-user-update is the actual end-to-end test.

Risk classification:
- **#1** = doc-cleanup hygiene, low impact
- **#2** = no new risk
- **#3** = expected first-real-world test of the retrofit + hardening pipeline; mitigation is that all 4 contracts match prior conventions, so the existing user-base auto-updater logic exercises in the same shape

None of these justify a "Not ready" verdict.

---

## 7. Exact publish order

Per Decision #4 from `PHOENIX_4_APP_RC_RELEASE_PLAN.md`: **CAD → Checkout → ValveMaster → Job Tracker.**

### Commands (do NOT execute yet — operator approval required)

```bash
# 1. Phoenix CAD / Lab Layout Tool v0.1.2
gh release edit v0.1.2 \
  --draft=false \
  --latest \
  --repo JustinGlave/lab-layout-tool

# 2. Phoenix Checkout Tool v1.7.1
gh release edit v1.7.1 \
  --draft=false \
  --latest \
  --repo JustinGlave/Phoenix-Checkout-Tool

# 3. Phoenix Master Tool v1.1.1
gh release edit v1.1.1 \
  --draft=false \
  --latest \
  --repo JustinGlave/phoenix-master-tool

# 4. Project Tracking Tool v1.8.6
gh release edit v1.8.6 \
  --draft=false \
  --latest \
  --repo JustinGlave/project-tracking-tool
```

`--latest` marks each release as the "latest release" for its repo (visible in repo header, default download in `gh release download`). `--draft=false` flips the release from admin-only to publicly visible + makes the auto-updater path see it.

### Alternative ordering options

| Option | Description | Risk |
|--------|-------------|------|
| **Sequential publish (recommended)** | Publish CAD first; observe ≥ 10 min for any in-app updater traffic; then Checkout; then VM; then JT | Lowest — catches any unexpected first-publish issue before all 4 are exposed |
| **All-at-once publish** | Run all 4 `gh release edit` commands in a single batch | Higher — first-real-world test runs simultaneously on 4 different update contracts |
| **Pilot + batch** | Publish CAD first; if smoke-clean after observation, publish the remaining 3 in a single batch | Middle — minimizes wait without 4× full sequential |

---

## 8. Final operator approval checklist

Each item below requires explicit operator approval. None have happened yet.

| # | Action | Approval status |
|---|--------|------------------|
| 1 | Confirm draft titles + release notes match expectation (operator reviews each draft URL in browser) | ⏳ pending |
| 2 | Confirm asset filenames match updater contracts (CAD/JT full-folder, Checkout/VM exe-only) | ✅ already verified by audit — operator can re-confirm |
| 3 | Choose publish ordering option (sequential / all-at-once / pilot+batch) | ⏳ pending |
| 4 | Approve publication of **Phoenix CAD v0.1.2** (first in the canonical order) | ⏳ pending |
| 5 | Approve publication of **Phoenix Checkout Tool v1.7.1** | ⏳ pending |
| 6 | Approve publication of **Phoenix Master Tool v1.1.1** | ⏳ pending |
| 7 | Approve publication of **Project Tracking Tool v1.8.6** | ⏳ pending |
| 8 | (Optional) Authorize `*_FullInstall.zip` uploads to any draft before publication | ⏳ pending — operator can skip entirely |
| 9 | (Post-publish) Spot-check the auto-updater path on one tool by triggering an in-app update check from a prior-version installed instance | ⏳ pending |

### Approval phrases I'll act on

If operator says any of these I'll execute correspondingly:

| Operator phrase | Execution |
|-----------------|-----------|
| "Publish CAD" | execute step 4 only |
| "Publish Checkout" | execute step 5 only |
| "Publish ValveMaster" / "Publish PMT" | execute step 6 only |
| "Publish Job Tracker" / "Publish JT" / "Publish PTT" | execute step 7 only |
| "Publish all 4" / "Publish everything" | execute steps 4-7 sequentially with brief observation between each |
| "Publish CAD then pause" | execute step 4; report; await |
| "Upload `*_FullInstall.zip` for <App>" | upload to that draft before publish |

I will NOT publish without an explicit publish phrase. Browsing the audit / draft URLs does not trigger publication.

---

## 9. Confirmation

- **No source changed** in any of the 4 repos.
- **No tags changed.** RC tags (`-rc1`) remain immutable; stable tags (`v0.1.2` / `v1.7.1` / `v1.1.1` / `v1.8.6`) created earlier today and unchanged.
- **No assets uploaded** during this gate. The 8 assets uploaded yesterday remain attached.
- **No releases published.** All 4 in `draft: true` with `publishedAt: null`.
- **No `.gitignore` changes** (deferred to post-release per operator direction).
- **No version.py changes.**
- **No production deployment.**
- **No commits, no pushes** triggered by this gate (this report will be committed to `phoenix-commons` after authoring; it does not affect any tool's release state).

---

## Verdict

### **A — Ready to publish.**

All gates green:

- ✅ Source-bloat audit clean (4-app tracked source ~64k LOC; no generated artifacts in git)
- ✅ 4 drafts exist with correct titles, tags, draft state, prerelease state
- ✅ 8 assets uploaded with correct names byte-exact match to updater contracts
- ✅ No FullInstall zips attached (operator's call to add or skip)
- ✅ `version.py` matches tag for every app
- ✅ No uncommitted or staged source changes in any repo
- ✅ No release already published (`publishedAt: null` × 4)
- ✅ No updater contract drift
- ✅ Release notes factual and consistent

**Awaiting operator approval phrase** (see § 8). I will not execute any `gh release edit --draft=false` without explicit approval. The `.gitignore` venv gap remains explicitly deferred to post-release housekeeping.
