"""_embedded_qss.py — DEPRECATED back-compat shim (Phase 2.1).

This module used to contain a hand-maintained ``_EMBEDDED_QSS`` string
that mirrored ``phoenix_style.qss``. Phase 2.1 of the UI Platform
stabilization replaced that with a generated fallback at
``phoenix_commons.theme.embedded_qss`` (no leading underscore) produced
by ``phoenix_commons.theme.generate_embedded_qss``.

This shim re-exports the new module's content under the legacy name
so any external consumer that imports

    from phoenix_commons.theme._embedded_qss import _EMBEDDED_QSS

keeps working unchanged. New code should import the public name:

    from phoenix_commons.theme.embedded_qss import EMBEDDED_QSS

Removal target: this shim will be deleted once Phase 7 / Phase 8
production-tool retrofits land and we've confirmed no consumer
imports the underscored name. Until then it is a one-line forward.
"""
from __future__ import annotations

from .embedded_qss import EMBEDDED_QSS as _EMBEDDED_QSS

__all__ = ["_EMBEDDED_QSS"]
