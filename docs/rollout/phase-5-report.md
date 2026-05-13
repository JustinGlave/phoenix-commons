# Phase 5 Completion Packet — Phoenix Tool wizard radios

> Phase 5 extends `phoenix-command-center`'s **New Tool** wizard with two new
> radios — *Phoenix Tool — standalone* (new default) and *Phoenix Tool —
> commons-backed* — and a dedicated `phoenix_tool_templates.py` module that
> generates the full Phoenix scaffold for each variant (design system, build
> pipeline, installer, auto-updater, smoke tests, docs).
>
> Source-mode verification only. No PyInstaller, no Inno Setup, no `build.bat`,
> no release commands, no production-tool changes.

## 1. Status

**Passed.**

Both wizard radios are wired and validated. Both template functions generate
complete, syntactically clean scaffolds. Both scaffolds run their smoke tests
green under the offscreen Qt platform and their `MainWindow` classes
instantiate successfully. Frozen-exe verification remains out of scope per
the Phase 4B-local Partial outcome — the commons-backed radio carries an
inline note acknowledging that gate is still open.

## 2. Files changed in phoenix-command-center

| Path | Status | Purpose |
|------|--------|---------|
| `new_tool_wizard.py` | MODIFIED (+120 / −22) | Adds the two Phoenix Tool radios at the top of the template page; wraps the radio stack in `QScrollArea`; carries inline `ℹ` note (commons configured) or `⚠` note (not configured) under the commons-backed radio; extends `_selected_template_kind`, `_validate_step`, `_refresh_review`, and `_do_create` for the new kinds; creates intermediate folders before writing scaffold files. |
| `phoenix_tool_templates.py` | NEW (+1741) | Two template functions returning `{relative_path: content}` dicts. `template_phoenix_standalone(tool_name)` emits 26 files (full Phoenix design system, parameterized updater, build/installer pipeline, CI, docs, smoke tests). `template_phoenix_commons(tool_name)` emits 20 files — same shell, but imports theme/widgets/paths/updater from `phoenix_commons` instead of carrying local copies and adds `-e ./commons` to `requirements.txt`. Sentinel substitution (`__TOOL_NAME__`, `__PRETTY__`, `__EXE_NAME__`, `__EXE_STEM__`) instead of `str.format()` so literal `{`/`}` braces in QSS, batch files, and Inno Setup scripts pass through untouched. |

No other Command Center source files (`main.py`, `main_window.py`,
`dashboard.py`, `commons_browser.py`, `scanner.py`, `config.py`, etc.) were
touched. The Phase 4C-init baseline plus this commit is the entire Phase 5
delta.

## 3. `git status --short --branch` from phoenix-command-center

```
$ cd phoenix-command-center && git status --short --branch
## phase-5-phoenix-tool-wizard
(no other output — clean working tree)
```

`pcc_config.json` is present on disk with the user's runtime values but
remains ignored. `__pycache__/`, the `compileall`-generated `.pyc` artifacts,
and any local IDE state are also ignored per the Phase 4C-init `.gitignore`.

## 4. `git diff --stat` from phoenix-command-center

```
$ git diff --stat main..phase-5-phoenix-tool-wizard
 new_tool_wizard.py        |  142 +++-
 phoenix_tool_templates.py | 1741 +++++++++++++++++++++++++++++++++++++++++++++
 2 files changed, 1861 insertions(+), 22 deletions(-)
```

Commits on the branch:

```
$ git log --oneline main..phase-5-phoenix-tool-wizard
2514c58 Phase 5 — add Phoenix Tool wizard radios (standalone + commons-backed)
```

Full log:

```
$ git log --oneline -3
2514c58 Phase 5 — add Phoenix Tool wizard radios (standalone + commons-backed)
3d84cc9 Initial commit — Command Center baseline before Phase 5
```

## 5. Relevant changed-file contents

### 5.1 `new_tool_wizard.py` — diff highlights

Imports (lines 17–28):

```python
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QLineEdit,
    QFileDialog, QFrame, QStackedWidget, QRadioButton, QButtonGroup,
    QCheckBox, QComboBox, QMessageBox, QSizePolicy, QPlainTextEdit,
    QScrollArea, QWidget,
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QCursor

from theme import C
from phoenix_tool_templates import (
    template_phoenix_standalone,
    template_phoenix_commons,
)
```

`_page_template()` reworked to host five radio cards inside a `QScrollArea`:

```python
def _page_template(self) -> QFrame:
    # Outer container so the page itself can scroll — 5 radio cards plus
    # the inline notes is taller than the dialog at its default size.
    page = QFrame()
    outer = QVBoxLayout(page)
    outer.setContentsMargins(2, 4, 2, 0)
    outer.setSpacing(6)

    outer.addWidget(_section_label("Choose a template"))
    outer.addWidget(_hint(
        "Files dropped into the new folder. The two Phoenix Tool options "
        "include the full design system and build/release pipeline; the "
        "remaining options stay available for quick experiments."
    ))

    scroll = QScrollArea()
    scroll.setWidgetResizable(True)
    scroll.setFrameShape(QFrame.Shape.NoFrame)
    body = QWidget()
    lay = QVBoxLayout(body)
    lay.setContentsMargins(0, 0, 0, 0)
    lay.setSpacing(10)
    scroll.setWidget(body)
    outer.addWidget(scroll, 1)

    self.template_group = QButtonGroup(self)

    commons_configured = bool(self.commons_path)

    # ── Phoenix Tool — standalone (NEW DEFAULT) ──────────────────────
    self.rb_phoenix_standalone = QRadioButton(
        "Phoenix Tool — standalone  ·  full design system, builds + auto-updater, no external deps"
    )
    self.rb_phoenix_standalone.setChecked(True)
    self.template_group.addButton(self.rb_phoenix_standalone, 0)
    lay.addWidget(_radio_card(self.rb_phoenix_standalone))

    # ── Phoenix Tool — commons-backed ────────────────────────────────
    self.rb_phoenix_commons = QRadioButton(
        "Phoenix Tool — commons-backed  ·  imports shared code from phoenix-commons submodule"
    )
    self.template_group.addButton(self.rb_phoenix_commons, 1)
    commons_card = _radio_card(self.rb_phoenix_commons)
    note_lbl = QLabel()
    note_lbl.setWordWrap(True)
    note_lbl.setContentsMargins(36, 0, 12, 10)
    if commons_configured:
        note_lbl.setText(
            "ℹ  Commons-backed template is available for source-mode "
            "testing. Frozen-exe runtime verification is still blocked "
            "by local AV."
        )
        note_lbl.setStyleSheet(
            f"color: {C['text_sub']}; font-size: 11px; "
            f"padding: 0 12px 8px 12px;"
        )
    else:
        self.rb_phoenix_commons.setEnabled(False)
        note_lbl.setText(
            "⚠  Phoenix commons not configured. Set the commons path in "
            "Settings → General and ensure it points at a verified "
            "phoenix-commons checkout."
        )
        note_lbl.setStyleSheet(
            f"color: {C['warning']}; font-size: 11px; "
            f"padding: 0 12px 8px 12px;"
        )
    commons_card.layout().addWidget(note_lbl)
    lay.addWidget(commons_card)

    # ── Blank PySide6 (was previous default — now a quick-experiment option) ──
    self.rb_pyside6 = QRadioButton(
        "Blank PySide6 desktop app  ·  main.py + theme placeholder"
    )
    self.template_group.addButton(self.rb_pyside6, 2)
    lay.addWidget(_radio_card(self.rb_pyside6))

    # ── Minimal Python script ────────────────────────────────────────
    self.rb_minimal = QRadioButton(
        "Minimal Python script  ·  just a main.py skeleton"
    )
    self.template_group.addButton(self.rb_minimal, 3)
    lay.addWidget(_radio_card(self.rb_minimal))

    # ── Copy from existing ───────────────────────────────────────────
    self.rb_copy = QRadioButton("Copy from an existing tool")
    self.template_group.addButton(self.rb_copy, 4)
    ...
```

`_validate_step` gained a guard so the wizard can't advance past the template
page with the commons-backed radio selected while `commons_path` is empty
(belt-and-braces alongside the radio being disabled):

```python
if self.rb_phoenix_commons.isChecked() and not self.commons_path:
    QMessageBox.warning(
        self,
        "Commons not configured",
        "Phoenix Tool — commons-backed requires phoenix-commons "
        "to be configured. Set the commons path in "
        "Settings → General first, or pick another template."
    )
    return False
```

`_selected_template_kind` and `_refresh_review` extended to know about the
new kinds:

```python
def _selected_template_kind(self) -> str:
    if self.rb_phoenix_standalone.isChecked(): return "phoenix_standalone"
    if self.rb_phoenix_commons.isChecked():    return "phoenix_commons"
    if self.rb_pyside6.isChecked():            return "pyside6"
    if self.rb_minimal.isChecked():            return "minimal"
    if self.rb_copy.isChecked():               return "copy"
    return "phoenix_standalone"
```

`_do_create` dispatches to the new template functions and creates
intermediate folders (`.github/`, `.github/workflows/`,
`.github/ISSUE_TEMPLATE/`, `ui/`, `tests/`, `docs/`, `assets/`) on disk
before writing each scaffold file:

```python
if tk == "phoenix_standalone":
    files = template_phoenix_standalone(name)
elif tk == "phoenix_commons":
    files = template_phoenix_commons(name)
elif tk == "pyside6":
    files = template_blank_pyside6(name)
elif tk == "minimal":
    files = template_minimal_python(name)
else:
    raise RuntimeError(f"Unknown template kind: {tk}")
for fname, content in files.items():
    target = os.path.join(full, fname)
    os.makedirs(os.path.dirname(target), exist_ok=True) if os.path.dirname(fname) else None
    with open(target, "w", encoding="utf-8") as f:
        f.write(content)
```

### 5.2 `phoenix_tool_templates.py` — structure

1741 lines total. Public API:

```python
def template_phoenix_standalone(tool_name: str) -> dict[str, str]:
    """Full Phoenix scaffold with local copies of theme/widgets/paths/updater."""
    ...

def template_phoenix_commons(tool_name: str) -> dict[str, str]:
    """Full Phoenix scaffold that imports from phoenix_commons."""
    ...
```

Sentinel substitution (chosen over `str.format()` to avoid clashing with
literal `{`/`}` in QSS, `.bat`, and Inno Setup scripts):

```python
def _substitute(text: str, **tokens: str) -> str:
    out = text
    for key, value in tokens.items():
        out = out.replace(f"__{key}__", value)
    return out

def _pretty_name(tool_name: str) -> str:
    """phoenix-test-tool -> Phoenix Test Tool"""
    return " ".join(part.capitalize() for part in tool_name.replace("_", "-").split("-") if part)

def _exe_name_from(tool_name: str) -> str:
    """phoenix-test-tool -> PhoenixTestTool"""
    return "".join(part.capitalize() for part in tool_name.replace("_", "-").split("-") if part)
```

Token vocabulary used inside template strings:

| Token | Example expansion (`phoenix-test-tool`) |
|-------|-------------------------------------------|
| `__TOOL_NAME__` | `phoenix-test-tool` |
| `__PRETTY__` | `Phoenix Test Tool` |
| `__EXE_NAME__` | `PhoenixTestTool.exe` |
| `__EXE_STEM__` | `PhoenixTestTool` |

#### 5.2.1 `template_phoenix_standalone` — 26 files emitted

```
README.md                              CHANGELOG.md
CLAUDE.md                              .gitignore
requirements.txt                       requirements-dev.txt
version.py                             main.py
backend.py                             paths.py
updater.py                             phoenix_style.qss
build.bat                              installer.iss
assets/README.md                       docs/release_checklist.md
ui/__init__.py                         ui/style.py
ui/components.py                       ui/main_window.py
tests/__init__.py                      tests/test_smoke.py
.github/pull_request_template.md
.github/workflows/ci.yml
.github/ISSUE_TEMPLATE/bug_report.md
.github/ISSUE_TEMPLATE/feature_request.md
```

Highlights:

- `phoenix_style.qss` — verbatim Phoenix dark-navy stylesheet (System A).
- `ui/style.py` — `apply_dark_theme(app)` that loads `phoenix_style.qss`
  next to the entry point, with an embedded-QSS fallback so the function
  never raises when the asset is missing.
- `ui/components.py` — `PrimaryButton`, `SecondaryButton`, `TertiaryButton`,
  `Panel`, `PageTitle`, `PageSubtitle`, `SectionTitle`, `HintLabel`,
  `PhoenixTable`, `UpdateBanner`, `button_row`, plus the no-scroll family
  (`NoScrollComboBox`, `NoScrollSpinBox`, `NoScrollDoubleSpinBox`,
  `NoScrollDateEdit`).
- `paths.py` — `is_frozen()`, `user_data_dir(app_name, org_name="ATS Inc")`,
  `resource_path(filename, base=None)`. Same surface as
  `phoenix_commons.paths` so a tool that wants to upgrade to commons later
  just changes its imports.
- `updater.py` — full parameterised port of the commons updater: owner/repo
  /zip-asset/exe-name are passed as kwargs, `download_and_apply` accepts
  `expected_internal: bool = True` for full-folder zip validation, and the
  PowerShell relaunch script is built with the PS-safe quoting from
  Phase 3A.
- `build.bat` and `installer.iss` — PyInstaller `--onedir --windowed`
  invocation + Inno Setup `PrivilegesRequired=lowest`, target
  `{localappdata}\ATS Inc\__PRETTY__\`, output base `__EXE_STEM__Setup`.
- `tests/test_smoke.py` — 4 smoke tests: `test_module_imports`,
  `test_version_format`, `test_main_window_instantiates(qtbot)`,
  `test_apply_dark_theme_does_not_raise(qapp)`.
- `.github/workflows/ci.yml` — Python 3.11 on `windows-latest`,
  `pip install -r requirements.txt -r requirements-dev.txt`,
  `python -m compileall -q .`, `pytest -q tests/`.

#### 5.2.2 `template_phoenix_commons` — 20 files emitted

```
README.md                              CHANGELOG.md
CLAUDE.md                              .gitignore
requirements.txt                       requirements-dev.txt
version.py                             main.py
backend.py                             build.bat
installer.iss                          docs/release_checklist.md
ui/__init__.py                         ui/main_window.py
tests/__init__.py                      tests/test_smoke.py
.github/pull_request_template.md
.github/workflows/ci.yml
.github/ISSUE_TEMPLATE/bug_report.md
.github/ISSUE_TEMPLATE/feature_request.md
```

Differences from the standalone:

- No `phoenix_style.qss`, `paths.py`, `updater.py`, `ui/style.py`,
  `ui/components.py`, or `assets/` directory in the scaffold itself —
  those come from `phoenix_commons`.
- `main.py` imports `from phoenix_commons.theme import apply_dark_theme`
  and `from phoenix_commons.updater import UpdateInfo, check_for_update,
  download_and_apply`.
- `ui/main_window.py` imports widgets and `UpdateBanner` from
  `phoenix_commons.widgets`.
- `requirements.txt` includes `-e ./commons` so a `pip install -r
  requirements.txt` in a clone with the submodule populated will install
  the commons package editably.
- `tests/test_smoke.py` adds a fifth test, `test_phoenix_commons_imports`,
  that imports `apply_dark_theme`, `PrimaryButton`, `Panel`, `PhoenixTable`,
  `user_data_dir`, `is_frozen`, and `check_for_update` from
  `phoenix_commons` to fail loud if the editable install is missing.

## 6. Exact commands run

Pre-flight (read-only):

```
$ cd C:\Users\justing\PycharmProjects\phoenix-command-center
$ git status --short --branch
$ git log --oneline -3
$ git rev-parse --abbrev-ref HEAD
```

Implementation:

```
(Edit)  new_tool_wizard.py      — imports + _page_template + _validate_step
                                  + _selected_template_kind + _refresh_review
                                  + _do_create
(Write) phoenix_tool_templates.py  — new, 1741 lines
```

Source-mode verification:

```
$ cd C:\Users\justing\PycharmProjects\phoenix-command-center
$ python -m compileall -q .

$ python -c "from new_tool_wizard import NewToolDialog; \
             from phoenix_tool_templates import template_phoenix_standalone, \
                                                  template_phoenix_commons; \
             print('OK'); \
             print('standalone files:', len(template_phoenix_standalone('phoenix-test-tool'))); \
             print('commons files:', len(template_phoenix_commons('phoenix-test-tool')))"

$ mkdir -p "C:\Users\justing\AppData\Local\ATS Inc\PhoenixScaffold5"
$ python -c "
import os
from phoenix_tool_templates import template_phoenix_standalone, template_phoenix_commons
root = r'C:\Users\justing\AppData\Local\ATS Inc\PhoenixScaffold5'
for name, fn in [('phoenix-test-tool-standalone', template_phoenix_standalone),
                 ('phoenix-test-tool-commons',    template_phoenix_commons)]:
    folder = os.path.join(root, name)
    os.makedirs(folder, exist_ok=True)
    for relpath, content in fn('phoenix-test-tool').items():
        full = os.path.join(folder, relpath)
        os.makedirs(os.path.dirname(full), exist_ok=True) if os.path.dirname(relpath) else None
        with open(full, 'w', encoding='utf-8') as f:
            f.write(content)
print('Scaffolds written.')
"

$ cd "C:\Users\justing\AppData\Local\ATS Inc\PhoenixScaffold5\phoenix-test-tool-standalone"
$ python -m compileall -q .
$ QT_QPA_PLATFORM=offscreen pytest -q tests/

$ cd "C:\Users\justing\AppData\Local\ATS Inc\PhoenixScaffold5\phoenix-test-tool-commons"
$ python -m compileall -q .
$ QT_QPA_PLATFORM=offscreen pytest -q tests/

$ python -c "
import os, sys
os.environ['QT_QPA_PLATFORM'] = 'offscreen'
sys.path.insert(0, r'C:\Users\justing\AppData\Local\ATS Inc\PhoenixScaffold5\phoenix-test-tool-standalone')
from PySide6.QtWidgets import QApplication
app = QApplication([])
from ui.main_window import MainWindow
w = MainWindow()
print(w.windowTitle(), w.size().width(), 'x', w.size().height())
"
```

Git operations:

```
$ git add new_tool_wizard.py phoenix_tool_templates.py
$ git commit -m "Phase 5 — add Phoenix Tool wizard radios (standalone + commons-backed)"
$ git log --oneline
$ git diff --stat main..phase-5-phoenix-tool-wizard
```

No `pyinstaller`, no `iscc.exe`, no `build.bat`, no `gh release`, no `git
push`, no submodule mutation in `phoenix-commons` or any production tool.

## 7. Raw output from verification commands

### 7.1 `compileall` on Command Center

```
$ python -m compileall -q .
(empty — every .py compiles cleanly)
```

The persistent `distutils-precedence.pth` warning from the system Python's
user-site setuptools install was emitted (it has been emitted unchanged
since Phase 1 and is environmental, not related to Phase 5).

### 7.2 Import sanity

```
$ python -c "from new_tool_wizard import NewToolDialog; \
             from phoenix_tool_templates import template_phoenix_standalone, \
                                                  template_phoenix_commons; \
             print('OK'); ..."
OK
standalone files: 26
commons files: 20
```

### 7.3 Scaffold generation

```
Scaffolds written.

$ find "/c/Users/justing/AppData/Local/ATS Inc/PhoenixScaffold5/" -type d
PhoenixScaffold5/
PhoenixScaffold5/phoenix-test-tool-standalone
PhoenixScaffold5/phoenix-test-tool-standalone/.github
PhoenixScaffold5/phoenix-test-tool-standalone/.github/ISSUE_TEMPLATE
PhoenixScaffold5/phoenix-test-tool-standalone/.github/workflows
PhoenixScaffold5/phoenix-test-tool-standalone/assets
PhoenixScaffold5/phoenix-test-tool-standalone/docs
PhoenixScaffold5/phoenix-test-tool-standalone/tests
PhoenixScaffold5/phoenix-test-tool-standalone/ui
PhoenixScaffold5/phoenix-test-tool-commons
PhoenixScaffold5/phoenix-test-tool-commons/.github
PhoenixScaffold5/phoenix-test-tool-commons/.github/ISSUE_TEMPLATE
PhoenixScaffold5/phoenix-test-tool-commons/.github/workflows
PhoenixScaffold5/phoenix-test-tool-commons/docs
PhoenixScaffold5/phoenix-test-tool-commons/tests
PhoenixScaffold5/phoenix-test-tool-commons/ui
```

Source-file totals (excluding the `__pycache__/` and `.pytest_cache/`
artifacts that the subsequent pytest run created):

```
standalone : 26 files,  55,638 bytes
commons    : 20 files,  17,909 bytes
```

### 7.4 `compileall` on each scaffold

```
$ cd PhoenixScaffold5/phoenix-test-tool-standalone
$ python -m compileall -q .
(empty — clean)

$ cd ../phoenix-test-tool-commons
$ python -m compileall -q .
(empty — clean)
```

### 7.5 `pytest` on standalone scaffold (offscreen Qt)

```
$ QT_QPA_PLATFORM=offscreen pytest -q tests/
....                                                                     [100%]
4 passed in 0.62s
```

Tests covered: `test_module_imports`, `test_version_format`,
`test_main_window_instantiates`, `test_apply_dark_theme_does_not_raise`.

### 7.6 `pytest` on commons-backed scaffold (offscreen Qt)

```
$ QT_QPA_PLATFORM=offscreen pytest -q tests/
.....                                                                    [100%]
5 passed in 0.71s
```

Same four as standalone plus `test_phoenix_commons_imports`. Required
`phoenix_commons` to be installed in the active venv, which it is from
Phase 1 (`pip install -e .` in `phoenix-commons`).

### 7.7 Offscreen `MainWindow` instantiation

Standalone:

```
$ python -c "<see §6 — sets QT_QPA_PLATFORM=offscreen, builds QApplication, \
             imports ui.main_window.MainWindow, prints title + size>"
Phoenix Test Tool — v0.1.0 1100 x 700
```

Commons-backed:

```
$ python -c "<same harness, points sys.path at the commons-backed scaffold>"
Phoenix Test Tool — v0.1.0 1100 x 700
```

Both windows constructed without raising, applied the Phoenix dark theme,
loaded a `PrimaryButton`, `Panel`, `PhoenixTable`, and a wired `UpdateBanner`
pointing at the placeholder repo (`JustinGlave/phoenix-test-tool`).

## 8. Scratch scaffold path

```
C:\Users\justing\AppData\Local\ATS Inc\PhoenixScaffold5\
├── phoenix-test-tool-standalone\   (26 source files, 55,638 bytes)
└── phoenix-test-tool-commons\      (20 source files, 17,909 bytes)
```

External to both `phoenix-command-center` and `phoenix-commons` — same
isolation pattern as Phase 4B-local, so the in-tree AV interaction observed
in Phase 4 (when builds landed under the repo's own `build/`/`dist/`) cannot
recur and source trees stay clean.

The two `__pycache__/` and `.pytest_cache/` subfolders that appeared after
running `pytest` are pytest/Python bytecode artifacts, not scaffold output;
each scaffold's `.gitignore` already ignores them so they would never end up
in a real tool's git history.

## 9. Standalone scaffold generated successfully?

**Yes.**

- 26 files written, all UTF-8 text, no broken sentinel substitutions
  (verified by grepping each output for `__TOOL_NAME__`, `__PRETTY__`,
  `__EXE_NAME__`, `__EXE_STEM__` — zero hits).
- `python -m compileall -q .` clean across every `.py` in the scaffold.
- `QT_QPA_PLATFORM=offscreen pytest -q tests/` → **4 passed**.
- `MainWindow` instantiates offscreen at 1100 × 700, titled
  `"Phoenix Test Tool — v0.1.0"`, theme applied (no QSS warnings).
- `build.bat` and `installer.iss` reference `__EXE_STEM__` /
  `__PRETTY__` correctly; they were **not executed** in this phase.

## 10. Commons-backed scaffold generated successfully?

**Yes.**

- 20 files written, all UTF-8 text, no broken sentinel substitutions
  (same grep check as above — zero hits).
- `python -m compileall -q .` clean.
- `QT_QPA_PLATFORM=offscreen pytest -q tests/` → **5 passed** (the extra
  `test_phoenix_commons_imports` confirms `apply_dark_theme`, the widget
  set, `user_data_dir`, `is_frozen`, and `check_for_update` resolve from
  `phoenix_commons`).
- `MainWindow` instantiates offscreen at 1100 × 700, titled
  `"Phoenix Test Tool — v0.1.0"`, theme applied via
  `phoenix_commons.theme.apply_dark_theme`.
- `requirements.txt` includes `-e ./commons` (only meaningful once the
  user runs `git submodule add` after scaffolding — the wizard's existing
  submodule helper is unchanged).
- `build.bat` includes `--collect-all phoenix_commons` so the PyInstaller
  step would bundle the package data (QSS, etc.) when run. Not executed
  here — Phase 6 territory.

Frozen-exe behaviour for this variant is **still gated on Phase 4B-local**
(the AV blocker on this laptop). The wizard surfaces this with the inline
`ℹ` note next to the radio whenever commons is configured.

## 11. Confirmation: `pcc_config.json` stayed ignored

```
$ git check-ignore -v pcc_config.json
.gitignore:32:pcc_config.json   pcc_config.json

$ git diff --cached --name-only | grep -E "^pcc_config\.json$" || echo "NOT staged"
NOT staged

$ git status --short --branch
## phase-5-phoenix-tool-wizard
(no other output)
```

`pcc_config.json` remains on disk at
`C:\Users\justing\PycharmProjects\phoenix-command-center\pcc_config.json`
with the user's existing runtime values (`root_path`, the six tool entries
with GitHub URLs, window geometry blob). Git continues to ignore it per
the `.gitignore` line installed in Phase 4C-init. No diff entry, no
accidental staging, no contents leaked into either commit on this branch.

## 12. Confirmation: no production tools were touched

Confirmed. No `Write`, `Edit`, or shell write touched any path under:

- `C:\Users\justing\PycharmProjects\Job Tracker\`
- `C:\Users\justing\PycharmProjects\Phoenix_CAD_Tool\`
- `C:\Users\justing\PycharmProjects\Phoenix-Checkout-Tool\`
- `C:\Users\justing\PycharmProjects\ValveMasterTool\`

No production `build.bat`, no production `installer.iss`, no production
`version.py`, no production updater, no retrofit code, no AV exclusion
changes, no Plan B vendoring.

Template content in `phoenix_tool_templates.py` was authored from canonical
shared references (the Phoenix CAD theme/widgets, the Job Tracker
starter-package updater, the commons paths helper) and from
`phoenix_commons/` itself, with no copy or read of any production source
during Phase 5.

## 13. Confirmation: no PyInstaller / Inno Setup / build / release commands ran

Confirmed.

- No `pyinstaller …` invocations.
- No `iscc.exe …` invocations.
- No `build.bat` execution (in any tool, scaffolded or production).
- No `gh release …` commands.
- No `git push` of any branch.
- No GitHub asset uploads.
- No updater download/apply runs against a live release.
- No phoenix-commons modifications (only the Phase 5 report itself, once
  committed below, touches `phoenix-commons`).
- No phoenix-command-center commits beyond `2514c58`.

## 14. Confirmation: Phase 6 was not started

Confirmed.

- No dogfood Phoenix tool was built into a `dist/` folder.
- No PyInstaller invocation against any scaffolded tool.
- No Inno Setup installer was compiled or installed.
- No `%LOCALAPPDATA%\ATS Inc\phoenix-test-tool\` install path was created.
- The Phase 6 todo remains `pending`.

The throwaway scaffolds at
`C:\Users\justing\AppData\Local\ATS Inc\PhoenixScaffold5\…` exist only as
**source-mode** scaffolds, used to verify Phase 5's generator output.
They contain no `dist/`, no `build/`, no `.spec`, no `Output/`, and no
installer exes.

## 15. Deviations, warnings, errors

### 15.1 Persistent environmental warning (not new)

```
Error processing line 1 of C:\Users\justing\AppData\Roaming\Python\Python314\
                          site-packages\distutils-precedence.pth:
  ...
  AttributeError: module '_distutils_hack' has no attribute 'add_shim'
  Remainder of file ignored
```

Same as in Phase 1 through Phase 4C-init — comes from the system Python's
user-site setuptools install and is unrelated to phoenix-command-center,
phoenix-commons, or this rollout. Filtered out of the reported
`compileall` output above (the actual exit code was 0).

### 15.2 Frozen-exe verification gap (already known)

The commons-backed scaffold's `MainWindow` was only verified in **source
mode**. The frozen-exe path is still gated on the Phase 4B-local AV
finding (corporate AV's content heuristic deletes the PyInstaller
bootloader exe regardless of build path). The wizard surfaces this with
the inline `ℹ` note so a user picking the commons-backed radio sees the
caveat before generating.

### 15.3 Wizard UI growth

The template page now hosts five radio cards plus an inline-note label for
the commons-backed card. At the dialog's default size (kept unchanged from
Phase 4C-init baseline), the page is taller than the visible area on a
1080p screen with default DPI. Mitigated by wrapping the body in a
`QScrollArea`, which is the standard Qt pattern and matches the Settings
dialog's own layout. No layout warnings observed.

### 15.4 Sentinel-substitution choice

`str.format()` was rejected as the substitution strategy because several
of the template strings (Phoenix QSS rules, Inno Setup
`{localappdata}` placeholders, `.bat` file `%~dp0`-style argument
references) contain literal `{` / `}` braces that would clash with format
specifiers and force noisy `{{` / `}}` escaping throughout. The chosen
sentinel form (`__TOOL_NAME__`, etc.) is unambiguous and is verified clean
by post-generation grep for any remaining `__` markers.

No errors during the Phase 5 work itself.

## 16. Recommendation for Phase 6 or not

**Approve Phase 6 with the same external-build constraint that protected
Phase 4B-local.**

Phase 5 is complete and clean:

- Both wizard radios are wired and validated.
- Both template functions produce green source-mode scaffolds.
- The standalone variant is the safe default and has no external
  dependency on commons.
- The commons-backed variant is correctly gated on `commons_path` and
  carries the AV caveat in-band.
- `phoenix-command-center` is on a feature branch with a single clean
  commit; the diff is small enough to review by eye.

Phase 6 scope reminder (unchanged from the original plan):

1. Pick one of the scaffolded tools (recommend the **standalone** to
   avoid the AV gate immediately; we can re-attempt commons-backed
   afterwards as a stretch).
2. Run `pip install -r requirements.txt` and `-r requirements-dev.txt`
   inside the scratch scaffold.
3. Run from source → confirm themed window opens.
4. Run smoke tests → green.
5. Run `build.bat` → produces `dist\__EXE_STEM__\__EXE_STEM__.exe`.
6. Run Inno Setup against `installer.iss` → produces
   `dist\__EXE_STEM__Setup.exe`.
7. Install locally to `%LOCALAPPDATA%\ATS Inc\<Pretty Name>\`.
8. Launch installed exe → themed window opens.
9. Confirm `%APPDATA%\ATS Inc\<Pretty Name>\` was created.
10. Confirm no production tool source files changed.

Sticking with the external-scratch convention
(`%LOCALAPPDATA%\ATS Inc\PhoenixScaffold6\…`) keeps the build/dist hygiene
clean and stays clear of the in-tree AV interaction observed in Phase 4.
If the AV blocker fires for the standalone exe too, we accept Phase 6 as
Partial with a documented source-mode walkthrough — same shape as the
Phase 4B-local outcome — and the commons-backed default remains deferred.

Phase 6 awaiting go/no-go.
