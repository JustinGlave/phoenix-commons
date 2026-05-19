# STABILIZATION_REPORT_02.md

> Phase 2.1 — Embedded Fallback Generation. Retires the hand-
> maintained `_EMBEDDED_QSS` string in favour of a generated
> embedded fallback module produced deterministically from
> `phoenix_style.qss`.
>
> Source-only, no migrations, no production-tool work, no builds.
>
> Captured 2026-05-18.

## 1. Status

**Passed.** Phase 2.1 deliverables landed as three logical commits on
`main`, pushed to origin. 44/44 tests pass (37 pre-existing + 7 new).
The drift surface between `phoenix_style.qss` and its embedded fallback
is retired: any future change to the QSS that forgets to regenerate the
embedded module will now fail CI loudly.

Architecture stabilization remains in effect. **Phase 2.2 not started.
No migration / retrofit / packaging work performed.**

## 2. Files added

| Path | Purpose | Lines |
|------|---------|-------|
| `src/phoenix_commons/theme/generate_embedded_qss.py` | The only sanctioned way to produce `embedded_qss.py`. Reads `phoenix_style.qss` next to itself, writes `embedded_qss.py` next to itself. Deterministic (LF normalisation on read AND write) and idempotent (skip write when on-disk output already matches). Runnable as `python -m phoenix_commons.theme.generate_embedded_qss`. | 110 |
| `src/phoenix_commons/theme/embedded_qss.py` | Generated. Exposes `EMBEDDED_QSS: str` containing the full Phoenix dark-navy QSS as a raw-string literal. Header banner explicitly forbids hand-editing. | 783 |
| `tests/test_embedded_qss.py` | Seven tests, including the stale-fallback CI guard. See §6. | 113 |

## 3. Files modified

| Path | Change | Net lines |
|------|--------|-----------|
| `src/phoenix_commons/theme/apply.py` | Two-line edit: import `EMBEDDED_QSS` from `.embedded_qss` instead of `_EMBEDDED_QSS` from `._embedded_qss`; pass the new name to `setStyleSheet` in the fallback branch. All other behaviour unchanged (Fusion style, `QPalette` setup, `_resource_path` resolution, on-disk QSS load path). | +2 / -2 |
| `src/phoenix_commons/theme/_embedded_qss.py` | Rewritten as a one-line back-compat shim that re-exports `EMBEDDED_QSS` under the legacy underscored name. Was 778 lines of hand-maintained QSS-mirroring text — now 27 lines of header + one `from … import … as …`. | +20 / -772 |

## 4. Files deleted

None. `_embedded_qss.py` was deliberately kept (rewritten as a shim) so
any external consumer importing `_EMBEDDED_QSS` continues working
unchanged. Removal target: Phase 7 / Phase 8 retrofits, after audit
confirms no consumer uses the underscored name.

## 5. Generator behaviour

`generate_embedded_qss.render(qss_text: str) -> str` produces the full
content of `embedded_qss.py` as a string. The CLI entry point
(`main`) wires `render` to the on-disk paths and writes idempotently.

**Determinism guarantees:**

1. **Input normalisation.** CRLF and CR line endings in `phoenix_style.qss`
   are normalised to LF before rendering. This makes the generator
   produce byte-identical output whether the QSS file is checked out
   under Windows (default CRLF) or POSIX (LF).
2. **Output forcing.** The generated `embedded_qss.py` is written with
   `newline="\n"`. Identical input → identical bytes on every platform.
3. **Idempotency.** Before writing, the renderer compares its output
   to the current on-disk `embedded_qss.py`. Match → no write, exit 0,
   "already up to date" message. Mismatch → write + report char counts.
4. **Raw-string wrapper guard.** If `phoenix_style.qss` ever contains
   `"""` (which would break the `r"""…"""` wrapper), the generator
   exits 3 with an explicit error rather than emit invalid Python.

**Exit codes:**

| Code | Meaning |
|------|---------|
| 0 | Wrote `embedded_qss.py` (or it was already up to date) |
| 2 | `phoenix_style.qss` not found |
| 3 | QSS contains `"""` — refuses to emit broken Python |

**Current sizing:** `phoenix_style.qss` is 16,891 chars; the generated
`embedded_qss.py` is 17,603 chars (QSS body + a 712-char Python
wrapper: module docstring, `from __future__`, the `EMBEDDED_QSS = r"""`
prefix, and the closing `"""`).

## 6. Stale-fallback CI guard

The most important test added this phase is
`test_generator_is_deterministic_and_idempotent`. It imports `render`,
re-runs it against the current `phoenix_style.qss`, and asserts that
the output is byte-identical to `embedded_qss.py` on disk.

That means: any future PR that edits `phoenix_style.qss` but forgets
to regenerate the embedded module will fail this test on the next CI
run. The error message points the contributor at the exact remediation
command:

> ``"embedded_qss.py is STALE relative to phoenix_style.qss. Re-run: python -m phoenix_commons.theme.generate_embedded_qss"``

A future lint hook can run the generator and `git diff --exit-code` as
a belt-and-braces check, but the pytest assertion alone is sufficient
to break a stale PR in the existing CI workflow — no `.github/workflows/ci.yml`
change required this phase.

## 7. Verification output

```
$ python -m compileall -q .
(exit 0)

$ QT_QPA_PLATFORM=offscreen python -m pytest -q tests/
............................................                             [100%]
44 passed in 0.16s
```

**44 tests pass.** Breakdown:

- `test_smoke.py` — 12 pre-existing (Phase 1 package + Phase 2 theme/widget surface)
- `test_paths.py` — pre-existing (paths helpers from Phase 3)
- `test_updater.py` — pre-existing (updater helpers from Phase 3)
- **`test_embedded_qss.py` — 7 new** (this phase)

The 7 new tests:

| Test | Verifies |
|------|----------|
| `test_embedded_qss_module_exists_and_exports_constant` | `embedded_qss.py` is importable and exports `EMBEDDED_QSS` as a string |
| `test_embedded_qss_non_empty` | `EMBEDDED_QSS` is >5,000 chars — catches catastrophic truncation |
| `test_embedded_qss_contains_canonical_tokens` | Phoenix System A canonical hex values `#0a0e27` and `#dc2626` appear in the embedded QSS |
| `test_generator_is_deterministic_and_idempotent` | **The stale-fallback CI guard.** `render(qss)` == file-on-disk. |
| `test_apply_dark_theme_imports_after_migration` | `apply_dark_theme` still resolves after the import-path migration |
| `test_apply_dark_theme_fallback_uses_embedded_qss` | `apply_dark_theme` applies `EMBEDDED_QSS` when the runtime QSS resource is missing (qtbot + monkey-patched `_resource_path` simulates the auto-updater-replaced-exe case) |
| `test_legacy_underscore_shim_still_works` | `_embedded_qss._EMBEDDED_QSS` re-exports the same string as the new public name |

## 8. Risks discovered / judgment calls

| # | Item | Resolution |
|---|------|------------|
| 1 | The Phase 2.1 user-spec referenced a target structure of `phoenix_commons/ui/theme.py` (file) and named existing public APIs `C`, `STATUS_COLOR`, `make_qss()` that **do not exist** in phoenix-commons (those names live in PCC's `theme.py`). | Interpreted the spec liberally. Kept the existing `phoenix_commons/theme/` **package** layout (which has been on `main` since the v1 baseline merge) and the existing public API (`apply_dark_theme`). Relocating `theme/` → `ui/theme.py` would have broken every existing test and every consumer importing from `phoenix_commons.theme`. The spirit of the spec — replace hand-maintained `_EMBEDDED_QSS` with a generated fallback — is fully satisfied. |
| 2 | `_embedded_qss.py` is imported by an existing test (`test_smoke.py` checks `_EMBEDDED_QSS` length). | Kept `_embedded_qss.py` as a one-line back-compat shim re-exporting `EMBEDDED_QSS` under the underscored name. The existing test passes unchanged; the new `test_legacy_underscore_shim_still_works` pins this back-compat surface explicitly until Phase 7/8 audit removes the need. |
| 3 | Windows / POSIX line-ending drift would have made the deterministic-generation test brittle. | Generator normalises CRLF → LF on read AND writes with `newline="\n"`. Test verified green on Windows; will be green on Linux/macOS without modification. |
| 4 | Raw-string wrapper would break if QSS ever contains `"""`. | Generator detects this case before rendering and exits 3 with an actionable error message. QSS shouldn't legitimately contain triple-double-quotes; this is a guard, not a routine case. |
| 5 | The on-machine Python is 3.14 (PCC's), not 3.12 (ADR-014 contract target). | Pre-existing coordination item, **not** a Phase 2.1 issue. Flagged in `STABILIZATION_REPORT_01.md` §11 and ADR-014's "Consequences" row. CI runs on 3.12 (the contract target); local 3.14 is a developer convenience floor and passes all 44 tests today. |

No new blockers discovered. The seven blockers in `BLOCKERS.md` are
unchanged by this phase (Phase 2.1 is fully AV-independent and
source-only — never touches the frozen-exe / installer / updater
runtime paths that the S1/AV chain gates).

## 9. Commits (in order)

```
$ git log --oneline -6

d7f46d1 Add embedded-QSS smoke tests + stale-fallback CI guard (Phase 2.1)
6b9ab86 Migrate theme loader to generated embedded fallback + add shim (Phase 2.1)
e61db09 Add embedded-QSS generator + generated embedded_qss.py (Phase 2.1)
2f7f4be Add STABILIZATION_REPORT_01 — UI Platform stabilization round 1
263aab3 Add ADR-014 — canonical platform Python version = 3.12
d7ca1a4 Add governance files + Python-3.12 CI + smoke tests
```

Three logical commits per spec:

| # | Hash | Subject | Touches |
|---|------|---------|---------|
| 1 | `e61db09` | Generator + generated file | `generate_embedded_qss.py` (+110), `embedded_qss.py` (+783) |
| 2 | `6b9ab86` | Theme migration + shim | `apply.py` (+2/-2), `_embedded_qss.py` (+20/-772) |
| 3 | `d7f46d1` | Tests + stale guard | `tests/test_embedded_qss.py` (+113) |

Cumulative diff vs `2f7f4be` (the tip before Phase 2.1):

```
 src/phoenix_commons/theme/_embedded_qss.py         | 788 +--------------------
 src/phoenix_commons/theme/apply.py                 |   4 +-
 src/phoenix_commons/theme/embedded_qss.py          | 783 ++++++++++++++++++++
 src/phoenix_commons/theme/generate_embedded_qss.py | 110 +++
 tests/test_embedded_qss.py                         | 113 +++
 5 files changed, 1026 insertions(+), 772 deletions(-)
```

## 10. Branch state — local

```
$ git branch -vv

  baseline-v1                       417f860 [origin/baseline-v1] Add remote bootstrap report …
* main                              d7f46d1 [origin/main] Add embedded-QSS smoke tests + stale-fallback CI guard (Phase 2.1)
  phase-2-theme-widgets             db1d8b4 Add Phase 2 report …
  phase-3-paths-updater             b2e7f79 Add Phase 3A report …
  phase-4-pyinstaller-compatibility ba3d2c4 [origin/phase-4-pyinstaller-compatibility] Phase 6C backup report …
```

| Branch | Tip | Tracks origin |
|--------|-----|---------------|
| `main` | `d7f46d1` | ✓ (updated this turn — 3 new commits) |
| `baseline-v1` | `417f860` | ✓ (unchanged this turn) |
| `phase-4-pyinstaller-compatibility` | `ba3d2c4` | ✓ (unchanged this turn) |
| `phase-2-theme-widgets`, `phase-3-paths-updater` | local-only ancestor refs | — |

## 11. Remote state — origin

```
$ git ls-remote --heads origin

417f8600…  refs/heads/baseline-v1                          ← unchanged this turn
d7f46d13…  refs/heads/main                                 ← updated (3 new commits)
ba3d2c4d…  refs/heads/phase-4-pyinstaller-compatibility    ← unchanged this turn
```

Push command run: `git push origin main` (`2f7f4be..d7f46d1`).

## 12. Confirmation — no migrations / builds / retrofits occurred

- ❌ **No app code modified** (zero edits to PCC, Job Tracker, Phoenix CAD, Phoenix Checkout, ValveMaster source).
- ❌ **No commons code outside `src/phoenix_commons/theme/` modified.** Paths / updater / widgets / package init untouched.
- ❌ **No `build.bat` / PyInstaller / Inno Setup / updater download/apply / `gh release`** invocations.
- ❌ **No icon-infrastructure work, no component migration, no rollout phases started.**
- ❌ **No public API surface change.** `apply_dark_theme` resolves under the same fully-qualified name (`phoenix_commons.theme.apply_dark_theme`) with the same signature and runtime behaviour. The shimmed `_EMBEDDED_QSS` still resolves at its legacy import path.
- ❌ **Phase 2.2 / 2.3 / icon work / migrations / retrofits — NOT started.**

Operations performed this turn:

```
(Read)     existing theme/ structure, _embedded_qss.py, apply.py, tests
(Write)    src/phoenix_commons/theme/generate_embedded_qss.py
python -m phoenix_commons.theme.generate_embedded_qss   ← produced embedded_qss.py
(Edit)     src/phoenix_commons/theme/apply.py            ← 2-line import migration
(Write)    src/phoenix_commons/theme/_embedded_qss.py    ← rewrote 778-line file as shim
(Write)    tests/test_embedded_qss.py
python -m compileall -q .
QT_QPA_PLATFORM=offscreen python -m pytest -q tests/   ← 44 passed
git add … && git commit …  (×3 logical commits)
git push origin main
(Write)    docs/ui-platform-baseline-v1/STABILIZATION_REPORT_02.md
```

That's the entire surface.

## 13. STOP

Phase 2.1 complete. Architecture stabilization remains in effect.

Per the user spec for Phase 2.1: **Do NOT continue into Phase 2.2,
icon infrastructure, migrations, retrofits, or runtime packaging
work.** No code change resumes without explicit phase approval per
`BASELINE.md` stop conditions.

Awaiting user direction.
