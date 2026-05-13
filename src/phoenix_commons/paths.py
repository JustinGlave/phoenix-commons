"""Phoenix path helpers — frozen vs source resolution.

Public API:
    is_frozen() -> bool
    user_data_dir(app_name: str, org_name: str = "ATS Inc") -> Path
    resource_path(filename: str, base: Path | None = None) -> Path

Ported and parameterized from ``Phoenix_CAD_Tool/paths.py:30-79``. The original
file hardcoded ``ORG_NAME = "ATS Inc"`` and ``APP_NAME = "Lab Layout Tool"``;
here both are function parameters so the same commons module serves every tool.

Key invariants preserved from the source:

- Writable user data NEVER lives under PyInstaller's ``_internal/`` folder.
  The auto-updater wipes ``_internal/`` on every update — putting user data
  there silently destroys it.
- Frozen mode writes to ``%APPDATA%/<org>/<app>`` on Windows (or
  ``~/<org>/<app>`` as a fallback when ``%APPDATA%`` is unset).
- Source mode uses the same ``%APPDATA%`` location so a developer's dev run
  reads/writes exactly the data that the installed copy would touch.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path


def is_frozen() -> bool:
    """True when running as a PyInstaller bundle."""
    return getattr(sys, "frozen", False)


def user_data_dir(app_name: str, org_name: str = "ATS Inc") -> Path:
    """Return the writable user-data folder for ``<org_name>/<app_name>``.

    Path is created if it doesn't already exist.

    On Windows (or anywhere ``%APPDATA%`` is set):
        ``%APPDATA%/<org_name>/<app_name>``
    Elsewhere (fallback):
        ``~/<org_name>/<app_name>``

    The same path is returned in frozen and source mode so developer runs
    use the same on-disk state the installed copy would.
    """
    appdata = os.environ.get("APPDATA")
    if appdata:
        base = Path(appdata) / org_name / app_name
    else:
        base = Path.home() / org_name / app_name
    base.mkdir(parents=True, exist_ok=True)
    return base


def resource_path(filename: str, base: Path | None = None) -> Path:
    """Resolve a bundled-resource path. Works in dev and under PyInstaller.

    Frozen mode: returns ``Path(_MEIPASS) / filename`` — PyInstaller's
    resource extraction directory.
    Source mode: returns ``Path(base) / filename`` if ``base`` is provided,
    otherwise ``Path(filename)`` as-is.

    Tools typically call this with ``base=Path(__file__).resolve().parent``
    from their ``main.py`` so resources resolve against the calling tool's
    source tree without commons needing to know the tool's repo layout.
    """
    if is_frozen():
        meipass = getattr(sys, "_MEIPASS", None)
        if meipass:
            return Path(meipass) / filename
    if base is not None:
        return Path(base) / filename
    return Path(filename)
