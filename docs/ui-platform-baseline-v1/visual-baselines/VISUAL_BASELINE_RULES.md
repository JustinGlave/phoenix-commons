# VISUAL_BASELINE_RULES.md

> Governance for the per-app visual baselines under
> `visual-baselines/`. Naming, sizing, DPI, dark-mode, capture
> consistency, and the line between "acceptable parity" and
> "regression that needs sign-off" during retrofit review.

## Why baselines exist

A retrofit (Phase 3A onwards) replaces an app's local theme +
widgets with the commons equivalents. The retrofit is supposed
to be **visually neutral** for every production tool already
shipping on System A — Phoenix CAD, Job Tracker, Phoenix Checkout,
**and ValveMaster / Phoenix Master Tool** (`v1.1.0` already shipped
the canonical System A palette in `phoenix_style.qss`; the
`WAVE_8A_VALVEMASTER_PREFLIGHT_AUDIT.md` byte-match verification
deflated the earlier "System B → A" prediction. Expected visible
change ≈ 0%, Phoenix-CAD profile).

Without a captured reference, "visually neutral" devolves into
"looks fine to me" — and small drifts pile up. Baselines are
the objective reference. A retrofit PR that produces a different
result than the baseline must EITHER:

1. Adjust the change so the result matches the baseline, OR
2. Justify the visual difference in the PR description with
   explicit sign-off in `MIGRATION_VISUAL_REVIEW_CHECKLIST.md`.

## Capture mode (Phase 2.7)

The Phase 2.7 baselines are **markdown-only**, no screenshots.
Three reasons:

1. **AV/S1 quarantine prevents reliable frozen-exe execution on
   the dev laptop.** A screenshot of the source-run app under
   offscreen Qt isn't a faithful representation of what end
   users see on their installed copies.
2. **Production tool source isn't modified during Phase 2.7.**
   Spinning up each tool just to screenshot would be the start
   of mucking with the apps — out of scope.
3. **Screenshots become stale fast.** A markdown reference
   describing the **structure** (objectNames, widget classes,
   layout containers, palette tokens) survives small visual
   drift; a pixel-perfect PNG doesn't.

Each retrofit PR is responsible for capturing **its own**
screenshots when the first migration screenshot run is possible
(post-AV chain resolution), and uploading them alongside the
markdown baseline as `screenshots/<surface>.png`.

## File naming

### Per-app baseline file

Exactly one file per app folder:

```
visual-baselines/<app>/baseline.md
```

Section structure defined in `README.md` § "Reading the per-app
baselines".

### Screenshot files (when captured)

```
visual-baselines/<app>/screenshots/<surface>-<state>.png
```

Surface name from the 10-row capture list (see `README.md`):

| Surface name | Maps to |
|--------------|---------|
| `main-window` | (1) Main window |
| `dashboard` | (2) Dashboard / home view |
| `forms` | (3) Forms |
| `tables` | (4) Tables / grids |
| `dialogs` | (5) Dialogs |
| `update-banner` | (6) Update banner state |
| `empty` | (7) Empty states |
| `dense` | (8) Dense-data states |
| `error` | (9) Error / warning states |
| `sidebar` | (10) Sidebar / navigation states |

State suffix (when relevant):

| State | Meaning |
|-------|---------|
| `default` | Standard appearance (omit suffix for default) |
| `hover` | Mouse-over highlight |
| `focus` | Keyboard focus |
| `selected` | Active selection |
| `disabled` | Greyed out |
| `error` | With validation error |

Example:

```
visual-baselines/checkout/screenshots/forms-default.png
visual-baselines/checkout/screenshots/forms-error.png
visual-baselines/checkout/screenshots/main-window-empty.png
```

### Branch-tag for retrofit screenshots

When a retrofit captures its **post-retrofit** screenshots,
suffix the filename with the retrofit phase identifier:

```
visual-baselines/checkout/screenshots/forms-default--phase-3a.png
visual-baselines/checkout/screenshots/forms-default--phase-3b.png
```

`--phase-2.7` for the pre-migration originals; later phases get
their own suffix. The diff at PR-review time is between the
nearest predecessor (or `--phase-2.7` if it's the first
retrofit).

## Window sizing

Standard screenshot window size: **1920×1080** (FHD), the most
common ATS workstation resolution.

Smaller window variants for surfaces that need it:

| Width | Use case |
|-------|----------|
| 480 px | Dialogs (one of the centred-modal screenshots) |
| 1280×720 | Compact-laptop variant (if a tool's dense-data view doesn't fit smaller) |
| 1920×1080 | Default — every full-window capture |
| 2560×1440 | QHD variant for the few users on bigger monitors |

If a tool's window doesn't resize down to 1280×720 cleanly,
that's itself a visual-debt finding — flag it in the baseline's
`Known visual debt` section.

## DPI assumptions

| Capture mode | DPI |
|--------------|-----|
| Standard | 1.0 (96 DPI Windows default) |
| Hi-DPI | 1.5 (some laptops) — capture if available |
| Very-hi-DPI | 2.0 — out of scope (no ATS workstation runs at 2x) |

Tools that have explicit hi-DPI bugs (icon misalignment, font
clip) should be screenshot-captured at both 1.0 and 1.5 for the
affected surface.

## Dark-mode assumption

**Phoenix is dark-mode only.** ADR-011 deferred light mode
indefinitely. Every screenshot, every baseline reference, every
retrofit visual is dark-mode.

The Windows-level "Use dark mode for apps" setting must be **ON**
during screenshot capture so the OS-rendered chrome (window
title bar, scrollbar arrows) matches the in-app dark theme. A
dark Phoenix app inside a light Windows title bar reads as a
bug.

## Capture consistency rules

When the first screenshot run starts, follow these to keep the
visual diff legible:

1. **Same monitor for every capture in a given run.** Different
   monitor colour profiles produce different pixels for the
   same input.
2. **Same Windows scaling setting** (100 %, 125 %, etc.) for
   every capture. Note the value in the screenshot filename
   if non-default (`...@125pct.png`).
3. **Same window state** (maximised / standard) for every capture
   of the same surface across apps. Mixed states make
   apples-vs-oranges comparison.
4. **Hide the cursor** for shots that aren't specifically
   capturing hover state. A stray cursor over a button creates
   spurious hover highlight.
5. **Wait for animations to settle** before capturing. Hover
   halos / scroll-position settling can take 200 ms.
6. **No personal data in the frame.** Sample data only — never
   capture real customer names / project numbers / file paths
   that include `Justin`.
7. **PNG, not JPEG.** Lossless for visual diffs.

## Acceptable parity

A retrofit PR is **visually neutral / acceptable parity** if:

- ✅ Spacing matches within ±2 px on every dimension visible in the screenshot.
- ✅ Typography matches: same font family, same size, same weight,
  same letter-spacing.
- ✅ Palette matches: every colour used in the new render is in
  `phoenix_commons.theme.tokens.SEMANTIC_COLORS` AND every
  colour used in the baseline has a corresponding match in the
  new render (no "muted" rendering as "text" or vice versa).
- ✅ Panel / card hierarchy matches: same `objectName="Panel"` or
  equivalent, same border, same radius, same padding.
- ✅ Button semantics match: primary/secondary/tertiary
  distribution is unchanged.
- ✅ Icon set matches: every icon either present in both or
  intentionally replaced (with rationale).
- ✅ Update banner appears in the same status-bar position with
  the same copy template.
- ✅ Focus / hover / disabled states render with the same
  semantic colours (not necessarily pixel-identical — minor
  hover-halo recoloring is acceptable if the semantic is
  preserved).

## What counts as regression

A retrofit produces a **regression** if any of:

- ❌ A widget that used to be a `Panel` is now a raw `QWidget`
  with no rounded-card chrome.
- ❌ A button that used to be `PrimaryButton` is now a raw
  `QPushButton`.
- ❌ A colour used in the new render is **not** in the commons
  tokens AND is not from the app's per-app addendum stylesheet.
- ❌ A surface that fit on 1920×1080 in the baseline now
  requires scrolling or window resizing.
- ❌ Form-field tab order changed without explicit reason.
- ❌ Update-banner placement moved from status bar to somewhere
  else.
- ❌ Empty-state copy / help text removed (functional
  regression).

Regression PRs are not merged. Either fix the regression or
escalate to the explicit-sign-off path below.

## What requires explicit sign-off

Some changes are visible but **intentional**. They go through
this gate:

1. The PR description names the visual change explicitly.
   *"This retrofit changes the Panel hover state from a
   gradient to a flat colour — matches the commons standard
   per `COMPONENT_CONTRACT.md` § Reserved objectNames."*
2. The `MIGRATION_VISUAL_REVIEW_CHECKLIST.md` checklist line
   for that change is checked **and** annotated.
3. The reviewer (Justin) explicitly approves the diff. A
   thumbs-up alone isn't sign-off; the comment must say
   "approved with the noted intentional change at
   <screenshot-path>".

Examples of changes that always require explicit sign-off:

- Any change in font family (e.g. dropping a bundled font in
  favour of system Segoe UI — would change kerning slightly).
- Any change in primary/secondary semantics (e.g. promoting a
  button tier).
- Replacement of an emoji icon with a Lucide SVG (different
  glyph shape; acceptable per `ICON_POLICY.md` but visible).
- Any future tool that arrives on a non-canonical palette and
  is retrofitted to System A. (No production tool currently
  matches this case — ValveMaster's `v1.1.0` release already
  shipped the canonical palette per
  `WAVE_8A_VALVEMASTER_PREFLIGHT_AUDIT.md`. The earlier
  "ValveMaster System B → A palette swap" example was retired
  on 2026-05-26.)

## When baselines update

Two triggers re-capture a baseline:

1. **Post-retrofit re-baseline.** Once a retrofit lands, the
   "after" state becomes the new baseline for that surface.
   Replace `screenshots/<surface>-default.png` with the new
   capture; keep the old as `<surface>-default--phase-2.7.png`
   for historical diff.
2. **Phoenix System A revision.** If the canonical palette /
   token / spacing scale changes (e.g. light mode lands,
   System A v2 spec), every baseline re-captures against the
   new spec. Mark the re-capture date in the markdown's "Last
   captured" footer.

Baselines do **NOT** update for:

- Bug fixes that don't affect the visual baseline (e.g. a
  backend race condition).
- Copy / content changes that don't alter layout (the baseline
  references "the empty state shows a hint and a CTA button" —
  not the exact text).

## Non-canonical baselines (mid-migration tools)

ValveMaster's current state is **non-canonical** — it runs on
the deprecated System B. The same logic applies to any future
tool found running an out-of-spec palette during Phase 0
inventory.

Rules for non-canonical baselines:

1. **Don't carry a long-term baseline doc for the non-canonical
   state.** The state is, by definition, going to be replaced.
2. **Capture the non-canonical baseline only at the start of
   the migration PR**, in `visual-baselines/<app>/screenshots/`
   with the `--system-b` suffix.
3. **The "after" baseline is whatever the canonical retrofit
   produces.** Use the migration review checklist's "System B
   → A cutover" section.

## Migration review expectations

For every Phase 3A+ retrofit PR:

1. Apply `MIGRATION_VISUAL_REVIEW_CHECKLIST.md` row by row.
2. Attach screenshots for **at minimum** the main window + one
   form + one table + the update banner + one dialog state.
3. Diff each new screenshot against its `--phase-2.7` baseline
   (or against the most recent successor).
4. Address every regression. Document every intentional
   visible change with explicit sign-off.
5. Once merged, replace the `--phase-2.7` baseline with the
   new state under a `--phase-3a` (or appropriate) suffix.

PRs that skip the visual review block on the reviewer.

## See also

- `MIGRATION_VISUAL_REVIEW_CHECKLIST.md` — the per-PR checklist
- `README.md` (in this dir) — structure + alias map
- `../DESIGN_SYSTEM.md` — design-system reference (palette,
  type ramp, spacing scale)
- `../PLATFORM_CONTRACT.md` § Forbidden patterns — the visual
  anti-patterns retrofits must remove
- `../ADR-011` (in `DECISIONS.md`) — "No light mode"
