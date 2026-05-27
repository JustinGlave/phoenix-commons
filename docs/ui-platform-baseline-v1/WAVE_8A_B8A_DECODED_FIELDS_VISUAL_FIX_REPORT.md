# Wave 8a B8a — Decoded Fields Visual Fix Report

> **Status:** fix committed + frozen build rebuilt. Operator visual confirmation deferred to interactive desktop.
> **Commit:** `2fa160e` on `ValveMasterTool:phase-8a-valvemaster-retrofit`.
> **Date:** 2026-05-26.

---

## 1. Root cause

B4's switch from local-disk QSS loading to `phoenix_commons.theme.apply_dark_theme(app)` dropped every ValveMaster-specific object-name selector. Commons' canonical QSS only carries generic System A rules (`QMainWindow`, `QPushButton`, `QLineEdit`, etc.). The local repo-root `phoenix_style.qss` carries app-specific selectors that have **no equivalent** in commons:

- `#FieldCardButton` with `[invalid="true"]` and `[editable="true"]` validity variants
- `#ModeBadge`, `#ProductBadge`, `#ValidationBadge`
- `#ValidationIssueRow` / `#ValidationIssueField` / `#ValidationIssueMessage`
- `#SectionCard` / `#HeaderCard` / `#CalcHeader`

Without these selectors, `ClickableFieldCard` (`objectName="FieldCardButton"`) fell back to the generic `QPushButton` red-primary rule (`#dc2626` from DEFAULT_BRAND), painting every Decoded Fields card red — independent of the `invalid` dynamic property. The property mechanism itself was working correctly; only the QSS selectors were missing.

---

## 2. Files changed

| File | Change |
|------|--------|
| `phoenix_master_pyside6.py` | +27 / -17 (`load_phoenix_stylesheet` body grew from 1-line `apply_dark_theme(app)` to a 2-layer compose; re-added `from paths import resource_path` import) |

No other files touched. Domain logic, updater, build.bat, installer.iss, version.py, commons API all unchanged.

---

## 3. Exact fix

Two-layer QSS composition:

```python
def load_phoenix_stylesheet(app: QApplication) -> None:
    """Apply the Phoenix Controls dark-navy theme.

    Two-layer composition:
      1. commons apply_dark_theme(app) for System A baseline
      2. repo-root phoenix_style.qss appended for app-specific selectors
    """
    apply_dark_theme(app)
    try:
        with open(resource_path("phoenix_style.qss"), "r", encoding="utf-8") as fh:
            app.setStyleSheet(app.styleSheet() + "\n" + fh.read())
    except OSError:
        pass
```

- Commons applies first: Fusion style + canonical QPalette + generic Phoenix widget QSS with DEFAULT_BRAND sentinel substitution.
- Local QSS appends second: adds app-specific object-name rules. Where it overlaps with commons selectors, Qt's "later wins" rule applies — but the overlapping rules are byte-equal (verified pre-flight audit), so the result is identical.
- If repo-root QSS is unreadable (partial install), commons baseline alone applies — app remains usable, only app-specific validity/badge styling reverts to defaults.

---

## 4. Source-mode validation

| Check | Result |
|-------|--------|
| `compileall -q phoenix_master_pyside6.py` | clean |
| Merged stylesheet length | 42,932 chars (commons ≈ 19k + local ≈ 24k) |
| `#FieldCardButton` base selector | present |
| `#FieldCardButton[invalid="true"]` | present |
| `#FieldCardButton[editable="true"]` | present |
| Invalid-state color `#ef4444` | present |
| Neutral card bg `#141829` | present |
| DEFAULT_BRAND brand colors `#dc2626` + `#3b82f6` | present |
| Sentinel residue (`__BRAND_PRIMARY__`) | absent |
| `#SectionCard` / `#ValidationBadge` | both present |
| `ClickableFieldCard(invalid=False).property("invalid")` | `'false'` (will receive non-red treatment) |
| `ClickableFieldCard(invalid=True).property("invalid")` | `'true'` (will receive red treatment) |
| `tests/test_updater.py` + `tests/test_validation.py` | 156/156 green |

---

## 5. Frozen-build rerun result

Rebuilt under `.venv312` (Python 3.12.10):

| Artifact | Size | Δ from B8 |
|----------|------|-----------|
| `dist/PhoenixMasterTool/PhoenixMasterTool.exe` | ~2.08 MB | within 1 KB |
| `dist/PhoenixMasterTool/_internal/phoenix_style.qss` | 24,593 B | **present** (bundled by `--add-data` flag already in build.bat — no flag change) |
| `dist/PhoenixMasterTool/_internal/phoenix_commons/...` | unchanged | commons bundle identical to B8 |
| `dist/PhoenixMasterToolSetup.exe` | 33.83 MB | +5 KB |
| `dist/PhoenixMasterTool.zip` (updater payload) | 1.95 MB | +2 KB |
| `dist/PhoenixMasterTool_FullInstall.zip` | 46.80 MB | +1.5 KB |

Updater zip contract verified: contents are `['PhoenixMasterTool.exe']` only — ADR-003 exe-only payload preserved.

---

## 6. S1 / visual confirmation status

- **Build-time S1 quarantine:** none observed; all 4 artifacts persisted on disk after build completed.
- **5-min interactive S1 observation:** deferred to operator (different Windows session/window-station).
- **Visual confirmation that Decoded Fields renders green/red correctly:** deferred to operator on interactive desktop.

The structural evidence (QSS selectors present, dynamic property mechanism working, local QSS bundled in `_internal/`, frozen exe produced without errors) gives high confidence the regression is fixed. Operator visual review at the merge gate confirms.

---

## 7. Confirmation

- No domain validation logic changed (validation_issues computation in `phoenix_master_backend` untouched)
- No model decoding rules changed
- No `ClickableFieldCard` implementation changed (the property mechanism was already correct)
- No commons API changes (commons-side selectors not added; fix is local-side composition only)
- No `updater.py` changes (B3 facade preserved at `828a99a`)
- No widget retrofit changes (B4+B5 facades preserved at `f2fa97a`)
- No `build.bat` changes (B6 hardening preserved at `704acd4`; the rebuild used the existing hardened pipeline as-is)
- No `installer.iss` changes (AppId `{A7F3C2D1-9B4E-4F6A-8C3D-1E5B7A9F2C4D}` preserved)
- No `version.py` change (stays at `1.1.0`)
- No production deployment (artifacts in `dist/` are dev-build only; no GitHub Release; no upload)

Branch HEAD: `2fa160e`. Operator visual confirmation → B9 merge gate.
