"""Phoenix button widgets.

Three semantic levels:
    PrimaryButton   — red, main/destructive actions (Save, Generate, Submit)
    SecondaryButton — blue, supporting actions (Export, Save Draft, Refresh)
    TertiaryButton  — outline, low-emphasis (Cancel, Help, Dismiss)

Object names match the selectors in ``phoenix_style.qss`` so the QSS picks them
up automatically (``secondaryButton``, ``tertiaryButton``; ``PrimaryButton``
uses the default ``QPushButton`` style).

Ported verbatim from ``Phoenix_CAD_Tool/ui/components.py:108-134``.
"""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QPushButton

__all__ = ["PrimaryButton", "SecondaryButton", "TertiaryButton"]


class PrimaryButton(QPushButton):
    """Red primary-action button."""

    def __init__(self, text: str, parent=None):
        super().__init__(text, parent)
        self.setMinimumHeight(36)
        self.setCursor(Qt.CursorShape.PointingHandCursor)


class SecondaryButton(QPushButton):
    """Blue secondary-action button."""

    def __init__(self, text: str, parent=None):
        super().__init__(text, parent)
        self.setObjectName("secondaryButton")
        self.setMinimumHeight(36)
        self.setCursor(Qt.CursorShape.PointingHandCursor)


class TertiaryButton(QPushButton):
    """Outline tertiary button (low-emphasis / cancel / dismiss)."""

    def __init__(self, text: str, parent=None):
        super().__init__(text, parent)
        self.setObjectName("tertiaryButton")
        self.setMinimumHeight(36)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
