"""Tests for :class:`phoenix_commons.widgets.StatusBadge`.

Verifies the variant + compact-mode property contract that the QSS
selectors in ``phoenix_style.qss`` depend on. The QSS itself isn't
under test here (covered by ``test_embedded_qss``); these tests
exercise the widget API.
"""
from __future__ import annotations

import pytest

from phoenix_commons.widgets import StatusBadge


# ---------------------------------------------------------------------------
# Construction
# ---------------------------------------------------------------------------


def test_default_construction(qtbot) -> None:
    """Default args produce an unknown-variant non-compact badge."""
    badge = StatusBadge()
    qtbot.addWidget(badge)
    assert badge.text() == ""
    assert badge.variant == "unknown"
    assert badge.compact is False
    assert badge.objectName() == "StatusBadge"
    assert badge.property("variant") == "unknown"
    assert badge.property("compact") == "false"


def test_construction_with_text_and_variant(qtbot) -> None:
    badge = StatusBadge("Clean", variant="clean")
    qtbot.addWidget(badge)
    assert badge.text() == "Clean"
    assert badge.variant == "clean"
    assert badge.property("variant") == "clean"


def test_compact_mode_flows_to_property(qtbot) -> None:
    badge = StatusBadge("3 changes", variant="dirty", compact=True)
    qtbot.addWidget(badge)
    assert badge.compact is True
    assert badge.property("compact") == "true"


def test_invalid_variant_falls_back_to_unknown(qtbot) -> None:
    """Invalid variant doesn't raise; falls back to 'unknown'."""
    badge = StatusBadge("?", variant="not-a-variant")
    qtbot.addWidget(badge)
    assert badge.variant == "unknown"
    assert badge.property("variant") == "unknown"


# ---------------------------------------------------------------------------
# Variant set
# ---------------------------------------------------------------------------


def test_variants_is_frozen_set() -> None:
    """Variant set is a frozenset (immutable) — closed-set contract."""
    assert isinstance(StatusBadge.VARIANTS, frozenset)


def test_variants_contains_canonical_seven() -> None:
    """The seven canonical variants are present."""
    expected = {
        "clean", "dirty", "warning", "error",
        "unknown", "syncing", "scanning",
    }
    assert StatusBadge.VARIANTS == expected


@pytest.mark.parametrize(
    "variant",
    sorted(["clean", "dirty", "warning", "error",
            "unknown", "syncing", "scanning"]),
)
def test_each_canonical_variant_constructs(qtbot, variant: str) -> None:
    """Every canonical variant can be passed to the constructor."""
    badge = StatusBadge(variant.title(), variant=variant)
    qtbot.addWidget(badge)
    assert badge.variant == variant


# ---------------------------------------------------------------------------
# set_status
# ---------------------------------------------------------------------------


def test_set_status_updates_text_only(qtbot) -> None:
    """set_status without variant kwarg keeps the existing variant."""
    badge = StatusBadge("Clean", variant="clean")
    qtbot.addWidget(badge)
    badge.set_status("Scanning…")
    assert badge.text() == "Scanning…"
    assert badge.variant == "clean"  # unchanged


def test_set_status_updates_variant(qtbot) -> None:
    """set_status with variant kwarg updates both text and variant."""
    badge = StatusBadge("Unknown", variant="unknown")
    qtbot.addWidget(badge)
    badge.set_status("3 changes", variant="dirty")
    assert badge.text() == "3 changes"
    assert badge.variant == "dirty"
    assert badge.property("variant") == "dirty"


def test_set_status_invalid_variant_falls_back(qtbot) -> None:
    """Invalid variant in set_status falls back to unknown (no raise)."""
    badge = StatusBadge("Clean", variant="clean")
    qtbot.addWidget(badge)
    badge.set_status("?", variant="bogus")
    assert badge.variant == "unknown"


def test_set_status_to_same_variant_no_op(qtbot) -> None:
    """Setting variant to its current value is a no-op style-wise."""
    badge = StatusBadge("Clean", variant="clean")
    qtbot.addWidget(badge)
    # Should not raise; should just update text.
    badge.set_status("Still clean", variant="clean")
    assert badge.text() == "Still clean"
    assert badge.variant == "clean"


# ---------------------------------------------------------------------------
# Public-API surface
# ---------------------------------------------------------------------------


def test_statusbadge_exported_from_widgets() -> None:
    """StatusBadge is in phoenix_commons.widgets.__all__."""
    from phoenix_commons import widgets
    assert "StatusBadge" in widgets.__all__
    assert widgets.StatusBadge is StatusBadge


def test_variant_property_is_read_only(qtbot) -> None:
    """The ``variant`` property is read-only — callers use set_status."""
    badge = StatusBadge("Clean", variant="clean")
    qtbot.addWidget(badge)
    with pytest.raises(AttributeError):
        badge.variant = "dirty"  # type: ignore[misc]


def test_compact_property_is_read_only(qtbot) -> None:
    """The ``compact`` property is read-only — constructor-time only."""
    badge = StatusBadge("Clean", variant="clean", compact=True)
    qtbot.addWidget(badge)
    with pytest.raises(AttributeError):
        badge.compact = False  # type: ignore[misc]
