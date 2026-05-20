# Design Items — Phoenix brand asset sources

> Brand-asset source files for the Phoenix tool family. **Not packaged**
> — this folder is repository-tracked but not included in the
> `phoenix_commons` Python package (see `pyproject.toml`). Consumers
> are humans and asset-management workflows, not runtime code.
>
> The canonical contract for how to consume these files in a Phoenix
> tool is `docs/ui-platform-baseline-v1/BRANDING_ASSET_GUIDE.md`. Read
> that first.

## Inventory

### Phoenix logo (large brand source)

| File | Size | Purpose |
|------|------|---------|
| `PTT Normal.jpg` | ~270 KB | Large-format Phoenix logo on a solid background. Brand-design source — not used at runtime by any tool. |
| `PTT Transparent.jpg` | ~370 KB | Large-format Phoenix logo with a transparent-style background (JPG, so not actually alpha-channel transparent). |
| `PTT Transparent.ico` | ~4 KB | ICO export of the transparent Phoenix logo. Possible installer-icon source for future tools. |

**Note on the "PTT" prefix** — `PTT` stands for "Project Tracking
Tool" (Job Tracker), but these large-format brand sources are NOT
specific to Job Tracker. They're the generic Phoenix logo, captured
back when PTT was the only consumer. Future renames should drop the
`PTT_` prefix (e.g. `Phoenix Normal.jpg`, `Phoenix Transparent.jpg`).
See `BRANDING_ASSET_GUIDE.md` § "Outstanding naming inconsistencies"
for the full list.

### Color variants (`colors/` subdirectory)

The Phoenix logo recoloured into the per-tool brand colors:

| Color | `.png` (transparent) | `.ico` | Consumed by |
|-------|----------------------|--------|-------------|
| **orange** | `orange.png` (214 KB) | `orange.ico` (2 KB) | Phoenix CAD (Lab Layout Tool) — copied as `LLT_Transparent.png` + `LLT_Normal.ico` |
| **green** | `green.png` (225 KB) | `green.ico` (2 KB) | Phoenix Checkout — copied as `green.png` + `PTT_Normal_green.ico` (note: PTT prefix is a misnomer) |
| **blue** | `blue.png` (1.4 MB) | `blue.ico` (4 KB) | Job Tracker — copied as `PTT_Transparent.png` + `PTT_Normal.ico` |
| **red** | `red.png` (214 KB) | `Normal_red.ico` (4 KB) | ValveMaster — copied as `Transparent_red.png` (note: slight content divergence — ValveMaster's tracked file is 215,115 B vs commons's 214,472 B, cause unknown) + `Normal_red.ico` (byte-identical) |
| purple | `purple.png` + `purple.ico` | — | Reserved — no production tool uses this color yet. Available for future tools. |
| yellow | `yellow.png` + `yellow.ico` | — | Reserved — same. |

Each production tool's tracked icon/PNG was hash-verified against
the commons sources on 2026-05-19 — see `BRANDING_ASSET_GUIDE.md` for
the SHA-256 results.

### Naming oddity

Only `Normal_red.ico` uses the `Normal_<color>` form. The other ICOs
in `colors/` are bare-colour (`green.ico`, `blue.ico`, etc.). This is
historical drift — at some point the convention was to prefix with
`Normal_` (and presumably have a `Transparent_<color>.ico` companion)
but the prefix was dropped before being applied to the other colors.

Future cleanup: rename `Normal_red.ico` → `red.ico` (matches the rest
of `colors/`). Deferred — touches ValveMaster's `installer.iss`
`SetupIconFile=Normal_red.ico` reference, so the rename must be
coordinated with a ValveMaster release.

## How to add a new color variant

If a future tool needs a new color (the four-color palette currently
in use is orange / green / blue / red; purple and yellow are
pre-rendered and available):

1. Have the brand designer produce the recolored logo:
   - **PNG**: same dimensions as the existing color PNGs (varies —
     `orange.png` is 214 KB; `blue.png` is 1.4 MB — large variance is
     itself a known issue, target ~250 KB at 512 × 512 for new
     additions). Transparent background. 8-bit/channel RGBA.
   - **ICO**: multi-resolution (16 / 32 / 48 / 256). Generated from
     the PNG via ImageMagick or similar.
2. Save to `colors/<color>.png` + `colors/<color>.ico`.
3. Commit on a `brand-assets/<color>` branch and PR — keeps the
   asset-add diff separate from any tool-side consumption.
4. The consuming tool copies the files into its own repo (see
   `BRANDING_ASSET_GUIDE.md` § "How to add branding for a NEW tool").

## What this folder is NOT

- **Not a runtime-bundled resource** — `phoenix_commons` does not
  ship `Design Items/` in its installed package. Tools cannot
  `from phoenix_commons.design_items import ...` (no such Python
  module exists; the folder isn't importable).
- **Not a screenshot reference** — visual references live in
  `docs/ui-platform-baseline-v1/visual-baselines/`.
- **Not the canonical color palette** — that lives in
  `src/phoenix_commons/theme/tokens.py` (and `docs/ui-platform-baseline-v1/DESIGN_SYSTEM.md`
  for prose). The files in `colors/` are the *logos* in each color,
  not the palette definitions.

## Future cleanup (deferred)

Per `BRANDING_ASSET_GUIDE.md` § "Recommended folder layout":

1. **Rename `Design Items/` → `design-assets/`** (kebab-case, no
   space) to match the rest of commons. Low-risk — nothing in
   commons code imports from this path; only the repo's own README
   mentions it.
2. **Rename `colors/Normal_red.ico` → `colors/red.ico`** — but only
   in coordination with a ValveMaster release that updates
   `installer.iss`.
3. **Rename `PTT Normal.jpg` / `PTT Transparent.jpg` / `PTT Transparent.ico`**
   to drop the misleading `PTT_` prefix. Currently no runtime
   consumer; rename is repo-only.

Track these as a `brand-assets-cleanup` issue when the operational
stabilization window closes.

## See also

- `../docs/ui-platform-baseline-v1/BRANDING_ASSET_GUIDE.md` — full
  asset audit + naming conventions + how-to guides.
- `../docs/ui-platform-baseline-v1/INSTALLER_NOTES.md` — wizard
  artwork specs (BMPs derived from these PNGs).
- `../docs/ui-platform-baseline-v1/DESIGN_SYSTEM.md` — color palette
  (the abstract tokens, not the recoloured logos).
- `../docs/ui-platform-baseline-v1/visual-baselines/README.md` — visual
  baseline of how each tool looks today.
- The PCC `assets/README.md` (in the `phoenix-command-center` repo)
  — the gold-standard example of per-folder asset documentation.
