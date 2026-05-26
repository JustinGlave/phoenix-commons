# App Alignment Checklist

> **Status:** practical retrofit checklist.
> **Date:** 2026-05-22.
> **Companion to:** `PHOENIX_APP_STANDARD_BASELINE_V1.md` (the canonical
> standard) and `MIGRATION_RULES.md` (retrofit doctrine).
> **Use:** check items off during a retrofit. Anything unchecked is
> either a Stop Condition or an explicit deferral that must be
> documented in the retrofit's post-retrofit report.

---

## How to use

Copy this checklist into the retrofit PR's body. Tick each item as it lands. **Anything left unchecked at merge time is a merge blocker** unless the post-retrofit report documents why (with a future-phase cleanup commitment).

Sections track the standards baseline categories. Items reference the authoritative source so you can dig deeper without re-reading the whole baseline doc.

---

## A. Pre-retrofit

  - [ ] Tool's working tree is clean (or WIP is isolated to `feature/<slug>` per MIGRATION_RULES § 9)
  - [ ] Pre-flight commons-API gap inventory authored (MIGRATION_RULES § 0)
  - [ ] Each gap has an explicit Option A (keep local) / Option B (add to commons) decision
  - [ ] Option B gaps have a commons PR landed BEFORE retrofit work begins
  - [ ] Retrofit branch created from tool's `main`/`master` at a clean baseline
  - [ ] Branch name follows `phase-<id>-<tool-slug>-retrofit` convention
  - [ ] Frequency limit verified — at least 14 days since the previous *other-tool* retrofit's merge (MIGRATION_RULES § Frequency limits)

## B. Visual standards

  - [ ] App uses `phoenix_commons.theme.apply_dark_theme(app, brand=…)` for theme application
  - [ ] App's `BrandProfile` documented in `theme.py` (or equivalent root file)
  - [ ] No locked-token overrides (BG / SURFACE / TEXT / status colours stay canonical)
  - [ ] `Panel` used for every section card — no inline-styled `QFrame { background: card; … }` containers
  - [ ] `StatusBadge` used for every status pill — no chip-soup QLabels with inline colour
  - [ ] `PrimaryButton` / `SecondaryButton` / `TertiaryButton` used for every visible action button
  - [ ] Zero raw `QPushButton` with `setObjectName("accentBtn")` / `"ghostBtn")` for new code
  - [ ] All chrome icons are Lucide via `icon(name, color)` — no emoji on chrome
  - [ ] Page titles use `setObjectName("pageTitle")` (22px 800-weight)
  - [ ] Section headers use `setObjectName("sectionHeader")` (10px uppercase muted)
  - [ ] No new commons primitive added without documented two-consumer evidence
  - [ ] No new commons icon added unless a clear semantic gap surfaces (and it's added in a separate commons PR)
  - [ ] No animation, no loading spinners, no command palette, no chrome emoji

## C. Functional standards

  - [ ] `main.py` is the single canonical entry point
  - [ ] `version.py` carries `__version__ = "X.Y.Z"`
  - [ ] README current-version line matches `version.py`
  - [ ] User data lives under `%APPDATA%\ATS Inc\<App Name>` (verified via `phoenix_commons.paths.user_data_dir`)
  - [ ] Install files live under `{localappdata}\ATS Inc\<App Name>`
  - [ ] No user data under PyInstaller `_internal/`
  - [ ] Atomic JSON writes (temp-file-then-replace)
  - [ ] Updater uses `phoenix_commons.updater.check_for_update` + `download_and_apply` (commons-backed apps)
  - [ ] `expected_internal` kwarg matches the app's payload contract (`True` for full-folder updaters; `False` for exe-only)
  - [ ] All subprocess calls use `creationflags=subprocess.CREATE_NO_WINDOW` on Windows EXCEPT intentional GUI-launching ones (editor, browser)
  - [ ] Background work uses `QThread` (no raw `threading.Thread`)
  - [ ] Transient status feedback uses `StatusBadge` or status-bar messages — no inline-styled status QLabels

## D. Packaging / build standards

  - [ ] Build venv uses Python 3.12.x (`py -3.12 -m venv .venv` or `.venv-build`)
  - [ ] `requirements.txt` includes `-e ./commons` for commons-backed apps
  - [ ] `requirements-dev.txt` pins `pyinstaller==6.20.0`
  - [ ] `build.bat` includes `--noupx`
  - [ ] `build.bat` includes the stdlib `--exclude-module` list per `FROZEN_BUILD_BASELINE.md`
  - [ ] `build.bat` includes `--collect-all phoenix_commons` for commons-backed apps
  - [ ] `build.bat` includes Step 0 cleanup (`rmdir /S /Q build dist` before each run)
  - [ ] `build.bat` includes commons-submodule preflight (fail loudly if `import phoenix_commons` fails from venv)
  - [ ] Installer Inno Setup script uses `PrivilegesRequired=lowest`
  - [ ] Installer output filename matches the canonical per-tool name (e.g. `LabLayoutToolSetup.exe`)
  - [ ] Updater GitHub Release zip asset name matches the canonical per-tool name (e.g. `LabLayoutTool.zip`)
  - [ ] AppId GUID unchanged from the previous release
  - [ ] Frozen exe launches in the operator's interactive session (5-minute observation window)
  - [ ] S1 didn't quarantine the exe (PID stable, file present, no kill+respawn cycle)

## E. Repository standards

  - [ ] `.github/workflows/ci.yml` exists
  - [ ] CI runs on `windows-latest`
  - [ ] CI uses Python 3.12 via `actions/setup-python@v5`
  - [ ] CI checkout uses `with: submodules: recursive` (commons-backed apps)
  - [ ] CI installs `requirements.txt` and `requirements-dev.txt` as separate steps
  - [ ] CI runs `import phoenix_commons` smoke after install
  - [ ] CI runs `compileall -q .`
  - [ ] CI runs `pytest -q tests/`
  - [ ] CI passes on the retrofit branch tip
  - [ ] Repo root contains: `README.md`, `CHANGELOG.md`, `CLAUDE.md`, `requirements.txt`, `requirements-dev.txt`, `version.py`, `main.py`, `build.bat`, `installer.iss`, `.gitignore`, `.gitmodules` (commons-backed)
  - [ ] `assets/`, `tests/`, `ui/` directories present where applicable
  - [ ] No machine-specific absolute paths committed

## F. Retrofit doctrine

  - [ ] Local facade strategy applied — caller-side imports unchanged
  - [ ] Identity-equal widget verification passes (`assert ui.X is phoenix_commons.widgets.X`)
  - [ ] Pre-flight gap inventory's Option A / Option B decisions all documented in the post-retrofit report
  - [ ] No opportunistic "while we're here" refactors
  - [ ] No business logic touched outside the retrofit's explicit scope
  - [ ] Small logical commits (B1, B2, … or Step 1, 2, …) — not one mono-commit
  - [ ] Each commit passes compileall + pytest independently (bisectable)
  - [ ] Submodule pinned to commons `main` HEAD (or documented intentional older SHA in post-retrofit report)
  - [ ] commons pytest passes on the pinned commons SHA

## G. Source-mode validation (MIGRATION_RULES § 10)

  - [ ] Row 1 — `compileall -q -x "commons|build|dist|\.venv" .` → Exit 0
  - [ ] Row 2 — import-only smoke: `python -c "import paths, updater, ui.style, ui.components, ui.<other>"` → No errors
  - [ ] Row 3 — Identity check: `ui.components.<W> is phoenix_commons.widgets.<W>` → True
  - [ ] Row 4 — Updater config constants preserved
  - [ ] Row 5 — `expected_internal` matches the tool's payload contract
  - [ ] Row 6 — `paths.<APP_CONSTANT>` resolves to the expected path
  - [ ] Row 7 — Offscreen apply_dark_theme + widget construction succeeds; styleSheet substantial; sentinels absent
  - [ ] Row 8 — Offscreen `import <entry-module>` succeeds
  - [ ] Row 9 — Submodule pin matches commons main (or documented older SHA)
  - [ ] Row 10 — Commons pytest green
  - [ ] Row 11 — **Actual source-mode app launch** — process alive ≥3 sec; MainWindowTitle correct; no stderr

## H. Frozen-build validation (production tools only)

  - [ ] Hardened build.bat produces the expected dist/exe + installer
  - [ ] Installer installs into `{localappdata}\ATS Inc\<App Name>`
  - [ ] Installed exe launches
  - [ ] Process alive ≥3 minutes in S1 observation window
  - [ ] No process-kill quarantine
  - [ ] No file-quarantine (exe still present on disk)
  - [ ] No bootloader-content quarantine (exe successfully launched)
  - [ ] User data preserved across upgrade from the previous release
  - [ ] Uninstall round-trip clean

## I. Pre-merge sign-off

  - [ ] Working tree clean
  - [ ] All B-commits / Step-commits pushed to retrofit branch on origin
  - [ ] Operator visual review passed (screenshots in PR or report)
  - [ ] Post-retrofit report authored under `phoenix-commons/docs/ui-platform-baseline-v1/<PHASE>_<TOOL>_REPORT.md`
  - [ ] Report covers what shipped, what stayed local, gap-inventory decisions, validation results
  - [ ] PR uses the `RETROFIT_PR_TEMPLATE.md` structure (when applicable)
  - [ ] Screenshot baseline: before/after captures per the visible-change band for this tool

## J. Merge execution

  - [ ] Push retrofit branch to origin
  - [ ] `git checkout main` (or master)
  - [ ] `git submodule update --init commons` (sync to main's recorded pin)
  - [ ] `git merge --no-ff <retrofit-branch> -m "Merge <Phase> — <App Name> retrofit ..."`
  - [ ] Post-merge validation passes (compileall + pytest)
  - [ ] Annotated tag created on the merge commit (NOT a later cleanup commit): `git tag -a <app-slug>-retrofit-vX.Y.Z <merge-sha> -m "..."`
  - [ ] Push `main`
  - [ ] Push the tag
  - [ ] CI green on the new `main` tip
  - [ ] Retrofit branch preserved on origin (do NOT delete)

## K. Post-merge consolidation (when needed)

If the retrofit deferred any cleanup-eligible items to a post-merge commit (mirrors Phase 3D `d466202`, Phase 3E `829c513`):

  - [ ] Single consolidation commit: submodule bump + dead-import removal + redundant inline-QSS retirement
  - [ ] No code changes bundled that weren't pre-identified in the retrofit's gate report
  - [ ] Push the consolidation commit
  - [ ] CI green on the consolidation commit

## L. Governance

  - [ ] `MIGRATION_RULES.md § Migration order` row appended for this retrofit
  - [ ] Row includes: merge date, merge commit SHA, branch name, tag name, surface summary, scope-preservation confirmation (no scanner change / no commons API change / no Wave-X conflict / etc.)
  - [ ] Commons commit + push for the governance update

---

## Anti-checklist — what NOT to do

The most common ways a retrofit goes wrong. If you find yourself doing any of these, stop and ask:

  - ❌ Adding a new commons primitive "while we're here"
  - ❌ Renaming a variable or refactoring an import block beyond the retrofit's explicit scope
  - ❌ Modifying `AppId` GUID, `<App>.zip` asset name, install path, or user-data path
  - ❌ Skipping the `submodules: recursive` checkout in CI (the Phase 3D CI-fix doctrine)
  - ❌ Using Python 3.13/3.14 for the frozen build (S1 quarantines them — ADR-014)
  - ❌ Tagging the post-merge cleanup commit instead of the merge commit
  - ❌ Force-pushing `main` or rewriting merge-commit history
  - ❌ Deleting the retrofit branch from origin before the post-retrofit window expires
  - ❌ Squashing the retrofit branch's B-commits before merge (lose forensic bisect)
  - ❌ Adding inline `setStyleSheet` to commons primitives (B6 violation)
  - ❌ Adding emoji to chrome (use Lucide)
  - ❌ Adding bespoke colour tokens outside `phoenix_commons.theme.tokens.SEMANTIC_COLORS`
  - ❌ Changing scanner / FileViewer / domain-logic contracts as a side effect
  - ❌ Skipping operator visual review before merge
  - ❌ Promising "we'll fix it in a follow-up" without an actual follow-up commit on the same branch or an explicit issue

---

*End of App Alignment Checklist. Copy this into every retrofit PR. Anything unchecked is either a blocker or an explicit, documented deferral.*
