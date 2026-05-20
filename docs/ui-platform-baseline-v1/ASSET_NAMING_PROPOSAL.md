# ASSET_NAMING_PROPOSAL.md

> Future-polish roadmap for normalising brand-asset naming across the
> Phoenix tool family. **No runtime renames are performed by this
> document** — it captures the proposed convention, migration
> strategy, and compatibility concerns so a future release-prep PR
> can execute the renames cleanly.
>
> Authored 2026-05-19 during the Operational Hardening Sprint.
> Companion to `BRANDING_ASSET_GUIDE.md` (current state) and
> `Design Items/README.md` (commons-side source inventory).

## Why this needs to happen

Brand-asset naming drifted across the four production tools (and the
commons source folder) over their independent development histories.
Drift symptoms documented in `OPERATIONAL_STABILIZATION_REPORT_01.md`
§ 1.3:

1. **`PTT_Normal_green.ico`** in Phoenix Checkout — the `PTT_` prefix
   suggests "Project Tracking Tool" (= Job Tracker), but this is a
   Phoenix Checkout asset. Misleading for anyone scanning the repo.
2. **`green.png`** in Phoenix Checkout — no app prefix, no
   "Transparent" / "Normal" discriminator (unlike every other tool's
   variant filenames).
3. **Dead-code fallback** at `checkout_tool_gui.py:500` to
   non-existent `PTT_Transparent_green.png` — historical artifact of
   an aborted rename.
4. **ValveMaster** (now Phoenix Master Tool) has no app prefix:
   `Normal_red.ico`, `Transparent_red.png`. The rename to "Phoenix
   Master Tool" landed in v1.1.0 but the asset filenames weren't
   updated.
5. **commons `Design Items/`** folder name uses capitalisation +
   space — diverges from every other commons folder (lowercase /
   kebab-case / snake_case).
6. **commons `Design Items/colors/Normal_red.ico`** is the only ICO
   in `colors/` with a `Normal_` prefix; all others are bare-colour
   (`green.ico`, `blue.ico`, `orange.ico`).
7. **commons `Design Items/PTT Normal.jpg` / `PTT Transparent.jpg`**
   use the misleading `PTT_` prefix for generic Phoenix brand
   sources, not PTT-specific assets.

Each rename, taken individually, is trivial. The cost is in
**coordination**: every rename touches `build.bat` (`--add-data=`
lines), `installer.iss` (`SetupIconFile=` references), and runtime
code (`_resource_path()` calls). A coordinated rename PR must
land all three pieces atomically per tool.

## Proposed naming convention

The convention proposed below applies to **new** Phoenix tools and
to **opportunistic renames** in existing tools (carried in the same
PR as another tool-specific change).

### Filename format

```
<ToolSlug>_<Variant>_<Color>.<ext>
```

| Segment | Definition | Example |
|---------|------------|---------|
| `<ToolSlug>` | The PascalCase short identifier of the tool, mirroring the executable name without its extension | `LLT`, `Checkout`, `PTT`, `PMT`, `PCC` |
| `<Variant>` | `Normal` for the opaque-background ICO; `Transparent` for the alpha-channel PNG used as a watermark or About-dialog logo | `Normal`, `Transparent` |
| `<Color>` | The lowercase brand color | `orange`, `green`, `blue`, `red`, `purple` |
| `<ext>` | `ico` for the Normal variant; `png` for the Transparent variant | `ico`, `png` |

Examples:

- `LLT_Normal_orange.ico` (Phoenix CAD / Lab Layout Tool)
- `Checkout_Transparent_green.png`
- `PTT_Normal_blue.ico` (Job Tracker / Project Tracking Tool)
- `PMT_Transparent_red.png` (Phoenix Master Tool, formerly ValveMaster)

### Tool-slug map

| Display name | Slug |
|--------------|------|
| Lab Layout Tool | `LLT` |
| Phoenix Valve Checkout Tool | `Checkout` |
| Project Tracking Tool | `PTT` |
| Phoenix Master Tool | `PMT` |
| Phoenix Command Center | `PCC` |

Future tools pick a slug at creation time and document it in their
`assets/README.md`.

### Folder layout (per tool repo)

```
<tool-repo>/
├── assets/
│   ├── README.md
│   ├── <ToolSlug>_Normal_<color>.ico
│   ├── <ToolSlug>_Transparent_<color>.png
│   └── (optional) watermark.png
├── installer-assets/                ← Inno Setup only, NOT bundled into exe
│   ├── wizard.bmp                   ← 164×314, when ready
│   └── wizard-small.bmp             ← 55×58, when ready
└── ...
```

PCC's existing `assets/` folder is the gold standard reference.

### commons source folder

| Current | Proposed |
|---------|----------|
| `Design Items/` | `design-assets/` (kebab-case) OR keep `Design Items/` if rename risk outweighs benefit |
| `Design Items/PTT Normal.jpg` | `design-assets/Phoenix-logo-normal.jpg` (drop misleading `PTT_` prefix) |
| `Design Items/PTT Transparent.jpg` | `design-assets/Phoenix-logo-transparent.jpg` |
| `Design Items/PTT Transparent.ico` | `design-assets/Phoenix-logo-transparent.ico` |
| `Design Items/colors/Normal_red.ico` | `design-assets/colors/red.ico` (drop `Normal_` prefix; match siblings) |
| `Design Items/colors/<color>.{png,ico}` | `design-assets/colors/<color>.{png,ico}` (unchanged) |

## Migration strategy

Each tool's rename is its own PR. **Never bundle multiple tools'
renames into the same PR** — it bloats the diff and makes a regression
harder to bisect.

### Per-tool rename PR template

For tool `<X>` with current asset `<old>` → proposed `<new>`:

1. **Branch**: `rename-assets-<x>` off `main` (or `master` for tools
   on that name).

2. **Rename** the files via `git mv`:
   ```bash
   git mv <old.ico> assets/<new.ico>
   git mv <old.png> assets/<new.png>
   ```
   Uses `assets/` if the tool is migrating to the new layout; keeps
   repo-root if the tool isn't ready for the layout migration yet.

3. **Update `build.bat`**:
   ```diff
   - --add-data="<old.ico>;." ^
   - --add-data="<old.png>;." ^
   + --add-data="assets/<new.ico>;assets" ^
   + --add-data="assets/<new.png>;assets" ^
   ```

4. **Update `installer.iss`**:
   ```diff
   - SetupIconFile=<old.ico>
   + SetupIconFile=assets/<new.ico>
   ```

5. **Update runtime `_resource_path()` calls** — grep the codebase:
   ```bash
   git grep -nE '<old\.(ico|png)>' -- '*.py'
   ```
   Update every match. Be careful with fallback chains (e.g. Phoenix
   Checkout's `for _name in ("green.png", "PTT_Transparent_green.png"):`
   — drop the dead fallback path while renaming).

6. **Verify**:
   ```bash
   python -m compileall -q .
   python <entry-script>.py   # source-mode launch must succeed
   ```

7. **Update the tool's CHANGELOG.md** with a `### Changed` entry
   under `[Unreleased]`.

8. **Open the PR**. Use `RETROFIT_PR_TEMPLATE.md`-style structure.
   Reviewer checks: source-mode launch, identity of the rendered
   icon in the title bar, identity of the installer icon in the
   Setup.exe.

### Per-tool execution order

Recommended order (least visible / least risky first):

1. **Phoenix CAD** (`LLT_*` → already correctly prefixed) — only
   needs the layout migration to `assets/` if the team wants to
   modernise. Lowest-risk; nothing surprising in the diff.
2. **Job Tracker** (`PTT_*` → already correctly prefixed) — same
   as Phoenix CAD; only layout migration if desired.
3. **Phoenix Checkout** (`PTT_Normal_green.ico` → `Checkout_Normal_green.ico`,
   `green.png` → `Checkout_Transparent_green.png`) — the
   highest-impact rename because the prefix is actively misleading.
   Also drop the dead-code fallback in `checkout_tool_gui.py:500`.
4. **Phoenix Master Tool** (`Normal_red.ico` → `PMT_Normal_red.ico`,
   `Transparent_red.png` → `PMT_Transparent_red.png`) — completes
   the v1.1.0 rename's asset-side work. Coordinate with the
   `installer.iss SetupIconFile=` change carefully.
5. **commons `Design Items/` rename** — last, because every consuming
   tool's documentation references the `Design Items/colors/` path.
   When commons folder renames, update every doc cross-reference in
   the same PR.

### Compatibility concerns

| Concern | Risk | Mitigation |
|---------|------|------------|
| **Auto-updater asset filename** | Auto-updater looks for `<ExeName>.zip` (not the icon filename), so renames of `.ico` / `.png` files do NOT affect the updater contract. | None needed — the auto-updater is downstream of the rename. |
| **Inno Setup `SetupIconFile` change after a tool has shipped** | The exe icon in Add/Remove Programs comes from the embedded resource (PyInstaller embeds the ICO at build time). Renaming the source file does not change the embedded resource. | Verify by running the renamed installer in a VM that has the previous version; confirm the Add/Remove Programs icon updates correctly. |
| **PyInstaller `--icon=<path>` reference** | If `build.bat` uses `--icon=<old.ico>`, the rename breaks the build until `build.bat` is updated. | Update `build.bat` in the same commit as the rename. CI catches this. |
| **Runtime watermark / About-dialog logo** | Tools that hardcode `_resource_path("<old.png>")` will fail at runtime after the rename if not updated. | Update every reference in the same commit. Source-mode launch verification per MIGRATION_RULES.md § 10 row 11 catches this. |
| **Production-tool repos with stale local clones** | Justin's local dev workspaces may have local .venv files that reference the old paths. | Each rename PR's `git mv` is detected as a rename (not an add+delete) so existing clones see the file move cleanly on `git pull`. |
| **GitHub Release asset names** | Release assets (`<ExeName>.zip`, `<ExeName>Setup.exe`) are NOT affected by icon-file renames. | None needed. |
| **Existing installer behaviour during upgrade** | Inno Setup's upgrade is identity-keyed by `AppId` + install path; the icon source path is not part of the identity. | Verified safe by Phoenix CAD's Phase 3A precedent (which renamed embedded QSS path during retrofit without breaking upgrades). |

## Rollout plan

This proposal does NOT mandate a timeline. Renames execute
opportunistically — bundled into whatever PR a tool's next release
includes, OR as standalone PRs when a maintainer chooses.

Suggested cadence:

1. **No proactive renames during the current operational stabilization
   window** (this is the explicit STOP at the end of this sprint).
2. **Phoenix Checkout rename** — natural rider on the next Checkout
   release that fixes a bug or adds a feature. The misleading `PTT_`
   prefix is the highest-priority single fix.
3. **Phoenix Master Tool rename** — natural rider on the next PMT
   release; coordinates with the v1.1.0 rename already done.
4. **Phoenix CAD layout migration** — when a Phoenix CAD PR touches
   `build.bat` or `installer.iss` for other reasons, fold in the
   `assets/` layout move.
5. **Job Tracker layout migration** — same opportunistic approach.
6. **commons `Design Items/` rename** — last. Affects every
   downstream doc; benefits are smallest because nothing imports
   from this path at runtime.

## Out of scope for this proposal

- **Wizard artwork** (Inno Setup `WizardImageFile` BMPs) — separate
  brand-design commission. Specs documented in `INSTALLER_NOTES.md`.
- **Re-rendering the source logos** at different dimensions or
  colours — brand-design work, not a naming convention issue.
- **New tools' asset checklist** — covered in `BRANDING_ASSET_GUIDE.md`
  § "How to add branding for a NEW tool".
- **Code-signing certificates** — see `INSTALLER_NOTES.md` § "Code signing".

## Cross-references

- `BRANDING_ASSET_GUIDE.md` — current state of all brand assets
  (audited 2026-05-19) + the "four colors" pattern.
- `Design Items/README.md` (in commons repo root, not docs/) —
  per-folder inventory of the brand-asset sources.
- `INSTALLER_NOTES.md` — Inno Setup conventions, wizard artwork
  specs.
- `OPERATIONAL_STABILIZATION_REPORT_01.md` — original audit findings
  that motivated this proposal.
- `MIGRATION_RULES.md` § 10 row 11 — source-mode launch as the
  release gate after any rename.
- PCC's `assets/README.md` — the gold-standard reference for a
  per-tool asset folder.
