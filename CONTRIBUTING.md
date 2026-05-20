# Contributing to phoenix-commons

Thanks for considering a contribution. **phoenix-commons** is the
**Phoenix UI Platform** — shared theme, widgets, paths, updater,
and icons that every Phoenix Controls desktop tool depends on.

Changes here ripple outward to every consuming tool (Job Tracker,
Phoenix CAD, Phoenix Checkout, Phoenix Master Tool, Phoenix Command
Center). The platform contract therefore takes priority over any
single change. Before contributing, read:

- `docs/ui-platform-baseline-v1/PLATFORM_CONTRACT.md` — ownership map
- `docs/ui-platform-baseline-v1/API_BOUNDARIES.md` — what's public vs private
- `docs/ui-platform-baseline-v1/MIGRATION_RULES.md` — retrofit doctrine
- `docs/ui-platform-baseline-v1/DECISIONS.md` — finalised ADRs

## Quick start

```powershell
git clone https://github.com/JustinGlave/phoenix-commons.git
cd phoenix-commons

py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -e .[test]

# Run the smoke tests
$env:QT_QPA_PLATFORM = "offscreen"
.\.venv\Scripts\python.exe -m pytest -q tests/
```

Python **3.12** is the canonical platform version per ADR-014. Newer
versions (3.13, 3.14) work for dev convenience but commits must not
introduce 3.13-or-newer-only syntax.

## Branching

- `main` — always green. Submodule consumers track this branch (or
  pin a specific SHA, per ADR-015).
- Feature branches — named `feature-<topic>` or `phase-<id>-<scope>`
  for retrofit-enabling work. Merge with `--no-ff`; preserve the
  branch on origin until the post-merge report explicitly clears it
  for deletion (per MIGRATION_RULES.md § Per-retrofit branch + PR
  convention).

## What's in scope

- **New widgets / improvements to existing widgets** — additive
  changes that compose with the existing System A theme. Must
  follow `docs/ui-platform-baseline-v1/COMPONENT_CONTRACT.md`.
- **Theme refinements** — adjustments to non-locked tokens. Brand
  slots (PRIMARY / SECONDARY / ACCENT per ADR-016) can move. Locked
  tokens (BG / SURFACE / TEXT / MUTED / status colours) require a
  superseding ADR.
- **Path / updater hardening** — backwards-compatible additions.
  Adding a kwarg with a sensible default is fine; removing a
  positional argument is not.
- **New ADRs** — file in `docs/ui-platform-baseline-v1/DECISIONS.md`
  per the table at the bottom of that document.
- **Documentation** — clarifications, examples, cross-references
  between docs.
- **Tests** — new tests for existing code are always welcome;
  uncovered widgets / paths are good targets.

## What's out of scope

- **Modifying production tool source.** Each consuming app has its
  own repo. Commons changes propagate to apps via submodule SHA
  bumps in those apps' own PRs.
- **Removing or renaming a public API export** without an ADR + a
  deprecation cycle. The consumer apps depend on the names.
- **Adding a new tool's runtime asset** to commons. Per
  `BRANDING_ASSET_GUIDE.md`, each tool owns its own runtime brand
  assets; commons hosts the SOURCES (`Design Items/colors/*.png`)
  but not the per-tool runtime copies.
- **Light theme additions.** Per ADR-011, commons is dark-only.

## Coding conventions

- **Python 3.12** target (per ADR-014).
- **PySide6** (Qt for Python). No PyQt.
- **Path handling** via `pathlib.Path`.
- **Public API** lives at the package surface (`phoenix_commons.X`).
  Underscore-prefixed modules are internal and must not be imported
  by consumers — see `API_BOUNDARIES.md`.
- **No inline hex colours** — use tokens from
  `phoenix_commons.theme.tokens` or add a new token via a token-only
  PR if the colour is genuinely universal.
- **QSS edits** go in `src/phoenix_commons/theme/phoenix_style.qss`.
  The embedded fallback in `_embedded_qss.py` is generated from this
  source — DO NOT edit the generated file directly. Run
  `python tools/generate_embedded_qss.py` to regenerate after
  editing the QSS.
- **Generated artifacts** are read-only outputs of build tools — see
  `PLATFORM_CONTRACT.md` § Generated Artifacts Policy.

## Tests

```powershell
$env:QT_QPA_PLATFORM = "offscreen"
.\.venv\Scripts\python.exe -m pytest -q tests/
```

CI runs the same command on Windows-latest, Python 3.12. The current
test surface (~90 tests as of Phase 2.6) covers theme application,
widget construction, path resolution, updater payload parsing,
icon loading, and packaging contracts.

When adding new public API, add a test that imports it through the
public surface. When fixing a bug, add a regression test that fails
before your fix and passes after.

## Commit messages

Long, descriptive bodies are encouraged — phoenix-commons is the
platform that anchors every Phoenix tool, so the commit log is the
durable design-decision record. A commit message that explains
*why* the change happened earns its keep.

Phase 3A / 3B retrofit commits and the operational stabilization
sprint set the bar; recent examples in `git log` are the canonical
reference for length + structure.

## Pull requests

Open a PR against `main`. The PR should:

- `compileall -q .` clean.
- `pytest` (offscreen, Windows-latest) green — CI enforces this.
- Update `CHANGELOG.md`'s `## [Unreleased]` section.
- Bump `src/phoenix_commons/_version.py` if the change affects the
  public API (MAJOR / MINOR / PATCH per the comment in that file).
- Cross-reference any ADR the change implements or supersedes.

If the change touches `theme/` or `widgets/`, include a brief note
about visual impact:

- ≈ 0% change expected (refactor) → no screenshots needed.
- Possibly visible change → before / after screenshots from the
  scratch widget gallery (`tools/widget_gallery.py` if available, or
  a brief PySide6 snippet).

## Reporting issues

`.github/ISSUE_TEMPLATE/` is **not currently populated** for
phoenix-commons (it is for the consuming tools). For the moment,
file commons issues as plain GitHub Issues with:

- The consuming tool (or "platform-only").
- The version of commons (`phoenix_commons.__version__`).
- The version of Python.
- Reproduction steps.

## License

phoenix-commons is **proprietary — internal use only**. See
[LICENSE](LICENSE) for the full terms. By contributing, you confirm
that your contribution is original work and that you grant ATS Inc
the right to use it under the project's license.
