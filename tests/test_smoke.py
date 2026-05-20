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


# ── Platform-stabilization smoke (added with UI Platform Baseline v1) ──
#
# Every Phoenix app inherits these checks. Keep them lightweight + fast.

def test_make_qss_non_empty() -> None:
    """The canonical QSS resource resolves to a non-empty stylesheet.

    Both forms are checked:
      - the package-data ``phoenix_style.qss`` file
      - the embedded fallback string in ``_embedded_qss._EMBEDDED_QSS``
    """
    from pathlib import Path
    import phoenix_commons.theme as theme_pkg
    qss_file = Path(theme_pkg.__file__).parent / "phoenix_style.qss"
    assert qss_file.exists(), f"missing canonical QSS at {qss_file}"
    file_text = qss_file.read_text(encoding="utf-8")
    assert len(file_text) > 5000, (
        f"canonical QSS shrank to {len(file_text)} chars — likely truncated"
    )

    from phoenix_commons.theme._embedded_qss import _EMBEDDED_QSS
    assert isinstance(_EMBEDDED_QSS, str)
    assert len(_EMBEDDED_QSS) > 5000, (
        f"embedded QSS fallback shrank to {len(_EMBEDDED_QSS)} chars"
    )


def test_component_instantiation(qtbot) -> None:
    """Every public widget must construct under offscreen Qt.

    Doesn't render or interact — just proves the constructors don't
    raise. qtbot manages the QApplication lifecycle.
    """
    from phoenix_commons.widgets import (
        PrimaryButton, SecondaryButton, TertiaryButton,
        Panel, PageTitle, PageSubtitle, SectionTitle, HintLabel,
        PhoenixTable, UpdateBanner,
    )
    # Widgets that accept an optional text label
    for cls in (
        PrimaryButton, SecondaryButton, TertiaryButton,
        Panel, PageTitle, PageSubtitle, SectionTitle, HintLabel,
    ):
        try:
            w = cls("smoke")
        except TypeError:
            w = cls()
        qtbot.addWidget(w)

    # PhoenixTable — no args
    qtbot.addWidget(PhoenixTable())

    # UpdateBanner — requires (current_version, latest_version) positional args
    qtbot.addWidget(UpdateBanner("0.1.0", "0.2.0"))


def test_no_scroll_instantiation(qtbot) -> None:
    """The no-scroll widget family must also construct."""
    from phoenix_commons.widgets.no_scroll import (
        NoScrollComboBox, NoScrollSpinBox,
        NoScrollDoubleSpinBox, NoScrollDateEdit,
    )
    for cls in (
        NoScrollComboBox, NoScrollSpinBox,
        NoScrollDoubleSpinBox, NoScrollDateEdit,
    ):
        w = cls()
        qtbot.addWidget(w)


def test_canonical_token_names_present_in_qss() -> None:
    """The canonical QSS contains locked tokens literally + brand sentinels.

    Locked tokens (BG, SURFACE, …) appear as hex literals because they're
    universal across every Phoenix tool. Brand tokens (PRIMARY, SECONDARY,
    ACCENT) appear as ``__BRAND_*__`` sentinels per ADR-016 — substituted
    at apply time against the active :class:`BrandProfile`.

    Guards against:
      - QSS regenerated with a different palette (e.g. someone accidentally
        lifting ValveMaster's legacy gray "System B" colours)
      - brand tokens accidentally un-sentinelized (which would bake the
        default brand in and silently break PCC-style overrides)
    """
    from pathlib import Path
    import phoenix_commons.theme as theme_pkg
    qss = (Path(theme_pkg.__file__).parent / "phoenix_style.qss").read_text(
        encoding="utf-8"
    )

    # Locked tokens — must appear literally.
    locked_substrings = [
        "#0a0e27",   # BG
        "#141829",   # SURFACE
    ]
    missing_locked = [s for s in locked_substrings if s.lower() not in qss.lower()]
    assert not missing_locked, (
        f"canonical Phoenix locked-token(s) missing from QSS: {missing_locked!r}"
    )

    # Brand sentinels — must appear (ADR-016).
    brand_sentinels = [
        "__BRAND_PRIMARY__",
        "__BRAND_SECONDARY__",
        "__BRAND_ACCENT__",
    ]
    missing_sentinels = [s for s in brand_sentinels if s not in qss]
    assert not missing_sentinels, (
        f"brand sentinel(s) missing from QSS: {missing_sentinels!r} — "
        f"BrandProfile override path is broken"
    )
