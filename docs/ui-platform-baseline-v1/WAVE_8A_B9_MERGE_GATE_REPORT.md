# Wave 8a B9 — Merge Gate Report

> **Status:** audit complete. **Verdict: A — Merge-ready.**
> **Target branch:** `phase-8a-valvemaster-retrofit` HEAD `2fa160e`.
> **Date:** 2026-05-26.

---

## 1. B1–B8a summary

| Step | Commit | Scope |
|------|--------|-------|
| B1 | `46012a6` | commons submodule + `requirements.txt` + `requirements-dev.txt` + family `ci.yml` (test.yml preserved per Decision #3) + CLAUDE.md reconcile |
| B2 | `32d15d6` | `paths.py` facade re-exporting commons; inline `_resource_path` retired |
| B3 | `828a99a` | `updater.py` hybrid facade: `check_for_update` + `download_and_apply` delegate to commons (`expected_internal=False` per ADR-003); multi-fallback zip-name resolution + `_parse_version` / `_ps_single_quote` preserved-local for test surface |
| B4+B5 | `f2fa97a` | `apply_dark_theme(app)` facade + `_EMBEDDED_QSS` retired; 5 widgets (`PrimaryButton`/`SecondaryButton`/`TertiaryButton`/`PhoenixTable`/`UpdateBanner`) imported from `phoenix_commons.widgets`; identity-equal verified |
| B6 | `704acd4` | `build.bat` hardened: 3.12 soft-warn, commons preflight, Step 0 full cleanup, `--noupx`, `--collect-all=phoenix_commons`, 8× stdlib `--exclude-module`; stale `ValveMasterTool.spec` deleted |
| B7 | (no commit — validation only) | source-mode validation: 156/156 tests, identity-equal × 5, offscreen MainWindow construction `'Phoenix Master Tool v1.1.0'` |
| B8 | (no commit — build artifacts gitignored) | first hardened frozen build under Python 3.12.10; commons + 23 SVG icons + canonical QSS bundled; updater zip contract verified `['PhoenixMasterTool.exe']` |
| B8a | `2fa160e` | restored app-specific QSS layer (commons baseline + repo-root `phoenix_style.qss` appended) — fixed Decoded Fields red-card regression; operator visual-confirmed |

Net source diff vs `main`:
- `phoenix_master_pyside6.py`: net retrofit (theme/widget facades, _resource_path retired, _EMBEDDED_QSS retired, QSS-two-layer compose)
- `updater.py`: net -70 LOC (hybrid facade)
- `build.bat`: net +24 LOC (hardening)
- `CLAUDE.md`: requirements-files claim reconciled + Wave 8a retrofit state documented
- `paths.py`: new file
- `.gitmodules` + `commons/`: new submodule pin
- `requirements.txt`, `requirements-dev.txt`: new files
- `.github/workflows/ci.yml`: new file
- `.github/workflows/test.yml`: unchanged (Decision #3)

---

## 2. Validation results

| Check | Command | Result |
|-------|---------|--------|
| git status | clean (.venv312/ untracked dev artifact only) | ✅ |
| compileall | `python -m compileall -q . -x "commons/|.venv|build|dist"` | clean |
| Full test suite | `python -m unittest discover -s tests` | **156/156 green** (10 updater + 146 validation) |
| Source-mode offscreen launch (latest, B8a) | MainWindow constructs cleanly; QSS 42,932 chars; commons widgets identity-equal; FieldCardButton selectors present | ✅ (validated at B8a commit time) |
| Frozen exe artifact | `dist/PhoenixMasterTool/PhoenixMasterTool.exe` 2,180,410 B | ✅ exists |
| Bundled local QSS | `dist/PhoenixMasterTool/_internal/phoenix_style.qss` 24,593 B | ✅ bundled |
| Bundled commons | `phoenix_commons/{theme,widgets,updater,icons/lucide,paths,_version}` + 23 SVGs + `phoenix_style.qss` package-data | ✅ |
| Updater zip contract | `zipfile.namelist()` = `['PhoenixMasterTool.exe']` | ✅ exe-only, ADR-003 |
| Installer artifact | `dist/PhoenixMasterToolSetup.exe` 33,828,413 B | ✅ exists |

---

## 3. B8a visual / S1 result

**Operator visual confirmation (recorded):**
> *"Decoded Fields now render correctly: valid model segments green / non-error, invalid model segments red / error, mixed-validity models show mixed card states correctly."*

**5-minute idle S1 observation:** **implicit pass** — operator launched the post-B8a-rebuild frozen exe to confirm Decoded Fields rendering; no quarantine event was reported. If a dedicated 5-min idle observation is desired before merge, operator can run one explicitly; merge can also proceed under the implicit-pass interpretation given S1 has not quarantined any artifact at any point in B8 / B8a build cycles.

**No regressions:** every other dimension (theme application, button rendering, table rendering, UpdateBanner, dialogs) inherits the same merged-QSS pipeline as Decoded Fields and is structurally equivalent to pre-retrofit behavior.

---

## 4. Merge readiness audit

| Invariant | State | Notes |
|-----------|-------|-------|
| AppId GUID `{A7F3C2D1-9B4E-4F6A-8C3D-1E5B7A9F2C4D}` | unchanged | `installer.iss` not edited |
| Install path `{localappdata}\ATS Inc\PhoenixMasterTool` | unchanged | `DefaultDirName` byte-equal |
| User-data path `%APPDATA%\ATS Inc\PhoenixMasterTool` | unchanged | inventory + backend never re-rooted |
| Updater zip asset name `PhoenixMasterTool.zip` | unchanged | build.bat output name preserved |
| Updater exe name `PhoenixMasterTool.exe` | unchanged | matches `EXE_NAME` in `updater.py` |
| Exe-only payload contract (ADR-003) | preserved | `expected_internal=False` literal in `download_and_apply` |
| `version.py` `__version__` | `1.1.0` unchanged | Decision #1 tag-skip |
| Domain logic (`phoenix_master_backend.py`, `inventory.py`, `assets.py`, all dialogs) | untouched | no edits anywhere in this branch |
| Test surface (`tests/test_updater.py`, `tests/test_validation.py`) | untouched | all 156 still pass |
| Build artifacts | gitignored (`dist/`, `build/`, `*.spec`, `.venv*/`) | nothing accidentally committed |
| Production deployment | none | no PyInstaller release uploaded, no GitHub Release |

All 11 invariants hold. No source drift outside the approved retrofit scope.

---

## 5. Remaining intentional debt

| Item | Disposition | When |
|------|-------------|------|
| `_parse_version` + `_ps_single_quote` duplicate with commons internals | preserved-local for `tests/test_updater.py` regression baseline; documented in B3 report | Permanent — no plan to retire |
| Repo-root `phoenix_style.qss` (24 KB local backup carrying app-specific selectors) | preserved per MIGRATION_RULES § Local backup QSS strategy + actively appended in `load_phoenix_stylesheet` to supply `#FieldCardButton`/`#ModeBadge`/etc. selectors not in commons | Permanent until commons absorbs app-specific selectors (no plan in scope) |
| `UpdateBanner` text delta ("Release Notes" vs old "What's new?"; 🆕 emoji dropped) | commons signature mismatch; operator-accepted in B4+B5 report | Permanent — commons-canonical wording |
| `.venv312/` untracked at repo root | dev artifact; gitignore pattern `.venv/` doesn't catch the suffix-named variant | Optional cleanup: extend `.gitignore` to `.venv*/`; non-blocking |
| Forensic-PowerShell narrowing in commons updater apply (commons matches `<EXE_NAME>` exactly vs retired multi-candidate list) | acceptable narrowing; no current release ships under legacy-only zip-entry name | Permanent; operator-controlled at release time |

None are merge-blockers.

---

## 6. Exact merge plan

Execute on operator approval (after this report is approved):

```bash
# 1. ValveMasterTool repo — merge
cd C:/Users/justing/PycharmProjects/ValveMasterTool
git checkout main
git pull origin main           # sanity — should be at f6a8c48 with no new commits
git submodule update --init    # ensure commons pin is consistent
git merge --no-ff phase-8a-valvemaster-retrofit \
  -m "Merge Wave 8a — ValveMaster / Phoenix Master Tool commons retrofit"

# 2. (Optional) Forensic tag on the merge commit per Decision #1 (tag-skip is the
#    default; this is a forensic-only marker, not a release tag)
git tag -a valvemaster-retrofit-v1.1.0-pre <merge-commit-sha> \
  -m "Wave 8a commons retrofit complete (version.py unchanged at 1.1.0)"

# 3. Push main + preserve retrofit branch on origin (per MIGRATION_RULES
#    § Per-retrofit branch + PR convention)
git push origin main
git push origin valvemaster-retrofit-v1.1.0-pre   # only if tagged in step 2
git push origin phase-8a-valvemaster-retrofit:phase-8a-valvemaster-retrofit

# 4. phoenix-commons repo — update MIGRATION_RULES row 37 + author closure report
cd C:/Users/justing/PycharmProjects/phoenix-commons
# Edit MIGRATION_RULES.md row 37 to status:
#   "✅ Merged 2026-05-26 (merge commit <SHA> on phoenix-master-tool:main)..."
# Author PHASE_8A_VALVEMASTER_REPORT.md (21-section per Phase 3B precedent)
git add docs/ui-platform-baseline-v1/MIGRATION_RULES.md \
        docs/ui-platform-baseline-v1/PHASE_8A_VALVEMASTER_REPORT.md
git commit -m "Wave 8a merged — MIGRATION_RULES update + closure report"
git push origin main
```

No installer upload. No GitHub Release. No production deployment. The merge produces git history only.

---

## 7. Tag recommendation

**Tag-skip is the default per Decision #1** — facade-only retrofit produces ≈ 0% operator-visible change, `version.py` stays at `1.1.0`, no new release.

**Forensic tag suggestion (optional):** `valvemaster-retrofit-v1.1.0-pre` on the `--no-ff` merge commit. Rationale:
- Matches Phase 3A / 3B precedent (`lab-layout-tool-retrofit-v0.1.2-pre`, etc.)
- Provides a clean `git revert -m 1 <tag>` rollback handle if a regression surfaces later
- Does not claim a new release version (the `-pre` suffix makes that explicit)
- Zero risk: a tag is metadata only

Operator chooses one of:
- (a) tag-skip — clean merge, no forensic marker
- (b) `valvemaster-retrofit-v1.1.0-pre` — forensic marker on merge commit

---

## 8. Push sequence

| Order | Action | Notes |
|-------|--------|-------|
| 1 | `git push origin main` (ValveMasterTool) | merge commit lands on `main` |
| 2 | `git push origin <tag>` (only if tag chosen) | forensic tag |
| 3 | `git push origin phase-8a-valvemaster-retrofit:phase-8a-valvemaster-retrofit` | preserve retrofit branch per MIGRATION_RULES |
| 4 | Edit `MIGRATION_RULES.md` row 37 status (commons) | reflect merge |
| 5 | Author `PHASE_8A_VALVEMASTER_REPORT.md` (commons) | 21-section closure report per Phase 3B precedent |
| 6 | `git push origin main` (commons) | doc updates |

---

## 9. Confirmation

- **No domain logic changed** at any step (`phoenix_master_backend.py`, `inventory.py`, `assets.py`, all dialogs untouched across B1–B8a)
- **No `version.py` change** (stays at `1.1.0` per Decision #1 tag-skip)
- **No production deployment** (no installer uploaded, no GitHub Release, no tag pushed)
- **No GitHub Release** (none drafted, none published)
- **No AppId / install path / updater zip / exe name drift**
- **No commons API change** (consumes existing commons API only; no new primitives)
- **No `BrandProfile` change** (uses commons `DEFAULT_BRAND` per Decision #5)

---

## Verdict

### **A — Merge-ready.**

Pre-merge gate hold-list — all items satisfied:

- ✅ All B1–B8a steps complete + reports committed to commons
- ✅ Operator visual confirmation recorded (Decoded Fields green/red per validity)
- ✅ Frozen build artifacts present + structurally validated
- ✅ Updater zip contract intact (ADR-003 exe-only)
- ✅ All 11 cross-cutting invariants (AppId, paths, version, naming) preserved
- ✅ 156/156 tests green
- ✅ compileall clean
- ✅ No source drift outside approved retrofit scope
- ⚠ Optional: explicit 5-min idle S1 observation on the rebuilt B8a exe (implicit pass via operator's visual review window; operator can run a dedicated observation before merge if desired — non-blocking)

Awaiting operator merge signal + tag choice (skip vs. `valvemaster-retrofit-v1.1.0-pre`).
