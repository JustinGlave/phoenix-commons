# ICON_POLICY.md

> Governance for the Phoenix icon system. Naming rules, commons-vs-
> app boundaries, promotion criteria, authoring rules, and the
> extension workflow that lets the icon set grow without churning
> the public API.
>
> Implementation details (the recolour pipeline, cache mechanics,
> rasterisation strategy) live in the package README at
> `src/phoenix_commons/icons/README.md`. This document covers
> *policy* — the package README covers *how*.

## Scope

This policy applies to every icon used by every Phoenix tool —
whether the icon ships in `phoenix_commons.icons` or stays
app-local. The naming, sizing, and recolour rules are the same in
both cases; only the *ownership* differs.

The Phoenix UI Platform is built on **[Lucide](https://lucide.dev/)
icons exclusively**. The set is MIT-licensed, stroke-based, visually
coherent, and actively maintained. Any new commons icon must come
from Lucide. App-local icons should also be Lucide unless there's a
specific reason not to (logo, third-party brand mark, etc.).

## Semantic naming rules

1. **Names describe meaning, not shape.** `save` (not `floppy-disk`).
   `warning` (not `triangle-bang`). `x` (not `cross`).
2. **Lowercase, hyphen-free where possible.** Single-word names are
   the default (`check`, `info`, `refresh`). Hyphenated names are
   acceptable when one word can't carry the meaning
   (`arrow-right`, `chevron-up`). The hyphen separates two
   semantically meaningful tokens; it's not decorative.
3. **Map to a real Lucide icon.** Don't invent shapes. Find the
   closest Lucide visual and rename it to the Phoenix semantic
   version if needed. Document the mapping in the PR description.
4. **The name appears in app source for years.** Adding it means
   committing to keeping it stable. Bikeshedding is encouraged
   *before* the PR lands, not after.
5. **Closed set.** Names are declared in
   `phoenix_commons.icons.registry.ICON_NAMES` (a `frozenset`). The
   loader raises `IconNotFoundError` for anything outside the set,
   so typos surface at call time instead of as silent blanks.

### Reserved name conventions

| Pattern | Meaning |
|---------|---------|
| `arrow-{direction}` | Cardinal arrows: `arrow-up`, `arrow-down`, `arrow-left`, `arrow-right` |
| `chevron-{direction}` | Compact directional indicators (collapse / expand) |
| Status verbs (`check`, `x`, `info`, `warning`, `error`) | Match the status colour names in `SEMANTIC_COLORS` where it makes sense |
| Single-word common actions (`save`, `delete`, `refresh`, `search`) | Default form |

Avoid:

| Anti-pattern | Why |
|--------------|-----|
| `floppy-disk` for save, `gear-2` for settings | Visual not semantic. The icon's shape may evolve; the meaning won't. |
| `cad-export-special` | App-specific by name. If it belongs in commons, name it semantically (`export-cad`). If it's truly one-of-a-kind, keep it app-local. |
| Two icons with overlapping meanings (`x` AND `close` AND `dismiss`) | Pick one. Aliases dilute the closed-set discipline. |

## Commons vs app-local

An icon belongs in **`phoenix_commons.icons`** when:

1. **Generic UI chrome.** Buttons, menu items, toolbar actions —
   things every Phoenix tool's UI plausibly uses (save, settings,
   search, plus, trash, warning, info, check, x, refresh).
2. **Used by 2+ tools** independently (the promotion rule below).
3. **Stable shape.** The Lucide source for the icon is unlikely to
   change radically across Lucide versions. Re-vendoring a wildly
   different shape would be a user-visible regression.

An icon stays **app-local** when:

1. **Per-app branding.** `LLT_Transparent.png`, `phoenix-cad-logo.svg`,
   the Command Center wordmark. These NEVER move to commons —
   they're tool identity, not shared chrome.
2. **Tool-specific business meaning.** Phoenix CAD's BricsCAD-specific
   glyphs ("layer-property-toggle", "viewport-anchor"). The shape only
   makes sense within that tool's mental model.
3. **One tool, one use.** Until a second tool independently asks for
   the same icon, an app-local SVG is the right call. Premature
   commons promotion is a slow form of bloat.

Logos / wordmarks / brand marks **always** stay app-local. There is
no path for them into commons. The icons package is for *generic UI
chrome only*.

## Promotion rules — when an app icon becomes a commons icon

Promotion is triggered by **independent demand**, not pre-emptive
generosity.

Promotion checklist:

1. **Two or more apps** independently want the same icon. "Same"
   means same semantic meaning, not just visually similar.
2. The current app-local copies are **Lucide-derived** (or can be
   replaced with the Lucide equivalent). Bespoke shapes do not
   qualify — they go to commons only if they survive a redraw to
   match Lucide's stroke style.
3. There's a sensible **semantic name** that follows the naming
   rules above. If naming is contested, the PR-review thread is
   where it gets resolved.
4. The promotion PR:
   - Drops the canonical SVG into `src/phoenix_commons/icons/lucide/`.
   - Adds the name to `ICON_NAMES` (alphabetised).
   - Updates the test file (the `test_every_registered_icon_loads`
     parametrisation picks the new name up automatically; just
     verify it green's in CI).
   - Adds a row to the commons CHANGELOG.
   - Updates `ICON_POLICY.md` and `src/phoenix_commons/icons/README.md`
     if any policy text references a specific count.

Demotion (commons → app-local) is not a thing. Once an icon is in
commons, removing it is a MAJOR-version break.

## Recolour expectations

The recolour pipeline is documented in detail in the package README.
**Policy:**

1. **Every commons icon ships with `currentColor` strokes/fills.**
   The test `test_package_data_includes_all_starter_svgs` enforces
   this at CI time — a vendored pre-coloured SVG fails the build.
2. **App-local icons SHOULD also use `currentColor`.** If they don't,
   `phoenix_commons.icons.icon()` can't recolour them — apps would
   need to either run the SVG through `sed` or use Qt's painter
   compositing path.
3. **Colour is passed at call time**, never baked into the asset.
   The same SVG renders red on a destructive button and white on
   the default chrome.
4. **The semantic palette is the public colour vocabulary.**
   `color="primary"`, `color="warning"`, `color="muted"` —
   not `color="#dc2626"` in app code. The hex form exists as an
   escape hatch for non-palette situations (e.g. matching an
   external brand colour); 95% of usages should be semantic.

## Sizing conventions

| Pixel size | Typical use |
|------------|--------------|
| 14 / 16    | Inline text decorations, tiny tag chips |
| 18 / 20    | Toolbar buttons, table-row action buttons |
| **24** (default) | Primary buttons, sidebar items, the standard form |
| 28 / 32    | Dialog headers, empty-state illustrations |
| 48+        | Onboarding splash, large feature callouts |

Always one of the sizes above. **No arbitrary sizes** — pick the
closest standard rung and let Qt downsample if a widget needs
something in between.

## Cache assumptions

1. The cache lives in-process and is keyed `(name, raw_color, size)`.
2. Repeated calls with identical arguments return the **same `QIcon`
   instance**.
3. The cache survives across QObject lifetimes (one QApplication for
   the whole process — Qt's normal model).
4. **Tests** call `phoenix_commons.icons.clear_cache()` before / after
   each case via an autouse fixture (see `tests/test_icons.py`). App
   code should never need to call it manually.
5. There is no automatic eviction. The closed `ICON_NAMES` set and
   the closed semantic palette bound total cache size to a small
   constant.

## SVG authoring expectations

For new commons icons:

1. **Source from Lucide.** Use [lucide.dev](https://lucide.dev/) and
   copy the raw SVG markup — don't redraw.
2. **Preserve the Lucide attribute set.** `viewBox="0 0 24 24"`,
   `fill="none"`, `stroke="currentColor"`, `stroke-width="2"`,
   `stroke-linecap="round"`, `stroke-linejoin="round"`. The loader
   relies on `currentColor` for recolouring; the test suite
   verifies the token is present.
3. **No `style=""` attributes.** Inline styles bypass the
   `currentColor` substitution path. Use raw `stroke=` and `fill=`.
4. **Single-line minified SVG OK.** The vendored set is single-line;
   diffs stay reviewable because each icon is ~250 B.
5. **One SVG per file.** Filename matches the semantic name:
   `<name>.svg`. No subdirectories under `lucide/`.

For app-local icons:

The same rules apply *unless* the icon is a logo / brand mark — those
are exempt from `currentColor` (they're typically multi-colour brand
assets). App-local logos load via `phoenix_commons.paths.resource_path`,
not through the `icon()` loader.

## "No pre-coloured SVGs" rule

**Commons icons must not ship with baked-in colours.** Specifically:

- ❌ `<svg stroke="#dc2626">` — hardcoded hex
- ❌ `<svg stroke="rgb(220, 38, 38)">` — hardcoded rgb
- ❌ `<svg style="stroke: red">` — inline style
- ✅ `<svg stroke="currentColor">` — only acceptable form

Violations are caught by the test suite:
`test_package_data_includes_all_starter_svgs` asserts every shipped
SVG contains `currentColor`. A pre-coloured asset breaks CI.

The rationale: pre-coloured icons can't be recoloured. The whole
point of the recolour pipeline is that one asset renders correctly
on every Phoenix surface (dark navy bg, light dialog, status banner,
destructive button), driven by `color="..."` at call time.

## Extension workflow — how to add a new icon

1. **Survey existing usage.** Check whether the action already has a
   semantic name in the registry. Re-use over invention.
2. **Confirm two-app demand** (commons) or scope-bound use (app-local).
3. **Pick the Lucide source icon.** Note the Lucide name in the PR
   description.
4. **Drop the SVG** in either:
   - `src/phoenix_commons/icons/lucide/<name>.svg` (commons), OR
   - `<your-app>/assets/icons/<name>.svg` (app-local)
5. **For commons:** add the name to `ICON_NAMES` (alphabetised) in
   `src/phoenix_commons/icons/registry.py`.
6. **For commons:** verify the test parametrisation picks up the new
   row — run `pytest -q tests/test_icons.py -k all_starter`.
7. **For commons:** update `CHANGELOG.md` with a one-line entry under
   `[Unreleased]`. Bump `_version.py` to the next MINOR before
   release.
8. **PR review** checks naming, Lucide source, currentColor presence,
   alphabetisation, and the test green.

## See also

- `src/phoenix_commons/icons/README.md` — implementation README
  (loader internals, cache mechanics, sizing helpers)
- `PLATFORM_CONTRACT.md` § Icons — ownership map
- `API_BOUNDARIES.md` — what's public on the icons module
- `COMPONENT_CONTRACT.md` — how widgets consume icons
- [lucide.dev](https://lucide.dev/) — the upstream icon source
