"""Phase 3 — tests for phoenix_commons.updater.

Covers:
- import surface of ``phoenix_commons.updater`` and the ``qt`` submodule
- ``UpdateInfo`` dataclass construction
- internal ``_parse_version`` semantics (used by check_for_update)
- ``_validate_update_zip`` with synthetic zip files exercising both the
  full-folder (``expected_internal=True``) and exe-only (``expected_internal=False``)
  payload contracts, plus negative cases

Tests never invoke ``download_and_apply`` (it would call ``sys.exit``) and
never hit the real GitHub API.
"""

from __future__ import annotations

import zipfile

import pytest


# ─── Import surface ──────────────────────────────────────────────────────────

def test_updater_public_imports() -> None:
    from phoenix_commons.updater import (
        UpdateInfo,
        check_for_update,
        download_and_apply,
    )
    assert callable(check_for_update)
    assert callable(download_and_apply)
    # UpdateInfo is a dataclass type
    assert hasattr(UpdateInfo, "__dataclass_fields__")


def test_updater_qt_thread_importable() -> None:
    from phoenix_commons.updater.qt import UpdateCheckThread
    # Subclass of QThread (don't instantiate — needs QApplication)
    from PySide6.QtCore import QThread
    assert issubclass(UpdateCheckThread, QThread)


def test_updater_package_error_importable() -> None:
    """UpdatePackageError is reachable from the installer submodule and is a
    RuntimeError subclass (so callers can catch RuntimeError)."""
    from phoenix_commons.updater.installer import UpdatePackageError
    assert issubclass(UpdatePackageError, RuntimeError)


# ─── UpdateInfo ──────────────────────────────────────────────────────────────

def test_update_info_construction() -> None:
    from phoenix_commons.updater import UpdateInfo
    info = UpdateInfo(
        current_version="1.0.0",
        latest_version="1.1.0",
        download_url="https://example.com/asset.zip",
        release_notes="Test notes",
    )
    assert info.current_version == "1.0.0"
    assert info.latest_version == "1.1.0"
    assert info.download_url == "https://example.com/asset.zip"
    assert info.release_notes == "Test notes"


# ─── _parse_version ──────────────────────────────────────────────────────────

def test_parse_version_basic() -> None:
    from phoenix_commons.updater.client import _parse_version
    assert _parse_version("1.2.3") == (1, 2, 3)
    assert _parse_version("v1.2.3") == (1, 2, 3)
    assert _parse_version("V0.1.0") == (0, 1, 0)


def test_parse_version_returns_zero_tuple_when_unparseable() -> None:
    """Matches starter_package behaviour: garbage tags compare as (0,)."""
    from phoenix_commons.updater.client import _parse_version
    assert _parse_version("garbage") == (0,)
    assert _parse_version("") == (0,)


def test_parse_version_orders_correctly() -> None:
    """Sanity check the ordering ``check_for_update`` relies on."""
    from phoenix_commons.updater.client import _parse_version
    assert _parse_version("1.2.3") < _parse_version("1.2.4")
    assert _parse_version("1.2.3") < _parse_version("2.0.0")
    assert _parse_version("0.1.0") < _parse_version("0.10.0")
    assert _parse_version("1.0.0") == _parse_version("v1.0.0")


# ─── Zip validation: helpers ─────────────────────────────────────────────────

def _make_full_folder_flat_zip(zip_path, exe_name: str = "MyTool.exe") -> None:
    """Write ``<exe_name>`` and ``_internal/lib.dll`` at the zip root."""
    with zipfile.ZipFile(zip_path, "w") as zf:
        zf.writestr(exe_name, b"fake exe bytes")
        zf.writestr("_internal/lib.dll", b"fake lib bytes")


def _make_full_folder_nested_zip(zip_path, exe_name: str = "MyTool.exe") -> None:
    """Write ``<stem>/<exe_name>`` and ``<stem>/_internal/lib.dll``."""
    from pathlib import Path as _P
    stem = _P(exe_name).stem
    with zipfile.ZipFile(zip_path, "w") as zf:
        zf.writestr(f"{stem}/{exe_name}", b"fake exe bytes")
        zf.writestr(f"{stem}/_internal/lib.dll", b"fake lib bytes")


def _make_exe_only_zip(zip_path, exe_name: str = "MyTool.exe") -> None:
    """Write only ``<exe_name>`` at the zip root."""
    with zipfile.ZipFile(zip_path, "w") as zf:
        zf.writestr(exe_name, b"fake exe bytes")


# ─── Zip validation: positive cases ──────────────────────────────────────────

def test_validate_full_folder_flat_zip_passes_with_internal_required(tmp_path) -> None:
    """Job Tracker / Phoenix CAD shape: exe + _internal/ at zip root."""
    from phoenix_commons.updater.installer import _validate_update_zip
    z = tmp_path / "full_flat.zip"
    _make_full_folder_flat_zip(z)
    _validate_update_zip(z, "MyTool.exe", expected_internal=True)  # no raise


def test_validate_full_folder_nested_zip_passes_with_internal_required(tmp_path) -> None:
    """Defensive: same exe + _internal/ but inside a top-level folder."""
    from phoenix_commons.updater.installer import _validate_update_zip
    z = tmp_path / "full_nested.zip"
    _make_full_folder_nested_zip(z)
    _validate_update_zip(z, "MyTool.exe", expected_internal=True)  # no raise


def test_validate_exe_only_zip_passes_when_internal_not_required(tmp_path) -> None:
    """Phoenix Checkout / ValveMaster shape: exe only, no _internal/."""
    from phoenix_commons.updater.installer import _validate_update_zip
    z = tmp_path / "exe_only.zip"
    _make_exe_only_zip(z)
    _validate_update_zip(z, "MyTool.exe", expected_internal=False)  # no raise


# ─── Zip validation: negative cases ──────────────────────────────────────────

def test_validate_exe_only_zip_fails_when_internal_required(tmp_path) -> None:
    """Critical asymmetry guard — passing an exe-only payload with
    ``expected_internal=True`` must fail loudly so the retrofit catches it."""
    from phoenix_commons.updater.installer import _validate_update_zip, UpdatePackageError
    z = tmp_path / "exe_only.zip"
    _make_exe_only_zip(z)
    with pytest.raises(UpdatePackageError) as ei:
        _validate_update_zip(z, "MyTool.exe", expected_internal=True)
    assert "_internal" in str(ei.value)


def test_validate_missing_exe_fails(tmp_path) -> None:
    from phoenix_commons.updater.installer import _validate_update_zip, UpdatePackageError
    z = tmp_path / "missing_exe.zip"
    with zipfile.ZipFile(z, "w") as zf:
        zf.writestr("wrong_name.exe", b"fake")
        zf.writestr("_internal/lib.dll", b"fake")
    with pytest.raises(UpdatePackageError) as ei:
        _validate_update_zip(z, "MyTool.exe", expected_internal=True)
    assert "MyTool.exe" in str(ei.value)


def test_validate_corrupt_zip_fails(tmp_path) -> None:
    from phoenix_commons.updater.installer import _validate_update_zip, UpdatePackageError
    z = tmp_path / "corrupt.zip"
    z.write_bytes(b"this is not a zip file")
    with pytest.raises(UpdatePackageError) as ei:
        _validate_update_zip(z, "MyTool.exe", expected_internal=False)
    assert "not a valid zip" in str(ei.value)


def test_validate_exe_only_zip_fails_when_exe_missing(tmp_path) -> None:
    """Even with ``expected_internal=False`` the exe must be present."""
    from phoenix_commons.updater.installer import _validate_update_zip, UpdatePackageError
    z = tmp_path / "no_exe.zip"
    with zipfile.ZipFile(z, "w") as zf:
        zf.writestr("readme.txt", b"oops, no exe")
    with pytest.raises(UpdatePackageError):
        _validate_update_zip(z, "MyTool.exe", expected_internal=False)


# ─── Phase 3A: regression for the incomplete-download bug ────────────────────

def test_incomplete_download_raises_clean_runtime_error(tmp_path, monkeypatch) -> None:
    """Regression for the Phase 3A bug.

    When the server reports Content-Length larger than the bytes actually
    delivered, ``download_and_apply`` must raise a ``RuntimeError`` whose
    message contains both the captured-actual size and the expected total.
    Before the fix, ``tmp_zip.stat().st_size`` was evaluated AFTER
    ``tmp_zip.unlink()`` which raced the deletion and raised
    ``FileNotFoundError``, masking the real cause. The fix captures
    ``actual_size`` before the unlink call.
    """
    import os
    import sys
    import phoenix_commons.updater.installer as installer
    from phoenix_commons.updater import UpdateInfo, download_and_apply

    # download_and_apply early-exits when not frozen — pretend we are.
    monkeypatch.setattr(sys, "frozen", True, raising=False)
    fake_exe = tmp_path / "fake.exe"
    monkeypatch.setattr(sys, "executable", str(fake_exe))

    EXPECTED_TOTAL = 1000
    ACTUAL_BYTES = b"x" * 100  # Server lies about Content-Length

    class _FakeResponse:
        headers = {"Content-Length": str(EXPECTED_TOTAL)}

        def __init__(self) -> None:
            self._pos = 0

        def read(self, chunk: int) -> bytes:
            if self._pos >= len(ACTUAL_BYTES):
                return b""
            block = ACTUAL_BYTES[self._pos : self._pos + chunk]
            self._pos += len(block)
            return block

        def __enter__(self):
            return self

        def __exit__(self, *args):
            return False

    def fake_urlopen(req, timeout=60):
        return _FakeResponse()

    monkeypatch.setattr(installer.urllib.request, "urlopen", fake_urlopen)

    # Use a known temp path so we can assert cleanup happened
    known_zip = tmp_path / "predictable.zip"

    def fake_mkstemp(suffix: str = ".zip"):
        fd = os.open(str(known_zip), os.O_CREAT | os.O_RDWR)
        return (fd, str(known_zip))

    monkeypatch.setattr(installer.tempfile, "mkstemp", fake_mkstemp)

    info = UpdateInfo(
        current_version="1.0.0",
        latest_version="1.1.0",
        download_url="https://example.com/test.zip",
        release_notes="",
    )

    with pytest.raises(RuntimeError) as exc_info:
        download_and_apply(info, "MyTool.exe", expected_internal=False)

    msg = str(exc_info.value)

    # The friendly "Download incomplete" path, NOT a leaked FileNotFoundError
    assert "Download incomplete" in msg, (
        f"Expected 'Download incomplete' in message, got: {msg!r}"
    )

    # Both byte counts must be present
    assert str(len(ACTUAL_BYTES)) in msg, (
        f"Expected actual size {len(ACTUAL_BYTES)} in message, got: {msg!r}"
    )
    assert str(EXPECTED_TOTAL) in msg, (
        f"Expected total size {EXPECTED_TOTAL} in message, got: {msg!r}"
    )

    # Explicit anti-regression: the original bug surfaced as FileNotFoundError
    assert not isinstance(exc_info.value, FileNotFoundError), (
        "FileNotFoundError leaked instead of the friendly RuntimeError. "
        "The fix's actual_size capture must happen BEFORE tmp_zip.unlink()."
    )

    # And the temp zip must have been cleaned up
    assert not known_zip.exists(), (
        f"Temp zip should have been removed after the failure: {known_zip}"
    )


# ─── Phase 3A: PowerShell-safe quoting helper ───────────────────────────────

def test_ps_literal_simple() -> None:
    """_ps_literal wraps plain strings in single quotes."""
    from phoenix_commons.updater.installer import _ps_literal
    assert _ps_literal("simple") == "'simple'"
    assert _ps_literal("") == "''"


def test_ps_literal_escapes_internal_single_quotes() -> None:
    """PowerShell convention: single quote inside a single-quoted string is
    doubled. Protects exe-only batch generation when a path or exe name
    happens to contain an apostrophe."""
    from phoenix_commons.updater.installer import _ps_literal
    assert _ps_literal("with'quote") == "'with''quote'"
    assert _ps_literal("two'with'quotes") == "'two''with''quotes'"
    # And a realistic Windows path with an apostrophe (rare but legal)
    assert _ps_literal(r"C:\Users\justing's tool\app.exe") == (
        "'C:\\Users\\justing''s tool\\app.exe'"
    )
