# Phoenix Family — 4-App Release Closure Report

> **Status:** ✅ **RELEASE CYCLE CLOSED.** All 4 production tools published, smoke-verified, updater-discoverable.
> **Date:** 2026-06-01.
> **Canonical record** for the coordinated 4-app release. Supersedes the forward-looking state in `PHOENIX_4_APP_FINAL_RELEASE_PROMOTION_PLAN.md`, `PHOENIX_4_APP_RC_VALIDATION_SUMMARY.md`, and `PHOENIX_4_APP_RC_KICKOFF_READY.md`.

---

## 1. Final published versions

| App | Display name | Version | Repo |
|-----|--------------|---------|------|
| Phoenix CAD | Lab Layout Tool | **v0.1.2** | `JustinGlave/lab-layout-tool` |
| Phoenix Checkout | Phoenix Checkout Tool | **v1.7.1** | `JustinGlave/Phoenix-Checkout-Tool` |
| ValveMaster | Phoenix Master Tool | **v1.1.1** | `JustinGlave/phoenix-master-tool` |
| Job Tracker | Project Tracking Tool | **v1.8.6** | `JustinGlave/project-tracking-tool` |

All 4 published 2026-06-01 in a 27-second sequential window (21:14:36 → 21:15:03 UTC), CAD → Checkout → ValveMaster → Job Tracker per Decision #4.

---

## 2. Release URLs

| App | Live release |
|-----|--------------|
| Phoenix CAD | https://github.com/JustinGlave/lab-layout-tool/releases/tag/v0.1.2 |
| Phoenix Checkout | https://github.com/JustinGlave/Phoenix-Checkout-Tool/releases/tag/v1.7.1 |
| ValveMaster / PMT | https://github.com/JustinGlave/phoenix-master-tool/releases/tag/v1.1.1 |
| Job Tracker / PTT | https://github.com/JustinGlave/project-tracking-tool/releases/tag/v1.8.6 |

All `--latest` for their repos; `/releases/latest` REST endpoint resolves to each stable tag.

---

## 3. Asset list

Each release carries exactly 2 assets (installer + updater zip). No `*_FullInstall.zip` uploaded.

| App | Installer | Updater zip |
|-----|-----------|--------------|
| Phoenix CAD | `LabLayoutToolSetup.exe` (36.3 MB) | `LabLayoutTool.zip` (55.6 MB) |
| Phoenix Checkout | `PhoenixCheckoutToolSetup.exe` (39.5 MB) | `PhoenixCheckoutTool.zip` (4.4 MB) |
| ValveMaster | `PhoenixMasterToolSetup.exe` (32.3 MB) | `PhoenixMasterTool.zip` (1.9 MB) |
| Job Tracker | `ProjectTrackingToolSetup.exe` (37.3 MB) | `ProjectTrackingTool.zip` (54.8 MB) |

Published assets are byte-identical (sha256) to the operator-validated RC artifacts.

---

## 4. Updater contract summary

| App | Asset name | Contract | Layout | `expected_internal` |
|-----|------------|----------|--------|----------------------|
| Phoenix CAD | `LabLayoutTool.zip` | full-folder | 305 entries (exe + `_internal/*`) | `True` |
| Phoenix Checkout | `PhoenixCheckoutTool.zip` | exe-only | 1 entry (`['PhoenixCheckoutTool.exe']`) | `False` |
| ValveMaster | `PhoenixMasterTool.zip` | exe-only (ADR-003) | 1 entry (`['PhoenixMasterTool.exe']`) | `False` |
| Job Tracker | `ProjectTrackingTool.zip` | full-folder | 260 entries (exe + `_internal/*`) | `True` |

All 4 contracts preserved across retrofit → hardening → RC → publish. No drift.

---

## 5. Post-release smoke result

Per `PHOENIX_4_APP_POST_RELEASE_SMOKE_REPORT.md` (verdict A):

- ✅ All 4 releases public, non-draft, non-prerelease, latest
- ✅ All 8 assets downloaded fresh + sha256 byte-identical to local validated artifacts
- ✅ All 4 updater zip layouts match contract
- ✅ All 4 installers valid PE executables
- ✅ Published CAD frozen exe boots clean from the downloaded zip
- ✅ **Update-check discovery passed for all 4** — commons `check_for_update` against live GitHub API resolved correct version + correct asset for each tool (CAD 0.1.1→0.1.2, Checkout 1.7.0→1.7.1, VM 1.1.0→1.1.1, JT 1.8.5→1.8.6)

---

## 6. Source-bloat result

Per `PHOENIX_4_APP_SOURCE_BLOAT_AUDIT.md`:

- ✅ No `dist/`, `build/`, `_internal/`, `.venv*/`, `site-packages/`, `*.pyc`, `__pycache__` tracked in any of the 4 repos
- ✅ Total tracked source ~33k `.py` LOC / ~64k total tracked LOC across all 4
- ✅ The "~1M LOC" perception was untracked venv content + bundled frozen-exe output — not source-of-truth bloat
- ⚠ `.gitignore` venv-suffix gap → **resolved** in post-release housekeeping (`PHOENIX_POST_RELEASE_HOUSEKEEPING_REPORT.md`)

---

## 7. Tag inventory

| App | Forensic retrofit tag | RC tag (immutable) | Stable release tag |
|-----|------------------------|---------------------|---------------------|
| Phoenix CAD | (Phase 3A merge, no `-pre` tag) | `v0.1.2-rc1` @ `35a0661` | `v0.1.2` @ `35a0661` |
| Phoenix Checkout | (Phase 3B merge, no `-pre` tag) | `v1.7.1-rc1` @ `274b0a8` | `v1.7.1` @ `274b0a8` |
| ValveMaster | `valvemaster-retrofit-v1.1.0-pre` | `v1.1.1-rc1` @ `e6eefa1` | `v1.1.1` @ `e6eefa1` |
| Job Tracker | `job-tracker-retrofit-v1.8.5-pre` | `v1.8.6-rc1` @ `689e8ee` | `v1.8.6` @ `689e8ee` |

RC + retrofit tags remain immutable. Stable tags are separate annotations at the same SHAs (Decision #2).

---

## 8. Final verdict

### **✅ RELEASE CYCLE CLOSED — Phoenix UI Platform Baseline v1 fully shipped.**

The 4 deployed Phoenix production tools are live on GitHub Releases, on a unified commons-backed platform with S1-safe hardened builds and validated updater contracts. End users can install via the public installer URLs; existing-version users receive the upgrade through the in-app auto-updater (discovery path verified live).

### Rollout arc timeline

| Milestone | Date |
|-----------|------|
| Phase 0 — baseline generation | 2026-05-13 |
| Phases 1–2 — commons API + tests + ADRs | 2026-05-14..16 |
| Phases 3A–3G — PCC + pilot retrofits (CAD, Checkout) | 2026-05-18..26 |
| Wave 8a — ValveMaster retrofit | 2026-05-26 |
| Wave 8b — Job Tracker retrofit | 2026-05-28 |
| CAD + Checkout release-hardening | 2026-05-29 |
| 4-app RC sequence | 2026-05-30..31 |
| 4-app stable release publication | 2026-06-01 |
| Post-release smoke + closure | 2026-06-01 |

---

## 9. Remaining optional follow-ups (not part of this release cycle)

1. Real-client `download_and_apply` round-trip per tool (operator clicks "Install & Restart" from a prior install)
2. 24-h S1 reputation watch on published exes
3. Wave 8c — Screenshot_Tool retrofit (operator-gated decision)
4. PCC packaging decision (currently source-run only)
5. Asset-naming cleanup (`ASSET_NAMING_PROPOSAL.md` — retire legacy prefixes)

---

## 10. Confirmation

- **No app source logic changed** during closure.
- **No rebuild.** Published assets are the RC-validated artifacts.
- **No tags moved.** RC + stable + retrofit tags all intact.
- **No assets uploaded.** No releases edited.
- **No new feature work started.**

---

*Phoenix 4-app coordinated release closed 2026-06-01. Platform baseline v1 rollout complete.*
