# DEPENDENCY_GRAPH.md

> **Critical file.** Maps every coupling so the blast radius of any
> change is known before it lands. If you're about to modify
> something in this graph and the change isn't listed here, stop and
> update the graph first.

## High-level coupling

```
                        ┌────────────────────────┐
                        │  AV / S1 (environment) │
                        └────────────┬───────────┘
                                     │ gates
                                     ▼
                        ┌────────────────────────┐
                        │  PyInstaller bootloader│   ←── frozen-exe verification
                        └────────────┬───────────┘            for all apps
                                     │ depended on by
        ┌────────────────────────────┼────────────────────────────┐
        ▼                            ▼                            ▼
  ┌───────────┐              ┌─────────────┐              ┌─────────────┐
  │  PCC      │              │ Job Tracker │              │  Phoenix    │
  │  Command  │              │ Phoenix CAD │              │  CAD / Job  │
  │  Center   │              │ Checkout    │              │  Tracker    │
  │           │              │ ValveMaster │              │  (BricsCAD) │
  └─────┬─────┘              └──────┬──────┘              └──────┬──────┘
        │ depends on (today: local │ depends on (today: own       │
        │ copies; Phase 7+: commons)│ helpers; Phase 7+: commons)  │
        ▼                            ▼                            ▼
  ┌──────────────────────────────────────────────────────────────────────┐
  │                       phoenix-commons                                │
  │   theme   widgets   paths   updater    [tokens] [icons] [resources] │
  │   ✓       ✓         ✓       ✓ (3A)     (2.1)    (2.6)   (2.5)        │
  └──────────────────────────────────────────────────────────────────────┘
```

## What depends on commons today

| Consumer | What it imports | Verification status |
|----------|-----------------|---------------------|
| `phoenix-commons` own tests | `phoenix_commons.{paths,theme,widgets,updater}` | ✅ Verified (phase tests) |
| **Nothing else yet** | — | — |

PCC has **local copies** of `paths.py` and `updater.py` (the
templates the wizard generates). It does NOT yet import from
`phoenix_commons`. This is intentional — the commons-backed scaffold
variant stays non-default until frozen-exe verification clears.

## What WILL depend on commons after Phase 7+

| Consumer | What it'll import | Phase |
|----------|-------------------|-------|
| `phoenix-command-center` | `phoenix_commons.{theme,widgets,paths,updater,icons,resources}` | 7+ (after pilot proves it works) |
| `Phoenix-Checkout-Tool` | `phoenix_commons.{theme,widgets,paths,updater}` | 7 (pilot) |
| `Phoenix_CAD_Tool` | same | 7 (pilot) |
| `ValveMasterTool` | same | 8a |
| `Job Tracker` | same | 8b |
| Future scaffolded tools | All commons modules via the commons-backed wizard radio | When wizard's commons-backed becomes default (post Phase 6C verification) |

## What depends on package-data bundling

`phoenix-commons` ships these files that consumers need at runtime:

| File | Loaded by | Bundled via |
|------|-----------|-------------|
| `src/phoenix_commons/theme/phoenix_style.qss` | `apply_dark_theme(app)` | `pyproject.toml` `package-data` + PyInstaller `--collect-data phoenix_commons` (Phase 3C) |
| `src/phoenix_commons/theme/_embedded_qss.py` | `apply_dark_theme` fallback | Pure Python — bundled automatically |
| `src/phoenix_commons/icons/*.svg` (Phase 2.6) | `phoenix_commons.icons.<name>()` | Same as QSS |
| App-owned assets (`logo.ico`, `logo.png`, `watermark.png`, etc.) | `paths.resource_path("assets/...")` | App's `build.bat` via `--add-data` |

**Failure modes if package-data isn't bundled correctly:**

| Failure | Symptom |
|---------|---------|
| Commons QSS missing | App falls back to embedded fallback, logs a warning. Still themed. |
| Commons icon missing | Empty `QIcon()` returned; UI looks broken but doesn't crash. |
| App asset missing | `paths.resource_path` returns a non-existent path; `QPixmap(...)` returns null; widget renders empty. |
| Both QSS forms missing | Default Qt look — Phoenix dark navy is gone. Visible regression. |

## What depends on icons

| Consumer | What | Phase |
|----------|------|-------|
| `UpdateBanner` widget | "info" icon (currently hardcoded text glyph) | Will migrate to commons icon set when Phase 2.6 lands |
| PCC sidebar buttons | "✦", "↻", "⚙" glyphs (Unicode text today) | Could migrate to commons icons; not required |
| Production tools' status indicators | Various app-local PNGs | Stays app-local |
| App taskbar icon | Each app's `logo.ico` | Always app-local |

Icon coupling is intentionally minimal. Apps can opt out of the
commons icon set entirely and continue using Unicode glyphs or
app-local PNGs.

## What depends on QSS

Everything visual.

| Component | Coupling type |
|-----------|---------------|
| Every widget with an `objectName` | Coupled to the QSS rules selecting that name. |
| Every widget that calls `setStyleSheet(...)` | Coupled to its local QSS string. |
| Apps that call `apply_dark_theme(app)` | Coupled to the commons QSS file path + its content. |
| Apps that override commons selectors via app-local QSS | **Drift risk** — see MIGRATION_RULES.md. |

The QSS is the single largest blast-radius file. A change to a
commons selector affects every consumer simultaneously.

## What depends on updater contracts

| Consumer | Contract |
|----------|----------|
| `Job Tracker` updater | Full-folder (Contract A) |
| `Phoenix_CAD_Tool` updater | Full-folder (Contract A) |
| `Phoenix-Checkout-Tool` updater | Exe-only (Contract B) |
| `ValveMasterTool` updater | Exe-only (Contract B) |
| `phoenix-command-center` updater | Full-folder (Contract A) |
| Future scaffolded tools | Full-folder (Contract A) — wizard default |
| `phoenix_commons.updater.download_and_apply` | Both, via `expected_internal` kwarg |
| `scripts/validate_release_zip.py` | Both, via `--require-internal` flag |

**Key invariant:** the deployed installer's zip-asset shape MUST
match the updater code expectations on the deployed exe. A retrofit
that switches from B → A on a tool without a coordinated full-reinstall
deployment is a bug. See PACKAGING_CONTRACT.md §1.

## What depends on AV clearance

| Item | Why it's blocked |
|------|-------------------|
| Phase 6C frozen-exe dogfood | Bootloader gets quarantined |
| Phase 7 pilot retrofit | Can't verify the retrofitted exe |
| Phase 8 wave retrofit | Same |
| PCC v2.0.0 installer release | Can't produce a runnable installer |
| Future scaffolded apps' first build verification | Same |
| Commons-backed scaffold becoming wizard's default | Same |

**Everything frozen-exe is one single root blocker.** Cleared once,
all of these unblock.

## Migration coupling

Some retrofits must precede others because the later one depends on
the earlier one's outcome:

```
  AV gate ──┐
            ▼
      Phase 6C ──┐
                 ▼
   ┌─Phase 2.1 ──┼── tokens API stable
   │             ▼
   ├─Phase 2.2 ──┼── widget API stable
   │             ▼
   ├─Phase 2.5 ──┼── runtime-resource API stable
   │             ▼
   └─Phase 7 ────┴── pilot retrofit (Checkout + CAD)
                     │
                     ▼
                Phase 8a (ValveMaster) ──┐
                                          ▼
                                    Phase 8b (Job Tracker)
                                          │
                                          ▼
                                       Phase 9
```

You can run Phases 2.1 / 2.2 / 2.5 / 2.6 in parallel with each other
once started, but Phase 7 needs **all of them done** plus AV cleared.

## Packaging coupling

```
  build.bat
    │
    ├── PyInstaller    (depends on PyInstaller version + Python version)
    │     │
    │     └── --add-data flags    (each one couples to an app-local asset)
    │     └── --collect-data flags (Phase 3C couples to commons package-data layout)
    │     └── --collect-submodules (PySide6 internals — couples to PySide6 version)
    │
    ├── Inno Setup     (depends on Inno Setup 6 install — found via path search)
    │     │
    │     └── installer.iss    (couples to AppId GUID, install path, asset list)
    │
    ├── Compress-Archive   (PowerShell built-in — couples to PS version, but stable)
    │
    └── validate_release_zip.py    (depends on Python + zipfile stdlib only)
```

Single coupling out of the box: `build.bat` reads `version.py`
once, injects `MyAppVersion` into `installer.iss`, AND passes it to
PyInstaller via the exe metadata. Version drift between these
consumers is impossible by construction.

## Blast radius cheat-sheet

If you change… | …it affects |
---|---
A commons-owned token (`C['accent']` hex value) | Every Phoenix app's primary buttons, accent titles, glow halos. Visible across all 5 apps. |
A commons widget's `objectName` | Every QSS rule selecting that name (commons + every app's overrides). |
A commons widget's public API (kwargs, methods) | Every app that imports it. Subclasses break if signatures change. |
The commons QSS file | Every app using `apply_dark_theme`. App-local QSS additions may now conflict. |
`paths.user_data_dir` return value | User-data location for every app — including production tools post-retrofit. Could lose data on upgrade. |
`updater.download_and_apply` extraction logic | Every app on Contract A (Job Tracker, Phoenix CAD, PCC) when their next release publishes. |
`scripts/validate_release_zip.py` exit codes | Every app's `build.bat` tail validation. |
An AppId GUID in any production installer | Orphans every existing user install of that tool. **NEVER DO THIS.** |
A `<App>.zip` asset name | Breaks the auto-updater for users on the prior version. |
PCC's wizard `phoenix_tool_templates.py` | Every future scaffolded app. No retroactive effect on already-scaffolded apps. |

## Reading order for a new retrofit

If you're starting a Phase 7+ retrofit, read this file first to
understand what you're touching, then walk:

1. `MIGRATION_RULES.md` — process
2. `PACKAGING_CONTRACT.md` — checklist
3. `NAMING_REGISTRY.md` — preserve-these values
4. `PLATFORM_CONTRACT.md` — what to import, what to subclass

Then start the retrofit on its branch.
