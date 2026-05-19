"""Phase 2.2 — tests for the Phoenix icon infrastructure.

Covers:

  1. ``icon()`` returns a non-null :class:`QIcon`.
  2. Repeated calls hit the cache (same instance returned).
  3. Unknown icon names raise :class:`IconNotFoundError` with a helpful
     message that lists at least one valid name.
  4. Recolouring actually changes the rendered pixels (the
     ``currentColor`` byte-substitution path works end-to-end).
  5. The ``size=`` argument is honoured by the rasterised pixmap.
  6. Every name in :data:`ICON_NAMES` has a corresponding ``.svg``
     under package data and renders cleanly. Parametrised so a missing
     SVG fails as an individual test, not a generic load error.
  7. Unknown colour names raise :class:`UnknownColorError` whose
     message names the valid semantic options.
  8. Hex literal colours work (both 3- and 6-digit forms).
  9. Passing a hex equivalent of a semantic colour produces the same
     pixels as the semantic name (different cache entries, same render).
 10. The byte-substitution helper ``_recolor`` works as a unit, with no
     Qt involvement.
 11. ``(name, color, size)`` cache key really does separate different
     parameter combinations.
 12. Package data is discoverable via :func:`importlib.resources.files`
     (the path PyInstaller ``--collect-data`` follows).
"""
from __future__ import annotations

from importlib.resources import files

import pytest

from phoenix_commons.icons import (
    ICON_NAMES,
    IconNotFoundError,
    UnknownColorError,
    clear_cache,
    icon,
)


@pytest.fixture(autouse=True)
def _reset_cache() -> None:
    """Each test starts and ends with an empty icon cache.

    Stops a cache entry created in one test (e.g. ``size=18``) from
    silently satisfying a different test that expected a fresh render.
    """
    clear_cache()
    yield
    clear_cache()


def test_icon_returns_qicon(qtbot) -> None:
    from PySide6.QtGui import QIcon
    result = icon("save")
    assert isinstance(result, QIcon)
    assert not result.isNull(), "rendered QIcon was null — SVG load likely failed"


def test_cache_hit_returns_same_instance(qtbot) -> None:
    a = icon("save")
    b = icon("save")
    assert a is b, "repeated icon() call did not hit the cache"


def test_missing_icon_raises_clear_error(qtbot) -> None:
    with pytest.raises(IconNotFoundError) as excinfo:
        icon("definitely-not-an-icon")
    msg = str(excinfo.value)
    assert "definitely-not-an-icon" in msg, "error message didn't echo the bad name"
    # Should suggest at least one real icon so the human can pick the right one.
    assert any(name in msg for name in ICON_NAMES), (
        "error message didn't suggest any valid icon names"
    )


def test_recolour_produces_different_pixels(qtbot) -> None:
    """``color="primary"`` must produce a visibly different render from default."""
    from PySide6.QtCore import QSize
    default_icon = icon("save")
    primary_icon = icon("save", color="primary")

    default_img = default_icon.pixmap(QSize(24, 24)).toImage()
    primary_img = primary_icon.pixmap(QSize(24, 24)).toImage()

    assert default_img != primary_img, (
        "default and primary-coloured icons produced identical pixels — "
        "currentColor substitution likely broken"
    )


def test_size_parameter_is_honoured(qtbot) -> None:
    from PySide6.QtCore import QSize
    small = icon("save", size=18)
    large = icon("save", size=48)
    assert small.pixmap(QSize(18, 18)).size() == QSize(18, 18)
    assert large.pixmap(QSize(48, 48)).size() == QSize(48, 48)


@pytest.mark.parametrize("name", sorted(ICON_NAMES))
def test_every_registered_icon_loads(qtbot, name: str) -> None:
    """Every name in ICON_NAMES resolves to a real, non-null QIcon."""
    from PySide6.QtGui import QIcon
    result = icon(name)
    assert isinstance(result, QIcon)
    assert not result.isNull(), f"{name!r} rendered as a null icon"


def test_unknown_color_raises_clear_error(qtbot) -> None:
    with pytest.raises(UnknownColorError) as excinfo:
        icon("save", color="puce")
    msg = str(excinfo.value)
    assert "puce" in msg, "error message didn't echo the bad colour"
    assert "primary" in msg, "error message didn't suggest semantic options"


def test_hex_color_literal_works(qtbot) -> None:
    from PySide6.QtGui import QIcon
    result = icon("save", color="#dc2626")
    assert isinstance(result, QIcon)
    assert not result.isNull()


def test_short_hex_color_works(qtbot) -> None:
    """Three-digit hex (``#fff``) is just as valid as six-digit (``#ffffff``)."""
    from PySide6.QtGui import QIcon
    result = icon("save", color="#fff")
    assert isinstance(result, QIcon)
    assert not result.isNull()


def test_hex_and_semantic_resolve_to_same_pixels(qtbot) -> None:
    """``color="#dc2626"`` and ``color="primary"`` must render identically.

    They use different cache keys (we intentionally don't normalise to
    hex on lookup — see loader docstring) but the rasterised output
    must match pixel-for-pixel.
    """
    from PySide6.QtCore import QSize
    direct = icon("save", color="#dc2626")
    semantic = icon("save", color="primary")
    assert direct.pixmap(QSize(24, 24)).toImage() == semantic.pixmap(QSize(24, 24)).toImage()


def test_recolor_unit_substitution() -> None:
    """Direct test of the byte-substitution helper. No Qt involved."""
    from phoenix_commons.icons.loader import _recolor

    svg = b'<svg stroke="currentColor"><path/></svg>'
    out = _recolor(svg, "#dc2626")
    assert b"currentColor" not in out, "substitution left currentColor token behind"
    assert b'stroke="#dc2626"' in out, "substitution didn't insert the new hex"


def test_recolor_handles_single_quotes() -> None:
    """Some SVG editors emit single-quoted attributes — recolour must cover both."""
    from phoenix_commons.icons.loader import _recolor

    svg = b"<svg stroke='currentColor'/>"
    out = _recolor(svg, "#dc2626")
    assert b"currentColor" not in out
    assert b"stroke='#dc2626'" in out


def test_cache_distinguishes_name_color_and_size(qtbot) -> None:
    """Each ``(name, color, size)`` triple gets its own cache entry."""
    a = icon("save")
    b = icon("save", color="primary")
    c = icon("save", size=18)
    d = icon("settings")
    assert a is not b
    assert a is not c
    assert a is not d
    assert b is not c
    assert b is not d
    assert c is not d


def test_package_data_includes_all_starter_svgs() -> None:
    """Every name in ICON_NAMES has a real SVG bundled with the package.

    Resolves through :func:`importlib.resources.files` — the same path
    PyInstaller's ``--collect-data phoenix_commons`` follows when the
    consuming app is frozen. If this passes, the frozen build will
    bundle the icons.
    """
    base = files("phoenix_commons.icons.lucide")
    for name in sorted(ICON_NAMES):
        svg = base / f"{name}.svg"
        assert svg.is_file(), f"missing SVG asset for icon {name!r}"
        content = svg.read_bytes()
        assert len(content) > 50, f"{name}.svg is suspiciously small ({len(content)} B)"
        assert content.startswith(b"<svg"), f"{name}.svg doesn't start with <svg"
        assert b"currentColor" in content, (
            f"{name}.svg lacks currentColor — recolouring will silently no-op"
        )
