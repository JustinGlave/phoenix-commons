# Phase 3 Completion Packet — phoenix-commons

## 1. Status

**Passed.**

`phoenix_commons.paths` and `phoenix_commons.updater` are ported and parameterized — every previously-hardcoded production value (`ORG_NAME`, `APP_NAME`, `GITHUB_OWNER`, `GITHUB_REPO`, `ZIP_ASSET_NAME`, `EXE_NAME`) is now a function parameter. The updater's `expected_internal` kwarg preserves the production payload asymmetry documented in `production-inventory.md` — full-folder zips (Job Tracker + Phoenix CAD) and exe-only zips (Phoenix Checkout + ValveMaster) are both supported. 30/30 tests pass.

## 2. Files created or changed

Branch `phase-3-paths-updater`. Commit `79d92c8`. 7 files: 6 new, 1 modified (the Phase 1 updater stub).

| # | Path | Status | Origin / purpose |
|---|------|--------|------------------|
| 1 | `src/phoenix_commons/paths.py` | NEW | `is_frozen()`, `user_data_dir(app_name, org_name="ATS Inc")`, `resource_path(filename, base=None)`. Port of `Phoenix_CAD_Tool/paths.py:30-79` with the org/app constants converted to function kwargs. |
| 2 | `src/phoenix_commons/updater/client.py` | NEW | `UpdateInfo` dataclass + `check_for_update(owner, repo, current_version, zip_asset_name)`. Parameterized port of `Job Tracker/starter_package/updater.py:60-110`. |
| 3 | `src/phoenix_commons/updater/installer.py` | NEW | `download_and_apply(info, exe_name, *, expected_internal=True, progress_callback=None)` + `UpdatePackageError`. Combines starter_package's downloader (lines 112-188) with Job Tracker's heavier zip validator (lines 148-233). |
| 4 | `src/phoenix_commons/updater/qt.py` | NEW | `UpdateCheckThread(QThread)` emitting `update_available(UpdateInfo)`. Parameterized port of `starter_package/app_gui.py:52-58`. |
| 5 | `src/phoenix_commons/updater/__init__.py` | MODIFIED | Replaced Phase 1 stub. Re-exports `UpdateInfo`, `check_for_update`, `download_and_apply`. Notes the `qt.UpdateCheckThread` + `installer.UpdatePackageError` reachability. |
| 6 | `tests/test_paths.py` | NEW | 7 tests covering all paths.py behavior including APPDATA-fallback to home. |
| 7 | `tests/test_updater.py` | NEW | 14 tests covering imports, dataclass, version parsing/ordering, and zip-validation across all production payload contracts. |

## 3. `git status --short`

```
$ git status --short
(no output — clean working tree)
```

## 4. `git diff --stat`

`main..phase-3-paths-updater`:

```
 src/phoenix_commons/paths.py             |  75 +++++++
 src/phoenix_commons/updater/__init__.py  |  45 +++--
 src/phoenix_commons/updater/client.py    | 119 +++++++++++
 src/phoenix_commons/updater/installer.py | 333 +++++++++++++++++++++++++++++++
 src/phoenix_commons/updater/qt.py        |  66 ++++++
 tests/test_paths.py                      |  75 +++++++
 tests/test_updater.py                    | 181 +++++++++++++++++
 7 files changed, 879 insertions(+), 15 deletions(-)
```

The 15 deletions are the Phase 1 stub docstring in `updater/__init__.py` replaced by the real export module.

## 5. Full contents of new/adapted files

### `src/phoenix_commons/paths.py`

```python
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
```

**Adaptations from `Phoenix_CAD_Tool/paths.py:30-79`:**
- `ORG_NAME = "ATS Inc"` (line 36) and `APP_NAME = "Lab Layout Tool"` (line 37) module constants removed. Both are now kwargs on `user_data_dir`.
- `USER_DATA_DIR` and `PROJECT_ROOT` module-level constants removed. They were computed at import time which would have baked in the org/app values; now the caller controls per-call.
- App-specific subdirs (`JOBS_DIR`, `OUTPUT_DIR`, `TEMPLATES_DIR`, etc.) removed — those are CAD-specific. Each tool defines its own subdirs by joining the `user_data_dir(...)` result.
- `_resolve_project_root` collapsed into `resource_path` with `base` parameter.
- Behavioural difference: source mode now uses `%APPDATA%` (was `_SOURCE_ROOT = Path(__file__).parent` in CAD). Dev/prod parity, no source-tree pollution.

### `src/phoenix_commons/updater/client.py`

```python
"""GitHub Releases auto-updater — API client.

Public API:
    UpdateInfo (dataclass)
    check_for_update(owner, repo, current_version, zip_asset_name)
        -> UpdateInfo | None

Ported and parameterized from
``Job Tracker/starter_package/updater.py:60-110``. The original used
module-level constants for ``GITHUB_OWNER``, ``GITHUB_REPO``,
``ZIP_ASSET_NAME``, ``EXE_NAME``; here those are function parameters so the
commons module serves every tool without baked-in production values.
"""

from __future__ import annotations

import json
import logging
import urllib.error
import urllib.request
from dataclasses import dataclass
from typing import Optional

logger = logging.getLogger(__name__)

REQUEST_TIMEOUT = 8  # seconds


@dataclass
class UpdateInfo:
    """Update metadata returned by :func:`check_for_update`."""
    current_version: str
    latest_version: str
    download_url: str
    release_notes: str


def _parse_version(tag: str) -> tuple[int, ...]:
    """Convert ``'v1.2.3'``, ``'V1.2.3'``, or ``'1.2.3'`` to ``(1, 2, 3)``
    for ordered comparison.

    Returns ``(0,)`` if the tag is empty or unparseable. Matches the
    starter_package behaviour so a malformed remote tag never suppresses
    valid local versions.
    """
    cleaned = tag.lstrip("vV").strip()
    try:
        return tuple(int(part) for part in cleaned.split("."))
    except ValueError:
        return (0,)


def check_for_update(
    owner: str,
    repo: str,
    current_version: str,
    zip_asset_name: str,
) -> Optional[UpdateInfo]:
    """Query the GitHub Releases API for ``<owner>/<repo>``.

    Returns an :class:`UpdateInfo` when ``zip_asset_name`` is attached to a
    release whose tag parses to a strictly newer version than
    ``current_version``. Returns ``None`` otherwise — including when the
    network is unavailable, GitHub returns garbled JSON, or no matching
    asset is attached.

    Safe to call from a background thread — never raises. Network errors are
    logged at ``DEBUG`` level; payload/parsing problems at ``WARNING``.
    """
    releases_api = (
        f"https://api.github.com/repos/{owner}/{repo}/releases/latest"
    )
    try:
        req = urllib.request.Request(
            releases_api,
            headers={
                "Accept": "application/vnd.github+json",
                "User-Agent": zip_asset_name,
            },
        )
        with urllib.request.urlopen(req, timeout=REQUEST_TIMEOUT) as resp:
            data = json.loads(resp.read().decode())

        latest_tag = data.get("tag_name", "")
        if not latest_tag:
            return None
        if _parse_version(latest_tag) <= _parse_version(current_version):
            return None  # already up to date

        assets = data.get("assets", [])
        zip_asset = next(
            (
                a
                for a in assets
                if a.get("name", "").lower() == zip_asset_name.lower()
            ),
            None,
        )
        if zip_asset is None:
            logger.warning(
                "New release %s found but asset %s not attached.",
                latest_tag,
                zip_asset_name,
            )
            return None

        return UpdateInfo(
            current_version=current_version,
            latest_version=latest_tag.lstrip("vV"),
            download_url=zip_asset["browser_download_url"],
            release_notes=data.get("body", "").strip(),
        )

    except urllib.error.URLError as exc:
        logger.debug("Update check failed (network): %s", exc)
        return None
    except (json.JSONDecodeError, KeyError, TypeError, ValueError, AttributeError) as exc:
        logger.warning("Update check failed: %s", exc)
        return None
```

**Adaptations from `starter_package/updater.py:60-110`:**
- Module-level `GITHUB_OWNER`, `GITHUB_REPO`, `ZIP_ASSET_NAME`, `EXE_NAME` constants removed. `check_for_update` now takes them as parameters.
- `RELEASES_API` is built inside `check_for_update` instead of at module import time.
- `from version import __version__` is **not** imported — `current_version` is now a parameter, satisfying the user rule "Do not import a tool's version.py".
- Logic body otherwise verbatim: same tag-comparison, same case-insensitive asset matching, same logging behaviour.

### `src/phoenix_commons/updater/installer.py`

```python
"""GitHub Releases auto-updater — download, validate, install, relaunch.

Public API:
    download_and_apply(info, exe_name, *, expected_internal=True,
                       progress_callback=None) -> None
    UpdatePackageError (RuntimeError subclass — raised by zip validation)

Ported and parameterized from
``Job Tracker/starter_package/updater.py:112-188``, with zip-validation logic
adapted from ``Job Tracker/updater.py:148-176``. Both kinds of production
updater payload are supported:

- ``expected_internal=True`` (default) for the **full-folder** PyInstaller
  ``--onedir`` layout used by Job Tracker + Phoenix CAD. Validates that the
  zip contains both ``<exe_name>`` and ``_internal/`` at the zip root (or
  inside a single top-level folder named after the exe stem). On apply, the
  whole folder is extracted over the install directory via a small
  PowerShell wrapper that handles both flat and nested layouts.
- ``expected_internal=False`` for the **exe-only** updater zips shipped by
  Phoenix Checkout + ValveMaster. Validates only that the zip contains
  ``<exe_name>``. On apply, the single exe is extracted via inline
  PowerShell.

See ``docs/production-inventory.md`` for the cross-tool asymmetry that
drives this kwarg.
"""

from __future__ import annotations

import logging
import os
import subprocess
import sys
import tempfile
import urllib.error
import urllib.request
import zipfile
from pathlib import Path
from typing import Callable, Optional

from phoenix_commons.updater.client import UpdateInfo

logger = logging.getLogger(__name__)


class UpdatePackageError(RuntimeError):
    """Raised when the downloaded update package is missing required files."""


# ─── Zip validation ──────────────────────────────────────────────────────────

def _validate_update_zip(
    zip_path: Path,
    exe_name: str,
    *,
    expected_internal: bool = True,
) -> None:
    """Ensure ``zip_path`` is a readable zip with the expected layout.

    With ``expected_internal=True`` (full-folder layout):
        - ``<exe_name>`` exists at the zip root **or** inside a top-level
          folder named after the exe stem.
        - ``_internal/`` exists at the zip root **or** inside the same
          top-level folder.

    With ``expected_internal=False`` (exe-only layout):
        - ``<exe_name>`` exists at the zip root.

    Raises :class:`UpdatePackageError` (a ``RuntimeError`` subclass) if any
    expected member is missing or the zip cannot be read.
    """
    try:
        with zipfile.ZipFile(zip_path) as zf:
            names = {
                name.replace("\\", "/").lstrip("/") for name in zf.namelist()
            }
    except zipfile.BadZipFile as exc:
        raise UpdatePackageError(
            "The downloaded update package is not a valid zip file.\n"
            "Please download the installer manually from GitHub."
        ) from exc

    exe_stem = Path(exe_name).stem
    flat_exe = exe_name
    nested_exe = f"{exe_stem}/{exe_name}"
    has_exe = flat_exe in names or nested_exe in names

    if not has_exe:
        raise UpdatePackageError(
            f"The downloaded update package does not contain {exe_name}.\n"
            "Please download the installer manually from GitHub."
        )

    if expected_internal:
        has_internal = any(
            name.startswith("_internal/")
            or name.startswith(f"{exe_stem}/_internal/")
            for name in names
        )
        if not has_internal:
            raise UpdatePackageError(
                "The downloaded update package is incomplete: the _internal "
                "runtime folder is missing.\n"
                "Please download the installer manually from GitHub."
            )


# ─── PowerShell + batch wrappers ─────────────────────────────────────────────

def _ps_literal(value: Path | str) -> str:
    """Return a PowerShell single-quoted string literal."""
    return "'" + str(value).replace("'", "''") + "'"


def _build_full_folder_powershell(zip_path, install_dir, exe_path, exe_name):
    """PowerShell that extracts a full-folder zip (flat **or** nested layout)
    over ``install_dir``, then verifies the new exe exists."""
    exe_stem = Path(exe_name).stem
    return f"""$ErrorActionPreference = 'Stop'
$zipPath = {_ps_literal(zip_path)}
$installDir = {_ps_literal(install_dir)}
$exePath = {_ps_literal(exe_path)}
$exeName = {_ps_literal(exe_name)}
$exeStem = {_ps_literal(exe_stem)}

if (-not (Test-Path -LiteralPath $zipPath)) {{
    throw "Update package was not found: $zipPath"
}}
if (-not (Test-Path -LiteralPath $installDir)) {{
    throw "Install folder was not found: $installDir"
}}

$stage = Join-Path ([IO.Path]::GetTempPath()) ('phoenix_update_' + [guid]::NewGuid().ToString('N'))
New-Item -ItemType Directory -Force -Path $stage | Out-Null

try {{
    Expand-Archive -LiteralPath $zipPath -DestinationPath $stage -Force
    $payload = $stage
    $nested = Join-Path $stage $exeStem
    if (Test-Path -LiteralPath (Join-Path $nested $exeName)) {{
        $payload = $nested
    }}

    Get-ChildItem -LiteralPath $payload -Force | Copy-Item -Destination $installDir -Recurse -Force

    if (-not (Test-Path -LiteralPath $exePath)) {{
        throw "Updated executable was not found after copy: $exePath"
    }}
}}
finally {{
    if (Test-Path -LiteralPath $stage) {{
        Remove-Item -LiteralPath $stage -Recurse -Force -ErrorAction SilentlyContinue
    }}
    if (Test-Path -LiteralPath $zipPath) {{
        Remove-Item -LiteralPath $zipPath -Force -ErrorAction SilentlyContinue
    }}
}}
"""


def _build_full_folder_batch(pid, ps_path, exe_path):
    """Batch wrapper that waits for the parent process, runs the PowerShell
    script that does the heavy lifting, then relaunches the exe."""
    ps_str = str(ps_path)
    exe_str = str(exe_path)
    return f"""@echo off
setlocal
:wait
tasklist /FI "PID eq {pid}" 2>nul | find "{pid}" >nul
if not errorlevel 1 (
    timeout /t 1 /nobreak >nul
    goto wait
)
powershell -NoProfile -ExecutionPolicy Bypass -File "{ps_str}"
if errorlevel 1 (
    start "" "{exe_str}"
    del "{ps_str}" >nul 2>nul
    del "%~f0"
    exit /b 1
)
start "" "{exe_str}"
del "{ps_str}" >nul 2>nul
del "%~f0"
"""


def _build_exe_only_batch(pid, zip_path, exe_path, exe_name):
    """Batch + inline PowerShell that waits for the parent, extracts only
    ``<exe_name>`` from the zip over the existing exe, then relaunches."""
    zip_str = str(zip_path)
    exe_str = str(exe_path)
    return f"""@echo off
:wait
tasklist /FI "PID eq {pid}" 2>nul | find "{pid}" >nul
if not errorlevel 1 (
    timeout /t 1 /nobreak >nul
    goto wait
)
powershell -ExecutionPolicy Bypass -Command "Add-Type -AssemblyName System.IO.Compression.FileSystem; $zip = [System.IO.Compression.ZipFile]::OpenRead('{zip_str}'); $entry = $zip.Entries | Where-Object {{ $_.Name -eq '{exe_name}' }} | Select-Object -First 1; if ($entry) {{ [System.IO.Compression.ZipFileExtensions]::ExtractToFile($entry, '{exe_str}', $true) }}; $zip.Dispose()"
del "{zip_str}"
start "" "{exe_str}"
del "%~f0"
"""


# ─── Public entry point ──────────────────────────────────────────────────────

def download_and_apply(
    info: UpdateInfo,
    exe_name: str,
    *,
    expected_internal: bool = True,
    progress_callback: Optional[Callable[[int, int], None]] = None,
) -> None:
    """Download the update zip, validate it, apply it, and restart the app.

    ``progress_callback(bytes_done, total_bytes)`` is invoked during the
    download so a GUI can drive a progress bar. Pass ``None`` to skip.

    On success the function calls ``sys.exit(0)`` — Windows takes it from
    there via a small batch/PowerShell wrapper that waits for this process
    to terminate, replaces the install files, and relaunches the exe.

    Raises :class:`RuntimeError` (or :class:`UpdatePackageError`, a subclass)
    on any failure so the caller can show an error dialog rather than fail
    silently.
    """
    if not getattr(sys, "frozen", False):
        raise RuntimeError(
            "Update can only be applied to a compiled build.\n"
            "You're running from source — pull the latest code from GitHub "
            "or build locally instead."
        )

    current_exe = Path(sys.executable).resolve()
    install_dir = current_exe.parent

    # ── 1. Download to a temp zip ─────────────────────────────────────────
    tmp_fd, tmp_zip_str = tempfile.mkstemp(suffix=".zip")
    tmp_zip = Path(tmp_zip_str)

    try:
        req = urllib.request.Request(
            info.download_url,
            headers={"User-Agent": exe_name},
        )
        with urllib.request.urlopen(req, timeout=60) as resp:
            total = int(resp.headers.get("Content-Length", 0))
            done = 0
            chunk = 64 * 1024
            with open(tmp_fd, "wb") as fh:
                while True:
                    block = resp.read(chunk)
                    if not block:
                        break
                    fh.write(block)
                    done += len(block)
                    if progress_callback:
                        progress_callback(done, total)

        if total > 0 and tmp_zip.stat().st_size < total:
            tmp_zip.unlink(missing_ok=True)
            raise RuntimeError(
                f"Download incomplete: got {tmp_zip.stat().st_size} of "
                f"{total} bytes.\nPlease try again or download manually "
                "from GitHub."
            )

    except RuntimeError:
        raise
    except (OSError, urllib.error.URLError, ValueError) as exc:
        try:
            tmp_zip.unlink(missing_ok=True)
        except OSError:
            logger.exception(
                "Failed to remove incomplete update download: %s", tmp_zip
            )
        raise RuntimeError(f"Download failed: {exc}") from exc

    # ── 2. Validate the zip layout ────────────────────────────────────────
    try:
        _validate_update_zip(
            tmp_zip, exe_name, expected_internal=expected_internal
        )
    except RuntimeError:
        tmp_zip.unlink(missing_ok=True)
        raise

    # ── 3. Write the helper scripts ───────────────────────────────────────
    pid = os.getpid()

    if expected_internal:
        # Full-folder: separate .ps1 + .bat wrapper
        ps_fd, ps_path_str = tempfile.mkstemp(suffix=".ps1")
        bat_fd, bat_path_str = tempfile.mkstemp(suffix=".bat")
        ps_path = Path(ps_path_str)
        bat_path = Path(bat_path_str)

        with open(ps_fd, "w", encoding="utf-8") as fh:
            fh.write(
                _build_full_folder_powershell(
                    tmp_zip, install_dir, current_exe, exe_name
                )
            )
        with open(bat_fd, "w", encoding="utf-8") as fh:
            fh.write(_build_full_folder_batch(pid, ps_path, current_exe))
    else:
        # Exe-only: inline PowerShell inside the .bat
        bat_fd, bat_path_str = tempfile.mkstemp(suffix=".bat")
        bat_path = Path(bat_path_str)

        with open(bat_fd, "w", encoding="utf-8") as fh:
            fh.write(
                _build_exe_only_batch(pid, tmp_zip, current_exe, exe_name)
            )

    # ── 4. Launch the bat and exit ────────────────────────────────────────
    subprocess.Popen(
        ["cmd.exe", "/c", str(bat_path)],
        creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
        close_fds=True,
    )
    sys.exit(0)
```

**Adaptations:**
- Download loop ported verbatim from `starter_package/updater.py:118-160` (params: `info.download_url`, `exe_name` for User-Agent — was hardcoded `EXE_NAME`).
- Zip validation logic adapted from `Job Tracker/updater.py:148-176` (`_validate_update_zip`). Parameterized: takes `exe_name` and `expected_internal` (the original was hardcoded for ProjectTrackingTool with no toggle).
- Helper-script generation: full-folder path uses the more-robust separate-.ps1+.bat pattern from Job Tracker (handles flat AND nested zip layouts via PowerShell). Exe-only path uses the simpler inline PowerShell from starter_package. Both are parameterized.

### `src/phoenix_commons/updater/qt.py`

```python
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
```

**Adaptations:**
- Class renamed `_UpdateChecker` → `UpdateCheckThread` for clearer public-API naming.
- Signal renamed `found` → `update_available` (more descriptive).
- Constructor now takes `owner`, `repo`, `current_version`, `zip_asset_name` as required kwargs (originally pulled from module constants).
- Body of `run()` otherwise identical: call check_for_update, emit on success.

### `src/phoenix_commons/updater/__init__.py` (replaced Phase 1 stub)

```python
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
```

### Test coverage summary

`tests/test_paths.py` (7 tests):
- Import surface: `is_frozen`, `user_data_dir`, `resource_path` are all callable.
- `is_frozen()` returns `False` in source/pytest.
- `user_data_dir("Test Tool")` creates `<APPDATA>/ATS Inc/Test Tool` (monkeypatched APPDATA → tmp_path; asserts directory creation + literal path segments).
- `user_data_dir("My Tool", org_name="ACME")` returns `<APPDATA>/ACME/My Tool`; confirms ACME is in the path and the default "ATS Inc" is not.
- APPDATA-unset fallback: `Path.home()` is monkeypatched, then `user_data_dir(...)` lands at `<home>/ATS Inc/<App Name>`.
- `resource_path("phoenix_style.qss", base=tmp_path)` returns `tmp_path / "phoenix_style.qss"`.
- `resource_path("phoenix_style.qss")` (no base) returns `Path("phoenix_style.qss")`.

`tests/test_updater.py` (14 tests):
- Imports: `UpdateInfo`, `check_for_update`, `download_and_apply`, `UpdateCheckThread` (subclass of `QThread`), `UpdatePackageError` (subclass of `RuntimeError`).
- `UpdateInfo` dataclass construction with all 4 fields.
- `_parse_version` basic ("1.2.3", "v1.2.3", "V0.1.0").
- `_parse_version` unparseable returns `(0,)`.
- `_parse_version` ordering: `1.2.3 < 1.2.4`, `1.2.3 < 2.0.0`, `0.1.0 < 0.10.0`, `1.0.0 == v1.0.0`.
- Validation positive: full-folder flat zip + `expected_internal=True` → pass.
- Validation positive: full-folder nested zip + `expected_internal=True` → pass.
- Validation positive: exe-only zip + `expected_internal=False` → pass.
- Validation negative: exe-only zip + `expected_internal=True` → `UpdatePackageError` containing "_internal".
- Validation negative: zip missing exe → `UpdatePackageError` containing the expected exe name.
- Validation negative: corrupt zip → `UpdatePackageError` containing "not a valid zip".
- Validation negative: zip with only `readme.txt` + `expected_internal=False` → still fails (exe must be present in either mode).

All 30 tests across all 3 test files pass (Phase 1+2 9 tests + Phase 3 21 tests).

## 6. Exact commands run

```
# Pre-flight: verify Phase 2 state, merge to main, branch for Phase 3
cd "C:/Users/justing/PycharmProjects/phoenix-commons" && git status --short --branch
                                                       && git ls-files docs/rollout/phase-2-report.md
git checkout main && git merge --no-ff phase-2-theme-widgets -m "Merge Phase 2 — theme and widgets"
git checkout -b phase-3-paths-updater
git status --short --branch && git log --oneline -6

# Read canonical sources (already in context from earlier phases):
#   Phoenix_CAD_Tool/paths.py
#   Job Tracker/starter_package/updater.py
#   Job Tracker/starter_package/app_gui.py
#   Job Tracker/updater.py    (for the validator pattern)

# Write 7 files via Write tool:
#   src/phoenix_commons/paths.py
#   src/phoenix_commons/updater/{client.py, installer.py, qt.py, __init__.py}
#   tests/test_paths.py
#   tests/test_updater.py

# Verification
cd "C:/Users/justing/PycharmProjects/phoenix-commons" && python -m compileall -q src tests
cd "C:/Users/justing/PycharmProjects/phoenix-commons" && python -m pytest -q tests/
python -c "from phoenix_commons.paths import user_data_dir, is_frozen, resource_path; print('is_frozen:', is_frozen()); print('user_data_dir(\"Test Tool\"):', user_data_dir('Test Tool'))"
python -c "from phoenix_commons.updater import UpdateInfo, check_for_update, download_and_apply; from phoenix_commons.updater.qt import UpdateCheckThread; print('updater imports ok')"

# Optional network check
timeout 20 python -c "from phoenix_commons.updater import check_for_update; print(check_for_update('JustinGlave', 'phoenix-command-center', '0.0.1', 'phoenix-command-center.zip'))"

# Cleanup the smoke-test-created %APPDATA% folder (un-monkeypatched smoke
# actually created %APPDATA%\ATS Inc\Test Tool on disk; tests use a
# monkeypatched temp directory and leave no real artifacts)
python -c "import shutil, pathlib; d = pathlib.Path.home() / 'AppData' / 'Roaming' / 'ATS Inc' / 'Test Tool'; ...; shutil.rmtree(d, ignore_errors=True); ..."

# Stage + commit
cd "C:/Users/justing/PycharmProjects/phoenix-commons" && git add . && git status --short
git commit -m "Phase 3 — paths + updater ported from CAD and starter_package"
git log --oneline -5 && git status --short && git diff --stat main..phase-3-paths-updater

# Then write this report.
```

No `git push`, no build, no PyInstaller, no Inno Setup, no GitHub release commands, no production-tool edits.

## 7. Raw output from verification commands

### `python -m compileall -q src tests`

```
(no output — all .py files compiled cleanly)
```

### `python -m pytest -q tests/`

```
..............................                                           [100%]
30 passed in 0.26s
```

Breakdown:
- 4 Phase 1 + 5 Phase 2 = 9 tests from `tests/test_smoke.py`
- 7 Phase 3 paths tests from `tests/test_paths.py`
- 14 Phase 3 updater tests from `tests/test_updater.py`

### `python -c "from phoenix_commons.paths import user_data_dir, is_frozen, resource_path; print(is_frozen()); print(user_data_dir('Test Tool'))"`

```
is_frozen: False
user_data_dir("Test Tool"): C:\Users\justing\AppData\Roaming\ATS Inc\Test Tool
```

(This un-monkeypatched smoke call actually created the directory on disk. Cleaned up afterwards — see "Deviations" below.)

### `python -c "from phoenix_commons.updater import UpdateInfo, check_for_update, download_and_apply; from phoenix_commons.updater.qt import UpdateCheckThread; print('updater imports ok')"`

```
updater imports ok
```

### Optional network check: `check_for_update('JustinGlave', 'phoenix-command-center', '0.0.1', 'phoenix-command-center.zip')`

```
None
```

Non-blocking. Either the repo has no Releases yet, or the latest release tag parses to ≤ `0.0.1` (unlikely), or there was a transient network/rate-limit failure (the function swallows those silently by design). No code bug surfaced.

## 8. Confirmation: production tools were not modified

Confirmed. `Phoenix_CAD_Tool` and `Job Tracker` were read-only sources of the ports; no writes. `Phoenix-Checkout-Tool` and `ValveMasterTool` were neither read nor written. No `Write`, `Edit`, or shell write touched any path under:

- `C:\Users\justing\PycharmProjects\Job Tracker\`
- `C:\Users\justing\PycharmProjects\Phoenix_CAD_Tool\`
- `C:\Users\justing\PycharmProjects\Phoenix-Checkout-Tool\`
- `C:\Users\justing\PycharmProjects\ValveMasterTool\`

The optional network check made one outbound HTTPS call to `api.github.com/repos/JustinGlave/phoenix-command-center/releases/latest`. No write to any production tool.

## 9. Confirmation: phoenix-command-center was not modified

Confirmed. Zero reads or writes inside `C:\Users\justing\PycharmProjects\phoenix-command-center\` during Phase 3. The wizard changes happen in Phase 5.

## 10. Confirmation: Phase 4 was not started

Confirmed.

- No PyInstaller invocation. No `pyinstaller --collect-all phoenix_commons` test. Phase 4 will be the dedicated phase for that gate.
- No vendoring scaffold (`vendor/phoenix_commons/` + `refresh_commons.bat`) was created. That's the Plan B fallback if Phase 4's editable-install + PyInstaller check fails.
- The Phase 4 todo remains `pending`.

## 11. Deviations, warnings, issues

### Deliberate adaptations (spec-allowed)

The user's Phase 3 rules explicitly say "owner, repo, current_version, zip_asset_name, and exe_name must be parameters", so all parameterizations are within scope. The parameterized changes:

1. `paths.py` — `ORG_NAME` / `APP_NAME` removed from module scope; both are now `user_data_dir` kwargs.
2. `paths.py` — source mode now uses `%APPDATA%` (was `_SOURCE_ROOT = Path(__file__).parent` in CAD). Same path returned in dev and prod. Documented in module docstring.
3. `updater/client.py` — module-level `GITHUB_OWNER` / `GITHUB_REPO` / `ZIP_ASSET_NAME` / `EXE_NAME` removed; all now function kwargs.
4. `updater/client.py` — no `from version import __version__` import. The user rule "Do not import a tool's version.py" is satisfied; `current_version` is a kwarg.
5. `updater/installer.py` — combined two sources: simpler downloader from starter_package + heavier zip validator from Job Tracker's main updater.py. `expected_internal` toggles the validation strictness and which extraction script is generated.
6. `updater/qt.py` — class renamed `_UpdateChecker` → `UpdateCheckThread`; signal renamed `found` → `update_available`. Constructor now takes the 4 parameters explicitly.

### Test artifact (cleaned)

The un-monkeypatched `python -c "...user_data_dir('Test Tool')..."` smoke command created `C:\Users\justing\AppData\Roaming\ATS Inc\Test Tool` (empty directory) since the function creates the directory by contract. This was cleaned up at the end of verification — verified by `pathlib.Path.exists()` before `shutil.rmtree`. The actual unit tests (`tests/test_paths.py`) use `monkeypatch.setenv("APPDATA", str(tmp_path))` to redirect, so they leave no real artifacts.

### Optional network check returned None

Non-blocking per user rule: "If the optional network check fails because of network/API/rate-limit conditions, report it as non-blocking unless the failure shows a code bug." The function's `None` return is the documented contract for "no newer release found or transient network error" — exactly what was asked for. No code bug surfaced.

### Warnings (cosmetic, not blocking)

- `git add` printed `LF will be replaced by CRLF` for 7 files. Same Windows `core.autocrlf=true` behaviour as earlier phases. No content impact.
- Bash tool's `Shell cwd was reset to ...` artifact appears after every `cd`. Harness artifact, no impact.

### Open items unchanged from Phase 1

- `phoenix-commons` remote still not configured. No `git push` until you approve the destination URL.
- PyInstaller `--collect-all phoenix_commons` smoke test still open. Now sits squarely in Phase 4 (its dedicated phase).

### Errors

**None.** All verification commands succeeded.

## 12. Recommendation for Phase 4

**Approve Phase 4.**

The commons package now has everything Phase 4 needs to exercise:

- `apply_dark_theme` + the widget set (need to verify QSS resource resolution under PyInstaller — both the file-on-disk path and the embedded-QSS fallback)
- `user_data_dir()` (need to verify writes don't end up under `_internal/` after a frozen build runs it)
- `check_for_update()` (need to verify the HTTPS module + JSON stdlib are correctly bundled)

The scratch app for Phase 4 should:
1. Build a `dist/scratch/scratch.exe` via `pyinstaller --onedir --windowed --collect-all phoenix_commons scratch.py`.
2. Confirm the .exe launches.
3. Confirm a button rendered via `PrimaryButton` shows the Phoenix red.
4. Confirm `_internal/phoenix_commons/theme/phoenix_style.qss` exists (or the embedded fallback is reachable if it doesn't).
5. Confirm `user_data_dir("Phase 4 Test")` returns a path under `%APPDATA%/ATS Inc/Phase 4 Test/`.

**Phase 4 decision tree:**
- If everything works → commons-backed template becomes the wizard default in Phase 5. Plan B (vendoring) stays in `docs/` as a fallback recipe but isn't activated.
- If the editable-install + PyInstaller story breaks → activate Plan B. Generate the `vendor/phoenix_commons/` scaffold + `refresh_commons.bat` template. Adjust the Phase 5 template to use vendored imports instead.

Phase 4 scope reminder: **read-only on Phoenix_CAD_Tool / Job Tracker / Phoenix-Checkout-Tool / ValveMasterTool / phoenix-command-center.** All work happens in `phoenix-commons/` (creating a scratch test main.py) + a temp PyInstaller build directory.

Phase 4 awaiting go/no-go.
