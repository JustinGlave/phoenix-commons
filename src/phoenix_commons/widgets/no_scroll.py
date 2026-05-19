"""No-scroll input widgets — wheel-event guards for scrollable forms.

Default Qt behavior changes a combo/spin's value when the mouse wheel is
rolled over it, even if the widget isn't focused. In a long scrollable form
that's a usability landmine — users scrolling the page accidentally shift
values. These subclasses ignore wheel events unless the widget has focus.

Ported verbatim from ``Phoenix_CAD_Tool/ui/components.py:57-105``.
"""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QComboBox, QDateEdit, QDoubleSpinBox, QSpinBox

__all__ = [
    "NoScrollComboBox",
    "NoScrollSpinBox",
    "NoScrollDoubleSpinBox",
    "NoScrollDateEdit",
]


class NoScrollComboBox(QComboBox):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # StrongFocus = accept focus on click and tab, NOT on wheel scroll.
        # Without this, the first wheel scroll grants focus and subsequent
        # scrolls change the value even though wheelEvent ignored the first.
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

    def wheelEvent(self, event):
        if self.hasFocus():
            super().wheelEvent(event)
        else:
            event.ignore()


class NoScrollSpinBox(QSpinBox):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

    def wheelEvent(self, event):
        if self.hasFocus():
            super().wheelEvent(event)
        else:
            event.ignore()


class NoScrollDoubleSpinBox(QDoubleSpinBox):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

    def wheelEvent(self, event):
        if self.hasFocus():
            super().wheelEvent(event)
        else:
            event.ignore()


class NoScrollDateEdit(QDateEdit):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

    def wheelEvent(self, event):
        if self.hasFocus():
            super().wheelEvent(event)
        else:
            event.ignore()
