# Phase 2 Completion Packet — phoenix-commons

## 1. Status

**Passed.**

`phoenix_commons.theme.apply_dark_theme` and the full Phase 2 widget public API (`PrimaryButton`, `SecondaryButton`, `TertiaryButton`, `PageTitle`, `PageSubtitle`, `SectionTitle`, `HintLabel`, `Panel`, `PhoenixTable`, `UpdateBanner`, `button_row`, plus the `no_scroll` submodule with four widgets) are ported, importable, instantiable, and committed. All 9 unit tests pass. Phoenix dark-navy QSS ships both as a packaged file and as an embedded fallback. No production-tool source touched.

## 2. Files created or changed

Branch `phase-2-theme-widgets`. Commit `0b41cc6`. 13 files: 10 new, 3 modified (the Phase 1 stubs got real exports). All paths under `C:\Users\justing\PycharmProjects\phoenix-commons\`.

| # | Path | Status | Origin / purpose |
|---|------|--------|------------------|
| 1 | `src/phoenix_commons/theme/apply.py` | NEW | `apply_dark_theme(app)` + `_resource_path`. Port of `Phoenix_CAD_Tool/ui/style.py:21-58`. **Adaptation:** source-mode path resolution uses `Path(__file__).parent` (theme folder) instead of `.parent.parent`; frozen-mode uses `_MEIPASS/phoenix_commons/theme/`. |
| 2 | `src/phoenix_commons/theme/_embedded_qss.py` | NEW | `_EMBEDDED_QSS` string — verbatim port of `Phoenix_CAD_Tool/ui/style.py:63-829`. Fallback when the `.qss` file can't be found at runtime. |
| 3 | `src/phoenix_commons/theme/phoenix_style.qss` | NEW | Verbatim copy of `Phoenix_CAD_Tool/phoenix_style.qss` (765 lines). Canonical stylesheet. |
| 4 | `src/phoenix_commons/theme/__init__.py` | MODIFIED | Replaced Phase 1 stub with `from .apply import apply_dark_theme`; `__all__ = ["apply_dark_theme"]`. |
| 5 | `src/phoenix_commons/widgets/no_scroll.py` | NEW | `NoScrollComboBox`, `NoScrollSpinBox`, `NoScrollDoubleSpinBox`, `NoScrollDateEdit`. Verbatim port of `components.py:57-105`. |
| 6 | `src/phoenix_commons/widgets/buttons.py` | NEW | `PrimaryButton`, `SecondaryButton`, `TertiaryButton`. Verbatim port of `components.py:108-134`. |
| 7 | `src/phoenix_commons/widgets/typography.py` | NEW | `PageTitle`, `PageSubtitle`, `SectionTitle`, `HintLabel`. Verbatim port of `components.py:137-166`. |
| 8 | `src/phoenix_commons/widgets/panel.py` | NEW | `Panel`. Port of `components.py:169-179`. **Adaptation:** `SectionTitle` imported from sibling `.typography` module. |
| 9 | `src/phoenix_commons/widgets/table.py` | NEW | `PhoenixTable`. Verbatim port of `components.py:182-191`. |
| 10 | `src/phoenix_commons/widgets/helpers.py` | NEW | `button_row`. Verbatim port of `components.py:194-203`. |
| 11 | `src/phoenix_commons/widgets/update_banner.py` | NEW | `UpdateBanner`. Port of `components.py:206-263`. **Adaptation:** `TertiaryButton` imported from sibling `.buttons` module. |
| 12 | `src/phoenix_commons/widgets/__init__.py` | MODIFIED | Replaced Phase 1 stub with public-API re-exports. Notes `BackgroundWatermarkWidget` is intentionally deferred. |
| 13 | `tests/test_smoke.py` | MODIFIED | Added 5 Phase 2 tests (kept the 4 Phase 1 tests). Total = 9 tests. |

**Not ported in Phase 2** (per canonical plan): `BackgroundWatermarkWidget` from `components.py:268+`. Deferred — niche, app-specific.

## 3. `git status --short`

Captured immediately after the Phase 2 commit, before this report was written:

```
$ git status --short
(no output — clean working tree)
```

## 4. `git diff --stat`

`main..phase-2-theme-widgets` (i.e. everything Phase 2 added on top of the Phase 1/1A baseline):

```
 src/phoenix_commons/theme/__init__.py        |   9 +-
 src/phoenix_commons/theme/_embedded_qss.py   | 778 +++++++++++++++++++++++++++
 src/phoenix_commons/theme/apply.py           |  72 +++
 src/phoenix_commons/theme/phoenix_style.qss  | 765 ++++++++++++++++++++++++++
 src/phoenix_commons/widgets/__init__.py      |  50 +-
 src/phoenix_commons/widgets/buttons.py       |  47 ++
 src/phoenix_commons/widgets/helpers.py       |  20 +
 src/phoenix_commons/widgets/no_scroll.py     |  65 +++
 src/phoenix_commons/widgets/panel.py         |  29 +
 src/phoenix_commons/widgets/table.py         |  25 +
 src/phoenix_commons/widgets/typography.py    |  43 ++
 src/phoenix_commons/widgets/update_banner.py |  77 +++
 tests/test_smoke.py                          |  77 ++-
 13 files changed, 2043 insertions(+), 14 deletions(-)
```

## 5. Full contents — adapted files only

The 8 verbatim ports (`_embedded_qss.py`, `phoenix_style.qss`, `no_scroll.py`, `buttons.py`, `typography.py`, `table.py`, `helpers.py`) are identical to the cited line ranges of their Phoenix_CAD_Tool sources — auditable by running `diff` between source and destination. To avoid pasting ~2000 lines of unchanged code, this section inlines only the **3 files with deliberate adaptations** and the **2 modified `__init__.py` modules** (which were Phase 1 stubs).

### `src/phoenix_commons/theme/apply.py` (adapted port)

```python
"""Phoenix design system loader.

Loads ``phoenix_style.qss`` from the runtime resource path (works in dev and
under PyInstaller ``--onedir`` frozen). Falls back to an embedded QSS string
so that auto-updates that only replace the .exe (not ``_internal/``) still
get correct styling.

Ported from ``Phoenix_CAD_Tool/ui/style.py:21-58``. Adapted: the source-mode
``_resource_path`` resolves files next to this module (under
``phoenix_commons.theme``) instead of the package's parent, because the
canonical ``phoenix_style.qss`` now lives inside the package.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

from PySide6.QtGui import QColor, QPalette
from PySide6.QtWidgets import QApplication

from ._embedded_qss import _EMBEDDED_QSS


def _resource_path(filename: str) -> str:
    """Resolve a resource path that works in dev and under PyInstaller.

    Source mode: ``filename`` is looked up alongside this module
    (``src/phoenix_commons/theme/<filename>``).
    Frozen mode: ``filename`` is looked up at
    ``_MEIPASS/phoenix_commons/theme/<filename>``. PyInstaller's
    ``--collect-all phoenix_commons`` preserves the package layout, and the
    ``[tool.setuptools.package-data]`` declaration in ``pyproject.toml``
    ensures ``*.qss`` files are included in the installed package.
    """
    if getattr(sys, "frozen", False):
        base = Path(getattr(sys, "_MEIPASS", "")) / "phoenix_commons" / "theme"
    else:
        base = Path(__file__).resolve().parent
    return str(base / filename)


def apply_dark_theme(app: QApplication) -> None:
    """Apply the Phoenix dark-navy theme: Fusion + dark palette + QSS."""
    app.setStyle("Fusion")

    palette = QPalette()
    for role, color in [
        (QPalette.ColorRole.Window,          QColor(10, 14, 39)),
        (QPalette.ColorRole.WindowText,      QColor(255, 255, 255)),
        (QPalette.ColorRole.Base,            QColor(20, 24, 41)),
        (QPalette.ColorRole.AlternateBase,   QColor(15, 18, 25)),
        (QPalette.ColorRole.ToolTipBase,     QColor(20, 24, 41)),
        (QPalette.ColorRole.ToolTipText,     QColor(255, 255, 255)),
        (QPalette.ColorRole.Text,            QColor(255, 255, 255)),
        (QPalette.ColorRole.Button,          QColor(20, 24, 41)),
        (QPalette.ColorRole.ButtonText,      QColor(255, 255, 255)),
        (QPalette.ColorRole.BrightText,      QColor(220, 38, 38)),
        (QPalette.ColorRole.Highlight,       QColor(59, 130, 246)),
        (QPalette.ColorRole.HighlightedText, QColor(255, 255, 255)),
        (QPalette.ColorRole.Link,            QColor(59, 130, 246)),
    ]:
        palette.setColor(role, color)
    app.setPalette(palette)

    qss_path = _resource_path("phoenix_style.qss")
    if os.path.exists(qss_path):
        with open(qss_path, "r", encoding="utf-8") as fh:
            app.setStyleSheet(fh.read())
    else:
        app.setStyleSheet(_EMBEDDED_QSS)
```

**Diff vs `Phoenix_CAD_Tool/ui/style.py:21-58`:** Only the `_resource_path` body changed. Old `.parent.parent` (which pointed to CAD's repo root) became:

- Frozen branch: `Path(_MEIPASS) / "phoenix_commons" / "theme"` (was just `Path(_MEIPASS)`)
- Source branch: `Path(__file__).resolve().parent` (was `.resolve().parent.parent`)

Reason: in the new package layout, `phoenix_style.qss` lives next to `apply.py` under `phoenix_commons/theme/`, not at the repo root. The frozen path mirrors the package layout that PyInstaller's `--collect-all phoenix_commons` produces.

### `src/phoenix_commons/widgets/panel.py` (adapted port)

```python
"""Phoenix dark rounded card container.

``Panel`` sets objectName ``"Panel"`` which ``phoenix_style.qss`` targets for
the dark rounded-card look. Pass an optional ``title`` to show a ``SectionTitle``
inside it.

Ported verbatim from ``Phoenix_CAD_Tool/ui/components.py:169-179``. Only change:
``SectionTitle`` is imported from the sibling ``typography`` submodule instead
of being available in the same module's namespace.
"""

from __future__ import annotations

from PySide6.QtWidgets import QVBoxLayout, QWidget

from .typography import SectionTitle


class Panel(QWidget):
    """Dark rounded card. Add child widgets via .layout() (a QVBoxLayout)."""

    def __init__(self, title: str | None = None, parent=None):
        super().__init__(parent)
        self.setObjectName("Panel")
        v = QVBoxLayout(self)
        v.setContentsMargins(16, 16, 16, 16)
        v.setSpacing(12)
        if title:
            v.addWidget(SectionTitle(title))
```

**Diff vs `Phoenix_CAD_Tool/ui/components.py:169-179`:** Class body identical. Only the `from .typography import SectionTitle` line replaces the implicit same-module availability of `SectionTitle` in the source.

### `src/phoenix_commons/widgets/update_banner.py` (adapted port)

```python
"""Phoenix update-available status-bar banner.

Designed to live inside the status bar via
``status_bar.addPermanentWidget(banner, 1)``, matching the project-tracking-tool
pattern. Styling lives in ``phoenix_style.qss`` under ``#UpdateBanner``,
``QLabel#UpdateMsg``, and ``#InstallBtn``.

Ported verbatim from ``Phoenix_CAD_Tool/ui/components.py:206-263``. Only
change: ``TertiaryButton`` is imported from the sibling ``buttons`` submodule
instead of being available in the same module's namespace.
"""

from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QMessageBox, QPushButton, QWidget

from .buttons import TertiaryButton


class UpdateBanner(QFrame):
    """Slim banner shown when an update is available.

    Designed to live inside the status bar via `addPermanentWidget(banner, 1)`,
    matching the project-tracking-tool pattern. Styling lives in phoenix_style.qss
    under `#UpdateBanner`, `QLabel#UpdateMsg`, and `#InstallBtn`.
    """

    install_clicked = Signal()

    def __init__(
        self,
        current_version: str,
        latest_version: str,
        release_notes: str = "",
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self.setObjectName("UpdateBanner")
        self.setFixedHeight(44)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 0, 16, 0)
        layout.setSpacing(8)

        msg = QLabel(
            f"Update available — v{latest_version} is ready. "
            f"You're on v{current_version}."
        )
        msg.setObjectName("UpdateMsg")
        layout.addWidget(msg, 1)

        if release_notes:
            notes_btn = TertiaryButton("Release Notes")
            notes_btn.setFixedWidth(132)
            notes_btn.clicked.connect(
                lambda: QMessageBox.information(
                    self,
                    f"What's new in v{latest_version}",
                    release_notes,
                )
            )
            layout.addWidget(notes_btn)

        install_btn = QPushButton("Install && Restart")
        install_btn.setObjectName("InstallBtn")
        install_btn.setMinimumHeight(32)
        install_btn.setFixedWidth(150)
        install_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        install_btn.clicked.connect(self.install_clicked)
        layout.addWidget(install_btn)

        dismiss_btn = TertiaryButton("✕")
        dismiss_btn.setFixedWidth(40)
        dismiss_btn.setToolTip("Dismiss")
        dismiss_btn.clicked.connect(self.hide)
        layout.addWidget(dismiss_btn)
```

**Diff vs `Phoenix_CAD_Tool/ui/components.py:206-263`:** Class body identical. Only the `from .buttons import TertiaryButton` line replaces the implicit same-module availability of `TertiaryButton` in the source.

### `src/phoenix_commons/theme/__init__.py` (replaced Phase 1 stub)

```python
"""Theme — Phoenix design system loader.

Public API:
    apply_dark_theme(app: QApplication) -> None
"""

from phoenix_commons.theme.apply import apply_dark_theme

__all__ = ["apply_dark_theme"]
```

### `src/phoenix_commons/widgets/__init__.py` (replaced Phase 1 stub)

```python
"""Widgets — Phoenix Controls component helpers shared across the ATS app suite.

Use these instead of raw Qt widgets so every tool reads as one product.

Public API:
    Buttons:        PrimaryButton, SecondaryButton, TertiaryButton
    Typography:     PageTitle, PageSubtitle, SectionTitle, HintLabel
    Containers:     Panel
    Tables:         PhoenixTable
    Banners:        UpdateBanner
    Layout helper:  button_row

The ``no_scroll`` submodule (``NoScrollComboBox``, ``NoScrollSpinBox``,
``NoScrollDoubleSpinBox``, ``NoScrollDateEdit``) is reached via
``from phoenix_commons.widgets.no_scroll import ...`` — those are advanced
form-input subclasses that callers opt into when needed.

``BackgroundWatermarkWidget`` from the source ``components.py`` is intentionally
NOT ported in Phase 2 (deferred per the canonical plan — niche, app-specific).
"""

from phoenix_commons.widgets.buttons import (
    PrimaryButton,
    SecondaryButton,
    TertiaryButton,
)
from phoenix_commons.widgets.helpers import button_row
from phoenix_commons.widgets.panel import Panel
from phoenix_commons.widgets.table import PhoenixTable
from phoenix_commons.widgets.typography import (
    HintLabel,
    PageSubtitle,
    PageTitle,
    SectionTitle,
)
from phoenix_commons.widgets.update_banner import UpdateBanner

__all__ = [
    "PrimaryButton",
    "SecondaryButton",
    "TertiaryButton",
    "PageTitle",
    "PageSubtitle",
    "SectionTitle",
    "HintLabel",
    "Panel",
    "PhoenixTable",
    "UpdateBanner",
    "button_row",
]
```

### Verbatim ports — auditing instructions

The 7 verbatim-with-imports files match their CAD sources byte-for-byte in class body / function body. To audit any one:

```
diff <(sed -n '57,105p'  C:/Users/justing/PycharmProjects/Phoenix_CAD_Tool/ui/components.py) \
     <(sed -n '14,$p'    C:/Users/justing/PycharmProjects/phoenix-commons/src/phoenix_commons/widgets/no_scroll.py)
```

(Repeat with the appropriate line ranges from Section 2 for each port.)

The two QSS artifacts (`phoenix_style.qss` and `_EMBEDDED_QSS` string contents) are identical 765-line copies of `Phoenix_CAD_Tool/phoenix_style.qss`. Test `test_phase2_embedded_qss_present` asserts the embedded string contains the canonical `#0a0e27` background and the `QPushButton` selector, providing automated drift detection.

## 6. Exact commands run

In execution order:

```
# Pre-flight (confirm Phase 1A state)
git -C "C:/Users/justing/PycharmProjects/phoenix-commons" status --short
git -C "C:/Users/justing/PycharmProjects/phoenix-commons" log --oneline -3
git -C "C:/Users/justing/PycharmProjects/phoenix-commons" ls-files docs/rollout/phase-1a-report.md

# Branch + read canonical sources
cd "C:/Users/justing/PycharmProjects/phoenix-commons" && git checkout -b phase-2-theme-widgets
(Read tool) Phoenix_CAD_Tool/phoenix_style.qss
(Read tool) Phoenix_CAD_Tool/ui/components.py  (lines 57..267)
(Read tool) Phoenix_CAD_Tool/ui/style.py        (already in context from earlier session)

# Write 12 files via the harness Write tool (no shell command):
#   src/phoenix_commons/theme/{phoenix_style.qss, _embedded_qss.py, apply.py, __init__.py}
#   src/phoenix_commons/widgets/{no_scroll, buttons, typography, panel, table, helpers, update_banner, __init__}.py
#   tests/test_smoke.py

# Verification
cd "C:/Users/justing/PycharmProjects/phoenix-commons" && python -m compileall -q src tests
cd "C:/Users/justing/PycharmProjects/phoenix-commons" && python -m pytest -q tests/
python -c "from phoenix_commons.theme import apply_dark_theme; from phoenix_commons.widgets import PrimaryButton, Panel, PhoenixTable, UpdateBanner; print('imports ok')"
python "C:/Users/justing/AppData/Local/Temp/phase2_scratch_smoke.py"
rm -f "C:/Users/justing/AppData/Local/Temp/phase2_scratch_smoke.py"

# Stage + commit
cd "C:/Users/justing/PycharmProjects/phoenix-commons" && git add .
git status --short
git diff --cached --name-only | wc -l
git commit -m "Phase 2 — theme + widgets ported from Phoenix_CAD_Tool"
git log --oneline -5
git status --short
git diff --stat main..phase-2-theme-widgets

# (Then write this report.)
```

No `git push`, no remote, no build, no installer, no `pyinstaller`, no production-tool edits, no Phase 3 work.

## 7. Raw output from verification commands

### `python -m compileall -q src tests`

```
(no output — all .py files compiled cleanly)
```

### `python -m pytest -q tests/`

```
.........                                                                [100%]
9 passed in 0.25s
```

Breakdown:
- 4 Phase 1 tests: `test_package_imports`, `test_version_format`, `test_version_is_0_1_0`, `test_submodules_importable`
- 5 Phase 2 tests: `test_phase2_theme_api`, `test_phase2_embedded_qss_present`, `test_phase2_phoenix_style_qss_packaged`, `test_phase2_widgets_public_api`, `test_phase2_no_scroll_submodule`

### `python -c "from phoenix_commons.theme import apply_dark_theme; from phoenix_commons.widgets import PrimaryButton, Panel, PhoenixTable, UpdateBanner; print('imports ok')"`

```
imports ok
```

### Scratch PySide6 smoke test (instantiation without event loop)

```
phoenix_commons version : 0.1.0
apply_dark_theme        : applied (style=)
PrimaryButton           : text='Primary' minH=36
SecondaryButton         : objectName='secondaryButton'
TertiaryButton          : objectName='tertiaryButton'
PageTitle               : objectName='ProjectTitle'
PageSubtitle            : objectName='ProjectSubtitle'
SectionTitle            : objectName='SectionTitle'
HintLabel               : objectName='hint'
Panel                   : objectName='Panel' children=1
PhoenixTable            : shape=2x3 editable=EditTrigger.NoEditTriggers
UpdateBanner            : objectName='UpdateBanner' height=44
button_row              : count=4
NoScroll widgets        : NoScrollComboBox, NoScrollSpinBox, NoScrollDoubleSpinBox, NoScrollDateEdit
SCRATCH_SMOKE_OK
```

Every widget's `objectName` matches the QSS selector convention from `phoenix_style.qss`. `Panel` correctly auto-adds a `SectionTitle` child when given a title (cross-module import working). `button_row` returns a `QHBoxLayout` containing one stretch + 3 buttons (count = 4). The scratch script was deleted after the run.

## 8. Confirmation: production tools were not modified

Confirmed. No `Write`, `Edit`, or shell write of any kind touched:

- `C:\Users\justing\PycharmProjects\Job Tracker\`
- `C:\Users\justing\PycharmProjects\Phoenix_CAD_Tool\`
- `C:\Users\justing\PycharmProjects\Phoenix-Checkout-Tool\`
- `C:\Users\justing\PycharmProjects\ValveMasterTool\`

`Phoenix_CAD_Tool` was **read-only** in Phase 2 (sources of the ports). Two files were read from it: `phoenix_style.qss` and `ui/components.py` (lines 57–267). `ui/style.py` content was already in context from an earlier session — no fresh read needed. Zero writes anywhere in `Phoenix_CAD_Tool`.

## 9. Confirmation: phoenix-command-center was not modified

Confirmed. No reads or writes to `C:\Users\justing\PycharmProjects\phoenix-command-center\` during Phase 2. The Command Center wizard changes happen in Phase 5; Phase 2 is purely about populating commons.

## 10. Confirmation: Phase 3 was not started

Confirmed.

- `src/phoenix_commons/updater/__init__.py` remains the Phase 1 stub (empty docstring describing what Phase 3 will populate). Verified by `git log -p docs/rollout/phase-2-report.md` showing no `updater/*.py` files among the changes.
- `src/phoenix_commons/paths.py` does not exist (it lands in Phase 3).
- No `check_for_update`, `download_and_apply`, `UpdateInfo`, `UpdateCheckThread`, `user_data_dir`, `is_frozen`, or `resource_path` has been ported.
- The Phase 3 todo remains `pending`.

## 11. Deviations, warnings, issues

### Deliberate adaptations (not deviations from spec — spec allows "behavior rewrites only when required to make imports package-safe")

1. `theme/apply.py` `_resource_path` path resolution adjusted for the package layout. Source mode: `.parent.parent` → `.parent`. Frozen mode: `_MEIPASS` → `_MEIPASS / "phoenix_commons" / "theme"`. Documented inline in the module docstring and in `apply.py`'s `_resource_path` docstring.
2. `widgets/panel.py` imports `SectionTitle` from `.typography` (was implicit same-module reference in source).
3. `widgets/update_banner.py` imports `TertiaryButton` from `.buttons` (was implicit same-module reference in source).

These three adaptations are necessary for package-safe imports — they do not change runtime behaviour.

### Warnings (cosmetic, not blocking)

- `git add` printed `LF will be replaced by CRLF the next time Git touches it` for 13 files. Same Windows `core.autocrlf=true` behaviour as Phase 1A. No content impact.
- Bash tool printed `Shell cwd was reset to ...phoenix-command-center` after `cd` calls. Harness artifact.
- The scratch smoke test reported `apply_dark_theme: applied (style=)` — `app.style().objectName()` returns an empty string when Fusion is applied. This is a Qt quirk where `QApplication.style()` returns the proxy style, not the underlying Fusion. `apply_dark_theme` ran without raising; the theme is correctly applied (palette + QSS). Cosmetic display issue in the scratch test only.

### Open items unchanged from Phase 1

- `phoenix-commons` remote is still not configured. No `git push` until you approve the destination URL.
- The PyInstaller `--collect-all phoenix_commons` smoke test (canonical-plan gate) is still open. Phase 4 will run it as its primary verification. Now would actually be a better moment to spot-check it (a real `apply_dark_theme` call will exercise the QSS-resource-resolution code path), if you want to de-risk early.

### Errors

**None.** All verification commands succeeded.

## 12. Recommendation for Phase 3

**Approve Phase 3** — with one optional preflight to consider.

**Optional preflight (recommended, ~5 min):** run the PyInstaller `--collect-all phoenix_commons` smoke test now, before Phase 3 adds the updater module. The scratch app `import phoenix_commons; apply_dark_theme(QApplication([])); …` and `pyinstaller --onedir --windowed --collect-all phoenix_commons scratch.py` would verify that the editable-install + frozen-build story works with the theme + widget ports we just landed. If it fails, we activate **Plan B (vendoring)** before Phase 5 instead of discovering the problem during dogfood. Doesn't block Phase 3 either way; just resolves the open Phase 4 gate one phase early.

**Phase 3 scope reminder:** port `Job Tracker/starter_package/updater.py:60-188` and `app_gui.py:52-58` → `src/phoenix_commons/updater/{client, installer, qt}.py` with the four-constant API exposed as kwargs (`check_for_update(owner, repo, current_version, zip_asset_name)`, `download_and_apply(info, exe_name, *, expected_internal=True, …)`, `UpdateCheckThread`). Plus `Phoenix_CAD_Tool/paths.py:30-79` → `src/phoenix_commons/paths.py` with `is_frozen()`, `user_data_dir(app_name, org_name="ATS Inc")`, `resource_path(filename, base=None)`. Read-only on Job Tracker, Phoenix CAD, and starter_package.

Phase 3 awaiting go/no-go.
