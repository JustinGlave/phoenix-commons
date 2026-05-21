"""registry.py — declared icon names + semantic colour palette.

Pure-Python, Qt-free. Importing this module must work from any context
(tests, headless CI, build scripts) without dragging in a QApplication.

Design notes:

* ``ICON_NAMES`` is a closed set. ``icon("foo")`` for any ``foo`` not
  listed here raises :class:`IconNotFoundError` with the available
  names suggested in the message. Closed-set semantics is what lets
  the IDE / lint surface typos at call time rather than runtime.
* ``SEMANTIC_COLORS`` is re-exported from
  :mod:`phoenix_commons.theme.tokens` (the canonical token module
  landed in Phase 2.5). Future palette changes live there; this
  module is a thin facade so the public icon API (``color="primary"``)
  keeps the same import path.
* Both maps are deliberately tiny. New names go through a commons PR.
"""
from __future__ import annotations

# SEMANTIC_COLORS is canonical in theme.tokens — re-exported here so
# the icon-side import stays stable even if tokens move under
# phoenix_commons.generated/ in a later phase.
from phoenix_commons.theme.tokens import SEMANTIC_COLORS


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
    "file-text",
    "git-branch",
    "hard-drive",
    "info",
    "layout-dashboard",
    "package",
    "plus",
    "refresh",
    "save",
    "search",
    "settings",
    "trash",
    "warning",
    "x",
})


# Semantic palette is canonical in theme.tokens. Re-exported above so
# `from phoenix_commons.icons.registry import SEMANTIC_COLORS` keeps
# working (and so the icon API documentation lists it in one place).
# Source of truth: ``phoenix_commons.theme.tokens.SEMANTIC_COLORS``.


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
