"""Phoenix design system loader.

Loads ``phoenix_style.qss`` from the runtime resource path (works in dev and
under PyInstaller ``--onedir`` frozen). Falls back to an embedded QSS string
so that auto-updates that only replace the .exe (not ``_internal/``) still
get correct styling.

Per ADR-016 (Phase 3A), the canonical QSS carries sentinel tokens for the
three brand-profile slots (``__BRAND_PRIMARY__``, ``__BRAND_SECONDARY__``,
``__BRAND_ACCENT__``). Substitution happens here, at apply time, against
the caller-supplied :class:`BrandProfile` (defaulting to
:data:`DEFAULT_BRAND` — Phoenix System A canonical red + deep blue + blue).

Ported from ``Phoenix_CAD_Tool/ui/style.py:21-58``. Adapted: the source-mode
``_resource_path`` resolves files next to this module (under
``phoenix_commons.theme``) instead of the package's parent, because the
canonical ``phoenix_style.qss`` now lives inside the package.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

from PySide6.QtGui import QColor, QPalette
from PySide6.QtWidgets import QApplication

from .embedded_qss import EMBEDDED_QSS
from .tokens import BrandProfile, DEFAULT_BRAND

__all__ = ["apply_dark_theme"]


# Sentinel tokens emitted by ``phoenix_style.qss``. Substituted at apply
# time per the active brand profile. Adding a fourth slot requires a new
# ADR superseding ADR-016 (the closed list is intentional).
_BRAND_SENTINELS: tuple[tuple[str, str], ...] = (
    ("__BRAND_PRIMARY__",   "primary"),
    ("__BRAND_SECONDARY__", "secondary"),
    ("__BRAND_ACCENT__",    "accent"),
)


def _resource_path(filename: str) -> str:
    """Resolve a resource path that works in dev and under PyInstaller.

    Source mode: ``filename`` is looked up alongside this module
    (``src/phoenix_commons/theme/<filename>``).
    Frozen mode: ``filename`` is looked up at
    ``_MEIPASS/phoenix_commons/theme/<filename>``. PyInstaller's
    ``--collect-all phoenix_commons`` preserves the package layout, and the
    ``[tool.setuptools.package-data]`` declaration in ``pyproject.toml``
    ensures ``*.qss`` files are included in the installed package.
    """
    if getattr(sys, "frozen", False):
        base = Path(getattr(sys, "_MEIPASS", "")) / "phoenix_commons" / "theme"
    else:
        base = Path(__file__).resolve().parent
    return str(base / filename)


def _substitute_brand(qss_text: str, brand: BrandProfile) -> str:
    """Replace ``__BRAND_*__`` sentinels with the active brand profile's hex.

    Plain string substitution — sentinels are designed not to collide with
    any legitimate QSS identifier (the leading + trailing ``__`` make them
    visually + lexically distinct).
    """
    for sentinel, attr in _BRAND_SENTINELS:
        qss_text = qss_text.replace(sentinel, getattr(brand, attr))
    return qss_text


def apply_dark_theme(
    app: QApplication,
    brand: BrandProfile | None = None,
) -> None:
    """Apply the Phoenix dark-navy theme: Fusion + dark palette + QSS.

    Parameters
    ----------
    app
        The :class:`QApplication` instance to style.
    brand
        Optional :class:`BrandProfile`. ``None`` (default) uses the
        commons-canonical :data:`DEFAULT_BRAND` (navy + red + blue).
        Apps that need PCC's orange + teal pass their own
        :class:`BrandProfile` here.

    The function:

    1. Switches the app to the ``Fusion`` Qt style.
    2. Sets a :class:`QPalette` whose brand-relevant slots
       (``BrightText`` / ``Highlight`` / ``Link``) follow the active
       brand profile; locked slots (``Window`` / ``Base`` / ``Text`` / …)
       use the canonical Phoenix hex values universally.
    3. Loads the canonical QSS from the package resource path (or the
       embedded fallback if the resource is missing — the auto-update
       "exe replaced but ``_internal/`` not refreshed" case).
    4. Substitutes brand sentinels in the QSS, then applies it via
       :meth:`QApplication.setStyleSheet`.
    """
    profile = brand if brand is not None else DEFAULT_BRAND

    app.setStyle("Fusion")

    # Locked QPalette slots — universal across every Phoenix tool.
    locked_palette = [
        (QPalette.ColorRole.Window,          QColor(10, 14, 39)),
        (QPalette.ColorRole.WindowText,      QColor(255, 255, 255)),
        (QPalette.ColorRole.Base,            QColor(20, 24, 41)),
        (QPalette.ColorRole.AlternateBase,   QColor(15, 18, 25)),
        (QPalette.ColorRole.ToolTipBase,     QColor(20, 24, 41)),
        (QPalette.ColorRole.ToolTipText,     QColor(255, 255, 255)),
        (QPalette.ColorRole.Text,            QColor(255, 255, 255)),
        (QPalette.ColorRole.Button,          QColor(20, 24, 41)),
        (QPalette.ColorRole.ButtonText,      QColor(255, 255, 255)),
        (QPalette.ColorRole.HighlightedText, QColor(255, 255, 255)),
    ]
    # Brand-profile slots — follow the active brand.
    brand_palette = [
        (QPalette.ColorRole.BrightText, QColor(profile.primary)),
        (QPalette.ColorRole.Highlight,  QColor(profile.accent)),
        (QPalette.ColorRole.Link,       QColor(profile.accent)),
    ]
    palette = QPalette()
    for role, color in locked_palette + brand_palette:
        palette.setColor(role, color)
    app.setPalette(palette)

    qss_path = _resource_path("phoenix_style.qss")
    if os.path.exists(qss_path):
        with open(qss_path, "r", encoding="utf-8") as fh:
            qss_text = fh.read()
    else:
        qss_text = EMBEDDED_QSS

    app.setStyleSheet(_substitute_brand(qss_text, profile))
