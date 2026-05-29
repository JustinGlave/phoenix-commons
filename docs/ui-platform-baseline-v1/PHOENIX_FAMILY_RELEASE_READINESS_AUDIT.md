# Phoenix Family — Release Readiness Audit

> **Status:** read-only post-Wave-8b audit. No source modified.
> **Date:** 2026-05-29.
> **Scope:** 4 deployed production tools + PCC + Screenshot_Tool.

---

## 1. App-by-app release readiness table

| App | Repo / branch / HEAD | Version | Last release tag | Retrofit merge | build.bat hardened | AppId | Release-ready? |
|-----|----------------------|---------|------------------|----------------|---------------------|-------|----------------|
| **Lab Layout Tool** (Phoenix CAD) | `Phoenix_CAD_Tool` / `master` / `fb383af` | `0.1.1` | `v0.1.1` (2026-05-12, **before** retrofit) | ✅ Phase 3A `79c7003` (2026-05-19) | **PARTIAL** — `--collect-all=phoenix_commons` ✅, `--noupx` ❌, stdlib excludes ❌, 3.12 soft-warn ❌ | not declared (AppName-hashed default) | ❌ NO — needs build-hardening pass before RC |
| **Phoenix Checkout Tool** | `Phoenix-Checkout-Tool` / `main` / `700f565` | `1.7.0` | `v1.7.0` (2026-05-04, **before** retrofit) | ✅ Phase 3B `26a4689` (2026-05-19) | **PARTIAL** — `--collect-all=phoenix_commons` ✅, `--noupx` ❌, stdlib excludes ❌, 3.12 soft-warn ❌ | not declared (AppName-hashed default) | ❌ NO — needs build-hardening pass before RC |
| **ValveMaster / Phoenix Master Tool** | `ValveMasterTool` / `main` / `631dbe8` | `1.1.0` | `v1.1.0` (2026-05-10) · forensic `valvemaster-retrofit-v1.1.0-pre` (2026-05-26) | ✅ Wave 8a `631dbe8` (2026-05-26) | **FULL** — `--noupx` ✅, stdlib excludes (8) ✅, 3.12 soft-warn ✅, `--collect-all=phoenix_commons` ✅ | `{A7F3C2D1-9B4E-4F6A-8C3D-1E5B7A9F2C4D}` declared | ✅ **YES** — operator B10 visual + S1 passed |
| **Project Tracking Tool** (Job Tracker) | `Job Tracker` / `main` / `6a0d60b` | `1.8.5` | `v1.8.5` (2026-05-12) · forensic `job-tracker-retrofit-v1.8.5-pre` (2026-05-28) | ✅ Wave 8b `6a0d60b` (2026-05-28) | **FULL** — `--noupx` ✅, stdlib excludes (8) ✅, 3.12 soft-warn ✅, `--collect-all=phoenix_commons` ✅ | NOT declared (Decision #8 hard rule preserved) | ✅ **YES** — operator B10 visual + S1 passed |
| **Phoenix Command Center** (PCC) | `phoenix-command-center` / `main` / `3a13eed` | no `version.py` | `pcc-phase-3g-merged-v2.4.0` (forensic) | ✅ Phases 3A/B/C/D/E/F/G all merged | **FULL** (and then some — 3.12 soft-warn ✅, --noupx ✅, 9 stdlib excludes, `--collect-all=phoenix_commons` ✅) | `{B6E4A1F2-3D5C-4B7A-9E1F-8C2D5A7B9E4F}` declared | ⚠️ **operator discretion** — per CLAUDE.md "source-run hub, not itself one of the four shipping production tools" but installer.iss + AppId + hardened build.bat are ready if operator decides to ship |
| **Screenshot_Tool** | `Screenshot_Tool` / `main` / `ee266d5` | `1.4.0` | `v1.4.0` (2026-05-04) | ❌ **not retrofit** (no commons submodule) | **NONE** — 0/4 hardening flags present | not declared (AppName-hashed default) | ⚠️ **operator decision needed** (see §5) |

### Detail per ready-now tool

**ValveMaster / Phoenix Master Tool — release-ready**
- Updater zip contract: exe-only payload (ADR-003)
- Frozen-build validation: Wave 8a B8/B8a operator visual passed + 5-min S1 idle clean
- Installer round-trip: included in Wave 8a B8
- Recommended next: produce `v1.1.1` RC from `main` HEAD `631dbe8` (or RC-tag the existing `valvemaster-retrofit-v1.1.0-pre` if the operator considers the retrofit a release-worthy change; otherwise the next functional change triggers a real `v1.1.1` bump)

**Job Tracker / Project Tracking Tool — release-ready**
- Updater zip contract: full-folder payload (`expected_internal=True`, ADR-003)
- Frozen-build validation: Wave 8b B10 operator visual passed + 5-min S1 idle clean + 57-record Excel load functionally proven
- Installer round-trip: included in Wave 8b B10
- Recommended next: produce `v1.8.6` RC from `main` HEAD `6a0d60b` (or RC-tag the existing forensic tag; same logic as ValveMaster)

---

## 2. Blockers

| Blocker | Apps affected | Severity | Remediation |
|---------|---------------|----------|-------------|
| `build.bat` missing FROZEN_BUILD_BASELINE hardening flags | Phoenix CAD + Phoenix Checkout | **MEDIUM** — frozen exes built from these `build.bat` lack `--noupx` + stdlib excludes + 3.12 soft-warn; S1-safe profile not verified for this build shape. Their Phase 3A/3B retrofits predated the FROZEN_BUILD_BASELINE doctrine's codification. | Small "Wave 8c/8d-style maintenance retrofit" applying just the 11-line build.bat hardening diff from Wave 8a/Wave 8b precedent. Source untouched; build-script-only change. Estimated ≤ 1 working session per tool. |
| Screenshot_Tool not in retrofit roadmap | Screenshot_Tool | **UNCLEAR** — depends on operator's production-vs-internal classification | See §5 — operator decision needed |
| PCC packaging status unclear | PCC | **LOW** — CLAUDE.md says "source-run only" but the repo has full packaging infrastructure (installer.iss + AppId + hardened build.bat). | Operator decision: ship PCC as a 5th packaged tool, or formally archive the packaging infrastructure as "ready if needed". |
| AppId absence in 4 tools (CAD, Checkout, Job Tracker, Screenshot_Tool) | 4 tools | **NOT a blocker** — intentional preservation per Decision #8 (Job Tracker) and per existing-user-base upgrade detection for the other three. Adding AppId now would break upgrades. |

---

## 3. Recommended release order

Sequential, each tool gates the next based on operator validation:

1. **ValveMaster / Phoenix Master Tool first** — most-recently validated (Wave 8a B8a 2026-05-26 + operator visual pass + 5-min S1 idle clean). Simplest payload (exe-only). Lowest release risk. RC tag suggestion: `v1.1.1-rc1` from current `main`.
2. **Job Tracker / Project Tracking Tool second** — also recently validated (Wave 8b B10 2026-05-28). Larger payload (full-folder) but commons facade ensures contract preserved. RC tag suggestion: `v1.8.6-rc1` from current `main`.
3. **Phoenix CAD / Lab Layout Tool third** — *after* a small build.bat hardening pass. The Phase 3A retrofit is solid; the build script just predates the canonical hardening recipe.
4. **Phoenix Checkout Tool fourth** — same logic as Phoenix CAD; small build-hardening pass needed.
5. **PCC** — operator decision (defer or ship).
6. **Screenshot_Tool** — operator decision (defer, retrofit, or deprecate).

---

## 4. Apps that should NOT release yet

- **Phoenix CAD / Lab Layout Tool** — release blocked pending build.bat hardening.
- **Phoenix Checkout Tool** — release blocked pending build.bat hardening.
- **Screenshot_Tool** — release blocked pending operator classification (see §5).

ValveMaster + Job Tracker + (optionally) PCC are unblocked.

---

## 5. Screenshot_Tool recommendation

**Operator decision required.**

Findings:
- Active production tool: regular versioned releases (v1.2.1 → v1.3.0 → v1.4.0 with weekly cadence)
- Origin: public `JustinGlave/Screenshot_Tool` on GitHub
- Installer.iss: declares `MyAppPublisher="ATS Inc."`, install path `{localappdata}\ATS Inc\Screenshot Tool`, `OutputBaseFilename=ScreenshotToolSetup` — same conventions as the 4 retrofitted tools
- README: positions it as a Snipping-Tool replacement with screenshot annotation features
- AppId: not declared (existing-user-base upgrade detection same as 3 of the 4 production tools)
- **NOT in MIGRATION_RULES `§ Migration order`** — never scheduled for retrofit
- Build.bat: not hardened (0/4 FROZEN_BUILD_BASELINE flags present)
- No CLAUDE.md, no CHANGELOG.md, no commons submodule
- The original `APP_STANDARDIZATION_READINESS_MATRIX.md` line 117 says *"Not scheduled. If operator wants it modernized, classify it as Wave 8c+ AFTER Wave 8a + 8b close"* — those waves are now closed.

Three operator paths:

| Path | Effort | Outcome |
|------|--------|---------|
| **A. Defer** — accept as-is, no changes | 0 | Keeps shipping under its existing pattern; no commons retrofit; no hardened build.bat |
| **B. Audit + retrofit (Wave 8c)** — apply the canonical Phoenix retrofit pattern (commons submodule + theme/widget facades + build hardening + AppId-absence preservation) | 1-2 sessions (similar scope to Wave 8a) | Brings Screenshot_Tool into the family standard; enables shared icon updates + theme consistency |
| **C. Hardening-only pass** — leave commons alone, just apply the FROZEN_BUILD_BASELINE flags to build.bat | < 1 session | S1-safe builds without commons consumption; tool stays standalone |

**Recommendation:** path **B** (Wave 8c) — Screenshot_Tool has the same shape as the other 4 production tools and meets the deployment criteria for inclusion in the family. The retrofit pattern is now proven across 4 tools. But this is an operator policy decision (whether Phoenix family includes 4 tools or 5).

---

## 6. Asset-naming cleanup recommendation

Per `ASSET_NAMING_PROPOSAL.md`, legacy prefixes remain in the family:

| Tool | Legacy asset prefix | Proposal status |
|------|---------------------|------------------|
| Phoenix CAD | `Normal_red.ico`, `Transparent_red.png` | proposal authored, not yet executed |
| Phoenix Checkout | `Normal_red.ico`, `Transparent_red.png` | proposal authored, not yet executed |
| ValveMaster | `Normal_red.ico`, `Transparent_red.png` (also referenced in `assets.py` base64) | proposal authored, not yet executed |
| Job Tracker | `PTT_Normal.ico`, `PTT_Transparent.png` | proposal authored, not yet executed |
| PCC | `PCC_*.ico` | proposal authored, not yet executed |

**Recommendation: defer.** Asset renames touch build.bat `--add-data` lines + installer.iss `SetupIconFile` + every `_resource_path()`/`resource_path()` call site referencing them. The diff is mechanical but **broad-surface-touch** — not the right pass to ship before release-candidate builds. Better as a follow-up "Operational Hardening Sprint 02" after the first release wave clears.

---

## 7. Doc cleanup — minor forward-looking residue

Mild stale-language residue exists in 2 active doc sites:

| File | Line | Status |
|------|------|--------|
| `APP_STANDARDIZATION_READINESS_MATRIX.md` | 117 | *"Not scheduled. If operator wants it modernized, classify it as Wave 8c+ AFTER Wave 8a + 8b close"* — the condition is now satisfied; Wave 8a and 8b ARE closed. Minor reword. |
| `APP_STANDARDIZATION_READINESS_MATRIX.md` | 168 | *"Wave 8a first because it's already doctrinally scheduled..."* — historical (state-at-time-of-authoring). Acceptable as forensic record. |

Plus: a few `BLOCKERS.md` / `OPERATIONAL_STABILIZATION_REPORT_01.md` references to "Phase 8b retrofit planned" may still be forward-looking. The `PHASE_8B_JOB_TRACKER_REPORT.md § 12` already flagged these as optional cleanup.

These are documentation-only nits; not release-blocking.

---

## 8. Next actionable deliverable step

**Suggested:** produce **ValveMaster `v1.1.1` release-candidate build** from `main` HEAD `631dbe8` using the existing hardened `build.bat`. This is the smallest possible production validation — single tool, fully validated, all invariants confirmed.

If that smoke succeeds (5-min S1 clean + installer round-trip + visible upgrade from v1.1.0 to v1.1.1 on a real machine), produce **Job Tracker `v1.8.6` release-candidate build** next.

After both ship and bake clean, return to Phoenix CAD + Phoenix Checkout for the small build-hardening pass.

---

## Verdict

### **B — Ready after small doc cleanup.**

Two tools (ValveMaster + Job Tracker) are immediately release-ready with no remaining blockers. Two tools (Phoenix CAD + Phoenix Checkout) need a small build-hardening pass before their next release. Screenshot_Tool needs operator classification. PCC is operator-discretion.

Doc cleanup is minor (1-2 lines in the readiness matrix) — strictly speaking, it doesn't block ValveMaster or Job Tracker from going to RC; but verdict B reflects that the doc system has 2 small forward-looking residues that would be neat to clean up before publishing RC notes.

If operator wants verdict A immediately: cleanup is trivial and unblocks release-candidate builds for ValveMaster + Job Tracker.

---

## Confirmation

- **No app source edits.**
- **No version.py changes.**
- **No builds executed.**
- **No GitHub Releases drafted or published.**
- **No installer uploads.**
- **No Screenshot_Tool retrofit performed.**
- **No commons API changes.**
- This is an audit-only deliverable. The next operator-approved step decides which tool produces the first release-candidate.
