# PCC Settings Dialog Modernization — Phase 3G Report

> **Status:** complete (PCC commit on retrofit branch, pending operator
> review + push).
> **Date:** 2026-05-22.
> **Branch:** `phase-3g-pcc-settings-dialog` (PCC).
> **Scope:** Modernize `settings_dialog.py` to the Phase 3C/3D/3E/3F
> unified vocabulary. Bounded dialog polish — no schema, persistence,
> or feature changes.
> Per the Phase 3G operator brief.
> **Operator gate:** visual review before merge-gate preparation.

---

## 1. Audit findings

### Pre-Phase-3G (legacy) — `settings_dialog.py` snapshot

`settings_dialog.py` was 230 LOC, 15 inline `setStyleSheet` call sites, 1 emoji glyph, 4 raw `QPushButton` instances.

#### Header (lines 81-84)

```python
title = QLabel("⚙  Settings")
title.setStyleSheet(f"color: {C['text']}; font-size: 18px; font-weight: 700;")
```

  - Gear emoji (U+2699) glyph prefix — last operator-visible emoji on chrome inside the PCC main app
  - Inline-styled font/colour — duplicates `#pageTitle` global QSS rule
  - 18px font size (`#pageTitle` is 22px) — visually smaller than the rest of PCC's page titles

#### General-tab content cards (lines 96-162)

Three nearly-identical inline-styled `QFrame` cards: Root Path / Editor Command / Commons Repo Name. Each:

```python
xx_frame = QFrame()
xx_frame.setStyleSheet(f"QFrame {{ background: {C['card']}; border-radius: 8px; }}")
xx_layout = QVBoxLayout(xx_frame)
xx_layout.setContentsMargins(14, 12, 14, 12)
xx_layout.setSpacing(8)
xx_title = QLabel("…")
xx_title.setStyleSheet(f"color: {C['text']}; font-weight: 700;")
xx_desc = QLabel("…")
xx_desc.setStyleSheet(f"color: {C['text_sub']}; font-size: 12px;")
…
```

Each card carries:
  - 1 inline-styled QFrame container chrome
  - 1 inline-styled title QLabel
  - 1 inline-styled description QLabel
  - The actual field (QLineEdit + optional Browse button)

Total inline `setStyleSheet` calls just for the 3 cards: **9**.

#### ToolRow (lines 15-59)

```python
class ToolRow(QFrame):
    def __init__(self, name, cfg, parent=None):
        super().__init__(parent)
        self.setStyleSheet(f"QFrame {{ background: {C['card']}; border-radius: 8px; }}")
        ...
        header = QLabel(name.replace("-", " ").replace("_", " ").title())
        header.setStyleSheet(f"color: {C['text']}; font-weight: 700; font-size: 13px;")
        ...
        gh_lbl.setStyleSheet(f"color: {C['text_sub']}; font-size: 12px;")
        ...
        lc_lbl.setStyleSheet(f"color: {C['text_sub']}; font-size: 12px;")
```

  - Inline-styled `QFrame` container chrome — same pattern as General-tab cards, duplicated per row
  - 3 inline-styled QLabels (header + 2 row labels)

#### Buttons (lines 197-209)

  - `Cancel` — raw `QPushButton#ghostBtn` (outline style via theme.py overlay)
  - `Save & Apply` — raw `QPushButton#accentBtn` (accent fill via theme.py overlay)
  - `Browse…` (inside Root Path card, line 112) — raw `QPushButton#ghostBtn`

All three buttons render correctly via the PCC theme overlay, but they bypass the commons `PrimaryButton` / `TertiaryButton` tier vocabulary that the rest of the PCC main app now uses.

#### What works and must not change

  - Settings schema (`root_path` / `editor_cmd` / `commons_name` / `tools{name: {github_url, launch_cmd, enabled}}`)
  - `get_config()` return shape
  - `accept` / `reject` Qt signals
  - `_browse_root()` flow
  - Constructor signature `SettingsDialog(cfg, tools, parent=None)`
  - `ToolRow.get_values()` return shape
  - main_window.py integration call site
  - First-run modal behavior

---

## 2. Header modernization

### Before

```python
title = QLabel("⚙  Settings")
title.setStyleSheet(f"color: {C['text']}; font-size: 18px; font-weight: 700;")
root.addWidget(title)
```

### After

```python
hdr_row = QHBoxLayout()
hdr_row.setSpacing(10)
hdr_icon = QLabel()
hdr_icon.setPixmap(icon("settings", color=C["text_muted"]).pixmap(QSize(18, 18)))
hdr_icon.setFixedWidth(20)
title = QLabel("Settings")
title.setObjectName("pageTitle")
hdr_row.addWidget(hdr_icon)
hdr_row.addWidget(title)
hdr_row.addStretch()
root.addLayout(hdr_row)
```

### What changed

  - Gear emoji (U+2699) glyph **retired**
  - Title text now `"Settings"` (the standalone word — Phase 3C/3D/3E pattern)
  - `#pageTitle` object name picks up canonical 22px 800-weight typography (matches dashboard / detail panel / Commons Browser)
  - Leading Lucide `settings` icon at 18×18 in `text_muted` (visual anchor, calm tint)
  - Inline title styling **retired** — global `#pageTitle` QSS does the work

### What's preserved

  - Title text semantic ("Settings")
  - `setWindowTitle("Phoenix Command Center — Settings")` constructor call unchanged (window-manager title preserved)
  - Dialog modality (`setModal(True)`)
  - Min size (600×500)

---

## 3. Panel/content modernization

### `_make_general_card(title, description)` helper

```python
def _make_general_card(title: str, description: str) -> tuple[Panel, QVBoxLayout]:
    """Build one General-tab Panel-wrapped card. Returns (panel, layout)
    so the caller can append the field-specific row(s) into the same
    layout."""
    p = Panel(title=None)
    p.layout().setContentsMargins(14, 12, 14, 12)
    p.layout().setSpacing(8)

    title_lbl = QLabel(title)
    title_lbl.setStyleSheet(f"color: {C['text']}; font-weight: 700;")
    desc_lbl = QLabel(description)
    desc_lbl.setStyleSheet(f"color: {C['text_sub']}; font-size: 12px;")
    desc_lbl.setWordWrap(True)

    p.layout().addWidget(title_lbl)
    p.layout().addWidget(desc_lbl)
    return p, p.layout()
```

  - Single source of truth for General-tab card chrome
  - Returns the layout so the caller can append the field-specific input(s)
  - Tightens Panel's default 16/16/16/16 margins to 14/12/14/12 (matches Phase 3D SyncStatusCard convention)
  - Title + description QLabels keep inline styling — they're semantic content text (B6 carve-out, same as detail-panel `status_lbl`)

### General-tab card construction (per card)

Before (Root-path card, ~26 LOC):

```python
rp_frame = QFrame()
rp_frame.setStyleSheet(f"QFrame {{ background: {C['card']}; border-radius: 8px; }}")
rp_layout = QVBoxLayout(rp_frame)
rp_layout.setContentsMargins(14, 12, 14, 12)
rp_layout.setSpacing(8)
rp_title = QLabel("Tools Root Folder")
rp_title.setStyleSheet(f"color: {C['text']}; font-weight: 700;")
rp_desc = QLabel("The parent folder…")
rp_desc.setStyleSheet(f"color: {C['text_sub']}; font-size: 12px;")
rp_desc.setWordWrap(True)
rp_row = QHBoxLayout()
self.root_edit = QLineEdit(self.cfg.get("root_path", ""))
…
browse_btn = QPushButton("Browse…")
browse_btn.setObjectName("ghostBtn")
…
rp_row.addWidget(self.root_edit, 1)
rp_row.addWidget(browse_btn)
rp_layout.addWidget(rp_title)
rp_layout.addWidget(rp_desc)
rp_layout.addLayout(rp_row)
general_layout.addWidget(rp_frame)
```

After (Root-path card, ~12 LOC):

```python
rp_panel, rp_lay = _make_general_card(
    "Tools Root Folder",
    "The parent folder that contains all your tool repos (each as a subfolder).",
)
rp_row = QHBoxLayout()
self.root_edit = QLineEdit(self.cfg.get("root_path", ""))
self.root_edit.setPlaceholderText("C:\\Projects  or  /home/user/projects")
browse_btn = TertiaryButton("Browse…")
browse_btn.setFixedWidth(96)
browse_btn.clicked.connect(self._browse_root)
rp_row.addWidget(self.root_edit, 1)
rp_row.addWidget(browse_btn)
rp_lay.addLayout(rp_row)
general_layout.addWidget(rp_panel)
```

  - QFrame inline-styled container → `Panel` (commons primitive)
  - Title + description QLabels factored into the helper
  - 3 cards × (1 QFrame chrome + 1 title + 1 description = 3 inline `setStyleSheet` calls each) **retired**
  - Net: 9 inline `setStyleSheet` call sites → 6 (3 per `_make_general_card` call — all on semantic-content text labels)

---

## 4. ToolRow modernization

### Before

```python
class ToolRow(QFrame):
    def __init__(self, name, cfg, parent=None):
        super().__init__(parent)
        self.setStyleSheet(f"QFrame {{ background: {C['card']}; border-radius: 8px; }}")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 10, 12, 10)
        layout.setSpacing(6)
        …
```

### After

```python
class ToolRow(Panel):
    def __init__(self, name: str, cfg: dict, parent=None):
        super().__init__(title=None, parent=parent)
        self.name = name
        self.layout().setContentsMargins(12, 10, 12, 10)
        self.layout().setSpacing(6)
        root = self.layout()
        …
```

  - Now extends commons `Panel` (same pattern as Phase 3D's `SyncStatusCard(Panel)`)
  - Inline `setStyleSheet` on the container **retired** — chrome flows from canonical commons `#Panel` QSS
  - Tighter 12/10/12/10 margins preserve the prior row-density rhythm (Panel default is 16/16/16/16)
  - Per-row label inline styles (header / `GitHub URL:` / `Launch cmd:`) retained as B6 carve-outs for semantic content text — same pattern detail-panel uses for sync-card detail rows

### Public API preserved

  - Constructor signature: `ToolRow(name, cfg, parent=None)` — unchanged
  - `get_values()` return shape: `{github_url, launch_cmd, enabled}` — unchanged
  - `self.gh_edit` / `self.launch_edit` attribute access — unchanged
  - `self.name` attribute — unchanged
  - QFrame methods + signals inherited via Panel → QFrame chain — unchanged

---

## 5. Button migration

### Three buttons migrated

| Pre-Phase-3G | Post-Phase-3G | Tier rationale |
|--------------|----------------|----------------|
| `QPushButton("Save & Apply")` + `setObjectName("accentBtn")` | `PrimaryButton("Save & Apply")` | The dialog's primary action — matches detail panel's `PrimaryButton Launch Installed` convention (red brand-primary anchors the right edge) |
| `QPushButton("Cancel")` + `setObjectName("ghostBtn")` | `TertiaryButton("Cancel")` | Non-destructive navigation — matches detail panel's `TertiaryButton Back / VS Code / GitHub` convention |
| `QPushButton("Browse…")` + `setObjectName("ghostBtn")` | `TertiaryButton("Browse…")` | Supporting page-level action — matches Commons Browser's `TertiaryButton Rescan` convention from Phase 3E Step 3 |

### Click connections preserved

  - `save_btn.clicked.connect(self.accept)` → unchanged (PrimaryButton inherits QPushButton's `clicked` signal)
  - `cancel_btn.clicked.connect(self.reject)` → unchanged
  - `browse_btn.clicked.connect(self._browse_root)` → unchanged

### Qt accept/reject semantics preserved

`dlg.exec()` returns `QDialog.Accepted` (1) on Save click and `QDialog.Rejected` (0) on Cancel click — same as before. Main window's `_open_settings` flow that checks `if dlg.exec(): cfg = dlg.get_config(); config.save(cfg)` continues to work without changes.

---

## 6. Validation results

### Static checks

| Check | Result |
|-------|--------|
| PCC `python -m compileall -q . -x "\.venv\|commons\|build\|dist\|__pycache__"` | ✓ clean (exit 0) |
| PCC `python -m pytest -q tests/` | ✓ **4 passed in 0.33s** |
| Commons working tree | ✓ clean (no commons changes in Phase 3G) |
| PCC working tree | ✓ clean (smoke + launcher temp files removed) |
| Diff scope vs main | 1 file (`settings_dialog.py`); +140 / −83 |

### Offscreen 12-scenario smoke

| # | Scenario | Result |
|---|----------|--------|
| 1 | Dialog constructs | ✓ window title / size / modal flag correct |
| 2 | Header text + objectName | ✓ "Settings" with `#pageTitle` object name |
| 3 | Header has Lucide settings icon | ✓ (QPixmap on hdr_icon QLabel) |
| 4 | Gear emoji absent from source | ✓ — `assert '⚙' not in src` passed |
| 5 | 5 Panel instances (3 general cards + 2 ToolRow) | ✓ |
| 6 | ToolRow is Panel subclass | ✓ — `isinstance(tr, Panel)` for both rows |
| 7 | 1 PrimaryButton (Save & Apply) | ✓ |
| 8 | 2 TertiaryButton (Cancel + Browse…) | ✓ |
| 9 | 0 raw QPushButton instances | ✓ (`type(b).__name__ == 'QPushButton'` count = 0) |
| 10 | `get_config()` returns identical schema | ✓ — all 4 top-level keys + nested tools dict match pre-Phase-3G |
| 11 | Save click emits `accepted` signal | ✓ |
| 12 | Cancel click emits `rejected` signal | ✓ |
| 13 | Empty-tools state still renders "No tools found…" QLabel | ✓ |

### Configuration / persistence integrity

| Surface | Status |
|---------|--------|
| `config.py` load/save logic | ✓ untouched |
| `cfg["root_path"]` field | ✓ unchanged read/write |
| `cfg["editor_cmd"]` field | ✓ unchanged read/write |
| `cfg["commons_name"]` field | ✓ unchanged read/write |
| `cfg["tools"][name]` shape (github_url / launch_cmd / enabled) | ✓ unchanged read/write |
| `pcc_config.json` schema | ✓ unchanged (the dialog produces/consumes the same shape) |
| `main_window.py._open_settings` flow | ✓ untouched — same `dlg.exec()` + `dlg.get_config()` + `config.save()` sequence works |

### Invariants preserved

| Invariant | Status |
|-----------|--------|
| B5 — subprocess CREATE_NO_WINDOW | ✓ N/A (no subprocess calls in Settings dialog) |
| B6 — no widget-level setStyleSheet on commons primitives | ✓ preserved — no inline styles on `Panel`/`PrimaryButton`/`TertiaryButton`; remaining inline styles are documented B6 carve-outs for semantic-content text labels (`title_lbl`, `desc_lbl`, ToolRow per-row labels, empty-tools placeholder) |
| BrandProfile — orange + teal per ADR-016 | ✓ untouched |
| Commons API stability | ✓ no commons changes |
| Phase 3C/3D/3E/3F retrofit chrome | ✓ no regressions; settings opens via existing `_open_settings` route |

---

## 7. Remaining intentional debt

| Item | Status |
|------|--------|
| ToolRow header inline label style (`color: text; font-weight: 700; font-size: 13px`) | **B6 carve-out** — per-row data label, not chrome. Same pattern detail panel uses for sync-card status rows. |
| `GitHub URL:` / `Launch cmd:` inline label colour | **B6 carve-out** — semantic content (form-field labels) |
| `_make_general_card` title + description inline labels | **B6 carve-out** — semantic content (section title + helper text); same pattern Phase 3D Files-tab placeholder uses |
| Empty-tools "No tools found…" QLabel inline style | **B6 carve-out** — informational placeholder, not chrome |
| `setFrameShape(QFrame.NoFrame)` on the Tools-tab QScrollArea | **Local import of `QFrame`** at the call site (since top-level `QFrame` import was retired) — single-use pattern, doesn't justify keeping the top-level import |

These are the same B6 carve-outs Phase 3D, 3E, 3F all preserved. **No chrome-level inline stylesheets remain in the file.**

### Items intentionally NOT modernized in Phase 3G

  - **General-tab field layout** — single QLineEdit per card (root path / editor / commons name) stays simple. Per spec §3: "Keep all fields, all labels, all current interactions." No add/remove/reorder.
  - **Tools tab structure** — flat scroll list of ToolRow widgets. No table view promotion (would be a new feature, not chrome polish).
  - **First-run validation feedback** — no inline error states added. The existing `get_config()` + `config.save()` flow handles malformed input via fallback defaults.
  - **Confirmation dialogs** — Save/Cancel close immediately. No "are you sure?" prompts (would be a feature change).

---

## 8. Merge readiness recommendation

### Recommendation: **A — Merge-ready as-is.**

Phase 3G is a clean single-commit modernization on `phase-3g-pcc-settings-dialog`. All validation green, no schema changes, no persistence regressions, no caller-side changes needed.

### Why this is straightforward

  - **1 commit, 1 file, +140/-83 diff.** Smaller than Phase 3F (3 files +599/-16).
  - **0 dead code at gate.** No orphan helpers, no dead imports, no redundant inline QSS to clean up.
  - **0 submodule lag.** Branched from main `a6e8f02` (post-Phase-3F merge); no commons commits intervening.
  - **0 new commons primitives.** `Panel`, `PrimaryButton`, `TertiaryButton`, `icon("settings", …)` all pre-existing.
  - **0 caller-side changes.** `main_window._open_settings` flow unchanged.

### Next phase suggested merge plan

Mirroring the Phase 3F closure pattern (smallest closure of the 3C/3D/3E/3F/3G series — actually 3G is even smaller than 3F):

  1. Operator visual review on `phase-3g-pcc-settings-dialog` branch
  2. Push retrofit branch
  3. `git checkout main && git merge --no-ff phase-3g-pcc-settings-dialog -m "..."`
  4. No post-merge consolidation needed (no dead code, no submodule lag)
  5. Tag `pcc-phase-3g-merged-v2.4.0` on the merge commit
  6. Push main + tag
  7. Append Phase 3G row to `MIGRATION_RULES.md § Migration order`

---

## 9. Confirmation

  - **No architecture changes occurred.** No new ADR. No commons API change. No new commons widget. No new commons icon (`settings` already in `ICON_NAMES` since Phase 2.2). `BrandProfile` unchanged. ADR-014 / ADR-015 / ADR-016 all hold.
  - **No BrandProfile changes occurred.** PCC `BrandProfile` (orange + teal per ADR-016) unchanged. `PrimaryButton` consumes commons sentinel substitution → PCC orange. `TertiaryButton` is brand-independent outline tier.
  - **No settings schema changes occurred.** `cfg` shape (`root_path` / `editor_cmd` / `commons_name` / `tools{name: {github_url, launch_cmd, enabled}}`) unchanged. `get_config()` return shape preserved. `pcc_config.json` persistence format unchanged.
  - **No production deployment occurred.** PCC is unpackaged per `CLAUDE.md`. No installer built. No `dist/` artifact. No GitHub Release. Phase 3G commit lives on local `phase-3g-pcc-settings-dialog` branch (not yet pushed — operator-gated).
  - **No Wave 8a work occurred.** Wave 8a remains operator-gated to the existing 2026-06-02 doctrinal cooldown floor.
  - **No production tool source touched.** Phoenix CAD / Phoenix Checkout / PTT / ValveMaster all unmodified.
  - **No New Tool Wizard work occurred.** `new_tool_wizard.py` untouched. Remains a separate deferred candidate.
  - **No About / Shortcuts dialog work occurred.** `about_dialog.py` untouched. Remains a separate deferred candidate.
  - **No search backend work occurred.** Phase 3F MVP remains as-is; no V2 spec authoring began.
  - **No `config.py` / `pcc_config.json` changes.** Persistence layer untouched.
  - **No `main_window.py` integration changes.** The `_open_settings` flow continues to work without caller-side edits.

---

## Commit summary

| Repo | Commit | Subject | Pushed |
|------|--------|---------|--------|
| `phoenix-command-center` `phase-3g-pcc-settings-dialog` | `7c5e8ab` | Settings dialog modernization (Phase 3G) | pending (operator-gated) |
| `phoenix-commons` `main` | (this report, pending) | Add PCC_SETTINGS_DIALOG_MODERNIZATION_REPORT | pending |

PCC retrofit branch tip after Phase 3G: `7c5e8ab` (1 commit ahead of `a6e8f02` = post-Phase-3F merge tip on main).

No commons source change in Phase 3G — only this report file is added.

---

*End of report. Phase 3G modernization is complete. Operator gate before merge execution opens.*
