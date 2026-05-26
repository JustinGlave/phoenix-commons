# App Standardization Readiness Matrix

> **Status:** assessment only. No implementation.
> **Date:** 2026-05-22.
> **Companion to:** `PHOENIX_APP_STANDARD_BASELINE_V1.md`,
> `APP_ALIGNMENT_CHECKLIST.md`, `MIGRATION_RULES.md`.
> **Purpose:** classify each remaining Phoenix app against the
> v1 baseline. Identifies drift, blockers, retrofit risk, and
> the likely phase order.
> **What this is NOT:** retrofit work, source modification, or
> spec authoring for any specific app.

---

## 0. Scope + inputs

### Apps in this matrix

| App | Folder | Production? | Already retrofitted? |
|-----|--------|-------------|------------------------|
| Phoenix CAD / Lab Layout Tool | `Phoenix_CAD_Tool/` | ✅ Yes | ✅ Phase 3A (2026-05-19) |
| Phoenix Checkout Tool | `Phoenix-Checkout-Tool/` | ✅ Yes | ✅ Phase 3B (2026-05-19) |
| Phoenix Command Center | `phoenix-command-center/` | ❌ Unpackaged hub | ✅ Phase 3C/3D/3E/3F/3G |
| phoenix-commons | `phoenix-commons/` | ❌ Library | n/a — IS the platform |
| **ValveMasterTool** | `ValveMasterTool/` | ✅ Yes | ❌ **Wave 8a candidate** |
| **Job Tracker (PMT)** | `Job Tracker/` | ✅ Yes | ❌ **Wave 8b candidate** |
| Screenshot_Tool | `Screenshot_Tool/` | unclear | ❌ — assessment below |

Not in this matrix (deferred to a separate inventory):

  - `Trin.py` — single-file script; not an app
  - `phoenix-rollout/` — separate rollout repo; not an app
  - `step-1-patch/` — historical artifact
  - `Audit/`, `Backups/`, `Inventory.xlsx` — operational, not apps

### Inputs

  - File-system inventory of each candidate folder (top-level structure surveyed 2026-05-22)
  - `production-inventory.md` (commons docs)
  - Historical Phase 3A / 3B / 6 retrofit experience
  - `MIGRATION_RULES.md` § Migration order + § Frequency limits

This matrix does NOT include deep code-level inspection of each candidate — that's the per-retrofit pre-flight gap inventory (MIGRATION_RULES § 0) which happens when the operator opens the corresponding phase.

---

## 1. Wave 8a — ValveMasterTool

| Dimension | Status |
|-----------|--------|
| **Display name** | ValveMasterTool |
| **Exe name** | ValveMasterTool.exe |
| **Install path** | `{localappdata}\ATS Inc\ValveMasterTool` |
| **User-data path** | `%APPDATA%\ATS Inc\ValveMasterTool` |
| **GitHub release zip** | `ValveMasterTool.zip` |
| **Current `version.py`** | unknown — read at retrofit kickoff |
| **Source files (top-level)** | `phoenix_master_pyside6.py` (main GUI), `phoenix_master_backend.py`, `inventory.py`, `assets.py`, `ValveMasterTool.spec`, `build.bat`, `installer.iss` |
| **Visual drift** | **LOW** — **revised after pre-flight audit (2026-05-22).** v1.1.0 already shipped the System A palette in `phoenix_style.qss` (byte-match `#0a0e27` BG / `#141829` surface / DEFAULT_BRAND red+blue). The earlier "HIGH — System B grey palette" prediction is outdated; the swap was completed pre-Wave-8a. Lucide iconography + raw-QPushButton inventory pending operator review during retrofit (low expected delta). See `WAVE_8A_VALVEMASTER_PREFLIGHT_AUDIT.md`. |
| **Functional drift** | **MEDIUM** — own `inventory.py` for domain data, own updater integration. Theme application via programmatic palette (no QSS file). |
| **Commons readiness** | LOW — no `commons/` submodule, no `requirements.txt` includes `-e ./commons`, theme/widget/paths all local |
| **Build readiness** | **HIGH** — already has `ValveMasterTool.spec` + `build.bat`. Per `OPERATIONAL_HARDENING_REPORT_01` it gained CI in 2026-05. PyInstaller present. |
| **Packaging readiness** | MEDIUM — needs `--noupx` + stdlib excludes + Step-0 cleanup verification against `FROZEN_BUILD_BASELINE.md` |
| **Expected retrofit risk** | **LOW-MEDIUM (revised)** — facade-only retrofit (theme application mechanism, updater facade, widget monolith inline-class swap per MIGRATION_RULES § 11, build hardening). Theme palette already canonical. Domain logic (`inventory.py`, `phoenix_master_backend.py`, `assets.py`) is app-specific business logic that MUST stay local. |
| **Visible-change band** | **LOW ≈ 0% (revised, Phoenix-CAD profile)** — the v1.1.0 release already shipped the System A palette. The pre-flight audit (`WAVE_8A_VALVEMASTER_PREFLIGHT_AUDIT.md`) verified byte-match canonical tokens. Earlier predictions of "HIGH gray→navy swap" are outdated. Release note framing: facade retrofit, not theme swap. |
| **Likely phase order** | **Wave 8a** (next per `MIGRATION_RULES § Migration order`) |
| **Doctrinal cooldown floor** | **2026-06-02** (14 days after Phase 3B's 2026-05-19 merge) |
| **Blockers before implementation** | (a) Operator approval to open the phase; (b) confirm cooldown floor cleared; (c) pre-flight gap inventory of `inventory.py` / `assets.py` symbols against commons; (d) confirm `phoenix_master_pyside6.py` theme region is cleanly separable from domain logic |
| **Estimated step count** | 6-8 small commits (B1 submodule + editable install, B2 paths facade, B3 updater facade, B4 theme retrofit + BrandProfile if needed, B5 widget retrofit, B6 build.bat alignment, B7+ frozen-build validation + visual review) |
| **Expected scope per spec** | `MIGRATION_RULES` Migration order row predicts ~1-2 sessions; high visible change |

---

## 2. Wave 8b — Job Tracker (Project Tracking Tool)

| Dimension | Status |
|-----------|--------|
| **Display name** | Project Tracking Tool (a.k.a. Job Tracker) |
| **Exe name** | ProjectTrackingTool.exe |
| **Install path** | `{localappdata}\ATS Inc\Project Tracking Tool` |
| **User-data path** | `%APPDATA%\ATS Inc\Project Tracking Tool` |
| **GitHub release zip** | `ProjectTrackingTool.zip` |
| **Current `version.py`** | unknown — read at retrofit kickoff |
| **Source files (top-level)** | `financials_dashboard.py`, `financials_dialog.py`, `financials_excel.py`, `Financials mod/` (sub-dir), `ProjectTrackingTool.spec`, `build.bat`, `Project Tracking Tool - User Guide.pdf` |
| **Visual drift** | LOW-MEDIUM — theme already System A per inventory; pre-Lucide chrome likely |
| **Functional drift** | **HIGH** — largest surface area; Excel integration (`financials_excel.py` + `openpyxl`); financials dashboard + dialog; `starter_package/` historically embedded (per MIGRATION_RULES note "delete `starter_package/` in same PR") |
| **Commons readiness** | LOW — no `commons/` submodule yet |
| **Build readiness** | **HIGH** — already has `ProjectTrackingTool.spec` + `build.bat`; CI exists per `OPERATIONAL_HARDENING_REPORT_01` |
| **Packaging readiness** | MEDIUM — needs `--noupx` + stdlib excludes confirmation; `openpyxl` runtime dep must be carried through to the frozen build |
| **Expected retrofit risk** | **HIGH** — largest production surface; longest history; Excel integration is a hidden dep web; `starter_package/` deletion in same PR adds scope |
| **Visible-change band** | < 5% (theme already System A; refactor primarily code-side per MIGRATION_RULES Screenshot baseline) |
| **Likely phase order** | **Wave 8b** (after Wave 8a) |
| **Doctrinal cooldown floor** | 14 days after Wave 8a's merge |
| **Blockers before implementation** | (a) Wave 8a must close first; (b) pre-flight gap inventory of `financials_*` + `Financials mod/` symbols against commons (high chance of preserved-local symbols); (c) confirm `openpyxl` + `pywin32` deps survive the frozen build; (d) `starter_package/` deletion plan |
| **Estimated step count** | 8-10 small commits (largest scope; B1 submodule + install, B2 paths, B3 updater facade with split-install if needed, B4 theme retrofit, B5 widget retrofit, B6 financials-module review, B7 starter_package deletion, B8 build.bat alignment, B9+ frozen build + validation) |
| **Expected scope per spec** | `MIGRATION_RULES` Migration order row: "largest surface; `starter_package/` deletion in same PR" |

---

## 3. Screenshot_Tool — TBD inventory

| Dimension | Status |
|-----------|--------|
| **Display name** | Screenshot Tool (working name) |
| **Exe name** | unknown — `ScreenshotTool.spec` present |
| **Install path** | unknown — likely `{localappdata}\ATS Inc\Screenshot Tool` if deployed |
| **User-data path** | unknown |
| **GitHub release zip** | unknown — not in `production-inventory.md` |
| **Current `version.py`** | unknown |
| **Source files** | `capture_overlay.py`, `config.py`, `ScreenshotTool.spec`, `build.bat`, `NOTES.txt`, `build_output.txt` |
| **Visual drift** | unknown |
| **Functional drift** | unknown — capture-overlay tool suggests Windows screen-capture domain logic |
| **Commons readiness** | LOW — no `commons/` submodule visible |
| **Build readiness** | MEDIUM — has spec + build.bat |
| **Packaging readiness** | unknown |
| **Expected retrofit risk** | **UNCLEAR** — not part of the original 4-tool production inventory. May be operator-internal-only |
| **Visible-change band** | unknown |
| **Likely phase order** | **Not scheduled.** If operator wants it modernized, classify it as Wave 8c+ AFTER Wave 8a + 8b close |
| **Blockers before implementation** | (a) Determine whether Screenshot_Tool is deployed to operators or internal-only; (b) add to `production-inventory.md` if it ships; (c) full pre-flight gap inventory; (d) Wave 8a + 8b must close first per cadence |
| **Recommendation** | **Document, don't schedule.** If operator confirms it's operator-deployed, add a row to `production-inventory.md` and revisit after Wave 8b |

---

## 4. Cross-cutting readiness summary

### Per-dimension status across remaining apps

| Dimension | ValveMaster | Job Tracker | Screenshot_Tool |
|-----------|-------------|-------------|------------------|
| Visual drift vs System A | HIGH (B→A swap) | LOW-MEDIUM | unknown |
| Functional drift | MEDIUM | HIGH | unknown |
| Commons readiness | LOW | LOW | LOW |
| Build readiness | HIGH | HIGH | MEDIUM |
| Packaging readiness | MEDIUM | MEDIUM | unknown |
| Retrofit risk | MEDIUM-HIGH | HIGH | unclear |
| Visible-change band | HIGH | < 5% | unknown |
| Cooldown floor | 2026-06-02 | 14 days post-Wave-8a | n/a |
| Pre-flight inventory needed | YES | YES | YES |
| Operator approval needed | YES | YES (after 8a) | YES |

### Common blockers across all three

  - **Commons submodule absent** in all three repos. Each retrofit begins with B1 = add submodule + `requirements.txt` `-e ./commons` line.
  - **Theme application currently local.** Each app applies its own QSS / palette. Retrofit replaces with `phoenix_commons.theme.apply_dark_theme(app, brand=...)`.
  - **Widgets currently local.** Each app has bespoke buttons + cards. Retrofit replaces with commons primitives via local facade.
  - **build.bat hardening not verified.** `FROZEN_BUILD_BASELINE.md` flags + Step-0 cleanup need confirmation per-app.
  - **Frozen-build validation pending.** Each retrofit's final gate requires a clean build + S1 5-minute observation window.

### Differences

  - **ValveMaster has the highest visible change** (theme swap). Documents loudly in release notes.
  - **Job Tracker has the largest scope** (Excel integration + financials subsystem + `starter_package/` deletion in same PR).
  - **Screenshot_Tool is uninventoried** — needs operator decision on whether to include it in the cadence at all.

---

## 5. Recommended order

### Phase order

1. **Phase 3G closure** — ✅ done (this session)
2. **Standards baseline approval** — author + operator-review (this session)
3. **Wave 8a — ValveMasterTool** — operator-gated; cooldown clears 2026-06-02
4. **Wave 8b — Job Tracker / PMT** — operator-gated; ≥ 14 days after 8a merge
5. **Wave 8c — Screenshot_Tool (optional)** — only if operator confirms it ships to end users

### Why this order

  - **Wave 8a first** because it's already doctrinally scheduled (`MIGRATION_RULES § Migration order`) and the high-visible-change swap is best handled before the operator forgets the visual cadence established in Phase 3C/3D/3E/3F/3G.
  - **Wave 8b second** because it's the largest surface and benefits most from doing Wave 8a's proof-of-pattern first.
  - **Screenshot_Tool last (if ever)** because its operator-visibility is unverified and it's not in `production-inventory.md`.

### Why NOT now

  - **PCC polish items deferred** (New Tool Wizard, About/Shortcuts, Push Preview, Search V2) — operator direction post-3G is to PAUSE these. They're future-phase candidates with no scheduled order.

---

## 6. Pre-flight requirements per app

Each Wave 8x retrofit MUST complete these before opening implementation:

  1. **Operator approval to open the phase.**
  2. **Doctrinal cooldown floor cleared.** (Wave 8a: 2026-06-02; Wave 8b: 14 days post-Wave-8a-merge)
  3. **Pre-flight commons-API gap inventory** (MIGRATION_RULES § 0) — table of every locally-defined symbol with binary Option A (keep local) / Option B (add to commons) decision per gap.
  4. **WIP isolation** if the tool's working tree has unfinished feature work (MIGRATION_RULES § 9).
  5. **Branch created from tool's `main`/`master` at a clean baseline.**
  6. **Branch name follows `phase-8x-<tool-slug>-retrofit` convention.**
  7. **Operator visual-change-band approval.** (Wave 8a: ≈ 0% expected per the pre-flight audit's byte-match verification of `phoenix_style.qss`. Light review only.)

---

## 7. What's intentionally NOT included in this matrix

  - **PCC main app** — already retrofitted (3C-3G); no further retrofit scheduled.
  - **phoenix-commons** — IS the platform; not a retrofit target.
  - **Phoenix CAD / Lab Layout Tool** — already retrofitted in Phase 3A.
  - **Phoenix Checkout Tool** — already retrofitted in Phase 3B.
  - **Trin.py / phoenix-rollout / step-1-patch / Audit / Backups** — not apps in scope.

If the operator wants any of these revisited (e.g. PCC dialog polish, Phoenix CAD frozen-build re-validation), open a separate phase brief — not a Wave-8x retrofit.

---

## 8. Open questions for operator

Before Wave 8a opens, the operator should confirm:

  1. **Wave 8a target version.** Does ValveMaster bump `version.py` as part of the retrofit? If yes, to what? If no, tag-skip pattern (Phase 3B precedent).
  2. **Wave 8a screenshot baseline.** Where to keep pre/post screenshots for the high-visible-change swap?
  3. **Wave 8b Excel scope.** Does retrofit preserve the financials subsystem as-is (preserved-local under MIGRATION_RULES § 1 hybrid facade), or does it warrant its own surface-spec doc?
  4. **Screenshot_Tool inclusion.** Skip permanently, defer until 8b closes, or add to `production-inventory.md` now?
  5. **Wave 8 cadence frequency.** MIGRATION_RULES § Frequency limits sets a 14-day floor between retrofits. Operator may want a longer interval if production-user feedback windows are needed.

These questions are surfaced here so they're answered before the corresponding phase-kickoff brief is authored.

---

## 9. Confirmation

  - **No implementation occurred.** This matrix is assessment only. No source files in any app were modified.
  - **No architecture changes occurred.** No new ADR. No commons API change.
  - **No BrandProfile changes occurred.**
  - **No production deployment occurred.**
  - **No Wave 8a implementation began.** Wave 8a remains operator-gated to its 2026-06-02 doctrinal cooldown floor.
  - **No Wave 8b implementation began.**
  - **No Screenshot_Tool work began.**

---

*End of App Standardization Readiness Matrix. This matrix is the input to whichever Wave 8x phase the operator opens next.*
