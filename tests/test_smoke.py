"""Smoke tests for phoenix-commons.

Phase 1 scope: only verify the package installs cleanly, reports its version
in the expected MAJOR.MINOR.PATCH format, and that the (currently empty)
submodules import without error.

Richer smoke tests (apply_dark_theme works, widgets instantiate, updater
client returns an UpdateInfo) land alongside their respective phases.
"""

from __future__ import annotations

import re


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
    """The Phase 1 submodule stubs must import cleanly even though they have no API yet."""
    from phoenix_commons import theme, widgets, updater
    assert theme is not None
    assert widgets is not None
    assert updater is not None
