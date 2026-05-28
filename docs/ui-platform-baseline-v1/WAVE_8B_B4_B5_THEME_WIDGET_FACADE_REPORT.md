# Wave 8b B4+B5 — Theme Facade + Widget Retrofit Report

> **Status:** B4+B5 committed (lean combined session).
> **Commit:** `6c70acf` on `phase-8b-job-tracker-retrofit`.
> **Date:** 2026-05-28.

---

## 1. Files changed

| File | Change | Delta |
|------|--------|-------|
| `project_tracker_gui.py` | modified | +85 / -241 (net **-156 LOC**) — _EMBEDDED_QSS retired (~116 LOC), 5 widget classes retired (~80 LOC), apply_phoenix_theme body replaced (+15 LOC), commons import block (+8 LOC), UpdateBanner call site updated (+5 LOC) |
| `phoenix_style.qss` | modified | rewritten — stale Checkout leftover (~894 LOC) replaced with Job-Tracker app-specific overlay (~135 LOC migrated from _EMBEDDED_QSS) |

---

## 2. B4 theme facade summary

- `apply_phoenix_theme(app)` body → `apply_dark_theme(app)` + append `phoenix_style.qss` overlay
- `_EMBEDDED_QSS` constant body deleted
- `# ── Theme ──` section header retired
- DEFAULT_BRAND used (palette byte-matches retired tokens)
- Caller surface preserved: `main` still calls `apply_phoenix_theme(app)` unchanged

---

## 3. App-specific QSS overlay preservation (Decision #9 execution)

**Pre-B4 state of repo-root `phoenix_style.qss`:** mislabeled `"Phoenix Valve Checkout Tool — QSS Stylesheet"` leftover (894 LOC). It carried Checkout-specific selectors (`#CheckoutTag`, `#StepBadge`, `#TagPreview`, `#RowSep`) but **NO** Job-Tracker-specific selectors (`#StatCard`, `#FinDataMeta`, `#taskToolsButton`, `#ResizeHandle`, etc.). It was bundled by build.bat's `--add-data` flag but never loaded at runtime (`apply_phoenix_theme` only consumed `_EMBEDDED_QSS`).

**Post-B4 state:** Overwrote `phoenix_style.qss` with the Job-Tracker-specific QSS extracted verbatim from `_EMBEDDED_QSS` (~135 lines including section header documenting the two-layer compose pattern). The new file carries all 23 Job-Tracker-specific selectors required for the post-B4 rendering:

| Selector | Widget |
|----------|--------|
| `#Panel`, `#StatCard`, `#StatTitle`, `#StatValue` | StatCard widget (preserved-local) |
| `#ProjectTitle`, `#ProjectSubtitle` | project header labels |
| `#SectionTitle`, `#dialogTitle`, `#dialogSubtitle` | section / dialog labels |
| `#FinDataMeta`, `#MetaCaption`, `#MetaValue` | financials labels |
| `#VersionStatus`, `#UpdateBanner`, `#UpdateMsg`, `#InstallBtn`, `#RestoreBtn` | update banner + restore button |
| `#PassBadge`, `#FailBadge`, `#ArchivedBadge` | status badges |
| `#ResizeHandle`, `#VResizeHandle` | resize handles |
| `#taskToolsButton` | task tools dropdown |
| `#Div25Btn`, `#WebProIdBtn` | Div25 / Web Pro action buttons |
| `#ReadOnlyNotes`, `#errorLabel` | notes + error labels |

---

## 4. B5 widget retrofit summary

| Class | Old line | Disposition |
|-------|----------|-------------|
| `PrimaryButton(QPushButton)` | 330 | retired → `phoenix_commons.widgets.PrimaryButton` |
| `SecondaryButton(QPushButton)` | 338 | retired → `phoenix_commons.widgets.SecondaryButton` |
| `TertiaryButton(QPushButton)` | 347 | retired → `phoenix_commons.widgets.TertiaryButton` |
| `PhoenixTable(QTableWidget)` | 356 | retired → `phoenix_commons.widgets.PhoenixTable` |
| `UpdateBanner(QFrame)` | 1704 | retired → `phoenix_commons.widgets.UpdateBanner` |

Single import block at top of file imports all 5 from `phoenix_commons.widgets`. UpdateBanner call site updated (1 site) from `UpdateBanner(info, self)` to commons signature `UpdateBanner(info.current_version, info.latest_version, info.release_notes, self)`.

Preserved app-specific verbatim: `ReorderableTaskTable`, `StatCard`, `SegmentedProgressBar`, `ElidingLabel`, `_BackgroundWidget`, `_WatermarkViewport`, `ResizeHandle`, `_HeaderResizeHandle`, `_VResizeHandle`, all `*Dialog` classes, `RSS*` dialogs, `NotesWindow`, `ChangeOrderWindow`, `ManageUsersDialog`, etc.

---

## 5. Identity checks

```
PrimaryButton    is phoenix_commons.widgets.PrimaryButton    : True
SecondaryButton  is phoenix_commons.widgets.SecondaryButton  : True
TertiaryButton   is phoenix_commons.widgets.TertiaryButton   : True
PhoenixTable     is phoenix_commons.widgets.PhoenixTable     : True
UpdateBanner     is phoenix_commons.widgets.UpdateBanner     : True
```

All 5 `is`-equal. Zero local re-definitions remain.

---

## 6. Validation results

| Check | Result |
|-------|--------|
| `py_compile project_tracker_gui.py` | clean ✅ |
| `_EMBEDDED_QSS` grep post-B4 | 0 hits ✅ |
| `phoenix_style.qss` present + non-empty | 135 LOC ✅ |
| 5/5 widget identity-equal to commons | ✅ |
| Offscreen merged QSS length | **30,769 chars** ✅ |
| DEFAULT_BRAND tokens (`#0a0e27`, `#dc2626`, `#3b82f6`) | all present ✅ |
| Sentinels (`__BRAND_PRIMARY__`, `__BRAND_ACCENT__`) | both absent ✅ |
| App-specific selectors (`#StatCard`, `#taskToolsButton`, `#FinDataMeta`, `#ResizeHandle`, `#PassBadge`) | all 5 present ✅ |
| `tests/test_regressions.py` | **29/29 green** ✅ |

---

## 7. Visual-change assessment

**Expected ≈ 0%** (Phoenix-CAD profile).

- Palette byte-equal: `_EMBEDDED_QSS` token values (`#0a0e27`, `#141829`, `#dc2626`, `#1e3a8a`, `#3b82f6`) match commons `DEFAULT_BRAND` exactly.
- Commons widget primitives carry the same `setMinimumHeight(36)`, `setObjectName("secondaryButton"/"tertiaryButton")`, `setCursor(PointingHandCursor)` defaults as the retired inline classes.
- `PhoenixTable` defaults preserved (vertical header hidden, no edit, no selection, alternating rows).
- Two-layer compose (Wave 8a B8a pattern) ensures every app-specific selector (`#StatCard`, `#taskToolsButton`, financials labels, badges, resize handles) survives the retrofit.
- One small operator-visible delta: commons `UpdateBanner` drops the `🆕` emoji prefix (local version had `f"🆕  Update available — v{...}"`; commons uses `f"Update available — v{...}"`). Operator-accepted at the Wave 8a precedent.

Operator interactive review at B10 will confirm pixel-level parity.

---

## 8. Blockers / issues

None blocking. Three observations:

1. **`phoenix_style.qss` was completely overwritten** — the prior content was stale Checkout leftover (mislabeled, never loaded at runtime). The new content is the migrated Job-Tracker overlay. This is intentional (Decision #9 explicit).

2. **🆕 emoji delta** — minor user-visible UpdateBanner text change (no emoji prefix). Wave 8a precedent.

3. **`StatCard` is preserved-local** — `#StatCard` selector lives in `phoenix_style.qss` overlay; the `StatCard(QFrame)` class is preserved-local in `project_tracker_gui.py`. Per the audit (gap inventory): function similar to PCC's AggregateTile but PCC's is also local. Promotion to commons needs two-consumer evidence per MIGRATION_RULES § 0 — out of Wave 8b scope.

---

## 9. Confirmation

- No domain logic changed (`project_tracker_backend.py`, financials_*.py, `user_auth.py`, `generate_guide.py` all untouched)
- No financials changed
- No auth changed
- No updater changed (B3 facade preserved at `33fd3d9`)
- No `build.bat` changed (B8 will harden)
- No `installer.iss` changed — **AppId still NOT declared** per Decision #8 hard rule
- No `version.py` change (stays at `1.8.5`)
- `starter_package/` untouched (B7 will delete)
- No production deployment

Branch HEAD: `6c70acf`. Ready for **B6 (preserved-local no-op audit) + B7 (starter_package deletion)**.
