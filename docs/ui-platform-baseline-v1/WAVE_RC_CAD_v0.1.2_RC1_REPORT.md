# Phoenix CAD / Lab Layout Tool — v0.1.2-rc1 Report

> **Status:** RC built, tagged, pushed. Awaiting operator interactive validation + 1-day bake.
> **Date:** 2026-05-30.
> **Repo:** `JustinGlave/lab-layout-tool`.

---

## 1. Merge commit

`aa950a5` on `master` — *Merge release-hardening — build.bat aligned with FROZEN_BUILD_BASELINE*

Merged `release-hardening/cad-rc-readiness` @ `38cb3a5` → `master` (was at `fb383af`) via `--no-ff`.

## 2. Version bump commit

`35a0661` on `master` — *v0.1.2 — release hardening, no functional changes*

Changes:
- `version.py`: `__version__ = "0.1.1"` → `"0.1.2"`
- `README.md`: "Current Version: v0.1.1" → "v0.1.2"
- `CHANGELOG.md`: new `[0.1.2] — 2026-05-30` section documenting release hardening (no functional changes); prior unreleased Phase 3A note absorbed into the v0.1.2 entry

## 3. RC branch

`release/v0.1.2-rc1` @ `35a0661` (same SHA as the version-bump commit). Pushed to origin.

## 4. RC tag

Annotated tag `v0.1.2-rc1` pointing at `35a0661`.
Tag message: *Phoenix CAD v0.1.2 RC1 — release hardening, no functional changes*.
Pushed to origin. **Will remain immutable** per Decision #2.

## 5. Build result

Build executed successfully under existing `.venv` (Python 3.12.10) — soft-warn did not fire, commons preflight passed, full pipeline completed:

```
Detected venv Python: 3.12.10
============================================================
 Building Lab Layout Tool v0.1.2
============================================================
[0/4] Full cleanup (rmdir /s /q dist build)
[1/4] PyInstaller — hardened flags (--noupx + --collect-all=phoenix_commons + 8× stdlib excludes)
[2/4] Inno Setup compile — Successful compile (41.109 sec)
[3/4] Zip archives — full-folder updater zip + full-install zip
[4/4] Artifact verification passed
```

## 6. Artifacts produced

| Path | Size | Purpose |
|------|------|---------|
| `dist/LabLayoutTool/LabLayoutTool.exe` | 2,303,741 B (2.20 MB) | frozen exe |
| `dist/LabLayoutTool/_internal/` | folder | PyInstaller runtime + commons + assets |
| `dist/LabLayoutToolSetup.exe` | 38,016,778 B (36.3 MB) | Inno Setup installer |
| `dist/LabLayoutTool.zip` | 58,264,923 B (55.6 MB) | auto-updater zip (**full-folder**) |
| `dist/LabLayoutTool_FullInstall.zip` | 58,273,463 B (55.6 MB) | manual full-folder zip |

**Commons bundled** under `_internal/phoenix_commons/` with `theme/`, `widgets/`, `updater/`, `icons/`, `paths.py`, `_version.py`.

## 7. Updater zip contract result

```
entries: 305
has exe at root: True
has _internal/: True
full-folder contract: ✅ PRESERVED
```

Matches the Phase 3A precedent: Phoenix CAD updater zip ships the full folder (exe + `_internal/`), consumed by commons `download_and_apply` with `expected_internal=True` (commons default).

## 8. Operator validation status

**⏳ Awaiting operator interactive validation.**

### Validation instructions for operator

```
1. Install:
   double-click  dist\LabLayoutToolSetup.exe
   accept default install path  {localappdata}\ATS Inc\Lab Layout Tool

2. Launch:
   %LOCALAPPDATA%\ATS Inc\Lab Layout Tool\LabLayoutTool.exe

3. 5-min idle S1 observation:
   - leave the app open and idle for 5 minutes on your desktop
   - no Crowdstrike S1 quarantine pop expected
   - exe must remain on disk; no kill / relaunch cycle

4. Visual + functional review:
   - main window opens
   - parts catalog loads
   - layout canvas renders
   - BricsCAD integration buttons visible (active COM session not required for this smoke)
   - visual change ≈ 0% vs deployed v0.1.1 (commons retrofit is theme-neutral)

5. (Optional) upgrade smoke:
   - if you have v0.1.1 installed somewhere, install v0.1.2 over it
   - confirm user data / settings preserved
   - confirm install path unchanged ({localappdata}\ATS Inc\Lab Layout Tool)
```

Report back: ✅ pass or ❌ fail + observed issue.

## 9. Remaining blockers

**None** — RC is built, tagged, pushed; awaits operator interactive validation only.

If operator validation passes, no further work on CAD RC until bake completes.

If operator validation fails, halt the 4-app RC sequence and triage.

## 10. Bake start time

**Bake clock starts at the build completion timestamp: 2026-05-30 22:00 (local).**

(Per Decision #3 — bake begins when the RC artifacts exist on disk. Operator validation can happen during the bake window.)

## 11. Earliest Checkout RC start time

**Earliest: 2026-05-31 22:00 (local)** — 1-day minimum bake from CAD build completion.

Operator may extend by discretion (Decision #3) if any issue appears during CAD bake.

## 12. Confirmation

- **No GitHub Release created.** (Decision #5 — wait until all 4 RCs pass.)
- **No assets uploaded** to GitHub or anywhere else.
- **No production deployment.** Artifacts exist only in local `dist/`.
- **No AppId added** to installer.iss (CAD never had one declared; AppName-hashed default preserved for upgrade detection).
- **No install path change** (`{localappdata}\ATS Inc\Lab Layout Tool` byte-equal).
- **No user-data path change** (CAD uses commons `user_data_dir("Lab Layout Tool")` → `%APPDATA%\ATS Inc\Lab Layout Tool`).
- **No updater contract change** (full-folder payload preserved; 305-entry zip with exe + `_internal/*`).
- **No domain logic change**, no UI redesign, no commons API touch.

## Origin state

| Ref | SHA |
|-----|-----|
| `origin/master` | `35a0661` |
| `origin/release/v0.1.2-rc1` | `35a0661` |
| `origin/release-hardening/cad-rc-readiness` (preserved) | `38cb3a5` |
| `refs/tags/v0.1.2-rc1` | annotated tag → points at `35a0661` |

---

*Phoenix CAD v0.1.2-rc1 baking. Earliest Checkout RC kickoff: 2026-05-31 22:00 local.*
