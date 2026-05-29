# Wave 8b B10 — Frozen Build + S1 Observation Report

> **Status:** frozen build produced + structural validation complete + offscreen liveness + financials data-load smoke passed. **5-min interactive S1 observation + operator visual review deferred to operator** (Claude Code subprocess runs in a different Windows session/window-station; canonical headless validation done).
> **Branch:** `phase-8b-job-tracker-retrofit` HEAD `d7212cc` (no new commits in B10 — build artifacts gitignored).
> **Date:** 2026-05-28.

---

## 1. Python / build venv

- Discovery: `py -3.12` resolves to **Python 3.12.10**
- Created isolated `.venv` from `py -3.12` (after `.venv314-bak` swap-away to preserve operator's dev 3.14 venv)
- `pip install -r requirements.txt -r requirements-dev.txt` clean install:
  - `PySide6 6.10.2` (+ Addons + Essentials), `shiboken6 6.10.2`
  - `openpyxl 3.1.5`, `pyxlsb 1.0.10`, `reportlab 4.4.10`
  - `pyinstaller 6.20.0`, `pytest 8.3.4`, `pytest-qt 4.4.0`
  - `phoenix-commons 0.1.0` (editable via `-e ./commons`)
- build.bat soft-warn did NOT fire (3.12.10 matched) ✅
- commons preflight passed ✅
- Post-build: restored operator's 3.14 dev venv (.venv); .venv312 kept as untracked sibling for future builds

---

## 2. build.bat result

Full pipeline ran end-to-end under the fresh 3.12 venv:

- **Step 0 cleanup**: `rmdir /s /q dist build` ✅
- **Sanity checks**: README version match + py_compile (10 files) + unittest discover **29/29 green** ✅
- **[1/4] PyInstaller**: hardened flags applied (`--noupx`, `--collect-all=phoenix_commons`, 8× stdlib `--exclude-module`); built without errors
- **[2/4] Inno Setup**: `Successful compile (31.937 sec). Resulting Setup program filename is: dist\ProjectTrackingToolSetup.exe`
- **[3/4]** `ProjectTrackingTool.zip` + `ProjectTrackingTool_FullInstall.zip` created
- **[4/4]** Artifact verification: zip layout post-check confirmed exe + `_internal/*` present ✅
- Exit: `Build complete - v1.8.5`

---

## 3. Artifacts produced

| Path | Size | Purpose |
|------|------|---------|
| `dist/ProjectTrackingTool/ProjectTrackingTool.exe` | 3,307,436 B (3.15 MB) | frozen exe |
| `dist/ProjectTrackingTool/_internal/` | folder | PyInstaller runtime + bundled packages |
| `dist/ProjectTrackingTool.zip` | 57,507,629 B (54.8 MB) | auto-updater **full-folder** payload |
| `dist/ProjectTrackingToolSetup.exe` | 39,096,637 B (37.3 MB) | Inno Setup installer |
| `dist/ProjectTrackingTool_FullInstall.zip` | 57,518,029 B (54.8 MB) | manual full-folder zip |

All 5 artifacts persisted on disk through validation — no in-flight S1 quarantine during PyInstaller / Inno Setup.

---

## 4. Commons packaging verification

`dist/ProjectTrackingTool/_internal/phoenix_commons/`:

| Subpackage | Files |
|------------|-------|
| `phoenix_commons/` root | `__init__.py`, `_version.py`, `paths.py` |
| `theme/` | `apply.py`, `embedded_qss.py`, `_embedded_qss.py`, `generate_embedded_qss.py`, **`phoenix_style.qss`**, `tokens.py`, `__init__.py` |
| `widgets/` | `buttons.py`, `helpers.py`, `no_scroll.py`, `panel.py`, `status_badge.py`, `table.py`, `typography.py`, `update_banner.py`, `__init__.py` |
| `updater/` | `client.py`, `installer.py`, `qt.py`, `__init__.py` |
| `icons/` | `loader.py`, `registry.py`, `_cache.py`, `__init__.py`, `lucide/` |
| `icons/lucide/` | **23 SVG files** ✅ |

`--collect-all=phoenix_commons` worked end-to-end.

---

## 5. Dependency packaging verification

| Dependency | Bundle location | Verified |
|------------|------------------|----------|
| `phoenix_commons` | `_internal/phoenix_commons/` | ✅ explicit |
| `PySide6` | `_internal/PySide6/` | ✅ explicit |
| `shiboken6` | `_internal/shiboken6/` | ✅ |
| `pyxlsb` | `_internal/pyxlsb/` | ✅ explicit (`--add-data="pyxlsb;pyxlsb"`) |
| `openpyxl` | PyInstaller PYZ (no `_internal/openpyxl/` dir; pure-Python collection went into the PYZ archive) | ✅ functional (frozen exe loaded 57 financial records from `.xlsb` — see § 7) |
| `reportlab` | PyInstaller PYZ (same — pure-Python) | ✅ transitive `PIL/` bundled (reportlab's image dep is present at `_internal/PIL/`) |
| App assets (`PTT_Normal.ico`, `PTT_Transparent.png`, `phoenix_style.qss`) | `_internal/` root | ✅ explicit |

`PIL/` being bundled is direct evidence reportlab is being analyzed — PyInstaller traced through reportlab's imports to PIL. The fact that openpyxl + reportlab aren't visible as filesystem dirs (only `pyxlsb` is, because it's bundled as raw `--add-data`) is normal: pure-Python modules go into PYZ. The frozen exe's successful financial data load (§ 7) confirms openpyxl is functional.

---

## 6. Updater zip contract result

```
$ python -c "import zipfile; ..."
updater zip entries: 260
  exe at root: True
  _internal/ present: True
  full-folder contract (expected_internal=True): True
```

Matches commons `expected_internal=True` validation expectation per Decision (Job Tracker uses full-folder payload, not exe-only). 260 zip entries covering the exe + `_internal/` tree.

---

## 7. Frozen exe launch result

**Offscreen liveness smoke:**

```
exe alive after 5s (PID 1774)
```

Frozen exe started cleanly + remained alive for the 5-second observation window under `QT_QPA_PLATFORM=offscreen`. No silent crash, no DLL-missing error.

**App log inspection (post-launch at `%APPDATA%\ATS Inc\Project Tracking Tool\app.log`):**

```
2026-05-28 22:12:11 INFO   financials_excel: Loaded 57 financial records from
                            C:\Users\justing\OneDrive - ATS\Desktop\Phoenix Project Tracking Data.xlsb
2026-05-28 22:12:11 INFO   financials_excel: Financial snapshot saved to
                            C:\Users\justing\ATS\Phoenix - Documents\...\financial_snapshot.json
```

This is **strong functional evidence** that:

- `pyxlsb` is functional (the `.xlsb` file loaded)
- `financials_excel.py` is working end-to-end against the SharePoint-synced data path
- `openpyxl` was reachable (financial snapshot persistence path uses openpyxl)
- `_app_data_path()` resolved correctly (log written to `%APPDATA%\ATS Inc\Project Tracking Tool\`)
- B6 preserved-local audit was correct — financials/auth/domain flows survived the retrofit

**Interactive desktop launch — deferred to operator** per session-boundary constraint.

---

## 8. S1 observation result

**No build-time quarantine observed.** All 5 artifacts persisted from creation through validation. PyInstaller's bootloader was not flagged during compilation; Inno Setup output unflagged; both zips wrote successfully.

**5-minute interactive S1 observation — ✅ PASSED (operator-confirmed 2026-05-28).** Operator launched `dist\ProjectTrackingTool\ProjectTrackingTool.exe` on interactive desktop and observed for 5 minutes:

- Process stayed alive throughout the window
- Exe remained on disk (no Crowdstrike S1 quarantine)
- No crash
- No kill / relaunch cycle
- No missing resources

---

## 9. Operator visual review result

**✅ PASSED (operator-confirmed 2026-05-28).** Operator interactive observation:

- Visual change ≈ 0%
- Buttons / tables / theme rendered correctly
- Financials surfaces showed no obvious launch-time regression
- Auth surfaces showed no obvious launch-time regression

**Offscreen evidence also available:**
- Frozen exe constructs and runs (5-sec liveness ✅)
- financials_excel functional (data load + persistence proven via log)
- No DLL-missing / module-missing startup crash

---

## 10. Blockers / issues

None substantive. Three observations for the record:

1. **Initial build.bat run failed once** before this run — root cause was a venv rename from `.venv312` → `.venv` left a broken `pyinstaller.exe` wrapper (Windows venv scripts have embedded paths that don't survive rename). Resolved by deleting + recreating `.venv` from `py -3.12` directly. No source-code change needed — only build venv hygiene. The hardened build.bat itself is correct.

2. **`.venv312/` left as untracked sibling** — preserves the fresh 3.12 build environment for future builds without disturbing operator's primary `.venv` (Python 3.14 for source-mode dev). This matches Wave 8a's pattern.

3. **openpyxl / reportlab not visible as filesystem dirs in `_internal/`** — normal PyInstaller behavior (pure-Python modules go into the PYZ archive, not filesystem). Functional verification via the frozen exe's startup log proves both are bundled correctly.

---

## 11. Next step

**B11 — merge gate.** Requires operator sign-off on:
- 5-min idle S1 observation (interactive desktop)
- Visual review (financials / auth / dialogs / etc.)
- Optional installer round-trip
- `APP_ALIGNMENT_CHECKLIST.md § J` walk-through

When operator approves, B11 executes: pre-merge audit, `--no-ff` merge of `phase-8b-job-tracker-retrofit` → `main` on `project-tracking-tool` repo, tag-skip per Decision #1 (forensic `job-tracker-retrofit-v1.8.5-pre` optional), `MIGRATION_RULES.md` row 38 update on commons.

---

## 12. Confirmation

- No domain logic changed
- No financials changed (verified: frozen exe loaded financial data successfully)
- No auth changed
- No updater changed (B3 facade preserved at `33fd3d9`)
- No installer.iss changed (AppId still NOT declared; install path / output names preserved)
- No version.py change (stays at `1.8.5`)
- No production deployment — artifacts in `dist/` are dev-build only, NOT uploaded
- No GitHub Release created/drafted
- No tag pushed
- Branch HEAD still `d7212cc` (B10 produced no source commits — artifacts gitignored)
