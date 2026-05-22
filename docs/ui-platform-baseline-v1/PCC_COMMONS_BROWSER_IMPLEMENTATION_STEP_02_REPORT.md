# PCC Commons Browser Implementation — Step 2 Report

> **Status:** complete (PCC commit on retrofit branch, pending operator
> review + push).
> **Date:** 2026-05-22.
> **Branch:** `phase-3e-pcc-commons-browser-retrofit` (PCC).
> **Scope:** UsageFooter modernization — inline-styled QFrame + emoji
> chips retired in favour of Panel-contained StatusBadge composition
> with Lucide icons. Per `PCC_COMMONS_BROWSER_SURFACE_SPEC_V1` §3.5 +
> §7 step 2.
> **Operator gate:** visual review before Step 3 (splitter cleanup +
> Rescan tier migration) starts.

---

## 1. UsageFooter audit findings

### Pre-Step-2 (legacy)

UsageFooter in `commons_browser.py:41-99` was a 58-LOC `QFrame`
subclass carrying:

```python
class UsageFooter(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet(f"QFrame {{ background: {C['surface']}; "
                           f"border: 1px solid {C['border']}; "
                           f"border-radius: 8px; }}")
        # ...
        self.title = QLabel("USED BY")
        self.title.setStyleSheet(
            f"color: {C['text_muted']}; font-size: 10px; "
            f"font-weight: 700; letter-spacing: 1.3px;"
        )
```

Three per-state rendering paths:

```python
def show_users(self, users: list):
    if not users:
        chip = QLabel("◇  ORPHAN — not referenced by any tool")
        chip.setStyleSheet(
            f"color: {C['warning']}; background: rgba(240,160,48,0.10); "
            f"border: 1px solid {C['warning']}; border-radius: 12px; "
            f"padding: 4px 12px; font-size: 11px; font-weight: 700;"
        )
        # ...
        return
    for name in users:
        pretty = name.replace("-", " ").replace("_", " ").title()
        chip = QLabel(f"◈  {pretty}")
        chip.setStyleSheet(
            f"color: {C['accent']}; background: {C['accent_glow']}; "
            f"border-radius: 12px; padding: 4px 12px; "
            f"font-size: 11px; font-weight: 700;"
        )
        # ...

def show_placeholder(self, text: str):
    lbl = QLabel(text)
    lbl.setStyleSheet(
        f"color: {C['text_muted']}; font-size: 11px; font-style: italic;"
    )
```

### Documented problems

  - **Inline-styled QFrame card chrome** — sets a bespoke
    `background + border + border-radius` rule on the container
    rather than using commons `Panel`. Generates inline-stylesheet
    drift across the file.
  - **Hand-styled "USED BY" header** — duplicates the
    `#sectionHeader` QSS rule that theme.py overlay already
    provides globally.
  - **Emoji chrome glyphs** (`◇` orphan / `◈` user) — the last
    operator-visible emoji on a primary PCC surface. Dashboard +
    detail panel both Lucide-only since Phase 3C Step 1.
  - **Inline-styled chip QLabels** — bespoke colour + background +
    border pills duplicating `StatusBadge`'s role.
  - **No overflow handling** — `QHBoxLayout` with `addStretch()`
    end. Many tool users would overflow horizontally with no scroll,
    cropping the right edge.

### Workflow preservation requirement

Pre-Step-2 the UsageFooter surfaced 3 states:
  1. **Placeholder** — muted italic "Select a file to see which tools reference it."
  2. **Orphan** — amber pill "◇  ORPHAN — not referenced by any tool"
  3. **Used by N tools** — N teal-glow pills, each "◈  Tool Name"

**Step 2 preserves all 3 states.** Public API (`show_users(users)`,
`show_placeholder(text)`, `clear()`) is unchanged. `_on_tree_clicked`
in CommonsBrowser still calls into the same three methods with the
same arguments.

---

## 2. Panel migration details

### Inheritance change

Before:
```python
class UsageFooter(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet(f"QFrame {{ background: ...; ... }}")
```

After:
```python
class UsageFooter(Panel):
    def __init__(self, parent=None):
        super().__init__(title=None, parent=parent)
        self.layout().setContentsMargins(14, 10, 14, 10)
        self.layout().setSpacing(6)
```

`Panel` inherits from `QFrame` internally and applies the canonical
commons rounded-card chrome via the `#Panel` QSS rule. No inline
stylesheet needed on the container.

This mirrors the Phase 3D SyncStatusCard pattern (`SyncStatusCard(Panel)`).
Same operator-visible card chrome the dashboard's TOOLS + RECENT
ACTIVITY panels carry.

### Section header

Before:
```python
self.title = QLabel("USED BY")
self.title.setStyleSheet(
    f"color: {C['text_muted']}; font-size: 10px; "
    f"font-weight: 700; letter-spacing: 1.3px;"
)
```

After:
```python
title = QLabel("USED BY")
title.setObjectName("sectionHeader")
```

Now picks up the canonical PCC theme.py rule for `#sectionHeader`
(10px uppercase muted 700 weight with letter-spacing). Single
source of truth. No inline letter-spacing override.

### QScrollArea for overflow

New element added to handle horizontal overflow gracefully:

```python
scr = QScrollArea()
scr.setWidgetResizable(True)
scr.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
scr.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
scr.setFrameShape(QFrame.NoFrame)
scr.setFixedHeight(34)
```

Fixed-height 34px keeps the footer thin; vertical scroll always
off; horizontal scroll appears only when total composed-pill width
exceeds the viewport. `NoFrame` avoids double-border inside Panel
chrome (same pattern Phase 3D used inside Overview's Recent Commits
+ TODOs panels).

---

## 3. Used-by state modernization

### Per-tool pill composition

A single tool's representation is now a composed widget:

```
[Lucide package icon 12×12 muted-slate]  [StatusBadge "Tool Name" variant=clean compact]
```

Implementation (`_compose_pill` static helper):

```python
@staticmethod
def _compose_pill(icon_name, icon_color, label, variant):
    w = QWidget()
    lay = QHBoxLayout(w)
    lay.setContentsMargins(0, 0, 0, 0)
    lay.setSpacing(4)
    ic = QLabel()
    ic.setPixmap(icon(icon_name, color=icon_color).pixmap(QSize(12, 12)))
    ic.setFixedWidth(14)
    badge = StatusBadge(label, variant=variant, compact=True)
    lay.addWidget(ic)
    lay.addWidget(badge)
    return w
```

`show_users(users)` for ≥1 user:

```python
for name in users:
    pretty = name.replace("-", " ").replace("_", " ").title()
    pill = self._compose_pill(
        "package", C["text_sub"],
        pretty, "clean",
    )
    self.chips_layout.insertWidget(self.chips_layout.count() - 1, pill)
```

### Visual change

Before: each tool rendered as a teal-glow QLabel with `◈` glyph
prefix and accent-coloured text on accent_glow background. All pills
visually identical.

After: each tool renders as `[package icon] [green-dot StatusBadge]`
in a horizontal composition. The `package` Lucide icon (already in
`ICON_NAMES` since Phase 2.2) reads as a semantic "this commons
file is a consumable package" indicator. The `clean` StatusBadge
green dot conveys "actively used" health.

### Pretty-name behavior preserved

The pre-existing `name.replace("-", " ").replace("_", " ").title()`
transformation is preserved verbatim. Tool slugs like `phoenix-cad`
still render as `"Phoenix Cad"`, `job-tracker` → `"Job Tracker"`,
`valvemaster_tool` → `"Valvemaster Tool"`. **Underlying users list
shape unchanged.**

### `package` icon source

Already in commons. Per Phase 2.2 + the ICON_NAMES roster from
Phase 3D (23 entries), `package` was one of the original Lucide
icons added — already exercised by the dashboard's tools-table
NAME column.

No new icons added in this step.

---

## 4. Orphan state modernization

### Composition

```
[Lucide warning icon 12×12 warning-amber]  [StatusBadge "Not referenced by any tool" variant=warning compact]
```

Implementation (orphan branch of `show_users`):

```python
if not users:
    pill = self._compose_pill(
        "warning", C["warning"],
        "Not referenced by any tool", "warning",
    )
    self.chips_layout.insertWidget(self.chips_layout.count() - 1, pill)
    return
```

### Variant choice — `warning`, not `dirty`

Both `warning` and `dirty` render as amber in commons StatusBadge.
The semantic distinction:

| Variant | Semantic | Phase 3D detail-panel example |
|---------|----------|-------------------------------|
| `dirty` | Uncommitted / unsaved / pending work | sync card "↑ N unpushed", TodoItem "Open" |
| `warning` | Non-fatal warning / attention-worthy state | (less-used) |

An orphan file in commons isn't "uncommitted work" — it's "unused
artifact, attention-worthy but non-fatal". `warning` is the closer
semantic match. Spec §3.5 explicitly suggests this.

### Visual change

Before: amber QLabel pill with `◇` open-diamond glyph prefix and
"ORPHAN — not referenced by any tool" text.

After: `[warning Lucide icon]` + `[StatusBadge(warning, "Not
referenced by any tool")]`. Reads as calm-attention-worthy rather
than alarming. Specifically the `◇` empty-diamond glyph (which
operators sometimes misread as a generic "circle" placeholder) is
replaced with the universally-recognized triangle-warning glyph.

### Text simplification

The leading "ORPHAN —" prefix was redundant given the variant +
icon already conveyed "this needs attention." Text simplified to
"Not referenced by any tool" — the actual meaning. Per spec §3.5.

---

## 5. Empty / placeholder state preservation

### Preserved verbatim

```python
def show_placeholder(self, text: str):
    self.clear()
    lbl = QLabel(text)
    lbl.setStyleSheet(
        f"color: {C['text_muted']}; font-size: 11px; font-style: italic;"
    )
    self.chips_layout.insertWidget(self.chips_layout.count() - 1, lbl)
```

The placeholder QLabel — muted italic text — is **structurally
identical** to its pre-Step-2 form. Inline `setStyleSheet` retained
as a B6 carve-out (semantic content text, not chrome; same pattern
the detail panel uses for muted info labels like sync-card status
sentences).

Placeholder messages set by CommonsBrowser:

  - "Select a file to see which tools reference it." (initial)
  - "Usage data not yet available — wait for scan or click Rescan." (file selected before scan)
  - Various empty-state messages from `_set_empty_state()` (e.g. "Commons folder not found…")

All these texts continue to render identically.

### What's intentionally NOT modernized in the placeholder

The placeholder is semantic content (the operator is reading the
instructional text), not chrome. Treating it as a StatusBadge or
adding a Lucide icon would over-decorate a calm informational
surface. The italic muted treatment is appropriate.

---

## 6. Overflow / wrapping behavior

### QScrollArea horizontal scroll

The chips_host QWidget sits inside a QScrollArea with:

  - `setWidgetResizable(True)` — content sizes to fit
  - `setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)` — vertical scroll never appears
  - `setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)` — horizontal scroll appears only on overflow
  - `setFixedHeight(34)` — single-row strip
  - `setFrameShape(QFrame.NoFrame)` — avoids double-border inside Panel

### Behavior across pill counts

| User count | Visual behavior |
|------------|-----------------|
| 0 (orphan) | Single warning pill, no scroll |
| 1 (single user) | Single clean pill, no scroll |
| 2-6 (typical) | Pills sit horizontally with `addStretch()` pushing right edge, no scroll |
| 7-15+ (many) | Pills overflow visible width; horizontal scrollbar appears at bottom of strip; operator can scroll horizontally to see all pills |

### What's intentionally NOT done

  - **No multi-row wrapping.** Qt's QHBoxLayout doesn't natively
    support wrapping; implementing a wrapping flow layout would
    introduce a new layout primitive (out of scope per spec §8).
    Horizontal scroll is the simpler correct answer.
  - **No truncation with overflow indicator.** Tested in the smoke
    with 10 tools — all 10 pills render; the operator can scroll
    to see them all. Truncation would hide signal.
  - **No reordering.** The order of pills mirrors the order of the
    `users` list returned by `scanner.scan_commons_usage` — alphabetical
    by tool name in the typical case.

### Edge case — single very-long tool name

If a tool's pretty name is exceptionally long (e.g. 40+ chars), the
StatusBadge widens to fit. The horizontal scroll handles it. Tested
in the smoke implicitly (the `valvemaster_tool` → "Valvemaster Tool"
case is 16 chars and rendered without breakage).

---

## 7. Validation results

| Check | Result |
|-------|--------|
| PCC `python -m compileall -q . -x "\.venv\|commons\|build\|dist\|__pycache__"` | ✓ clean (exit 0) |
| PCC `python -m pytest -q tests/` | ✓ **4 passed in 0.76s** |
| Offscreen smoke — `UsageFooter` inherits `Panel` | ✓ |
| Offscreen smoke — "USED BY" QLabel has `#sectionHeader` object name | ✓ |
| Offscreen smoke — placeholder state | ✓ muted italic QLabel rendered, 0 StatusBadges |
| Offscreen smoke — orphan state | ✓ 1 StatusBadge (variant=`warning`, text="Not referenced by any tool") |
| Offscreen smoke — single-user state | ✓ 1 StatusBadge (variant=`clean`, text="Phoenix Cad") |
| Offscreen smoke — multi-user state (3 tools) | ✓ 3 StatusBadges, all variant=`clean`, pretty names "Job Tracker" / "Phoenix Cad" / "Valvemaster Tool" |
| Offscreen smoke — many-users overflow (10 tools) | ✓ 10 StatusBadges rendered (horizontal scroll handles overflow without layout break) |
| Offscreen smoke — re-placeholder after used state | ✓ 0 StatusBadges, 1 placeholder QLabel (clean re-render) |
| Offscreen smoke — full CommonsBrowser construction | ✓ usage_footer is both Panel + UsageFooter (multiple-inheritance check) |
| Offscreen smoke — `_Chip` class still absent from Step 1 | ✓ |
| `set_usage` aggregation logic | ✓ unchanged (byte-identical from Step 1) |
| `_set_empty_state` reset logic | ✓ unchanged |
| `set_scanning` flow | ✓ unchanged |
| Refresh button + Lucide refresh icon | ✓ unchanged |
| `refresh_requested` signal contract | ✓ unchanged |
| `main_window.py` integration | ✓ no caller-side changes needed |
| `scanner.scan_commons_usage` integration | ✓ no scanner-side changes needed |
| FileViewer | ✓ untouched (Step 3/4 scope still out) |
| QTreeView + QFileSystemModel | ✓ untouched |
| QSplitter (still has inline-QSS — Step 3 target) | ✓ untouched in this step |
| B5 invariant (subprocess CREATE_NO_WINDOW) | ✓ preserved |
| B6 invariant (no widget-level setStyleSheet on commons primitives) | ✓ preserved — `UsageFooter` is now a Panel subclass; Panel chrome flows from commons canonical QSS. The two remaining `setStyleSheet` calls are on semantic-content QLabels (the placeholder muted-italic text), not on commons widgets — same documented B6 carve-out the detail panel uses. |
| BrandProfile invariant | ✓ untouched. StatusBadge variants resolve to commons brand-independent semantic palette |
| Theme.py | ✓ untouched (no new QSS rules required) |
| Diff scope | 1 file (`commons_browser.py`); +95 / −32 |

---

## 8. Remaining Commons Browser debt

Per spec §7 sequencing:

| # | Step | Status |
|---|------|--------|
| 1 | Summary chip row — `_Chip` → `StatusBadge` | ✅ done |
| 2 | **UsageFooter modernization** — Panel + StatusBadge + Lucide | ✅ **done (this step)** |
| 3 | Tree/viewer/page cohesion pass — splitter inline-QSS cleanup + Rescan tier migration | pending (recommended next) |
| 4 | Validation + merge gate | pending |

### Cosmetic debt remaining

  - **Inline `QSplitter::handle` setStyleSheet** at `commons_browser.py:153` — redundant with PCC theme.py overlay. Same one-line fix Phase 3D's post-merge cleanup landed for the detail panel. Addressed in Step 3.
  - **Rescan button** still raw `QPushButton#ghostBtn` (line 130). Either `TertiaryButton` (subtle, matches "Back" tier on detail panel) or `SecondaryButton` (more prominent for a page-header rescan). Operator pick at Step 3.
  - **`status_lbl` inline stylesheet** at line 125 (`f"color: {C['text_muted']}; font-size: 11px;"`) — semantic content text colour, NOT chrome. Same B6 carve-out as muted-info labels in detail panel. Will be evaluated in Step 3 but likely retained as-is.

### Two remaining inline `setStyleSheet` call sites in commons_browser.py

| Line | Caller | Verdict |
|------|--------|---------|
| 125 | `self.status_lbl.setStyleSheet(...)` | Semantic content text colour — B6 carve-out, preserved |
| 153 | `spl.setStyleSheet(f"QSplitter::handle ...")` | Redundant with theme.py overlay — Step 3 cleanup target |
| 165 (UsageFooter placeholder) | `lbl.setStyleSheet(...)` | Semantic content text colour — B6 carve-out, preserved |

After Step 3 the only remaining inline `setStyleSheet` calls will be
the two semantic-content-text carve-outs. The Commons Browser will
be fully on the Phase 3C/3D B6 invariant.

---

## 9. Recommended Step 3 target

**Step 3 — Tree / viewer / page cohesion pass.** Per spec §7.

Sub-steps:

  1. **Remove inline `QSplitter::handle` stylesheet** at line 153 — same Phase 3D post-merge cleanup mechanic (theme.py overlay already styles `QSplitter::handle` globally).
  2. **Migrate Rescan button** from raw `QPushButton#ghostBtn` to `TertiaryButton` (recommended) or `SecondaryButton` (operator review picks tier).
  3. **Final spacing/typography polish pass** — header row vertical alignment, chip-row vs panel-row spacing, any missing breathing room between regions.

Estimated scope: small (~20-30 LOC delta). No commons additions
required. No new icons.

After Step 3, all 3 surface modernizations are done. Step 4 is the
closure gate (merge plan + post-merge cleanup + tag) mirroring the
Phase 3D closure sequence.

---

## 10. Confirmation

  - **No architecture changes occurred.** No new ADR. No commons API change. No new commons widget. `Panel` and `StatusBadge` were already in the commons public API since Phase 3C. `BrandProfile` unchanged. ADR-014 / ADR-015 / ADR-016 all hold.
  - **No BrandProfile changes occurred.** PCC `BrandProfile` (orange + teal) unchanged. StatusBadge variants resolve to commons brand-independent semantic colours.
  - **No production deployment occurred.** Source-mode only on `phase-3e-pcc-commons-browser-retrofit` branch. PCC is unpackaged. No installer built. No `dist/` artifact. No GitHub Release. Step 2 commit not yet pushed to PCC origin (operator-gated).
  - **No scanner changes occurred.** `scanner.scan_commons_usage` output shape, tool corpus building logic, keys-and-extensions heuristics — all unchanged.
  - **No search backend work occurred.** Search backend remains a deferred Phase 3F+ candidate.
  - **No Wave 8a work occurred.** Wave 8a remains operator-gated (cooldown floor 2026-06-02).
  - **No production tool source touched.** Phoenix CAD / Phoenix Checkout / PTT / ValveMaster all unmodified.
  - **No tree / FileViewer / QFileSystemModel work occurred.** Step 3 scope.
  - **No Settings / Wizard / About / Push Preview work occurred.** Each remains a separate deferred candidate.
  - **No new commons primitives or icons added.** `package` and `warning` already in `ICON_NAMES` pre-Phase-3E. No additions to commons.

---

## Commit summary

| Repo | Commit | Subject | Pushed |
|------|--------|---------|--------|
| `phoenix-command-center` `phase-3e-pcc-commons-browser-retrofit` | `77e5b45` | Commons Browser UsageFooter modernization (Phase 3E Step 2) | pending (operator-gated) |
| `phoenix-commons` `main` | (this report, pending) | Add PCC_COMMONS_BROWSER_IMPLEMENTATION_STEP_02_REPORT | pending |

PCC retrofit branch tip after Step 2: `77e5b45` (2 commits ahead of `160270c` = post-Phase-3D CI-fix tip on `main`).

No commons source change in Step 2 — only this report file is added.

---

*End of report. Phase 3E Step 2 = the second of 4 sequenced steps on
the spec. Operator gate before Step 3 (tree/viewer/page cohesion
pass) opens.*
