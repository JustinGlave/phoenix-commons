# Wave 8b B2 — paths.py Facade Report

> **Status:** B2 committed on `phase-8b-job-tracker-retrofit`.
> **Commit:** `949675d` (parent `cc7acdb` — B1).
> **Date:** 2026-05-27.

---

## 1. Files changed

| File | Change | Delta |
|------|--------|-------|
| `paths.py` | **new** | +55 LOC |
| `project_tracker_gui.py` | modified | +6 / -11 (removed 5-LOC inline helper; added 1-line import; 4 call sites updated) |

No other files touched.

---

## 2. Facade shape

Wave 8a B2 pattern with `Path` return type (vs ValveMaster's `str`) to byte-match Job Tracker's retired helper:

```python
from phoenix_commons.paths import is_frozen, user_data_dir
from phoenix_commons.paths import resource_path as _commons_resource_path

__all__ = ["is_frozen", "user_data_dir", "resource_path"]

_TOOL_ROOT: Path = Path(__file__).resolve().parent


def resource_path(filename: str) -> Path:
    """Resolve a bundled-resource path. Frozen-aware via commons.

    Returns the same ``Path`` a caller would have gotten from the retired
    ``_resource_path`` helper in ``project_tracker_gui.py``.
    """
    return _commons_resource_path(filename, base=_TOOL_ROOT)
```

The wrapper binds `_TOOL_ROOT` internally so the 4 call sites stay one-character away from byte-identical (drop the leading `_`).

---

## 3. `_resource_path` retirement

### Pre-B2 audit

5 sites in repo proper: 1 def + 4 callers.

| Line | Site |
|------|------|
| `project_tracker_gui.py:21` (def) | `def _resource_path(filename: str) -> Path` |
| `project_tracker_gui.py:2721` | `_icon_path = _resource_path("PTT_Normal.ico")` |
| `project_tracker_gui.py:2761` | `_BackgroundWidget(_resource_path("PTT_Transparent.png"))` |
| `project_tracker_gui.py:3360` | `_WatermarkViewport(_resource_path("PTT_Transparent.png"))` |
| `project_tracker_gui.py:3648` | `asset_path = _resource_path(asset_name)` |

(`starter_package/app_gui.py` also has its own `_resource_path` — out of scope per Decision #2; will be deleted with the package at B7.)

### Post-B2 grep

```
$ rg -n '_resource_path' --glob 'project_tracker_gui.py'
(no matches)
```

Zero functional references remain in repo proper.

### Behavior preservation

`resource_path('phoenix_style.qss')` returns `C:\Users\justing\PycharmProjects\Job Tracker\phoenix_style.qss` — byte-identical to the retired helper's source-mode output (`Path(__file__).with_name(filename)` evaluated when `__file__ == project_tracker_gui.py`).

Frozen-mode behavior also preserved: commons honors `_MEIPASS` first regardless of `base`.

---

## 4. Preserved-local path helpers

| Symbol | Location post-B2 | Why local |
|--------|-------------------|-----------|
| `_app_data_path()` | `project_tracker_gui.py:23` | Job-Tracker-specific: returns the `data.json` path under `%APPDATA%\ATS Inc\Project Tracking Tool\` + performs one-time legacy-location migration from next-to-exe. Commons `user_data_dir` returns directory only — different shape. |
| `_backup_data_file(data_path)` | `project_tracker_gui.py:38` | Job-Tracker-specific: timestamped backup with 10-file retention. No commons equivalent. |

Caller sites preserved:
- `_app_data_path()` called at lines 3610 + 3691
- `_backup_data_file(data_path)` called at line 3850

All untouched. Domain backup + migration behavior intact.

---

## 5. Validation results

| Check | Result |
|-------|--------|
| Pre-flight clean tree | ✅ on `phase-8b-job-tracker-retrofit` |
| `py_compile paths.py project_tracker_gui.py` | clean ✅ |
| `_resource_path` grep post-edit (repo proper) | 0 functional refs ✅ |
| `from paths import resource_path, is_frozen, user_data_dir` | ✅ |
| `resource_path('phoenix_style.qss')` | `C:\Users\justing\PycharmProjects\Job Tracker\phoenix_style.qss` ✅ |
| `is_frozen()` | `False` (source mode) ✅ |
| `tests/test_regressions.py` | **29/29 green** ✅ |
| Post-commit tree | clean ✅ |

---

## 6. Blockers / issues

None. Two observations:

1. **Return type alignment** — Wave 8a B2 (ValveMaster) wrapped to return `str` because the retired helper there returned `str`. Job Tracker's retired helper returned `Path`, so this facade returns `Path`. Per-tool byte-identity preserved.

2. **`starter_package/app_gui.py` has its own `_resource_path`** — left untouched here per Decision #2; the entire `starter_package/` is deleted in B7.

---

## 7. Confirmation

- No app logic changed
- No UI / theme changed (`_EMBEDDED_QSS` and all widget classes untouched)
- No updater changed (B3 will hybrid-facade)
- No `build.bat` changed (B8 will harden)
- No `installer.iss` changed — **AppId still NOT declared** per Decision #8 hard rule
- No `version.py` changed (stays at `1.8.5`)
- `starter_package/` untouched (B7 will delete)
- No production deployment

Branch HEAD: `949675d`. Ready for **B3 (updater hybrid facade, `expected_internal=True`)**.
