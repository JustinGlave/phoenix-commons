# PCC Dashboard Surface Spec — v1

> **Status:** product direction. Pre-implementation.
> **Date:** 2026-05-21.
> **Scope:** the PCC dashboard surface — its purpose, hierarchy, layout,
> visual feel, and the surfaces it composes. No code. No retrofit
> doctrine. No architectural change to commons or ADR-016.
> **Inputs:** current PCC (post-B7 on `phase-3c-pcc-retrofit`), operator's
> directional screenshot, ADR-016 + BrandProfile, current commons API
> (`phoenix_commons.theme/widgets/icons/paths/updater`),
> PHOENIX_ROLLOUT_SUPERSEDED_NOTICE conclusions.
> **Output:** this file. Operator approves the spec; implementation
> sequencing follows separately, one surface at a time.

---

## 1. Product intent

PCC is the **operator's command surface for the Phoenix tool family.** Not a customer product. Not a developer IDE. Not a generic launcher. It is the single pane through which one person manages four shipping production tools + commons + their own scaffolding workflow.

The dashboard answers four questions, in this priority:

1. **"What needs my attention right now?"** — dirty repos, failed scans, stale branches, growing TODO debt.
2. **"What's the state of my fleet?"** — at-a-glance health across all tools.
3. **"What changed recently?"** — last commits, last scans, last builds.
4. **"How do I jump into work?"** — open in editor, open in browser, pull, launch.

Everything else is structural chrome that should disappear.

### What dominates visually

The **tools surface.** It's the answer to questions 1 and 2 above and the operator's main glance-and-decide target. Everything else exists to support it.

### What feels secondary

Aggregate metrics (totals across the fleet), recent activity (background context). These are confirmatory — they answer "is the picture I'm forming correct?" rather than driving the next action.

### What feels alive

Live data updating: scan-in-progress indicator, status-dot color changes on completion, sync-pill timestamp ticking. These are *targeted* aliveness — a few small surfaces that change in response to background work. Everything else is static and calm.

### What feels calm

Sidebar chrome, status bar, section headers. These define the workspace; they don't compete for attention. Surface treatment over flashy treatment.

---

## 2. Dashboard philosophy

### Table over cards for repeated entities

Tools are a uniform set — every tool has the same attributes (name, last commit, LOC, size, status, TODO count). A table aligns those attributes columnwise, which makes comparison the dominant interaction: "which tool has the most TODOs?", "which is dirty?", "which hasn't been touched in a week?". Cards force the operator's eye to traverse the same per-tool layout repeatedly and obscure cross-tool comparison.

Cards remain right for **non-repeated** entities (the four aggregate tiles at the top — each is a distinct stat with its own context, not a row in a series).

### Density: developer-comfortable, not Linear-dense

PCC's operator works with the dashboard for sustained sessions, not 90-second triage. The right density target is **GitHub Desktop / Raycast / Sourcegraph**, not Linear (too tight) and not Notion (too airy). Row heights ~36-44px in the tools table. Sidebar items ~32-36px. Aggregate tiles roomy enough to read at a glance from 4-6 feet.

### Whitespace is structural

Whitespace separates **sections**, not items. Within a section the rhythm is tight; between sections it breathes. Operators should perceive 4 distinct zones on the dashboard (top tiles row, tools panel, activity panel, status bar) without needing dividers — the whitespace alone does that work.

### Chrome should disappear

Sidebar, status bar, section headers, scrollbars: all defined by neutrals. Their treatment is restrained so the operator's eye lands on data, not widgetry. A successful dashboard makes the operator unaware that they are using Qt.

### Motion: restrained

Allowed: hover transitions (~150ms), scan-in-progress text indicator, status-dot color change on completion, focus rings on inputs. Not allowed: animated tile counters, sliding panels, fade-ins on data load, persistent loading spinners, "shimmer" placeholders. The sprite in the sidebar is **identity**, not "live feedback."

---

## 3. Surface-by-surface definitions

Six surfaces compose the dashboard. Each gets one paragraph of intent.

### 3.1 Sidebar (left, fixed ~280-320px)

Operator's persistent identity + navigation surface. Top: small ATS brand mark + "Phoenix / Command Center" wordmark. Middle: section headers (NAVIGATION, TOOLS) with nav items + per-tool rows. Each tool row carries a brand icon (per-tool Lucide glyph), the tool name, and a status dot. Below the nav list: a single brand artifact (the ATS sprite, scaled smaller than today — see §4 motion). Bottom: three action buttons (✦ New Tool, ↻ Refresh, ⚙ Settings) where New Tool is the only primary-treated button.

The sidebar's job is to be **always there, never demanding.** It doesn't scroll independently except for the tool list. It doesn't surface alerts. It doesn't animate beyond the sprite. Width is fixed; the operator never resizes it.

### 3.2 Top utility/search area (above body, ~56-72px tall)

A single horizontal band spanning the dashboard's content area. Left: the current page title ("Dashboard" / "Commons" / detail breadcrumb). Center: a persistent **search input** with a ⌘K shortcut affordance. Right: a **sync-state pill** ("All synced · 14:22" / "Scanning…" / "Last sync failed · retry"). 

This is the surface that says "this is a 2026 developer tool." Search is the operator's primary command — type to find tools, commits, TODOs across the fleet without navigating. Sync pill is the surface that tells the operator the fleet's data is current (vs the spinner-in-status-bar pattern, which is hard to find).

### 3.3 Aggregate metrics row (top of body, 4 tiles)

Four glance metrics across the fleet. Each tile: leading Lucide icon, label (uppercase, muted), large value, subtitle providing context.

| Tile | What | Subtitle example |
|------|------|------------------|
| Tools | total count | "across ~/PycharmProjects" |
| Total LOC | sum of all tools' LOC | "+1,840 this week" (trend) |
| Open TODOs | sum across tools | "2 marked FIXME" (severity) |
| Total Size | disk footprint | "Largest: ValveMasterTool" (focus) |

Calm. No animation. Don't compete with the tools surface. The subtitle is what makes each tile *interesting* — without it they're just numbers.

(The current "Needs Commit" tile retires — that information lives in the tools table's STATUS column where comparison is easier.)

### 3.4 Tools section (body left, dominant)

The dashboard's primary surface. A table with columns: **NAME / LAST COMMIT / LOC / SIZE / STATUS**. Each row is a tool. Status is a colored text pill ("Clean" / "3 changes" / "12 changes" / "Unknown"), not a bare dot. Row click → detail panel. Per-row context menu → VS Code / GitHub / Pull / Launch (the four actions B8 attempted to surface on cards now live as a context menu off each row — same actions, less visual weight).

Above the table: section title "TOOLS" + a small count + click-hint ("5 repos · click to open"). Below the table: nothing — the table fills the remaining vertical space.

This surface is where the operator spends their attention. Everything else should make this surface easier to read.

### 3.5 Activity section (body right, ~30-35% width)

A chronological feed of recent commits across the fleet. Each entry: a short bullet, the commit message (truncated to ~50 chars), a per-tool colored tag pill, and a relative timestamp ("2h ago" / "yesterday" / "3d ago"). The tag colors come from each tool's brand identity (per ADR-016: PCC orange-tinted, Lab Layout orange-amber, Checkout green, PTT blue, Master magenta, ValveMaster... TBD — see §8 design tokens).

Section header: "RECENT ACTIVITY" + a small count ("Last 12"). Scrollable; never paginated.

Secondary surface. Background context, not driver of action. Should never visually compete with the tools table.

### 3.6 Status bar (bottom, ~24px)

Three slots:

- Left: **discovered state** ("✓ 5 tools discovered" with a small icon).
- Center: **last scan timestamp** ("Last scan 14:22:08").
- Right: **shortcut hint** ("Press ⌘K to search").

Calm. Single-line. Never blinks. Never alerts. The status bar exists to confirm the dashboard is functioning — it's not a notification surface.

---

## 4. Visual direction

### Flagship feel

Confident, restrained, modern. "If you described PCC in one word, it would be **considered**." Every surface intentional. No filler chrome. No unstyled-Qt corners showing through.

### Modernity target

2026 dev tools: **GitHub Desktop, Linear (density tone), Raycast (utility tone), Sourcegraph (table tone).** Not 2018 Electron apps. Not 2010 Qt-default. Specifically NOT consumer (Notion, Slack), NOT enterprise BI (Tableau, PowerBI), NOT IDE (VS Code, JetBrains).

### Enterprise vs developer-tool

Developer-tool leaning. PCC is operator-only — no marketing surface, no onboarding flow, no friendly empty states explaining what PCC is. The empty states are operational ("No tools discovered — set the root folder in Settings"), not promotional.

### Typography

Segoe UI throughout. Page titles bold and prominent (22-24px, 800 weight, slight negative letter-spacing). Section headers small + uppercase + muted (10-11px, 700 weight, 1.5px letter-spacing). Data values readable at sustained-attention range (12-14px). Subtitles muted (11px). The current B7 typography polish is on the right path — extend that thinking everywhere.

### Motion / restraint

Allowed: hover transitions (~150ms ease-out on background-color, color, border-color), focus rings on inputs (instant), status-dot color change on scan completion (instant — no fade), scan-in-progress indicator (small "Scanning…" text, no spinner). The sidebar sprite remains animated — that's the *one* "alive" element, intentionally — but at a smaller display size than today (sprite as identity flourish, not focal point).

Forbidden: tile counter animations on first paint, sliding section transitions, fade-ins on data load, loading-spinner overlays, "shimmer" skeleton placeholders, modal animations beyond a 100ms opacity fade.

### Chrome philosophy

Chrome (sidebar, status bar, section headers, scrollbars, dividers) is rendered in neutrals that recede. The accent colors (orange/teal per PCC's BrandProfile, see §8) are reserved for **interactive affordances**: primary CTAs, focus rings, status pills, the active nav item, the per-tool activity tag. If a surface uses an accent color, it should be doing something semantic.

---

## 5. Information hierarchy

### Primary

The **tools table** + the **sync-state pill**. These are the two surfaces the operator's eye should hit first on every load. The tools table answers "what needs attention?"; the sync pill answers "is my data current?".

### Secondary

The **aggregate tiles** + the **search bar**. Confirmatory information (tiles) + on-demand command surface (search). Operators glance at tiles to confirm the picture, type into search to navigate when the primary surface doesn't surface what they need.

### Tertiary

The **activity feed** + the **sidebar nav list**. Context (what's been happening) + persistent structure (where am I, what else exists). Both are always present but neither demands attention.

### Quaternary

The **status bar** + the **bottom-of-sidebar action buttons**. Operational confirmations + rare-use commands (settings, refresh, new tool). Operators interact with these intentionally, never accidentally.

### What this hierarchy implies

The dashboard's vertical real-estate budget should split roughly: tiles 15%, tools+activity body 75%, status bar + sidebar action buttons 10%. The tools table itself should get ~65% of the body's horizontal width; the activity feed gets ~35%. These are guidelines, not pixel mandates — but if a surface deviates more than 10% from this it likely indicates a hierarchy problem.

---

## 6. Implementation sequencing

Strict order by **value-per-risk**. Each step is a separate B-series commit on `phase-3c-pcc-retrofit` with operator approval before landing. Stop at any step if visual review reveals an issue.

| # | Step | Why first | Risk | Spec needed before? |
|---|------|-----------|------|---------------------|
| 1 | **Lucide icons replace emoji glyphs** in sidebar nav + sidebar tool rows + dashboard tile labels | `phoenix_commons.icons` already ships the loader + ~10 Lucide SVGs. Mechanical migration, high visual upgrade, lowest risk. | Low | No — just inventory which emoji map to which Lucide name. |
| 2 | **`StatusBadge` widget added to commons** (new file in `phoenix_commons/widgets/`) | Required primitive for steps 3 + 5. Tiny additive component. | Low | Yes — small spec (variants: clean / dirty-N / unknown; size / padding / typography). |
| 3 | **Tools section: list → table** (`PhoenixTable` instance with NAME / LAST COMMIT / LOC / SIZE / STATUS columns) | The single most visible improvement. Replaces the current `ToolRow` list + the reverted B8 cards in one shot. Per-row context menu carries the four actions. | Medium | Yes — column widths, sort behavior, row-height, click-vs-context-menu semantics. |
| 4 | **Per-tool activity tag colors** in the existing activity feed | Small wiring — colour map per tool name. Activity feed already exists; just tints the tag pill. | Low | Yes — the per-tool color map (PCC orange, Lab Layout amber, Checkout green, etc.). |
| 5 | **Aggregate tile refresh**: 5 tiles → 4 tiles with leading icons + subtitle copy | Existing `AggregateTile` widget gets a small extension (icon slot, subtitle slot). Drops the "Needs Commit" tile since status now lives in the table. | Low-medium | Yes — which 4 tiles, subtitle copy convention, icon mapping. |
| 6 | **Top utility band**: page title + search bar (⌘K) + sync-state pill | Net-new surface above the dashboard body. Search shell only at first (no search backend) — keyboard shortcut works, surfaces a "coming soon" hint until step 7. | Medium | Yes — surface spec + sync-pill state machine (idle / scanning / synced / failed) + ⌘K binding. |
| 7 | **Search backend**: search across tool names, recent commit messages, open TODOs | First feature-level addition. Pure backend work behind the existing search shell from step 6. | Medium | Yes — search corpus + result ranking + result list shape. |
| 8 | **Status-bar shortcut hint**: "Press ⌘K to search" right-aligned | One-line addition. Depends on step 6 existing. | Trivial | No (covered by step 6 spec). |

Steps 1, 2, 4, 8 are mechanical and could land in a single sitting. Steps 3 + 5 + 6 each deserve their own session. Step 7 is a feature, not a polish; could defer indefinitely.

**Recommended sequencing of first cycle:** 1 → 2 → 3 (one operator-approved PR per step, with visual confirmation at each).

---

## 7. Explicit "what NOT to do"

- **Do not change PCC's BrandProfile slots.** Orange + teal stay per ADR-016. The screenshot's red/blue is reference, not mandate.
- **Do not invent a second design system.** All new components come from `phoenix_commons.widgets`, even if it requires authoring a small additive primitive (`StatusBadge`).
- **Do not animate the aggregate tiles.** No count-up animations on first paint. No tile flash on scan completion.
- **Do not add a notification surface.** Status bar and sync pill are the only places non-error operational state surfaces. If a notification system is needed later, it gets its own spec.
- **Do not change the sidebar's structural composition.** The sidebar's six current zones (logo / nav header / nav list / tool list / sprite / actions) stay. Internal styling can evolve; the structure doesn't.
- **Do not let the activity feed dominate.** It's tertiary. If it visually competes with the tools table, the activity feed is wrong — never the table.
- **Do not introduce per-surface palettes.** All accents come from the active BrandProfile (PCC's orange/teal) or commons semantic tokens (success green / warning amber / error red). No bespoke "this surface's accent is X."
- **Do not implement search before its spec lands.** Step 6 ships an empty search shell; step 7 is search backend. They don't merge.
- **Do not touch the production tools.** This spec is scoped to PCC's dashboard. Lab Layout, Checkout, PTT, PMT, ValveMaster have their own UX considerations; nothing here applies to them without separate per-tool review.
- **Do not redesign the detail panel, commons browser, or new-tool wizard.** Each of those surfaces deserves its own spec. This file is dashboard-only.
- **Do not propose net-new ADRs while implementing this spec.** If a step seems to require an ADR change, stop and raise it.

---

## 8. Relationship to ADR-016 + BrandProfile

ADR-016 is canonical. This spec operates inside its rules, not around them.

### What ADR-016 fixes

PCC's three brand slots stay:

```
PCC_BRAND = BrandProfile(
    primary   = "#E8783C",   # orange
    secondary = "#2A8880",   # teal-dark
    accent    = "#3CB8AE",   # teal
)
```

These slots feed the canonical sentinel-substituted commons QSS. They render every commons selector that targets a brand color. They are the PCC identity layer.

### What this spec adds (within ADR-016's envelope)

PCC's **chrome colors** (background, sidebar, surface, card, border) are NOT in any brand slot — they are not constrained by ADR-016 either way. PCC's current chrome (`bg=#18181F` purple-grey family) is a separate PCC choice that preserves the "management-app distinct from production tools" identity rationale ADR-016 cites.

This spec recommends **keeping the current purple-grey chrome family.** It distinguishes PCC visually from the navy-chrome production tools (Lab Layout, Checkout, PTT, etc.) at a glance — which IS the ADR-016 rationale, applied to chrome rather than just brand slots.

If a later operator review wants PCC to adopt the deeper navy chrome the screenshot shows, that's not an ADR-016 change — it's a separate decision on chrome bg tokens. The spec is neutral on that decision; it just notes it's a one-line `C["bg"]` change in PCC's `theme.py`.

### Per-tool activity-tag color map (commons additive)

The activity feed's per-tool tag colors (§3.5) should source from per-tool brand identity, not bespoke per-feed choices:

| Tool | Brand color reference | Source |
|------|----------------------|--------|
| Phoenix Command Center | `#E8783C` (orange — PCC_BRAND.primary) | ADR-016 |
| Lab Layout Tool | TBD (per the per-app brand-mark color in INVENTORY.md — "Orange/amber") | App-specific |
| Phoenix Checkout Tool | TBD (per INVENTORY.md — "Green") | App-specific |
| Project Tracking Tool | TBD (per INVENTORY.md — "Blue") | App-specific |
| Phoenix Master Tool | TBD (per INVENTORY.md — "Magenta") | App-specific |
| ValveMasterTool | TBD (no current brand-mark color recorded) | Needs assignment |
| phoenix-commons | a neutral teal (`#3CB8AE` per PCC_BRAND.accent — "platform" reads as "commons") | This spec |

**This implies a small commons addition:** a `TOOL_BRAND_COLORS` constant in `phoenix_commons.theme.tokens` mapping tool short-names to their tag-pill color. Authoring + populating this is part of step 4 in §6.

### Net architectural change

**Zero.** No new ADR. No BrandProfile reshape. No commons API breaking change. The additions described (`StatusBadge` widget, `TOOL_BRAND_COLORS` map) are pure-additive primitives. The PCC dashboard work is entirely within commons + PCC repos as they stand today.

---

## 9. What this spec is

A product/UX direction document. It describes *what* PCC's dashboard should be, not *how* to build it. Implementation specs for each step in §6 are separate documents (authored at step-approval time, not upfront). Code lands one approved step at a time on `phase-3c-pcc-retrofit`.

## 10. What this spec is not

- Not an implementation plan. §6 sequences the work; it does not specify the code.
- Not architecture doctrine. ADR-016 + PLATFORM_CONTRACT + MIGRATION_RULES remain the doctrinal layer.
- Not a redesign mandate. It absorbs the operator's directional screenshot into PCC's existing ADR-016 identity; PCC stays orange/teal.
- Not exhaustive. The detail panel, commons browser, settings dialog, and new-tool wizard each deserve their own spec when their time comes. This file is dashboard-only.

---

*End of spec.*
