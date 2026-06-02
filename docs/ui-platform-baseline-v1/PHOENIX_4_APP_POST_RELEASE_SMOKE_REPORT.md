# Phoenix Family — 4-App Post-Release Smoke + Updater Verification

> **Status:** all published releases verified usable + updater-discoverable.
> **Date:** 2026-06-01.
> **Companions:** `PHOENIX_4_APP_FINAL_PUBLISH_REPORT.md`, `PHOENIX_4_APP_FINAL_RELEASE_DRAFTS_REPORT.md`.

---

## 1. Release visibility results

| App | Repo visibility | Title correct | Tag correct | Draft | Prerelease | `/releases/latest` |
|-----|-----------------|---------------|-------------|-------|------------|---------------------|
| Phoenix CAD v0.1.2 | PUBLIC | ✅ `Lab Layout Tool v0.1.2` | ✅ `v0.1.2` | ✅ false | ✅ false | ✅ → `v0.1.2` |
| Phoenix Checkout v1.7.1 | PUBLIC | ✅ `Phoenix Checkout Tool v1.7.1` | ✅ `v1.7.1` | ✅ false | ✅ false | ✅ → `v1.7.1` |
| ValveMaster v1.1.1 | PUBLIC | ✅ `Phoenix Master Tool v1.1.1` | ✅ `v1.1.1` | ✅ false | ✅ false | ✅ → `v1.1.1` |
| Job Tracker v1.8.6 | PUBLIC | ✅ `Project Tracking Tool v1.8.6` | ✅ `v1.8.6` | ✅ false | ✅ false | ✅ → `v1.8.6` |

All 4 repos public, all 4 releases live + non-draft, all 4 `/releases/latest` REST endpoints resolve to the published stable tag. No `*_FullInstall.zip` attached to any (verified via `[.assets[].name] | map(select(test("FullInstall")))` = empty).

Live URLs:
- https://github.com/JustinGlave/lab-layout-tool/releases/tag/v0.1.2
- https://github.com/JustinGlave/Phoenix-Checkout-Tool/releases/tag/v1.7.1
- https://github.com/JustinGlave/phoenix-master-tool/releases/tag/v1.1.1
- https://github.com/JustinGlave/project-tracking-tool/releases/tag/v1.8.6

---

## 2. Asset download results

Each release's 2 assets downloaded fresh via `gh release download` and sha256-compared against the local validated `dist/` artifacts. **All 8 byte-identical.**

| App | Installer download | sha256 vs local | Updater zip download | sha256 vs local |
|-----|---------------------|------------------|------------------------|------------------|
| Phoenix CAD | `LabLayoutToolSetup.exe` (36.3 MB) | ✅ MATCH | `LabLayoutTool.zip` (55.6 MB) | ✅ MATCH |
| Phoenix Checkout | `PhoenixCheckoutToolSetup.exe` (39.5 MB) | ✅ MATCH | `PhoenixCheckoutTool.zip` (4.4 MB) | ✅ MATCH |
| ValveMaster | `PhoenixMasterToolSetup.exe` (32.3 MB) | ✅ MATCH | `PhoenixMasterTool.zip` (1.9 MB) | ✅ MATCH |
| Job Tracker | `ProjectTrackingToolSetup.exe` (37.3 MB) | ✅ MATCH | `ProjectTrackingTool.zip` (54.8 MB) | ✅ MATCH |

Filenames exact; bytes identical. The published assets are the same artifacts that passed operator RC validation — GitHub did not alter or re-compress anything on upload.

---

## 3. Updater zip layout results

Downloaded updater zips re-inspected (not the local copies — the actual published payloads):

| App | Zip | Entries | exe @ root | `_internal/` | Contract | Expected | Match |
|-----|-----|---------|------------|---------------|----------|----------|-------|
| Phoenix CAD | `LabLayoutTool.zip` | 305 | ✅ | ✅ | full-folder | full-folder | ✅ |
| Phoenix Checkout | `PhoenixCheckoutTool.zip` | 1 | ✅ (`['PhoenixCheckoutTool.exe']`) | n/a | exe-only | exe-only | ✅ |
| ValveMaster | `PhoenixMasterTool.zip` | 1 | ✅ (`['PhoenixMasterTool.exe']`) | n/a | exe-only (ADR-003) | exe-only | ✅ |
| Job Tracker | `ProjectTrackingTool.zip` | 260 | ✅ | ✅ | full-folder | full-folder | ✅ |

All 4 contracts match expectation. `download_and_apply` will validate each correctly: full-folder zips pass `expected_internal=True`; exe-only zips pass `expected_internal=False`.

---

## 4. Installer smoke results

**File-integrity smoke (headless):** Each downloaded installer's PE header verified — all 4 begin with the `MZ` (`4d5a`) magic = valid Windows PE executable. Sizes match the published asset sizes byte-for-byte.

| Installer | PE magic | Size |
|-----------|----------|------|
| `LabLayoutToolSetup.exe` | ✅ MZ | 38,016,778 B |
| `PhoenixCheckoutToolSetup.exe` | ✅ MZ | 41,381,486 B |
| `PhoenixMasterToolSetup.exe` | ✅ MZ | 33,828,432 B |
| `ProjectTrackingToolSetup.exe` | ✅ MZ | 39,108,336 B |

**Frozen-exe launch smoke (from the published updater zip):** the CAD updater zip was extracted from the *downloaded* `LabLayoutTool.zip` and `LabLayoutTool.exe` launched offscreen — exited cleanly (exit 0), proving the published full-folder payload boots. The other 3 exes were already launch-validated at RC time (byte-identical artifacts confirmed by sha256 in § 2).

**Full GUI install + interactive launch — operator-completed at RC validation** (CAD 2026-05-30, Checkout 2026-05-30, VM 2026-05-30, JT 2026-05-31). Since the published assets are byte-identical to the RC-validated artifacts (§ 2), no new interactive install smoke is required. Operator may optionally re-install from the published installer URLs to confirm the GitHub-download → install path on a clean machine.

---

## 5. Update-check results

The commons `phoenix_commons.updater.check_for_update(owner, repo, current_version, zip_asset_name)` was run against the **live GitHub Releases API** for each tool, simulating a prior-version client's update check:

| Simulated client | Discovered latest | Expected | Version match | Correct asset in download URL |
|-------------------|-------------------|----------|----------------|--------------------------------|
| CAD v0.1.1 → | `0.1.2` | `0.1.2` | ✅ | ✅ `LabLayoutTool.zip` |
| Checkout v1.7.0 → | `1.7.1` | `1.7.1` | ✅ | ✅ `PhoenixCheckoutTool.zip` |
| ValveMaster v1.1.0 → | `1.1.1` | `1.1.1` | ✅ | ✅ `PhoenixMasterTool.zip` |
| Job Tracker v1.8.5 → | `1.8.6` | `1.8.6` | ✅ | ✅ `ProjectTrackingTool.zip` |

**All 4 update-check discovery paths pass end-to-end against the live published releases.** A prior-version client running its in-app updater will:
1. Hit the GitHub Releases API ✅
2. Discover the new version ✅
3. Resolve the correct zip asset download URL ✅

This is stronger than the brief's "API/asset-name verified only" fallback — the actual commons `check_for_update` code path executed against live releases and returned correct `UpdateInfo` for all 4. The only step not exercised headlessly is the final `download_and_apply` self-replace + relaunch (requires a real frozen-exe client install + restart; the download + validate portion is covered by §§ 2-3 byte-equality + layout checks).

---

## 6. Any issues

**None blocking.** Two cosmetic notes:

1. **`gh release view --json isLatest` rejected** — the installed `gh` 2.88.1 doesn't expose an `isLatest` JSON field. Worked around by querying the REST `repos/<owner>/<repo>/releases/latest` endpoint directly, which confirmed each published tag is the repo's latest release. No impact.

2. **`distutils-precedence.pth` warning** from the host's system-Python 3.14 site-packages printed to stderr during a couple of zip-inspection one-liners. Harmless environment noise (a `_distutils_hack` shim incompatibility); the actual script output was correct in every case. Did not affect the venv-based update-check run (which used the 3.12 `.venv312`).

Neither is a release-health issue.

---

## 7. Final release health verdict

### **A — Post-release smoke passed.**

Every gate green:

- ✅ All 4 releases public, non-draft, non-prerelease, marked latest
- ✅ All 8 assets present, no FullInstall zips, filenames exact
- ✅ All 8 assets byte-identical (sha256) to RC-validated local artifacts
- ✅ All 4 updater zip layouts match contract (CAD/JT full-folder, Checkout/VM exe-only)
- ✅ All 4 installers are valid PE executables
- ✅ Published CAD frozen exe boots clean from the downloaded zip
- ✅ All 4 update-check discovery paths resolve correct version + correct asset against the live GitHub API

The Phoenix family of 4 production tools is live, usable, and auto-update-discoverable.

---

## 8. Recommended optional follow-ups (non-blocking)

1. **Real-client `download_and_apply` round-trip** — on a prior-version installed client, click the in-app "Install & Restart" and confirm the self-replace + relaunch completes. This is the one path not headlessly exercisable; covered indirectly by the Phase 6C-B fake-release round-trip during platform development, but a live confirmation per tool would close the loop.
2. **24-h S1 reputation watch** — published exes can attract AV reputation lag; monitor for first 24 h.
3. **`.gitignore` venv gap** — still deferred (per `PHOENIX_4_APP_SOURCE_BLOAT_AUDIT.md` § 5).

---

## 9. Confirmation

- **No source changed.** No edits to any of the 4 production repos' source trees (verified: `git status --porcelain` clean except a pre-existing untracked operator `.docx` in Checkout, unrelated to this smoke).
- **No tags changed.** RC + stable tags untouched.
- **No assets uploaded.** This smoke only *downloaded* assets; nothing was pushed to any release.
- **No releases modified.** No release notes edited, no draft/publish state changed, no asset add/remove. All 4 remain exactly as published.
- **Download scratch cleaned.** The temporary `~/.tmp/rel-dl/` download directory was removed after verification.

---

*Post-release smoke complete. Verdict A — all 4 Phoenix production releases are healthy, usable, and updater-discoverable.*
