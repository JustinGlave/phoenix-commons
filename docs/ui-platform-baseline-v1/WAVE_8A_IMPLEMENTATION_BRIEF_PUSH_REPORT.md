# Wave 8a — Implementation Brief Push Report

> **Status:** doc-only finalization complete.
> **Date:** 2026-05-26.
> **Companion docs:** `WAVE_8A_IMPLEMENTATION_BRIEF.md`,
> `WAVE_8A_KICKOFF_DECISION_RECORD.md`,
> `WAVE_8A_KICKOFF_READINESS_FINAL_REPORT.md`,
> `WAVE_8A_VALVEMASTER_PREFLIGHT_AUDIT.md`.

This report closes the Wave 8a implementation brief preparation phase. The brief is now committed and pushed; the next operator-actionable step is the Wave 8a kickoff signal on or after **2026-06-02**.

---

## 1. Commit

| Field | Value |
|-------|-------|
| **Commit SHA** | `d44dd262e4c630f23378fa953926844e5acf0ea7` (short `d44dd26`) |
| **Branch** | `main` (on `JustinGlave/phoenix-commons`) |
| **Author** | JustinGlave <justing@atsinc.org> |
| **Date** | 2026-05-26 14:23:03 -0700 |
| **Subject** | `Wave 8a — implementation brief + final active-doc cleanup` |
| **Type** | docs-only |
| **Files changed** | 6 (5 modified + 1 new) |
| **Line delta** | +498 / -61 |
| **Parent** | `55cbc4c` (previous: *Wave 8a — residual cleanup + kickoff decision finalization*) |

---

## 2. Files committed

All 6 files reside under `docs/ui-platform-baseline-v1/`. Zero source-code paths involved.

| File | Change | Scope |
|------|--------|-------|
| `PACKAGING_CONTRACT.md` | modified | Per-retrofit safety checklist row 160 reframed: "theme swap" → "facade retrofit (≈ 0%), AppId preserved byte-for-byte" |
| `RETROFIT_PR_TEMPLATE.md` | modified | PR-body summary template line 45 reframed: ValveMaster now grouped with the System A tools (visible impact ≈ 0%) |
| `visual-baselines/VISUAL_BASELINE_RULES.md` | modified | Two sites reframed (intro § Why baselines exist + § Sign-off examples). ValveMaster included in "visually neutral on System A" set; cutover-example row retired |
| `visual-baselines/README.md` | modified | ValveMaster overview section revised. Replaced "lone System B tool" framing with "Status revised 2026-05-26 — v1.1.0 already shipped canonical System A palette; Wave 8a is a facade retrofit, ≈ 0% visible change" |
| `visual-baselines/MIGRATION_VISUAL_REVIEW_CHECKLIST.md` | modified | ValveMaster section retitled "Wave 8a facade retrofit"; rows reframed from "all ⚠️ intentional change" to ✅ parity expectations; AppId preservation row preserved verbatim; release-note framing switched to "facade retrofit, ≈ 0% visible change" |
| `WAVE_8A_IMPLEMENTATION_BRIEF.md` | **NEW** | 9-section execution-ready B1-B9 plan: Step 1 closure + B-series sequence + resolved-decisions cross-reference + validation plan + stop conditions + expected visible-change statement + operator checklist + readiness verdict + confirmation |

---

## 3. Push result

| Check | Result |
|-------|--------|
| Local branch | `main` |
| Local HEAD | `d44dd26` |
| Push target | `origin/main` (`https://github.com/JustinGlave/phoenix-commons.git`) |
| Push command | `git push origin main` |
| Push output | `55cbc4c..d44dd26  main -> main` |
| Post-push `git status` | `On branch main / Your branch is up to date with 'origin/main'. / nothing to commit, working tree clean` |
| Post-push `git log origin/main..HEAD` | empty (no commits ahead) |
| Verdict | ✅ **clean push** — local matches remote |

---

## 4. Source-code confirmation

**No source files changed in this session.**

`git show --stat d44dd26` output shows 6 files, all under `docs/ui-platform-baseline-v1/`. The path prefix is exclusive:

```
docs/ui-platform-baseline-v1/PACKAGING_CONTRACT.md
docs/ui-platform-baseline-v1/RETROFIT_PR_TEMPLATE.md
docs/ui-platform-baseline-v1/WAVE_8A_IMPLEMENTATION_BRIEF.md
docs/ui-platform-baseline-v1/visual-baselines/MIGRATION_VISUAL_REVIEW_CHECKLIST.md
docs/ui-platform-baseline-v1/visual-baselines/README.md
docs/ui-platform-baseline-v1/visual-baselines/VISUAL_BASELINE_RULES.md
```

Specifically, the diff does **not** touch:

  - Any path under `src/phoenix_commons/` (no commons API change)
  - Any path under `tests/` (no test surface change)
  - `pyproject.toml`, `requirements*.txt`, `.github/workflows/*` on commons (no packaging or CI change)
  - Any path inside any production-tool repo (`ValveMasterTool`, `Phoenix_CAD_Tool`, `Phoenix-Checkout-Tool`, `Job Tracker`, `phoenix-command-center`) — those repos were not touched at all this session

Cross-verified: `git status` is clean across all sibling repos in `C:/Users/justing/PycharmProjects/` (zero working-tree changes outside `phoenix-commons`).

---

## 5. Wave 8a implementation gate

**Wave 8a remains BLOCKED until 2026-06-02 operator go-ahead.**

| Gate | State |
|------|-------|
| Doctrinal cooldown floor | **2026-06-02** (14 days after Phase 3B's 2026-05-19 merge per MIGRATION_RULES § Frequency limits) |
| Today | 2026-05-26 |
| Days remaining | **7 days** to floor clearance |
| Decision record finalized | ✅ all 12 resolved (3 explicit-approved + 9 default-accepted) — `WAVE_8A_KICKOFF_DECISION_RECORD.md` § 13 |
| Pre-flight audit complete | ✅ `WAVE_8A_VALVEMASTER_PREFLIGHT_AUDIT.md` |
| Standards-baseline approval | ✅ `STANDARDS_BASELINE_APPROVAL_REPORT.md` |
| Implementation brief authored | ✅ `WAVE_8A_IMPLEMENTATION_BRIEF.md` |
| Active-doc consistency | ✅ clean — every active surface aligns with the "facade retrofit, ≈ 0% visible change" framing |
| Operator go-ahead | ⏳ **pending** — operator declares Wave 8a kickoff work-session date when ready |
| Retrofit branch (`phase-8a-valvemaster-retrofit`) | ❌ **not created** (B1 task at kickoff) |
| Commons submodule on ValveMaster | ❌ **not added** (B1 task at kickoff) |
| ValveMaster source modifications | ❌ **none** (B2-B6 tasks at kickoff) |
| build.bat hardening | ❌ **not applied** (B6 task at kickoff) |
| Frozen build with hardened flags | ❌ **not built** (B8 task at kickoff) |
| Merge to `main` on ValveMasterTool | ❌ **not merged** (B9 task at kickoff) |

**Nothing in this push opens the Wave 8a implementation gate.** The brief commit is doc-only; the gate is calendar-bound (2026-06-02) and operator-bound (explicit kickoff signal). Either condition unmet → implementation cannot begin.

---

## 6. Next action on or after 2026-06-02

When the operator declares the Wave 8a kickoff work-session date (must be **on or after 2026-06-02**), execute **B1** from `WAVE_8A_IMPLEMENTATION_BRIEF.md` § 2.

### B1 first-action summary (preview only — do not execute today)

| Step | Action |
|------|--------|
| Pre-B1 | Operator activates a Python 3.12 build venv on the working machine. Confirms `python --version` reports 3.12.x. |
| B1.1 | `cd ValveMasterTool && git checkout -b phase-8a-valvemaster-retrofit` (branch from `main` HEAD) |
| B1.2 | `git submodule add https://github.com/JustinGlave/phoenix-commons commons` |
| B1.3 | Write new `requirements.txt`: `PySide6==6.10.2` / `PySide6_Addons==6.10.2` / `PySide6_Essentials==6.10.2` / `shiboken6==6.10.2` / `-e ./commons` |
| B1.4 | Write new `requirements-dev.txt`: `pyinstaller==6.20.0` / `pytest==8.3.4` / `pytest-qt==4.4.0` |
| B1.5 | Add new `.github/workflows/ci.yml` (windows-latest, Python 3.12, `submodules: recursive`, commons import smoke) |
| B1.6 | Preserve `.github/workflows/test.yml` unchanged (ubuntu-latest 3.10/3.11/3.12 matrix per Decision #3) |
| B1.7 | Reconcile `CLAUDE.md` requirements language if stale |
| B1.8 | Validate: `import phoenix_commons` from venv succeeds + `git submodule status` shows pin |
| B1 commit | One commit: "Wave 8a B1 — commons submodule + requirements + CI baseline" |

After B1: proceed sequentially through B2 (paths facade) → B3 (updater facade) → B4 (theme facade + `_EMBEDDED_QSS` retirement) → B5 (widget retrofit) → B6 (build hardening + .spec cleanup) → B7 (source-mode validation) → B8 (frozen build + S1 observation) → B9 (merge gate + closure report).

Estimated total: 2 working sessions (one for B1-B6 ≈ 3-4 hours; one for B7-B9 ≈ 2-3 hours).

### Cross-cutting invariants for every B step

Carry forward from `WAVE_8A_IMPLEMENTATION_BRIEF.md` § 3:

  - AppId GUID `{A7F3C2D1-9B4E-4F6A-8C3D-1E5B7A9F2C4D}` preserved byte-for-byte
  - Install path `{localappdata}\ATS Inc\PhoenixMasterTool` preserved
  - User-data path `%APPDATA%\ATS Inc\PhoenixMasterTool` preserved
  - Updater zip asset name `PhoenixMasterTool.zip` preserved
  - Updater exe-only payload contract (ADR-003) preserved — `expected_internal=False` always
  - Base64 brand assets in `assets.py` preserved-local (PyInstaller module-scan bundle)
  - SharePoint-synced inventory JSON path in `inventory.py` preserved-local
  - `phoenix_master_backend.py` (169 KB domain logic) preserved-local
  - All app-specific dialogs preserved-local
  - Legacy-name updater resolution (`LEGACY_EXE_NAMES`, `_ps_single_quote`, PowerShell extraction script) preserved-local

---

## 7. Confirmation block

  - **No implementation occurred.** No source-code changes in any production tool repo.
  - **No app code changed.** Zero edits to `ValveMasterTool`, `phoenix-command-center`, `Phoenix_CAD_Tool`, `Phoenix-Checkout-Tool`, or `Job Tracker` source.
  - **No commons API changed.** Zero edits to `src/phoenix_commons/` in this session.
  - **No `BrandProfile` change.** Wave 8a will use commons `DEFAULT_BRAND` (Decision #5). No `BrandProfile` instance created.
  - **No production deployment.** No installer built. No frozen build produced. No GitHub Release tagged. No installer uploaded.
  - **No retrofit branch created.** `phase-8a-valvemaster-retrofit` is **not** on the ValveMasterTool repo. B1 creates it on or after 2026-06-02.
  - **No commons submodule on any production tool.** B1 adds it to ValveMaster on or after 2026-06-02.
  - **No `build.bat`, `installer.iss`, `requirements*.txt`, `version.py`, theme file, UI file, or `.spec` modifications** in any production tool. All such changes are scheduled for B1-B6 on or after 2026-06-02.
  - **All doc-only changes pushed to `origin/main`.** Working tree clean across all sibling repos.

---

## 8. End condition

  - ✅ Wave 8a brief committed (`d44dd26`)
  - ✅ Brief + 5 residual corrections pushed to `origin/main`
  - ✅ Docs remotely stable — local matches remote, no commits ahead
  - ✅ Implementation ready for 2026-06-02 or later
  - ✅ No B1 work started
  - ✅ No retrofit branch creation
  - ✅ No source modification

The Wave 8a kickoff signal from the operator (on or after 2026-06-02) unblocks B1. Until then, the platform sits in a stable, documented, decision-finalized state ready for execution.

---

*End of Wave 8a Implementation Brief Push Report. Next operator action: declare Wave 8a kickoff work-session date on or after 2026-06-02, at which point B1 begins per WAVE_8A_IMPLEMENTATION_BRIEF.md.*
