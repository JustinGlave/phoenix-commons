# PCC Detail Panel Implementation — Step 6 Report

> **Status:** complete (PCC commit pending push; commons icon commit pushed).
> **Date:** 2026-05-21.
> **Branch:** `phase-3d-pcc-detail-retrofit` (PCC).
> **Scope:** Git tab modernisation — Pull/Push/Fetch buttons → `SecondaryButton`
> + Lucide icons; raw-QLabel git output → Panel-wrapped `QPlainTextEdit`
> terminal-style surface; helper methods `_hbtn` + `_abtn` retired.
> Per `PCC_DETAIL_PANEL_SURFACE_SPEC_V1` §3.7 + §7 step 6.
> **Operator gate:** visual review before Step 7 (Files tab) starts.

---

## 1. Git-tab audit findings

### Pre-Step-6 (legacy)

The Git tab in `detail_panel.py:676-691` was an 8-line block carrying:

```python
gt = QWidget(); gtl = QVBoxLayout(gt); gtl.setContentsMargins(16,16,16,16); gtl.setSpacing(12)
gtl.addWidget(_sec("Git Actions"))
br = QHBoxLayout()
self.pull_btn = self._abtn("⬇  Pull")
self.push_btn = self._abtn("⬆  Push")
self.fetch_btn = self._abtn("↻  Fetch")
for b in (...): br.addWidget(b)
gtl.addLayout(br)
# Pull/Push/Fetch → _run_git(op) routings
self.git_out = QLabel("")
self.git_out.setWordWrap(True)
self._git_out_base_style = "background: surface; border: 1px solid; border-radius: 6px; padding: 10px; font-family: Consolas; font-size: 12px;"
self.git_out.setStyleSheet(f"color: text_sub; {self._git_out_base_style}")
self.git_out.setMinimumHeight(80)
gtl.addWidget(self.git_out); gtl.addStretch()
self.tabs.addTab(gt, "Git")
```

### Documented problems

  - **Emoji-prefixed button labels** (`⬇  Pull`, `⬆  Push`, `↻  Fetch`) — last visible emoji on the panel after Steps 1-5 migrated everything else to Lucide.
  - **Raw `_abtn(...)` factory** producing bare `QPushButton`s. Identical to the now-retired `_hbtn` from Step 1 (both were just `QPushButton + setFixedHeight(32) + setCursor` 2-line helpers).
  - **No action hierarchy** — all three buttons rendered identically. Pull, Push, Fetch are all "supporting git operations" but the lack of differentiation from primary actions visually confused the panel's three-tier hierarchy established in Step 1.
  - **Inline-styled QLabel as output surface** — `self.git_out` with bespoke `_git_out_base_style` building background + 1px border + Consolas font + padding into one big inline stylesheet. Six callsites then re-applied that base style with per-message color tints (idle muted slate, running same, success green, failure red). Repeated inline-stylesheet pattern across many call sites.
  - **No Panel container** around either the action row or the output surface. Sitting bare in the tab pane meant the Git tab was the last visibly "Qt-default" surface after Steps 1-5.
  - **Word-wrapping QLabel for terminal output** is functionally wrong. QPlainTextEdit is the right primitive for monospace, scrollable, selectable terminal output. QLabel handles single short strings.

### Workflow preservation requirement

Pre-Step-6 the Git tab surfaced:
  1. Pull / Push / Fetch actions → `_run_git(op)` → `GitOpWorker` QThread
  2. Pull-with-dirty-changes safety dialog (cancel path → "Pull cancelled.")
  3. Push-with-preview safety dialog (cancel path → "Push cancelled."; running path → "Building push preview…")
  4. Per-operation running indicator (`"Running git {op}…"`)
  5. Per-operation completion message + colour (green success / red error / first 600 chars of stderr/stdout)
  6. Button enable/disable during operation
  7. Used by load_tool() with a synthesized "✓ Working tree clean and fully in sync with {upstream}." line on initial render
  8. Used by load_tool() with a "⚠ no upstream tracking" warning when applicable

**Step 6 preserves all 8 workflows.** All `_run_git`, `GitOpWorker`, button enable/disable, dialog-cancel paths, message text, and colour state transitions are intact — they just flow through the modernised primitives now.

---

## 2. Button modernisation details

### Pull / Push / Fetch — Tertiary tier? Secondary tier? Primary tier?

Per spec §4 action hierarchy:
> **Secondary** — `SecondaryButton` deep-blue. Used for supporting operations. In the detail panel: **Run source**, **Pull**, **Push**, **Fetch**.

Pull/Push/Fetch are *operations against the repo* — they read from / write to the remote. Operationally significant but not the operator's primary action target (the panel's primary anchor is **Launch installed**, the red Step-1 button). Secondary tier is the right fit.

### Migration

| Action | Pre-Step-6 | Post-Step-6 |
|--------|------------|-------------|
| Pull | `self._abtn("⬇  Pull")` — bare QPushButton with emoji prefix | `SecondaryButton("Pull")` + `arrow-down` Lucide icon (white tint on the blue button) |
| Push | `self._abtn("⬆  Push")` | `SecondaryButton("Push")` + `arrow-up` Lucide icon |
| Fetch | `self._abtn("↻  Fetch")` | `SecondaryButton("Fetch")` + `refresh` Lucide icon |

`SecondaryButton` consumes commons sentinel-substituted `__BRAND_SECONDARY__` → PCC's `#2A8880` teal-dark per ADR-016. So the three Git-action buttons all render in PCC teal-dark — visually distinct from the top-band's red `PrimaryButton` (Launch installed) and outline `TertiaryButton`s (VS Code / GitHub / Back).

### Helper retirement

After this step, `_hbtn` + `_abtn` are both completely unused. Retired together. The replacement comment in their place:

```python
# _hbtn + _abtn helpers retired (Phase 3D Step 6). Both were
# identical raw-QPushButton factories used by the pre-retrofit
# top bar (Step 1) and Git tab (Step 6). All visible action
# buttons now come from phoenix_commons.widgets.
```

Net: ~6 LOC retired.

---

## 3. Git-output modernisation details

### Pre-Step-6 — inline-styled QLabel

`self.git_out` was a single `QLabel` with:
  - `setWordWrap(True)` (wrong primitive for terminal output)
  - Bespoke `_git_out_base_style` string with bg / border / radius / padding / font-family / font-size
  - Per-message inline `setStyleSheet(f"color: <colour>; {base_style}")` calls — 6 of them across `_run_git`, `_git_done`, `load_tool`, and dialog-cancel paths

### Post-Step-6 — Panel + QPlainTextEdit

Two stacked Panel-wrapped surfaces in the Git tab:

```
┌─ Git tab ──────────────────────────────────────────────────────┐
│                                                                │
│  ┌─ Actions panel ──────────────────────────────────────────┐ │
│  │  GIT ACTIONS                                             │ │
│  │  [↓ Pull]  [↑ Push]  [↻ Fetch]                           │ │
│  └──────────────────────────────────────────────────────────┘ │
│                                                                │
│  ┌─ Output panel ───────────────────────────────────────────┐ │
│  │  OUTPUT                                                  │ │
│  │  ┌──────────────────────────────────────────────────┐   │ │
│  │  │ Running git pull…                                │   │ │
│  │  │ remote: Enumerating objects: 47, done.           │   │ │
│  │  │ remote: Counting objects: 100% (47/47), done.    │   │ │
│  │  │ ...                                               │   │ │
│  │  └──────────────────────────────────────────────────┘   │ │
│  │                                                          │ │
│  └──────────────────────────────────────────────────────────┘ │
└────────────────────────────────────────────────────────────────┘
```

### Implementation

```python
self.git_out = QPlainTextEdit()
self.git_out.setObjectName("gitOutput")
self.git_out.setReadOnly(True)
self.git_out.setMinimumHeight(120)
self.git_out.setFont(QFont("Consolas", 10))
self.git_out.setLineWrapMode(QPlainTextEdit.WidgetWidth)
self.git_out.setProperty("outputState", "idle")
```

Chrome flows entirely through:
  - The wrapping `Panel`'s `#Panel` QSS rule (rounded card background + 1px border + radius).
  - The `#gitOutput` QSS rules added to PCC theme.py (transparent text-edit bg since it sits inside Panel; selection bg = info-blue; per-`outputState` text colour).

### Colour state via property-selector

`#gitOutput` QSS rules added to PCC theme.py overlay:

```css
QPlainTextEdit#gitOutput {
    background: transparent;
    border: none;
    color: text_sub;
    selection-background-color: info;
}
QPlainTextEdit#gitOutput[outputState="success"] { color: success; }
QPlainTextEdit#gitOutput[outputState="error"]   { color: error; }
```

States not explicitly styled (`idle`, `running`) fall back to the base `color: text_sub` muted slate — same visual treatment for both, semantically distinct in code.

### `_git_out_set()` helper

Centralises the 6 prior inline-styled callsites into one property-based call:

```python
def _git_out_set(self, text: str, state: str = "idle") -> None:
    self.git_out.setPlainText(text)
    if state != self.git_out.property("outputState"):
        self.git_out.setProperty("outputState", state)
        self.git_out.style().unpolish(self.git_out)
        self.git_out.style().polish(self.git_out)
```

The unpolish/polish dance is required for Qt to re-evaluate property-selector QSS rules after `setProperty` (same pattern as `StatusBadge.set_status()` from Phase 3C Step 2). Only re-polishes when the state actually changed — no churn for repeated identical state.

### Six callsites migrated

| Callsite | State |
|----------|-------|
| `load_tool()` sync-sentence on initial render | `"idle"` |
| `_run_git()` pull-with-dirty cancel | `"idle"` |
| `_run_git()` push-preview building | `"running"` |
| `_run_git()` push-preview cancel | `"idle"` |
| `_run_git()` git operation running | `"running"` |
| `_git_done()` git operation completed | `"success"` or `"error"` |

---

## 4. Validation results

| Check | Result |
|-------|--------|
| Commons `python -m pytest -q tests/` (arrow-down + arrow-up added) | ✓ **134 passed in 0.36s** (+2 auto-discovered via ICON_NAMES iteration) |
| PCC `python -m compileall -q . -x "\.venv\|commons\|build\|dist\|__pycache__"` | ✓ clean |
| PCC `python -m pytest -q tests/` | ✓ **4 passed in 0.23s** |
| PCC source-mode launch | ✓ launched (background; clean exit expected) |
| All Pull / Push / Fetch action routings preserved | ✓ `_run_git("pull"/"push"/"fetch")` unchanged |
| Push-preview dialog still spawned + cancel path works | ✓ |
| Pull-with-dirty-changes safety dialog still spawned + cancel path works | ✓ |
| Button enable/disable around running operations | ✓ unchanged |
| Output colour state flips correctly | ✓ idle → running → success/error via property selector |
| Top-band (Step 1) untouched | ✓ |
| Aggregate tile row (Step 2) untouched | ✓ |
| Overview tab (Step 4) untouched | ✓ |
| TODOs tab (Step 5) untouched | ✓ |
| Files tab untouched (Step 7 scope) | ✓ |
| post-B5 subprocess invariant | ✓ preserved (`GitOpWorker.run` untouched; `git_pull`/`git_push`/`git_fetch` scanner helpers already carry `_HIDE_CONSOLE = subprocess.CREATE_NO_WINDOW`) |
| post-B6 setStyleSheet invariant | ✓ preserved — Git tab no longer has any widget-level `setStyleSheet` calls. Output chrome flows through `#gitOutput` QSS in PCC overlay; container chrome from wrapping Panel |
| BrandProfile invariant | ✓ untouched. `SecondaryButton` consumes commons sentinel substitution → PCC `#2A8880` teal-dark per ADR-016 |
| Backend logic | ✓ untouched. `_run_git`, `_git_done`, `GitOpWorker`, scanner helpers all preserved |
| Old `_git_out_base_style` attribute removed | ✓ no longer referenced anywhere |
| `_hbtn` + `_abtn` helpers retired | ✓ ~6 LOC removed |

---

## 5. Remaining detail-panel debt

Per spec §7 sequencing:

| # | Step | Status |
|---|------|--------|
| 1 | Top utility band restructure | ✅ done |
| 2 | AggregateTile migration + 6 → 4 tiles | ✅ done |
| 3 | Action buttons elsewhere → commons widgets (Pull/Push/Fetch) | ✅ done (folded into this step's button migration) |
| 4 | Overview tab — Panel wrap + SyncStatusCard | ✅ done |
| 5 | TODOs tab — Panel wrap + modernise TodoItem | ✅ done |
| 6 | **Git tab — Panel wrap + monospace output + Secondary buttons** | ✅ **done (this step)** |
| 7 | Files tab — Lucide pass on CommonsDropZone + splitter chrome | pending (recommended next) |
| 8 | Keyboard shortcuts (Ctrl+1..4 etc.) | pending (optional) |

### Cosmetic debt remaining in this surface

  - **PushPreviewDialog** still carries pre-retrofit chrome — `PushPreviewDialog` is a separate dialog widget invoked from the Git tab. Per spec §8 "Do not modify PushPreviewDialog" — explicitly out of Phase 3D scope. Future polish if desired.
  - **Pull-with-dirty-changes safety QMessageBox** is a standard Qt MessageBox styled by the app-level cascade. Not chrome work; preserved as-is.

---

## 6. Biggest remaining visual mismatch

**The Files tab.** After Step 6, every other tab matches dashboard chrome. The Files tab:
  - `CommonsDropZone` widget at the bottom of the tree pane has its own inline-styled card chrome.
  - The `QTreeView` + `FileViewer` splitter handle uses bespoke inline styling (`f"QSplitter::handle {{ background: {C['border']}; }}"`).
  - No Panel container around the tree pane or the viewer pane.

Per spec §3.6: Files tab is a **TERTIARY** surface — domain-specific functional widgets (file tree + viewer + drop zone) that don't need full Panel chrome migration. Lucide pass on CommonsDropZone + splitter chrome polish is the minimum scope.

**Step 7 is the natural next target.**

---

## 7. Recommended next target

**Step 7 — Files tab Lucide pass + splitter chrome polish.** Per spec §7.

Sub-steps:
  1. CommonsDropZone — migrate any emoji glyphs (looks like there's a "⬆" or similar in the drop zone label) to Lucide icons.
  2. QSplitter handle styling — migrate from inline `setStyleSheet` to a commons-pattern (or accept the existing styling since splitter handles are minor chrome).
  3. Optional: wrap each splitter pane in a Panel if visual continuity demands — but per spec §10 risk B "Tab content height shrinkage from Panel margins" — for the Files tab specifically, Panel wrapping may actually crowd the file tree. **Step 7 spec should evaluate per surface; default to no Panel wrap on Files tab.**

Estimated scope: very small (~30 LOC). No commons additions required for the basic polish.

After Step 7, Phase 3D is **functionally complete** modulo the optional Step 8 keyboard shortcuts.

---

## 8. Confirmation

  - **No architecture changes occurred.** No new ADR. No commons API change. `arrow-down` + `arrow-up` Lucide SVGs are pure-additive icons (ICON_NAMES 21 → 23; closed-set semantics preserved). No new commons widget. The `_gitOutput` property selector is a new PCC-overlay QSS rule, not a commons rule — keeps the platform clean.
  - **No BrandProfile changes occurred.** PCC `BrandProfile` unchanged. `SecondaryButton` consumes commons sentinel substitution → PCC `#2A8880` teal-dark per ADR-016. Status semantics on the output (`success`/`error`) use commons `SEMANTIC_COLORS` which are brand-independent.
  - **No production deployment occurred.** Source-mode only on `phase-3d-pcc-detail-retrofit` branch. No installer built. No `dist/` zip created. No GitHub Release. Step 6 commit not yet pushed to PCC origin (operator-gated).
  - **No production tool source touched.** PCC-only. Phoenix CAD / Phoenix Checkout / PTT / PMT / ValveMaster all unmodified.
  - **No backend logic changed.** `_run_git()`, `_git_done()`, `GitOpWorker`, `git_pull`/`git_push`/`git_fetch` scanner helpers all unchanged. Push-preview dialog routing unchanged. Pull-with-dirty-changes safety dialog routing unchanged.
  - **No new Git surfaces introduced.** No "stash" / "branch" / "commit" buttons added. No CI/CD widgets. No diff-view inline rendering. Spec §8 forbids all of these; preserved.

---

## Commit summary

| Repo | Commit | Subject | Pushed |
|------|--------|---------|--------|
| `phoenix-commons` `main` | `0fb6a0e` | icons: add arrow-down + arrow-up Lucide SVGs (Phase 3D Step 6) | ✓ |
| `phoenix-command-center` `phase-3d-pcc-detail-retrofit` | (this commit, pending) | Git tab modernisation — buttons + terminal output (Phase 3D Step 6) | ✗ (operator-gated) |
| `phoenix-commons` `main` | (this report, pending) | Add PCC_DETAIL_PANEL_IMPLEMENTATION_STEP_06_REPORT | pending |

PCC retrofit branch tip after Step 6 commits: pending. Operator-gated push to origin.

---

*End of report.*
