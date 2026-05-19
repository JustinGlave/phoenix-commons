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

from .embedded_qss import EMBEDDED_QSS


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
        app.setStyleSheet(EMBEDDED_QSS)
