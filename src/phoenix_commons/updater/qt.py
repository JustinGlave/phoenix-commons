"""GitHub Releases auto-updater — Qt integration.

Public API:
    UpdateCheckThread

Ported and parameterized from
``Job Tracker/starter_package/app_gui.py:52-58`` (``_UpdateChecker`` class).
``check_for_update`` is called from the thread's ``run()`` method so the
GitHub API call never blocks the GUI thread.
"""

from __future__ import annotations

from PySide6.QtCore import QThread, Signal

from phoenix_commons.updater.client import check_for_update

__all__ = ["UpdateCheckThread"]


class UpdateCheckThread(QThread):
    """Background thread that polls GitHub Releases for a newer version.

    Emits :pyattr:`update_available` with an :class:`UpdateInfo` when a newer
    version is found. Emits nothing when there's no update or when the API
    call fails (network errors are logged inside ``check_for_update``, never
    raised).

    Usage::

        from phoenix_commons.updater.qt import UpdateCheckThread

        checker = UpdateCheckThread(
            owner="JustinGlave",
            repo="my-tool",
            current_version=__version__,
            zip_asset_name="MyTool.zip",
            parent=self,
        )
        checker.update_available.connect(self._on_update_found)
        checker.start()
    """

    update_available = Signal(object)  # UpdateInfo

    def __init__(
        self,
        owner: str,
        repo: str,
        current_version: str,
        zip_asset_name: str,
        parent=None,
    ) -> None:
        super().__init__(parent)
        self.owner = owner
        self.repo = repo
        self.current_version = current_version
        self.zip_asset_name = zip_asset_name

    def run(self) -> None:
        info = check_for_update(
            self.owner,
            self.repo,
            self.current_version,
            self.zip_asset_name,
        )
        if info is not None:
            self.update_available.emit(info)
