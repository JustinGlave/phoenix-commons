# BLOCKERS.md

> Active blockers. Each has: impact, mitigation, owner, next action,
> status. Resolving any of these unblocks specific phases — see
> "Blocks" column for the gate map.

## 1. S1 / corporate AV bootloader quarantine

| Field | Value |
|-------|-------|
| **Impact** | Cannot verify any frozen-exe build end-to-end on the current developer laptop. PyInstaller-generated bootloader exes are deleted by the S1 endpoint-protection agent within seconds of being written, before any launch attempt. The unpacked `dist\<App>\<Exe>.exe` disappears; `Compress-Archive` then writes an updater zip with the exe missing; the validator correctly fails. |
| **Evidence** | Reproduced 3 times: Phase 4 (in-tree build), Phase 4B-local (external `%LOCALAPPDATA%` build path), Phase 6 (PCC standalone dogfood). The signature is content-heuristic, not path-based — external build paths don't help. |
| **Mitigation today** | External build path protects the SOURCE tree from collateral damage (Phase 4B-local proved this). The exe itself is still deleted. Source-mode verification (compileall + pytest + offscreen MainWindow) is the only signal we can run. |
| **Owner** | IT / DevOps + Justin |
| **Next action** | Pick one of three resolution paths: (1) IT/S1 allow-list, (2) Authenticode code-signing pipeline, (3) approved alternate build machine. |
| **Status** | **Open. Indefinite.** No ETA. |
| **Blocks** | Phase 4 (final pass), Phase 6C, Phase 7, Phase 8, Phase 8a, Phase 8b, PCC v2.0.0 release, commons-backed wizard becoming default |
| **Cross-link** | `phoenix-command-center/docs/known-issues.md` (canonical), `phase-6-standalone-dogfood-report.md` §19 |

### Resolution-option detail

| Path | Effort | Long-term durability | Notes |
|------|--------|----------------------|-------|
| (1) IT/S1 allow-list | Low if IT is responsive | Per-machine; doesn't help external users | Cheap fix if approval is fast |
| (2) Authenticode code-signing | Higher (cert provisioning + `signtool` integration in `build.bat`) | Best — signed bootloaders bypass many AV heuristics; required for some enterprise allow-listing flows. **Final behavior depends on S1 policy and DevOps approval.** | The durable answer |
| (3) Alternate build host | Medium (set up CI runner / VM / clean workstation) | Works for any build; doesn't help if S1 deletes exes on END-USER machines too | Useful for producing release artifacts even if local laptop stays blocked |

Any single one of these unblocks Phase 6C and the downstream
retrofits. Pick whichever lines up with operational constraints
first.

## 2. Frozen-exe verification

| Field | Value |
|-------|-------|
| **Impact** | We have no proof that PCC (or any wizard-scaffolded tool) actually runs end-to-end after PyInstaller + Inno Setup. Source mode is green; the install / launch / user-data-folder-creation chain is untested. |
| **Mitigation today** | Phase 6C plan (`docs/rollout/phase-6c-frozen-exe-dogfood-plan.md`) is drafted and ready to run the moment the AV blocker clears. |
| **Owner** | Justin (after AV is cleared) |
| **Next action** | Execute Phase 6C plan after Blocker #1 resolves |
| **Status** | **Blocked on #1.** |
| **Blocks** | Phase 7 (retrofit pilot), all subsequent retrofits, any release of PCC as an installer |
| **Cross-link** | `phoenix-commons/docs/rollout/phase-6c-frozen-exe-dogfood-plan.md` |

## 3. Installer runtime behaviour

| Field | Value |
|-------|-------|
| **Impact** | Inno Setup compiles `PhoenixCommandCenterSetup.exe` successfully (Phase 6 proved this), but we've never run the installer to its conclusion — install + launch + uninstall round-trip. The installer's `[Code]` section that prompts before deleting user data has never been observed firing. |
| **Mitigation today** | Inno Setup script is reviewed and follows the pattern used by all 4 production installers, which are known to work in production. |
| **Owner** | Justin (after Blockers 1 + 2 resolve) |
| **Next action** | Part of Phase 6C step 5 — install + launch + verify user-data folder + (later) test uninstall prompt. |
| **Status** | **Blocked on #2.** |
| **Blocks** | Same as Blocker #2 |

## 4. Updater runtime behaviour

| Field | Value |
|-------|-------|
| **Impact** | `updater.py` has never been called against a live GitHub release with a real PhoenixCommandCenter.zip asset. The full download → validate → relaunch flow is unverified. Logic was carried forward from Job Tracker's `starter_package/updater.py` (which IS proven in production) and is unit-tested via the validator helper, but the end-to-end glue is unproven. |
| **Mitigation today** | The PowerShell relaunch helper uses safe single-quoted strings (Phase 3A); the validator helper covers zip-shape correctness (Phase 6A); the source logic mirrors a working production tool. |
| **Owner** | Justin (after Blockers 1 + 2 + 3 resolve) |
| **Next action** | First release of PCC v2.0.0 — observe updater check at startup, observe download+apply against a v2.0.1 follow-up. |
| **Status** | **Blocked on #3.** |
| **Blocks** | PCC stable release, future retrofits that adopt the commons-backed updater |

## 5. Commons distribution strategy unresolved

| Field | Value |
|-------|-------|
| **Impact** | `phoenix-commons` is installable via `pip install -e .` from a sibling-folder checkout, but there's no published wheel and no decision about whether/where to publish one. Retrofitted apps would need either (a) a git submodule pointing at this repo, (b) a private PyPI / index, or (c) full vendoring (Plan B from the unified rollout plan). |
| **Mitigation today** | None — wizard's commons-backed radio currently sets up a submodule, which works but adds operational complexity for users. |
| **Owner** | Justin + Architecture |
| **Next action** | Pick a distribution strategy. Options: PyPI publish (public), GitHub Packages (private), private internal index, submodule-only, Plan B vendoring. |
| **Status** | **Open. Defer until Phase 9** unless a retrofit forces the decision earlier. |
| **Blocks** | Phase 8 (full retrofits at scale benefit from a clean distribution story), Phase 9 |

### Distribution option comparison

| Option | Pros | Cons |
|--------|------|------|
| Submodule (current wizard default) | Zero infrastructure | Users must `git submodule update --init` on first checkout; version pinning via commit SHA is awkward |
| Private PyPI | Clean `requirements.txt` line; semver-friendly | Need to maintain a private index |
| Public PyPI | Same as private + free; auto-publishes via CI | Source becomes public (`LICENSE` prohibits — see PCC's LICENSE) |
| GitHub Packages | Auth via existing PAT; works for private orgs | Less mature than PyPI; tooling quirks |
| Plan B vendoring | No external dependency at runtime | Each retrofit ships its own copy; defeats half the point of commons |

Recommendation when this becomes urgent: **GitHub Packages** for
private hosting matches ATS's existing GitHub workflow without
exposing source code.

## 6. CI for phoenix-commons missing

| Field | Value |
|-------|-------|
| **Impact** | `phoenix-commons` has no GitHub Actions workflow yet. Pushes to commons can't be smoke-tested before they affect retrofitted apps. |
| **Mitigation today** | Manual smoke testing during each phase; no automated guardrail. |
| **Owner** | Justin |
| **Next action** | Adapt PCC's `.github/workflows/ci.yml` for the commons repo — Python 3.14, `pip install -e .`, `pytest -q tests/`. |
| **Status** | **Open. Not blocking** but should land before Phase 7. |
| **Blocks** | Phase 7 confidence (without CI, every retrofit is the first integration test) |

## 7. Backup strategy is local-only

| Field | Value |
|-------|-------|
| **Impact** | Phase 6C Layer 1 produced git bundles at `C:\Users\justing\PycharmProjects\Backups\`. Same-disk location — protects against `.git/objects/` corruption or AV deletion inside the live repo, but NOT against whole-disk failure / laptop loss / theft. |
| **Mitigation today** | None — bundles aren't copied to OneDrive or any remote. PCC is pushed to GitHub which is durable; commons has no remote yet (just local). |
| **Owner** | Justin |
| **Next action** | (a) Push commons to GitHub (private repo), OR (b) copy bundles to `OneDrive - ATS\` periodically. |
| **Status** | **Open. Not urgent** but low-effort to resolve. |
| **Blocks** | Disaster recovery for `phoenix-commons` |
| **Cross-link** | `phoenix-commons/docs/rollout/phase-6c-backup-report.md` |

## Blocker dependency graph

```
                  Blocker #1 (S1/AV)
                        │
              ┌─────────┴─────────┐
              │                   │
              ▼                   ▼
        Blocker #2          (resolution paths
        (frozen-exe verif)   are environmental — IT,
              │              signing, alt host)
              ▼
        Blocker #3
        (installer runtime)
              │
              ▼
        Blocker #4
        (updater runtime)

  Blocker #5 (distribution)  ── independent — resolve in Phase 9
  Blocker #6 (commons CI)   ── independent — resolve before Phase 7
  Blocker #7 (backups)      ── independent — low-effort, low-urgency
```

Blockers 1 → 2 → 3 → 4 are a single chain. Resolve #1 and #2-#4
unblock automatically as Phase 6C executes.

## Closed (historical) blockers

These were active during the original rollout and have since been
resolved. Listed for posterity.

| Closed blocker | Resolution |
|----------------|------------|
| `phoenix-command-center` not a git repo (Phase 5 pre-flight) | Phase 4C-init created the repo + baseline commit |
| Wizard's commons-backed submodule not auto-checked (Phase 5A finding) | Phase 5B auto-ticked the submodule checkbox + added inline skip warning + tailored post-create message |
| `build.bat`'s inline-PowerShell zip validator fragile under PS-wrapped invocation (Phase 6 finding) | Phase 6A moved validation into `scripts/validate_release_zip.py` |
| GitHub Actions CI failing on PCC (no tests/ directory) | `fix-ci-smoke-tests` branch added the canonical smoke baseline; merged at `a9d9433` |
| Bad-frame rendering in animated sidebar sprite (QMovie disposal bug) | Phase pre-baseline GUI polish — switched to QImageReader + QTimer with manual frame compositing |
| AUTOMATION text in sprite wrong colour | Resolved by cropping the banner out entirely (user decision) |

## Reporting cadence

Active blockers are reviewed at the start of every phase to confirm
they're still relevant. A blocker can be reclassified as "closed"
only when its "Next action" has been completed AND the downstream
phase it gates has either executed successfully or been re-scoped to
no longer need it.
