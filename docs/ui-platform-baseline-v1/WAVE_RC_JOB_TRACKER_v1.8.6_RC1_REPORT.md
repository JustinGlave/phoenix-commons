# Job Tracker / Project Tracking Tool — v1.8.6-rc1 Report

> **Status:** RC built, tagged, pushed. Awaiting operator interactive validation. **Final RC in the 4-app sequence.**
> **Date:** 2026-05-31.
> **Repo:** `JustinGlave/project-tracking-tool`.

---

## 1. Prior RC validation summary

All 3 prior RCs operator-validated 2026-05-30 (bake windows waived 2026-05-30):

| RC | Tag | Operator pass | Updater zip contract |
|----|-----|---------------|----------------------|
| Phoenix CAD | `v0.1.2-rc1` @ `35a0661` | ✅ 2026-05-30 (5-min S1 + visual + main window + parts catalog + layout canvas + BricsCAD buttons) | full-folder (305 entries) |
| Phoenix Checkout | `v1.7.1-rc1` @ `274b0a8` | ✅ 2026-05-30 (5-min S1 + visual + checkout form + xlsx template-load end-to-end) | exe-only (1 entry, ADR-003) |
| ValveMaster / PMT | `v1.1.1-rc1` @ `e6eefa1` | ✅ 2026-05-30 (5-min S1 + visual + Decoded Fields valid/invalid coloring + main validation workflow) | exe-only (1 entry, ADR-003) |

## 2. Version bump commit

`689e8ee` on `main` — *v1.8.6 — Wave 8b retrofit + hardening + starter_package removal, no functional changes*

Changes:
- `version.py`: `__version__ = "1.8.5"` → `"1.8.6"`
- `README.md`: "**Current Version: v1.8.5**" → "**Current Version: v1.8.6**"
- `CHANGELOG.md`: new `[1.8.6] — 2026-05-30` section consolidating Wave 8b retrofit + build hardening + starter_package removal as a single shipping milestone (Excel/pyxlsb/reportlab pin preservation noted; AppId absence preservation noted)

## 3. RC branch

`release/v1.8.6-rc1` @ `689e8ee`. Pushed to origin.

## 4. RC tag

Annotated tag `v1.8.6-rc1` pointing at `689e8ee`.
Tag message: *Job Tracker / Project Tracking Tool v1.8.6 RC1 — commons retrofit + release hardening, no functional changes*.
Pushed to origin. **Immutable** per Decision #2.

## 5. Build result

Build executed under fresh `.venv` (Python 3.12.10, recreated for this run after the pyinstaller wrapper-path issue from prior renames). Hardened build.bat 3.12 soft-warn did not fire, commons preflight passed, sanity checks (README version + py_compile + 29-test unittest discover + post-build zip layout verify) all green:

```
Detected venv Python: 3.12.10
============================================================
 Building Project Tracking Tool v1.8.6
============================================================
[0/4] Sanity checks + full cleanup (rmdir /s /q dist build)
[1/4] PyInstaller — hardened flags (--noupx + --collect-all=phoenix_commons +
                                    8× stdlib excludes + openpyxl/pyxlsb hidden
                                    imports + --add-data="pyxlsb;pyxlsb")
[2/4] Inno Setup compile — Successful compile (32.969 sec)
[3/4] Zip archives — full-folder updater zip + full-install zip
[4/4] Artifact verification passed
Build complete - v1.8.6
```

## 6. Artifacts produced

| Path | Size | Purpose |
|------|------|---------|
| `dist/ProjectTrackingTool/ProjectTrackingTool.exe` | ~3 MB | frozen exe |
| `dist/ProjectTrackingTool/_internal/` | folder | PyInstaller runtime + commons + pyxlsb + assets |
| `dist/ProjectTrackingToolSetup.exe` | 39,108,336 B (37.3 MB) | Inno Setup installer |
| `dist/ProjectTrackingTool.zip` | 57,508,860 B (54.8 MB) | auto-updater zip (**full-folder**, `expected_internal=True`) |
| `dist/ProjectTrackingTool_FullInstall.zip` | 57,519,260 B (54.9 MB) | manual full-folder zip |

## 7. Dependency packaging result

| Dep | Pin | Bundled where | Verified |
|-----|-----|---------------|----------|
| `phoenix_commons` | 0.1.0 (editable) | `_internal/phoenix_commons/` (theme/widgets/updater/icons/paths) | ✅ flat directory present |
| `pyxlsb` | 1.0.10 | `_internal/pyxlsb/` (flat-extracted via `--add-data="pyxlsb;pyxlsb"`) | ✅ directory present |
| `openpyxl` | 3.1.5 | `_internal/base_library.zip` (PyInstaller pure-Python archive — `--hidden-import=openpyxl` + `--collect-submodules=openpyxl`) | ✅ offscreen launch exit 0 = imports clean |
| `reportlab` | 4.4.10 | `_internal/base_library.zip` | ✅ same offscreen smoke |
| `PySide6` | 6.10.2 | `_internal/PySide6/` | ✅ flat directory present |

## 8. Updater zip contract result

```
entries: 260
exe at root: True
has _internal/: True
full-folder contract (expected_internal=True): ✅ PRESERVED
```

Matches the Wave 8b contract: Job Tracker updater zip ships the full folder (exe + `_internal/*` including `phoenix_commons`/`pyxlsb`/`openpyxl`). Consumed by commons `download_and_apply` with `expected_internal=True`.

## 9. Operator validation status

**⏳ Awaiting operator interactive validation.**

### Validation instructions for operator

```
1. Install:
   double-click  dist\ProjectTrackingToolSetup.exe
   accept default install path  {localappdata}\ATS Inc\Project Tracking Tool

2. Launch:
   %LOCALAPPDATA%\ATS Inc\Project Tracking Tool\ProjectTrackingTool.exe

3. 5-min idle S1 observation:
   - leave the app open and idle for 5 minutes
   - no Crowdstrike S1 quarantine pop expected
   - exe must remain on disk; no kill / relaunch cycle

4. Visual + functional review:
   - main project list opens
   - financials / auth surfaces show no obvious launch-time regression
   - Excel-related surfaces (financials dashboard / xlsx export) do
     not show "missing dependency" errors
   - visual change ≈ 0% vs deployed v1.8.5

5. (Optional) upgrade smoke:
   - if you have v1.8.5 installed, install v1.8.6 over it
   - confirm AppName-hashed upgrade detection works
     (installer should prompt "Upgrade" not "New install" — Decision #8
     hard rule preserves the existing user-base upgrade path)
   - user data preserved at %APPDATA%\ATS Inc\Project Tracking Tool
```

Report back: ✅ pass or ❌ fail + observed issue.

## 10. Remaining blockers

**None.** RC is built, tagged, pushed; awaits operator interactive validation only.

## 11. Confirmation

- **No GitHub Release created.** (Decision #5 — wait until all 4 RCs pass.)
- **No assets uploaded** to GitHub or anywhere else.
- **No production deployment.** Artifacts exist only in local `dist/`.
- **No AppId added** to installer.iss (Decision #8 hard rule — AppName-hashed default preserved for v1.6.0..v1.8.5 user-base upgrade detection).
- **No install path change** (`{localappdata}\ATS Inc\Project Tracking Tool` byte-equal).
- **No user-data path change** (`%APPDATA%\ATS Inc\Project Tracking Tool`).
- **No updater contract change** (full-folder payload preserved; 260-entry zip with exe + `_internal/*`).
- **No financials/auth/domain logic changes** (`project_tracker_backend.py`, `financials_*.py`, `user_auth.py`, `generate_guide.py` 0-diff vs Wave 8b merge HEAD).
- **CAD, Checkout, ValveMaster untouched.**

## Origin state

| Ref | SHA |
|-----|-----|
| `origin/main` | `689e8ee` |
| `origin/release/v1.8.6-rc1` | `689e8ee` |
| `refs/tags/v1.8.6-rc1` | annotated tag → `689e8ee` |
| `refs/tags/job-tracker-retrofit-v1.8.5-pre` (preserved forensic) | `6a0d60b` |

---

## Next step

**On Job Tracker operator validation pass → all 4 RCs are validated.**

Then prepare:
- 4-app RC package status summary (`PHOENIX_4_APP_RC_STATUS_REPORT.md`)
- GitHub Release draft authoring (no asset upload yet)
- Final stable tags (`v0.1.2` / `v1.7.1` / `v1.1.1` / `v1.8.6`) on the same SHAs as the `-rc1` tags
- Asset upload sequence on operator publish-go-ahead

*Job Tracker v1.8.6-rc1 ready for operator validation. This is the last RC in the 4-app sequence.*
