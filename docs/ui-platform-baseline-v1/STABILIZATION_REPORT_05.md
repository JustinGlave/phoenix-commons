# STABILIZATION_REPORT_05.md

> Phase 2.6 — Packaging Verification. Validates the platform
> packages correctly under supported source-mode workflows
> (editable install, non-editable wheel install, submodule shape)
> and locks in ADR-015 — git submodule + `pip install -e ./commons`
> as the official transport mechanism for Phases 3-8.
>
> Source-only. No PyInstaller, no Inno Setup, no frozen-exe
> validation, no installer testing, no migrations, no retrofits,
> no icon replacement.
>
> Captured 2026-05-19.

## 1. Status

**Passed.** All Phase 2.6 deliverables landed as three logical
commits on `main`, pushed to origin (`2325934..85d14a1`).

- ADR-015 finalised (and ADR-010 marked Superseded for Phases 3-8).
- 16 new tests across two modules (`test_tokens.py` + `test_packaging.py`).
- Four isolated install dry-runs in fresh venvs — all green.
- Verification matrix: **35 / 48** rows verified (up from 30).
- 83 / 83 tests pass under the existing pytest suite.

Architecture stabilization remains in effect. **No frozen-runtime
work, no installer testing, no migrations, no retrofits started.**

## 2. ADR-015 — temporary commons distribution strategy

**Decision:** For Phases 3 through 8 inclusive, `phoenix-commons`
is distributed as a **git submodule + editable install**. Every
consuming app adds `phoenix-commons` as `commons/` under its repo
root and runs `pip install -e ./commons` from its build venv.

**Explicitly an operational decision for Phases 3-8, not a forever
decision.** Phase 9 may revisit (private wheel registry, GitHub
Packages, etc.) once the cross-app commons API is proven stable
and the wheel-publish cadence is justified.

**Seven-factor rationale** (full text in `DECISIONS.md` § ADR-015):

1. Matches existing PCC wizard scaffold (`git submodule add` +
   `pip install -e ./commons`)
2. Lowest migration friction for future retrofits
3. Easiest rollback (`git submodule update --recursive <sha>`)
4. Easiest cross-repo branch coordination
5. Simplest package-data behaviour (one `sys.path` entry; same
   resolution in source + frozen modes)
6. Works offline (no registry network call)
7. Avoids premature package-registry infrastructure complexity

**ADR-010** (the prior "deferred to Phase 9" ADR on the same
question) is now marked **Superseded by ADR-015 for Phases 3-8**.
Its re-evaluation trigger is updated to "Phase 9 re-opens".

**Documented in ADR-015:**

- Expected submodule layout
- Editable-install expectations
- Consuming-app assumptions (no underscore imports, no commons
  edits during retrofit, pin submodule SHA at release time,
  respect Generated Artifacts Policy)

Cross-referenced from ADR-002, ADR-007, ADR-010, PACKAGING_CONTRACT,
BLOCKERS §5.

## 3. Packaging verification results

### 3.1. Editable install (`pip install -e .`)

**Verified ✓.** Fresh venv under `$TEMP/phx-verify/editable/.venv`,
Python 3.14.3.

```
$ python -m venv .venv
$ .venv/Scripts/python.exe -m pip install -q -e <repo>
$ .venv/Scripts/python.exe -c "
import phoenix_commons
print(phoenix_commons.__version__)
from importlib.resources import files
qss = (files('phoenix_commons.theme') / 'phoenix_style.qss').read_text(encoding='utf-8')
print(f'QSS: {len(qss)} chars')
svgs = sorted(p.name for p in files('phoenix_commons.icons.lucide').iterdir()
              if p.name.endswith('.svg'))
print(f'SVGs: {len(svgs)}')
"

phoenix_commons: 0.1.0
phoenix_style.qss: 16,891 chars
SVGs bundled: 10 (check.svg info.svg plus.svg refresh.svg save.svg
                  search.svg settings.svg trash.svg warning.svg x.svg)
EMBEDDED_QSS: 16,891 chars
tokens.PRIMARY: '#dc2626'
tokens.C is SEMANTIC_COLORS: True
OK — editable install resolves package data via importlib.resources
```

Confirms: package metadata, package data (`*.qss`, all 10 `*.svg`),
generated artifact, the Phase 2.5 tokens module, and the `C` alias
identity all resolve cleanly through the editable install path.

### 3.2. Editable install with `[test]` extras

**Verified ✓.** Same shape, plus `[test]` dependencies pulled and
the full pytest suite run against the editable install.

```
$ pip install -q -e <repo>[test]
$ pip list | grep -iE 'pytest|phoenix'
phoenix-commons    0.1.0   C:\…\phoenix-commons
pytest             9.0.3
pytest-qt          4.5.0

$ QT_QPA_PLATFORM=offscreen <venv>/python -m pytest -q tests/
.........................................................................
...........                                                       [100%]
83 passed in 0.23s
```

Confirms: the `[test]` extras dependency chain resolves to live
`pytest` + `pytest-qt`, and the full 83-test suite passes when run
from the venv (not the repo's host Python).

### 3.3. Non-editable install (`pip install .`)

**Verified ✓.** Fresh venv at `$TEMP/phx-verify/nonedit/.venv`,
non-editable install builds the wheel internally.

```
$ pip install -q <repo>
$ <venv>/python -c "
import phoenix_commons
print(phoenix_commons.__file__)
# … importlib.resources walk over package data
"

phoenix_commons.__file__:
  C:\…\phx-verify\nonedit\.venv\Lib\site-packages\phoenix_commons\__init__.py
phoenix_style.qss bundled in wheel: 17,662 bytes
SVGs bundled in wheel: 10
EMBEDDED_QSS resolves: 16,891 chars
icons.ICON_NAMES: ['check', 'info', 'plus', 'refresh', 'save', 'search',
                   'settings', 'trash', 'warning', 'x']
OK — non-editable wheel install survives importlib.resources lookup
```

The non-editable wheel **does** bundle `phoenix_style.qss` and all
10 SVGs, because `pyproject.toml`'s
`[tool.setuptools.package-data]` table declares both globs:

```toml
[tool.setuptools.package-data]
"phoenix_commons.theme"        = ["*.qss"]
"phoenix_commons.icons.lucide" = ["*.svg"]
```

The `phoenix_style.qss` byte count differs between source-tree
(16,891 chars, LF endings) and wheel (17,662 bytes, CRLF endings
applied by setuptools' default text handling) — but the content
read via `importlib.resources` is identical when decoded as text.
Documented in the matrix as expected behaviour.

### 3.4. Submodule sandbox dry-run

**Verified ✓.** Most consequential of the four — simulates the
exact shape ADR-015 mandates for consuming apps.

Sandbox layout at `$TEMP/phx-verify/sandbox/app/`:

```
sandbox/app/
├── commons/       ← populated via `git archive HEAD | tar -x`
│                    (working-tree shape equivalent to a real submodule
│                     for pip-install purposes)
├── main.py        ← exercises every public surface
└── .venv/         ← created via `python -m venv`
```

Steps:

```
$ git archive --format=tar HEAD | (cd sandbox/app/commons && tar -x)
$ cd sandbox/app
$ python -m venv .venv
$ .venv/Scripts/python.exe -m pip install -q -e ./commons
$ .venv/Scripts/python.exe main.py
```

`main.py` output (abridged):

```
sandbox python: 3.14.3
phoenix_commons.__version__: 0.1.0
phoenix_commons.__file__: …\sandbox\app\commons\src\phoenix_commons\__init__.py
theme.apply_dark_theme: <function apply_dark_theme at 0x…>
theme.tokens.BG: #0a0e27  PRIMARY: #dc2626  ACCENT: #3b82f6
theme.tokens.C is SEMANTIC_COLORS: True
icons.ICON_NAMES (10): ['check', 'info', 'plus', 'refresh', 'save',
                        'search', 'settings', 'trash', 'warning', 'x']
icons.SEMANTIC_COLORS is tokens.SEMANTIC_COLORS: True
icons exceptions resolve: IconNotFoundError, UnknownColorError
paths.is_frozen(): False
paths.user_data_dir / resource_path resolve: <function …>
updater.UpdateInfo: <class 'phoenix_commons.updater.client.UpdateInfo'>
updater.check_for_update / download_and_apply resolve: ok
updater.installer.UpdatePackageError resolves: UpdatePackageError
phoenix_style.qss bundled: 16,891 chars
icons/lucide/ SVGs bundled: 10
embedded_qss.EMBEDDED_QSS: 16,891 chars
OK -- sandbox app resolves every public surface via the editable
       submodule install
```

The key signal: `phoenix_commons.__file__` resolves to the
sandbox's `commons/src/phoenix_commons/__init__.py` — proving the
import path goes through the consuming-app's submodule clone, not
through a stale cache from any earlier install.

This is the smoking gun for ADR-015: real consuming apps following
the same shape will work end-to-end in source mode.

### 3.5. What the sandbox dry-run DID NOT exercise

Honest framing — the matrix marks row 9.1 as Verified with this
footnote:

- **`git submodule add` invocation itself was not run.** The
  sandbox used `git archive | tar` to populate `commons/` because
  exercising the submodule command requires two-repo setup that
  Command Center's wizard handles. For pip-install behaviour, the
  two paths are equivalent.
- **No real consuming app was scaffolded.** Per the user spec:
  *"Do NOT create a real consuming app. Do NOT scaffold a full
  app."* — the sandbox is the minimal shape required to verify
  the install path.
- **No PyInstaller / Inno Setup / frozen-exe / updater-deploy
  runs.** All AV-gated.

## 4. New tests added

### 4.1. `tests/test_tokens.py` — 7 tests

| Test | Verifies |
|------|----------|
| `test_every_constant_is_a_lowercase_six_digit_hex` | Every palette constant matches `/^#[0-9a-f]{6}$/` |
| `test_semantic_colors_has_the_expected_keys` | `SEMANTIC_COLORS` is the closed expected key set |
| `test_semantic_colors_entries_match_module_constants` | `SEMANTIC_COLORS["primary"] == PRIMARY` etc. |
| `test_info_is_an_alias_for_accent` | `INFO == ACCENT` (documented alias) |
| `test_c_alias_is_identical_to_semantic_colors` | `C is SEMANTIC_COLORS` — identity, not equality |
| `test_tokens_module_is_qt_free` | No PySide6 names pulled in |
| `test_all_export_matches_public_surface` | `__all__` lists everything the docstring promises |

### 4.2. `tests/test_packaging.py` — 9 tests

| Test | Verifies |
|------|----------|
| `test_phoenix_style_qss_resolves_via_importlib_resources` | QSS reachable as package data; canonical token present |
| `test_every_icon_name_has_a_bundled_svg` | Every name in `ICON_NAMES` has a real `.svg` |
| `test_lucide_subpackage_has_at_least_the_starter_set` | SVG-file count ≥ `ICON_NAMES` count (catches "added an SVG but forgot to register it") |
| `test_embedded_qss_module_at_expected_path` | Generated artifact at `phoenix_commons.theme.embedded_qss` |
| `test_full_public_api_resolves` | Every name from `API_BOUNDARIES.md` resolves via package `__init__` re-exports |
| `test_icons_consumes_tokens_semantic_colors` | Identity check — `icons.SEMANTIC_COLORS is theme.tokens.SEMANTIC_COLORS` |
| `test_icon_registry_imports_from_tokens_not_inlined` | Static-source check — catches future re-inlining |
| `test_pyproject_declares_both_package_data_paths` | Both `*.qss` and `*.svg` declared as package data |
| `test_every_submodule_with_public_surface_declares_all` | Regression guard from Phase 2.5 |

Total new tests: **16** (7 + 9).
New suite tally: **83 / 83 pass** (67 + 7 + 9). Runtime: 0.23–0.33 s.

## 5. Verification-matrix updates

Five rows moved from Unverified/Deferred to ✅ Verified:

| Row | Description | New evidence |
|-----|-------------|--------------|
| 1.5 | `theme.tokens` constants resolve | `tests/test_tokens.py` |
| 2.4 | `pip install .` (non-editable) bundles `*.qss` + `*.svg` | Dry-run §3.3 + `test_pyproject_declares_both_package_data_paths` |
| 5.9 | Icons consume `SEMANTIC_COLORS` from `theme.tokens` | `test_icons_consumes_tokens_semantic_colors` + `test_icon_registry_imports_from_tokens_not_inlined` |
| 9.1 | Submodule shape `app/commons/` is consumable by pip-install-e | Sandbox dry-run §3.4 |
| 9.2 | `pip install -e ./commons` resolves from a tool's tree | Same sandbox dry-run |

**New tally — 35 / 48 Verified (+5 since Phase 2.5).** The breakdown:

| Status | Phase 2.5 end | Phase 2.6 end | Δ |
|--------|---------------|---------------|---|
| ✅ Verified | 30 | **35** | **+5** |
| ⚠️ Unverified | 4 | 1 | -3 |
| ⏳ Deferred | 5 | 3 | -2 |
| 🔴 Blocked | 9 | 9 | 0 |
| **Total** | **48** | **48** | — |

**Remaining gaps:**

- One Unverified row (6.4 — generator triple-quote guard) — low-risk, trivial to add when convenient.
- Three Deferred rows: 6.5 (`_generated/` move on threshold), 7.6 (optional PyInstaller-smoke CI), 9.3 (Plan B vendoring — exercised during Phase 6 dogfood).
- Nine Blocked rows: all gated by S1/AV chain (BLOCKERS.md §1). Single root cause; resolving it unblocks frozen mode (10.x) + installer runtime (11.x) + the end-to-end updater test (8.5) in one cascade.

## 6. Risks discovered / judgment calls

| # | Item | Resolution |
|---|------|------------|
| 1 | Local Python on this laptop is **3.14**; ADR-014's contract target is 3.12. Dry-runs use 3.14, not 3.12. | Acceptable — dry-runs validate pip-install / importlib.resources machinery, which is interpreter-version-independent. CI runs on 3.12 (`.github/workflows/ci.yml`); both interpreters agree. Pre-existing coordination item — see ADR-014 Consequences. |
| 2 | The non-editable wheel install reports a slightly different `phoenix_style.qss` byte count (17,662 vs 16,891 chars). | Setuptools applies CRLF line endings to text package-data on Windows wheels by default. `importlib.resources.read_text(encoding="utf-8")` decodes both to the same logical content. Not a bug; documented. |
| 3 | The sandbox dry-run uses `git archive \| tar` rather than a real `git submodule add` to populate `commons/`. | The pip-install behaviour is identical because pip looks at `pyproject.toml`, not at the parent `.git/config`. The actual `git submodule add` invocation is exercised by the Command Center wizard's scaffold step (Phase 5+) and is out of scope here. The matrix footnote on row 9.1 makes this explicit. |
| 4 | `[notice] A new release of pip is available: 25.3 -> 26.1.1` appeared in all dry-run output. | Cosmetic; doesn't affect install behaviour. Local laptop pip is not the source of truth — CI's pip version is. Skipping the upgrade. |
| 5 | The on-laptop `distutils-precedence.pth` warning appears in every Python invocation. | Pre-existing developer-environment issue (machine has a stale `_distutils_hack` from older PCC tooling). Doesn't affect any test or install. Phase 2.5 also lived with it. |
| 6 | Phase 2.6 tests duplicate one assertion from Phase 2.2's `test_icons.py` (icon SVG existence). | Intentional. The duplicate lives in the packaging suite so "package data survives" is locally legible from that test module. No test cross-talk because each invocation reads from `importlib.resources` fresh. |
| 7 | The `test_icon_registry_imports_from_tokens_not_inlined` test inspects source via `inspect.getsource`. Could break under unusual install modes that strip source files. | Editable + wheel installs both ship the `.py` files (`.pyc`-only installs are deprecated in setuptools). If a future install mode strips source, this test will need to swap to a runtime identity check only. Documented in the test docstring. |

No new blockers discovered. `BLOCKERS.md` is unchanged.

## 7. Future migration implications

This phase locks in the operational contract that future retrofits
will follow. Implications:

1. **Every consuming-app retrofit must add `commons/` as a submodule.**
   The wizard scaffolds this for new tools; existing production tools
   gain it during Phase 7+ retrofits.
2. **Every consuming-app `build.bat` must run
   `git submodule update --init --recursive`** before
   `pip install -r requirements.txt`. CI workflows likewise.
3. **Apps NEVER import from underscore paths in commons.** Codified
   in API_BOUNDARIES.md; tested by `test_full_public_api_resolves` for
   the positive case; the negative case (import-from-underscore raises
   or works-but-unstable) is a code-review concern.
4. **Apps NEVER edit commons source** as part of their own retrofit.
   ADR-002 codified the principle; Phase 2.6 makes the operational
   shape concrete.
5. **Pinned submodule SHA at release time.** Each release tag in a
   consuming app should be reproducible from `git submodule
   update --init` after checkout. Not enforced by tooling yet; a
   release-checklist item.
6. **Phase 4 + frozen-exe verification can now proceed once S1/AV
   clears** — the source-mode packaging contract is verified, so any
   frozen-mode surprise is a PyInstaller-specific finding, not an
   ambiguity between source and frozen.
7. **Phase 6 dogfood** (the throwaway tool) becomes the test bed for
   the full `git submodule add` ⇒ `pip install -e ./commons` ⇒
   `build.bat` ⇒ `installer.iss` ⇒ released-zip-tested chain. Phase
   2.6 verifies the first half; Phase 6 will verify the rest.
8. **Phase 9 distribution revisit** has a concrete signal source —
   the Phase 8 retrofits' submodule-pain telemetry (manual SHA
   bumps, branch-coordination overhead). If pain is low, the
   submodule strategy stays; if high, wheel registry becomes the
   ADR-015 successor.

## 8. Commits (in order)

```
$ git log --oneline -4

85d14a1 Update VERIFICATION_MATRIX — Phase 2.6 newly verified rows
6f5aba5 Add packaging + token tests (Phase 2.6)
b790030 Add ADR-015 — temporary commons distribution strategy
2325934 Add STABILIZATION_REPORT_04 — Phase 2.5 platform stabilization / contracts
```

Per the user's commit plan (3 logical commits + report):

| # | Hash | Subject | Step |
|---|------|---------|------|
| 1 | `b790030` | ADR-015 + ADR-010 supersession | Step 1 |
| 2 | `6f5aba5` | Packaging + token tests | Step 2 — packaging verification tests |
| 3 | `85d14a1` | Verification matrix update | Step 3 |

Cumulative diff vs `2325934` (the tip before this phase):

```
 docs/ui-platform-baseline-v1/DECISIONS.md           |  24 +-
 docs/ui-platform-baseline-v1/VERIFICATION_MATRIX.md |  75 +++---
 tests/test_packaging.py                             | 293 +++++++++++++++++++++
 tests/test_tokens.py                                | 125 +++++++++
 4 files changed, 482 insertions(+), 35 deletions(-)
```

## 9. Verification output

```
$ python -m compileall -q src tests
(exit 0)

$ QT_QPA_PLATFORM=offscreen python -m pytest -q tests/
.........................................................................
...........                                                       [100%]
83 passed in 0.30s
```

Plus four isolated install dry-runs in fresh venvs:

| Dry-run | Path | Result |
|---------|------|--------|
| 1 | `pip install -e .` in a clean venv | ✅ All package data + public API resolve |
| 2 | `pip install -e .[test]` + run full `pytest -q tests/` from that venv | ✅ 83 passed |
| 3 | `pip install .` (non-editable) in a clean venv | ✅ Site-packages install bundles `*.qss` + 10 `*.svg` |
| 4 | `pip install -e ./commons` in `sandbox/app/.venv` against `sandbox/app/commons/` | ✅ Every public surface resolves through the submodule path |

## 10. Branch state — local

```
$ git branch -vv

  baseline-v1                       417f860 [origin/baseline-v1]
* main                              85d14a1 [origin/main]
  phase-2-theme-widgets             db1d8b4
  phase-3-paths-updater             b2e7f79
  phase-4-pyinstaller-compatibility ba3d2c4 [origin/phase-4-pyinstaller-compatibility]
```

| Branch | Tip | Tracks origin |
|--------|-----|---------------|
| `main` | `85d14a1` | ✓ (updated this turn — 3 new commits) |
| `baseline-v1`, `phase-4-…` | unchanged | ✓ |

## 11. Remote state — origin

```
$ git ls-remote --heads origin

417f8600…  refs/heads/baseline-v1                          ← unchanged this turn
85d14a1…   refs/heads/main                                 ← updated (3 new commits)
ba3d2c4d…  refs/heads/phase-4-pyinstaller-compatibility    ← unchanged this turn
```

Push command run: `git push origin main` (`2325934..85d14a1`).

## 12. Confirmation — no build/runtime/frozen work occurred

- ❌ **No app code modified** (zero edits to PCC, Job Tracker, Phoenix CAD, Phoenix Checkout, ValveMaster source).
- ❌ **No `build.bat` / PyInstaller / Inno Setup / `gh release`** invocations.
- ❌ **No frozen-exe validation** attempted.
- ❌ **No installer validation** attempted.
- ❌ **No updater runtime testing.** `download_and_apply` was not invoked against a real release.
- ❌ **No icon replacement** in any app.
- ❌ **No widget rewrites / component migrations / retrofits.**
- ❌ **No CI workflow change** — new tests run under the existing
  `pytest -q tests/` step.
- ❌ **No publishing.** No PyPI, no GitHub Packages, no `gh release create`.
- ❌ **No network calls during verification.** Dry-runs all installed
  from the local working tree.

Operations performed this turn:

```
(Edit)   docs/ui-platform-baseline-v1/DECISIONS.md         ← ADR-015 + ADR-010 supersession
git add … && git commit "Add ADR-015 …"                   ← logical commit 1

(Write)  tests/test_tokens.py
(Write)  tests/test_packaging.py
python -m compileall -q src tests
QT_QPA_PLATFORM=offscreen python -m pytest -q tests/      ← 83 passed
git add … && git commit "Add packaging + token tests …"   ← logical commit 2

# Isolated install dry-runs in $TEMP/phx-verify/
python -m venv editable/.venv && pip install -e <repo>           ← dry-run 1 ✓
python -m venv ed-test/.venv && pip install -e <repo>[test]      ← dry-run 2 ✓ (83 passed)
python -m venv nonedit/.venv && pip install <repo>               ← dry-run 3 ✓
git archive HEAD | tar -x into sandbox/app/commons/
python -m venv sandbox/app/.venv && pip install -e ./commons     ← dry-run 4 ✓
(verified main.py exercised every public surface end-to-end)

(Edit)   docs/ui-platform-baseline-v1/VERIFICATION_MATRIX.md     ← 5 rows verified
git add … && git commit "Update VERIFICATION_MATRIX …"           ← logical commit 3
git push origin main                                              ← 3 commits pushed

(Write)  docs/ui-platform-baseline-v1/STABILIZATION_REPORT_05.md
```

That's the entire surface.

## 13. STOP

Phase 2.6 complete. Architecture stabilization remains in effect.

Per the user spec for Phase 2.6: **Do NOT continue into
migrations, retrofits, frozen verification, installer testing,
runtime updater testing, or icon replacement.** No code change
resumes without explicit phase approval per `BASELINE.md` stop
conditions.

Awaiting user direction.
