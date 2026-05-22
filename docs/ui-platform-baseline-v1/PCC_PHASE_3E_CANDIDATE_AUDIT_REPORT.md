# PCC Phase 3E — Candidate Surface Audit

> **Status:** candidate audit only. No implementation. No architecture change.
> **Date:** 2026-05-22.
> **Inputs:** PCC source-mode inspection of the 6 remaining surface modules,
> Phase 3C + 3D closure reports, MIGRATION_RULES doctrine.
> **Output:** ONE recommended Phase 3E direction + reasoning. Operator
> approves before any spec or implementation begins.
> **Successor to:** `PHASE_3D_FINAL_MERGE_REPORT.md`.

---

## 1. Remaining surface inventory

PCC source modules audited:

| Surface | File | LOC | `setStyleSheet` count | Emoji on chrome | Retrofit status |
|---------|------|-----|-----------------------|------------------|-----------------|
| Dashboard | `dashboard.py` | 38,825 | (cleaned) | none | ✅ Phase 3C done |
| Detail panel | `detail_panel.py` | 51,900 | (cleaned) | none | ✅ Phase 3D done |
| **Commons Browser** | `commons_browser.py` | 240 | 12 | `◇` orphan / `◈` user chips | ⚠ Pre-retrofit |
| **Settings dialog** | `settings_dialog.py` | 230 | 15 | `⚙` in title | ⚠ Pre-retrofit |
| **New Tool Wizard** | `new_tool_wizard.py` | 1,000+ | 29 | none (cleaned in Phase 5/5B/6) | ⚠ Chrome pre-retrofit |
| **About + Shortcuts dialogs** | `about_dialog.py` | 202 | 7 | `⌨` in shortcuts title only | 🟡 Mostly done (Phase 3C ATS hero icon landed); Shortcuts row-cards still inline-styled |
| **Search shell** | `dashboard.py` + `main_window.py` | n/a | (cleaned) | none | 🟡 Shell ✅; **backend = placeholder** |
| **Push Preview dialog** | `push_preview_dialog.py` | ~250 | 8.5 KB | (unchecked) | ⚠ Explicitly preserved by Phase 3D spec §8 |
| **Status bar / global chrome** | `main_window.py` | n/a | (cleaned) | none | ✅ Phase 3C done (Ctrl+K hint, status messages) |
| **Sidebar sprite + tool widget** | `sidebar_sprite.py` / `sidebar_tool_widget.py` | 90+45 | minor | none | ✅ Phase 3C done (Lucide nav glyphs) |

### Per-surface state notes (from inspection)

#### Commons Browser (`commons_browser.py`)
  - `pageTitle` `QLabel` ✅
  - Rescan button: Phase 3C Step 1 already migrated to Lucide `refresh` icon
  - `_Chip` inline-styled QLabel (lines 25-36): 4 summary chips (files / referenced / orphans / size)
  - `UsageFooter` inline-styled QFrame with `◇`/`◈` glyph chips
  - QSplitter handle has the same redundant inline `setStyleSheet` Phase 3D post-merge cleanup just removed from the detail panel (line 153)
  - FileViewer + QTreeView + QFileSystemModel — same pattern as detail-panel Files tab
  - No `Panel` containers. No `StatusBadge`. Mostly raw QFrame chrome.

#### Settings dialog (`settings_dialog.py`)
  - QDialog with two-tab QTabWidget (General / Tools)
  - Title row: `"⚙  Settings"` emoji-prefixed QLabel (line 82)
  - Every content card is a raw QFrame with inline `setStyleSheet` (lines 21, 98, 126, 146)
  - Save/Cancel: raw `QPushButton` + `accentBtn`/`ghostBtn` objectName (lines 199-209)
  - `ToolRow` custom widget repeats the inline-styled card pattern
  - No `Panel`. No `StatusBadge`. No `SecondaryButton`/`PrimaryButton`/`TertiaryButton`.

#### About dialog (`about_dialog.py`)
  - `AboutDialog`: Phase 3C Step 1 ATS brand-mark hero (logo.png at 48px) replaced 🔥 emoji
  - Inline-styled author card (lines 86-91) — analogous to `Panel` but inline
  - Close button: `accentBtn` objectName
  - `ShortcutsDialog` (lines 149+): `"⌨  Keyboard Shortcuts"` emoji title; per-row cards inline-styled (lines 168, 175); 9 hardcoded shortcuts

#### New Tool Wizard (`new_tool_wizard.py`)
  - QDialog with 4-page QStackedWidget
  - Phase 5/5B/6 modernized template content emission + frozen-build baseline; chrome is unchanged
  - 29 `setStyleSheet` call sites scattered across header / section labels / radio cards / preview area / footer
  - Footer buttons: raw `QPushButton` + `ghostBtn`/`accentBtn`
  - Inline-styled `_section_label()` + `_hint()` + `_radio_card()` helpers
  - Mostly LARGE but mechanical migration target

#### Search shell + backend
  - Shell: `dashboard.py` `searchFrame` + `dashboardSearch` lineedit + `searchShortcutChip` (Ctrl+K) — Phase 3C Step 6 done
  - Wiring: `main_window._focus_dashboard_search()` ✅; `_on_search_submitted()` ✅ but body is placeholder
  - Placeholder text: `f'Search: "{query}" — backend coming in Step 7'` (main_window.py:642) — a leftover hint from Phase 3C Step 6
  - **Backend: does not exist.** No indexer, no result UI, no result-ranking logic.
  - Operator visible affordance: typing into the box does nothing operational; status-bar shows the "backend coming" hint then clears.

#### Push Preview dialog (`push_preview_dialog.py`)
  - Spec §8 of `PCC_DETAIL_PANEL_SURFACE_SPEC_V1` explicitly preserves it.
  - Visited only during the detail-panel Git tab Push button's confirmation flow.
  - Operator-visible chrome is pre-retrofit but rare-use.

---

## 2. Candidate ranking table

Six dimensions, scored ↓1-5 (5 = most weight toward selection):

| Surface | Operator frequency | Visual mismatch | Workflow importance | Impl. risk (5 = lowest) | Primitive reuse | Scope creep risk (5 = lowest) | **Total** |
|---------|--------------------|-----------------|---------------------|--------------------------|-----------------|--------------------------------|-----------|
| Commons Browser | 4 (every cross-tool inspection) | 5 (most jarring after dashboard + detail done) | 3 (real workflow surface) | 5 (clear Files-tab analog) | 5 (zero new primitives) | 5 (structurally clear) | **27** |
| Settings dialog | 2 (low — first-run + reconfigure) | 4 (raw QFrame chrome) | 3 (config workflow) | 4 (standard dialog modernization) | 5 (Panel + Lucide cover it) | 4 (limited content) | **22** |
| Wizard | 1 (rare — new tool creation) | 3 (pre-retrofit but logic mostly modernized) | 4 (high-stakes when used) | 2 (largest LOC; 4 stepped pages) | 4 (most primitives applicable) | 3 (4-page surface with cross-page state) | **17** |
| About + Shortcuts (bundle) | 1 (rare) | 2 (mostly done; Shortcuts is the gap) | 1 (informational) | 5 (small isolated surface) | 5 (Panel-trivial) | 5 (very small scope) | **19** |
| Push Preview dialog | 2 (only during push) | 2 (pre-retrofit but rare) | 2 (already operator-spec preserved) | 5 (small isolated dialog) | 5 (Panel + StatusBadge fit) | 5 (very small) | **21** |
| Search **backend** | 5 (shell is on screen every session) | n/a (feature work, not chrome) | 5 (potential workflow accelerator) | 1 (indexer + result UI + ranking — feature work) | 1 (no existing primitive — needs new spec) | 1 (high — every dimension is open) | **13** |

**Ranking (highest priority first):**

  1. Commons Browser (27)
  2. Settings dialog (22)
  3. Push Preview dialog (21)
  4. About + Shortcuts bundle (19)
  5. Wizard (17)
  6. Search backend (13)

The scoring weights are equal across the six dimensions — they encode the Phase 3C/3D principle ("small disciplined surface work beats broad redesign") plus an implementation-risk inversion.

---

## 3. Search backend assessment

### Current state

  - **Shell exists** (Phase 3C Step 6, `searchFrame` / `dashboardSearch` / `Ctrl+K` chip).
  - **Hotkey wired** (`main_window._focus_dashboard_search` switches to dashboard and focuses the box).
  - **Submission wired** (`Enter` → `_on_search_submitted(query)`).
  - **Submission body is a status-bar placeholder** that says "backend coming in Step 7." That Step-7 reference is from Phase 3C's sequencing — never specified, never scheduled.

### What "search backend" would require

  - **An indexer.** What gets indexed? Tool names? File contents? Commit messages? Recent activity? TODOs? File paths?
  - **A query parser.** Free-text? Tag syntax (`tool:cad`, `tag:fixme`)? Wildcards?
  - **A result ranker.** Recency? Relevance? Tool affinity?
  - **A result UI.** Inline dropdown under the search box? Dedicated results page? Status-bar pills?
  - **A keyboard model.** Up/down to navigate? Enter to commit? Esc to dismiss?
  - **A spec.** None exists yet.

Each of those is an open product question with operator implications. None of the Phase 3C/3D primitives directly answer them — `Panel` and `StatusBadge` would be reusable for chrome but the *information design* is greenfield.

### Has operator pain been expressed?

  - The "backend coming" hint has been visible since Phase 3C Step 6 (~2 weeks).
  - No operator complaint has surfaced about it.
  - The Ctrl+K affordance is calm; the placeholder behaviour is non-disruptive.
  - Operator workflow today: click sidebar → click tool. Two clicks. Search would save one click in some flows. Not zero, not large.

### Recommendation

**Defer to a later phase (call it 3F or beyond).** Reasons:

  1. **Feature work, not surface polish.** Spec §-class question — needs a `PCC_SEARCH_SURFACE_SPEC` document first.
  2. **No operator demand.** The placeholder hint hasn't surfaced as friction.
  3. **Scope creep risk is high.** Every sub-decision (indexer, ranker, result UI, keyboard model) is an open question.
  4. **Other surfaces are higher value/risk ratio.** Commons Browser specifically would deliver visible cohesion improvement at near-zero risk.

If/when search becomes Phase 3F or later:
  - Open with a `PCC_SEARCH_SURFACE_SPEC_V1` doc analogous to `PCC_DASHBOARD_SURFACE_SPEC_V1`.
  - Define the operator question being answered. ("What does the operator want to find?")
  - Treat the existing shell as a stable affordance — only the backend body changes.
  - Update the placeholder hint OR remove it once a real Enter-action lands.

---

## 4. Commons Browser assessment

### Operator frequency: high-moderate

The Commons Browser is PCC's surface for cross-tool dependency inspection — "which tools use `phoenix_commons.widgets.PrimaryButton`?" / "is this file an orphan?" Operator hits it whenever:
  - Auditing whether a commons addition is used
  - Sanity-checking submodule pin consistency
  - Reviewing what a commons file IS before bumping a tool's pin
  - Inspecting orphan files for cleanup candidates

After Wave 8 retrofits land, the Commons Browser becomes the central inspection surface for that "which tool consumes this widget?" workflow. Frequency is moderate now and grows post-Wave-8.

### Visual mismatch severity: HIGH

After Phase 3C + 3D, Commons Browser is now the **single conspicuously pre-retrofit surface** in the PCC main app. Specifically:
  - `_Chip` inline-styled QLabel chips (lines 25-36) — same generic-Qt look that Phase 3C's `StatusBadge` replaced everywhere else
  - `UsageFooter` `◇` orphan / `◈` used-by chips — emoji glyphs on chrome (the kind Phase 3C-Step-1 + 3D-Step-7 retired)
  - QSplitter inline-styled handle (identical to the line Phase 3D's post-merge cleanup just removed)
  - No `Panel` containers

The operator visiting Commons Browser today sees the contrast immediately after using the modernized dashboard/detail panel: "this surface still looks like the old PCC."

### Primitive reuse: HIGH

| Pre-retrofit element | Commons primitive |
|----------------------|-------------------|
| `_Chip` summary chips (4 of them) | Already-exists `StatusBadge` (compact variant) or `AggregateTile`-style inline metric strip |
| `UsageFooter` orphan/user chips | `StatusBadge` with `clean` (used) / `warning` (orphan) variants |
| `◇` / `◈` emoji glyphs | Lucide `package` (used) + Lucide `warning` (orphan) — both already in `ICON_NAMES` |
| QSplitter inline QSS | Theme.py overlay covers it globally — same fix as Phase 3D cleanup |
| Header refresh button | Already on Lucide (Phase 3C Step 1) |
| Header / page title | Already on `#pageTitle` |
| Could-be-Panel surfaces | `Panel` from `phoenix_commons.widgets` (used in Phase 3D for sync card / commits / TODOs / Git output) |

**Zero new commons primitives needed.** No new icons. No new widgets. The retrofit is mechanical migration to the Phase 3C+3D vocabulary.

### Workflow change: NONE expected

`set_commons_path()` + `set_scanning()` + `set_usage()` + `_on_tree_clicked()` API stays unchanged. The `refresh_requested` signal stays unchanged. The scanner integration (in `main_window.py`) stays unchanged. Only the inside of `_build()` and the `_Chip` + `UsageFooter` classes change.

### Estimated scope

3-4 small commits on a `phase-3e-pcc-commons-browser-retrofit` branch (mirrors the Phase 3D sequencing):

| Hypothetical step | What |
|-------------------|------|
| Step 1 | Summary chip row migration — `_Chip` → `StatusBadge` (compact) or `AggregateTile`-style strip |
| Step 2 | UsageFooter modernization — `◇`/`◈` → Lucide + StatusBadge variants |
| Step 3 | Panel-wrap the tree + viewer + footer surfaces |
| Step 4 (maybe) | Splitter chrome cleanup + final cohesion pass |

Each step ~30-50 LOC delta + an operator-visible review. Same cadence as Phase 3D.

### Risk: LOW

  - No backend logic touched.
  - No new commons API.
  - No BrandProfile change.
  - No new doctrine.
  - Per Phase 3D pattern, identity-preserving and behaviour-preserving.

---

## 5. Settings / Wizard / About / Shortcuts assessment

### Settings dialog — small polish

**Classification:** small polish (not full modernization).

  - 15 inline `setStyleSheet` calls but the surface is small (230 LOC).
  - Could be done in 2 commits: card-wrapping in `Panel` + button migration to commons widgets.
  - Operator frequency: LOW (first-run + reconfigure).
  - Best candidate for Phase 3E's *follow-on* if Commons Browser ships fast.

### New Tool Wizard — full surface modernization OR defer

**Classification:** full surface modernization.

  - Largest remaining surface (1,000+ LOC, 29 setStyleSheet sites).
  - 4-page QStackedWidget with cross-page state coupling.
  - Phase 5/5B/6 already modernized template generation; chrome is the pre-retrofit residue.
  - Risk: medium-high — wizard is the "first impression" surface for tool creation, and the 4-page state machine + commons-detection logic + git submodule wiring make it easy to break.
  - Recommendation: defer until Commons Browser proves the Phase 3E cadence. Treat it as Phase 3F or 3G candidate.

### About dialog — defer (mostly done)

**Classification:** mostly done; defer.

  - Phase 3C Step 1 landed the ATS brand-mark hero (replaced 🔥 emoji).
  - Author card is inline-styled but is appropriate semantic content card (B6 carve-out potential, like dashboard activity rows).
  - Operator frequency: very low.

### Keyboard Shortcuts dialog — small polish OR bundle

**Classification:** small polish (if bundled with About) or leave alone.

  - `⌨` emoji title (line 162).
  - Per-row inline-styled QFrame cards (lines 168, 175).
  - 9 hardcoded shortcuts.
  - Trivial to migrate. ~1 commit.
  - Could be bundled with About into "Phase 3E.2 — about/shortcuts polish" if operator wants both touched.

### Push Preview dialog — leave alone

**Classification:** leave alone (Phase 3D spec §8 preserved it).

  - Operator rarely sees it (only during the detail-panel Push action's confirmation flow).
  - Phase 3D explicitly preserved as out-of-scope.
  - Reopening would re-expand Phase 3D scope, which the closure forbids.

---

## 6. Recommended Phase 3E target

### **A — Commons Browser modernization.**

**Why it is next:**

  - **Highest combined score** (27/30) in the §2 ranking.
  - **Most jarring remaining visual mismatch** — after dashboard + detail panel landed cohesively, Commons Browser is the conspicuous odd-one-out in the PCC main app.
  - **Zero new commons primitives required.** Every chrome migration maps to a primitive already proven in Phase 3C or 3D (Panel, StatusBadge, Lucide icons).
  - **Risk profile mirrors Phase 3D's lowest steps.** Mechanical migration; clear analogs in the detail panel's Files tab.
  - **Operator value grows post-Wave-8** — Commons Browser becomes the central "which tool uses this?" inspection surface as production tools roll into the retrofit cadence.
  - **Cadence fits the proven Phase 3C/3D discipline.** 3-4 small operator-gated commits on `phase-3e-pcc-commons-browser-retrofit`.
  - **Continuous-improvement principle.** "Small disciplined surface work beats broad redesign."

**Why the others are not next:**

  - **B — Search backend:** feature work, not surface polish. No operator pain. Needs its own surface spec doc. High risk, high scope creep. Defer to Phase 3F+.
  - **C — Settings dialog polish:** low operator frequency. Should follow Commons Browser, not lead.
  - **D — Wizard modernization:** largest LOC, highest risk in the candidate pool. Better to land Commons Browser first as a Phase 3E proof point before touching the wizard.
  - **E — About dialog polish:** mostly done in Phase 3C. Only the Shortcuts row-cards remain. Trivial; bundle later.
  - **F — Bundle several tiny dialog polish items:** viable as Phase 3E.2 after Commons Browser ships, but as a *standalone Phase 3E* it spreads attention too thin. Commons Browser is the higher single-target value.
  - **G — Do nothing until Wave 8a cooldown clears:** would leave an obvious visual mismatch in place for 11+ days. Phase 3E shipping during the Wave 8a cooldown actually *strengthens* the operator's confidence in the retrofit cadence; the cooldown is a Wave-8a-specific gate, not a global pause.

### Expected scope

| Dimension | Estimate |
|-----------|----------|
| Branch | `phase-3e-pcc-commons-browser-retrofit` |
| Step count | 3-4 small commits |
| LOC delta | +50 / −50 (modernization, not expansion) |
| Commons primitives added | **0** |
| Commons icons added | **0** (or 1, only if a clear semantic gap surfaces) |
| ADR changes | **0** |
| BrandProfile changes | **0** |
| Backend logic changes | **0** |
| New doctrine | **0** |
| Spec doc required | Small — likely `PCC_COMMONS_BROWSER_SURFACE_SPEC_V1` (analogous to detail-panel spec; ~300 lines) |
| Operator-visible chrome change | High (the surface goes from "old PCC" to dashboard/detail-cohesive) |
| Operator workflow change | Zero |

### Risk level: LOW

Matches Phase 3D's lowest-risk steps. Equivalent in risk to Phase 3D Step 7 (Files-tab cohesion pass).

### Spec required: yes — small

A short spec doc (≤300 lines) following the `PCC_DETAIL_PANEL_SURFACE_SPEC_V1` template. Sections likely:
  - Product intent (recap)
  - Workflow audit
  - Surface inventory (~3 surfaces: header chip row, splitter body, usage footer)
  - Step sequencing (3-4 steps)
  - Explicit "do NOT" list (no backend change, no scanner change, no usage-data format change)
  - Visual review checkpoints

---

## 7. Risks

### R1 — Operator perceives "more retrofit work" as fatigue

Phase 3D just closed. Phase 3C-3D were back-to-back. Even a small Phase 3E could feel like the retrofit cadence won't stop. **Mitigation:** Frame Phase 3E explicitly as the *final* PCC main-app surface to modernize. Settings / Wizard / About can be sub-phases later with no doctrinal commitment.

### R2 — Commons-side scanner/usage-data format drift

The Commons Browser depends on `scanner.set_usage()` returning a specific dict shape (`{rel_path: {users: [...], size: int}}`). Spec §8 of the Phase 3E spec must explicitly forbid altering that shape. **Mitigation:** Audit the scanner contract before authoring the spec; document the shape in §8.

### R3 — Splitter / FileViewer coupling

Commons Browser uses the same QSplitter + QFileSystemModel + FileViewer pattern as detail-panel Files tab. The detail panel preserved FileViewer; Phase 3E spec must do the same. **Mitigation:** Direct copy-paste of the Phase 3D Files-tab `do NOT` list into the Phase 3E spec.

### R4 — Wave 8a pressure conflict

If the operator opens Wave 8a immediately on 2026-06-02 (cooldown floor), and Phase 3E is still mid-flight, there's a parallel-work risk. **Mitigation:** Phase 3E is small (3-4 commits over 1-2 sessions). Should fit comfortably inside the 11-day window before 2026-06-02. If it doesn't, Wave 8a is the higher doctrinal priority and Phase 3E pauses.

### R5 — Scope creep into search backend

The Commons Browser is on the dashboard page. Operator might want "search across commons files" while we're already in the file. **Mitigation:** Phase 3E spec explicitly forbids search backend work. Search backend is its own future Phase 3F or later.

### R6 — Scope creep into wizard or settings

Once Phase 3E is open, the temptation to "while we're modernizing dialogs, do settings too" is real. **Mitigation:** Phase 3E spec scope is *Commons Browser only*. Settings + wizard + about are explicit future-phase candidates; not in Phase 3E.

---

## 8. Suggested next prompt after operator approval

If operator approves direction A (Commons Browser), the next prompt should follow the Phase 3D / Phase 3C pattern:

```
Proceed with:

# Phase 3E — PCC Commons Browser Surface Spec Authoring

Context:
PCC_PHASE_3E_CANDIDATE_AUDIT_REPORT.md concluded with direction
A — Commons Browser modernization.

Phase 3E is now:
ready for surface-spec authoring.

PRIMARY OBJECTIVE
Author PCC_COMMONS_BROWSER_SURFACE_SPEC_V1.md following the
PCC_DETAIL_PANEL_SURFACE_SPEC_V1 template.

Output file path:
phoenix-commons/docs/ui-platform-baseline-v1/
   PCC_COMMONS_BROWSER_SURFACE_SPEC_V1.md

Spec must include:
- Product intent (recap)
- Workflow audit (current commons_browser.py state)
- Surface inventory (3 surfaces: header chip row, splitter body, usage footer)
- Interaction philosophy (recap from dashboard/detail)
- Visual direction (no new BrandProfile slots)
- Information hierarchy
- Implementation sequencing (3-4 steps)
- Explicit "do NOT do" list (no backend change, no scanner change,
  no usage-data format change, no FileViewer redesign, no search
  backend, no settings/wizard scope, no commons API change)
- Relationship to existing dashboard/detail language

STRICT CONSTRAINTS:
- spec only; no implementation
- no commons primitives added
- no BrandProfile changes
- no ADR work
- no Phase 3F work
- no Wave 8a interaction

OUTPUT:
PCC_COMMONS_BROWSER_SURFACE_SPEC_V1.md
+ short rationale why each section is included
+ stop conditions for the implementation phases

Do NOT begin implementation until spec is operator-approved.
```

---

## 9. Confirmation

  - **No implementation occurred in this audit session.** No source files edited. No commits made (except this report). No commons API change. No PCC code change.
  - **No architecture changes occurred.** No new ADR. No commons widget added. No BrandProfile change. No commons API extension.
  - **No production deployment occurred.** PCC remains unpackaged. No installer built. No `dist/` artifact. No GitHub Release.
  - **No production tool source touched.** Phoenix CAD / Phoenix Checkout / PTT / ValveMaster all unmodified.
  - **No Phase 3E implementation has begun.** This is the candidate audit only.
  - **No Wave 8a work has begun.** Wave 8a remains operator-gated (cooldown floor 2026-06-02).
  - **No Step 8 work has begun.** Detail-panel keyboard shortcuts remain deferred.
  - **No search backend work has begun.** Search backend remains a deferred Phase 3F+ candidate.

---

*End of report. Phase 3E direction recommended: A — Commons Browser modernization. Awaiting operator approval before spec authoring begins.*
