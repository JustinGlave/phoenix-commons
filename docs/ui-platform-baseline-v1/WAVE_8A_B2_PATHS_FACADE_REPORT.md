# Wave 8a B2 — paths.py Facade Report

> **Status:** B2 committed on `phase-8a-valvemaster-retrofit`.
> **Commit:** `32d15d6` (parent `46012a6` — B1).
> **Date:** 2026-05-26.
> **Target:** ValveMasterTool / Phoenix Master Tool.
> **Brief:** `WAVE_8A_IMPLEMENTATION_BRIEF.md` § 2 (B2 spec).

---

## 1. Files changed

`git show --stat 32d15d6` reports 2 files, +49 / -10 lines.

| File | Change | Size delta |
|------|--------|------------|
| `paths.py` | **new** | +45 lines (docstring + 3 imports + `__all__` + `_TOOL_ROOT` constant + `resource_path` wrapper) |
| `phoenix_master_pyside6.py` | modified | +3 / -10 (removed 7-LOC inline `_resource_path` helper; added 1-line `from paths import resource_path`; changed 1 call site by dropping the leading `_`) |

Files **not touched** in B2 (verified by `git show --stat`):

  - `phoenix_master_backend.py` (domain logic — 169 KB)
  - `inventory.py` (SharePoint parts catalog)
  - `assets.py` (base64-embedded brand PNGs)
  - `phoenix_style.qss` (System A canonical palette — still on disk; B4 retires the disk-read path)
  - `updater.py` (B3 will hybrid-facade)
  - `build.bat` (B6 will harden)
  - `installer.iss` (AppId GUID `{A7F3C2D1-9B4E-4F6A-8C3D-1E5B7A9F2C4D}` preserved)
  - `version.py` (stays at `1.1.0`; Decision #1 tag-skip)
  - `ValveMasterTool.spec` (B6 will delete — dead code)
  - `.github/workflows/test.yml` + `.github/workflows/ci.yml` (preserved from B1)
  - `requirements.txt` + `requirements-dev.txt` (preserved from B1)
  - `CLAUDE.md` (preserved from B1)
  - `tests/test_updater.py` + `tests/test_validation.py` (regression baseline)

---

## 2. Exact facade shape

`paths.py` is a thin local facade — pure re-export for `is_frozen` and `user_data_dir`, plus a minimal wrapper for `resource_path` to preserve the historical call-site shape.

```python
"""Phoenix Master Tool — local paths facade.

Re-exports commons path helpers and binds the tool-specific source-tree
``base`` for ``resource_path`` so call sites can use the historical
``resource_path(filename) -> str`` shape (byte-identical to the
``_resource_path`` helper this file retires at Wave 8a B2).

[full docstring elided in this report — see source]
"""

from __future__ import annotations
from pathlib import Path

from phoenix_commons.paths import is_frozen, user_data_dir
from phoenix_commons.paths import resource_path as _commons_resource_path

__all__ = ["is_frozen", "user_data_dir", "resource_path"]

_TOOL_ROOT: Path = Path(__file__).resolve().parent


def resource_path(filename: str) -> str:
    """Resolve a bundled-resource path. Frozen-aware via commons."""
    return str(_commons_resource_path(filename, base=_TOOL_ROOT))
```

### Why a wrapper (not a pure re-export)

The implementation brief's literal spec was *"pure re-export"*. Inspection of the commons API revealed a behavior-preservation issue with that approach:

| Helper | Source-mode `resource_path('phoenix_style.qss')` |
|--------|---------------------------------------------------|
| Retired local `_resource_path(filename)` | `os.path.join(os.path.dirname(os.path.abspath(__file__)), filename)` → repo-root + filename, `str` return |
| Commons `phoenix_commons.paths.resource_path(filename, base=None)` (pure re-export, no base) | `Path(filename)` (cwd-relative — breaks if cwd ≠ repo root) |
| Commons `phoenix_commons.paths.resource_path(filename, base=_TOOL_ROOT)` (B2 wrapper) | `Path(_TOOL_ROOT) / filename` → repo-root + filename, wrapped in `str()` for return-type parity |

The wrapper binds `_TOOL_ROOT = Path(__file__).resolve().parent` where `__file__` is `paths.py` at the repo root — identical resolution to the retired helper (which used `__file__` = `phoenix_master_pyside6.py`, also at the repo root). Frozen-mode behavior is unchanged (commons honors `_MEIPASS` first regardless of `base`).

### Why `str()` wrap

Commons `resource_path` returns `Path`; the retired helper returned `str`. `open(...)` accepts both, but a `str()` wrapper keeps the return type byte-identical for any downstream consumer that may stringify, concatenate, or pass to a `str`-only API. Zero risk, zero behavior change.

### Call-site diff

```diff
-def _resource_path(filename: str) -> str:
-    """Resolve a bundled-asset path that works both in dev and in PyInstaller bundles."""
-    if getattr(sys, "frozen", False):
-        base = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
-    else:
-        base = os.path.dirname(os.path.abspath(__file__))
-    return os.path.join(base, filename)
-
-
 def load_phoenix_stylesheet(app: QApplication) -> None:
     """Load the Phoenix Controls QSS file, falling back to the embedded copy
     if the file isn't bundled with the installation (e.g. a partial update)."""
     app.setStyle("Fusion")
-    qss_path = _resource_path(QSS_FILENAME)
+    qss_path = resource_path(QSS_FILENAME)
     try:
         with open(qss_path, "r", encoding="utf-8") as fh:
             app.setStyleSheet(fh.read())
     except OSError:
         app.setStyleSheet(_EMBEDDED_QSS)
```

Plus an import added near the other first-party imports:

```diff
 )

+from paths import resource_path
+
 from phoenix_master_backend import (
     APP_NAME,
     PRODUCT_DISPLAY_NAMES,
```

---

## 3. `_resource_path` retirement details

### Pre-B2 audit (per the pre-flight audit § 3)

Predicted: 1 definition site + 1 caller site, both in `phoenix_master_pyside6.py`.

### B2 confirmation

Confirmed by grep across the ValveMaster repo proper (excluding `commons/` submodule):

```
$ rg -n '_resource_path' --glob '!commons/**' --glob '*.py'
phoenix_master_pyside6.py:138:def _resource_path(filename: str) -> str:
phoenix_master_pyside6.py:151:    qss_path = _resource_path(QSS_FILENAME)
```

Exactly 2 sites. No site missed.

### Post-B2 grep

```
$ rg -n '_resource_path' --glob '!commons/**' --glob '*.py'
paths.py:5:    ``_resource_path`` helper this file retires at Wave 8a B2).
paths.py:35:    ``_resource_path`` helper in ``phoenix_master_pyside6.py``.
```

Two remaining references — both inside `paths.py` docstrings, naming the retired symbol for documentation purposes. Zero functional references remain.

(The other 25 grep hits across the repo are all inside the `commons/` submodule, which is untouched in any retrofit step. Commons has its own internal `_resource_path` symbol in `phoenix_commons.theme.apply` — that's commons' own implementation detail and a separate concept from ValveMaster's retired helper.)

### Behavior preservation

The retired `_resource_path` resolved `phoenix_style.qss` to `<repo>\phoenix_style.qss` in source mode and `<_MEIPASS>\phoenix_style.qss` in frozen mode. The new `paths.resource_path` produces the same two outputs by routing through commons with `base=_TOOL_ROOT`. Verified directly:

```
$ python -c "from paths import resource_path; print(resource_path('phoenix_style.qss'))"
C:\Users\justing\PycharmProjects\ValveMasterTool\phoenix_style.qss
```

---

## 4. Validation results

| Check | Command | Result |
|-------|---------|--------|
| Pre-flight clean tree | `git status` on `phase-8a-valvemaster-retrofit` | clean ✅ |
| `_resource_path` site audit | `Grep` for `_resource_path` excluding commons/ | 2 functional sites found in `phoenix_master_pyside6.py` (line 138 def, line 151 call) ✅ |
| `compileall` on touched files | `python -m compileall -q paths.py phoenix_master_pyside6.py` | exit 0, no output (clean) ✅ |
| Import smoke (3 names) | `from paths import resource_path, is_frozen, user_data_dir; print('paths import OK')` | prints `paths import OK` ✅ |
| `resource_path` resolution | `print(resource_path('phoenix_style.qss'))` | `C:\Users\justing\PycharmProjects\ValveMasterTool\phoenix_style.qss` (byte-identical to retired helper output) ✅ |
| `is_frozen()` in source mode | `print(is_frozen())` | `False` ✅ |
| `user_data_dir` round-trip | `print(user_data_dir('PhoenixMasterTool'))` | `C:\Users\justing\AppData\Roaming\ATS Inc\PhoenixMasterTool` (canonical APPDATA path; creates dir if absent) ✅ |
| Entry-module import | `import phoenix_master_pyside6` | exit 0 (no import-time side-effects regressed) ✅ |
| Post-commit tree state | `git status` after commit | clean ✅ |
| Grep post-B2 — functional refs | `Grep _resource_path --glob *.py` (excluding commons/) | 0 functional refs (2 docstring mentions in paths.py only) ✅ |

### Deferred to B7 source-mode validation

  - Full `pip install -r requirements.txt -r requirements-dev.txt` from a clean Python 3.12 venv (current `.venv/` is Python 3.14)
  - Full `pytest -q tests/` run with PySide6 installed (currently no PySide6 in the venv — import smoke used `sys.path.insert(0, 'commons/src')` for a lightweight check)
  - Actual GUI launch (`python phoenix_master_pyside6.py`) — operator action at B7

The B2 brief's *"pytest if available"* hedge applies here; the deferred items will run at B7 against a fresh 3.12 venv.

---

## 5. Issues / observations

### None blocking. Three observations for the record:

1. **`os` and `sys` imports preserved at top of `phoenix_master_pyside6.py`.** The retired `_resource_path` was the largest consumer of `os.path` in that immediate region, but both `os` and `sys` remain in heavy use elsewhere in the file (e.g. `sys._MEIPASS` at line 219, environment lookups, file-system operations in dialogs). No orphan-import cleanup needed.

2. **Line 219 `BASE_DIR = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))`** is a separate `_MEIPASS`-aware code path inside the module-level `BASE_DIR` constant — not consumed by `_resource_path` and not in scope for B2. Will be re-evaluated at later B-steps if it becomes a clean refactor target; otherwise stays as-is per the "preserve domain-adjacent invariants" rule.

3. **`load_phoenix_stylesheet` body is unchanged.** It still does `try: open(qss_path).read() ... except OSError: app.setStyleSheet(_EMBEDDED_QSS)`. B4 retires this entire fallback path (`_EMBEDDED_QSS` constant + the disk-read + the fallback exception handler) by replacing the function body with `apply_dark_theme(app)`. B2 deliberately preserves it.

---

## 6. Confirmation

  - **No UI changed.** No widget, layout, or QSS edit. `load_phoenix_stylesheet` body preserved (B4 will retire it).
  - **No theme changed.** `phoenix_style.qss` unchanged. `_EMBEDDED_QSS` constant unchanged. `apply_dark_theme` not yet called (B4 task).
  - **No updater changed.** `updater.py` unchanged. `UpdateInfo`, `check_for_update`, `download_and_apply` all still local (B3 task). ADR-003 exe-only payload contract preserved.
  - **No `build.bat` changed.** B6 will harden it. PyInstaller flags, `--noupx`, stdlib excludes, `--collect-all phoenix_commons` — all deferred.
  - **No `installer.iss` changed.** AppId GUID `{A7F3C2D1-9B4E-4F6A-8C3D-1E5B7A9F2C4D}` preserved byte-for-byte. `DefaultDirName`, `OutputBaseFilename` preserved.
  - **No production deployment.** No PyInstaller invocation, no frozen exe, no installer build, no GitHub Release, no tag.
  - **No version bump.** `version.py` stays at `__version__ = "1.1.0"` (Decision #1 — tag-skip).
  - **No scope expansion.** B2 strictly held to: 1 facade file + 1 inline helper removal + 1 call-site swap + 1 import insertion.
  - **Branch state.** `phase-8a-valvemaster-retrofit` HEAD now `32d15d6`. Working tree clean. Branch local-only (push deferred to B9 per the canonical retrofit pattern).

---

## 7. Next step — B3: `updater.py` hybrid facade

When the operator signals B3 kickoff, execute per `WAVE_8A_IMPLEMENTATION_BRIEF.md` § 2 (B3):

| Item | Value |
|------|-------|
| Files to touch | `updater.py` (facade body + preserved-local legacy logic) · `tests/test_updater.py` (must stay green) |
| Purpose | Replace local `check_for_update` and `download_and_apply` with commons facades; preserve legacy-name resolution (Class A preserved-local) |
| Critical invariant | `expected_internal=False` per ADR-003 (exe-only payload contract) |
| Stop conditions | `test_updater.py` regresses; legacy-name resolution path touched; `expected_internal` defaults to anything but `False` |
| Expected visible change | None |

---

## 8. End condition

  - ✅ B2 committed (`32d15d6`) on `phase-8a-valvemaster-retrofit`
  - ✅ `paths.py` exists with the documented thin-facade shape
  - ✅ `_resource_path` removed from `phoenix_master_pyside6.py` (0 functional references in repo)
  - ✅ Branch ready for B3
  - ❌ No updater facade (B3)
  - ❌ No theme facade (B4)
  - ❌ No widget retrofit (B5)
  - ❌ No build hardening (B6)

---

*End of Wave 8a B2 report. Branch `phase-8a-valvemaster-retrofit` HEAD: `32d15d6`. Ready for B3 on operator signal.*
