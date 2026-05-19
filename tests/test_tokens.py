"""Phase 2.5/2.6 — tests for ``phoenix_commons.theme.tokens``.

Pins the contract behind the canonical token module that landed in
Phase 2.5: every Phoenix System A constant is a valid hex literal;
:data:`SEMANTIC_COLORS` mirrors the constants by name; the ``C``
alias is the same dict; ``INFO`` is the documented alias for
``ACCENT``.

These tests do NOT exercise Qt — the tokens module is intentionally
Qt-free so it can be imported from CI lints, doc builds, scripts,
etc. without dragging in PySide6.
"""
from __future__ import annotations

import re


# Six-digit lowercase hex. The tokens module commits to one canonical
# form across the platform — the icons recolour code and any future
# QSS-generation tooling can rely on it.
_HEX_RE = re.compile(r"^#[0-9a-f]{6}$")

# Every constant the tokens module exposes plus its expected
# semantic-palette key, if any.
_PALETTE_PAIRS: tuple[tuple[str, str | None], ...] = (
    ("BG",          None),
    ("SURFACE",     None),
    ("SURFACE_ALT", None),
    ("PRIMARY",     "primary"),
    ("SECONDARY",   "secondary"),
    ("ACCENT",      "accent"),
    ("TEXT",        "text"),
    ("MUTED",       "muted"),
    ("SUCCESS",     "success"),
    ("WARNING",     "warning"),
    ("ERROR",       "error"),
    ("INFO",        "info"),
)


def test_every_constant_is_a_lowercase_six_digit_hex() -> None:
    from phoenix_commons.theme import tokens

    for name, _ in _PALETTE_PAIRS:
        value = getattr(tokens, name)
        assert isinstance(value, str), f"{name} must be a string"
        assert _HEX_RE.match(value), (
            f"{name}={value!r} must match #rrggbb (lowercase six-digit hex)"
        )


def test_semantic_colors_has_the_expected_keys() -> None:
    """``SEMANTIC_COLORS`` is the closed semantic palette."""
    from phoenix_commons.theme.tokens import SEMANTIC_COLORS

    expected = {key for _, key in _PALETTE_PAIRS if key is not None}
    assert set(SEMANTIC_COLORS) == expected


def test_semantic_colors_entries_match_module_constants() -> None:
    """``SEMANTIC_COLORS["primary"]`` is the same hex as the ``PRIMARY`` constant."""
    from phoenix_commons.theme import tokens

    for name, key in _PALETTE_PAIRS:
        if key is None:
            continue
        const_value = getattr(tokens, name)
        dict_value = tokens.SEMANTIC_COLORS[key]
        assert const_value == dict_value, (
            f"SEMANTIC_COLORS[{key!r}]={dict_value!r} doesn't match "
            f"tokens.{name}={const_value!r}"
        )


def test_info_is_an_alias_for_accent() -> None:
    """``INFO`` is documented as an alias for ``ACCENT`` (same blue)."""
    from phoenix_commons.theme.tokens import ACCENT, INFO, SEMANTIC_COLORS

    assert INFO == ACCENT
    assert SEMANTIC_COLORS["info"] == SEMANTIC_COLORS["accent"]


def test_c_alias_is_identical_to_semantic_colors() -> None:
    """``C`` is the PCC-compatible alias for ``SEMANTIC_COLORS``.

    Identity, not equality — PCC's retrofit relies on ``C`` BEING
    ``SEMANTIC_COLORS`` so mutations in one are visible in the other
    (defensive: no one should mutate either, but if they do, identity
    keeps them in sync).
    """
    from phoenix_commons.theme.tokens import C, SEMANTIC_COLORS

    assert C is SEMANTIC_COLORS


def test_tokens_module_is_qt_free() -> None:
    """Importing tokens must not require Qt to be importable.

    Verified by introspecting the module's imports — there must be no
    ``PySide6`` import path. This is the property that lets non-Qt
    contexts (CI lint, doc builds) consume the canonical palette.
    """
    import phoenix_commons.theme.tokens as tokens_mod

    # `tokens_mod.__dict__` only contains what was bound by the module
    # itself; modules its imports don't appear here unless re-bound.
    bound_names = set(tokens_mod.__dict__)
    qt_traces = {n for n in bound_names if "QtCore" in n or "PySide6" in n}
    assert not qt_traces, (
        f"tokens module accidentally pulled in Qt: {sorted(qt_traces)}"
    )


def test_all_export_matches_public_surface() -> None:
    """``__all__`` lists every name the docstring promises."""
    from phoenix_commons.theme import tokens

    expected = {
        "BG", "SURFACE", "SURFACE_ALT",
        "PRIMARY", "SECONDARY", "ACCENT",
        "TEXT", "MUTED",
        "SUCCESS", "WARNING", "ERROR", "INFO",
        "SEMANTIC_COLORS", "C",
    }
    assert set(tokens.__all__) == expected
