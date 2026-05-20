# VERSIONING_POLICY.md

> Semantic-versioning policy for Phoenix tools. Defines when to bump
> MAJOR vs MINOR vs PATCH, the tag format, and the "retrofit release"
> conventions established during the Phase 3A / 3B platform retrofits.
>
> Documentation only. Each tool's actual current version lives in its
> own `version.py`; this file describes the policy for picking the
> next one.

## Format

Every Phoenix tool's `version.py` contains exactly one assignment:

```python
__version__ = "X.Y.Z"
```

Where:

- **X (MAJOR)** — incremented on breaking user-visible changes
  (incompatible data schema, removed feature, redesign requiring user
  re-training). Rare.
- **Y (MINOR)** — incremented on new features or significant additions
  that are backward-compatible.
- **Z (PATCH)** — incremented on bug fixes, small UX tweaks,
  documentation, refactors, dependency bumps, platform retrofits that
  preserve behaviour.

No pre-release suffixes (`-alpha`, `-rc1`, etc.). No build metadata
(`+sha`). The Phoenix auto-updater compares versions numerically and
extra suffixes confuse it.

## When to bump

### PATCH (Z)

Any of:

- A bug fix users have hit.
- A platform retrofit that preserves behaviour (e.g. Phase 3A Phoenix
  CAD, Phase 3B Phoenix Checkout).
- A small UX tweak (button label, dialog text, icon swap).
- A `requirements.txt` pin bump that doesn't change runtime behaviour.
- A code refactor / cleanup with no functional change.
- A docs-only release.

PATCH bumps are the common case. Most Phoenix releases are PATCH.

### MINOR (Y)

Any of:

- A new feature (new menu entry, new dialog, new file format support,
  new tool integration).
- A new build-time dependency that meaningfully changes the install
  footprint (e.g. adding `openpyxl` to support a new export format).
- A breaking change to a **non-user-facing** API (e.g. a refactor that
  changes the on-disk format of a config the user doesn't directly
  edit, but where backward-compat migration is automatic and
  invisible).

When MINOR bumps: reset PATCH to `0`.

### MAJOR (X)

Reserved for changes the user would notice as a different product:

- A redesigned UI requiring re-training.
- A removed feature that users rely on.
- A required data migration the user has to consent to (or that has
  any chance of failing).
- Dropping support for an entire workflow.

When MAJOR bumps: reset MINOR and PATCH to `0`.

## Retrofit releases — Phase 3A / 3B precedent

The platform retrofits (commons-backed pattern adoption) preserve
behaviour by design. They are **PATCH-eligible by policy**, but the
precedent set by Phase 3A and Phase 3B was to **defer the version
bump** — the retrofit merge lands on `main` without a new release,
and the version is incremented later when the next user-visible
change ships.

The reasoning:

1. A retrofit-only release would carry no user-visible change but
   still trigger the auto-updater's "Update available — restart"
   prompt. Users restart, see nothing new, lose trust.
2. The retrofit changes the build pipeline (commons submodule,
   `--collect-all=phoenix_commons`); shipping it stand-alone front-loads
   any frozen-build risk without the benefit of bundling it with
   actual features.

So:

- **Retrofit MERGES** → no tag, no release. `version.py` stays at
  the pre-retrofit value.
- **Next release that includes the retrofit** → normal PATCH (or
  MINOR if the release also adds a feature). Notes mention "platform
  retrofit (Phase XX)" but the user-visible changelog focuses on
  what they care about.

Both Phase 3A (Phoenix CAD, retrofit merged into `lab-layout-tool:master`
2026-05-19, `version.py` still `0.1.1`) and Phase 3B (Phoenix Checkout,
retrofit merged 2026-05-19, `version.py` still `1.7.0`) follow this
precedent.

## Tag format

```
vX.Y.Z
```

Lowercase `v`, no app prefix, no suffix. Examples: `v1.7.0`, `v0.1.1`,
`v1.8.5`.

Tags are placed on the merge commit that lands the release-prep work
(version bump + changelog) into `main`/`master`.

## Branch / repo naming relationship

| Repo | Tag prefix | Notes |
|------|-----------|-------|
| Job Tracker (`project-tracking-tool`) | `v` | e.g. `v1.8.5` |
| Phoenix CAD (`lab-layout-tool`) | `v` | e.g. `v0.1.1` |
| Phoenix Checkout (`Phoenix-Checkout-Tool`) | `v` | e.g. `v1.7.0` |
| ValveMaster (`valve-master-tool`) | `v` | e.g. `v1.0.9` |
| phoenix-commons | `v` (when tagged at all) | Currently never tagged — commons rolls forward with the consuming tools' submodule pins. May start tagging when commons becomes a registered Python package per ADR-014. |
| phoenix-command-center | `v` | Currently never released; v2.0.0 in `version.py` is the dev-tracked current state. |

## Cross-tool version coordination

There is **no** cross-tool version sync. Each Phoenix tool versions
independently. A change in commons does NOT trigger a version bump
in the consuming tools — the consuming tools pick up commons via
submodule SHA, and only release when their own release criteria are
met.

This is intentional. Coupling versions would require every tool to
re-release on every commons change, which is impractical for a small
team.

## Pre-1.0 tools

Phoenix CAD is at `v0.1.1` — explicitly pre-1.0. Convention:

- Pre-1.0 tools may break things in MINOR bumps without an explicit
  MAJOR. The intent of `0.X` is "still finding the shape".
- A `1.0.0` bump is meaningful — it signals "this is the API the tool
  promises to keep".
- Tools should not stay in `0.X` indefinitely. If a tool has been
  stable for 6+ months and is in production use, bump to `1.0.0`
  on the next PATCH cycle.

## Anti-patterns to avoid

| Anti-pattern | Why it's bad |
|--------------|--------------|
| `1.8.5.1` (4-segment) | The auto-updater parses 3-segment SemVer. The 4th segment is ignored. |
| `v1.8.5-rc1` | Same — suffix is ignored, and now you have a tag that "wins" over `v1.8.5`. Use a separate pre-release repo or branch, not a confused tag. |
| Re-using a tag (force-push) | Auto-updater compares versions; the user is already on the version it claims, so they won't pull the new artifact. |
| Skipping versions (`1.7.0` → `1.9.0`) | Confuses users and disrupts the changelog timeline. If you must skip, document why in the CHANGELOG. |
| Out-of-order versions (`1.7.0` released after `1.8.0`) | Same — confuses the auto-updater and the user. |
| `version.py` says X but README says Y | One of them is wrong; the pre-release checklist catches this but it's still embarrassing in a release. |

## See also

- `RELEASE_CHECKLIST.md` — full release procedure (the place where
  version-bump actually happens).
- `INSTALLER_NOTES.md` — `AppVersion=` in `installer.iss` is fed from
  `version.py`; the policy here applies to both.
- `MIGRATION_RULES.md` — retrofit-release conventions (cross-references
  the "Retrofit releases" section above).
- [Semantic Versioning 2.0.0](https://semver.org/) — the spec this
  policy follows.
