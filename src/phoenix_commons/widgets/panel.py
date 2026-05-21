"""Phoenix dark rounded card container.

``Panel`` sets objectName ``"Panel"`` which ``phoenix_style.qss`` targets for
the dark rounded-card look. Pass an optional ``title`` to show a ``SectionTitle``
inside it.

Ported verbatim from ``Phoenix_CAD_Tool/ui/components.py:169-179``. Only change:
``SectionTitle`` is imported from the sibling ``typography`` submodule instead
of being available in the same module's namespace.
"""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QVBoxLayout, QWidget

from .typography import SectionTitle

__all__ = ["Panel"]


class Panel(QWidget):
    """Dark rounded card. Add child widgets via .layout() (a QVBoxLayout)."""

    def __init__(self, title: str | None = None, parent=None):
        super().__init__(parent)
        self.setObjectName("Panel")
        # Qt gotcha: QWidget subclasses don't paint their QSS-defined
        # background/border by default — that's reserved for QFrame
        # and friends. Setting WA_StyledBackground enables QSS chrome
        # (the #Panel selector in phoenix_style.qss) on this widget.
        # Without this attribute Panel renders transparent, defeating
        # the rounded-card treatment.
        self.setAttribute(Qt.WA_StyledBackground, True)
        v = QVBoxLayout(self)
        v.setContentsMargins(16, 16, 16, 16)
        v.setSpacing(12)
        if title:
            v.addWidget(SectionTitle(title))
