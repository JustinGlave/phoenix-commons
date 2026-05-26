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
| **Operator approval** | `operator-must-confirm` — if there's a reason the file was deleted (e.g. intentional minimalism), operator should say so before B1. |
| **Implementation implication** | New `requirements.txt` at B1 with: `PySide6==6.10.2`, `PySide6_Addons==6.10.2`, `PySide6_Essentials==6.10.2`, `shiboken6==6.10.2`, `-e ./commons`. New `requirements-dev.txt` with: `pyinstaller==6.20.0`, `pytest==8.3.4`, `pytest-qt==4.4.0`. |

---

## 3. CI shape — preserve or normalize

| | |
|---|---|
| **Decision** | Current `.github/workflows/test.yml` is on `ubuntu-latest` with Python `3.10/3.11/3.12` matrix ("intentional divergence" per CLAUDE.md). Family convention is `.github/workflows/ci.yml` on `windows-latest` with Python 3.12 only + commons submodule init + `import phoenix_commons` smoke. Preserve or normalize? |
| **Default** | **Preserve `test.yml`; add a parallel `ci.yml` for the family convention.** Keep the existing ubuntu matrix per documented operator preference. Add a NEW `ci.yml` (windows-latest, Python 3.12, submodule init + import smoke) so the retrofit gets the family-standard signal without removing the existing operator-preferred matrix. |
| **Operator approval** | `operator-must-confirm` — operator may prefer single-CI to avoid duplication; alternative is to merge the two into one matrixed workflow. |
| **Implementation implication** | At B1: keep `test.yml` as-is; add `ci.yml` with the family pattern. Both pass on the retrofit branch tip. |

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
| **Operator approval** | `operator-must-confirm` — operator picks a specific date. |
| **Implementation implication** | Once the date is picked, the operator runs the kickoff brief (which references this decision record + the pre-flight audit). B1 begins on the chosen date. |

---

## 13. Open decisions summary

### `operator-must-confirm` (block kickoff until answered)

  2. `requirements.txt` discrepancy — does the operator know why it's missing?
  3. CI shape — preserve `test.yml` + add `ci.yml`, OR merge into one workflow?
  12. Wave 8a opening date

### `default-accept` (silent acceptance OK)

  1, 4, 5, 6, 7, 8, 9, 10, 11 — all defaults are conservative + reversible. Operator can amend at the kickoff brief stage if desired.

### Summary

  - **3 decisions require operator confirmation.**
  - **9 decisions default-accept silently.**

Once the 3 must-confirm decisions are answered, the kickoff brief can be authored and Wave 8a may open (on or after 2026-06-02).

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

*End of Wave 8a Kickoff Decision Record. Awaits operator answers to the 3 `operator-must-confirm` decisions before Wave 8a opens.*
