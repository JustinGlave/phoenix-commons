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


def _build_full_folder_powershell(
    zip_path: Path,
    install_dir: Path,
    exe_path: Path,
    exe_name: str,
) -> str:
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


def _build_full_folder_batch(pid: int, ps_path: Path, exe_path: Path) -> str:
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


def _build_exe_only_batch(
    pid: int,
    zip_path: Path,
    exe_path: Path,
    exe_name: str,
) -> str:
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
