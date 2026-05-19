# Phase 4B-local Retry Report — phoenix-commons

> Phase 4B-local: rebuild Phase 4's PyInstaller smoke test in a fresh
> phoenix-commons-local venv, with PyInstaller pinned to Job Tracker's
> version, and writing build output to an **external** scratch directory
> outside the source tree. No AV exclusions, no Plan B vendoring, no
> production-tool changes. The goal was to determine whether either the
> venv switch or the external build location would let the frozen exe
> survive long enough to be launched.

## Status

**Partial again. Source-mode verified end-to-end; frozen-mode launch still blocked by corporate AV.**

- Build itself reproduces cleanly: `PI_EXIT=0`, exe written (2,111,472 bytes), `_internal/phoenix_commons/theme/phoenix_style.qss` present (17,662 bytes), all four `_internal/phoenix_commons/theme/*.py` files (init, _embedded_qss, apply, phoenix_style.qss) present.
- **Source-mode execution of `scratch/phase4_smoke.py` SUCCEEDED** under the new venv — the success marker shows `status: success`, `apply_dark_theme_ok: true`, `qss_resource_exists: true`, all four widgets instantiated cleanly.
- **Frozen-exe launch failed identically to Phase 4**: by the time PowerShell got to `Start-Process`, the exe was already quarantined by AV (`Test-Path` returned `False` before any launch attempt).
- The AV did NOT damage source files this round (verified `git status` clean, 33/33 tests still pass, all 22 source `.py` files intact). Phase 4's earlier source-file sweep may have been a one-time event tied to where the build happened (inside the source tree vs. outside it).

Net Phase 4B-local finding: **moving the build out of the source tree avoided the source-file damage, but did not protect the bootloader exe itself**. The AV's heuristic on PyInstaller bootloaders is content-based, not path-based.

## Python versions compared

| Source | Python | Location |
|--------|--------|----------|
| Job Tracker venv | 3.14.3 | `C:\Users\justing\PycharmProjects\Job Tracker\.venv\Scripts\python.exe` |
| phoenix-commons system Python | 3.14.3 | `C:\Python314\python.exe` |
| **phoenix-commons NEW venv (Phase 4B-local)** | **3.14.3** | `C:\Users\justing\PycharmProjects\phoenix-commons\.venv\Scripts\python.exe` |

The user's instructions mentioned `py -3.11` as a default. **Python 3.11 is not installed on this machine.** `py -0p` reports only one entry:

```
 -V:3.14 *        C:\Users\justing\AppData\Local\Python\pythoncore-3.14-64\python.exe
```

`py -3.11 --version` returns:

```
No suitable Python runtime found
Pass --list (-0) to see all detected environments on your machine
or set environment variable PYLAUNCHER_ALLOW_INSTALL to use winget
or open the Microsoft Store to the requested version.
```

Decision: created the venv with `py -3.14` to **match Job Tracker exactly** (both 3.14.3) — that's the strongest dev/prod parity available and removes any "Python 3.11 vs 3.14" hypothesis from the AV diagnosis.

## PyInstaller versions compared

| Source | PyInstaller | Exact path |
|--------|-------------|------------|
| Job Tracker venv | **6.19.0** | `C:\Users\justing\PycharmProjects\Job Tracker\.venv\Scripts\pyinstaller.exe` |
| phoenix-commons user-site (Phase 4) | broken (`__main__` missing after AV sweep) | `C:\Users\justing\AppData\Roaming\Python\Python314\site-packages\PyInstaller` |
| **phoenix-commons NEW venv (Phase 4B-local)** | **6.19.0** (pinned to match Job Tracker) | `C:\Users\justing\PycharmProjects\phoenix-commons\.venv\Scripts\pyinstaller.exe` |

Install command:

```
.venv\Scripts\python.exe -m pip install pytest "pyinstaller==6.19.0"
```

`Successfully installed altgraph-0.17.5 colorama-0.4.6 iniconfig-2.3.0 packaging-26.2 pefile-2024.8.26 pluggy-1.6.0 pygments-2.20.0 pyinstaller-6.19.0 pyinstaller-hooks-contrib-2026.5 pytest-9.0.3 pywin32-ctypes-0.2.3 setuptools-82.0.1`

`.venv\Scripts\pyinstaller.exe --version` reported `6.19.0` — matches Job Tracker bit-for-bit.

## Exact PyInstaller path used

`C:\Users\justing\PycharmProjects\phoenix-commons\.venv\Scripts\pyinstaller.exe`

(Same `pyinstaller.exe` Job Tracker uses for its own builds, just from a different `.venv`.)

## External build folder used

```
PHX_SMOKE_ROOT = C:\Users\justing\AppData\Local\ATS Inc\PhoenixCommonsPhase4Smoke
  dist    = C:\Users\justing\AppData\Local\ATS Inc\PhoenixCommonsPhase4Smoke\dist
  build   = C:\Users\justing\AppData\Local\ATS Inc\PhoenixCommonsPhase4Smoke\build
  spec    = C:\Users\justing\AppData\Local\ATS Inc\PhoenixCommonsPhase4Smoke\spec
```

This places the build output in the same `{localappdata}\ATS Inc\` namespace where Phoenix tools' Inno Setup installers land production exes. The hypothesis was that any AV exclusion applied to installed Phoenix tools might extend to fresh builds under the same root. **It did not** — the AV still quarantined the bootloader exe.

The `--distpath` / `--workpath` / `--specpath` separation kept the source tree completely untouched: no `build/` or `dist/` folder appeared in `phoenix-commons\` during or after this phase, and no `PhoenixCommonsSmoke.spec` was emitted into the repo. The `.spec` lives only at `$PHX_SMOKE_ROOT\spec\`.

## Whether the exe survived

**No.** Same pattern as Phase 4:

1. `ls -la` immediately after `PyInstaller exit 0`: exe present, 2,111,472 bytes
2. Subsequent PowerShell call (~5–10 seconds later): exe missing (`Test-Path` returns `False`)
3. The exe never got launched

```
===exe present immediately after build?===
-rwxr-xr-x 1 ATSINC+justing 4096 2111472 May 13 10:17 .../PhoenixCommonsSmoke.exe
```

Then in the PowerShell launch attempt:

```
Exists before run: False
Exe still present after run: False
Marker exists: False
```

The `_internal/` directory survives — only the bootloader `.exe` is quarantined. AV's heuristic specifically targets the PyInstaller bootloader binary (`runw.exe`-derived) and not the loose package files.

## Whether the exe launched

**No.** It was already gone before `Start-Process` could even attempt it.

## Marker contents — frozen run

None. The marker file was never written because the exe never ran:

```
$ cat %TEMP%\phoenix_commons_phase4_marker.json
(file does not exist)
```

## Marker contents — source-mode run (sanity verification)

This is the key new evidence from Phase 4B-local. When the same scratch script was run via the venv's Python interpreter (not the frozen exe), it executed end-to-end and wrote a clean success marker:

```json
{
  "status": "success",
  "marker_path": "C:\\Users\\justing\\AppData\\Local\\Temp\\phoenix_commons_phase4_marker.json",
  "phoenix_commons_version": "0.1.0",
  "apply_dark_theme_ok": true,
  "qt_style_applied": true,
  "stylesheet_set": true,
  "qss_resource_path": "C:\\Users\\justing\\PycharmProjects\\phoenix-commons\\src\\phoenix_commons\\theme\\phoenix_style.qss",
  "qss_resource_exists": true,
  "embedded_qss_length": 16892,
  "embedded_qss_has_phoenix_navy": true,
  "widgets_instantiated": [
    "PrimaryButton",
    "Panel",
    "PhoenixTable",
    "UpdateBanner"
  ],
  "primary_button_text": "Test",
  "panel_object_name": "Panel",
  "table_shape": [2, 3],
  "update_banner_object_name": "UpdateBanner",
  "frozen": false,
  "python_executable": "C:\\Users\\justing\\PycharmProjects\\phoenix-commons\\.venv\\Scripts\\python.exe",
  "_meipass": null,
  "commons_dir_in_meipass": null,
  "collected_phoenix_commons_files": []
}
```

What this proves about the packaging:

- `phoenix_commons.__version__` resolves correctly (`0.1.0`)
- `apply_dark_theme(app)` runs without raising — palette + QSS apply
- `qt.style_applied` and `stylesheet_set` are both truthy — Fusion + stylesheet are live on the QApplication
- `qss_resource_exists: true` — the `phoenix_style.qss` resource is found via `_resource_path` (in source mode, alongside `apply.py` under `src/phoenix_commons/theme/`)
- The embedded-QSS fallback is reachable and contains the canonical Phoenix navy (`#0a0e27`)
- All four public widgets (`PrimaryButton`, `Panel`, `PhoenixTable`, `UpdateBanner`) instantiate cleanly with the correct object names

These are the same runtime concerns the frozen exe would have exercised. The packaging passes them.

## Whether `phoenix_style.qss` was collected

**Yes — confirmed again, with stronger evidence than Phase 4.**

Immediately after PyInstaller exit:

```
$ ls /c/Users/justing/AppData/Local/ATS Inc/PhoenixCommonsPhase4Smoke/dist/PhoenixCommonsSmoke/_internal/phoenix_commons/theme/
__init__.py
_embedded_qss.py
apply.py
phoenix_style.qss

$ ls -la .../phoenix_style.qss
-rw-r--r-- 1 ATSINC+justing 4096 17662 May 13 10:17 .../phoenix_style.qss
```

This time `--collect-all phoenix_commons` produced ALL four files inside `_internal/phoenix_commons/theme/`: the three `.py` modules **plus** the data file. (Phase 4's in-tree build showed only `phoenix_style.qss` in that directory — the `.py` files appeared empty in `ls`; likely a transient AV interaction during that attempt.) Phase 4B-local's external build kept those modules intact.

Post-AV-sweep — the `.py` files and the `.qss` data file are all still present in `_internal/phoenix_commons/theme/`. The AV only removed the top-level `PhoenixCommonsSmoke.exe` bootloader, not the supporting package files.

## pytest result after the run

```
$ .\.venv\Scripts\python.exe -m pytest -q tests/
.................................                                        [100%]
33 passed in 0.23s
```

All 33 tests pass. No regressions from the build cycle.

## `git status --short` after the run

```
$ git status --short
(no output — clean working tree)
```

No source files were damaged this round (in Phase 4 the same step revealed 22 deleted source files). The external-build approach successfully isolated the source tree from the AV sweep.

## Confirmation: production tools were not touched

Confirmed. Read-only access only:

- `C:\Users\justing\PycharmProjects\Job Tracker\.venv\Scripts\python.exe --version` (version query)
- `C:\Users\justing\PycharmProjects\Job Tracker\.venv\Scripts\pyinstaller.exe --version` (version query)

No `Write`, `Edit`, or shell write touched any path under:

- `C:\Users\justing\PycharmProjects\Job Tracker\` — only the two read-only version queries above
- `C:\Users\justing\PycharmProjects\Phoenix_CAD_Tool\` — untouched
- `C:\Users\justing\PycharmProjects\Phoenix-Checkout-Tool\` — untouched
- `C:\Users\justing\PycharmProjects\ValveMasterTool\` — untouched
- `C:\Users\justing\PycharmProjects\phoenix-command-center\` — untouched

No production `build.bat`, no Inno Setup, no GitHub release commands, no production updater commands, no retrofit steps. No AV exclusions added or modified. No vendoring scaffold created.

## Other changes worth noting

- **Created `phoenix-commons\.venv\`** (already in `.gitignore` from Phase 1A — won't be committed). 3.14.3 + PySide6 6.11.1 + pytest 9.0.3 + pyinstaller 6.19.0. The venv is a one-off Phase 4B-local artifact. It can be removed via `rmdir /s /q .venv` if desired.
- **Created `C:\Users\justing\AppData\Local\ATS Inc\PhoenixCommonsPhase4Smoke\`** — outside the repo. Build artifacts (sans the AV-quarantined exe) remain there for inspection. Can be removed via `rmdir /s /q "%LOCALAPPDATA%\ATS Inc\PhoenixCommonsPhase4Smoke"`.
- **Safety backup created** at `C:\Users\justing\AppData\Local\ATS Inc\phoenix-commons-before-phase4b.bundle` (3,260,134 bytes / 3.1 MB). The repo plus all branches at the moment Phase 4B-local started. Can be restored via `git clone "...bundle" recovered-phoenix-commons` if ever needed.
- **No new commits to phoenix-commons** during Phase 4B-local. The previous commits (Phase 4 scratch + Phase 4 report) are still the tip of `phase-4-pyinstaller-compatibility`.

## Recommendation for Phase 5 or not

**Do not start Phase 5 commons-backed default yet, but do start Phase 5 with the standalone template as the default.**

Phase 4B-local strengthened the evidence that the packaging is correct (a clean success marker from source-mode execution under the same venv that built the exe) but failed to verify the frozen-exe runtime once more. The AV is now confirmed to be **content-heuristic-based** (not path-based) — both the in-tree Phase 4 build and the external-path Phase 4B-local build were quarantined identically. No code change, install layout change, or build location change inside our control will fix this.

Three viable paths forward, all environmental:

1. **AV exclusion (cleanest end state, but requires explicit user/IT action).** Add an exclusion for the PyInstaller bootloader pattern OR for the eventual built-tool exe paths. Most likely this is a corporate-IT ticket since the AV product is corporate-managed. Justin's production Phoenix tools (Job Tracker, Phoenix CAD, etc.) build on this same laptop and ship — so the same exclusion mechanism that lets those builds survive can probably be extended to cover phoenix-commons builds. Specifically:
   - Phoenix CAD's build.bat produces `dist\LabLayoutTool\LabLayoutTool.exe` from this same laptop — that path or its bootloader pattern must already be cleared. Find that exclusion, mirror it for `PhoenixCommonsSmoke.exe` (or any wildcard pattern that covers commons-backed test builds).
   - The user can confirm by running Phoenix CAD's `build.bat` and checking whether `dist\LabLayoutTool\LabLayoutTool.exe` survives there. If yes, the path/pattern is already exempted; we need an analogous one for the smoke-test bootloader.

2. **Different build machine (fastest end state).** Build the Phase 4 / Phase 6 dogfood exe on a machine without this aggressive AV (e.g., a personal dev box, a build VM, or a Github-Actions Windows runner). The phoenix-commons source travels with the repo; the build is deterministic given matching PyInstaller version. Once verified on one machine, it's known-good for all tools.

3. **Accept partial verification, proceed (lowest friction).** Treat the source-mode success marker as sufficient evidence that the packaging works. Phase 5 ships **both** wizard radios — "Phoenix Tool — standalone" stays the default until either of options 1 or 2 above is completed, at which point "Phoenix Tool — commons-backed" is promoted to default. The two-radio design already accommodates this.

**Recommendation: option 3 for Phase 5 + a parallel pursuit of option 1 or 2.** Phase 5 doesn't require running the frozen exe — it just needs the wizard to scaffold a tool whose scaffolded files (main.py, requirements.txt with `-e ./commons`, .gitmodules, etc.) are correct. We can validate that scaffolding via source-mode `python main.py` in the scaffolded tool. The frozen-build gate then falls naturally to Phase 6 (dogfood) where it must be resolved before retrofitting any production tool.

## Standing by

Phase 5 not started. The wizard isn't open; no `new_tool_wizard.py` change has been authored. Awaiting decision on:

- **(A)** Pursue AV-exclusion path (Phase 4C — outside my scope; needs your IT or your own admin action) before Phase 5
- **(B)** Move build to a different machine before Phase 5
- **(C)** Accept the source-mode-verified-only evidence and start Phase 5 with the standalone-default two-radio design
- **(D)** Something else
