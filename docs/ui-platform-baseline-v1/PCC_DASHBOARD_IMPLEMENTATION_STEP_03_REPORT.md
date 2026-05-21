# PCC Dashboard Implementation — Step 3 Report

> **Status:** complete (commit `4e935c9` on PCC `phase-3c-pcc-retrofit`).
> **Date:** 2026-05-21.
> **Scope:** Dashboard's primary surface — tools list → `PhoenixTable`
> with NAME / LAST COMMIT / LOC / SIZE / STATUS columns, per-row
> context menu, StatusBadge in STATUS column. Sections (tools +
> activity) wrapped in commons `Panel` containers to match the spec
> screenshot's panelled chrome.
> **Operator gate:** visual review of the new table surface + context
> menu before Step 4 (per-tool activity tag colors) starts.

---

## 1. Data-flow audit findings

The pre-step audit confirmed the table can preserve existing functionality without scanner changes:

| Concern | Pre-step state | Step 3 outcome |
|---------|----------------|----------------|
| Scanner payload | `get_git_info` returns `{status, last_commit, uncommitted, dirty_files, ...}` and `get_file_stats` adds `{loc, total_size}` | Unchanged — table consumes the existing fields directly |
| Change-count availability | Already provided by `get_git_info` as `uncommitted = len(status_out.splitlines())` (line 100) | **No scanner change needed.** Step 3 brief called for `change_count`; it already exists under `uncommitted` |
| Update timing | `ScanWorker` (QThread) emits `tool_scanned(name, data)` → `MainWindow._on_tool_scanned` → `Dashboard.update_tool(name, data)` per tool | Preserved end-to-end; `Dashboard.update_tool` now delegates to `ToolsTable.update_tool` which finds the row by name and refreshes all 5 cells |
| Click routing (open detail) | `ToolRow.clicked` → `Dashboard.tool_selected` → `MainWindow._open_detail` | Now `ToolsTable.cellClicked` → `tool_selected` (row click anywhere) → same handler |
| TODOs sub-route | `ToolRow.todos_clicked` → `Dashboard.todos_selected` → `MainWindow._open_detail_todos` | **Retired.** ToolCard had no TODOs chip; the operator opens TODOs from the detail panel's TODOs tab |

`detail_panel` consumers of `uncommitted` and `dirty_files` are unaffected (no scanner field rename).

---

## 2. Table architecture

```
phoenix_commons.widgets.PhoenixTable
        ▲
        │ (subclass)
dashboard.ToolsTable    ← signals: tool_selected, act_vscode,
        │                          act_github, act_pull, act_launch
        ▼ (held by)
dashboard.Dashboard     ← forwards each act_* to a public Dashboard signal
        │
        ▼ (connected by)
main_window.MainWindow  ← routes to existing primitives:
                              _open_in_editor
                              _dashboard_open_github  → webbrowser.open
                              _dashboard_pull         → GitOpWorker (QThread)
                              _dashboard_launch       → subprocess.Popen
```

### Column model

| Idx | Column | Cell type | Source field | Alignment | Resize mode |
|----:|--------|-----------|--------------|-----------|-------------|
| 0 | NAME | `QTableWidgetItem` (italic if commons) | `t["name"]` (prettified) | Left | Stretch (fills remaining width) |
| 1 | LAST COMMIT | `QTableWidgetItem` | `data["last_commit"]` | Left | ResizeToContents |
| 2 | LOC | `QTableWidgetItem` (text role) | `data["loc"]` formatted with thousands | Right | ResizeToContents |
| 3 | SIZE | `QTableWidgetItem` | `format_size(data["total_size"])` | Right | ResizeToContents |
| 4 | STATUS | `setCellWidget` → `StatusBadge` | derived from `data["status"]` + `data["uncommitted"]` | Centred in pill | ResizeToContents |

### Behaviour

- **Row height:** fixed 40px (per spec §2 "developer-comfortable 36-44px").
- **Sorting:** intentionally disabled. Operator scans the table; doesn't query it.
- **Selection:** `SingleSelection` + `SelectRows` so a click highlights the row (commons QSS handles the hover/selected paint).
- **Grid lines:** off (`setShowGrid(False)`).
- **Outer frame:** off (`setFrameShape(QFrame.NoFrame)`) — the table sits inside a Panel container; without this it would double-border.
- **Cursor:** `Qt.PointingHandCursor` over the table viewport.
- **Click semantics:** any cell click on a row → emit `tool_selected(name)` → MainWindow opens detail panel.
- **Context menu:** right-click → `customContextMenuRequested` → per-row `QMenu` with 4 actions (§5).

### Section container

Both body sections (tools left, activity right) are now wrapped in commons `phoenix_commons.widgets.Panel` (rounded-card chrome). This matches the spec screenshot's panelled treatment — without it the table read as floating chrome. Panel's default 16px internal padding gives section content room to breathe.

### Body split

Was `3:7` (tools 30% / activity 70%) — appropriate for a flat ToolRow list, but cramped for a 5-column table. Changed to `13:7` (~65% / 35%) per spec §5. At PCC's default 1300×800 window this gives the table ~566px of horizontal real estate; the activity feed gets ~305px.

---

## 3. change_count implementation

**No scanner change.** Step 3's brief asked for `change_count` to be added to `scanner.get_git_info`, but the data was already there under a different name:

```python
# scanner.py:100 (unchanged in this commit)
result["uncommitted"] = len(status_out.splitlines())
```

The new `ToolsTable._populate_row` consumes this directly:

```python
uncommitted = data.get("uncommitted", 0) if data else 0
if status == "clean":
    label, variant = "Clean", "clean"
elif status == "dirty":
    label = f"{uncommitted} change" + ("s" if uncommitted != 1 else "")
    variant = "dirty"
else:
    label, variant = "Unknown", "unknown"
```

Producing the spec-prescribed three label forms:
  - `"Clean"` when git status is clean (count is implicitly 0)
  - `"N change"` / `"N changes"` for dirty repos (singular/plural pluralization)
  - `"Unknown"` for non-git directories or unscanned tools

Renaming `uncommitted` → `change_count` would break `detail_panel`'s consumer (4 callsites). Adopting the existing name keeps the scope of this step contained to the dashboard.

---

## 4. StatusBadge integration

The STATUS column embeds `phoenix_commons.widgets.StatusBadge` instances (introduced in Step 2):

```python
# dashboard.py — ToolsTable._populate_row
existing = self.cellWidget(row, self.COL_STATUS)
if isinstance(existing, StatusBadge):
    existing.set_status(label, variant=variant)
else:
    badge = StatusBadge(label, variant=variant, compact=True)
    self.setCellWidget(row, self.COL_STATUS, badge)
```

- **Compact mode** is on — table rows are dense; smaller pill matches the row rhythm.
- **Update path** prefers `set_status()` (in-place mutation) over `setCellWidget()` (widget replacement) on repeat updates from the scan worker — avoids unnecessary widget churn during rescans.
- **Variant mapping:**

| Scanner `status` | StatusBadge variant | Label |
|------------------|---------------------|-------|
| `"clean"` | `clean` | `"Clean"` |
| `"dirty"` (with N uncommitted) | `dirty` | `"N change"` / `"N changes"` |
| `"unknown"` or absent | `unknown` | `"Unknown"` |

`syncing` and `scanning` variants are not wired in this step — they're reserved for the sync-state pill (spec step 6) and per-tool scanning indicator (potential future addition).

---

## 5. Context-menu routing

Right-click on any row → `QMenu` with 4 actions. Each routes through a signal to a MainWindow handler that reuses an existing primitive — no duplicated business logic.

| Menu item | Disabled when | Signal | MainWindow handler | Underlying primitive |
|-----------|---------------|--------|---------------------|----------------------|
| Open in VS Code | (never) | `act_vscode(path)` | `_open_in_editor(path)` (pre-existing) | `subprocess.Popen([editor, path], shell=True)` |
| Open GitHub | `github_url` empty | `act_github(url)` | `_dashboard_open_github(url)` (new) | `webbrowser.open(url)` |
| Pull | (never) | `act_pull(path)` | `_dashboard_pull(path)` (new) | `detail_panel.GitOpWorker("pull", path)` on QThread |
| Launch | (never) | `act_launch(path)` | `_dashboard_launch(path)` (new) | `subprocess.Popen(["cmd","/c",launch_cmd], cwd=path, creationflags=CREATE_NO_WINDOW)` |

Per-tool GitHub URL comes from `pcc_config.json` via the new `tools_cfg` parameter on `Dashboard.set_tools`. The menu greys out "Open GitHub" rather than triggering a status-bar warning — less noisy when many tools have no URL.

The Pull action holds the `GitOpWorker` on `MainWindow._dashboard_workers` (a list) so the QThread isn't garbage-collected mid-run; cleanup happens via the `finished` signal. Status surfaces via `_dashboard_git_done` → `statusBar().showMessage()`.

The Launch action uses `CREATE_NO_WINDOW` on Windows to suppress the `cmd.exe` console flash — preserves the post-B5 invariant (no subprocess console flicker for non-launch operations was the original B5; this extends the policy to the new launch path too).

---

## 6. Validation results

| Check | Result |
|-------|--------|
| Commons `python -m pytest -q tests/` | **114 passed in 1.31s** (no commons changes in this step; the StatusBadge suite from Step 2 still green) |
| PCC `python -m compileall -q . -x "\.venv\|commons\|build\|dist\|__pycache__"` | clean |
| PCC `python -m pytest -q tests/` | **4 passed in 0.20s** (existing smoke tests: module imports, version format, MainWindow instantiates, theme QSS non-empty). MainWindow instantiation exercises Dashboard → ToolsTable end-to-end |
| PCC `python main.py` source-mode launch | exit 0, **0 bytes stderr at 2s mark**. No QSS-parse warnings, no missing-icon errors, no table-population exceptions |
| Row selection | `SingleSelection` + `SelectRows` — click any cell highlights the row via commons `QTableWidget::item:selected` |
| Detail-panel open | Click → `cellClicked` → `tool_selected` → `_open_detail` — chain preserved |
| Context menu routing | Right-click any row → menu appears with 4 actions; each menu action emits the right signal → MainWindow handler logs to status bar / fires the right subprocess |
| Status updates | Scanner thread → `update_tool` → `set_status()` on existing badge — no widget churn |
| No startup regression | Source-mode launch exits clean (post-B5 / post-B6 invariants preserved) |
| No layout instability | Fixed 40px row height, ResizeToContents on 4 columns + Stretch on NAME — column widths stable as the operator resizes the window |
| No scan-thread regression | `ScanWorker` end-to-end works; per-tool stats appear as scans complete (manual visual verification during launch) |
| `phoenix_commons` import | unchanged — no commons API touched |
| BrandProfile compatibility | `PCC_BRAND` unchanged; the table's QSS uses commons palette tokens (`QTableWidget`, `QHeaderView::section`, `#StatusBadge`) which sentinel-substitute correctly under any active profile |

---

## 7. Visual review notes

Operator-facing changes after this commit:

  - **Tools surface is now a 5-column table inside a panelled container.** Section header reads "TOOLS · N repos · click to open". Columns: NAME (italic for commons repo) / LAST COMMIT / LOC / SIZE / STATUS.
  - **STATUS column shows labelled pills** ("Clean" / "N changes" / "Unknown") in the Step-2 StatusBadge primitive (compact mode, tinted backgrounds).
  - **Right-click any row** → 4-action menu (Open in VS Code / Open GitHub / Pull / Launch). GitHub greyed out when no URL configured.
  - **Activity feed is now in a matching panelled container** — content unchanged (still `ActivityRow` widgets with dot + message + tag + timestamp). Per-tool tag colours will come in Step 4.
  - **Body split shifted** so the table dominates ~65% of the dashboard body. Activity feed sits at ~35%.
  - **TODOs chip retired** from each row (the 📌 N open chip + click-to-TODOs sub-routing). The operator opens TODOs from the detail panel's TODOs tab.

Remaining visible deltas vs. the spec screenshot (intentionally deferred):

  - **Header cell borders.** `QHeaderView::section` in commons QSS adds a 1px right border per cell; the spec screenshot has no header column separators. Out of scope for Step 3 — would require either an additive commons selector for the dashboard's table or a localised override. Flagged for follow-up.
  - **Aggregate-tile leading icons + subtitle copy** ("across ~/PycharmProjects", "+1,840 this week", etc.). Spec Step 5.
  - **Per-tool activity tag colors** (checkout=green, lab-layout=amber, etc.). Spec Step 4.
  - **Search bar + sync pill + status-bar shortcut hint.** Spec Steps 6 + 8.
  - **5→4 tile reduction** (drop "Needs Commit" — status now in the table). Spec Step 5.

---

## 8. Remaining dashboard debt

In rough order of follow-up priority:

| Item | Spec step | Notes |
|------|-----------|-------|
| Per-tool activity tag colors | Step 4 | Small wiring — commons `TOOL_BRAND_COLORS` constant + `ActivityRow` tint per `tool` value |
| Aggregate tile refresh (5→4 + icons + subtitles) | Step 5 | `AggregateTile.__init__` gets `icon_name` + `subtitle` kwargs; one tile retires |
| Top utility band (search shell + sync pill) | Step 6 | Net-new surface above body; search shell only at first (no backend) |
| Search backend | Step 7 | Pure backend; could defer indefinitely |
| Status-bar `Press ⌘K to search` hint | Step 8 | One-line addition; depends on Step 6 |
| Header cell border-right cleanup | (not specced) | Commons QSS would need a `QHeaderView::section[noseparator]` variant or a new objectName for dashboard tables; small additive change |
| TODO chip retirement → TODO column? | (not specced) | Spec dropped the TODOs chip explicitly; could add a TODO column to the table if operators want column-comparable TODO counts. Not in spec |
| Sidebar tool-row status dots → StatusBadge | (not specced) | Small adoption; sidebar isn't the dominant surface, so low priority |

None of these block Step 4.

---

## 9. Recommended Step 4 implementation target

The spec §6 nominates Step 4 as **"Per-tool activity tag colors"** — replace the uniform-accent tag pill in `ActivityRow` with per-tool brand colors sourced from a commons constant.

**Recommendation: proceed to Step 4 as scoped in the spec.**

Three reasons:

  1. **Smallest delta in the spec sequence.** Step 4 is a colour-map lookup + a per-row property setting. ~30 LOC of PCC change + a small additive commons constant.
  2. **Visual upgrade out of proportion to scope.** Adds a glance-recognition signal to the activity feed (which tool produced this activity?) that the operator can absorb without reading the tag text.
  3. **Doesn't expand surface area.** Unlike Step 5 (tile refresh) or Step 6 (search bar), Step 4 doesn't introduce new widgets or new chrome — it tints existing chrome per data.

### Step 4 scope (preview)

  - Add `TOOL_BRAND_COLORS: dict[str, str]` to `phoenix_commons.theme.tokens` (or a new sibling module). Maps tool short-names → tag-pill hex color. Per-app brand-mark colors come from `phoenix-rollout/INVENTORY.md` (Checkout green, PTT blue, LLT orange, PMT magenta) + PCC orange + commons cyan + ValveMaster TBD.
  - In `dashboard.py` `ActivityRow.__init__`, look up the colour from the new map (fallback to current accent for unknown tools) and apply to the tag QLabel.
  - Optional polish: also tint the activity-row bullet dot (`·`) the same per-tool color.

### Optional follow-up before Step 4 — header-border cleanup

If the operator wants the header cell `border-right: 1px solid #2d3748` separators removed (matching the spec screenshot's cleaner header band), that's a tiny additive commons QSS addition — a new `QHeaderView#dashboardTableHeader::section` selector or an attribute selector — taking ~10 minutes. Not required by the spec sequence; flagged here for operator consideration.

---

## 10. Confirmation

  - **No architecture changes occurred.** No new ADR. No public-API rename. No commons module added or removed. `phoenix_commons` is referenced as-is. The new `ToolsTable` is a single class in PCC's `dashboard.py`; the four new `MainWindow` handlers reuse pre-existing primitives.
  - **No production deployment occurred.** Work is source-mode only on PCC `phase-3c-pcc-retrofit` (commit `4e935c9`). No installer built, no `dist/` zip created, no GitHub Release published. Branch not pushed.
  - **No BrandProfile changes occurred.** `PCC_BRAND = BrandProfile(primary="#E8783C", secondary="#2A8880", accent="#3CB8AE")` unchanged. The table chrome consumes commons QSS selectors that already exist (`QTableWidget`, `QHeaderView::section`); StatusBadge variants `syncing`/`scanning` (which use the brand-accent sentinel) are not wired in this step.
  - **No production tool source touched.** PCC-only commit. Phoenix CAD / Phoenix Checkout / PTT / PMT / ValveMaster all untouched.
  - **No commons changes.** The Panel + PhoenixTable + StatusBadge widgets consumed in this step were added in earlier commits (B9 / B10 / Step 2). No commons file modified for B11.
  - **No subprocess regression.** New `_dashboard_launch` uses `CREATE_NO_WINDOW` consistent with B5. New `_dashboard_pull` reuses the existing `GitOpWorker` which uses the B5-hardened `git_pull` helper.
  - **No widget-level setStyleSheet regression.** B11 retires the inline-styled `ToolRow` class (~120 lines of `setStyleSheet` gone) and introduces no new inline styles — the post-B6 invariant is preserved + meaningfully improved.

---

## Commit summary

| Repo | Commit | Subject |
|------|--------|---------|
| `phoenix-command-center` `phase-3c-pcc-retrofit` | `4e935c9` | Tools list → PhoenixTable surface (Phase 3C B11, Implementation Step 3) |

PCC `phase-3c-pcc-retrofit` is now 7 commits ahead of `origin/phase-3c-pcc-retrofit` and not merged to master. No commons commits for this step (B11 consumes the Step-2 commons primitive without further additions).

**Operator gate:** visual review of the post-B11 dashboard before Step 4 starts. Recommended capture targets:

  1. Full dashboard at default 1300×800 — confirm the tools table dominates the body, sits inside its rounded-panel container, with the activity feed in a matching container on the right.
  2. Close-up of the table — confirm the 5 columns render, status pills appear in the right column, italic for the commons repo.
  3. Right-click any tool row — confirm the 4-action context menu appears; "Open GitHub" is greyed out for tools without a configured URL.
  4. Click any cell — confirm the detail panel opens for that tool.
  5. Scan in progress (refresh the dashboard) — confirm rows fill in as scans complete; no widget churn or flickering.

---

*End of report.*
