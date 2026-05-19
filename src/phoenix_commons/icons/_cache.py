"""_cache.py — internal QIcon cache for ``phoenix_commons.icons``.

Module-name underscore signals **this is private to the icons package**.
External code must never import ``phoenix_commons.icons._cache`` directly
— go through ``phoenix_commons.icons.clear_cache`` (the only function
re-exported from the package ``__init__``) for the legitimate consumer
need (test cache reset / explicit invalidation).

Why a dedicated module:

* Encapsulates the cache-key shape (``(name, color, size)``). The
  loader and the cache talk through ``get`` / ``put`` / ``clear``;
  nobody constructs keys directly.
* Lets tests reset the cache cleanly between cases via :func:`clear`
  without poking at private globals on ``loader``.
* No Qt imports at runtime — :class:`QIcon` is only referenced under
  :data:`typing.TYPE_CHECKING` so the module is importable from
  Qt-free contexts (CI lint, doc generation, etc.).

The cache is a plain dict (process-wide, no eviction). Icons are tiny
and the closed ``ICON_NAMES`` set bounds total entries — no LRU
machinery needed.
"""
from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from PySide6.QtGui import QIcon


# Cache key: (icon name, raw color argument, pixel size).
# Storing the *raw* color (e.g. "primary") rather than the resolved
# hex means a future change to SEMANTIC_COLORS invalidates the user-
# visible name without leaving stale resolved bytes behind.
CacheKey = tuple[str, str, int]

_CACHE: dict[CacheKey, "QIcon"] = {}


def get(key: CacheKey) -> "QIcon | None":
    """Return the cached :class:`QIcon` for ``key``, or ``None`` if absent."""
    return _CACHE.get(key)


def put(key: CacheKey, value: "QIcon") -> None:
    """Insert (or overwrite) ``value`` under ``key`` in the cache."""
    _CACHE[key] = value


def clear() -> None:
    """Drop every cached icon. Safe to call before/after any test."""
    _CACHE.clear()


def size() -> int:
    """Return the number of cached icons. Useful in tests."""
    return len(_CACHE)


__all__ = ["CacheKey", "get", "put", "clear", "size"]
