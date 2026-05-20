# BRANDING_ASSET_GUIDE.md

> Convention for naming, sourcing, and organising brand assets across
> the Phoenix tool family. Captures the current state of the four
> production tools' brand assets (audited 2026-05-19) and the
> recommended target convention for future tools and future polish
> on existing tools.
>
> Documentation only — this file does not move or rename any
> production tool's existing assets. Every recommendation here is
> labelled "current" or "target".

## The Phoenix brand system

### Color palette (System A — locked per ADR-016)

| Token | Hex | Semantic role |
|-------|-----|---------------|
| BG | `#0a0e27` | App background — universal across every Phoenix tool |
| SURFACE | `#141829` | Cards, panels, dialogs — universal |
| TEXT | `#ffffff` | Primary text — universal |
| MUTED | `#9ca3af` | Secondary text — universal |
| PRIMARY (brand slot 1) | `#dc2626` (red) | Primary action buttons. Overridable per tool via `BrandProfile` — see ADR-016. |
| SECONDARY (brand slot 2) | `#1e3a8a` (deep blue) | Secondary actions, secondary buttons. Overridable. |
| ACCENT (brand slot 3) | `#3b82f6` (blue) | Focus rings, hyperlinks, highlight. Overridable. |
| Status colours (success / warn / error) | green / amber / red | Universal, not overridable. |

The "background / surface / text / muted / status" tokens are
**universal** — they don't change per tool. The "primary / secondary /
accent" tokens are the three slots a tool's `BrandProfile` can
override (subject to ADR-016 constraints).

### App-color logos (the "four colors" pattern)

Each production tool ships with a color-variant of the same base
Phoenix logo:

| Tool | Color | Source-of-truth file in commons |
|------|-------|----------------------------------|
| Phoenix CAD (Lab Layout Tool) | **orange** | `Design Items/colors/orange.png` + `Design Items/colors/orange.ico` |
| Phoenix Checkout (Phoenix Valve Checkout Tool) | **green** | `Design Items/colors/green.png` + `Design Items/colors/green.ico` |
| Job Tracker (Project Tracking Tool) | **blue** | `Design Items/colors/blue.png` + `Design Items/colors/blue.ico` |
| ValveMaster (Valve Master Tool) | **red** | `Design Items/colors/red.png` + `Design Items/colors/Normal_red.ico` |

Each production tool has a copy of its color variant in its own repo
root (because PyInstaller can't `--add-data` from a sibling repo).
Hash-verified 2026-05-19: each tool's tracked PNG/ICO is byte-identical
to the corresponding `Design Items/colors/<color>.{png,ico}` file in
commons (the one exception is ValveMaster's `Transparent_red.png`
which is 215,115 B vs commons's `red.png` at 214,472 B — slight content
divergence; cause unknown).

### Logo style (transparent variants)

The "transparent" variants used as background watermarks in
runtime are the same color logo at very low opacity (~12%) overlaid
behind the work surface. Each tool wires its own watermark widget
that loads `<color>.png` (or the legacy aliases) via
`_resource_path()`.

PCC has a more polished watermark — `assets/watermark.png` at 512 × 512
with 18% alpha pre-applied to the source. The production tools apply
the opacity at render time instead.

## Current asset inventory (audited 2026-05-19)

### phoenix-command-center

| Path | Size | Purpose |
|------|------|---------|
| `assets/logo.png` | 52 KB | 256 × 256 transparent PNG (placeholder generated from sidebar sprite frame 0) |
| `assets/logo.ico` | 87 KB | Multi-resolution ICO (16/32/48/64/128/256) — placeholder |
| `assets/watermark.png` | 151 KB | 512 × 512, ~18% opacity logo |
| `assets/ats_automation_stable_transparent.webp` | 2.0 MB | Animated sidebar sprite (corporate ATS Automation animated logo) |
| `assets/ats_automation_stable_transparent.apng` | 2.5 MB | APNG source for the WebP above (regeneration source) |
| `assets/README.md` | 4.4 KB | **Excellent reference for how assets/ folders should be documented.** Specifies dimensions, consumers, regeneration steps. |

PCC is the **gold standard** for asset organisation. The other tools
should aspire to this layout.

### phoenix-commons

| Path | Size | Purpose |
|------|------|---------|
| `Design Items/PTT Normal.jpg` | 270 KB | Large brand source (not used at runtime) |
| `Design Items/PTT Transparent.jpg` | 367 KB | Large brand source |
| `Design Items/PTT Transparent.ico` | 4.2 KB | Possible installer icon source |
| `Design Items/colors/<color>.png` × 6 | 200 KB – 1.4 MB | Color-variant logos (production-tool source-of-truth) |
| `Design Items/colors/<color>.ico` × 6 | 2 – 4 KB | Color-variant icons |
| `Design Items/colors/Normal_red.ico` | 4.2 KB | ValveMaster's icon source |
| `src/phoenix_commons/icons/lucide/*.svg` × 10 | tiny | UI control icons (check, info, plus, refresh, save, search, settings, trash, warning, x) — packaged via `phoenix_commons.icons` |

**Issues with the current layout:**

- Folder name `Design Items` uses capitalisation and a space; every
  other folder in commons is lowercase / kebab-case / snake_case.
- `PTT Normal.jpg` and `PTT Transparent.jpg` have spaces in filenames
  (cross-platform friction).
- The `colors/` folder mixes naming styles: `green.ico` (lowercase) vs
  `Normal_red.ico` (capitalised + prefixed). Probably a historical
  artifact — at some point the convention was `Normal_<color>.ico`
  but only red kept that form.

### Production tools (4 of 4)

| Tool | Tracked brand files at repo root |
|------|-----------------------------------|
| Phoenix CAD | `LLT_Normal.ico`, `LLT_Transparent.png` |
| Phoenix Checkout | `PTT_Normal_green.ico`, `green.png` |
| Job Tracker | `PTT_Normal.ico`, `PTT_Transparent.png` |
| ValveMaster | `Normal_red.ico`, `Transparent_red.png` |

**Issues:**

- **No `assets/` folder.** Brand files live at repo root, mixed in
  with Python source and build scripts.
- **Naming chaos** (see § "Outstanding naming inconsistencies" below).
- **No installer wizard artwork** — see `INSTALLER_NOTES.md` § "Wizard artwork".
- **Phoenix Checkout's code references a non-existent file:**
  `checkout_tool_gui.py:500` falls back to `PTT_Transparent_green.png`
  if `green.png` isn't found. The fallback path is dead code (file
  doesn't exist in the repo) — historical artifact of an aborted
  rename. Cleanup candidate, not blocking.

## Outstanding naming inconsistencies

These are real divergences in production today. Future renames
**must** be coordinated with `build.bat` (`--add-data=` lines) and
runtime code (`_resource_path()` calls) — see § "How to rename an
asset safely" below.

| Tool | Issue | Recommended target name |
|------|-------|--------------------------|
| Phoenix Checkout | `PTT_Normal_green.ico` — the `PTT_` prefix is misleading. PTT stands for "Project Tracking Tool" (Job Tracker), not Phoenix Checkout. | `Checkout_Normal_green.ico` (or `Checkout.ico` if dropping the variant suffix) |
| Phoenix Checkout | `green.png` has no app prefix and no `Transparent` / `Normal` discriminator. | `Checkout_Transparent_green.png` |
| Phoenix CAD | `LLT_*` prefix is fine (LLT = Lab Layout Tool). Consistent within the tool. | Keep — no change needed. |
| Job Tracker | `PTT_*` prefix is fine (PTT = Project Tracking Tool). Consistent. | Keep. |
| ValveMaster | No app prefix at all — `Normal_red.ico`, `Transparent_red.png`. | `VMT_Normal_red.ico`, `VMT_Transparent_red.png` (or `VM_*` if shortening). |
| commons | `Design Items/` folder name has space + capitalisation. Diverges from rest of commons. | `design-assets/` (kebab-case) or `brand-assets/`. |
| commons | `Design Items/colors/Normal_red.ico` is the only ICO with a `Normal_` prefix. | Drop the prefix → `red.ico` (matches `green.ico`, `blue.ico`, `orange.ico`). |

**All of these renames are deferred** — they require coordinated
changes to `build.bat`, `installer.iss`, and any `_resource_path()`
call. Track in each tool's `docs/` for future polish PR.

## Recommended folder layout (target)

For each production tool's repo:

```
<tool-repo>/
├── assets/                         ← all brand + UI assets
│   ├── README.md                   ← document every file (PCC's `assets/README.md` is the template)
│   ├── icon.ico                    ← Inno Setup `SetupIconFile`, PyInstaller `--icon=`
│   ├── icon.png                    ← 256×256 source, About dialog
│   └── watermark.png               ← Faint background mark (optional)
├── installer-assets/               ← Inno Setup only (NOT bundled into exe)
│   ├── wizard.bmp                  ← 164×314, dark navy with color logo
│   └── wizard-small.bmp            ← 55×58, color logo
└── ...
```

The split between `assets/` (runtime-bundled) and `installer-assets/`
(installer-only) makes the `build.bat` `--add-data=` list smaller and
the installer's footprint smaller (the wizard BMPs don't need to ship
inside `_internal/`).

## How to rename an asset safely

Renaming a tracked brand asset in a production tool touches three
places:

1. **`build.bat`** — every `--add-data="<old>;..."` line for that file.
2. **`installer.iss`** — `SetupIconFile=<old>`, possibly `[Files]`
   entries if the asset is referenced there.
3. **Runtime code** — every `_resource_path("<old>")` call. Run a
   grep to find them all.

Procedure for a single asset rename:

```bash
cd <tool-repo>
git checkout -b rename-<asset-old>-to-<asset-new>

# 1. Rename in the working tree (preserving git history)
git mv <old-name> <new-name>

# 2. Update build.bat
# 3. Update installer.iss
# 4. Update runtime code (grep -rn '<old-name>' --include='*.py')

# 5. Verify
python -m compileall -q .
python <entry-script>.py    # source-mode launch must still work

# 6. Run the full pre-release checklist before merging
```

**Do not rename multiple assets in the same PR** — keeps the diff
auditable and the bisect-on-regression manageable.

## How to add branding for a NEW tool

When scaffolding a new Phoenix tool (via the Command Center wizard
or manually), follow this checklist:

1. **Pick a color** — orange, green, blue, red are taken. Available:
   purple, yellow (already in commons `Design Items/colors/`). Or
   commission a new color variant.
2. **Copy the source-of-truth files** from
   `phoenix-commons/Design Items/colors/<color>.{png,ico}` into the
   new tool's `assets/` folder. Rename to `icon.png` and `icon.ico`
   (PCC convention) — or `<ToolSlug>_Normal_<color>.ico` and
   `<ToolSlug>_Transparent_<color>.png` if you want to follow the
   production-tool pattern.
3. **Wire `build.bat`**: `--add-data="assets\icon.ico;assets"` (or
   the equivalent for the chosen layout).
4. **Wire `installer.iss`**: `SetupIconFile=assets\icon.ico`.
5. **Wire runtime code**: `_resource_path("assets/icon.ico")` for
   the window icon, etc.
6. **Add an `assets/README.md`** — copy PCC's verbatim and edit.

## Organization names — "ATS Inc" vs "ATS Automation"

Audited 2026-05-19:

| Repo | Organization name in LICENSE |
|------|-------------------------------|
| phoenix-command-center | **ATS Automation** |
| phoenix-commons | **ATS Automation** |
| Phoenix_CAD_Tool | **ATS Inc** |
| Phoenix-Checkout-Tool | **ATS Inc** |
| Job Tracker | **ATS Inc** |
| ValveMasterTool | **ATS Inc** |

The user-data root (`%APPDATA%\ATS Inc\<App>\`) and install root
(`{localappdata}\ATS Inc\<App>\`) are **always** `ATS Inc` on every
production tool. Changing the publisher namespace would orphan
existing installs, so this stays.

The LICENSE divergence reflects which entity formally holds the
copyright — `ATS Automation` is the parent operating brand, `ATS Inc`
is the legal entity. Both are valid; the docs going forward should
prefer **ATS Inc** for legal/copyright contexts and **ATS Automation**
(or **Phoenix Controls** for tool branding) for prose / UI / marketing.

PCC's and commons' LICENSE files were authored 2026 and use
`ATS Automation`; the production tools predate that and use `ATS Inc`.
Recommendation: **leave each tool's LICENSE alone** until a release
cycle requires touching it. When touching, normalise to `ATS Inc` for
copyright lines.

## See also

- `RELEASE_CHECKLIST.md` — release procedure (assets are part of the
  installer step).
- `INSTALLER_NOTES.md` — wizard artwork specifications.
- `DESIGN_SYSTEM.md` — full color palette + token definitions.
- `ADR_PCC_PALETTE_RECONCILIATION.md` (ADR-016) — BrandProfile mechanism.
- PCC's `assets/README.md` — the gold standard for per-tool asset
  documentation.
