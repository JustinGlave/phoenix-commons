"""Updater — GitHub-Releases-based auto-update for Phoenix tools.

Public API:
    UpdateInfo                                  (dataclass)
    check_for_update(owner, repo, current_version, zip_asset_name) -> UpdateInfo | None
    download_and_apply(info, exe_name, *, expected_internal=True,
                       progress_callback=None) -> None

The Qt thread wrapper is reachable as::

    from phoenix_commons.updater.qt import UpdateCheckThread

The validation error class (used by ``download_and_apply`` when the zip
layout doesn't match ``expected_internal``) is reachable as::

    from phoenix_commons.updater.installer import UpdatePackageError

It subclasses ``RuntimeError``, so callers that just want to show a friendly
"update failed" dialog can catch ``RuntimeError``.

Production payload asymmetry (documented in ``docs/production-inventory.md``):
    Job Tracker + Phoenix CAD ship full-folder updater zips → ``expected_internal=True``
    Phoenix Checkout + ValveMaster ship exe-only updater zips → ``expected_internal=False``
"""

from phoenix_commons.updater.client import UpdateInfo, check_for_update
from phoenix_commons.updater.installer import download_and_apply

__all__ = [
    "UpdateInfo",
    "check_for_update",
    "download_and_apply",
]
