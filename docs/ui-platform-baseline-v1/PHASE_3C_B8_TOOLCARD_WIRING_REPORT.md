# Phase 3C B8 — ToolCard Wiring Report

> **Status:** complete (commit `2d04c7d` on PCC `phase-3c-pcc-retrofit`).
> **Date:** 2026-05-21.
> **Scope:** wire the pre-existing `ToolCard` widget into the live
> dashboard per `PHASE_3C_DESIGN_WIRING_AUDIT_REPORT.md` fix plan.
> **Out of scope:** new design, commons changes, polish, production
> deployment, widget swap to `phoenix_commons.widgets.*`.

This commit closes the audit's primary finding: PCC's intended richer
dashboard design was sitting orphaned in `tool_card.py` and is now
actually used by the running app.

---

## 1. Files changed

| File | LOC delta | Nature |
|------|----------:|--------|
| `dashboard.py` | -166 / +144 (net -22) | Removed inline `ToolRow` class + `todos_selected` signal. Added 4 forward signals, `QGridLayout` placement, `_layout_cards`, `_compute_columns`, `resizeEvent`. Updated `set_tools` signature. |
| `main_window.py` | +95 / +6 (net +89) | Replaced `todos_selected` connection with 4 new action connections. Added 4 new handlers (`_dashboard_open_github`, `_dashboard_pull`, `_dashboard_git_done`, `_dashboard_launch`). Updated `_load_tools` to pass per-tool config. |
| `tool_card.py` | unchanged | Pre-existing widget — no edits. |
| `theme.py` | unchanged | No QSS rules added. |
| `main.py` | unchanged | |

Two files modified. All other PCC source untouched. No commons
changes. No production-tool source changes.

---

## 2. Exact wiring changes

### 2a. `dashboard.py`

**New import:**
```python
from tool_card import ToolCard
```

**New / changed signals on `Dashboard`:**

```python
class Dashboard(QWidget):
    tool_selected = Signal(str)            # tool name (preserved)
    tool_vscode   = Signal(str)            # NEW — absolute path
    tool_github   = Signal(str)            # NEW — github URL (may be empty)
    tool_pull     = Signal(str)            # NEW — absolute path
    tool_launch   = Signal(str)            # NEW — absolute path
    # `todos_selected` REMOVED — ToolCard has no TODO shortcut.
```

**Layout swap:**

```python
# was:
self.list_layout = QVBoxLayout(self.list_container)
self.list_layout.setContentsMargins(0, 0, 4, 0)
self.list_layout.setSpacing(6)
self.list_layout.addStretch()

# now:
self.list_layout = QGridLayout(self.list_container)
self.list_layout.setContentsMargins(0, 0, 4, 0)
self.list_layout.setHorizontalSpacing(14)
self.list_layout.setVerticalSpacing(14)
self.list_layout.setAlignment(Qt.AlignTop | Qt.AlignLeft)
```

The `QGridLayout` import was already present in `dashboard.py:8`
since the initial commit — the audit identified this as the smoking
gun that a card grid had been intended from day one.

**Scrollbar policy:**

```python
# was:
scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
# now:
self._scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
```

`ToolCard` is fixed-height (215px). With ≥4 tools the grid overflows
the default dashboard height; the operator needs to scroll. The flat
`ToolRow` was variable-height so AlwaysOff used to work.

**`set_tools` signature + body:**

```python
def set_tools(self, tools: list, commons_name: str = "phoenix-commons",
              tools_cfg: dict | None = None):
    # ... constructs one ToolCard per tool:
    card = ToolCard(
        name=t["name"], path=t["path"],
        github_url=tc.get("github_url", ""), is_commons=is_c,
    )
    card.selected.connect(self.tool_selected)
    card.act_vscode.connect(self.tool_vscode)
    card.act_github.connect(self.tool_github)
    card.act_pull.connect(self.tool_pull)
    card.act_launch.connect(self.tool_launch)
    self._rows[t["name"]] = card
    # ...then defers placement to _layout_cards()
```

`tools_cfg` is the per-tool `pcc_config.json` dict so each card knows
its `github_url`. Defaults to empty for callers that don't have config
— GitHub button no-ops with a status-bar message when URL is empty.

**`update_tool` unchanged:** `ToolCard.update_stats(data)` accepts the
same dict shape `ToolRow.update_stats(data)` did, just with more keys
(commit/branch/loc/size/todo_count/status — all already produced by
`scanner.py`).

### 2b. `main_window.py`

**Replaced connection block:**

```python
# was:
self.dashboard.tool_selected.connect(self._open_detail)
self.dashboard.todos_selected.connect(self._open_detail_todos)
# now:
self.dashboard.tool_selected.connect(self._open_detail)
self.dashboard.tool_vscode.connect(self._open_in_editor)
self.dashboard.tool_github.connect(self._dashboard_open_github)
self.dashboard.tool_pull.connect(self._dashboard_pull)
self.dashboard.tool_launch.connect(self._dashboard_launch)
```

**Pass per-tool config to dashboard:**

```python
# was:
self.dashboard.set_tools(self.tools, commons_name)
# now:
self.dashboard.set_tools(
    self.tools, commons_name, self.cfg.get("tools", {}),
)
```

**New handlers — all small, all reuse existing helpers:**

  - `_dashboard_open_github(url)` — `webbrowser.open(url)` if non-empty,
    else status-bar message.
  - `_dashboard_pull(path)` — spawn `detail_panel.GitOpWorker("pull",
    path)` on a QThread; hold ref on `self._dashboard_workers`; wire
    `worker.done` → `_dashboard_git_done`; clean up via
    `worker.finished`.
  - `_dashboard_git_done(name, op, ok, msg)` — surface a single-line
    summary in the status bar.
  - `_dashboard_launch(path)` — look up `launch_cmd` from
    `pcc_config["tools"][name]` (default `"python main.py"`); invoke
    via `cmd /c` on Windows with `CREATE_NO_WINDOW` (no console
    flash, consistent with B5).

No new business logic. Each handler is a thin adapter onto a primitive
that already exists in `main_window` or `detail_panel`.

---

## 3. How the old `ToolRow` path was retired

  - The inline `ToolRow(QFrame)` class (formerly `dashboard.py` lines
    51–177) was deleted in full and replaced with a 10-line comment
    block explaining the change and pointing at the audit report.
  - The `todos_selected = Signal(str)` declaration was removed from
    `Dashboard`. The corresponding `MainWindow._open_detail_todos`
    method was **deliberately left in place** — it's now dead code,
    but it's defensive (any future code path that wants to open the
    detail panel on the TODOs tab can still call it). Trimming dead
    methods is out of scope for B8.
  - `dashboard.py` no longer constructs any `ToolRow` instances. The
    `_rows` dict (formerly `dict[str, ToolRow]`) is now `dict[str,
    ToolCard]`.

Search verification:

```
$ grep -rn 'ToolRow\|todos_clicked' phoenix-command-center/*.py
# (no PCC running-code matches — only mentions in the audit report
#  and this report, both in commons docs)
```

Old code path is gone end-to-end.

---

## 4. Responsive grid behaviour

The card grid recomputes its column count from the scroll viewport's
current width:

```python
def _compute_columns(self) -> int:
    viewport_w = self._scroll.viewport().width()
    if viewport_w <= 0:
        return 1  # pre-paint; resizeEvent will fix
    card_w, spacing = 270, 14
    return max(1, (viewport_w + spacing) // (card_w + spacing))
```

Concrete fits:

| Window width | Content area | Left column (3:7) | Columns shown |
|-------------:|-------------:|------------------:|--------------:|
| 1100 (min) | ~738 | ~221 | **1** |
| 1300 (default) | ~938 | ~281 | **1** |
| 1600 | ~1238 | ~371 | **1** |
| 1920 | ~1558 | ~467 | **1** |
| 2200 | ~1838 | ~551 | **1** |
| 2280+ | ~1918+ | ~575+ | **2** |
| 2920+ | ~2558+ | ~767+ | **2** |
| 3200+ | ~2838+ | ~851+ | **3** |

At realistic monitor sizes (1080p–1440p) the operator sees a
**1-column stack of cards in the left column**, with the right-column
activity feed at 7:3 width as before. Multi-column behavior unlocks
on ultra-wide and 4K monitors. This matches the spec's responsive
requirement ("1 column when narrow; 2–3 when space allows") without
clipping cards or causing horizontal overflow.

`resizeEvent` only re-layouts when `_compute_columns()` returns a
different value than `_current_cols` — pixel-level resize drags don't
churn the grid.

If the operator wants wider, denser card display before they hit a
4K monitor, the dashboard body split (`body.addWidget(left, 3); body
.addWidget(right, 7)`) could be changed to `(5, 5)` or `(7, 3)`.
**Out of scope for B8** — that's a layout design decision, not a
wiring fix.

---

## 5. Action-button routing

Each `ToolCard` action signal flows: card button → ToolCard signal →
Dashboard forward signal → MainWindow handler → existing primitive.

| Card button | ToolCard signal | Dashboard signal | MainWindow handler | Primitive |
|-------------|-----------------|------------------|--------------------|-----------|
| **VS Code** | `act_vscode(path)` | `tool_vscode(path)` | `_open_in_editor(path)` | `subprocess.Popen([editor, path], shell=...)` — **pre-existing** at `main_window.py:544` |
| **GitHub** | `act_github(url)` | `tool_github(url)` | `_dashboard_open_github(url)` | `webbrowser.open(url)` — stdlib, new 1-line handler |
| **Pull** | `act_pull(path)` | `tool_pull(path)` | `_dashboard_pull(path)` | `detail_panel.GitOpWorker("pull", path)` on QThread — **pre-existing** worker class, just spawned from a new caller |
| **Launch** | `act_launch(path)` | `tool_launch(path)` | `_dashboard_launch(path)` | `subprocess.Popen(["cmd","/c",launch_cmd], cwd=path, creationflags=CREATE_NO_WINDOW)` — mirrors `detail_panel._run_source` at `detail_panel.py:674-687` |

Card body click (anywhere not on a button) → `ToolCard.selected(name)`
→ `Dashboard.tool_selected(name)` → `MainWindow._open_detail(name)` —
unchanged from the previous `ToolRow.clicked` wiring.

No duplicated business logic. `GitOpWorker` is imported locally inside
`_dashboard_pull` to avoid pulling `detail_panel` into the top of
`main_window` (`detail_panel` already imports things from
`main_window`'s dependency graph).

---

## 6. Validation results

| Check | Result |
|-------|--------|
| `python -m compileall -q . -x "\.venv\|commons\|build\|dist\|__pycache__"` | **clean** (no errors) |
| `python -m pytest -q tests/` | **4 passed in 0.17s** (smoke: module imports, version format, MainWindow instantiates, theme QSS non-empty) |
| `python main.py` source-mode launch | **exit 0, no stderr** — window opened, ran, was closed cleanly |
| No widget-level setStyleSheet override regression (post-B6 invariant) | preserved — no setStyleSheet additions in B8 |
| No subprocess console-flash regression (post-B5 invariant) | preserved — `_dashboard_launch` uses `CREATE_NO_WINDOW`; `_dashboard_pull` uses `GitOpWorker` which uses the B5-hardened `git_pull` helper |
| Commons cascade still applies at app level (post-B6 invariant) | preserved — no widget-level overrides added |
| `phoenix_commons` import still resolves to local editable install | preserved — unchanged |
| No production-tool source touched | confirmed — only `dashboard.py` + `main_window.py` modified |
| No commons changes | confirmed — `commons/` submodule pointer unchanged |
| No `BrandProfile` / theme architecture changes | confirmed — `theme.py` unmodified |

---

## 7. Remaining visual issues

Operator-visible state after B8, **without** further code changes:

  - **At default 1300×800, cards stack 1-wide in the left column.**
    With ≥4 tools the column scrolls vertically. This IS the intended
    design at this monitor size — the audit report flagged it
    explicitly (Risk 1). Multi-column unlocks at 2280+ px window
    width (see §4).
  - **`ToolCard._mini_btn` action buttons use inline styles** (`#2E2E42`
    background, `#BBBBCC` text, accent on Launch). They don't pick up
    PCC overlay's `#accentBtn` / `#ghostBtn` palette. Visually
    consistent within the card, but diverges from the sidebar's
    button styling. Out of scope for B8 — separate touch-up if
    desired.
  - **`ToolCard` emoji glyphs** (`⏱ 📄 💾 📌 ◈ ◆ ●`) render with
    Segoe UI Emoji on Windows. Same as the rest of PCC. Consistent
    with the existing visual identity until `phoenix_commons.icons`
    SVG adoption (a separate phase).
  - **No selection state on cards.** Clicking a card opens the detail
    panel but doesn't mark the card as selected. `ToolCard` has a
    `set_selected(bool)` method already implemented — could be wired
    to track the currently-open detail tool. Out of scope for B8.
  - **Activity feed (right column) is unchanged.** Still `ActivityRow`
    in a `QVBoxLayout`. The B8 spec scoped to the tool list only.
  - **AggregateTile (top of dashboard) still inline-styled.** Same
    state as documented in `PHASE_3C_RUNTIME_POLISH_REPORT_01.md`
    §7. Out of scope here.

None are merge blockers. None are regressions. All are documented
deferred items.

---

## 8. Operator review required before merge?

**Yes — strongly recommended.** B8 is the first commit on
`phase-3c-pcc-retrofit` that changes what the operator actually sees
on the dashboard. The previous commits (B1–B7) addressed wiring +
runtime hygiene + minor polish without visibly restructuring the
dashboard.

Specific review questions the operator should answer before any merge
to `master`:

  1. Does the new card grid match the intended PCC design from
     operator memory / screenshots? (If not, the audit may have
     identified the wrong target — escalate before merging.)
  2. Is the 1-column-at-default behaviour acceptable, or should the
     body split change from 3:7 to give cards more horizontal room?
  3. Are the four action buttons (VS Code / GitHub / Pull / Launch)
     in the right order and visually distinguishable enough?
  4. Should the cards have a selection state when their detail panel
     is open?
  5. Should the GitHub button be hidden (vs. no-op) when no URL is
     configured?

If all five are "looks good as-is or as-is-with-small-tweaks," the
branch is mergeable. If any answer requires a layout-level change,
that becomes a B9 follow-up before merge.

---

## 9. Confirmation

  - **No new design invented.** `ToolCard` already existed in
    `tool_card.py` (initial commit `3d84cc9`). `QGridLayout` was
    already imported in `dashboard.py`. No new widget classes, no new
    visual concepts, no new QSS rules.
  - **No commons changes.** B8 touches only PCC source. The
    `phoenix-commons` submodule pointer is unchanged. No commons
    module was edited.
  - **No production deployment occurred.** Work is source-mode only on
    `phase-3c-pcc-retrofit`. No installer built, no `dist/` zip
    created, no GitHub Release published.
  - **No production-tool source touched.** PCC-only edits. Job
    Tracker, Phoenix CAD, Phoenix Checkout, ValveMaster all
    untouched.
  - **No BrandProfile / theme architecture changes.** `theme.py` is
    unmodified. The `apply_pcc_theme(app)` cascade from B3 + the B6
    widget-level-setStyleSheet removal are both preserved.
  - **No subprocess hygiene regression.** New `_dashboard_launch`
    uses `CREATE_NO_WINDOW` consistent with B5; new `_dashboard_pull`
    spawns the existing `GitOpWorker` which uses the B5-hardened
    `git_pull` helper.

---

## Commit summary

| Commit | Subject | Files |
|--------|---------|-------|
| `2d04c7d` | Wire ToolCard into dashboard grid (Phase 3C B8) | `dashboard.py`, `main_window.py` |

Branch tip after B8: `2d04c7d` on `phase-3c-pcc-retrofit`. Branch is
3 commits ahead of `origin/phase-3c-pcc-retrofit` (B6 + B7 + B8) and
not merged to `master`.

---

*End of report.*
