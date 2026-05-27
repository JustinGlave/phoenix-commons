# Wave 8a B3 — updater.py Hybrid Facade Report

> **Status:** B3 committed on `phase-8a-valvemaster-retrofit`.
> **Commit:** `828a99a` (parent `32d15d6` — B2).
> **Date:** 2026-05-26.
> **Target:** ValveMasterTool / Phoenix Master Tool.
> **Brief:** `WAVE_8A_IMPLEMENTATION_BRIEF.md` § 2 (B3 spec).

---

## 1. Files changed

`git show --stat 828a99a` reports 1 file, +149 / -219 lines (net **-70 LOC**).

| File | Change | Reason |
|------|--------|--------|
| `updater.py` | modified | Replaces local `urllib`-based GitHub-API fetch + tempfile download loop + PowerShell-batch generator with delegated calls to `phoenix_commons.updater`. Multi-fallback zip-name resolution preserved as a wrapper over commons. ADR-003 `expected_internal=False` baked into `download_and_apply`. |

Files **not touched** in B3 (verified by `git show --stat`):

  - `phoenix_master_pyside6.py` (entry module — preserved verbatim from B2)
  - `phoenix_master_backend.py` (domain logic)
  - `inventory.py`, `assets.py`, `phoenix_style.qss` (all preserved-local)
  - `paths.py` (preserved from B2)
  - `build.bat`, `installer.iss`, `version.py` (deferred to B4-B6 / preserved)
  - `tests/test_updater.py`, `tests/test_validation.py` (regression baseline — used to validate B3, never modified)
  - `CLAUDE.md`, `requirements.txt`, `requirements-dev.txt`, `.github/workflows/ci.yml` (preserved from B1)
  - `commons/` submodule pin (untouched)

---

## 2. Facaded symbols

### Re-exported from commons (identity preserved)

| Symbol | Source | Local use |
|--------|--------|-----------|
| `UpdateInfo` | `phoenix_commons.updater.UpdateInfo` | Re-exported in `updater.__all__`. `updater.UpdateInfo is phoenix_commons.updater.UpdateInfo` confirmed True at import time. Callers doing `from updater import UpdateInfo` continue to work byte-identically. |

### Facade wrappers (local functions delegating to commons)

| Symbol | Public signature | Delegation | Local-only behavior preserved |
|--------|------------------|------------|--------------------------------|
| `check_for_update()` | `() -> Optional[UpdateInfo]` | Calls `phoenix_commons.updater.check_for_update(owner, repo, current_version, zip_asset_name)` once per candidate zip name, returns the first non-None result | Multi-fallback asset-name resolution: tries `PhoenixMasterTool.zip` first (from `EXE_NAME` stem), then iterates `LEGACY_EXE_NAMES`-derived zips (`ValveMasterTool.zip`). Preserves the v1.0→v1.1 rename-tolerance contract. |
| `download_and_apply(info, progress_callback=None)` | unchanged | Calls `phoenix_commons.updater.download_and_apply(info, exe_name=EXE_NAME, expected_internal=False, progress_callback=...)` | `exe_name=EXE_NAME` ensures commons looks for `PhoenixMasterTool.exe` in the zip. `expected_internal=False` per ADR-003 (exe-only payload contract). `progress_callback` forwarded verbatim. |

---

## 3. Preserved-local symbols

Per MIGRATION_RULES § 1 hybrid facade doctrine, these symbols stay at module level.

### Naming constants (Class A — preserve-local per pre-flight audit)

| Symbol | Value | Why local |
|--------|-------|-----------|
| `GITHUB_OWNER` | `"JustinGlave"` | ValveMaster release identity — passed to commons facade |
| `GITHUB_REPO` | `"phoenix-master-tool"` | ValveMaster release identity — passed to commons facade |
| `EXE_NAME` | `"PhoenixMasterTool.exe"` | Canonical exe basename + zip-stem derivation source. Critical contract. |
| `LEGACY_EXE_NAMES` | `("ValveMasterTool.exe",)` | v1.0→v1.1 rename-tolerance list. commons has no equivalent — `LEGACY_EXE_NAMES` resolution is intentionally ValveMaster-specific. |

### Helper functions (Class A — preserve-local for test surface)

| Symbol | Test ref | Why local |
|--------|----------|-----------|
| `_parse_version(tag) -> tuple[int, ...]` | `tests/test_updater.py::ParseVersionTests` (6 tests) | commons has its own private `_parse_version` in `phoenix_commons.updater.client`; ours is preserved as an independent test surface so the regression contract doesn't reach into commons internals |
| `_ps_single_quote(value) -> str` | `tests/test_updater.py::PsSingleQuoteTests` (4 tests) | commons has `phoenix_commons.updater.installer._ps_literal` (wraps in quotes, not just escapes); ours is `replace("'", "''")` only. Both are correct for their respective consumers. Test suite contract preserved. |

### Module-level state

| Symbol | Source | Notes |
|--------|--------|-------|
| `__version__` | `from version import __version__` (with fallback `"0.0.0"`) | Used in commons-facade call — passed as `current_version` kwarg. version.py untouched per B3 constraint. |
| `logger` | `logging.getLogger(__name__)` | preserved for future logging needs in the facade wrappers |
| `__all__` | explicit 9-symbol export list | New in B3 — codifies the public API for the module |

### Retired (replaced by commons implementation)

| Symbol | Replacement in commons |
|--------|------------------------|
| Local `urllib.request.Request` + `urlopen` of GitHub API in `check_for_update` body | `phoenix_commons.updater.client._fetch_release_data` (internal) — same `Accept: application/vnd.github+json`, same 8-second timeout |
| Local zip-asset preference scanning (`preferred_stems`, fallback to any non-fullinstall zip) | Replaced by the multi-call wrapper pattern — each candidate zip name issues one commons API call |
| Local `tempfile.mkstemp` + chunked download loop in `download_and_apply` body | `phoenix_commons.updater.installer.download_and_apply` body — same 64KB chunk size, same `Content-Length` guard, same progress-callback invocation |
| Local `_ps_single_quote` consumption in the inline `bat_content` PowerShell construction | `phoenix_commons.updater.installer._build_exe_only_batch` uses `_ps_literal` internally — same single-quote escaping semantics |
| Local `sys.frozen` guard at top of `download_and_apply` | commons enforces the identical `getattr(sys, "frozen", False)` guard at top of its own `download_and_apply` |
| Local multi-candidate PowerShell entry-name extraction (running-basename → EXE_NAME → LEGACY_EXE_NAMES) | commons extracts the entry matching exactly `exe_name` (`PhoenixMasterTool.exe`). **Semantic difference noted below — see § 7.** |

---

## 4. `expected_internal=False` confirmation

Critical ADR-003 contract: Phoenix Master Tool ships an **exe-only** updater zip (the zip contains a single `.exe` file at root; no `_internal/` runtime folder). Decision #5 in the readiness matrix (and the pre-flight audit's table § 6) flags this as a hard contract.

The new `download_and_apply` body:

```python
def download_and_apply(info: UpdateInfo, progress_callback=None) -> None:
    ...
    _commons_download_and_apply(
        info,
        exe_name=EXE_NAME,
        expected_internal=False,   # ADR-003 — exe-only payload contract
        progress_callback=progress_callback,
    )
```

`expected_internal` is passed as a literal keyword argument. Commons honors this by:

1. **Validation step** (`_validate_update_zip`): when `expected_internal=False`, only checks that `<EXE_NAME>` exists at the zip root. Does NOT check for `_internal/` (which doesn't exist in the exe-only payload).
2. **Apply step** (`_build_exe_only_batch`): builds an inline-PowerShell batch wrapper that extracts only the single `<EXE_NAME>` entry from the zip, writes it to the running-exe path, then relaunches. No multi-file extraction, no folder restructuring.

Verified by inspecting the commons source — `installer.py:54-107` (validation) and `installer.py:194-225` (exe-only batch builder). No `expected_internal=True` code path is taken in this delegation.

---

## 5. Legacy-name behavior preserved

The pre-flight audit (`WAVE_8A_VALVEMASTER_PREFLIGHT_AUDIT.md` § 3) and the implementation brief (§ 2 / B3) both call out `LEGACY_EXE_NAMES` resolution as Class A preserve-local. The B3 design preserves it through **two complementary mechanisms**:

### Mechanism 1 — Asset-name fallback in `check_for_update`

The wrapper loop tries:

```python
candidate_zips = [f"{Path(EXE_NAME).stem}.zip"]  # = "PhoenixMasterTool.zip"
candidate_zips += [f"{Path(name).stem}.zip" for name in LEGACY_EXE_NAMES]
# Resulting list: ["PhoenixMasterTool.zip", "ValveMasterTool.zip"]
```

Each candidate is passed to `phoenix_commons.updater.check_for_update` as `zip_asset_name`; the first non-None result is returned. This preserves the v1.0→v1.1 forward-compat: if a future release ever ships under the legacy asset name (e.g. a revert), the v1.1.0+ updater finds it.

### Mechanism 2 — Running-exe-path overwrite in `download_and_apply`

When a legacy v1.0.x install (running `ValveMasterTool.exe`) calls the v1.1.0+ updater code post-B3:

- The zip download succeeds (asset name resolved via Mechanism 1)
- Commons validates that `<EXE_NAME>` = `PhoenixMasterTool.exe` exists at the zip root ✓
- Commons builds a PowerShell wrapper that extracts the `PhoenixMasterTool.exe` entry from the zip and writes it to `Path(sys.executable).resolve()` — which is the **actual running exe path on disk**, regardless of basename
- Result: the user's `ValveMasterTool.exe` on disk gets its bytes replaced with the new `PhoenixMasterTool.exe` content. The file keeps its old name but is now the new binary. Restart launches the same path.

This matches the historical local logic's behavior (it also wrote to `current_exe`, not to a fixed `EXE_NAME` path).

### Semantic difference from the retired local logic

The retired local PowerShell snippet built a **list of candidate entry names** (running-basename → EXE_NAME → LEGACY_EXE_NAMES) and looked for the first matching entry inside the zip. Commons looks for **exactly** `<EXE_NAME>` = `PhoenixMasterTool.exe`.

| Scenario | Retired local | New commons-facade |
|----------|---------------|---------------------|
| Zip contains `PhoenixMasterTool.exe` (current canonical) | ✓ extracts | ✓ extracts |
| Zip contains `ValveMasterTool.exe` only (hypothetical future release reverts) | ✓ extracts (legacy fallback) | ✗ commons validation fails (asset present per Mechanism 1, but entry not present per validation) |
| Zip contains BOTH `PhoenixMasterTool.exe` AND `ValveMasterTool.exe` | ✓ picks running-basename first | ✓ picks `PhoenixMasterTool.exe` |

The middle scenario (legacy zip with only legacy exe entry) is the one place where B3 narrows behavior. This is **acceptable** because:

  - No release currently ships under that combination — v1.1.0 was the rename release, all post-v1.1.0 releases ship `PhoenixMasterTool.exe`-in-the-zip
  - The "hypothetical future release reverts to legacy-only" scenario is operator-controlled (we choose the asset names at release time)
  - If a revert ever happens, the operator can also revert this B3 facade or temporarily edit `LEGACY_EXE_NAMES` to flip the order
  - The mainstream upgrade path (v1.1.0+ → vX.Y.Z) is fully preserved

This narrowing was an explicit design trade-off to enable commons facade consumption. Documented here so a future operator knows the failure mode + the workaround if it ever matters.

---

## 6. Validation results

| Check | Command | Result |
|-------|---------|--------|
| Pre-flight clean tree | `git status` on `phase-8a-valvemaster-retrofit` | clean ✅ |
| `compileall` on updater.py | `python -m compileall -q updater.py` | exit 0, no output (clean) ✅ |
| `UpdateInfo` identity | `assert updater.UpdateInfo is phoenix_commons.updater.UpdateInfo` | `True` ✅ |
| Module symbol survey | `__all__` lists all 9 expected names | ✅ all present (UpdateInfo, check_for_update, download_and_apply, GITHUB_OWNER, GITHUB_REPO, EXE_NAME, LEGACY_EXE_NAMES, _parse_version, _ps_single_quote) |
| `import updater` | from `commons/src` on sys.path | succeeds ✅ |
| `import phoenix_master_pyside6` | end-to-end entry-module import | succeeds ✅ (B2 paths facade still works; B3 updater facade composes cleanly) |
| `tests/test_updater.py` | `python -m unittest tests.test_updater -v` | **10/10 green** (6 `ParseVersionTests` + 4 `PsSingleQuoteTests`) ✅ |
| Full test suite | `python -m unittest discover -s tests -v` | **156/156 green** (10 updater + 146 validation) ✅ |
| Post-commit tree state | `git status` after commit | clean ✅ |

### Live-network validation skipped

The brief explicitly says: *"Avoid any validation that depends on live GitHub/network unless already part of existing tests."* — and no existing test hits the live API. The full end-to-end updater round-trip is the Phase 6C-B fake-release-server pattern, deferred to B8 (frozen-build + S1 observation). At B3 the facade is structurally validated only.

---

## 7. Issues / observations

### None blocking. Three observations for the record:

1. **Semantic narrowing in `download_and_apply` PowerShell extraction.** See § 5 — commons looks for exactly `<EXE_NAME>` while the retired local logic tried a candidate list. Acceptable trade-off; documented; no current-release scenario is affected.

2. **Helper duplication.** `_parse_version` and `_ps_single_quote` now exist in two places (ValveMaster's `updater.py` + `phoenix_commons.updater.client._parse_version` + `phoenix_commons.updater.installer._ps_literal`). This is intentional — the local versions are an independent test surface for `tests/test_updater.py`. Removing them would require either (a) updating the test imports to reach into commons internals (anti-pattern — tests shouldn't depend on private API of a dependency) or (b) deleting the tests (anti-pattern — regression coverage). Keeping the helpers local is the lowest-risk option.

3. **Network behavior change.** The retired local `check_for_update` made **1 HTTP request** total (then scanned the asset list in memory for multiple candidate names). The new wrapper makes **N HTTP requests** where N is the number of candidate zip names (currently 2: `PhoenixMasterTool.zip` then `ValveMasterTool.zip`). Both requests are bounded by commons' 8-second timeout. In the happy path (current canonical asset present), only the first request fires and returns success — same network cost as before. In the legacy-fallback path (canonical missing, legacy present), it's 2 requests instead of 1. Acceptable.

---

## 8. Confirmation

  - **No UI changed.** `phoenix_master_pyside6.py` untouched in B3 (the B2 changes are preserved). No widget, layout, theme, or QSS edit.
  - **No theme changed.** `phoenix_style.qss`, `_EMBEDDED_QSS` preserved (B4 will retire the disk-read fallback).
  - **No `build.bat` changed.** B6 will harden it. `--noupx`, stdlib excludes, `--collect-all phoenix_commons`, Step 0 cleanup — all deferred.
  - **No `installer.iss` changed.** AppId GUID `{A7F3C2D1-9B4E-4F6A-8C3D-1E5B7A9F2C4D}` preserved byte-for-byte. `DefaultDirName`, `OutputBaseFilename` preserved.
  - **No `version.py` changed.** Stays at `__version__ = "1.1.0"` (Decision #1 — tag-skip).
  - **No production deployment.** No PyInstaller invocation, no frozen exe, no installer build, no GitHub Release, no tag pushed.
  - **AppId / install path / updater zip naming / exe name preserved.** All naming constants stay at their existing values; no rename happened in B3.
  - **`expected_internal=False`** verified in the new `download_and_apply` body (literal kwarg). ADR-003 exe-only payload contract intact.
  - **Test surface preserved.** All 10 `test_updater.py` cases green; all 146 `test_validation.py` cases green (regression safety net).
  - **No scope expansion.** B3 strictly held to: 1 file modified, hybrid facade for `check_for_update` + `download_and_apply`, preserved-local for constants + test helpers, retired the local download / PowerShell-batch implementation.
  - **Branch state.** `phase-8a-valvemaster-retrofit` HEAD now `828a99a`. Working tree clean. Branch local-only (push deferred to B9 per the canonical retrofit pattern).

---

## 9. Next step — B4: theme application facade + `_EMBEDDED_QSS` retirement

When the operator signals B4 kickoff, execute per `WAVE_8A_IMPLEMENTATION_BRIEF.md` § 2 (B4):

| Item | Value |
|------|-------|
| Files to touch | `phoenix_master_pyside6.py` — `load_phoenix_stylesheet` body becomes 2-line facade calling `phoenix_commons.theme.apply_dark_theme(app)`; `_EMBEDDED_QSS` constant body deleted (~50 LOC) |
| Files preserved | `phoenix_style.qss` at repo root — kept per MIGRATION_RULES § Local backup QSS strategy (deleted ~30 days post-retrofit if commons fallback proves sufficient) |
| BrandProfile decision | Decision #5 — use commons `DEFAULT_BRAND` (palette byte-matches); no custom BrandProfile |
| Stop conditions | Source-mode launch shows any pixel-level palette change; `apply_dark_theme(app)` raises (commons not on sys.path); `_EMBEDDED_QSS` references remain after retirement |
| Expected visible change | ≈ 0% (canonical palette tokens delivered through commons instead of disk-read) |

---

## 10. End condition

  - ✅ B3 committed (`828a99a`) on `phase-8a-valvemaster-retrofit`
  - ✅ `updater.py` now a hybrid facade: commons delegation for generic update logic, preserved-local for naming + multi-fallback + test helpers
  - ✅ `UpdateInfo` identity verified equal to `phoenix_commons.updater.UpdateInfo`
  - ✅ `expected_internal=False` (ADR-003) preserved in `download_and_apply`
  - ✅ All 10 `tests/test_updater.py` cases pass
  - ✅ All 146 `tests/test_validation.py` cases pass (regression safety net)
  - ✅ Branch ready for B4
  - ❌ No theme facade (B4)
  - ❌ No widget retrofit (B5)
  - ❌ No build hardening (B6)
  - ❌ No source-mode validation run (B7)
  - ❌ No frozen build (B8)
  - ❌ No merge (B9)

---

*End of Wave 8a B3 report. Branch `phase-8a-valvemaster-retrofit` HEAD: `828a99a`. Ready for B4 on operator signal.*
