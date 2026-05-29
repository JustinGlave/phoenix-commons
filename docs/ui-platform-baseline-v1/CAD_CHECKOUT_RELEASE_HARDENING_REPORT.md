# Phoenix CAD + Checkout — Release-Hardening Report

> **Status:** both hardening branches pushed.
> **Date:** 2026-05-29.
> **Scope:** build.bat only on each repo; no source touched.

---

## 1. Phoenix CAD changes

| Item | Value |
|------|-------|
| Repo | `JustinGlave/lab-layout-tool` |
| Branch | `release-hardening/cad-rc-readiness` |
| Commit | `38cb3a5` |
| Parent | `master` HEAD `fb383af` |
| Files changed | `build.bat` (+23 / -2) |

Additions to `build.bat`:
- Python 3.12 soft-warn (non-blocking)
- Step 0 explicit cleanup: `rmdir /s /q dist build`
- PyInstaller flags: `--noupx`, 8× `--exclude-module` (tkinter, _tkinter, tcl, tk, lib2to3, idlelib, turtle, turtledemo)

Preserved verbatim:
- `--onedir --windowed --noconfirm`, `--icon=LLT_Normal.ico`, `--name=LabLayoutTool`
- `--add-data` for `LLT_Normal.ico`, `LLT_Transparent.png`, `config/`, `blocks/`, `templates/`, `jobs/*.json`
- `--collect-all=phoenix_commons`, `--collect-submodules=PySide6.{QtCore,QtGui,QtWidgets}`
- `--hidden-import=win32com / win32com.client / pythoncom` (BricsCAD COM)
- Pre-existing commons preflight, README/version sanity check, py_compile checks, Inno Setup compilation, post-build zip layout verification
- `app.py` entry

---

## 2. Phoenix CAD validation / build / S1 result

| Check | Result |
|-------|--------|
| `.venv` swapped to fresh Python 3.12.10 (3.14 → `.venv314-bak`) | ✅ |
| `pip install -r requirements.txt -r requirements-dev.txt` | clean |
| build.bat end-to-end | DONE — v0.1.1 |
| Artifacts produced | 4: `LabLayoutTool.exe` + `_internal/`, installer (38.0 MB), updater zip (58.3 MB), full-install zip (58.3 MB) |
| Commons bundled | `phoenix_commons/{theme,widgets,updater,icons,paths,_version}` at `_internal/phoenix_commons/` ✅ |
| Updater zip contract | 305 entries; exe at root + `_internal/*` present — full-folder payload ✅ |
| Post-build zip layout verify (in build.bat) | passed ✅ |
| Inno Setup compilation | succeeded (31.95 sec) |
| 5-min interactive S1 + operator visual | **deferred to operator** (Claude Code subprocess cannot drive interactive desktop) |

---

## 3. Phoenix Checkout changes

| Item | Value |
|------|-------|
| Repo | `JustinGlave/Phoenix-Checkout-Tool` |
| Branch | `release-hardening/checkout-rc-readiness` |
| Commit | `4da0c47` |
| Parent | `main` HEAD `700f565` |
| Files changed | `build.bat` (+23 / -0) |

Additions to `build.bat`:
- Python 3.12 soft-warn (non-blocking)
- Step 0 explicit cleanup: `rmdir /s /q dist build`
- PyInstaller flags: `--noupx`, 8× `--exclude-module` (same list as CAD)

Preserved verbatim:
- `--onedir --windowed --noconfirm`, `--icon=PTT_Normal_green.ico`, `--name=PhoenixCheckoutTool`
- `--add-data` for ico/png + 5 xlsx templates (`checkout_template`, `template_gex`, `template_mav`, `template_cscp_fh`, `template_pbc_room`)
- `--collect-all=phoenix_commons`
- Pre-existing commons preflight, version.py readout, Inno Setup compilation step
- `checkout_tool_gui.py` entry

---

## 4. Phoenix Checkout validation / build / S1 result

| Check | Result |
|-------|--------|
| `.venv` swapped to fresh Python 3.12.10 (3.14 → `.venv314-bak`) | ✅ |
| `pip install -r requirements.txt pyinstaller==6.20.0` | clean (no `requirements-dev.txt` in repo; PyInstaller installed ad-hoc) |
| build.bat end-to-end | DONE — v1.7.0 |
| Artifacts produced | 4: `PhoenixCheckoutTool.exe` + `_internal/`, installer (33.8 MB), updater zip (1.8 MB), full-install zip (49.0 MB) |
| Commons bundled | `phoenix_commons/{theme,widgets,updater,icons,paths,_version}` at `_internal/phoenix_commons/` ✅ |
| Updater zip contract | **1 entry, `['PhoenixCheckoutTool.exe']`** — exe-only payload preserved (Phase 3B contract, `expected_internal=False` compatible) ✅ |
| Inno Setup compilation | succeeded (29.61 sec) |
| 5-min interactive S1 + operator visual | **deferred to operator** |

---

## 5. Contracts preserved

| Contract | Phoenix CAD | Phoenix Checkout |
|----------|--------------|-------------------|
| AppName | "Lab Layout Tool" — byte-equal | "Phoenix Valve Checkout Tool" — byte-equal |
| Exe name | `LabLayoutTool.exe` | `PhoenixCheckoutTool.exe` |
| Installer name | `LabLayoutToolSetup.exe` | `PhoenixCheckoutToolSetup.exe` |
| Updater zip name | `LabLayoutTool.zip` | `PhoenixCheckoutTool.zip` |
| Updater payload shape | full-folder (exe + `_internal/`) | **exe-only** (1 entry) |
| AppId | not declared (AppName-hash for v0.1.x users) | not declared (AppName-hash for v1.5.x..v1.7.0 users) |
| Install path | `{localappdata}\ATS Inc\Lab Layout Tool` | `{localappdata}\ATS Inc\Phoenix Valve Checkout Tool` |
| User-data path | unchanged | unchanged |
| `version.py` | `0.1.1` (unchanged) | `1.7.0` (unchanged) |
| Domain code | untouched | untouched |
| Updater module | untouched | untouched |
| installer.iss | untouched | untouched |
| BricsCAD COM integration | untouched (`win32com/pythoncom` hidden imports preserved) | n/a |
| Excel templates | n/a | preserved (5 `--add-data` lines unchanged) |

---

## 6. Blockers / issues

None blocking. Three observations:

1. **Phoenix Checkout PySide6 6.11.0 vs family canonical 6.10.2** — preserved as-is (out of release-hardening scope; bump-back is a separate decision if family wants version convergence).

2. **Phoenix Checkout lacks `requirements-dev.txt`** — PyInstaller pin installed ad-hoc this session. Family standard (ValveMaster/Job Tracker/PCC) has a `requirements-dev.txt` file. Could be added in a follow-up but is non-blocking for release.

3. **Both venvs swapped 3.14 → 3.12** — pre-existing `.venv314-bak/` folders left untracked on disk. Per the family convention from Wave 8a/8b, the canonical `.venv` going forward is Python 3.12.

---

## 7. Final 4-app release readiness verdict

| App | Status | Notes |
|-----|--------|-------|
| **ValveMaster / Phoenix Master Tool** | ✅ READY | Wave 8a hardened + operator-validated (2026-05-26) |
| **Job Tracker / Project Tracking Tool** | ✅ READY | Wave 8b hardened + operator-validated (2026-05-28) |
| **Phoenix CAD / Lab Layout Tool** | ✅ READY (structurally) | This commit hardened; needs operator 5-min interactive S1 + visual review before RC |
| **Phoenix Checkout Tool** | ✅ READY (structurally) | This commit hardened; needs operator 5-min interactive S1 + visual review before RC |

**All 4 production tools are now structurally release-ready.** Two are operator-validated (ValveMaster + Job Tracker); two need a single operator validation session (CAD + Checkout). After that, all 4 can ship as RC builds.

---

## 8. Recommended RC release order

For the "release all 4 production apps together" operator direction:

### Step A — Operator validation pass (single working session)

Operator runs the 2 unvalidated build pipelines on the interactive desktop and confirms:
1. **Phoenix CAD** — install from `LabLayoutToolSetup.exe`, launch, 5-min S1 idle, walk through main window + parts/layouts UI, confirm no quarantine + no visible regression
2. **Phoenix Checkout** — install from `PhoenixCheckoutToolSetup.exe`, launch, 5-min S1 idle, walk through main window + checkout flow, confirm no quarantine + no visible regression

### Step B — Decide RC tag policy + merge hardening branches

Either:
- (a) Merge `release-hardening/cad-rc-readiness` → `master` and `release-hardening/checkout-rc-readiness` → `main` BEFORE producing RC tags, or
- (b) Produce RC artifacts from the hardening branches first, then merge after validation

Either pattern is fine; (a) is the cleaner mainline state.

### Step C — Coordinated 4-app RC

Recommended tag scheme (forensic style, similar to existing precedent):

| Tool | Current ver | Suggested RC tag | Notes |
|------|-------------|-------------------|-------|
| ValveMaster | 1.1.0 | `v1.1.0-rc1` (or `v1.1.1-rc1` if treating hardening as new) | Hardening already merged to main |
| Job Tracker | 1.8.5 | `v1.8.5-rc1` (or `v1.8.6-rc1`) | Hardening already merged to main |
| Phoenix CAD | 0.1.1 | `v0.1.2-rc1` | Merge `release-hardening/cad-rc-readiness` first |
| Phoenix Checkout | 1.7.0 | `v1.7.1-rc1` | Merge `release-hardening/checkout-rc-readiness` first |

The `version.py` bump (1.1.0 → 1.1.1, 1.8.5 → 1.8.6, etc.) is operator policy — both schools (treat hardening as patch-bump-worthy OR keep version steady) are defensible.

### Step D — RC bake window + final release decision

After RCs build + install cleanly on 1-2 operator machines for a week (or shorter at operator discretion), promote to actual `vX.Y.Z` release tags + GitHub Release with installer + updater zip uploaded.

---

## 9. Confirmation

- **No UI changes** in either tool.
- **No domain logic changes** in either tool (CAD's `cad/` subsystem + BricsCAD COM untouched; Checkout's xlsx template handling untouched).
- **No updater contract changes** — CAD remains full-folder, Checkout remains exe-only.
- **No production deployment** — no installer uploaded, no GitHub Release.
- **No GitHub Release** drafted or published.
- **No version.py bumps** — CAD stays at `0.1.1`, Checkout stays at `1.7.0`.
- **No `installer.iss` edits** — AppId absence preserved for both.
- **No commons API change** — both consumed existing commons API.
- **All hardening confined to `build.bat`** — single-file change per tool.

---

## Verdict

### **Hardening complete — both tools structurally release-ready.**

Awaiting operator interactive validation session for CAD + Checkout (5-min S1 idle + visual review each). Once that clears, all 4 production tools can proceed to coordinated RC builds.

Branches pushed:
- `JustinGlave/lab-layout-tool` → `release-hardening/cad-rc-readiness` @ `38cb3a5`
- `JustinGlave/Phoenix-Checkout-Tool` → `release-hardening/checkout-rc-readiness` @ `4da0c47`

---

*End of Phoenix CAD + Checkout release-hardening report. Next: operator 5-min S1 + visual validation on both tools, then a coordinated 4-app RC plan.*
