# Phase 6C Plan — Frozen-exe Dogfood (Prepared, Not Yet Executed)

> Runs the build / install / launch verification that Phase 6 had to
> skip because the corporate AV (SentinelOne / S1) quarantined the
> PyInstaller bootloader exe within seconds of the build completing.
>
> **Status: drafted only.** Phase 6C does not start until at least one
> of the §0 gate-clear conditions is confirmed in writing.
>
> Scope is narrow: dogfood **one** throwaway standalone Phoenix tool
> end-to-end (generate → build → install → launch → user-data folder).
> No production tools touched. No commons-backed PyInstaller dogfood.
> No `git push`, no `gh release`, no production `build.bat`, no
> production updater.

## 0. Preconditions — gate-clear path

Phase 6C does not start until at least one of these is confirmed in
writing (email, ticket, signed cert in place — anything explicit):

| Path | Concrete signal that it landed |
|------|--------------------------------|
| **(a) IT / S1 allow-list** | IT confirms the PyInstaller bootloader signature is allow-listed for this laptop, OR `%LOCALAPPDATA%\ATS Inc\` is excluded from S1 real-time scanning. |
| **(b) Authenticode code signing** | A signing certificate is provisioned and a `signtool sign` step has been added to `phoenix_tool_templates.py`'s `BUILD_BAT` template (between PyInstaller and Inno Setup), committed and merged to `phoenix-command-center` `main`. A manual smoke build of the resulting signed bootloader survives on disk for at least 5 minutes. |
| **(c) Approved alternate build host** | A second machine (CI runner, freshly imaged workstation, build-server VM) is approved to host the dogfood. Phase 6C runs there instead of this laptop. |

No PyInstaller / Inno Setup / `build.bat` invocations until one of
(a) / (b) / (c) is confirmed. Re-reading the §1 / §13 sections of
`phase-6-standalone-dogfood-report.md` is recommended right before
kickoff so the failure mode is fresh in mind.

## 1. Boundaries (unchanged from Phase 6 spec)

**Do not:**

- Touch `Job Tracker`, `Phoenix_CAD_Tool`, `Phoenix-Checkout-Tool`,
  `ValveMasterTool` — no reads, no writes, no builds.
- Run production `build.bat`, production updater, `gh release`,
  `git push`, or any release-asset upload.
- Promote commons-backed as default.
- Activate Plan B vendoring.
- Start Phase 7.
- Merge anything to `main` (Phase 5 wizard is already merged at
  commit `e3cb7d7`; Phase 6C is verification only).

**Do:**

- Work in an external scratch dir: `%LOCALAPPDATA%\ATS Inc\PhoenixScaffold6C\`.
- Generate **one** throwaway standalone tool through the actual
  `NewToolDialog._do_create()` path.
- Stop the moment any gate fails; capture evidence; mark Partial.

## 2. Pre-flight checks

Both repos must be clean before starting:

```
cd C:\Users\justing\PycharmProjects\phoenix-command-center
git status --short --branch     →  ## main (clean)
git log --oneline -1            →  e3cb7d7 Merge Phoenix Tool wizard templates
git check-ignore -v pcc_config.json
                                →  .gitignore:32:pcc_config.json   pcc_config.json

cd C:\Users\justing\PycharmProjects\phoenix-commons
git status --short --branch     →  clean
ls docs/rollout/phase-6b-command-center-merge-report.md
                                →  exists (committed at e8b8183)
```

If (b) Authenticode signing was the gate-clear path: confirm the
`build.bat` template in `phoenix_tool_templates.py` has been updated
on `phoenix-command-center` `main` (a Phase 6.5 / 6D landing commit).
Phase 6C verifies that change end-to-end.

## 3. Step-by-step procedure

### Step A — Generate scaffold through the actual wizard

Same harness pattern as Phase 6 (`generate_phase6_tool.py`). Save the
new harness under the scratch dir:

```
mkdir -p "%LOCALAPPDATA%\ATS Inc\PhoenixScaffold6C\"
```

Drive `NewToolDialog._do_create()` with offscreen Qt + monkey-patched
`QMessageBox`. Tool name: `phoenix-phase6c-standalone`. Inputs:

- `name_edit.text = "phoenix-phase6c-standalone"`
- `root_edit.text = SCRATCH`
- `rb_phoenix_standalone` checked (default — assert at construction)
- `cb_git = True`
- `cb_commons = False`
- `cb_open = False`

Capture: `defaults` snapshot, post-create message, file list.

**Pass criteria:** 27 files generated, including
`scripts/validate_release_zip.py` (from Phase 6A).
`_selected_template_kind()` returns `"phoenix_standalone"` at
construction.

### Step B — Source-mode verification (fresh venv)

```
cd "%LOCALAPPDATA%\ATS Inc\PhoenixScaffold6C\phoenix-phase6c-standalone"
py -3.14 -m venv .venv
.venv\Scripts\python.exe -m pip install --upgrade pip
.venv\Scripts\python.exe -m pip install -r requirements.txt
.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
.venv\Scripts\python.exe -m compileall -q .
set QT_QPA_PLATFORM=offscreen
.venv\Scripts\python.exe -m pytest -q tests/
```

**Pass criteria:** `compileall` exit 0; `pytest` 7/7 green (4 smoke
tests + 3 release-zip validator tests).

Also capture an offscreen `MainWindow` smoke (title, version, size,
button count) for the report.

### Step C — Build attempt (the part Phase 6 was blocked on)

```
cd "%LOCALAPPDATA%\ATS Inc\PhoenixScaffold6C\phoenix-phase6c-standalone"
& cmd.exe /c ".\build.bat"     # run via PowerShell — same surface as Phase 6
```

Capture the full `build-output.log` (UTF-16 encoding from `*>`; read
via `Get-Content -Encoding Unicode` or `Select-String` when grepping).

#### Step C.1 — Exe survival check

```
Test-Path "dist\PhoenixPhase6cStandalone\PhoenixPhase6cStandalone.exe"
Test-Path "dist\PhoenixPhase6cStandalone\_internal"
Get-Item "dist\PhoenixPhase6cStandalone\PhoenixPhase6cStandalone.exe" |
    Select-Object LastWriteTime, Length
```

Both `Test-Path` calls must return `True`. The exe's `LastWriteTime`
should be fresh (within the last 5 minutes).

**Stop and mark Partial if the exe is missing.** This is exactly the
gate Phase 6 failed at — re-failing here means the gate-clear path
selected in §0 didn't actually clear the gate.

#### Step C.2 — Auto-updater zip integrity (Phase 6A validator)

```
.venv\Scripts\python.exe scripts\validate_release_zip.py `
    --zip dist\PhoenixPhase6cStandalone.zip `
    --exe PhoenixPhase6cStandalone.exe `
    --require-internal
```

Expect exit 0 and a message like
`zip OK: N entries, PhoenixPhase6cStandalone.exe present, _internal/ present`.
Phase 6A confirmed this helper works under PowerShell wrapping with
synthetic zips; Phase 6C confirms it on a real freshly-built zip.

#### Step C.3 — Launch the built exe (once)

```
$exe = "dist\PhoenixPhase6cStandalone\PhoenixPhase6cStandalone.exe"
$proc = Start-Process -FilePath $exe -PassThru -WindowStyle Hidden
Start-Sleep -Seconds 5
$running = Get-Process -Id $proc.Id -ErrorAction SilentlyContinue
if ($running) { Stop-Process -Id $proc.Id -Force }
```

**Pass criteria:** Process started (PID > 0), survived 5 seconds
without AV deletion, and exited cleanly when terminated.

If AV deletes the exe during the 5-second window, the gate-clear path
wasn't sufficient. Stop. Mark Partial.

### Step D — Installer execution

Only if Step C.3 passed:

```
$installer = "dist\PhoenixPhase6cStandaloneSetup.exe"
Start-Process -FilePath $installer `
    -ArgumentList "/VERYSILENT","/SUPPRESSMSGBOXES","/NORESTART" -Wait

Test-Path "$env:LOCALAPPDATA\ATS Inc\Phoenix Phase6c Standalone\PhoenixPhase6cStandalone.exe"
```

`/VERYSILENT` is Inno Setup's silent-install switch.

**Pass criteria:** Installed exe exists at
`%LOCALAPPDATA%\ATS Inc\Phoenix Phase6c Standalone\PhoenixPhase6cStandalone.exe`.

### Step E — Installed exe launch + user-data folder

```
$installed = "$env:LOCALAPPDATA\ATS Inc\Phoenix Phase6c Standalone\PhoenixPhase6cStandalone.exe"
$proc = Start-Process -FilePath $installed -PassThru -WindowStyle Hidden
Start-Sleep -Seconds 5
$running = Get-Process -Id $proc.Id -ErrorAction SilentlyContinue
if ($running) { Stop-Process -Id $proc.Id -Force }

Test-Path "$env:APPDATA\ATS Inc\Phoenix Phase6c Standalone"
```

**Pass criteria:** Installed exe starts (PID > 0), exits cleanly, and
`%APPDATA%\ATS Inc\Phoenix Phase6c Standalone\` directory was created
on first run.

The user-data path comes from
`paths.user_data_dir("Phoenix Phase6c Standalone")` inside the
scaffold's `paths.py`. The first run of any code path that calls it
(backend init / settings load / etc.) materialises the directory.

### Step F — Post-checks

```
# Source tree intact?
cd "%LOCALAPPDATA%\ATS Inc\PhoenixScaffold6C\phoenix-phase6c-standalone"
.venv\Scripts\python.exe -m pytest -q tests/       # re-run; expect 7 passed

# Both repos still clean?
cd C:\Users\justing\PycharmProjects\phoenix-command-center
git status --short --branch         →  ## main (clean)
cd C:\Users\justing\PycharmProjects\phoenix-commons
git status --short --branch         →  clean
```

### Step G — Do not uninstall

Leave the installed throwaway at
`%LOCALAPPDATA%\ATS Inc\Phoenix Phase6c Standalone\` for Justin to
inspect. Don't run the uninstaller. Don't delete the user-data
folder.

## 4. Pass / fail / partial rubric

| Outcome | Conditions |
|---------|------------|
| **Passed** | Steps A → F all green; installed app launches; user-data folder exists. |
| **Partial — AV still active** | Step C.1 fails (exe quarantined). Stop. Capture evidence. Same outcome as Phase 6. Gate-clear path didn't work — return to one of the §0 paths. |
| **Partial — installer-side AV** | C.1 + C.3 pass but D or E fail because AV fires on the installed exe under `%LOCALAPPDATA%`. Document; the gate-clear path needs to cover the install root too. |
| **Failed** | Any step before C.1 fails (compileall, pytest, source-mode smoke, …). Indicates a regression in the wizard or templates since Phase 6A — investigate before merging anything new. |

## 5. Report deliverable

```
C:\Users\justing\PycharmProjects\phoenix-commons\docs\rollout\phase-6c-frozen-exe-dogfood-report.md
```

Mirror the 24-section structure from
`phase-6-standalone-dogfood-report.md`, plus an extra section at the
top stating:

- Which §0 gate-clear path was active when Phase 6C ran (a / b / c).
- The date the gate cleared.
- A pointer to whatever IT ticket / signing cert / build-host
  approval was used.

Commit on phoenix-commons with the standard report-commit pattern.
No commits or edits to phoenix-command-center expected — Phase 6C is
verification only.

## 6. Recovery clauses

- **Don't rerun `build.bat` in a tight loop.** If C.1 fails, stop.
  Two rebuilds at most before declaring Partial.
- **Don't add AV exclusions during Phase 6C itself.** The gate-clear
  path was supposed to land before kickoff; touching AV settings
  mid-phase muddies the evidence.
- **Don't sign the exe inside Phase 6C if signing wasn't the §0
  path.** If you decide to flip from path (a) → (b) mid-run, abandon
  the current Phase 6C, document the pivot, and start a fresh
  Phase 6C session.

## 7. After Phase 6C

**If Passed:**

- Lift the `docs/known-issues.md` entry from Open → Resolved (or
  split it into a "Historical: AV bootloader quarantine (resolved
  YYYY-MM-DD)" subsection).
- Approve Phase 7 retrofits in the order from the unified plan:
  Phoenix CAD → Phoenix Checkout → ValveMaster → Job Tracker. Each
  is its own feature branch off `main`, with the per-retrofit
  safety checklist from the unified plan.

**If Partial / Failed:**

- Don't touch Phase 7.
- Return to §0 with the new evidence.

## 8. What this plan deliberately leaves out

- **Commons-backed PyInstaller dogfood.** Out of scope — commons-
  backed is not the default and stays gated on the same AV signature.
  A separate Phase 6D could dogfood the commons-backed variant later,
  but only after Phase 6C lifts the AV blocker for the standalone
  bootloader.
- **CI builds.** A `pyinstaller-smoke` job in the generated tool's
  `.github/workflows/ci.yml` is conceivable once a remote exists for
  Command Center, but adding CI is out of Phase 6C scope.
- **Updater download/apply against a live release.** Out of scope.
  The auto-updater path is exercised only via the in-scaffold smoke
  tests (Phase 6A added validator coverage for the release zip
  structure). A real updater dry-run could be a discrete future
  phase against a tagged-but-unpublished GitHub release.

Phase 6C is verification only. The wizard, templates, and known
issues all stay exactly as `main` left them at merge commit `e3cb7d7`.
