"""Phoenix read-only data table.

``PhoenixTable`` is a ``QTableWidget`` with the Phoenix defaults (no edit, no
selection, no focus rectangle, alternating row colours). Styling lives in
``phoenix_style.qss`` under ``QTableWidget`` selectors.

Ported verbatim from ``Phoenix_CAD_Tool/ui/components.py:182-191``.
"""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QTableWidget

__all__ = ["PhoenixTable"]


class PhoenixTable(QTableWidget):
    """Read-only data table with Phoenix styling defaults."""

    def __init__(self, rows: int = 0, cols: int = 0, parent=None):
        super().__init__(rows, cols, parent)
        self.verticalHeader().setVisible(False)
        self.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.setSelectionMode(QTableWidget.SelectionMode.NoSelection)
        self.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.setAlternatingRowColors(True)
