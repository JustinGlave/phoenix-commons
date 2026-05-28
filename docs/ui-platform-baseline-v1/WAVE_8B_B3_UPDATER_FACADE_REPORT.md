# Wave 8b B3 — updater.py Hybrid Facade Report

> **Status:** B3 committed on `phase-8b-job-tracker-retrofit`.
> **Commit:** `33fd3d9` (parent `949675d` — B2).
> **Date:** 2026-05-28.

---

## 1. Files changed

| File | Change | Delta |
|------|--------|-------|
| `updater.py` | modified | +169 / -231 (net **-62 LOC**) |

No other files touched.

---

## 2. Facaded symbols

### Re-exported from commons (identity preserved)

| Symbol | Commons source | Verified |
|--------|----------------|----------|
| `UpdateInfo` | `phoenix_commons.updater.UpdateInfo` | `updater.UpdateInfo is cu.UpdateInfo` ✅ |
| `UpdatePackageError` | `phoenix_commons.updater.installer.UpdatePackageError` | `updater.UpdatePackageError is ci.UpdatePackageError` ✅ |

### Facade wrappers

| Symbol | Public signature | Commons delegation |
|--------|------------------|---------------------|
| `check_for_update()` | `() -> Optional[UpdateInfo]` | `_commons_check_for_update(owner=GITHUB_OWNER, repo=GITHUB_REPO, current_version=__version__, zip_asset_name=ZIP_ASSET_NAME)` |
| `download_and_apply(info, progress_callback=None)` | unchanged | `_commons_download_and_apply(info, exe_name=EXE_NAME, expected_internal=True, progress_callback=progress_callback)` |

---

## 3. Preserved-local symbols

Per MIGRATION_RULES § 1 hybrid facade — preserved-local for the `tests/test_regressions.py` regression baseline:

| Symbol | Why local |
|--------|-----------|
| `_parse_version(tag)` | Returns `None` on unparseable (vs commons `(0,)`); Job Tracker depends on the soft-skip behavior. |
| `_validate_update_zip(zip_path)` | Single-arg signature; commons equivalent is `(zip_path, exe_name, *, expected_internal=True)` — different API shape. Tests use the single-arg form. |
| `_build_update_powershell_script(zip_path, install_dir, exe_path)` | 3-arg signature; commons equivalent is `_build_full_folder_powershell(zip_path, install_dir, exe_path, exe_name)` — different API shape. |
| `_ps_literal(value)` | Private helper consumed by `_build_update_powershell_script`. |

### Naming constants (extracted to module top)

| Constant | Value |
|----------|-------|
| `GITHUB_OWNER` | `"JustinGlave"` |
| `GITHUB_REPO` | `"project-tracking-tool"` |
| `EXE_NAME` | `"ProjectTrackingTool.exe"` |
| `ZIP_ASSET_NAME` | `"ProjectTrackingTool.zip"` |

### Retired (replaced by commons)

- Local urllib API fetch + parse in `check_for_update` body
- Local zip-asset preference scanning (semantic narrowing: commons matches `ProjectTrackingTool.zip` exactly; the retired "any non-fullinstall.zip" fallback is dropped — no current release ships under non-canonical names)
- Local `tempfile` + chunked download loop in `download_and_apply`
- Local PowerShell + .bat orchestration in `download_and_apply` body (commons' `_build_full_folder_powershell` + `_build_full_folder_batch` are used internally)
- Local `_build_update_batch` (commons-internal equivalent now used)
- Local `sys.frozen` guard at top of `download_and_apply` (commons enforces the same)

---

## 4. `expected_internal=True` confirmation

Critical ADR-003 contract: Project Tracking Tool ships a **full-folder** updater zip (exe + `_internal/` runtime folder).

```python
def download_and_apply(info: UpdateInfo, progress_callback=None) -> None:
    ...
    _commons_download_and_apply(
        info,
        exe_name=EXE_NAME,
        expected_internal=True,   # ADR-003 — full-folder payload
        progress_callback=progress_callback,
    )
```

Literal kwarg present. Commons honors via:
- **Validation step** (`_validate_update_zip` with `expected_internal=True`): asserts `<EXE_NAME>` exists at zip root **or** inside top-level `ProjectTrackingTool/` AND `_internal/` exists at the same level.
- **Apply step**: writes a separate `.ps1` (full-folder PowerShell) + `.bat` wrapper; extracts to a staging dir, copies the whole folder over the install dir, relaunches.

This is the opposite of Wave 8a's exe-only payload (`expected_internal=False`). Decision #3 in the production-inventory cross-tool asymmetry.

---

## 5. Updater zip / exe contract

| Element | Value | Preserved? |
|---------|-------|------------|
| Zip asset | `ProjectTrackingTool.zip` | ✅ unchanged |
| Updater exe | `ProjectTrackingTool.exe` | ✅ unchanged |
| Payload contract | full-folder (exe + `_internal/`) | ✅ ADR-003 |
| GitHub owner | `JustinGlave` | ✅ |
| GitHub repo | `project-tracking-tool` | ✅ |
| Local `_validate_update_zip` enforces | `ProjectTrackingTool.exe` flat-or-nested + `_internal/` flat-or-nested | ✅ (preserved-local for tests) |
| Commons `_validate_update_zip` enforces (via facade) | same shape | ✅ |

Both validation paths are functionally equivalent. The local one stays callable for tests; the facade path runs at production update time.

---

## 6. Validation results

| Check | Result |
|-------|--------|
| Pre-flight clean tree | ✅ on `phase-8b-job-tracker-retrofit` |
| `py_compile updater.py` | clean ✅ |
| `UpdateInfo` identity | `updater.UpdateInfo is phoenix_commons.updater.UpdateInfo` ✅ |
| `UpdatePackageError` identity | `updater.UpdatePackageError is phoenix_commons.updater.installer.UpdatePackageError` ✅ |
| Symbols importable from `updater` | `UpdateInfo`, `UpdatePackageError`, `check_for_update`, `download_and_apply`, `_parse_version`, `_validate_update_zip`, `_build_update_powershell_script`, `GITHUB_OWNER`, `GITHUB_REPO`, `EXE_NAME`, `ZIP_ASSET_NAME` ✅ |
| `tests/test_regressions.py` | **29/29 green** ✅ |
| Post-commit tree | clean ✅ |

---

## 7. Blockers / issues

None. Two observations:

1. **Semantic narrowing in `check_for_update`** — commons matches `ProjectTrackingTool.zip` exactly. The retired local logic also had a "any non-fullinstall.zip" fallback. No current release uses non-canonical names; if a future release ever does, the fallback can be reintroduced locally without touching commons.

2. **`_parse_version` semantic difference** — local returns `None` on unparseable; commons returns `(0,)`. The local soft-skip semantic is preserved (Job Tracker's behavior). Tests assume the local semantic.

---

## 8. Confirmation

- No app logic changed (GUI / backend / financials / auth / generate_guide / paths.py / starter_package all untouched)
- No UI / theme changed
- No `build.bat` changed (B8 will harden)
- No `installer.iss` changed — **AppId still NOT declared** per Decision #8 hard rule
- No `version.py` change (stays at `1.8.5`)
- `starter_package/` untouched (B7 will delete)
- No production deployment

Branch HEAD: `33fd3d9`. Ready for **B4 (theme facade + two-layer QSS compose)**.
