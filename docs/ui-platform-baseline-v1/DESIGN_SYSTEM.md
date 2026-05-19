# DESIGN_SYSTEM.md

> The Phoenix dark-navy design system (System A). One palette, one
> type ramp, one spacing scale, one widget catalog. Apps follow it
> without exception; deviations require a Phase 2.1 token-vocabulary
> PR before any app code lands.

## Palette (System A)

Background / surface tier (darker → lighter):

| Token | Hex | Used for |
|-------|-----|----------|
| `bg` | `#18181F` | Window background |
| `sidebar` | `#1C1C2A` | Sidebar background |
| `surface` | `#21212E` | Content surface (input rows, etc.) |
| `card` | `#27273A` | Cards, panels, tool rows |
| `card_hover` | `#2E2E42` | Card hover state |
| `card_sel` | `#32324A` | Card selected state |
| `border` | `#34344A` | Default border |
| `border_hi` | `#4A4A68` | Hover / highlighted border |

Accent + brand:

| Token | Hex | Used for |
|-------|-----|----------|
| `accent` | `#E8783C` | Phoenix orange — primary CTAs, brand emphasis |
| `accent_dark` | `#C05E28` | Pressed-state CTAs |
| `accent_glow` | `rgba(232, 120, 60, 0.18)` | Soft glow / hover halo |
| `teal` | `#3CB8AE` | Secondary brand colour — totals, commons indicators |
| `teal_dark` | `#2A8880` | Pressed-state secondary |

Text (high → low contrast):

| Token | Hex | Used for |
|-------|-----|----------|
| `text` | `#E4E4F0` | Primary body / labels |
| `text_sub` | `#9090B0` | Secondary text (subtitles, hints) |
| `text_muted` | `#58587A` | Muted (placeholder, disabled) |
| `text_inv` | `#18181F` | Text on light surfaces (rare) |

Status (semantic):

| Token | Hex | Used for |
|-------|-----|----------|
| `success` | `#4EC47A` | "clean", "passed", "online" |
| `warning` | `#F0A030` | "dirty", "needs attention" |
| `error` | `#E84848` | Failure, blocked |

Forbidden:

- The legacy ValveMaster gray `#1c1c1c` palette ("System B"). Will
  be replaced by System A in Phase 8a retrofit.
- Pure black (`#000`) — use `text_inv` or `bg`.
- Pure white (`#FFF`) — use `text` for body text.
- Saturated mid-blues that clash with `accent_glow` halos.

## Typography

| Role | Family | Size | Weight | Letter-spacing |
|------|--------|------|--------|----------------|
| Body | "Segoe UI", "SF Pro Display", sans-serif | 13 px | 400 | — |
| Section header (`sectionHeader`) | same | 10 px | 700 (uppercase) | 1.2 px |
| Page title (`pageTitle`) | same | 28 px | 800 | -0.5 px |
| Stat value (`statValue`) | same | 28 px | 800 | -0.5 px |
| Stat label (`statLabel`) | same | 10 px | 700 (uppercase) | 1.2 px |
| Card title (`cardTitle`) | same | 13 px | 700 | — |
| Hint label (`HintLabel`) | same | 11 px | 400 | — |
| Monospaced (`mono` rule, planned) | "Consolas", monospace | 12 px | 400 | — |

System fonts only — no bundled `.ttf`. PySide6 inherits the user's
Segoe UI on Windows; the fallback chain covers macOS / Linux for
dev work but production is Windows-only.

## Spacing scale

Phoenix uses a 4 px base spacing scale:

| Token (planned) | Value | Used for |
|-----------------|-------|----------|
| `space_1` | 4 px | Tight inline gaps |
| `space_2` | 8 px | Default widget spacing |
| `space_3` | 12 px | Between rows in a list |
| `space_4` | 16 px | Padding inside a card |
| `space_5` | 20 px | Section padding |
| `space_6` | 24 px | Outer page padding |
| `space_8` | 32 px | Major section break |

Spacing tokens will be exposed via `phoenix_commons.theme.tokens`
in Phase 2.1. Today they're inline magic numbers; the migration is
mostly find-and-replace.

## Border radius

| Token (planned) | Value | Used for |
|-----------------|-------|----------|
| `radius_sm` | 4 px | Inline chips, small buttons |
| `radius_md` | 6 px | Standard buttons, sidebar list items |
| `radius_lg` | 8 px | Tool cards, panels, larger buttons |
| `radius_xl` | 10 px | Dashboard tool-row cards (current value after Phase 6 polish) |

Cards never have square corners. Pure rectangles read as legacy
Windows chrome.

## Button semantics

Three button tiers, all from `phoenix_commons.widgets.buttons`:

| Class | objectName | Visual | Use for |
|-------|-----------|--------|---------|
| `PrimaryButton` | `accentBtn` | Filled orange, white text | The one main action on the screen (New Tool, Save, Launch installed) |
| `SecondaryButton` | `ghostBtn` | Card-coloured fill, body text | Supporting actions (Refresh, Settings, Cancel) |
| `TertiaryButton` | (default) | Transparent, accent text | Inline / row-level actions (icon-only buttons, back arrows) |

Rules:

- **One PrimaryButton per dialog / screen.** If you need two, one
  should be Secondary.
- **Don't put a coloured icon on a Primary** — the colour is
  already doing the work.
- **Use object-name overrides for "this button only" rules** — never
  inline `setStyleSheet("color: …")`.

## Interaction colours

| State | Treatment |
|-------|-----------|
| Default | Token colour as listed above |
| Hover | `*_hover` token if defined, else 10% brightness boost |
| Pressed | `*_dark` token if defined, else 15% brightness drop |
| Focused | Add a 1 px `accent` outline (`border-color: {C['accent']}`) |
| Disabled | 50% opacity; cursor `Qt.ForbiddenCursor` |

## Panel rules

`phoenix_commons.widgets.Panel` is the only sanctioned card
container.

- Rounded corners (`radius_lg` minimum)
- 1 px `border` border
- `card` background
- 14 px inner padding (current `setContentsMargins(14, ...)` value)
- Hover state lifts to `card_hover` + `border_hi`

A "card" that's not a `Panel` (e.g. dashboard tool-row cards) is a
domain-specific widget that follows the same visual rules but adds
hit-target behaviour.

## Icon philosophy

| Tier | Owner | Examples |
|------|-------|----------|
| Base set | commons (Phase 2.6) | refresh, settings, search, info, warning, error, success, chevron, sidebar-collapse |
| App logo | each app | Phoenix Command Center's logo (the ATS cityscape); Job Tracker's PTT mark; Phoenix CAD's LLT mark |
| Per-app status | each app | Phoenix CAD's BricsCAD-specific glyphs; ValveMaster's valve-type icons |
| User-content icons | the user | n/a — Phoenix tools don't load arbitrary user images at UI level |

Icon files MUST be:

- SVG when possible (scales cleanly under DPI changes).
- 16 / 24 / 32 px for raster fallbacks (matches PySide6 standard
  sizes).
- ICO multi-resolution for the **exe icon** (16 / 32 / 48 / 64 /
  128 / 256). One per app, lives at `app/assets/logo.ico`.

## App-specific identity rules

Apps express identity via:

- **Logo + wordmark** (app-local)
- **Animated splash / sprite** (optional, app-local — see PCC's
  sidebar sprite)
- **Window title** (`<App Display Name>` from `NAMING_REGISTRY.md`)
- **Taskbar icon** (`logo.ico`)
- **Per-app accent variations** (e.g. an app might emphasise `teal`
  over `accent` in its primary nav — this is allowed because both
  are commons tokens)

Apps do NOT express identity via:

- Custom colour palettes outside System A
- Custom typefaces
- Custom button shapes that aren't `radius_lg`-rounded rectangles
- "Skinned" widgets that look meaningfully different from the
  commons catalog

## Forbidden patterns

| Pattern | Why |
|---------|-----|
| Hard-coded hex colour in app code (`setStyleSheet("color: #ABCDEF")`) | Bypasses tokens; theme drifts over time. |
| Buttons styled with `setStyleSheet` instead of `objectName + QSS` | Same — drift surface. |
| Custom font import (`QFontDatabase.addApplicationFont(...)`) | Adds bundled-font weight + locale issues. Use system fonts. |
| Square-cornered cards / panels | Looks legacy. |
| White text on Phoenix orange (the orange accent) | Insufficient contrast; pressed-state confusion. Use `text` (light gray) which has been WCAG-checked. |
| ValveMaster's `#1c1c1c` gray palette | "System B" is being phased out in Phase 8a. |
| Coloured icons on a `PrimaryButton` | Visual noise. |
| `QMessageBox` for routine info (e.g. "Saved.") | Use the status bar. Modal dialogs are for decisions, not narration. |
| Inline `font-family: Consolas` in widget code | Use the planned mono `objectName` rule. Six existing occurrences in PCC; tracked in TODOs. |

## Visual rhythm checklist

Run through this before merging any UI change:

- [ ] Every coloured pixel comes from a token.
- [ ] Every font size comes from the type ramp.
- [ ] Every padding / margin value is a multiple of 4.
- [ ] Every border radius comes from the radius scale.
- [ ] Buttons are the right tier (one Primary per screen).
- [ ] Cards have rounded corners + the standard border.
- [ ] No `setStyleSheet` with hex literals.
- [ ] No commons selector overridden (only extended).

## Future work

| Item | Phase | Notes |
|------|-------|-------|
| `phoenix_commons.theme.tokens` module | 2.1 | Promotes the current `C` dict to a real public API. |
| Auto-generated component gallery | 9 | Snapshot screenshots of every widget in every state. |
| Light-mode palette | not planned | Phoenix apps are dark-mode by design. No light mode on roadmap. |
| WCAG audit | 9 | All accent / status combos against text colours. |
