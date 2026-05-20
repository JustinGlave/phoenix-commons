# DESIGN_SYSTEM.md

> The Phoenix dark-navy design system. One canonical structure
> (spacing, typography, widgets, QSS architecture, locked tokens),
> with a narrow controlled brand-profile override (3 tokens —
> `PRIMARY`, `SECONDARY`, `ACCENT`) per ADR-016. Apps follow this
> without exception; deviations beyond the brand-profile slots
> require a new ADR superseding ADR-016.

## Canonical palette (the default brand profile + locked tokens)

The canonical Phoenix palette landed in
`phoenix_commons.theme.tokens` in Phase 2.5. ADR-016 (2026-05-19)
classifies the tokens into two tiers: **locked** (commons-owned;
apps may NOT override) and **brand-profile variant-allowed**
(apps may override via the BrandProfile mechanism, landing in
Phase 3+).

### Locked tokens (universal across every Phoenix tool)

Background / surface tier:

| Token | Hex | Used for |
|-------|-----|----------|
| `BG` | `#0a0e27` | Window background |
| `SURFACE` | `#141829` | Cards / panels / inputs |
| `SURFACE_ALT` | `#0f1219` | Alternating-row surface |

Text (high → low contrast):

| Token | Hex | Used for |
|-------|-----|----------|
| `TEXT` | `#ffffff` | Primary body / labels |
| `MUTED` | `#94a3b8` | Secondary / placeholder / disabled |

Status (semantic — must be universal across all Phoenix tools so
affordances transfer cleanly between apps):

| Token | Hex | Used for |
|-------|-----|----------|
| `SUCCESS` | `#22c55e` | "clean", "passed", "online" |
| `WARNING` | `#f59e0b` | "dirty", "needs attention" |
| `ERROR` | `#ef4444` | Failure, blocked |

Spacing, typography, and radii (see later sections) are all
locked; apps may not override.

### Brand-profile tokens (variant-allowed per ADR-016)

Three named slots. Apps may override via `BrandProfile` at
`apply_dark_theme(app, brand=...)` time. The default profile
matches the values below — every tool that doesn't register an
override gets these.

| Token | Default hex | Used for |
|-------|-------------|----------|
| `PRIMARY` | `#dc2626` | Brand red — primary / destructive CTAs |
| `SECONDARY` | `#1e3a8a` | Deep blue — secondary brand chrome |
| `ACCENT` | `#3b82f6` | Blue — focus / link / highlight chrome |
| `INFO` | (= `ACCENT`) | Informational chrome — aliased to ACCENT, follows brand override automatically |

PCC's registered profile (per ADR-016 § 9 "Migration
implications"):

| Token | PCC override | Versus default |
|-------|---------------|-----------------|
| `PRIMARY` | `#E8783C` (Phoenix orange) | red → orange |
| `SECONDARY` | `#3CB8AE` (teal) | deep blue → teal |
| `ACCENT` | `#3CB8AE` (teal) | blue → teal |

Other production tools (Phoenix CAD / Job Tracker / Phoenix
Checkout / ValveMaster post-Phase-8a) use the default profile.

### Forbidden

- The legacy ValveMaster gray `#1c1c1c` palette ("System B"). Will
  be replaced by the default brand profile in Phase 8a retrofit.
- Pure black (`#000`) — use `BG` or `SURFACE_ALT`.
- App-local QSS / Python overriding **locked** tokens. Apps may
  override ONLY the three brand tokens above via `BrandProfile`.
- Inline `setStyleSheet("color: #ABCDEF")` in app code — even for
  brand-profile colours; route through `tokens.SEMANTIC_COLORS`
  / `tokens.PRIMARY` etc.
- Saturated mid-blues that clash with whichever brand `ACCENT`
  resolves to.

## Typography

Locked (apps may NOT override).

The objectNames below are the source of truth from
`phoenix_commons.widgets.typography`:

| Role | objectName | Family | Size | Weight |
|------|------------|--------|------|--------|
| Body | (default) | "Segoe UI", system | 13 px | 400 |
| Page title (`PageTitle` class) | `ProjectTitle` | same | 14 pt | bold |
| Page subtitle (`PageSubtitle`) | `ProjectSubtitle` | same | 10 pt | muted |
| Section title (`SectionTitle`) | `SectionTitle` | same | 12 pt | semibold |
| Hint label (`HintLabel`) | `hint` | same | 9 pt | muted |
| Monospaced (`mono` rule, planned) | (TBD) | "Consolas", monospace | 12 px | 400 |

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

Three button tiers, all from `phoenix_commons.widgets.buttons`.
The objectNames below are the **canonical source of truth** from
the widget code (verified Phase 2.5 / ADR-016 reconciliation —
earlier doc revisions named `accentBtn` / `ghostBtn` which never
existed in commons code; corrected here):

| Class | objectName | Visual | Use for |
|-------|-----------|--------|---------|
| `PrimaryButton` | (default — none) | Filled with brand `PRIMARY`, white text | The one main action on the screen (Save, Generate, Submit, Launch installed) |
| `SecondaryButton` | `secondaryButton` | Surface fill, body text | Supporting actions (Refresh, Settings, Cancel) |
| `TertiaryButton` | `tertiaryButton` | Transparent, brand-accent text | Inline / row-level actions (icon-only buttons, back arrows, dismiss ✕) |

Under the default brand profile, `PrimaryButton` renders red;
under PCC's registered profile, the same widget renders orange.
The class / objectName don't change — the brand-profile
substitution at apply time does.

Rules:

- **One `PrimaryButton` per dialog / screen.** If you need two,
  one should be `SecondaryButton`.
- **Don't put a coloured icon on a `PrimaryButton`** — the brand
  colour is already doing the work.
- **Use objectName-based QSS for "this button only" rules** —
  never inline `setStyleSheet("color: …")`.
- **App-local objectNames must not collide with commons-owned
  names** (`secondaryButton`, `tertiaryButton`, `Panel`,
  `ProjectTitle`, `ProjectSubtitle`, `SectionTitle`, `hint`,
  `UpdateBanner`, `UpdateMsg`, `InstallBtn`) — see
  `COMPONENT_CONTRACT.md` § Reserved name rules.

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
| `phoenix_commons.theme.tokens` module | 2.5 ✅ landed | Canonical token home; mirrors the QSS-file palette per Phase 2.5. |
| `BrandProfile` mechanism + sentinel-form QSS | 3A ✅ landed | Implements ADR-016. `apply_dark_theme(app, brand=...)` kwarg sentinel-substitutes `__BRAND_PRIMARY__` / `__BRAND_SECONDARY__` / `__BRAND_ACCENT__` at apply time. Default profile preserves canonical Phoenix red + deep blue + blue. |
| PCC retrofit registering its brand profile | 3C | Per ADR-016 § 9. The mechanism is now in place; PCC's retrofit just registers `BrandProfile(primary="#E8783C", secondary="#3CB8AE", accent="#3CB8AE")`. |
| Auto-generated component gallery | 9 | Snapshot screenshots of every widget in every state. |
| Light-mode palette | not planned | Phoenix apps are dark-mode by design. ADR-011 deferred indefinitely. |
| WCAG audit | 9 | All brand-accent / status combos against text colours, per brand profile. |
