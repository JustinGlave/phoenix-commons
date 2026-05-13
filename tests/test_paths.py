"""Phase 3 — tests for phoenix_commons.paths."""

from __future__ import annotations

from pathlib import Path


def test_paths_imports() -> None:
    from phoenix_commons.paths import is_frozen, user_data_dir, resource_path
    assert callable(is_frozen)
    assert callable(user_data_dir)
    assert callable(resource_path)


def test_is_frozen_false_in_source() -> None:
    """Running from source (pytest) is NOT a frozen PyInstaller build."""
    from phoenix_commons.paths import is_frozen
    assert is_frozen() is False


def test_user_data_dir_default_org_creates_path(tmp_path, monkeypatch) -> None:
    """``user_data_dir("Test Tool")`` returns ``ATS Inc/Test Tool`` and the
    directory is created on disk."""
    monkeypatch.setenv("APPDATA", str(tmp_path))
    from phoenix_commons.paths import user_data_dir

    p = user_data_dir("Test Tool")

    assert isinstance(p, Path)
    assert p.exists()
    assert p.is_dir()
    assert p == tmp_path / "ATS Inc" / "Test Tool"
    # Sanity: literal segments are present
    assert "ATS Inc" in str(p)
    assert "Test Tool" in str(p)


def test_user_data_dir_custom_org(tmp_path, monkeypatch) -> None:
    monkeypatch.setenv("APPDATA", str(tmp_path))
    from phoenix_commons.paths import user_data_dir

    p = user_data_dir("My Tool", org_name="ACME")

    assert p == tmp_path / "ACME" / "My Tool"
    assert p.exists() and p.is_dir()
    assert "ACME" in str(p)
    assert "ATS Inc" not in str(p)


def test_user_data_dir_falls_back_to_home(tmp_path, monkeypatch) -> None:
    """When ``APPDATA`` is unset, fall back to ``~/<org>/<app>``."""
    monkeypatch.delenv("APPDATA", raising=False)
    monkeypatch.setattr(Path, "home", classmethod(lambda cls: tmp_path))

    from phoenix_commons.paths import user_data_dir
    p = user_data_dir("Fallback Tool")

    assert p == tmp_path / "ATS Inc" / "Fallback Tool"
    assert p.exists() and p.is_dir()


def test_resource_path_returns_path_with_base(tmp_path) -> None:
    from phoenix_commons.paths import resource_path
    p = resource_path("phoenix_style.qss", base=tmp_path)
    assert isinstance(p, Path)
    assert p == tmp_path / "phoenix_style.qss"


def test_resource_path_without_base_returns_filename_path() -> None:
    """When no ``base`` is given in source mode, return ``Path(filename)``
    as-is so callers can resolve it themselves."""
    from phoenix_commons.paths import resource_path
    p = resource_path("phoenix_style.qss")
    assert isinstance(p, Path)
    assert p == Path("phoenix_style.qss")
