# Wave 8b B11 — Merge Gate Report

> **Status:** audit complete. **Verdict: A — Merge-ready.**
> **Target branch:** `phase-8b-job-tracker-retrofit` HEAD `d7212cc`.
> **Date:** 2026-05-28.

---

## 1. B1–B10 summary

| Step | Commit | Scope |
|------|--------|-------|
| B1 | `cc7acdb` | commons submodule + `requirements-dev.txt` + `requirements.txt -e ./commons` + ci.yml minor edit + CLAUDE.md retrofit note |
| B2 | `949675d` | `paths.py` facade (Path-returning wrapper around commons); inline `_resource_path` retired; `_app_data_path` + `_backup_data_file` preserved-local |
| B3 | `33fd3d9` | `updater.py` hybrid facade: `check_for_update` + `download_and_apply` delegate to commons (`expected_internal=True`); `UpdatePackageError` re-exported from commons; `_validate_update_zip` + `_build_update_powershell_script` preserved-local for test surface |
| B4+B5 | `6c70acf` | `apply_phoenix_theme` body → `apply_dark_theme(app)` + two-layer overlay; `_EMBEDDED_QSS` retired (~116 LOC); repo-root `phoenix_style.qss` rewritten with Job-Tracker overlay (former Checkout-leftover content superseded); 5 widgets (PrimaryButton/SecondaryButton/TertiaryButton/PhoenixTable/UpdateBanner) imported from commons; identity-equal verified |
| B6+B7 | `45d26f7` | preserved-local audit (7 files clean-diff vs main) + `starter_package/` deletion (8 files via `git rm -r`) + CHANGELOG.md retrospective |
| B8+B9 | `d7212cc` | `build.bat` hardened: 3.12 soft-warn, commons preflight, Step 0 full cleanup, `--noupx`, `--collect-all=phoenix_commons`, 8× stdlib `--exclude-module`; preserved sanity checks + Excel hidden imports + zip layout verify + Inno Setup; .spec preserved (entry correct) |
| B10 | (no commit — build artifacts gitignored) | Frozen build under Python 3.12.10; 5 artifacts produced; commons + 23 SVGs + canonical QSS bundled; updater zip = full-folder (260 entries); offscreen liveness 5+ sec; financials_excel functional (57 records loaded from .xlsb) |

Net source diff vs `main`:
- `project_tracker_gui.py`: -156 LOC net (5 widgets + _EMBEDDED_QSS retired, theme facade body + commons imports added)
- `updater.py`: hybrid facade (preserved test-surface helpers)
- `build.bat`: +32 LOC hardening flags
- `phoenix_style.qss`: rewritten (Checkout-leftover → Job-Tracker overlay)
- `paths.py`: new facade
- `CLAUDE.md`: retrofit-state section + early-open override
- `CHANGELOG.md`: retrospective starter_package removal note
- `requirements.txt`: appended `-e ./commons`
- `requirements-dev.txt`: new
- `.gitmodules` + `commons/`: new submodule
- `.github/workflows/ci.yml`: minor edits (submodules:recursive + reqs-dev + commons import smoke)
- `starter_package/`: 8 files deleted

---

## 2. Operator B10 frozen exe / S1 result

**✅ PASSED (operator-confirmed 2026-05-28).** Operator launched `dist\ProjectTrackingTool\ProjectTrackingTool.exe` on interactive desktop, observed 5 minutes:

- Process stayed alive throughout the window
- Exe remained on disk (no S1 quarantine)
- No crash
- No missing resources
- Visual change ≈ 0%
- Buttons / tables / theme rendered correctly
- Financials surfaces showed no obvious launch-time regression
- Auth surfaces showed no obvious launch-time regression

Recorded in `WAVE_8B_B10_FROZEN_BUILD_S1_REPORT.md` §§ 8–9.

---

## 3. Validation results

| Check | Command | Result |
|-------|---------|--------|
| Branch state | `git branch --show-current` | `phase-8b-job-tracker-retrofit` ✅ |
| Working tree | `git status` | clean (`.venv312/` untracked build artifact only) ✅ |
| compileall | `python -m py_compile <10 files>` | clean ✅ |
| Full test suite | `python -m unittest discover -s tests` | **29/29 green** ✅ |
| `version.py` | `"1.8.5"` | unchanged ✅ |
| `installer.iss` AppId | absent | preserved (Decision #8) ✅ |
| `installer.iss DefaultDirName` | `{localappdata}\ATS Inc\Project Tracking Tool` | unchanged ✅ |
| `installer.iss OutputBaseFilename` | `ProjectTrackingToolSetup` | unchanged ✅ |
| `updater.py` `GITHUB_OWNER` / `GITHUB_REPO` | `JustinGlave` / `project-tracking-tool` | unchanged ✅ |
| `updater.py` `EXE_NAME` / `ZIP_ASSET_NAME` | `ProjectTrackingTool.exe` / `ProjectTrackingTool.zip` | unchanged ✅ |
| `expected_internal=True` in facade body | literal `True` | preserved ✅ |
| Frozen build artifacts (from B10) | 5 artifacts present | exe 3.15 MB / installer 37.3 MB / updater zip 54.8 MB / full-install zip 54.8 MB ✅ |
| Updater zip contract | 260 entries, exe + `_internal/` at root | full-folder (ADR-003) ✅ |
| Operator S1 observation | 5 min idle, no quarantine | ✅ |
| Operator visual review | ≈ 0% visible change | ✅ |

---

## 4. Merge readiness audit

| Invariant | State | Notes |
|-----------|-------|-------|
| AppId GUID absence | preserved | `installer.iss` not edited; v1.6.0..v1.8.5 users' AppName-hashed default preserved per Decision #8 hard rule |
| AppName "Project Tracking Tool" | unchanged | `installer.iss #define MyAppName` |
| Install path `{localappdata}\ATS Inc\Project Tracking Tool` | unchanged | `DefaultDirName` byte-equal |
| User-data path `%APPDATA%\ATS Inc\Project Tracking Tool` | unchanged | `_app_data_path()` preserved-local |
| Updater zip asset name `ProjectTrackingTool.zip` | unchanged | build.bat output name preserved |
| Updater exe name `ProjectTrackingTool.exe` | unchanged | matches `EXE_NAME` in `updater.py` |
| Full-folder payload contract (ADR-003) | preserved | `expected_internal=True` literal in `download_and_apply` |
| `version.py` `__version__` | `1.8.5` unchanged | Decision #1 tag-skip |
| Test surface (`tests/test_regressions.py`) | untouched | 29/29 still pass |
| Domain logic | untouched | `project_tracker_backend.py`, financials_*.py, `user_auth.py`, `generate_guide.py` — 0-diff vs main (B6 audit) |
| Excel/PDF runtime deps | preserved | `openpyxl` + `pyxlsb` + `reportlab` pinned in `requirements.txt`; hidden imports + `--collect-submodules=openpyxl` + `--add-data="pyxlsb;pyxlsb"` intact in build.bat (B6 audit + B10 functional proof: 57 records loaded from .xlsb in frozen exe) |
| Build artifacts | gitignored (`dist/`, `build/`, `*.spec`, `.venv*/`) | nothing committed |
| Production deployment | none | no PyInstaller release uploaded, no GitHub Release |

All 13 invariants hold. No source drift outside the approved retrofit scope.

---

## 5. Remaining intentional debt

| Item | Disposition | When |
|------|-------------|------|
| `_validate_update_zip` + `_build_update_powershell_script` preserved-local | required by `tests/test_regressions.py` import surface; identical hybrid pattern to Wave 8a `_parse_version` / `_ps_single_quote` | permanent — no plan to retire |
| Repo-root `phoenix_style.qss` as Job-Tracker app-specific overlay | actively appended in `apply_phoenix_theme` to supply selectors not in commons (`#StatCard`, `#taskToolsButton`, `#FinDataMeta`, `#ResizeHandle`, `#PassBadge`, etc.) | permanent until commons absorbs app-specific selectors (no plan in scope) |
| `UpdateBanner` 🆕 emoji dropped | commons signature does not include the emoji prefix; operator-accepted via B10 visual pass | permanent — commons-canonical wording |
| `.venv312/` untracked at repo root | dev artifact; matches Wave 8a pattern; `.gitignore` `.venv/` doesn't catch the suffix-named variant | optional cleanup later; non-blocking |
| `ProjectTrackingTool.spec` minor divergence | spec has `upx=True` (build.bat uses `--noupx`) + lacks `--collect-all=phoenix_commons` + lacks stdlib excludes | preserved per "if still correct, leave alone"; affects only ad-hoc spec-based builds; canonical pipeline (build.bat) unaffected |
| AppId absent in installer.iss | **NOT** debt — it's a hard preservation rule (Decision #8). Adding one would break upgrade detection for v1.6.0..v1.8.5 users. |

None are merge-blockers.

---

## 6. Exact merge plan

Execute on operator approval (after this report is approved):

```bash
# 1. Job Tracker repo — merge
cd "C:/Users/justing/PycharmProjects/Job Tracker"
git checkout main
git pull origin main           # sanity — confirm no drift since branch creation
git submodule update --init    # ensure commons pin is consistent
git merge --no-ff phase-8b-job-tracker-retrofit \
  -m "Merge Wave 8b — Job Tracker / Project Tracking Tool commons retrofit"

# 2. (Optional) Forensic tag on the merge commit per Decision #1 (tag-skip is the
#    default; this is a forensic-only marker, not a release tag)
git tag -a job-tracker-retrofit-v1.8.5-pre <merge-commit-sha> \
  -m "Wave 8b commons retrofit complete (version.py unchanged at 1.8.5). \
Forensic rollback marker only; not a release tag."

# 3. Push main + preserve retrofit branch on origin (per MIGRATION_RULES
#    § Per-retrofit branch + PR convention)
git push origin main
git push origin job-tracker-retrofit-v1.8.5-pre   # only if tagged in step 2
git push origin phase-8b-job-tracker-retrofit:phase-8b-job-tracker-retrofit

# 4. phoenix-commons repo — update MIGRATION_RULES row 38 + author closure report
cd C:/Users/justing/PycharmProjects/phoenix-commons
# Edit MIGRATION_RULES.md row 38 status:
#   "✅ Merged 2026-05-28 (merge commit <SHA> on project-tracking-tool:main)..."
# Author PHASE_8B_JOB_TRACKER_REPORT.md (21-section per Phase 3B/Wave 8a precedent)
git add docs/ui-platform-baseline-v1/MIGRATION_RULES.md \
        docs/ui-platform-baseline-v1/PHASE_8B_JOB_TRACKER_REPORT.md
git commit -m "Wave 8b merged — MIGRATION_RULES update + closure report"
git push origin main
```

No installer upload. No GitHub Release. No production deployment. The merge produces git history only.

---

## 7. Tag recommendation

**Tag-skip is the default per Decision #1** — facade-only retrofit produces ≈ 0% operator-visible change, `version.py` stays at `1.8.5`, no new release.

**Forensic tag suggestion (optional):** `job-tracker-retrofit-v1.8.5-pre` on the `--no-ff` merge commit. Rationale:
- Matches Phase 3A / 3B / Wave 8a precedent (`lab-layout-tool-retrofit-v0.1.2-pre`, `valvemaster-retrofit-v1.1.0-pre`, etc.)
- Provides a clean `git revert -m 1 <tag>` rollback handle if a regression surfaces later
- The `-pre` suffix makes "not a release tag" explicit
- Zero risk: tag is metadata only

Operator chooses one of:
- (a) tag-skip — clean merge, no forensic marker
- (b) `job-tracker-retrofit-v1.8.5-pre` — forensic marker on merge commit

---

## 8. Push sequence

| Order | Action | Notes |
|-------|--------|-------|
| 1 | `git push origin main` (Job Tracker) | merge commit lands on `main` |
| 2 | `git push origin <tag>` (only if tag chosen) | forensic tag |
| 3 | `git push origin phase-8b-job-tracker-retrofit:phase-8b-job-tracker-retrofit` | preserve retrofit branch per MIGRATION_RULES |
| 4 | Edit `MIGRATION_RULES.md` row 38 status (commons) | reflect merge |
| 5 | Author `PHASE_8B_JOB_TRACKER_REPORT.md` (commons) | 21-section closure per precedent |
| 6 | `git push origin main` (commons) | doc updates |

---

## 9. Confirmation

- **No domain logic changed** (`project_tracker_backend.py`, `financials_*.py`, `user_auth.py`, `generate_guide.py` all clean-diff vs main from B6 audit)
- **No financials changed** (verified: frozen exe loaded 57 records from .xlsb + persisted financial snapshot)
- **No auth changed**
- **No `version.py` change** (stays at `1.8.5` per Decision #1 tag-skip)
- **No production deployment** (no installer uploaded, no GitHub Release, no tag pushed)
- **No GitHub Release** (none drafted, none published)
- **No AppId added** (Decision #8 hard rule preserved)
- **No install path / user-data / updater zip / exe name drift**
- **No commons API change** (consumes existing commons API only)
- **No `BrandProfile` change** (uses commons `DEFAULT_BRAND` per Decision #10)

---

## Verdict

### **A — Merge-ready.**

Pre-merge hold-list — all items satisfied:

- ✅ B1–B10 complete + reports committed to commons
- ✅ Operator interactive S1 observation passed (5 min idle, no quarantine)
- ✅ Operator visual review passed (≈ 0% change, buttons/tables/theme correct, financials + auth surfaces clean)
- ✅ Frozen build artifacts present + functionally validated
- ✅ Updater zip contract intact (full-folder, 260 entries — ADR-003)
- ✅ All 13 cross-cutting invariants preserved (AppId absence, paths, version, naming, deps)
- ✅ 29/29 tests green
- ✅ compileall clean
- ✅ No source drift outside approved retrofit scope

Awaiting operator merge signal + tag choice (skip vs. `job-tracker-retrofit-v1.8.5-pre`).
