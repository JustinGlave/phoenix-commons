# Phase 8a — ValveMaster / Phoenix Master Tool Retrofit Closure Report

> **Status:** ✅ Merged 2026-05-26.
> **Merge commit:** `631dbe8` on `phoenix-master-tool:main`.
> **Forensic tag:** `valvemaster-retrofit-v1.1.0-pre` (annotated, on merge commit).
> **Retrofit branch (preserved):** `phase-8a-valvemaster-retrofit` HEAD `2fa160e`.

---

## 1. Merge commit

```
631dbe8 Merge Wave 8a — ValveMaster / Phoenix Master Tool commons retrofit
```

Stat: 10 files changed, +393 / -405 net.

Parents: `21ba5dfc` (main pre-merge) and `2fa160e` (retrofit branch tip).

---

## 2. Tag state

| Ref | Target | Type |
|-----|--------|------|
| `valvemaster-retrofit-v1.1.0-pre` | `631dbe8` (merge commit) | annotated, pushed |

Tag message: *"Wave 8a commons retrofit complete. version.py unchanged at 1.1.0. Forensic rollback marker only; not a release tag."*

Per Decision #1: tag-skip is the baseline (no version bump); the forensic-only `-pre` suffix marker was operator-chosen for clean `git revert -m 1 <tag>` rollback handle.

---

## 3. B1–B8a summary

| Step | Commit | Scope |
|------|--------|-------|
| B1 | `46012a6` | commons submodule + `requirements.txt` + `requirements-dev.txt` + family `ci.yml` (test.yml preserved per Decision #3) + CLAUDE.md reconcile |
| B2 | `32d15d6` | `paths.py` facade re-exporting commons; inline `_resource_path` retired (1-char call-site diff via wrapped facade binding tool-source-tree base) |
| B3 | `828a99a` | `updater.py` hybrid facade: `check_for_update` + `download_and_apply` delegate to commons with `expected_internal=False` per ADR-003; multi-fallback zip-name resolution + `_parse_version` / `_ps_single_quote` preserved-local for `tests/test_updater.py` regression surface; net -70 LOC |
| B4+B5 | `f2fa97a` | `apply_dark_theme(app)` facade + `_EMBEDDED_QSS` retired (~50 LOC); 5 widgets (`PrimaryButton`/`SecondaryButton`/`TertiaryButton`/`PhoenixTable`/`UpdateBanner`) imported from `phoenix_commons.widgets`; identity-equal × 5 verified; app-specific widgets preserved (BadgeLabel, SectionCard, ClickableFieldCard, ValidationIssueRow, WatermarkWidget, dialogs); net -115 LOC |
| B6 | `704acd4` | `build.bat` hardened: 3.12 soft-warn, commons preflight, Step 0 full cleanup, `--noupx`, `--collect-all=phoenix_commons`, 8× stdlib `--exclude-module`; stale `ValveMasterTool.spec` deleted from disk |
| B7 | (no commit — validation only) | source-mode validation: 156/156 tests, identity-equal × 5, offscreen MainWindow construction `'Phoenix Master Tool v1.1.0'` 1500×940, QSS 19,420 chars |
| B8 | (no commit — build artifacts gitignored) | first hardened frozen build under Python 3.12.10 venv: commons + 23 SVG icons + canonical QSS bundled; 4 artifacts produced; updater zip contract = `['PhoenixMasterTool.exe']` |
| B8a | `2fa160e` | Decoded Fields visual regression fix: B4's commons-only QSS dropped app-specific selectors (`#FieldCardButton[invalid]`, `#ModeBadge`, etc.); restored via two-layer compose (commons baseline + repo-root `phoenix_style.qss` appended); merged QSS 42,932 chars; valid cards green, invalid cards red; operator visual-confirmed |

7 retrofit commits + 1 merge commit = 8 total commits on the merge.

---

## 4. Validation results

Post-merge:

| Check | Result |
|-------|--------|
| compileall (`python -m compileall -q . -x "commons/|.venv|build|dist"`) | clean ✅ |
| Full test suite (`unittest discover -s tests`) | **156/156 green** (10 updater + 146 validation) ✅ |
| `version.py` | `__version__ = "1.1.0"` unchanged ✅ |
| `installer.iss` AppId | `{A7F3C2D1-9B4E-4F6A-8C3D-1E5B7A9F2C4D}` byte-equal ✅ |
| `installer.iss` `DefaultDirName` | `{localappdata}\ATS Inc\{#MyAppName}` preserved ✅ |
| `installer.iss` `OutputBaseFilename` | `PhoenixMasterToolSetup` preserved ✅ |
| Submodule pin | `d21d0fd0 commons (heads/main)` ✅ |
| Working tree | clean (.venv312/ untracked dev artifact only) ✅ |

---

## 5. Frozen build / S1 / visual result

| Item | Result |
|------|--------|
| Hardened frozen build (B8 + B8a rebuilds) | 2 successful runs under Python 3.12.10 venv |
| Frozen exe | `dist/PhoenixMasterTool/PhoenixMasterTool.exe` 2,180,410 B |
| Bundled local QSS | `dist/PhoenixMasterTool/_internal/phoenix_style.qss` 24,593 B (app-specific selectors carried into the frozen build) |
| Bundled commons | `phoenix_commons/{theme,widgets,updater,icons/lucide,paths,_version}` + 23 SVGs + canonical `phoenix_style.qss` |
| Inno Setup installer | `dist/PhoenixMasterToolSetup.exe` 33,828,413 B |
| Build-time S1 quarantine | none observed across both B8 + B8a build cycles |
| Operator visual confirmation (B8a) | passed — Decoded Fields: valid segments green/non-error; invalid segments red/error; mixed-validity models correct per-card |
| 5-min idle S1 observation | implicit pass (operator launched exe for visual review without reporting quarantine; no dedicated observation flag raised) |

---

## 6. Updater zip contract

```
$ python -c "import zipfile; print(zipfile.ZipFile('dist/PhoenixMasterTool.zip').namelist())"
['PhoenixMasterTool.exe']
```

ADR-003 exe-only payload contract preserved. `expected_internal=False` literal in `download_and_apply` body (B3 facade).

---

## 7. Invariants preserved

| Invariant | State post-merge |
|-----------|-------------------|
| AppId GUID `{A7F3C2D1-9B4E-4F6A-8C3D-1E5B7A9F2C4D}` | byte-equal |
| Install path `{localappdata}\ATS Inc\PhoenixMasterTool` | preserved |
| User-data path `%APPDATA%\ATS Inc\PhoenixMasterTool` | preserved (no retrofit step touched `inventory.py` or backend writes) |
| Updater zip asset name `PhoenixMasterTool.zip` | preserved (build.bat output) |
| Updater exe name `PhoenixMasterTool.exe` | preserved (`EXE_NAME` in `updater.py`) |
| Exe-only payload contract (ADR-003) | preserved (`expected_internal=False`) |
| `version.py` `__version__` | `1.1.0` unchanged |
| Domain logic (`phoenix_master_backend.py`, `inventory.py`, `assets.py`, all dialogs) | untouched |
| Test surface (`tests/test_updater.py`, `tests/test_validation.py`) | untouched; 156/156 green |
| Base64 brand assets in `assets.py` | preserved-local; PyInstaller module-scan bundle path intact |
| SharePoint-synced inventory JSON path | preserved-local |
| Legacy-name updater logic (`LEGACY_EXE_NAMES`, `_ps_single_quote`, PowerShell extraction) | preserved per MIGRATION_RULES § 1 hybrid facade |

---

## 8. Remaining intentional debt

| Item | Disposition |
|------|-------------|
| `_parse_version` + `_ps_single_quote` duplicate with commons internals | preserved-local for `tests/test_updater.py` regression contract |
| Repo-root `phoenix_style.qss` (24 KB) carrying app-specific selectors | preserved + actively appended in `load_phoenix_stylesheet` (two-layer compose). Permanent until commons absorbs `#FieldCardButton`/`#ModeBadge`/etc. (no plan in scope; would need a separate commons API decision) |
| `UpdateBanner` user-visible text delta ("Release Notes" vs old "What's new?"; 🆕 emoji dropped) | commons-canonical wording; operator-accepted at B4+B5 merge gate |
| Forensic-PowerShell narrowing (commons matches `<EXE_NAME>` exactly vs retired multi-candidate list) | acceptable narrowing; no current release ships under legacy-only zip-entry name; operator-controlled at release time |
| `.venv312/` untracked at repo root | optional gitignore extension to `.venv*/`; non-blocking |

None are merge-blockers (all carried through the merge as designed).

---

## 9. Remote push results

| Repo | Ref | SHA | Result |
|------|-----|-----|--------|
| `phoenix-master-tool` | `refs/heads/main` | `631dbe8` | pushed |
| `phoenix-master-tool` | `refs/tags/valvemaster-retrofit-v1.1.0-pre` | annotated `77e805a` → `631dbe8` | pushed |
| `phoenix-master-tool` | `refs/heads/phase-8a-valvemaster-retrofit` | `2fa160e` | pushed (preserved per MIGRATION_RULES) |
| `phoenix-commons` | `refs/heads/main` | (pending — MIGRATION_RULES update + this report) | pending |

---

## 10. Recommended next phase

**Wave 8b — Job Tracker / Project Tracking Tool retrofit.**

Per MIGRATION_RULES § Frequency limits: 14-day cooldown floor from Wave 8a merge = **2026-06-09** (computed from 2026-05-26 merge date). Operator-gated.

Wave 8b scope (per MIGRATION_RULES row 38 + the pre-flight audit's cross-cutting summary):
- Largest production tool surface (3-4× the LOC of ValveMaster)
- `starter_package/` deletion in same PR (vestigial legacy scaffold)
- Full-folder updater payload (`expected_internal=True` — different from Wave 8a's exe-only)
- Pre-flight audit + decision record + implementation brief required before kickoff (same pattern as Wave 8a)

Pre-Wave-8b operator checklist:
- Wait until 2026-06-09 or later
- Pre-flight audit of Job Tracker (commons-API gap inventory + visible-change assessment)
- Decision record for Job Tracker-specific items (e.g., starter_package fate, BrandProfile choice, CI shape)
- Implementation brief
- Then operator approves kickoff

---

## 11. Confirmation

- **No domain logic changed** across the entire Wave 8a retrofit (B1 → B8a)
- **No `version.py` change** (`__version__` stays at `1.1.0` per Decision #1 tag-skip)
- **No production deployment** (no PyInstaller release uploaded, no installer published, no GitHub Release drafted or created)
- **No GitHub Release** — the forensic tag `valvemaster-retrofit-v1.1.0-pre` is a git-tag-only artifact; no associated release object on GitHub
- **No installer/updater contract drift** (AppId, install path, user-data path, zip asset name, exe name, exe-only payload contract all preserved byte-for-byte)
- **No commons API change** (Wave 8a consumed existing commons surface only; zero new commons primitives, zero `__all__` mutations, zero new tests on commons-side)
- **No `BrandProfile` change** (uses commons `DEFAULT_BRAND` per Decision #5)

---

*Wave 8a closed and remote-stable. Next retrofit: Wave 8b on or after 2026-06-09.*
