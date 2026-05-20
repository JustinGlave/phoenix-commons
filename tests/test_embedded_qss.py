"""Phase 2.1 — tests for the generated embedded-QSS fallback.

Covers:

  1. ``embedded_qss.py`` exists and exports ``EMBEDDED_QSS``.
  2. ``EMBEDDED_QSS`` is non-empty.
  3. Canonical Phoenix System A tokens are present (``#0a0e27`` background
     and ``#dc2626`` accent red).
  4. The generator is **deterministic + idempotent**: re-running
     ``generate_embedded_qss`` against the current QSS produces output
     byte-identical to the file on disk. This is the stale-fallback CI guard.
  5. The ``apply_dark_theme`` import surface still works after the migration
     (smoke check that the runtime-resource fallback path didn't regress).
  6. The deprecated back-compat shim at ``_embedded_qss`` still re-exports
     ``_EMBEDDED_QSS`` for any external consumer that hasn't migrated.
"""
from __future__ import annotations

from pathlib import Path


def test_embedded_qss_module_exists_and_exports_constant() -> None:
    """The generated module must expose ``EMBEDDED_QSS`` as a string."""
    from phoenix_commons.theme.embedded_qss import EMBEDDED_QSS
    assert isinstance(EMBEDDED_QSS, str)


def test_embedded_qss_non_empty() -> None:
    """``EMBEDDED_QSS`` must be substantial — catches catastrophic truncation."""
    from phoenix_commons.theme.embedded_qss import EMBEDDED_QSS
    assert len(EMBEDDED_QSS) > 5000, (
        f"EMBEDDED_QSS shrank to {len(EMBEDDED_QSS)} chars — likely truncated"
    )


def test_embedded_qss_contains_locked_tokens_and_brand_sentinels() -> None:
    """Phoenix System A locked tokens must appear literally; brand tokens
    must appear as ADR-016 sentinels (post Phase 3A sentinelization).

    Guards against:
      - accidental regeneration from a wrong / forked QSS file
        (e.g. someone lifting ValveMaster's legacy gray palette)
      - accidental un-sentinelization of brand tokens (which would
        bake the default brand into the QSS and silently break the
        BrandProfile override path)
    """
    from phoenix_commons.theme.embedded_qss import EMBEDDED_QSS

    # Locked tokens — present literally.
    assert "#0a0e27" in EMBEDDED_QSS, "missing canonical background #0a0e27"
    assert "#141829" in EMBEDDED_QSS, "missing canonical surface #141829"

    # Brand sentinels — present (substituted at apply time per ADR-016).
    assert "__BRAND_PRIMARY__" in EMBEDDED_QSS, (
        "missing __BRAND_PRIMARY__ sentinel — brand override path broken"
    )
    assert "__BRAND_SECONDARY__" in EMBEDDED_QSS, (
        "missing __BRAND_SECONDARY__ sentinel — brand override path broken"
    )
    assert "__BRAND_ACCENT__" in EMBEDDED_QSS, (
        "missing __BRAND_ACCENT__ sentinel — brand override path broken"
    )

    # Brand defaults must NOT be baked into the QSS — they live in tokens.py
    # as DEFAULT_BRAND values, never literally in the QSS itself.
    assert "#dc2626" not in EMBEDDED_QSS, (
        "default brand red #dc2626 leaked into QSS — sentinel substitution broken"
    )
    assert "#1e3a8a" not in EMBEDDED_QSS, (
        "default brand secondary #1e3a8a leaked into QSS — sentinel substitution broken"
    )
    assert "#3b82f6" not in EMBEDDED_QSS, (
        "default brand accent #3b82f6 leaked into QSS — sentinel substitution broken"
    )


def test_generator_is_deterministic_and_idempotent() -> None:
    """Re-running the generator must produce byte-identical output.

    This is the **stale-fallback CI guard**: if ``phoenix_style.qss``
    changes but the embedded module isn't regenerated, this test fails
    on the next CI run. CI / future lint hook can also run
    ``python -m phoenix_commons.theme.generate_embedded_qss`` and
    ``git diff --exit-code`` to enforce regeneration in PR review.
    """
    import phoenix_commons.theme as theme_pkg
    from phoenix_commons.theme.generate_embedded_qss import render

    qss_path  = Path(theme_pkg.__file__).parent / "phoenix_style.qss"
    out_path  = Path(theme_pkg.__file__).parent / "embedded_qss.py"
    assert qss_path.exists(), f"canonical QSS missing at {qss_path}"
    assert out_path.exists(), f"generated module missing at {out_path}"

    qss_text   = qss_path.read_text(encoding="utf-8")
    rendered   = render(qss_text)
    on_disk    = out_path.read_text(encoding="utf-8")

    assert rendered == on_disk, (
        "embedded_qss.py is STALE relative to phoenix_style.qss. "
        "Re-run: python -m phoenix_commons.theme.generate_embedded_qss"
    )


def test_apply_dark_theme_imports_after_migration() -> None:
    """apply_dark_theme must still resolve after the import-path migration."""
    from phoenix_commons.theme import apply_dark_theme
    assert callable(apply_dark_theme)


def test_apply_dark_theme_fallback_uses_embedded_qss(qtbot, monkeypatch, tmp_path) -> None:
    """When the on-disk ``phoenix_style.qss`` is missing, ``apply_dark_theme``
    must apply the embedded fallback instead of leaving the app unstyled.

    Tested by monkey-patching ``_resource_path`` to point at a non-existent
    file (simulating the auto-updater-replaced-exe-but-not-_internal/ case).

    Post Phase 3A (ADR-016), ``apply_dark_theme`` substitutes brand
    sentinels at apply time, so the styleSheet is the brand-substituted
    form of ``EMBEDDED_QSS`` — not literally ``EMBEDDED_QSS`` itself.
    """
    from PySide6.QtWidgets import QApplication
    from phoenix_commons.theme import apply as apply_mod
    from phoenix_commons.theme.embedded_qss import EMBEDDED_QSS
    from phoenix_commons.theme.tokens import DEFAULT_BRAND

    fake_path = tmp_path / "does_not_exist.qss"
    monkeypatch.setattr(apply_mod, "_resource_path", lambda _name: str(fake_path))

    app = QApplication.instance() or QApplication([])
    apply_mod.apply_dark_theme(app)

    sheet = app.styleSheet()

    # The fallback path was taken — sheet must be derived from EMBEDDED_QSS.
    # Concrete signal: sentinels gone, default-brand hex literals appeared,
    # and the substituted form matches the in-test substitution.
    expected = apply_mod._substitute_brand(EMBEDDED_QSS, DEFAULT_BRAND)
    assert sheet == expected, (
        "fallback path didn't apply substituted EMBEDDED_QSS — runtime would "
        "render unstyled or render sentinels-as-invalid-colors"
    )
    # And the sheet must NOT contain any brand sentinels after substitution.
    assert "__BRAND_PRIMARY__" not in sheet
    assert "__BRAND_SECONDARY__" not in sheet
    assert "__BRAND_ACCENT__" not in sheet
    # The default-brand primary hex must have been substituted in.
    assert "#dc2626" in sheet


def test_substitute_brand_replaces_all_three_sentinels() -> None:
    """``_substitute_brand`` replaces every ``__BRAND_*__`` sentinel.

    Unit-level test of the substitution helper — no Qt needed.
    """
    from phoenix_commons.theme.apply import _substitute_brand
    from phoenix_commons.theme.tokens import BrandProfile

    src = (
        "color: __BRAND_PRIMARY__; background: __BRAND_SECONDARY__; "
        "border: 1px solid __BRAND_ACCENT__;"
    )
    bp = BrandProfile(primary="#aabbcc", secondary="#112233", accent="#445566")
    out = _substitute_brand(src, bp)

    assert "__BRAND_PRIMARY__" not in out
    assert "__BRAND_SECONDARY__" not in out
    assert "__BRAND_ACCENT__" not in out
    assert "#aabbcc" in out
    assert "#112233" in out
    assert "#445566" in out


def test_apply_dark_theme_pcc_brand_substitutes_orange_teal(qtbot) -> None:
    """End-to-end: PCC-style brand profile produces orange + teal in styleSheet.

    Pins the override path that PCC's retrofit (Phase 3C) will exercise.
    Without this test, a regression in ``apply_dark_theme``'s
    substitution wiring would only surface during PCC's retrofit PR —
    too late for a clean fix.
    """
    from PySide6.QtWidgets import QApplication
    from phoenix_commons.theme import apply_dark_theme
    from phoenix_commons.theme.tokens import BrandProfile

    pcc_brand = BrandProfile(
        primary="#E8783C",
        secondary="#3CB8AE",
        accent="#3CB8AE",
    )
    app = QApplication.instance() or QApplication([])
    apply_dark_theme(app, brand=pcc_brand)

    sheet = app.styleSheet()

    # PCC brand values present.
    assert "#E8783C" in sheet, "PCC orange did not substitute into styleSheet"
    assert "#3CB8AE" in sheet, "PCC teal did not substitute into styleSheet"

    # Default brand values absent (substitution must replace, not append).
    assert "#dc2626" not in sheet, "default brand red leaked through PCC override"
    assert "#1e3a8a" not in sheet, "default brand secondary leaked through PCC override"
    assert "#3b82f6" not in sheet, "default brand accent leaked through PCC override"

    # Sentinels gone.
    assert "__BRAND_PRIMARY__" not in sheet
    assert "__BRAND_SECONDARY__" not in sheet
    assert "__BRAND_ACCENT__" not in sheet


def test_legacy_underscore_shim_still_works() -> None:
    """``_embedded_qss._EMBEDDED_QSS`` must still resolve via the shim.

    Removal target: this assertion goes away once Phase 7 / 8 retrofits
    have confirmed no consumer imports the underscored name.
    """
    from phoenix_commons.theme._embedded_qss import _EMBEDDED_QSS
    from phoenix_commons.theme.embedded_qss import EMBEDDED_QSS
    assert _EMBEDDED_QSS == EMBEDDED_QSS, (
        "legacy shim _EMBEDDED_QSS diverged from canonical EMBEDDED_QSS"
    )
