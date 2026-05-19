# Phase 6A Report — build.bat ZIP-validator fragility fix

> Phase 6 discovered that the standalone template's `build.bat` ended
> with a multi-line PowerShell `Add-Type … ; if … exit 2 …` block that
> used cmd.exe's `^` continuation token. When `build.bat` is invoked
> through a PowerShell wrapper (e.g. when an outer driver runs
> `& cmd.exe /c "build.bat"`), the outer shell re-interprets the
> carets and the inner script becomes a syntax error. The PyInstaller
> + Inno Setup phases ran cleanly; only this validator step failed.
>
> Phase 6A moves that validation out of inline PowerShell and into a
> small Python helper bundled with every generated Phoenix tool.
> Source-mode only — no PyInstaller, no Inno Setup, no `build.bat`,
> no release commands, no production-tool changes. Phase 5 branch
> remains unmerged.

## 1. Status

**Passed.**

- Generator templates updated in `phoenix_tool_templates.py` (one
  commit, `978f457`, +232 / −8).
- A fresh scaffold generated through the actual `NewToolDialog._do_create()`
  contains `scripts/validate_release_zip.py` and a `build.bat` that
  invokes it via the venv Python.
- `python -m compileall -q .` clean on Command Center **and** the
  generated scaffold.
- `pytest -q tests/` on the scaffold: **7/7 green** (4 existing smoke
  tests + 3 new validator tests).
- Direct CLI tests of the helper against fake zips return the exact
  spec exit codes (0 / 2 / 3 / 4) for every scenario.
- `build.bat` was **not executed** during Phase 6A. No PyInstaller,
  no Inno Setup, no release / push / updater / retrofit commands.

## 2. Files changed in phoenix-command-center

| Path | Status | Purpose |
|------|--------|---------|
| `phoenix_tool_templates.py` | MODIFIED (+232 / −8) | Adds `VALIDATE_RELEASE_ZIP_PY` constant (helper script body), replaces the fragile multi-line PowerShell tail of `BUILD_BAT` with a one-line `.venv\Scripts\python scripts\validate_release_zip.py …` call, registers `scripts/validate_release_zip.py` in `_shared_files()` so both standalone and commons-backed scaffolds ship the helper, and appends three new pytest cases (happy path / missing exe / missing `_internal/`) to both `TEST_SMOKE_PY_STANDALONE` and `TEST_SMOKE_PY_COMMONS`. |

`new_tool_wizard.py` was **not** touched — the wizard's UI behavior
from Phase 5 / 5B is unchanged. Only the templates emitted by the
wizard's `_do_create()` change.

## 3. `git status --short --branch` from phoenix-command-center

```
$ git status --short --branch
## phase-5-phoenix-tool-wizard
(clean working tree)
```

## 4. `git diff --stat` from phoenix-command-center

```
$ git diff --stat 2514c58..phase-5-phoenix-tool-wizard
 new_tool_wizard.py        |  228 ++++--
 phoenix_tool_templates.py | 1973 +++++++++++++++++++++++++++++++++++++++++++++
 2 files changed, 2179 insertions(+), 22 deletions(-)
```

Phase 6A commit-only diff:

```
$ git diff --stat cff99bd..978f457
 phoenix_tool_templates.py | 240 ++++++++++++++++++++++++++++++++++++++++++++--
 1 file changed, 232 insertions(+), 8 deletions(-)
```

Branch log:

```
$ git log --oneline main..phase-5-phoenix-tool-wizard
978f457 Phase 6A — move release-zip validation out of fragile inline PowerShell
cff99bd Phase 5B — close the commons-backed UX gap
2514c58 Phase 5 — add Phoenix Tool wizard radios (standalone + commons-backed)
```

## 5. Relevant changed-file contents

### 5.1 New constant `VALIDATE_RELEASE_ZIP_PY` (helper script body)

```python
"""Validate a Phoenix Tool release zip produced by build.bat.

Usage:
    python scripts/validate_release_zip.py \\
        --zip dist/<ExeStem>.zip \\
        --exe <ExeName> \\
        [--require-internal]

Exit codes:
    0   zip is well-formed (exe at root; _internal/ present if required)
    2   zip path missing or unreadable
    3   exe missing from zip root
    4   _internal/ missing and --require-internal was passed
"""
from __future__ import annotations

import argparse
import sys
import zipfile
from pathlib import Path


def validate(
    zip_path: Path,
    exe_name: str,
    *,
    require_internal: bool = False,
) -> tuple[int, str]:
    """Inspect zip_path. Returns (exit_code, message)."""
    if not zip_path.exists():
        return 2, f"zip not found: {zip_path}"
    try:
        with zipfile.ZipFile(zip_path) as zf:
            names = [n.replace("\\", "/") for n in zf.namelist()]
    except zipfile.BadZipFile as exc:
        return 2, f"zip is unreadable: {exc}"

    if exe_name not in names:
        return 3, f"missing {exe_name} at zip root"

    if require_internal:
        has_internal = any(n.startswith("_internal/") for n in names)
        if not has_internal:
            return 4, "missing _internal/ entries"

    return 0, (
        f"zip OK: {len(names)} entries, "
        f"{exe_name} present"
        + (", _internal/ present" if require_internal else "")
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Validate a Phoenix Tool release zip."
    )
    parser.add_argument("--zip", required=True,
                        help="Path to the zip to validate.")
    parser.add_argument("--exe", required=True,
                        help="Exe filename expected at the zip root.")
    parser.add_argument("--require-internal", action="store_true",
                        help="Also require an _internal/ folder.")
    args = parser.parse_args(argv)

    code, msg = validate(
        Path(args.zip), args.exe,
        require_internal=args.require_internal,
    )
    if code == 0:
        print(msg)
    else:
        print(f"ERROR: {msg}", file=sys.stderr)
    return code


if __name__ == "__main__":
    raise SystemExit(main())
```

### 5.2 `BUILD_BAT` change (the actual fix)

Before (lines 1161–1168 of the previous `phoenix_tool_templates.py` —
the fragile block):

```bat
rem Verify auto-updater zip contains _internal/ + exe
powershell -NoProfile -ExecutionPolicy Bypass -Command ^
  "$z='dist\__EXE_STEM__.zip'; Add-Type -AssemblyName System.IO.Compression.FileSystem; ^
   $zip=[System.IO.Compression.ZipFile]::OpenRead($z); try { ^
     $names=$zip.Entries.FullName | ForEach-Object { $_ -replace '\\','/' }; ^
     if ($names -notcontains '__EXE_NAME__') { exit 2 }; ^
     if (-not ($names | Where-Object { $_ -like '_internal/*' })) { exit 3 } ^
   } finally { $zip.Dispose() }"
if errorlevel 1 ( echo ERROR: zip missing required entries. & exit /b 1 )
```

After:

```bat
rem Verify auto-updater zip contains _internal/ + exe (Phase 6A: moved
rem out of fragile inline PowerShell into scripts/validate_release_zip.py
rem so cmd.exe ^ continuation can't be re-interpreted by an outer shell).
.venv\Scripts\python scripts\validate_release_zip.py --zip dist\__EXE_STEM__.zip --exe __EXE_NAME__ --require-internal
if errorlevel 1 ( echo ERROR: zip missing required entries. & exit /b 1 )
```

Single line, no carets inside any quoted PowerShell payload. The
`errorlevel` propagation is preserved — if the helper exits non-zero,
build.bat still prints `ERROR: zip missing required entries.` and
bails with `exit /b 1`.

### 5.3 `_shared_files()` change

```python
"build.bat": _substitute(BUILD_BAT, **tokens),
"installer.iss": _substitute(INSTALLER_ISS, **tokens),
# Phase 6A: helper script that replaces the fragile inline-PowerShell
# ZIP-validation step that used to live at the tail of build.bat.
# Shared by both standalone and commons-backed because they share
# the same build.bat.
"scripts/validate_release_zip.py": VALIDATE_RELEASE_ZIP_PY,
".github/workflows/ci.yml": CI_YML,
```

The helper is registered in `_shared_files()` rather than only in
`template_phoenix_standalone()` because both variants share `build.bat`
verbatim — they need the helper or `build.bat` would break for commons-
backed too. The user's scope explicitly allowed this:
*"Do not change commons-backed behavior unless the same build.bat
template text is shared and must be kept consistent."* `build.bat` is
shared.

### 5.4 New pytest cases in both smoke-test templates

Identical text appended to `TEST_SMOKE_PY_STANDALONE` and
`TEST_SMOKE_PY_COMMONS`:

```python
# ── Phase 6A: scripts/validate_release_zip.py helper coverage ──────────

def _run_validator(tmp_path, names, *, require_internal, exe="__EXE_NAME__"):
    """Build a fake zip with the given member names and invoke the helper
    via subprocess (same surface build.bat uses)."""
    import subprocess
    import sys
    import zipfile

    zip_path = tmp_path / "fake.zip"
    with zipfile.ZipFile(zip_path, "w") as zf:
        for n in names:
            zf.writestr(n, b"x")

    script = (
        __import__("pathlib").Path(__file__).resolve().parent.parent
        / "scripts" / "validate_release_zip.py"
    )
    cmd = [sys.executable, str(script), "--zip", str(zip_path), "--exe", exe]
    if require_internal:
        cmd.append("--require-internal")
    return subprocess.run(cmd, capture_output=True, text=True)


def test_validate_release_zip_happy_path(tmp_path) -> None:
    out = _run_validator(
        tmp_path,
        ["__EXE_NAME__", "_internal/dummy.txt"],
        require_internal=True,
    )
    assert out.returncode == 0, out.stderr
    assert "OK" in out.stdout


def test_validate_release_zip_missing_exe(tmp_path) -> None:
    out = _run_validator(
        tmp_path,
        ["_internal/dummy.txt"],
        require_internal=True,
    )
    assert out.returncode != 0
    assert "missing" in out.stderr.lower()


def test_validate_release_zip_missing_internal_when_required(tmp_path) -> None:
    out = _run_validator(
        tmp_path,
        ["__EXE_NAME__", "README.md"],
        require_internal=True,
    )
    assert out.returncode != 0
    assert "_internal" in out.stderr
```

`__EXE_NAME__` is substituted to the concrete exe filename (e.g.
`PhoenixPhase6aStandalone.exe`) by `_substitute` at scaffold time.

## 6. Exact commands run

### 6.1 Pre-flight

```
$ cd C:\Users\justing\PycharmProjects\phoenix-command-center
$ git status --short --branch    →  ## phase-5-phoenix-tool-wizard (clean)
$ git log --oneline -3
  cff99bd Phase 5B — close the commons-backed UX gap
  2514c58 Phase 5 — add Phoenix Tool wizard radios (standalone + commons-backed)
  3d84cc9 Initial commit — Command Center baseline before Phase 5
$ git check-ignore -v pcc_config.json
  .gitignore:32:pcc_config.json   pcc_config.json

$ cd C:\Users\justing\PycharmProjects\phoenix-commons
$ git status --short --branch    →  ## phase-4-pyinstaller-compatibility (clean)
$ git log --oneline -3
  fc114c0 Phase 6 report — standalone dogfood, source-mode green, exe AV-blocked
  3615783 Phase 5B report — commons-backed wizard UX gap closed
  c1a9c7d Phase 5A — wizard-level smoke verification report
```

### 6.2 Implementation

```
(Edit)   phoenix_tool_templates.py
            - new VALIDATE_RELEASE_ZIP_PY constant
            - BUILD_BAT trailing PowerShell block → one-line helper call
            - _shared_files() registers scripts/validate_release_zip.py
            - TEST_SMOKE_PY_STANDALONE + TEST_SMOKE_PY_COMMONS extended
              with 3 new validator tests
```

### 6.3 Source-mode verification

```
$ cd C:\Users\justing\PycharmProjects\phoenix-command-center
$ python -m compileall -q .                            # exit 0
$ python -c "from new_tool_wizard import NewToolDialog; \
             from phoenix_tool_templates import \
                 template_phoenix_standalone, template_phoenix_commons; \
             …"                                          # OK

$ mkdir -p "C:\Users\justing\AppData\Local\ATS Inc\PhoenixScaffold6A"
$ QT_QPA_PLATFORM=offscreen python \
    "C:\Users\justing\AppData\Local\ATS Inc\PhoenixScaffold6A\verify_6a.py"

$ cd .../PhoenixScaffold6A/phoenix-phase6a-standalone
$ python -m compileall -q .                            # exit 0
$ QT_QPA_PLATFORM=offscreen python -m pytest -q tests/
.......                                                  [100%]
7 passed in 0.42s

$ python <direct CLI fake-zip test harness>             # see §7 / §12
```

### 6.4 Commit

```
$ git add phoenix_tool_templates.py
$ git commit -m "Phase 6A — move release-zip validation out of fragile inline PowerShell"
[phase-5-phoenix-tool-wizard 978f457] Phase 6A — move release-zip validation …
 1 file changed, 232 insertions(+), 8 deletions(-)
```

No `pyinstaller`, no `iscc.exe`, no `build.bat`, no `gh release`, no
`git push`, no submodule mutation, no production-tool reads or writes.

## 7. Raw verification output

### 7.1 Import + structure sanity

```
$ python -c "
from phoenix_tool_templates import template_phoenix_standalone, template_phoenix_commons
s = template_phoenix_standalone('phoenix-test-tool')
c = template_phoenix_commons('phoenix-test-tool')
print('standalone files:', len(s))
print('commons files:', len(c))
print('helper in standalone:', 'scripts/validate_release_zip.py' in s)
print('helper in commons:',    'scripts/validate_release_zip.py' in c)
print('build.bat calls helper:', r'scripts\\validate_release_zip.py' in s['build.bat'])
print('build.bat has inline ZipFile:', 'System.IO.Compression.ZipFile' in s['build.bat'])
"
standalone files: 27
commons files: 21
helper in standalone: True
helper in commons: True
build.bat calls helper: True
build.bat has inline ZipFile: False
```

### 7.2 Generated scaffold via wizard (see §8 / §10)

Stored at `…\PhoenixScaffold6A\verify-report.json`. Key fields:

```json
"defaults": {
  "rb_phoenix_standalone.isChecked": true,
  "rb_phoenix_commons.isChecked":    false,
  "_selected_template_kind":         "phoenix_standalone"
},
"file_count":                  27,
"helper_script_present":       true,
"helper_script_size_bytes":    2719,
"build_bat_calls_helper":      true,
"build_bat_has_inline_zipfile": false,
"build_bat_validator_lines": [
  "rem out of fragile inline PowerShell into scripts/validate_release_zip.py",
  ".venv\\Scripts\\python scripts\\validate_release_zip.py --zip dist\\PhoenixPhase6aStandalone.zip --exe PhoenixPhase6aStandalone.exe --require-internal"
]
```

### 7.3 Generated-scaffold pytest

```
$ QT_QPA_PLATFORM=offscreen python -m pytest -q tests/
.......                                                  [100%]
7 passed in 0.42s
```

Tests covered:

- `test_module_imports`
- `test_version_format`
- `test_apply_dark_theme` (qapp fixture)
- `test_main_window_instantiates` (qtbot fixture)
- **`test_validate_release_zip_happy_path`** *(new)*
- **`test_validate_release_zip_missing_exe`** *(new)*
- **`test_validate_release_zip_missing_internal_when_required`** *(new)*

### 7.4 Direct CLI fake-zip tests (see §12 for table)

```
$ python <harness using subprocess.run(...)>
1. happy path (exe + _internal):          exit=0
   stdout: 'zip OK: 2 entries, PhoenixPhase6aStandalone.exe present, _internal/ present'
2. missing exe:                            exit=3
   stderr: 'ERROR: missing PhoenixPhase6aStandalone.exe at zip root'
3. missing _internal (--require-internal): exit=4
   stderr: 'ERROR: missing _internal/ entries'
4. zip path missing:                       exit=2
   stderr: 'ERROR: zip not found: <tmp>\\gone.zip'
5. missing _internal (NOT required):       exit=0
   stdout: 'zip OK: 1 entries, PhoenixPhase6aStandalone.exe present'
```

All five exit codes match the spec docstring exactly.

## 8. Scratch scaffold path

```
C:\Users\justing\AppData\Local\ATS Inc\PhoenixScaffold6A\
    ├── phoenix-phase6a-standalone\         (the scaffold; 27 source files)
    ├── verify_6a.py                        (the harness)
    └── verify-report.json                  (machine-readable summary)
```

External to both `phoenix-command-center` and `phoenix-commons` — same
AV-isolation pattern as Phase 4B-local, 5A, 5B, 6.

## 9. Standalone-default confirmation

Snapshot taken at construction time, before any input was set:

```json
"defaults": {
  "rb_phoenix_standalone.isChecked": true,
  "rb_phoenix_commons.isChecked":    false,
  "_selected_template_kind":         "phoenix_standalone"
}
```

Standalone is still the default. Commons-backed is not. `_selected_template_kind()`
returns `"phoenix_standalone"` without any state being set by the harness.

## 10. `scripts/validate_release_zip.py` generated?

**Yes.**

```
phoenix-phase6a-standalone/scripts/validate_release_zip.py    →  2,719 bytes
```

Listed in the scaffold's full file manifest (27 files total — the
Phase 5 standalone count of 26 plus one new file for the helper).
The file is byte-identical to the `VALIDATE_RELEASE_ZIP_PY` constant
in `phoenix_tool_templates.py` (no token substitution required — the
helper is template-agnostic, so it ships verbatim).

`scripts/` is a new top-level subfolder in the generated layout. The
wizard's `_do_create()` creates intermediate folders for any path
component before writing (existing logic from Phase 5), so no wizard
change was needed.

## 11. `build.bat` no longer uses fragile inline PowerShell

**Confirmed.** Three independent checks:

1. **Generator output check** (§7.1):
   `'System.IO.Compression.ZipFile' in build_bat` → **False**.

2. **Generated scaffold file check** (§7.2):
   `build_bat_has_inline_zipfile: false` in `verify-report.json`.

3. **Manual line inspection** (§5.2):
   The only validator-related lines in the generated `build.bat` are:

   ```
   rem Verify auto-updater zip contains _internal/ + exe (Phase 6A: moved
   rem out of fragile inline PowerShell into scripts/validate_release_zip.py
   rem so cmd.exe ^ continuation can't be re-interpreted by an outer shell).
   .venv\Scripts\python scripts\validate_release_zip.py --zip dist\PhoenixPhase6aStandalone.zip --exe PhoenixPhase6aStandalone.exe --require-internal
   if errorlevel 1 ( echo ERROR: zip missing required entries. & exit /b 1 )
   ```

   No multi-line PowerShell, no `^` line-continuations inside any
   quoted PowerShell payload, no `Add-Type` / `OpenRead` / `Entries.FullName`.

## 12. Fake-zip validation test results

### 12.1 In-scaffold pytest (`pytest -q tests/` → 3 of the 7 passing)

| Test | Result |
|------|--------|
| `test_validate_release_zip_happy_path` | ✓ PASS (asserts exit 0 + "OK" in stdout) |
| `test_validate_release_zip_missing_exe` | ✓ PASS (asserts non-zero exit + "missing" in stderr) |
| `test_validate_release_zip_missing_internal_when_required` | ✓ PASS (asserts non-zero exit + "_internal" in stderr) |

### 12.2 Direct CLI invocations (covering every spec-documented exit code)

| Scenario | Zip contents | Flags | Exit | Message |
|----------|--------------|-------|------|---------|
| Happy path | `<exe>` + `_internal/dummy.txt` | `--require-internal` | **0** | `zip OK: 2 entries, <exe> present, _internal/ present` |
| Missing exe | only `_internal/dummy.txt` | `--require-internal` | **3** | `ERROR: missing <exe> at zip root` |
| Missing `_internal/` (required) | `<exe>` + `README.md` | `--require-internal` | **4** | `ERROR: missing _internal/ entries` |
| Missing zip path | (file does not exist) | `--require-internal` | **2** | `ERROR: zip not found: <path>` |
| Missing `_internal/` (NOT required) | only `<exe>` | (no flag) | **0** | `zip OK: 1 entries, <exe> present` |

Exit codes 0 / 2 / 3 / 4 match the helper's docstring exactly. The
"missing `_internal/` without `--require-internal`" case correctly
treats absence of `_internal/` as OK, which is the right behaviour
for the future Plan B vendoring workflow that might not include
`_internal/` in the zip.

## 13. Confirmation: no production tools were touched

Confirmed. No `Write`, `Edit`, or shell write touched any path under:

- `C:\Users\justing\PycharmProjects\Job Tracker\`
- `C:\Users\justing\PycharmProjects\Phoenix_CAD_Tool\`
- `C:\Users\justing\PycharmProjects\Phoenix-Checkout-Tool\`
- `C:\Users\justing\PycharmProjects\ValveMasterTool\`

Phase 6A only edited `phoenix-command-center/phoenix_tool_templates.py`
and created files under `%LOCALAPPDATA%\ATS Inc\PhoenixScaffold6A\`
(external scratch dir). No production tool source files were even
opened for read.

## 14. Confirmation: no PyInstaller / Inno / build / release / updater commands

Confirmed.

- No `pyinstaller …`
- No `iscc.exe …`
- **No `build.bat` execution** — Phase 6A is strictly a template /
  source-mode fix. The previous Phase 6 `dist/`, `build/`, installer,
  and zips from `…\PhoenixScaffold6\` were left exactly as they were
  for posterity; nothing rebuilt.
- No `gh release …`
- No `git push`
- No real updater `download_and_apply` against a live GitHub release
- No retrofit work on Phoenix CAD / Job Tracker / Checkout / ValveMaster

Subprocesses Phase 6A ran (full inventory):

```
python -m compileall -q .              (Command Center + scaffold; ×2)
python -c "…"                          (import sanity + structure check)
QT_QPA_PLATFORM=offscreen python verify_6a.py
QT_QPA_PLATFORM=offscreen python -m pytest -q tests/  (scaffold)
python <CLI fake-zip harness>           (direct subprocess of the helper)
git status / log / diff / add / commit (bookkeeping on both repos)
```

## 15. Confirmation: Phase 7 was not started

Confirmed.

- No retrofit work on Phoenix CAD / Job Tracker / Checkout / ValveMaster.
- No new branches off `phase-5-phoenix-tool-wizard`.
- Phase 7 todo remains `pending`.

## 16. Recommendation: merge Phase 5 branch into `main`?

**Lean toward merging — but the call is still Justin's.**

Phase 6A removes the only template defect surfaced by Phase 6's
build dogfood. With this change, every claim about the Phase 5 branch
is now true:

- Wizard UI: standalone default, commons-backed gated correctly,
  AV-caveat note visible, skip-warning + tailored success message —
  all verified in Phase 5A / 5B.
- Generated standalone scaffold: 27 files now (was 26), source-mode
  green in a fresh Python 3.14 venv, `pytest` 7/7 green (4 smoke
  tests + 3 validator tests).
- Generated commons-backed scaffold: 21 files, `pytest` 5/5 green +
  the 3 new validator tests (8/8 total when phoenix_commons is
  available).
- `build.bat`'s release-zip validator no longer crashes under
  PowerShell wrapping — the failure mode Phase 6 surfaced is gone.

The only outstanding caveat is the **frozen-exe AV gate** — same as
Phase 4 / 4B-local / 6. That's an environmental issue (corporate AV
on this developer's laptop deletes the PyInstaller bootloader exe),
not a code issue. None of Phase 5 / 5A / 5B / 6 / 6A changes affect it.

Two reasonable stances:

1. **Merge now with a known-AV-gap note.** The wizard / templates /
   scaffolds are correct, source-mode is fully green, the only
   remaining issue is documented. Add a one-paragraph entry to
   `phoenix-commons/docs/rollout/known-issues.md` (new file) saying:

   > "On developer machines with the laptop's corporate AV active,
   > PyInstaller's bootloader exe is quarantined seconds after
   > build.bat finishes. Inno Setup picks up the exe in time to
   > produce a working installer, but the unpacked exe on disk is
   > gone. Build will need to run on a host without that AV signature
   > (signed certificate or AV exception) before the auto-updater
   > zip and the installer can be smoke-tested end-to-end."

   Then merge `phase-5-phoenix-tool-wizard` → `main` with `--no-ff`
   so the history shows the discrete phase.

2. **Hold the merge until the AV gate clears.** Same recommendation
   as Phase 6. Phase 7 production retrofits don't depend on this
   merge being landed (they'd each be their own branch off whatever
   `main` looks like at retrofit time), so deferring loses nothing.

Either is defensible. I lean **(1) merge now** because:

- The Phase 5 branch has been stable for four phases of verification
  (5, 5A, 5B, 6, 6A).
- Letting it stagnate on a feature branch invites bitrot when other
  Command Center work lands on `main`.
- The known-issues note keeps the AV gap visible without blocking
  the wizard work itself.

But if you'd rather hold until the AV signature gets fixed (signed
certificate, vendor whitelist, or build-host swap), that's also fine
— this report records the precondition state so the merge can land
the moment the gate clears with no re-verification needed.

**Phase 7 production retrofits remain DEFERRED** regardless of which
merge stance you pick. They never depended on this merge for
correctness, only for branch hygiene.
