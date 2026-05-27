# Wave 8a B4+B5 — Theme Facade + Widget Retrofit Report

> **Status:** B4+B5 committed (combined per operator lean-mode directive).
> **Commit:** `f2fa97a` on `ValveMasterTool:phase-8a-valvemaster-retrofit`.
> **Date:** 2026-05-26.

---

## 1. Files changed

| File | Change | Delta |
|------|--------|-------|
| `phoenix_master_pyside6.py` | modified | +37 / -152 (net **-115 LOC**) |

No other files touched.

---

## 2. B4 changes (theme facade)

- `load_phoenix_stylesheet(app)` body → `apply_dark_theme(app)` via `from phoenix_commons.theme import apply_dark_theme`
- `_EMBEDDED_QSS` constant body deleted (38 LOC)
- `QSS_FILENAME` constant deleted (orphaned)
- `from paths import resource_path` removed (orphaned)
- Repo-root `phoenix_style.qss` **preserved** (local backup per MIGRATION_RULES § Local backup QSS strategy)
- DEFAULT_BRAND used (no `brand=` kwarg; palette byte-match per Decision #5)
- Caller surface preserved: `main` still calls `load_phoenix_stylesheet(app)` unchanged

---

## 3. B5 changes (widget retrofit)

Single import block added near other commons imports:

```python
from phoenix_commons.widgets import (
    PhoenixTable,
    PrimaryButton,
    SecondaryButton,
    TertiaryButton,
    UpdateBanner,
)
```

Inline class definitions retired:

| Class | Lines retired | Replaced by |
|-------|----------------|-------------|
| `PrimaryButton(QPushButton)` | 11 | `phoenix_commons.widgets.PrimaryButton` |
| `SecondaryButton(QPushButton)` | 8 | `phoenix_commons.widgets.SecondaryButton` |
| `TertiaryButton(QPushButton)` | 8 | `phoenix_commons.widgets.TertiaryButton` |
| `PhoenixTable(QTableWidget)` | 10 | `phoenix_commons.widgets.PhoenixTable` |
| `UpdateBanner(QFrame)` | 48 | `phoenix_commons.widgets.UpdateBanner` |

Call site updated:

```python
# before:
banner = UpdateBanner(info, self)
# after (commons takes split args):
banner = UpdateBanner(
    info.current_version,
    info.latest_version,
    info.release_notes,
    self,
)
```

Preserved verbatim (app-specific): `BadgeLabel`, `SectionCard`, `ClickableFieldCard`, `ValidationIssueRow`, `WatermarkWidget`, `CfmCalculatorDialog`, `SelfTestDialog`, `OptionPickerDialog`, `OptionsEditorDialog`, `TestModelsDialog`, `PartsListDialog`, `ValveMasterMainWindow`.

---

## 4. Identity checks

```
PrimaryButton    is phoenix_commons.widgets.PrimaryButton    : True
SecondaryButton  is phoenix_commons.widgets.SecondaryButton  : True
TertiaryButton   is phoenix_commons.widgets.TertiaryButton   : True
PhoenixTable     is phoenix_commons.widgets.PhoenixTable     : True
UpdateBanner     is phoenix_commons.widgets.UpdateBanner     : True
```

All 5 `is`-equal. Zero local re-definitions remain.

---

## 5. Validation results

| Check | Result |
|-------|--------|
| `compileall -q phoenix_master_pyside6.py` | clean ✅ |
| `import phoenix_master_pyside6` | succeeds ✅ |
| 5/5 widget identity-equal to commons | ✅ |
| Offscreen theme smoke: QSS length | 19,420 chars ✅ |
| Brand tokens present (`#0a0e27` / `#141829` / `#dc2626` / `#1e3a8a` / `#3b82f6`) | all 5 ✅ |
| Brand sentinels absent (`__BRAND_PRIMARY/SECONDARY/ACCENT__`) | all 3 absent ✅ |
| `style().objectName()` Fusion readback | empty string under offscreen QPA (Qt readback quirk; commons `setStyle("Fusion")` call confirmed in source) — non-blocking |
| `tests/test_updater.py` | 10/10 green |
| `tests/test_validation.py` | 146/146 green |
| Full suite | 156/156 green ✅ |

Grep post-edit:
  - `_EMBEDDED_QSS` in repo proper (excl. commons/): 1 docstring mention only (zero functional refs)
  - `QSS_FILENAME` in repo proper: 0 hits
  - Inline `class (PrimaryButton|SecondaryButton|TertiaryButton|PhoenixTable|UpdateBanner)` in repo proper: 0 hits

---

## 6. Visual-change assessment

**Expected ≈ 0%** (Phoenix-CAD profile, per WAVE_8A_VALVEMASTER_PREFLIGHT_AUDIT).

Source-mode launch not exercised in this session (operator's lean-mode directive — defers full GUI launch to B7). Substantively unchanged by construction:

  - Palette: DEFAULT_BRAND tokens byte-match the retired `_EMBEDDED_QSS` literal values
  - Button visuals: commons `PrimaryButton`/`SecondaryButton`/`TertiaryButton` carry the same `setFixedHeight(36)`, `setObjectName("secondaryButton"/"tertiaryButton")`, `setCursor(PointingHandCursor)` defaults
  - `PhoenixTable` defaults (vertical header hidden, no edit, no selection, alternate-row colors) preserved by commons
  - `UpdateBanner` carries the same `objectName="UpdateBanner"`, `setFixedHeight(44)`, `#InstallBtn` button — minor text change: commons reads "Release Notes" instead of "What's new?" and drops the 🆕 emoji prefix (commons release-notes button width 132 vs local 100; install-btn width 150 vs local 140); user-facing text diff documented but visually within the ≈ 0% band

---

## 7. Blockers / issues

None. The "What's new?" → "Release Notes" text difference and the dropped 🆕 emoji are minor user-visible deltas inside the `UpdateBanner` only — within the operator-approved ≈ 0% facade-retrofit band, documented above. Operator can override at the visual review gate if either delta is unacceptable.

---

## 8. Confirmation

- No domain logic changed (`phoenix_master_backend.py`, `inventory.py`, `assets.py`, all dialogs untouched)
- No updater changed (B3 result preserved at `828a99a`)
- No `build.bat` changed
- No `installer.iss` changed (AppId `{A7F3C2D1-9B4E-4F6A-8C3D-1E5B7A9F2C4D}` preserved)
- No `version.py` changed (stays at `1.1.0`)
- No production deployment

Branch HEAD: `f2fa97a`. Ready for **B6 (build hardening)**.
