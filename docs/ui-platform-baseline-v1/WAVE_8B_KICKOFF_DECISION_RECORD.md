# Wave 8b — Kickoff Decision Record

> **Status:** all 12 decisions resolved (3 explicit-approved + 9 default-accepted).
> **Target:** Job Tracker / Project Tracking Tool.
> **Date:** 2026-05-27.
> **Companion:** `WAVE_8B_JOB_TRACKER_PREFLIGHT_AUDIT.md`.

---

## ✅ Explicitly operator-approved (3)

### #2 — starter_package disposition

| | |
|---|---|
| Decision | **APPROVED (2026-05-27) — Delete `starter_package/` in the same PR at B7.** |
| Reason | Audit confirmed no runtime/build/test dependency. MIGRATION_RULES row 38 already expected deletion. |
| Implementation | `git rm -r starter_package/` at B7. |

### #9 — phoenix_style.qss disposition

| | |
|---|---|
| Decision | **APPROVED (2026-05-27) — Use Wave 8a B8a two-layer compose pattern.** Commons baseline first, then append repo-root `phoenix_style.qss`. If the file is empty/stale, extract the app-specific overlay (selectors not in commons QSS — e.g. `#taskToolsButton`) from `_EMBEDDED_QSS` and write it into `phoenix_style.qss` before retiring `_EMBEDDED_QSS`. |
| Reason | Wave 8a B8a proved the two-layer compose pattern preserves app-specific selectors without commons-side modification. |
| Implementation | At B4: `apply_dark_theme(app)` + `app.setStyleSheet(app.styleSheet() + open(resource_path('phoenix_style.qss')).read())`. If repo-root QSS is dead/empty, extract app-specific selectors from `_EMBEDDED_QSS` first. |

### #12 — Cooldown / opening date

| | |
|---|---|
| Decision | **APPROVED EARLY-OPEN OVERRIDE (2026-05-27)** — Wave 8b implementation may begin before the 2026-06-09 doctrinal cooldown floor by explicit operator instruction. |
| Reason | Pre-flight audit complete, repo clean, decisions resolved, operator wants to keep making deliverable progress. |
| Implementation | Record override in B1 commit message + every B-step report (mirrors Wave 8a early-open precedent). |

---

## ✅ Default-accepted (9)

| # | Decision | Resolution |
|---|----------|------------|
| 1 | Version bump or tag-skip | **tag-skip.** `version.py` stays at `1.8.5`. Forensic tag `job-tracker-retrofit-v1.8.5-pre` on merge commit (Wave 8a precedent). |
| 3 | Excel / financials scope | **preserve verbatim.** `financials_dashboard.py` / `financials_dialog.py` / `financials_excel.py` / `financials_models.py` untouched. `openpyxl` / `pyxlsb` / `reportlab` hidden imports preserved in build.bat. |
| 4 | Screenshot baseline location | `phoenix-commons/docs/ui-platform-baseline-v1/screenshots/wave-8b/`. |
| 5 | CI shape | minor edit to existing `.github/workflows/ci.yml`: add `submodules: recursive`, `pip install -r requirements-dev.txt`, `import phoenix_commons` smoke. No parallel workflow needed (already family-standard). |
| 6 | Python 3.12 build-venv enforcement | **soft-warn** at build.bat entry (Wave 8a Decision #9 pattern). |
| 7 | Step 0 cleanup | **full cleanup** — `rmdir /s /q dist build` per FROZEN_BUILD_BASELINE. |
| 8 | AppId GUID addition | **DO NOT ADD** — hard rule. installer.iss currently has no explicit AppId; v1.6.0..v1.8.5 users have AppName-hashed default; adding one would break upgrade detection. |
| 10 | BrandProfile | commons **`DEFAULT_BRAND`** (palette byte-matches `_EMBEDDED_QSS`). |
| 11 | WIP isolation | not needed — working tree clean. |

---

## Cross-cutting invariants

  - **AppId absence** preserved (do not add explicit AppId to installer.iss)
  - **AppName "Project Tracking Tool"** preserved byte-for-byte (Inno Setup upgrade detection depends on it)
  - **Install path `{localappdata}\ATS Inc\Project Tracking Tool`** preserved (note space)
  - **User-data path `%APPDATA%\ATS Inc\Project Tracking Tool`** preserved
  - **Updater zip asset name `ProjectTrackingTool.zip`** preserved
  - **Updater exe name `ProjectTrackingTool.exe`** preserved
  - **Full-folder payload contract** — `expected_internal=True` (commons default)
  - **`version.py` `__version__ = "1.8.5"`** unchanged
  - **`tests/test_regressions.py` (441 LOC)** stays green throughout
  - **Preserved-local symbols** for test-import contract: `UpdatePackageError` (re-export from commons), `_validate_update_zip`, `_build_update_powershell_script` (local helpers)
  - **Preserved-local domain logic:** `project_tracker_backend.py`, financials_*.py, `user_auth.py`, `generate_guide.py`, `_app_data_path`, `_backup_data_file`

---

## Summary

  - **12 decisions resolved.**
  - **0 decisions blocking kickoff.**
  - Early-open override recorded (2026-06-09 floor breached by explicit operator instruction).
  - Wave 8b implementation (B1) starts on next explicit operator approval.

---

*End of Wave 8b kickoff decision record.*
