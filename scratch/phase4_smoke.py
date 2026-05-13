"""Phase 4 — PyInstaller compatibility smoke test.

This is the gate that determines whether Phase 5 can ship a commons-backed
wizard template (editable install + ``--collect-all phoenix_commons``), or
whether Plan B (vendoring under ``vendor/phoenix_commons/``) needs to be
activated.

What the smoke test exercises:
  - ``import phoenix_commons``
  - ``apply_dark_theme(app)`` runs without raising
  - ``PrimaryButton``, ``Panel``, ``PhoenixTable``, ``UpdateBanner``
    instantiate without raising
  - the bundled ``phoenix_style.qss`` is resolvable via
    ``phoenix_commons.theme.apply._resource_path``
  - the embedded-QSS fallback string is reachable

Output:
  A JSON success marker is written to
  ``<TEMP>/phoenix_commons_phase4_marker.json``. The verification step
  parses this file to assert the smoke test passed end-to-end.

This script never enters ``app.exec()`` — it imports, instantiates, writes
the marker, and exits. ``--windowed`` PyInstaller builds have no console,
so the marker is the only way to know what happened.
"""

from __future__ import annotations

import json
import os
import sys
import tempfile
import traceback
from pathlib import Path

MARKER_PATH = Path(tempfile.gettempdir()) / "phoenix_commons_phase4_marker.json"

result: dict = {
    "status": "starting",
    "marker_path": str(MARKER_PATH),
}


def _walk_collected_commons(meipass: str) -> list[str]:
    """Return every file under ``<_MEIPASS>/phoenix_commons/`` so the report
    can show exactly what PyInstaller's ``--collect-all`` actually bundled."""
    commons_root = Path(meipass) / "phoenix_commons"
    if not commons_root.is_dir():
        return []
    out: list[str] = []
    for root, _dirs, files in os.walk(commons_root):
        for fname in files:
            rel = os.path.relpath(os.path.join(root, fname), meipass)
            out.append(rel.replace("\\", "/"))
    return sorted(out)


try:
    # ── 1. Basic import ───────────────────────────────────────────────────
    import phoenix_commons
    result["phoenix_commons_version"] = phoenix_commons.__version__

    # ── 2. Theme imports + run ────────────────────────────────────────────
    from phoenix_commons.theme import apply_dark_theme
    from phoenix_commons.theme.apply import _resource_path
    from phoenix_commons.theme._embedded_qss import _EMBEDDED_QSS

    from PySide6.QtWidgets import QApplication

    app = QApplication.instance() or QApplication(sys.argv)
    apply_dark_theme(app)
    result["apply_dark_theme_ok"] = True
    result["qt_style_applied"] = bool(app.style())
    result["stylesheet_set"] = bool(app.styleSheet())

    # ── 3. QSS resource path: did --collect-all bundle the .qss file? ─────
    qss_path = _resource_path("phoenix_style.qss")
    result["qss_resource_path"] = str(qss_path)
    result["qss_resource_exists"] = os.path.exists(qss_path)
    result["embedded_qss_length"] = len(_EMBEDDED_QSS)
    result["embedded_qss_has_phoenix_navy"] = "#0a0e27" in _EMBEDDED_QSS

    # ── 4. Widget instantiation ───────────────────────────────────────────
    from phoenix_commons.widgets import (
        PrimaryButton,
        Panel,
        PhoenixTable,
        UpdateBanner,
    )

    btn = PrimaryButton("Test")
    panel = Panel("Demo")
    table = PhoenixTable(2, 3)
    banner = UpdateBanner(
        current_version="0.1.0",
        latest_version="0.2.0",
        release_notes="Phase 4 smoke",
    )

    result["widgets_instantiated"] = [
        "PrimaryButton",
        "Panel",
        "PhoenixTable",
        "UpdateBanner",
    ]
    result["primary_button_text"] = btn.text()
    result["panel_object_name"] = panel.objectName()
    result["table_shape"] = [table.rowCount(), table.columnCount()]
    result["update_banner_object_name"] = banner.objectName()

    # ── 5. PyInstaller environment introspection ──────────────────────────
    frozen = bool(getattr(sys, "frozen", False))
    result["frozen"] = frozen
    result["python_executable"] = sys.executable

    if frozen:
        meipass = getattr(sys, "_MEIPASS", "")
        result["_meipass"] = str(meipass)
        commons_in_meipass = Path(meipass) / "phoenix_commons"
        result["commons_dir_in_meipass"] = commons_in_meipass.is_dir()
        result["collected_phoenix_commons_files"] = _walk_collected_commons(meipass)
    else:
        result["_meipass"] = None
        result["commons_dir_in_meipass"] = None
        result["collected_phoenix_commons_files"] = []

    result["status"] = "success"

except Exception as exc:  # noqa: BLE001 — we genuinely want any failure
    result["status"] = "error"
    result["error_type"] = type(exc).__name__
    result["error_msg"] = str(exc)
    result["traceback"] = traceback.format_exc()

# Always write the marker — even on failure, so verification can read it.
try:
    MARKER_PATH.write_text(json.dumps(result, indent=2), encoding="utf-8")
except Exception as marker_exc:  # noqa: BLE001
    print(f"FATAL: could not write marker {MARKER_PATH}: {marker_exc}", file=sys.stderr)

sys.exit(0 if result.get("status") == "success" else 1)
