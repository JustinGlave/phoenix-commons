"""registry.py — declared icon names + semantic colour palette.

Pure-Python, Qt-free. Importing this module must work from any context
(tests, headless CI, build scripts) without dragging in a QApplication.

Design notes:

* ``ICON_NAMES`` is a closed set. ``icon("foo")`` for any ``foo`` not
  listed here raises :class:`IconNotFoundError` with the available
  names suggested in the message. Closed-set semantics is what lets
  the IDE / lint surface typos at call time rather than runtime.
* ``SEMANTIC_COLORS`` mirrors the Phoenix System A palette (see
  ``PLATFORM_CONTRACT.md``). When the formal token module lands in a
  later Phase 2.x step, this map will become a thin facade over it;
  the public icon API (``color="primary"``) stays unchanged.
* Both maps are deliberately tiny. New names go through a commons PR.
"""
from __future__ import annotations


class IconNotFoundError(KeyError):
    """Raised when ``icon(name)`` is called with a name not in :data:`ICON_NAMES`.

    Inherits :class:`KeyError` so existing ``except KeyError`` code paths
    that expect missing-icon behaviour continue working, while the
    explicit subclass lets new code be specific.
    """


class UnknownColorError(ValueError):
    """Raised when ``color=`` is neither a known semantic name nor valid hex."""


# ---------------------------------------------------------------------------
# Closed set of icon names — must match the .svg stems under lucide/.
# Keep alphabetised. Each entry has a corresponding ``lucide/<name>.svg``.
# ---------------------------------------------------------------------------
ICON_NAMES: frozenset[str] = frozenset({
    "check",
    "info",
    "plus",
    "refresh",
    "save",
    "search",
    "settings",
    "trash",
    "warning",
    "x",
})


# ---------------------------------------------------------------------------
# Semantic colour palette. Hex values aligned to Phoenix System A.
# ``text`` is the default (white-on-navy reads cleanly across all icons).
# ---------------------------------------------------------------------------
SEMANTIC_COLORS: dict[str, str] = {
    "primary":   "#dc2626",   # accent red
    "secondary": "#1e3a8a",   # deep blue
    "accent":    "#3b82f6",   # blue
    "text":      "#ffffff",   # default — white on the dark navy bg
    "muted":     "#94a3b8",   # subdued slate
    "success":   "#22c55e",   # green
    "warning":   "#f59e0b",   # amber
    "error":     "#ef4444",   # red (lighter than primary on purpose)
    "info":      "#3b82f6",   # same as accent — informational chrome
}


# ---------------------------------------------------------------------------
# Defaults for ``icon(name, color=..., size=...)``. Centralised so tests
# and consuming docs reference one source of truth.
# ---------------------------------------------------------------------------
DEFAULT_COLOR: str = "text"
DEFAULT_SIZE: int = 24


__all__ = [
    "IconNotFoundError",
    "UnknownColorError",
    "ICON_NAMES",
    "SEMANTIC_COLORS",
    "DEFAULT_COLOR",
    "DEFAULT_SIZE",
]
