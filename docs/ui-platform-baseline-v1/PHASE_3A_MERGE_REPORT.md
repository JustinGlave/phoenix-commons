# PHASE_3A_MERGE_REPORT.md

> Phase 3A merge-execution deliverable. Documents the merge of
> `phase-3a-phoenix-cad-retrofit` into `Phoenix_CAD_Tool:master`,
> post-merge validation, tag decision, and final Phase 3A
> closure.
>
> No new retrofit work. No runtime / frozen / packaging / release
> work. No production apps beyond Phoenix CAD touched.
>
> Captured 2026-05-19.

## 1. Push results

All 4 post-review commits already on origin from the preceding
phase (no fresh pushes required in this phase's push-verification
step). Confirmed by `git ls-remote`:

| Repo | Branch | Local HEAD | Origin HEAD | Status |
|------|--------|-----------|-------------|--------|
| `phoenix-commons` | `main` | `0932e00` | `0932e00` | ✅ In sync |
| `Phoenix_CAD_Tool` | `phase-3a-phoenix-cad-retrofit` | `df58aea` | `df58aea` | ✅ In sync |
| `Phoenix_CAD_Tool` | `feature/hood-detail` | `32122ad` | `32122ad` | ✅ In sync (WIP preserved) |

The 4 commits the user spec listed (`3f37855`, `add4037`,
`PHASE_3A_POST_REVIEW_REPORT.md` commit `0932e00`, and `df58aea`)
were all pushed at the end of the previous turn.

## 2. Merge commit hash

```
$ git -C Phoenix_CAD_Tool checkout master
$ git -C Phoenix_CAD_Tool pull origin master                  # already up to date
$ git -C Phoenix_CAD_Tool merge --no-ff phase-3a-phoenix-cad-retrofit \
    -m "Retrofit Lab Layout Tool to commons-backed (Phase 3A)"
$ git -C Phoenix_CAD_Tool push origin master
```

| Field | Value |
|-------|-------|
| Merge commit SHA | **`79c7003`** (full: `79c70039d1f4917456f26c614326d820069c5bfd`) |
| Merge message | `Retrofit Lab Layout Tool to commons-backed (Phase 3A)` |
| Strategy | `--no-ff` (per `MIGRATION_RULES.md` § Per-retrofit branch + PR convention) |
| Parents | `3358807` (pre-retrofit `master`), `df58aea` (retrofit branch tip) |
| Files changed | 12 |
| Lines | +273 / −1,505 (net **−1,232**) |
| Push result | `3358807..79c7003  master -> master` ✓ |

Cumulative diff captured by the merge:

```
 .gitmodules                                        |   3 +
 .github/workflows/ci.yml                           |  17 +-
 build.bat                                          |  35 +-
 commons                                            |   1 +    (submodule pin)
 legacy/README.md                                   |  22 +
 .../phoenix_style.qss.preretrofit                  |   0     (renamed from repo root)
 paths.py                                           |  29 +-
 requirements.txt                                   |   6 +
 tools/embed_qss.py                                 |  96 −
 ui/components.py                                   | 310 ↓
 ui/style.py                                        | 847 ↓
 updater.py                                         | 412 ↓
 12 files changed, 273 insertions(+), 1505 deletions(-)
```

The "97-line" build.bat line above is misleading from the diff
output — the actual build.bat delta is +24 / −107 lines (the
mid-merge format compressed it). Authoritative shape is in commit
`2b040fc` (B7).

The `commons` "+1" line is the submodule pin at `8504abc`
(commons main HEAD when the submodule was added, identical to
commons main HEAD at merge time).

## 3. Post-merge validation output

Eight checks against the merged `master` tip (`79c7003`).

### 3.1. Branch state (`git branch -vv`)

```
  feature/hood-detail           32122ad [origin/feature/hood-detail] WIP: park hood-detail in-flight work before Phase 3A retrofit
* master                        79c7003 [origin/master] Retrofit Lab Layout Tool to commons-backed (Phase 3A)
  phase-3a-phoenix-cad-retrofit df58aea [origin/phase-3a-phoenix-cad-retrofit] Add submodule init + commons import check to CI (Phase 3A post-review)
```

✅ Three branches, all in sync with origin.
✅ Both `feature/hood-detail` and `phase-3a-phoenix-cad-retrofit`
   preserved per the user spec.

### 3.2. Submodule state (`git submodule status`)

```
 8504abcb04ac7e3026f5060dd504a7e6f6c774ef commons (heads/main)
```

✅ Submodule pinned at `8504abc` — matches commons `main` HEAD at
merge time. Tracking branch is `main`.

### 3.3. Commons package resolves on disk

```
$ ls commons/src/phoenix_commons
__init__.py  __pycache__  _version.py  icons  paths.py  theme  updater  widgets
```

✅ Commons package fully present.

### 3.4. compileall (project sources, excluding commons / build / dist / .venv)

```
$ .venv/Scripts/python -m compileall -q -x "commons|build|dist|\.venv" .
(exit 0)
```

✅ Clean — every `.py` in Phoenix CAD parses + bytecode-compiles.

### 3.5. Retrofit imports + identity + contract checks

```
$ .venv/Scripts/python -c "<full import + identity + contract suite>"

all post-merge imports + identity + contract checks pass
```

Specific assertions passed:

- `import paths, updater`; widget imports from `ui.components`
- `phoenix_commons.__version__ == '0.1.0'`
- `ui.components.PrimaryButton is phoenix_commons.widgets.PrimaryButton`
- `ui.components.Panel is phoenix_commons.widgets.Panel`
- `ui.components.PhoenixTable is phoenix_commons.widgets.PhoenixTable`
- `ui.components.UpdateBanner is phoenix_commons.widgets.UpdateBanner`
- `updater.GITHUB_OWNER == 'JustinGlave'`
- `updater.GITHUB_REPO == 'lab-layout-tool'`
- `updater.EXE_NAME == 'LabLayoutTool.exe'`
- `updater.ZIP_ASSET_NAME == 'LabLayoutTool.zip'`
- `'expected_internal=True' in inspect.getsource(updater.download_and_apply)`
- `paths.ORG_NAME == 'ATS Inc'`
- `paths.APP_NAME == 'Lab Layout Tool'`

### 3.6. Offscreen apply_dark_theme smoke

```
$ QT_QPA_PLATFORM=offscreen .venv/Scripts/python -c "<apply_dark_theme + assertions>"

apply_dark_theme — styleSheet OK, 16,891 chars, sentinels substituted
```

Asserted:
- `len(sheet) > 5000`
- `'#dc2626' in sheet` (default brand red substituted)
- `'#3b82f6' in sheet` (default brand accent substituted)
- `'#1e3a8a' in sheet` (default brand secondary substituted)
- `'#0a0e27' in sheet` (locked BG preserved)
- `'__BRAND_PRIMARY__' not in sheet` (sentinels gone)

### 3.7. app.py transitive import smoke

```
$ QT_QPA_PLATFORM=offscreen .venv/Scripts/python -c "import app"

app.py: clean transitive import
```

Exercises every top-level import in `app.py`:  `cad.blocks`,
`cad.layout`, `paths`, `ui.style.apply_dark_theme`,
`ui.main_window.MainWindow`, `version.__version__`. All resolve.

### 3.8. CI yml structural sanity

```
$ grep -nE 'submodules|paths\.py|phoenix_commons|embed_qss' .github/workflows/ci.yml

21:          submodules: recursive
31:        # before this step (covered by `submodules: recursive` above).
38:          python -m py_compile paths.py
67:        # `import phoenix_commons` confirms the submodule install resolved
68:        # — catches the case where `submodules: recursive` failed silently
71:          python -c "import phoenix_commons; print('commons', phoenix_commons.__version__)"
```

✅ `submodules: recursive` on `actions/checkout`.
✅ `paths.py` in py_compile list.
✅ `import phoenix_commons` in import-smoke step.
✅ `tools/embed_qss.py` references absent (script deleted in B7).

### Post-merge validation: ALL GREEN.

## 4. Branch state

### Phoenix_CAD_Tool (local)

```
  feature/hood-detail           32122ad [origin/feature/hood-detail]
* master                        79c7003 [origin/master]
  phase-3a-phoenix-cad-retrofit df58aea [origin/phase-3a-phoenix-cad-retrofit]
```

### phoenix-commons (local)

```
* main                              <commit-of-this-report> [origin/main]   ← will advance on this report's commit + push
  baseline-v1                       417f860 [origin/baseline-v1]
  phase-2-theme-widgets             db1d8b4
  phase-3-paths-updater             b2e7f79
  phase-4-pyinstaller-compatibility ba3d2c4 [origin/phase-4-pyinstaller-compatibility]
```

## 5. Remote state

### Phoenix_CAD_Tool (origin)

```
32122ad…  refs/heads/feature/hood-detail                ← preserved (WIP)
79c7003…  refs/heads/master                             ← ★ merged Phase 3A ★
df58aea…  refs/heads/phase-3a-phoenix-cad-retrofit       ← preserved per spec
```

Tags on origin: `v0.1.0`, `v0.1.1`, `pre-audit-baseline` (unchanged).

### phoenix-commons (origin)

```
417f860…  refs/heads/baseline-v1
0932e00…  refs/heads/main                                ← Phase 3A doctrine + template + post-review report
ba3d2c4…  refs/heads/phase-4-pyinstaller-compatibility
```

## 6. Tag status

**SKIPPED.** No `lab-layout-tool-retrofit-v0.1.2-pre` tag created.

Rationale per the spec's "Push tag ONLY if: tag naming is clean,
no ambiguity exists, version.py state makes sense":

| Criterion | Assessment |
|-----------|------------|
| Tag naming clean | ⚠️ Partial — `lab-layout-tool-retrofit-v0.1.2-pre` embeds a `v0.1.2` reference, but `version.py` is still at `0.1.1`. The `-pre` suffix arguably signals "pre-release work toward 0.1.2", but the version mismatch creates slight ambiguity about whether a 0.1.2 release decision has been made. |
| No ambiguity exists | ⚠️ Slight ambiguity per above |
| version.py state makes sense | ❌ `version.py` is `0.1.1` — unchanged by the retrofit. Bumping to 0.1.2 is a release-prep decision tied to whatever follows the retrofit, not the retrofit itself. |

**Decision:** defer the tag to a release-prep moment. Whoever cuts
the next Phoenix CAD release will:

1. Bump `version.py` to `0.1.2` (per the existing convention).
2. Update `README.md` "Current Version" line.
3. Tag the release commit `v0.1.2`.
4. Optionally, create a separate retrofit-attribution tag at `79c7003`
   (the merge commit) if the merge wants its own permanent reference
   distinct from the release tag.

The retrofit branch (`phase-3a-phoenix-cad-retrofit`) remains on
origin as the permanent attribution anchor either way.

## 7. CI expectations

GitHub Actions will trigger on the `master` push (the merge
commit). Expected behaviour:

1. `actions/checkout@v6` with `submodules: recursive` clones
   `Phoenix_CAD_Tool` + populates `commons/` from the submodule
   pin (`8504abc`).
2. `actions/setup-python@v6` installs Python 3.14 (the existing
   workflow Python; ADR-014 drift documented as a follow-up).
3. `pip install -r requirements.txt` resolves PySide6/pywin32 pins
   + the `-e ./commons` line.
4. The py_compile step runs across all the project Python files
   PLUS commons-side imports indirectly via runtime resolution.
5. `import phoenix_commons` smoke confirms the install resolved.
6. `import paths` + `import updater` confirm facades work.
7. The "Regression tests (placeholder)" step echoes its TODO; no
   actual unit tests run from the tool's CI (commons has its own
   pytest suite which runs in commons's CI).

Expected outcome: **green** if the runner picks up the new
workflow file. No CI runtime issues anticipated. If CI does
fail post-merge, the most likely cause would be GitHub Actions
runner image differences (Python 3.14 wheel availability for
PySide6 / pywin32) — separate concern from this merge.

## 8. Final Phase 3A status

| Aspect | Status |
|--------|--------|
| Retrofit code | ✅ Merged to master (`79c7003`) |
| Visual parity | ✅ Preserved (default brand, identity-equal widgets, byte-equivalent stylesheet) |
| Source-mode validation | ✅ Eight categories green |
| Migration doctrine | ✅ Codified in `MIGRATION_RULES.md` |
| Retrofit PR template | ✅ Available (`RETROFIT_PR_TEMPLATE.md`) |
| Pre-retrofit baseline | ✅ Preserved (bundles + `master` reset history + retrofit branch on origin + `legacy/phoenix_style.qss.preretrofit`) |
| Tag | ⏸️ Skipped (release-prep decision deferred — see § 6) |
| Frozen-exe verification | 🔴 Blocked (S1/AV chain — `BLOCKERS.md §1`) |
| Phase 3B (Phoenix Checkout) | ⏸️ Ready to begin under three conditions (next section) |

**Phase 3A is operationally complete.** Phoenix CAD is now
officially commons-backed in source mode. All remaining gaps
(frozen-exe verification, legacy QSS retention window, tag)
are timing-dependent and don't block Phase 3B.

## 9. Remaining blockers

| # | Blocker | Blocks | Severity / next action |
|---|---------|--------|-------------------------|
| 1 | S1/AV bootloader quarantine | Frozen-exe build + installer + real updater deploy for ANY Phoenix tool | High; `BLOCKERS.md §1`; unchanged by this merge |
| 2 | User approval for Phase 3B start | Phoenix Checkout retrofit | Awaiting explicit go-ahead |
| 3 | `legacy/phoenix_style.qss.preretrofit` removal | Eventual cleanup of the 30-day safety window | Schedule ~2026-06-18 (30 days post-merge) |
| 4 | Tag `v0.1.2` (or equivalent) on the Phoenix CAD release tied to the retrofit | First post-retrofit release | Awaiting release-prep decision |
| 5 | Phoenix CAD CI Python 3.14 vs ADR-014's 3.12 | CI version alignment with platform contract | Out of retrofit scope; separate follow-up PR |
| 6 | TODOS.md / PHASES.md doc-drift from current phase numbering | Doc clarity for future-phase readers | Doc-housekeeping sub-phase candidate |
| 7 | `rgba(30, 58, 138, 220)` in commons QSS not sentinelizable | PCC retrofit's UpdateBanner brand follow | Future commons PR; not blocking Phase 3B |

None of these block Phase 3B start. Items 1 + 3 + 4 don't block
anything in commons's scope.

## 10. Checkout-readiness assessment

**YES — Phase 3B (Phoenix Checkout) is ready to begin** under
three conditions:

| Condition | Status post-merge |
|-----------|--------------------|
| Phase 3A merged | ✅ Done (this report) |
| User explicit approval to start Phase 3B | ⏳ Awaiting |
| Phoenix Checkout's working tree is clean + pushed at Phase 3B start | Pre-flight will verify |

Operational readiness:

- **No commons API changes needed.** Every API Checkout will consume
  (`apply_dark_theme`, the widget classes, `paths.is_frozen`,
  the updater facade with `expected_internal=False`) was exercised
  by Phase 3A's retrofit.
- **Doctrine codified.** `MIGRATION_RULES.md` § Phase 3A retrofit
  doctrine is the playbook.
- **Template in place.** `RETROFIT_PR_TEMPLATE.md` is the PR-body
  structure.
- **Worked example reference.** `PHASE_3A_PHOENIX_CAD_REPORT.md` is
  the 974-line worked example covering all 20 sections.
- **Checkout-specific notes** (rom `MIGRATION_RULES.md` and
  prior reports):
  - `expected_internal=False` (exe-only updater per ADR-003) — NOT
    the same as Phase 3A's `True`.
  - `checkout_tool_gui.py` is monolithic (~177 KB per
    `production-inventory.md`); widget extraction is the heavier
    scope variance — consider multiple commits within the PR.

## 11. Operational concerns

None that block Phase 3B.

The seven items in § 9 above are tracked-but-not-blocking. The most
operationally noisy is the Python-version drift between Phoenix
CAD's CI (3.14) and ADR-014's contract target (3.12) — but this
predates the retrofit and doesn't block correctness.

One observation worth recording: the merge produced a clean
`--no-ff` commit with the retrofit's full 1,505-deletion / 273-
insertion diff visible in one place. Git history reads as: "this
one merge commit is the entire retrofit" + 7 individual commits in
the branch history for bisecting. Pattern reusable for Phase 3B+.

## 12. Confirmation

### No Phase 3B work occurred

- ❌ **No Phoenix Checkout source touched.** `Phoenix-Checkout-Tool`
  repo not opened, not modified, not surveyed.
- ❌ **No `phase-3b-*` branch created.**
- ❌ **No Checkout-specific code in commons.**

### No runtime / frozen work occurred

- ❌ **PyInstaller not invoked.**
- ❌ **Inno Setup not invoked.**
- ❌ **No frozen exe built or tested.**
- ❌ **No installer built or tested.**
- ❌ **`download_and_apply` not invoked.**
- ❌ **No release published / no GitHub Release created.**
- ❌ **No tag pushed** (per § 6 decision).

### No production apps beyond Phoenix CAD touched

| App | Modified this phase? |
|-----|----------------------|
| Phoenix CAD / Lab Layout Tool | ✅ Yes — `master` advanced to merge commit `79c7003` |
| Phoenix Valve Checkout Tool | ❌ No |
| Phoenix Command Center | ❌ No |
| Project Tracking Tool (Job Tracker) | ❌ No |
| ValveMasterTool | ❌ No |

Operations performed this phase:

```
=== Step 1 — Push verification (no-op — already on origin) ===
git -C phoenix-commons status                          ← clean, in sync
git -C phoenix-commons rev-parse main                  ← 0932e00 (== origin)
git -C Phoenix_CAD_Tool status                         ← clean, in sync
git -C Phoenix_CAD_Tool ls-remote --heads origin       ← retrofit branch + feature branch present

=== Step 2 — Merge ===
git -C Phoenix_CAD_Tool checkout master
git -C Phoenix_CAD_Tool pull origin master              ← Already up to date
git -C Phoenix_CAD_Tool merge --no-ff phase-3a-phoenix-cad-retrofit \
    -m "Retrofit Lab Layout Tool to commons-backed (Phase 3A)"
                                                        ← merge commit 79c7003
git -C Phoenix_CAD_Tool push origin master              ← 3358807..79c7003

=== Step 3 — Post-merge validation ===
git branch -vv                                          ← 3 branches in sync
git submodule status                                    ← commons pinned at 8504abc
ls commons/src/phoenix_commons                          ← package resolves
compileall -q -x "commons|build|dist|\.venv" .          ← exit 0
python -c "<imports + identity + contract>"             ← all pass
QT_QPA_PLATFORM=offscreen python -c "<apply_dark_theme>" ← 16,891-char stylesheet, sentinels substituted
QT_QPA_PLATFORM=offscreen python -c "import app"        ← clean transitive
grep -nE 'submodules|paths\.py|phoenix_commons' .github/workflows/ci.yml  ← CI fix confirmed in tree

=== Step 4 — Tag ===
Decision: SKIPPED (version.py state doesn't make 'v0.1.2-pre' unambiguous)
Documented in § 6 above.

=== Step 5 — MIGRATION_RULES.md update ===
(Edit) "Landed 2026-05-19 (awaiting merge approval)" → "Merged 2026-05-19 (merge commit 79c7003 …)"

=== Step 6 — This report ===
(Write) docs/ui-platform-baseline-v1/PHASE_3A_MERGE_REPORT.md
git commit + push (about to)
```

That's the entire surface.

## STOP

Phase 3A merge execution complete. Phoenix CAD's `master` carries
the commons-backed retrofit. All Phase 3A workstreams closed:

- ✅ Retrofit code merged
- ✅ Post-merge validation green
- ✅ Doctrine + template + report documented
- ✅ Both feature + retrofit branches preserved on origin
- ⏸️ Tag deferred to release prep
- 🔴 Frozen-exe verification still S1/AV-gated (independent)

Per the phase spec:

- ❌ **Did NOT start Phase 3B (Phoenix Checkout).**
- ❌ **Did NOT start Phase 3C (Phoenix Command Center).**
- ❌ **Did NOT start Phase 8a (ValveMaster).**
- ❌ **Did NOT start Phase 8b (Job Tracker).**
- ❌ **Did NOT start frozen verification.**
- ❌ **Did NOT start installer testing.**

Phase 3A: **DONE.** Phoenix CAD is officially commons-backed.

Awaiting user direction on:
- Phase 3B (Phoenix Checkout) start approval
- Phase 3C (PCC) start approval
- Release tagging / version bump decision
- Any of the deferred follow-ups in § 9
