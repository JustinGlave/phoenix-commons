# Wave 8b B8+B9 — Build Hardening + Source-Mode Validation Report

> **Status:** B8+B9 committed.
> **Commit:** `d7212cc` on `phase-8b-job-tracker-retrofit`.
> **Date:** 2026-05-28.

---

## 1. Files changed

| File | Change |
|------|--------|
| `build.bat` | modified (+32 / -2) |

No other files touched. CLAUDE.md retrofit-state already documents Python 3.12 canonical (from B1).

---

## 2. build.bat hardening summary

Added (per FROZEN_BUILD_BASELINE):

| Addition | Behavior |
|----------|----------|
| Python 3.12 soft-warn | Reads `.venv\Scripts\python --version`; prints yellow warning if not 3.12.x; build continues (Decision #6) |
| commons preflight | `python -c "import phoenix_commons"` — hard-fail with `git submodule update --init` hint on failure |
| Step 0 explicit cleanup | `rmdir /s /q dist build` (Decision #7) |
| `--noupx` | added to PyInstaller flags |
| `--collect-all=phoenix_commons` | added |
| Stdlib excludes | 8× `--exclude-module=` for tkinter, _tkinter, tcl, tk, lib2to3, idlelib, turtle, turtledemo |

---

## 3. Preserved build/packaging contracts

| Item | State |
|------|-------|
| AppName "Project Tracking Tool" | unchanged |
| Exe name `ProjectTrackingTool.exe` | unchanged |
| Updater zip `ProjectTrackingTool.zip` | unchanged (full-folder payload) |
| Full-install zip `ProjectTrackingTool_FullInstall.zip` | unchanged |
| AppId in installer.iss | **still NOT declared** (Decision #8 hard rule) |
| Install path `{localappdata}\ATS Inc\Project Tracking Tool` | unchanged |
| `--add-data` for PTT_Normal.ico / PTT_Transparent.png / phoenix_style.qss / pyxlsb | preserved verbatim |
| `--hidden-import=openpyxl`, `--hidden-import=openpyxl.cell._writer`, `--collect-submodules=openpyxl` | preserved |
| `--hidden-import=pyxlsb` | preserved |
| `--collect-submodules=PySide6.{QtCore,QtGui,QtWidgets}` | preserved |
| README/version sanity check (`findstr "Current Version: v%VERSION%"`) | preserved |
| `py_compile` across all preserved-local files | preserved |
| `python -m unittest discover -s tests` | preserved |
| Inno Setup compilation step | preserved |
| Inno Setup path probes (4 locations including `%LOCALAPPDATA%`) | preserved |
| Post-build zip layout verify (must contain exe + `_internal/*`) | preserved |
| `version.py` at `1.8.5` | unchanged |

### `ProjectTrackingTool.spec` disposition

**Preserved.** Entry is correct (`project_tracker_gui.py` — not stale). build.bat uses CLI flags exclusively, so the .spec is unused by the canonical pipeline. Per the brief's "if still correct, leave it alone" — no changes.

Known minor divergence (documented, non-blocking):
- `.spec` has `upx=True` (build.bat now uses `--noupx`)
- `.spec` lacks `--collect-all=phoenix_commons`
- `.spec` lacks stdlib excludes

Affects only ad-hoc manual `pyinstaller ProjectTrackingTool.spec` invocations. The canonical pipeline (build.bat) is unaffected.

---

## 4. Validation results

| Check | Result |
|-------|--------|
| `py_compile` across 11 preserved-local + facade files | clean ✅ |
| `tests/test_regressions.py` | **29/29 green** ✅ |
| Identity-equal × 5 widgets vs commons | ✅ all True |
| `updater.UpdateInfo is phoenix_commons.updater.UpdateInfo` | True ✅ |
| `updater.EXE_NAME` = `'ProjectTrackingTool.exe'` | unchanged ✅ |
| `updater.ZIP_ASSET_NAME` = `'ProjectTrackingTool.zip'` | unchanged ✅ |
| Offscreen theme smoke: merged QSS length | 30,769 chars ✅ |
| Brand tokens present (`#0a0e27`, etc.) | ✅ |
| Sentinels absent (`__BRAND_PRIMARY__` etc.) | ✅ |
| App-specific selectors (`#StatCard`, `#taskToolsButton`) | ✅ both present |
| `project_tracker_gui` module import | clean ✅ |
| `_EMBEDDED_QSS` retired (hasattr → False) | ✅ |
| `_resource_path` retired (hasattr → False) | ✅ |
| `starter_package/` deleted from disk | ✅ (leftover __pycache__ also removed) |
| `version.py` at `1.8.5` | unchanged ✅ |

build.bat itself not executed (B8 is hardening definition only; full frozen build is B10 per the brief).

---

## 5. Source-mode launch result

**Headless module import smoke:** offscreen import of `project_tracker_gui` succeeds clean. Module exports the expected facade surface:
- `apply_phoenix_theme` (rewritten body, two-layer compose)
- `resource_path` (imported from local `paths`)
- `apply_dark_theme` (imported from `phoenix_commons.theme`)
- 5 widget classes (all identity-equal to commons)

Module retirements confirmed by `hasattr` returning False for `_EMBEDDED_QSS` and `_resource_path`.

**Full MainWindow construction** deferred to B10 — Job Tracker's `MainWindow` requires login flow + admin auth + initial data load, which is heavier than ValveMaster's MainWindow construction smoke. Operator interactive launch at B10 is the canonical surface-level check.

---

## 6. Visual-change assessment

≈ 0% expected (Phoenix-CAD profile). Substantively confirmed by:

- Merged QSS = 30,769 chars (commons baseline + Job-Tracker overlay)
- All DEFAULT_BRAND tokens present + 0 sentinels remaining
- All Job-Tracker-specific selectors (`#StatCard`, `#taskToolsButton`, `#FinDataMeta`, `#ResizeHandle`, `#PassBadge`, etc.) preserved via overlay
- 5/5 commons widgets identity-equal to local refs
- No widget body / palette / QPalette setting change in commons facade
- Single known operator-visible delta: commons `UpdateBanner` drops `🆕` emoji prefix (Wave 8a precedent)

Operator interactive review at B10 confirms pixel-level parity.

---

## 7. Blockers / issues

None.

---

## 8. Next step

**B10 — frozen build + S1 observation** (operator action: activate Python 3.12 venv, run `build.bat`, observe S1 for 5 min, validate installer round-trip).

---

## 9. Confirmation

- No domain logic changed
- No financials changed
- No auth changed
- No updater changed (B3 facade preserved at `33fd3d9`)
- No installer.iss changed — **AppId still NOT declared** per Decision #8 hard rule
- No `version.py` change (stays at `1.8.5`)
- No production deployment (no PyInstaller invocation, no frozen exe, no installer build, no GitHub Release)

Branch HEAD: `d7212cc`. Ready for **B10**.
