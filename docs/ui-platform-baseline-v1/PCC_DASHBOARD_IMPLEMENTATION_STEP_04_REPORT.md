# PCC Dashboard Implementation — Step 4 Report

> **Status:** complete.
> **Date:** 2026-05-21.
> **Scope:** Per-tool activity tag colors. New `TOOL_BRAND_COLORS` map
> + `color_for_tool()` helper added to `phoenix_commons.theme.tokens`;
> `ActivityRow` in PCC's dashboard consumes them so each tag pill
> renders in the originating tool's brand color.
> **Operator gate:** visual review of the multi-coloured Recent
> Activity feed before Step 5 (aggregate-tile refresh) starts.

---

## 1. What changed

| Repo / Branch | Commit | Subject |
|---------------|--------|---------|
| sibling `phoenix-commons` `main` | `0864745` | tokens: add TOOL_BRAND_COLORS + color_for_tool() (Step 4) |
| PCC submodule `commons` `main` | `e8fe0f7` | tokens: add TOOL_BRAND_COLORS + color_for_tool (Step 4) |
| `phoenix-command-center` `phase-3c-pcc-retrofit` | (B12, this commit) | Per-tool activity tag colors (Phase 3C B12, Implementation Step 4) |

**Commons surface change:** pure additive. `TOOL_BRAND_COLORS: dict[str, str]` + `color_for_tool(name, default='#94a3b8') -> str` added to `phoenix_commons.theme.tokens`. Both exported from `__all__`. 10 new unit tests in `tests/test_tokens.py`. 124/124 commons tests pass.

**PCC change:** `dashboard.py` — 4 net additions:
1. Import `color_for_tool` from `phoenix_commons.theme.tokens`.
2. New module-level `_rgba_glow(hex_color, alpha=0.18)` helper to convert `#rrggbb` to `rgba(r, g, b, a)` for QSS backgrounds.
3. `ActivityRow.__init__` computes `tag_color = color_for_tool(tool, default=C["text_muted"])` per row.
4. `ActivityRow` tag pill `setStyleSheet` uses `{tag_color}` for foreground + `{_rgba_glow(tag_color, 0.18)}` for background (was uniform `C["accent"]` / `C["accent_glow"]`).

---

## 2. API spec

### `TOOL_BRAND_COLORS: dict[str, str]`

Closed set. 9 entries. Keyed by canonical short identifier (after normalisation by `color_for_tool`). Values are 6-digit lowercase hex.

| Key | Color | Tool |
|-----|-------|------|
| `commons` | `#3cb8ae` teal | platform / commons identity |
| `checkout` | `#4ec47a` green | Phoenix Checkout Tool brand-mark |
| `project-tracker` | `#3b82f6` blue | Project Tracking Tool brand-mark |
| `job-tracker` | `#3b82f6` blue | Display-name alias for PTT |
| `lab-layout` | `#f59e0b` amber | Lab Layout Tool brand-mark |
| `cad` | `#f59e0b` amber | Phoenix CAD Tool (LLT precursor) |
| `master` | `#c0398c` magenta | Phoenix Master Tool brand-mark |
| `command-center` | `#e8783c` orange | PCC brand primary |
| `valvemaster` | `#7c5bcc` purple | INVENTORY.md TBD slot; allocated by Step 4 |

Adding a tenth entry requires a commons PR. Not a brand-profile mechanism; this is a UI lookup table.

### `color_for_tool(name, default='#94a3b8') -> str`

6-step normalisation pipeline:

1. Lowercase + replace spaces / underscores with dashes.
2. Strip a leading `phoenix-` prefix (shared family namespace).
3. Strip a trailing `-tool` suffix (so `checkout-tool` matches `checkout`).
4. Exact-match lookup against `TOOL_BRAND_COLORS`.
5. Substring fallback — iterate keys **longest first** so `valvemaster` (11 chars) matches inside `valvemastertool` before `master` (6 chars) would.
6. Return `default` (muted slate) when nothing matches.

Examples:

| Input | Returns |
|-------|---------|
| `"phoenix-commons"` | `#3cb8ae` |
| `"Phoenix Checkout Tool"` | `#4ec47a` |
| `"Phoenix Cad Tool"` | `#f59e0b` |
| `"Job Tracker"` | `#3b82f6` |
| `"Phoenix Command Center"` | `#e8783c` |
| `"ValveMasterTool"` | `#7c5bcc` (substring fallback) |
| `"never-heard-of-this"` | `#94a3b8` (default) |
| `"never-heard"` (with `default="#000000"`) | `#000000` |

---

## 3. Color map rationale

Tool colors lifted from `phoenix-rollout/INVENTORY.md` § Per-app brand mark:

```
PCC      → Pixel-art ATS city, Navy/blue
Checkout → Droplet+gear sticker, Green
PTT      → Droplet+gear sticker, Blue
LLT      → Droplet+gear sticker, Orange
Master   → Droplet+gear sticker, Magenta
```

Two adjustments to the literal INVENTORY values:

  - **PCC color** uses `#e8783c` (the `PCC_BRAND.primary` orange from ADR-016) rather than navy/blue. INVENTORY described the brand-mark *artwork* as navy/blue; the activity-tag color should match PCC's chrome accent, not its sprite illustration. Using the brand primary makes PCC's own events read consistently with the rest of PCC's UI.
  - **LLT amber** is `#f59e0b` (a deeper amber) rather than PCC's `#e8783c` orange — so the two warm-orange-family tools are visibly distinguishable in the same activity feed. Without this differentiation, "lab-layout" and "command-center" tags would read identically.

`commons` is teal — matches PCC's `BRAND.accent` so the platform layer reads as one visual entity across PCC's chrome and the activity feed's commons-origin events.

`valvemaster` is purple — `INVENTORY.md` left this TBD (no brand-mark color on file). Allocated here per the Step 4 brief; a future ValveMaster branding decision can update this slot via a commons PR. Operator can override at any time.

`Screenshot Tool` and any other operator-side scratch tools that appear in the scan get the default `#94a3b8` muted slate — visually deferred so they don't compete with the production-tool palette.

---

## 4. PCC consumer

### `ActivityRow.__init__` per-row color resolution

```python
tag_text = _short_tool_tag(tool)
tag_color = color_for_tool(tool, default=C["text_muted"])
tool_lbl = QLabel(tag_text)
tool_lbl.setStyleSheet(f"""
    color: {tag_color};
    background: {_rgba_glow(tag_color, alpha=0.18)};
    border-radius: 4px;
    padding: 1px 6px;
    font-size: 10px;
    font-weight: 600;
""")
```

### `_rgba_glow(hex_color, alpha=0.18)`

Module-level helper. Reads `#rrggbb`, splits into r/g/b integers, returns `rgba(r, g, b, a)` string. Qt QSS doesn't accept hex with alpha so we have to convert.

Defensive: invalid input (not 6-digit hex) falls back to the neutral slate glow rather than raising — the layout doesn't break under unexpected color strings.

### Tag-color outcomes in the live activity feed

(snapshot from operator's current scan corpus):

| Tool | Tag color rendered |
|------|---------------------|
| Phoenix Commons | teal `#3cb8ae` |
| Phoenix Checkout Tool | green `#4ec47a` |
| Phoenix Cad Tool | amber `#f59e0b` |
| Job Tracker | blue `#3b82f6` |
| Phoenix Command Center | orange `#e8783c` (PCC primary) |
| ValveMasterTool | purple `#7c5bcc` |
| Screenshot Tool | muted slate `#94a3b8` (default) |

---

## 5. Validation results

| Check | Result |
|-------|--------|
| Commons `python -m pytest -q tests/` | **124 passed in 0.25s** (+10 new for `test_tokens.py` Step-4 cases; was 114 pre-Step-4) |
| Commons substring-fallback ordering | verified via `test_color_for_tool_substring_fallback` — `valvemaster` (11 chars) wins over `master` (6 chars) for `valvemastertool` |
| Commons Qt-free invariant | preserved — `test_tokens_module_is_qt_free` still green |
| PCC `python -m compileall -q .` | clean |
| PCC `python -m pytest -q tests/` | **4 passed in 0.20s** |
| PCC source-mode launch | exit 0, 0 stderr expected (operator visual review pending) |
| post-B5 subprocess invariant | preserved (no subprocess changes) |
| post-B6 setStyleSheet invariant | preserved (ActivityRow's `setStyleSheet` was already inline-styled by design — this commit changes the **values** flowing into the styled QSS string but doesn't add a new inline call site, and doesn't shift any commons-cascade-styled widget into inline territory) |
| BrandProfile invariant | preserved — `TOOL_BRAND_COLORS` is a UI lookup table, not a brand-profile mechanism. Per-app theming still flows through `BrandProfile` per ADR-016 |

---

## 6. Remaining dashboard debt

Per the spec §6 sequence:

| # | Step | Status |
|---|------|--------|
| 1 | Lucide icons + sidebar modernization | done (B9) |
| 2 | StatusBadge primitive + dashboard pilot | done (Step 2 / B10) |
| 3 | Tools list → PhoenixTable | done (B11) + polish (B11.1-B11.4) |
| 4 | **Per-tool activity tag colors** | **done (this commit, B12)** |
| 5 | Aggregate tile refresh (5→4 + icons + subtitles) | pending |
| 6 | Top utility band (search shell + sync pill) | pending |
| 7 | Search backend | pending |
| 8 | Status-bar `Press ⌘K to search` hint | pending |

---

## 7. Recommended Step 5 implementation target

The spec §6 nominates Step 5 as **"Aggregate tile refresh"** — reduce the 5 tiles to 4, add leading Lucide icons + subtitle copy.

**Recommendation: proceed to Step 5 as scoped in the spec.**

Three reasons:

  1. **Status now lives in the table column.** The current "Needs Commit" tile is redundant — every operator can scan the STATUS column for "N changes" rows. Step 5 retires it without losing information.
  2. **Icons + subtitles per tile** turns the top metrics band from "numbers without context" into "numbers with framing" (the screenshot's "across ~/PycharmProjects", "+1,840 this week", "2 marked FIXME", "Largest: ValveMasterTool"). Significant visual upgrade for minimal scope.
  3. **No new commons primitive required.** `AggregateTile` already lives in `dashboard.py`; gets new optional kwargs (`icon_name`, `subtitle`). Step 5 is pure PCC source — no commons additions, no submodule bump.

### Step 5 scope (preview)

  - `AggregateTile.__init__` gets two new kwargs: `icon_name: str | None = None`, `subtitle: str = ""`.
  - When `icon_name` is provided, render a 16px Lucide icon at the top-left of the tile (next to the label).
  - When `subtitle` is provided, render a small muted line beneath the value.
  - `Dashboard._build()` reduces from 5 tiles to 4: drop `Needs Commit`. The 4 remaining tiles each get an icon + subtitle.
  - Subtitle copy is data-driven where possible: "Largest: {tool_name}" for the size tile, "+N this week" for LOC if a delta is available (otherwise omit), "{n} marked FIXME" for TODOs if FIXME-priority TODOs exist (otherwise omit). Static-text fallback for tiles with no data hook yet.

### Optional sub-step before Step 5

`scanner.get_todos` doesn't currently flag FIXME-priority items separately. If we want the "2 marked FIXME" subtitle copy to be data-driven, scanner needs a small extension (one boolean per TODO indicating FIXME priority). Otherwise the subtitle stays static (e.g., "across N tools").

---

## 8. Confirmation

  - **No architecture changes occurred.** No new ADR. No public-API rename. No commons module added or removed. `TOOL_BRAND_COLORS` + `color_for_tool` are additive entries in an existing module (`phoenix_commons.theme.tokens`).
  - **No production deployment occurred.** Work is source-mode only. PCC branch is `phase-3c-pcc-retrofit`; commons branch is `main` (not pushed). No installer built, no `dist/` zip created, no GitHub Release published.
  - **No BrandProfile changes occurred.** `PCC_BRAND` unchanged. `BrandProfile` API unchanged. `DEFAULT_BRAND` unchanged. `TOOL_BRAND_COLORS` is parallel infrastructure — a per-tool UI lookup, not a brand-token override.
  - **No production tool source touched.** PCC-only PCC-side change. Phoenix CAD / Phoenix Checkout / PTT / PMT / ValveMaster all unmodified.
  - **No subprocess regression.** No new subprocess calls. Post-B5 invariant preserved.
  - **No widget-level setStyleSheet regression.** Post-B6 invariant preserved — the `ActivityRow.setStyleSheet` call site predates B6 (it was always inline-styled by design); this commit changes the values in the style string but doesn't introduce a new inline-styled widget.
  - **No commons API break.** All commons additions are pure-additive — pre-existing imports of `phoenix_commons.theme.tokens` continue to work unchanged.

---

## Commit summary

| Repo | Commit | Subject |
|------|--------|---------|
| sibling `phoenix-commons` `main` | `0864745` | tokens: add TOOL_BRAND_COLORS + color_for_tool() (Step 4) |
| PCC submodule `commons` `main` | `e8fe0f7` | tokens: add TOOL_BRAND_COLORS + color_for_tool (Step 4) |
| `phoenix-command-center` `phase-3c-pcc-retrofit` | (B12) | Per-tool activity tag colors (Phase 3C B12, Implementation Step 4) |

**Operator gate:** visual review of the new per-tool tag colors in the Recent Activity feed before Step 5 starts. Recommended capture targets:

  1. Activity feed with at least 3-4 different tools' events visible — confirm pill colors are distinct (green / amber / blue / purple / etc.).
  2. PCC's own recent activity entries — confirm orange tag (matches the sidebar's primary CTA).
  3. Commons-side entries (PCC dashboard work) — confirm teal tag.
  4. Tooltip on any tag pill — confirm the full tool name appears.

---

*End of report.*
