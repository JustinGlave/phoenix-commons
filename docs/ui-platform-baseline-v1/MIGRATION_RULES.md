# MIGRATION_RULES.md

> The rules of safe migration. Every retrofit (Phase 3A, 3B, 3C, 8a,
> 8b) follows this document. Anything not explicitly permitted here
> is forbidden.
>
> Updated 2026-05-19 with codified doctrine from the Phase 3A
> Phoenix CAD pilot (`PHASE_3A_PHOENIX_CAD_REPORT.md`,
> `PHASE_3A_POST_REVIEW_REPORT.md`). The retrofit-doctrine section
> below is the canonical "how to do a retrofit" reference.

## Migration order

Actual ordering (Phase 3A pilot proved single-tool retrofits scale —
the original "two tools at once" framing was relaxed):

| Phase | Tool | Branch name | Status |
|-------|------|-------------|--------|
| **3A** | Phoenix CAD Tool (Lab Layout Tool) | `phase-3a-phoenix-cad-retrofit` | ✅ Landed 2026-05-19 (awaiting merge approval) |
| **3B** | Phoenix Checkout Tool | `phase-3b-phoenix-checkout-retrofit` | Not started — gated by Phase 3A merge + user approval |
| **3C** | Phoenix Command Center | `phase-3c-pcc-retrofit` | Not started — gated by Phase 3A merge + PCC palette ADR implementation (ADR-016 mechanism is ready in commons; PCC just registers its BrandProfile) |
| **8a** | ValveMasterTool | `phase-8a-valvemaster-retrofit` | Not started — System B → A visible-theme swap |
| **8b** | Job Tracker (Project Tracking Tool) | `phase-8b-job-tracker-retrofit` | Not started — largest surface; `starter_package/` deletion in same PR |

The Phase 3A pilot deliberately retrofitted **one tool** rather than
two, against the earlier "pilot batch of two" framing. Rationale,
documented retrospectively in `PHASE_3A_PHOENIX_CAD_REPORT.md`:

- Phoenix CAD is the source of the canonical commons widgets — its
  retrofit is the lowest-risk possible first move; doing it alone
  surfaces the retrofit workflow without confounding it with a
  second tool's specifics.
- Phoenix Checkout's monolithic `checkout_tool_gui.py` (177 KB,
  per `production-inventory.md`) is the heavier lift; benefits from
  applying Phoenix CAD's proven facade pattern after Phase 3A merges.

## Pilot migration policy

Phase 3A served as the pilot. Phase 3B (Phoenix Checkout) and beyond
are no longer "pilot batch" — they're single-tool retrofits applying
the **Phase 3A retrofit doctrine** (next section). Each retrofit:

1. Branches from the tool's `master`/`main` at a clean baseline.
2. Lands as its own PR with the canonical retrofit-PR structure
   (see `RETROFIT_PR_TEMPLATE.md`).
3. Includes its own post-retrofit report — `PHASE_<id>_<tool>_REPORT.md`
   in this directory, structured per `PHASE_3A_PHOENIX_CAD_REPORT.md`.
4. Does not start until the previous retrofit has either merged OR
   been explicitly cleared not to block.

## Phase 3A retrofit doctrine — the canonical pattern

This section codifies what worked in the Phase 3A Phoenix CAD pilot.
Every subsequent retrofit (3B onward) follows this pattern unless an
explicit deviation is approved.

### 1. Local facade strategy

Each retrofitted subsystem stays as a **local file** in the consuming
app, with internals that delegate to commons. The local file
preserves the entire caller-side import surface, so no business-logic
file (e.g. `app.py`, `main_window.py`, domain modules) needs editing.

Concrete shapes observed in Phoenix CAD:

| Local file | Pre-retrofit | Post-retrofit |
|-----------|--------------|---------------|
| `paths.py` | Self-contained — `is_frozen` + path constants + helpers | Imports `is_frozen` from commons; keeps app-specific path constants and source-mode policy locally |
| `updater.py` | ~350 lines duplicating commons | ~100-line facade — 4 config constants + 2 wrapper functions |
| `ui/style.py` | ~800 lines with hand-maintained `_EMBEDDED_QSS` | ~55-line shim — `apply_dark_theme` re-export + `_resource_path` for app-local assets |
| `ui/components.py` | ~640 lines with full widget catalog | ~460 lines — commons re-exports + app-specific dialogs only |

Why local facades over direct commons imports at every call site:

- Caller-side imports (e.g. `from ui.style import apply_dark_theme`)
  don't change — business-logic files stay untouched.
- App-specific configuration (GitHub owner/repo, app-local asset
  paths, source-mode policy) lives where it belongs (in the app).
- The retrofit PR's diff is concentrated in the platform-helper
  files; reviewers can audit ~5 small files instead of every call site.

### 2. Identity-equal widget verification

For every commons widget the retrofit adopts, a smoke-test assert:

```python
ui.components.PrimaryButton  is  phoenix_commons.widgets.PrimaryButton  # True
ui.components.Panel          is  phoenix_commons.widgets.Panel          # True
```

`is` (not `==`) — the local re-export must be the **same Python class
object** as the commons class. This catches the failure mode where a
retrofit accidentally re-defines a class instead of re-exporting it.
Pre-Phase-3B / 3C / 8 retrofits include this check in their post-
retrofit validation step.

### 3. Sentinel substitution workflow (BrandProfile)

The canonical QSS (`phoenix_commons/theme/phoenix_style.qss`) carries
three sentinel tokens for the brand-profile slots:
`__BRAND_PRIMARY__`, `__BRAND_SECONDARY__`, `__BRAND_ACCENT__`.

`apply_dark_theme(app, brand=None)` substitutes them at apply time
against the active `BrandProfile`. Apps that pass no `brand=` kwarg
get `DEFAULT_BRAND` (commons canonical red + deep blue + blue).

Per ADR-016, locked tokens (BG, SURFACE, TEXT, MUTED, status colours)
stay as literal hex in the QSS — they're universal across every
Phoenix tool.

Tooling consequences:

- **Editing the canonical QSS** (under commons) is the only way to
  change locked tokens. Apps cannot override at runtime.
- **Adding a fourth brand slot** requires a new ADR superseding
  ADR-016 — the closed slot list is intentional.
- **A rare edge case**: one `rgba(30, 58, 138, 220)` literal at QSS
  line 665 (UpdateBanner background) is SECONDARY in rgba form. Not
  cleanly sentinelizable in the current pipeline; brand-override apps
  see one surface render in canonical SECONDARY. Acceptable; flagged
  for PCC retrofit consideration.

### 4. Submodule initialization expectations

Every retrofitted app inherits a `commons/` git submodule per
ADR-015. Three operational requirements:

1. **`requirements.txt` includes `-e ./commons`.**
2. **`build.bat` preflights the submodule** — fails loudly with an
   actionable error if `commons/src/phoenix_commons/__init__.py` is
   missing or `import phoenix_commons` fails from the venv.
3. **CI checks out submodules recursively.** `actions/checkout` step
   uses `with: submodules: recursive`. CI also runs `python -c "import
   phoenix_commons; print(phoenix_commons.__version__)"` as a smoke
   check that the install resolved.

Fresh-clone procedure for any retrofitted tool:

```bash
git clone <tool-repo>
cd <tool-repo>
git submodule update --init --recursive
.venv/Scripts/pip install -r requirements.txt
```

### 5. Duplicate-removal sequencing

Delete locally-defined platform code **only after the replacement
path is proven green**. The Phase 3A sequence:

1. Add commons submodule + editable install. ✅ Verify
   `import phoenix_commons` works.
2. Retrofit one subsystem (e.g. `paths.py` → facade). ✅ Verify
   imports + behaviour preserved.
3. Move to next subsystem. ✅ Verify.
4. ... etc.
5. Only at the end — once every subsystem is on commons — delete
   anything that was just commons-duplicate (the `_EMBEDDED_QSS`
   body, the heavy updater implementation, the `tools/embed_qss.py`
   helper, etc.).

Never delete and replace in the same commit. Always: replace,
verify, then delete-with-evidence.

### 6. "Delete duplication, not behaviour"

Two failure modes the doctrine forbids:

- **Behavioral regression for the sake of consumption.** If commons's
  API does subtly different things than the local helper (e.g.
  Phoenix CAD's `_resolve_user_data` returns repo root in source
  mode; commons's `user_data_dir` always returns `%APPDATA%`), the
  app KEEPS its local behaviour. The retrofit consumes only what
  cleanly matches.
- **Cleanup of unrelated code "while we're here."** A retrofit
  doesn't refactor business logic, doesn't rename variables, doesn't
  modernise idioms. Purely: remove platform-duplicate code, replace
  with commons calls, preserve behaviour.

### 7. Drift-vs-extension heuristic

(Section below — already canonical, cross-referenced from this
doctrine section.)

For Phase 3A's specific judgment calls:

| Local code | Drift or extension? | Why |
|------------|---------------------|-----|
| `paths._resolve_user_data` — source-mode → repo root | **Extension** | Phoenix CAD's intentional source-mode policy; differs from commons's default; uses commons primitive (`is_frozen`) |
| `paths.JOBS_DIR` / `BLOCKS_DIR` / etc. | **Extension** | App-local path constants composing on commons |
| `ui.style._resource_path` for `LLT_Normal.ico` | **Extension** | App-local asset resolution; commons resources go through commons API |
| `WelcomeDialog` / `PreferencesDialog` / `JobBrowserDialog` | **Extension** | App-specific UX composing commons primitives |
| Anywhere business logic touches color hex directly | **Drift** | Use tokens; if not available, propose a commons PR |
| Hand-maintained QSS in an app | **Drift** | Use commons's canonical QSS |

### 8. Commit granularity expectations

Retrofit PRs use **many small logical commits**, not one giant
mono-commit. The Phase 3A pattern was 7 commits:

| # | What | Phoenix CAD example |
|---|------|---------------------|
| B1 | Submodule + editable install + `requirements.txt` | `6770cee` |
| B2 | Retrofit one platform helper (paths) | `b4fd625` |
| B3 | Retrofit another (updater) | `461687f` |
| B4 | Retrofit theme load | `ed1de8d` |
| B5 | Retrofit widgets | `dd53be2` |
| B6 | Preserve legacy QSS + delete repo-root | `7f08ad6` |
| B7 | Update `build.bat` + delete `embed_qss` | `2b040fc` |

Plus commons-side enabling work as separate commits in `phoenix-commons`
(Phase 3A had 3 — BrandProfile mechanism / sentinel substitution / doc
update).

Each commit independently passes `compileall` + `pytest` (commons-side)
+ source-mode smoke (tool-side). PR review can bisect.

### 9. Pre-flight WIP isolation procedure

If a tool's working tree has unfinished feature work when a retrofit
is approved, the retrofit blocks until the WIP is isolated. Phase 3A's
exact procedure (user-approved Option 3):

1. `git checkout -b feature/<feature-slug>` from the dirty `master`.
2. Stage + commit the WIP files with an honest "WIP: park <feature>
   before retrofit" message.
3. `git push -u origin feature/<feature-slug>` — WIP is now safe on
   remote.
4. `git checkout master` (or `main`).
5. `git reset --hard origin/master` (DESTRUCTIVE — requires user
   approval).
6. `git checkout -b phase-<id>-<tool>-retrofit` — the actual retrofit
   branch.
7. `git push -u origin phase-<id>-<tool>-retrofit`.

After the retrofit lands, the feature branch is resumed normally —
either rebased onto the post-retrofit `master`, or merged separately.

### 10. Source-mode validation checklist

Every retrofit's final-validation step exercises (minimum):

| # | Check | Pass criterion |
|---|-------|----------------|
| 1 | `compileall -q -x "commons\|build\|dist\|\.venv" .` | Exit 0 |
| 2 | `python -c "import paths, updater, ui.style, ui.components, ui.<other>"` | No errors |
| 3 | `ui.components.<WidgetClass> is phoenix_commons.widgets.<WidgetClass>` | True (identity check) |
| 4 | Updater config constants preserved | Match pre-retrofit values |
| 5 | `inspect.getsource(updater.download_and_apply)` contains the expected `expected_internal=<True/False>` | Match tool's payload contract |
| 6 | `paths.<APP_CONSTANT>` resolves to the expected path | Match pre-retrofit value |
| 7 | `QT_QPA_PLATFORM=offscreen` apply_dark_theme + widget construction | No exceptions; styleSheet substantial; default-brand hex present; sentinels absent |
| 8 | `QT_QPA_PLATFORM=offscreen python -c "import app"` | No exceptions (exercises every transitive import) |
| 9 | `git -C commons rev-parse HEAD == git -C <commons-parent> rev-parse main` | Submodule pinned to commons main HEAD (or an intentional older SHA — document if so) |
| 10 | Commons-side `pytest -q tests/` | All tests pass (no regressions from retrofit-enabling commons changes) |

Any failing row = retrofit blocks merge.

## Rollback policy

## Rollback policy

| Failure during retrofit | Action |
|--------------------------|--------|
| Compileall or pytest fails on the retrofit branch | Fix on the branch; do not merge. |
| Frozen-exe build fails in a way that AV explains | Mark Partial; consult `BLOCKERS.md`. |
| Installed exe fails to launch | Revert the retrofit branch; investigate; re-attempt as a new PR. |
| User-data loss reproduced on upgrade | **Hard stop.** Revert immediately. Patch `paths.user_data_dir` or migration code; do not retry until cause confirmed. |
| Theme regression discovered post-merge | Hotfix release with the legacy QSS dropped back in as app-local file; retrofit re-attempted later. |

A retrofit PR is **always revertable as a single git revert**. This
is non-negotiable. If a retrofit needs more than one commit, squash
them in the PR before merge.

## Screenshot baseline requirements

Each retrofit PR includes **before + after** screenshots of:

- The app's main window (centered, default size).
- Any dialog the retrofit visibly affects (Settings, About, etc.).
- A representative data view (Job Tracker's job list; Phoenix
  CAD's hood-wiring page; etc.).

Screenshots taken at the deployed version's last release vs the
retrofit branch's head, on the same monitor / DPI / OS theme.

Visible-change goal:

| Tool | Acceptable visible change |
|------|---------------------------|
| Phoenix CAD | ≈ 0% (already on System A; widget refactor only) |
| Phoenix Checkout | < 5% (theme already System A; widget swap may shift padding 1–2 px) |
| ValveMaster | High — explicit gray→navy theme swap. Document loudly. |
| Job Tracker | < 5% (theme already System A; refactor primarily code-side) |

If the visible change exceeds the band for a tool that's supposed to
be invisible, the retrofit isn't ready to merge.

## Local backup QSS strategy

Every retrofit lands the canonical commons QSS via
`apply_dark_theme()`. Before merging:

1. The tool's existing `phoenix_style.qss` (or programmatic palette
   in ValveMaster's case) gets copied to
   `<app>/legacy/phoenix_style.qss.preretrofit`.
2. That file is **not** loaded at runtime. It exists as a known-good
   fallback if a critical theme regression is discovered post-merge.
3. The file is removed in a follow-up PR ~30 days after the retrofit
   ships if no regression surfaces.

The phrase "local backup QSS" specifically refers to this preservation
pattern. Not to be confused with the git bundle backups in Phase 6C.

## Drift-vs-extension heuristic

The hardest judgment call during retrofit: is this app-specific code
**extending** commons (allowed) or **drifting from** it (forbidden)?

| Symptom | Drift or extension? |
|---------|---------------------|
| App-local class subclasses a commons widget and adds a method | **Extension** ✓ |
| App-local class subclasses commons widget and **overrides** its `__init__` to change colours | **Drift** ✗ — recolour via QSS object-name override instead. |
| App copies the commons QSS string + edits 2 selectors | **Drift** ✗ — append app-local QSS lines after commons QSS. |
| App invents a new colour token because the closest commons token "isn't quite right" | Likely **drift** — propose the new token as a commons PR first. If only one app needs it, keep it strictly app-local with a comment explaining why. |
| App imports `phoenix_commons.theme.tokens.C` and uses `C['accent']` | **Extension** ✓ — using the public API. |
| App imports `phoenix_commons.theme._embedded_qss` (private module) | **Drift** ✗ — bypassing the public API. Lint should catch this in Phase 9. |

When in doubt, ask: "if I had to delete this app and reinstall it
fresh, would I need to keep this snippet around to recreate the same
look?" If yes → commons. If no → app-local extension.

## Stop conditions

A retrofit **must stop and ask** if any of these surface during the
PR:

| Stop condition | Reason |
|----------------|--------|
| Need to modify a commons-owned file | Triggers a separate commons PR first. Retrofit waits. |
| Need to change the `AppId` GUID | Hard rule — would orphan existing installs. Justin must approve. |
| Need to change `<App>.zip` asset name | Breaks the auto-updater for users still on the prior version. Justin must approve. |
| Need to change install path or user-data path | Same — breaks upgrades. Justin must approve. |
| Frozen-exe verification fails for a reason **other than** the documented S1/AV pattern | New blocker. Document in `BLOCKERS.md` before continuing. |
| A test that passes on `main` fails on the retrofit branch | Fix in the retrofit before merge; do not merge a regression. |
| The visible-change band for the tool is exceeded | Re-scope the retrofit. |

## Per-retrofit branch + PR convention

| Item | Convention | Phase 3A example |
|------|------------|-------------------|
| Branch name | `phase-<phase-id>-<tool-slug>-retrofit` | `phase-3a-phoenix-cad-retrofit` |
| PR title | `Retrofit <App Display Name> to commons-backed (Phase <id>)` | `Retrofit Lab Layout Tool to commons-backed (Phase 3A)` |
| PR body | Use `RETROFIT_PR_TEMPLATE.md`. Plus a "what changed in commons during this retrofit" section (may be empty for later retrofits — commons API is now stable). |
| Merge strategy | `--no-ff`. Preserve the retrofit branch on origin until the post-review report (this doc / equivalent) explicitly clears it for deletion. |
| Tag | `<app-slug>-retrofit-vX.Y.Z` matching the post-retrofit release. |

The earlier `retrofit-<tool-slug>` convention has been superseded by
`phase-<id>-<tool>-retrofit` — phase-prefixed names make the ordering
explicit in `git branch` output and match the directory naming the
post-retrofit reports use.

## Frequency limits

| Wave | Cadence rule |
|------|---------------|
| Pilot (Phase 7) | Both tools merged within 2 weeks of each other. |
| Wave 8a (ValveMaster) | At least 2 weeks **after** the pilot's last merge. |
| Wave 8b (Job Tracker) | At least 2 weeks after Wave 8a. |

Spacing exists so production-user incident reports can surface before
the next retrofit lands.
