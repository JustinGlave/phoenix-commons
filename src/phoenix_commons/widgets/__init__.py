"""Widgets — Phoenix Controls component helpers shared across the ATS app suite.

Use these instead of raw Qt widgets so every tool reads as one product.

Public API:
    Buttons:        PrimaryButton, SecondaryButton, TertiaryButton
    Typography:     PageTitle, PageSubtitle, SectionTitle, HintLabel
    Containers:     Panel
    Tables:         PhoenixTable
    Banners:        UpdateBanner
    Layout helper:  button_row

The ``no_scroll`` submodule (``NoScrollComboBox``, ``NoScrollSpinBox``,
``NoScrollDoubleSpinBox``, ``NoScrollDateEdit``) is reached via
``from phoenix_commons.widgets.no_scroll import ...`` — those are advanced
form-input subclasses that callers opt into when needed.

``BackgroundWatermarkWidget`` from the source ``components.py`` is intentionally
NOT ported in Phase 2 (deferred per the canonical plan — niche, app-specific).
"""

from phoenix_commons.widgets.buttons import (
    PrimaryButton,
    SecondaryButton,
    TertiaryButton,
)
from phoenix_commons.widgets.helpers import button_row
from phoenix_commons.widgets.panel import Panel
from phoenix_commons.widgets.table import PhoenixTable
from phoenix_commons.widgets.typography import (
    HintLabel,
    PageSubtitle,
    PageTitle,
    SectionTitle,
)
from phoenix_commons.widgets.update_banner import UpdateBanner

__all__ = [
    "PrimaryButton",
    "SecondaryButton",
    "TertiaryButton",
    "PageTitle",
    "PageSubtitle",
    "SectionTitle",
    "HintLabel",
    "Panel",
    "PhoenixTable",
    "UpdateBanner",
    "button_row",
]
