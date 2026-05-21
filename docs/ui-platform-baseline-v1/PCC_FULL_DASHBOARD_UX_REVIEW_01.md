# PCC Full Dashboard UX Review — 01

> **Status:** product review. Pre-implementation.
> **Date:** 2026-05-21.
> **Branch reviewed:** `phase-3c-pcc-retrofit` at tip (B14.1 / `c6b72e5`).
> **Scope:** holistic evaluation of PCC's dashboard as a complete
> system after Steps 1-6 of `PCC_DASHBOARD_SURFACE_SPEC_V1`.
> **What this is:** opinionated product assessment + a single
> recommended next move.
> **What this isn't:** retrofit doctrine, implementation mechanics,
> architecture governance.

---

## 1. Overall dashboard assessment

**PCC's dashboard is meaningfully modern now.** It crossed a threshold somewhere between Steps 3 (table) and 5 (tile refresh) — from "PySide6 inline-styled chrome" to "considered operator surface." A few specific moments confirm this:

  - First paint after launch reads as **a 2026 developer tool**, not a 2010 Qt-default app. The icon vocabulary, typography rhythm, and surface composition are all coherent within ~3 seconds of looking at it.
  - The **tools table is the dashboard's centre of gravity** as intended by the spec. The operator's eye lands there immediately. Status pills are glanceable. Per-tool icons are recognisable. The context menu is discoverable.
  - The **utility band at the top** transformed the page from "data display" into "command surface." Even without a search backend, the existence of the input + the visible Ctrl+K chip + the sync pill says "this is an operator tool" before any data renders.
  - The **per-tool activity tag colors** turned the activity feed from "uniform accent noise" into a recognisable per-tool legend. Operator can identify the originating tool by tag colour without reading text.

The dashboard is **not yet flagship-finished** — there are visible loose ends documented in §5 — but it is **flagship-quality in its dominant surfaces**. The remaining work is consolidation, not transformation.

---

## 2. What now feels flagship-quality

  - **Sync pill (top-band right).** "Scanning…" → "All synced · HH:MM" transition. Calm, operational, brand-accent during scan. Single most modern element on the surface.
  - **Tools table headers.** Quiet, no inter-column separators, single thin underline. Reads like a Linear or Sourcegraph table, not a Qt grid.
  - **StatusBadge pills in the STATUS column.** Tinted-bg + saturated-text treatment is restrained. "1 change" / "12 changes" / "Clean" reads at a glance. Compact mode integrates cleanly into the row rhythm.
  - **Per-tool activity tag colors.** Subtle, distinctive, semantic. Operator absorbs "this commit came from Checkout" without reading the tag text.
  - **Lucide icon vocabulary** across sidebar nav + tool rows + menu actions + aggregate tiles + search input. No emoji glyphs in primary surfaces. Coherent across the whole surface.
  - **Top utility band composition.** Page title left, search shell centred, sync pill right. Single-band command surface — Linear / Raycast inspired.
  - **Aggregate tiles with leading icons + subtitles.** "across PycharmProjects" / "Largest: ValveMasterTool" turns numbers into framed metrics.
  - **Panel containers around tools + activity sections.** Rounded-card chrome makes both surfaces feel intentional rather than floating in the body.

---

## 3. What still feels old

Honest list. These are the surfaces that haven't been touched since the Phase 3C kickoff and still carry their pre-retrofit chrome.

  - **Sidebar tool rows' stats chips** (📄 LOC, 💾 Size, 📌 TODOs). Still emoji glyphs in dense compact widgets in the sidebar's tool list. The migration to Lucide stops at the badge icon; the stats chips lag behind.
  - **Activity feed bullets and row composition.** The blue dot + msg + tag + timestamp layout works, but the *typography* and *vertical rhythm* of the activity rows haven't been touched. They feel like they came from a slightly earlier era than the tools table.
  - **Detail panel** (everything behind a tool-row click). Untouched in Phase 3C. The dashboard's flagship feel evaporates the moment the operator clicks into a tool. The detail panel still has the pre-retrofit chip-heavy "chip soup" feel.
  - **Status bar.** Now quieter (no `● Scanning…` indicator), but its typography and chrome are still the pre-retrofit treatment. Reads as utilitarian rather than considered.
  - **Settings dialog + New Tool wizard.** Untouched. Both feel pre-retrofit when opened.
  - **About dialog.** Hero icon updated (Step 1) but typography + button treatment still pre-retrofit.
  - **Sidebar action buttons.** Have Lucide icons (Step 1) but button chrome (height, padding, hover state) is the pre-retrofit treatment.

None of these are catastrophic. They're "noticeable if you look for them" surfaces, not "noticeable on first paint" surfaces.

---

## 4. What still feels noisy

  - **5 aggregate tiles is right at the edge of "too many."** Per the spec V1 the target was 4 (with "Needs Commit" retired in favour of the table's STATUS column). Operator preference brought it back as a 5th tile in B14.1. The row is now functional but visually denser than the 4-tile version. Not a problem; flagging it as the closest thing to "tile-row over-density."
  - **Per-row context menu — 4 actions + greyed GitHub.** Operator-tested. Discoverable. But it relies on right-click as the primary affordance, which is less obvious than a visible chip or button. Not noisy per se; flagging because the discoverability cost is real.
  - **Activity-feed tag pill widths.** With 12-char tag truncation + tooltip on hover, no rows currently clip. But the activity column at 13:9 split is still ~40% of body width — gives the operator strong context but consumes screen real estate. Acceptable trade.

Overall: **the dashboard is calm.** No surface visibly competes for attention with the tools table.

---

## 5. What still feels unfinished

  - **Search has no backend.** The shell exists, the Ctrl+K shortcut works, but Enter just surfaces a status-bar "coming soon" message. The operator who types a query and presses Enter gets nothing visible in the place where results should appear. This is the single most "promise without payoff" surface on the dashboard.
  - **Sync pill error state never fires.** API exposed (`set_sync_state("error")`) but no `ScanWorker` failure callback triggers it. Scan failures currently surface only as silent gaps. Latent UX bug.
  - **Status bar missing "Press ⌘K to search" hint** (Step 8 in the spec). The Ctrl+K chip on the input itself is the only visible affordance; spec §3.6 calls for a right-aligned status-bar reminder too.
  - **Aggregate tile subtitles use static fallback for some data.** "across N tools" for LOC could be a trend ("+1,840 this week") if we tracked scan history. We don't, so the static fallback reads as "filler text" rather than "interesting context."
  - **Detail panel disconnect.** Clicking any table row opens the detail panel, which retains Phase 3B chrome (different from the dashboard's Step 1-6 chrome). The transition between dashboard and detail panel is a visual gear-shift that the operator will notice.

---

## 6. Remaining UX debt — categorised by priority

### A. High-impact / low-risk (should happen soon)

| Item | Why now | Estimated scope |
|------|---------|-----------------|
| **Status-bar "Press ⌘K to search" hint** (Step 8) | Trivial addition. Completes the Ctrl+K affordance pairing the chip can't carry alone. | ~5 LOC. One commit. |
| **Sync-pill error state wiring** | API exists; `ScanWorker` needs to emit `failed` on exception. Scan failures becoming visible removes a latent UX bug. | ~15 LOC in scanner.py + 5 in main_window.py. One commit. |
| **Sidebar tool-row stats chips → Lucide icons** | Last 3 emoji glyphs (📄 💾 📌) on a primary surface. Mechanical migration; finishes the Step-1 icon work. | 2-3 new Lucide SVGs in commons + ~30 LOC in sidebar_tool_widget.py. One commit + commons commit. |

### B. Medium-impact (optional refinement)

| Item | Why medium | Estimated scope |
|------|------------|-----------------|
| **Search backend (Step 7)** | Delivers on the promise of the search input. But it's a multi-day feature (corpus indexing + result UI + result routing). Real value, real scope. | Multi-day. New `search.py` module + result UI + routing wiring. Operator-approval-per-decision step. |
| **Detail-panel modernization** | The biggest "still feels old" surface. Operator notices the disconnect on every tool click. But scope is large (the detail panel is the second-most complex surface after the dashboard). | Multi-day. Comparable in scope to the dashboard retrofit itself. Belongs in a separate phase, not Phase 3C. |
| **Activity-feed typography pass** | Tighter line spacing, slightly larger message text, maybe even a 2-line layout for long commits. Small wins per row × 20 rows = noticeable. | ~50 LOC in `ActivityRow`. One commit. |
| **Settings dialog + New Tool wizard chrome pass** | Both feel pre-retrofit when opened. Each is a self-contained dialog so easy to address independently. | ~1 dialog per session. Two sessions total. |

### C. Avoid / over-polish risk (should probably NOT pursue)

| Item | Risk |
|------|------|
| **Tile-count tuning** | 5 vs 4 vs 6 tiles. We've already flipped on this once. Further tuning is taste; not value. |
| **Animation / transitions** | The spec is explicit about restraint. Any animation work risks Arc Browser / Notion AI territory. |
| **Per-surface palette experiments** | Brand profile is settled. Re-litigating accent colour choices is wasted motion. |
| **Command-palette UI** | Out of scope. ⌘K opens the search input; that's enough. Don't introduce a modal command palette. |
| **Aggregate-tile trend lines / sparklines** | Requires scan-history persistence — not in scope. Spec explicitly forbade "fake analytics." |
| **Notification toast system** | Spec §7 explicitly forbade. Status-bar + sync pill cover the entire operational-feedback surface. |

---

## 7. Biggest remaining risks

  - **Detail-panel disconnect.** Operator workflow regularly crosses from dashboard → detail panel. The visual chrome shift between them undercuts the dashboard's flagship feel for any operator who actually uses the tool. If the dashboard improves but the detail panel doesn't, the *perception* of "PCC got modernised" is partial.
  - **Frozen-build drift.** Phase 3C has 20+ commits unpushed and unbuilt. The FROZEN_BUILD_BASELINE pipeline (Python 3.12 + PyInstaller 6.20.0 + S1-quarantine survival) hasn't been exercised since the retrofit branch's B4 commit. Source-mode launches are clean, but no frozen artifact has been produced. There's a non-zero chance the Phase-3C commits introduced a behavior that the frozen build catches differently (e.g., resource paths, QSS resolution, icon-loading-from-pkgresources under PyInstaller).
  - **Scope creep into detail-panel territory.** If the next session opens "detail panel modernization" we will spend multiple days there. That's a legitimate phase, but it shouldn't be tacked onto Phase 3C; it deserves its own spec + plan + approval.
  - **"Just one more polish" loop.** The dashboard is good. The risk of every session adding small polish is real. A merge-and-validate gate would reset the velocity.

---

## 8. Recommended next move

**Recommendation: option 2 — Pause and polish existing surfaces.**

Specifically: complete the three §6.A items in a single session, then **build a frozen artifact** to validate the FROZEN_BUILD_BASELINE pipeline still survives the Phase-3C commits, then **operator-decision-gate the merge** to master.

### Why this over the other options

  - **Not option 1 (search backend)** — Search backend is multi-day work that exposes a fresh feature surface. Better to consolidate what's already shipped before opening a new front. Search backend stays the right *next* feature, but it should land on top of a merged-and-validated baseline.
  - **Not option 3 (detail-panel modernization)** — Belongs in its own phase with its own spec. Treating it as a Phase 3C extension would balloon scope.
  - **Not option 4 (sidebar refinement)** — Sidebar is functional + modernised on its primary surfaces. The remaining items (stats chips) fall under §6.A and are part of the polish recommendation.
  - **Not option 5 (broad spacing / typography normalization)** — High-risk for low value. Across-the-board typography pass tends to surface 50 micro-decisions and stall.
  - **Not option 6 (merge immediately)** — Branch is `phase-3c-pcc-retrofit` with 20+ commits and no frozen-build validation. Merging without that validation risks shipping to operators a build that doesn't survive S1 quarantine or PyInstaller resolution.

### The "Pause and polish" session shape

One bounded session covering the three §6.A items:

  1. **Status-bar "Press ⌘K to search" hint** added. (~5 LOC, ~5 min)
  2. **Sync-pill error state wired** — `ScanWorker` emits failure signal; `MainWindow._start_scan` connects it; `set_sync_state("error")` fires. (~20 LOC, ~30 min)
  3. **Sidebar tool-row stats chips migrated to Lucide** (last 3 emoji). (~30 LOC + 2-3 commons SVGs, ~30 min)
  4. **Frozen build** via `build.bat` to validate FROZEN_BUILD_BASELINE + S1 survival. Confirm `dist\PhoenixCommandCenter\PhoenixCommandCenter.exe` launches + the retrofitted dashboard renders correctly in the frozen build. (~10 min build + ~5 min observation)
  5. **Operator visual review** of the frozen build. If clean, **merge gate**: ready or not.

After this session the branch is genuinely "release-quality flagship dashboard" — and Step 7 (search backend) can land on top of a merged, validated foundation as a separate forward push.

---

## 9. Is the dashboard "modern enough"?

**Yes — for a v1 flagship.** Not yet for "the final form."

Concretely:

  - For "the operator looks at PCC and feels they're using a 2026 developer tool" — **yes, achieved.** The dashboard would not embarrass next to GitHub Desktop or Sourcegraph at first paint.
  - For "every surface in PCC feels consistent with this dashboard" — **no, not yet.** The detail panel is the visible gap; settings + new-tool wizard are smaller gaps.
  - For "the operator does substantive work and never thinks about PCC's chrome" — **mostly yes** within the dashboard surface. The chrome recedes the way good chrome should. The exception is the empty-promise search input, which the operator will notice every time they type something.
  - For "PCC has flagship identity distinct from but consistent with the production tools" — **yes.** Orange + teal accents read as PCC; the table treatment + utility band + StatusBadge + per-tool tags are platform-shared semantics with PCC-specific brand colors.

The phrase "modern enough" understates it. The dashboard went from **"functional Qt app"** to **"considered operator surface."** The remaining work is consolidation and rolling that quality outward to the surfaces the dashboard now points at (detail panel, settings, wizard).

---

## 10. Confirmation

  - **No implementation occurred.** This review is markdown-only. No PCC source touched. No commons source touched. No tests run beyond what was already passing.
  - **No architecture changes occurred.** No new ADR. No commons API change. No new modules.
  - **No production deployment occurred.** No installer built. No `dist/` zip created. No GitHub Release published. No branch pushed.
  - **No new design proposed.** The review compares actual delivered surfaces to the operator-approved `PCC_DASHBOARD_SURFACE_SPEC_V1` and to the original operator concerns. It doesn't invent a new direction.
  - **No "next feature" opened.** The recommendation is to pause, polish, validate, and gate the merge — not to start search backend or detail-panel modernization.

---

## Branch state at time of review

| Item | State |
|------|-------|
| Branch | `phase-3c-pcc-retrofit` |
| HEAD | `c6b72e5` (B14.1 — restore Needs Commit + lighten ⌘K chip) |
| Commits ahead of `origin` | 20+ (not pushed) |
| Commons commits ahead | 8 (not pushed) |
| Tests | 4/4 PCC smoke, 126/126 commons (all green) |
| Source-mode launch | exit 0, 0 stderr (verified repeatedly) |
| Frozen build | **not exercised since B4** (4 commits in; now 16 commits behind) |
| Operator visual review | complete through B14.1 |

---

## Strategic next-phase nomination

  1. **Pause-and-polish session** (this review's recommendation) — 3 §6.A items + frozen build + merge gate. Bounded, validating, consolidating.
  2. **After merge:** spec authoring for the next phase. Two strong candidates:
     - **Phase 3D — Detail-panel modernization.** Carries the dashboard's chrome into the second-most-used PCC surface. Multi-day. Deserves its own spec.
     - **Phase 3E — Search backend.** Completes the dashboard's search promise. Smaller scope. Could land first.
  3. **Either way, Phase 3C closes at the merge point** as the "dashboard modernization" phase. Future work is additive on top of a validated, shipped baseline.

The discipline that makes "this dashboard is modern" durable is **knowing when to stop** and ship before the next big push.

---

*End of review.*
