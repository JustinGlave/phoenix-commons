# Phoenix Command Center — Visual Baseline

> Phase 2.7 pre-migration markdown baseline. PCC is **the
> platform owner** — the management / scaffolding app the
> rest of the Phoenix tools are coordinated from — and the
> lone tool currently running a **different palette** than
> the QSS-based production tools.
>
> Captured 2026-05-19. PCC is source-run (not packaged), so the
> "deployed view" is the same as the dev view: `python main.py`
> from the working tree.

## 1. Identity

| Field | Value |
|-------|-------|
| App name (display) | **Phoenix Command Center** |
| Source repo | `phoenix-command-center` |
| Exe | n/a — source-run only (not packaged) |
| Install path | n/a |
| User-data | `pcc_config.json` (stored alongside `main.py` at project root) |
| Current version | `2.0.0` |
| Build pipeline | n/a — no `build.bat`, no PyInstaller, no Inno Setup |
| Updater | n/a |

## 2. Current theme system — **the divergent palette**

**PCC does not use `phoenix_style.qss`.** It uses `theme.py` —
a Python QSS generator with a `C` dict that produces a
**different palette** than the QSS-based tools.

| Component | Where it lives | What it generates |
|-----------|----------------|--------------------|
| `theme.py` (PCC repo) | `phoenix-command-center/theme.py` | Generates QSS from a Python `C` dict |
| `C` dict | inside `theme.py` | Maps semantic names → hex; **different hex values** than the QSS-file palette |

Looking at `DESIGN_SYSTEM.md` in this repo (which documents PCC's
palette as "System A"):

| Token | PCC `theme.py` `C` dict (per `DESIGN_SYSTEM.md`) | `phoenix_style.qss` (Phoenix CAD / Job Tracker / Phoenix Checkout) |
|-------|----------------------------------------------------|-----------------------------------------------------------------|
| Background | `#18181F` | `#0a0e27` |
| Surface | `#21212E` / `#27273A` (card) | `#141829` |
| Primary brand colour | **orange** `#E8783C` | **red** `#dc2626` |
| Secondary brand colour | **teal** `#3CB8AE` | **blue** `#3b82f6` |
| Body text | `#E4E4F0` (light gray) | `#ffffff` (pure white) |
| Status warning | `#F0A030` | `#f59e0b` (different exact orange) |
| Status error | `#E84848` | `#ef4444` (different exact red) |

These are not "minor drifts" — they're **two distinct visual
systems**, both currently labelled "System A" in different docs.
This is the headline finding of Phase 2.7. See
`STABILIZATION_REPORT_06.md` § Visual inconsistencies discovered.

`phoenix_commons.theme.tokens` (landed Phase 2.5) mirrors the
**QSS-file palette** (navy + red + blue), so commons-canonical
is the QSS-file palette. PCC's retrofit will produce a
**user-visible palette swap** when it migrates to the commons
tokens.

## 3. Main window

PCC is a tool launcher / management hub. Window layout
(inferred from the project's V1 description in memory):

- **Left sidebar** with the list of Phoenix tools (each as a
  `ToolCard` widget)
- **Right content pane** showing the selected tool's actions
  (Open, Settings, Build, Run from Source, etc.) and metadata
- **Top bar** with the current Phoenix-commons indicator,
  global actions
- **Status bar** with version + (post-retrofit) update banner

Window is sized to comfortably show ~6 tool cards in the sidebar
without scroll. Window remembers position/size via `QSettings`
or `pcc_config.json`.

## 4. Dashboard / home view

The default view on launch is **the tool hub** — sidebar shows
every Phoenix tool, right pane shows the currently-selected
tool's actions. No separate "dashboard" — the hub IS the home.

Visual identity comes from:

- The orange/teal palette (currently — pre-retrofit)
- The `SidebarSprite` widget (a small animated mark, app-local
  identity asset)
- The Phoenix Command Center wordmark in the top-left

## 5. Forms

- **Settings dialogs / panels** — text inputs for commons path,
  GitHub auth, default new-tool location
- **New Tool wizard** — multi-step form (template choice → name
  → location → confirm)
- **Per-tool settings panels** — version + path + recent commits

Form rows use `Panel` containers and the Phoenix button tiers
— but **the buttons' visual is different** because PCC's `theme.py`
generates different QSS rules for them.

## 6. Tables / grids

- **Tool list (in the sidebar)** — `ToolCard` widgets in a
  `QListWidget` or hand-rolled scroll area
- **Recent commits per tool** — small table showing SHA + author
  + message + date
- **Branch list** — table of branches with HEAD indicator
- **Diff preview** (planned V2) — table or text view

## 7. Dialogs

- **New Tool wizard** — multi-page `QDialog`
- **Settings dialog** — `QDialog` with tabs (General /
  Advanced / Commons)
- **Confirmation modals** — `QMessageBox.question` for
  destructive actions (delete a scaffold, push to main)
- **Error modals** — `QMessageBox.critical`

## 8. Update banner

**N/A.** PCC is source-run; no updater. (When PCC eventually
gets packaged — open question per `production-inventory.md`
§ phoenix-command-center — it inherits the `UpdateBanner`
pattern.)

## 9. Empty states

- **No tools configured** — hint pointing at `Settings →
  Configure tool paths`
- **No commons configured** — disabled "commons-backed" radio
  in the new-tool wizard with the inline reason copy (see
  `MIGRATION_RULES.md` for the exact wording)
- **No recent commits** — "No commits in the last N days"
  message

## 10. Dense-data states

PCC's heaviest dense-data surface is **the git history view**
for a tool — can be hundreds of commits. Uses pagination or
limit-by-date to keep it tractable.

## 11. Error / warning states

- **Tool path misconfigured** — banner-style warning at the
  top of the right pane
- **Commons submodule out of date** — explicit warning with
  "Update submodule" CTA
- **Git operation failed** — modal `QMessageBox.critical` with
  the git stderr inline

## 12. Sidebar / navigation states

The sidebar is **the primary navigation surface** — selecting
a tool drives the right pane. Different from the production
tools which have menu-bar-driven navigation.

Sidebar items:

- One entry per Phoenix tool (Job Tracker, Phoenix CAD, Phoenix
  Checkout, ValveMaster, plus PCC itself)
- Each entry shows: tool icon + display name + current version
  + commit status indicator (clean / dirty / ahead-behind)

## 13. Known visual debt

| # | Item | Severity |
|---|------|----------|
| 1 | **Different palette than the rest of Phoenix tools** (orange/teal vs navy/red/blue) | **High — the headline Phase 2.7 finding** |
| 2 | `theme.py` is a Python QSS generator, divergent shape from `phoenix_style.qss` (file-based) | High — different generation model entirely |
| 3 | `DESIGN_SYSTEM.md` documents PCC's palette as "System A" while the QSS file claims the same name | High — naming collision, will confuse retrofit reviewers |
| 4 | Six inline `font-family: Consolas` usages in widget code (per `DESIGN_SYSTEM.md` § Forbidden patterns) | Medium — tracked in TODOs |
| 5 | No `paths.py` helper; config stored at project root in source-run mode | Low — packaging-time concern, not visual |

## 14. Known inconsistencies

| # | Item | Notes |
|---|------|-------|
| 1 | PCC defines its own widget classes (`CommonsDropZone`, `SidebarSprite`, `ToolCard`) that don't exist elsewhere | These are PCC-specific by design — see `PLATFORM_CONTRACT.md` § Widgets. Stay app-local. |
| 2 | PCC's `theme.py` uses a `C` dict — the same name as the alias in `phoenix_commons.theme.tokens` (deliberate, for compatibility) | The shape matches; the values diverge. PCC's retrofit must reconcile. |
| 3 | PCC uses `theme.py`-generated QSS at runtime; no `*.qss` file is bundled | Different shape than every other tool. Retrofit will swap the runtime generation for the QSS-file path. |

## 15. Migration sensitivity

**Headline:** PCC's retrofit is the **most visually visible**
retrofit in the production batch — the palette literally swaps
from orange/teal to red/blue (or whatever the commons-canonical
ends up being post-Phase-9 ADR discussion).

| Surface | Sensitivity | Why |
|---------|-------------|-----|
| Primary CTAs (orange → red) | **Very high** | Every "primary" button on every screen changes colour. |
| Status indicators (orange warning → amber warning) | High | Subtle but visible. |
| Card chrome (different surface hex values) | High | Every panel reads as a slightly different shade. |
| Typography (light gray text → pure white text) | Medium | Body text changes contrast. |
| Sidebar identity sprite | Low | App-local asset; stays put. |
| Tool icons | Medium | Migration to Lucide set per `ICON_POLICY.md`; emoji-style decorations replaced. |
| Settings + wizard chrome | High | Form inputs, buttons, dropdowns all reshade. |
| Update banner | New | Doesn't exist today; appears post-packaging. Sign-off required. |

**This retrofit needs explicit user-visible sign-off** before
landing. Two paths to consider in the PCC retrofit PR:

1. **Adopt the commons-canonical palette as-is** — PCC becomes
   visually identical to the production tools. Loses some of
   the "Phoenix Command Center identity" but gains cohesion.
2. **Negotiate a token revision** — propose adding an
   `accent_alt` token to commons that maps to PCC's current
   orange, and use that for PCC's brand accents while
   adopting commons surfaces / type / spacing for the rest.
   Compromise: PCC keeps brand-identifying colours while
   adopting all the structural System A goodness.

The decision goes in an ADR before the retrofit PR opens.

## 16. High-risk screens

For PCC's eventual retrofit:

1. **The tool hub (default view)** — most-seen screen; palette
   swap is most visible here.
2. **The new-tool wizard** — multi-step UX with prominent
   primary CTAs that change colour.
3. **Settings dialog** — combo / spin / line-edit chrome all
   change subtly.
4. **Sidebar — `ToolCard` widget** — each card's hover /
   selected state depends on the palette.
5. **Any usage of `SidebarSprite`** — confirm it still
   composites cleanly over the new background colour.

## See also

- `../README.md` § "Three palettes coexist in production" —
  the cross-cutting finding this baseline anchors
- `../MIGRATION_VISUAL_REVIEW_CHECKLIST.md` § "PCC palette
  reconciliation"
- `../../DESIGN_SYSTEM.md` — currently documents PCC's
  palette as System A; will need an update once the
  retrofit decision lands
- `../../production-inventory.md` § phoenix-command-center —
  identity source
- `../../STABILIZATION_REPORT_06.md` — Phase 2.7 deliverable
