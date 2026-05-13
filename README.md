# phoenix-commons

Shared design system, widgets, auto-updater, and utilities for the Phoenix Controls family of PySide6 desktop tools.

## Status

**Phase 1 — skeleton.** The package installs and imports but ships no behaviour yet. Theme + widgets land in Phase 2; paths + updater land in Phase 3.

The canonical rollout plan lives at `C:\Users\justing\.claude\plans\ok-now-we-have-lively-koala.md`. The frozen production-tool inventory is at `docs/production-inventory.md`.

## Install (development)

From a Phoenix tool repo that will eventually add this as a git submodule at `./commons`:

```
pip install -e ./commons
```

For now (Phase 1), `phoenix_commons` exposes only `__version__`. Real public API arrives in Phases 2–3:

```python
from phoenix_commons import __version__
```

## Layout

```
phoenix-commons/
├── pyproject.toml                 — package manifest
├── README.md                      — this file
├── src/phoenix_commons/           — the installable package
│   ├── theme/                     — apply_dark_theme + phoenix_style.qss   (Phase 2)
│   ├── widgets/                   — buttons, panel, table, banner, …       (Phase 2)
│   ├── updater/                   — GitHub Releases auto-updater          (Phase 3)
│   └── paths.py                   — user_data_dir, is_frozen, resource    (Phase 3)
├── tests/                         — smoke tests
├── docs/
│   └── production-inventory.md    — frozen snapshot of every deployed tool's identity, paths, build, and updater contract (Phase 0)
├── Design Items/                  — existing design references (will move to docs/ + assets/ later, not in this rollout)
├── AUDIT_METHODOLOGY.md           — existing audit methodology doc (unmoved)
├── audit-reviewer.md              — existing audit reviewer doc (unmoved)
└── phoenix-ui-reviewer.md         — existing UI reviewer doc (unmoved)
```

## Development

```
pip install -e .
pip install -e .[test]   # adds pytest
pytest -q tests/
```

## Versioning

Tracked in `src/phoenix_commons/_version.py`. Bump alongside any change to the public API.
