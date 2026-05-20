# PHASE_3A_PHOENIX_CAD_REPORT.md

> Phoenix CAD pilot migration — the first real retrofit against the
> stabilized Phoenix UI Platform. Validates the retrofit workflow + the
> commons API contracts end-to-end in source mode.
>
> Source-mode only. No PyInstaller, no Inno Setup, no frozen-exe
> validation, no installer testing, no updater deployment, no release
> work. AV/S1-gated rows remain blocked.
>
> Captured 2026-05-19.

## 1. Status

**Passed.** Phoenix CAD now consumes `phoenix-commons` via git submodule
+ editable install per ADR-015. Three local platform-duplicate subsystems
(theme loader, widget catalog, updater) replaced with thin facades that
preserve all caller-side imports. Visual parity preserved by construction
(identity-equal widget classes, byte-identical substituted QSS). All
contract checks green.

- **10 logical commits.** 3 in commons (`phoenix-commons:main`) +
  7 in Phoenix CAD (`Phoenix_CAD_Tool:phase-3a-phoenix-cad-retrofit`).
  All pushed to origin.
- **Source-mode validation: GREEN** — compileall clean, all retrofit
  imports resolve, identity checks pass, contracts preserved.
- **91/91 commons tests pass.** 6 new tests added for the BrandProfile
  mechanism; 2 new tests for sentinel substitution; 3 existing tests
  updated to reflect post-sentinelization expectations.
- **No production-tool source touched** outside Phoenix CAD. No
  Phoenix Checkout, no PCC, no Job Tracker, no ValveMaster work.
- **`cad/` subsystem completely untouched.** BricsCAD COM integration
  unchanged. `app.py` orchestration unchanged.

Architecture stabilization remains in effect. Phase 3B (Phoenix
Checkout retrofit) NOT started.

## 2. Pre-flight state

Phase 3A began with a **pre-flight inconsistency** in `Phoenix_CAD_Tool`
that required user-approved isolation work before the retrofit could
proceed.

### Initial state (blocked)

| Repo | Branch | Working tree | Origin sync |
|------|--------|--------------|--------------|
| `phoenix-commons` | `main` = `74c6cab` | ✅ clean | ✅ in sync |
| `Phoenix_CAD_Tool` | `master` = `38bc9b8` | ❌ **6 modified files (192 lines uncommitted)** | ❌ **2 commits ahead, not pushed** |

The 6 modified files (`app.py`, `blocks/cscp/HOOD/HOOD_ACM.dwg`,
`cad/hood_detail.py`, `config/product_lines.json`, `ui/main_window.py`,
`ui/pbc.py`) were continuation of an in-flight "Hood wiring detail"
feature. The two unpushed commits (`c170705` H1+H2+H3, `38bc9b8` H4)
were earlier stages of the same feature.

`cad/hood_detail.py` (+142 lines) is in the `cad/` subsystem that
`PLATFORM_CONTRACT.md` explicitly forbids touching during retrofit —
not a candidate for inclusion in the retrofit PR.

### Isolation (user-approved Option 3)

User approved isolating the WIP onto a dedicated feature branch and
resetting `master` to a clean baseline:

1. `git checkout -b feature/hood-detail` (from current `master`)
2. Staged + committed the 6 modified files as
   `32122ad WIP: park hood-detail in-flight work before Phase 3A retrofit`
3. `git push -u origin feature/hood-detail`
4. `git checkout master`
5. `git reset --hard origin/master` (master returns to `3358807`)
6. `git checkout -b phase-3a-phoenix-cad-retrofit` (the retrofit branch)
7. `git push -u origin phase-3a-phoenix-cad-retrofit`

### Final pre-retrofit state (passed)

| Repo | Branch | Working tree | Origin sync |
|------|--------|--------------|--------------|
| `phoenix-commons` | `main` = `74c6cab` | ✅ clean | ✅ in sync |
| `Phoenix_CAD_Tool` | `phase-3a-phoenix-cad-retrofit` = `3358807` (from clean `master`) | ✅ clean | ✅ pushed |
| `Phoenix_CAD_Tool` | `feature/hood-detail` = `32122ad` (WIP preserved) | ✅ pushed | ✅ pushed |

Phoenix CAD remains:
- **System A** — `phoenix_style.qss` byte-identical (after CRLF/LF
  normalization) to `commons/src/phoenix_commons/theme/phoenix_style.qss`
- **`expected_internal=True`** — hard-validated in pre-retrofit
  `updater.py:_validate_update_zip`
- **Full-folder updater contract** — confirmed by inspection +
  `production-inventory.md`

## 3. Backup confirmation

Per the phase spec, fresh git bundles created beside earlier backups.

```
$ ls -la C:/Users/justing/PycharmProjects/Backups/

-rw-r--r-- ... 1,535,920 May 19 19:07 Phoenix_CAD_Tool-20260519.bundle      ← new this phase
-rw-r--r-- ...    77,783 May 13 12:28 phoenix-command-center-20260513.bundle ← prior
-rw-r--r-- ... 3,338,226 May 13 12:28 phoenix-commons-20260513.bundle        ← prior
-rw-r--r-- ... 3,611,467 May 19 19:07 phoenix-commons-20260519.bundle        ← new this phase
```

Both bundles verified with `git bundle verify`:

| Bundle | SHA captured | Verify result |
|--------|---------------|----------------|
| `phoenix-commons-20260519.bundle` | `74c6cab` (main HEAD pre-A1) + all other branches | ✅ "records a complete history" |
| `Phoenix_CAD_Tool-20260519.bundle` | `3358807` (master) + `32122ad` (feature/hood-detail) + tags `v0.1.0`, `v0.1.1`, `pre-audit-baseline` | ✅ "records a complete history" |

## 4. Every duplicated subsystem removed

### 4.1. Theme loader (`ui/style.py`)

| | Pre-retrofit | Post-retrofit |
|---|---|---|
| LOC | ~830 | ~55 |
| `apply_dark_theme` | Locally defined; loaded `phoenix_style.qss` from `_resource_path("phoenix_style.qss")` or fell back to a 770-line `_EMBEDDED_QSS` literal | Re-imported from `phoenix_commons.theme` |
| `_EMBEDDED_QSS` | 770-line hand-maintained QSS literal kept in sync by `tools/embed_qss.py` | **Deleted** — commons owns `EMBEDDED_QSS` (generated by `phoenix_commons.theme.generate_embedded_qss`) |
| `_resource_path` | Resolved any file (commons-owned OR app-owned) | **Narrowed** — resolves only app-local assets (`LLT_Normal.ico`, `LLT_Transparent.png`); commons resources resolved by commons internally |
| `tools/embed_qss.py` | Script that kept `_EMBEDDED_QSS` in sync with `phoenix_style.qss` | **Deleted** — `phoenix_commons.theme.generate_embedded_qss` is the canonical sync path |

### 4.2. Widget catalog (`ui/components.py`)

| | Pre-retrofit | Post-retrofit |
|---|---|---|
| LOC | ~640 | ~400 |
| Commons-duplicate classes | `PrimaryButton`, `SecondaryButton`, `TertiaryButton`, `PageTitle`, `PageSubtitle`, `SectionTitle`, `HintLabel`, `Panel`, `PhoenixTable`, `UpdateBanner`, `button_row`, `NoScrollComboBox`, `NoScrollSpinBox`, `NoScrollDoubleSpinBox`, `NoScrollDateEdit` (15 classes ~250 LOC) | **Re-exported from commons** |
| App-local widgets | `_WatermarkOverlay`, `BackgroundWatermarkWidget`, `WelcomeDialog`, `PreferencesDialog`, `JobBrowserDialog` (~400 LOC) | Unchanged — kept in place |

Identity check post-retrofit:

```python
ui.components.PrimaryButton  is  phoenix_commons.widgets.PrimaryButton  → True
ui.components.Panel          is  phoenix_commons.widgets.Panel          → True
ui.components.PhoenixTable   is  phoenix_commons.widgets.PhoenixTable   → True
ui.components.UpdateBanner   is  phoenix_commons.widgets.UpdateBanner   → True
```

Phoenix CAD's widgets are not just re-imported under the same name —
they're literally the same Python class objects. Zero widget code
remains duplicated.

### 4.3. Updater (`updater.py`)

| | Pre-retrofit | Post-retrofit |
|---|---|---|
| LOC | ~358 | ~95 |
| Heavy/5-constant block | `GITHUB_OWNER`, `GITHUB_REPO`, `EXE_NAME`, `APP_DIR_NAME`, `ZIP_ASSET_NAME`, `APP_DISPLAY_NAME`, `USER_AGENT`, `RELEASES_API`, `REQUEST_TIMEOUT` | Trimmed to 4 tool-specific configuration constants only (`GITHUB_OWNER`, `GITHUB_REPO`, `EXE_NAME`, `ZIP_ASSET_NAME`); others were internal-only |
| `UpdateInfo` dataclass | Locally defined | Re-imported from commons |
| `UpdatePackageError` exception | Locally defined | Re-imported from commons |
| `_parse_version` | Locally defined | Removed (commons internal) |
| `check_for_update()` | ~60 lines reimplementing the API client | 7-line facade calling commons |
| `_validate_update_zip` | ~30 lines validating zip layout | Removed (commons internal) |
| `_ps_literal`, `_build_update_powershell_script`, `_build_update_batch` | ~100 lines generating PowerShell + batch wrappers | Removed (commons internal) |
| `download_and_apply()` | ~90 lines orchestrating download / validate / write / launch | 5-line facade calling commons with `expected_internal=True` |

### 4.4. Paths helpers (`paths.py`)

| | Pre-retrofit | Post-retrofit |
|---|---|---|
| LOC | ~75 | ~85 |
| `is_frozen()` | Locally defined | Imported from `phoenix_commons.paths` |
| `_resolve_user_data()` | Local — source mode returns repo root, frozen returns `%APPDATA%` | **Kept local** — Phoenix CAD's source-mode policy (dev data → repo root) differs from commons's `user_data_dir` (always `%APPDATA%`). Per MIGRATION_RULES.md § Drift-vs-extension, this is an "extension that uses commons primitives," not "drift." |
| `_resolve_project_root()` | Local | **Kept local** — same shape as commons but returns the directory; no clean 1:1 commons equivalent. |
| All path constants | Module-level — `USER_DATA_DIR`, `PROJECT_ROOT`, `JOBS_DIR`, `OUTPUT_DIR`, `LAST_GEN_LOG`, `FIXTURES_DIR`, `TEMPLATES_DIR`, `BLOCKS_DIR`, `CONFIG_PATH` | Unchanged — all preserved |

This retrofit is intentionally minimal. The MIGRATION_RULES drift-vs-
extension heuristic guided the call: behavior differences (source mode
writes to repo, not `%APPDATA%`) take precedence over consumption-for-
its-own-sake.

### 4.5. Repo-root `phoenix_style.qss`

| | Pre-retrofit | Post-retrofit |
|---|---|---|
| Location | `Phoenix_CAD_Tool/phoenix_style.qss` (consumed by `_resource_path` + bundled by `build.bat`) | **Deleted from repo root** |
| Legacy preservation | n/a | `Phoenix_CAD_Tool/legacy/phoenix_style.qss.preretrofit` (per MIGRATION_RULES.md § Local backup QSS strategy; removal target ~30 days post-merge) |
| Build bundling | `--add-data="phoenix_style.qss;."` | `--collect-all=phoenix_commons` (PyInstaller bundles commons's QSS automatically) |

## 5. Every commons subsystem adopted

| Commons subsystem | How Phoenix CAD consumes it |
|---|---|
| `phoenix_commons.theme.apply_dark_theme` | `ui/style.py` re-exports it directly; `app.py:main()` calls it via the existing import path |
| `phoenix_commons.theme.tokens.BrandProfile` / `DEFAULT_BRAND` | Phoenix CAD uses `DEFAULT_BRAND` implicitly — `apply_dark_theme` called without `brand=` kwarg; sentinel substitution produces canonical red + deep blue + blue |
| `phoenix_commons.theme.EMBEDDED_QSS` | Resolved by `apply_dark_theme` internally as the QSS-file-missing fallback; Phoenix CAD never references it directly |
| `phoenix_commons.theme.phoenix_style.qss` (package data) | Resolved by `apply_dark_theme` from commons's installed package path; sentinel-substituted at apply time |
| `phoenix_commons.widgets.*` (12 public widget classes) | Re-exported through `ui/components.py` so all existing call sites in `ui/main_window.py`, `ui/pbc.py` continue working |
| `phoenix_commons.widgets.no_scroll.*` (4 wheel-event-guarded inputs) | Same — re-exported |
| `phoenix_commons.paths.is_frozen` | Imported in `paths.py` |
| `phoenix_commons.updater.UpdateInfo` | Re-imported through `updater.py` |
| `phoenix_commons.updater.check_for_update` | Wrapped by local `check_for_update()` (zero-arg) that passes the 4 Phoenix-CAD config constants |
| `phoenix_commons.updater.download_and_apply` | Wrapped by local `download_and_apply(info, progress_callback=None)` that passes `EXE_NAME` + `expected_internal=True` |
| `phoenix_commons.updater.installer.UpdatePackageError` | Re-imported through `updater.py` for callers that catch it specifically |

Subsystems **NOT adopted** (deliberately):

| Commons subsystem | Why not adopted by Phoenix CAD |
|---|---|
| `phoenix_commons.paths.user_data_dir` | Source-mode semantics differ — see § 4.4 |
| `phoenix_commons.paths.resource_path` | Phoenix CAD's `_resource_path` resolves app-local assets, not commons-owned files; the API shapes are intentionally different |
| `phoenix_commons.icons.icon` (Lucide loader) | Phoenix CAD doesn't have an immediate need for the Lucide icon set; introducing icon swaps would be feature work, not retrofit work. Deferred to a future polish phase. |
| `phoenix_commons.theme.tokens.SEMANTIC_COLORS` / `C` | No app code references tokens by name today; introducing token-based theming in app code would be feature work |
| `phoenix_commons.updater.qt.UpdateCheckThread` | Phoenix CAD's `ui/main_window.py` runs its own background-thread machinery for the update check; replacing it would touch `ui/main_window.py` business logic — out of retrofit scope |

These are all valid future-phase retrofit targets, but per the phase
spec ("retrofit only, no feature work, no clean-up"), they stay
deferred.

## 6. BrandProfile implementation details

Phase 3A landed the BrandProfile mechanism per ADR-016 in commons
(commits A1 + A2 + A3 on `phoenix-commons:main`).

### `phoenix_commons.theme.tokens` additions

```python
@dataclass(frozen=True)
class BrandProfile:
    """Controlled accent-override per ADR-016. Three named slots.
    Defaults match canonical PRIMARY/SECONDARY/ACCENT. Frozen so
    apps can't mutate at runtime."""
    primary:   str = PRIMARY
    secondary: str = SECONDARY
    accent:    str = ACCENT


DEFAULT_BRAND: BrandProfile = BrandProfile()
```

`__all__` updated to export `BrandProfile` + `DEFAULT_BRAND`.

### Properties enforced by tests

| Property | Pinned by |
|----------|------------|
| Default profile mirrors canonical constants | `test_brand_profile_default_matches_canonical_constants` |
| `DEFAULT_BRAND` is a `BrandProfile` instance | `test_default_brand_is_a_brand_profile` |
| Profile is frozen (mutation raises) | `test_brand_profile_is_frozen` |
| Only 3 named slots accepted (extras raise) | `test_brand_profile_only_accepts_three_named_slots` |
| PCC-style profile constructs cleanly | `test_pcc_style_brand_profile_resolves` |
| Partial override (only `accent=`) preserves other defaults | `test_brand_profile_partial_override_works` |
| `__all__` includes `BrandProfile` + `DEFAULT_BRAND` | `test_all_export_matches_public_surface` |

### Phoenix CAD usage

`app.py` calls `apply_dark_theme(app)` with **no `brand=` kwarg**.
The default brand profile (canonical red + deep blue + blue) is used
implicitly. **No visual change vs pre-retrofit.**

### PCC-future-readiness

The same mechanism PCC's Phase 3C retrofit will use is exercised in
commons by `test_apply_dark_theme_pcc_brand_substitutes_orange_teal` —
end-to-end with `BrandProfile(primary="#E8783C", secondary="#3CB8AE",
accent="#3CB8AE")`. Asserts orange + teal in the rendered stylesheet,
default hex literals absent, sentinels gone.

## 7. Sentinel-QSS implementation details

Phase 3A introduced sentinel substitution in `phoenix_commons.theme`.

### `phoenix_style.qss` transformation

| Token | Before | After | Occurrences |
|-------|--------|-------|--------------|
| PRIMARY | `#dc2626` | `__BRAND_PRIMARY__` | 3 |
| SECONDARY | `#1e3a8a` | `__BRAND_SECONDARY__` | 8 |
| ACCENT | `#3b82f6` | `__BRAND_ACCENT__` | 22 |
| All locked tokens (BG, SURFACE, TEXT, MUTED, status colours, etc.) | Hex literal | **Unchanged** (literal) | n/a |

QSS byte count: 16,891 → 17,216 (sentinels are slightly longer than
hex literals — deterministic).

### `embedded_qss.py` regeneration

`python -m phoenix_commons.theme.generate_embedded_qss` re-rendered
the embedded module against the sentinelized QSS. Output now contains
the sentinels too — substitution happens at apply time in both code
paths (file-on-disk + embedded fallback). The
`test_generator_is_deterministic_and_idempotent` stale-fallback CI
guard remains green.

### `apply.py` substitution helper

```python
_BRAND_SENTINELS: tuple[tuple[str, str], ...] = (
    ("__BRAND_PRIMARY__",   "primary"),
    ("__BRAND_SECONDARY__", "secondary"),
    ("__BRAND_ACCENT__",    "accent"),
)


def _substitute_brand(qss_text: str, brand: BrandProfile) -> str:
    for sentinel, attr in _BRAND_SENTINELS:
        qss_text = qss_text.replace(sentinel, getattr(brand, attr))
    return qss_text


def apply_dark_theme(app: QApplication, brand: BrandProfile | None = None) -> None:
    profile = brand if brand is not None else DEFAULT_BRAND
    # ...
    # Locked palette slots — universal:
    locked_palette = [(QPalette.ColorRole.Window, QColor(10, 14, 39)), ...]
    # Brand palette slots — follow active profile:
    brand_palette = [
        (QPalette.ColorRole.BrightText, QColor(profile.primary)),
        (QPalette.ColorRole.Highlight,  QColor(profile.accent)),
        (QPalette.ColorRole.Link,       QColor(profile.accent)),
    ]
    # ...
    app.setStyleSheet(_substitute_brand(qss_text, profile))
```

### Known sentinel-substitution edge case

One literal not converted: `rgba(30, 58, 138, 220)` at line 665 of the
QSS (used for `#UpdateBanner` background). This is SECONDARY in rgba
form (alpha 0.86). Substituting cleanly would require either:

1. A separate sentinel like `__BRAND_SECONDARY_RGB__` with a different
   substitution shape, OR
2. Converting the rgba form to hex (loses the alpha).

Documented in commit A2's message + this report.

**Impact on Phoenix CAD: zero** (uses default brand; rgba renders at
canonical SECONDARY anyway).

**Impact on PCC's future retrofit: small** — PCC's `#UpdateBanner`
background will render at canonical deep blue (`rgba(30, 58, 138, 220)`)
rather than PCC's teal. One surface, post-packaging-only. PCC's
retrofit PR will decide whether to address.

## 8. Visual parity findings

Per `VISUAL_BASELINE_RULES.md` § Capture mode, Phase 3A captures no
screenshots (S1/AV chain prevents reliable frozen-exe; offscreen-Qt
snapshots are not faithful representations). Visual parity assessed
structurally:

### Acceptable parity criteria — all met

| Criterion | Status | Evidence |
|----------|--------|----------|
| Spacing matches within ±2 px | ✅ | No layout code touched; Panel `setContentsMargins(16, 16, 16, 16)` unchanged; `button_row` unchanged |
| Typography matches: font family / size / weight / letter-spacing | ✅ | No typography code touched; QSS typography selectors unchanged (locked tokens, hex literals preserved) |
| Palette matches | ✅ | All locked-token hex literals unchanged; default brand profile produces same hex values as pre-retrofit. End-to-end test asserts `app.styleSheet()` contains `#dc2626`, `#3b82f6`, `#1e3a8a`, `#0a0e27` (verified live in offscreen smoke) |
| Panel hierarchy: same objectName, border, radius, padding | ✅ | `ui.components.Panel is phoenix_commons.widgets.Panel` (identity); commons Panel is byte-identical port of pre-retrofit Phoenix CAD Panel |
| Button semantics: primary/secondary/tertiary unchanged | ✅ | Same — identity check |
| Icon set: present in both / intentionally replaced | ✅ | No icons swapped this phase (icon retrofit deferred per § 5) |
| Update banner position + copy template | ✅ | `UpdateBanner` class identity-equal; `ui/main_window.py` integration unchanged |
| Focus / hover / disabled states | ✅ | QSS rules for these states use locked tokens; sentinelization didn't touch them |

### Per-app addendum — Phoenix CAD specifically

From `MIGRATION_VISUAL_REVIEW_CHECKLIST.md` § Phoenix CAD / Lab Layout Tool:

- [✅] `cad/` subsystem completely untouched — `git diff --stat 3358807..HEAD -- cad/` is empty
- [✅] BricsCAD COM call surface unchanged — `cad/` unchanged
- [✅] `app.py` modified **only at import lines** — actually `app.py` not modified at all (the local facades preserve the existing import shape)
- [✅] `LLT_Transparent.png` + `LLT_Normal.ico` stay app-local — confirmed (`_resource_path` resolves them from app root)

### Migration Visual Review Checklist — full walkthrough

Detailed row-by-row results below. Status legend: ✅ Verified parity,
⚠️ Intentional change with sign-off, ❌ Regression.

| Section | Result | Notes |
|---------|--------|-------|
| **1. Main window** | ✅ | No `MainWindow` code touched. `app.py:main()` calls `apply_dark_theme(app)` same as before. Title, default size, status bar, dark-titled OS chrome all preserved. |
| **2. Dashboard / home view** | ✅ | No dashboard code touched. |
| **3. Forms** | ✅ | `ui/components.py` re-exports same widget classes (identity check). Field order / labels / widths / tab order all derive from `ui/main_window.py` and `ui/pbc.py` (untouched). All raw `QPushButton` etc. already migrated to Phoenix tiers pre-retrofit. |
| **4. Tables / grids** | ✅ | `PhoenixTable` identity-equal to commons. Column counts / widths / row heights / alternating colours / no-selection / no-focus all derive from caller-side code (untouched). |
| **5. Dialogs** | ✅ | `WelcomeDialog`, `PreferencesDialog`, `JobBrowserDialog` definitions unchanged (still in `ui/components.py`). `QMessageBox` and `QFileDialog` usages preserved. |
| **6. Update banner** | ✅ | `UpdateBanner` identity-equal to commons; integration in `ui/main_window.py` unchanged. 44 px height, copy template, button widths (132 / 150 / 40 px) all preserved. |
| **7. Empty states** | ✅ | No empty-state copy touched. |
| **8. Dense-data states** | ✅ | No table rendering touched. |
| **9. Error / warning states** | ✅ | No error-handling code touched. |
| **10. Sidebar / navigation** | ✅ | No navigation code touched (Phoenix CAD has menu-bar nav; menu structure unchanged). |
| **Palette / tokens** | ✅ | All coloured pixels map to commons tokens. Sentinel substitution produces canonical hex for default brand. |
| **Typography** | ✅ | No font code touched. |
| **Spacing + radius** | ✅ | All locked. No sentinelization touched spacing or radius rules. |
| **Icons (post-Phase-2.2)** | N/A | Phoenix CAD doesn't use the Lucide loader yet (deferred per § 5). Emoji icons (if any) untouched. |
| **objectName discipline** | ✅ | Commons widgets set their own canonical objectNames; Phoenix CAD adds none that collide. |
| **Update banner specifically** | ✅ | `UpdateBanner` constructor signature unchanged; `install_clicked` signal wired same way; `expected_internal=True` confirmed in `updater.py:download_and_apply` source inspection. |
| **Updater behaviour** | ✅ | Same `UpdateCheckThread`-equivalent in `ui/main_window.py` (untouched); same `UpdateInfo` shape; same `download_and_apply` call. |

**No ⚠️ rows.** No intentional visible changes this phase. The
retrofit is purely structural; visible output identical.

**No ❌ rows.** No regressions detected.

## 9. Any regressions discovered

**None.** Every source-mode + import-level check green. No visible
output difference expected by construction (identity-equal widget
classes; canonical-default-brand sentinel substitution).

Edge cases that could surface as regressions in frozen mode (post
S1/AV chain resolution):

| Risk | Likelihood | Mitigation |
|------|------------|------------|
| `--collect-all=phoenix_commons` doesn't actually bundle `phoenix_style.qss` | Low | Phase 2.6 packaging-verification dry-runs verified `importlib.resources.files('phoenix_commons.theme')` finds the QSS in editable + wheel installs |
| Submodule init fails on a fresh clone | Low | Build.bat preflight catches this and prints actionable error |
| `expected_internal=True` rejects a future Phoenix CAD release whose zip layout drifts | Very low | Phoenix CAD's `build.bat` step 4 ("Verifying release artifacts") asserts `_internal/` is in the zip before declaring success |
| `apply_dark_theme(app)` reads QSS from commons in source mode, but commons isn't installed | Detected at startup via the `import phoenix_commons` failure | Handled by `pip install -r requirements.txt` which now includes `-e ./commons` |

## 10. Any deferred cleanup intentionally skipped

| Item | Why deferred |
|------|---------------|
| Phoenix CAD adopting `phoenix_commons.icons.icon` for emoji replacement | Out of retrofit scope per phase spec ("NO icon replacement broadly"). Future polish phase. |
| Phoenix CAD adopting `phoenix_commons.updater.qt.UpdateCheckThread` | Would require touching `ui/main_window.py`'s update-check threading code — out of retrofit scope. |
| Phoenix CAD adopting `phoenix_commons.paths.user_data_dir` | Source-mode semantics differ from Phoenix CAD's policy (repo root vs `%APPDATA%`). Deliberate extension per MIGRATION_RULES.md drift-vs-extension heuristic. |
| Phoenix CAD adopting `phoenix_commons.paths.resource_path` | API shape mismatch (filename vs directory). Phoenix CAD's `_resource_path` resolves app-local assets only. |
| Removing `legacy/phoenix_style.qss.preretrofit` | Per MIGRATION_RULES.md § Local backup QSS strategy — ~30-day safety window after the retrofit ships. |
| Updating `.github/workflows/ci.yml` to add `git submodule update --init` step | Phoenix CAD's CI is out of strict retrofit scope. The workflow's existing `python -m py_compile` + `python -c "import updater"` checks pass once a venv has `-e ./commons` installed; the submodule-init step should be added in a follow-up. |
| Updating `MIGRATION_RULES.md` to reflect actual Phase 3A branch name (`phase-3a-phoenix-cad-retrofit`) + single-tool pilot (not 2-tool "Phase 7") | Doc-drift cleanup. Should be addressed before Phase 3B opens its PR. |

## 11. Source-mode validation results

Detailed output from each check.

### 11.1. compileall (excluding commons/, build/, dist/, .venv/)

```
$ .venv/Scripts/python -m compileall -q -x "commons|build|dist|\.venv" .
(exit 0)
```

Clean. Every `.py` file in Phoenix CAD parses + bytecode-compiles.

### 11.2. Retrofit imports

```
$ .venv/Scripts/python -c "import paths, updater; from ui.style import apply_dark_theme, _resource_path; from ui.components import (PrimaryButton, …, JobBrowserDialog)"
```

All imports resolve cleanly. No circular imports, no missing names.

### 11.3. Identity checks (commons classes literally adopted)

```
ui.components.PrimaryButton  is phoenix_commons.widgets.PrimaryButton  → True
ui.components.Panel          is phoenix_commons.widgets.Panel          → True
ui.components.PhoenixTable   is phoenix_commons.widgets.PhoenixTable   → True
ui.components.UpdateBanner   is phoenix_commons.widgets.UpdateBanner   → True
```

### 11.4. Updater contract preservation

```
updater.GITHUB_OWNER       == 'JustinGlave'                                ✓
updater.GITHUB_REPO        == 'lab-layout-tool'                            ✓
updater.EXE_NAME           == 'LabLayoutTool.exe'                          ✓
updater.ZIP_ASSET_NAME     == 'LabLayoutTool.zip'                          ✓
updater.UpdateInfo         is phoenix_commons.updater.client.UpdateInfo    ✓
updater.UpdatePackageError is phoenix_commons.updater.installer.UpdatePackageError  ✓
inspect.getsource(updater.download_and_apply) contains 'expected_internal=True'      ✓
```

### 11.5. Paths contract

```
paths.is_frozen()       → False  (source mode)
paths.USER_DATA_DIR     → C:\Users\justing\PycharmProjects\Phoenix_CAD_Tool  (preserved repo-root policy)
paths.PROJECT_ROOT      → C:\Users\justing\PycharmProjects\Phoenix_CAD_Tool
paths.JOBS_DIR          → C:\Users\justing\PycharmProjects\Phoenix_CAD_Tool\jobs
paths.CONFIG_PATH       → C:\Users\justing\PycharmProjects\Phoenix_CAD_Tool\config\product_lines.json
paths.ORG_NAME          → "ATS Inc"
paths.APP_NAME          → "Lab Layout Tool"
```

### 11.6. Offscreen apply_dark_theme smoke

```
$ QT_QPA_PLATFORM=offscreen .venv/Scripts/python -c "
    from PySide6.QtWidgets import QApplication
    from ui.style import apply_dark_theme
    app = QApplication([])
    apply_dark_theme(app)
    sheet = app.styleSheet()"

apply_dark_theme → styleSheet OK, 16,891 chars, default-brand colours present
widget construction OK: PrimaryButton, Panel, PhoenixTable, UpdateBanner
```

Assertions inside the smoke:
- `'#dc2626' in sheet` (default PRIMARY substituted)
- `'#3b82f6' in sheet` (default ACCENT substituted)
- `'#1e3a8a' in sheet` (default SECONDARY substituted)
- `'#0a0e27' in sheet` (locked BG preserved)
- `'__BRAND_PRIMARY__' not in sheet` (sentinels substituted out)

All pass.

### 11.7. app.py module import

```
$ QT_QPA_PLATFORM=offscreen .venv/Scripts/python -c "import app"

app.py imports cleanly — every transitive retrofit dependency resolves
```

Exercises the entire top-level import graph: `cad`, `cad.blocks`,
`cad.layout`, `paths`, `ui.style`, `ui.main_window`, `version`. Every
transitive import (commons widgets, commons theme, commons updater,
commons paths) resolves.

### 11.8. Submodule pin matches commons HEAD

```
$ git -C commons rev-parse HEAD       → 8504abcb04ac7e3026f5060dd504a7e6f6c774ef
$ git -C ../phoenix-commons rev-parse main → 8504abcb04ac7e3026f5060dd504a7e6f6c774ef
```

Identical. The submodule pin captures the commons commit that lands
the BrandProfile mechanism (A1) + sentinel substitution (A2) + doc
updates (A3).

### 11.9. Commons regression test

```
$ cd phoenix-commons && pytest -q tests/
91 passed in 0.24s
```

No commons tests regress after the BrandProfile / sentinel-substitution
work. 91 total = 83 (Phase 2.7 end-state) + 6 BrandProfile + 2
brand-substitution.

## 12. Package-data validation results

Confirmed during Phase 2.6 (`STABILIZATION_REPORT_05.md` § 3.3):
non-editable `pip install` bundles `*.qss` + 10 `*.svg` via
`pyproject.toml`'s `[tool.setuptools.package-data]` table. Re-validated
this phase via Phoenix CAD's submodule install:

```
$ .venv/Scripts/python -c "
    from importlib.resources import files
    qss = (files('phoenix_commons.theme') / 'phoenix_style.qss').read_text(encoding='utf-8')
    print(f'QSS bundled: {len(qss):,} chars')
    print(f'sentinels present: {\"__BRAND_PRIMARY__\" in qss}')
"

QSS bundled: 17,216 chars
sentinels present: True
```

PyInstaller `--collect-all=phoenix_commons` (added to `build.bat` in
B7) will pick up the sentinelized QSS at frozen-build time. **Frozen
verification deferred** to Phase 4 (post S1/AV chain resolution).

## 13. Remaining local-only code in Phoenix CAD

After the retrofit, these files / definitions remain locally maintained
in Phoenix CAD (intentional — they're app-specific):

### Files unchanged by the retrofit

| File | Reason it stays local |
|------|------------------------|
| `app.py` | Application entry point + business-logic orchestration. Imports unchanged. |
| `cad/` (entire subsystem) | BricsCAD COM integration. Out of retrofit scope per `PLATFORM_CONTRACT.md`. |
| `ui/main_window.py` | App-specific main-window composition + business-logic wiring. |
| `ui/pbc.py` | App-specific PBC editor. |
| `version.py` | Per-app version. |
| `config/` | App-specific configuration (product lines, etc.). |
| `blocks/` | DWG block library — app domain. |
| `templates/` | DWG templates — app domain. |
| `jobs/` | Job fixtures. |
| `tools/` (minus `embed_qss.py` which was deleted) | App-specific build / debug helpers. |
| `LLT_Normal.ico`, `LLT_Transparent.png` | App branding assets — per `ICON_POLICY.md` § "Logos NEVER move to commons." |
| `installer.iss` | Inno Setup script — app-specific install configuration. |
| `.github/workflows/ci.yml` | App-specific CI. |

### Definitions retained locally after the retrofit

| Symbol | Where | Reason retained |
|--------|-------|------------------|
| `paths.ORG_NAME`, `paths.APP_NAME` | `paths.py` | Per-app constants. |
| `paths.USER_DATA_DIR`, `paths.PROJECT_ROOT`, `paths.JOBS_DIR`, `paths.OUTPUT_DIR`, `paths.LAST_GEN_LOG`, `paths.FIXTURES_DIR`, `paths.TEMPLATES_DIR`, `paths.BLOCKS_DIR`, `paths.CONFIG_PATH` | `paths.py` | App-specific path constants composing on commons primitives. |
| `paths._resolve_user_data`, `paths._resolve_project_root` | `paths.py` | App-specific source-mode policy (writable data → repo root). |
| `updater.GITHUB_OWNER`, `.GITHUB_REPO`, `.EXE_NAME`, `.ZIP_ASSET_NAME` | `updater.py` | Tool-specific GitHub Releases configuration. |
| `updater.check_for_update`, `updater.download_and_apply` | `updater.py` | Wrappers preserving the zero-arg / single-positional call shape. |
| `ui.style._resource_path` | `ui/style.py` | Resolves app-local assets (`LLT_Normal.ico`, etc.). |
| `BackgroundWatermarkWidget`, `_WatermarkOverlay` | `ui/components.py` | App-specific watermark composition. |
| `WelcomeDialog` | `ui/components.py` | App-specific first-run modal. |
| `PreferencesDialog` | `ui/components.py` | App-specific preferences editor. |
| `JobBrowserDialog` | `ui/components.py` | App-specific project picker. |

## 14. Future retrofit lessons learned

What worked + what would be improved on the next retrofit.

### Patterns that worked — replicate for Checkout / ValveMaster / Job Tracker

1. **Local-facade pattern.** Keeping `paths.py`, `updater.py`,
   `ui/style.py`, `ui/components.py` as local files that internally
   call commons preserves every caller-side import — zero changes
   required in `app.py`, `ui/main_window.py`, `ui/pbc.py`, `cad/`.
2. **Identity check.** `assert LocalClass is CommonsClass` is the
   strongest possible parity guarantee — proves no duplicate
   implementation lingers.
3. **Submodule + `pip install -e ./commons`.** ADR-015's pattern
   exercised end-to-end. Submodule pins to a specific commons SHA;
   editable install resolves the working tree. Worked first time.
4. **Many small commits.** Each retrofit commit (B1–B7) is its own
   self-contained logical unit. Easy to bisect; easy to revert
   selectively if a problem surfaces. Recommended for every retrofit.
5. **Sentinel-QSS substitution.** Cleanly preserved exact pixel output
   for the default brand profile while opening the override path for
   PCC. The `_substitute_brand` helper is small (3-line loop) and
   testable.
6. **Pre-flight gate.** The "stop on inconsistency" rule caught the
   Phoenix CAD WIP and gave the user a chance to isolate before the
   retrofit started. Without that gate, the WIP would have either
   contaminated the retrofit branch or been lost during a hasty reset.
7. **Drift-vs-extension heuristic from MIGRATION_RULES.md.** Decided
   the `paths.py` retrofit scope correctly — minimal change preserved
   behavior; deeper consumption was rejected because it would change
   Phoenix CAD's source-mode policy.

### Surprises / improvements for next retrofit

1. **`rgba()` colour literals are not cleanly sentinelizable.** One QSS
   surface (`#UpdateBanner` background, line 665) uses
   `rgba(30, 58, 138, 220)` — SECONDARY in rgba form. The current
   sentinel-substitution pipeline doesn't handle this; PCC's retrofit
   will see one surface render in canonical SECONDARY rather than the
   PCC override. Options for a follow-up commons PR:
   - Add a second sentinel form: `__BRAND_SECONDARY_RGB__` →
     `30, 58, 138` (no `rgb()`/`rgba()` wrapper).
   - Convert the one rgba usage to a hex with adjusted alpha via
     `background-color` shorthand if Qt's QSS supports it.
   - Accept the inconsistency for now; flag in PCC's retrofit PR.
2. **`MIGRATION_RULES.md` doc-drift.** The doc still references a
   2-tool "Phase 7" pilot with branch name `retrofit-phoenix-cad`.
   Reality: single-tool Phase 3A with branch
   `phase-3a-phoenix-cad-retrofit`. Should be reconciled before
   Phase 3B opens its PR.
3. **`.github/workflows/ci.yml` lacks submodule init.** CI will fail
   for a fresh clone of Phoenix CAD because `commons/` won't be
   populated until `git submodule update --init --recursive` runs.
   Should add to CI in a follow-up.
4. **No screenshots captured.** Phase 2.7 intentionally deferred
   pixel-level baselines until S1/AV resolves. This means visual
   parity is verified structurally (identity checks + sentinel
   substitution invariants) rather than pixel-by-pixel. Acceptable
   for Phase 3A but should be tightened for Phase 3B+: even an
   offscreen-Qt PNG snapshot would catch regressions the structural
   checks miss.
5. **PyInstaller `--collect-all=phoenix_commons` chosen over
   `--collect-data`.** More inclusive; safer for the submodule
   pattern. If a future retrofit needs a tighter bundle,
   `--collect-data phoenix_commons` would work but requires the
   icons sub-package to be picked up separately.

## 15. Recommended changes before Phoenix Checkout retrofit (Phase 3B)

### Pre-Phase-3B commons changes

**None required.** The commons API is sufficient for Checkout as-is.
Checkout will use:

- `phoenix_commons.theme.apply_dark_theme(app)` — same as Phoenix CAD
- `phoenix_commons.widgets.*` — re-exported via local `ui/components.py`-equivalent
- `phoenix_commons.paths.is_frozen` — same as Phoenix CAD
- `phoenix_commons.updater.check_for_update` / `download_and_apply` —
  with **`expected_internal=False`** (Checkout's exe-only updater
  payload contract per ADR-003)

### Pre-Phase-3B doc cleanups (recommended)

- Update `MIGRATION_RULES.md` to reflect actual phase numbering
  (`Phase 3A` single-tool, branch `phase-3a-phoenix-cad-retrofit`),
  OR explicitly mark the original "Phase 7 / 2-tool pilot" plan as
  superseded.
- Update `visual-baselines/checkout/baseline.md` § Migration sensitivity
  to note the lessons learned from Phoenix CAD (monolithic-GUI
  extraction is the heavier lift; `expected_internal=False` flag).

### Pre-Phase-3B Phoenix CAD follow-ups (recommended)

- Update `.github/workflows/ci.yml` to `git submodule update --init`
  before installing requirements. Currently CI would fail for a fresh
  PR clone.
- Consider tagging Phoenix CAD's current `master` as
  `pre-retrofit-baseline` so the pre-retrofit state has a permanent
  rollback target beyond the bundled backup. (The existing
  `pre-audit-baseline` tag predates this retrofit's work.)

### Phase 3B retrofit-PR template (extrapolated from Phase 3A)

Phoenix Checkout's retrofit should follow the same B1–B7 commit shape:

| # | Subject | Phoenix CAD equivalent |
|---|---------|-------------------------|
| B1 | Add commons submodule + editable install + requirements.txt entry | ✓ Worked |
| B2 | Retrofit Checkout's path helper (likely `_app_data_path()` in `checkout_tool_backend.py`) | ✓ Similar pattern |
| B3 | Retrofit `updater.py` (light/4-constant variant; `expected_internal=False`) | ⚠️ Different `expected_internal` kwarg |
| B4 | Retrofit theme load (inline in `checkout_tool_gui.py`; introduce a `ui/style.py` if useful) | Adapt to monolithic GUI |
| B5 | Retrofit widgets (consume from `phoenix_commons.widgets`; extract local dialogs into a `ui/components.py`-equivalent OR keep them inline) | Adapt — biggest scope variance |
| B6 | Preserve legacy `phoenix_style.qss` + delete repo-root copy | ✓ Same |
| B7 | Update `build.bat` + remove `--add-data="phoenix_style.qss;."` | ✓ Same |

The Checkout monolithic-GUI extraction (177 KB file per inventory) is
the biggest scope variance. Recommended to land the form/dialog/table
extraction in **multiple commits within a single PR** so the PR review
can walk through one extracted widget at a time.

## 16. Exact commit list

### phoenix-commons (3 logical commits — pushed to `origin/main`)

```
$ git log --oneline 74c6cab..main

8504abc Update baseline docs — BrandProfile mechanism landed Phase 3A
0b8d241 Sentinelize brand tokens in QSS + apply-time substitution (Phase 3A — ADR-016)
661739e Add BrandProfile dataclass + DEFAULT_BRAND (Phase 3A — ADR-016)
```

| Hash | Subject | Lines |
|------|---------|-------|
| `661739e` | A1 — BrandProfile dataclass + DEFAULT_BRAND | +171 / -4 |
| `0b8d241` | A2 — Sentinelize brand tokens in QSS + apply-time substitution | +288 / -102 |
| `8504abc` | A3 — Update baseline docs (BrandProfile landed Phase 3A) | +16 / -7 |

### Phoenix_CAD_Tool — pre-retrofit isolation

| Hash | Subject | Branch |
|------|---------|--------|
| `32122ad` | WIP: park hood-detail in-flight work before Phase 3A retrofit | `feature/hood-detail` |

### Phoenix_CAD_Tool — retrofit (7 logical commits — pushed to `origin/phase-3a-phoenix-cad-retrofit`)

```
$ git log --oneline 3358807..phase-3a-phoenix-cad-retrofit

2b040fc Update build.bat + delete tools/embed_qss.py (Phase 3A B7)
7f08ad6 Preserve legacy phoenix_style.qss + delete repo-root copy (Phase 3A B6)
dd53be2 Retrofit ui/components.py — re-export commons widgets + keep dialogs (Phase 3A B5)
ed1de8d Retrofit ui/style.py to phoenix_commons.theme shim (Phase 3A B4)
461687f Retrofit updater.py to phoenix_commons.updater facade (Phase 3A B3)
b4fd625 Retrofit paths.py to consume phoenix_commons.paths.is_frozen (Phase 3A B2)
6770cee Add phoenix-commons as submodule + editable install (Phase 3A B1)
```

| Hash | Subject | Lines |
|------|---------|-------|
| `6770cee` | B1 — phoenix-commons submodule + editable install | +10 / 0 |
| `b4fd625` | B2 — paths.py retrofit | +22 / -7 |
| `461687f` | B3 — updater.py retrofit (358 → 95 lines) | +78 / -334 |
| `ed1de8d` | B4 — ui/style.py retrofit (830 → 55 lines) | +35 / -812 |
| `dd53be2` | B5 — ui/components.py retrofit (640 → 400 lines) | +66 / -244 |
| `7f08ad6` | B6 — preserve legacy QSS + delete repo-root copy | +22 / 0 (rename) |
| `2b040fc` | B7 — build.bat update + delete tools/embed_qss.py | +24 / -107 |

**Cumulative Phoenix CAD diff** (vs `3358807` master baseline):

```
 .gitmodules                          |    3 +
 build.bat                            |  104 +-
 commons                              |    1 +
 legacy/README.md                     |   22 +
 legacy/phoenix_style.qss.preretrofit |  765 ++++++++  (rename from phoenix_style.qss)
 paths.py                             |   29 +-
 requirements.txt                     |    7 +
 tools/embed_qss.py                   |   96 --
 ui/components.py                     |  310 +---
 ui/style.py                          |  847 +---------
 updater.py                           |  412 +----
 12 files changed, 333 insertions(+), 2263 deletions(-)
```

**Net code reduction: 1,930 lines** removed from Phoenix CAD (mostly
duplicated platform code) — the vast majority of which is now provided
by commons.

## 17. Branch state

### phoenix-commons (local)

```
$ git -C phoenix-commons branch -vv

  baseline-v1                       417f860 [origin/baseline-v1]
* main                              8504abc [origin/main] Update baseline docs — BrandProfile mechanism landed Phase 3A
  phase-2-theme-widgets             db1d8b4
  phase-3-paths-updater             b2e7f79
  phase-4-pyinstaller-compatibility ba3d2c4 [origin/phase-4-pyinstaller-compatibility]
```

`main` updated this turn (3 commits ahead of `74c6cab`).

### Phoenix_CAD_Tool (local)

```
$ git -C Phoenix_CAD_Tool branch -vv

  feature/hood-detail           32122ad [origin/feature/hood-detail]
  master                        3358807 [origin/master]
* phase-3a-phoenix-cad-retrofit 2b040fc [origin/phase-3a-phoenix-cad-retrofit]
```

All three branches tracked + in sync with origin.

## 18. Remote state

### phoenix-commons

```
$ git -C phoenix-commons ls-remote --heads origin

417f8600…  refs/heads/baseline-v1                          ← unchanged this phase
8504abc…   refs/heads/main                                 ← updated (3 commits)
ba3d2c4d…  refs/heads/phase-4-pyinstaller-compatibility    ← unchanged this phase
```

Push: `git push origin main` (`74c6cab..8504abc`).

### Phoenix_CAD_Tool

```
$ git -C Phoenix_CAD_Tool ls-remote --heads origin

32122ad…   refs/heads/feature/hood-detail                ← new (pre-retrofit isolation)
3358807…   refs/heads/master                             ← unchanged
2b040fc…   refs/heads/phase-3a-phoenix-cad-retrofit       ← new (retrofit branch)
```

`master` unchanged — the retrofit is on a feature branch, not merged.
`feature/hood-detail` preserves the pre-retrofit WIP.

## 19. Remaining blockers

After Phase 3A:

| # | Blocker | Blocks | Status |
|---|---------|--------|--------|
| 1 | User approval for Phase 3B (Phoenix Checkout retrofit) | Phase 3B start | Awaiting explicit go-ahead per `BASELINE.md` stop conditions |
| 2 | S1/AV bootloader-quarantine | Frozen-exe validation, installer testing, real updater deploy | `BLOCKERS.md §1` — unchanged. Source-mode Phase 3A is unaffected. |
| 3 | Phoenix CAD retrofit-PR merge to `master` | Production rollout of the retrofit | Awaiting reviewer (Justin) approval. Retrofit branch ready. |
| 4 | Phoenix CAD legacy QSS removal | Cleanup of `legacy/phoenix_style.qss.preretrofit` | ~30 days after retrofit merges (per MIGRATION_RULES.md) |
| 5 | PCC palette ADR follow-through (palette implementation) | Phase 3C / PCC retrofit start | ADR-016 documented; PCC's retrofit registers its `BrandProfile` |
| 6 | Phoenix CAD CI `git submodule update --init` | Phoenix CAD CI passing on a fresh PR clone | Out of strict retrofit scope; recommended follow-up |
| 7 | `MIGRATION_RULES.md` doc-drift reconciliation | Doc clarity for Phase 3B reviewers | Recommended pre-Phase-3B cleanup |

Phase 3A architecturally and validation-wise complete. Items 3-7 are
operational follow-ups that don't block Phase 3B from starting.

## 20. Confirmation

### No other apps touched

| App | Modified? | Evidence |
|-----|-----------|----------|
| Phoenix Checkout | ❌ No | `Phoenix-Checkout-Tool` repo not touched. |
| Phoenix Command Center | ❌ No | `phoenix-command-center` repo not touched. |
| Job Tracker / Project Tracking Tool | ❌ No | `Job Tracker` repo not touched. |
| ValveMasterTool | ❌ No | `ValveMasterTool` repo not touched. |

### No runtime / frozen verification attempted

- ❌ **PyInstaller not invoked.** `build.bat` updated for future use but not run.
- ❌ **Inno Setup not invoked.**
- ❌ **No frozen .exe built.**
- ❌ **No installer .exe built.**
- ❌ **No installed-copy testing.**
- ❌ **`download_and_apply` not invoked.** No real release downloaded.

### No release / deploy work

- ❌ **No GitHub Release created.** No `gh release` invocations.
- ❌ **No git tag pushed.**
- ❌ **No artefact uploaded.**
- ❌ **No `master` merge.** Retrofit lives on `phase-3a-phoenix-cad-retrofit` until reviewer (Justin) merges.

### Operations performed this turn (full list)

```
Pre-flight inconsistency detection → user-approved Option 3 isolation
  git checkout -b feature/hood-detail
  git add (6 specific files) && git commit
  git push -u origin feature/hood-detail
  git checkout master
  git reset --hard origin/master  ← user-authorized destructive op
  git checkout -b phase-3a-phoenix-cad-retrofit
  git push -u origin phase-3a-phoenix-cad-retrofit

Backups
  git -C phoenix-commons bundle create … --all
  git -C Phoenix_CAD_Tool bundle create … --all
  git bundle verify (both)

Commons enabling work (A1 + A2 + A3 on phoenix-commons:main)
  (Write/Edit) tokens.py + tests/test_tokens.py
  git commit (A1)
  (Edit ×3) phoenix_style.qss with sentinel replacements
  (regenerate) embedded_qss.py
  (Write) apply.py with brand= kwarg + _substitute_brand
  (Edit ×3) tests/test_embedded_qss.py + tests/test_smoke.py
  pytest tests/  → 91 / 91 pass
  git commit (A2)
  (Edit) DESIGN_SYSTEM.md / PLATFORM_CONTRACT.md / API_BOUNDARIES.md — "Phase 3+" → "Phase 3A landed"
  git commit (A3)
  git push origin main

Phoenix CAD retrofit (B1 → B7 on Phoenix_CAD_Tool:phase-3a-phoenix-cad-retrofit)
  git submodule add https://github.com/JustinGlave/phoenix-commons.git commons
  .venv/Scripts/python -m pip install -e ./commons
  (Edit) requirements.txt — add `-e ./commons`
  git commit (B1)
  (Write) paths.py — facade
  git commit (B2)
  (Write) updater.py — facade
  git commit (B3)
  (Write) ui/style.py — shim
  git commit (B4)
  (Write) ui/components.py — re-export + dialogs
  git commit (B5)
  mkdir legacy && cp phoenix_style.qss legacy/...preretrofit
  (Write) legacy/README.md
  git rm phoenix_style.qss
  git commit (B6)
  (Edit ×3) build.bat — submodule preflight, drop embed_qss invocation, drop add-data, add --collect-all
  git rm tools/embed_qss.py
  git commit (B7)
  git push origin phase-3a-phoenix-cad-retrofit

Source-mode validation
  compileall (-x commons|build|dist|.venv) → exit 0
  python -c "<import + identity + contract checks>" → all pass
  QT_QPA_PLATFORM=offscreen python -c "<apply_dark_theme smoke + widget construction>" → green
  QT_QPA_PLATFORM=offscreen python -c "import app" → green
  git submodule SHA = commons main HEAD → match
  cd phoenix-commons && pytest -q tests/ → 91/91 pass

Report
  (Write) docs/ui-platform-baseline-v1/PHASE_3A_PHOENIX_CAD_REPORT.md  ← this file
```

That's the entire surface.

## STOP

Phase 3A complete. Phoenix CAD pilot retrofit landed on
`phase-3a-phoenix-cad-retrofit` (not yet merged to `master`). All
contract checks green; visible parity preserved by construction;
BrandProfile mechanism proven end-to-end with both default + override
paths.

Per the phase spec, **DO NOT** continue into:

- Phoenix Checkout retrofit (Phase 3B)
- Phoenix Command Center retrofit (Phase 3C)
- ValveMaster retrofit (Phase 8a)
- Job Tracker retrofit (Phase 8b)
- Frozen verification
- Installer testing
- Release work

No code change resumes without explicit phase approval per
`BASELINE.md` stop conditions.

Awaiting user direction on:
- Phase 3A retrofit-PR merge approval (squash + `--no-ff` per MIGRATION_RULES.md)
- Phase 3B (Phoenix Checkout) start approval
- The 4 operational follow-ups noted in § 15 (CI submodule init, MIGRATION_RULES doc-drift, pre-retrofit tag, etc.)
