# RELEASE_CHECKLIST.md

> Pre-release and post-release procedure for any Phoenix tool that
> ships via GitHub Releases. Conservative by design — the four
> deployed production tools (Job Tracker, Phoenix CAD, Phoenix
> Checkout, ValveMaster) all auto-update against this contract, so
> a mistake here orphans users on the previous version.
>
> Owner: tool maintainer (Justin). Scope: documentation only — this
> file does not execute anything. Pair with `VERSIONING_POLICY.md`,
> `INSTALLER_NOTES.md`, and the tool's own `docs/release_checklist.md`
> (if one exists; tool-local versions override these defaults).

## When to release

Bump and release when any of these surface:

- A bug fix users have hit.
- A new feature complete enough to use.
- A platform retrofit landed on `main` that you want users to receive
  (treat as a patch unless the retrofit changes user-visible behaviour
  — see VERSIONING_POLICY.md § "Retrofit releases").

Do NOT release because "we haven't in a while". Empty releases burn
trust with the auto-updater (users see "v1.X.Y → restart" and discover
nothing changed).

## Pre-release checklist

Run through this top-to-bottom on the merge candidate (usually `main`).
Stop at the first failure; do not proceed with a half-checked list.

### 1. Repo state

- [ ] Working tree clean (`git status` shows nothing).
- [ ] On the release branch (`main` or `master`, per tool).
- [ ] Up to date with origin (`git pull --ff-only`).
- [ ] All target commits already merged (check open PRs).

### 2. Version

- [ ] `version.py` bumped to the new `X.Y.Z`.
- [ ] README's "Current version" line (if present) matches `version.py`.
- [ ] `CHANGELOG.md` has a new `[X.Y.Z] — YYYY-MM-DD` section with
      `### Added` / `### Changed` / `### Fixed` / `### Removed`
      subsections as appropriate. Don't ship empty release notes.
- [ ] No `__version__ = "X.Y.Z-dev"` or similar dev suffix left in.

### 3. Static checks

- [ ] `compileall -q -x "(\.venv|build|dist|commons)" .` exits 0.
- [ ] Tool's pytest (if any) green.
- [ ] Source-mode launch (`python <entry>.py` or `pythonw <entry>.py`)
      opens the window without crash. Per MIGRATION_RULES § 10 row 11,
      verify process alive ≥ 3 seconds and `MainWindowTitle` matches.

### 4. Commons submodule (commons-backed tools only)

- [ ] `git submodule status` reports a clean SHA (no `+` or `-` prefix).
- [ ] Submodule SHA is on `phoenix-commons:main` (run
      `git -C commons branch --contains $(git -C commons rev-parse HEAD)`
      — must include `main`).
- [ ] If you intend to bump the submodule, do it as its own PR before
      the release PR (see MIGRATION_RULES § Per-retrofit branch + PR
      convention for the bump procedure).

### 5. Build

- [ ] `build.bat` succeeds end to end. No PyInstaller warnings about
      missing files; no Inno Setup errors.
- [ ] `dist\<ExeName>.exe` is the right size (sanity-check against the
      previous release — wild swings in size mean something changed
      that you didn't intend).
- [ ] Updater zip (`dist\<ExeName>.zip`) exists and matches the tool's
      payload contract:
  - **Full-folder** tools (Job Tracker, Phoenix CAD): zip contains
    `<ExeName>.exe` AND `_internal/` at the root.
  - **Exe-only** tools (Phoenix Checkout, ValveMaster): zip contains
    only `<ExeName>.exe` at the root. Per ADR-003.
- [ ] Installer (`dist\<ExeName>Setup.exe`) exists.

### 6. Local smoke install

- [ ] Uninstall the currently-installed version of the tool.
- [ ] Run `dist\<ExeName>Setup.exe`. Installer wizard completes
      without prompts you didn't expect.
- [ ] Launch the installed app. Window opens. No crash.
- [ ] Exercise the core path of whatever changed in this release —
      the bug you fixed, the feature you added.
- [ ] Confirm `%APPDATA%\ATS Inc\<App Name>\` still has the user data
      from the previous version (Settings, recent files, etc.) — the
      upgrade should NOT have wiped it.

### 7. Release notes

- [ ] CHANGELOG.md section for this version reads like something you'd
      want to receive. No "various fixes" — name the bug, name the
      feature.
- [ ] Cross-check against the commit log: every meaningful commit
      since the previous tag is reflected in the changelog.

## Release execution

### 1. Tag

```bash
git tag -a vX.Y.Z -m "vX.Y.Z — <one-line summary>"
git push origin vX.Y.Z
```

Tag format is `vX.Y.Z` (lowercase `v`, no app prefix). Tag the same
commit as the merge that lands the release-prep work; usually tip of
`main`.

### 2. GitHub Release

Create on github.com — Releases → Draft new release. Required fields:

- **Tag**: select the `vX.Y.Z` you just pushed.
- **Release title**: `vX.Y.Z — <one-line summary>` (mirror the tag annotation).
- **Description**: paste the CHANGELOG section for this version, with
  the `## [X.Y.Z]` heading replaced by what GitHub shows above the
  description.
- **Attached binaries** (drag-drop into the release):
  - `<ExeName>.zip` — auto-updater zip. REQUIRED. Auto-updater
    fetches by this exact filename — case-sensitive.
  - `<ExeName>Setup.exe` — installer for first-time users.
  - `<ExeName>_FullInstall.zip` — manual-install fallback for users
    who can't run the installer.

Do NOT publish before confirming all three files uploaded (GitHub
sometimes silently drops one if the network blips). If a re-upload is
needed, delete the partial release entirely and re-create — never
"edit" attachments in place.

- [ ] Click "Publish release".

### 3. Verify auto-updater catches

Within 1 minute of publishing, on a machine that has the previous
version installed:

- [ ] Launch the installed app.
- [ ] The `UpdateBanner` (or equivalent for the tool) shows "Update
      available — vX.Y.Z" within ~30 seconds.
- [ ] Click "Install" / "What's New". Update completes. App restarts.
- [ ] Post-restart, the app reports the new version (Help → About, or
      the title bar, depending on the tool).

If the banner does NOT show up:

1. Confirm the GitHub Release is marked "Latest release" (not draft,
   not pre-release).
2. Confirm the asset filename exactly matches what the tool's
   `updater.py` expects (case-sensitive on GitHub's API path).
3. Check the tool's log file (under `%APPDATA%\ATS Inc\<App Name>\`)
   for the updater's diagnostic output.

## Post-release

- [ ] Bump `version.py` to the next dev version on `main` if the
      project uses dev suffixes (most Phoenix tools do not — they
      stay on the released `X.Y.Z` between releases).
- [ ] Close any GitHub issues that this release fixed.
- [ ] If the release was driven by a retrofit, update the relevant
      `MIGRATION_RULES.md` § Migration-order row.

## Hotfix path

If a critical bug is discovered post-release:

1. Branch from the release tag: `git checkout -b hotfix-X.Y.Z+1 vX.Y.Z`.
2. Fix the bug. Bump `version.py` to `X.Y.Z+1`. CHANGELOG entry.
3. Run the full pre-release checklist on the hotfix branch.
4. Merge `hotfix-X.Y.Z+1` → `main` and tag `vX.Y.Z+1`.
5. Release as above. Users on `X.Y.Z` will auto-update to `X.Y.Z+1`
   the next time they launch.

Never silently re-upload a fixed `<ExeName>.zip` to the same release —
the auto-updater compares versions, not file checksums, and will not
re-pull the same `vX.Y.Z` even if you replace the zip.

## Stop conditions

If any of these surface during release prep, stop and ask before
proceeding:

| Condition | Reason |
|-----------|--------|
| Local smoke install fails to launch | The installer or PyInstaller bundle is broken; releasing would orphan users on the previous version. |
| `version.py` and `CHANGELOG.md` disagree | One of them is wrong; pick whichever reflects the actual intended release. |
| Updater zip doesn't match the tool's payload contract | Releasing the wrong shape (full-folder vs exe-only) will break the auto-updater on the user's machine. |
| User data is wiped on upgrade in the smoke install | **Hard stop.** This is a P0 bug. Revert any path-handling change in the release and re-test. |
| The release would change `AppId`, install path, or user-data path | These are hard contracts; changing them strands existing installs (see MIGRATION_RULES § Stop conditions). |

## See also

- `VERSIONING_POLICY.md` — when MAJOR / MINOR / PATCH applies.
- `INSTALLER_NOTES.md` — Inno Setup conventions, wizard artwork,
  signing notes, AppId management.
- `BRANDING_ASSET_GUIDE.md` — icon / wizard image sourcing.
- `MIGRATION_RULES.md` — full retrofit doctrine (some checklist items
  here cross-reference rules there).
