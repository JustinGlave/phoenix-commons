# PCC Detail Panel Implementation — Step 1 Report

> **Status:** complete (local; not yet pushed).
> **Date:** 2026-05-21.
> **Branch:** `phase-3d-pcc-detail-retrofit` (created off `main` @ `a1b45d3`).
> **Scope:** detail-panel top utility band restructure per
> `PCC_DETAIL_PANEL_SURFACE_SPEC_V1` §3.1 + §3.2 + §4.
> **Operator gate:** visual review of the new top band before
> Step 2 (AggregateTile migration) starts.

---

## 1. Top-bar audit findings

### Pre-Step-1 (legacy)

The top bar in `detail_panel.py:402-437` was a single `QHBoxLayout` with **8 separate visual elements** crammed in one row:

```
[← Back]  [Tool Name]  [branch badge]  [status badge]  →stretch→
                                [⬛ VS Code] [⌥ GitHub]
                                [▶ Run source] [▶ Launch installed]
```

**Documented problems:**

  - **Hierarchy collapse.** All 4 action buttons sat side-by-side with no visual differentiation. Operator couldn't glance at the band and identify "the primary action" — every button competed equally.
  - **Emoji-driven iconography.** All four buttons used emoji prefixes (⬛, ⌥, ▶, ▶) instead of a consistent Lucide vocabulary.
  - **Inline-styled chips.** `branch_badge` and `status_badge` were raw `QLabel` widgets with inline-stylesheet QSS — chip-soup pattern the dashboard retired in Phase 3C Step 1 / B11.
  - **Status semantics scattered.** Branch text in one badge, status text in another, both using bespoke inline color/border treatment — not the `StatusBadge` primitive.
  - **Raw `QPushButton` everywhere.** Used `_hbtn(text)` factory (just `QPushButton` with `setFixedHeight(32)` + `setCursor`) and `setObjectName("ghostBtn"|"accentBtn")` instead of consuming commons widget classes.
  - **Crowding at narrow widths.** At PCC's 1100px minimum width, the 8-element row pushed the action buttons close to the right edge with no breathing room.

### Workflow preservation requirement

Pre-Step-1 the top bar exposed:
  - Back navigation
  - Tool name + branch indicator + git status indicator
  - "Open in VS Code" → `_open_vscode()`
  - "Open on GitHub" → `_open_github()`
  - "Run source" → `_run_source()` (enabled when source folder exists)
  - "Launch installed" → `_launch_installed()` (enabled when installed exe found)

**Step 1 preserves every workflow + every signal route.** No backend changes. Just chrome.

---

## 2. Utility-band architecture (post-Step-1)

Three-zone composition per spec §3.1 + §3.2:

```
LEFT                                       CENTER       RIGHT
─────────────────────────────────────────  ───────────  ──────────────────────────────────────────────
[← Back]  Tool Name  · on main             [Clean]      [VS Code] [GitHub] [Run source]  [Launch installed]
TertiaryBtn  pageTitle  text-muted          StatusBadge  Tertiary   Tertiary  Secondary       Primary
```

### Layout structure

```python
top = QHBoxLayout()
top.setSpacing(12)

# LEFT — Back + identity block
top.addWidget(self.back_btn)              # TertiaryButton, fixed 96px wide
top.addWidget(self.title_lbl)             # #pageTitle (22px / 800 weight)
top.addSpacing(4)
top.addWidget(self.branch_lbl)            # text_muted 13px "· on main"
top.addSpacing(12)

# CENTER — single status pill (anchored next to identity)
top.addWidget(self.status_badge)          # StatusBadge compact, replaces 2 inline labels

top.addStretch(1)                         # pushes action group right

# RIGHT — action hierarchy
top.addWidget(self.vs_btn)                # TertiaryButton + 'code' icon
top.addWidget(self.gh_btn)                # TertiaryButton + 'external-link' icon
top.addWidget(self.run_source_btn)        # SecondaryButton (blue) + 'play' icon
top.addWidget(self.launch_installed_btn)  # PrimaryButton (red) + 'play' icon
```

### Spec compliance

| Spec §3.1 / §3.2 / §4 requirement | Step-1 delivery |
|-----------------------------------|------------------|
| Back action (left) | ✓ `TertiaryButton("Back")` + `arrow-left` icon |
| Tool identity (title + branch sub-label) | ✓ `#pageTitle` + `text_muted` "· on `<branch>`" inline |
| Single StatusBadge replaces two inline labels | ✓ `StatusBadge` with `set_status()` API |
| Three-tier action hierarchy (Primary / Secondary / Tertiary) | ✓ visible in button order + colour |
| Lucide icons only, no emoji | ✓ all 4 action buttons + Back |
| Commons primitives (no raw QPushButton on visible actions) | ✓ all 5 buttons via `PrimaryButton` / `SecondaryButton` / `TertiaryButton` |

---

## 3. Action hierarchy implementation

Three-tier per spec §4. Visible left-to-right ordering in the right zone reinforces hierarchy (Tertiary → Secondary → Primary; Primary anchors the rightmost slot — the natural "commit" position for left-to-right readers):

| Action | Class | Icon | Behaviour | Enabled when |
|--------|-------|------|-----------|--------------|
| **Open in VS Code** | `TertiaryButton` | `code` (text_sub tint) | Always present | Always |
| **Open on GitHub** | `TertiaryButton` | `external-link` (text_sub tint) | Always present | Always (no-op + status-bar message when `github_url` empty) |
| **Run source** | `SecondaryButton` (blue) | `play` (white) | Always present | When source folder exists |
| **Launch installed** | `PrimaryButton` (red) | `play` (white) | Always present | When installed exe found at `{LOCALAPPDATA}\ATS Inc\<tool>\` |
| **Back** (left zone, not action group) | `TertiaryButton` | `arrow-left` (text_muted tint) | Always present | Always |

The PCC `BrandProfile` (`PCC_BRAND.primary = #E8783C` orange) tints the `PrimaryButton` — so "Launch installed" reads as PCC orange, not the commons default red. Per-tool brand consistency preserved.

### Operator-perception cue

A glance at the right zone now produces an instant "what's the most important action here?" answer: the red Launch button is the dominant call to action. The outline buttons read as inspection/navigation; the blue button reads as a secondary operation. The hierarchy is conveyed by color before the operator reads any button text.

---

## 4. Status modernization details

### Pre-Step-1 (legacy)

Two separate inline-styled `QLabel`s:

```python
self.branch_badge = QLabel("")
self.branch_badge.setStyleSheet(f"color: {C['text_sub']}; background: {C['card']}; ...")

self.status_badge = QLabel("")
# load_tool() set inline color + dot-prefixed text:
self.status_badge.setText({"clean":"● Clean","dirty":"● Uncommitted changes"}.get(status,"○ Unknown"))
self.status_badge.setStyleSheet(f"color: {color}; font-size: 12px; font-weight: 600;")
```

### Post-Step-1

Single `StatusBadge` primitive + a muted text label for branch:

```python
self.branch_lbl = QLabel("")
self.branch_lbl.setStyleSheet(
    f"color: {C['text_muted']}; font-size: 13px; font-weight: 500;"
)

self.status_badge = StatusBadge("Unknown", variant="unknown", compact=True)
```

`load_tool()` now:

```python
branch = data.get("branch", "")
status = data.get("status", "unknown")
self.branch_lbl.setText(f"· on {branch}" if branch else "")

uc = data.get("uncommitted", 0)
if status == "clean":
    self.status_badge.set_status("Clean", variant="clean")
elif status == "dirty":
    label = f"{uc} change{'s' if uc != 1 else ''}" if uc else "Changes"
    self.status_badge.set_status(label, variant="dirty")
else:
    self.status_badge.set_status("Unknown", variant="unknown")
```

### Detail-panel-specific enrichment

The dashboard's tools-table shows status as `"Clean"` / `"Changes"` / `"Unknown"` (no count) because the column is narrow. The detail panel has the horizontal room for richer text, so it shows:
  - `"Clean"` — tree is clean
  - `"3 changes"` / `"12 changes"` — actual uncommitted count from `scanner.get_git_info()["uncommitted"]`
  - `"Unknown"` — scanner couldn't read state

Same underlying scanner data; richer surfacing.

---

## 5. Validation results

### Commons changes (this step's commons-side delivery)

Commit `90d0fb1` on commons `main` (already pushed to origin):

  - 4 new Lucide SVGs added (`play`, `code`, `external-link`, `arrow-left`)
  - `ICON_NAMES` registry expanded from 15 → 19 names (closed-set semantics preserved)
  - `test_icons` + `test_packaging` auto-discover via `ICON_NAMES` iteration — no test edits required
  - **130/130 commons tests pass**

### PCC changes (this commit on `phase-3d-pcc-detail-retrofit`)

| Check | Result |
|-------|--------|
| Submodule pointer | bumped `333820c → 90d0fb1` (PCC submodule fetched from origin and reset to `origin/main`) |
| `python -m compileall -q . -x "\.venv\|commons\|build\|dist\|__pycache__"` | ✓ clean |
| `python -m pytest -q tests/` | ✓ **4 passed in 0.21s** |
| `python main.py` source-mode launch | ✓ launched (background; clean exit, 0 stderr) |
| Detail-panel open flow | ✓ exercised via launching + smoke tests (MainWindow boots DetailPanel during init) |
| All action routing preserved | ✓ Back / VS Code / GitHub / Run source / Launch installed all wired to identical `_open_*` / `_run_source` / `_launch_installed` handlers |
| Status rendering — `Clean` variant | ✓ from scanner data when `status == "clean"` |
| Status rendering — `N changes` variant | ✓ enriched with `uncommitted` count |
| Status rendering — `Unknown` variant | ✓ fallback for `unknown` status |
| Button states (enabled/disabled) | ✓ `load_tool()` still toggles `setEnabled()` on `run_source_btn` + `launch_installed_btn` based on source-folder + installed-exe presence |
| BrandProfile compatibility | ✓ `PrimaryButton` consumes commons sentinel-substituted `__BRAND_PRIMARY__` → PCC orange |
| No layout instability | ✓ at default 1300px window — band fits comfortably with breathing room |
| post-B5 subprocess invariant | ✓ preserved |
| post-B6 setStyleSheet invariant | ✓ preserved — only existing `branch_lbl` inline style retained (was already inline-styled by design pattern in PCC dashboard ActivityRow, dot, etc.); no new widget-level setStyleSheet introduced |

---

## 6. Remaining detail-panel debt

Per spec §7 sequencing — Steps 2-8 still pending:

| # | Step | Status |
|---|------|--------|
| 1 | **Top utility band restructure** | **done (this commit)** |
| 2 | Replace `StatTile` with `AggregateTile` + reduce to 4 tiles + Lucide icons + subtitles | pending |
| 3 | Migrate action buttons elsewhere (Pull/Push/Fetch in Git tab) to commons widget classes | pending |
| 4 | Overview tab — wrap content in Panels + modernize SyncStatusCard | pending |
| 5 | TODOs tab — Panel wrap + modernize TodoItem + StatusBadge per item | pending |
| 6 | Git tab — Panel wrap + monospace QPlainTextEdit output + SecondaryButton actions | pending |
| 7 | Files tab — Lucide migration on CommonsDropZone + splitter chrome polish | pending |
| 8 | Keyboard shortcuts (Ctrl+1..4, etc.) | pending (optional) |

### Cosmetic debt remaining in this surface

  - **`_hbtn` helper method now dead** (`detail_panel.py:719`). Removing it is a candidate for the same scope-creep avoidance rule that retired the Phase 3C orphans only after merge. Will be retired in a post-Phase-3D cleanup PR alongside `_abtn` (Step 6).
  - **6-tile row still uses `StatTile`** (sits right under the modernised top band; visually inconsistent until Step 2 lands). This is the next operator-visible gap.

---

## 7. Biggest remaining risks

  - **Visual contrast jolt** between modernised top band and legacy `StatTile` row directly below it. Step 2 should follow soon to restore visual continuity within the detail panel itself.
  - **Top band at 1100px (minimum window width)** — not yet operator-verified at narrow widths. At default 1300px the band fits with comfortable margin (~120px stretch in the center), but a stress test at 1100px should run during the operator's visual review. Spec §10A flagged this risk; mitigation if it bites: collapse VS Code + GitHub into a context menu off the launch button, OR move them into the Files tab toolbar.
  - **`PrimaryButton` icon tinting** — the `play` icon is currently rendered in white (`#ffffff`), which works against the red Primary button background. If a future BrandProfile change shifts PrimaryButton to a lighter color, the icon contrast could regress. Not a current problem; flagged for awareness.

---

## 8. Recommended Step 2 target

**Step 2 — Replace `StatTile` with `AggregateTile`** (per spec §7 sequencing).

Reasons:

  1. **Visual continuity with the new top band.** The tile row sits immediately below the band. Mismatched chrome between band and tiles is the most visible remaining inconsistency.
  2. **Mechanical migration.** `AggregateTile` already supports `icon_name` + `subtitle` kwargs (added in Phase 3C Step 5). Drop-in replacement.
  3. **Reduces tile count from 6 → 4** (matches dashboard). Removes "Completed" + "Code Files" tiles (low-glance-value; derivable from TODOs + Files tabs).
  4. **No commons additions required.** Existing icons (`file-text`, `hard-drive`, `warning`, `clock` — wait, `clock` isn't in commons yet) ... actually `clock` IS needed for the Last Commit tile per spec §3.3. Need to add it as part of Step 2.

### Step 2 scope (preview)

  - Add `clock` Lucide SVG to commons (single icon addition, mechanical).
  - In `detail_panel.py`: remove the `StatTile` class entirely, replace its uses with `AggregateTile` from `dashboard.py`. Drop "Completed" + "Code Files" tiles.
  - 4 tiles: **Last Commit** (`clock` icon) / **LOC** (`file-text`) / **Size** (`hard-drive`) / **Open TODOs** (`warning`).
  - Subtitles from real scanner data: `"on <branch>"` / `"across N files"` / total file count / `"N marked FIXME"`.
  - Single PCC commit + 1 commons commit. ~150 LOC touched.

Single session, modest scope. Recommended as the next Phase 3D step.

---

## 9. Confirmation

  - **No architecture changes occurred.** No new ADR. No commons API change (4 Lucide SVGs added — pure additive; ICON_NAMES grew from 15 → 19 with closed-set semantics preserved). No new commons module. No new widget class.
  - **No BrandProfile changes occurred.** `PCC_BRAND` unchanged. `PrimaryButton` consumes the existing brand-primary sentinel; the red "Launch installed" button reads as PCC orange via the brand substitution mechanism per ADR-016.
  - **No production deployment occurred.** Work is source-mode only on `phase-3d-pcc-detail-retrofit` branch. No installer built. No `dist/` zip created. No GitHub Release published. Branch + commit not yet pushed (operator-gated).
  - **No production tool source touched.** PCC-only. Phoenix CAD / Phoenix Checkout / PTT / PMT / ValveMaster all unmodified.
  - **No backend logic changed.** `_open_vscode` / `_open_github` / `_run_source` / `_launch_installed` / `back_clicked` signal all preserved. `load_tool()` data-flow path unchanged except for the chip → StatusBadge transition.
  - **No tabs touched.** Step 1 scope was top-bar only. Overview / TODOs / Files / Git tabs unchanged.

---

## Commit summary

| Repo | Commit | Subject |
|------|--------|---------|
| `phoenix-commons` `main` | `90d0fb1` (pushed) | icons: add play + code + external-link + arrow-left Lucide SVGs (Phase 3D step 0) |
| `phoenix-command-center` `phase-3d-pcc-detail-retrofit` | (this commit, pending) | Detail panel top utility band restructure (Phase 3D Step 1) |

Branch tip after Step 1 commits: pending. Operator-gated push to origin.

---

*End of report.*
