# CLAUDE.md — phoenix-commons

> Operator orientation for the Phoenix UI Platform repo. Canonical
> doctrine lives in `docs/ui-platform-baseline-v1/` — this file points
> at it, does not restate it.

## Purpose

Shared Python package consumed by every Phoenix Controls desktop
tool. Provides:

- `phoenix_commons.theme` — System A QSS + BrandProfile (ADR-016)
- `phoenix_commons.widgets` — Primary/Secondary/Tertiary buttons,
  Panel, PhoenixTable, UpdateBanner, no-scroll family
- `phoenix_commons.paths` — `is_frozen`, `user_data_dir`
- `phoenix_commons.updater` — auto-updater (full-folder + exe-only
  payload contracts per ADR-003)
- `phoenix_commons.icons` — Lucide UI icon set

**Library, not application.** No `build.bat`, no installer, no exe.
Distributed to consumers as a **git submodule + editable install**
per ADR-015; not published to PyPI.

## Operational entrypoints

```powershell
py -3.12 -m venv .venv                         # ADR-014 canonical
.\.venv\Scripts\python.exe -m pip install -e .[test]
$env:QT_QPA_PLATFORM = "offscreen"
.\.venv\Scripts\python.exe -m pytest -q tests/
```

CI runs the same on windows-latest, Python 3.12.

## Retrofit state

Stable platform. Phase 3A (Lab Layout Tool) + Phase 3B (Phoenix
Checkout) consume commons in production. Phase 3C / 8a / 8b retrofits
inherit a stable API surface — no opportunistic expansion during
those phases.

## Do NOT change casually

| Item | Reason |
|------|--------|
| Public-API surface (`phoenix_commons.theme/widgets/paths/updater/icons`) | Consumers import by name; renames break their imports |
| Locked theme tokens (BG `#0a0e27`, SURFACE `#141829`, TEXT, MUTED, status colours) | Universal per ADR-016; only brand slots (primary/secondary/accent) are overridable via `BrandProfile` |
| Light theme exclusion | Per ADR-011 commons is dark-only |
| Underscore-prefixed modules | Private per `API_BOUNDARIES.md`; consumers must not import |
| Generated artifacts (e.g. `_embedded_qss.py`) | Output of `tools/generate_embedded_qss.py` — edit the source `.qss`, regenerate |

## Canonical references

- `docs/ui-platform-baseline-v1/PLATFORM_CONTRACT.md`
- `docs/ui-platform-baseline-v1/MIGRATION_RULES.md`
- `docs/ui-platform-baseline-v1/DECISIONS.md` (full ADR series)
- `docs/ui-platform-baseline-v1/RETROFIT_PLAYBOOK.md`
- `CONTRIBUTING.md` (library-flavoured workflow)
