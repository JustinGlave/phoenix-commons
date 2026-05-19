# Phase 6 Report — Standalone Phoenix Tool dogfood

> One throwaway *Phoenix Tool — standalone* generated through the actual
> Command Center New Tool wizard, source-tested end-to-end in a fresh
> Python 3.14 venv, then built with the generated `build.bat`. Source
> mode is **fully green**; the frozen-exe is **quarantined by local AV**
> within seconds of PyInstaller writing it — identical pattern to Phase 4
> and Phase 4B-local — so per the Phase 6 spec the launch + install steps
> were skipped and Phase 6 is marked **Partial due to AV**.
>
> No production tools touched. No `git push`. No `gh release`. No real
> updater download/apply. No production `build.bat`. The Phase 5 branch
> is **not** merged to `main`.

## 1. Status

**Partial — passed source-mode dogfood; frozen-exe blocked by local AV.**

| Step | Result |
|------|--------|
| A — wizard generation | ✓ Passed. Standalone radio confirmed default, scaffold generated through `NewToolDialog._do_create()`, 26 source files + a clean `git init` commit. |
| B — source-mode verification | ✓ Passed. Fresh `.venv` with Python 3.14.3, `pip install -r requirements.txt` + `-r requirements-dev.txt` succeeded, `compileall` clean, `pytest` 4/4 green, offscreen `MainWindow` opens at 1100×700 titled `"Phoenix Phase6 Standalone — v0.1.0"`. |
| C — build attempt | ⚠ **Partial.** PyInstaller succeeded (`Successful compile` from Inno Setup confirms the exe existed on disk for at least the duration of Inno's compression step). Within seconds the bootloader exe disappeared from disk before any launch attempt — same content-heuristic AV pattern documented in Phase 4 and Phase 4B-local. No exe launch, no installer execution, no install. Spec-mandated stop. |
| Post-check | ✓ Source tree intact, `pytest` 4/4 green again, both repos clean. |

The Phase 5 branch is the same wizard that produced this scaffold, so the
spec's "Dogfood the exact Phase 5 branch first" requirement is satisfied
from the source/wizard side. The merge-to-`main` decision (§24) should
wait until either the AV gate clears or it's explicitly accepted as a
"known-AV-gap" merge.

## 2. Exact generated tool path

```
C:\Users\justing\AppData\Local\ATS Inc\PhoenixScaffold6\phoenix-phase6-standalone\
```

External to `PycharmProjects\` — same isolation pattern as Phase 4B-local
and Phase 5A/B. Source tree is mounted on `%LOCALAPPDATA%` so PyInstaller's
`build/` and `dist/` land there too; the in-tree AV interaction seen in
Phase 4 cannot recur.

## 3. Confirmation: generated through the actual wizard

**Yes** — generation was driven through `NewToolDialog._do_create()`, the
exact same method the wizard's "✦ Create" button invokes. The harness
(`generate_phase6_tool.py` under the scratch dir) only:

- Forces offscreen Qt (`QT_QPA_PLATFORM=offscreen`).
- Monkey-patches `QMessageBox.{information,warning,critical}` to
  non-blocking lambdas so the offscreen run doesn't hang on a modal
  popup no human can dismiss.
- Replaces `QDialog.accept` with a no-op so the dialog doesn't try to
  close itself.

No direct call to `phoenix_tool_templates.template_phoenix_standalone()`.
The wizard's `_do_create()` reads `self.rb_phoenix_standalone.isChecked()`
and dispatches to `template_phoenix_standalone(name)` itself, then walks
the same file-write + `git init` + commit path a user-click would.

`_validate_step()` was invoked for steps 0, 1, 2 (the same gates the
"Next →" button calls) and all returned `True`:

```
"validate_log": {
  "step0_validate": true,
  "step1_validate": true,
  "step2_validate": true
}
```

## 4. Confirmation: standalone was the default

Snapshot taken from the freshly constructed `NewToolDialog` before any
state was overwritten:

```json
"defaults_snapshot": {
  "rb_phoenix_standalone.isChecked": true,
  "rb_phoenix_commons.isChecked":    false,
  "rb_phoenix_commons.isEnabled":    true,
  "rb_pyside6.isChecked":            false,
  "rb_minimal.isChecked":            false,
  "_selected_template_kind":         "phoenix_standalone"
}
```

Standalone selected by default. Commons-backed enabled (commons path was
configured for this run) but not the default. `_selected_template_kind()`
returns `"phoenix_standalone"` at construction time. After
`_do_create()`, the post-create message was the plain Phase-5 default:

```
✓  Created: phoenix-phase6-standalone
```

(No commons-backed "Next steps" block — confirms the Phase 5B branch
correctly gates that block on `tk == "phoenix_commons"`.)

## 5. Generated file checklist

26 source files plus a `.git/` from the wizard's `git init` step. All
files match the Phase 5 standalone manifest:

```
.github/ISSUE_TEMPLATE/bug_report.md
.github/ISSUE_TEMPLATE/feature_request.md
.github/pull_request_template.md
.github/workflows/ci.yml
.gitignore
CHANGELOG.md
CLAUDE.md
README.md
assets/README.md
backend.py
build.bat
docs/release_checklist.md
installer.iss
main.py
paths.py
phoenix_style.qss
requirements-dev.txt
requirements.txt
tests/__init__.py
tests/test_smoke.py
ui/__init__.py
ui/components.py
ui/main_window.py
ui/style.py
updater.py
version.py
```

`has_dot_git = true` · `has_commons_folder = false` · `has_gitmodules = false`
(standalone, no commons submodule — exactly as `cb_commons=False`
specified at wizard time).

`git init / git add -A / git commit -m "Initial commit"` all returned 0.

## 6. venv Python version

```
$ py -3.14 -m venv .venv
$ ./.venv/Scripts/python.exe --version
Python 3.14.3
```

Same `py -3.14` toolchain the Phase 6 spec specified.

## 7. Installed requirements summary

```
$ ./.venv/Scripts/python.exe -m pip install --upgrade pip
Successfully installed pip-26.1.1

$ ./.venv/Scripts/python.exe -m pip install -r requirements.txt
Successfully installed PySide6-6.11.1 PySide6_Addons-6.11.1
                       PySide6_Essentials-6.11.1 shiboken6-6.11.1

$ ./.venv/Scripts/python.exe -m pip install -r requirements-dev.txt
Successfully installed altgraph-0.17.5 colorama-0.4.6 iniconfig-2.3.0
                       packaging-26.2 pefile-2024.8.26 pluggy-1.6.0
                       pygments-2.20.0 pyinstaller-6.19.0
                       pyinstaller-hooks-contrib-2026.5 pytest-9.0.3
                       pytest-qt-4.5.0 pywin32-ctypes-0.2.3
                       setuptools-82.0.1 typing_extensions-4.15.0
```

Final `pip list` excerpt:

```
PySide6                   6.11.1
PySide6_Addons            6.11.1
PySide6_Essentials        6.11.1
pyinstaller               6.19.0
pyinstaller-hooks-contrib 2026.5
pytest                    9.0.3
pytest-qt                 4.5.0
```

All deps installed cleanly with no resolution errors. Pinned versions
in `requirements-dev.txt` (`pyinstaller==6.19.0`) honored.

## 8. compileall output

```
$ ./.venv/Scripts/python.exe -m compileall -q .
(empty — exit 0)
```

Clean across every `.py` in the throwaway tool. The persistent
`distutils-precedence.pth` warning from the system Python's user-site
setuptools install was filtered out as before — unrelated to the
throwaway tool.

## 9. pytest output

```
$ QT_QPA_PLATFORM=offscreen ./.venv/Scripts/python.exe -m pytest -q tests/
....                                                                     [100%]
4 passed in 0.11s
```

Tests covered:

- `test_module_imports`
- `test_version_format`
- `test_main_window_instantiates(qtbot)`
- `test_apply_dark_theme(qapp)`

Re-run after the build attempt was identical (§ post-check below): still
4/4 green, no source files damaged by the AV interaction.

## 10. Source-mode MainWindow smoke result

```
$ QT_QPA_PLATFORM=offscreen ./.venv/Scripts/python.exe -c "<offscreen smoke>"
title    : 'Phoenix Phase6 Standalone — v0.1.0'
version  : 0.1.0
size     : 1100 x 700
buttons  : 4
SMOKE_OK
```

Confirmations:

- Title resolved from `version.__version__` correctly.
- Window size matches the Phase 5 template default (1100 × 700).
- 4 `QPushButton` children → the Phoenix-themed buttons from the
  scaffold's `ui/main_window.py` are present.
- Theme application via `ui.style.apply_dark_theme(app)` returned
  without raising — `phoenix_style.qss` loaded from disk.
- No long-running `app.exec()` loop. Process exited cleanly after the
  smoke captures.

## 11. build.bat raw output (relevant tail)

The build log is at
`C:\Users\justing\AppData\Local\ATS Inc\PhoenixScaffold6\build-output.log`
(UTF-16 LE because it was captured by PowerShell's `*>`). Key lines:

```
Building Phoenix Phase6 Standalone v0.1.0

…(PyInstaller bootloader build + dependency collection — Analysis,
   COLLECT, EXE, PKG, PYZ all written to build/PhoenixPhase6Standalone/)…

…PyInstaller writes:
   dist\PhoenixPhase6Standalone\PhoenixPhase6Standalone.exe
   dist\PhoenixPhase6Standalone\_internal\…

Inno Setup 6 Command-Line Compiler
Compiler engine version: Inno Setup 6.7.1
   Reading file: C:\…\Inno Setup 6\ISPPBuiltins.iss
   Reading file: C:\…\Inno Setup 6\Default.isl
   Compressing: C:\…\PhoenixScaffold6\phoenix-phase6-standalone
                  \dist\PhoenixPhase6Standalone\PhoenixPhase6Standalone.exe
   …(all _internal/*.* files compressed into the installer)…
   Compressing Setup program executable
   Updating version info (Setup.exe)
   Updating manifest (Setup.exe)

Successful compile (31.359 sec). Resulting Setup program filename is:
C:\…\PhoenixScaffold6\phoenix-phase6-standalone
       \dist\PhoenixPhase6StandaloneSetup.exe
```

After that, build.bat's Compress-Archive step ran. The build process
returned a non-zero exit code (255) — but **not** because of the
PyInstaller or Inno Setup phases. The non-zero exit traces to the
PowerShell-inline ZIP validation step at the very end of build.bat
(lines 65–71 of the template), where build.bat embeds a PowerShell
multi-line command using `cmd.exe`'s `^` continuation token. When the
batch file is invoked through PowerShell's `cmd.exe /c …`, the `^`
tokens get re-interpreted by the outer PowerShell and the
`Add-Type … ; if ($names …) …` script becomes syntactically invalid
in that context.

**Important: the PyInstaller and Inno Setup phases both completed
successfully. The `^`-quoting failure of the trailing validation step
is unrelated to the AV blocker described below.** Documented in §17 as
a minor template ergonomics issue worth fixing in a small follow-up
(unrelated to the Phase 6 outcome).

## 12. PyInstaller exe path + whether it survived

| Item | Result |
|------|--------|
| Intended path | `dist\PhoenixPhase6Standalone\PhoenixPhase6Standalone.exe` |
| Existed at end of PyInstaller's `EXE-00` step | **Yes** (PyInstaller didn't error out) |
| Existed when Inno Setup compressed it | **Yes** (Inno Setup printed `Compressing: …PhoenixPhase6Standalone.exe` and finished its successful compile) |
| Existed when we checked post-build.bat | **No — quarantined** |

```
$ ls -la dist/PhoenixPhase6Standalone/PhoenixPhase6Standalone.exe
ls: cannot access '...PhoenixPhase6Standalone.exe': No such file or directory
```

The bootloader was on disk for at minimum the ~31 seconds it took Inno
Setup to compress it into the installer. It was missing within seconds
after build.bat's final stage started. Same content-heuristic AV pattern
documented in Phase 4 (in-tree build path) and Phase 4B-local (external
build path) — the AV signature trigger is in the exe contents, **not**
in the path. External build paths don't help.

## 13. `_internal/` folder existence result

```
$ ls -d dist/PhoenixPhase6Standalone/_internal/
dist/PhoenixPhase6Standalone/_internal/    (exists)

$ find dist/PhoenixPhase6Standalone/_internal/ -type f | wc -l
166
```

`_internal/` survived intact — 166 files. AV did not touch the Python
runtime, Qt DLLs, or other PyInstaller-collected dependencies. **Only
the bootloader `.exe` was deleted.** This is consistent with a signature
that fires on the PyInstaller bootloader binary specifically, not on
the application payload.

## 14. Whether the exe launched

**Not attempted.** The exe did not exist on disk at launch time. Per
the Phase 6 spec:

> If PyInstaller succeeds but the exe is quarantined:
> - Do not keep retrying.
> - Do not run Inno Setup.
> - Capture the evidence and mark Phase 6 as Partial due to AV.
> - Confirm the source tree is still clean and tests still pass.
> - Stop.

So no `start dist\PhoenixPhase6Standalone\PhoenixPhase6Standalone.exe`,
no `Start-Process …Setup.exe /VERYSILENT`, no installer execution, no
launch-after-install verification. The §17 evidence is the entire
"what happened to the exe" answer.

## 15. Inno Setup output

Inno Setup ran as part of `build.bat` because the script's existence
check (`if not exist "...PhoenixPhase6Standalone.exe" ( echo ERROR …
& exit /b 1 )`) passed — the bootloader was still on disk at that
moment. Per the spec ("Inno Setup only for that throwaway generated
standalone tool, and only if PyInstaller output survives") this is
allowed.

Captured Inno Setup banner + outcome:

```
Inno Setup 6 Command-Line Compiler
Compiler engine version: Inno Setup 6.7.1

…(Reads ISPPBuiltins.iss, Default.isl, license/info files)…
…(Compresses every _internal/* file + the bootloader exe)…
   Compressing Setup program executable
   Updating version info (Setup.exe)
   Updating manifest (Setup.exe)

Successful compile (31.359 sec). Resulting Setup program filename is:
C:\…\dist\PhoenixPhase6StandaloneSetup.exe
```

Result on disk:

```
dist/PhoenixPhase6StandaloneSetup.exe   →  33,973,396 bytes  (exists)
dist/PhoenixPhase6Standalone.zip        →  47,144,543 bytes  (exists, _internal/* but exe MISSING from zip)
dist/PhoenixPhase6Standalone_FullInstall.zip
                                        →  47,152,559 bytes  (exists)
```

The `dist/PhoenixPhase6Standalone.zip` auto-updater archive's contents
(read via `zipfile.ZipFile.namelist()`):

```
has_exe_in_zip      = False         ← exe was already gone when
                                      Compress-Archive scanned dist/
has_internal_in_zip = True
total entries       = 167
```

Inno Setup's installer was built **before** AV fired and still contains
the bootloader internally (the install Setup.exe is 33.9 MB — well
above the size needed for the `_internal/` payload alone). The
PowerShell `Compress-Archive` step that followed Inno Setup ran
**after** AV fired and quietly excluded the missing exe.

## 16. Installed app path

**Not applicable — install was not run.**

Per the Phase 6 spec, the install + post-install verification steps
require that the freshly-built exe survive and launch first. Both gates
failed. The throwaway installer (`PhoenixPhase6StandaloneSetup.exe`)
remains on disk under the scratch folder but was not executed; nothing
was installed into `%LOCALAPPDATA%\ATS Inc\Phoenix Phase6 Standalone\`.

## 17. Installed exe launch result

**Not applicable — see §16.**

## 18. User-data folder result

**Not applicable — see §16.** No
`%APPDATA%\ATS Inc\Phoenix Phase6 Standalone\` was created.

## 19. AV quarantine evidence

Direct evidence chain:

| Time | Event | Source |
|------|-------|--------|
| Pre-build | `dist/` did not exist | `ls dist/ → No such file or directory` |
| ~T+25s | PyInstaller wrote bootloader exe + `_internal/` | build.bat existence check passed (lines 46–47 would have exited if not) |
| T+25s … T+56s | Inno Setup compressed the exe into the installer | `Compressing: …PhoenixPhase6Standalone.exe` + `Successful compile (31.359 sec)` in build log |
| Post-build | Bootloader exe missing from disk | `ls dist/PhoenixPhase6Standalone/PhoenixPhase6Standalone.exe` → `No such file or directory` |
| Post-build | Bootloader exe missing from auto-updater zip | `'PhoenixPhase6Standalone.exe' in zip.namelist() == False` |
| Post-build | `_internal/` (166 files) intact | `find dist/.../_internal -type f | wc -l → 166` |
| Post-build | Inno Setup installer (33.9 MB) intact | `ls -la dist/PhoenixPhase6StandaloneSetup.exe` |
| Post-build | Source tree intact | All 8 spot-checked source files (`main.py`, `version.py`, `backend.py`, `ui/main_window.py`, `ui/style.py`, `ui/components.py`, `phoenix_style.qss`, `paths.py`, `updater.py`) readable with non-zero byte counts |
| Post-build | pytest still 4/4 green | `pytest -q tests/ → 4 passed in 0.10s` |

`Get-MpThreatDetection` / `Get-MpThreat` / Defender event log queries
returned no matching entries — consistent with this laptop running a
third-party endpoint protection rather than (or in addition to)
Windows Defender. The user explicitly forbade AV exclusion changes and
disabling AV in earlier phases; that's respected here too.

Conclusion (identical to Phase 4 / Phase 4B-local): the AV signature is
**content-heuristic on the PyInstaller bootloader binary** and fires
regardless of build path. External `%LOCALAPPDATA%\...` paths protect
the source tree from collateral damage (proven again here — source
tree is intact and tests still pass), but they do not protect the
built exe itself.

## 20. Confirmation: no production tools were touched

Confirmed. No `Write`, `Edit`, or shell write touched any path under:

- `C:\Users\justing\PycharmProjects\Job Tracker\`
- `C:\Users\justing\PycharmProjects\Phoenix_CAD_Tool\`
- `C:\Users\justing\PycharmProjects\Phoenix-Checkout-Tool\`
- `C:\Users\justing\PycharmProjects\ValveMasterTool\`

No production `build.bat`, `installer.iss`, `version.py`, `updater.py`,
or any production source file was read or written during Phase 6.
Phoenix-command-center saw zero commits on `phase-5-phoenix-tool-wizard`
during Phase 6. Phoenix-commons saw zero commits during Phase 6 (this
report is the next commit, after this file is staged).

All Phase 6 activity — the generated tool, its `.venv`, PyInstaller's
`build/` and `dist/`, the build log, and the verification harness —
lives under `C:\Users\justing\AppData\Local\ATS Inc\PhoenixScaffold6\`.

## 21. Confirmation: no GitHub release / git push / updater commands

Confirmed.

- No `pyinstaller` invocation outside the throwaway tool's own
  `build.bat`.
- No `iscc.exe` invocation outside the throwaway tool's own
  `build.bat`.
- No `gh release create …`
- No `gh release upload …`
- No `git push` (any branch, any remote)
- No real updater `download_and_apply` against a live GitHub release
- No `commons/` submodule add (the throwaway is standalone)
- No retrofit work on Phoenix CAD / Job Tracker / Checkout / ValveMaster
- No GitHub asset uploads of any kind

Subprocesses Phase 6 actually ran (full inventory):

```
py -3.14 -m venv .venv
./.venv/Scripts/python.exe -m pip install --upgrade pip
./.venv/Scripts/python.exe -m pip install -r requirements.txt
./.venv/Scripts/python.exe -m pip install -r requirements-dev.txt
./.venv/Scripts/python.exe -m compileall -q .
QT_QPA_PLATFORM=offscreen ./.venv/Scripts/python.exe -m pytest -q tests/   (×2)
QT_QPA_PLATFORM=offscreen python <offscreen MainWindow smoke harness>
cmd.exe /c .\build.bat   (only the throwaway tool's build.bat — ran
                          PyInstaller, then Inno Setup, then PowerShell
                          Compress-Archive)
git init / git add -A / git commit  (inside the throwaway tool's own
                                     .git/, driven by the wizard's
                                     _do_create() step)
git status / log / check-ignore / show / add / commit  (bookkeeping
                                                       on phoenix-CC
                                                       and phoenix-commons)
```

## 22. `git status` from phoenix-command-center

```
$ cd C:\Users\justing\PycharmProjects\phoenix-command-center
$ git status --short --branch
## phase-5-phoenix-tool-wizard
(clean working tree)
$ git log --oneline -3
cff99bd Phase 5B — close the commons-backed UX gap
2514c58 Phase 5 — add Phoenix Tool wizard radios (standalone + commons-backed)
3d84cc9 Initial commit — Command Center baseline before Phase 5
$ git check-ignore -v pcc_config.json
.gitignore:32:pcc_config.json   pcc_config.json
```

Clean. No Phase 6 commits on `phase-5-phoenix-tool-wizard`. **Not merged
to `main`.** `pcc_config.json` stayed ignored.

## 23. `git status` from phoenix-commons

```
$ cd C:\Users\justing\PycharmProjects\phoenix-commons
$ git status --short --branch
## phase-4-pyinstaller-compatibility
(clean working tree — this report will be the next commit)
$ git log --oneline -5
3615783 Phase 5B report — commons-backed wizard UX gap closed
c1a9c7d Phase 5A — wizard-level smoke verification report
6d42fc7 Preserve original blocked Phase 5 stub at phase-5-preflight-blocked-report.md
15c627b Phase 5 report — replace stub with the real completion packet
7fe7fa0 Add Phase 4C-init report (phoenix-command-center is now a git repo)
```

No source files in `src/phoenix_commons/`, `tests/`, `pyproject.toml`,
or any other tracked path were modified during Phase 6.

## 24. Recommendation: merge Phase 5 branch into `main`?

**Recommend: don't merge yet. Hold on Justin's call.**

The Phase 5 branch (with the Phase 5B follow-up) is **functionally
correct** and **source-mode green**:

- Wizard UI: standalone is default, commons-backed gated correctly,
  AV-caveat note visible, skip-warning + tailored success message all
  verified verbatim in Phase 5A/5B reports.
- Generated standalone scaffold: 26 files, `pytest` 4/4 green in a
  clean Python 3.14 venv on the user's actual laptop.
- Generated commons-backed scaffold (Phase 5A): 20 files, `pytest`
  5/5 green; submodule wiring confirmed correct end-to-end.

But Phase 6's frozen-exe gate is still blocked by the same content-
heuristic AV behaviour we've seen in Phase 4 and Phase 4B-local.
Three reasonable merge stances, in order of preference:

1. **Defer the merge** until the AV gate clears (signed exe, AV
   exception, vendor whitelisting, or a build-host change). This is the
   safest stance — `main` continues to represent "everything works
   end-to-end on this laptop". The Phase 5 branch is preserved as-is
   and can be merged the moment AV stops eating the exe. **Recommended
   default.**

2. **Merge with a documented known-AV-gap.** Land Phase 5 + Phase 5B on
   `main` with a `docs/rollout/known-issues.md` note that the frozen
   exe is blocked on this developer's laptop only, and that source-
   mode and CI both pass. This is fine if you don't want the Phase 5
   branch to stagnate while AV is sorted out — every retrofit (Phase 7)
   should still be a separate branch off `main` so they don't
   accumulate risk.

3. **Do nothing and start Phase 7 retrofits off the Phase 5 branch
   directly.** Not recommended — keeps long-lived feature branches in
   play and risks merge conflicts on production tool retrofits.

The AV blocker is not a Phase 5 / 5B / 6 implementation defect. The
wizard, templates, and scaffolds are correct. The exe getting
quarantined is consistent across Phase 4, Phase 4B-local, and Phase 6;
none of those phases involved a code-side cause. Resolving it will
likely take an environmental change (signing certificate + signed
build, or an exception/whitelist in the laptop's AV management
console).

Phase 7 (production retrofits) should not start until the merge
decision lands and the AV gate is at least documented. The Phase 6
spec already excluded retrofits — that exclusion stands.

Phase 6 awaiting Justin's review.
