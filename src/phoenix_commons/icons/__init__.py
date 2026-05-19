"""icons — Phoenix UI icon loader (Phase 2.2).

Public API:

    from phoenix_commons.icons import icon

    btn.setIcon(icon("save"))
    btn.setIcon(icon("settings", color="primary"))
    btn.setIcon(icon("warning", size=18))

The catalog of available names is :data:`ICON_NAMES`. The semantic
colour palette is :data:`SEMANTIC_COLORS`. Both are intentionally
small — additions go through a commons PR.

See ``README.md`` next to this module for the philosophy, the
recolour strategy, sizing guidance, and the migration plan for the
emoji-icon usages still scattered through the production tools.
"""
from __future__ import annotations

from .cache import clear as clear_cache
from .loader import icon
from .registry import (
    DEFAULT_COLOR,
    DEFAULT_SIZE,
    ICON_NAMES,
    IconNotFoundError,
    SEMANTIC_COLORS,
    UnknownColorError,
)

__all__ = [
    "icon",
    "clear_cache",
    "ICON_NAMES",
    "SEMANTIC_COLORS",
    "DEFAULT_COLOR",
    "DEFAULT_SIZE",
    "IconNotFoundError",
    "UnknownColorError",
]
