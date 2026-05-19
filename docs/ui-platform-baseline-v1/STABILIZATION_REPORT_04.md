# STABILIZATION_REPORT_04.md

> Phase 2.5 — Platform Stabilization / Contracts. Freezes the
> public API surface, formalises private boundaries, lands the
> canonical token module, codifies icon + component contracts,
> and produces the Phase 2.6 verification matrix.
>
> Source-only. No migrations, no production-tool work, no builds.
> No retrofits. No icon replacement. No emoji removal.
>
> Captured 2026-05-19.

## 1. Status

**Passed.** All Phase 2.5 deliverables landed as three logical
commits on `main`, pushed to origin (`2f21ae5..e314a0d`). 67/67
tests pass. Five new governance documents under
`docs/ui-platform-baseline-v1/`. One new source module
(`theme/tokens.py`) with no breaking imports — the icon registry
re-exports from it transparently.

Architecture stabilization remains in effect. **No packaging
verification, migrations, retrofits, frozen-exe work, or icon
replacement started.**

## 2. API-boundary decisions

### Public-vs-private signal hierarchy

| Signal | Meaning |
|--------|---------|
| Re-exported from a package `__init__.py` AND listed in `__all__` | **Stable public API.** Will not break across MINOR versions. |
| Defined in a submodule with `__all__` but not re-exported from the package | **Conditionally public.** Stable across PATCH; may move during MINOR with a shim. |
| Underscore prefix on a name (`_recolor`, `_HEX_RE`) | **Private.** Implementation detail. |
| Underscore prefix on a module (`_cache`, `_embedded_qss`, `_version`) | **Private module.** Do not import directly. |

### Concrete changes

1. **`__all__` everywhere.** Added explicit `__all__` lists to the
   13 modules that lacked one:
   - `_version`, `paths`
   - `theme/apply`, `theme/generate_embedded_qss`, `theme/embedded_qss`
     (via generator HEADER + regeneration)
   - `widgets/{buttons, typography, panel, table, no_scroll, helpers, update_banner}`
   - `updater/{client, installer, qt}`

   The package `__init__.py` files already declared `__all__` —
   this fills in the submodules. Star imports now resolve the
   intended public set.

2. **Rename `icons/cache.py` → `icons/_cache.py`.** The cache module
   is truly internal — no consumer should ever import it. The
   leading underscore makes that explicit at the module level. The
   only consumer-facing surface is `clear_cache`, re-exported from
   the package `__init__`. Loader + package `__init__` import paths
   updated.

3. **Regenerate `embedded_qss.py`** with the new HEADER that includes
   `__all__ = ["EMBEDDED_QSS"]`. Deterministic generator →
   byte-identical re-render → stale-fallback CI guard still passes.

### Deprecation policy

Codified in `API_BOUNDARIES.md`:

- **MAJOR bump** for removal or signature change of public API.
- **One MINOR version of overlap** for renames (deprecation warning
  on old name; new name live).
- **Underscore module shim** for relocated modules (canonical example:
  `phoenix_commons.theme._embedded_qss`).
- **CHANGELOG entry required** for any removal / rename / move.
- **No silent breaking changes** even for conditionally-public API.

## 3. Public/private exports (summary)

Listed in full in `API_BOUNDARIES.md`. Headline:

| Package | Public exports |
|---------|----------------|
| `phoenix_commons` | `__version__` |
| `phoenix_commons.theme` | `apply_dark_theme` |
| `phoenix_commons.theme.tokens` (new this phase) | `BG`, `SURFACE`, `SURFACE_ALT`, `PRIMARY`, `SECONDARY`, `ACCENT`, `TEXT`, `MUTED`, `SUCCESS`, `WARNING`, `ERROR`, `INFO`, `SEMANTIC_COLORS`, `C` |
| `phoenix_commons.icons` | `icon`, `clear_cache`, `ICON_NAMES`, `SEMANTIC_COLORS`, `DEFAULT_COLOR`, `DEFAULT_SIZE`, `IconNotFoundError`, `UnknownColorError` |
| `phoenix_commons.widgets` | `PrimaryButton`, `SecondaryButton`, `TertiaryButton`, `PageTitle`, `PageSubtitle`, `SectionTitle`, `HintLabel`, `Panel`, `PhoenixTable`, `UpdateBanner`, `button_row` |
| `phoenix_commons.widgets.no_scroll` | `NoScrollComboBox`, `NoScrollSpinBox`, `NoScrollDoubleSpinBox`, `NoScrollDateEdit` |
| `phoenix_commons.paths` | `is_frozen`, `user_data_dir`, `resource_path` |
| `phoenix_commons.updater` | `UpdateInfo`, `check_for_update`, `download_and_apply` |
| `phoenix_commons.updater.qt` | `UpdateCheckThread` |
| `phoenix_commons.updater.installer` | `UpdatePackageError` |

Private modules: `_version`, `icons/_cache`, `theme/_embedded_qss`.
Private functions: `_recolor`, `_resolve_color`, `_load_svg_bytes`,
`_render_qicon`, `_HEX_RE`, `_CURRENT_COLOR_PATTERNS`,
`_resource_path` (theme/apply), `_parse_version`,
`_validate_update_zip`, `_ps_literal`, `_build_*` (updater).

## 4. Token strategy

### What landed

`src/phoenix_commons/theme/tokens.py` — the canonical home for
named hex values across the platform.

**Module-level constants** (Phoenix System A):

```python
BG          = "#0a0e27"   # base canvas
SURFACE     = "#141829"   # cards / panels / inputs
SURFACE_ALT = "#0f1219"   # alternating rows
PRIMARY     = "#dc2626"   # red — primary / destructive
SECONDARY   = "#1e3a8a"   # deep blue — secondary
ACCENT      = "#3b82f6"   # blue — links / highlights / focus
TEXT        = "#ffffff"   # white text on dark navy
MUTED       = "#94a3b8"   # subdued slate
SUCCESS     = "#22c55e"
WARNING     = "#f59e0b"
ERROR       = "#ef4444"
INFO        = ACCENT      # alias
```

**Dict APIs:**

- `SEMANTIC_COLORS` — `dict[str, str]` mapping `"primary"` →
  `"#dc2626"`, etc. Consumed today by
  `phoenix_commons.icons.registry.SEMANTIC_COLORS` (re-export).
- `C` — alias for `SEMANTIC_COLORS`. **PCC-compatibility hook**:
  PCC's `theme.py` exposes a `C` dict of the same shape, so its
  retrofit to commons becomes a one-line import change (`from theme
  import C` → `from phoenix_commons.theme.tokens import C`) instead
  of a rewrite of every call site.

### Migration impact

- **Zero breaking imports.** `phoenix_commons.icons.SEMANTIC_COLORS`
  resolves to the same dict via the new re-export path. Existing
  tests work unchanged.
- **`apply.py` not refactored this phase.** The 13 `QColor(...)`
  lines in the QPalette setup still use literal RGB tuples. The
  refactor is trivial but adds churn to a recently-migrated file;
  deferred until the apply.py / palette story is otherwise opened.
  Documented as an unverified row in the matrix (1.5).

### Token-addition policy

Codified in the tokens module's docstring:

1. Added through commons PR, not by app developers.
2. Must be semantically named (`ACCENT`, not `BLUE_3B82F6`). Hex
   values change; meanings persist.
3. Two-app independent demand is strong evidence the value belongs
   in commons.
4. Re-use over invention. If a near-match exists under a different
   name, use the existing name rather than create a synonym.

### What's deferred

- **Font tokens** (family, weight ramp) — currently inline in QSS.
- **Spacing tokens** (gutter, padding tiers) — currently inline in
  QSS.
- **Border-radius tokens** — currently inline in QSS.

All three are listed in `PLATFORM_CONTRACT.md` § Theme tokens as
"land in a later phase". Phase 2.5 covers the palette only.

## 5. Icon policy summary

`docs/ui-platform-baseline-v1/ICON_POLICY.md` is the governance-
level companion to `src/phoenix_commons/icons/README.md`. Highlights:

- **Lucide-only.** New commons icons must come from Lucide
  ([lucide.dev](https://lucide.dev/), MIT). App-local icons should
  also be Lucide unless there's a specific brand reason not to be.
- **Semantic names** (`save`, `warning`) — never visual
  (`floppy-disk`, `triangle-bang`).
- **Commons icons must use `currentColor`.** Pre-coloured SVGs are
  forbidden — they break recolouring. Enforced by
  `test_package_data_includes_all_starter_svgs` (asserts every
  shipped SVG contains `b"currentColor"`).
- **Closed set.** `ICON_NAMES` is a `frozenset` — typos raise
  `IconNotFoundError` at call time.
- **Promotion rule.** An app-local icon becomes a commons icon when
  2+ apps independently need it AND it's Lucide-derived AND it has
  a sensible semantic name. Demotion (commons → app-local) is not
  a thing — once an icon is in commons, removal is a MAJOR-version
  break.
- **App-specific logos / wordmarks NEVER move to commons.** They're
  per-tool branding, not shared chrome.
- **Extension workflow** — concrete checklist for adding a new icon:
  survey existing names → confirm scope → pick Lucide source →
  drop SVG → add to `ICON_NAMES` → run parametrised test → update
  CHANGELOG.

## 6. Component contract summary

`docs/ui-platform-baseline-v1/COMPONENT_CONTRACT.md` codifies the
widget-extension rules. Highlights:

- **Core principle: QSS owns visuals, Python owns behaviour and
  layout.** The decision rule for "does this go in commons or in
  the app": if the theme had to be replaced wholesale, would the
  code need to change? Yes → QSS. No → Python.
- **Extend via addendum, not fork.** Subclass, compose, or
  `objectName`+app-local-QSS — never copy-and-modify or
  re-implement-under-a-different-name.
- **Constructor stability.** Commons widgets pin constructor
  signatures. New features arrive as keyword-only args (MINOR).
  Rename / removal / positional change is MAJOR.
- **Reserved `objectName` list.** Commons-owned names
  (`secondaryButton`, `tertiaryButton`, `Panel`, `ProjectTitle`,
  `ProjectSubtitle`, `SectionTitle`, `hint`, `UpdateBanner`,
  `UpdateMsg`, `InstallBtn`) are part of the public API. Apps
  must not re-use them on unrelated widgets.
- **Inline `setStyleSheet("color: ...")` is forbidden in app code.**
  Bypasses tokens + the design system. Use `objectName` + QSS.
- **No method shadowing without a reason.** Overriding event
  handlers to add behaviour: yes. Overriding `paintEvent` to
  redraw the whole widget: write a separate widget instead.

## 7. Generated-artifact placement decision

The Phase 2.2 Generated Artifacts Policy
(`PLATFORM_CONTRACT.md` § Generated artifacts) says:

> Generated artifacts should live under
> `phoenix_commons/generated/` or `phoenix_commons/_generated/`
> **once there are more than one or two**. Until then, individual
> artifacts may sit alongside their consumers.

There is **one generated artifact today**:
`phoenix_commons/theme/embedded_qss.py`. The threshold is not yet
met.

**Decision:** Do not move yet. Reasons:

1. **Threshold not met.** One artifact is below the "more than one
   or two" trigger.
2. **Avoid back-to-back churn.** `embedded_qss.py` and its shim
   (`_embedded_qss.py`) landed in Phase 2.1. Moving them in Phase
   2.5 would require a second deprecation shim and a re-write of
   the test that imports the underscore shim.
3. **Co-location works today.** `embedded_qss` lives next to its
   sole consumer (the theme loader). That's the right placement
   for a single-consumer artifact.

**Trigger conditions for the future move:**

- A second generated artifact lands (icon registry, token export,
  template manifest — any of the candidates in PLATFORM_CONTRACT.md).
- OR a non-theme consumer of `embedded_qss.py` appears
  (very unlikely — the file is theme-loader-specific).

When triggered, the migration is:

```
src/phoenix_commons/theme/embedded_qss.py
    → src/phoenix_commons/_generated/embedded_qss.py
src/phoenix_commons/theme/embedded_qss.py  (new shim — re-exports from _generated)
```

Plus updates to `phoenix_commons/theme/apply.py`'s import. The
existing `theme/_embedded_qss.py` shim's docstring already
references this future path.

**No code changes this phase for Step 5** — the decision is
captured here and the policy in PLATFORM_CONTRACT.md is the
durable record. The verification matrix marks the future move as
`⏳ Deferred` (row 6.5).

## 8. Verification-matrix summary

`docs/ui-platform-baseline-v1/VERIFICATION_MATRIX.md` — 48 rows
across 11 categories. Phase 2.6 input artefact.

| Category | Total | ✅ Verified | ⚠️ Unverified | ⏳ Deferred | 🔴 Blocked |
|----------|-------|------------|---------------|------------|------------|
| Source mode | 10 | 9 | 1 | 0 | 0 |
| Editable install | 4 | 3 | 1 | 0 | 0 |
| Package-data loading | 4 | 4 | 0 | 0 | 0 |
| QSS loading | 4 | 4 | 0 | 0 | 0 |
| Icon loading | 9 | 8 | 1 | 0 | 0 |
| Generated fallback | 5 | 3 | 1 | 1 | 0 |
| CI | 6 | 5 | 0 | 1 | 0 |
| Updater payload contracts | 6 | 5 | 0 | 0 | 1 |
| Submodule usage | 3 | 0 | 0 | 3 | 0 |
| Frozen mode | 5 | 0 | 0 | 0 | 5 |
| Installer runtime | 4 | 0 | 0 | 0 | 4 |
| **Total** | **48** | **30** | **4** | **5** | **9** |

**62.5% of rows verified today.** All 9 blocked rows trace back to
a single root cause: the S1/AV bootloader-quarantine
(`BLOCKERS.md §1`). Resolving that unblocks Phase 4 (PyInstaller
verification), which unblocks all frozen-mode + installer-runtime
rows in one cascade. The 4 unverified rows are low-risk additions
for a future polish phase. The 5 deferred rows are explicit
"later phase" items (`_generated/` migration on threshold,
submodule + vendoring tested by the first consuming tool, optional
PyInstaller-smoke CI job).

## 9. Risks discovered / judgment calls

| # | Item | Resolution |
|---|------|------------|
| 1 | The Phase 2.5 spec referenced "C, STATUS_COLOR, make_qss()" as existing PCC APIs (already noted in Phase 2.1 report). | Provided `C` in `theme/tokens.py` as an alias for `SEMANTIC_COLORS` so PCC's retrofit is a one-line import swap. `STATUS_COLOR` not provided — it's not a current commons consumer, can be added when PCC's retrofit lands. `make_qss()` not relevant — commons exposes `apply_dark_theme` as the canonical entry point. |
| 2 | The cache rename (`cache.py` → `_cache.py`) is a private-API change but technically observable to anyone who imported from the non-underscore path. | Safe: only `loader.py` and the package `__init__.py` import from the cache module; both updated. The module landed in Phase 2.2 (one phase ago) — no external consumer exists. Git tracks the rename explicitly (`rename src/phoenix_commons/icons/{cache.py => _cache.py} (67%)`). |
| 3 | Regenerating `embedded_qss.py` after the generator HEADER change touches the file's bytes. The stale-fallback CI guard could be triggered if regeneration is forgotten. | Regenerated immediately; test pinned and confirmed green. The guard worked as designed — any future HEADER change requires regeneration in the same PR. |
| 4 | `API_BOUNDARIES.md` references `theme.tokens` constants before the tokens module landed (it's in commit 2 of the phase). | Acceptable within a single phase push. Commit 1 ships the doc; commit 2 ships the module; both pushed in the same `git push`. No window where the doc references a missing import path on origin. |
| 5 | The `_generated/` directory exists nowhere yet — neither created nor populated. Some readers may interpret the policy doc as implying the directory exists. | Clarified: PLATFORM_CONTRACT.md § Generated artifacts says "should eventually live under", not "lives under". The verification matrix row 6.5 explicitly marks the migration as deferred. The directory will be created when triggered. |
| 6 | `apply.py` still has 13 hardcoded `QColor(R, G, B)` literals that could use `tokens.BG`, `tokens.SURFACE`, etc. | Not in scope for this phase. Refactor would touch a recently-migrated file (Phase 2.1) for low absolute value. Documented as unverified row 1.5 in the matrix. Trivial to land when the palette is otherwise revisited. |
| 7 | The new `ICON_POLICY.md` overlaps with the existing `src/phoenix_commons/icons/README.md`. | Distinct roles: README is implementation (loader internals, cache mechanics, sizing helpers); ICON_POLICY is governance (naming rules, commons-vs-app boundaries, promotion criteria, the extension workflow). README cross-references the policy doc and vice versa. |
| 8 | `COMPONENT_CONTRACT.md` overlaps with `PLATFORM_CONTRACT.md` § Widgets. | Same approach: PLATFORM_CONTRACT is the ownership map; COMPONENT_CONTRACT is the extension rules. PLATFORM_CONTRACT cross-references COMPONENT_CONTRACT from the Widgets row. |

No new blockers discovered. `BLOCKERS.md` is unchanged. Phase 2.5 is
fully source-only and AV-independent.

## 10. Future migration implications

The contracts landed this phase shape every future retrofit:

1. **Apps that retrofit to commons** must respect the public API as
   defined in `API_BOUNDARIES.md`. Direct imports from underscore
   paths or non-`__all__` symbols are not supported and may break
   between commons versions.
2. **Apps that already have a `C` dict** (PCC, possibly others)
   become drop-in compatible: `from theme import C` →
   `from phoenix_commons.theme.tokens import C`. No call-site
   rewrites.
3. **Apps that use inline `setStyleSheet("color: #...")`** must
   migrate to `objectName` + commons QSS during retrofit (per
   COMPONENT_CONTRACT.md). The hex-literal pattern is forbidden in
   the post-retrofit app code.
4. **Apps that re-implement updater logic** must migrate to
   `phoenix_commons.updater`'s public API. The `expected_internal`
   asymmetry between full-folder (Job Tracker, Phoenix CAD) and
   exe-only (Phoenix Checkout, ValveMaster) is already documented.
5. **Future generated artifacts** (icon registries, token exports)
   automatically gain the stale-fallback CI guard pattern via the
   Generated Artifacts Policy. The pattern from Phase 2.1's
   `test_generator_is_deterministic_and_idempotent` is the
   template.

The verification matrix tracks where each retrofit will need new
test coverage when it lands.

## 11. Commits (in order)

```
$ git log --oneline -4

e314a0d Add VERIFICATION_MATRIX.md (Phase 2.5 step 6)
6f602de Add token module + icon/component contracts (Phase 2.5 steps 2-4)
64389bf Stabilize commons API boundaries (Phase 2.5 step 1)
2f21ae5 Add STABILIZATION_REPORT_03 — Phase 2.2 icon infrastructure
```

Per the user's commit plan (4 logical commits + report):

| # | Hash | Subject | Step |
|---|------|---------|------|
| 1 | `64389bf` | Stabilize commons API boundaries | Step 1 — `__all__` audit + `_cache` rename + `API_BOUNDARIES.md` |
| 2 | `6f602de` | Token module + icon/component contracts | Steps 2 + 3 + 4 — `tokens.py`, `ICON_POLICY.md`, `COMPONENT_CONTRACT.md`, PLATFORM_CONTRACT update |
| 3 | — | (no commit) | Step 5 — generated-artifact placement decision is doc-only, captured in this report |
| 4 | `e314a0d` | VERIFICATION_MATRIX.md | Step 6 |

Cumulative diff vs `2f21ae5` (the tip before this phase):

```
 docs/ui-platform-baseline-v1/API_BOUNDARIES.md     | 232 ++++++++++++++++++++
 docs/ui-platform-baseline-v1/COMPONENT_CONTRACT.md | 214 ++++++++++++++++++
 docs/ui-platform-baseline-v1/ICON_POLICY.md        | 239 +++++++++++++++++++++
 docs/ui-platform-baseline-v1/PLATFORM_CONTRACT.md  |   8 +-
 docs/ui-platform-baseline-v1/VERIFICATION_MATRIX.md | 175 +++++++++++++++
 src/phoenix_commons/_version.py                    |   2 +
 src/phoenix_commons/icons/__init__.py              |   2 +-
 src/phoenix_commons/icons/{cache.py => _cache.py}  |  19 +-
 src/phoenix_commons/icons/loader.py                |   2 +-
 src/phoenix_commons/icons/registry.py              |  33 ++-
 src/phoenix_commons/paths.py                       |   2 +
 src/phoenix_commons/theme/apply.py                 |   2 +
 src/phoenix_commons/theme/embedded_qss.py          |   2 +
 src/phoenix_commons/theme/generate_embedded_qss.py |   4 +
 src/phoenix_commons/theme/tokens.py                | 127 +++++++++++
 src/phoenix_commons/updater/client.py              |   2 +
 src/phoenix_commons/updater/installer.py           |   2 +
 src/phoenix_commons/updater/qt.py                  |   2 +
 src/phoenix_commons/widgets/buttons.py             |   2 +
 src/phoenix_commons/widgets/helpers.py             |   2 +
 src/phoenix_commons/widgets/no_scroll.py           |   7 +
 src/phoenix_commons/widgets/panel.py               |   2 +
 src/phoenix_commons/widgets/table.py               |   2 +
 src/phoenix_commons/widgets/typography.py          |   2 +
 src/phoenix_commons/widgets/update_banner.py       |   2 +
 25 files changed, 1057 insertions(+), 31 deletions(-)
```

## 12. Verification output

```
$ python -m compileall -q src tests
(exit 0)

$ QT_QPA_PLATFORM=offscreen python -m pytest -q tests/
...................................................................      [100%]
67 passed in 0.22s
```

67/67 tests pass — same coverage as Phase 2.2 end-state. No tests
added this phase; the underlying behaviour was unchanged (tokens
re-exported transparently, cache renamed without functional change,
generator HEADER updated and re-rendered byte-identically).

## 13. Branch state — local

```
$ git branch -vv

  baseline-v1                       417f860 [origin/baseline-v1] Add remote bootstrap report …
* main                              e314a0d [origin/main] Add VERIFICATION_MATRIX.md (Phase 2.5 step 6)
  phase-2-theme-widgets             db1d8b4 Add Phase 2 report …
  phase-3-paths-updater             b2e7f79 Add Phase 3A report …
  phase-4-pyinstaller-compatibility ba3d2c4 [origin/phase-4-pyinstaller-compatibility] Phase 6C backup report …
```

## 14. Remote state — origin

```
$ git ls-remote --heads origin

417f8600…  refs/heads/baseline-v1                          ← unchanged this turn
e314a0d…   refs/heads/main                                 ← updated (3 new commits)
ba3d2c4d…  refs/heads/phase-4-pyinstaller-compatibility    ← unchanged this turn
```

Push command run: `git push origin main` (`2f21ae5..e314a0d`).

## 15. Confirmation — no migration/build/runtime work occurred

- ❌ **No app code modified** (zero edits to PCC, Job Tracker, Phoenix CAD, Phoenix Checkout, ValveMaster source).
- ❌ **No emoji-icon replacement.** Production tools still use whatever icons they have today.
- ❌ **No component migration.** Existing widget classes unchanged.
- ❌ **No widget rewrites.** The contract doc describes the rules — it doesn't change any widget implementation.
- ❌ **No `build.bat` / PyInstaller / Inno Setup / updater download/apply / `gh release`** invocations.
- ❌ **No CI workflow change** (the new tests landed in Phase 2.1 and 2.2 already; Phase 2.5 added no new tests).
- ❌ **No frozen-exe verification** attempted. Still gated by S1/AV (BLOCKERS.md §1).
- ❌ **No `_generated/` directory created.** Decision documented; no source change.
- ❌ **No retrofits started. No packaging verification started. No migrations started.**

Operations performed this turn:

```
(Edit)   13 modules — added __all__ to each
(Edit)   src/phoenix_commons/theme/generate_embedded_qss.py    ← HEADER += __all__
python -m phoenix_commons.theme.generate_embedded_qss          ← regenerated embedded_qss.py
git mv   src/phoenix_commons/icons/cache.py → _cache.py        (via Write + git rm; git detected rename)
(Edit)   src/phoenix_commons/icons/loader.py + __init__.py     ← import path update
(Write)  docs/ui-platform-baseline-v1/API_BOUNDARIES.md
python -m compileall -q src tests
QT_QPA_PLATFORM=offscreen python -m pytest -q tests/           ← 67 passed
git add … && git commit "Stabilize commons API boundaries"     ← Step 1

(Write)  src/phoenix_commons/theme/tokens.py
(Edit)   src/phoenix_commons/icons/registry.py                 ← re-export SEMANTIC_COLORS from tokens
(Write)  docs/ui-platform-baseline-v1/ICON_POLICY.md
(Write)  docs/ui-platform-baseline-v1/COMPONENT_CONTRACT.md
(Edit)   docs/ui-platform-baseline-v1/PLATFORM_CONTRACT.md     ← drop "planned Phase 2.1" caveats
python -m compileall -q src tests
QT_QPA_PLATFORM=offscreen python -m pytest -q tests/           ← 67 passed
git add … && git commit "Add token module + icon/component contracts"  ← Steps 2-4

(Write)  docs/ui-platform-baseline-v1/VERIFICATION_MATRIX.md
git add … && git commit "Add VERIFICATION_MATRIX.md"           ← Step 6

git push origin main                                            ← 3 commits pushed (2f21ae5..e314a0d)

(Write)  docs/ui-platform-baseline-v1/STABILIZATION_REPORT_04.md
```

That's the entire surface.

## 16. STOP

Phase 2.5 complete. Architecture stabilization remains in effect.

Per the user spec for Phase 2.5: **Do NOT continue into packaging
verification, migrations, retrofits, icon replacement, component
rewrites, frozen verification, or installer/runtime work.** No code
change resumes without explicit phase approval per `BASELINE.md`
stop conditions.

Awaiting user direction.
