# Phase 3D — Final Merge Report

> **Status:** Merged. Remote stable. Closure complete.
> **Date:** 2026-05-22.
> **Tag:** `pcc-phase-3d-merged-v2.1.0` on merge commit `2196082`.
> **What this is:** the record of the merge execution + post-merge
> cleanup + remote stabilization that closed Phase 3D.
> **Successor to:** `PHASE_3D_FINAL_MERGE_GATE_REPORT.md` (the
> closure preparation; that report's §7 was wording-fixed in the
> same closure session to be conservative about Wave 8a timing).

---

## 1. Merge commit

| Field | Value |
|-------|-------|
| SHA | `2196082` |
| Parents | `a1b45d3` (PCC main pre-merge) + `390df84` (retrofit branch tip) |
| Strategy | `ort` |
| Mode | `--no-ff` (preserves Phase 3D's 6-commit history as a side branch) |
| Title | `Merge Phase 3D — PCC detail panel modernization` |
| Files touched | `commons`, `detail_panel.py`, `theme.py` (3 files, +604 / −204) |
| Branch | `main` on `phoenix-command-center` |

Full merge message (preserved at `git show 2196082`) lists all 6 step commits, notes Step 3 folded into Steps 1+6, notes Step 8 deferred indefinitely, cross-references the spec + per-step reports + closure gate report, and reaffirms BrandProfile / ADR-014 / ADR-015 / ADR-016 unchanged + no production tool source touched + PCC unpackaged status.

---

## 2. Cleanup commit

| Field | Value |
|-------|-------|
| SHA | `d466202` |
| Parent | `2196082` (the merge commit) |
| Title | `Cleanup: remove Phase 3D inert orphans + bump commons (post-merge)` |
| Files touched | `commons` (submodule pin bump), `detail_panel.py` (2 files, +10 / −13) |

Bounded items removed per `PHASE_3D_FINAL_MERGE_GATE_REPORT.md` §4.2:

  - Dead `_sec()` helper (retired in Step 4 — Overview tab moved to internal Panel section-header QLabels).
  - Dead imports: `QPushButton`, `QMimeData`, `QUrl`, `QModelIndex` (no usages), `QCursor` (used by retired `_hbtn`/`_abtn` helpers in Step 6), `STATUS_COLOR` (replaced by `StatusBadge` variants in Step 4).
  - Redundant inline `QSplitter::handle` stylesheet on Files tab (theme.py overlay covers it globally at lines 601-607).
  - Submodule bump: `0fb6a0e` → `91bbd45` (Step 6 + Step 7 reports + §7 timing-wording fix).

**Cleanup scope was strict.** No other code touched. No surface behaviour change. Mirrors Phase 3C's `a1b45d3` post-merge precedent.

---

## 3. Tag state

| Tag | Points at | Type | Pushed |
|-----|-----------|------|--------|
| `pcc-phase-3d-merged-v2.1.0` | `2196082` (merge commit, NOT cleanup) | annotated | ✓ origin |

Tag-on-merge convention mirrors Phase 3C (`pcc-phase-3c-merged-v2.0.0`). `v2.1.0` claims the detail-panel modernization as a new minor (`v2.0.0` claimed the dashboard modernization). PCC is unpackaged — the tag is operational/forensic only. A single `git revert -m 1 pcc-phase-3d-merged-v2.1.0` would roll back the entire phase.

Tag annotation contents include the 6-commit step manifest, the Step 3 fold note, and the Step 8 deferral note.

---

## 4. Branch state

| Branch | Tip | Tracks | Pushed |
|--------|-----|--------|--------|
| `main` (PCC) | `d466202` (cleanup) | `origin/main` | ✓ |
| `phase-3d-pcc-detail-retrofit` (PCC) | `390df84` (Step 7) | `origin/phase-3d-pcc-detail-retrofit` | ✓ (preserved per MIGRATION_RULES § Per-retrofit branch + PR convention) |
| `main` (commons) | `b67bce1` (governance row + 8a cooldown annotation) | `origin/main` | ✓ |

Retrofit branch is **preserved on origin** per doctrine. The `--no-ff` merge commit retains the entire B-series-style step history as a side branch for forensic / bisect purposes; the branch ref itself stays on origin until the post-review report explicitly clears it for deletion (not in this session — operator decides).

PCC HEAD post-merge graph:

```
*   d466202 Cleanup: remove Phase 3D inert orphans + bump commons (post-merge)
*   2196082 Merge Phase 3D — PCC detail panel modernization                  [pcc-phase-3d-merged-v2.1.0]
|\
| * 390df84 Files tab cohesion pass — CommonsDropZone Lucide (Phase 3D Step 7)
| * 83fada8 Git tab modernisation — buttons + terminal output (Phase 3D Step 6)
| * 50d5142 TODOs tab modernisation — TodoItem + summary (Phase 3D Step 5)
| * 25c4154 Overview tab — SyncStatusCard + Recent Commits modernised (Phase 3D Step 4)
| * 30a9333 Detail panel aggregate tiles — StatTile → AggregateTile (Phase 3D Step 2)
| * 03fdfa3 Detail panel top utility band restructure (Phase 3D Step 1)
|/
* a1b45d3 Cleanup: remove Phase 3C inert orphans (post-merge)
* 060d08c Bump commons: consolidate to canonical sibling chain (post-Phase-3C)
* 058a67a Merge Phase 3C — PCC dashboard modernization                       [pcc-phase-3c-merged-v2.0.0]
```

---

## 5. Submodule state

| Pin | Value |
|-----|-------|
| PCC `commons/` recorded pin (on `main`) | `91bbd45` |
| Commons `main` HEAD on origin | `b67bce1` |
| Drift | 1 commit (governance update added after submodule bump landed) |

The 1-commit drift is intentional and consistent with the Phase 3C pattern: the submodule bump landed in the post-merge cleanup commit (`d466202`), and the MIGRATION_RULES governance update happened immediately after on commons. PCC's pin captures commons through the §7 wording fix (`91bbd45`); the governance commit (`b67bce1`) is downstream. **No corrective bump is required** — the drift is the natural consequence of governance updates landing post-cleanup. A future commit on PCC main may absorb it organically; nothing else depends on it.

`git submodule status` post-cleanup:
```
 91bbd4556d15b176c039822db78dc9b6e4e02d6b commons (heads/main)
```

`heads/main` confirms the submodule's recorded SHA resolves to commons's main branch tip line at the time of the cleanup commit.

---

## 6. Validation results

### Pre-merge

| Check | Result |
|-------|--------|
| PCC branch | `phase-3d-pcc-detail-retrofit` ✓ |
| PCC working tree | clean ✓ |
| PCC HEAD | `390df84` ✓ |
| 6 commits ahead of main | ✓ |
| PCC compileall | clean ✓ |
| PCC pytest | 4 passed in 0.87s ✓ |

### Post-merge (before cleanup)

| Check | Result |
|-------|--------|
| Merge commit `2196082` exists | ✓ |
| Both parents preserved | ✓ |
| Submodule pin updated to `0fb6a0e` | ✓ |
| PCC compileall | clean ✓ |
| PCC pytest | 4 passed in 0.85s ✓ |
| Offscreen smoke (MainWindow + DetailPanel construction + state flips) | ✓ |

### Post-cleanup (final state)

| Check | Result |
|-------|--------|
| Cleanup commit `d466202` exists | ✓ |
| Diff scope strictly within §4.2 cleanup-eligible items | ✓ (+10 / −13 across `commons` + `detail_panel.py` only) |
| PCC compileall | clean ✓ |
| PCC pytest | 4 passed in 0.80s ✓ |
| Submodule pin: `91bbd45` (commons main HEAD at cleanup time) | ✓ |
| Working tree clean | ✓ |

### Invariant preservation

| Invariant | Status |
|-----------|--------|
| B5 — subprocess CREATE_NO_WINDOW | ✅ preserved |
| B6 — no widget-level setStyleSheet on commons primitives | ✅ preserved |
| BrandProfile (orange + teal per ADR-016) | ✅ untouched |
| Locked colour tokens per ADR-016 | ✅ untouched |
| Commons API stability | ✅ preserved (icons-only additions; no widget API change) |
| ADR-014 / ADR-015 / ADR-016 | ✅ all hold |

---

## 7. Remote push results

Pushed in safe order:

| # | Repo | Ref | Result |
|---|------|-----|--------|
| 1a | `phoenix-commons` `main` | `91bbd45` (§7 wording fix) | `ae0c38b..91bbd45  main -> main` ✓ |
| 2 | `phoenix-command-center` `phase-3d-pcc-detail-retrofit` | `390df84` | `* [new branch]  phase-3d-pcc-detail-retrofit -> phase-3d-pcc-detail-retrofit` ✓ |
| 3 | `phoenix-command-center` `main` | `d466202` (cleanup tip) | `a1b45d3..d466202  main -> main` ✓ |
| 4 | `phoenix-command-center` tag | `pcc-phase-3d-merged-v2.1.0` | `* [new tag]  pcc-phase-3d-merged-v2.1.0 -> pcc-phase-3d-merged-v2.1.0` ✓ |
| 1b | `phoenix-commons` `main` | `b67bce1` (governance row) | `91bbd45..b67bce1  main -> main` (post-merge) |

The pre-merge wording fix (step 1a) was pushed before the PCC merge so the submodule could pick it up in the post-merge cleanup bump. The governance update (step 1b) was pushed last so MIGRATION_RULES reflects the merge commit SHA that just landed.

No push rejected. No remote-state ambiguity. All four PCC remote refs (main, retrofit branch, tag, plus the existing branches) resolve.

---

## 8. Governance update summary

`MIGRATION_RULES.md § Migration order` got one new row and one annotation:

**New row 3D** (between 3C and 8a):
> **3D** | Phoenix Command Center — Detail Panel | `phase-3d-pcc-detail-retrofit` | ✅ Merged 2026-05-22 (merge commit `2196082` on `phoenix_command_center:main`, post-merge cleanup + submodule consolidation `d466202`). Retrofit work: Steps 1, 2, 4, 5, 6, 7 across 6 commits (`03fdfa3`..`390df84`) delivering the detail-panel modernization (top utility band restructure + AggregateTile migration + Overview / TODOs / Git / Files tab Panel-wrap + Lucide cohesion). Step 3 folded into Steps 1+6; Step 8 (keyboard shortcuts) deferred indefinitely per spec §7. Tag `pcc-phase-3d-merged-v2.1.0` on the merge commit. Retrofit branch preserved on origin per MIGRATION_RULES § Per-retrofit branch + PR convention. PCC keeps orange + teal `BrandProfile` per ADR-016. Reports under this directory: `PCC_DETAIL_PANEL_SURFACE_SPEC_V1`, `PCC_DETAIL_PANEL_IMPLEMENTATION_STEP_01/02/04/05/06/07_REPORT`, `PHASE_3D_FINAL_MERGE_GATE_REPORT`, `PHASE_3D_FINAL_MERGE_REPORT`.

**Wave 8a row annotation:**
> Not started — System B → A visible-theme swap. Operator-gated; doctrinal cooldown floor 2026-06-02 (14 days after Phase 3B's 2026-05-19 merge).

Commit: `b67bce1` "Update MIGRATION_RULES — Phase 3D PCC detail-panel merged". Pushed to commons origin.

---

## 9. Remaining intentional debt

### 9.1 Submodule pin lag — intentional, harmless

PCC `main` records `91bbd45` for commons; commons `main` is at `b67bce1` (one commit ahead with the governance row). Documented in §5 above. **No action required.**

### 9.2 Step 8 keyboard shortcuts

Deferred indefinitely. Per spec §7 + §4 "optional and deferrable." Recommendation logged in the merge gate report §4.1 and §6.5; mirrored in the governance row. Reopening Step 8 would be a future polish decision, not a doctrinal requirement.

### 9.3 Operationally-semantic inline chrome (intentional B6 carve-outs)

Preserved end-to-end through Phase 3D and through the post-merge cleanup:
- `CommonsDropZone` dashed-border drop affordance
- Recent-commits per-row `#card`-background frame
- Sync-card per-status colour codes on porcelain status flags
- TodoItem strikethrough on `done`
- Branch sub-label muted inline colour
- Various semantic content-text colour inline styles

Each is a documented carve-out, not debt.

### 9.4 `load_tool()` runtime status-sentence emoji glyphs

Preserved INSIDE the QPlainTextEdit terminal output surface (not chrome). Per Step 7 report §4 — terminal output is a calm surface for whatever the runtime decides to print.

---

## 10. Recommended next phase options

**No phase is auto-scheduled by this merge.** The operator decides which (if any) to open.

| Option | Status | Cooldown / gate |
|--------|--------|-----------------|
| **Wave 8a — ValveMaster** | Operator-gated. Next sequenced production-tool retrofit per MIGRATION_RULES § Migration order. System B → A theme swap. | Doctrinal floor: 2026-06-02 (14 days after Phase 3B's 2026-05-19 merge). Today 2026-05-22 → floor is ~11 days away, not past. Opening on or after the floor is the operator's call. |
| **Wave 8b — Job Tracker** | Operator-gated. Largest production surface; deletes `starter_package/` in same PR. | Doctrinal floor: 2 weeks after Wave 8a's merge. Cannot open until 8a closes. |
| **Phase 3E — PCC polish (Commons Browser / Settings / Wizard / About)** | Not scheduled. Operator decides whether to open. | None — same tool as Phase 3C/3D; opens immediately if started. |
| **Phase 3D Step 8 — keyboard shortcuts** | Indefinitely deferred. Reopening optional. | None — same scope as Phase 3D; opens immediately if started. |
| **Search backend work / new feature work** | Out of scope for the retrofit doctrine. Operator schedules independently. | n/a |

**No recommendation is being made for which to open next.** The doctrine sets cooldowns and operator-gating; the choice is the operator's.

---

## 11. Confirmation

  - **No architecture changes occurred.** No new ADR. No commons API change. No new commons widget. The §7 wording fix was a *report-text* edit, not architecture. The MIGRATION_RULES row addition was *governance text*, not architecture. ADR-014 / ADR-015 / ADR-016 all hold.
  - **No BrandProfile changes occurred.** PCC `BrandProfile` (orange + teal) unchanged throughout the merge + cleanup. Commons sentinel substitution unchanged. The post-cleanup smoke confirmed `PrimaryButton` still resolves to PCC orange and `SecondaryButton` to PCC teal-dark per ADR-016.
  - **No production deployment occurred.** PCC is unpackaged per `CLAUDE.md`. No installer was built. No `dist/` artifact was produced. No GitHub Release was created. The tag is operational/forensic only.
  - **No production tool source touched.** Phoenix CAD / Phoenix Checkout / Project Tracking Tool / ValveMaster all unmodified throughout Phase 3D and through the merge + cleanup.
  - **No Phase 3E work occurred.** Phase 3D scope was the detail panel; closure execution does not expand scope. No PCC source outside `detail_panel.py` was touched during the merge or cleanup (theme.py was touched only during Step 6, before the merge).
  - **No Step 8 implementation occurred.** Keyboard shortcuts remain deferred indefinitely.
  - **No search backend work occurred.** Not in scope.
  - **No Wave 8a work occurred.** Wave 8a remains operator-gated with the 2026-06-02 doctrinal floor still in the future.

---

## Closure commit summary

| Repo / branch | Commit | Subject |
|---------------|--------|---------|
| commons / main | `91bbd45` | Fix Phase 3D gate report §7 — conservative Wave-8a timing language |
| PCC / phase-3d-pcc-detail-retrofit (pushed) | `390df84` (branch tip) | Files tab cohesion pass — CommonsDropZone Lucide (Phase 3D Step 7) |
| PCC / main | `2196082` (merge, `--no-ff`) | Merge Phase 3D — PCC detail panel modernization |
| PCC / main | `d466202` (cleanup) | Cleanup: remove Phase 3D inert orphans + bump commons (post-merge) |
| PCC / tag | `pcc-phase-3d-merged-v2.1.0` | Annotated tag on `2196082` |
| commons / main | `b67bce1` | Update MIGRATION_RULES — Phase 3D PCC detail-panel merged |
| commons / main | (this report, pending commit) | Add PHASE_3D_FINAL_MERGE_REPORT |

---

*End of report. Phase 3D is closed. Remote state stable. Next phase is the operator's call.*
