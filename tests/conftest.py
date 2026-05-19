"""pytest configuration for phoenix-commons smoke tests.

Sets ``QT_QPA_PLATFORM=offscreen`` BEFORE pytest-qt imports Qt — gives
CI a guaranteed headless surface so the widget-instantiation tests
work without a display server. The CI workflow also sets the env var
at the job level; this conftest is the defensive double-set.
"""
from __future__ import annotations

import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
