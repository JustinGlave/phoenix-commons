# PCC Dashboard Implementation — Step 1 Report

> **Status:** complete (commit `f9c948a` on PCC `phase-3c-pcc-retrofit`).
> **Date:** 2026-05-21.
> **Scope:** Lucide icon migration + sidebar modernization per
> `PCC_DASHBOARD_SURFACE_SPEC_V1.md` §6 step 1.
> **Operator gate:** visual review of the post-Step-1 sidebar before
> Step 2 (StatusBadge in commons + tools list→table) starts.

---

## 1. Glyph inventory

Pre-migration inventory of every emoji/glyph in PCC's running code, categorised by surface:

| Surface | Glyph | File:line | Visibility | In scope? |
|---------|-------|-----------|------------|-----------|
| Sidebar logo | 🔥 | `main_window.py:87` | Always (top of sidebar) | YES |
| Sidebar nav: Dashboard | ◎ | `main_window.py:101` | Always | YES |
| Sidebar nav: Commons | ◆ | `main_window.py:102` | Always | YES |
| Sidebar action: New Tool | ✦ | `main_window.py:115` | Always | YES |
| Sidebar action: Refresh All | ↻ | `main_window.py:122` | Always | YES |
| Sidebar action: Settings | ⚙ | `main_window.py:128` | Always | YES |
| Sidebar tool-row badges | ◆ / ◈ | `sidebar_tool_widget.py:44` | Per tool (5-7×) | YES |
| Status-bar scan dot | ● | `main_window.py:225, 307` | When scanning | NO — semantic |
| Status-bar separator | · | `main_window.py:392` | Always | NO — semantic |
| Menu bar actions: 5× | ✦ ↻ ⚙ ◎ ◆ | `main_window.py:400–413` | When File/Tools menu open | YES |
| Dashboard ToolRow badge | ◆ / ◈ | `dashboard.py:85` | Per tool (5-7×) | YES |
| Dashboard ToolRow TODO chip | 📌 | `dashboard.py:114, 161` | Per tool | DEFERRED (chip widget) |
| Dashboard ToolRow status dot | ● | `dashboard.py:137` | Per tool | NO — semantic |
| Dashboard ToolRow arrow | › | `dashboard.py:143` | Per tool | NO — semantic |
| Dashboard activity dot | · | `dashboard.py:192` | Per activity row | NO — semantic |
| Sidebar tool stats: LOC | 📄 | `sidebar_tool_widget.py:65, 78` | Per tool | DEFERRED |
| Sidebar tool stats: Size | 💾 | `sidebar_tool_widget.py:67, 79` | Per tool | DEFERRED |
| About dialog hero | 🔥 | `about_dialog.py:40` | When About open | YES |
| Commons browser Rescan | ↻ | `commons_browser.py:127` | Always on Commons page | YES |
| Commons browser usage chip | ◈ | `commons_browser.py:85` | Per file usage | DEFERRED (chip widget) |
| Detail panel Pull/Push/Fetch | ⬇ ⬆ ↻ | `detail_panel.py:493` | Per tool detail | OUT OF SCOPE |
| Detail panel status badge | ● / ○ | `detail_panel.py:555` | Per tool detail | OUT OF SCOPE — Step 2 (StatusBadge) |
| Tool card stats (orphan) | ⏱ 📄 💾 📌 ◆ ◈ ● | `tool_card.py` (multiple) | NEVER (orphan since initial commit) | N/A |
| Settings dialog title | ⚙ | `settings_dialog.py:82` | When Settings open | DEFERRED (low priority) |
| New tool wizard title | ✦ | `new_tool_wizard.py:197, 556` | When wizard open | DEFERRED (low priority) |

**Totals:** 14 distinct glyphs across ~30 source locations. 11 locations migrated in this step; 7 deferred to follow-up; 4 left as semantic indicators (●/·/›); 6 out of scope per Step 1 brief (detail panel + orphan).

---

## 2. Lucide mapping table

The commons icon set grew from 10 → 13 Lucide SVGs. Three added, all Lucide-standard, no API change:

| Glyph in PCC | Lucide icon | Status in commons | Notes |
|--------------|-------------|-------------------|-------|
| 🔥 (logo) | n/a — **asset, not icon** | n/a | `assets/logo.png` already shipping with PCC. Uses the existing ATS pixel-art mark. |
| ◎ (Dashboard) | `layout-dashboard` | **NEW (commons b75f2bd)** | Lucide-standard four-square grid. |
| ◆ (Commons / commons-tool) | `package` | **NEW (commons b75f2bd)** | Lucide-standard 3D box. |
| ◈ (regular tool) | `git-branch` | **NEW (commons b75f2bd)** | Lucide-standard branching glyph. |
| ✦ (New Tool) | `plus` | existing | Already in commons. |
| ↻ (Refresh / Rescan / Fetch) | `refresh` | existing | Already in commons. |
| ⚙ (Settings) | `settings` | existing | Already in commons. |
| 📄 (LOC chip) | `file-text` | **NOT YET** | Deferred. Adding a 4th Lucide icon was beyond the "1-2 missing" budget. |
| 💾 (Size chip) | `hard-drive` | **NOT YET** | Deferred. |
| 📌 (TODO chip) | `pin` | **NOT YET** | Deferred. |
| ⏱ (commit time) | `clock` | **NOT YET** | N/A — only used in orphan `tool_card.py`. |
| ⬇ ⬆ (push/pull) | `arrow-down` / `arrow-up` | **NOT YET** | Out of scope (detail panel). |

Commons icon registry (post-step):
```
check, git-branch, info, layout-dashboard, package, plus,
refresh, save, search, settings, trash, warning, x
```
13 total. Closed-set semantics preserved. Pyproject package-data already covers `*.svg` under `phoenix_commons/icons/lucide/`, so the new SVGs ship with both editable installs and frozen builds without further packaging work.

---

## 3. Surfaces modernized

### 3a. Sidebar (primary scope)

  - **Logo:** flame emoji (🔥) → ATS pixel-art brand mark scaled to 24×24px from `assets/logo.png`. Sidebar header now reads as Phoenix Controls / ATS identity instead of a generic flame glyph.
  - **Nav: Dashboard** (◎ → `layout-dashboard`, tinted `text_sub`). Item label changed from `"  ◎  Dashboard"` to `"   Dashboard"`; the icon takes the leading position via `QListWidgetItem.setIcon()`.
  - **Nav: Commons** (◆ → `package`, tinted `teal` to match the per-tool commons badge color).
  - **Nav iconSize** explicitly set to `QSize(16, 16)` on the QListWidget so both nav icons render consistently regardless of Qt's per-style default.
  - **Per-tool sidebar badges** (◆ / ◈ → `package` / `git-branch`, tinted `teal` / `accent` — same color treatment the emoji used). Applied in `sidebar_tool_widget.py`.
  - **Action: New Tool** (✦ → `plus`, white `#ffffff` icon on the red `accentBtn`).
  - **Action: Refresh All** (↻ → `refresh`, `text_sub` tint on `ghostBtn`).
  - **Action: Settings** (⚙ → `settings`, `text_sub` tint on `ghostBtn`).

### 3b. Menu bar actions

Five `QAction`s get matching icons via `QAction.setIcon()`. Labels lose their emoji prefix:
  - File → New Tool (plus), Refresh All (refresh), Settings (settings)
  - Tools → Dashboard (layout-dashboard), Commons Browser (package)

Menu items now show platform-standard icon + text rather than emoji-in-text. Behaviour unchanged.

### 3c. Dashboard ToolRow (inline class in dashboard.py)

Same badge migration as the sidebar tool widget — ◆/◈ → `package`/`git-branch` with the same teal/accent tinting. Keeps the dashboard row visually consistent with the sidebar tool list.

### 3d. About dialog

Hero flame (🔥 at 38px) → ATS brand mark (48×48px from `assets/logo.png`). Consistent with the sidebar logo change.

### 3e. Commons browser

Rescan button (↻ → `refresh`).

---

## 4. Validation results

| Check | Result |
|-------|--------|
| `python -c "from phoenix_commons.icons import icon; icon('package')"` etc. | OK (all 3 new icons load, isNull=False) |
| commons `pytest -q tests/` | **93 passed in 0.39s** — `test_icons.py` + `test_packaging.py` iterate `ICON_NAMES` dynamically and pick up the new entries without modification. |
| PCC `python -m compileall -q .` | clean |
| PCC `python -m pytest -q tests/` | **4 passed in 0.26s** |
| PCC `python main.py` source-mode launch | **exit 0, 0 bytes stderr.** No icon-not-found errors, no QPixmap warnings, no startup flashing regression (B5 invariant preserved), no render hang (B6 invariant preserved). |
| Sidebar alignment | Visual review pending (operator gate, §6). |
| Aggregate tile rendering | Unchanged (tiles not touched in this step). |
| Dark-theme compatibility | All icons tinted via `icon(name, color=...)` against PCC's palette tokens; no hard-coded white/black. |
| BrandProfile compatibility | No change to PCC_BRAND or commons brand sentinels. Icon colors source from `theme.C[...]` (PCC chrome tokens) — unaffected by future BrandProfile changes. |

---

## 5. Remaining emoji debt

In rough order of follow-up priority:

| Glyph | Surface | What's needed |
|-------|---------|---------------|
| 📄 / 💾 / 📌 | Sidebar tool stats chips (LOC / Size / TODOs) | Add `file-text`, `hard-drive`, `pin` Lucide SVGs to commons; restructure each chip from single QLabel to icon+text composition. ~30-40 LOC in `sidebar_tool_widget.py`. |
| 📄 / 💾 / 📌 / box | Aggregate dashboard tiles (Total LOC / Total Size / Open TODOs / Tools) | Same SVGs as above + 1 more (`package` already added). `AggregateTile.__init__` gets an optional `icon_name` parameter. ~20 LOC in `dashboard.py`. |
| ◈ | Commons browser usage chips | Restructure `_Chip` helper class from single QLabel to icon+text composition. ~15 LOC in `commons_browser.py`. |
| ⬇ / ⬆ | Detail panel Pull / Push buttons | Out of scope for dashboard; defer to a separate detail-panel polish step. Would need `arrow-down` + `arrow-up` Lucide SVGs. |
| ⏱ / 📄 / 💾 / 📌 / ◆ / ◈ / ● | `tool_card.py` orphan | N/A — file never imported by running code. Defer indefinitely. |
| ✦ / ⚙ | Settings dialog + New Tool wizard titles | Cosmetic only; setIcon on those header QLabels is fine but low priority. |
| ● / · / › | Status dots, activity dots, row arrows | Intentional semantic indicators. Stay as Unicode glyphs unless replaced by `StatusBadge` widget in Step 2. |

Adding the 3-4 stats/chip icons (`file-text`, `hard-drive`, `pin`) would be a natural Step 1.5 — small, mechanical, finishes the sidebar end-to-end. Folded into Step 2 below if the operator approves it as a precursor.

---

## 6. Screenshots generated

**None — this report does not include captured screenshots.** PCC was launched in source mode for visual confirmation (exit code 0, no stderr), but on-screen capture is an operator-side task. Recommended capture targets for the operator's visual review:

  1. Sidebar full height — confirms logo + nav items + per-tool rows + action buttons all render with Lucide icons (and no remaining ◎ outside the deferred set).
  2. Sidebar tool list at scroll — confirms `package` badge on the commons entry and `git-branch` badges on the rest, with correct teal / accent tinting.
  3. About dialog — confirms the ATS brand mark is anchored where 🔥 used to be.
  4. File menu open + Tools menu open — confirms menu QActions show Lucide icons next to their labels.
  5. Side-by-side with the pre-B9 state (if available) — confirms calmer, more professional sidebar.

If you want me to capture frames programmatically, I can install a small offscreen-Qt screenshot helper, but the spec said operator-side visual review, so I have not done so.

---

## 7. Remaining dashboard work (per PCC_DASHBOARD_SURFACE_SPEC_V1 §6)

The spec's 8-step sequence stands:

| # | Step | Status |
|---|------|--------|
| 1 | **Lucide icons replace emoji glyphs** in sidebar nav + sidebar tool rows + dashboard tile labels | **DONE in this commit** (sidebar nav + sidebar tool rows + menu actions + about + commons rescan). Aggregate-tile leading icons + stats chips deferred to Step 1.5. |
| 2 | `StatusBadge` widget added to commons | Pending |
| 3 | Tools section: list → table | Pending |
| 4 | Per-tool activity tag colors | Pending |
| 5 | Aggregate tile refresh (5→4, leading icons, subtitle copy) | Pending |
| 6 | Top utility band: page title + search bar + sync pill | Pending |
| 7 | Search backend | Pending |
| 8 | Status-bar shortcut hint | Pending |

---

## 8. Recommended Step 2 implementation target

The spec §6 nominates Step 2 as **`StatusBadge` widget added to commons** — small additive primitive that unblocks Step 3 (tools list → table) and the future status-pill refresh.

**Recommendation:** keep Step 2 as scoped in the spec — `StatusBadge` widget in commons only, no PCC source change. Two reasons:

  1. It's a 30-50 LOC additive component in `phoenix_commons/widgets/`. Low risk, easy to commons-test, no PCC dependency.
  2. Step 3 (tools-table) needs it. Building Step 2 in commons before Step 3 lands keeps the per-PR scope small and the API contract visible to the operator before any PCC code consumes it.

**Optional precursor — Step 1.5 (Lucide stats icons):** before Step 2, if the operator wants the sidebar fully emoji-free in a small follow-up commit, add `file-text` + `hard-drive` + `pin` to commons (3 more Lucide-standard SVGs, mechanical) and finish the sidebar tool-row chips + the aggregate tile leading icons. ~50 LOC across PCC, no widget restructure beyond what was already done in Step 1. Operator's call.

---

## 9. Confirmation

  - **No architecture changes occurred.** Sidebar structure unchanged. Layout philosophy unchanged. No new widget classes. No commons API change. The 3 added Lucide SVGs + ICON_NAMES additions are pure-additive commons content; the icon loader function signature is unchanged.
  - **No production deployment occurred.** Work is source-mode only on PCC `phase-3c-pcc-retrofit` (commit `f9c948a`) and commons `main` (commit `bc25621` sibling / `b75f2bd` submodule). No installer built, no dist zip created, no GitHub Release published. Neither commons commit pushed yet.
  - **No BrandProfile changes occurred.** `PCC_BRAND = BrandProfile(primary="#E8783C", secondary="#2A8880", accent="#3CB8AE")` unchanged. The icon colors source from `theme.C[...]` PCC chrome tokens (`teal`, `accent`, `text_sub`), not from the brand slots — so a future BrandProfile change does not affect this commit's color choices unless it also alters the chrome palette.
  - **No production-tool source touched.** PCC-only commit. Lab Layout, Phoenix Checkout, PTT, PMT, ValveMaster all untouched.
  - **No subprocess regression** (post-B5 invariant preserved — no new subprocess calls added).
  - **No widget-level setStyleSheet override added** (post-B6 invariant preserved — `apply_pcc_theme(app)` cascade remains the only cascade root).
  - **No layout instability** — all icon widgets use either fixed-width QLabels (badges, logo) or built-in `QPushButton.setIcon` / `QAction.setIcon` / `QListWidgetItem.setIcon` (mature Qt APIs).

---

## Commit summary

| Repo | Commit | Subject |
|------|--------|---------|
| `phoenix-commons` (sibling checkout) | `bc25621` | icons: add package + git-branch Lucide SVGs |
| `phoenix-commons` (PCC submodule) | `b75f2bd` | icons: add package + git-branch Lucide SVGs |
| `phoenix-command-center` | `f9c948a` | Lucide icons + sidebar modernization (Phase 3C B9, Implementation Step 1) |

PCC `phase-3c-pcc-retrofit` is now 5 commits ahead of `origin/phase-3c-pcc-retrofit` and not merged to master. Commons `main` is 5 commits ahead of `origin/main` and not pushed.

**Operator gate:** visual review of the post-Step-1 PCC sidebar before Step 2 starts.

---

*End of report.*
