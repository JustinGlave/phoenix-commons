# PHASE_3C_PCC_RETROFIT_AND_VISUAL_IMPLEMENTATION_REPORT.md

> Phase 3C — Phoenix Command Center retrofit + BrandProfile
> implementation. First identity-sensitive retrofit; first use of
> the ADR-016 BrandProfile mechanism in a consuming app; first
> alignment of a PCC-class tool to the FROZEN_BUILD_BASELINE.md
> hardened-build doctrine.
>
> Authored 2026-05-20.
>
> **Outcome: SUCCESS** — PCC now consumes phoenix-commons via
> submodule + editable install, applies commons base + PCC's
> custom orange + teal BrandProfile + a PCC-specific chrome overlay,
> and its build.bat enforces the Python 3.12 + hardening baseline.
> Visual polish work + paths.py / updater.py facade retrofits are
> deferred to follow-up sessions.

## 1. Retrofit inventory

### Commons-API gap inventory

| Symbol | Commons equivalent | PCC retrofit treatment |
|--------|--------------------|--------------------------|
| `theme.C` (24 keys) | `phoenix_commons.theme.tokens.C` (9 keys) | Cannot direct-swap — commons C has 9 keys; PCC has 24. **Preserved PCC's C dict at pre-retrofit shape**; brand-slot keys (`accent`, `teal`, `teal_dark`) now reference `PCC_BRAND` so the BrandProfile flows through; chrome keys (`bg`, `surface`, `sidebar`, `card`, `card_hover`, `card_sel`, `border`, etc.) remain PCC-app-specific because they describe object names commons does not carry. Per MIGRATION_RULES § "Drift-vs-extension heuristic" — extension, not duplication. |
| `theme.make_qss()` | `phoenix_commons.theme.apply_dark_theme()` (whole pipeline) | **Hybrid**: commons `apply_dark_theme` installs the canonical base; PCC's `make_qss()` is preserved as an *overlay* (returned at the bottom of theme.py, unchanged). `apply_pcc_theme()` chains both. |
| `paths.py` (`is_frozen`, `user_data_dir`, `resource_path`) | `phoenix_commons.paths.{is_frozen, user_data_dir, resource_path}` | **NOT retrofitted this phase.** PCC's `paths.py` is already mirror-shaped (its own docstring states "Mirrors phoenix_commons.paths shape so a future migration to the commons-backed standard is a near-zero source change"). Facade retrofit deferred. |
| `updater.py` (`check_for_update`, `download_and_apply`, `UpdateInfo`) | `phoenix_commons.updater.{check_for_update, download_and_apply, UpdateInfo}` | **NOT retrofitted this phase.** PCC's `updater.py` uses full-folder payload contract (matching commons default). Facade retrofit deferred. |
| PCC widget set (`SidebarToolWidget`, `SidebarSprite`, `ToolCard`, etc.) | None — these are PCC-app-specific UI components | **No retrofit needed.** No commons equivalents; not duplications. |
| Standard widgets used in dialogs (raw QPushButton, QLabel, QListWidget, etc.) | `phoenix_commons.widgets.{PrimaryButton, SecondaryButton, etc.}` | **NOT retrofitted this phase.** PCC mostly uses raw Qt widgets with QSS object-name styling rather than commons widget classes. Widget migration is a separate UX evolution decision; not required for retrofit. |

### Visual divergence inventory

| Property | PCC pre-retrofit | Commons canonical (System A) | Post-retrofit |
|----------|-------------------|--------------------------------|----------------|
| Canvas background | `#18181F` (darker purple-gray) | `#0a0e27` (dark navy) | **Hybrid**: commons base installs `#0a0e27` for production-tool widgets (dialogs, dropdowns, menus, file tree); PCC chrome (sidebar, tool cards) retains `#18181F` via overlay. Visible result: deep purple-gray PCC chrome floating on commons' navy edges where dialogs/menus appear. |
| Surface | `#21212E` | `#141829` | Same hybrid pattern. |
| Primary brand | Phoenix orange `#E8783C` | red `#dc2626` | **PCC orange preserved via PCC_BRAND.primary** (sentinel substitution into commons QSS). |
| Secondary | teal_dark `#2A8880` | deep blue `#1e3a8a` | **PCC teal_dark preserved via PCC_BRAND.secondary**. |
| Accent | teal `#3CB8AE` | blue `#3b82f6` | **PCC teal preserved via PCC_BRAND.accent**. |
| Text | `#E4E4F0` (off-white) | `#ffffff` | PCC's off-white preserved in chrome; commons widgets use pure white. |
| Font | "Segoe UI" 13px (in QSS) | "Segoe UI" 11pt (in QSS) | PCC's app-level `QFont("Segoe UI", 10)` set in main.py governs the base; commons + PCC QSS layer applies size + family per selector. |

### BrandProfile dependency inventory

PCC declares **one** `BrandProfile` instance:

```python
PCC_BRAND = BrandProfile(
    primary="#E8783C",   # Phoenix orange
    secondary="#2A8880",  # teal_dark
    accent="#3CB8AE",    # teal
)
```

Used by:
- `apply_pcc_theme(app)` — passes to `commons.apply_dark_theme(app, brand=PCC_BRAND)`.
- `theme.C["accent"]`, `theme.C["teal"]`, `theme.C["teal_dark"]` — sourced from PCC_BRAND so a future profile change ripples through every PCC widget call site without per-file edits.

### Runtime packaging inventory

| Item | Pre-retrofit | Post-retrofit |
|------|---------------|----------------|
| Python contract | (not enforced) | **Python 3.12.x** enforced at build.bat preflight per FROZEN_BUILD_BASELINE.md |
| PyInstaller pin | 6.20.0 (requirements-dev.txt) | unchanged ✓ already aligned |
| PySide6 pin | 6.10.2 (requirements.txt) | unchanged ✓ already aligned |
| Commons submodule | none | `commons/` submodule + `-e ./commons` in requirements.txt |
| Build cleanup | none | `rmdir /s /q build dist` at Step 0 |
| `--noupx` | implicit (spec generated upx=True; UPX not on PATH → no-op) | **explicit `--noupx` flag** |
| stdlib `--exclude-module` | none | 8 modules (tkinter family, lib2to3, idlelib, turtle, turtledemo) |
| `--collect-all=phoenix_commons` | n/a | added — bundles commons package data (phoenix_style.qss, icons SVGs, embedded_qss.py) |
| Preflight Python version check | none | **hard ERROR** if not 3.12.x, with explicit recovery instructions |
| Preflight submodule check | none | **hard ERROR** if commons not populated |
| Preflight phoenix_commons import check | none | **hard ERROR** if `phoenix_commons` not importable |

### Updater-contract inventory

PCC's `updater.py` (still local; not retrofitted this phase) uses the **full-folder payload contract** (`expected_internal=True` default) — same as Job Tracker + Phoenix CAD. This is the commons default; no contract divergence.

## 2. BrandProfile integration details

First production use of the ADR-016 controlled accent-override
mechanism in a consuming app.

### Architecture flow

```
main.py
  └── apply_pcc_theme(app)              [theme.py]
       ├── commons.apply_dark_theme(app, brand=PCC_BRAND)
       │     └── Fusion style + locked QPalette + commons QSS
       │         with __BRAND_PRIMARY__   → "#E8783C"
       │              __BRAND_SECONDARY__ → "#2A8880"
       │              __BRAND_ACCENT__    → "#3CB8AE"
       └── app.setStyleSheet(commons_qss + "\n\n" + pcc_overlay)
             └── PCC overlay adds QFrame#sidebar, #topbar,
                 #toolCard, #statCard, #sectionHeader, status badges,
                 file tree, etc. — object names commons doesn't carry.
```

### Sentinel substitution chain (verified)

Commons's `phoenix_style.qss` carries `__BRAND_PRIMARY__`,
`__BRAND_SECONDARY__`, `__BRAND_ACCENT__` sentinels. `apply.py`'s
`_substitute_brand()` replaces them with the active `BrandProfile`'s
hex values at apply time. With `PCC_BRAND`:

- Anywhere commons QSS used `__BRAND_PRIMARY__` (e.g. focus rings on
  buttons) now uses Phoenix orange.
- Anywhere it used `__BRAND_SECONDARY__` (e.g. button hover chrome)
  now uses teal_dark.
- Anywhere it used `__BRAND_ACCENT__` (e.g. selection highlights,
  link colour) now uses teal.

PCC's existing C dict keys (`accent`, `teal`, `teal_dark`) reference
the same `BrandProfile` slots, so PCC's own QSS overlay stays in sync.

### Locked tokens (not overridable per ADR-016)

PCC does NOT attempt to override:

- `BG`, `SURFACE`, `SURFACE_ALT` (locked by ADR-016)
- `TEXT`, `MUTED` (locked)
- `SUCCESS`, `WARNING`, `ERROR` (locked)

PCC's overlay defines its OWN values for `#bg`, `#surface`, etc. via
its chrome-specific object names — but it doesn't override commons's
QPalette settings or commons QSS for production-tool widgets. Each
acts on a different selector scope.

## 3. Visual-system changes

### Implemented this phase

| Change | Effect |
|--------|--------|
| Commons base QSS installed at QApplication level | Production-tool widgets (QPushButton, QTreeView, QMenu, QComboBox, QScrollBar, etc.) now match the canonical Phoenix System A look. |
| PCC orange + teal brand slots active via PCC_BRAND | Focus rings, selection highlights, link colour use PCC's brand instead of commons' default red + blue. |
| PCC chrome overlay layered on top | PCC's sidebar, top bar, tool cards, status badges, file viewer tree retain their pre-retrofit visual identity. |
| Build.bat enforces frozen-build baseline | Future PCC frozen builds use Python 3.12 + hardening flags = S1-safe. |

### NOT implemented this phase (deferred to follow-up)

| Change | Why deferred |
|--------|--------------|
| Layout polish (spacing, hierarchy, density) | Open-ended UX work; benefits from human design review rather than unilateral changes |
| Sidebar visual evolution | Requires UX direction |
| Dashboard density tuning | Open-ended |
| Installer wizard artwork | INSTALLER_NOTES.md § "Wizard artwork" lists this as future polish; requires brand-design work |
| Splash / identity surfaces | Out of retrofit scope |
| Navigation feel changes | UX review needed |
| Widget migration from raw Qt to commons widgets | Each migration is a UX decision (e.g. should PCC's "Open in Editor" button use PrimaryButton or stay ghostBtn?) |

## 4. Commons integration details

### Submodule

| Item | Value |
|------|-------|
| Path | `commons/` |
| URL | `https://github.com/JustinGlave/phoenix-commons.git` |
| Pinned SHA | `0444bb6` (DOC_CLEANUP_REPORT_PHASE_6D commit at time of pin; will bump as commons evolves) |
| Editable install line | `-e ./commons` in `requirements.txt` after the PySide6 pins |
| `.gitmodules` | 3 lines, standard layout |

### Imports added to PCC source

- `theme.py`:
  - `from phoenix_commons.theme import apply_dark_theme as _commons_apply_dark_theme`
  - `from phoenix_commons.theme.tokens import BrandProfile`
- `main.py`:
  - `from theme import apply_pcc_theme` (which transitively imports the commons symbols above)

Nothing else in PCC source imports from phoenix_commons. The retrofit
surface is minimal — theme is the only PCC subsystem currently
consuming commons.

## 5. Runtime / build alignment changes

### `build.bat`

Major preflight + flag additions documented in § 1 "Runtime packaging
inventory". Specifically:

1. Submodule existence check (`commons\src\phoenix_commons\__init__.py`
   must exist).
2. Python 3.12 build-venv enforcement (`if not "%PYVER%"=="3.12"`).
3. `phoenix_commons` importability check.
4. `rmdir /s /q build dist` deterministic cleanup at Step 0.
5. `--noupx` flag.
6. 8 stdlib `--exclude-module` flags.
7. `--collect-all=phoenix_commons` for commons package data bundling.

The build.bat now enforces FROZEN_BUILD_BASELINE.md mechanically;
running it under a 3.13/3.14 venv produces an explicit error message
with recovery instructions, not a quarantined exe.

### `requirements.txt`

Added `-e ./commons` line. PySide6 6.10.2 pin preserved.

### `requirements-dev.txt`

Already pinned `pyinstaller==6.20.0` (pre-retrofit); no change needed.

### No frozen-build attempted in this phase

Per Phase 3C spec ("Do NOT perform release deployment yet"), the
build.bat changes are STATIC alignment work. No PyInstaller run was
attempted as part of this report. When the next frozen build is
attempted, the build.bat will enforce the baseline at preflight.

## 6. Validation results

### Static checks (all green)

| Check | Result |
|-------|--------|
| `compileall -q -x '\.venv\|commons\|build\|dist\|__pycache__'` | ✓ clean |
| Smoke import of `theme` | ✓ |
| Smoke import of `main_window` | ✓ |
| `theme.PCC_BRAND.primary == "#E8783C"` | ✓ |
| `theme.PCC_BRAND.secondary == "#2A8880"` | ✓ |
| `theme.PCC_BRAND.accent == "#3CB8AE"` | ✓ |
| `theme.C["accent"] == theme.PCC_BRAND.primary` (sentinel chain) | ✓ |
| `isinstance(theme.PCC_BRAND, BrandProfile)` | ✓ |
| `theme.PCC_BRAND != DEFAULT_BRAND` (override active) | ✓ |
| Venv versions: Python 3.12.10 / PyInstaller 6.20.0 / PySide6 6.10.2 / phoenix_commons 0.1.0 | ✓ all aligned |

### Source-mode launch (MIGRATION_RULES § 10 row 11 — actual launch gate)

| Stage | Result |
|-------|--------|
| `pythonw main.py` (background launch) | ✓ spawned PID 56868 |
| T+6 s | ✓ ALIVE, WS 14.4 MB |
| T+10 s | ✓ ALIVE, WS 14.4 MB |
| Termination via `Stop-Process` | ✓ clean |

Process survived 10+ seconds without crash, exception, or
quarantine. Memory consistent with PyQt initialization complete.

### Build.bat preflight verification (without running PyInstaller)

| Preflight check | Behavior |
|-----------------|----------|
| Commons submodule present | ✓ would pass (commons populated) |
| Python 3.12 build venv | ✓ would pass (`.venv` is Python 3.12.10) |
| `phoenix_commons` importable | ✓ would pass (verified directly) |

Build.bat preflight will accept the current environment when invoked.

## 7. Visual review findings

**Not captured in this phase** — operator-driven visual review with
before/after screenshots is the right next step, per Phase 3C spec § 6
"Visual Review". This report's author cannot reliably interact with the
PCC GUI at runtime through the available tooling; the source-mode
launch test confirms the app starts and the theme apply chain runs,
but qualitative visual review (does it FEEL like the flagship
application?) requires Justin's eyes.

What CAN be said now from the architecture:

| Question | Architectural answer |
|----------|----------------------|
| Does PCC feel like the canonical platform owner? | The base theme is now commons + PCC brand; the structural ingredients are in place. Visual polish (spacing, hierarchy) is the next layer that would crystallize this. |
| Does PCC feel like the flagship application? | The brand + base alignment ARE the foundation; remaining work is wide-area polish + identity surfaces (splash, About dialog branding, installer artwork). |
| Does PCC feel like the visual reference implementation? | Architecturally yes (it's the first BrandProfile + commons-overlay pattern); presentationally requires the deferred polish. |

Recommendation: Justin should run `python main.py` on the
`phase-3c-pcc-retrofit` branch and capture screenshots of:

- Main window dashboard
- A tool-card hover state
- Settings dialog
- About dialog
- File viewer tree
- Any context menu

Compare against pre-retrofit screenshots (would need to be captured
from `git stash` of pre-retrofit state, or against the
`main` branch). Document findings in a follow-up `PHASE_3C_VISUAL_REVIEW_REPORT.md`.

## 8. Remaining drift

### Intentional, preserved

| Item | Why intentional |
|------|------------------|
| PCC canvas background `#18181F` (vs commons `#0a0e27`) | PCC is the management/scaffolding app; intentionally distinct from deployed production-tool look |
| PCC text `#E4E4F0` (vs commons `#ffffff`) | Same — slightly off-white for management-app feel |
| PCC chrome object names (#sidebar, #toolCard, etc.) | Extensions, not duplications — commons doesn't carry these |
| PCC widget set largely raw Qt + object-name styling (not commons widget classes) | PCC's UX patterns differ from production tools (e.g. tool cards aren't PrimaryButtons); migration is opt-in not retrofit-required |
| `theme.C` dict shape (24 keys vs commons C 9 keys) | PCC chrome needs the additional semantic colour names; commons C kept minimal per ADR-016 |

### Unintentional, deferred-to-followup

| Item | Why deferred |
|------|--------------|
| `paths.py` not yet a commons facade | Already mirror-shaped per its own docstring; facade is mechanical; defer to keep this phase scoped |
| `updater.py` not yet a commons facade | Functional + uses correct full-folder contract; facade is mechanical; defer |
| Visual polish (spacing/hierarchy/density) | Open-ended UX work; defer to operator-driven review |
| Installer wizard artwork (Inno Setup `WizardImageFile`) | INSTALLER_NOTES.md tracks this as future polish; design work needed |
| About dialog branding | Could surface PCC + commons + brand info; defer to UX cycle |

## 9. Remaining blockers

**None blocking Phase 3C completion.** All blockers are
implementation-scope choices for follow-up phases:

| Item | Severity |
|------|----------|
| Paths/updater facade retrofits | None — current local copies work |
| Visual polish | None — basic retrofit is functional |
| Frozen build smoke (Phase 6C-style end-to-end PCC build) | None — would validate the build.bat alignment; deferred to authorized follow-up |
| BrandProfile changes triggering visual regressions in commons widgets we haven't manually inspected | Low — sentinel substitution is purely additive (no commons widget breaks because the brand changed; only chrome appearance changes) |

## 10. Recommended next implementation priorities

In order of value / effort:

| # | Priority | Effort | Value |
|---|----------|--------|-------|
| **R1** | Operator-driven visual review (run PCC on retrofit branch; capture before/after screenshots; produce `PHASE_3C_VISUAL_REVIEW_REPORT.md`) | Low (interactive session) | HIGH — confirms BrandProfile + chrome overlay landed correctly |
| **R2** | Frozen-build smoke of PCC under the new build.bat (Phase 6C-A pattern but for PCC) | Medium (1 build run, observe) | HIGH — validates build.bat hardening end-to-end on PCC specifically |
| **R3** | Merge `phase-3c-pcc-retrofit` to `main` if R1+R2 green | Low | Codifies the retrofit |
| R4 | paths.py → commons facade | Low | Cleanup; pattern-matched to Phase 3A/3B style |
| R5 | updater.py → commons facade (split download/apply if needed) | Medium | Cleanup; PCC could become first commons-updater consumer |
| R6 | Visual polish pass (spacing, hierarchy, dashboard density) | Medium | UX evolution per Phase 3C spec |
| R7 | Installer wizard artwork (Phoenix orange + teal navy bg) | Medium-High (design) | Brand coherence |
| R8 | About dialog branding refresh | Low | Surfaces PCC's flagship identity |

R1 and R2 are the immediate logical successors. R3 follows naturally
after both clear. R4–R8 are sustained UX work that can interleave with
other phase work.

## 11. Confirmation

| Item | Status |
|------|--------|
| No production tools touched | ✅ |
| No production tool source modified | ✅ |
| No production deployment occurred | ✅ |
| No production rebuilds occurred | ✅ |
| No AV bypass behavior | ✅ |
| No security controls disabled | ✅ |
| No obfuscation introduced | ✅ |
| No frozen build attempted (build.bat aligned but not executed) | ✅ |
| No releases | ✅ |
| Branch preserved on origin (`phase-3c-pcc-retrofit`) | ✅ |
| Commons API unchanged (no commons-side commits this phase) | ✅ |
| ADR-016 BrandProfile mechanism used as designed (sentinel substitution only) | ✅ |
| Locked tokens (BG/SURFACE/TEXT/MUTED/status colours) preserved | ✅ |
| Identity-equal widget verification (where commons widgets are now in play) | n/a — PCC didn't swap widget classes this phase |

## 12. Sign-off

| Field | Value |
|-------|-------|
| Phase | Phase 3C — Phoenix Command Center retrofit + BrandProfile + visual-system implementation |
| Outcome | **SUCCESS** (foundation work) |
| Status | ✅ Complete (retrofit foundation); visual polish deferred to R1+R6 |
| Date | 2026-05-20 |
| Branch | `phase-3c-pcc-retrofit` on `phoenix-command-center` origin |
| Commits in this phase | 5 on PCC + 1 (this report) on commons |
| — PCC `67fc294` | B1: commons submodule |
| — PCC `03483bf` | B1a: requirements.txt += `-e ./commons` |
| — PCC `c4463d5` | B2: theme.py retrofit (BrandProfile + apply_pcc_theme) |
| — PCC `1451513` | B3: main.py wires apply_pcc_theme |
| — PCC `a08214a` | B4: build.bat aligned to FROZEN_BUILD_BASELINE |
| — commons | (this report) |
| Files modified in production-tool repos | 0 |
| Files modified in PCC | 5 (`.gitmodules`, `commons` (submodule), `requirements.txt`, `theme.py`, `main.py`, `build.bat`) — all on retrofit branch |
| Files modified in commons | 1 (this report) |
| Merge state | branch preserved on origin; **NOT merged**; awaits R1+R2 validation |
| ADR-016 first production use | ✅ this phase |
| FROZEN_BUILD_BASELINE first production-class adoption | ✅ this phase |
| Saved to | `phoenix-commons/docs/ui-platform-baseline-v1/PHASE_3C_PCC_RETROFIT_AND_VISUAL_IMPLEMENTATION_REPORT.md` |
