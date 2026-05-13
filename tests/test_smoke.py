"""Smoke tests for phoenix-commons.

Phase 1: verify the package installs cleanly, reports its version in the
expected MAJOR.MINOR.PATCH format, and that the submodule namespaces import.

Phase 2: verify the new public API (``apply_dark_theme`` and the widget set)
is importable. Instantiation tests live in the Phase 2 scratch smoke script
(they require a ``QApplication``, which is awkward to share across pytest
without ``pytest-qt``).

Richer instantiation tests will land alongside future phases or once
``pytest-qt`` is added to the dev dependencies.
"""

from __future__ import annotations

import re


# ── Phase 1: package skeleton ────────────────────────────────────────────────

def test_package_imports() -> None:
    """phoenix_commons must be importable."""
    import phoenix_commons
    assert phoenix_commons.__version__


def test_version_format() -> None:
    """__version__ must be MAJOR.MINOR.PATCH — Phoenix tools depend on this format."""
    import phoenix_commons
    assert re.fullmatch(r"\d+\.\d+\.\d+", phoenix_commons.__version__), (
        f"Expected 3-part numeric version, got {phoenix_commons.__version__!r}"
    )


def test_version_is_0_1_0() -> None:
    """Phase 1 ships the package at 0.1.0. Bumps happen alongside API changes."""
    import phoenix_commons
    assert phoenix_commons.__version__ == "0.1.0"


def test_submodules_importable() -> None:
    """Submodule namespaces must import cleanly."""
    from phoenix_commons import theme, widgets, updater
    assert theme is not None
    assert widgets is not None
    assert updater is not None


# ── Phase 2: theme + widgets ─────────────────────────────────────────────────

def test_phase2_theme_api() -> None:
    """apply_dark_theme is exported and callable (not invoked here — needs QApplication)."""
    from phoenix_commons.theme import apply_dark_theme
    assert callable(apply_dark_theme)


def test_phase2_embedded_qss_present() -> None:
    """The embedded QSS fallback must be a non-empty string."""
    from phoenix_commons.theme._embedded_qss import _EMBEDDED_QSS
    assert isinstance(_EMBEDDED_QSS, str)
    assert "QPushButton" in _EMBEDDED_QSS
    assert "#0a0e27" in _EMBEDDED_QSS  # Phoenix dark navy background


def test_phase2_phoenix_style_qss_packaged() -> None:
    """phoenix_style.qss ships alongside the theme module."""
    from pathlib import Path
    import phoenix_commons.theme as theme_pkg
    qss = Path(theme_pkg.__file__).parent / "phoenix_style.qss"
    assert qss.exists(), f"Expected QSS at {qss}"
    text = qss.read_text(encoding="utf-8")
    assert "QPushButton" in text
    assert "#0a0e27" in text


def test_phase2_widgets_public_api() -> None:
    """All public widget symbols must be importable from phoenix_commons.widgets."""
    from phoenix_commons.widgets import (
        PrimaryButton, SecondaryButton, TertiaryButton,
        PageTitle, PageSubtitle, SectionTitle, HintLabel,
        Panel, PhoenixTable, UpdateBanner, button_row,
    )
    # Types: subclasses of the expected Qt bases. Don't instantiate (needs QApplication).
    assert PrimaryButton.__name__ == "PrimaryButton"
    assert SecondaryButton.__name__ == "SecondaryButton"
    assert TertiaryButton.__name__ == "TertiaryButton"
    assert PageTitle.__name__ == "PageTitle"
    assert Panel.__name__ == "Panel"
    assert PhoenixTable.__name__ == "PhoenixTable"
    assert UpdateBanner.__name__ == "UpdateBanner"
    assert callable(button_row)


def test_phase2_no_scroll_submodule() -> None:
    """no_scroll subclasses are reachable via the dotted submodule path."""
    from phoenix_commons.widgets.no_scroll import (
        NoScrollComboBox,
        NoScrollSpinBox,
        NoScrollDoubleSpinBox,
        NoScrollDateEdit,
    )
    assert NoScrollComboBox.__name__ == "NoScrollComboBox"
    assert NoScrollSpinBox.__name__ == "NoScrollSpinBox"
    assert NoScrollDoubleSpinBox.__name__ == "NoScrollDoubleSpinBox"
    assert NoScrollDateEdit.__name__ == "NoScrollDateEdit"
