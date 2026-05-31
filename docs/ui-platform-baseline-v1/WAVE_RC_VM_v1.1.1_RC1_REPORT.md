# ValveMaster / Phoenix Master Tool — v1.1.1-rc1 Report

> **Status:** RC built, tagged, pushed. **Operator interactive validation ✅ PASSED 2026-05-30.** Job Tracker v1.8.6-rc1 kicked off immediately.
> **Date:** 2026-05-30.
> **Repo:** `JustinGlave/phoenix-master-tool`.

---

## 1. Checkout validation pass + bake waiver

Phoenix Checkout v1.7.1-rc1 passed operator interactive validation 2026-05-30 (5-min S1 + visual + xlsx template-load end-to-end). Bake windows remain waived per operator decision 2026-05-30. RC progression proceeds immediately on validation pass.

CAD + Checkout state on origin (preserved, untouched in this session):
- CAD: `master` @ `35a0661`, `release/v0.1.2-rc1`, tag `v0.1.2-rc1`
- Checkout: `main` @ `274b0a8`, `release/v1.7.1-rc1`, tag `v1.7.1-rc1`

## 2. Merge commit

**Not needed.** ValveMaster's Wave 8a hardening was already merged to `main` at `631dbe8` (Wave 8a merge commit). No additional hardening branch — build.bat hardening was part of Wave 8a B6.

## 3. Version bump commit

`e6eefa1` on `main` — *v1.1.1 — Wave 8a retrofit + hardening (commons-backed), no functional changes*

Changes:
- `version.py`: `__version__ = "1.1.0"` → `"1.1.1"`
- `CHANGELOG.md`: new `[1.1.1] — 2026-05-30` section documenting Wave 8a retrofit + build hardening + Decoded Fields visual fix; prior `[Unreleased]` Pending note retired

(`README.md` has no "Current Version" line — no edit required.)

## 4. RC branch

`release/v1.1.1-rc1` @ `e6eefa1` (same SHA as the version-bump commit). Pushed to origin.

## 5. RC tag

Annotated tag `v1.1.1-rc1` pointing at `e6eefa1`.
Tag message: *ValveMaster / Phoenix Master Tool v1.1.1 RC1 — Wave 8a retrofit + hardening, no functional changes*.
Pushed to origin. **Immutable** per Decision #2.

## 6. Build result

Build executed successfully under `.venv312` (Python 3.12.10, Wave 8a B8 build venv reused). Hardened build.bat soft-warn did not fire, commons preflight passed:

```
Building version 1.1.1...
[0/4] Cleaning previous build + dist (full cleanup)
[1/4] PyInstaller — hardened flags (--noupx + --collect-all=phoenix_commons + 8× stdlib excludes)
[2/4] Inno Setup compile — Successful compile (30.547 sec)
[3/4] PhoenixMasterTool.zip — exe-only (ADR-003)
[4/4] PhoenixMasterTool_FullInstall.zip — full folder
DONE — v1.1.1
```

## 7. Artifacts produced

| Path | Size | Purpose |
|------|------|---------|
| `dist/PhoenixMasterTool/PhoenixMasterTool.exe` | ~2 MB | frozen exe |
| `dist/PhoenixMasterTool/_internal/` | folder | PyInstaller runtime + commons + assets |
| `dist/PhoenixMasterToolSetup.exe` | 33,828,432 B (32.3 MB) | Inno Setup installer |
| `dist/PhoenixMasterTool.zip` | 2,044,232 B (1.95 MB) | auto-updater zip (**exe-only** per ADR-003) |
| `dist/PhoenixMasterTool_FullInstall.zip` | 49,071,698 B (46.8 MB) | manual full-folder zip |

**Commons bundled** under `_internal/phoenix_commons/` with `theme/`, `widgets/`, `updater/`, `icons/`, `paths.py`, `_version.py`.

## 8. Updater zip contract result

```
entries: 1
names: ['PhoenixMasterTool.exe']
exe-only contract (ADR-003): ✅ PRESERVED
```

ValveMaster updater zip is exe-only — consumed by commons `download_and_apply` with `expected_internal=False`. Same contract as Checkout; different from CAD (full-folder) and Job Tracker (full-folder).

## 9. AppId preservation result

```
installer.iss line 11: AppId={{A7F3C2D1-9B4E-4F6A-8C3D-1E5B7A9F2C4D}
```

**AppId GUID `{A7F3C2D1-9B4E-4F6A-8C3D-1E5B7A9F2C4D}` preserved byte-for-byte** from v1.1.0. Inno Setup upgrade detection works against existing v1.1.0 installs.

## 10. Offscreen launch smoke

`QT_QPA_PLATFORM=offscreen timeout 6 dist/PhoenixMasterTool/PhoenixMasterTool.exe` → exit 0 cleanly. No startup crash, no missing-module traceback, commons import works in frozen context.

## 11. Operator validation status

**✅ PASSED 2026-05-30** (recorded after operator interactive run).

Operator-observed gates:
- ✅ Installed from `dist\PhoenixMasterToolSetup.exe`
- ✅ Launched installed `PhoenixMasterTool.exe`
- ✅ No S1 quarantine
- ✅ No crash; exe remained on disk
- ✅ Visual review passed
- ✅ **Decoded Fields valid/invalid coloring still correct** (Wave 8a B8a fix preserved end-to-end)
- ✅ Main validation workflow looked normal

No issues observed. VM RC clears.

### Validation instructions for operator (original, preserved for forensic record)

```
1. Install:
   double-click  dist\PhoenixMasterToolSetup.exe
   accept default install path  {localappdata}\ATS Inc\PhoenixMasterTool

2. Launch:
   %LOCALAPPDATA%\ATS Inc\PhoenixMasterTool\PhoenixMasterTool.exe

3. 5-min idle S1 observation:
   - leave the app open and idle for 5 minutes on your desktop
   - no Crowdstrike S1 quarantine pop expected
   - exe must remain on disk; no kill / relaunch cycle

4. Visual + functional review:
   - main window opens
   - decode a model number (any from the test models list)
   - confirm Decoded Fields render correctly: VALID segments GREEN,
     INVALID segments RED (Wave 8a B8a fix — most important
     visual gate for VM)
   - inventory / parts list dialog opens
   - CFM calculator opens
   - visual change ≈ 0% vs deployed v1.1.0

5. (Optional) upgrade smoke:
   - if you have v1.1.0 installed, install v1.1.1 over it
   - confirm AppId-based upgrade detection works
     (installer should prompt "Upgrade" not "New install")
   - user data preserved
```

Report back: ✅ pass or ❌ fail + observed issue.

## 12. Remaining blockers

**None.** RC is built, tagged, pushed; awaits operator interactive validation only.

## 13. Build start / bake state

**Build completion: 2026-05-30 22:57 local.** Bake windows waived 2026-05-30 — RC progression proceeds after successful operator validation.

## 14. Next app

**Job Tracker v1.8.6-rc1** kicks off immediately after VM operator validation passes. Final app in the 4-app RC sequence.

## 15. Confirmation

- **No GitHub Release created.** (Decision #5 — wait until all 4 RCs pass.)
- **No assets uploaded** to GitHub or anywhere else.
- **No production deployment.** Artifacts exist only in local `dist/`.
- **AppId preserved byte-for-byte** (`{A7F3C2D1-9B4E-4F6A-8C3D-1E5B7A9F2C4D}` — Inno Setup upgrade-detection identity unchanged from v1.1.0).
- **No install path change** (`{localappdata}\ATS Inc\PhoenixMasterTool` byte-equal).
- **No user-data path change** (`%APPDATA%\ATS Inc\PhoenixMasterTool`).
- **No updater contract change** (exe-only payload preserved per ADR-003; 1-entry zip).
- **No domain logic change**, no UI redesign, no commons API touch.
- **CAD, Checkout, Job Tracker untouched.**

## Origin state

| Ref | SHA |
|-----|-----|
| `origin/main` | `e6eefa1` |
| `origin/release/v1.1.1-rc1` | `e6eefa1` |
| `refs/tags/v1.1.1-rc1` | annotated tag → `e6eefa1` |
| `refs/tags/valvemaster-retrofit-v1.1.0-pre` (preserved forensic) | `631dbe8` |

---

*ValveMaster v1.1.1-rc1 ready for operator validation. Job Tracker v1.8.6-rc1 kicks off on operator pass.*
