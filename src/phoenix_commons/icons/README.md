# `phoenix_commons.icons` — Phoenix UI icon infrastructure

Phase 2.2 of the UI Platform stabilization. Source-only foundation —
no production-tool migration runs from this phase. Apps continue to
use whatever they have today (emoji literals, app-local SVGs, ad-hoc
QIcons) until a separate, explicitly-approved retrofit phase swaps
them over.

---

## Philosophy

1. **One shared visual vocabulary across the Phoenix family.**
   Job Tracker's "settings" icon, Phoenix CAD's "settings" icon, and
   Phoenix Checkout's "settings" icon should all be visually identical
   without anyone manually keeping three copies in sync.
2. **Lucide only.**
   [Lucide](https://lucide.dev/) is MIT-licensed, vector-only, stroke-
   based, visually coherent, and actively maintained. Picking exactly
   one icon library eliminates the "every tool has its own style"
   problem.
3. **Recolouring is a first-class concern.**
   The same `save` icon needs to render white on a dark navy button,
   red on a destructive button, and muted-grey when disabled. The
   loader recolours at runtime — apps never ship pre-coloured copies.
4. **Semantic names only.**
   `save`, `settings`, `warning` — not `floppy-disk`, `gear-2`, or
   `triangle-with-bang`. Naming describes the user-facing action /
   meaning, not the visual shape. Closed-set semantics
   (`ICON_NAMES`) so typos surface at call time, not as silent
   blanks at render time.
5. **Generated derivatives, hand-curated source.**
   The SVG files in `lucide/` are vendored hand-curated source. Future
   phases may add a generated catalogue / registry alongside, per the
   Generated Artifacts Policy in `PLATFORM_CONTRACT.md` — but the SVGs
   themselves remain hand-managed because there are only ever a few
   dozen of them.

---

## API

```python
from phoenix_commons.icons import icon

btn.setIcon(icon("save"))                               # default colour (white)
btn.setIcon(icon("settings", color="primary"))          # semantic palette
btn.setIcon(icon("warning", size=18))                   # custom size
btn.setIcon(icon("trash", color="#dc2626", size=20))    # hex + size
```

Constants:

| Name | Type | Meaning |
|------|------|---------|
| `ICON_NAMES` | `frozenset[str]` | The closed set of available icon names |
| `SEMANTIC_COLORS` | `dict[str, str]` | Semantic palette name → hex literal |
| `DEFAULT_COLOR` | `"text"` | Default colour for omitted `color=` arg |
| `DEFAULT_SIZE` | `24` | Default square pixel size |

Exceptions:

| Name | Raised when |
|------|--------------|
| `IconNotFoundError` (inherits `KeyError`) | `icon(name)` for `name` not in `ICON_NAMES` |
| `UnknownColorError` (inherits `ValueError`) | `color=` is neither a semantic name nor a valid hex literal |

Test helper:

| Name | Purpose |
|------|---------|
| `clear_cache()` | Drop the in-memory cache (between tests, or after a SEMANTIC_COLORS change) |

---

## Naming

Current set (Phase 2.2 starter — 10 icons):

```
check    info      plus       refresh    save
search   settings  trash      warning    x
```

Rules for adding a name:

1. **Semantic, not visual.** `check` not `tick`. `x` not `cross`.
   `warning` not `triangle-bang`.
2. **Lowercase, hyphen-free where possible.** Prefer `arrow_right`
   over `arrow-right` if you ever need a two-word name (the stem
   becomes a `lucide/<name>.svg` filename — keep it filesystem-clean).
   The current set is single-word only.
3. **Map to a real Lucide icon.** Don't invent shapes. Find the
   closest Lucide name and rename it to the Phoenix semantic version
   if needed.
4. **PR-reviewed.** Names appear in app source for years. Adding one
   means committing to keeping it stable.

Adding a new icon:

1. Drop `lucide/<name>.svg` (raw export from Lucide, no edits).
2. Add `"<name>"` to `ICON_NAMES` in `registry.py` (alphabetised).
3. Add a test row in `tests/test_icons.py` exercising it (the
   `test_all_starter_icons_load` parametrize covers this automatically
   if you re-use that fixture).

---

## Sizing

| Pixel size | Typical use |
|------------|--------------|
| 14 / 16    | Inline text decorations, tiny tag chips |
| 18 / 20    | Toolbar buttons, table-row action buttons |
| **24** (default) | Primary buttons, sidebar items |
| 28 / 32    | Dialog headers, empty-state illustrations |
| 48+        | Onboarding splash, large feature callouts |

Pixmaps are rasterised at the requested size. Qt will downsample
sharply if a consuming widget renders smaller; for hi-DPI / sharp
upscaling, request the larger size explicitly:

```python
# Sharp on a 2x display:
btn.setIconSize(QSize(24, 24))
btn.setIcon(icon("save", size=48))
```

A future iteration may add multi-resolution pixmaps in a single
`QIcon` automatically. The current single-pixmap path is the simpler
foundation.

---

## Recolouring

Lucide SVGs ship with `stroke="currentColor"` — a CSS escape meaning
"inherit from the calling element's colour". Browsers honour this;
Qt's `QSvgRenderer` does **not** — it renders `currentColor` as opaque
black, which is invisible on the Phoenix dark navy bg.

The loader handles this by **byte-substituting `currentColor` for the
resolved hex** before parsing the SVG. Faster than QPainter
compositing, and produces cleaner output (no source-in alpha
artifacts at small sizes).

Semantic colour palette:

| Name | Hex | Use |
|------|-----|-----|
| `primary` | `#dc2626` | Accent red — destructive actions, brand emphasis |
| `secondary` | `#1e3a8a` | Deep blue — secondary action chrome |
| `accent` | `#3b82f6` | Blue — links, highlights, info chrome |
| `text` (default) | `#ffffff` | White — readable on the dark navy bg |
| `muted` | `#94a3b8` | Subdued slate — disabled / placeholder |
| `success` | `#22c55e` | Green — success states |
| `warning` | `#f59e0b` | Amber — warning states |
| `error` | `#ef4444` | Red — error states (lighter than `primary` on purpose) |
| `info` | `#3b82f6` | Blue — same as `accent` for informational chrome |

Hex literals also accepted: `color="#dc2626"` or `color="#fff"`.

---

## Caching

Each `(name, color, size)` triple is rasterised once and cached as a
`QIcon` in a process-wide dict. Subsequent calls return the same
instance. The cache key uses the *raw* colour argument (e.g.
`"primary"`) rather than the resolved hex, so a future change to
`SEMANTIC_COLORS["primary"]` invalidates old entries through their
user-visible name — no silent staleness.

Tests can reset the cache with `clear_cache()`. There's no automatic
eviction: `ICON_NAMES` is a closed set and Phoenix tools touch
maybe a dozen icons each, so total cache size is bounded by a small
constant.

A :class:`QApplication` must exist before any `icon()` call, because
:class:`QPixmap` construction does. This is consistent with the rest
of `phoenix_commons.widgets`.

---

## Package-data handling

The `lucide/` directory is a real Python sub-package (`__init__.py`
present) so:

1. `pyproject.toml` declares `phoenix_commons.icons.lucide = ["*.svg"]`
   under `[tool.setuptools.package-data]`. Wheels include the SVGs.
2. `importlib.resources.files("phoenix_commons.icons.lucide")` resolves
   in both editable installs and frozen builds.
3. PyInstaller's `--collect-data phoenix_commons` picks the SVGs up
   automatically when consuming apps are built — no per-app
   `--add-data` flag required.

---

## Migration philosophy (this is a FUTURE phase, not now)

Phase 2.2 lands the infrastructure only. No production tool is
modified by this phase. When the explicit retrofit phase is approved:

1. **Emoji icons** (`"⚙️"`, `"🔍"`, `"💾"`, `"🗑️"`, `"⚠️"`) — replaced
   with `icon(...)` calls. Visually consistent across OS / font
   stacks. Lays Job Tracker / Phoenix CAD / Phoenix Checkout
   side-by-side.
2. **App-local SVGs that match the commons set** (e.g. PCC's vendored
   gear icon, Phoenix CAD's local settings glyph) — deleted, replaced
   with `icon("settings")` etc.
3. **App-local SVGs that DON'T match the commons set** — stay app-
   local, loaded via `phoenix_commons.paths.resource_path`. If two
   apps independently need the same one, it gets promoted to commons
   via a PR adding the SVG + `ICON_NAMES` entry.

App-specific logos (`LLT_Transparent.png`, etc.) NEVER move to
commons — they're per-tool branding. The commons set is generic UI
chrome only.

---

## See also

- `PLATFORM_CONTRACT.md` § Icons — ownership rules
- `PLATFORM_CONTRACT.md` § Generated artifacts policy — applies to
  future icon-catalogue generation
- `DESIGN_SYSTEM.md` § Iconography — high-level brand stance
- Phase 2.2 stabilization report — implementation details, risks,
  verification output
