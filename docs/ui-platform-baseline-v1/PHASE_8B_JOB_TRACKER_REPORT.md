# Phase 8B — Job Tracker / Project Tracking Tool Commons Retrofit (Closure)

> **Status:** merged + remote-stable.
> **Date:** 2026-05-28.
> **Wave:** 8b (Job Tracker).
> **Companions:** WAVE_8B_JOB_TRACKER_PREFLIGHT_AUDIT, WAVE_8B_KICKOFF_DECISION_RECORD, WAVE_8B_IMPLEMENTATION_BRIEF, WAVE_8B_B1/B2/B3/B4_B5/B6_B7/B8_B9/B10/B11_MERGE_GATE_REPORT.

---

## 1. Merge commit

| Field | Value |
|-------|-------|
| Repo | `JustinGlave/project-tracking-tool` |
| Merge commit SHA | `6a0d60b1e04d9b99d500d4c4f3c2fd1ab6a7cdd6` (short `6a0d60b`) |
| Merge message | `Merge Wave 8b — Job Tracker commons retrofit` |
| Strategy | `--no-ff` |
| Parent 1 (main pre-merge) | `0eaed43` *CI: workflow name 'CI' -> 'ci' (N2 — Operational Convergence)* |
| Parent 2 (retrofit branch HEAD) | `d7212cc` *Wave 8b B8 — build.bat hardening + B9 source-mode validation* |
| Files changed | 20 (+497 / -2508 = net **-2011 LOC**) |

---

## 2. Tag state

| Field | Value |
|-------|-------|
| Tag | `job-tracker-retrofit-v1.8.5-pre` |
| Type | annotated, signed by default git config |
| Points at | `6a0d60b` (the `--no-ff` merge commit) |
| Message | *Wave 8b commons retrofit complete. version.py unchanged at 1.8.5. Forensic rollback marker only; not a release tag.* |
| Pushed | ✅ to `origin` |

Decision #1 tag-skip baseline preserved (no version bump). The forensic tag enables `git revert -m 1 job-tracker-retrofit-v1.8.5-pre` for atomic rollback.

---

## 3. B1–B10 summary

| Step | Commit | Scope |
|------|--------|-------|
| B1 | `cc7acdb` | commons submodule pinned at `ff2fb40` + `requirements-dev.txt` (pyinstaller 6.20.0 / pytest 8.3.4 / pytest-qt 4.4.0) + `requirements.txt -e ./commons` + ci.yml minor edit (submodules:recursive + reqs-dev + import smoke) + CLAUDE.md retrofit-state |
| B2 | `949675d` | `paths.py` facade (Path-returning wrapper around commons `resource_path`) + inline `_resource_path` retired (5 LOC) + 4 call sites updated; `_app_data_path` + `_backup_data_file` preserved-local |
| B3 | `33fd3d9` | `updater.py` hybrid facade — `check_for_update` + `download_and_apply` delegate to commons (`expected_internal=True`); `UpdateInfo` + `UpdatePackageError` re-exported from commons; `_validate_update_zip` + `_build_update_powershell_script` preserved-local for `tests/test_regressions.py` import surface |
| B4+B5 | `6c70acf` | `apply_phoenix_theme` body → `apply_dark_theme(app)` + two-layer overlay (Wave 8a B8a pattern); `_EMBEDDED_QSS` retired (~116 LOC); repo-root `phoenix_style.qss` rewritten — stale Checkout leftover (~894 LOC mislabeled "Phoenix Valve Checkout Tool") replaced with Job-Tracker app-specific overlay (~135 LOC migrated from retired `_EMBEDDED_QSS`); 5 inline widgets (PrimaryButton/SecondaryButton/TertiaryButton/PhoenixTable/UpdateBanner) replaced with `phoenix_commons.widgets` imports; UpdateBanner call site updated for commons signature; identity-equal × 5 verified |
| B6+B7 | `45d26f7` | preserved-local audit: 7 domain files confirmed 0-diff vs main (`project_tracker_backend.py`, financials_*.py × 4, `user_auth.py`, `generate_guide.py`); Excel/openpyxl/pyxlsb/reportlab pins + hidden imports preserved; `starter_package/` deletion (8 source files via `git rm -r`); CHANGELOG.md retrospective entry |
| B8+B9 | `d7212cc` | build.bat hardening: 3.12 soft-warn + commons preflight + Step 0 full cleanup (`rmdir /s /q dist build`) + `--noupx` + `--collect-all=phoenix_commons` + 8× stdlib `--exclude-module`. Preserved verbatim: existing README/version sanity check, `py_compile` checks, `unittest discover -s tests`, Excel/pyxlsb hidden imports, `--add-data` for all assets, Inno Setup compilation, full-folder updater zip generation, post-build zip layout verify. `ProjectTrackingTool.spec` preserved (entry correct; minor non-canonical divergence documented). B9 source-mode validation: compileall + 29/29 tests + 5/5 identity + offscreen QSS smoke all green |
| B10 | (no commit) | Frozen build under fresh Python 3.12.10 venv; build.bat ran end-to-end producing 4 artifacts (exe 3.15 MB / installer 37.3 MB / updater zip 54.8 MB / full-install zip 54.8 MB); commons + 23 Lucide SVGs + canonical QSS bundled at `_internal/phoenix_commons/`; updater zip = full-folder (260 entries, exe + `_internal/*` at root — ADR-003); operator interactive 5-min S1 observation passed; operator visual review passed (≈ 0% change) |

---

## 4. Validation results (post-merge)

| Check | Result |
|-------|--------|
| Branch | `main` ✅ |
| Working tree | clean (`.venv312/` untracked build artifact only) ✅ |
| compileall | clean across 10 source files ✅ |
| Full test suite | **29/29 green** ✅ |
| `version.py` | `"1.8.5"` unchanged ✅ |
| `installer.iss` AppId | absent (Decision #8 hard rule preserved) ✅ |
| `installer.iss DefaultDirName` | `{localappdata}\ATS Inc\Project Tracking Tool` ✅ |
| `installer.iss OutputBaseFilename` | `ProjectTrackingToolSetup` ✅ |
| `updater.py EXE_NAME` | `ProjectTrackingTool.exe` ✅ |
| `updater.py ZIP_ASSET_NAME` | `ProjectTrackingTool.zip` ✅ |
| `expected_internal=True` in facade body | literal preserved ✅ |
| Full-folder payload contract (ADR-003) | preserved ✅ |

---

## 5. Frozen build / S1 / visual result

Recorded in detail in `WAVE_8B_B10_FROZEN_BUILD_S1_REPORT.md` §§ 1–9. Summary:

| Dimension | Result |
|-----------|--------|
| Python build venv | 3.12.10 (canonical per ADR-014) |
| build.bat | end-to-end success |
| Artifacts produced | 5 (frozen exe + `_internal/` + installer + updater zip + full-install zip) |
| Commons bundle | `phoenix_commons/{theme,widgets,updater,icons/lucide,paths,_version}` + 23 SVGs + canonical `phoenix_style.qss` at `_internal/phoenix_commons/theme/` |
| Excel deps bundled | `pyxlsb/` (full pkg) + `openpyxl` + `reportlab` (in PYZ/base_library.zip) |
| Updater zip contract | full-folder, 260 entries (`expected_internal=True` per ADR-003) |
| Operator 5-min S1 idle observation | ✅ PASSED (no quarantine, no crash, exe persists) |
| Operator visual review | ✅ PASSED (≈ 0% change, buttons/tables/theme correct, financials + auth surfaces clean) |

---

## 6. Updater zip contract

| Property | Value |
|----------|-------|
| File name | `ProjectTrackingTool.zip` |
| Total entries | 260 |
| Root contains | `ProjectTrackingTool.exe` + `_internal/` (260+ files) |
| Contract type | **Full-folder payload (`expected_internal=True`)** per ADR-003 — Job Tracker is the canonical full-folder updater consumer; commons facade default matches |
| Validation logic | both build.bat post-build PowerShell check AND `phoenix_commons.updater.installer._validate_update_zip` |
| Local `_validate_update_zip` | preserved at `updater.py` for `tests/test_regressions.py` import contract |

---

## 7. Invariants preserved

All 13 cross-cutting invariants from `WAVE_8B_B11_MERGE_GATE_REPORT.md` § 4 confirmed post-merge:

1. AppId GUID absence (`installer.iss` not edited)
2. AppName "Project Tracking Tool" byte-equal
3. Install path `{localappdata}\ATS Inc\Project Tracking Tool`
4. User-data path `%APPDATA%\ATS Inc\Project Tracking Tool`
5. Updater zip asset name `ProjectTrackingTool.zip`
6. Updater exe name `ProjectTrackingTool.exe`
7. Full-folder payload contract (`expected_internal=True`)
8. `version.py __version__ = "1.8.5"`
9. Test surface (`tests/test_regressions.py` 29 tests)
10. Domain logic untouched (`project_tracker_backend.py`, financials_*.py × 4, `user_auth.py`, `generate_guide.py`)
11. Excel/PDF runtime deps preserved (openpyxl + pyxlsb + reportlab + all hidden imports)
12. Build artifacts gitignored
13. No production deployment

---

## 8. `starter_package/` deletion summary

Deleted 8 source files in B7 per Decision #2:

| File | Size |
|------|------|
| `starter_package/CLAUDE.md` | 5.8 KB |
| `starter_package/app_backend.py` | 3.0 KB |
| `starter_package/app_gui.py` | 22.2 KB |
| `starter_package/build.bat` | 3.9 KB |
| `starter_package/gitignore.txt` | 67 B |
| `starter_package/installer.iss` | 2.6 KB |
| `starter_package/updater.py` | (size n/a — deleted) |
| `starter_package/version.py` | 6 B |

Pre-deletion grep confirmed 0 functional references in repo proper. Historical context preserved inside `commons/` submodule docs (`phase-1-completion-packet.md`, `phase-3-report.md` etc. document the port of starter_package's updater + GUI patterns into commons). CHANGELOG.md updated from forward-looking "Pending — deletion planned" to retrospective "Removed — deleted at Wave 8b B7 per Decision #2". Zero runtime / build / test impact.

---

## 9. Financials / auth / domain preserved-local

Verified at B6 audit (7 files clean-diff vs main): `git diff main -- <file>` returned 0 lines for each:

- `project_tracker_backend.py` (2,317 LOC) — `ProjectRecord`, `ProjectTrackerBackend`, `PHOENIX_TASKS`, `parse_currency`, change-order logic, RSS export, all job/task data models
- `financials_dashboard.py` (405 LOC) — financial-summary UI
- `financials_dialog.py` (333 LOC) — financial entry/edit dialogs
- `financials_excel.py` (413 LOC) — openpyxl + pyxlsb integration; Excel import/export
- `financials_models.py` (69 LOC) — financial data structures
- `user_auth.py` (381 LOC) — admin/user authentication; `UserManager`, `AuthStoreError`, password hashing
- `generate_guide.py` (256 LOC) — help/guide generator

**B10 functional proof:** the frozen exe successfully loaded 57 records from `.xlsb` via openpyxl + pyxlsb at runtime — confirms the Excel hidden-import chain survived PyInstaller bundling.

`tests/test_regressions.py` (441 LOC, 29 tests) preserved verbatim. Imports of `UpdatePackageError`, `_validate_update_zip`, `_build_update_powershell_script` from local `updater` all resolve correctly (hybrid-facade pattern).

---

## 10. Remaining intentional debt

| Item | Disposition |
|------|-------------|
| `_validate_update_zip` + `_build_update_powershell_script` preserved-local | required by test surface; permanent |
| Repo-root `phoenix_style.qss` overlay | actively appended for app-specific selectors; permanent |
| `UpdateBanner` 🆕 emoji dropped | commons-canonical wording; operator-accepted |
| `.venv312/` untracked at repo root | dev artifact; `.gitignore` pattern doesn't catch suffix-named variant; non-blocking |
| `ProjectTrackingTool.spec` minor divergence | spec has `upx=True` + lacks `--collect-all=phoenix_commons` + lacks stdlib excludes; affects only ad-hoc spec-based builds; canonical pipeline (build.bat) unaffected |
| AppId absence in installer.iss | **NOT debt** — hard preservation rule (Decision #8); permanent |

None are merge-blockers (already resolved by the merge).

---

## 11. Remote push results

| Push | Result |
|------|--------|
| `git push origin main` (Job Tracker) | `0eaed43..6a0d60b  main -> main` ✅ |
| `git push origin job-tracker-retrofit-v1.8.5-pre` | `[new tag] job-tracker-retrofit-v1.8.5-pre -> job-tracker-retrofit-v1.8.5-pre` ✅ |
| `git push origin phase-8b-job-tracker-retrofit:phase-8b-job-tracker-retrofit` | `[new branch] phase-8b-job-tracker-retrofit -> phase-8b-job-tracker-retrofit` ✅ |
| Commons MIGRATION_RULES + closure report | (pending in this session) |

`.venv312/` not staged at any point (correctly excluded as dev artifact).

---

## 12. Recommended next phase

**Wave 8b closes the production-tool retrofit series** (Phase 3A Phoenix CAD → Phase 3B Phoenix Checkout → Wave 8a ValveMaster → Wave 8b Job Tracker — all 4 deployed production tools now commons-backed).

Suggested follow-up directions (operator-prioritized):

1. **Optional documentation cleanup:** retire any remaining "Phase 8b retrofit planned" forward-looking notes in commons docs (`OPERATIONAL_STABILIZATION_REPORT_01.md`, `BLOCKERS.md` § 8b row, etc.) and convert to retrospective status.
2. **Asset naming proposal execution:** PCC and Job Tracker still use legacy "PTT_" / "PCC_" prefixed icon files (`PTT_Normal.ico`, `PTT_Transparent.png`); audit + rename is documented in `ASSET_NAMING_PROPOSAL.md` but deferred from Wave 8b scope.
3. **`StatCard` promotion candidate:** Job Tracker has a local `StatCard(QFrame)` widget that's similar in shape to PCC's `AggregateTile` — promotion to commons needs two-consumer evidence per MIGRATION_RULES § 0.
4. **Phase 6C / 6D continuation:** the deferred frozen-exe dogfood + installer round-trip cycles from `FROZEN_BUILD_BASELINE.md` are unblocked by the family's commons-readiness.
5. **Wave 9 candidates:** Phoenix Command Center polish, additional Lucide-icon expansion, or operator-chosen platform improvements.

No production deployment is gated by Wave 8b's merge.

---

## 13. Confirmation

- **No domain logic changed** — `project_tracker_backend.py`, `financials_*.py × 4`, `user_auth.py`, `generate_guide.py` all 0-diff vs main pre-merge (B6 audit)
- **No financials changed** — frozen-exe-proven via 57-record .xlsb load
- **No auth changed** — `user_auth.py` 0-diff vs main; admin role behavior preserved
- **No `version.py` change** — stays at `1.8.5`
- **No production deployment** — no installer uploaded, no frozen exe distributed
- **No GitHub Release** — none drafted, none published
- **No AppId added** — Decision #8 hard rule preserved (existing v1.6.0..v1.8.5 user base safe)
- **No install path / user-data / updater zip / exe name drift**
- **No commons API change** — Wave 8b consumed existing commons API; zero new primitives
- **No `BrandProfile` change** — uses commons `DEFAULT_BRAND` per Decision #10

---

*End of Phase 8B Job Tracker closure report. Wave 8b merged + remote-stable on 2026-05-28. All 4 production tools in the Phoenix family are now commons-backed.*
