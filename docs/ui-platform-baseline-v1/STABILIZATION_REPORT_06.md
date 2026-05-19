# STABILIZATION_REPORT_06.md

> Phase 2.7 — Visual Baselines. The final stabilization /
> safety phase before pilot migrations begin. Establishes the
> per-app visual references, the governance rules for capturing
> + comparing them, and the per-PR checklist Phase 3A retrofits
> will use.
>
> Source-only. Documentation-only. No source code touched, no
> production tools modified, no screenshots captured (markdown
> references only this phase), no migrations / retrofits /
> builds / runtime work.
>
> Captured 2026-05-19.

## 1. Status

**Passed.** All Phase 2.7 deliverables landed as three logical
commits on `main`, plus this report (commit 4). Pushed to
origin (`c48c030..5d47c85`, then this report).

- 8 new markdown documents under `visual-baselines/` (3
  governance + 6 per-app baselines, see §2).
- ValveMaster explicitly excluded from the per-app folder
  structure (rationale: §3).
- Headline finding: **three palettes coexist in production.**
  PCC's `theme.py` palette ≠ `phoenix_style.qss` palette ≠
  ValveMaster's System B. Documented in every per-app baseline
  + the cross-cutting docs + this report.
- Pilot readiness: **ready for Phase 3A** with one ADR pending
  (PCC palette reconciliation) — see §8.

Architecture stabilization remains in effect. **No source code
touched. No production-tool work. No screenshots captured. No
migrations / retrofits started.**

## 2. Apps documented

Six per-app baselines, each at
`docs/ui-platform-baseline-v1/visual-baselines/<app>/baseline.md`,
each following the 16-section template defined in
`VISUAL_BASELINE_RULES.md`:

| Folder | Display name | Source repo | Theme | `expected_internal` | Retrofit order |
|--------|--------------|-------------|-------|----------------------|----------------|
| `checkout/` | Phoenix Valve Checkout Tool | `Phoenix-Checkout-Tool` | `phoenix_style.qss` (System A) | `False` (exe-only) | 3rd (Phase 3B) |
| `phoenix-cad/` | Lab Layout Tool — **source / dev view** | `Phoenix_CAD_Tool` (working copy) / `lab-layout-tool` (GitHub) | `phoenix_style.qss` (canonical source) | `True` (full-folder) | 1st (Phase 3A) |
| `llt/` | Lab Layout Tool — **deployed product view** | (same as `phoenix-cad/`) | (same) | (same) | (same) |
| `pcc/` | Phoenix Command Center | `phoenix-command-center` | `theme.py` (orange + teal — the **divergent** palette) | n/a (source-run) | TBD pending ADR |
| `job-tracker/` | Project Tracking Tool — **source / dev view** | `Job Tracker` (working copy) / `project-tracking-tool` (GitHub) | `phoenix_style.qss` (System A) | `True` (full-folder) | 5th (Phase 8) |
| `ptt/` | Project Tracking Tool — **deployed product view** | (same as `job-tracker/`) | (same) | (same) | (same) |

The dual-folder pattern (`phoenix-cad/` + `llt/`; `job-tracker/`
+ `ptt/`) carries the source-repo perspective and the
deployed-product perspective independently because the
naming and visible identity differ between them.

## 3. Apps not represented as per-app folders

### ValveMaster — deliberately omitted

The user-spec directory list excluded ValveMaster. The Phase
2.7 work honoured that exclusion:

- No `valvemaster/baseline.md` written.
- ValveMaster's System B (gray `#1c1c1c`) state is documented
  in cross-cutting docs:
  - `VISUAL_BASELINE_RULES.md` § "Non-canonical baselines" —
    the policy for tools mid-migration off the deprecated
    System B.
  - `MIGRATION_VISUAL_REVIEW_CHECKLIST.md` § "ValveMaster —
    System B → A cutover (Phase 8a)" — every checklist row
    that applies only to ValveMaster's retrofit PR.
  - `visual-baselines/README.md` § "Apps not represented as
    subdirectories" — explicit explanation of the omission.
  - This report — §5 (highest-risk surfaces), §6 (apps most
    likely to regress visually).

**Rationale for the omission.** ValveMaster's pre-migration state
is the deprecated System B that the Phase 8a retrofit
explicitly replaces. A long-term `baseline.md` for the
soon-to-be-deleted state would carry one-phase-lifetime value.
When ValveMaster's retrofit PR opens, a fresh
`valvemaster/baseline.md` will be captured at PR-open time —
that captures the System B state immediately before the
cutover and lets the post-retrofit screenshots diff against
the documented "intentional change" rather than against a
months-stale baseline.

## 4. Screenshots captured

**Zero screenshots captured this phase.** Three reasons (per
`VISUAL_BASELINE_RULES.md` § Capture mode):

1. **S1/AV bootloader-quarantine** (BLOCKERS.md §1) prevents
   reliable frozen-exe execution on the dev laptop. A
   screenshot of an offscreen-Qt source run wouldn't be a
   faithful representation of what end users see on installed
   copies.
2. **Production tool source isn't modified during Phase 2.7.**
   Spinning up each tool just to screenshot would be the first
   modification — out of scope.
3. **Screenshots become stale fast.** Markdown references
   describing structure (objectNames, widget classes, layout
   containers, palette tokens) survive small visual drift;
   pixel-perfect PNGs don't.

Each retrofit PR (Phase 3A onwards) is responsible for capturing
its own screenshots under `<app>/screenshots/<surface>-<state>.png`
naming with `--phase-<N>` suffixes. The Phase 2.7 markdown
references are the **structural** baseline; the screenshots
will be the **pixel** baseline.

## 5. Highest-risk migration surfaces

Ranked by the combination of "user-visible blast radius" and
"surface-area being touched":

| Rank | Surface | App | Why high-risk |
|------|---------|-----|---------------|
| 1 | **Entire palette swap** | Phoenix Command Center | Orange/teal → red/blue (or other commons-canonical) is a top-to-bottom user-visible change. Every primary CTA, every status badge, every panel-hover state reshades. |
| 2 | **System B → System A** | ValveMaster | The entire visual identity changes intentionally. Brand-level visible change; requires explicit release notes. |
| 3 | **Monolithic `checkout_tool_gui.py` extraction** | Phoenix Checkout | 177 KB of GUI code in one file. Untangling form / dialog / table presentation into separate widget classes creates the most opportunities for accidental visual regression per LOC touched. |
| 4 | **Job Tracker's form + table volume** | Project Tracking Tool | Many forms, many tables, deepest history. Surface area is the risk; any one form / table could regress silently. |
| 5 | **Update banner pattern swap (modal → banner)** | PTT (Job Tracker) and Phoenix Checkout | Both currently use `QMessageBox` for "Update available" prompts (legacy). Migrating to the status-bar `UpdateBanner` is a visible UX change requiring sign-off. |
| 6 | **`QMessageBox` for routine info → inline labels** | All four production tools | `DESIGN_SYSTEM.md` § Forbidden lists `QMessageBox` for routine info as deprecated. Migrating to inline `error` / `warning` labels is visible. |
| 7 | **`starter_package/` deletion (without breaking imports)** | Job Tracker | If anything in production code references the scaffold, deletion breaks. Audit during retrofit PR. |
| 8 | **`cad/` subsystem and BricsCAD COM** | Phoenix CAD / LLT | NOT touched by retrofit (per `PLATFORM_CONTRACT.md`), but the retrofit PR risks accidentally importing through `cad/` symbols. Audit per PR. |

## 6. Visual inconsistencies discovered

The headline Phase 2.7 finding: **three palettes coexist in
production today.** Documented in
`visual-baselines/README.md` § "Three palettes coexist in
production" and in each per-app baseline's § "Current theme
system" + § "Known visual debt":

### The palette divergence

| Tool | Palette in use | Source of palette |
|------|----------------|--------------------|
| Phoenix CAD / Lab Layout Tool | navy + red + blue | `phoenix_style.qss` (the "canonical System A" per Phase 2.1+2.5) |
| Job Tracker / PTT | navy + red + blue | `phoenix_style.qss` (same file) |
| Phoenix Checkout | navy + red + blue | `phoenix_style.qss` (same file) |
| **Phoenix Command Center** | **navy + orange + teal** | `theme.py` (Python `C` dict — **diverges from the QSS-file palette**) |
| **ValveMaster** | **gray "System B"** | programmatic `QPalette` (no QSS file, no shared tokens) |

**`DESIGN_SYSTEM.md` documents PCC's palette as "System A"** —
but the QSS file shipping in Phoenix CAD / Job Tracker /
Phoenix Checkout uses different hex values:

| Token | `DESIGN_SYSTEM.md` (PCC's `C` dict) | `phoenix_style.qss` / `phoenix_commons.theme.tokens` |
|-------|-----------------------------------------|-------------------------------------------------------|
| Background | `#18181F` | `#0a0e27` |
| Primary brand | **orange** `#E8783C` | **red** `#dc2626` |
| Accent | **teal** `#3CB8AE` | **blue** `#3b82f6` |
| Body text | `#E4E4F0` | `#ffffff` |

**`phoenix_commons.theme.tokens` (landed Phase 2.5) mirrors the
QSS-file values** — so commons-canonical is navy + red + blue.
PCC's retrofit will need a deliberate decision (see §8).

### Other inconsistencies surfaced

| Inconsistency | Tools affected | Notes |
|----------------|----------------|-------|
| `UpdateBanner` placement: status-bar strip vs modal `QMessageBox` | Phoenix CAD has the strip; Phoenix Checkout has the modal; PTT has either-or | Retrofit unifies to the strip; sign-off needed for the visible change |
| Phoenix Checkout: monolithic GUI vs Phoenix CAD's separate `ui/` modules | Phoenix Checkout vs Phoenix CAD | Architectural; retrofit extracts |
| `_EMBEDDED_QSS` hand-maintained in Phoenix CAD `ui/style.py:63-829` | Phoenix CAD only (others bundle the file) | Resolved by Phase 2.1's generated fallback; Phoenix CAD's retrofit deletes the local copy |
| Repo-name CamelCase + hyphens (`Phoenix-Checkout-Tool`) vs lowercase-kebab-case | Phoenix Checkout vs all others | Cosmetic; doesn't affect runtime UI |
| Six inline `font-family: Consolas` usages in PCC widget code | PCC | `DESIGN_SYSTEM.md` § Forbidden; tracked in TODOs |
| Modal `QMessageBox` for routine info | All production tools | `DESIGN_SYSTEM.md` § Forbidden; migration target |
| Naming-variant proliferation (e.g. PTT has 4 names: working-copy / GitHub repo / display / exe) | Job Tracker, Phoenix CAD | `NAMING_REGISTRY.md` is the source of truth |

## 7. Apps most likely to regress visually

Ordered by likelihood of an **accidental** regression (NOT a
deliberate one — that's §5):

1. **Phoenix Checkout** — the monolithic GUI file has form,
   dialog, table, and styling concerns all tangled. Extracting
   them into separate widget classes creates many opportunities
   for ±2 px drift / accidental colour-token misuse / button-tier
   swap. **Pixel-level review of every form / dialog required.**
2. **Project Tracking Tool / Job Tracker** — sheer surface area.
   Each of dozens of forms and tables is its own potential
   regression site. **Reviewer fatigue is the actual risk here**
   — incentive to wave through later screens. The checklist is
   the mitigation.
3. **Phoenix Command Center** — the deliberate palette change is
   the headline, but Russian-doll risks lurk: a button that
   shouldn't have changed colour did, because its `objectName`
   matched a commons selector now coloured differently. Every
   `objectName` in PCC's `theme.py`-generated QSS needs audit
   against `COMPONENT_CONTRACT.md` § Reserved `objectName` rules.
4. **ValveMaster** — entire visual change, but **change is
   intentional**, so a regression here means "didn't change the
   thing we expected to change." Lower risk because the change
   is welcome.
5. **Phoenix CAD / Lab Layout Tool** — lowest accidental-regression
   risk in the batch. Phoenix CAD IS the source of the commons
   widgets; the retrofit is mostly deletion of local copies in
   favour of imports. Visible change should be 0.

## 8. Migration recommendations

### Pre-Phase-3A blockers (must resolve before any retrofit PR)

1. **ADR: PCC palette reconciliation.** Decide before PCC's
   retrofit PR opens. Two paths in
   `pcc/baseline.md` § Migration sensitivity:
   - Adopt commons-canonical (orange/teal → red/blue): PCC
     becomes visually identical to other tools. Cohesive but
     loses PCC's current identity.
   - Negotiate an `accent_alt` token in commons: PCC keeps
     brand-identifying colours while adopting commons surfaces /
     type / spacing for the rest. Requires a commons PR adding
     the token.
2. **Update `DESIGN_SYSTEM.md`** to reflect the actual palette
   divergence. Today the doc describes PCC's `C` dict as
   "System A" — which collides with `phoenix_style.qss`'s claim
   to the same name. Resolve by:
   - Renaming PCC's variant if it stays distinct (e.g. "System
     A (PCC variant)"), OR
   - Deleting the divergent palette from `DESIGN_SYSTEM.md` if
     PCC adopts the commons-canonical, OR
   - Adding both palettes to `DESIGN_SYSTEM.md` with explicit
     scope-per-tool. Whichever the ADR decides.
3. **Decide the screenshot-capture moment.** Phase 2.7's
   markdown baselines stand on their own, but pixel-level
   review requires PNGs. Two options:
   - First retrofit PR captures the pre-migration screenshots
     for itself + commits them under `--phase-2.7` for posterity
     (proceeds today; light AV exposure).
   - Wait until AV chain resolves (BLOCKERS.md §1) and capture
     all tools' baselines in one batch (cleaner; blocked).

### Retrofit ordering (refines the original plan)

1. **Phoenix CAD / Lab Layout Tool** — lowest visible risk, the
   canonical source. Confirms commons-import-only retrofits
   work end-to-end. Phase 3A.
2. **Phoenix Checkout** — moderate-volume retrofit; the
   monolithic-GUI extraction surfaces the form/dialog/table
   extraction patterns that subsequent retrofits will re-use.
   Phase 3B.
3. **PCC retrofit** — depends on ADR (above); palette
   reconciliation lands first, then the retrofit. Phase 3C or
   delayed pending ADR.
4. **Job Tracker / PTT** — largest surface; goes last in the
   non-ValveMaster batch. Phase 8.
5. **ValveMaster** — deliberate System B → A cutover. Goes
   after Job Tracker. Phase 8a (per the original plan).

### Process recommendations

- Run `MIGRATION_VISUAL_REVIEW_CHECKLIST.md` row-by-row for
  every retrofit PR. ✅ / ⚠️ / ❌ each row explicitly.
- Capture screenshots into `visual-baselines/<app>/screenshots/`
  with `--phase-<N>` suffixes. Retain `--phase-2.7` baselines
  for historical comparison.
- Update each retrofitted app's `baseline.md` with any
  newly-confirmed facts (e.g. "Phoenix Checkout's main form
  has X — confirmed during retrofit").
- Land a `CHANGELOG.md` entry in the retrofitted app's repo
  describing the visible changes.

## 9. Pilot-readiness assessment

| Readiness criterion | Status | Notes |
|---------------------|--------|-------|
| Per-app reference baselines exist | ✅ Ready | 6 per-app `baseline.md` files |
| Capture rules defined | ✅ Ready | `VISUAL_BASELINE_RULES.md` |
| Per-PR checklist defined | ✅ Ready | `MIGRATION_VISUAL_REVIEW_CHECKLIST.md` |
| ADR-015 (commons transport) | ✅ Ready | Phase 2.6 |
| Commons API public/private boundaries | ✅ Ready | Phase 2.5 — API_BOUNDARIES.md |
| Token module (canonical palette) | ✅ Ready | Phase 2.5 — `phoenix_commons.theme.tokens` |
| Icon infrastructure | ✅ Ready | Phase 2.2 — 10 Lucide SVGs + recolour pipeline |
| Embedded QSS fallback | ✅ Ready | Phase 2.1 — generated, deterministic, CI-guarded |
| Editable / non-editable / submodule install dry-runs | ✅ Ready | Phase 2.6 — all green |
| **PCC palette ADR** | ⚠️ **Pending** | Must land before PCC retrofit PR opens (see §8 #1) |
| `DESIGN_SYSTEM.md` palette rename | ⚠️ Pending | Resolve the "System A" naming collision (see §8 #2) |
| S1/AV chain (frozen-exe verification) | 🔴 Blocked | BLOCKERS.md §1 — gates frozen-mode rows in `VERIFICATION_MATRIX.md` |
| First retrofit (Phase 3A — Phoenix CAD) approval | 🔴 Blocked | Requires explicit user approval per `BASELINE.md` stop conditions |

**Net assessment: ready for Phase 3A** with two pending items
(PCC palette ADR + `DESIGN_SYSTEM.md` rename) that block
specifically PCC's retrofit, not the broader pilot. Phoenix CAD
can begin Phase 3A immediately upon user approval; PCC waits
for its ADR.

## 10. Remaining blockers before Phase 3A

Five items, listed by what they block:

| # | Blocker | Blocks | Resolution path |
|---|---------|--------|------------------|
| 1 | **No user approval to start Phase 3A** | Every retrofit | Explicit user approval per `BASELINE.md` stop conditions. Not in commons's hands. |
| 2 | **PCC palette reconciliation ADR not yet written** | PCC retrofit only (Phoenix CAD / Checkout / Job Tracker unaffected) | Write the ADR before PCC's retrofit PR opens. Two paths in §8. |
| 3 | **`DESIGN_SYSTEM.md` "System A" naming collision** | Doc clarity for every retrofit reviewer | Edit `DESIGN_SYSTEM.md` to reflect post-ADR-#2 decision. |
| 4 | **S1/AV chain (BLOCKERS.md §1)** | Frozen-exe verification + installer testing + real updater deployment | Out of commons's scope. Tracked in `BLOCKERS.md`. Phase 4 + 10.x + 11.x rows in `VERIFICATION_MATRIX.md`. |
| 5 | **Screenshot-capture moment** | Pixel-level visual baselines (but NOT the markdown structural baselines, which are already done) | First retrofit PR captures the `--phase-2.7` originals as part of its own work, OR (slower) wait until S1/AV resolves and batch-capture every tool. |

Blockers 2 + 3 are commons-side and can be resolved in a
sub-phase (e.g. "ADR-016 + DESIGN_SYSTEM.md update") before
Phase 3A's first PR opens. Blockers 1, 4, 5 are coordination /
external dependency.

## 11. Risks discovered / judgment calls

| # | Item | Resolution |
|---|------|------------|
| 1 | User spec listed 6 directories — no `valvemaster/`. | Honoured the explicit list. ValveMaster gets cross-cutting coverage in the governance docs + this report. The omission is explained in `visual-baselines/README.md` § "Apps not represented as subdirectories". Fresh `valvemaster/baseline.md` to be captured at the start of its retrofit PR. |
| 2 | Two pairs of folders represent the same underlying tool (`phoenix-cad/` + `llt/`; `job-tracker/` + `ptt/`). | Distinguished as source-repo perspective vs deployed-product perspective. Each folder's baseline focuses on what's distinctive from that viewpoint; cross-references its twin. |
| 3 | Three palettes in production, two of them called "System A". | Documented honestly. PCC's palette is divergent; `phoenix_commons.theme.tokens` is the canonical (QSS-file) palette per Phase 2.5. ADR needed to resolve which "System A" survives. |
| 4 | Markdown-only baselines (no screenshots) are an imperfect reference. | Honest framing: structural baselines today (objectNames, widget classes, layout containers, palette tokens); pixel baselines at first retrofit PR. The structural references survive small visual drift better than PNGs anyway. |
| 5 | The per-app baselines describe behaviour inferred from the canonical theme + widget catalogue + production-inventory rather than from direct source-tree inspection of each tool. | Sections marked **Inferred** in each baseline. First retrofit PR confirms / updates each row. Lower fidelity than full screenshots, but correct enough for retrofit reviewers to know **what to look for**. |
| 6 | `MIGRATION_VISUAL_REVIEW_CHECKLIST.md` has per-app addenda that pre-prescribe what each retrofit must verify. Risks being out-of-date when the retrofit actually happens. | Acceptable. The addenda capture today's known state. If a retrofit PR finds the state differs (e.g. Phoenix Checkout's GUI has been refactored independently), the PR description notes the deviation and the checklist gets updated in the same PR. |

No new blockers added to `BLOCKERS.md`. Phase 2.7 is fully
source-only + doc-only + AV-independent.

## 12. Future migration implications

This phase is the **final stabilization-phase deliverable**.
What's locked in for Phase 3A+:

1. **Every retrofit PR opens with a screenshot-capture step.**
   The PR's first commit captures the pre-migration state (or
   confirms the existing `--phase-2.7` baseline still matches),
   then makes the retrofit changes, then captures the post-
   migration state. Both sets ship with the PR.
2. **Every retrofit PR runs `MIGRATION_VISUAL_REVIEW_CHECKLIST.md`
   row-by-row** before merge. ❌ rows block; ⚠️ rows require
   explicit sign-off.
3. **Every retrofit PR updates its app's `baseline.md`** with
   newly-confirmed facts (replacing "Inferred" sections with
   observed ones).
4. **PCC's palette ADR lands first** (before PCC's retrofit
   PR opens) and updates `DESIGN_SYSTEM.md` accordingly.
5. **ValveMaster's `valvemaster/baseline.md` is captured at the
   start of its Phase 8a retrofit PR** — the System B "before"
   state preserved as the diff target.
6. **Screenshots accumulate over time** at
   `visual-baselines/<app>/screenshots/` with `--phase-<N>`
   suffixes. Old baselines NEVER deleted — they're the
   regression-protection history.

## 13. Commits (in order)

```
$ git log --oneline -5

5d47c85 Add MIGRATION_VISUAL_REVIEW_CHECKLIST.md (Phase 2.7)
6a59ed5 Add per-app visual baselines (Phase 2.7)
5de1583 Add visual-baselines/ structure + rules (Phase 2.7)
c48c030 Add STABILIZATION_REPORT_05 — Phase 2.6 packaging verification
85d14a1 Update VERIFICATION_MATRIX — Phase 2.6 newly verified rows
```

Per the user's commit plan (3 logical commits + report):

| # | Hash | Subject | Touches |
|---|------|---------|---------|
| 1 | `5de1583` | Structure + rules | `visual-baselines/README.md`, `VISUAL_BASELINE_RULES.md` (+474 lines) |
| 2 | `6a59ed5` | Per-app baselines | 6 × `<app>/baseline.md` (+1,327 lines) |
| 3 | `5d47c85` | Migration review checklist | `MIGRATION_VISUAL_REVIEW_CHECKLIST.md` (+325 lines) |

Cumulative diff vs `c48c030` (the tip before this phase):

```
 .../visual-baselines/MIGRATION_VISUAL_REVIEW_CHECKLIST.md | 325 +++++++++
 .../ui-platform-baseline-v1/visual-baselines/README.md    | 152 +++++
 .../visual-baselines/VISUAL_BASELINE_RULES.md             | 322 +++++++++
 .../visual-baselines/checkout/baseline.md                 | 187 ++++++
 .../visual-baselines/job-tracker/baseline.md              | 215 +++++++
 .../visual-baselines/llt/baseline.md                      | 197 ++++++
 .../visual-baselines/pcc/baseline.md                      | 241 +++++++
 .../visual-baselines/phoenix-cad/baseline.md              | 215 +++++++
 .../visual-baselines/ptt/baseline.md                      | 272 ++++++++
 9 files changed, 2126 insertions(+)
```

## 14. Verification output

No code change → no compileall / pytest impact. For
completeness, the existing suite was re-run after each commit:

```
$ python -m compileall -q src tests
(exit 0)

$ QT_QPA_PLATFORM=offscreen python -m pytest -q tests/
.........................................................................
...........                                                       [100%]
83 passed in 0.22s
```

Unchanged from Phase 2.6 end-state.

## 15. Branch state — local

```
$ git branch -vv

  baseline-v1                       417f860 [origin/baseline-v1]
* main                              5d47c85 [origin/main]
  phase-2-theme-widgets             db1d8b4
  phase-3-paths-updater             b2e7f79
  phase-4-pyinstaller-compatibility ba3d2c4 [origin/phase-4-pyinstaller-compatibility]
```

`main` updated this turn (3 new commits before this report;
report = 4th).

## 16. Remote state — origin

```
$ git ls-remote --heads origin

417f8600…  refs/heads/baseline-v1                          ← unchanged this turn
5d47c85…   refs/heads/main                                 ← updated (3 commits + report)
ba3d2c4d…  refs/heads/phase-4-pyinstaller-compatibility    ← unchanged this turn
```

Push run: `git push origin main` (`c48c030..5d47c85` for the
3-commit batch; the report adds a 4th).

## 17. Confirmation — no migration / build / runtime work occurred

- ❌ **No app code modified** (zero edits to PCC, Job Tracker, Phoenix CAD, Phoenix Checkout, ValveMaster source).
- ❌ **No commons source code modified.** Theme / paths / updater / widgets / icons / tokens unchanged.
- ❌ **No tests added or modified.**
- ❌ **No PyInstaller / Inno Setup / `gh release` / `build.bat`** invocations.
- ❌ **No frozen-exe validation** attempted.
- ❌ **No installer testing.**
- ❌ **No updater runtime testing.**
- ❌ **No icon replacement** in any app.
- ❌ **No widget rewrites / component migrations / retrofits.**
- ❌ **No screenshot captures.** Markdown-only baselines this phase.
- ❌ **No CI workflow change.**
- ❌ **No publishing** (no PyPI, no GitHub Releases).
- ❌ **No network calls.**
- ❌ **`BLOCKERS.md` unchanged.** No new blockers introduced.
- ❌ **`VERIFICATION_MATRIX.md` unchanged.** Same 35 / 48 Verified as Phase 2.6 end-state.

Operations performed this turn:

```
(Read)   docs/production-inventory.md            ← identity source for every baseline
(Read)   docs/ui-platform-baseline-v1/DESIGN_SYSTEM.md  ← surfaced the palette divergence

(Write)  visual-baselines/README.md
(Write)  visual-baselines/VISUAL_BASELINE_RULES.md
git add … && git commit "Add visual-baselines/ structure + rules"  ← logical commit 1

(Write)  visual-baselines/checkout/baseline.md
(Write)  visual-baselines/phoenix-cad/baseline.md
(Write)  visual-baselines/llt/baseline.md
(Write)  visual-baselines/pcc/baseline.md
(Write)  visual-baselines/job-tracker/baseline.md
(Write)  visual-baselines/ptt/baseline.md
git add … && git commit "Add per-app visual baselines"  ← logical commit 2

(Write)  visual-baselines/MIGRATION_VISUAL_REVIEW_CHECKLIST.md
git add … && git commit "Add MIGRATION_VISUAL_REVIEW_CHECKLIST.md"  ← logical commit 3
git push origin main  ← 3 commits pushed (c48c030..5d47c85)

(Write)  docs/ui-platform-baseline-v1/STABILIZATION_REPORT_06.md
```

That's the entire surface.

## 18. STOP

Phase 2.7 complete. **All stabilization phases (2.1 / 2.2 / 2.5
/ 2.6 / 2.7) are now complete.** The platform is ready for the
pilot migrations.

Per the user spec for Phase 2.7: **Do NOT continue into Phase
3A, migrations, retrofits, icon replacement, component rewrites,
or frozen verification.** No code change resumes without
explicit phase approval per `BASELINE.md` stop conditions.

Two commons-side sub-tasks would unblock PCC specifically
before its retrofit PR (the palette ADR + `DESIGN_SYSTEM.md`
rename). Neither is required for Phoenix CAD's Phase 3A —
Phoenix CAD can proceed immediately upon user approval.

Awaiting user direction.
