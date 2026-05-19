"""lucide — vendored Lucide-icon SVG assets.

Exists as a Python sub-package (rather than a plain data directory) so
``importlib.resources.files("phoenix_commons.icons.lucide")`` is the
canonical way to enumerate / open the SVGs at runtime. That same import
path is what PyInstaller's ``--collect-data phoenix_commons`` follows,
so source-mode and frozen-mode share one resolution rule.

Hand-edit policy: the SVGs in this directory are vendored copies of
Lucide-icon source files (Lucide is MIT-licensed). Future Phase 2.x
may move ingestion behind a generator (per the Generated Artifacts
Policy in PLATFORM_CONTRACT.md); until then, drop new SVGs in here
and add their stem to ``phoenix_commons.icons.registry.ICON_NAMES``.
"""
