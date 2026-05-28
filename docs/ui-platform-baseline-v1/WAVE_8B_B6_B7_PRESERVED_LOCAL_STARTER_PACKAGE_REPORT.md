# Wave 8b B6+B7 — Preserved-Local Audit + starter_package Deletion Report

> **Status:** B6+B7 committed (lean combined session).
> **Commit:** `45d26f7` on `phase-8b-job-tracker-retrofit`.
> **Date:** 2026-05-28.

---

## 1. Files changed

| File | Change |
|------|--------|
| `starter_package/CLAUDE.md` | deleted |
| `starter_package/app_backend.py` | deleted |
| `starter_package/app_gui.py` | deleted |
| `starter_package/build.bat` | deleted |
| `starter_package/installer.iss` | deleted |
| `starter_package/updater.py` | deleted |
| `starter_package/version.py` | deleted |
| `starter_package/gitignore.txt` | deleted |
| `CHANGELOG.md` | retrospective note (was "Pending — deletion planned", now "Changed/Removed — deleted at Wave 8b B7 per Decision #2") |

Net: 9 files changed, +12 / -1,304.

---

## 2. Preserved-local audit result

All 7 preserved-local files confirmed **unmodified** on `phase-8b-job-tracker-retrofit` vs `main` (`git diff main -- <file>` returns 0 lines for each):

| File | Diff vs main |
|------|--------------|
| `project_tracker_backend.py` | clean |
| `financials_dashboard.py` | clean |
| `financials_dialog.py` | clean |
| `financials_excel.py` | clean |
| `financials_models.py` | clean |
| `user_auth.py` | clean |
| `generate_guide.py` | clean |

**Excel / PDF dependency surface preserved:**

- `requirements.txt` pins intact: `openpyxl==3.1.5`, `pyxlsb==1.0.10`, `reportlab==4.4.10`
- `build.bat` hidden imports intact: `--add-data="pyxlsb;pyxlsb"`, `--hidden-import=openpyxl`, `--hidden-import=openpyxl.cell._writer`, `--collect-submodules=openpyxl`, `--hidden-import=pyxlsb`

No changes required. No commons migration proposed for any preserved-local symbol.

---

## 3. starter_package deletion confirmation

### Pre-deletion grep

Single reference in Job Tracker repo proper: `CHANGELOG.md:18` (forward-looking note). All other matches were inside `commons/` submodule docs (historical port-source context — no runtime dependency on the directory existing).

| Reference type | Count in repo proper |
|----------------|----------------------|
| Python import | 0 |
| build.bat reference | 0 |
| installer.iss reference | 0 |
| test reference | 0 |
| Live doc requiring it as code | 0 |
| Forward-looking note | 1 (CHANGELOG.md — retired in this commit) |

### Deletion

```
$ git rm -r starter_package/
rm 'starter_package/CLAUDE.md'
rm 'starter_package/app_backend.py'
rm 'starter_package/app_gui.py'
rm 'starter_package/build.bat'
rm 'starter_package/gitignore.txt'
rm 'starter_package/installer.iss'
rm 'starter_package/updater.py'
rm 'starter_package/version.py'
```

`__pycache__` entries also removed by git rm.

### Post-deletion state

```
$ grep -rE "starter_package" --exclude-dir=commons .
./CHANGELOG.md:- `starter_package/` directory — historical Phoenix-tool scaffold
```

The lone remaining reference is the new retrospective CHANGELOG entry documenting the deletion. Zero functional references. Zero runtime / build / test risk.

---

## 4. Validation results

| Check | Result |
|-------|--------|
| `git diff main -- <preserved-local files>` × 7 | all clean ✅ |
| `py_compile` across 11 preserved-local + facade files | clean ✅ |
| `tests/test_regressions.py` | **29/29 green** ✅ |
| `grep -r starter_package` post-deletion (excl commons/) | 1 retrospective CHANGELOG entry only ✅ |
| Post-commit tree | clean ✅ |

---

## 5. Blockers / issues

None.

---

## 6. Next step

**B8 — build.bat hardening** (per WAVE_8B_IMPLEMENTATION_BRIEF.md § B8):

- Add Python 3.12 soft-warn
- Add `phoenix_commons` import preflight
- Add Step 0 full cleanup (`rmdir /s /q dist build`)
- Add to PyInstaller: `--noupx`, `--collect-all=phoenix_commons`, 8× stdlib `--exclude-module`
- Preserve existing sanity checks (README version + py_compile + unittest), `--hidden-import=openpyxl/pyxlsb`, `--collect-submodules=openpyxl`, post-build zip layout verify, Inno Setup compilation, full-install zip generation, signing hooks (if any)
- Delete stale `ProjectTrackingTool.spec` from disk if present

---

## 7. Confirmation

- No domain logic changed (`project_tracker_backend.py` / financials_*.py / `user_auth.py` / `generate_guide.py` all 0-diff vs main)
- No financials changed
- No auth changed
- No updater changed (B3 facade preserved at `33fd3d9`)
- No `build.bat` changed (B8 will harden)
- No `installer.iss` changed — **AppId still NOT declared** per Decision #8 hard rule
- No `version.py` change (stays at `1.8.5`)
- No production deployment

Branch HEAD: `45d26f7`. Ready for **B8 (build.bat hardening)**.
