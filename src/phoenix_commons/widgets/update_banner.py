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

__all__ = ["UpdateBanner"]


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
