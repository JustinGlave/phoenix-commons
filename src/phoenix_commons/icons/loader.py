"""loader.py — Phoenix icon loader: SVG → recoloured QIcon, with caching.

Public entry point is :func:`icon`. Returns a :class:`QIcon` ready for
use with any Qt consumer (``QPushButton.setIcon``, ``QAction.setIcon``,
``QStandardItem.setIcon``, etc.).

Recolour strategy: **byte-substitution before SVG parse.** Lucide SVGs
ship with ``stroke="currentColor"`` (the standard CSS escape for
inheriting the caller's text colour). Qt's :class:`QSvgRenderer` does
*not* honour ``currentColor`` — it renders it as opaque black, which is
invisible on the Phoenix dark-navy bg. So before handing the SVG to
``QSvgRenderer`` we replace ``currentColor`` with the resolved hex in
the in-memory bytes. Faster than QPainter compositing and produces
cleaner output (no source-in alpha artifacts).

Cache lookup uses the **raw colour argument** (e.g. ``"primary"``)
rather than the resolved hex. That keeps the cache invalidatable
through a single point — bump :data:`SEMANTIC_COLORS` and old entries
become unreachable rather than silently-stale-but-still-served.

Requires a :class:`QApplication` to exist before any ``icon()`` call,
because :class:`QPixmap` construction does. This matches the rest of
``phoenix_commons.widgets`` — Qt primitives never come for free.
"""
from __future__ import annotations

import re
from importlib.resources import files

from PySide6.QtCore import QByteArray, QSize, Qt
from PySide6.QtGui import QIcon, QPainter, QPixmap
from PySide6.QtSvg import QSvgRenderer

from . import cache
from .registry import (
    DEFAULT_COLOR,
    DEFAULT_SIZE,
    ICON_NAMES,
    IconNotFoundError,
    SEMANTIC_COLORS,
    UnknownColorError,
)

# Matches a 3- or 6-digit hex colour, case-insensitive: #rgb / #rrggbb.
_HEX_RE = re.compile(r"^#(?:[0-9a-fA-F]{3}|[0-9a-fA-F]{6})$")

# Lucide SVGs are stroke-only; some future icons may use fill="currentColor".
# Cover both attribute names + both quote styles so the recolour path is
# robust against the small set of variants SVG editors emit.
_CURRENT_COLOR_PATTERNS: tuple[bytes, ...] = (
    b'stroke="currentColor"',
    b"stroke='currentColor'",
    b'fill="currentColor"',
    b"fill='currentColor'",
)


def icon(name: str, *, color: str | None = None, size: int = DEFAULT_SIZE) -> QIcon:
    """Return a Phoenix-themed :class:`QIcon` for ``name``.

    Parameters
    ----------
    name : str
        Semantic icon name. Must be in
        :data:`phoenix_commons.icons.registry.ICON_NAMES`.
    color : str, optional
        Either a semantic palette name (``"primary"``, ``"accent"``, …
        — see :data:`SEMANTIC_COLORS`) or a hex literal (``"#dc2626"``,
        ``"#fff"``). If omitted, falls back to :data:`DEFAULT_COLOR`
        (``"text"`` → white, the Phoenix dark-navy default).
    size : int, optional
        Square pixel size for the rasterised pixmap. Defaults to
        :data:`DEFAULT_SIZE` (24). Qt downsamples sharply if the
        consuming widget renders at a smaller logical size.

    Returns
    -------
    QIcon
        A cached :class:`QIcon`. Repeated calls with the same arguments
        return the same instance.

    Raises
    ------
    IconNotFoundError
        If ``name`` is not in :data:`ICON_NAMES`. The message lists the
        available names so typos surface immediately.
    UnknownColorError
        If ``color`` is neither a semantic name nor a valid hex literal.
    """
    # Normalise: ``None`` == ``DEFAULT_COLOR``. Sharing one cache entry
    # for both keeps reuse high without surprising the user.
    color_key = color if color is not None else DEFAULT_COLOR

    cache_key = (name, color_key, size)
    cached = cache.get(cache_key)
    if cached is not None:
        return cached

    if name not in ICON_NAMES:
        suggestions = ", ".join(sorted(ICON_NAMES))
        raise IconNotFoundError(
            f"Unknown icon name: {name!r}. Available: {suggestions}"
        )

    hex_color = _resolve_color(color_key)
    svg_bytes = _load_svg_bytes(name)
    svg_bytes = _recolor(svg_bytes, hex_color)

    icon_obj = _render_qicon(svg_bytes, size)
    cache.put(cache_key, icon_obj)
    return icon_obj


def _resolve_color(color: str) -> str:
    """Resolve a semantic palette name or a hex literal to a hex string.

    Returns the hex with leading ``#``. Raises
    :class:`UnknownColorError` for anything we don't understand — the
    message names the valid semantic options so the caller can correct
    typos without consulting the source.
    """
    if color in SEMANTIC_COLORS:
        return SEMANTIC_COLORS[color]
    if _HEX_RE.match(color):
        return color
    raise UnknownColorError(
        f"Unknown color: {color!r}. "
        f"Pass a hex literal (e.g. '#dc2626') or one of: "
        f"{', '.join(sorted(SEMANTIC_COLORS))}"
    )


def _load_svg_bytes(name: str) -> bytes:
    """Read the raw SVG bytes for ``name`` from package data.

    Uses :func:`importlib.resources.files` so source-mode (editable
    install) and frozen-mode (PyInstaller ``--collect-data
    phoenix_commons``) share the same resolution path. ``Traversable``
    abstracts over both filesystem and zip-based package sources.
    """
    resource = files("phoenix_commons.icons.lucide") / f"{name}.svg"
    return resource.read_bytes()


def _recolor(svg_bytes: bytes, hex_color: str) -> bytes:
    """Substitute every ``currentColor`` attribute in ``svg_bytes`` with ``hex_color``.

    Operates on raw bytes (not parsed XML) for speed and to avoid pulling
    ``xml.etree`` into every icon load. Lucide SVGs are well-formed and
    the ``currentColor`` token only appears inside attribute values, so
    plain substitution is safe and ~100× faster than an XML round-trip.
    """
    encoded = hex_color.encode("ascii")
    out = svg_bytes
    for pattern in _CURRENT_COLOR_PATTERNS:
        replacement = pattern.replace(b"currentColor", encoded)
        out = out.replace(pattern, replacement)
    return out


def _render_qicon(svg_bytes: bytes, size: int) -> QIcon:
    """Rasterise ``svg_bytes`` to a transparent QPixmap, wrap as :class:`QIcon`.

    The pixmap is filled with :data:`Qt.GlobalColor.transparent` before
    rendering so the icon composites cleanly over any background. The
    painter is closed in ``finally`` so partially-rendered pixmaps don't
    leak a live :class:`QPainter` if rendering raises.
    """
    renderer = QSvgRenderer(QByteArray(svg_bytes))
    pixmap = QPixmap(QSize(size, size))
    pixmap.fill(Qt.GlobalColor.transparent)
    painter = QPainter(pixmap)
    try:
        renderer.render(painter)
    finally:
        painter.end()
    return QIcon(pixmap)


__all__ = ["icon"]
