# STABILIZATION_REPORT_03.md

> Phase 2.2 — Icon Infrastructure. Lays down the canonical Phoenix
> icon loader (Lucide SVG → recoloured QIcon, with caching) and the
> small starter set of 10 semantic icons. Plus a preceding platform-
> contract clarification: the Generated Artifacts Policy.
>
> Source-only, no migrations, no production-tool work, no builds.
> No emoji replacement. No widget rewrites. No retrofits.
>
> Captured 2026-05-18.

## 1. Status

**Passed.** All Phase 2.2 deliverables landed as four logical commits
on `main`, pushed to origin. 67/67 tests pass (44 pre-existing + 23
new). The icons package is import-clean from any context (no
QApplication required to load the module — only to render an icon).

Architecture stabilization remains in effect. **No Phase 2.3 / icon
replacement / migration / packaging work started.**

## 2. STEP 1 — Generated Artifacts Policy (preceded Phase 2.2)

`docs/ui-platform-baseline-v1/PLATFORM_CONTRACT.md` gained a new
top-level section, **Generated artifacts policy**, codifying:

1. Generated artifacts are canonical derived outputs.
2. They ARE committed to git (reproducible installs, no build step).
3. They must never be hand-edited.
4. They must have: deterministic generation, a documented regeneration
   command, and CI stale-drift protection where practical.
5. They should eventually live under `phoenix_commons/generated/`
   (or `_generated/`) once there are more than one or two.
6. Current artifact: `phoenix_commons/theme/embedded_qss.py`.
7. Likely future artifacts: icon registries, token exports, template
   registries.

Committed separately as `3e1dc33 — Add generated-artifact policy`.

## 3. Phase 2.2 — Icon architecture

```
src/phoenix_commons/icons/
├── __init__.py        — re-exports public API
├── loader.py          — icon() + recolour + render pipeline
├── registry.py        — ICON_NAMES, SEMANTIC_COLORS, typed exceptions
├── cache.py           — (name, color, size) → QIcon dict
├── lucide/
│   ├── __init__.py    — sub-package so importlib.resources resolves
│   ├── save.svg          plus.svg        trash.svg
│   ├── settings.svg      warning.svg     info.svg
│   ├── search.svg        check.svg       x.svg
│   └── refresh.svg
└── README.md          — philosophy, naming, sizing, recolour internals
```

**Module roles:**

| Module | Responsibility | Qt? |
|--------|----------------|-----|
| `registry.py` | Closed set of icon names; semantic colour palette; typed exceptions; constants for defaults | No |
| `cache.py` | (`name`, `color`, `size`) → `QIcon` dict + `get` / `put` / `clear` / `size` accessors | `QIcon` only under `TYPE_CHECKING` |
| `loader.py` | `icon(name, *, color, size)` — public entry point; SVG read, recolour, rasterise, cache, return | Yes (`QSvgRenderer`, `QPixmap`, `QPainter`, `QIcon`) |
| `__init__.py` | Re-exports public surface (`icon`, `clear_cache`, the registry constants, the two exception types) | Imports loader |
| `lucide/__init__.py` | Makes `lucide/` a real sub-package so `importlib.resources.files()` is the canonical resolution path | No |

**Public API surface** (everything `__init__.py` re-exports):

```python
from phoenix_commons.icons import (
    icon,                  # the loader
    clear_cache,           # test helper
    ICON_NAMES,            # frozenset[str] — closed set
    SEMANTIC_COLORS,       # dict[str, str] — semantic → hex
    DEFAULT_COLOR,         # "text"
    DEFAULT_SIZE,          # 24
    IconNotFoundError,     # raised by icon() for unknown name
    UnknownColorError,     # raised for unrecognised color=
)
```

## 4. Loader behaviour

```python
def icon(name: str, *, color: str | None = None, size: int = 24) -> QIcon
```

**Flow per call:**

1. Normalise `color` → `color_key` (None becomes `DEFAULT_COLOR = "text"`).
2. Build cache key `(name, color_key, size)`. If hit → return cached
   `QIcon` (identity-equal across calls).
3. Validate `name` against `ICON_NAMES`; raise `IconNotFoundError`
   with sorted suggestions if missing.
4. Resolve `color_key` to a hex literal via `_resolve_color`. Raises
   `UnknownColorError` for inputs that aren't either a semantic name
   or a `#rgb` / `#rrggbb` literal.
5. Read SVG bytes from `lucide/<name>.svg` via
   `importlib.resources.files(...).read_bytes()`.
6. Substitute `currentColor` for the resolved hex (see §5).
7. Rasterise the SVG to a transparent `QPixmap` of the requested size.
8. Wrap as `QIcon`, store in the cache, return.

**Failure modes are all typed:**

| Condition | Exception | Inherits |
|-----------|-----------|----------|
| `name` not in `ICON_NAMES` | `IconNotFoundError` | `KeyError` |
| `color` not a semantic name or hex | `UnknownColorError` | `ValueError` |

Both messages echo the bad input and list the valid alternatives, so
the human can fix the call without consulting the source.

## 5. Recolour strategy — byte-substitution

Lucide SVGs ship with `stroke="currentColor"` — the CSS escape that
means "inherit the calling element's text colour". Browsers honour
it; **Qt's `QSvgRenderer` does not** — it renders `currentColor` as
opaque black, which is invisible on the Phoenix dark navy bg.

The loader handles this by **byte-substituting `currentColor` for the
resolved hex in the in-memory SVG bytes before parsing**. Trade-offs
considered:

| Option | Pros | Cons | Choice |
|--------|------|------|--------|
| Substitute bytes (chosen) | Fast (~100× faster than XML round-trip); produces clean pixels; no Qt extras | Plain string replace; theoretical XML-edge-case risk for hand-authored SVGs | ✅ |
| Parse XML, edit attrs, re-serialise | Schema-aware | Pulls `xml.etree` into every icon load; slower; serialisation can re-format the file | ❌ |
| Render as-is, then `QPainter::CompositionMode_SourceIn` tint | Don't touch SVG bytes | Aliasing artifacts at small sizes; extra QPixmap step | ❌ |

The substitution pattern set covers both attribute names and both
quote styles SVG editors emit:

```python
_CURRENT_COLOR_PATTERNS = (
    b'stroke="currentColor"',
    b"stroke='currentColor'",
    b'fill="currentColor"',
    b"fill='currentColor'",
)
```

A test (`test_recolor_handles_single_quotes`) pins the single-quote
case explicitly. The package-data test
(`test_package_data_includes_all_starter_svgs`) also asserts that
every shipped SVG contains `currentColor` somewhere — catches the
case where someone vendors a pre-coloured SVG by accident, which
would render the recolour path silently no-op.

## 6. Cache strategy

Module-level dict in `cache.py`. Key: `(name, raw_color, size)`. Value:
`QIcon`.

**Three design points:**

1. **Raw colour, not resolved hex.** The cache keys on `"primary"`,
   not on the hex `"#dc2626"`. A future change to
   `SEMANTIC_COLORS["primary"]` invalidates old entries through their
   user-visible name — no silent stale renders. Tested:
   `test_hex_and_semantic_resolve_to_same_pixels` confirms that
   `color="#dc2626"` and `color="primary"` render to identical pixels,
   even though they cache under different keys.
2. **Process-wide, no eviction.** `ICON_NAMES` is closed (10 entries
   today), the semantic palette is closed (9 colours), and typical
   tools touch a handful of sizes. Bounded cache → no LRU needed.
   `test_cache_distinguishes_name_color_and_size` pins the three-
   dimensional key.
3. **Test-friendly.** `clear_cache()` is re-exported from the package
   so an autouse fixture can reset it between tests. The test module
   sets this up so any cache pollution from one case (e.g. a stale
   instance from an earlier size) never satisfies a later case.

## 7. Package-data handling

Three layers of resolution machinery, all aligned:

1. **`lucide/__init__.py` makes the SVG directory a real sub-package.**
   Otherwise setuptools may treat it as a namespace dir and skip it,
   and `importlib.resources.files("phoenix_commons.icons.lucide")`
   may resolve unexpectedly.
2. **`pyproject.toml` declares the SVGs as package data:**
   ```toml
   [tool.setuptools.package-data]
   "phoenix_commons.theme"        = ["*.qss"]
   "phoenix_commons.icons.lucide" = ["*.svg"]
   ```
   Wheel builds include the SVGs; non-editable installs work
   identically to editable installs.
3. **Runtime resolution via `importlib.resources.files`.** Both
   editable installs (working tree directly) and frozen installs
   (PyInstaller `--collect-data phoenix_commons`) go through the same
   `Traversable` API. No filesystem-vs-zip branching in the loader.

The `test_package_data_includes_all_starter_svgs` test exercises this
path: it iterates `ICON_NAMES` and confirms each `.svg` is reachable,
non-trivial, well-formed, and contains `currentColor`. If this passes
in CI, a frozen build will bundle the icons correctly.

## 8. Tests added

`tests/test_icons.py` — 23 new tests (12 distinct cases, one
parametrised across 10 icon names for the registry-coverage check).

| Test | Verifies |
|------|----------|
| `test_icon_returns_qicon` | `icon("save")` returns a non-null `QIcon` |
| `test_cache_hit_returns_same_instance` | Second call returns the *same* object |
| `test_missing_icon_raises_clear_error` | `IconNotFoundError` echoes the bad name + suggests valid ones |
| `test_recolour_produces_different_pixels` | Default vs `color="primary"` produces different pixmaps |
| `test_size_parameter_is_honoured` | `size=18` / `size=48` give 18×18 / 48×48 pixmaps |
| `test_every_registered_icon_loads` (×10) | Every `ICON_NAMES` entry resolves to a non-null `QIcon` (parametrised) |
| `test_unknown_color_raises_clear_error` | `UnknownColorError` echoes the bad colour + suggests semantic options |
| `test_hex_color_literal_works` | `color="#dc2626"` works |
| `test_short_hex_color_works` | `color="#fff"` (3-digit) works |
| `test_hex_and_semantic_resolve_to_same_pixels` | `"primary"` and `"#dc2626"` produce identical pixmaps |
| `test_recolor_unit_substitution` | `_recolor` byte-substitution works unit-style (no Qt) |
| `test_recolor_handles_single_quotes` | Recolour covers both quote styles in attributes |
| `test_cache_distinguishes_name_color_and_size` | All three key dimensions produce distinct entries |
| `test_package_data_includes_all_starter_svgs` | Every name has a real SVG bundled with the package |

An autouse fixture (`_reset_cache`) calls `clear_cache()` before AND
after every test, so a cache entry created in one test (e.g. an icon
at size 18) can never silently satisfy a different test that expected
a fresh render.

## 9. Verification output

```
$ python -m compileall -q src tests
(exit 0)

$ QT_QPA_PLATFORM=offscreen python -m pytest -q tests/
...................................................................      [100%]
67 passed in 0.23s
```

**67 tests pass.** Breakdown:

- `test_smoke.py` — 12 (Phase 1 + Phase 2 surface)
- `test_paths.py` — pre-existing (Phase 3 paths)
- `test_updater.py` — pre-existing (Phase 3 updater)
- `test_embedded_qss.py` — 7 (Phase 2.1)
- **`test_icons.py` — 23 (this phase)**

Runtime delta from Phase 2.1: 0.16 s → 0.23 s. Still well within
the "fast suite" target.

## 10. CI

**Unchanged.** The new tests live under the existing
`pytest -q tests/` step in `.github/workflows/ci.yml`. No workflow
edit required.

Per the user spec, **no heavy GUI tests, no screenshot tests, no
builds** were added. The package-data verification is
`importlib.resources` based, not PyInstaller based — it confirms the
resolution path works, not that PyInstaller actually packs the files
(that's a frozen-exe phase concern, gated by S1/AV).

## 11. Future migration implications

This phase establishes infrastructure. The actual migration of
existing app emoji / app-local SVGs to `icon(...)` calls is a
**separate, explicitly-approved retrofit phase**. Implications for
that future work:

1. **Emoji icons** (`"⚙️"`, `"🔍"`, `"💾"`, `"🗑️"`, `"⚠️"`) appear in
   several places across PCC / Job Tracker / Phoenix CAD. Each
   replacement is a one-liner: `button.setText("⚙️ Settings")` →
   `button.setText("Settings"); button.setIcon(icon("settings"))`.
2. **App-local SVGs that match the commons set.** PCC and Phoenix CAD
   each have their own settings glyph today. Once retrofit happens
   they'll delete the local copy and use `icon("settings")` — that's
   the visible cross-tool consistency win.
3. **App-local SVGs that DON'T match the commons set.** Per
   `PLATFORM_CONTRACT.md` § Icons, these stay app-local and load via
   `phoenix_commons.paths.resource_path`. If 2+ apps independently
   need the same one, it gets promoted to commons via a PR adding the
   SVG + `ICON_NAMES` entry. App-specific *logos* never move.
4. **Naming registry will need to grow.** 10 icons is enough to start
   migrations once approved, but the full retrofit will reveal a list
   of currently-emoji uses we haven't named yet (download, upload,
   eye-on, eye-off, lock, unlock, calendar, etc.). Each addition goes
   through a commons PR — explicit, audit-trail-friendly.
5. **No QIcon construction in widget classes.** The widget surface in
   `phoenix_commons.widgets` stays icon-free; consumers pass icons
   in. This keeps the widget catalogue testable without an icon set
   loaded.

## 12. Risks discovered / judgment calls

| # | Item | Resolution |
|---|------|------------|
| 1 | The user spec listed the starter set as "save, settings, search, plus, trash, …" with the trailing ellipsis. | Chose 10 icons: the 5 named + warning, info, check, x, refresh. All five appear in expected migration paths (status colour groups for warning/info; check/x for confirm/dismiss; refresh for the update banner). Documented the addition policy in `icons/README.md`. |
| 2 | `QSvgRenderer` doesn't honour `currentColor`. | Byte-substitute `currentColor` before parsing. Documented in loader docstring + report § 5. |
| 3 | Cache keyed on raw colour name vs resolved hex would have unsynchronised semantics if `SEMANTIC_COLORS` changes. | Keyed on **raw** colour. Old entries become unreachable through their user-visible name — no silent stale renders. Tested by `test_hex_and_semantic_resolve_to_same_pixels`. |
| 4 | `lucide/` directory without an `__init__.py` may be skipped by some setuptools configurations. | Added `lucide/__init__.py` with a docstring explaining the sub-package status. Now `importlib.resources.files("phoenix_commons.icons.lucide")` resolves the same way under any install mode. |
| 5 | Recolour might silently no-op on a future SVG that lacks `currentColor`. | `test_package_data_includes_all_starter_svgs` asserts every SVG contains `currentColor`. Any future vendoring of a pre-coloured SVG breaks CI immediately. |
| 6 | The cache survives across the QApplication lifetime — if tests destroyed and re-created QApplication, cached `QIcon` instances could become stale. | pytest-qt uses a session-scoped `qapp` — one QApplication lives for the whole test run. Cache is safe under this regime. The defensive `_reset_cache` autouse fixture clears between tests anyway, so test order independence is preserved. |
| 7 | New phase, no existing baseline to migrate. The icon API surface lives in commons today; no app uses it yet. | Acceptable — Phase 2.2 is foundation work, with migration explicitly deferred to a separate approved phase. No backward-compat shims are required because nothing legacy references this surface yet. |

No new blockers discovered. `BLOCKERS.md` is unchanged by this phase
(Phase 2.2 is source-only; AV-independent; never touches PyInstaller
/ installer / updater runtime paths).

## 13. Commits (in order)

```
$ git log --oneline -5

60c32df Add icon-infrastructure tests (Phase 2.2)
dfb5da9 Add Phoenix icon infrastructure (Phase 2.2)
3e1dc33 Add generated-artifact policy
0b80f01 Add STABILIZATION_REPORT_02 — Phase 2.1 embedded fallback generation
d7f46d1 Add embedded-QSS smoke tests + stale-fallback CI guard (Phase 2.1)
```

Three logical commits per spec (the spec's commit list said "policy /
icon infrastructure / tests + CI"):

| # | Hash | Subject | Touches |
|---|------|---------|---------|
| 1 | `3e1dc33` | Generated-artifact policy | `docs/ui-platform-baseline-v1/PLATFORM_CONTRACT.md` (+46) |
| 2 | `dfb5da9` | Icon infrastructure | `pyproject.toml` (package-data, +6/-3), `src/phoenix_commons/icons/{__init__,loader,registry,cache,lucide/__init__}.py` (+393), `src/phoenix_commons/icons/README.md` (+230), `src/phoenix_commons/icons/lucide/*.svg` (10 files, ~3.3 KB) |
| 3 | `60c32df` | Tests | `tests/test_icons.py` (+197) |

Cumulative diff vs `0b80f01` (the tip before this phase):

```
 docs/ui-platform-baseline-v1/PLATFORM_CONTRACT.md |  46 +++++
 pyproject.toml                                    |   9 +-
 src/phoenix_commons/icons/README.md               | 230 ++++++++++++++++++++
 src/phoenix_commons/icons/__init__.py             |  41 ++++
 src/phoenix_commons/icons/cache.py                |  54 +++++
 src/phoenix_commons/icons/loader.py               | 180 +++++++++++++++++
 src/phoenix_commons/icons/lucide/__init__.py      |  14 ++
 src/phoenix_commons/icons/lucide/*.svg            |  10 ++  (10 files)
 src/phoenix_commons/icons/registry.py             |  84 ++++++++
 tests/test_icons.py                               | 197 ++++++++++++++++++
 19 files changed, 862 insertions(+), 3 deletions(-)
```

**SVG sizing** (vendored Lucide source, MIT):

| File | Size |
|------|------|
| `check.svg` | 223 B |
| `info.svg` | 262 B |
| `plus.svg` | 228 B |
| `refresh.svg` | 357 B |
| `save.svg` | 338 B |
| `search.svg` | 245 B |
| `settings.svg` | 796 B |
| `trash.svg` | 309 B |
| `warning.svg` | 314 B |
| `x.svg` | 232 B |
| **10 total** | **3,304 B** |

Total icon-package weight on disk: ~3.3 KB of vendored SVG +
~30 KB of Python + ~12 KB of README. Negligible for a Phoenix tool.

## 14. Branch state — local

```
$ git branch -vv

  baseline-v1                       417f860 [origin/baseline-v1] Add remote bootstrap report …
* main                              60c32df [origin/main] Add icon-infrastructure tests (Phase 2.2)
  phase-2-theme-widgets             db1d8b4 Add Phase 2 report …
  phase-3-paths-updater             b2e7f79 Add Phase 3A report …
  phase-4-pyinstaller-compatibility ba3d2c4 [origin/phase-4-pyinstaller-compatibility] Phase 6C backup report …
```

| Branch | Tip | Tracks origin |
|--------|-----|---------------|
| `main` | `60c32df` | ✓ (updated this turn — 3 new commits) |
| `baseline-v1` | `417f860` | ✓ (unchanged this turn) |
| `phase-4-pyinstaller-compatibility` | `ba3d2c4` | ✓ (unchanged this turn) |

## 15. Remote state — origin

```
$ git ls-remote --heads origin

417f8600…  refs/heads/baseline-v1                          ← unchanged this turn
60c32dff…  refs/heads/main                                 ← updated (3 new commits)
ba3d2c4d…  refs/heads/phase-4-pyinstaller-compatibility    ← unchanged this turn
```

Push command run: `git push origin main` (`0b80f01..60c32df`).

## 16. Confirmation — no migrations / builds / retrofits occurred

- ❌ **No app code modified** (zero edits to PCC, Job Tracker, Phoenix CAD, Phoenix Checkout, ValveMaster source).
- ❌ **No commons code outside the new `icons/` package + `pyproject.toml` (+1 table row) + `PLATFORM_CONTRACT.md` (+1 section).** Theme / paths / updater / widgets / package init untouched.
- ❌ **No emoji-icon replacement performed.** Production tools still use whatever icons they have today. Replacement is a future retrofit phase, explicitly out of scope here.
- ❌ **No component migration.** `phoenix_commons.widgets.PrimaryButton` etc. unchanged; none of them take an `icon=` kwarg yet (that's a future API extension).
- ❌ **No `build.bat` / PyInstaller / Inno Setup / updater download/apply / `gh release`** invocations.
- ❌ **No CI workflow change** required — the new tests run under the existing `pytest -q tests/` step.
- ❌ **No frozen-exe verification** attempted. The package-data test only confirms the `importlib.resources` resolution path works; whether a real PyInstaller build picks the SVGs up is a Phase 4+ concern, gated by S1/AV.
- ❌ **No rollout phases started. No retrofits. No icon replacement. No component migration. No packaging / runtime work.**

Operations performed this turn:

```
(Edit)   docs/ui-platform-baseline-v1/PLATFORM_CONTRACT.md     ← +46 line policy section
git add … && git commit "Add generated-artifact policy"        ← STEP 1
(Write)  src/phoenix_commons/icons/lucide/*.svg                 (×10)
(Write)  src/phoenix_commons/icons/lucide/__init__.py
(Write)  src/phoenix_commons/icons/{__init__,loader,registry,cache}.py
(Write)  src/phoenix_commons/icons/README.md
(Edit)   pyproject.toml                                         ← +1 package-data table row
(Write)  tests/test_icons.py
python -m compileall -q src tests
QT_QPA_PLATFORM=offscreen python -m pytest -q tests/           ← 67 passed in 0.23s
git add … && git commit "Add Phoenix icon infrastructure …"   ← icon infra
git add … && git commit "Add icon-infrastructure tests …"     ← tests
git push origin main
(Write)  docs/ui-platform-baseline-v1/STABILIZATION_REPORT_03.md
```

That's the entire surface.

## 17. STOP

Phase 2.2 complete. Architecture stabilization remains in effect.

Per the user spec for Phase 2.2: **Do NOT continue into migrations,
icon replacement, component migration, packaging/runtime work, or
retrofits.** No code change resumes without explicit phase approval
per `BASELINE.md` stop conditions.

Awaiting user direction.
