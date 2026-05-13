# Phase 1 Completion Packet — phoenix-commons

## 1. Status

**Passed.**

phoenix-commons installs cleanly as an editable package at version 0.1.0, the `phoenix_commons` namespace plus its theme/widgets/updater submodule stubs all import without error, and all 4 smoke tests pass — with no production-tool source touched and no existing `phoenix-commons` docs/assets moved.

## 2. Files created or changed

All paths under `C:\Users\justing\PycharmProjects\phoenix-commons\`. **9 new files authored.** Zero files modified, renamed, or moved.

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

Tool-generated side-effects from `pip install -e .` and `pytest` (NOT authored by me, will be `.gitignore`d once the repo is initialized):

- `src/phoenix_commons.egg-info/` (5 metadata files)
- `__pycache__/` directories under each Python package + `tests/`
- `.pytest_cache/` (4 files)

Untouched pre-existing files: `AUDIT_METHODOLOGY.md`, `audit-reviewer.md`, `phoenix-ui-reviewer.md`, all of `Design Items/` (PTT icons, color palette, Phoenix_Tool_Design_V1 subfolder, Checkout_Sheets_Styled subfolder). Phase 0's `docs/production-inventory.md` is also untouched.

## 3. Git status

```
$ git -C "C:\Users\justing\PycharmProjects\phoenix-commons" status --short
fatal: not a git repository (or any of the parent directories): .git
$ echo $?
128
```

`phoenix-commons` is not yet a git repository locally. Recorded as a deviation in Section 9.

## 4. Diff summary

```
$ git -C "C:\Users\justing\PycharmProjects\phoenix-commons" diff --stat
warning: Not a git repository. Use --no-index to compare two paths outside a working tree
usage: git diff --no-index [<options>] <path> <path> [<pathspec>...]
[…usage text elided…]
$ echo $?
129
```

Same root cause as Section 3. Cannot produce a real diff. Full contents of each new file are included in Section 5 below.

## 5. Full diff or new file contents

No git diff is available (no `.git`). Including the full contents of each new file instead.

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

## 6. Commands run

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

# Re-ran for the completion packet:
git -C "C:\Users\justing\PycharmProjects\phoenix-commons" status --short
git -C "C:\Users\justing\PycharmProjects\phoenix-commons" diff --stat
```

No `git init`, no `git add`, no `git commit`, no `git push`, no build/installer/release/retrofit commands.

## 7. Raw command output

### `pip install -e .`

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

## 8. Safety confirmations

- **No files changed in `Job Tracker`** — confirmed. No reads or writes touched this directory.
- **No files changed in `Phoenix_CAD_Tool`** — confirmed. No reads or writes touched this directory.
- **No files changed in `Phoenix-Checkout-Tool`** — confirmed. No reads or writes touched this directory.
- **No files changed in `ValveMasterTool`** — confirmed. No reads or writes touched this directory.
- **No files changed in `phoenix-command-center`** — confirmed. No reads or writes touched this directory.
- **No existing `phoenix-commons` docs/assets were moved** — confirmed. Glob output verifies `AUDIT_METHODOLOGY.md`, `audit-reviewer.md`, `phoenix-ui-reviewer.md`, and all 23 files under `Design Items/` (PTT icons, badge color palette, `Phoenix_Tool_Design_V1/`, `Checkout_Sheets_Styled/`) remain at their original repo-root paths.
- **No production build, installer, updater, release, or retrofit steps were run** — confirmed. No `build.bat`, no `pyinstaller`, no Inno Setup, no `gh release`, no `git push`, no retrofit of any production tool.

## 9. Deviations, warnings, or errors

### Deviations from the approved Phase 1 scope

1. **`phoenix-commons` is not a git repository.** `git status` exits 128. This blocked the canonical plan's "create a branch first" step and prevented a real `git diff` for this packet. Recommended fix (you initiate when ready): `git init`, write `.gitignore` covering `*.egg-info/`, `__pycache__/`, `.pytest_cache/`, `dist/`, `build/`, `.venv/`; commit Phase 1 files; push to GitHub. Must be in place before Phase 5 (the wizard's commons-backed template scaffolds tools that `git submodule add` this repo).

2. **`pytest` was not preinstalled.** The verification spec listed `pytest -q tests/` as a verification command, but `import pytest` raised `ModuleNotFoundError`. I ran `python -m pip install pytest` (one extra command outside the spec) — pytest 9.0.3 installed to user-site. Tests then passed cleanly. Going forward, `pip install -e ".[test]"` (using the `[test]` extra already declared in `pyproject.toml`) avoids this.

3. **PyInstaller `--collect-all` smoke test was NOT run.** The canonical plan's Phase 1 includes a "PyInstaller compatibility check" as the gate before Phase 4's editable-install + PyInstaller story is relied upon. Your explicit Phase 1 verification commands listed three commands and did not include the PyInstaller test, so I followed your commands literally. This gate remains open. Quick scratch test — recommend running it before Phase 5 (will determine whether Phase 4 is "all green" or "activate Plan B vendoring").

### Warnings (cosmetic, not blocking)

- `pip` printed `new release available` notice (25.3 → 26.1.1). I did not upgrade pip.
- The harness Bash tool printed `Shell cwd was reset to ...` after each `cd` call. Harness artifact, no impact on the commands themselves.

### Tool-generated artifacts (called out in Section 2)

- `src/phoenix_commons.egg-info/` (5 files) — pip's editable-install metadata
- `__pycache__/` folders under each Python package — Python bytecode cache
- `.pytest_cache/` (4 files) — pytest cache
- `tests/__pycache__/` — pytest bytecode cache

None should be committed. They'll be `.gitignore`d once the repo is initialized.

### Errors

**None.** All three Phase 1 verification commands met expected outcomes: import succeeds, version prints `0.1.0`, all 4 tests pass.

## 10. Recommendation

**Approve Phase 2** — with two notes:

1. The PyInstaller `--collect-all phoenix_commons` smoke test (Phase 1's canonical-plan gate) is still open. It does not block Phase 2 work (theme + widgets ports are pure-Python and don't depend on the editable-install / PyInstaller story). It does need to land before Phase 4 ends and certainly before Phase 5 starts. Easiest moment to run it: right after Phase 2 lands so the test exercises both the package skeleton AND a real `apply_dark_theme()` call.

2. The `git init` step on `phoenix-commons` does not block Phase 2 either, but should land before Phase 5. If you'd like, I can prepare a tight Phase 1.5 PR — `git init`, `.gitignore`, initial commit, push to GitHub — as its own discrete approval step, or fold it into the start of Phase 5.

Phase 2 scope reminder: lift `Phoenix_CAD_Tool/ui/style.py:21-829` → `phoenix_commons/theme/{apply.py, _embedded_qss.py, phoenix_style.qss}` and `Phoenix_CAD_Tool/ui/components.py:57-263` → `phoenix_commons/widgets/{buttons, typography, panel, table, no_scroll, update_banner, helpers}.py`, verbatim copies, with a scratch script exercising `apply_dark_theme` + each widget class. **Read-only on Phoenix CAD** — only read source files there, no edits.

Awaiting Phase 2 go/no-go.
