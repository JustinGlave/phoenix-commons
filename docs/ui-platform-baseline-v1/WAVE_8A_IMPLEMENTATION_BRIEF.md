# Wave 8a — Implementation Brief

> **Status:** ready for execution on or after 2026-06-02 (doctrinal cooldown floor).
> **Target:** ValveMasterTool / Phoenix Master Tool retrofit (Wave 8a).
> **Date authored:** 2026-05-26.
> **Companion docs:**
>   - `WAVE_8A_VALVEMASTER_PREFLIGHT_AUDIT.md` (read-only audit + 9-step plan + 15+ Class-A / 0 Class-B / 10 Class-C gap inventory)
>   - `WAVE_8A_KICKOFF_DECISION_RECORD.md` (12 resolved decisions: 3 explicit-approved + 9 default-accepted)
>   - `WAVE_8A_KICKOFF_READINESS_FINAL_REPORT.md` (verdict A — ready on/after 2026-06-02)
>   - `MIGRATION_RULES.md` (governance — § 0, § 1, § 10, § 11, § Stop conditions)
>   - `FROZEN_BUILD_BASELINE.md` (build hardening recipe)
>   - `APP_ALIGNMENT_CHECKLIST.md` (§ A–L)
>   - `PHOENIX_APP_STANDARD_BASELINE_V1.md` (canonical platform standard)

This brief is **execution-ready**. When the operator declares the Wave 8a kickoff date (≥ 2026-06-02), this document is the single source of truth for what gets done in B1 through B9. No further planning needed.

---

## 1. Step 1 closure — final active-doc consistency

The Step 1 pass (run 2026-05-26 against the canonical regex `System B → A | gray→navy | grey→navy | high visible change | theme swap`) found 5 residual stale-active sites carrying the outdated framing. All 5 were corrected inline before brief authoring proceeded.

### Corrections applied 2026-05-26

| File | Site | Before | After |
|------|------|--------|-------|
| `PACKAGING_CONTRACT.md` | line 160 (per-retrofit safety checklist) | "For ValveMaster: theme swap explicitly noted in release notes" | "For ValveMaster / Phoenix Master Tool: facade retrofit (≈ 0% visible change per WAVE_8A_VALVEMASTER_PREFLIGHT_AUDIT) — AppId GUID `{A7F3C2D1-9B4E-4F6A-8C3D-1E5B7A9F2C4D}` preserved byte-for-byte" |
| `RETROFIT_PR_TEMPLATE.md` | line 45 (PR-body summary template) | "for ValveMaster, it's 'explicit System B → A theme swap — see release notes'" | "For tools already on System A (Phoenix CAD, Phoenix Checkout, ValveMaster / Phoenix Master Tool — see `WAVE_8A_VALVEMASTER_PREFLIGHT_AUDIT` for the byte-match verification), the visible impact is '≈ 0%'…" |
| `visual-baselines/VISUAL_BASELINE_RULES.md` | line 14 (Why baselines exist) | "deliberate visual upgrade for ValveMaster (System B → A)" | "visually neutral for every production tool already shipping on System A — Phoenix CAD, Job Tracker, Phoenix Checkout, and ValveMaster / Phoenix Master Tool…" |
| `visual-baselines/VISUAL_BASELINE_RULES.md` | line 244 (Sign-off examples) | "ValveMaster's System B → A palette swap (intentional — it's the whole point of the retrofit)" | retired; replaced with forward-looking "any future tool that arrives on a non-canonical palette" + supersession note |
| `visual-baselines/README.md` | lines 67–89 (ValveMaster status overview) | "lone production tool that runs on System B — the deprecated `#1c1c1c` gray palette…System B → A migration risks" | revised to "Status revised 2026-05-26 per `WAVE_8A_VALVEMASTER_PREFLIGHT_AUDIT.md`. ValveMaster's `v1.1.0` release already shipped the canonical System A palette…Wave 8a is a facade retrofit — NOT a visible theme swap. Expected visible change ≈ 0%." |
| `visual-baselines/MIGRATION_VISUAL_REVIEW_CHECKLIST.md` | lines 269–296 (ValveMaster section) | "ValveMaster — System B → A cutover (Phase 8a)…every row here is expected to be ⚠️ intentional change with explicit sign-off — the whole point of the retrofit is to replace System B with System A" + 10 cutover-specific checklist rows | revised to "ValveMaster / Phoenix Master Tool — Wave 8a facade retrofit"…"original cutover framing is superseded"…rows reframed to ✅ parity expectations, AppId preservation row preserved, release-note framing changed from "the look has changed intentionally" to "facade retrofit, ≈ 0% visible change" |

### Stale language deliberately preserved (forensic / historical)

The grep still hits these sites — **intentional, do not correct**:

  - Active docs containing supersession markers (e.g. `APP_STANDARDIZATION_READINESS_MATRIX.md:64` *"Earlier predictions of 'HIGH gray→navy swap' are outdated. Release note framing: facade retrofit, not theme swap"*; `PHOENIX_APP_STANDARD_BASELINE_V1.md:414` *"Earlier 'High — gray→navy swap' prediction is superseded"*) — these document the supersession deliberately.
  - `DECISIONS.md:58, 69` (ADR-004, ADR-005) — ADR convention preserves the original decision rationale at the time it was made.
  - Phase-locked historical reports (`PHASE_3*_FINAL_MERGE*.md`, `OPERATIONAL_STABILIZATION_REPORT_01.md`, `STABILIZATION_REPORT_06.md`, `PHASES.md`, `PHASE_3B_POST_REVIEW_AND_MERGE_REPORT.md`) — state-as-of-the-time-of-authoring.
  - Wave 8a forensic record (`WAVE_8A_VALVEMASTER_PREFLIGHT_AUDIT.md`, `WAVE_8A_PREFLIGHT_DOC_CORRECTION_REPORT.md`, `WAVE_8A_KICKOFF_READINESS_FINAL_REPORT.md`) — these quote the outdated framing in order to refute / document its correction.

### Active-doc consistency verdict

✅ **CLEAN.** No active planning doc presents the Wave 8a retrofit as a "System B → A theme swap" or "high visible change". Every active surface aligns with the *facade retrofit, ≈ 0% visible change, Phoenix-CAD profile* framing.

---

## 2. Implementation sequence — B1 through B9

The B-series mirrors `WAVE_8A_VALVEMASTER_PREFLIGHT_AUDIT.md` § 8. Each step is one focused commit (or commit cluster). All commits land on the new branch `phase-8a-valvemaster-retrofit` (created in B1 from `main` HEAD on the ValveMasterTool repo).

### B1 — Commons submodule + requirements + CI baseline

| | |
|---|---|
| **Files touched** | `.gitmodules` (new) · `commons/` (new submodule pointer) · `requirements.txt` (new) · `requirements-dev.txt` (new) · `.github/workflows/ci.yml` (new) · `.github/workflows/test.yml` (unchanged — preserve per Decision #3) · `CLAUDE.md` (reconcile requirements language) |
| **Purpose** | Establish commons consumption + family-standard CI signal + the deterministic build baseline. |
| **Concrete actions** | 1. `git checkout -b phase-8a-valvemaster-retrofit` from `main` HEAD. 2. `git submodule add https://github.com/JustinGlave/phoenix-commons commons`. 3. Write `requirements.txt`: `PySide6==6.10.2` / `PySide6_Addons==6.10.2` / `PySide6_Essentials==6.10.2` / `shiboken6==6.10.2` / `-e ./commons`. 4. Write `requirements-dev.txt`: `pyinstaller==6.20.0` / `pytest==8.3.4` / `pytest-qt==4.4.0`. 5. Add `.github/workflows/ci.yml` on `windows-latest` Python 3.12 with `submodules: recursive` checkout + `pip install -r requirements.txt -r requirements-dev.txt` + `python -c "import phoenix_commons; print(phoenix_commons.__version__)"` smoke + `python -m compileall -q .` + `pytest -q tests/`. 6. Preserve existing `.github/workflows/test.yml` unchanged (ubuntu-latest matrix). 7. Reconcile `CLAUDE.md` if it claims requirements files exist when they do not. |
| **Validation** | `import phoenix_commons` from the activated venv succeeds. `git submodule status` shows the commons pin. Both `ci.yml` and `test.yml` are syntactically valid YAML (`actionlint` or visual inspection). |
| **Stop conditions** | Submodule add fails. Pip resolver can't install pinned deps. CI workflow YAML fails parse. |
| **Expected visible change** | **None** — source not yet rewired. |

### B2 — `paths.py` facade

| | |
|---|---|
| **Files touched** | `paths.py` (new, ≈ 8 lines) · `phoenix_master_pyside6.py` (1 import replacement at the previous `_resource_path` site near line 138) |
| **Purpose** | Replace the inline `_resource_path` helper with a re-export from `phoenix_commons.paths`. Smallest possible facade — proves submodule consumption end-to-end before touching anything riskier. |
| **Concrete actions** | 1. Create `paths.py`: `from phoenix_commons.paths import is_frozen, user_data_dir, resource_path` + `__all__ = ["is_frozen", "user_data_dir", "resource_path"]`. 2. In `phoenix_master_pyside6.py`, remove the inline `_resource_path` helper and import `resource_path` from the new local `paths`. 3. Confirm no other file calls `_resource_path` (grep). |
| **Validation** | `python -c "from paths import resource_path; print(resource_path('phoenix_style.qss'))"` from the source-mode venv prints the absolute path. `compileall` clean. |
| **Stop conditions** | `_resource_path` is called from a site the audit missed (would require a separate audit pass). Path behavior shifts (frozen vs. source-mode resolution). |
| **Expected visible change** | **None.** Path semantics identical. |

### B3 — `updater.py` hybrid facade

| | |
|---|---|
| **Files touched** | `updater.py` (facade + preserved-local legacy logic) · `tests/test_updater.py` (smoke run only; must stay green) |
| **Purpose** | Replace the locally-implemented update check + apply with commons facades, while preserving the ValveMaster-specific legacy-name resolution logic (a Class A preserved-local symbol per the pre-flight audit). |
| **Concrete actions** | 1. `from phoenix_commons.updater import UpdateInfo, check_for_update as _commons_check, download_and_apply as _commons_apply` (re-export `UpdateInfo` for callers — identity preserved). 2. Replace local `check_for_update()` body with `_commons_check(owner="JustinGlave", repo="phoenix-master-tool", current_version=__version__, zip_asset_name="PhoenixMasterTool.zip")` — keep the local function signature `check_for_update()` so callers don't change. 3. Replace local `download_and_apply(info, progress_callback)` body with `_commons_apply(info, exe_name=EXE_NAME, expected_internal=False, progress_callback=progress_callback)` per ADR-003 (exe-only payload contract). 4. **PRESERVE** verbatim: `LEGACY_EXE_NAMES` list, `_ps_single_quote()` helper, the PowerShell extraction script with running-exe-basename detection. These remain Class A preserved-local logic per the audit. 5. Confirm `tests/test_updater.py` still passes. |
| **Validation** | `pytest tests/test_updater.py -q` green. `python -c "from updater import UpdateInfo, check_for_update; print(check_for_update())"` returns `UpdateInfo` or `None` without raising. `assert UpdateInfo is phoenix_commons.updater.UpdateInfo` (identity-equal). |
| **Stop conditions** | `test_updater.py` regresses. `expected_internal` defaults to anything but `False` (would break ADR-003 exe-only payload contract). Legacy-name resolution path is touched by the facade. |
| **Expected visible change** | **None.** Update-check + download UX is structurally identical. |

### B4 — Theme application facade + `_EMBEDDED_QSS` retirement

| | |
|---|---|
| **Files touched** | `phoenix_master_pyside6.py` (`load_phoenix_stylesheet` body + `_EMBEDDED_QSS` constant deletion, ~50 LOC removed) · `phoenix_style.qss` (preserved at repo root — local backup per MIGRATION_RULES § Local backup QSS strategy) |
| **Purpose** | Replace the local disk-read QSS path with `phoenix_commons.theme.apply_dark_theme(app)` using `DEFAULT_BRAND` (per Decision #5). Retire the embedded QSS fallback (per Decision #8). |
| **Concrete actions** | 1. Replace the body of `load_phoenix_stylesheet(app)` with a 2-line facade: `from phoenix_commons.theme import apply_dark_theme; apply_dark_theme(app)`. No `brand=` kwarg — `DEFAULT_BRAND` is the default (commons sentinel-substitution handles palette). 2. Delete the entire `_EMBEDDED_QSS = """…"""` constant body (~50 LOC). Leave a one-line comment: `# Embedded QSS fallback retired 2026-06-XX — commons covers fallback via package data.` 3. **PRESERVE** `phoenix_style.qss` at repo root. MIGRATION_RULES § Local backup QSS strategy keeps it as a safety net; can be deleted ~30 days post-retrofit if commons fallback proves sufficient. |
| **Validation** | Source-mode launch shows the same colors as the pre-retrofit run (palette byte-matches per audit). `compileall` clean. No `_EMBEDDED_QSS` references remain anywhere in the codebase (grep). |
| **Stop conditions** | Source-mode launch shows any pixel-level palette change. `apply_dark_theme(app)` raises (commons not on `sys.path` — would indicate B1 submodule wiring is broken). |
| **Expected visible change** | **≈ 0%** — same canonical palette tokens delivered through commons instead of disk-read. The `phoenix_style.qss` file remains on disk as backup. |

### B5 — Widget retrofit (monolith inline-class pattern, MIGRATION_RULES § 11)

| | |
|---|---|
| **Files touched** | `phoenix_master_pyside6.py` (replace 5 inline class definitions with a single import block; ~80-120 LOC removed) |
| **Purpose** | Swap 5 locally-defined widgets that share commons names for their commons equivalents. The audit verified these are name-collision matches (not behavior divergences). |
| **Concrete actions** | 1. Find the 5 inline class definitions: `class PrimaryButton(QPushButton): …`, `class SecondaryButton(QPushButton): …`, `class TertiaryButton(QPushButton): …`, `class PhoenixTable(QTableWidget): …`, `class UpdateBanner(QFrame): …`. 2. Delete the 5 class bodies. 3. Add a single import block near the top of the file: `from phoenix_commons.widgets import PrimaryButton, SecondaryButton, TertiaryButton, PhoenixTable, UpdateBanner`. 4. **PRESERVE** verbatim: `BadgeLabel`, `SectionCard`, `ClickableFieldCard`, `ValidationIssueRow`, `WatermarkWidget`, `SelfTestDialog`, `OptionPickerDialog`, `OptionsEditorDialog`, `CfmCalculatorDialog`, `TestModelsDialog`, `PartsListDialog`, `ValveMasterMainWindow`. All app-specific. |
| **Validation** | Identity-equal assertions: `import phoenix_master_pyside6 as v; from phoenix_commons.widgets import PrimaryButton, SecondaryButton, TertiaryButton, PhoenixTable, UpdateBanner; assert v.PrimaryButton is PrimaryButton; assert v.SecondaryButton is SecondaryButton; assert v.TertiaryButton is TertiaryButton; assert v.PhoenixTable is PhoenixTable; assert v.UpdateBanner is UpdateBanner`. All 5 must be `is`-equal. `compileall` clean. Source-mode launch identical to pre-B5. |
| **Stop conditions** | Any of the 5 widgets has a behavior gap (subtle styling difference, signal handler missing, override that the audit missed). Caller-site usage breaks — the substitution should be byte-identical at every call site. |
| **Expected visible change** | **≈ 0%** — name-collision widgets share semantics; commons primitive renders identically to the local class. |

### B6 — Build hardening + `.spec` cleanup

| | |
|---|---|
| **Files touched** | `build.bat` (hardening flags) · `ValveMasterTool.spec` (deleted — dead code, Decision #4) · `CLAUDE.md` (document 3.12 build-venv canonical) |
| **Purpose** | Bring `build.bat` onto the FROZEN_BUILD_BASELINE recipe so the frozen exe matches the family's S1-safe profile. |
| **Concrete actions** | 1. Add **Step 0 cleanup** as the very first step in build.bat: `rmdir /S /Q dist build 2>nul` (per Decision #10 — full cleanup). 2. Add **soft-warn** Python-version check: detect non-3.12 venv and print a yellow warning, do NOT block (per Decision #9). 3. Add **commons submodule preflight**: `python -c "import phoenix_commons" || exit /b 1` with a clear error message ("commons submodule not initialised — run `git submodule update --init`"). 4. Add to the pyinstaller command: `--noupx` (AV false-positive reduction), `--collect-all phoenix_commons` (bundle the package), stdlib `--exclude-module` list per FROZEN_BUILD_BASELINE (`tkinter`, `unittest`, `test`, `pydoc`, `lib2to3`, etc.). 5. Preserve verbatim: `--onedir`, `--windowed`, `--add-data` for `version.py` + `phoenix_style.qss` + `inventory.py`, code-signing path via `VMT_SIGNING_CERT` env var. 6. `git rm ValveMasterTool.spec` (Decision #4 — dead code; build.bat uses CLI flags exclusively). 7. Update `CLAUDE.md` to document Python 3.12 build-venv canonical convention per ADR-014. |
| **Validation** | `build.bat` syntactically valid (echo each step on first run). `git status` shows `ValveMasterTool.spec` deleted. Soft-warn fires when run from a non-3.12 venv (verify manually). Preflight succeeds when commons is initialised. |
| **Stop conditions** | Step 0 cleanup wipes an artifact the operator wanted to preserve (operator can override). Soft-warn becomes hard-fail accidentally. Stdlib excludes break frozen-exe imports (verify at B8). |
| **Expected visible change** | **None at source-mode**. Frozen-exe behavior changes are observed at B8. |

### B7 — Source-mode validation (MIGRATION_RULES § 10)

| | |
|---|---|
| **Files touched** | None (pure validation). |
| **Purpose** | Confirm every B1–B6 change holds in source mode before the frozen-build gate. |
| **Concrete actions** | Run all 11 rows of MIGRATION_RULES § 10 source-mode validation checklist: 1. `python -m compileall -q .` clean. 2. `pytest -q tests/` green. 3. `python -c "import phoenix_commons; print(phoenix_commons.__version__)"` succeeds. 4. Identity checks: 5 widget `is`-equal assertions from B5. 5. `from updater import UpdateInfo; assert UpdateInfo is phoenix_commons.updater.UpdateInfo`. 6. `expected_internal=False` is the default in the local `download_and_apply` facade. 7. `from paths import user_data_dir; print(user_data_dir('PhoenixMasterTool'))` returns `%APPDATA%\ATS Inc\PhoenixMasterTool`. 8. Offscreen theme apply: `QT_QPA_PLATFORM=offscreen python -c "from PySide6.QtWidgets import QApplication; import sys; app = QApplication(sys.argv); from phoenix_commons.theme import apply_dark_theme; apply_dark_theme(app)"` exits 0. 9. Entry-module import: `python -c "import phoenix_master_pyside6"` exits 0. 10. Submodule pin is committed (`git submodule status`). 11. **Actual source-mode launch ≥ 3 sec with `MainWindowTitle` correct** — operator-driven (run `python phoenix_master_pyside6.py`, confirm window opens, capture window title visually). |
| **Validation** | All 11 rows green. Operator confirms row 11 visually. |
| **Stop conditions** | Any row fails. Source-mode launch silent-crashes. `MainWindowTitle` is empty or wrong. |
| **Expected visible change** | **≈ 0%** — confirmed in row 11 by direct visual comparison against the pre-retrofit baseline (if operator captured one) or against `v1.1.0` installed reference. |

### B8 — Frozen build + S1 observation

| | |
|---|---|
| **Files touched** | None (build + observe; commits only happen if a regression is found and patched). |
| **Purpose** | Validate the hardened B6 build flags produce an S1-safe frozen exe + installer + run-from-installed exe. |
| **Concrete actions** | 1. Activate Python 3.12 build venv (operator). 2. `pip install -r requirements.txt -r requirements-dev.txt` (with commons editable install). 3. Run `build.bat`. 4. Verify `dist\PhoenixMasterTool\PhoenixMasterTool.exe` exists, has `_internal/` sibling, `phoenix_commons/` is bundled (poke `dist\PhoenixMasterTool\_internal\phoenix_commons\`). 5. Run Inno Setup compilation if not part of build.bat (`iscc installer.iss`). 6. Verify `PhoenixMasterToolSetup.exe` is produced. 7. Install via `PhoenixMasterToolSetup.exe` to `{localappdata}\ATS Inc\PhoenixMasterTool`. 8. Launch installed exe. 9. **5-minute S1 observation window** — leave the installed exe running idle on the operator's desktop. No AV pop, no Crowdstrike S1 quarantine, no process kill. 10. User-data path check: `%APPDATA%\ATS Inc\PhoenixMasterTool\` exists; existing user data preserved if any. 11. Optional comprehensive validation: fake-release updater round-trip per Phase 6C-B pattern. |
| **Validation** | All 6 rows green. S1 observation window clean. Installed exe relaunches without quarantine. User data preserved across install. |
| **Stop conditions** | S1 quarantines the exe within the 5-minute window. Installer fails. Installed exe silent-crashes. User data path drifts. AppId mismatch detected (the installer would prompt as a new install rather than upgrade). |
| **Expected visible change** | **≈ 0%** at the installed-app level. Frozen exe should pixel-match the source-mode launch from B7. |

### B9 — Merge gate + closure report

| | |
|---|---|
| **Files touched** | New report file `PHASE_8A_VALVEMASTER_REPORT.md` (in commons docs) · `MIGRATION_RULES.md` Phase 8a status row update · merge commit on `main` |
| **Purpose** | Close out the retrofit per the canonical merge-gate pattern. |
| **Concrete actions** | 1. Pre-merge audit per `APP_ALIGNMENT_CHECKLIST.md` § J (12-section pre-merge checklist). 2. Light visual review (≈ 0% expected — per Decision #6 the operator captures pre/post screenshots into `phoenix-commons/docs/ui-platform-baseline-v1/screenshots/wave-8a/` if they want forensic record). 3. Author `PHASE_8A_VALVEMASTER_REPORT.md` (21-section per Phase 3B precedent: pre-flight state / B1–B9 diffs / decision-record reconciliation / commons-API gap inventory closure / source-mode validation log / frozen-build validation log / S1 observation log / visual review log / regression-test log / stop-conditions check / file-modification table / preserved-local list / commons-pin / submodule state / pre-merge audit / merge command / post-merge state / lessons / open items / closure). 4. Merge `phase-8a-valvemaster-retrofit` → `main` with `--no-ff` on the ValveMasterTool repo. 5. Tag the merge commit per Decision #1 — **tag-skip** (no version bump; facade-only retrofit produces no new operator-visible functionality). If forensic tag desired: `valvemaster-retrofit-v1.1.0-pre`. 6. Push `main` + tag (if any) + the preserved retrofit branch. 7. Update `MIGRATION_RULES.md` § Migration order row 37 to status `✅ Merged YYYY-MM-DD (merge commit XXXXXXX on phoenix-master-tool:main)…` per the existing 3A/3B/3C/3D/3E/3F/3G pattern. 8. Commit + push the doc update on commons. |
| **Validation** | All § J checklist rows green. Report file authored, internally consistent, all 21 sections populated. Merge clean (no conflicts). Tag (if any) on the merge commit, not on a follow-up cleanup commit. Both repos pushed. `MIGRATION_RULES.md` row reflects the merge. |
| **Stop conditions** | § J checklist has any unresolved row. Visual review surfaces a > 5% visible change band. Merge conflicts (would indicate `main` drifted during the retrofit — re-base). AppId / install-path / updater-zip-name drift detected post-merge (rollback immediately per MIGRATION_RULES § Stop conditions). |
| **Expected visible change** | **≈ 0%** — codified in the report's visual review section. |

### Session-count estimate

  - **B1–B6:** 1 working session (~3-4 hours mechanical surgical work).
  - **B7–B9:** 1 working session (~2-3 hours validation + report + merge).
  - **Total:** 2 sessions (matches Phase 3B Phoenix Checkout retrofit duration).

---

## 3. Resolved decisions — embedded into the B-series

All 12 decisions from `WAVE_8A_KICKOFF_DECISION_RECORD.md` are resolved and reflected in the B-series above. The B step where each decision lands:

| # | Decision | Resolution | Lands at |
|---|----------|------------|----------|
| 1 | Version bump | **tag-skip** (no version.py change) | B9 |
| 2 | `requirements.txt` discrepancy | **APPROVED** — add `requirements.txt` + `requirements-dev.txt` from scratch | B1 |
| 3 | CI shape | **APPROVED** — preserve `test.yml`; add parallel `ci.yml` | B1 |
| 4 | `ValveMasterTool.spec` | **delete** (dead code) | B6 |
| 5 | BrandProfile | **use commons `DEFAULT_BRAND`** (palette byte-matches) | B4 |
| 6 | Screenshot baseline location | `phoenix-commons/docs/ui-platform-baseline-v1/screenshots/wave-8a/` | B9 (optional) |
| 7 | `SectionCard` retention | **keep local** (preserved-local per MIGRATION_RULES § 1) | B5 (excluded) |
| 8 | `_EMBEDDED_QSS` fallback | **retire at B4** (commons covers fallback) | B4 |
| 9 | Python 3.12 build venv | **soft-warn** at build.bat entry; not hard-fail | B6 |
| 10 | Step 0 cleanup | **full cleanup** (`rmdir /S /Q build dist`) | B6 |
| 11 | CI matrix | **retain 3.10/3.11/3.12** on `test.yml`; `ci.yml` is 3.12-only | B1 |
| 12 | Wave 8a opening date | **APPROVED** — doctrinal floor 2026-06-02; no implementation before that date | B1 trigger |

**Cross-cutting invariants** (apply to every B step):

  - **AppId GUID `{A7F3C2D1-9B4E-4F6A-8C3D-1E5B7A9F2C4D}` preserved byte-for-byte** — never touch `installer.iss` AppId line.
  - **Install path `{localappdata}\ATS Inc\PhoenixMasterTool` preserved** — never touch `installer.iss` `DefaultDirName`.
  - **User-data path `%APPDATA%\ATS Inc\PhoenixMasterTool` preserved** — backend / inventory / dialogs never re-rooted.
  - **Updater zip asset name `PhoenixMasterTool.zip` preserved** — installer.iss `OutputBaseFilename=PhoenixMasterToolSetup` unchanged.
  - **Updater exe-only payload contract (ADR-003) preserved** — `expected_internal=False` always.
  - **Base64 brand assets in `assets.py` preserved-local** — never migrate to `--add-data=`; PyInstaller bundles via module scan.
  - **SharePoint-synced inventory JSON path in `inventory.py` preserved-local** — never re-rooted.
  - **`phoenix_master_backend.py` (169 KB domain logic) untouched** — preserved-local in full.
  - **All app-specific dialogs preserved verbatim** — `SelfTestDialog`, `OptionPickerDialog`, `OptionsEditorDialog`, `CfmCalculatorDialog`, `TestModelsDialog`, `PartsListDialog`, `ValveMasterMainWindow`.
  - **Legacy-name updater resolution preserved-local** — `LEGACY_EXE_NAMES`, `_ps_single_quote`, PowerShell extraction script.

---

## 4. Validation plan

Validation runs at three gates: source-mode (after B6), frozen-build (after B8), merge (B9).

### Gate 1 — source-mode (end of B6, formal verification at B7)

| Check | Command / action | Pass criterion |
|-------|------------------|----------------|
| compileall | `python -m compileall -q .` from repo root | Exit 0 |
| pytest | `pytest -q tests/` from repo root | Exit 0 (both `test_updater.py` and `test_validation.py` green) |
| commons import | `python -c "import phoenix_commons; print(phoenix_commons.__version__)"` | Prints a non-error version string |
| Submodule pin | `git submodule status` | Lists `commons` at a specific commit (no `+` or `-` prefix) |
| Identity-equal widgets | Python REPL or smoke test asserting 5 widget `is`-equal | All 5 pass |
| Identity-equal UpdateInfo | `from updater import UpdateInfo; from phoenix_commons.updater import UpdateInfo as CI; assert UpdateInfo is CI` | Pass |
| Updater payload contract | Inspect local `download_and_apply` source for `expected_internal=False` | Default kwarg literally `False` |
| Paths facade | `python -c "from paths import user_data_dir; print(user_data_dir('PhoenixMasterTool'))"` | Prints `…\AppData\Roaming\ATS Inc\PhoenixMasterTool` (creates dir as side effect) |
| Theme apply offscreen | `QT_QPA_PLATFORM=offscreen python -c "from PySide6.QtWidgets import QApplication; import sys; app=QApplication(sys.argv); from phoenix_commons.theme import apply_dark_theme; apply_dark_theme(app)"` | Exit 0 (no QSS parse errors) |
| Entry-module import | `python -c "import phoenix_master_pyside6"` | Exit 0 (module imports without side effects raising) |
| **Source-mode launch ≥ 3 sec** | `python phoenix_master_pyside6.py` (operator-driven) | Window opens, title = "Phoenix Master Tool" (or current canonical), no exceptions in console, can be closed cleanly |

### Gate 2 — frozen-build + S1 observation (B8)

| Check | Command / action | Pass criterion |
|-------|------------------|----------------|
| build.bat hardened baseline | Inspect `build.bat` for: `--noupx`, stdlib excludes, `--collect-all phoenix_commons`, Step 0 cleanup, submodule preflight | All 5 present |
| Frozen exe produced | `dist\PhoenixMasterTool\PhoenixMasterTool.exe` exists | File present |
| `_internal/` sibling | `dist\PhoenixMasterTool\_internal\` exists | Folder present |
| `phoenix_commons/` bundled | `dist\PhoenixMasterTool\_internal\phoenix_commons\` exists with `.py` files | Present |
| Installer produced | `Output\PhoenixMasterToolSetup.exe` exists (or wherever installer.iss outputs) | File present |
| Installer runs cleanly | Run `PhoenixMasterToolSetup.exe`, accept defaults | Installs to `{localappdata}\ATS Inc\PhoenixMasterTool` |
| Installed exe launches | Double-click installed `.lnk` or exe | Window opens; pixel-match to B7 source-mode capture |
| **5-min S1 observation** | Leave installed exe running 5 min idle on operator desktop | No AV pop, no Crowdstrike S1 quarantine, no process kill |
| User-data path preserved | Inspect `%APPDATA%\ATS Inc\PhoenixMasterTool\` | Folder exists; any pre-retrofit data preserved (if upgrade scenario tested) |
| AppId upgrade detection | If upgrading from v1.1.0 installed: installer recognizes existing install | Installer prompts "Upgrade" not "New install" |
| Optional: fake-release updater | Run Phase 6C-B fake-release pattern (operator's call) | Updater check works; download + apply round-trips cleanly |

### Gate 3 — merge gate (B9)

| Check | Command / action | Pass criterion |
|-------|------------------|----------------|
| `APP_ALIGNMENT_CHECKLIST.md` § J | Walk all 12 checklist rows | Every row ✅ |
| Visual review (light) | Compare B7 source-mode launch + B8 installed-exe launch against `v1.1.0` reference | Pixel diff within ≈ 0-5% band (operator confirms) |
| Screenshot capture (optional) | Save before/after into `phoenix-commons/docs/ui-platform-baseline-v1/screenshots/wave-8a/` | Operator preference per Decision #6 |
| `PHASE_8A_VALVEMASTER_REPORT.md` authored | 21-section per Phase 3B precedent | File exists, every section populated |
| Pre-merge: clean tree | `git status` on retrofit branch | "nothing to commit, working tree clean" |
| Pre-merge: pushed | `git fetch && git status` | "Your branch is up to date with 'origin/phase-8a-valvemaster-retrofit'" |
| Merge command | `git checkout main && git merge --no-ff phase-8a-valvemaster-retrofit` | Clean merge, no conflicts, `--no-ff` produces an explicit merge commit |
| Tag (if any) | Per Decision #1: tag-skip. If forensic tag chosen: `git tag -a valvemaster-retrofit-v1.1.0-pre <merge-commit-sha> -m "…"` | Tag points at merge commit, not at a follow-up cleanup commit |
| Push main + tag | `git push origin main` + `git push origin valvemaster-retrofit-v1.1.0-pre` (if tagged) | Both pushed |
| Preserve retrofit branch on origin | `git push origin phase-8a-valvemaster-retrofit:phase-8a-valvemaster-retrofit` | Branch preserved per MIGRATION_RULES § Per-retrofit branch + PR convention |
| `MIGRATION_RULES.md` row update | Edit row 37 to status `✅ Merged YYYY-MM-DD (merge commit XXXXXXX on phoenix-master-tool:main)…` | Commit + push on commons |

---

## 5. Stop conditions — full catalog

The retrofit halts immediately and the operator is notified if any of these trigger. No partial commits land if a stop condition fires mid-step.

### Hard stops (rollback required)

  - **AppId GUID changes.** `{A7F3C2D1-9B4E-4F6A-8C3D-1E5B7A9F2C4D}` must be byte-equal pre/post.
  - **Install path drifts.** `{localappdata}\ATS Inc\PhoenixMasterTool` must remain in `installer.iss` `DefaultDirName`.
  - **Updater zip asset name drifts.** `PhoenixMasterTool.zip` is the GitHub-Release asset name; users have download URLs cached.
  - **User-data path drifts.** `%APPDATA%\ATS Inc\PhoenixMasterTool` must persist; inventory.py + backend writes must keep landing there.
  - **Exe-only payload contract breaks.** `expected_internal=False` per ADR-003 — `True` default would silently demand `_internal/` in the updater zip, breaking the contract.
  - **S1 quarantines the exe during the 5-minute observation window.** Investigate before retry — usually means a build flag drifted.
  - **Domain-logic files touched.** `phoenix_master_backend.py`, `inventory.py`, `assets.py` are preserved-local. Any retrofit-step diff touching them is rolled back.

### Soft stops (investigate before continuing)

  - Frozen exe shows visible change > 5% band at B8 visual review.
  - `tests/test_updater.py` or `tests/test_validation.py` regress at any step.
  - `pip install` resolver can't satisfy pins (e.g. PySide6 6.10.2 not available on the operator's Python 3.12).
  - Identity-equal widget assertion at B5 fails (would mean a name collision the audit missed — re-survey before continuing).
  - `_EMBEDDED_QSS` references remain after B4 (grep must come back empty).
  - Commons submodule pin moves during the retrofit (the submodule is pinned at retrofit-branch creation; moving it mid-retrofit means the commit history shifts under us).

### Operator-discretion pauses (not stops, but flag for sign-off)

  - Lucide-icon substitution introduces a visible glyph change (any chrome icon swap).
  - Build time grows > 60s due to full Step 0 cleanup (acceptable per Decision #10, but document the tradeoff in the closure report).
  - Soft-warn for non-3.12 venv fires (operator chooses to ignore for ad-hoc builds; mandatory for the canonical release build).

---

## 6. Expected visible-change statement

**≈ 0% (Phoenix-CAD profile).** Wave 8a is a facade retrofit; not a visible theme swap.

| Surface | Pre vs. post |
|---------|---------------|
| Window chrome / background | Identical (BG `#0a0e27` byte-matches both before and after) |
| Surface cards | Identical (`#141829` byte-matches; `SectionCard` preserved-local) |
| Buttons | Identical (DEFAULT_BRAND palette = byte-match of local QSS palette) |
| Tables | Within ±1-2px of identical (commons `PhoenixTable` may shift padding marginally) |
| Update banner | Identical (`UpdateBanner` widget swap is name-collision, not behavior change) |
| Dialogs (CFM calculator / options editor / parts list / etc.) | Identical (preserved-local) |
| Branding (PNG logos via `assets.py`) | Identical (preserved-local) |
| Validation pop-ups | Identical (`BadgeLabel`, `ValidationIssueRow` preserved-local) |
| Watermark | Identical (`WatermarkWidget` preserved-local) |

**Release-note framing:** facade retrofit. **Do not** describe Wave 8a as a "theme swap", "visual upgrade", or "look has changed" — those framings are explicitly superseded.

---

## 7. Operator work checklist — manual actions only

Items the operator does outside of the agent-executable B-series. These gate the work session in real time.

### Pre-kickoff (any time on or after 2026-06-02)

  - [ ] Confirm Wave 8a kickoff work-session date is **on or after 2026-06-02**. (Decision #12 — approved.)
  - [ ] Pre-flight clean state: both `phoenix-commons` and `ValveMasterTool` repos clean + pushed + bundles fresh in `Backups/`.
  - [ ] Activate Python 3.12 build venv on the working machine. Confirm `python --version` reports `3.12.x`.
  - [ ] (Optional) Capture **before** screenshots of: main window, parts-list dialog, validation dialog, CFM calculator, options editor — at the deployed v1.1.0 release. Save to `phoenix-commons/docs/ui-platform-baseline-v1/screenshots/wave-8a/before/`. Per Decision #6 location.

### During B1–B6 (mechanical work)

  - [ ] Visually review each step's diff before commit. Surgical diffs only.
  - [ ] If any stop condition fires, halt + flag the agent.
  - [ ] At B5: visually confirm the 5 identity-equal assertions pass in a REPL.

### During B7 (source-mode validation)

  - [ ] Visually review the source-mode launch (row 11 of the § 10 checklist). Window must:
        - Open within ~3 seconds
        - Show the correct `MainWindowTitle`
        - Render the dark-navy palette with no flashing
        - Close cleanly via the X button

### During B8 (frozen-build + S1 observation)

  - [ ] Run `build.bat` from the activated 3.12 venv.
  - [ ] Run `PhoenixMasterToolSetup.exe` to install.
  - [ ] Launch the installed exe + leave it running 5 minutes idle. **Confirm S1 / Crowdstrike does not quarantine.**
  - [ ] (Optional) Capture **after** screenshots of the same 5 surfaces. Save to `phoenix-commons/docs/ui-platform-baseline-v1/screenshots/wave-8a/after/`.
  - [ ] (Optional) Run fake-release updater round-trip per Phase 6C-B pattern.

### During B9 (merge gate)

  - [ ] Walk `APP_ALIGNMENT_CHECKLIST.md` § J row-by-row.
  - [ ] Approve merge by explicit "merge approved" signal to the agent.
  - [ ] Per Decision #1 — confirm tag-skip OR specify forensic tag name (`valvemaster-retrofit-v1.1.0-pre` recommended if any tag).

### Post-merge

  - [ ] Verify `MIGRATION_RULES.md` row 37 reflects the merge.
  - [ ] Verify `PHASE_8A_VALVEMASTER_REPORT.md` is on commons `main`.
  - [ ] Verify the retrofit branch is preserved on origin.
  - [ ] Wave 8b (Job Tracker / Project Tracking Tool) cooldown floor: **14 days after Wave 8a merge** (per MIGRATION_RULES § Frequency limits).

---

## 8. Final kickoff readiness

### Verdict: **READY** — execute on/after 2026-06-02 pending operator go-ahead.

  - ✅ 12 kickoff decisions resolved (3 explicit-approved + 9 default-accepted)
  - ✅ 5 residual stale-active doc sites corrected in this session
  - ✅ B1–B9 sequence specified with files / actions / validation / stop conditions / expected visible change
  - ✅ Cross-cutting invariants enumerated (AppId / install path / user-data / updater zip / exe-only payload / preserved-local list)
  - ✅ Validation plan at 3 gates (source-mode / frozen-build / merge)
  - ✅ Stop conditions cataloged (hard / soft / operator-discretion)
  - ✅ Operator manual-action checklist specified
  - ✅ Expected visible change statement: ≈ 0% (Phoenix-CAD profile), facade retrofit framing
  - ✅ Doctrinal cooldown floor honored: 2026-06-02 (today 2026-05-26 → floor is 7 days out)
  - ✅ Brief is self-contained — agent can execute B1 without re-reading the pre-flight audit / decision record (those are now historical record)

### What still gates the work

  1. **Calendar.** Today is 2026-05-26. Doctrinal floor is 2026-06-02. **7 days remain.** No implementation before then.
  2. **Operator go-ahead.** The operator declares the actual work-session date when ready. May be 2026-06-02 or any later date.

### What does NOT gate the work

  - Standards baseline (signed off per `STANDARDS_BASELINE_APPROVAL_REPORT.md`)
  - Pre-flight audit (complete per `WAVE_8A_VALVEMASTER_PREFLIGHT_AUDIT.md`)
  - Decision finalization (all 12 resolved per `WAVE_8A_KICKOFF_DECISION_RECORD.md` § 13)
  - Active-doc consistency (clean per this brief's § 1)
  - Implementation brief (this document)

### Sequencing into Wave 8b

After Wave 8a merge:
  - 14-day cooldown until Wave 8b (Job Tracker) per MIGRATION_RULES § Frequency limits.
  - Wave 8b earliest defensible open: **Wave 8a merge date + 14 days.**
  - Wave 8b scope: largest production tool surface; `starter_package/` deletion in same PR.

---

## 9. Confirmation

  - **No implementation occurred during this brief-authoring session.**
  - **No app code changed.** Zero source-code edits to `ValveMasterTool`, `phoenix-command-center`, `Phoenix_CAD_Tool`, `Phoenix-Checkout-Tool`, or `Job Tracker`.
  - **No commons API changed.** No new primitives, no new icons, no `__all__` modifications, no test additions/removals on the commons package itself.
  - **No `BrandProfile` change.** Wave 8a will use commons `DEFAULT_BRAND` per Decision #5. Today: no change.
  - **No production deployment occurred.** No installer built, no frozen build produced, no GitHub Release tagged, no installer uploaded.
  - **No retrofit branch created.** `phase-8a-valvemaster-retrofit` will be created at B1 on or after 2026-06-02.
  - **No commons submodule added to ValveMaster.** Also B1.
  - **No `build.bat`, `installer.iss`, `requirements*.txt`, `version.py`, theme file, UI file, or `.spec` modifications** in any production tool. All such changes are scheduled for B1–B6 on or after 2026-06-02.
  - **Doc-only changes** in this session: 5 residual stale-active language corrections (§ 1 above) + this implementation brief.

---

## Commit summary

Files modified or created in the brief-preparation session (all docs-only, all in `phoenix-commons/docs/ui-platform-baseline-v1/`):

  - `PACKAGING_CONTRACT.md` (1 site corrected)
  - `RETROFIT_PR_TEMPLATE.md` (1 site corrected)
  - `visual-baselines/VISUAL_BASELINE_RULES.md` (2 sites corrected)
  - `visual-baselines/README.md` (1 section revised)
  - `visual-baselines/MIGRATION_VISUAL_REVIEW_CHECKLIST.md` (1 section revised)
  - `WAVE_8A_IMPLEMENTATION_BRIEF.md` (NEW — this file)

Total: 5 active planning docs corrected + 1 new brief.

Zero source-code touch in any production tool. Zero commons API touch. Zero branch creation.

---

*End of Wave 8a Implementation Brief. Execute on or after 2026-06-02 pending operator go-ahead.*
