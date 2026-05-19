"""Phase 2.6 — packaging verification tests.

Pins the contracts the Phase 2.6 packaging-verification work made
explicit:

  1. Every package-data file declared in ``pyproject.toml`` is
     reachable via ``importlib.resources`` (the path PyInstaller
     ``--collect-data phoenix_commons`` and any consuming app
     will follow).
  2. The public API surface enumerated in ``API_BOUNDARIES.md``
     actually resolves through the package ``__init__`` re-exports.
  3. The Phase 2.5 cross-module wiring (``icons.SEMANTIC_COLORS``
     is the same object as ``theme.tokens.SEMANTIC_COLORS``) is
     in effect — the icon registry consumes from tokens, not a
     parallel copy.
  4. The generated artifact (``phoenix_commons.theme.embedded_qss``)
     is at the path the loader expects.
  5. ``pyproject.toml``'s ``[tool.setuptools.package-data]`` table
     declares both ``*.qss`` (theme) and ``*.svg``
     (icons.lucide).

No GUI, no network, no builds. Pure import + filesystem-via-
importlib.resources work.
"""
from __future__ import annotations

from importlib.resources import files


# ---------------------------------------------------------------------------
# Package-data resolution
# ---------------------------------------------------------------------------

def test_phoenix_style_qss_resolves_via_importlib_resources() -> None:
    """``phoenix_style.qss`` must be reachable through importlib.resources.

    This is the path PyInstaller follows for ``--collect-data
    phoenix_commons``. If this passes for an editable install, the
    frozen build will bundle the file too.
    """
    qss = files("phoenix_commons.theme") / "phoenix_style.qss"
    assert qss.is_file(), "phoenix_style.qss is not reachable as package data"
    body = qss.read_text(encoding="utf-8")
    assert len(body) > 5000, (
        f"phoenix_style.qss shrank to {len(body)} chars — likely truncated"
    )
    # Canonical Phoenix System A token must appear in the file.
    assert "#0a0e27" in body, "missing canonical bg token in phoenix_style.qss"


def test_every_icon_name_has_a_bundled_svg() -> None:
    """Every name in :data:`ICON_NAMES` resolves to a real SVG asset.

    Duplicates one of the icon-package-data tests intentionally —
    this version lives in the packaging-verification suite so the
    "package data survives" claim is locally legible from the
    packaging test module.
    """
    from phoenix_commons.icons import ICON_NAMES

    base = files("phoenix_commons.icons.lucide")
    for name in sorted(ICON_NAMES):
        svg = base / f"{name}.svg"
        assert svg.is_file(), f"missing SVG asset for {name!r}"


def test_lucide_subpackage_has_at_least_the_starter_set() -> None:
    """The vendored SVG directory contains at least N SVGs, where N
    is :data:`ICON_NAMES` size.

    Defensive: if a future PR adds an SVG without registering its
    name in :data:`ICON_NAMES`, ``icon(...)`` would still refuse to
    load it (closed-set guard) — but the file would be silently
    bundled as dead weight. This test catches the inverse mistake.
    """
    from phoenix_commons.icons import ICON_NAMES

    base = files("phoenix_commons.icons.lucide")
    svgs = sorted(p.name for p in base.iterdir() if p.name.endswith(".svg"))
    assert len(svgs) >= len(ICON_NAMES), (
        f"icons/lucide/ has {len(svgs)} SVGs but ICON_NAMES declares "
        f"{len(ICON_NAMES)} names — registry is out of sync"
    )


# ---------------------------------------------------------------------------
# Generated artifact placement
# ---------------------------------------------------------------------------

def test_embedded_qss_module_at_expected_path() -> None:
    """The Phase 2.1 generated artifact lives at the path the loader expects.

    Verifies the Generated Artifacts Policy contract: the artifact is
    co-located with its sole consumer (the theme loader). Moving the
    artifact under ``_generated/`` is a future-phase concern with
    explicit trigger conditions (see PLATFORM_CONTRACT.md).
    """
    import phoenix_commons.theme.embedded_qss as embedded_mod

    assert hasattr(embedded_mod, "EMBEDDED_QSS")
    assert embedded_mod.__name__ == "phoenix_commons.theme.embedded_qss"


# ---------------------------------------------------------------------------
# Public-API resolution (smoke check the API_BOUNDARIES.md contract)
# ---------------------------------------------------------------------------

def test_full_public_api_resolves() -> None:
    """Every public name listed in API_BOUNDARIES.md resolves cleanly.

    If this passes from a fresh interpreter, an editable install in
    a consuming app's venv will too.
    """
    # phoenix_commons root
    from phoenix_commons import __version__  # noqa: F401

    # theme
    from phoenix_commons.theme import apply_dark_theme  # noqa: F401

    # theme.tokens
    from phoenix_commons.theme.tokens import (  # noqa: F401
        BG, SURFACE, SURFACE_ALT,
        PRIMARY, SECONDARY, ACCENT,
        TEXT, MUTED,
        SUCCESS, WARNING, ERROR, INFO,
        SEMANTIC_COLORS, C,
    )

    # icons
    from phoenix_commons.icons import (  # noqa: F401
        icon,
        clear_cache,
        ICON_NAMES,
        SEMANTIC_COLORS as icons_SEMANTIC_COLORS,
        DEFAULT_COLOR,
        DEFAULT_SIZE,
        IconNotFoundError,
        UnknownColorError,
    )

    # widgets
    from phoenix_commons.widgets import (  # noqa: F401
        PrimaryButton, SecondaryButton, TertiaryButton,
        PageTitle, PageSubtitle, SectionTitle, HintLabel,
        Panel, PhoenixTable, UpdateBanner, button_row,
    )

    from phoenix_commons.widgets.no_scroll import (  # noqa: F401
        NoScrollComboBox, NoScrollSpinBox,
        NoScrollDoubleSpinBox, NoScrollDateEdit,
    )

    # paths
    from phoenix_commons.paths import (  # noqa: F401
        is_frozen, user_data_dir, resource_path,
    )

    # updater
    from phoenix_commons.updater import (  # noqa: F401
        UpdateInfo, check_for_update, download_and_apply,
    )

    from phoenix_commons.updater.qt import UpdateCheckThread  # noqa: F401
    from phoenix_commons.updater.installer import UpdatePackageError  # noqa: F401


# ---------------------------------------------------------------------------
# Phase 2.5 cross-module wiring
# ---------------------------------------------------------------------------

def test_icons_consumes_tokens_semantic_colors() -> None:
    """``icons.SEMANTIC_COLORS`` and ``theme.tokens.SEMANTIC_COLORS`` are
    the same object.

    Pins the Phase 2.5 wiring decision: the icon registry re-exports
    from the tokens module (single source of truth). Without this
    identity check, a future refactor could accidentally create a
    parallel copy and the two dicts would drift silently.
    """
    from phoenix_commons.icons import SEMANTIC_COLORS as icons_palette
    from phoenix_commons.theme.tokens import SEMANTIC_COLORS as tokens_palette

    assert icons_palette is tokens_palette, (
        "icons.SEMANTIC_COLORS and tokens.SEMANTIC_COLORS are not the "
        "same object — the re-export wiring is broken"
    )


def test_icon_registry_imports_from_tokens_not_inlined() -> None:
    """The icon registry module sources its palette from tokens, not a
    locally-defined dict.

    Static-import check: inspect the registry module's source to
    confirm the import line is present. Catches the case where a
    well-meaning future edit re-inlines the palette dict for
    convenience.
    """
    import inspect

    from phoenix_commons.icons import registry as icons_registry

    src = inspect.getsource(icons_registry)
    assert "from phoenix_commons.theme.tokens import" in src, (
        "icons.registry no longer imports SEMANTIC_COLORS from theme.tokens"
    )


# ---------------------------------------------------------------------------
# pyproject.toml package-data declaration
# ---------------------------------------------------------------------------

def test_pyproject_declares_both_package_data_paths() -> None:
    """``pyproject.toml``'s ``[tool.setuptools.package-data]`` table
    must declare both *.qss (theme) AND *.svg (icons.lucide).

    Verifies the declaration so non-editable wheel installs (which
    Phase 2.6 dry-runs) actually bundle the assets.
    """
    from pathlib import Path

    repo_root = Path(__file__).resolve().parent.parent
    pyproject = repo_root / "pyproject.toml"
    assert pyproject.is_file(), f"pyproject.toml missing at {pyproject}"

    body = pyproject.read_text(encoding="utf-8")
    assert '"phoenix_commons.theme"' in body
    assert '*.qss' in body
    assert '"phoenix_commons.icons.lucide"' in body
    assert '*.svg' in body


# ---------------------------------------------------------------------------
# Public submodule exports
# ---------------------------------------------------------------------------

def test_every_submodule_with_public_surface_declares_all() -> None:
    """Every submodule that exports public names has an ``__all__``.

    Phase 2.5 added these. Regression guard: any future module that
    forgets to declare its public surface gets caught here rather
    than discovered when a consumer imports the wrong path.
    """
    import phoenix_commons
    import phoenix_commons.icons
    import phoenix_commons.icons.loader
    import phoenix_commons.icons.registry
    import phoenix_commons.paths
    import phoenix_commons.theme
    import phoenix_commons.theme.apply
    import phoenix_commons.theme.embedded_qss
    import phoenix_commons.theme.generate_embedded_qss
    import phoenix_commons.theme.tokens
    import phoenix_commons.updater
    import phoenix_commons.updater.client
    import phoenix_commons.updater.installer
    import phoenix_commons.updater.qt
    import phoenix_commons.widgets
    import phoenix_commons.widgets.buttons
    import phoenix_commons.widgets.helpers
    import phoenix_commons.widgets.no_scroll
    import phoenix_commons.widgets.panel
    import phoenix_commons.widgets.table
    import phoenix_commons.widgets.typography
    import phoenix_commons.widgets.update_banner

    modules_with_required_all = [
        phoenix_commons,
        phoenix_commons.icons,
        phoenix_commons.icons.loader,
        phoenix_commons.icons.registry,
        phoenix_commons.paths,
        phoenix_commons.theme,
        phoenix_commons.theme.apply,
        phoenix_commons.theme.generate_embedded_qss,
        phoenix_commons.theme.tokens,
        phoenix_commons.updater,
        phoenix_commons.updater.client,
        phoenix_commons.updater.installer,
        phoenix_commons.updater.qt,
        phoenix_commons.widgets,
        phoenix_commons.widgets.buttons,
        phoenix_commons.widgets.helpers,
        phoenix_commons.widgets.no_scroll,
        phoenix_commons.widgets.panel,
        phoenix_commons.widgets.table,
        phoenix_commons.widgets.typography,
        phoenix_commons.widgets.update_banner,
    ]
    missing = [
        mod.__name__ for mod in modules_with_required_all
        if not getattr(mod, "__all__", None)
    ]
    assert not missing, f"modules missing __all__: {missing}"
