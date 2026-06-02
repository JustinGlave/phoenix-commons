# Phoenix Family — 4-App Live Updater Verification + Support Watch

> **Status:** updater discovery verified both directions; no older install available for a live upgrade-apply; entering monitor-only support watch.
> **Date:** 2026-06-01.
> **Companions:** `PHOENIX_4_APP_RELEASE_CLOSURE_REPORT.md`, `PHOENIX_4_APP_POST_RELEASE_SMOKE_REPORT.md`.

---

## 1. Older installs found / not found

Enumerated `%LOCALAPPDATA%\ATS Inc\` for installed production apps + their versions:

| App | Install dir | Installed exe | Installed version | Published | Older install available to upgrade FROM? |
|-----|-------------|----------------|--------------------|-----------|--------------------------------------------|
| Lab Layout Tool | `Lab Layout Tool` | `LabLayoutTool.exe` (2,303,741 B) | **v0.1.2** (exe byte-size + mtime match the v0.1.2 RC build) | v0.1.2 | ❌ no — already current |
| Phoenix Checkout Tool | `Phoenix Valve Checkout Tool` | `PhoenixCheckoutTool.exe` | **v1.7.1** (exe mtime 2026-05-30 22:36 = Checkout RC build) | v1.7.1 | ❌ no — already current |
| Phoenix Master Tool | `ValveMasterTool` | `PhoenixMasterTool.exe` | **v1.1.1** (bundled `version.py` = `1.1.1`) | v1.1.1 | ❌ no — already current |
| Project Tracking Tool | `Project Tracking Tool` | `ProjectTrackingTool.exe` (3,307,436 B) | **v1.8.6** (exe mtime 2026-05-31 00:47 = JT RC build) | v1.8.6 | ❌ no — already current |

**Finding:** all 4 installed apps are already at the published stable versions. During the RC interactive-validation step (2026-05-30 / 31), the operator installed each app from the RC installer — and the RC was built off the version-bump commit, so its version equals the final stable version (same SHA). Those installs overwrote any prior-version installs.

**Therefore: no older install exists locally to exercise the live `download_and_apply` upgrade path against.**

Per the brief's Step 1 fallback: **"live updater upgrade-apply path not available locally; the installed versions already match the published stable versions; API/asset contract already verified."**

(Also present in `ATS Inc\`: `Screenshot Tool` v1.4.0 — not part of this release cycle — plus throwaway `PhoenixScaffold*` / `PhoenixCommonsPhase4Smoke` dogfood scaffolds from earlier platform phases. None relevant here.)

---

## 2. Update-check results per app

Even without an older install, the updater **discovery** logic (the network + version-compare + asset-select half of the auto-updater) was verified live against the published GitHub Releases — in **both** directions:

### 2a. Older-client direction (does it correctly OFFER the update?)

From `PHOENIX_4_APP_POST_RELEASE_SMOKE_REPORT.md` § 5 — `check_for_update` simulating a prior-version client:

| Simulated client | Discovered latest | Correct asset in URL |
|-------------------|-------------------|------------------------|
| CAD v0.1.1 → | `0.1.2` ✅ | `LabLayoutTool.zip` ✅ |
| Checkout v1.7.0 → | `1.7.1` ✅ | `PhoenixCheckoutTool.zip` ✅ |
| ValveMaster v1.1.0 → | `1.1.1` ✅ | `PhoenixMasterTool.zip` ✅ |
| Job Tracker v1.8.5 → | `1.8.6` ✅ | `ProjectTrackingTool.zip` ✅ |

### 2b. Current-client direction (does it correctly NOT offer a false update?)

Run today — `check_for_update` with `current_version` = published version, expecting `None`:

| Already-current client | Result |
|-------------------------|--------|
| CAD @ v0.1.2 | ✅ `None` — no false-positive update |
| Checkout @ v1.7.1 | ✅ `None` — no false-positive update |
| ValveMaster @ v1.1.1 | ✅ `None` — no false-positive update |
| Job Tracker @ v1.8.6 | ✅ `None` — no false-positive update |

**Both directions correct.** A prior-version user gets offered the right upgrade with the right asset; an up-to-date user is not nagged with a phantom update. This is the complete updater *discovery* contract, verified live.

---

## 3. Optional update-apply result

**Not performed** — and not possible locally:

- No older install exists to upgrade from (§ 1).
- The brief gates a destructive apply behind explicit operator approval, which was not given.
- The `download → validate → self-replace → relaunch` apply path was previously exercised end-to-end during platform development via the Phase 6C-B fake-release round-trip (recorded in `PHASE_6C_B_RUNTIME_SMOKE_REPORT` lineage). The download + validate portion is also covered by the post-release smoke (byte-equal asset downloads + zip-layout verification).

The one piece never run against a *live published* release for these specific versions is the final self-replace-and-relaunch on a real client. That requires a deliberately-kept older install — see § 5 for how to capture this on the next genuine update cycle.

---

## 4. Issues found

**None.** No wrong-asset selection, no wrong version detection, no false-positive update, no failed launch, no S1 event. All four installed apps present and at the correct version.

---

## 5. Support-watch checklist

Lightweight checklist for the next few real uses of each app (operator runs passively — no action needed unless a row trips). Covers the windows where a problem would most likely surface.

### Per-use watch (all 4 apps)

- [ ] **Launch stability** — app opens within a few seconds; no silent exit; no Python traceback dialog
- [ ] **S1 / AV behavior** — no Crowdstrike S1 quarantine pop; exe not deleted/blocked; no "publisher unknown" hard-block beyond the normal SmartScreen prompt
- [ ] **Update prompts** — in-app updater banner appears only when a genuinely newer release exists; no phantom "update available" on a current install (verified absent in § 2b, but watch in the wild)
- [ ] **Installer behavior** — for any fresh install/upgrade: installs to `{localappdata}\ATS Inc\<App>`; desktop/start-menu shortcut created; no admin prompt (PrivilegesRequired=lowest)
- [ ] **Missing-dependency errors** — no "ModuleNotFoundError" / "DLL not found" / "Qt platform plugin" errors on launch
- [ ] **User-data preservation** — existing data under `%APPDATA%\ATS Inc\<App>` intact after launch/upgrade; no reset-to-empty
- [ ] **Visual regression** — theme renders dark-navy correctly; no unstyled white flash; buttons/tables/dialogs styled

### Per-app specific watch

| App | Watch the first real use of… |
|-----|------------------------------|
| Lab Layout Tool | layout canvas render · parts catalog load · BricsCAD COM round-trip (if used) |
| Phoenix Checkout Tool | xlsx template load + export (openpyxl path) · tag preview |
| Phoenix Master Tool | valve decode → Decoded Fields green/red coloring · inventory/parts dialog · CFM calc |
| Project Tracking Tool | project list · financials dashboard (xlsb load) · change-order/notes/RSS · login/auth |

### Update-apply capture (next genuine release)

When the next real version of any tool ships (e.g. a future v0.1.3 / v1.7.2 / v1.1.2 / v1.8.7):

- [ ] **Before upgrading**, keep the current install in place (don't manually reinstall)
- [ ] Let the in-app updater detect + offer the new version
- [ ] Click "Install & Restart" and confirm: app exits → updater script runs → app relaunches at the new version
- [ ] Confirm the installed version bumped + user data preserved + no S1 quarantine

This captures the one untested live path (self-replace-and-relaunch) on a real client at the moment it naturally occurs — no need to manufacture an older install now.

---

## 6. Final recommendation

### **Release healthy — monitor only.**

- All 4 releases published, public, latest, correctly-assetted (closure report)
- Post-release smoke passed verdict A (download + layout + PE + boot + update-discovery)
- Updater discovery verified both directions (offers correct upgrade to old clients; no false positive to current clients)
- All 4 installed apps confirmed at the published version
- No issues found; no action required

No active intervention needed. Enter passive support-watch using the § 5 checklist. The only deferred verification (live self-replace-and-relaunch on a real client) is best captured naturally on the next genuine release rather than manufactured now.

---

## 7. Confirmation

- **No source changed.**
- **No tags changed.**
- **No assets uploaded.**
- **No releases edited.**
- **No update applied** (no destructive operation performed).
- **No rebuild.**
- Read-only verification + a single live `check_for_update` network call per app (GET against the public GitHub Releases API; no state change).

---

*Live updater verification complete. Release healthy — monitor only. Support-watch checklist active for the next real uses.*
