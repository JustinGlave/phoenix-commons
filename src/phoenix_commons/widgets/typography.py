"""Phoenix typography QLabel subclasses.

Each label sets an objectName that ``phoenix_style.qss`` targets, so callers
just write ``PageTitle("Hello")`` and styling is automatic.

Ported verbatim from ``Phoenix_CAD_Tool/ui/components.py:137-166``.
"""

from __future__ import annotations

from PySide6.QtWidgets import QLabel

__all__ = ["PageTitle", "PageSubtitle", "SectionTitle", "HintLabel"]


class PageTitle(QLabel):
    """14pt bold page title (objectName 'ProjectTitle')."""

    def __init__(self, text: str, parent=None):
        super().__init__(text, parent)
        self.setObjectName("ProjectTitle")


class PageSubtitle(QLabel):
    """10pt muted subtitle (objectName 'ProjectSubtitle')."""

    def __init__(self, text: str, parent=None):
        super().__init__(text, parent)
        self.setObjectName("ProjectSubtitle")


class SectionTitle(QLabel):
    """12pt semibold section header (objectName 'SectionTitle')."""

    def __init__(self, text: str, parent=None):
        super().__init__(text, parent)
        self.setObjectName("SectionTitle")


class HintLabel(QLabel):
    """9pt muted helper text (objectName 'hint')."""

    def __init__(self, text: str, parent=None):
        super().__init__(text, parent)
        self.setObjectName("hint")
