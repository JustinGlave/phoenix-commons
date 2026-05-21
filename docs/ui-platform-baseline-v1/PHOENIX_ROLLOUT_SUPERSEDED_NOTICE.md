# STATUS: This rollout plan is SUPERSEDED

> **Status:** SUPERSEDED by ADR-016 (`phoenix-commons/docs/ui-platform-baseline-v1/ADR_PCC_PALETTE_RECONCILIATION.md`) and the subsequent baseline + retrofit work.
> **Confirmed by operator:** 2026-05-21.
> **Plan author timestamp:** files in this folder were last touched 2026-05-21 but represent the **pre-Phase-3A direction** — the rollout was drafted before the BrandProfile architecture was decided.
> **What's still useful:** ideas in Phases 4-6 (helper-class adoption, Lucide icon migration, status-pill semantics) remain compatible with the current architecture and should inform PCC's future polish phases. Phases 1-3 as written are no longer applicable — see §3 below for why.

---

## TL;DR

The rollout plan in this folder describes a **single canonical brand QSS** (navy + red + blue) shared verbatim by every Phoenix tool, with each app's `theme.py` reduced to a 10-line `_APP_ADDENDUM`. That was the original direction.

That direction was **changed** when the `BrandProfile` architecture was introduced (ADR-016) and codified in `phoenix-commons`. Under ADR-016, the canonical QSS still lives in commons but carries three sentinel tokens (`__BRAND_PRIMARY__`, `__BRAND_SECONDARY__`, `__BRAND_ACCENT__`) that get substituted at apply time per a caller-supplied `BrandProfile`. PCC is the only tool with a custom profile (orange + teal) — every other Phoenix tool uses `DEFAULT_BRAND` (red + deep blue + blue) implicitly.

**Phase 3A (Lab Layout Tool)** and **Phase 3B (Phoenix Checkout)** have already merged to master under this architecture. **Phase 3C (PCC)** is in flight on `phase-3c-pcc-retrofit` using the same architecture. The rollout plan's Phase 1 PCC-tactical patch (`step-1-patch/`) has never been applied and will not be — PCC moved directly to the commons-backed BrandProfile architecture in Phase 3C.

This file is a supersession notice + a salvage map of which rollout ideas remain useful under the new architecture. It is **not** a divergence-to-fix; the divergence is intentional and the rollout plan is the side that's been retired.

---

## 1. What changed since this plan was authored

| Aspect | This rollout plan said | What actually happened |
|--------|------------------------|-------------------------|
| QSS source-of-truth | One canonical file, copied verbatim from Checkout, hard-coded brand values | Same file, but sentinel-tokenised. Brand values substituted per `BrandProfile` at apply time. |
| Per-app palette | Universal red + navy + blue, no overrides allowed (VISION.md Principle 2) | Default red + navy + blue for most tools; PCC overrides via `BrandProfile(primary="#E8783C", secondary="#2A8880", accent="#3CB8AE")` per ADR-016 — sanctioned escape hatch with a closed list of 3 slots. |
| Per-app theme.py | 10-line `_APP_ADDENDUM` only — apps may NOT redefine tokens | Per-app theme.py can override the 3 brand slots via `BrandProfile` + an `_APP_ADDENDUM`-style overlay. Non-brand tokens still come from commons. |
| Commons package layout | `phoenix_commons/ui/` subpackage with `theme.py` / `components.py` / `icons/` | `phoenix_commons/` flat — `theme/` (apply.py + tokens.py + embedded_qss.py + phoenix_style.qss), `widgets/` (buttons / panel / table / typography / no_scroll / update_banner / helpers), `icons/` (loader + registry + 10 Lucide SVGs), `paths/`, `updater/` (client + installer + qt). |
| Commons distribution | `pip install -e .` or sys.path sibling | git submodule + editable install per ADR-015 |
| Components covered | PrimaryButton, SecondaryButton, TertiaryButton, PhoenixTable, StatusBadge (stub) | Same 3 buttons + Panel + PhoenixTable + PageTitle + PageSubtitle + SectionTitle + HintLabel + UpdateBanner + button_row + no-scroll family of 4. **`StatusBadge` is NOT yet implemented** — only mentioned in the rollout's Phase 6 spec. |
| Build hardening | Not specified | `FROZEN_BUILD_BASELINE.md` (Python 3.12, PyInstaller 6.20.0, --noupx, stdlib excludes, deterministic cleanup, build.bat Python-version gate) — empirically validated against SentinelOne quarantine in EXPERIMENT_REPORT_03. |
| Auto-updater | Not specified | Full `phoenix_commons.updater` (client + installer + Qt thread) + Phase 6C runtime + updater dry-run validated end-to-end. |
| Documentation | README + VISION + ROADMAP + INVENTORY in this folder | 30+ docs in `phoenix-commons/docs/ui-platform-baseline-v1/`: PLATFORM_CONTRACT, DECISIONS (full ADR series 001-016), MIGRATION_RULES, RETROFIT_PLAYBOOK, VERIFICATION_MATRIX, multiple STABILIZATION/OPERATIONAL/PHASE reports. |

The current architecture is much further along, much more documented, and much more tested than what this rollout plan describes. The rollout plan is a snapshot of an earlier intent.

---

## 2. What's still useful from this plan

Three ideas from the rollout plan are **compatible with ADR-016** and remain on the table as future PCC work. They've simply not been done yet under the new architecture's labels.

### Phase 4 — helper component classes (still applicable)

The plan's call for replacing `QPushButton().setObjectName("accentBtn")`-style construction with `PrimaryButton(...)` etc. is exactly what `phoenix_commons.widgets.*` exposes today. PCC currently does not consume these — its dashboard / sidebar / detail-panel widgets are raw Qt with PCC-specific `objectName`s. Migrating PCC to use the commons widget classes is a future polish step (call it Phase 3D or Phase 9), conceptually identical to the rollout's Phase 4.

### Phase 5 — Lucide SVG icons (still applicable)

`phoenix_commons.icons` already ships the loader, registry, and 10 Lucide SVGs (check, info, plus, refresh, save, search, settings, trash, warning, x). PCC currently uses emoji glyphs (🔥 ◎ ◆ ◈ ✦ ↻ ⚙ 📌 📄 💾 ●). The rollout's Phase 5 work — replace every emoji glyph with `icon(name, color)` — is still the correct next direction. Same scope, just using `phoenix_commons.icons.icon()` instead of a new-to-be-built helper.

### Phase 6 — labelled status pills (still applicable)

The screenshot's "Clean" / "3 changes" / "12 changes" tabular status indicators are exactly the `StatusBadge` widget the rollout's Phase 6 calls for. The widget does **not** yet exist in commons — it was specified in the rollout but never built. Building it is a fresh commons addition (small, additive, no ADR change needed) before PCC can adopt it.

---

## 3. What is NOT applicable (and why)

### Phase 1 (PCC tactical) — superseded

Phase 1 says: drop `phoenix_style.qss` + a brand-correct `theme.py` + an updated `build.bat` into PCC's root. PCC would then have its own local copy of the canonical QSS, no commons dependency.

**Why it doesn't apply:**

- PCC's Phase 3C (in flight) goes the **other** direction — PCC consumes the canonical QSS *from commons* via the submodule + editable install. There is no PCC-local `phoenix_style.qss`.
- Phase 1's `theme.py` mapped `C["accent"]` to `#dc2626` (Phoenix Red). PCC's current `theme.py` maps `C["accent"]` to `PCC_BRAND.primary = #E8783C` (Phoenix Orange) per ADR-016. The two are mutually exclusive.
- Phase 1's explicit non-goals ("don't touch emoji, status dots, sidebar width, objectNames, sprite") are still respected — but the chrome palette is intentionally different from what Phase 1 wanted.

Applying Phase 1 today would require **reverting** ADR-016 + Phase 3A + Phase 3B + PCC Phase 3C. Operator has confirmed this is the wrong direction.

### Phase 2 (commons UI foundation) — superseded

Phase 2 says: create `phoenix-commons/phoenix_commons/ui/` with a minimal QSS + theme + components + icons skeleton.

**Why it doesn't apply:**

- Commons is already past Phase 2's scope. It has the QSS (sentinel-tokenised), a programmatic theme apply with palette + Fusion style + brand substitution, a full widgets package, an icons package, paths, and an updater. None of this fits at `phoenix_commons/ui/` — it lives at the package root.
- Phase 2's `theme.py` exposes a `make_qss()` function that returns the QSS as a string. Commons exposes `apply_dark_theme(app, brand=...)` instead — it applies the theme directly to a `QApplication`. The interface is different.

Re-doing Phase 2 today would require deleting most of `phoenix_commons/` and rebuilding to the rollout's flatter shape. That's not happening.

### Phase 3 (migrate apps) — partial mismatch

Phase 3's per-app procedure (steps 1-8) is **roughly** the shape of the Phase 3A/3B retrofits that already merged — diff the app's QSS, extract legitimate selectors, replace local QSS with import-from-commons, update build.bat. But the **target signatures** differ:

- Phase 3 expects each app's theme.py to call `_base_qss()` (returns a string) + concatenate an addendum.
- Phase 3A/3B retrofits call `apply_dark_theme(app, brand=...)` (applies to app) and rely on the app cascade — no string concatenation.

The PCC Phase 3C retrofit (commits B1-B7 on `phase-3c-pcc-retrofit`) follows the 3A/3B pattern, not the rollout's Phase 3 pattern.

### Phases 7-8 — partial / different

- **Phase 7 (PCC New Tool wizard):** PCC's wizard was already updated for commons-backed templates during Phase 5/5B (well before the rollout's Phase 7). The wizard offers two radio options: "Phoenix Tool — standalone" and "Phoenix Tool — commons-backed" (per the lively-koala plan refinement). Done, but earlier than the rollout schedules it.
- **Phase 8 (CI guards):** CI exists per-app (windows-latest, Python 3.12, offscreen Qt smoke tests). The specific guards the rollout proposes ("fail if `setStyleSheet()` outside theme.py", "fail if emoji glyphs in source", "fail if local QSS exceeds size budget") are NOT implemented. These are legitimate future additions.

---

## 4. The operator's screenshot under the current architecture

The screenshot represents a future PCC design that has 14 visible surfaces. Under ADR-016 / commons, each maps as follows:

| Surface | Status | Phase under new architecture |
|---------|--------|------------------------------|
| Navy `#0a0e27` background | PCC currently `#18181F` (purple-grey per ADR-016) | **Open question:** does PCC adopt navy bg, or stay purple-grey per ADR-016's "management-app identity" rationale? If navy, change PCC_BRAND or change PCC `C["bg"]`. |
| Red `+ New tool` button | PCC currently orange `#E8783C` via `PCC_BRAND.primary` | If the screenshot's red is canonical for PCC, swap `PCC_BRAND.primary` from `#E8783C` to `#dc2626`. Single-line change in `theme.py`. Could also imply abandoning the PCC orange identity altogether. |
| Bright blue accents | PCC currently teal `#3CB8AE` via `PCC_BRAND.accent` | Same as above for the accent slot. |
| Lucide nav icons in sidebar | Emoji today | Adopt `phoenix_commons.icons.icon()` — "Phase 5 work under new architecture". Mechanical. |
| Status dots on sidebar tools | Already exists | Keep as-is (screenshot also uses dots in sidebar). |
| Page title "Dashboard" | Exists | Already works. |
| **Search bar with ⌘K shortcut** | Does not exist | **Net-new surface.** Spec needed: width / placeholder text / what it searches (tools / commits / TODOs) / activation hotkey / result list shape. |
| **"All synced · 14:22" status pill** | Does not exist | **Net-new surface.** Spec needed: what triggers the timestamp / what "synced" means / where the pill anchors. |
| **4 aggregate tiles with leading icons + subtitles** | 5 tiles, inline-styled, no icons | Spec needed: which 4 tiles (current has 5 — drop one?), tile icon mapping, subtitle copy convention. |
| **Tools TABLE with NAME / LAST COMMIT / LOC / SIZE / STATUS columns** | List of `ToolRow` widgets | **Net-new layout.** Spec needed: use `phoenix_commons.widgets.PhoenixTable`? Column order? Sort behavior? Row click → detail panel? Per-row context menu? |
| **Status pills in table ("Clean" / "3 changes" / "12 changes")** | Status dot only (no text) | **Net-new widget.** `StatusBadge` doesn't yet exist in commons (rollout Phase 6 spec). Build it in commons first, then PCC adopts it. |
| **Per-tool coloured activity tag pills** | Uniform accent colour for all tags | Spec needed: colour mapping per tool (checkout=green? lab-layout=orange? job-tracker=blue? commons=cyan? master-tool=red? — these match the per-app brand-mark colours in INVENTORY.md). |
| **Status-bar "Press ⌘K to search" hint** | Does not exist | Tied to the search bar spec. |
| **ATS sprite at small thumbnail size** | Animated WebP at large size in sidebar | Mechanical resize, or replace with the static `assets/logo.png` at thumbnail size. |

**4 surfaces are simple wiring** (icon adoption, palette swap, sprite resize). **3 surfaces need fresh specs** (search bar, status pill, aggregate-tile copy). **2 surfaces need new commons primitives** (`StatusBadge` widget, per-tool colour mapping). **1 surface is a major layout change** (tools table replacing tools list/cards).

---

## 5. Recommended next moves (for operator decision, not execution)

In rough order of safety:

1. **Archive this folder.** Move `phoenix-rollout/` to `phoenix-rollout-archive-2026-05-21/` or similar. The STATUS_SUPERSEDED.md you're reading is the breadcrumb that explains why.
2. **Decide the PCC palette question.** Is PCC navy + red + blue (matching the screenshot, matching siblings, abandoning ADR-016's orange/teal carve-out)? Or is PCC navy + orange + teal (keeping the management-app identity, screenshot's reds are aspirational and wrong for PCC)? This is a 1-line code change either way but it gates everything else.
3. **Author surface-level specs** for the screenshot's net-new surfaces (search bar, "All synced" pill, tools table, status badges, per-tool activity colours). These can live in `phoenix-commons/docs/ui-platform-baseline-v1/SCREENSHOT_TARGET_SPECS/` or similar. Operator approval per surface.
4. **Build `StatusBadge` in commons** as a small additive component (the rollout's Phase 6 spec is fine — implement it). Then PCC can adopt it for the tools-table status column.
5. **Adopt `phoenix_commons.icons` in PCC** — replace emoji glyphs with `icon()` calls. Mechanical migration, one PR.
6. **Wire the tools table** as a `PhoenixTable` instance in the dashboard. Replaces the current `ToolRow` list. This is the right "wire ToolCard"-shaped commit that B8 should have been.
7. **Net-new surfaces (search bar, status pill, status-bar hint)** as separate B-series commits with explicit operator approval per surface. None of these should land without their spec doc landing first.

None of these are scheduled here. The audit only documents the landscape.

---

## 6. What I am NOT doing

- Not editing PCC source.
- Not editing commons source.
- Not picking the PCC palette question.
- Not implementing any surface from the screenshot.
- Not building `StatusBadge`.
- Not committing this file anywhere — neither `phoenix-rollout/`, `phoenix-command-center/`, nor `phoenix-commons/`. Operator can move/rename/commit per their direction. (`phoenix-rollout/` is not a git repo, so this file lives on disk as a plain-text note.)
- Not reverting B5/B6/B7 on PCC.

This file is the only output of the audit.

---

*End of supersession notice.*
