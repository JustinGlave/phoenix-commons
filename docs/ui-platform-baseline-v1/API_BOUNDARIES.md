# API_BOUNDARIES.md

> What's public, what's private, what's unstable, and how that gets
> enforced. Codifies the import contract apps follow when consuming
> `phoenix-commons`.

## Core rule

**The public API is exactly what each package's `__init__.py`
re-exports.** Everything else is implementation detail and may change
without notice in any version bump.

If a name appears in a package's `__all__`, it's public.
If a name appears only in a submodule (and not re-exported from the
package `__init__`), it's **conditionally public** — apps may import
it, but commons reserves the right to relocate it during a phase.

The signals, in order of strength:

| Signal | Meaning |
|--------|---------|
| Re-exported from a package `__init__.py` AND listed in `__all__` | **Stable public API.** Will not break across MINOR versions. |
| Defined in a submodule with `__all__`, but not re-exported from the package | Conditionally public. Stable across PATCH; may move during MINOR. |
| Underscore prefix on the name (`_recolor`, `_resolve_color`, `_HEX_RE`) | **Private.** Do not import. Will change without notice. |
| Underscore prefix on the module (`_cache`, `_embedded_qss`, `_version`) | **Private module.** Do not import the module directly. |

## Public API surface (as of Phase 2.5)

These imports are stable. Apps may rely on them across `phoenix_commons`
MINOR versions. Breaking changes require a MAJOR bump.

### Package root

```python
from phoenix_commons import __version__
```

### Theme

```python
from phoenix_commons.theme import apply_dark_theme
```

### Theme — tokens (Phase 2.5)

```python
from phoenix_commons.theme.tokens import (
    # Module-level constants — Phoenix System A canonical palette
    BG, SURFACE, SURFACE_ALT,
    PRIMARY, SECONDARY, ACCENT,
    TEXT, MUTED,
    SUCCESS, WARNING, ERROR, INFO,
    # Semantic palette map (name → hex)
    SEMANTIC_COLORS,
    # PCC-compatible alias
    C,
)
```

### Icons

```python
from phoenix_commons.icons import (
    icon,                  # the loader
    clear_cache,           # test / explicit-invalidation helper
    ICON_NAMES,            # closed set of available icon names
    SEMANTIC_COLORS,       # re-exported from theme.tokens
    DEFAULT_COLOR,         # "text"
    DEFAULT_SIZE,          # 24
    IconNotFoundError,     # raised by icon() for unknown name
    UnknownColorError,     # raised for unrecognised color=
)
```

### Widgets

```python
from phoenix_commons.widgets import (
    PrimaryButton, SecondaryButton, TertiaryButton,
    PageTitle, PageSubtitle, SectionTitle, HintLabel,
    Panel, PhoenixTable, UpdateBanner, button_row,
)

from phoenix_commons.widgets.no_scroll import (
    NoScrollComboBox, NoScrollSpinBox,
    NoScrollDoubleSpinBox, NoScrollDateEdit,
)
```

`no_scroll` is reached via a submodule import (not re-exported from
`widgets/__init__`) so the smaller, more frequently-used widgets are
the default surface.

### Paths

```python
from phoenix_commons.paths import (
    is_frozen,
    user_data_dir,
    resource_path,
)
```

### Updater

```python
from phoenix_commons.updater import (
    UpdateInfo,
    check_for_update,
    download_and_apply,
)

from phoenix_commons.updater.qt import UpdateCheckThread
from phoenix_commons.updater.installer import UpdatePackageError
```

`UpdateCheckThread` is in a Qt-specific submodule so non-Qt callers
(headless tests, scripts) can use `check_for_update` without pulling
PySide6 into scope. `UpdatePackageError` lives in `installer` for the
same reason — callers that just want to catch `RuntimeError` don't
need to import it; callers that want to be specific about validation
failures can.

## Conditionally-public API

These are accessible today but reserved for relocation in a future
phase. Apps may use them; if they move, commons will provide a one-
line shim like `phoenix_commons.theme._embedded_qss` does.

```python
from phoenix_commons.theme.embedded_qss import EMBEDDED_QSS
from phoenix_commons.theme.tokens import (  # see above for the canonical list
    ...
)
from phoenix_commons.icons.registry import (
    ICON_NAMES, SEMANTIC_COLORS,
    DEFAULT_COLOR, DEFAULT_SIZE,
    IconNotFoundError, UnknownColorError,
)
```

The `theme.embedded_qss` module may eventually move under
`phoenix_commons/_generated/` (see PLATFORM_CONTRACT.md § Generated
artifacts policy). Apps that import `EMBEDDED_QSS` directly will get
a deprecation shim at the old import path during the transition.

## Private API

Underscore-prefixed names and underscore-prefixed modules:

| Surface | Why it's private |
|---------|-------------------|
| `phoenix_commons._version` | Versioning is a build concern; consumers read `phoenix_commons.__version__` |
| `phoenix_commons.icons._cache` | Internal cache implementation; consumers use `clear_cache` from the package `__init__` |
| `phoenix_commons.theme._embedded_qss` | Back-compat shim for the pre-Phase-2.1 `_EMBEDDED_QSS` import; new code imports from `phoenix_commons.theme.embedded_qss` |
| `phoenix_commons.icons.loader._recolor`, `_resolve_color`, `_load_svg_bytes`, `_render_qicon`, `_HEX_RE`, `_CURRENT_COLOR_PATTERNS` | Implementation details of the SVG rasterisation pipeline |
| `phoenix_commons.theme.apply._resource_path` | Implementation detail of the QSS loader; PyInstaller-aware path resolution |
| `phoenix_commons.updater.installer._validate_update_zip`, `_ps_literal`, `_build_*` | Internal helpers for the Windows update-apply pipeline |
| `phoenix_commons.updater.client._parse_version` | Internal version-tag parser |

## Unstable API

These exist on `main` but are not committed across versions. Use at
your own risk; commons may change them without a deprecation cycle.

| Surface | State |
|---------|-------|
| `phoenix_commons.theme.generate_embedded_qss.render`, `.main` | Generator CLI internals. The CLI invocation `python -m phoenix_commons.theme.generate_embedded_qss` is stable; the importable `render` function is not. |
| `phoenix_commons.icons._cache.get`, `.put`, `.size` | Internal cache mechanics. `clear` is reached only via `clear_cache`. |
| Anything not listed above and not underscore-prefixed | Implicit "depends on the wind direction" status — opening a commons PR to formally bless or rename is the way to get certainty. |

## Deprecation policy

Phase-2.5 baseline. May tighten in later phases.

1. **MAJOR bump** for any removal or signature change of a public API
   surface item.
2. **One MINOR version of overlap** for renames. Old name keeps
   working with a `DeprecationWarning`; new name is also live.
3. **Underscore module shim** for relocated modules — see
   `phoenix_commons.theme._embedded_qss` for the canonical example.
   The shim is a one-line `from .new_home import X as Y; __all__ = ["Y"]`.
4. **CHANGELOG.md entry required** for any removal, rename, or move.
   Format mirrors the `CHANGELOG.md` template the new-tool wizard
   generates (Keep-a-Changelog).
5. **No silent breaking changes** even for conditionally-public API
   between MINOR versions — at minimum, a one-line note in the
   release-notes / CHANGELOG.

## Enforcement

| Mechanism | Status |
|-----------|--------|
| `__all__` declared in every module that has public-ish surface | ✅ Phase 2.5 |
| Underscore prefix on private modules + functions | ✅ Phase 2.5 |
| Tests that exercise the public-API path explicitly (`tests/test_smoke.py` imports via the package `__init__`) | ✅ Phase 2.5 |
| Lint rule blocking app imports from underscore paths | Future (Phase 9 candidate) |
| `pyproject.toml` `py.typed` marker + typed `__all__` checking | Future (post-1.0) |
| Public-API change checklist in PR template | Future |

The contract is enforced at PR-review time today. Automation is a
later phase.

## How to add a new public API

1. Add the name to its module (e.g. a new widget class in
   `widgets/new_widget.py`).
2. Make sure the module declares `__all__` including the new name.
3. Re-export from the appropriate package `__init__.py` AND add to
   that package's `__all__`.
4. Add a smoke test (instantiation works under offscreen Qt).
5. Update this document's "Public API surface" section.
6. Update `PLATFORM_CONTRACT.md` if the new API belongs in an
   ownership category.
7. Bump `_version.py` per the rules above (MINOR for additions).
8. Add a `CHANGELOG.md` entry.

## How to remove or relocate a public API

1. Open an ADR if the surface has consumers (`docs/ui-platform-baseline-v1/DECISIONS.md`).
2. Land the new home first, with the old name kept as a shim.
3. Update consumers (one per session / PR per retrofit guidelines).
4. After at least one MINOR version of overlap, remove the shim.
5. Bump to a MAJOR version.

## See also

- `PLATFORM_CONTRACT.md` — ownership map; what each package is for
- `PACKAGING_CONTRACT.md` — runtime / package-data / installer contract
- `COMPONENT_CONTRACT.md` — widget extension rules (Phase 2.5)
- `ICON_POLICY.md` — icon promotion and naming rules (Phase 2.5)
- `DECISIONS.md` — ADRs (e.g. ADR-014 — canonical Python 3.12)
