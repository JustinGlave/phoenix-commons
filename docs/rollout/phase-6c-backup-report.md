# Phase 6C Backup Report — Layer 1 git bundles

> Local-disk `git bundle` snapshots of `phoenix-command-center` and
> `phoenix-commons`, captured before any Phase 7 work or AV-gate
> clearance activity begins. No remotes added. No `git push`. No
> production-tool involvement.

## 1. Status

**Passed.** Both bundles produced and verified.

| Repo | Bundle file | Size | Refs captured | Verified |
|------|-------------|------|---------------|----------|
| `phoenix-command-center` | `phoenix-command-center-20260513.bundle` | 77,783 B (~76 KB) | `main`, `phase-5-phoenix-tool-wizard`, `HEAD` | ✓ "The bundle records a complete history." |
| `phoenix-commons` | `phoenix-commons-20260513.bundle` | 3,338,226 B (~3.2 MB) | `main`, `phase-2-theme-widgets`, `phase-3-paths-updater`, `phase-4-pyinstaller-compatibility`, `HEAD` | ✓ "The bundle records a complete history." |

## 2. Bundle destination

**Approved destination:** `C:\Users\justing\PycharmProjects\Backups\`
(created by Phase 6C bundle work — did not exist before).

### Tradeoff to be aware of

This is a **same-disk location**, not OneDrive-synced. The folder
sits next to the repos themselves under `C:\Users\justing\PycharmProjects\`,
which means the bundles share fate with the working copies for these
scenarios:

| Failure mode | Same-disk backup covers it? |
|--------------|-----------------------------|
| Accidental folder delete in PycharmProjects | ✗ — both repo and bundle gone |
| `.git/objects/` corruption / AV deletion inside the live repo | ✓ — bundle is a sibling, untouched |
| Whole disk failure | ✗ — bundle disk dies with the repo disk |
| Laptop loss / theft | ✗ — bundle gone with the laptop |
| Accidental `git reset --hard` / branch delete | ✓ — bundle preserves history |

**OneDrive detected and available** (`C:\Users\justing\OneDrive - ATS\`
is the active commercial OneDrive on this laptop, env var
`OneDriveCommercial` points there). It can be layered on top of the
current local backup at any time — just copy the two `.bundle` files
into a OneDrive subfolder (e.g. `OneDrive - ATS\Phoenix\Backups\` or
`OneDrive - ATS\Phoenix Software\Backups\`). No re-bundling required;
the bundle files are self-contained and portable.

If you'd rather move the canonical backup location to OneDrive
outright, future bundle runs can target that path directly and the
existing files at `C:\Users\justing\PycharmProjects\Backups\` can be
moved over or deleted.

## 3. Bundle commands actually run

```
$ mkdir -p "C:\Users\justing\PycharmProjects\Backups"

$ cd C:\Users\justing\PycharmProjects\phoenix-command-center
$ git bundle create "C:\Users\justing\PycharmProjects\Backups\phoenix-command-center-20260513.bundle" --all
$ git bundle verify "C:\Users\justing\PycharmProjects\Backups\phoenix-command-center-20260513.bundle"

$ cd C:\Users\justing\PycharmProjects\phoenix-commons
$ git bundle create "C:\Users\justing\PycharmProjects\Backups\phoenix-commons-20260513.bundle" --all
$ git bundle verify "C:\Users\justing\PycharmProjects\Backups\phoenix-commons-20260513.bundle"
```

Date stamp `20260513` is today's date (`date +%Y%m%d`). Future bundle
runs append a fresh date stamp so old bundles accumulate naturally
until you choose to prune them.

## 4. Verification output

### 4.1 `phoenix-command-center` bundle

```
$ git bundle verify C:\Users\justing\PycharmProjects\Backups\phoenix-command-center-20260513.bundle
C:/Users/justing/PycharmProjects/Backups/phoenix-command-center-20260513.bundle is okay
The bundle contains these 3 refs:
e3cb7d70d075e28ce1d1ae309b1a20b2a99aef91 refs/heads/main
f592e93079f5917738e93b49ac21a5983d97a076 refs/heads/phase-5-phoenix-tool-wizard
e3cb7d70d075e28ce1d1ae309b1a20b2a99aef91 HEAD
The bundle records a complete history.
The bundle uses this hash algorithm: sha1
```

`main` HEAD is the Phase 5-wizard merge commit `e3cb7d7`. The merged
feature branch `phase-5-phoenix-tool-wizard` is preserved at
`f592e93` (the AV-known-issues doc commit, which is the tip of that
branch before it was merged into `main`). `HEAD` matches `main`,
which is the currently checked-out branch.

### 4.2 `phoenix-commons` bundle

```
$ git bundle verify C:\Users\justing\PycharmProjects\Backups\phoenix-commons-20260513.bundle
C:/Users/justing/PycharmProjects/Backups/phoenix-commons-20260513.bundle is okay
The bundle contains these 5 refs:
4049f7c85756598571214e8318fd856561497cdd refs/heads/main
db1d8b47c530d8a2a07539ac5614bcece5f5c202 refs/heads/phase-2-theme-widgets
b2e7f794facc35e65bacf0d15833ca6432f3d360 refs/heads/phase-3-paths-updater
c5106e1ccd96d8cd02e9431c9548b54a115d9fe7 refs/heads/phase-4-pyinstaller-compatibility
c5106e1ccd96d8cd02e9431c9548b54a115d9fe7 HEAD
The bundle records a complete history.
The bundle uses this hash algorithm: sha1
```

`HEAD` is on `phase-4-pyinstaller-compatibility` at commit `c5106e1`
(the Phase 6C plan, this report's predecessor). All long-running
phase branches are preserved — `phase-2-theme-widgets`,
`phase-3-paths-updater`, `phase-4-pyinstaller-compatibility`, plus
`main`.

## 5. Bundle file listing

```
$ ls -la C:\Users\justing\PycharmProjects\Backups\
-rw-r--r--  77,783  May 13 12:28  phoenix-command-center-20260513.bundle
-rw-r--r--  3,338,226  May 13 12:28  phoenix-commons-20260513.bundle
```

Total backup size: ~3.4 MB. Both files are byte-for-byte portable —
copying them to OneDrive, a USB drive, or another machine is a plain
file copy with no `git`-side ceremony.

## 6. Restore commands

`git bundle` produces a single-file archive that `git clone` can
treat as a remote. Restoration is the same surface as cloning any
other repo.

### 6.1 Restore phoenix-command-center

```
# Pick a fresh restore location — DO NOT restore on top of an
# existing working copy.
cd C:\Users\justing\PycharmProjects\

git clone "C:\Users\justing\PycharmProjects\Backups\phoenix-command-center-20260513.bundle" phoenix-command-center-restored

cd phoenix-command-center-restored
git remote remove origin      # the bundle file gets registered as 'origin' —
                              # remove it so a future `git fetch` doesn't
                              # try to read the bundle file
git branch -a                 # confirms main + phase-5-phoenix-tool-wizard
git log --oneline -3          # confirms e3cb7d7 / f592e93 / 978f457
```

After cleanup, the restored repo is functionally identical to the
original at the time of the bundle. Then either:
- continue working in `phoenix-command-center-restored\` and rename
  it back when you're satisfied, or
- copy specific files / branches back into a fresh checkout of an
  actual remote (if one is set up later).

### 6.2 Restore phoenix-commons

```
cd C:\Users\justing\PycharmProjects\

git clone "C:\Users\justing\PycharmProjects\Backups\phoenix-commons-20260513.bundle" phoenix-commons-restored

cd phoenix-commons-restored
git remote remove origin
git branch -a                 # confirms main + phase-2-theme-widgets +
                              # phase-3-paths-updater +
                              # phase-4-pyinstaller-compatibility
git log --oneline -3          # confirms c5106e1 / e8b8183 / 5f8be5f
```

Note that the bundle's `HEAD` is on `phase-4-pyinstaller-compatibility`
(matching the repo's state at bundle time). If you want `main`
checked out after restore:

```
git checkout main
```

### 6.3 Restore one specific branch only

If you only need a specific branch (e.g. after a `git branch -D` mishap
on the live repo):

```
cd C:\Users\justing\PycharmProjects\phoenix-command-center
git fetch "C:\Users\justing\PycharmProjects\Backups\phoenix-command-center-20260513.bundle" \
    phase-5-phoenix-tool-wizard:phase-5-phoenix-tool-wizard
```

That pulls `phase-5-phoenix-tool-wizard` from the bundle into the
live repo as a fresh branch, leaving everything else untouched.

### 6.4 Verify a bundle without restoring

```
git bundle verify "C:\Users\justing\PycharmProjects\Backups\phoenix-command-center-20260513.bundle"
git bundle list-heads "C:\Users\justing\PycharmProjects\Backups\phoenix-command-center-20260513.bundle"
```

`bundle verify` confirms the file isn't corrupt and matches the
expected hash chain. `bundle list-heads` lists the refs without
extracting anything.

## 7. Repo state at bundle time

### 7.1 phoenix-command-center

```
$ git status --short --branch
## main
(clean working tree)

$ git log --oneline -3
e3cb7d7 Merge Phoenix Tool wizard templates
f592e93 Document AV known issue before merging Phoenix Tool wizard
978f457 Phase 6A — move release-zip validation out of fragile inline PowerShell
```

### 7.2 phoenix-commons

```
$ git status --short --branch
## phase-4-pyinstaller-compatibility
(clean working tree)

$ git log --oneline -3
c5106e1 Phase 6C plan — frozen-exe dogfood after AV gate clears (drafted, not executed)
e8b8183 Phase 6B report — Phoenix Tool wizard merged into Command Center main
5f8be5f Phase 6A report — release-zip validator moved out of fragile inline PowerShell
```

This report (`phase-6c-backup-report.md`) is the next commit on
`phase-4-pyinstaller-compatibility`.

## 8. Suggested cadence

After every accepted phase (Phase 6C, then each Phase 7 retrofit),
re-run the two bundle commands. Each run produces a fresh dated file
without overwriting the previous one, so the backup folder
accumulates a natural per-phase history.

If the folder grows uncomfortably large (Phase 7 retrofits could
each add tens of MB to `phoenix-commons` if assets are touched),
prune by deleting older dated bundles. Keeping at least:

- The most recent bundle per repo, and
- The "last good before risky operation" bundle (e.g. before a
  retrofit branch lands)

is a sensible minimum.

## 9. Confirmation — what didn't happen

- **No git remotes added.** Both repos still have zero remotes
  configured locally (`git remote -v` is empty for both).
- **No `git push`.** Bundles are file-write only; nothing was
  uploaded anywhere.
- **No GitHub / GitLab / Azure DevOps account or repo touched.**
- **No production tools touched.** `Job Tracker`, `Phoenix_CAD_Tool`,
  `Phoenix-Checkout-Tool`, and `ValveMasterTool` were not read or
  written.
- **No PyInstaller / Inno Setup / `build.bat` / updater / release
  commands run.**
- **Phase 7 not started.**

## 10. Next steps

Immediate options, in order of dependency:

1. **(Optional) Copy bundles to OneDrive.** Lift the off-machine
   protection from the §2 tradeoff. A plain `Copy-Item` from
   `C:\Users\justing\PycharmProjects\Backups\` into a folder under
   `C:\Users\justing\OneDrive - ATS\` is all that's needed. No
   git ceremony.

2. **AV gate clearance work.** User-driven — IT/S1 allow-list,
   Authenticode signing, or alternate build host (see Phase 6C
   plan §0 for the three paths).

3. **Phase 6C execution.** Only after step 2 lands. Generates a
   fresh standalone scaffold, builds it, verifies the bootloader
   survives, installs, launches, confirms user-data folder.

4. **Phase 7 retrofits.** Only after Phase 6C passes. Phoenix CAD →
   Checkout → ValveMaster → Job Tracker, each on its own feature
   branch off `main`, per the unified plan.

No further bundle work or remote setup happens unless explicitly
approved.
