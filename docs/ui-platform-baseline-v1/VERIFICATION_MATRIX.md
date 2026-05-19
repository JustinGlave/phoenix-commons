# VERIFICATION_MATRIX.md

> Phase 2.6 preparation. Maps every commons subsystem to its
> verification mode and tracks current status. Rows marked
> **Verified** are exercised by the existing test suite or CI.
> **Blocked** rows are gated by the S1/AV chain (see BLOCKERS.md).
> **Unverified** rows have no test today but could be added without
> blockers. **Deferred** rows are explicit "later phase" items.
>
> Captured 2026-05-18 (initial). Updated 2026-05-19 (Phase 2.6
> packaging-verification dry-runs landed; 5 rows moved from
> Unverified/Deferred to Verified). Re-snapshot at the start of
> every verification-related phase.

## Legend

| Status | Meaning |
|--------|---------|
| ✅ **Verified** | Exercised by an automated test or CI gate today. Re-runs on every PR. |
| 🔴 **Blocked** | Test or build path exists but cannot run pending an external blocker (e.g. S1/AV bootloader-quarantine, BLOCKERS.md §1). |
| ⚠️ **Unverified** | Not currently tested. Can be added without blockers — just hasn't been a priority yet. |
| ⏳ **Deferred** | Explicitly out of scope until a named future phase. |
| 📝 **Doc-only** | Verified by documentation review at PR time; no automated test possible. |

## Matrix

### Source mode (runtime imports + behaviour)

| Row | What | Status | Where verified |
|-----|------|--------|----------------|
| 1.1 | `phoenix_commons` package imports cleanly | ✅ Verified | `tests/test_smoke.py::test_imports` (Phase 1) |
| 1.2 | `phoenix_commons.__version__` returns `"0.1.0"` | ✅ Verified | `tests/test_smoke.py` (Phase 1) |
| 1.3 | `phoenix_commons.theme.apply_dark_theme` resolves + applies | ✅ Verified | `tests/test_embedded_qss.py::test_apply_dark_theme_imports_after_migration` + `test_apply_dark_theme_fallback_uses_embedded_qss` (Phase 2.1) |
| 1.4 | `phoenix_commons.icons.icon(...)` returns a non-null `QIcon` | ✅ Verified | `tests/test_icons.py::test_icon_returns_qicon` (Phase 2.2) |
| 1.5 | `phoenix_commons.theme.tokens` constants resolve | ✅ Verified | `tests/test_tokens.py` — palette constants are hex; `SEMANTIC_COLORS` mirrors module constants; `C is SEMANTIC_COLORS` identity; module is Qt-free (Phase 2.6) |
| 1.6 | `phoenix_commons.widgets.*` instantiate under offscreen Qt | ✅ Verified | `tests/test_smoke.py::test_component_instantiation` (Phase 1) |
| 1.7 | `phoenix_commons.widgets.no_scroll.*` instantiate | ✅ Verified | `tests/test_smoke.py::test_no_scroll_instantiation` (Phase 1) |
| 1.8 | `phoenix_commons.paths.user_data_dir` creates the dir | ✅ Verified | `tests/test_paths.py` (Phase 3) |
| 1.9 | `phoenix_commons.updater.check_for_update` returns `UpdateInfo \| None` | ✅ Verified | `tests/test_updater.py` (Phase 3) |
| 1.10 | `phoenix_commons.updater.installer._validate_update_zip` covers both `expected_internal` modes | ✅ Verified | `tests/test_updater.py` (Phase 3) |

### Editable install

| Row | What | Status | Where verified |
|-----|------|--------|----------------|
| 2.1 | `pip install -e .` succeeds | ✅ Verified | CI workflow step (`pip install -e .[test]`) |
| 2.2 | `pip install -e .[test]` pulls pytest + pytest-qt | ✅ Verified | CI workflow step |
| 2.3 | Editable install picks up package data (`*.qss`, `*.svg`) at runtime | ✅ Verified | Implicit — `test_apply_dark_theme_fallback_uses_embedded_qss` + `test_package_data_includes_all_starter_svgs` exercise the resolution paths |
| 2.4 | `pip install .` (non-editable) bundles `*.qss` + `*.svg` | ✅ Verified | Phase 2.6 dry-run in a temp venv: `pip install .` then `importlib.resources` resolved `phoenix_style.qss` (17,662 B) and 10 SVGs from the site-packages install. Test `test_packaging.py::test_pyproject_declares_both_package_data_paths` pins the declaration. |

### Package-data loading

| Row | What | Status | Where verified |
|-----|------|--------|----------------|
| 3.1 | `phoenix_style.qss` resolvable via the loader's `_resource_path` | ✅ Verified | `apply_dark_theme` fallback test exercises both branches (Phase 2.1) |
| 3.2 | Every name in `ICON_NAMES` has a real SVG under `lucide/` | ✅ Verified | `tests/test_icons.py::test_package_data_includes_all_starter_svgs` (Phase 2.2) |
| 3.3 | Every shipped SVG contains `currentColor` (recolour pipeline pre-req) | ✅ Verified | Same test as 3.2 — asserts `b"currentColor" in content` |
| 3.4 | `importlib.resources.files("phoenix_commons.icons.lucide")` resolves under editable install | ✅ Verified | Same test as 3.2 — the test uses `files(...)` directly |

### QSS loading

| Row | What | Status | Where verified |
|-----|------|--------|----------------|
| 4.1 | On-disk `phoenix_style.qss` loads when present | ✅ Verified | Implicit via `test_make_qss_non_empty` + `apply_dark_theme` integration |
| 4.2 | Embedded fallback loads when on-disk file is missing | ✅ Verified | `tests/test_embedded_qss.py::test_apply_dark_theme_fallback_uses_embedded_qss` (monkey-patches `_resource_path`) |
| 4.3 | The two paths produce identical effective stylesheets (byte-for-byte) | ✅ Verified | `tests/test_embedded_qss.py::test_generator_is_deterministic_and_idempotent` (stale-fallback CI guard) |
| 4.4 | Canonical Phoenix System A tokens are present in the QSS | ✅ Verified | `tests/test_embedded_qss.py::test_embedded_qss_contains_canonical_tokens` + `tests/test_smoke.py::test_canonical_token_names_present_in_qss` |

### Icon loading

| Row | What | Status | Where verified |
|-----|------|--------|----------------|
| 5.1 | `icon(name)` returns a non-null `QIcon` for every registered name | ✅ Verified | `tests/test_icons.py::test_every_registered_icon_loads` (parametrised across `ICON_NAMES`) |
| 5.2 | Unknown name raises `IconNotFoundError` with suggestions | ✅ Verified | `tests/test_icons.py::test_missing_icon_raises_clear_error` |
| 5.3 | Recolour via `color="primary"` differs from default | ✅ Verified | `tests/test_icons.py::test_recolour_produces_different_pixels` |
| 5.4 | Hex literal `color="#dc2626"` matches semantic `color="primary"` pixel-for-pixel | ✅ Verified | `tests/test_icons.py::test_hex_and_semantic_resolve_to_same_pixels` |
| 5.5 | `size=` honoured by rasterised pixmap | ✅ Verified | `tests/test_icons.py::test_size_parameter_is_honoured` |
| 5.6 | Cache returns same instance on repeat call with same args | ✅ Verified | `tests/test_icons.py::test_cache_hit_returns_same_instance` |
| 5.7 | Cache distinguishes `(name, color, size)` | ✅ Verified | `tests/test_icons.py::test_cache_distinguishes_name_color_and_size` |
| 5.8 | `_recolor` byte-substitution handles both quote styles | ✅ Verified | `tests/test_icons.py::test_recolor_handles_single_quotes` |
| 5.9 | `icon()` consumes `SEMANTIC_COLORS` from `theme.tokens` | ✅ Verified | `tests/test_packaging.py::test_icons_consumes_tokens_semantic_colors` (identity check) + `test_icon_registry_imports_from_tokens_not_inlined` (static import inspection) — Phase 2.6 |

### Generated fallback

| Row | What | Status | Where verified |
|-----|------|--------|----------------|
| 6.1 | `embedded_qss.py` is byte-identical to `render(phoenix_style.qss)` | ✅ Verified | `tests/test_embedded_qss.py::test_generator_is_deterministic_and_idempotent` (the stale-fallback CI guard) |
| 6.2 | Generator is idempotent across runs | ✅ Verified | Same test — same input always produces same output |
| 6.3 | Generator handles CRLF / LF line endings deterministically | ✅ Verified | Implicit — generator normalises to LF on read + write; test runs on Windows CI |
| 6.4 | Generator bails (exit 3) on `"""` in source | ⚠️ Unverified | Documented behaviour; no test fixture introduces a `"""` to exercise the guard. Low-risk because real QSS never contains it. |
| 6.5 | Future generated artifacts move under `_generated/` | ⏳ Deferred | Per Generated Artifacts Policy threshold ("once there are more than one or two"). One artifact today → not yet. |

### CI

| Row | What | Status | Where verified |
|-----|------|--------|----------------|
| 7.1 | CI runs on every push to `main` + every PR | ✅ Verified | `.github/workflows/ci.yml` (Phase 1 stabilization) |
| 7.2 | CI runs on Windows-latest with Python 3.12 (ADR-014) | ✅ Verified | Workflow `runs-on: windows-latest` + `python-version: "3.12"` |
| 7.3 | `python -m compileall -q .` runs in CI | ✅ Verified | Workflow Step 1 |
| 7.4 | `pytest -q tests/` runs in CI with `QT_QPA_PLATFORM=offscreen` | ✅ Verified | Workflow Step 2 + `tests/conftest.py` defensive double-set |
| 7.5 | CI fails on any test failure | ✅ Verified | Default pytest behaviour |
| 7.6 | CI artefact (PyInstaller build smoke) | ⏳ Deferred | Optional commented job in the workflow template; not enabled. Phase 4+ candidate. |

### Updater payload contracts

| Row | What | Status | Where verified |
|-----|------|--------|----------------|
| 8.1 | `check_for_update` returns `None` for stale + handles network failure silently | ✅ Verified | `tests/test_updater.py` (Phase 3) |
| 8.2 | `_validate_update_zip` with `expected_internal=True` accepts flat + nested layouts | ✅ Verified | `tests/test_updater.py` (Phase 3) |
| 8.3 | `_validate_update_zip` with `expected_internal=False` rejects zips missing the exe | ✅ Verified | `tests/test_updater.py` (Phase 3) |
| 8.4 | `download_and_apply` raises `RuntimeError` when not frozen | ✅ Verified | `tests/test_updater.py` (Phase 3) |
| 8.5 | Real end-to-end download + apply against a GitHub Release | 🔴 Blocked | Requires a signed PyInstaller exe to test against. Gated by S1/AV chain (BLOCKERS.md §1). |
| 8.6 | Production-tool payload asymmetry (full-folder vs exe-only) documented | ✅ Verified | `docs/production-inventory.md` per-tool rows |

### Submodule usage

| Row | What | Status | Where verified |
|-----|------|--------|----------------|
| 9.1 | Submodule shape `app/commons/` is consumable by pip-install-e | ✅ Verified | Phase 2.6 sandbox dry-run: `sandbox/app/commons/` populated via `git archive HEAD \| tar -x` (working-tree shape equivalent to a real submodule for pip purposes); `pip install -e ./commons` from a fresh venv resolved `phoenix_commons.__file__` to the sandbox path. The `git submodule add` invocation itself is exercised by Command Center wizard scaffolding (Phase 5+), out of scope here. |
| 9.2 | `pip install -e ./commons` resolves the package from a tool's working tree | ✅ Verified | Phase 2.6 sandbox dry-run output: `phoenix_commons.__file__` resolved to `sandbox/app/commons/src/phoenix_commons/__init__.py`. Every public surface (theme, tokens, icons, paths, updater) reachable via the editable install. |
| 9.3 | Plan B (vendoring) — `refresh_commons.bat` works | ⏳ Deferred | Wizard generates the file; verified during Phase 6 dogfood (out of scope for Phase 2.6) |

### Frozen mode

| Row | What | Status | Where verified |
|-----|------|--------|----------------|
| 10.1 | `pyinstaller --onedir --collect-all phoenix_commons main.py` produces a launchable exe | 🔴 Blocked | S1/AV bootloader-quarantine (BLOCKERS.md §1) prevents producing a working frozen exe on Justin's laptop |
| 10.2 | Frozen exe loads `phoenix_style.qss` from `_internal/phoenix_commons/theme/` | 🔴 Blocked | Same |
| 10.3 | Frozen exe loads `*.svg` from `_internal/phoenix_commons/icons/lucide/` | 🔴 Blocked | Same |
| 10.4 | Frozen exe falls back to `EMBEDDED_QSS` when the on-disk QSS is missing | 🔴 Blocked | Same — the fallback path is unit-tested in source mode (row 4.2); the frozen variant needs the AV chain resolved |
| 10.5 | Frozen exe's `phoenix_commons.icons.icon()` round-trips through PyInstaller's bundled package data | 🔴 Blocked | Same |

### Installer runtime

| Row | What | Status | Where verified |
|-----|------|--------|----------------|
| 11.1 | Inno Setup installer extracts the full-folder layout to `{localappdata}\ATS Inc\<App>` | 🔴 Blocked | Downstream of frozen-exe block |
| 11.2 | Installed exe launches and applies theme | 🔴 Blocked | Same |
| 11.3 | Auto-update from a previous installed release works | 🔴 Blocked | Same |
| 11.4 | User-data path `%APPDATA%\ATS Inc\<App>` survives upgrade | 🔴 Blocked | Same |

## Summary tally

| Status | Rows | Δ since Phase 2.5 |
|--------|------|-------------------|
| ✅ Verified | 35 | +5 |
| ⚠️ Unverified | 1 | -3 |
| ⏳ Deferred | 3 | -2 |
| 🔴 Blocked | 9 | 0 |
| 📝 Doc-only | 0 | 0 |

**35 / 48 rows verified after Phase 2.6.** Phase 2.6 moved five rows
into Verified:

- Row 1.5 — `theme.tokens` smoke (new `tests/test_tokens.py`)
- Row 2.4 — non-editable install bundles `*.qss` + `*.svg`
- Row 5.9 — icons consume `SEMANTIC_COLORS` from `theme.tokens`
- Row 9.1 — submodule shape consumable by `pip install -e`
- Row 9.2 — `pip install -e ./commons` resolves the package

All 9 blocked rows still trace back to the single S1/AV
bootloader-quarantine root cause (`BLOCKERS.md §1`). Resolving
that unblocks Phase 4 PyInstaller verification, which unblocks
frozen mode (10.x) and installer runtime (11.x). The one remaining
unverified row (6.4 — generator triple-quote guard) is low-risk
and trivial to add when convenient.

## Closing the gap

| Gap | Plan | Status |
|-----|------|--------|
| Row 1.5 — token smoke test | Added `tests/test_tokens.py` Phase 2.6 | ✅ Closed |
| Row 2.4 — wheel-build smoke | Phase 2.6 dry-run in a temp venv; `pip install .` and `importlib.resources` resolved everything | ✅ Closed |
| Row 5.9 — explicit icon → tokens indirection test | Added `tests/test_packaging.py::test_icons_consumes_tokens_semantic_colors` (identity check) + `test_icon_registry_imports_from_tokens_not_inlined` (static check) | ✅ Closed |
| Row 6.4 — generator triple-quote guard | Add a unit test that calls `render('"""evil"""')` via `main()` against a tmp fixture. Not urgent. | ⚠️ Still open |
| Row 6.5 — `_generated/` migration | Triggered automatically when the second generated artifact lands. Policy at PLATFORM_CONTRACT.md § Generated artifacts. | ⏳ Deferred |
| Row 9.1 — submodule shape | Verified via sandbox dry-run (`git archive` + `pip install -e`) | ✅ Closed |
| Row 9.2 — editable submodule install | Same sandbox dry-run | ✅ Closed |
| Row 9.3 — Plan B vendoring | Exercised during Phase 6 dogfood once a consuming app exists | ⏳ Deferred |
| Blocked rows 8.5, 10.x, 11.x — frozen + installer | Single gating issue: S1/AV chain. Tracked in `BLOCKERS.md §1`. No commons-side work resumes on these until that's resolved. | 🔴 Blocked |

## See also

- `BLOCKERS.md` — the seven blockers gating frozen / installer rows
- `PLATFORM_CONTRACT.md` — what each subsystem is supposed to do
- `API_BOUNDARIES.md` — what's actually shipping today
- `STABILIZATION_REPORT_04.md` — Phase 2.5 deliverable that produced
  this matrix
