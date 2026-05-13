# Phoenix Tools — Phase 1 Reports

> Both Phase 1 completion reports from the rollout session, captured together for the record.
>
> - **Report 1** — initial completion summary delivered immediately after the Phase 1 verification commands passed.
> - **Report 2** — formal completion packet requested afterwards, with raw command outputs and full file contents.
>
> Phase 1 itself created 9 new files in `phoenix-commons/` (the package skeleton). No production-tool source was touched. The canonical plan lives at `C:\Users\justing\.claude\plans\ok-now-we-have-lively-koala.md`. The Phase 0 production inventory lives at `docs/production-inventory.md` (sibling of this file).
>
> Captured 2026-05-13.

---

# Report 1 — Initial Phase 1 Completion Report

> *Delivered immediately after `pytest -q tests/` returned green. Concise summary, organised by the items you originally asked for after the phase.*

Phase 1 complete. Stopped. Reporting back:

## 1. Files created/changed

All paths under `C:\Users\justing\PycharmProjects\phoenix-commons\`:

| File | Status | Purpose |
|------|--------|---------|
| `pyproject.toml` | **NEW** | Package manifest. `setuptools` build backend, `src/` layout, `PySide6>=6.5` dep, dynamic version from `_version.py`, `[test]` extra for `pytest`, package-data declaration for future `*.qss` in `theme/` |
| `README.md` | **NEW** | Package-skeleton README. Status note (Phase 1, skeleton-only), install recipe, layout map, dev recipe, versioning policy. Explicitly notes which existing `phoenix-commons` files were NOT moved |
| `src/phoenix_commons/__init__.py` | **NEW** | Re-exports `__version__` only |
| `src/phoenix_commons/_version.py` | **NEW** | `__version__ = "0.1.0"` |
| `src/phoenix_commons/theme/__init__.py` | **NEW** | Empty stub with a docstring describing what Phase 2 will populate |
| `src/phoenix_commons/widgets/__init__.py` | **NEW** | Empty stub with a docstring describing what Phase 2 will populate |
| `src/phoenix_commons/updater/__init__.py` | **NEW** | Empty stub with a docstring describing what Phase 3 will populate; flags the updater payload asymmetry for the per-tool retrofits |
| `tests/__init__.py` | **NEW** | Empty (makes `tests/` a package for pytest discovery) |
| `tests/test_smoke.py` | **NEW** | 4 tests: package imports, version format (`X.Y.Z`), version equals `0.1.0`, submodule stubs import |

Total: **9 new files**. No existing files modified, renamed, or moved.

## 2. Diff summary

`phoenix-commons` is **not a git repository** locally — no `.git` directory exists, so there is no `git diff` to produce. This is worth flagging (see point 7 below). A best-effort tree diff:

```
phoenix-commons/
+├── pyproject.toml                             [NEW]
+├── README.md                                  [NEW]
 ├── docs/
 │   └── production-inventory.md                (from Phase 0, untouched here)
+├── src/
+│   └── phoenix_commons/
+│       ├── __init__.py                        [NEW]
+│       ├── _version.py                        [NEW]
+│       ├── theme/__init__.py                  [NEW]
+│       ├── widgets/__init__.py                [NEW]
+│       └── updater/__init__.py                [NEW]
+├── tests/
+│   ├── __init__.py                            [NEW]
+│   └── test_smoke.py                          [NEW]
 ├── Design Items/                              (existing, untouched)
 ├── AUDIT_METHODOLOGY.md                       (existing, untouched)
 ├── audit-reviewer.md                          (existing, untouched)
 └── phoenix-ui-reviewer.md                     (existing, untouched)
```

## 3. Test commands run and output

```
$ cd C:\Users\justing\PycharmProjects\phoenix-commons && python -m pip install -e .
[…]
Successfully built phoenix-commons
Installing collected packages: phoenix-commons
Successfully installed phoenix-commons-0.1.0

$ python -c "import phoenix_commons; print(phoenix_commons.__version__)"
0.1.0

$ python -c "import pytest; print('pytest', pytest.__version__)"
ModuleNotFoundError: No module named 'pytest'
$ python -m pip install pytest        # installed pytest 9.0.3
$ python -c "import pytest; print('pytest', pytest.__version__)"
pytest 9.0.3

$ cd C:\Users\justing\PycharmProjects\phoenix-commons && python -m pytest -q tests/
....                                                                     [100%]
4 passed in 0.03s
```

All three expected outcomes met: import succeeds, version prints `0.1.0`, tests pass.

## 4. Confirmation: no production tool files were changed

**Confirmed.** Phase 1 wrote only to `phoenix-commons\`. No reads or writes touched `Job Tracker`, `Phoenix_CAD_Tool`, `Phoenix-Checkout-Tool`, `ValveMasterTool`, or `phoenix-command-center`. The only side-effect outside `phoenix-commons` was `pip install pytest` to user-site (a dev dependency for running the smoke tests). PySide6 was already present from earlier in this session.

## 5. Confirmation: no existing phoenix-commons docs/assets were moved

**Confirmed.** The following existing files remain at their original repo-root paths, byte-identical:

- `AUDIT_METHODOLOGY.md`
- `audit-reviewer.md`
- `phoenix-ui-reviewer.md`
- `Design Items/` (with all subdirectories: `Phoenix_Tool_Design_V1/`, `colors/`, `Checkout_Sheets_Styled/`, and the loose `PTT*` icons)

The new `docs/` directory was created (it now contains `production-inventory.md` from Phase 0), and a new `src/` directory was created — both purely additive. Nothing in `Design Items/` was moved into `assets/` (that reorganisation is explicitly deferred per the canonical plan and your instructions).

## 6. PyInstaller smoke test

Worth noting since it's listed as part of the canonical Phase 1 verification (and was the de-risking step ChatGPT's handoff doc called out): I did **not** run the `pyinstaller --onedir --windowed --collect-all phoenix_commons` smoke test in this phase. Your specific Phase 1 instructions listed three verification commands (`pip install -e .`, the import/version check, `pytest -q tests/`) and the PyInstaller test was not among them. If you want it run as part of Phase 1 before Phase 2 begins, say the word and I'll do it (it's a quick scratch test, no production tools touched).

## 7. Additional flag — phoenix-commons is not yet a git repo

`git -C C:\Users\justing\PycharmProjects\phoenix-commons status` returned `fatal: not a git repository`. This means:

- I couldn't create a branch (the canonical plan's "create a branch first" was skipped)
- I couldn't produce a real `git diff` for this report — the tree diff above is the best I can offer
- **Critically: the eventual submodule consumption model requires this to be a published git repo**. Before Phase 5's wizard scaffolds tools that do `git submodule add <commons URL>`, `phoenix-commons` will need to be `git init`ed, committed, and pushed to GitHub.

Recommend handling that as a discrete step (you initiate the `git init` + push when ready) rather than me doing it autonomously. It doesn't block Phase 2 or 3 — those still work fine inside the unversioned local copy — but it must land before Phase 5.

## 8. Production-inventory.md for review

> The original Report 1 message included the full text of `docs/production-inventory.md` pasted inline at this point so the file could be reviewed without opening it separately.
>
> Omitted from this combined report to avoid duplication — the canonical file is at `phoenix-commons/docs/production-inventory.md` (sibling of this file). It contains:
>
> - Summary table — one row per tool (display name, exe, install path, version)
> - Per-tool detail blocks — Job Tracker, Phoenix_CAD_Tool, Phoenix-Checkout-Tool, ValveMasterTool, phoenix-command-center (each with the 15-column schema specified in the canonical plan, including "Evidence files checked" and "Unknowns / needs verification")
> - **Critical asymmetry to plan around** — the discovery that Job Tracker + Phoenix CAD ship full-folder updater zips while Phoenix Checkout + ValveMaster ship exe-only updater zips (drives the `expected_internal` kwarg in commons)
> - Conventions confirmed across all four production tools
> - Per-tool divergences (Phoenix Checkout repo CamelCase, ValveMaster's unique AppId GUID, etc.)
> - Open items beyond the inventory rows (6 follow-ups for Phase 1+)
> - File-write summary

Standing by for review and go/no-go on Phase 2.

---

# Report 2 — Phase 1 Completion Packet

> *Delivered after Report 1, in response to the formal request for: files created or changed, raw git output, full diff or full file contents, exact commands, raw verification output, explicit no-change confirmations, and any deviations.*

## 1. Files created or changed

### Files I authored (9 + Phase 0 inventory)

All paths under `C:\Users\justing\PycharmProjects\phoenix-commons\`:

| # | Path | Status |
|---|------|--------|
| 1 | `pyproject.toml` | NEW |
| 2 | `README.md` | NEW |
| 3 | `src/phoenix_commons/__init__.py` | NEW |
| 4 | `src/phoenix_commons/_version.py` | NEW |
| 5 | `src/phoenix_commons/theme/__init__.py` | NEW |
| 6 | `src/phoenix_commons/widgets/__init__.py` | NEW |
| 7 | `src/phoenix_commons/updater/__init__.py` | NEW |
| 8 | `tests/__init__.py` | NEW (empty) |
| 9 | `tests/test_smoke.py` | NEW |
| — | `docs/production-inventory.md` | from Phase 0, **untouched in Phase 1** |

### Tool-generated side-effects (pip + pytest auto-created these — I did NOT author them)

These appeared as a result of running `pip install -e .` and `pytest -q tests/`. They'd normally be `.gitignore`d. Listing them for full disclosure:

| Path | Created by |
|------|------------|
| `src/phoenix_commons.egg-info/PKG-INFO` | `pip install -e .` |
| `src/phoenix_commons.egg-info/dependency_links.txt` | `pip install -e .` |
| `src/phoenix_commons.egg-info/requires.txt` | `pip install -e .` |
| `src/phoenix_commons.egg-info/top_level.txt` | `pip install -e .` |
| `src/phoenix_commons.egg-info/SOURCES.txt` | `pip install -e .` |
| `src/phoenix_commons/__pycache__/` (2 .pyc) | Python import |
| `src/phoenix_commons/theme/__pycache__/` (1 .pyc) | Python import |
| `src/phoenix_commons/widgets/__pycache__/` (1 .pyc) | Python import |
| `src/phoenix_commons/updater/__pycache__/` (1 .pyc) | Python import |
| `tests/__pycache__/` (2 .pyc) | pytest |
| `.pytest_cache/` (README.md, .gitignore, CACHEDIR.TAG, v/cache/nodeids) | pytest |

These should be added to `.gitignore` when `phoenix-commons` is initialized as a git repo (see Section 9, deviation #1).

---

## 2. `git status --short`

```
$ git -C "C:\Users\justing\PycharmProjects\phoenix-commons" status --short
fatal: not a git repository (or any of the parent directories): .git
$ echo $?
128
```

`phoenix-commons` is **not yet a git repository.** See Section 9, deviation #1.

---

## 3. `git diff --stat`

```
$ git -C "C:\Users\justing\PycharmProjects\phoenix-commons" diff --stat
warning: Not a git repository. Use --no-index to compare two paths outside a working tree
usage: git diff --no-index [<options>] <path> <path> [<pathspec>...]
[…usage text elided…]
$ echo $?
129
```

Same root cause: no `.git`. Cannot produce a real diff.

---

## 4. Full contents of each new file

### `pyproject.toml`

```toml
[build-system]
requires = ["setuptools>=61", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "phoenix-commons"
description = "Shared design system, widgets, auto-updater, and utilities for the Phoenix Controls family of PySide6 desktop tools."
readme = "README.md"
authors = [{ name = "Justin Glave" }]
requires-python = ">=3.10"
dynamic = ["version"]
dependencies = [
    "PySide6>=6.5",
]

[project.optional-dependencies]
test = [
    "pytest>=7",
]

[project.urls]
Homepage = "https://github.com/JustinGlave/phoenix-commons"

[tool.setuptools.dynamic]
version = { attr = "phoenix_commons._version.__version__" }

[tool.setuptools.packages.find]
where = ["src"]

# Phase 2 will add phoenix_style.qss under phoenix_commons/theme/.
# Declare it ahead of time so the package picks it up on install.
[tool.setuptools.package-data]
"phoenix_commons.theme" = ["*.qss"]
```

### `README.md`

````markdown
# phoenix-commons

Shared design system, widgets, auto-updater, and utilities for the Phoenix Controls family of PySide6 desktop tools.

## Status

**Phase 1 — skeleton.** The package installs and imports but ships no behaviour yet. Theme + widgets land in Phase 2; paths + updater land in Phase 3.

The canonical rollout plan lives at `C:\Users\justing\.claude\plans\ok-now-we-have-lively-koala.md`. The frozen production-tool inventory is at `docs/production-inventory.md`.

## Install (development)

From a Phoenix tool repo that will eventually add this as a git submodule at `./commons`:

```
pip install -e ./commons
```

For now (Phase 1), `phoenix_commons` exposes only `__version__`. Real public API arrives in Phases 2–3:

```python
from phoenix_commons import __version__
```

## Layout

```
phoenix-commons/
├── pyproject.toml                 — package manifest
├── README.md                      — this file
├── src/phoenix_commons/           — the installable package
│   ├── theme/                     — apply_dark_theme + phoenix_style.qss   (Phase 2)
│   ├── widgets/                   — buttons, panel, table, banner, …       (Phase 2)
│   ├── updater/                   — GitHub Releases auto-updater          (Phase 3)
│   └── paths.py                   — user_data_dir, is_frozen, resource    (Phase 3)
├── tests/                         — smoke tests
├── docs/
│   └── production-inventory.md    — frozen snapshot of every deployed tool's identity, paths, build, and updater contract (Phase 0)
├── Design Items/                  — existing design references (will move to docs/ + assets/ later, not in this rollout)
├── AUDIT_METHODOLOGY.md           — existing audit methodology doc (unmoved)
├── audit-reviewer.md              — existing audit reviewer doc (unmoved)
└── phoenix-ui-reviewer.md         — existing UI reviewer doc (unmoved)
```

## Development

```
pip install -e .
pip install -e .[test]   # adds pytest
pytest -q tests/
```

## Versioning

Tracked in `src/phoenix_commons/_version.py`. Bump alongside any change to the public API.
````

### `src/phoenix_commons/__init__.py`

```python
"""phoenix-commons — shared design system + utilities for Phoenix Controls tools.

Phase 1 skeleton: only `__version__` is exported. Theme, widgets, updater, and
paths arrive in subsequent phases (see the canonical rollout plan).
"""

from phoenix_commons._version import __version__

__all__ = ["__version__"]
```

### `src/phoenix_commons/_version.py`

```python
# Bump this alongside any change to the phoenix-commons public API.
# Format: MAJOR.MINOR.PATCH (matches the convention used by all Phoenix tools).
#   MAJOR — breaking changes to the commons API
#   MINOR — new exports, additive widgets, new functionality
#   PATCH — internal fixes, no API change
__version__ = "0.1.0"
```

### `src/phoenix_commons/theme/__init__.py`

```python
"""Theme — Phoenix design system loader.

Phase 2 will populate this with `apply_dark_theme(app)`, `phoenix_style.qss`,
and the embedded-QSS fallback string. Ported from
`Phoenix_CAD_Tool/ui/style.py:21-829`.
"""
```

### `src/phoenix_commons/widgets/__init__.py`

```python
"""Widgets — Phoenix Controls component helpers shared across the ATS app suite.

Use these instead of raw Qt widgets so every tool reads as one product.

Phase 2 will populate this with: `PrimaryButton`, `SecondaryButton`,
`TertiaryButton`, `PageTitle`, `PageSubtitle`, `SectionTitle`, `HintLabel`,
`Panel`, `PhoenixTable`, `UpdateBanner`, `button_row`, plus the `no_scroll`
submodule (`NoScrollComboBox`, `NoScrollSpinBox`, `NoScrollDoubleSpinBox`,
`NoScrollDateEdit`). Ported from `Phoenix_CAD_Tool/ui/components.py:57-263`.
"""
```

### `src/phoenix_commons/updater/__init__.py`

```python
"""Updater — GitHub-Releases-based auto-update for Phoenix tools.

Phase 3 will populate this with:
- `check_for_update(owner, repo, current_version, zip_asset_name) -> UpdateInfo | None`
- `download_and_apply(info, exe_name, *, expected_internal=True, progress_callback=None) -> None`
- `UpdateInfo` dataclass
- `qt.UpdateCheckThread` — QThread wrapper for use from a GUI

Ported (parameterized as kwargs) from
`Job Tracker/starter_package/updater.py:60-188` and
`Job Tracker/starter_package/app_gui.py:52-58`.

The `expected_internal=True` default fits the full-folder updater payload
contract used by Job Tracker and Phoenix CAD. Phoenix Checkout and ValveMaster
ship exe-only updater zips and will need to opt out via `expected_internal=False`
during their per-tool retrofits — see `docs/production-inventory.md` for the
"Critical asymmetry" details.
"""
```

### `tests/__init__.py`

```
(empty file — zero bytes)
```

### `tests/test_smoke.py`

```python
"""Smoke tests for phoenix-commons.

Phase 1 scope: only verify the package installs cleanly, reports its version
in the expected MAJOR.MINOR.PATCH format, and that the (currently empty)
submodules import without error.

Richer smoke tests (apply_dark_theme works, widgets instantiate, updater
client returns an UpdateInfo) land alongside their respective phases.
"""

from __future__ import annotations

import re


def test_package_imports() -> None:
    """phoenix_commons must be importable."""
    import phoenix_commons
    assert phoenix_commons.__version__


def test_version_format() -> None:
    """__version__ must be MAJOR.MINOR.PATCH — Phoenix tools depend on this format."""
    import phoenix_commons
    assert re.fullmatch(r"\d+\.\d+\.\d+", phoenix_commons.__version__), (
        f"Expected 3-part numeric version, got {phoenix_commons.__version__!r}"
    )


def test_version_is_0_1_0() -> None:
    """Phase 1 ships the package at 0.1.0. Bumps happen alongside API changes."""
    import phoenix_commons
    assert phoenix_commons.__version__ == "0.1.0"


def test_submodules_importable() -> None:
    """The Phase 1 submodule stubs must import cleanly even though they have no API yet."""
    from phoenix_commons import theme, widgets, updater
    assert theme is not None
    assert widgets is not None
    assert updater is not None
```

---

## 5. Exact commands run

In execution order:

```
git -C "C:\Users\justing\PycharmProjects\phoenix-commons" status --short --branch
git -C "C:\Users\justing\PycharmProjects\phoenix-commons" log -5 --oneline
                                                            # both failed: not a git repo

# Wrote the 9 files via the harness Write tool (no shell command).

cd "C:\Users\justing\PycharmProjects\phoenix-commons" && python -m pip install -e .
python -c "import phoenix_commons; print(phoenix_commons.__version__)"
python -c "import pytest; print('pytest', pytest.__version__)"
                                                            # ModuleNotFoundError
python -m pip install pytest                                # installed pytest 9.0.3
python -c "import pytest; print('pytest', pytest.__version__)"
cd "C:\Users\justing\PycharmProjects\phoenix-commons" && python -m pytest -q tests/

# Re-ran for this packet:
git -C "C:\Users\justing\PycharmProjects\phoenix-commons" status --short
git -C "C:\Users\justing\PycharmProjects\phoenix-commons" diff --stat
```

No `git init`, no `git add`, no `git commit`, no `git push`, no build/installer/release/retrofit commands.

---

## 6. Raw output

### `pip install -e .`

Output captured (tail-20 of `python -m pip install -e . 2>&1`):

```
  Checking if build backend supports build_editable: finished with status 'done'
  Getting requirements to build editable: started
  Getting requirements to build editable: finished with status 'done'
  Preparing editable metadata (pyproject.toml): started
  Preparing editable metadata (pyproject.toml): finished with status 'done'
Requirement already satisfied: PySide6>=6.5 in c:\users\justing\appdata\roaming\python\python314\site-packages (from phoenix-commons==0.1.0) (6.11.0)
Requirement already satisfied: shiboken6==6.11.0 in c:\users\justing\appdata\roaming\python\python314\site-packages (from PySide6>=6.5->phoenix-commons==0.1.0) (6.11.0)
Requirement already satisfied: PySide6_Essentials==6.11.0 in c:\users\justing\appdata\roaming\python\python314\site-packages (from PySide6>=6.5->phoenix-commons==0.1.0) (6.11.0)
Requirement already satisfied: PySide6_Addons==6.11.0 in c:\users\justing\appdata\roaming\python\python314\site-packages (from PySide6>=6.5->phoenix-commons==0.1.0) (6.11.0)
Building wheels for collected packages: phoenix-commons
  Building editable for phoenix-commons (pyproject.toml): started
  Building editable for phoenix-commons (pyproject.toml): finished with status 'done'
  Created wheel for phoenix-commons: filename=phoenix_commons-0.1.0-0.editable-py3-none-any.whl size=2409 sha256=9220595781afd5fe52b7ef9a5868c949dc9b227568fa8416a71fdf5da7aa73fe
  Stored in directory: C:\Users\justing\AppData\Local\Temp\pip-ephem-wheel-cache-mw04_pkn\wheels\ba\7d\08\b33e6f71aa52382fc16049363a06ee36f318980dc8267d39e3
Successfully built phoenix-commons
Installing collected packages: phoenix-commons
Successfully installed phoenix-commons-0.1.0

[notice] A new release of pip is available: 25.3 -> 26.1.1
[notice] To update, run: python.exe -m pip install --upgrade pip
```

### `python -c "import phoenix_commons; print(phoenix_commons.__version__)"`

```
0.1.0
```

### `pytest -q tests/`

```
....                                                                     [100%]
4 passed in 0.03s
```

---

## 7. Confirmation: no files changed in any production project

**Confirmed.** Across the entire Phase 1 session, no Write/Edit/NotebookEdit ran against any of these directories, and no shell commands ran inside them either (no `git init`, no `pip install` from within them, no file moves):

- `C:\Users\justing\PycharmProjects\Job Tracker\` — untouched
- `C:\Users\justing\PycharmProjects\Phoenix_CAD_Tool\` — untouched
- `C:\Users\justing\PycharmProjects\Phoenix-Checkout-Tool\` — untouched
- `C:\Users\justing\PycharmProjects\ValveMasterTool\` — untouched
- `C:\Users\justing\PycharmProjects\phoenix-command-center\` — untouched

The only PyCharmProjects directory touched in Phase 1 was `phoenix-commons\`, and all writes there were purely additive.

The only system-wide side effect outside `phoenix-commons` was `pip install pytest` to the user-site site-packages (per-user dev dependency, no virtualenv was active). PySide6 was already installed from earlier this session.

---

## 8. Confirmation: no existing phoenix-commons docs/assets were moved

**Confirmed.** Glob across `phoenix-commons\**\*` shows these pre-existing files still at their original paths (authoritative paths from current glob output):

```
C:\Users\justing\PycharmProjects\phoenix-commons\AUDIT_METHODOLOGY.md
C:\Users\justing\PycharmProjects\phoenix-commons\audit-reviewer.md
C:\Users\justing\PycharmProjects\phoenix-commons\phoenix-ui-reviewer.md
C:\Users\justing\PycharmProjects\phoenix-commons\Design Items\PTT Transparent.jpg
C:\Users\justing\PycharmProjects\phoenix-commons\Design Items\PTT Normal.jpg
C:\Users\justing\PycharmProjects\phoenix-commons\Design Items\PTT Transparent.ico
C:\Users\justing\PycharmProjects\phoenix-commons\Design Items\colors\blue.ico
C:\Users\justing\PycharmProjects\phoenix-commons\Design Items\colors\blue.png
C:\Users\justing\PycharmProjects\phoenix-commons\Design Items\colors\green.ico
C:\Users\justing\PycharmProjects\phoenix-commons\Design Items\colors\green.png
C:\Users\justing\PycharmProjects\phoenix-commons\Design Items\colors\Normal_red.ico
C:\Users\justing\PycharmProjects\phoenix-commons\Design Items\colors\orange.ico
C:\Users\justing\PycharmProjects\phoenix-commons\Design Items\colors\orange.png
C:\Users\justing\PycharmProjects\phoenix-commons\Design Items\colors\purple.ico
C:\Users\justing\PycharmProjects\phoenix-commons\Design Items\colors\purple.png
C:\Users\justing\PycharmProjects\phoenix-commons\Design Items\colors\red.png
C:\Users\justing\PycharmProjects\phoenix-commons\Design Items\colors\yellow.ico
C:\Users\justing\PycharmProjects\phoenix-commons\Design Items\colors\yellow.png
C:\Users\justing\PycharmProjects\phoenix-commons\Design Items\Phoenix_Tool_Design_V1\CLAUDE_STARTER_PROMPT.txt
C:\Users\justing\PycharmProjects\phoenix-commons\Design Items\Phoenix_Tool_Design_V1\INTEGRATION_GUIDE.md
C:\Users\justing\PycharmProjects\phoenix-commons\Design Items\Phoenix_Tool_Design_V1\phoenix_design_system.md
C:\Users\justing\PycharmProjects\phoenix-commons\Design Items\Phoenix_Tool_Design_V1\phoenix_implementation.py
C:\Users\justing\PycharmProjects\phoenix-commons\Design Items\Phoenix_Tool_Design_V1\phoenix_mockups.html
C:\Users\justing\PycharmProjects\phoenix-commons\Design Items\Phoenix_Tool_Design_V1\phoenix_style.qss
C:\Users\justing\PycharmProjects\phoenix-commons\Design Items\Checkout_Sheets_Styled\Phoenix_CSCP_FumeHood_Styled.xlsx
C:\Users\justing\PycharmProjects\phoenix-commons\Design Items\Checkout_Sheets_Styled\Phoenix_GEX_Styled.xlsx
C:\Users\justing\PycharmProjects\phoenix-commons\Design Items\Checkout_Sheets_Styled\Phoenix_MAV_Styled.xlsx
C:\Users\justing\PycharmProjects\phoenix-commons\Design Items\Checkout_Sheets_Styled\Phoenix_PBC_Room_Styled_2.xlsx
```

All 26 pre-existing files remain at their original paths. No `assets/` or `docs/legacy/` reorganisation was performed (deferred per the canonical plan and your explicit Phase 1 instructions). Only `docs/production-inventory.md` (Phase 0) sits alongside, also unmodified by Phase 1.

---

## 9. Errors, warnings, deviations

### Deviations

1. **`phoenix-commons` is not a git repository.** `git status --short` exits 128. This prevented branch creation (the canonical plan's "create a branch first") and prevents a real `git diff`. Discovered, not caused by Phase 1. Should be resolved before Phase 5 (the wizard scaffolds tools that `git submodule add` this repo, so it must be reachable as a git remote). Recommend: as a discrete follow-up step you initiate `git init`, set up `.gitignore` (covering `*.egg-info/`, `__pycache__/`, `.pytest_cache/`, `dist/`, `build/`, `.venv/`), commit the Phase 1 files, and push to GitHub. I have not done this autonomously.

2. **`pytest` was not preinstalled.** The verification spec listed `pytest -q tests/` as one of three commands, but `import pytest` raised `ModuleNotFoundError` on the user-site Python. I ran `python -m pip install pytest` (one extra command outside the spec). pytest 9.0.3 was installed to user-site. The smoke tests then passed cleanly. Alternative for future phases: have the wizard's commons-backed install do `pip install -e ".[test]"` to pick up the optional `[test]` extra that `pyproject.toml` already declares.

3. **PyInstaller `--collect-all` smoke test was NOT run.** The canonical plan's Phase 1 includes a "PyInstaller compatibility check" as the gate before relying on the editable-install model. Your explicit Phase 1 verification commands did NOT include it, so I followed your commands literally. **This gate is still open.** Recommend running it before Phase 5 (it's the de-risking step that determines whether Phase 4 is "all green" or "activate Plan B vendoring"). Quick scratch test, no production tools touched.

4. **`docs/` directory was created.** Phase 0 created `phoenix-commons/docs/production-inventory.md`. The parent `docs/` directory was created implicitly as part of that write. This is purely additive — no existing files were moved into it. The directory was empty before Phase 0 (it didn't exist at all).

### Warnings (cosmetic, not blocking)

- `pip` printed a `new release available` notice (25.3 → 26.1.1). I did **not** upgrade pip.
- The harness Bash tool printed `Shell cwd was reset to ...phoenix-command-center` after both `cd` calls. This is the harness's working-directory persistence model behaving as expected — no impact on the commands themselves.

### Tool-generated artifacts (called out in Section 1)

- `src/phoenix_commons.egg-info/` (5 files) — pip's editable-install metadata
- `__pycache__/` folders under each Python package — Python's bytecode cache
- `.pytest_cache/` (4 files) — pytest's cache directory
- `tests/__pycache__/` — pytest bytecode cache

None of these should be committed. They'll be in `.gitignore` once the repo is initialized.

### Errors

None. All three Phase 1 verification commands met their expected outcomes (import succeeds, version prints `0.1.0`, all 4 tests pass).

---

Phase 2 not started.
