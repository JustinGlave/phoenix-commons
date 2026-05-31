# Phoenix Checkout Tool — v1.7.1-rc1 Report

> **Status:** RC built, tagged, pushed. **Operator interactive validation ✅ PASSED 2026-05-30** (including xlsx template-load end-to-end). ValveMaster v1.1.1-rc1 kicked off immediately per bake waiver.
> **Date:** 2026-05-30.
> **Repo:** `JustinGlave/Phoenix-Checkout-Tool`.

---

## 1. CAD validation pass + bake waiver

Phoenix CAD v0.1.2-rc1 passed operator interactive validation on 2026-05-30 (5-min S1 + visual review). Operator waived bake windows the same day — RC progression now proceeds immediately after each successful operator validation.

CAD state on origin:
- `master` @ `35a0661` (v0.1.2 release-hardening commit)
- `release/v0.1.2-rc1` @ `35a0661`
- annotated tag `v0.1.2-rc1` → `35a0661` (immutable)

## 2. Merge commit

`f1722ff` on `main` — *Merge release-hardening — build.bat hardened + openpyxl declared*

Merged `release-hardening/checkout-rc-readiness` @ `9b638cb` → `main` (was at `700f565`) via `--no-ff`.

## 3. Version bump commit

`274b0a8` on `main` — *v1.7.1 — release hardening + openpyxl dependency declared*

Changes:
- `version.py`: `__version__ = "1.7.0"` → `"1.7.1"`
- `CHANGELOG.md`: new `[1.7.1] — 2026-05-30` section documenting release hardening + openpyxl declaration; prior `[Unreleased]` Phase 3B retrofit notes absorbed into the v1.7.1 entry under "Added"

(`README.md` has no "Current Version" line — no edit required.)

## 4. RC branch

`release/v1.7.1-rc1` @ `274b0a8` (same SHA as the version-bump commit). Pushed to origin.

## 5. RC tag

Annotated tag `v1.7.1-rc1` pointing at `274b0a8`.
Tag message: *Phoenix Checkout v1.7.1 RC1 — release hardening + openpyxl dependency declaration*.
Pushed to origin. **Immutable** per Decision #2.

## 6. Build result

Build executed successfully under existing `.venv` (Python 3.12.10) — soft-warn did not fire, commons preflight passed, openpyxl + PySide6 dependencies present:

```
Detected venv Python: 3.12.10
============================================================
 Building Phoenix Checkout v1.7.1
============================================================
[0/3] Sanity checks + full cleanup (rmdir /s /q dist build)
[1/3] PyInstaller — hardened flags (--noupx + --collect-all=phoenix_commons + 8× stdlib excludes)
[2/3] Inno Setup compile — Successful compile (35.531 sec)
[3/3] Zip archives — exe-only updater zip + full-install zip
```

## 7. Artifacts produced

| Path | Size | Purpose |
|------|------|---------|
| `dist/PhoenixCheckoutTool/PhoenixCheckoutTool.exe` | ~2 MB | frozen exe |
| `dist/PhoenixCheckoutTool/_internal/` | folder | PyInstaller runtime + commons + openpyxl + assets |
| `dist/PhoenixCheckoutToolSetup.exe` | 41,381,486 B (39.5 MB) | Inno Setup installer |
| `dist/PhoenixCheckoutTool.zip` | 4,593,289 B (4.4 MB) | auto-updater zip (**exe-only** per ADR-003) |
| `dist/PhoenixCheckoutTool_FullInstall.zip` | 61,684,530 B (58.8 MB) | manual full-folder zip |

**Commons bundled** under `_internal/phoenix_commons/` with `theme/`, `widgets/`, `updater/`, `icons/`, `paths.py`, `_version.py`.

## 8. Updater zip contract result

```
entries: 1
names: ['PhoenixCheckoutTool.exe']
exe at root: True
has _internal/: False
exe-only contract: ✅ PRESERVED (matches Phase 3B / ADR-003)
```

Phoenix Checkout's updater zip is exe-only — consumed by commons `download_and_apply` with `expected_internal=False`. Different contract from Phoenix CAD (which is full-folder). Both contracts preserved per their respective tools.

## 9. openpyxl packaging result

**✅ Bundled correctly inside `base_library.zip`** (PyInstaller's standard pure-Python archive — normal behavior, not flat-extracted under `_internal/openpyxl/`).

Runtime verification: offscreen frozen-exe launch (`QT_QPA_PLATFORM=offscreen timeout 6 PhoenixCheckoutTool.exe`) exits cleanly with no `ModuleNotFoundError` traceback. This is the same smoke that caught the root cause of the prior Wave 8b xlsx crash — now resolved by the `requirements.txt` `openpyxl==3.1.5` pin + PyInstaller `--hidden-import=openpyxl` + `--collect-submodules=openpyxl` flags added in the hardening branch (`9b638cb`).

## 10. Operator validation status

**✅ PASSED 2026-05-30** (recorded after operator interactive run).

Operator-observed gates:
- ✅ Installed from `dist\PhoenixCheckoutToolSetup.exe`
- ✅ Launched installed `PhoenixCheckoutTool.exe`
- ✅ 5-minute S1 observation — no quarantine, no kill / relaunch cycle
- ✅ No crash; exe remained on disk
- ✅ Visual review passed
- ✅ Checkout form rendered
- ✅ **xlsx template load worked** — confirms the openpyxl runtime fix end-to-end (the gap that was pending in Wave 8b is now closed)

No issues observed. Checkout RC clears.

### Validation instructions for operator (original, preserved for forensic record)

```
1. Install:
   double-click  dist\PhoenixCheckoutToolSetup.exe
   accept default install path  {localappdata}\ATS Inc\Phoenix Valve Checkout Tool

2. Launch:
   %LOCALAPPDATA%\ATS Inc\Phoenix Valve Checkout Tool\PhoenixCheckoutTool.exe

3. 5-min idle S1 observation:
   - leave the app open and idle for 5 minutes on your desktop
   - no Crowdstrike S1 quarantine pop expected
   - exe must remain on disk; no kill / relaunch cycle

4. Visual + functional review:
   - main window opens
   - checkout form renders
   - try opening one of the xlsx templates (checkout_template / template_gex /
     template_mav / template_cscp_fh / template_pbc_room) — validates the
     openpyxl runtime fix end-to-end
   - visual change ≈ 0% vs deployed v1.7.0
```

Report back: ✅ pass or ❌ fail + observed issue.

## 11. Remaining blockers

**None.** RC is built, tagged, pushed; awaits operator interactive validation only.

## 12. Bake start time

**Build completion: 2026-05-30 22:37 local.** Bake windows waived 2026-05-30 — RC progression proceeds after successful operator validation.

## 13. Next app

**ValveMaster v1.1.1-rc1** kicks off immediately after Checkout operator validation passes. No 1-day wait.

## 14. Confirmation

- **No GitHub Release created.** (Decision #5 — wait until all 4 RCs pass.)
- **No assets uploaded** to GitHub or anywhere else.
- **No production deployment.** Artifacts exist only in local `dist/`.
- **No AppId change** in installer.iss (Checkout never had an explicit AppId declared; AppName-hashed default preserved for upgrade detection).
- **No install path change** (`{localappdata}\ATS Inc\Phoenix Valve Checkout Tool` byte-equal).
- **No user-data path change** (Checkout uses `_app_data_path()` → `%APPDATA%\ATS Inc\Phoenix Valve Checkout Tool`).
- **No updater contract change** (exe-only payload preserved per ADR-003; 1-entry zip).
- **No domain logic change**, no UI redesign, no commons API touch.
- **CAD untouched** (CAD `master` HEAD still at `35a0661`; CAD RC tag immutable).
- **ValveMaster and Job Tracker untouched.**

## Origin state

| Ref | SHA |
|-----|-----|
| `origin/main` | `274b0a8` |
| `origin/release/v1.7.1-rc1` | `274b0a8` |
| `origin/release-hardening/checkout-rc-readiness` (preserved) | `9b638cb` |
| `refs/tags/v1.7.1-rc1` | annotated tag → `274b0a8` |

---

*Phoenix Checkout v1.7.1-rc1 ready for operator validation. ValveMaster v1.1.1-rc1 kicks off on operator pass.*
