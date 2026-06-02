# Phoenix Family — 4-App Final Publish Report

> **Status:** ✅ **ALL 4 RELEASES PUBLISHED.** 4-app coordinated release sequence complete.
> **Date:** 2026-06-01.
> **Companions:** `PHOENIX_4_APP_FINAL_PUBLISH_GATE_REPORT.md`, `PHOENIX_4_APP_FINAL_RELEASE_DRAFTS_REPORT.md`.

---

## 1. Publish timestamp per app

| App | Published at (UTC) | Elapsed window |
|-----|---------------------|----------------|
| Phoenix CAD / Lab Layout Tool v0.1.2 | `2026-06-01T21:14:36Z` | t = 0 |
| Phoenix Checkout Tool v1.7.1 | `2026-06-01T21:14:45Z` | t + 9 s |
| Phoenix Master Tool v1.1.1 | `2026-06-01T21:14:54Z` | t + 18 s |
| Project Tracking Tool v1.8.6 | `2026-06-01T21:15:03Z` | t + 27 s |

Sequential publish per Decision #4 build order. Total wall-clock to publish all 4: 27 seconds.

---

## 2. Release URL per app

All 4 URLs are now publicly visible and live in their repos' "Releases" pages:

| App | Live release URL |
|-----|-------------------|
| Phoenix CAD | https://github.com/JustinGlave/lab-layout-tool/releases/tag/v0.1.2 |
| Phoenix Checkout | https://github.com/JustinGlave/Phoenix-Checkout-Tool/releases/tag/v1.7.1 |
| ValveMaster / PMT | https://github.com/JustinGlave/phoenix-master-tool/releases/tag/v1.1.1 |
| Job Tracker / PTT | https://github.com/JustinGlave/project-tracking-tool/releases/tag/v1.8.6 |

The temporary `untagged-XXX` draft URLs from `PHOENIX_4_APP_FINAL_RELEASE_DRAFTS_REPORT.md` § 3 have been replaced with the canonical `/releases/tag/v<X.Y.Z>` URLs above. The draft URLs no longer resolve.

---

## 3. Published status verification

Post-publish `gh release view` for each:

| App | `isDraft` | `isPrerelease` | `publishedAt` | Asset count |
|-----|-----------|-----------------|----------------|--------------|
| Phoenix CAD | ✅ false | ✅ false | ✅ non-null | ✅ 2 |
| Phoenix Checkout | ✅ false | ✅ false | ✅ non-null | ✅ 2 |
| ValveMaster | ✅ false | ✅ false | ✅ non-null | ✅ 2 |
| Job Tracker | ✅ false | ✅ false | ✅ non-null | ✅ 2 |

All 4 marked `--latest` for their respective repos (shows in repo header + default for `gh release download`).

---

## 4. Final asset list per app

Each release carries exactly 2 assets — installer + updater zip. **No `*_FullInstall.zip` uploaded.**

| App | Installer | Updater zip |
|-----|-----------|--------------|
| Phoenix CAD | `LabLayoutToolSetup.exe` (38,016,778 B / 36.3 MB) | `LabLayoutTool.zip` (58,264,923 B / 55.6 MB) |
| Phoenix Checkout | `PhoenixCheckoutToolSetup.exe` (41,381,486 B / 39.5 MB) | `PhoenixCheckoutTool.zip` (4,593,289 B / 4.4 MB) |
| ValveMaster | `PhoenixMasterToolSetup.exe` (33,828,432 B / 32.3 MB) | `PhoenixMasterTool.zip` (2,044,232 B / 1.9 MB) |
| Job Tracker | `ProjectTrackingToolSetup.exe` (39,108,336 B / 37.3 MB) | `ProjectTrackingTool.zip` (57,508,860 B / 54.8 MB) |

Asset sizes byte-equal pre-publish vs post-publish. No re-upload occurred during publication (`gh release edit --draft=false` flips visibility only).

---

## 5. Updater asset-name confirmation

Each repo's `updater.py` looks for a specific zip filename via its `ZIP_ASSET_NAME` constant. Byte-exact match verification:

| App | Expected (in `updater.py`) | Published asset | Match |
|-----|-----------------------------|------------------|-------|
| Phoenix CAD | `LabLayoutTool.zip` | `LabLayoutTool.zip` | ✅ |
| Phoenix Checkout | `PhoenixCheckoutTool.zip` | `PhoenixCheckoutTool.zip` | ✅ |
| ValveMaster | `PhoenixMasterTool.zip` | `PhoenixMasterTool.zip` | ✅ |
| Job Tracker | `ProjectTrackingTool.zip` | `ProjectTrackingTool.zip` | ✅ |

Auto-update path is now live end-to-end for all 4 tools. Existing v<previous> installations can detect + download these releases via their in-app updaters.

---

## 6. Any issues encountered

**None.** Each `gh release edit --draft=false --latest` command returned the canonical release URL with no error. Each post-publish verification confirmed `isDraft: false`, non-null `publishedAt`, both assets intact.

No retry needed. No re-upload needed. No tag-mismatch correction needed. No revert needed.

---

## 7. Final family release verdict

### **✅ ALL 4 RELEASES PUBLISHED AND LIVE.**

The Phoenix family of 4 production tools is now coordinated-released on the commons-backed retrofit + hardened-build baseline:

| App | Repo | Stable tag | Live since |
|-----|------|------------|-------------|
| **Lab Layout Tool** | `JustinGlave/lab-layout-tool` | `v0.1.2` | 2026-06-01 21:14:36 UTC |
| **Phoenix Checkout Tool** | `JustinGlave/Phoenix-Checkout-Tool` | `v1.7.1` | 2026-06-01 21:14:45 UTC |
| **Phoenix Master Tool** | `JustinGlave/phoenix-master-tool` | `v1.1.1` | 2026-06-01 21:14:54 UTC |
| **Project Tracking Tool** | `JustinGlave/project-tracking-tool` | `v1.8.6` | 2026-06-01 21:15:03 UTC |

This closes the Phoenix UI Platform Baseline v1 rollout arc that began with Phase 0 baseline-generation 2026-05-13.

### Headline

- 4 deployed production tools commons-backed end-to-end
- Build pipeline S1-safe per `FROZEN_BUILD_BASELINE` (Python 3.12 + `--noupx` + stdlib excludes + commons preflight)
- All updater contracts intact (CAD/JT full-folder, Checkout/VM exe-only)
- Zero AppId drift; zero install-path drift; zero user-data-path drift
- All `-rc1` tags remain immutable forensic markers; final stable tags are separate annotations at the same SHAs

---

## 8. Recommended immediate post-release checks

These are operator-discretion follow-ups to confirm the in-app auto-updater path actually works on a real client install.

### Critical (within 24 hours)

1. **Auto-updater smoke per tool** — on each of 4 prior-version installed clients:
   - Phoenix CAD v0.1.1 installed → in-app updater detects v0.1.2 → click "Install & Restart" → confirm v0.1.2 boots
   - Phoenix Checkout v1.7.0 installed → updater detects v1.7.1 → confirm v1.7.1 boots
   - Phoenix Master Tool v1.1.0 installed → updater detects v1.1.1 → confirm v1.1.1 boots
   - Project Tracking Tool v1.8.5 installed → updater detects v1.8.6 → confirm v1.8.6 boots

   Why critical: this is the first time the commons-backed `download_and_apply` runs against a real GitHub Release for each contract type (full-folder + exe-only). If a contract surprise lurks, it surfaces here.

2. **S1 / Crowdstrike post-publish observation** — even though build-time + install-time + 5-min-idle S1 already passed at RC validation, post-publish AV reputation can lag. Watch each installed app for first 24 h after publish; if S1 flags any of the 4 exes, surface immediately for investigation.

3. **End-user smoke (Justin's primary workstation)** — install/upgrade each release on the operator's main workstation; spot-check the surfaces most likely to expose regression:
   - CAD: layout canvas + parts catalog
   - Checkout: xlsx template load + export
   - VM: Decoded Fields validation flow
   - JT: financials dashboard + xlsb load

### Optional (this week)

4. **Add `.venv*/` to 3 missing `.gitignore` files** (per `PHOENIX_4_APP_SOURCE_BLOAT_AUDIT.md` § 5) — Phoenix-Checkout-Tool, ValveMasterTool, Job Tracker. Plus extend Phoenix_CAD_Tool's `.venv/` → `.venv*/`. One-line change per repo. Closes the careless-`git add -A` tripwire.

5. **Optional `*_FullInstall.zip` upload** — if any user reports installer issues + needs the manual-unzip-into-folder workaround, upload the `_FullInstall.zip` to that release via `gh release upload <tag> dist/<App>_FullInstall.zip --repo <owner/repo>`.

6. **Local working-tree cleanup** — delete `.venv314-bak/` (CAD, Checkout) and `.venv312/` (VM, JT) from each repo's working dir. Frees ~3 GB across the 4 repos. Operator's call when convenient.

### Later

7. **Wave 8c — Screenshot_Tool retrofit** (per `PHOENIX_FAMILY_RELEASE_READINESS_AUDIT.md` § 5) — operator-gated decision on whether Screenshot_Tool joins the commons family.

8. **PCC packaging decision** — currently source-run only; packaging infrastructure exists if/when operator wants it shipped as a 5th tool.

9. **Asset-naming cleanup** (per `ASSET_NAMING_PROPOSAL.md`) — retire legacy `PTT_` / `Normal_red.ico` / `Transparent_red.png` prefixes. Out of scope for the release arc; future operational hardening sprint.

---

## 9. Confirmation

- **No source changed** in any of the 4 repos during publication.
- **No `version.py` changed.** Final stable versions (`0.1.2` / `1.7.1` / `1.1.1` / `1.8.6`) match the committed values from the RC commits — `gh release edit --draft=false` does not modify source.
- **No tags changed.** RC `-rc1` tags remain immutable. Final stable tags created earlier and not modified during publication.
- **No rebuild occurred.** The 8 assets uploaded yesterday are the same 8 assets now attached to the published releases (byte-equal sizes verified pre- and post-publish).
- **No extra assets uploaded.** No `*_FullInstall.zip` attached. No additional artifacts.
- **No source-bloat introduced** — no tracked changes to any repo's source tree triggered by publication.
- **`.gitignore` venv gap remains deferred** — not touched during publication per operator direction.

---

## Wrap-up

The Phoenix family — 4 deployed production tools — is now on a unified commons-backed platform baseline with hardened S1-safe builds, validated updater contracts, and live GitHub Releases. End users can install via the public installer URLs above, and existing-version users will receive the upgrade through the in-app auto-updater.

This concludes the Phoenix UI Platform Baseline v1 rollout arc:
- Phase 0 (baseline-generation) 2026-05-13
- Phases 1–2 (commons API + tests + ADRs) 2026-05-14..2026-05-16
- Phase 3A–3G (PCC modernization) 2026-05-18..2026-05-26
- Wave 8a (ValveMaster retrofit) 2026-05-26
- Wave 8b (Job Tracker retrofit) 2026-05-28
- CAD + Checkout release-hardening 2026-05-29
- 4-app RC sequence 2026-05-30..2026-05-31
- 4-app stable release publication 2026-06-01

**Next operator decision: post-release auto-updater smoke (item #1) or move on to Wave 8c / PCC packaging / asset naming.**
