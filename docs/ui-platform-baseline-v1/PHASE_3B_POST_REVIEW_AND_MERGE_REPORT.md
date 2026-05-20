# PHASE_3B_POST_REVIEW_AND_MERGE_REPORT.md

> Phase 3B post-review and merge-execution deliverable. Documents the
> review of `phase-3b-phoenix-checkout-retrofit`, the doctrine additions
> codified from this retrofit, the merge into `Phoenix-Checkout-Tool:main`,
> post-merge validation, the tag decision, and the final Phase 3B status.
> Companion to `PHASE_3B_PHOENIX_CHECKOUT_REPORT.md` (the retrofit-execution
> deliverable).

---

## 1. Summary

| Item | Value |
|------|-------|
| Tool | Phoenix Valve Checkout Tool |
| Repo | `JustinGlave/Phoenix-Checkout-Tool` |
| Pre-retrofit baseline | `2e03df6` (v1.7.0 tag) |
| Retrofit branch | `phase-3b-phoenix-checkout-retrofit` (preserved on origin) |
| Retrofit-branch tip | `80dace8` (B8 regression fix) |
| Merge commit | `26a4689` on `Phoenix-Checkout-Tool:main` |
| Merge strategy | `--no-ff` (per MIGRATION_RULES § Per-retrofit branch + PR convention) |
| Merge date | 2026-05-19 |
| Submodule pin | `phoenix-commons:70785a2` (code-equivalent to current commons main `0dd1aec`; difference is two doc-only commits) |
| Tag | Intentionally skipped — `version.py` unchanged at `1.7.0`; tag `v1.7.0` already exists at pre-retrofit commit |
| Commons doctrine commit | `0dd1aec` on `phoenix-commons:main` (Phase 3B doctrine additions) |

**Verdict.** Phase 3B merged cleanly with HIGH confidence. Post-merge
validation passed all four exercised rows of the § 10 checklist. Doctrine
was strengthened by four codified additions tied to specific Phase 3B
observations. STOP point per the user's spec was honoured — no PCC,
ValveMaster, or Job Tracker retrofit work started; no frozen-exe build,
PyInstaller, or installer testing performed.

---

## 2. Pre-merge state recap

Before STEP 1 launched the manual-QA pass, the retrofit branch state was:

```
80dace8 Fix regression: re-import os in checkout_tool_backend (Phase 3B B8)    [local-only at start of review]
5153aad Update build.bat — submodule preflight + --collect-all=phoenix_commons (Phase 3B B7)
2630792 Preserve legacy phoenix_style.qss + delete repo-root copy (Phase 3B B6)
61aac52 Retrofit inline widget classes to commons re-exports (Phase 3B B5)
30ca27a Retrofit apply_dark_theme + delete _EMBEDDED_QSS body (Phase 3B B4)
54458c1 Retrofit updater.py — facade check_for_update + keep split API local (Phase 3B B3)
0bb1618 Retrofit checkout_tool_backend._app_data_path to commons (Phase 3B B2)
76f2c23 Add phoenix-commons submodule + editable install + requirements.txt (Phase 3B B1)
2e03df6 v1.7.0 — Bug fixes, None-safety, threaded update install, notes counter   [pre-retrofit baseline]
```

B8 was pushed to origin as the first action of this review (`git push origin
phase-3b-phoenix-checkout-retrofit`, range `5153aad..80dace8`). The branch's
remote state then exactly matched the local tip.

---

## 3. Step 1 — Manual QA findings

Source-mode launch was re-validated post-B8 fix:

```
PID: 43944 (initial QA launch), then 12768 (validation re-run)
MainWindowTitle: "Phoenix Valve Checkout Tool — v1.7.0"
Memory: 177 MB → 187 MB
Process alive ≥ 4s on every launch
```

User-driven manual QA across the 9 priority areas (with extra scrutiny on
the preserved-local paths):

| # | Area | User result |
|---|------|-------------|
| 1 | Dark / Light theme toggle (preserved-local light mode per ADR-011) | ✅ PASS — works, persists via QSettings |
| 2 | Help menu structure | ✅ PASS — 4 items match pre-retrofit exactly (Version History, Email Support, Submit Bug, About). Initial confusion about a "Check for Updates" item was resolved: it has NEVER existed; update flow is auto-on-startup, surfacing an `UpdateBanner` at window-bottom when an update is found. Confirmed by `git diff 2e03df6 80dace8 -- checkout_tool_gui.py` zero hits on `help_menu\|_check_for_updates\|addMenu.*Help\|QAction.*Update`. |
| 3 | Threaded updater responsiveness | ✅ PASS — window not frozen, no crash on the silent no-update path |
| 4 | Menu actions | ✅ PASS |
| 5 | Forms | ✅ PASS |
| 6 | Tables | ✅ PASS |
| 7 | Dialogs | ✅ PASS |
| 8 | QSettings persistence | ✅ PASS |
| 9 | Visual parity (vs pre-retrofit v1.7.0 memory) | ✅ PASS |

**Important caveat about the updater UI banner.** The "actual update
available" UI path (`UpdateBanner` visible + Install / What's New buttons)
could not be exercised because the latest GitHub Release for
`Phoenix-Checkout-Tool` is v1.7.0, matching the local `version.py`. The
silent-no-update path WAS exercised and produced no crash, no UI freeze,
and no resource leak. The full UI banner path is deferred to whatever
post-merge release cuts a v1.8.0 (out of scope per the user's STOP-after
spec).

### 3.1 Pre-QA regression caught (B8)

The first attempt to launch the retrofit branch from `pythonw.exe` crashed
at startup with:

```
File "checkout_tool_backend.py", line 102, in _load
    if not os.path.exists(DATA_FILE):
NameError: name 'os' is not defined.
```

Root cause: the B2 retrofit (`0bb1618`) had removed `import os` from
`checkout_tool_backend.py` because the retrofitted `_app_data_path`
function no longer needed it — but `CheckoutStore._load()` (line 102) and
`_save()` (line 141) still use `os.path.exists()` and `os.replace()`.

B8 (`80dace8`) fixed this with a one-line `import os` re-addition. The
companion removal of `from pathlib import Path` correctly stayed removed
(audited — `Path` had no remaining uses in the file). The fix was pushed
to origin before STEP 1's manual-QA pass resumed.

This regression directly motivated MIGRATION_RULES § 10's new row 11 and
the whole-file import-removal audit rule corollary (see § 5 below).

---

## 4. Step 2 — Retrofit branch audit findings

Comprehensive audit across 11 risk categories:

| # | Risk category | Method | Result |
|---|---------------|--------|--------|
| 1 | Modernization / redesign | 2-hunk diff scan on `checkout_tool_gui.py` (widget region + theme region only) | PASS |
| 2 | Business-logic drift | Grep for menu / form / table / dialog / QSettings / org-name changes | PASS — zero diff outside retrofit zones |
| 3 | Updater contract drift | Grep for `GITHUB_OWNER`/`REPO`/`ZIP_ASSET_NAME`/`EXE_NAME` modifications | PASS — constants unchanged |
| 4 | `expected_internal` regression | Diff inspection of `download_update` / `apply_update`; PowerShell extraction code audit | PASS — `Copy-Item` count = 1; only `EXE_NAME` extracted; no `_internal/` references in executable code (docstring documents the absence) |
| 5 | Extraction snowball | `git diff main..retrofit -- checkout_tool_gui.py` hunk count | PASS — exactly 2 hunks |
| 6 | Commons contamination | `git status` + log on `phoenix-commons:main` during Phase 3B | PASS — only Phase 3B-related doc commits (`bc19432` retrofit report, `0dd1aec` doctrine update). `git diff 70785a2..0dd1aec -- src/ tests/ pyproject.toml` is empty |
| 7 | Hidden light-theme regressions | `apply_light_theme` diff inspection | PASS — intentionally untouched per ADR-011 |
| 8 | User-data path drift | `checkout_tool_backend.DATA_FILE` resolution | PASS — `%APPDATA%\ATS Inc\Phoenix Valve Checkout Tool\data.json` byte-identical |
| 9 | Legacy backup integrity | Byte-diff `2e03df6:phoenix_style.qss` vs `legacy/phoenix_style.qss.preretrofit` | PASS — byte-identical |
| 10 | Identity equality (no widget wrapping) | `is`-comparison on `PrimaryButton`/`SecondaryButton`/`TertiaryButton`/`_PhoenixTable`/`UpdateInfo` | PASS — all 5 are commons class objects, not copies |
| 11 | Static check | `compileall -q -x "(\.venv\|build\|dist\|commons)" .` | PASS (silent) |

### 4.1 Diff surface summary

```
.gitmodules                                          |   3 +
build.bat                                            |  20 +-
checkout_tool_backend.py                             |  20 +-
checkout_tool_gui.py                                 | 210 ++++-----------------
commons                                              |   1 +
legacy/README.md                                     |  22 +++
legacy/phoenix_style.qss.preretrofit                 |   0   (renamed from repo-root)
requirements.txt                                     |  10 +
updater.py                                           | 138 +++++++-------
9 files changed, 181 insertions(+), 243 deletions(-)
```

Net deletion of 62 lines: the retrofit reduced duplication without
expanding the application's source surface.

---

## 5. Step 3 — Doctrine additions codified

Four additions landed on commons main as commit `0dd1aec` ("Codify Phase
3B retrofit doctrine in MIGRATION_RULES (Phase 3B post-review)"). Each is
tied to a specific, proven Phase 3B observation.

### 5.1 § 0. Pre-flight commons-API gap inventory (new section)

**Observation.** Phase 3B's pre-flight discovered two locally-defined
symbols with no clean commons equivalent: (a) Checkout's `apply_light_theme`
(commons is dark-only per ADR-011); (b) the split `download_update` +
`apply_update` API (commons exposes only the combined `download_and_apply`).

**Doctrine added.** Before opening any retrofit branch, the engineer must
produce a gap-inventory table mapping every locally-defined platform
symbol to its commons equivalent (or `—` if none). For every gap, the
user explicitly chooses **A. Keep local** (default) or **B. Add to
commons** (requires evidence of ≥ 2 consumers). The decision per gap is
documented in the retrofit's post-retrofit report.

This step would have caught earlier sessions' false-starts where "retrofit
`updater.py` to commons" was discussed without inventorying which
functions had commons equivalents. The inventory forces the question.

### 5.2 § 1. Local facade strategy — hybrid coexistence (refinement)

**Observation.** Phoenix Checkout's `updater.py` ended up with BOTH
commons-facaded functions (`check_for_update`) and preserved-local
functions (`download_update`, `apply_update`, `download_and_apply`)
side-by-side in the same file. Similarly, the theme region of
`checkout_tool_gui.py` has facaded `apply_dark_theme` next to
preserved-local `apply_light_theme`.

**Doctrine added.** A single local file MAY contain both facade and
preserved-local symbols. Phase 3A's pattern (whole-file facade) is the
stricter subset. Rules for hybrid files: every preserved-local symbol
carries an inline docstring note citing why it's local (ADR reference,
behavioural contract, threading requirement); the pre-flight gap
inventory must list each preserved-local symbol with its Option-A
decision; the post-retrofit report's file-by-file narrative calls out
the hybrid structure.

### 5.3 § 10 row 8 strengthening + new row 11 (validation checklist)

**Observation.** The B8 regression passed `compileall` AND the row 8
import-only smoke (`python -c "import checkout_tool_gui"`). It crashed
only at runtime when `MainWindow.__init__()` constructed a `CheckoutStore`
and that store's `_load()` referenced the missing `os` module. Python's
lazy name resolution made the regression invisible to every static check
in the existing checklist.

**Doctrine added.**
- Row 8 prose clarified: import-only smoke does NOT catch undefined-name
  bugs inside function bodies executed later.
- New row 11: **actual source-mode app launch** with the process verified
  alive ≥ 3 seconds and `MainWindowTitle` matching the expected app title.
- Recommended PowerShell implementation included verbatim.
- Whole-file import-removal audit rule added as corollary: when a
  retrofit removes a top-level `import X`, grep the file for every
  remaining reference before merging.

### 5.4 § 11. Monolith inline-class retrofit pattern (new section)

**Observation.** Phoenix Checkout's `checkout_tool_gui.py` is monolithic
(3,468 lines). Widget classes (`PrimaryButton`, `SecondaryButton`,
`TertiaryButton`, `_PhoenixTable`) are defined INLINE at the top of the
module, not in a separate `ui/components.py`. The Phase 3A whole-file
facade pattern didn't apply.

**Doctrine added.** Replace inline class definitions with a single
`from phoenix_commons.widgets import ...` statement; use import-alias
for naming gaps (`PhoenixTable as _PhoenixTable`); leave every caller
site in the file ENTIRELY untouched. Identity-equality verification per
§ 2 is the gate. Scope discipline forbids extracting the imports to a
new file "while we're here" — that's a future refactor, out of retrofit
scope.

The Phase 3B B5 commit produced a 2-hunk diff in a 3,468-line file. The
pattern is now documented as canonical.

---

## 6. Step 4 — Merge readiness assessment

Formal 7-question assessment (per the user's review spec):

| # | Question | Result | Evidence |
|---|---|---|---|
| 1 | Source-mode launch verified after all fixes (including B8)? | YES | PID 12768, correct title, ≥ 4s alive |
| 2 | Full § 10 validation checklist (11 rows) all green? | YES | All 11 rows passed; row 5 refined to allow docstring mentions of `_internal/` while requiring zero references in executable code |
| 3 | User manual QA passed across the 9 priority areas? | YES | 8 explicit PASS + 1 non-regression clarification (Help menu) |
| 4 | Retrofit branch contained — no business-logic / scope drift? | YES | 9 files changed; 2-hunk diff in the monolith; net -62 lines |
| 5 | Commons contamination? | NO | Only Phase 3B-related doc commits on commons main; src/tests/pyproject diff between submodule pin and current commons main is empty |
| 6 | All B1-B8 commits pushed to origin? | YES | `5153aad..80dace8 phase-3b-phoenix-checkout-retrofit -> phase-3b-phoenix-checkout-retrofit` confirmed |
| 7 | Phase 3B doctrine additions reviewed + landed on commons main? | YES | Commit `0dd1aec` on `phoenix-commons:main` |

**Verdict: HIGH confidence.** User explicitly authorized merge via
AskUserQuestion.

---

## 7. Step 5 — Merge execution

Command sequence executed:

```bash
git checkout main
git pull --ff-only origin main          # already up-to-date
git merge --no-ff phase-3b-phoenix-checkout-retrofit \
    -m "Retrofit Phoenix Valve Checkout Tool to commons-backed (Phase 3B)"
git push origin main
```

Result: merge commit `26a4689` on `Phoenix-Checkout-Tool:main`. Push
range: `2e03df6..26a4689`. Remote tip confirmed via
`git ls-remote origin main` = `26a4689b9fd59c796bb9d6aa02b3094a885b7343`.

A benign warning surfaced during checkout (`unable to rmdir 'commons':
Directory not empty`) — harmless, caused by the submodule working tree
still being present while git switched the gitlink entry. The merge
itself succeeded and the submodule pointer (mode `160000`) is correctly
present in the merge commit.

The retrofit branch `phase-3b-phoenix-checkout-retrofit` was **preserved
on origin** (not deleted) per MIGRATION_RULES § Per-retrofit branch + PR
convention. It serves as the auditable history of the retrofit work.

---

## 8. Step 6 — Post-merge validation

Subset of the § 10 checklist re-run on `Phoenix-Checkout-Tool:main` after
the merge landed. Per the user's spec, no PyInstaller / installer / frozen
verification was performed.

| Row | Check | Result |
|-----|-------|--------|
| 1 | `compileall -q -x "(\.venv\|build\|dist\|commons)" .` | PASS (silent) |
| 2 | Imports clean (`checkout_tool_backend`, `updater`, `checkout_tool_gui`, `phoenix_commons.widgets/theme/updater/paths`) | PASS |
|   | Identity check: `gui.PrimaryButton is commons.PrimaryButton` | True |
|   | Identity check: `gui._PhoenixTable is commons.PhoenixTable` | True |
|   | Identity check: `updater.UpdateInfo is commons.UpdateInfo` | True |
|   | `DATA_FILE` resolution | `%APPDATA%\Roaming\ATS Inc\Phoenix Valve Checkout Tool\data.json` (byte-identical to pre-retrofit) |
| 7 | `QT_QPA_PLATFORM=offscreen` `apply_dark_theme(app)` | PASS — styleSheet 16,891 bytes; `#0a0e27`/`#dc2626`/`#3b82f6` all present; no `__BRAND_*` sentinels |
| 11 | Actual app launch via `pythonw.exe` + 4s alive | PASS — PID 42644, title "Phoenix Valve Checkout Tool — v1.7.0", 186MB |

---

## 9. Step 7 — Tag decision

**Decision: SKIP.**

Reasoning:

- `version.py` is unchanged at `1.7.0` after the retrofit.
- The tag `v1.7.0` already exists on origin at the pre-retrofit commit `2e03df6`.
- No new release version has been claimed by this merge.
- The user's spec explicitly said: *"Skip if version state ambiguous (Phase 3A precedent). Do NOT invent release version casually."*
- Inventing a `phoenix-checkout-retrofit-v1.7.0-post` tag would be exactly the casual invention the spec forbids.

Phase 3A precedent (Lab Layout Tool at v0.1.1) chose the same decision
for the same reason. The next real Checkout release — whenever a feature
or fix justifies a version bump — will get a normal `vX.Y.Z` tag at that
release commit, naturally rolling the Phase 3B work in.

---

## 10. Step 8 — MIGRATION_RULES status row update

`MIGRATION_RULES.md` § Migration order row for Phase 3B updated:

**Before** (Phase 3B doctrine commit `0dd1aec`):

```
| **3B** | Phoenix Checkout Tool | `phase-3b-phoenix-checkout-retrofit` | 🔵 Retrofit complete + reviewed; merge pending. Retrofit work: B1–B7 (`76f2c23`..`5153aad`) + regression fix B8 (`80dace8`). Doctrine additions in this document codified from `PHASE_3B_PHOENIX_CHECKOUT_REPORT.md` + `PHASE_3B_POST_REVIEW_AND_MERGE_REPORT.md`. |
```

**After** (this commit, post-merge):

```
| **3B** | Phoenix Checkout Tool | `phase-3b-phoenix-checkout-retrofit` | ✅ Merged 2026-05-19 (merge commit `26a4689` on `Phoenix-Checkout-Tool:main`). Retrofit work: B1–B7 (`76f2c23`..`5153aad`) + regression fix B8 (`80dace8`). Doctrine additions in this document codified from `PHASE_3B_PHOENIX_CHECKOUT_REPORT.md` + `PHASE_3B_POST_REVIEW_AND_MERGE_REPORT.md`. Retrofit branch preserved on origin per MIGRATION_RULES § Per-retrofit branch + PR convention. Tag intentionally skipped — `version.py` unchanged at 1.7.0; `v1.7.0` already exists at pre-retrofit commit; no new release version claimed by this merge. |
```

---

## 11. Repo state at end of Phase 3B

### 11.1 Phoenix-Checkout-Tool

```
$ git -C Phoenix-Checkout-Tool log --oneline -3 main
26a4689 (HEAD -> main, origin/main) Retrofit Phoenix Valve Checkout Tool to commons-backed (Phase 3B)
80dace8 Fix regression: re-import os in checkout_tool_backend (Phase 3B B8)
5153aad Update build.bat — submodule preflight + --collect-all=phoenix_commons (Phase 3B B7)

$ git -C Phoenix-Checkout-Tool branch -a
  main                                                  (at 26a4689)
  phase-3b-phoenix-checkout-retrofit                    (at 80dace8 — preserved)
  remotes/origin/main                                   (at 26a4689)
  remotes/origin/phase-3b-phoenix-checkout-retrofit     (at 80dace8)

$ git -C Phoenix-Checkout-Tool submodule status
 70785a2d7f80ce470d69cf587f90e27220f02f12 commons (heads/main)
```

### 11.2 phoenix-commons

```
$ git -C phoenix-commons log --oneline -3 main
<new>   Add PHASE_3B_POST_REVIEW_AND_MERGE_REPORT + mark Migration-order row Merged   [this commit]
0dd1aec Codify Phase 3B retrofit doctrine in MIGRATION_RULES (Phase 3B post-review)
bc19432 (origin/main) Add PHASE_3B_PHOENIX_CHECKOUT_REPORT — second retrofit complete
```

The submodule pin (`70785a2`) deliberately lags current commons main by
three doc-only commits (`bc19432` Phase 3B retrofit report, `0dd1aec`
Phase 3B doctrine additions, plus this report). No code drift —
`git diff 70785a2..<commons-tip> -- src/ tests/ pyproject.toml` is empty.

---

## 12. Known follow-ups (NOT done in this session)

Per the user's STOP-after spec, the following are explicitly NOT in scope
for this session and are recorded here for future planning only:

| Item | Why deferred | When to revisit |
|------|--------------|-----------------|
| Frozen-exe build + installer test | User spec: "no PyInstaller, no Inno Setup, no frozen verification, no release work" | Next time a v1.8.0 release is cut, or when explicitly approved |
| Updater banner UI exercise (requires a newer GitHub Release) | No newer release exists yet | When v1.8.0 ships |
| Bump submodule pin to current commons main | Pin is code-equivalent (doc-only commits between); no functional reason to rev now | Bundle with the next Checkout release that touches commons-versioned behaviour |
| Phase 3C (Phoenix Command Center) retrofit | STOP-after spec | Separate session per MIGRATION_RULES § Frequency limits (≥ 2 weeks after pilot's last merge if treating 3B as final pilot retrofit) |
| Phase 8a (ValveMaster) — System B → A theme swap | STOP-after spec | Separate session |
| Phase 8b (Job Tracker) — largest surface | STOP-after spec | Separate session |
| Commons PR adding the split `download_update` + `apply_update` API | No second consumer identified yet | If a second tool needs threaded-install separation, propose then |
| Hosting Phoenix Checkout's `apply_light_theme` either in commons or formalised as an app-local extension | ADR-011 says commons stays dark-only; current local placement is correct | Re-open only if ADR-011 is superseded |

---

## 13. Lessons learned (beyond the codified doctrine)

The four doctrine additions cover the durable structural lessons.
Additional non-doctrine lessons from this session, recorded for future
sessions but not promoted to MIGRATION_RULES:

1. **Manual QA prompts must match the actual UI, not the assumed UI.**
   My initial QA guidance asked the user to test "Help → Check for Updates"
   when no such menu item has ever existed. The user correctly flagged
   this. Future retrofit-review prompts should be written from the
   pre-retrofit code, not memory.

2. **Identity-equality check (§ 2) caught zero false positives but also
   would not have caught B8.** The widget retrofit was clean; the
   B8 regression was in a non-widget file that the identity-equality
   gate doesn't even examine. Identity-equality covers the widget-swap
   subset of risk; row 11 (actual launch) covers the import-removal
   subset.

3. **Doctrine commits should land BEFORE merge, not after.** This session
   committed the doctrine additions (`0dd1aec`) before executing the
   merge. That way the retrofit's merge commit reflects work-as-doctrine
   in the same instant. Phase 3A used the same sequencing — kept here.

4. **`pythonw.exe` vs `python.exe` matters for source-mode launch
   verification.** `python checkout_tool_gui.py` runs as a console app
   and the foreground Bash background-task wrapper reported "completed
   exit code 0" within seconds even when the GUI was still up. Switching
   to `pythonw.exe` + PowerShell `Start-Process -PassThru` + a 4-second
   sleep + `Get-Process -Id` is the reliable pattern. Codified in
   MIGRATION_RULES § 10 row 11's recommended implementation.

---

## 14. Sign-off

Phase 3B is complete. The second production tool (Phoenix Valve Checkout
Tool) is now on commons. The pilot pattern (Phase 3A Phoenix CAD) plus
the monolith-retrofit refinement (Phase 3B Checkout) cover the two main
structural shapes future retrofits will encounter:

- **Helper-file shape** (Phoenix CAD, separate `ui/components.py` + `ui/style.py` + `updater.py` + `paths.py`) → whole-file facades per § 1.
- **Monolithic shape** (Phoenix Checkout, inline classes + inline theme + separate `updater.py`/`paths`) → § 11 inline-import pattern + § 1 hybrid coexistence.

Phase 3C (Phoenix Command Center) is the next natural retrofit candidate
when the user re-engages, but its scoping, palette (ADR-016 BrandProfile
implementation), and pre-flight commons-API gap inventory all happen in a
fresh session per the STOP-after rule.

This session STOPS here. No PCC, no ValveMaster, no Job Tracker work
started. No frozen-exe build, no installer, no release.

| Field | Value |
|-------|-------|
| Phase | 3B |
| Status | ✅ Merged + reviewed + doctrine codified |
| Date | 2026-05-19 |
| Merge commit | `26a4689` |
| Author | Claude (under Justin Glave's direct supervision and explicit per-step approval) |
| Stop honoured | Yes |
