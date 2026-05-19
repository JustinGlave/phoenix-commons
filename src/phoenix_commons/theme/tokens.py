"""tokens.py — Phoenix System A canonical palette.

The single source of truth for every named colour value used across
the Phoenix UI Platform. Other modules (the QSS file, the icon
loader, the QPalette setup in :mod:`phoenix_commons.theme.apply`,
future widgets) consume these constants rather than redefining hex
literals inline.

**The forbidden anti-pattern:**

    # Don't do this anywhere except inside this module:
    button.setStyleSheet("color: #dc2626")

Instead:

    from phoenix_commons.theme.tokens import PRIMARY
    button.setStyleSheet(f"color: {PRIMARY}")

Or — preferably — set an ``objectName`` and let ``phoenix_style.qss``
apply the colour. Tokens are for code that genuinely needs the hex
value at runtime (e.g. recolouring an SVG, composing a gradient).

**Token addition policy:**

1. Tokens are added through a commons PR, not by app developers.
2. New tokens must be semantically named (``ACCENT``, not
   ``BLUE_3B82F6``). Hex values change; meanings persist.
3. If two apps independently want the same colour, that's strong
   evidence the value belongs in commons. Open a PR.
4. If an app needs a value that's already in commons under a different
   name (e.g. ``ACCENT`` instead of inventing ``LINK_COLOR``), use
   the existing name. Duplicate semantics are worse than misnaming.

**Forward compatibility:**

The :data:`SEMANTIC_COLORS` map is consumed today by
:mod:`phoenix_commons.icons.registry` (the icon loader's colour
palette). Future widget code, QSS-generation tooling, and the
new-tool wizard will all import from here. The :data:`C` alias is
provided so PCC's ``theme.py`` (which exports a ``C`` dict of the
same shape) retrofits to commons with zero call-site changes.

**Phoenix System A — the source of truth:**

The hex values below are the canonical Phoenix dark-navy palette
established by Phoenix CAD's ``ui/style.py`` and embedded in
``phoenix_style.qss``. ValveMaster's legacy grey palette
(``#1c1c1c``, ``#2a2a2a``) is **System B** and is deprecated —
not represented here.
"""
from __future__ import annotations


# ---------------------------------------------------------------------------
# Phoenix System A — module-level constants
# ---------------------------------------------------------------------------

# Backgrounds + surfaces (the dark navy chrome).
BG          = "#0a0e27"   # base canvas
SURFACE     = "#141829"   # cards / panels / inputs
SURFACE_ALT = "#0f1219"   # alternating rows / muted surface variant

# Brand + interaction colours.
PRIMARY     = "#dc2626"   # red — primary / destructive
SECONDARY   = "#1e3a8a"   # deep blue — secondary chrome
ACCENT      = "#3b82f6"   # blue — links / highlights / focus

# Text + ink.
TEXT        = "#ffffff"   # white — primary text on the dark navy bg
MUTED       = "#94a3b8"   # subdued slate — secondary / disabled text

# Semantic status colours.
SUCCESS     = "#22c55e"   # green — confirmations
WARNING     = "#f59e0b"   # amber — warnings (non-fatal)
ERROR       = "#ef4444"   # red — errors (lighter than PRIMARY on purpose)
INFO        = ACCENT      # blue — informational chrome (aliased to ACCENT)


# ---------------------------------------------------------------------------
# Semantic palette map (name → hex).
#
# Consumed by phoenix_commons.icons.loader.icon() for the
# ``color="primary"`` semantic API. Future widget code can use this
# the same way without having to know the underlying constant names.
# ---------------------------------------------------------------------------
SEMANTIC_COLORS: dict[str, str] = {
    "primary":   PRIMARY,
    "secondary": SECONDARY,
    "accent":    ACCENT,
    "text":      TEXT,
    "muted":     MUTED,
    "success":   SUCCESS,
    "warning":   WARNING,
    "error":     ERROR,
    "info":      INFO,
}


# ---------------------------------------------------------------------------
# PCC-compatible alias.
#
# Phoenix Command Center's ``theme.py`` exposes a ``C`` dict of
# semantic-name → hex. Re-exporting under the same name means PCC's
# retrofit to commons is a one-line import swap rather than a
# rewrite of every call site:
#
#     # PCC source today:
#     from theme import C
#     button.setStyleSheet(f"color: {C['primary']}")
#
#     # Post-retrofit:
#     from phoenix_commons.theme.tokens import C
#     button.setStyleSheet(f"color: {C['primary']}")
# ---------------------------------------------------------------------------
C: dict[str, str] = SEMANTIC_COLORS


__all__ = [
    # Module-level constants
    "BG", "SURFACE", "SURFACE_ALT",
    "PRIMARY", "SECONDARY", "ACCENT",
    "TEXT", "MUTED",
    "SUCCESS", "WARNING", "ERROR", "INFO",
    # Dict APIs
    "SEMANTIC_COLORS",
    "C",
]
