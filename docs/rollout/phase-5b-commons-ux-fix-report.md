# Phase 5B Report — Commons-backed wizard UX fix

> Closes the UX gap surfaced in Phase 5A (§13): when a user picks
> *Phoenix Tool — commons-backed* in the New Tool wizard, the submodule
> add box is now auto-ticked, the commons URL is auto-detected, an
> inline ⚠ note appears if the user unticks it anyway, and the
> post-create success message lists the next steps tailored to whether
> the submodule was added or skipped.
>
> Source-mode only. No PyInstaller, no Inno Setup, no `build.bat`, no
> release commands, no production-tool changes. Commons-backed remains
> NOT the default; frozen-exe runtime is NOT claimed verified.

## 1. Status

**Passed.**

All four implementation points landed cleanly, all seven offscreen UX
checks behaved as specified, and all three scaffold scenarios generated
the expected files with the expected post-create messaging. Compileall
clean on the wizard and on every scratch scaffold; pytest green on each
scaffold (4/4 standalone, 5/5 commons+submodule, 5/5 commons-no-submodule).

One environmental note: UX-7 (auto-refill the commons URL field when
blank) returned an empty string in this test environment because
`phoenix-commons` has no `origin` remote configured locally — the
wizard's `_detect_commons_url()` logic is invoked correctly, it just
has nothing to read. On a developer's machine where phoenix-commons was
cloned from GitHub the field would auto-fill with the GitHub HTTPS URL.

## 2. Files changed in phoenix-command-center

| Path | Status | Purpose |
|------|--------|---------|
| `new_tool_wizard.py` | MODIFIED (+86 / −1) | Adds the four Phase 5B changes — cross-page signal wiring at end of `_build()`, new `commons_skip_warning` QLabel in `_page_git()`, two new helper methods (`_on_phoenix_commons_toggled`, `_refresh_commons_skip_warning`), and the commons-aware post-create message branch in `_do_create()`. |

No other Command Center files touched. No changes to
`phoenix_tool_templates.py` — the templates themselves were already
correct in Phase 5; Phase 5B is strictly a wizard-UX fix.

## 3. `git status --short --branch` from phoenix-command-center

```
$ cd phoenix-command-center && git status --short --branch
## phase-5-phoenix-tool-wizard
(clean working tree)
```

## 4. `git diff --stat` from phoenix-command-center

```
$ git diff --stat main..phase-5-phoenix-tool-wizard
 new_tool_wizard.py        |  228 +++--
 phoenix_tool_templates.py | 1741 +++++++++++++++++++++++++++++++++++++++++++++
 2 files changed, 1947 insertions(+), 22 deletions(-)
```

Phase 5B commit-only diff:

```
$ git diff --stat 2514c58..cff99bd
 new_tool_wizard.py | 87 +++++++++++++++++++++++++++++++++++++++++++++++++++++-
 1 file changed, 86 insertions(+), 1 deletion(-)
```

Branch log on phase-5-phoenix-tool-wizard:

```
$ git log --oneline main..phase-5-phoenix-tool-wizard
cff99bd Phase 5B — close the commons-backed UX gap
2514c58 Phase 5 — add Phoenix Tool wizard radios (standalone + commons-backed)
```

## 5. Relevant diff / file contents

### 5.1 New signal wiring at end of `_build()`

```python
# ── Cross-page state wiring (Phase 5B) ──────────────────────────
# Connecting here (rather than inside each page builder) lets us
# touch widgets created by pages 2 and 3 in the same callback —
# at this point every page has been added to the stack.
self.rb_phoenix_commons.toggled.connect(self._on_phoenix_commons_toggled)
self.rb_phoenix_standalone.toggled.connect(
    lambda _checked: self._refresh_commons_skip_warning()
)
self.cb_commons.toggled.connect(
    lambda _checked: self._refresh_commons_skip_warning()
)
# Keep the warning state coherent on first show.
self._refresh_commons_skip_warning()
```

### 5.2 New inline skip-warning QLabel in `_page_git()`

```python
# ── Phase 5B: commons-backed + no-submodule skip warning ────────
# Hidden by default. Made visible by _refresh_commons_skip_warning()
# when (template == commons-backed) AND (submodule add unchecked).
self.commons_skip_warning = QLabel(
    "⚠  You picked the commons-backed template but won't be "
    "adding the submodule. requirements.txt references "
    "-e ./commons — pip install will fail until you put "
    "phoenix-commons at ./commons manually."
)
self.commons_skip_warning.setWordWrap(True)
self.commons_skip_warning.setStyleSheet(
    f"color: {C['warning']}; font-size: 11px; "
    f"padding: 4px 12px 8px 12px;"
)
self.commons_skip_warning.setVisible(False)
ccl.addWidget(self.commons_skip_warning)
```

### 5.3 New helper methods

```python
def _on_phoenix_commons_toggled(self, checked: bool) -> None:
    """Fired when the commons-backed radio toggles.

    When the radio becomes checked, auto-tick the submodule add box
    (if commons is configured and the box is interactable) and
    refill the URL field with the auto-detected commons remote if
    it's currently blank. The user can still uncheck the box
    afterwards — they'll see the skip warning in that case.
    """
    if checked and self.commons_path and self.cb_commons.isEnabled():
        self.cb_commons.setChecked(True)
        if not self.commons_url_edit.text().strip():
            url = self._detect_commons_url()
            if url:
                self.commons_url_edit.setText(url)
    self._refresh_commons_skip_warning()

def _refresh_commons_skip_warning(self) -> None:
    """Show the inline ⚠ note iff (commons-backed template) AND
    (submodule add unchecked). That combination is the broken-tool
    case — requirements.txt has -e ./commons but no commons/ folder
    will exist on disk after creation."""
    if not hasattr(self, "commons_skip_warning"):
        return
    show = (
        self.rb_phoenix_commons.isChecked()
        and not self.cb_commons.isChecked()
    )
    self.commons_skip_warning.setVisible(show)
```

### 5.4 Tailored post-create success message

```python
# ── Phase 5B: commons-backed tools get an explicit next-steps
#    success message that handles both the submodule-added and
#    submodule-skipped flows. Plain success message is reused
#    for every other template kind.
if tk == "phoenix_commons":
    steps = [
        f"✓  Created: {name}",
        "",
        "Next steps:",
        f"  1. cd {name}",
        "  2. If the commons submodule was added:",
        "       git submodule update --init",
        "  3. If you did NOT add the commons submodule:",
        "       Add phoenix-commons at ./commons before running pip install.",
        "  4. pip install -r requirements.txt",
        "  5. pip install -r requirements-dev.txt",
        "  6. python main.py",
    ]
    if do_open:
        steps += ["", "Opening in Command Center."]
    QMessageBox.information(self, "Tool created", "\n".join(steps))
elif do_open:
    QMessageBox.information(
        self, "Tool created",
        f"✓  Created: {name}\n\nOpening in Command Center."
    )
else:
    QMessageBox.information(self, "Tool created", f"✓  Created: {name}")
self.accept()
```

## 6. Exact commands run

### 6.1 Pre-flight

```
$ cd C:\Users\justing\PycharmProjects\phoenix-command-center
$ git status --short --branch    →  ## phase-5-phoenix-tool-wizard (clean)
$ git log --oneline -3
$ git check-ignore -v pcc_config.json
  .gitignore:32:pcc_config.json   pcc_config.json

$ cd C:\Users\justing\PycharmProjects\phoenix-commons
$ git status --short --branch    →  ## phase-4-pyinstaller-compatibility (clean)
$ ls docs/rollout/phase-5a-wizard-smoke-report.md   → present
$ git log --all --oneline -- docs/rollout/phase-5a-wizard-smoke-report.md
  c1a9c7d Phase 5A — wizard-level smoke verification report
```

### 6.2 Implementation

```
(Edit)  new_tool_wizard.py
        - signal wiring at end of _build()
        - commons_skip_warning QLabel in _page_git()
        - _on_phoenix_commons_toggled + _refresh_commons_skip_warning
        - commons-aware success message in _do_create()
```

### 6.3 Source-mode verification

```
$ cd C:\Users\justing\PycharmProjects\phoenix-command-center
$ python -m compileall -q .                                  # exit 0
$ python -c "from new_tool_wizard import NewToolDialog; \
             from phoenix_tool_templates import \
                 template_phoenix_standalone, template_phoenix_commons; \
             print('OK')"                                     # OK

$ mkdir -p "C:\Users\justing\AppData\Local\ATS Inc\PhoenixScaffold5B"
$ QT_QPA_PLATFORM=offscreen python \
    "C:\Users\justing\AppData\Local\ATS Inc\PhoenixScaffold5B\verify_wizard_5b.py"
REPORT_WRITTEN: …\PhoenixScaffold5B\wizard-verify-5b-report.json

$ cd .../PhoenixScaffold5B/test-a-standalone
$ python -m compileall -q .                                  # exit 0
$ QT_QPA_PLATFORM=offscreen python -m pytest -q tests/
....                                                          [100%]
4 passed in 0.10s

$ cd .../PhoenixScaffold5B/test-b-with-submodule
$ python -m compileall -q .                                  # exit 0
$ QT_QPA_PLATFORM=offscreen python -m pytest -q tests/
.....                                                         [100%]
5 passed in 0.10s

$ cd .../PhoenixScaffold5B/test-b-no-submodule
$ python -m compileall -q .                                  # exit 0
$ QT_QPA_PLATFORM=offscreen python -m pytest -q tests/
.....                                                         [100%]
5 passed in 0.10s
```

### 6.4 Commit

```
$ cd C:\Users\justing\PycharmProjects\phoenix-command-center
$ git add new_tool_wizard.py
$ git commit -m "Phase 5B — close the commons-backed UX gap"
[phase-5-phoenix-tool-wizard cff99bd] Phase 5B — close the commons-backed UX gap
 1 file changed, 86 insertions(+), 1 deletion(-)
```

### 6.5 Verification harness

A single script drove every wizard scenario, monkey-patching `QMessageBox`
to capture the post-create text and patching `_git` to inject
`-c protocol.file.allow=always` so the local-URL submodule add in B-with
isn't blocked by git's CVE-2022-39253 default (same workaround as
Phase 5A — irrelevant for real GitHub HTTPS URLs).

```
verify_wizard_5b.py
  → wizard-verify-5b-report.json
```

Both files live under `%LOCALAPPDATA%\ATS Inc\PhoenixScaffold5B\`.

## 7. Raw verification output

### 7.1 UX-check captures (from `wizard-verify-5b-report.json`)

```json
"UX_checks": {
  "UX1_standalone_default":                                  true,
  "UX2_commons_not_default":                                 true,
  "initial_cb_commons.isChecked":                            true,
  "initial_commons_skip_warning.visible":                    false,
  "after_uncheck_cb_commons.isChecked":                      false,
  "after_uncheck_skip_warning.visible":                      false,
  "UX3_after_commons_radio.cb_commons.isChecked":            true,
  "UX3_after_commons_radio.skip_warning.visible":            false,
  "UX3_after_commons_radio.commons_url_edit.text":           "",
  "UX4_after_user_uncheck.cb_commons.isChecked":             false,
  "UX5_after_user_uncheck.skip_warning.visible":             true,
  "UX5_skip_warning.text":
    "⚠  You picked the commons-backed template but won't be adding the
       submodule. requirements.txt references -e ./commons — pip install
       will fail until you put phoenix-commons at ./commons manually.",
  "UX5_skip_warning.styleSheet":
    "color: #F0A030; font-size: 11px; padding: 4px 12px 8px 12px;",
  "UX6_after_back_to_standalone.skip_warning.visible":       false,
  "UX7_after_blank_url_then_commons.commons_url_edit.text":  ""
}
```

(Visibility is captured via `not widget.isHidden()` rather than
`widget.isVisible()` — the offscreen dialog is never `.show()`-n, so Qt
returns `isVisible() == False` even when `setVisible(True)` was called.
`isHidden()` reflects the explicit-visibility flag and is the correct
check for this scenario.)

UX1–UX6 are all `True` (or `False` where appropriate) — every wizard
behaviour the spec required is in place. UX-7 is the documented
environmental empty (see §1 status).

### 7.2 Per-scaffold post-create messages

**A — standalone (plain message reused unchanged):**

```
✓  Created: test-a-standalone
```

**B-with — commons-backed + submodule added (tailored next-steps):**

```
✓  Created: test-b-with-submodule

Next steps:
  1. cd test-b-with-submodule
  2. If the commons submodule was added:
       git submodule update --init
  3. If you did NOT add the commons submodule:
       Add phoenix-commons at ./commons before running pip install.
  4. pip install -r requirements.txt
  5. pip install -r requirements-dev.txt
  6. python main.py
```

**B-no — commons-backed + submodule UNchecked (same tailored message):**

```
✓  Created: test-b-no-submodule

Next steps:
  1. cd test-b-no-submodule
  2. If the commons submodule was added:
       git submodule update --init
  3. If you did NOT add the commons submodule:
       Add phoenix-commons at ./commons before running pip install.
  4. pip install -r requirements.txt
  5. pip install -r requirements-dev.txt
  6. python main.py
```

### 7.3 Per-scaffold compileall + pytest

```
A   standalone
    python -m compileall -q .          → exit 0
    QT_QPA_PLATFORM=offscreen pytest   → 4 passed in 0.10s

B-with  commons + submodule
    python -m compileall -q .          → exit 0
    QT_QPA_PLATFORM=offscreen pytest   → 5 passed in 0.10s

B-no    commons (submodule unchecked)
    python -m compileall -q .          → exit 0
    QT_QPA_PLATFORM=offscreen pytest   → 5 passed in 0.10s
```

`test_phoenix_commons_imports` passes for B-no only because
`phoenix_commons` is already pip-installed editable in the active venv
(from Phase 1) — a fresh clone of the B-no scaffold would fail
`pip install -r requirements.txt` with `ERROR: file:./commons does not
exist`. That is exactly the scenario the new skip warning + post-create
instructions are designed to make visible to the user.

## 8. Standalone default confirmation

`UX1_standalone_default = True` and `UX2_commons_not_default = True` in
the captured UX block. `_selected_template_kind()` returns
`"phoenix_standalone"` at construction time. Test A produced the plain
success message (no Next-steps list) — confirming the commons-aware
branch is gated by template kind.

## 9. Commons-backed auto-check confirmation

`UX3_after_commons_radio.cb_commons.isChecked = True` — toggling
`rb_phoenix_commons` after an explicit unchecking of `cb_commons` snapped
the submodule box back on. Test B-with picked up the same auto-checked
state at create time:

```
"auto_check_state": {
  "after_commons_radio.cb_commons.isChecked":  true,
  "after_commons_radio.commons_url_edit.text": "",
  "after_commons_radio.skip_warning.visible":  false
}
```

`cb_commons` is auto-checked (`true`) and the skip-warning correctly
remains hidden (`false`) because the user hasn't unticked the box yet.

`commons_url_edit.text` is empty here for the same environmental reason
as UX-7 — `_detect_commons_url()` ran `git remote get-url origin` against
the local `phoenix-commons` checkout and got back nothing because the
local repo has no `origin` configured. On a developer machine with
`phoenix-commons` cloned from GitHub this field would auto-fill.

## 10. Submodule-checked scaffold result (Test B-with)

```
scratch_path:        …\PhoenixScaffold5B\test-b-with-submodule\
has_commons_folder:  true
has_gitmodules:      true
.gitmodules:
    [submodule "commons"]
            path = commons
            url = C:/Users/justing/PycharmProjects/phoenix-commons
requirements_txt:
    PySide6>=6.5
    -e ./commons
```

Generated source files (20, same Phase 5 set) plus the full
`phoenix-commons` working tree checked out into `commons/`, including
`commons/src/phoenix_commons/__init__.py` — so `-e ./commons` in
`requirements.txt` resolves to a real installable package.

git_trace returncodes (every git subprocess succeeded):
```
[git init, git add -A, git commit, git submodule add, git add -A, git commit]
[0,        0,           0,          0,                  0,           0]
```

`python -m compileall -q .` and `QT_QPA_PLATFORM=offscreen pytest -q
tests/` both green (5/5).

## 11. Submodule-unchecked scaffold result (Test B-no)

```
scratch_path:        …\PhoenixScaffold5B\test-b-no-submodule\
has_commons_folder:  false
has_gitmodules:      false
requirements_txt:    "PySide6>=6.5\n-e ./commons\n"
```

User-flow trace (captured from `wizard-verify-5b-report.json`):

```json
"before_user_uncheck": {
  "cb_commons.isChecked": true,           // auto-checked when commons radio selected
  "skip_warning.visible": false
},
"after_user_uncheck": {
  "cb_commons.isChecked": false,
  "skip_warning.visible": true,           // ⚠ now visible
  "skip_warning.text":
    "⚠  You picked the commons-backed template but won't be adding the
       submodule. requirements.txt references -e ./commons — pip install
       will fail until you put phoenix-commons at ./commons manually."
}
```

The wizard then completed `_do_create()`, emitted the tailored
post-create success message (§12), and produced 20 source files with no
`commons/` folder and no `.gitmodules` — exactly what the user opted
into.

`python -m compileall -q .` clean; `pytest` 5/5 green for the same
caveat as B-with (`phoenix_commons` available globally via Phase 1
`pip install -e .`).

## 12. Exact post-create instruction / warning text

### 12.1 Inline skip warning (in-wizard, on the Git & commons page)

Captured verbatim from `dlg.commons_skip_warning.text()`:

```
⚠  You picked the commons-backed template but won't be adding the
submodule. requirements.txt references -e ./commons — pip install
will fail until you put phoenix-commons at ./commons manually.
```

Styling captured verbatim from `dlg.commons_skip_warning.styleSheet()`:

```
color: #F0A030; font-size: 11px; padding: 4px 12px 8px 12px;
```

(`#F0A030` is `C['warning']` in the Command Center theme — matches the
"⚠ commons not configured" tone used elsewhere in the wizard.)

### 12.2 Post-create success message (commons-backed)

Captured verbatim from `QMessageBox.information(...)` for Test B-with
and Test B-no:

```
✓  Created: <tool-name>

Next steps:
  1. cd <tool-name>
  2. If the commons submodule was added:
       git submodule update --init
  3. If you did NOT add the commons submodule:
       Add phoenix-commons at ./commons before running pip install.
  4. pip install -r requirements.txt
  5. pip install -r requirements-dev.txt
  6. python main.py
```

If `cb_open` is True, the message has an extra blank line and "Opening
in Command Center." appended.

### 12.3 Post-create success message (every other template, unchanged)

```
✓  Created: <tool-name>
```

(or `… Opening in Command Center.` when `cb_open` is checked).

## 13. Confirmation: `pcc_config.json` stayed ignored

```
$ git check-ignore -v pcc_config.json
.gitignore:32:pcc_config.json   pcc_config.json

$ git diff --cached --name-only | grep -E "^pcc_config\.json$" || echo NOT staged
NOT staged
```

Verified at start of Phase 5B and again after the commit. `pcc_config.json`
remains on disk with the user's runtime values; git is unaware of it.

## 14. Confirmation: no production tools were touched

Confirmed. No `Write`, `Edit`, or shell write touched any path under:

- `C:\Users\justing\PycharmProjects\Job Tracker\`
- `C:\Users\justing\PycharmProjects\Phoenix_CAD_Tool\`
- `C:\Users\justing\PycharmProjects\Phoenix-Checkout-Tool\`
- `C:\Users\justing\PycharmProjects\ValveMasterTool\`

No production-tool source files were read during Phase 5B either.
phoenix-commons saw one diff during Phase 5B (this report); no
phoenix-commons source files (`src/phoenix_commons/...`, `tests/`,
`pyproject.toml`, etc.) were modified.

## 15. Confirmation: no PyInstaller / Inno / build / release / updater commands ran

Confirmed.

- No `pyinstaller …`
- No `iscc.exe …`
- No `build.bat`
- No `installer.iss` compilation
- No `gh release …`
- No `git push`
- No real updater download/apply against a live release
- No retrofit work on Phoenix CAD / Job Tracker / Checkout / ValveMaster

Subprocesses Phase 5B ran:

- `python -m compileall -q .` (×4 — Command Center plus the three
  scratch scaffolds)
- `QT_QPA_PLATFORM=offscreen python -m pytest -q tests/` (×3 — one per
  scratch scaffold)
- `git init`, `git add -A`, `git commit`, `git submodule add` (×6 total,
  inside the Test B-with scratch tool's own repo, all with
  `-c protocol.file.allow=always` for the local-URL workaround)
- `git status / log / diff / add / commit / check-ignore` for
  bookkeeping on phoenix-command-center and phoenix-commons.

## 16. Confirmation: Phase 6 was not started

Confirmed.

- No dogfood Phoenix tool was built into a `dist/` folder.
- No PyInstaller invocation against any scaffolded tool.
- No Inno Setup installer compiled or installed.
- No `%LOCALAPPDATA%\ATS Inc\phoenix-test-tool\` install path created.
- Phase 6 todo remains `pending`.

The Test B-with scratch tool exists on disk (with a `.git/` and a
`commons/` submodule checkout), but it was only exercised in source
mode — `compileall` and `pytest` — never built or installed.

## 17. Recommendation for Phase 6 or not

**Approve Phase 6** with the same external-build constraint that
protected Phase 4B-local.

Phase 5B is complete and self-contained:

- The Phase 5A UX gap is closed by construction — the broken-tool
  combo now requires the user to explicitly opt out (uncheck a box
  that auto-checks itself), at which point the wizard tells them
  in-band (inline ⚠ warning) and at create time (next-steps list)
  exactly what to do.
- Standalone behaviour is unchanged.
- Commons-backed is still NOT the default — the radio is still
  gated on `commons_path` being set, and the AV-caveat note next to
  it is unchanged from Phase 5.
- No claims about frozen-exe runtime — the frozen-exe gate is still
  open from Phase 4B-local.

Phase 6 scope reminder (unchanged from the original plan):

1. Pick the **standalone** scratch scaffold (the safe default; commons-
   backed frozen-exe is still gated on AV).
2. Land under `%LOCALAPPDATA%\ATS Inc\PhoenixScaffold6\` so the
   external-build hygiene from Phase 4B-local stays intact.
3. `pip install -r requirements.txt` + `-r requirements-dev.txt`,
   smoke-test from source, then `build.bat` → `dist\…\<exe>.exe`.
4. Run Inno Setup against `installer.iss` → `dist\<…>Setup.exe`.
   Install locally to `%LOCALAPPDATA%\ATS Inc\…`.
5. Confirm the installed exe launches themed; confirm
   `%APPDATA%\ATS Inc\…` got created; confirm no production tool
   source files changed.
6. If the AV blocker fires for the standalone exe too, accept Phase 6
   as Partial — same shape as Phase 4B-local — and the commons-backed
   default stays deferred.

Phase 6 awaiting go/no-go.
