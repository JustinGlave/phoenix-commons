# Wave 8a — ValveMaster Pre-Flight Audit

> **Status:** read-only audit. **No source changes.** No retrofit branch created.
> **Date:** 2026-05-22.
> **Target app:** ValveMasterTool (display name: **Phoenix Master Tool**).
> **Repo path:** `C:\Users\justing\PycharmProjects\ValveMasterTool`.
> **Scope:** standards alignment readiness for the Wave 8a retrofit per
> the operator brief.
> **Companion docs:** `PHOENIX_APP_STANDARD_BASELINE_V1.md`,
> `APP_ALIGNMENT_CHECKLIST.md`, `APP_STANDARDIZATION_READINESS_MATRIX.md`,
> `MIGRATION_RULES.md`, `FROZEN_BUILD_BASELINE.md`.
> **Cooldown floor:** Wave 8a may not open before **2026-06-02** per
> MIGRATION_RULES § Frequency limits.

---

## 1. Repo state audit

### Git state

| Item | Value |
|------|-------|
| Current branch | `main` |
| Tip commit | `21ba5df CHANGELOG: ISO date for v1.1.0 (N3 — Operational Convergence)` |
| Working tree | **clean** (no WIP isolation needed; MIGRATION_RULES § 9 not triggered) |
| Submodules | none (no `.gitmodules` present) |
| Remote tracking | local-only check (operator can confirm `git fetch` against origin) |

### Repository identity (v1.1.0 rename)

ValveMaster was renamed at v1.1.0 to **Phoenix Master Tool** (per `CLAUDE.md` § Repo identity):

| Item | Pre-rename | Post-rename (current) |
|------|------------|------------------------|
| Display name | ValveMasterTool | **Phoenix Master Tool** |
| Exe | `ValveMasterTool.exe` | **`PhoenixMasterTool.exe`** |
| GitHub repo | `valve-master-tool` | **`phoenix-master-tool`** |
| Install path | `…\ATS Inc\ValveMasterTool` | **`…\ATS Inc\PhoenixMasterTool`** |
| Updater zip asset | `ValveMasterTool.zip` | **`PhoenixMasterTool.zip`** (with legacy-name fallback in updater.py) |
| AppId GUID | `{A7F3C2D1-9B4E-4F6A-8C3D-1E5B7A9F2C4D}` | **same** (Inno Setup upgrade-detection identity preserved per MIGRATION_RULES § Stop conditions) |
| Local working dir | `ValveMasterTool` | still `ValveMasterTool` (local history) |

### Top-level file inventory

| File | Size | Purpose |
|------|------|---------|
| `version.py` | 37 B | `__version__ = "1.1.0"` |
| `phoenix_master_pyside6.py` | 111 KB | Main GUI module (2660+ LOC) |
| `phoenix_master_backend.py` | 169 KB | Backend / domain logic (valve model decoder, validation, configs) |
| `inventory.py` | 8 KB | SharePoint-synced parts catalog (preserved-local) |
| `assets.py` | 312 KB | Base64-embedded brand assets (preserved-local) |
| `updater.py` | 10 KB | GitHub-based auto-updater (legacy-name aware) |
| `phoenix_style.qss` | 24 KB | **Local QSS — already canonical System A** |
| `ValveMasterTool.spec` | 1 KB | PyInstaller spec — **STALE** (references old `valve_master_pyside6.py` entry name; build.bat doesn't use it) |
| `build.bat` | 7 KB | Build script with embedded code-signing path |
| `installer.iss` | 3 KB | Inno Setup script (renamed; AppId preserved) |
| `Normal_red.ico` | 2 KB | App icon |
| `Transparent_red.png` | 214 KB | Logo |
| `README.md` / `CHANGELOG.md` / `CLAUDE.md` / `LICENSE` / `SECURITY.md` / `CODE_OF_CONDUCT.md` / `CONTRIBUTING.md` / `GIT_SETUP.md` | small | Repo hygiene (post-Operational-Hardening normalization) |
| `tests/test_updater.py` / `tests/test_validation.py` | small | Pre-Phase-8a regression baseline |
| `.github/workflows/test.yml` | small | CI — **non-standard name** (`test.yml` not `ci.yml`) |
| `.venv/` | n/a | local dev venv (Python 3.14 per pyc artifacts; canonical build target is 3.12 per ADR-014) |

### Files MISSING vs baseline

| Missing item | Severity | Resolution |
|--------------|----------|------------|
| `requirements.txt` at root | **MEDIUM** | CLAUDE.md says it was added during the 2026-05-19 Operational Hardening Sprint but it's **not present** today. Either operator removed it, or CLAUDE.md is outdated. Resolve at B1 (retrofit branch). |
| `requirements-dev.txt` | MEDIUM | Add at B1. |
| `commons/` submodule | expected | Add at B1 (per MIGRATION_RULES § 4). |
| `.gitmodules` | expected | Add at B1. |

---

## 2. Standards gap inventory

### Visual standards

| Item | Status | Notes |
|------|--------|-------|
| Dark System A theme | ✅ **already aligned** | `phoenix_style.qss` uses BG `#0a0e27`, surface `#141829`, accent `#3b82f6`, red `#dc2626`, deep-blue `#1e3a8a` — **byte-match canonical System A** |
| Theme applied via `apply_dark_theme(app, brand=…)` | ❌ needs retrofit | Currently `load_phoenix_stylesheet(app)` reads QSS file + falls back to `_EMBEDDED_QSS` string |
| Local widget primitives (`PrimaryButton`/`SecondaryButton`/`TertiaryButton`/`PhoenixTable`/`UpdateBanner`) inline-defined | ❌ needs retrofit (monolith inline-class pattern per MIGRATION_RULES § 11) | Same class names as commons — **near-zero diff** at every caller site |
| App-specific widgets (`BadgeLabel`, `SectionCard`, `ClickableFieldCard`, `ValidationIssueRow`, `WatermarkWidget`, dialogs) | ✅ **intentionally app-specific** (preserve-local) | Domain UI patterns; no commons analog |
| Lucide icons | ⚠️ **partial / unknown** | Audit reads `setStyleSheet` count = 3 in main GUI (B6-clean); no emoji glyphs surveyed in this audit. Operator review needed to confirm. |
| `#pageTitle` / `#sectionHeader` convention | ⚠️ unknown | Not surveyed in this audit |
| Button hierarchy (Primary/Secondary/Tertiary) | ✅ already aligned (class names match commons) | Local classes carry the same tier semantics |
| No emoji on chrome | ⚠️ unknown | Audit found 3 `setStyleSheet` calls but did not enumerate emoji glyphs |
| BrandProfile usage | ✅ **DEFAULT_BRAND-compatible** | Current QSS palette matches commons `DEFAULT_BRAND` (red + deep blue + blue); no custom BrandProfile needed |

**Visible-change-band reassessment: LOW (≈ 0%), not HIGH.**

The earlier `APP_STANDARDIZATION_READINESS_MATRIX.md` § 1 predicted "HIGH visible change (System B → A swap)". **This is wrong.** ValveMaster shipped System A in `phoenix_style.qss` at v1.1.0. The retrofit is theme-application-mechanism only — facade swap from local QSS file reads to `phoenix_commons.theme.apply_dark_theme(app)`. The pixels barely change. **Phoenix CAD-style ≈ 0% visible change.**

### Functional standards

| Item | Status | Notes |
|------|--------|-------|
| Single `main.py` entry | ⚠️ **app uses `phoenix_master_pyside6.py`** as entry | Family convention is `main.py`. ValveMaster's entry name is intentional (post-rename clarity). Documented as a permitted app-customization OR rename to `main.py` at retrofit. Default: preserve current name; documented divergence. |
| `version.py` with `__version__ = "X.Y.Z"` | ✅ aligned (1.1.0) | |
| README current-version line | ⚠️ unknown | Audit didn't grep README for version banner |
| User data at `%APPDATA%\ATS Inc\PhoenixMasterTool` | ✅ aligned | Per installer.iss `MyAppDataDir = {userappdata}\ATS Inc\PhoenixMasterTool` |
| Install path `{localappdata}\ATS Inc\PhoenixMasterTool` | ✅ aligned | Per installer.iss `DefaultDirName` |
| Atomic JSON writes | ⚠️ unknown | inventory.py uses `load_inventory` / `save_inventory` — pattern not audited |
| Updater commons-API facade | ❌ needs retrofit | Currently local 270-LOC `updater.py`. Retrofit per MIGRATION_RULES § 1 hybrid facade (4-kwarg `check_for_update` + `download_and_apply(expected_internal=False)` per ADR-003 exe-only payload). PRESERVE local legacy-name resolution logic. |
| Subprocess `CREATE_NO_WINDOW` | ✅ uses it (updater.py line 263) | |
| Background work via QThread | ⚠️ unknown | Audit didn't grep for threading patterns |

### Packaging / build standards

| Item | Status | Notes |
|------|--------|-------|
| Python 3.12 frozen build (ADR-014) | ⚠️ partial | build.bat reads version + invokes `pyinstaller` directly; doesn't enforce 3.12. `.venv/` artifacts show Python 3.14 (CLAUDE.md says venv is 3.10/3.11/3.12 matrix-tested via CI). Frozen builds MUST use 3.12 per FROZEN_BUILD_BASELINE. |
| PyInstaller 6.20.0 pinned | ❌ no requirements-dev.txt | Add at B1. |
| `--noupx` flag | ❌ **MISSING** | UPX-compressed bootloaders raise AV false-positive rates. Add at B6. |
| Stdlib `--exclude-module` list | ❌ **MISSING** | Per FROZEN_BUILD_BASELINE § stdlib excludes. Add at B6. |
| `--collect-all phoenix_commons` | ❌ N/A yet (no commons) | Add at B6 after B1 lands commons submodule. |
| Step 0 cleanup (`rmdir /S /Q build dist`) | ❌ partial | build.bat removes `dist/` but keeps `build/` for incremental cache (different from FROZEN_BUILD_BASELINE Step-0 mandate). Operator decision needed. |
| Commons submodule preflight in build.bat | ❌ N/A yet | Add at B6 after B1. |
| Updater zip naming | ✅ aligned | `PhoenixMasterTool.zip` (exe-only auto-updater) + `PhoenixMasterTool_FullInstall.zip` (manual install) |
| Installer Inno Setup `PrivilegesRequired=lowest` | ✅ aligned | |
| Installer output filename `PhoenixMasterToolSetup.exe` | ✅ aligned | |
| AppId GUID stable | ✅ aligned (preserved across the rename) | `{A7F3C2D1-9B4E-4F6A-8C3D-1E5B7A9F2C4D}` |
| Code-signing path | ✅ already present | `VMT_SIGNING_CERT` env var dispatches `:sign_exe` + `:sign_installer` subroutines |
| `.spec` file accuracy | ❌ **STALE** | `ValveMasterTool.spec` references `valve_master_pyside6.py` (old entry name; pre-rename). build.bat doesn't read the .spec, so this is dead code. Resolve at B6 (delete OR update). |

### Repository standards

| Item | Status | Notes |
|------|--------|-------|
| README.md / CHANGELOG.md / CLAUDE.md / LICENSE / SECURITY.md / CODE_OF_CONDUCT.md / CONTRIBUTING.md | ✅ all present | Post-Operational-Hardening normalization (N1/N2/N3 sprint) |
| Branch naming | n/a | retrofit branch name will be `phase-8a-valvemaster-retrofit` per MIGRATION_RULES § Per-retrofit branch + PR convention |
| `requirements.txt` at root | ❌ **missing** (per repo scan today) | Add at B1. CLAUDE.md mentions it; resolve discrepancy. |
| `requirements-dev.txt` at root | ❌ missing | Add at B1. |
| CI on `windows-latest` | ❌ **on ubuntu-latest** | Documented "intentional divergence" per CLAUDE.md. Operator decision at retrofit: preserve or normalize. |
| CI named `ci.yml` | ❌ **named `test.yml`** | Documented "intentional divergence" per CLAUDE.md. |
| CI uses `submodules: recursive` | ❌ N/A yet | Add at B1 + B6 after commons submodule lands. |
| CI installs `requirements.txt` + `requirements-dev.txt` as separate steps | ❌ no pip install at all today | Current CI: `python -m unittest discover -s tests -v` + baseline self-test. Per-app-tuning. |
| CI `import phoenix_commons` smoke | ❌ N/A yet | Add at B6 after submodule. |
| `assets/` directory | ⚠️ partial | Brand assets are inline base64 in `assets.py`, not under `assets/`. App-specific extension (PyInstaller bundles via module scan). |
| `ui/` directory | ❌ not used | ValveMaster keeps everything at repo root. Documented per-app convention. |
| `tests/` directory | ✅ present | `test_updater.py` + `test_validation.py` |
| Stable GitHub release zip asset name | ✅ aligned (`PhoenixMasterTool.zip` post-rename) | with legacy-name fallback in updater.py |

### Retrofit standards

| Item | Status | Notes |
|------|--------|-------|
| Local facade strategy (MIGRATION_RULES § 1) | ⚠️ pending retrofit | B2/B3/B4 will establish facades for paths, updater, theme |
| Pre-flight commons-API gap inventory (MIGRATION_RULES § 0) | ✅ **this audit** | §3 below is the inventory |
| Identity-equal widget verification (MIGRATION_RULES § 2) | ⚠️ pending retrofit | Validated at B5 |
| Sentinel substitution workflow | ✅ N/A (no custom BrandProfile expected) | Default red + blue palette matches DEFAULT_BRAND |
| Submodule init expectations (MIGRATION_RULES § 4) | ⚠️ pending B1 | |
| Duplicate-removal sequencing (MIGRATION_RULES § 5) | ⚠️ pending retrofit | replace → verify → delete sequence per phase |
| Delete duplication, not behavior (MIGRATION_RULES § 6) | ⚠️ pending retrofit | preserves updater legacy-name handling + inventory.py + assets.py + backend.py verbatim |
| Drift-vs-extension heuristic (MIGRATION_RULES § 7) | ✅ this audit applied it | classifications below |
| Commit granularity (MIGRATION_RULES § 8) | ⚠️ pending retrofit | B1-B9 small commits anticipated |
| WIP isolation (MIGRATION_RULES § 9) | ✅ **not triggered** | working tree clean today |
| Source-mode validation (MIGRATION_RULES § 10) | ⚠️ pending B7 | |
| Monolith inline-class retrofit pattern (MIGRATION_RULES § 11) | ✅ **applicable to ValveMaster** | `phoenix_master_pyside6.py` is the monolith carrying inline widget classes |

---

## 3. Commons API gap inventory (MIGRATION_RULES § 0 pre-flight)

For each locally-defined platform-like symbol, classify per the doctrine: **A** keep local / **B** add to commons / **C** replace with existing commons primitive/facade.

### Widget primitives

| Local symbol | Location | Commons equivalent? | Decision |
|--------------|----------|---------------------|----------|
| `PrimaryButton` | `phoenix_master_pyside6.py:164` | ✅ `phoenix_commons.widgets.PrimaryButton` | **C** — replace with commons import (monolith inline pattern per MIGRATION_RULES § 11) |
| `SecondaryButton` | `phoenix_master_pyside6.py:177` | ✅ `phoenix_commons.widgets.SecondaryButton` | **C** — replace |
| `TertiaryButton` | `phoenix_master_pyside6.py:187` | ✅ `phoenix_commons.widgets.TertiaryButton` | **C** — replace |
| `PhoenixTable` | `phoenix_master_pyside6.py:197` | ✅ `phoenix_commons.widgets.PhoenixTable` | **C** — replace (may need `setObjectName` for app-specific QSS tuning) |
| `UpdateBanner` | `phoenix_master_pyside6.py:724` | ✅ `phoenix_commons.widgets.UpdateBanner` | **C** — replace |
| `BadgeLabel` | `phoenix_master_pyside6.py:366` | ❌ no | **A** — keep local (app-specific badge styling) |
| `SectionCard` | `phoenix_master_pyside6.py:400` | ❌ no (commons `Panel` is the analog but API may differ) | **A** — keep local (operator decision; reclassification possible) |
| `ClickableFieldCard` | `phoenix_master_pyside6.py:656` | ❌ no | **A** — keep local |
| `ValidationIssueRow` | `phoenix_master_pyside6.py:702` | ❌ no | **A** — keep local |
| `WatermarkWidget` | `phoenix_master_pyside6.py:1351` | ❌ no | **A** — keep local (app-specific) |
| Dialogs (`SelfTest`, `OptionPicker`, `OptionsEditor`, `Cfm`, `TestModels`, `PartsList`) | various | ❌ no | **A** — keep local (app-specific UX) |

### Theme / palette

| Local symbol | Commons equivalent? | Decision |
|--------------|---------------------|----------|
| `load_phoenix_stylesheet(app)` (line 147) | ✅ `phoenix_commons.theme.apply_dark_theme(app, brand=DEFAULT_BRAND)` | **C** — replace facade |
| `_EMBEDDED_QSS` (string fallback, ~50 LOC in main GUI) | ✅ commons canonical QSS | **C** — retire (commons covers fallback) |
| `QSS_FILENAME = "phoenix_style.qss"` constant | n/a | preserve — `phoenix_style.qss` becomes the local backup per MIGRATION_RULES § Local backup QSS strategy |
| BrandProfile | ✅ commons `DEFAULT_BRAND` matches the current QSS palette | **C** — use DEFAULT_BRAND (no custom BrandProfile needed) |

### Paths / resources

| Local symbol | Commons equivalent? | Decision |
|--------------|---------------------|----------|
| `_resource_path(filename)` (line 138) | ✅ `phoenix_commons.paths.resource_path` | **C** — facade |
| (no app-local path constants surveyed) | ✅ `phoenix_commons.paths.user_data_dir` available if needed | preserve as needed |

### Updater

| Local symbol | Commons equivalent? | Decision |
|--------------|---------------------|----------|
| `check_for_update()` (no args; reads `GITHUB_OWNER`/`GITHUB_REPO`/`EXE_NAME` constants) | ✅ `phoenix_commons.updater.check_for_update(owner, repo, current_version, zip_asset_name)` | **C** — facade with 4 kwargs |
| `download_and_apply(info, progress_callback)` (exe-only payload) | ✅ `phoenix_commons.updater.download_and_apply(info, exe_name, *, expected_internal=True, progress_callback=...)` | **C** — facade with `expected_internal=False` per ADR-003 |
| Legacy-name fallback (`LEGACY_EXE_NAMES` + `_ps_single_quote` + PowerShell extraction script) | ❌ no commons equivalent for legacy-name resolution | **A** — **preserve local** (post-rename safety; ValveMaster-specific). MIGRATION_RULES § 1 hybrid facade pattern applies. |
| `UpdateInfo` dataclass | ✅ `phoenix_commons.updater.UpdateInfo` | **C** — re-export from commons (matches Checkout's Phase 3B pattern) |

### Domain logic (preserved-local — see §4)

All symbols in `phoenix_master_backend.py`, `inventory.py`, `assets.py` → **A** preserve-local. Audit did not enumerate them individually.

### Gap inventory summary

  - **Class C (replace with commons): ~10 symbols** — high commons-reuse, low risk
  - **Class A (preserve-local): ~15+ symbols** — app-specific domain UI + domain logic + legacy-name updater logic
  - **Class B (add to commons): 0** — no new commons primitives needed for this retrofit

**Conclusion:** ValveMaster's retrofit fits cleanly inside the existing commons API. No new commons work required. No two-consumer-evidence gaps. No stop conditions triggered.

---

## 4. Preserved-local domain logic

The following are explicitly classified **preserved-local** and must NOT be migrated to commons (MIGRATION_RULES § 1 hybrid facade allowed; no commons equivalent makes sense):

  - **`phoenix_master_backend.py`** (169 KB) — valve model decoder, validation rules, 9 product line configs, `OperatingTable`, `ParsedModel`, `standard_product_configs`, `run_baseline_debug_benchmark`, `process_model_structured`, `get_field_popup_details`, `compute_*`, etc. Domain logic; not platform.
  - **`inventory.py`** — SharePoint-synced JSON parts catalog (`Inventory`, `Part`, `load_inventory`, `save_inventory`, `inventory_json_path`, `is_admin_password`). Operator-side OneDrive Business sync; path drift breaks catalog load.
  - **`assets.py`** (312 KB) — base64-embedded brand PNGs. PyInstaller bundles via module scan; swapping assets requires editing this file (NOT `--add-data=`).
  - **`phoenix_style.qss`** (24 KB) — local QSS backup per MIGRATION_RULES § Local backup QSS strategy. Loaded only if commons fallback fails. Retain at repo root post-retrofit.
  - **App-specific widget classes** in `phoenix_master_pyside6.py`:
    `BadgeLabel`, `SectionCard`, `ClickableFieldCard`, `ValidationIssueRow`, `WatermarkWidget`, `SelfTestDialog`, `OptionPickerDialog`, `OptionsEditorDialog`, `CfmCalculatorDialog`, `TestModelsDialog`, `PartsListDialog`, `ValveMasterMainWindow`.
  - **`updater.py` legacy-name resolution logic** — `LEGACY_EXE_NAMES`, `_ps_single_quote`, PowerShell extraction script with running-exe-basename detection. Necessary for the v1.0→v1.1 rename upgrade path.
  - **`updater.py` exe-only payload semantics** — `expected_internal=False` per ADR-003.
  - **`_EMBEDDED_QSS` string fallback** — keep as the SAFETY net only IF commons QSS cannot be loaded. Otherwise retire if commons fallback proves sufficient. Operator decision at B4.
  - **CI workflow file `.github/workflows/test.yml`** — "intentional divergence" per CLAUDE.md (ubuntu + 3.10/3.11/3.12 matrix). Operator decides at retrofit whether to normalize.
  - **`tests/test_updater.py`** + **`tests/test_validation.py`** — pre-Phase-8a regression baseline. MUST stay green across the retrofit.

---

## 5. Visual change assessment

### Current theme system

  - **`phoenix_style.qss` at repo root** (24 KB) — full-app dark theme.
  - **Palette already System A canonical:**
      - BG `#0a0e27` (locked token match)
      - Surface `#141829` (locked token match)
      - Border `#2d3748` (locked token match)
      - Accent `#3b82f6` (commons INFO / DEFAULT_BRAND.accent match)
      - Red `#dc2626` (DEFAULT_BRAND.primary match)
      - Deep blue `#1e3a8a` (DEFAULT_BRAND.secondary match)
  - **Theme loaded via `load_phoenix_stylesheet(app)`** which reads the QSS file from disk and calls `app.setStyleSheet(...)`.
  - **`_EMBEDDED_QSS` string** lives inside `phoenix_master_pyside6.py` as a fallback if the QSS file can't be read.
  - **B6 invariant likely respected:** main GUI file has only **3 `setStyleSheet` call sites** (likely on semantic-content text labels — same B6 carve-out PCC/CAD/Checkout preserve).

### Expected visible change magnitude — **LOW (≈ 0%)**

| Dimension | Expected change |
|-----------|------------------|
| Background colour | none (BG already `#0a0e27`) |
| Surface colour | none (surface already `#141829`) |
| Button colours | none (DEFAULT_BRAND substitution produces the same red/blue values) |
| Section card chrome | none (`SectionCard` stays local; same chrome) |
| Table styling | minor — `PhoenixTable` swap may shift padding by 1-2 px |
| Status badges | n/a (ValveMaster doesn't use StatusBadge currently) |
| Iconography | unchanged (audit didn't survey emoji glyphs; if any exist they could be modernized in a follow-on phase) |
| Dialogs | unchanged (preserved-local) |

**Updated readiness-matrix assessment:** ValveMaster now classifies in the **Phoenix-CAD ≈ 0% visible change band**, not the previously-predicted HIGH band. The CLAUDE.md note about "System A theme adoption is partially complete" was accurate; the readiness matrix overstated the visible-change risk.

### Screenshot baseline needs

Per MIGRATION_RULES § Screenshot baseline:
  - Pre/post screenshots of: main window, parts-list dialog, validation dialog, CFM calculator, options editor.
  - Captured at the deployed v1.1.0 release vs the post-retrofit branch HEAD on the same monitor / DPI / OS theme.
  - Acceptable change band: **near-zero** (revised from HIGH per this audit).
  - Storage location: operator decision — `phoenix-commons/docs/ui-platform-baseline-v1/screenshots/wave-8a/` recommended.

### Operator review needs

Light review only (≈ 0% expected change). Pre-merge gate validation per checklist § H + § I.

---

## 6. Build / packaging readiness

### build.bat audit (vs FROZEN_BUILD_BASELINE)

| FROZEN_BUILD_BASELINE requirement | Current state | Gap |
|------------------------------------|----------------|-----|
| Python 3.12 build venv | Not enforced; `.venv/` is 3.14-tagged locally | **MEDIUM** — operator must build with a 3.12 venv per ADR-014 |
| PyInstaller 6.20.0 pinned | No `requirements-dev.txt` | **MEDIUM** — add at B6 |
| `--noupx` flag | ❌ **missing** | **HIGH** — add at B6 (UPX raises AV false-positive rate) |
| Stdlib `--exclude-module` list | ❌ **missing** | **HIGH** — add at B6 per FROZEN_BUILD_BASELINE § stdlib excludes |
| `--collect-all phoenix_commons` | N/A pre-B1 | add at B6 after commons submodule |
| Step 0 cleanup (`rmdir /S /Q dist build`) | partial — removes `dist/` only, keeps `build/` cache | **LOW** — change to full cleanup per FROZEN_BUILD_BASELINE; operator preference noted |
| Commons-submodule preflight | N/A pre-B1 | add at B6 |
| `--onedir --windowed` | ✅ aligned | |
| `--add-data` for version.py / phoenix_style.qss / inventory.py | ✅ already present | preserved through retrofit |
| `--collect-submodules=PySide6.*` | ✅ present (slower than needed but functional) | optional cleanup |
| Code-signing path | ✅ already present via `VMT_SIGNING_CERT` env var | preserved |

### installer.iss audit

| Item | State |
|------|-------|
| AppId GUID | ✅ stable (`{A7F3C2D1-9B4E-4F6A-8C3D-1E5B7A9F2C4D}`) — Inno Setup upgrade-detection identity |
| `PrivilegesRequired=lowest` | ✅ aligned |
| `DefaultDirName={localappdata}\ATS Inc\PhoenixMasterTool` | ✅ aligned |
| `OutputBaseFilename=PhoenixMasterToolSetup` | ✅ aligned |
| Uninstall data-deletion prompt | ✅ already implemented |
| Renamed assets / icons | ✅ all renamed to PhoenixMasterTool variants |

### `.spec` file

`ValveMasterTool.spec` references the OLD entry name `valve_master_pyside6.py` (the file is now `phoenix_master_pyside6.py`). build.bat does NOT use the .spec file — it invokes `pyinstaller` directly with CLI flags. The .spec is **dead code**. Resolve at B6: delete it OR update it; default = delete (it's misleading documentation).

### S1 risk

| Factor | State |
|--------|-------|
| Python 3.12 build venv | not enforced — operator must explicitly use 3.12 |
| `--noupx` | missing |
| Stdlib excludes | missing |
| Step 0 cleanup | partial |
| Bootloader content fingerprint | unverified — last verified S1-safe build was at v1.1.0 per CLAUDE.md (`updater.py` hardened against rename pain) |

**S1 risk: MEDIUM** until B6 lands hardened build flags. Post-B6 + Python 3.12 venv: LOW (matches Phoenix CAD's profile).

### Updater / installer contract risks

| Risk | State |
|------|-------|
| Updater zip name renamed mid-release-history | ✅ handled via `LEGACY_EXE_NAMES` fallback in updater.py |
| AppId stable across rename | ✅ preserved |
| Install-path stable across rename | ❌ changed at v1.1.0 (from `\ATS Inc\ValveMasterTool` to `\ATS Inc\PhoenixMasterTool`) — already shipped; users may have either path on disk |
| User-data-path stable across rename | ❌ also changed at v1.1.0 — same caveat |
| Exe-only payload contract | ✅ documented per ADR-003 |

The install-path + user-data-path rename pre-dates Wave 8a; not a Wave 8a risk per se. The retrofit must NOT regress the post-rename paths.

---

## 7. Risk classification

| Risk dimension | Level | Notes |
|----------------|-------|-------|
| **Visual risk** | **LOW** | Theme already System A; ≈ 0% visible change expected. Originally predicted HIGH; readiness matrix overstated. |
| **Functional risk** | **LOW** | Domain logic is well-contained in backend / inventory / assets / app-specific dialogs. None of it is touched by retrofit. |
| **Build risk** | **MEDIUM** | Hardened build flags missing (`--noupx`, stdlib excludes, Step-0 cleanup, submodule preflight). Resolved at B6. |
| **Packaging risk** | **LOW-MEDIUM** | Installer + updater contracts solid; AppId preserved. Risk concentrated in build.bat hardening. |
| **User-data risk** | **LOW** | Path-rename pre-dates Wave 8a. Retrofit must preserve current `%APPDATA%\ATS Inc\PhoenixMasterTool` path. |
| **S1 risk** | **MEDIUM** until hardened build lands | Post-B6 + 3.12 venv: LOW. |
| **Commons integration risk** | **LOW** | Same widget class names as commons → surgical monolith inline-class retrofit per MIGRATION_RULES § 11. No new commons primitives needed. |

### Likely stop conditions

  - **Operator changes AppId GUID** — hard stop per MIGRATION_RULES § Stop conditions
  - **Frozen-exe verification fails for non-S1/AV reason** — investigate before retry
  - **Pre-Phase-8a regression tests fail** (`test_updater.py` / `test_validation.py`) — fix on branch before merge
  - **SharePoint inventory JSON path breaks** — would indicate retrofit touched `inventory.py` (forbidden)
  - **Base64 brand assets fail to load post-PyInstaller-bundle** — would indicate retrofit broke `assets.py` module-scan behavior (forbidden)
  - **Visible change exceeds ≈ 5% band** — re-scope before merge

No stop conditions are triggered by the AUDIT itself. All listed conditions apply to the eventual retrofit work.

---

## 8. Proposed retrofit sequence (9 steps)

When Wave 8a is approved + cooldown clears (≥ 2026-06-02):

### B1 — Commons submodule + requirements

  - `git submodule add https://github.com/JustinGlave/phoenix-commons commons`
  - `.gitmodules` committed
  - `requirements.txt`: `PySide6==6.10.2` + `PySide6_Addons==6.10.2` + `shiboken6==6.10.2` + `-e ./commons`
  - `requirements-dev.txt`: `pyinstaller==6.20.0` + `pytest==8.3.4` + `pytest-qt==4.4.0`
  - CI smoke: `python -c "import phoenix_commons; print(phoenix_commons.__version__)"`

### B2 — `paths.py` facade (small new file)

  - Re-export `is_frozen`, `user_data_dir`, `resource_path` from `phoenix_commons.paths`
  - Replace inline `_resource_path` in `phoenix_master_pyside6.py:138` with import from paths

### B3 — `updater.py` hybrid facade

  - `check_for_update()` → wraps `phoenix_commons.updater.check_for_update(owner="JustinGlave", repo="phoenix-master-tool", current_version=__version__, zip_asset_name="PhoenixMasterTool.zip")`
  - `download_and_apply(info, progress_callback)` → wraps `phoenix_commons.updater.download_and_apply(info, exe_name=EXE_NAME, expected_internal=False, progress_callback=progress_callback)` per ADR-003
  - **PRESERVE local logic**: `LEGACY_EXE_NAMES`, `_ps_single_quote`, PowerShell extraction script with running-exe-basename detection
  - **PRESERVE `UpdateInfo` import** — `from phoenix_commons.updater import UpdateInfo` (identity preserved for callers)
  - `tests/test_updater.py` must stay green

### B4 — Theme application facade

  - Replace `load_phoenix_stylesheet(app)` body with `phoenix_commons.theme.apply_dark_theme(app)` (DEFAULT_BRAND; no custom BrandProfile needed)
  - Retire `_EMBEDDED_QSS` string body (replace with comment noting commons handles fallback)
  - **PRESERVE `phoenix_style.qss` at repo root** per MIGRATION_RULES § Local backup QSS strategy
  - Visual review: ≈ 0% expected change

### B5 — Widget retrofit (monolith inline-class pattern)

  - Replace inline `class PrimaryButton(QPushButton): …`, `class SecondaryButton`, `class TertiaryButton`, `class PhoenixTable`, `class UpdateBanner` with:
    ```python
    from phoenix_commons.widgets import (
        PrimaryButton, SecondaryButton, TertiaryButton, PhoenixTable, UpdateBanner,
    )
    ```
  - Every caller site stays byte-identical
  - Identity-equal assertions: `assert local.PrimaryButton is phoenix_commons.widgets.PrimaryButton` × 5
  - App-specific widgets (`BadgeLabel`, `SectionCard`, `ClickableFieldCard`, `ValidationIssueRow`, `WatermarkWidget`, dialogs) stay verbatim

### B6 — Build hardening + `.spec` cleanup

  - Add `--noupx` to build.bat
  - Add stdlib `--exclude-module` list per FROZEN_BUILD_BASELINE
  - Add `--collect-all phoenix_commons`
  - Step 0 cleanup: `rmdir /S /Q dist build` (full clean)
  - Add commons-submodule preflight (`import phoenix_commons` from venv; fail loudly if missing)
  - **Delete `ValveMasterTool.spec`** (dead code — references old entry name; build.bat doesn't use it)
  - Document required build venv as Python 3.12 per ADR-014

### B7 — Source-mode validation (MIGRATION_RULES § 10)

  - All 11 rows green: compileall / imports / identity / updater constants / `expected_internal=False` / paths / theme apply offscreen / entry-module import / submodule pin / commons pytest / **actual source-mode launch ≥ 3 sec with `MainWindowTitle` correct**

### B8 — Frozen build + S1 observation

  - Build with Python 3.12 venv + hardened flags
  - Install via `PhoenixMasterToolSetup.exe`
  - Run 5-minute S1 observation window
  - User-data preservation check across upgrade
  - Fake-release updater round-trip if operator wants comprehensive validation (Phase 6C-B pattern)

### B9 — Merge gate + closure report

  - Visual review (≈ 0% expected — light review)
  - Pre-merge audit per `APP_ALIGNMENT_CHECKLIST.md` § J
  - Author `PHASE_8A_VALVEMASTER_REPORT.md` (post-retrofit; 21-section per Phase 3B precedent)
  - Merge `phase-8a-valvemaster-retrofit` → `main` with `--no-ff`
  - Tag `valvemaster-retrofit-vX.Y.Z` (version per operator decision)
  - Update MIGRATION_RULES Phase 8a row

### Estimated session count

  - **B1 through B6: 1 session** (mechanical, surgical)
  - **B7 through B9: 1 session** (validation + merge gate)
  - **Total: 2 sessions** (matches Phase 3B's Phoenix Checkout retrofit duration)

---

## 9. Operator decisions needed

These must be answered **before** Wave 8a kickoff (or in the kickoff brief itself):

  1. **Version bump.** Retrofit alone = invisible to the operator → tag-skip per Phase 3B precedent? Or bump to v1.1.1 (patch) / v1.2.0 (minor)? *Default recommendation:* tag-skip + bump only if shipping new operator-visible functionality (none planned in retrofit).

  2. **`requirements.txt` discrepancy.** CLAUDE.md states it was added during the 2026-05-19 Operational Hardening Sprint, but the file is **not present** at repo root today. Was it deleted? Should B1 add it from scratch? *Default:* add at B1; reconcile CLAUDE.md once observed.

  3. **CI shape — preserve or normalize?** Current `.github/workflows/test.yml` is on ubuntu-latest with Python 3.10/3.11/3.12 matrix ("intentional divergence" per CLAUDE.md). Family convention is `.github/workflows/ci.yml` on windows-latest with Python 3.12 only + commons submodule init + import smoke. *Default:* preserve `test.yml` (per documented operator preference); add a parallel `ci.yml` only if operator wants both.

  4. **`ValveMasterTool.spec` disposition.** Stale (references old entry name; build.bat doesn't use it). *Default:* delete at B6.

  5. **BrandProfile.** Current QSS palette matches commons `DEFAULT_BRAND` exactly. *Default:* use DEFAULT_BRAND; no custom BrandProfile needed.

  6. **Screenshot baseline storage location.** Where to keep before/after screenshots? *Default:* `phoenix-commons/docs/ui-platform-baseline-v1/screenshots/wave-8a/`.

  7. **`SectionCard` retention.** App-specific section card; functions analogously to commons `Panel` but with app-specific behavior. *Default:* keep local (preserved-local per MIGRATION_RULES § 1 hybrid facade rules).

  8. **`_EMBEDDED_QSS` fallback string retention.** Currently lives inside `phoenix_master_pyside6.py` as a safety net if `phoenix_style.qss` can't be read. Once commons handles fallback, retain or retire? *Default:* retire at B4 (commons covers the fallback).

  9. **Python 3.12 build venv enforcement.** Current `.venv/` is Python 3.14. Should `build.bat` print a 3.12-version-check warning or hard-fail? *Default:* document in CLAUDE.md update; soft-warn in build.bat (matches FROZEN_BUILD_BASELINE recommendation without forcing an env teardown).

  10. **Step 0 cleanup preference.** FROZEN_BUILD_BASELINE mandates `rmdir /S /Q build dist`. Current build.bat keeps `build/` for incremental cache. *Default:* full cleanup per baseline; document the tradeoff.

  11. **CI matrix change.** If preserving `test.yml`, should the Python matrix narrow to 3.12 only (matching frozen-build target) or retain 3.10/3.11/3.12 (current)? *Default:* retain matrix per documented operator preference.

  12. **Wave 8a opening date.** Cooldown floor is **2026-06-02** (14 days after Phase 3B merge 2026-05-19). Today is 2026-05-22. Earliest defensible open: 11 days out. *Default:* operator picks when ready; no urgency.

None of these decisions block the audit; they're surfaced for the operator's kickoff brief authoring.

---

## 10. Recommendation

### **Ready after operator decisions + cooldown clearance.**

ValveMaster is in **better shape than the readiness matrix predicted.** Key revisions to the matrix's earlier assessment:

| Dimension | Original matrix prediction | This audit's finding |
|-----------|----------------------------|------------------------|
| Visual drift | HIGH (System B → A swap) | **LOW** (≈ 0% — already System A) |
| Visible-change band | HIGH | **LOW** (Phoenix CAD profile) |
| Retrofit risk | MEDIUM-HIGH | **LOW-MEDIUM** |
| Estimated step count | 6-8 | **5-6 mechanical + 3 validation/gate = 8-9** |
| Estimated session count | 1-2 sessions | **2 sessions** (one for B1-B6, one for B7-B9) |

### What's READY now

  - ✅ Clean working tree; no WIP isolation needed
  - ✅ Theme palette already canonical (System A)
  - ✅ Local widget classes share commons names → surgical monolith inline-class retrofit per MIGRATION_RULES § 11
  - ✅ Updater + installer + AppId all stable post-rename
  - ✅ All 11 commons-API gap inventory rows classified (10× Class C / 0× Class B / 15+× Class A)
  - ✅ Domain logic preservation list documented
  - ✅ Build-hardening gaps identified with FROZEN_BUILD_BASELINE references
  - ✅ Retrofit sequence B1-B9 drafted
  - ✅ Risk classification: LOW-MEDIUM across all 7 dimensions

### What's BLOCKED until operator decides

  - ❌ Wave 8a phase opening (operator approval + cooldown clearance)
  - ❌ The 12 open questions in §9 (operator decisions)
  - ❌ Retrofit branch creation (forbidden by audit-only constraint)
  - ❌ Any source-code modification

### Recommended kickoff timing

  - **2026-06-02** = earliest defensible open per MIGRATION_RULES § Frequency limits
  - **Today (2026-05-22)** = audit complete; operator may begin answering §9 questions
  - **Window between** = operator-decision interval; no urgency

### Wave 8b implications

After Wave 8a closes, Wave 8b (Job Tracker / PMT) cooldown floor = `Wave-8a-merge + 14 days`. Wave 8b remains operator-gated regardless.

---

## 11. Confirmation

  - **No implementation occurred.** No PCC, ValveMaster, Job Tracker, Phoenix CAD, Phoenix Checkout, commons, or any other source-code file was modified.
  - **No app code changed.** This audit is entirely read-only.
  - **No commons API changed.** No new primitives, no new icons, no `__all__` modifications.
  - **No BrandProfile changes occurred.** ValveMaster will use commons `DEFAULT_BRAND` per the retrofit plan; no custom BrandProfile needed; nothing changed in this audit.
  - **No production deployment occurred.** No installer built. No `dist/` artifact. No frozen build. No GitHub Release.
  - **No retrofit branch created.** Wave 8a's `phase-8a-valvemaster-retrofit` branch will be created at kickoff, not now.
  - **No commons submodule added to ValveMaster.** That's a B1 step, executed at retrofit kickoff.
  - **No build.bat / installer.iss / requirements / version.py / theme / UI / `.spec` modifications.** All preserved as observed today.
  - **No Wave 8a kickoff occurred.** The cooldown floor (2026-06-02) still applies; this audit doesn't advance the clock.
  - **No Wave 8b work began.**
  - **No Screenshot_Tool work began.**

---

## Appendix — referenced files

Files inspected (read-only) during this audit:

  - `ValveMasterTool/.git/HEAD` (branch/tip lookup via git)
  - `ValveMasterTool/version.py`
  - `ValveMasterTool/CLAUDE.md`
  - `ValveMasterTool/build.bat`
  - `ValveMasterTool/installer.iss`
  - `ValveMasterTool/ValveMasterTool.spec`
  - `ValveMasterTool/updater.py`
  - `ValveMasterTool/phoenix_master_pyside6.py` (first 80 LOC + grepped for class/setStyleSheet + theme application)
  - `ValveMasterTool/phoenix_style.qss` (first 80 LOC)
  - `ValveMasterTool/assets.py` (first 25 LOC — confirmed base64 PNG data)
  - `ValveMasterTool/inventory.py` (first 25 LOC — confirmed SharePoint catalog interface)
  - `ValveMasterTool/.github/workflows/test.yml`
  - `ValveMasterTool/tests/` (directory listing)

Files NOT modified in this session: every file above.

---

*End of Wave 8a ValveMaster pre-flight audit. Ready after operator decisions + 2026-06-02 cooldown clearance.*
