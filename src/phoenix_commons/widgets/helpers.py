"""Widget convenience helpers.

Ported verbatim from ``Phoenix_CAD_Tool/ui/components.py:194-203``.
"""

from __future__ import annotations

from PySide6.QtWidgets import QHBoxLayout


def button_row(*buttons, align_right: bool = True) -> QHBoxLayout:
    """Convenience: horizontal layout of buttons with a leading stretch."""
    row = QHBoxLayout()
    if align_right:
        row.addStretch(1)
    for b in buttons:
        row.addWidget(b)
    if not align_right:
        row.addStretch(1)
    return row
