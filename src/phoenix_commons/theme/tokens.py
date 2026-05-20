"""tokens.py — Phoenix System A canonical palette + brand-profile mechanism.

The single source of truth for every named colour value used across
the Phoenix UI Platform. Other modules (the QSS file, the icon
loader, the QPalette setup in :mod:`phoenix_commons.theme.apply`,
future widgets) consume these constants rather than redefining hex
literals inline.

Per ADR-016 (Phase 3A landed the mechanism), tokens fall into two
tiers:

* **Locked** (BG, SURFACE, SURFACE_ALT, TEXT, MUTED, SUCCESS,
  WARNING, ERROR) — apps may NOT override these at runtime.
  Accessibility / semantic / structural — drift here is a
  design-system fork.
* **Brand-profile variant-allowed** (PRIMARY, SECONDARY, ACCENT,
  with INFO aliased to ACCENT) — apps may override via the
  :class:`BrandProfile` mechanism below. Phoenix CAD / Job Tracker /
  Phoenix Checkout / ValveMaster (post Phase 8a) use the default
  profile; PCC registers a custom profile (orange + teal) when its
  retrofit lands.

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

from dataclasses import dataclass


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


# ---------------------------------------------------------------------------
# BrandProfile — the controlled accent-override mechanism per ADR-016.
#
# Three named brand-token slots (PRIMARY / SECONDARY / ACCENT) which
# apps may override at apply time. Locked tokens are NOT included
# here and cannot be overridden.
#
# Default values match the canonical constants above (red + deep blue
# + blue). PCC registers its own profile (orange + teal + teal); every
# other Phoenix tool uses ``DEFAULT_BRAND``.
#
# Usage pattern (consuming apps):
#
#     # Phoenix CAD / Job Tracker / Phoenix Checkout / ValveMaster:
#     apply_dark_theme(app)  # uses DEFAULT_BRAND implicitly
#
#     # PCC (when its retrofit lands):
#     PCC_BRAND = BrandProfile(
#         primary   = "#E8783C",
#         secondary = "#3CB8AE",
#         accent    = "#3CB8AE",
#     )
#     apply_dark_theme(app, brand=PCC_BRAND)
#
# The QSS substitution happens inside ``apply_dark_theme`` — see
# :mod:`phoenix_commons.theme.apply`. ``phoenix_style.qss`` carries
# sentinel tokens (``__BRAND_PRIMARY__`` etc.) that get string-
# substituted with the active profile's hex values at apply time.
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class BrandProfile:
    """Controlled accent-override profile per ADR-016.

    Three named slots. Defaults match commons canonical
    (:data:`PRIMARY` / :data:`SECONDARY` / :data:`ACCENT`). Frozen
    so accidental mutation can't drift a tool's brand at runtime.

    Adding a fourth slot requires a new ADR superseding ADR-016
    (the closed slot list is intentional — it bounds the
    divergence surface).
    """

    primary:   str = PRIMARY
    secondary: str = SECONDARY
    accent:    str = ACCENT


#: The commons-canonical brand profile. Used when ``apply_dark_theme``
#: is called without a ``brand=`` kwarg.
DEFAULT_BRAND: BrandProfile = BrandProfile()


__all__ = [
    # Module-level constants — locked tokens
    "BG", "SURFACE", "SURFACE_ALT",
    "TEXT", "MUTED",
    "SUCCESS", "WARNING", "ERROR",
    # Module-level constants — variant-allowed defaults
    "PRIMARY", "SECONDARY", "ACCENT", "INFO",
    # Dict APIs
    "SEMANTIC_COLORS",
    "C",
    # Brand-profile mechanism (ADR-016)
    "BrandProfile",
    "DEFAULT_BRAND",
]
