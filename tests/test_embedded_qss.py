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


def test_embedded_qss_contains_canonical_tokens() -> None:
    """Phoenix System A canonical hex values must appear in the fallback.

    Guards against accidental regeneration from a wrong / forked QSS
    file (e.g. someone lifting ValveMaster's legacy gray palette).
    """
    from phoenix_commons.theme.embedded_qss import EMBEDDED_QSS
    assert "#0a0e27" in EMBEDDED_QSS, "missing canonical background #0a0e27"
    assert "#dc2626" in EMBEDDED_QSS, "missing canonical accent red #dc2626"


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
    """
    from PySide6.QtWidgets import QApplication
    from phoenix_commons.theme import apply as apply_mod
    from phoenix_commons.theme.embedded_qss import EMBEDDED_QSS

    fake_path = tmp_path / "does_not_exist.qss"
    monkeypatch.setattr(apply_mod, "_resource_path", lambda _name: str(fake_path))

    app = QApplication.instance() or QApplication([])
    apply_mod.apply_dark_theme(app)

    sheet = app.styleSheet()
    assert sheet == EMBEDDED_QSS, (
        "fallback path didn't apply the embedded QSS — runtime would render unstyled"
    )


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
