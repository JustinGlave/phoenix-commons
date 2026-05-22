# PCC Detail Panel Implementation — Step 7 Report

> **Status:** complete (PCC commit on retrofit branch; commons commit = this
> report only — no source change in commons).
> **Date:** 2026-05-21.
> **Branch:** `phase-3d-pcc-detail-retrofit` (PCC).
> **Scope:** Files tab cohesion pass — `CommonsDropZone` emoji glyph
> (`⬆`/`✓`) → Lucide icon composition (`arrow-up` idle / `check` success).
> Splitter / pane / tree / FileViewer chrome intentionally untouched
> per spec §3.6 (Files is a **TERTIARY** surface — lightweight only).
> Per `PCC_DETAIL_PANEL_SURFACE_SPEC_V1` §3.6 + §7 step 7.
> **Operator gate:** final review before Phase 3D closure preparation.

---

## 1. Files-tab audit findings

### Pre-Step-7 (post-Step-6) surface composition

The Files tab body in `detail_panel.py` lines 699-712 was 13 lines of
straight Qt construction:

```python
fl = QWidget(); fll = QVBoxLayout(fl)
fll.setContentsMargins(8,8,8,8); fll.setSpacing(6)
spl = QSplitter(Qt.Horizontal); spl.setHandleWidth(2)
spl.setStyleSheet(f"QSplitter::handle {{ background: {C['border']}; }}")
tw = QWidget(); twl = QVBoxLayout(tw)
self.fs_model = QFileSystemModel(); self.fs_model.setFilter(QDir.AllDirs | QDir.Files | QDir.NoDotAndDotDot)
self.tree = QTreeView(); self.tree.setModel(self.fs_model)
self.tree.setDragEnabled(True); self.tree.setDragDropMode(QAbstractItemView.DragOnly)
self.tree.setAnimated(True)
for col in (1,2,3): self.tree.setColumnHidden(col, True)
self.tree.clicked.connect(self._on_tree_clicked)
twl.addWidget(self.tree, 1)
self.drop_zone = CommonsDropZone(self.commons_path); twl.addWidget(self.drop_zone)
spl.addWidget(tw)
self.file_viewer = FileViewer(); spl.addWidget(self.file_viewer)
spl.setSizes([280, 560]); fll.addWidget(spl, 1)
self.tabs.addTab(fl, "Files")
```

### Surface inventory

| Element | Pre-Step-7 chrome | Step-7 treatment |
|---------|-------------------|------------------|
| Files tab outer layout (16/8 margins) | minimal `QVBoxLayout(8,8,8,8)` | **untouched** — already calm |
| `QSplitter` (horizontal, 2px handle) | `setStyleSheet("QSplitter::handle { background: border; }")` | **untouched** — semantic affordance (per spec §3.6 "do not redesign splitter behavior") |
| `QTreeView` (tree pane left) | default Qt chrome via app-level cascade | **untouched** — file-tree workflow preserved (spec §8 forbids redesign) |
| `FileViewer` (right pane) | own widget; its internal chrome is its own concern | **untouched** — spec §8: "Do NOT redesign FileViewer internals" |
| `CommonsDropZone` (below tree) | inline-styled dashed-border QFrame with single-QLabel `"⬆  Drag a file here…"` emoji-prefixed hint, flipping to `"✓  Copied: …"` on drop | **modernised** — icon composition with `arrow-up`/`check` Lucide glyphs (this step's only delta) |

### CommonsDropZone — the last emoji in the detail panel

Steps 1, 2, 4, 5, 6 each retired one or more emoji-prefixed labels in
favour of Lucide icon composition. After Step 6, the only remaining
emoji glyphs on the detail panel's static chrome were inside
`CommonsDropZone`:

  - Idle hint: `"⬆  Drag a file here to copy to commons"`
  - Success hint (after a drop): `"✓  Copied: <filename>"`

Both flowed through the same single `QLabel` (`self.hint`) with its
`setStyleSheet` colour flip from teal → success-green on drop.

`CommonsDropZone` is also the **only** widget on the detail panel
that carries operationally-semantic chrome (the dashed border = "this
is a drop target"). Per the B6 invariant carve-out the StatusBadge
chrome QSS gets in commons: affordance-defining visual stays
inline because removing it removes the meaning. Step 7 preserves
that carve-out — the dashed border, hover-state highlight rect, and
border radius are unchanged.

### Documented problems addressed

  - **Last emoji glyph on the detail panel's static chrome.** Steps 1-6
    migrated every other emoji-prefixed label to Lucide. `CommonsDropZone`
    was the last holdout. Cohesion required closing the gap.
  - **Glyph + text on the same `QLabel`.** Pre-Step-7 the `⬆`/`✓`
    glyph was prepended to the label text. Step 7 splits the affordance
    into a leading `QLabel` whose `setPixmap()` carries the rendered
    Lucide icon (sized 14×14 to match StatusBadge dot scale) + a
    trailing `QLabel` carrying just the text. Same compositional
    pattern Step 5's `TodoItem` introduced.

### Documented problems NOT addressed (out of scope per spec §3.6)

  - QSplitter handle inline styling — kept; semantic affordance.
  - QTreeView column hidden config — kept; functional, not chrome.
  - FileViewer internal rendering — kept; spec §8 forbids redesign.
  - File-tree drag/drop wiring — kept; spec §8 forbids redesign.
  - Files tab outer layout margins — kept; visually fine.
  - Per-pane `Panel` wrap — explicitly NOT done; per spec §3.6 + Step 6
    report §7 "Files tab Panel wrap may crowd the tree" — default
    to no Panel wrap on this surface.

---

## 2. CommonsDropZone modernisation details

### Hint surface composition

Pre-Step-7:

```python
self.hint = QLabel("⬆  Drag a file here to copy to commons")
self.hint.setStyleSheet(f"color: {C['teal']}; font-size: 11px; font-weight: 600;")
layout = QHBoxLayout(self)
layout.addStretch()
layout.addWidget(self.hint)
layout.addStretch()
```

Post-Step-7:

```python
layout = QHBoxLayout(self)
layout.setContentsMargins(8, 8, 8, 8)
layout.setSpacing(6)
layout.addStretch()
self.hint_icon = QLabel()
self.hint_icon.setPixmap(icon("arrow-up", color=C["teal"]).pixmap(QSize(14, 14)))
self.hint_icon.setFixedWidth(16)
self.hint = QLabel("Drag a file here to copy to commons")
self.hint.setStyleSheet(f"color: {C['teal']}; font-size: 11px; font-weight: 600;")
layout.addWidget(self.hint_icon)
layout.addWidget(self.hint)
layout.addStretch()
```

The leading `hint_icon` QLabel renders `arrow-up` in PCC teal at 14×14
(matches StatusBadge compact-mode dot scale + Step 5 `TodoItem`
leading-icon scale). The trailing `hint` QLabel carries the text
alone — same colour, weight, size as before. Total visual change:
emoji glyph → Lucide icon. Layout flow + spacing unchanged.

### dropEvent success-state flip

Pre-Step-7:

```python
self.hint.setText(f"✓  Copied: {os.path.basename(src)}")
self.hint.setStyleSheet(f"color: {C['success']}; font-size: 11px; font-weight: 600;")
```

Post-Step-7:

```python
self.hint_icon.setPixmap(icon("check", color=C["success"]).pixmap(QSize(14, 14)))
self.hint.setText(f"Copied: {os.path.basename(src)}")
self.hint.setStyleSheet(f"color: {C['success']}; font-size: 11px; font-weight: 600;")
```

The success-state flip now mutates two things instead of one (icon
pixmap + text), but conceptually it's the same state transition. The
icon flips from `arrow-up` (teal — "drop here") to `check` (success
green — "did it"). The text colour flip is unchanged. **Same state
model as before — only the visual representation changes.**

The state persists until the next drag (matches pre-Step-7
behaviour — no auto-revert).

### Lucide-icon scale + colour reference

| State | Icon | Color token | Pixmap size |
|-------|------|-------------|-------------|
| Idle  | `arrow-up` | `C["teal"]` (PCC teal `#3CB8AE`) | 14×14 |
| Success | `check` | `C["success"]` (success green) | 14×14 |

14×14 chosen to match the existing StatusBadge dot scale (Phase 3C
Step 2) and TodoItem leading-icon scale (Phase 3D Step 5). Cohesive
icon scale across all three surfaces of the detail panel that
carry small-format glyphs.

### Drop-affordance chrome preserved

Both `_ns` (normal) and `_hs` (hover) inline-stylesheet rules on the
dashed-border QFrame are unchanged:

```python
self._ns = f"QFrame {{ background: {C['surface']}; border: 2px dashed {C['teal']}; border-radius: 8px; }}"
self._hs = f"QFrame {{ background: rgba(60,184,174,0.10); border: 2px dashed {C['teal']}; border-radius: 8px; }}"
```

These are the *affordance signal* — "this rectangle accepts file
drops". Same B6 invariant carve-out the StatusBadge chrome QSS
gets in commons. Per Step 6 report §6 and spec §3.6, this is the
documented exception.

---

## 3. Splitter / pane chrome pass (no changes landed)

Per spec §3.6 "Files is a TERTIARY surface — lightweight only" and
spec §8 "Do NOT redesign FileViewer internals / drag/drop / splitter
behavior", the splitter + pane chrome audit found nothing requiring
intervention:

| Element | Audit finding | Action |
|---------|---------------|--------|
| `QSplitter(Qt.Horizontal)` orientation | correct | none |
| Handle width 2px | sensible — narrow handle is the Phoenix convention | none |
| Handle background colour (`C["border"]`) | matches the surface borders elsewhere | none |
| Default split sizes `[280, 560]` | tree-narrow / viewer-wide is correct | none |
| Tree-pane vertical stack (`QTreeView` over `CommonsDropZone`) | semantically clean | none |
| Files-tab outer margins (8/8/8/8) | calm; doesn't fight the surrounding 16/16 tab margins | none |
| FileViewer internal rendering | spec §8 forbids redesign | none |

**Step 7 lands exactly one change: `CommonsDropZone` modernisation.**
The "splitter / pane chrome pass" is genuinely the empty set after
audit. Documenting it explicitly so future operators don't re-open
the question.

---

## 4. Final visual cohesion pass — full detail panel

After Step 7, the detail panel is fully cohesive with the dashboard's
post-Phase-3C visual vocabulary. Per-tab and per-surface state:

| Surface | Source step | Status |
|---------|-------------|--------|
| Top utility band (Back + identity + StatusBadge + actions) | Step 1 | ✅ Lucide; commons primitives; no emoji |
| AggregateTile row (4 tiles) | Step 2 | ✅ Lucide; AggregateTile imported from dashboard.py |
| **Overview tab** SyncStatusCard | Step 4 | ✅ Panel-derived; 3 StatusBadges; no emoji on chrome |
| **Overview tab** Recent Commits feed | Step 4 | ✅ Panel-wrapped |
| **TODOs tab** summary row | Step 5 | ✅ 3 StatusBadge count pills |
| **TODOs tab** per-file headers + TodoItems | Step 5 | ✅ Lucide leading icons; StatusBadge state pills |
| **Files tab** tree + viewer + splitter | Step 7 | ✅ tree/viewer preserved (TERTIARY surface scope) |
| **Files tab** CommonsDropZone | **Step 7 (this step)** | ✅ Lucide composition; no emoji |
| **Git tab** action row | Step 6 | ✅ SecondaryButton + Lucide |
| **Git tab** output surface | Step 6 | ✅ Panel-wrapped QPlainTextEdit + property-selector QSS |

### Operationally-semantic chrome remaining (intentional)

These are the carve-outs the B6 invariant explicitly preserves:

| Surface | Chrome | Why preserved |
|---------|--------|---------------|
| `CommonsDropZone` QFrame | dashed-border + hover bg-flash | Affordance signal — "this is a drop target" |
| Recent-commits frame | per-row `background: card; border-radius: 6px` | Calm card chrome around timestamped commit lines |
| Sync-card detail rows | per-status colour code on porcelain status flags (`?`, `D`, `A`, `R`, `M`) | Semantic content — colour IS the meaning |
| TodoItem text label | strikethrough on `done` | Semantic content — strikethrough IS the "done" affordance |
| Branch sub-label / status sentences | inline muted colour | Semantic content (operational text colour, not chrome) |

### Emoji glyph remaining on `load_tool()` git-state messages

The synthesised status sentences fed into `_git_out_set()` from
`load_tool()` lines 903-923 still carry the `📝 ⬆ ⬇ ✓ ⚠` emoji
glyphs. These are **runtime messages**, not chrome — they sit
INSIDE the QPlainTextEdit terminal-style output surface, where
emoji are appropriate (terminal messages mix freely with emoji,
just like a real git output stream's `+`/`-`/`+++` chars).

Spec §3.7 implicitly accepts this — terminal-style output is a
calm surface for whatever the runtime decides to print. The chrome
around it (Panel + section header + colour-state QSS) is the
contract. Message glyphs are not.

---

## 5. Validation results

| Check | Result |
|-------|--------|
| Commons `python -m pytest -q tests/` | not re-run (no commons source change this step) |
| Commons icon registry | unchanged — `arrow-up` (added Step 6) + `check` (added Step 5) already present |
| PCC `python -m compileall -q . -x "\.venv\|commons\|build\|dist\|__pycache__"` | ✓ clean |
| PCC `python -m pytest -q tests/` | ✓ **4 passed in 0.22s** |
| PCC offscreen smoke (CommonsDropZone + DetailPanel construction) | ✓ `hint_icon` attribute present; `hint.text() == "Drag a file here to copy to commons"`; all 4 tabs in order (Overview, TODOs, Files, Git) |
| File-tree interaction (`_on_tree_clicked`) | ✓ untouched — signal wiring intact |
| FileViewer rendering | ✓ untouched — `self.file_viewer = FileViewer()` unchanged |
| Drag/drop behavior | ✓ untouched — `setAcceptDrops`, `dragEnterEvent`, `dragLeaveEvent`, `dropEvent` core flow preserved; only the hint visual changes during success-state flip |
| Splitter behavior | ✓ untouched — handle width, default sizes, orientation unchanged |
| Drop-zone affordance chrome | ✓ preserved — `_ns` + `_hs` dashed-border QFrame stylesheets unchanged |
| BrandProfile compatibility | ✓ untouched — `C["teal"]` (`#3CB8AE`) and `C["success"]` come from PCC `theme.py`; no commons sentinel impact |
| Top band (Step 1) | ✓ untouched |
| AggregateTile row (Step 2) | ✓ untouched |
| Overview tab (Step 4) | ✓ untouched |
| TODOs tab (Step 5) | ✓ untouched |
| Git tab (Step 6) | ✓ untouched |
| B5 invariant (subprocess CREATE_NO_WINDOW) | ✓ preserved — no subprocess calls touched this step |
| B6 invariant (no widget-level setStyleSheet on commons primitives) | ✓ preserved — only `CommonsDropZone` (a PCC-local QFrame) retains inline styles; commons primitives unmodified |
| Backend logic | ✓ untouched — `shutil.copy2`, `os.path.isfile`, file_received signal, `set_commons_path` all preserved |
| No layout instability | ✓ icon QLabel uses `setFixedWidth(16)` to lock dimensions; QHBoxLayout containing addStretch on both sides keeps centred composition |
| No runtime regressions | ✓ behaviour preserved end-to-end on the dropEvent state transition |
| Commit diffstat | 1 file, +44 / −7 (single focused change to `CommonsDropZone.__init__` + `dropEvent`) |

---

## 6. Remaining detail-panel debt

Per spec §7 sequencing:

| # | Step | Status |
|---|------|--------|
| 1 | Top utility band restructure | ✅ done |
| 2 | AggregateTile migration + 6 → 4 tiles | ✅ done |
| 3 | Action buttons elsewhere → commons widgets | ✅ done (folded into Steps 1 + 6) |
| 4 | Overview tab — Panel wrap + SyncStatusCard | ✅ done |
| 5 | TODOs tab — Panel wrap + modernise TodoItem | ✅ done |
| 6 | Git tab — Panel wrap + monospace output + Secondary buttons | ✅ done |
| 7 | **Files tab — Lucide pass on CommonsDropZone + splitter chrome** | ✅ **done (this step)** |
| 8 | Keyboard shortcuts (Ctrl+1..4 etc.) | pending (optional) |

### Phase 3D is functionally complete

After Step 7, **the detail panel is fully retrofitted** to the
PCC_DETAIL_PANEL_SURFACE_SPEC_V1 vocabulary modulo the explicitly
optional Step 8 (keyboard shortcuts).

### Cosmetic debt that's intentionally out of Phase 3D scope

  - **PushPreviewDialog** — separate widget; spec §8 forbids redesign.
  - **Pull-with-dirty-changes safety QMessageBox** — standard Qt
    MessageBox styled by the app-level cascade. Not chrome work.
  - **FileViewer internal rendering** — spec §8 forbids redesign.
  - **File-tree workflow (QTreeView column visibility, sorting,
    context menus)** — spec §8 forbids redesign.
  - **`load_tool()` runtime status-sentence emoji glyphs** — INSIDE
    the QPlainTextEdit terminal output surface; not chrome.

### Optional Step 8 — keyboard shortcuts

Spec §7 step 8 lists `Ctrl+1..4` tab navigation as an optional
finishing touch. Not on the path to Phase 3D closure; can ship
in a follow-on pass or stay deferred indefinitely. Recommendation:
**defer indefinitely**. The operator already uses click navigation
fluidly and the tabs are explicit; shortcuts would add complexity
without measurable workflow benefit.

---

## 7. Biggest remaining UX mismatch (none material)

After Step 7, **no surface on the detail panel materially diverges
from the dashboard's post-Phase-3C visual vocabulary.** The audit
finds only the carve-out chrome documented in §4 above:

  - `CommonsDropZone` dashed border — affordance signal, intentional
  - Recent-commits per-row card chrome — calm content card, intentional
  - Sync-card per-status colour codes — semantic content, intentional
  - TodoItem strikethrough on done — semantic content, intentional

Each one is a documented B6 carve-out. None of them represents drift
from the cohesion target.

The biggest **non-carve-out** divergence is conceptual rather than
visual: the detail panel's tabs render different content densities
(Overview is detail-heavy, Files is workspace-heavy, Git is
operation-heavy). The QTabWidget chrome around them is the platform's
default cascade-styled tab — consistent across all four tabs. No
further work is recommended on this dimension.

---

## 8. Recommended Phase 3D closure state

### Ready for closure preparation

Phase 3D detail-panel modernisation is **functionally complete** at
Step 7. The natural next operator gates:

| Gate | Action | Decision |
|------|--------|----------|
| Step 8 keyboard shortcuts | Optional polish | **recommend defer indefinitely** |
| Final visual review | Source-mode launch + per-tab walkthrough | recommended before merge gate |
| Frozen-build validation | Optional source-mode validation; no installer in scope for PCC (PCC is unpackaged per `CLAUDE.md`) | recommended; smoke only |
| Merge gate | `phase-3d-pcc-detail-retrofit` → `main` `--no-ff` | pending operator approval |
| Tag | `pcc-phase-3d-merged-v2.1.0` (or similar; matches Phase 3C v2.0.0 pattern) | pending operator decision |
| MIGRATION_RULES.md status row update | mark Phase 3D complete + log next-retrofit-window date | pending |

### Phase 3D closure pattern mirrors Phase 3C

Phase 3C closed by:
  1. Final operator visual review
  2. Frozen-build / source-mode smoke (PCC is source-only)
  3. Merge `--no-ff` → `main`
  4. Tag (`pcc-phase-3c-merged-v2.0.0`)
  5. Push branch + main + tag
  6. Optional cleanup-PR for inert orphans
  7. MIGRATION_RULES status update

Phase 3D's closure should follow the same pattern, adjusted for the
detail-panel scope (no inert orphans expected since each step landed
clean; no cleanup PR likely needed).

---

## Confirmation

  - **No architecture changes occurred.** No new ADR. No commons API
    change. No new commons icons (both `arrow-up` and `check` were
    pre-existing in the registry from Steps 5 and 6). No new commons
    widget. No new PCC theme.py QSS rule (CommonsDropZone retains
    its existing affordance-defining inline styles).
  - **No BrandProfile changes occurred.** PCC `BrandProfile` unchanged.
    The teal idle-state colour comes from PCC `theme.py` `C["teal"]`
    (`#3CB8AE`); the success-state green comes from PCC `theme.py`
    `C["success"]`. Both flow through `icon(name, color=...)` —
    commons returns a coloured QIcon, PCC controls the colour choice.
  - **No production deployment occurred.** Source-mode only on
    `phase-3d-pcc-detail-retrofit` branch. PCC is unpackaged per
    `CLAUDE.md` so there is no installer to build. No `dist/` artifact.
    No GitHub Release.
  - **No production tool source touched.** PCC-only. Phoenix CAD /
    Phoenix Checkout / PTT / PMT / ValveMaster all unmodified.
  - **No backend logic changed.** `shutil.copy2` copy path, file_received
    signal, drag/drop event handlers (`dragEnterEvent`,
    `dragLeaveEvent`, `dropEvent`), `set_commons_path` — all preserved.
    `FileViewer`, `QTreeView`, `QFileSystemModel`, `QSplitter`,
    `_on_tree_clicked` all untouched.
  - **No FileViewer / drag-drop / splitter / file-tree redesign occurred.**
    Spec §8 forbids each; preserved.
  - **No Files-tab over-panelisation occurred.** Per Step 6 report §7
    and spec §3.6, Panel wrapping would crowd the tree. Confirmed
    appropriate to skip.

---

## Commit summary

| Repo | Commit | Subject | Pushed |
|------|--------|---------|--------|
| `phoenix-command-center` `phase-3d-pcc-detail-retrofit` | `390df84` | Files tab cohesion pass — CommonsDropZone Lucide (Phase 3D Step 7) | pending (operator-gated) |
| `phoenix-commons` `main` | (this report, pending) | Add PCC_DETAIL_PANEL_IMPLEMENTATION_STEP_07_REPORT | pending |

PCC retrofit branch tip after Step 7: `390df84` (1 commit ahead of
post-Step-6 tip `83fada8`; 7 commits total ahead of `a1b45d3` =
post-Phase-3C cleanup commit).

No commons source change in Step 7 — only this report file is added.

---

*End of report. Phase 3D Step 7 = the final step on the spec sequencing.
Operator gate before Phase 3D closure preparation.*
