# Phase 5A — Wizard-Level Smoke Verification Report

> Phase 5A is a closeout + verification step that drives the actual
> `NewToolDialog._do_create()` code path (not the template functions
> directly) to confirm what the wizard generates from realistic user
> input. Three scenarios:
>
> - **A.** Standalone (default radio, commons unconfigured)
> - **B1.** Commons-backed template, submodule NOT added
> - **B2.** Commons-backed template, submodule added (with local commons URL)
>
> Source-mode only. No PyInstaller, no Inno Setup, no `build.bat`, no
> release commands, no production-tool changes.

## 1. Status

**Passed — with one documented UX gap and one environmental note.**

- Wizard UI behaves exactly as specified: standalone is the default radio,
  commons-backed is disabled with the `⚠` "not configured" note when
  `commons_path` is empty, and enabled with the `ℹ` AV-caveat note when
  `commons_path` is set. Note text and styling captured verbatim below.
- Standalone scaffold (Test A) generates 26 files and passes
  `compileall -q .` + `pytest -q tests/` (4/4 green).
- Commons-backed scaffold (Test B1) generates 20 files and passes the
  same checks (5/5 green).
- Commons-backed + submodule add (Test B2) successfully clones the local
  `phoenix-commons` checkout into `commons/`, writes `.gitmodules`, and
  commits — once git's CVE-2022-39253 `file://`-protocol policy is
  overridden for the local-path testing scenario. With an HTTPS URL (the
  realistic case) the wizard's existing `git submodule add` invocation
  is correct as-is.
- **One UX gap surfaced:** picking the commons-backed radio and unticking
  the "add submodule" checkbox produces a tool whose `requirements.txt`
  references `-e ./commons` but ships no `commons/` folder, no
  `.gitmodules`, and no post-create instructions telling the user to
  add the submodule first. The tool is then broken on first
  `pip install -r requirements.txt`. Recommended fix in §18.
- **One environmental note:** `git submodule add` with a local
  filesystem path is refused by git ≥ 2.38 unless
  `protocol.file.allow=always` is set. Not a wizard bug — only a
  local-testing artifact. Real GitHub HTTPS URLs work without override.

## 2. Exact commands run

### 2.1 Phoenix-commons housekeeping

```
$ cd C:\Users\justing\PycharmProjects\phoenix-commons
$ git show 723ef28:docs/rollout/phase-5-report.md > docs/rollout/phase-5-preflight-blocked-report.md
$ git add docs/rollout/phase-5-preflight-blocked-report.md
$ git commit -m "Preserve original blocked Phase 5 stub at phase-5-preflight-blocked-report.md"
$ git log --oneline -3
6d42fc7 Preserve original blocked Phase 5 stub at phase-5-preflight-blocked-report.md
15c627b Phase 5 report — replace stub with the real completion packet
7fe7fa0 Add Phase 4C-init report (phoenix-command-center is now a git repo)
$ git status --short --branch
## phase-4-pyinstaller-compatibility
```

### 2.2 Phoenix-command-center sanity

```
$ cd C:\Users\justing\PycharmProjects\phoenix-command-center
$ git status --short --branch
## phase-5-phoenix-tool-wizard
$ git log --oneline -3
2514c58 Phase 5 — add Phoenix Tool wizard radios (standalone + commons-backed)
3d84cc9 Initial commit — Command Center baseline before Phase 5
$ git check-ignore -v pcc_config.json
.gitignore:32:pcc_config.json   pcc_config.json
```

Branch unchanged from end of Phase 5. No new commits.

### 2.3 Wizard-level verification scripts

Three short Python harnesses were written under
`%LOCALAPPDATA%\ATS Inc\PhoenixScaffold5A\` so the scratch dir holds
both the generated scaffolds *and* the scripts that drove them:

| Script | Purpose |
|--------|---------|
| `verify_wizard.py` | Build `NewToolDialog` twice (once with `commons_path=""`, once with the real `phoenix-commons` path) to capture radio defaults + inline note text. Then drive `_do_create()` for Test A, Test B1, Test B2 and dump per-test results to `wizard-verify-report.json`. |
| `verify_submodule_b2.py` | Drill into B2 with an instrumented `_git` to capture every subprocess call. Surfaced the `protocol 'file' not allowed` git failure. |
| `verify_submodule_b2_with_proto.py` | Re-run B2 with `git -c protocol.file.allow=always …` to prove the wizard's submodule wiring path is correct. |

Each harness monkey-patches `QMessageBox.information / warning / critical`
to non-blocking lambdas and replaces `QDialog.accept` with a no-op so the
offscreen Qt run never blocks on a modal popup no one can dismiss.

```
$ QT_QPA_PLATFORM=offscreen python verify_wizard.py
REPORT_WRITTEN: C:\Users\justing\AppData\Local\ATS Inc\PhoenixScaffold5A\wizard-verify-report.json

$ QT_QPA_PLATFORM=offscreen python verify_submodule_b2.py
TRACE_WRITTEN:  C:\Users\justing\AppData\Local\ATS Inc\PhoenixScaffold5A\submodule-b2-trace.json

$ QT_QPA_PLATFORM=offscreen python verify_submodule_b2_with_proto.py
TRACE_WRITTEN:  C:\Users\justing\AppData\Local\ATS Inc\PhoenixScaffold5A\submodule-b2-with-proto-trace.json
```

### 2.4 Source-mode verification on each generated scaffold

```
$ cd .../PhoenixScaffold5A/test-a-standalone
$ python -m compileall -q .                          # exit 0
$ QT_QPA_PLATFORM=offscreen python -m pytest -q tests/
....                                                  [100%]
4 passed in 0.10s

$ cd .../PhoenixScaffold5A/test-b1-commons-no-submodule
$ python -m compileall -q .                          # exit 0
$ QT_QPA_PLATFORM=offscreen python -m pytest -q tests/
.....                                                 [100%]
5 passed in 0.10s

$ cd .../PhoenixScaffold5A/test-b2-commons-with-submodule
$ python -m compileall -q .                          # exit 0
$ QT_QPA_PLATFORM=offscreen python -m pytest -q tests/
.....                                                 [100%]
5 passed in 0.10s
```

Environment note: `pytest-qt` was installed in the system Python before
the first pytest run (`python -m pip install pytest-qt`); this is the
same dependency the scaffolded `requirements-dev.txt` already pins, so it
is what a developer cloning the new tool would install anyway.

## 3. Did the wizard UI show standalone as default?

**Yes — in both states of the dialog.**

Captured directly from `NewToolDialog` instances (offscreen):

| Property | Dialog A<br>(commons NOT configured) | Dialog B<br>(commons configured) |
|----------|--------------------------------------|----------------------------------|
| `rb_phoenix_standalone.isChecked` | `True` | `True` |
| `rb_phoenix_commons.isChecked`    | `False` | `False` |
| `rb_pyside6.isChecked`            | `False` | `False` |
| `rb_minimal.isChecked`            | `False` | `False` |
| `rb_copy.isChecked`               | `False` | `False` |
| `_selected_template_kind()`       | `"phoenix_standalone"` | `"phoenix_standalone"` |

Source: `wizard-verify-report.json` keys
`dialogA_no_commons_configured.default_radio` and
`dialogB_commons_configured.default_radio`.

## 4. Was commons-backed gated correctly?

**Yes.**

| Property | Dialog A | Dialog B |
|----------|---------|----------|
| `rb_phoenix_commons.isEnabled` | **`False`** | **`True`** |
| `_validate_step()` for B1/B2 (commons-backed) | (n/a — radio disabled, can't reach validation) | `True` |

Belt-and-braces also confirmed: `_validate_step()` would reject
commons-backed selection if `commons_path` were empty even if the radio
were forced on programmatically (see `new_tool_wizard.py` lines 557–565
in commit `2514c58`).

## 5. Was the AV caveat visible?

**Yes — and the text and style match the Phase 5 specification verbatim.**

Captured inline-note text from the dialog widget tree:

**Dialog A (commons NOT configured) — `⚠` warning note:**

```
⚠  Phoenix commons not configured. Set the commons path in Settings →
General and ensure it points at a verified phoenix-commons checkout.
```

styleSheet: `color: #F0A030; font-size: 11px; padding: 0 12px 8px 12px;`
(`#F0A030` is `C['warning']` in the Command Center theme.)

**Dialog B (commons configured) — `ℹ` info note with AV caveat:**

```
ℹ  Commons-backed template is available for source-mode testing.
Frozen-exe runtime verification is still blocked by local AV.
```

styleSheet: `color: #9090B0; font-size: 11px; padding: 0 12px 8px 12px;`
(`#9090B0` is `C['text_sub']` in the Command Center theme.)

The user is explicitly told the frozen-exe gate is still open whenever
they're in a position to select commons-backed.

## 6. Standalone scratch path

```
C:\Users\justing\AppData\Local\ATS Inc\PhoenixScaffold5A\test-a-standalone\
```

External to both `phoenix-command-center` and `phoenix-commons` — same
isolation pattern as Phase 4B-local. The dialog was driven with
`commons_path` set to the real `phoenix-commons` checkout (so the
commons radio was enabled), but the standalone radio was kept selected,
`cb_git = False`, `cb_commons = False`, `cb_open = False`. The wizard's
`_do_create()` then materialised the scaffold purely from
`template_phoenix_standalone("test-a-standalone")`.

## 7. Standalone file checklist

All 18 spec-required files present. Full generated file list (26 files,
no `.git/` because `cb_git=False`, no `__pycache__/` because no `.pyc`
artifact was loaded yet at capture time):

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

Spec-required check (all `expected_missing` empty):

```
README.md              ✓
CHANGELOG.md           ✓
CLAUDE.md              ✓
requirements.txt       ✓
requirements-dev.txt   ✓
version.py             ✓
main.py                ✓
backend.py             ✓
paths.py               ✓
updater.py             ✓
build.bat              ✓
installer.iss          ✓
phoenix_style.qss      ✓
ui/style.py            ✓
ui/components.py       ✓
ui/main_window.py      ✓
tests/test_smoke.py    ✓
.github/workflows/ci.yml  ✓
```

## 8. Standalone compileall + pytest output

```
$ cd .../PhoenixScaffold5A/test-a-standalone
$ python -m compileall -q .
(stderr only: the persistent distutils-precedence.pth warning from the
 system Python's user-site setuptools install — unrelated; exit 0.)

$ QT_QPA_PLATFORM=offscreen python -m pytest -q tests/
....                                                                     [100%]
4 passed in 0.10s
```

Tests covered (source: `tests/test_smoke.py`):
- `test_module_imports`
- `test_version_format`
- `test_main_window_instantiates(qtbot)`
- `test_apply_dark_theme(qapp)`

## 9. Commons-backed scratch paths

Two sub-scenarios share the parent scratch dir:

```
C:\Users\justing\AppData\Local\ATS Inc\PhoenixScaffold5A\
    ├── test-b1-commons-no-submodule\    (template only, no submodule)
    └── test-b2-commons-with-submodule\  (template + git submodule add)
```

B1 inputs: `rb_phoenix_commons=True`, `cb_git=False`, `cb_commons=False`.
B2 inputs: `rb_phoenix_commons=True`, `cb_git=True`, `cb_commons=True`,
`commons_url_edit="C:/Users/justing/PycharmProjects/phoenix-commons"`,
`commons_localpath_edit="commons"`.

## 10. Commons-backed file checklist

### 10.1 Test B1 — no submodule

20 files generated (no `.git/` because `cb_git=False`):

```
.github/ISSUE_TEMPLATE/bug_report.md
.github/ISSUE_TEMPLATE/feature_request.md
.github/pull_request_template.md
.github/workflows/ci.yml
.gitignore
CHANGELOG.md
CLAUDE.md
README.md
backend.py
build.bat
docs/release_checklist.md
installer.iss
main.py
requirements-dev.txt
requirements.txt
tests/__init__.py
tests/test_smoke.py
ui/__init__.py
ui/main_window.py
version.py
```

All spec-required commons-backed files present (`expected_missing` empty).
**`commons/` is absent**, **`.gitmodules` is absent** — see §12.

### 10.2 Test B2 — submodule added

Same 20 source files **plus**:
- `.git/` (from `cb_git=True`)
- `.gitmodules` (from the wizard's submodule add)
- `commons/` populated with the full `phoenix-commons` working tree —
  including `commons/src/phoenix_commons/__init__.py`, which is what
  `-e ./commons` resolves to.

89 paths total (most under `.git/objects/` and `commons/`).

## 11. Commons-backed compileall + pytest output

### 11.1 Test B1

```
$ cd .../PhoenixScaffold5A/test-b1-commons-no-submodule
$ python -m compileall -q .                          # exit 0
$ QT_QPA_PLATFORM=offscreen python -m pytest -q tests/
.....                                                 [100%]
5 passed in 0.10s
```

Tests: same four as the standalone plus `test_phoenix_commons_imports`,
which exercises:

```python
from phoenix_commons.theme import apply_dark_theme
from phoenix_commons.widgets import PrimaryButton, Panel, PhoenixTable
from phoenix_commons.paths import user_data_dir, is_frozen
from phoenix_commons.updater import check_for_update
```

**Caveat — see §13 for context.** This pytest run passes *only because*
`phoenix_commons` is already installed in the active venv (via the
Phase 1 `pip install -e C:\…\phoenix-commons`). A developer cloning the
generated B1 tool onto a fresh machine and running
`pip install -r requirements.txt` would hit `ERROR: file:./commons does
not exist` because the scaffold has no `commons/` folder.

### 11.2 Test B2

```
$ cd .../PhoenixScaffold5A/test-b2-commons-with-submodule
$ python -m compileall -q .                          # exit 0
$ QT_QPA_PLATFORM=offscreen python -m pytest -q tests/
.....                                                 [100%]
5 passed in 0.10s
```

`test_phoenix_commons_imports` works for the right reason here: the
`commons/` submodule is on disk and `-e ./commons` would resolve.

## 12. Explicit `commons/` and `.gitmodules` results

Per scratch folder:

| Path | A (standalone) | B1 (commons, no submodule) | B2 (commons, with submodule) |
|------|----------------|----------------------------|------------------------------|
| `commons/` directory | n/a — not relevant | **Absent** | **Present** (full phoenix-commons checkout, incl. `commons/src/phoenix_commons/__init__.py`) |
| `.gitmodules` file | n/a | **Absent** | **Present** |

B2 `.gitmodules` contents (verbatim from the generated file):

```
[submodule "commons"]
        path = commons
        url = C:/Users/justing/PycharmProjects/phoenix-commons
```

The B2 `git submodule add` initially returned exit 128 with
`fatal: transport 'file' not allowed` (git ≥ 2.38 CVE-2022-39253 default).
Re-running with `git -c protocol.file.allow=always …` succeeded and
produced the table above. **A real GitHub HTTPS URL** — which is what a
user would actually paste into the wizard — **is not affected by the
file-protocol policy** and would succeed with the wizard's existing git
invocation unchanged. See §15 for the captured stderr.

## 13. Is `-e ./commons` consistent with generated files / wizard instructions?

**Partially.** Both commons-backed scaffolds emit:

```
$ cat requirements.txt
PySide6>=6.5
-e ./commons
```

Consistency by scenario:

- **B2** (submodule added) → `-e ./commons` resolves to the on-disk
  `commons/src/phoenix_commons/`. `pip install -r requirements.txt`
  works. ✓
- **B1** (template only, no submodule) → `-e ./commons` points at a
  non-existent path. `pip install` will fail with
  `ERROR: file:./commons does not exist`. ✗

The wizard's success dialog after `_do_create()` says only:

```
✓  Created: <tool-name>
```

(or `…Opening in Command Center.` when `cb_open=True`).

**There is no post-create instruction telling the user to:**
- run `git submodule update --init` (if they cloned the tool elsewhere)
- run `pip install -e ../phoenix-commons` (if they prefer that to a
  vendored submodule)
- or tick the submodule checkbox in the first place

So the answer to *"does the wizard clearly instruct the user to add/init
the commons submodule before running pip install -r requirements.txt?"*
is **No.** This is the UX gap called out in §1 and the Phase 5B
recommendation in §18.

## 14. `git status` from phoenix-command-center

```
$ cd C:\Users\justing\PycharmProjects\phoenix-command-center
$ git status --short --branch
## phase-5-phoenix-tool-wizard
```

Clean working tree. Branch unchanged from end of Phase 5.

```
$ git log --oneline -3
2514c58 Phase 5 — add Phoenix Tool wizard radios (standalone + commons-backed)
3d84cc9 Initial commit — Command Center baseline before Phase 5
```

No new Command Center commits during Phase 5A. `pcc_config.json` stayed
ignored throughout (verified at start and end with `git check-ignore -v
pcc_config.json` → `.gitignore:32:pcc_config.json  pcc_config.json`).

Phase 5A intentionally did **not** merge `phase-5-phoenix-tool-wizard`
into `main` — per the Phase 5A scope, merge only after Phase 5A
verification passes. With the §18 UX-gap recommendation in mind, the
merge can either happen now (the gap is real but small and documented)
or after a Phase 5B follow-up — your call in the Phase 6 approval.

## 15. `git status` from phoenix-commons

```
$ cd C:\Users\justing\PycharmProjects\phoenix-commons
$ git status --short --branch
## phase-4-pyinstaller-compatibility
```

Clean working tree (this report will be the next commit on the same
branch).

```
$ git log --oneline -5
6d42fc7 Preserve original blocked Phase 5 stub at phase-5-preflight-blocked-report.md
15c627b Phase 5 report — replace stub with the real completion packet
7fe7fa0 Add Phase 4C-init report (phoenix-command-center is now a git repo)
723ef28 Add Phase 5 report — BLOCKED at pre-flight (phoenix-command-center not a git repo)
ec50fb5 Add Phase 4B-local retry report
```

Both Phase 5 reports — the original BLOCKED stub (under its new
permanent name `phase-5-preflight-blocked-report.md`) and the real
completion packet (`phase-5-report.md`) — are now committed
side by side under `docs/rollout/`.

## 16. Confirmation: no production tools were touched

Confirmed. No `Write`, `Edit`, or shell write touched any path under:

- `C:\Users\justing\PycharmProjects\Job Tracker\`
- `C:\Users\justing\PycharmProjects\Phoenix_CAD_Tool\`
- `C:\Users\justing\PycharmProjects\Phoenix-Checkout-Tool\`
- `C:\Users\justing\PycharmProjects\ValveMasterTool\`

The only reads from production tools during Phase 5A were zero — Phase 5A
never opened a production tool source file.

`phoenix-command-center` source was not modified — Phase 5A added zero
commits on `phase-5-phoenix-tool-wizard`.

`phoenix-commons` saw only:
- `docs/rollout/phase-5-preflight-blocked-report.md` restored from
  history (§2.1, commit `6d42fc7`).
- This report (§17, pending commit at end of Phase 5A).

The wizard-driven scaffolds live entirely under
`%LOCALAPPDATA%\ATS Inc\PhoenixScaffold5A\`, external to every repo.

## 17. Confirmation: no PyInstaller / Inno / build / release / updater commands ran

Confirmed.

- No `pyinstaller …`
- No `iscc.exe …`
- No `build.bat`
- No `installer.iss` compilation
- No `gh release …`
- No `git push`
- No real updater download/apply against a live release
- No GitHub asset upload
- No retrofit work on Phoenix CAD / Job Tracker / Checkout / ValveMaster

The only subprocesses Phase 5A spawned:

- `python -m compileall -q .` (×3, one per scratch scaffold + once on
  Command Center implicitly via the wizard's import-time compile cache)
- `QT_QPA_PLATFORM=offscreen python -m pytest -q tests/` (×3)
- `python -m pip install pytest-qt` (one-time, dev-dependency setup)
- `git init`, `git add -A`, `git commit -m …` (twice — once for Test B2
  inside the scratch tool's own repo, once for `git submodule add`)
- `git status / log / show / check-ignore / add / commit` against the
  two repos for bookkeeping

## 18. Recommendation for Phase 6 or not

**Approve Phase 6**, with one small Phase 5B follow-up that can land
either before Phase 6 or as part of the Phase 6 work — your choice. The
wizard itself is functionally correct; the gap is purely a post-create
UX hint.

### Phase 5B recommendation (small, low-risk)

Pick one of:

1. **Auto-tick `cb_commons` when `rb_phoenix_commons` is selected.** When
   the user picks the commons-backed radio in step 2, automatically
   check the submodule-add checkbox in step 3 (and pre-fill the URL via
   `_detect_commons_url()`, which already exists). User can still
   uncheck it if they don't want the submodule. Most users get the
   right behaviour without thinking; advanced users keep the override.

2. **Print post-create instructions when commons-backed.** After a
   successful `_do_create()`, if the template was commons-backed,
   replace the success dialog with one that lists the next steps:

   ```
   ✓  Created: <tool-name>

   Next steps:
     1.  cd <tool-name>
     2.  git submodule update --init    (if you didn't tick the submodule
                                        option in step 3)
     3.  pip install -r requirements.txt
     4.  pip install -r requirements-dev.txt
     5.  python main.py
   ```

3. **Make the `-e ./commons` line conditional.** In
   `template_phoenix_commons()`, generate two `requirements.txt`
   variants: one for the submodule case, one for the "use globally
   installed phoenix_commons" case. The wizard already knows which
   variant applies at `_do_create()` time based on `cb_commons`.

Option (2) is the cheapest and most informative — recommend doing that
as a tiny one-commit Phase 5B before merging the Phase 5 branch.

### Phase 6 scope reminder (unchanged from earlier plan)

Once you greenlight Phase 6:

- Pick the **standalone** scaffold (the safe default; commons-backed
  frozen-exe is still gated on the Phase 4B-local AV finding).
- Land it under `%LOCALAPPDATA%\ATS Inc\PhoenixScaffold6\` so the
  external-build hygiene from Phase 4B-local stays intact.
- Run `pip install -r requirements.txt` + `-r requirements-dev.txt`,
  smoke-test from source, then `build.bat` to produce
  `dist\…\<exe>.exe`.
- Run Inno Setup against `installer.iss` to produce
  `dist\<…>Setup.exe`. Install locally to `%LOCALAPPDATA%\ATS Inc\…`.
- Confirm the installed exe launches themed; confirm `%APPDATA%\ATS
  Inc\…` got created; confirm no production tool source files changed.
- If the AV blocker fires for the standalone exe too, accept Phase 6
  as Partial — same shape as Phase 4B-local — and the commons-backed
  default stays deferred.

Phase 6 awaiting go/no-go.
