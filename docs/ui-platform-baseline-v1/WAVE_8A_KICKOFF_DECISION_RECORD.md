# Wave 8a — Kickoff Decision Record

> **Status:** decision record. Defaults proposed for the 12 operator-decision items
> raised by `WAVE_8A_VALVEMASTER_PREFLIGHT_AUDIT.md` § 9.
> **Date:** 2026-05-22.
> **Target:** ValveMasterTool / Phoenix Master Tool retrofit (Wave 8a).
> **Cooldown floor:** 2026-06-02 (14 days after Phase 3B's 2026-05-19 merge).
> **Companion:** `WAVE_8A_VALVEMASTER_PREFLIGHT_AUDIT.md`, `PHOENIX_APP_STANDARD_BASELINE_V1.md`,
> `APP_ALIGNMENT_CHECKLIST.md`, `MIGRATION_RULES.md`.
> **Operator action required:** review the 12 defaults below + approve / amend
> before Wave 8a opens.

---

## 0. How to use this doc

Each row carries:
  - **Decision** — the question
  - **Default** — the audit's recommended answer (operator can accept silently)
  - **Operator approval status** — `default-accept` (no operator input needed if default is fine) vs `operator-must-confirm` (explicit answer needed before kickoff)
  - **Implementation implication** — what changes in the retrofit branch if this default holds

Accept all defaults silently OR mark amendments inline. **Decisions with `operator-must-confirm` block kickoff until answered.**

---

## 1. Version bump or tag-skip

| | |
|---|---|
| **Decision** | After the retrofit lands, does `version.py` bump from `1.1.0` to a new version, or do we tag-skip per Phase 3B precedent? |
| **Default** | **Tag-skip.** The retrofit produces ≈ 0% operator-visible change (facade-only). No new shipped functionality. Phase 3B Phoenix Checkout used this exact pattern: `version.py` stayed at 1.7.0; no new tag at merge. |
| **Operator approval** | `default-accept` (operator may amend if any new visible functionality lands during the retrofit). |
| **Implementation implication** | `version.py` untouched. No new GitHub Release. Existing v1.1.0 release remains the operator-facing version. Retrofit merge tagged forensically only (`valvemaster-retrofit-v1.1.0-pre` or skip per operator). |

---

## 2. `requirements.txt` discrepancy

| | |
|---|---|
| **Decision** | `CLAUDE.md` says `requirements.txt` was added during the 2026-05-19 Operational Hardening Sprint, but the file is **not present** at repo root today (`Glob` of `requirements*` returns only `.venv/` paths). Was it deleted? Should B1 add it from scratch? |
| **Default** | **Add at B1 from scratch.** The retrofit needs `requirements.txt` for the `-e ./commons` editable install + PySide6 pin. Either the file was deleted (operator may know why) or CLAUDE.md is stale; either way the retrofit adds it. Reconcile CLAUDE.md at the same commit if needed. |
| **Operator approval** | ✅ **APPROVED** (2026-05-22) — Add `requirements.txt` and `requirements-dev.txt` from scratch in B1. If CLAUDE.md says they already existed, reconcile CLAUDE.md as needed. |
| **Implementation implication** | New `requirements.txt` at B1 with: `PySide6==6.10.2`, `PySide6_Addons==6.10.2`, `PySide6_Essentials==6.10.2`, `shiboken6==6.10.2`, `-e ./commons`. New `requirements-dev.txt` with: `pyinstaller==6.20.0`, `pytest==8.3.4`, `pytest-qt==4.4.0`. CLAUDE.md reconciliation included in the same commit. |

---

## 3. CI shape — preserve or normalize

| | |
|---|---|
| **Decision** | Current `.github/workflows/test.yml` is on `ubuntu-latest` with Python `3.10/3.11/3.12` matrix ("intentional divergence" per CLAUDE.md). Family convention is `.github/workflows/ci.yml` on `windows-latest` with Python 3.12 only + commons submodule init + `import phoenix_commons` smoke. Preserve or normalize? |
| **Default** | **Preserve `test.yml`; add a parallel `ci.yml` for the family convention.** Keep the existing ubuntu matrix per documented operator preference. Add a NEW `ci.yml` (windows-latest, Python 3.12, submodule init + import smoke) so the retrofit gets the family-standard signal without removing the existing operator-preferred matrix. |
| **Operator approval** | ✅ **APPROVED** (2026-05-22) — Preserve existing `test.yml`. Add parallel family-standard `ci.yml`. Do not delete or merge the existing Ubuntu matrix workflow unless a later specific issue appears. |
| **Implementation implication** | At B1: keep `test.yml` as-is (ubuntu-latest, Py 3.10/3.11/3.12 matrix); add NEW `ci.yml` with the family pattern (windows-latest, Py 3.12, `submodules: recursive` checkout, `import phoenix_commons` smoke, compileall, pytest). Both workflows must pass on the retrofit branch tip before merge. |

---

## 4. Stale `ValveMasterTool.spec` — delete or update

| | |
|---|---|
| **Decision** | `ValveMasterTool.spec` references `valve_master_pyside6.py` (old entry name; pre-rename). `build.bat` does NOT use the .spec — it invokes `pyinstaller` directly with CLI flags. The .spec is dead code. Delete or update? |
| **Default** | **Delete at B6.** Dead code; misleading documentation. If the operator later wants spec-based builds, regenerate via `pyi-makespec`. |
| **Operator approval** | `default-accept`. |
| **Implementation implication** | `git rm ValveMasterTool.spec` at B6. Build path unchanged (build.bat already uses CLI flags). |

---

## 5. BrandProfile choice

| | |
|---|---|
| **Decision** | Does ValveMaster keep commons `DEFAULT_BRAND` (red + deep blue + blue per commons canonical), or does it adopt its own `BrandProfile` (like PCC does per ADR-016)? |
| **Default** | **Use commons `DEFAULT_BRAND`.** Pre-flight audit verified `phoenix_style.qss` palette byte-matches `DEFAULT_BRAND` (red `#dc2626`, deep blue `#1e3a8a`, accent blue `#3b82f6`). No custom BrandProfile needed. |
| **Operator approval** | `default-accept`. |
| **Implementation implication** | B4 calls `phoenix_commons.theme.apply_dark_theme(app)` with no `brand=` kwarg (DEFAULT_BRAND is the default). No custom BrandProfile object created in ValveMaster's source. |

---

## 6. Screenshot baseline location

| | |
|---|---|
| **Decision** | Where to keep before/after screenshots for the retrofit's visual review? |
| **Default** | **`phoenix-commons/docs/ui-platform-baseline-v1/screenshots/wave-8a/` (sibling to the audit + report files).** Keeps Wave 8a evidence colocated with the doctrine. Light review only (≈ 0% expected change). |
| **Operator approval** | `default-accept`. |
| **Implementation implication** | Operator takes pre-retrofit screenshots (current main tip) + post-retrofit screenshots (retrofit branch tip) and drops them into the `screenshots/wave-8a/` folder before the merge gate. ~5-10 minutes of operator time. |

---

## 7. `SectionCard` retention

| | |
|---|---|
| **Decision** | ValveMaster has an app-specific `SectionCard(QFrame)` class at `phoenix_master_pyside6.py:400`. It functions analogously to commons `Panel` but its API may differ. Keep local or migrate to `Panel`? |
| **Default** | **Keep local (preserved-local per MIGRATION_RULES § 1 hybrid facade pattern).** Per `Delete duplication, not behavior` doctrine: if commons API subtly differs, the app keeps its local behavior. Migration to `Panel` would risk per-section visual regression for no commons-API gain. |
| **Operator approval** | `default-accept`. |
| **Implementation implication** | `SectionCard` stays as a local class at line 400. B5 widget retrofit replaces ONLY the inline `PrimaryButton`, `SecondaryButton`, `TertiaryButton`, `PhoenixTable`, `UpdateBanner` classes (5 classes, byte-identical to commons). `SectionCard` ignored. |

---

## 8. `_EMBEDDED_QSS` fallback retention

| | |
|---|---|
| **Decision** | `phoenix_master_pyside6.py` carries an `_EMBEDDED_QSS` string fallback used if `phoenix_style.qss` can't be read at startup (~50 LOC). After B4 (commons theme facade), commons covers the fallback path automatically. Retire or retain? |
| **Default** | **Retire at B4.** Commons `apply_dark_theme(app)` reads the canonical QSS from package data — no disk-read fallback needed. The local `phoenix_style.qss` at repo root stays per MIGRATION_RULES § Local backup QSS strategy (deleted ~30 days post-retrofit per the same strategy). The `_EMBEDDED_QSS` string body retires entirely. |
| **Operator approval** | `default-accept`. |
| **Implementation implication** | B4 deletes the `_EMBEDDED_QSS` constant + its content (~50 LOC). `load_phoenix_stylesheet(app)` body becomes a 2-line facade calling `apply_dark_theme(app)`. |

---

## 9. Python 3.12 build-venv enforcement

| | |
|---|---|
| **Decision** | Current `.venv/` is Python 3.14 (per `cpython-314.pyc` artifacts). FROZEN_BUILD_BASELINE requires Python 3.12 for frozen builds (ADR-014 / `BUILD_HARDENING_EXPERIMENT_REPORT_03`). Should `build.bat` print a warning, hard-fail, or stay silent? |
| **Default** | **Soft-warn at build.bat entry.** Add a `python --version` check that prints a yellow warning if the active venv is not 3.12.x, but doesn't block the build. Matches FROZEN_BUILD_BASELINE recommendation without forcing operators to tear down their dev venv. Hard-fail is too aggressive for a tool that's already shipping; soft-warn lets operators choose. |
| **Operator approval** | `default-accept` (operator may amend to hard-fail if they want strict enforcement). |
| **Implementation implication** | B6 adds 4-line `python --version` check at top of build.bat. Prints warning + continues if not 3.12. CLAUDE.md updated to document the canonical 3.12 build-venv convention. |

---

## 10. Step 0 cleanup preference

| | |
|---|---|
| **Decision** | FROZEN_BUILD_BASELINE mandates `rmdir /S /Q build dist` before every build (deterministic state). Current build.bat removes `dist/` but keeps `build/` for PyInstaller's incremental cache (faster iteration). |
| **Default** | **Full cleanup per FROZEN_BUILD_BASELINE.** Determinism beats incremental-cache speed for the canonical retrofit + release build. Operator can manually keep `build/` for ad-hoc local iteration; `build.bat clean` already exists as the existing override. |
| **Operator approval** | `default-accept` (operator may amend to keep current behavior if iteration speed matters more than determinism). |
| **Implementation implication** | B6 changes the default to remove `build/` along with `dist/`. The existing `if /i "%1"=="clean"` block becomes the no-op fallback (or stays as an explicit "extra-clean" override for cache scenarios). Build time per run grows by ~30-60 seconds. |

---

## 11. CI matrix behavior

| | |
|---|---|
| **Decision** | If preserving `test.yml` (per §3 default), should the Python matrix narrow to 3.12 only (matching frozen-build target) or retain 3.10/3.11/3.12 (current)? |
| **Default** | **Retain 3.10/3.11/3.12 matrix on `test.yml`.** ValveMaster's domain logic (`phoenix_master_backend.py`, `inventory.py`) is Python-version-robust; the matrix catches accidental 3.12-only syntax sneaks. The new parallel `ci.yml` (§3) uses 3.12-only matching the frozen-build target. |
| **Operator approval** | `default-accept`. |
| **Implementation implication** | `test.yml` unchanged. `ci.yml` (new) is single-version 3.12. |

---

## 12. Wave 8a opening date

| | |
|---|---|
| **Decision** | Earliest defensible open per MIGRATION_RULES § Frequency limits is **2026-06-02** (today is 2026-05-22; floor is 11 days out). When does the operator want Wave 8a to actually open? |
| **Default** | **Open on or after 2026-06-02; exact date is operator choice.** No urgency. Per `WAVE_8A_VALVEMASTER_PREFLIGHT_AUDIT.md` § 10 the retrofit is in good shape and waits cleanly. |
| **Operator approval** | ✅ **APPROVED** (2026-05-22) — Use the doctrinal floor date 2026-06-02 OR the first operator-approved work session after that date. No implementation before 2026-06-02. |
| **Implementation implication** | Wave 8a kickoff brief authoring may begin any time; B1 (retrofit branch creation + commons submodule add) starts no earlier than 2026-06-02. Operator confirms the actual work-session date when ready. |

---

## 13. Final decision summary (all 12 resolved)

### ✅ Explicitly operator-approved (3)

  - **#2 `requirements.txt` discrepancy** — APPROVED 2026-05-22. Add `requirements.txt` + `requirements-dev.txt` from scratch in B1; reconcile CLAUDE.md as needed.
  - **#3 CI shape** — APPROVED 2026-05-22. Preserve `test.yml`; add parallel family-standard `ci.yml`. Do not delete/merge the existing Ubuntu matrix workflow unless a later specific issue appears.
  - **#12 Wave 8a opening date** — APPROVED 2026-05-22. Use doctrinal floor date 2026-06-02 OR the first operator-approved work session after that date. No implementation before 2026-06-02.

### ✅ Default-accepted (9)

  - **#1** Version: tag-skip (no version bump for facade-only retrofit)
  - **#4** `ValveMasterTool.spec`: delete at B6 (dead code)
  - **#5** BrandProfile: use commons `DEFAULT_BRAND` (palette byte-matches)
  - **#6** Screenshot baseline location: `phoenix-commons/docs/ui-platform-baseline-v1/screenshots/wave-8a/`
  - **#7** `SectionCard` retention: keep local (preserved-local per MIGRATION_RULES § 1)
  - **#8** `_EMBEDDED_QSS` fallback: retire at B4 (commons covers fallback)
  - **#9** Python 3.12 build venv: soft-warn at build.bat entry; not hard-fail
  - **#10** Step 0 cleanup: full cleanup per FROZEN_BUILD_BASELINE (`rmdir /S /Q build dist`)
  - **#11** CI matrix: retain 3.10/3.11/3.12 on `test.yml`; `ci.yml` is 3.12-only

### Summary

  - **12 decisions resolved.**
  - **0 decisions blocking kickoff.**
  - Wave 8a kickoff brief authoring may begin any time.
  - Wave 8a implementation (B1) starts no earlier than 2026-06-02.

---

## 14. Confirmation

  - **No implementation occurred.** No source-code changes to ValveMaster or any other app.
  - **No commons API changed.** All proposed defaults consume existing commons API.
  - **No BrandProfile changes.** ValveMaster will use commons `DEFAULT_BRAND` per the default in §5.
  - **No production deployment.** No installer built; no release tagged.
  - **No retrofit branch created.** Branch creation is a B1 task at kickoff.
  - **No commons submodule added to ValveMaster.** Also B1.
  - **No build.bat / installer.iss / requirements / version.py modifications.** All preserved as observed.
  - **Wave 8a remains operator-gated** to the 2026-06-02 doctrinal cooldown floor.

---

*End of Wave 8a Kickoff Decision Record. All 12 decisions resolved on 2026-05-22. Wave 8a may open on or after the 2026-06-02 doctrinal cooldown floor pending final operator go-ahead.*
