# STABILIZATION_REPORT_07.md

> ADR-016 — PCC palette reconciliation. The final architecture-
> level design decision before Phase 3A pilot migrations begin.
> Resolves the three-palettes-in-production finding from Phase
> 2.7.
>
> Documentation only. No source code touched, no production
> tools modified, no token implementation, no QSS rewrites, no
> screenshots captured, no migrations / retrofits / builds /
> runtime work.
>
> Captured 2026-05-19.

## 1. Status

**Passed.** ADR-016 finalised. All deliverables landed as two
logical commits on `main`, plus this report (commit 3). Pushed
to origin (`95c00f7..ea321c6` then this report).

- New standalone ADR document at
  `ADR_PCC_PALETTE_RECONCILIATION.md` (693 lines).
- Summary row mirrored in `DECISIONS.md` § FINALIZED.
- `DESIGN_SYSTEM.md` updated — replaced the misleading "PCC
  palette as System A" content with the accurate canonical +
  brand-profile structure.
- `PLATFORM_CONTRACT.md` § Theme tokens updated — locked vs
  variant-allowed classification per ADR-016.

**Outcome:** Option B chosen — **controlled accent override**.
Commons exposes 3 named brand tokens (`PRIMARY`, `SECONDARY`,
`ACCENT`) that apps may override via a `BrandProfile` mechanism;
every other token (BG, SURFACE, TEXT, MUTED, status colours, all
spacing, all typography, all radii) is locked. PCC keeps orange +
teal as its registered brand profile; every other production
tool uses the default red + blue.

**Phase 3A is now architecturally approved** — see §7.

## 2. Options evaluated

Full evaluation in `ADR_PCC_PALETTE_RECONCILIATION.md` § 3.
Summary:

### Option A — PCC adopts the full commons canonical palette

| Aspect | Verdict |
|--------|---------|
| Design simplicity | ✅ Highest |
| PCC brand identity | ❌ Eliminated |
| Path for future tool accent variants | ❌ None |
| Commons API surface | ✅ Zero added |
| Migration cost | Moderate (PCC retrofit only) |
| Fragmentation risk | ✅ Zero |
| **Verdict** | **Rejected** — loses PCC identity and has no path for legitimate future accent variants |

### Option B — controlled accent override (chosen)

| Aspect | Verdict |
|--------|---------|
| Design simplicity | Moderate (one extra concept: `BrandProfile`) |
| PCC brand identity | ✅ Preserved |
| Path for future tool accent variants | ✅ Explicit, controlled |
| One widget system / QSS / token hierarchy | ✅ Preserved |
| Commons API surface | One small addition (3-slot `BrandProfile` + `apply_dark_theme(brand=...)` kwarg) |
| Migration cost | Modest |
| Fragmentation risk | Low — bounded by the closed 3-slot list |
| **Verdict** | **CHOSEN** |

### Option C — per-app arbitrary themes

| Aspect | Verdict |
|--------|---------|
| Design simplicity | ❌ Slow-motion fork by design |
| Accessibility | ❌ Lost contrast guarantees |
| Semantic colour consistency | ❌ Drifts |
| Widget visual consistency | ❌ Breaks |
| Contradicts ADR-001 / ADR-002 | ❌ Yes |
| Fragmentation risk | ❌ Maximum |
| **Verdict** | **Rejected** — would invalidate the architecture stabilization work of the last six phases |

## 3. Chosen direction

**Option B — controlled accent override.**

### What changes

1. **Token classification** introduced in `tokens.py` semantics
   (per ADR-016 § 7):
   - **Locked** (apps may NOT override): BG, SURFACE, SURFACE_ALT,
     TEXT, MUTED, SUCCESS, WARNING, ERROR, all future
     spacing/typography/radius tokens.
   - **Variant-allowed** (apps may override via `BrandProfile`):
     PRIMARY, SECONDARY, ACCENT. INFO is aliased to ACCENT and
     follows automatically.
2. **`BrandProfile` mechanism** (lands in Phase 3+): a frozen
   dataclass with 3 named slots; default values match the
   commons canonical (red/blue). Apps that want a non-default
   brand register their own profile and pass it to
   `apply_dark_theme(app, brand=...)`.
3. **Sentinel-form QSS** (Phase 3+ implementation): brand-token
   hex literals in `phoenix_style.qss` become sentinels
   (`__BRAND_PRIMARY__`, etc.) substituted at apply time per the
   active brand profile. Locked tokens stay literal.
4. **PCC's brand profile**: orange + teal + teal (Phase 3C
   retrofit registers it).
5. **Phoenix CAD / Job Tracker / Phoenix Checkout / ValveMaster
   (post Phase 8a)**: use the default brand profile — no
   `brand=` kwarg required, no code change relative to current
   plans.

### What stays unchanged

- One widget system (`phoenix_commons.widgets`).
- One QSS architecture (`phoenix_style.qss`).
- One token hierarchy (`phoenix_commons.theme.tokens`).
- One spacing scale, one typography ramp, one radius scale.
- ADR-001 (commons as UI platform).
- ADR-002 (apps extend via addendum, not fork).
- The brand-profile mechanism IS the controlled extension point
  ADR-002 anticipates; it's not a violation of it.

## 4. Rejected directions

For the record (so the same proposals aren't re-litigated):

| Option | Why rejected | Future trigger to revisit |
|--------|---------------|----------------------------|
| A — full canonical | Loses PCC identity; no path for future tool accent variants | If PCC's brand-profile maintenance becomes a real burden in practice, ADR-016 could be superseded to force PCC to canonical. None today. |
| C — arbitrary themes | Slow-motion design-system fork; contradicts ADR-001 + ADR-002 | Effectively never. Adopting C would invalidate the architecture work; would require a foundational reset. |

## 5. Migration implications

For each tool, what changes after ADR-016:

| Tool | Brand profile | Retrofit work specific to ADR-016 |
|------|---------------|------------------------------------|
| Phoenix CAD / Lab Layout Tool | Default | None — Phase 3A retrofit uses default; no `brand=` kwarg required. (May land the `BrandProfile` mechanism itself as enabling work — see §7.) |
| Job Tracker / Project Tracking Tool | Default | None — Phase 8 retrofit uses default. |
| Phoenix Checkout | Default | None — Phase 3B retrofit uses default. |
| **Phoenix Command Center** | **Custom (orange + teal + teal)** | PCC's retrofit PR registers `BrandProfile(primary="#E8783C", secondary="#3CB8AE", accent="#3CB8AE")` and passes it to `apply_dark_theme(...)`. Deletes the local `theme.py` C-dict + QSS generator. Per ADR-016 § 9. |
| ValveMaster | Default (post Phase 8a) | None — Phase 8a retrofit moves from System B gray to default brand profile (red/blue). No PCC-style override. |

The `MIGRATION_VISUAL_REVIEW_CHECKLIST.md` § "Phoenix Command
Center" addendum (the row gating "Decision recorded in an ADR
before this PR opens") is **satisfied** by ADR-016. The
checklist will be updated when PCC's actual retrofit PR opens
to swap the gate for new rows verifying the brand profile is
correctly registered.

## 6. Platform-governance implications

ADR-016 introduces a new governance vector — **brand profiles** —
that must be governed lightly to avoid drift:

1. **Closed slot list.** The variant-allowed slot list (PRIMARY,
   SECONDARY, ACCENT) is intentionally minimal. Adding a fourth
   slot requires a new ADR superseding ADR-016.
2. **Brand profiles live in app source, not in commons.** Each
   tool declares its `BrandProfile` in its own repo, near the
   `apply_dark_theme(app, brand=...)` call. Changing a tool's
   brand profile is an app-side commit; doesn't require a
   commons release.
3. **Locked tokens at runtime: hard-failure on attempted
   override.** Phase 3+ implementation enforces — if app code
   tries to override `tokens.BG` at runtime, it raises (or is
   otherwise blocked) so the divergence surfaces immediately.
4. **PCC is currently the only tool with a non-default brand
   profile.** Future tools may register their own, but the
   commons PR-review process for the wizard's brand-profile
   question (Phase 5+) sets the bar — default is expected
   unless a brand reason is clear.

## 7. Token implications

`phoenix_commons.theme.tokens` (Phase 2.5) becomes
two-tiered:

```python
# After Phase 3+ implementation (sketch; NOT in this phase):

# LOCKED — apps may not override:
BG           = "#0a0e27"
SURFACE      = "#141829"
SURFACE_ALT  = "#0f1219"
TEXT         = "#ffffff"
MUTED        = "#94a3b8"
SUCCESS      = "#22c55e"
WARNING      = "#f59e0b"
ERROR        = "#ef4444"

# VARIANT-ALLOWED — default values; apps may override via BrandProfile:
PRIMARY      = "#dc2626"   # default brand red
SECONDARY    = "#1e3a8a"   # default brand deep blue
ACCENT       = "#3b82f6"   # default brand blue
INFO         = ACCENT      # alias — follows ACCENT automatically

@dataclass(frozen=True)
class BrandProfile:
    primary:   str = PRIMARY
    secondary: str = SECONDARY
    accent:    str = ACCENT

DEFAULT_BRAND = BrandProfile()

# SEMANTIC_COLORS and C remain — after Phase 3+ they become
# functions of the active brand profile.
```

**Today (this phase, post-ADR-016):** No code change.
`tokens.py` still has all twelve constants as plain literals.
The ADR is documentation; the mechanism lands in Phase 3+.

## 8. Phase 3A approval

**Architecturally: YES.** With ADR-016 landed and the baseline
docs updated, every architecture-level question raised by Phase
2.7's pre-pilot readiness audit is resolved.

The four-row pre-Phase-3A blocker list from
`STABILIZATION_REPORT_06.md` § 10 now stands at:

| # | Blocker | Status post-ADR-016 |
|---|---------|----------------------|
| 1 | User approval to start Phase 3A | ⏳ **Still required** — per `BASELINE.md` stop conditions. Not in commons's hands. |
| 2 | PCC palette reconciliation ADR | ✅ **Closed** by ADR-016 |
| 3 | `DESIGN_SYSTEM.md` "System A" naming collision | ✅ **Closed** by commit 2 of this phase |
| 4 | S1/AV chain (`BLOCKERS.md §1`) | 🔴 Still blocks frozen-mode + installer rows (out of commons scope; doesn't block source-mode Phase 3A) |
| 5 | Screenshot-capture moment | 🔴 First retrofit PR's choice; doesn't block start |

**Net:** Phase 3A architecturally approved. Only the user-
approval gate (#1) remains commons-side.

### Recommended order for Phase 3A first PR

Per ADR-016 § 12, the recommendation is:

**Phase 3A — Phoenix CAD retrofit** lands BOTH:
- The retrofit itself (delete local widget copies, switch to
  commons imports, etc. — visible change ≈ 0).
- The `BrandProfile` mechanism + sentinel-form QSS as enabling
  work (Phoenix CAD uses the default profile so the implementation
  is exercised but not the override path).

This avoids Phase 3C / PCC's retrofit landing both the
mechanism AND its first non-default usage in the same PR. The
override path is then exercised at PCC retrofit time.

This recommendation is for the user to accept or override at
Phase 3A approval — it's not part of ADR-016 itself.

## 9. Remaining blockers after the ADR

| # | Blocker | Blocks | Action needed |
|---|---------|--------|----------------|
| 1 | User approval to begin Phase 3A | Every retrofit | Explicit user approval per `BASELINE.md`. |
| 2 | S1/AV bootloader-quarantine | Frozen-exe validation + installer testing + real updater deploy | Out of commons scope (`BLOCKERS.md §1`). Source-mode Phase 3A unaffected. |
| 3 | Screenshot-capture moment | Pixel-level baselines (not markdown structural baselines, which are already done) | First retrofit PR's choice. |

Blockers 2 + 3 are external; they don't block the architectural
start of Phase 3A. Blocker 1 is the single gate remaining.

## 10. Risks discovered / judgment calls

| # | Item | Resolution |
|---|------|------------|
| 1 | ADR could have chosen Option A and saved future BrandProfile-mechanism implementation cost. | Rejected — loses PCC identity + no path for legitimate future accent variants. The mechanism cost is modest and one-time. Documented in ADR § 3 (Option A cons + rejection rationale). |
| 2 | ADR could have chosen Option C and given each tool freedom. | Rejected — contradicts ADR-001 + ADR-002; introduces slow-motion design-system fork. Documented in ADR § 6 (Option C rejection rationale). |
| 3 | The DESIGN_SYSTEM.md revision corrected a previously-published button-objectName table (`accentBtn` / `ghostBtn`) that never matched commons code. | Treated as a doc fact-fix, not a code change. The widget code's `(default)` / `secondaryButton` / `tertiaryButton` were always the source of truth; the previous doc revision was simply wrong. |
| 4 | DESIGN_SYSTEM.md previously documented PCC's `theme.py` palette (orange + teal) as the canonical "System A." | Replaced with the actual canonical (red + blue) + brand-profile explanation. The naming collision Phase 2.7 surfaced is now resolved at the doc level. |
| 5 | The 3-slot brand-profile design (`PRIMARY`, `SECONDARY`, `ACCENT`) could grow in future to 4+. | Closed slot list with explicit ADR-supersession rule for expansion. Documented in ADR § 9. |
| 6 | PCC's specific brand-profile mapping isn't 1-to-1 (PCC has `accent` = orange, `teal` = secondary; commons has `PRIMARY` = brand emphasis, `SECONDARY` = supporting, `ACCENT` = focus). | PCC's retrofit PR makes the exact mapping decision. ADR-016 § 9 documents the proposed mapping (`PRIMARY=#E8783C`, `SECONDARY=#3CB8AE`, `ACCENT=#3CB8AE`) but leaves the final call to the retrofit PR if PCC wants e.g. `ACCENT` to be a third colour distinct from teal. |
| 7 | Phase 3+ implementation timing (in Phase 3A vs Phase 3C) is recommended in the ADR but not mandated. | Decision belongs to Phase 3A's user-approval step. Recommendation: implement in Phase 3A as enabling work so PCC doesn't have to land mechanism + usage simultaneously. |

No new blockers added to `BLOCKERS.md`. This phase is fully
source-only + doc-only + AV-independent.

## 11. Commits (in order)

```
$ git log --oneline -4

ea321c6 Update DESIGN_SYSTEM + PLATFORM_CONTRACT post-ADR-016
ae231ec Add ADR-016 — PCC palette reconciliation (controlled accent override)
95c00f7 Add STABILIZATION_REPORT_06 — Phase 2.7 visual baselines
5d47c85 Add MIGRATION_VISUAL_REVIEW_CHECKLIST.md (Phase 2.7)
```

Per the user's commit plan (2 logical commits + report):

| # | Hash | Subject | Touches |
|---|------|---------|---------|
| 1 | `ae231ec` | ADR document | `ADR_PCC_PALETTE_RECONCILIATION.md` (+673 lines), `DECISIONS.md` (+20 lines ADR-016 row) |
| 2 | `ea321c6` | Baseline doc updates | `DESIGN_SYSTEM.md` (+89/-58 lines), `PLATFORM_CONTRACT.md` (+33/-6 lines) |

Cumulative diff vs `95c00f7`:

```
 ADR_PCC_PALETTE_RECONCILIATION.md | 673 +++++++++++++++++++++
 DECISIONS.md                      |  20 +-
 DESIGN_SYSTEM.md                  | 147 +++++++----
 PLATFORM_CONTRACT.md              |  39 +-
 4 files changed, 846 insertions(+), 64 deletions(-)
```

## 12. Branch state — local

```
$ git branch -vv

  baseline-v1                       417f860 [origin/baseline-v1]
* main                              ea321c6 [origin/main]
  phase-2-theme-widgets             db1d8b4
  phase-3-paths-updater             b2e7f79
  phase-4-pyinstaller-compatibility ba3d2c4 [origin/phase-4-pyinstaller-compatibility]
```

`main` updated this turn (2 commits + report).

## 13. Remote state — origin

```
$ git ls-remote --heads origin

417f8600…  refs/heads/baseline-v1                          ← unchanged this turn
ea321c6…   refs/heads/main                                 ← updated (2 commits + report)
ba3d2c4d…  refs/heads/phase-4-pyinstaller-compatibility    ← unchanged this turn
```

Push run: `git push origin main` (`95c00f7..ea321c6` for the
2-commit batch; the report adds a 3rd).

## 14. Confirmation — no migration / build / runtime work occurred

- ❌ **No source code modified.** Zero edits to any module in
  `src/phoenix_commons/`. `tokens.py` is unchanged; `apply.py`
  unchanged; widgets unchanged; updater unchanged.
- ❌ **No tests added or modified.** Test suite tally unchanged
  (83 tests; verified `pytest` unchanged).
- ❌ **No app code modified** (zero edits to PCC, Job Tracker,
  Phoenix CAD, Phoenix Checkout, ValveMaster source).
- ❌ **No PyInstaller / Inno Setup / `gh release` / `build.bat`** invocations.
- ❌ **No frozen-exe validation** attempted.
- ❌ **No installer testing.**
- ❌ **No updater runtime testing.**
- ❌ **No `BrandProfile` mechanism implemented.** Architecture
  specified in ADR-016; implementation slotted for Phase 3+.
- ❌ **No sentinel-form QSS conversion.** Documented as
  Phase 3+ enabling work.
- ❌ **No `apply_dark_theme(brand=...)` kwarg added.**
- ❌ **No `phoenix_style.qss` modified.** Hex literals stay.
- ❌ **No screenshot captures.**
- ❌ **No CI workflow change.**
- ❌ **No publishing** (no PyPI, no GitHub Releases).
- ❌ **No retrofits / migrations / icon replacement / component
  rewrites.**
- ❌ **No Phase 3A start.** Awaiting explicit user approval.

Operations performed this turn:

```
(Write)  ADR_PCC_PALETTE_RECONCILIATION.md         ← the new ADR
(Edit)   DECISIONS.md                              ← ADR-016 summary row
git add … && git commit "Add ADR-016 …"           ← logical commit 1

(Edit)   DESIGN_SYSTEM.md (×4 edits)               ← palette table, typography, button objectNames, future work
(Edit)   PLATFORM_CONTRACT.md                      ← Theme tokens locked/variant tables
git add … && git commit "Update DESIGN_SYSTEM + PLATFORM_CONTRACT …"  ← logical commit 2
git push origin main                                ← 2 commits pushed (95c00f7..ea321c6)

(Write)  STABILIZATION_REPORT_07.md
```

That's the entire surface.

## 15. STOP

ADR-016 landed. Architecture stabilization remains in effect.
All stabilization phases (2.1 / 2.2 / 2.5 / 2.6 / 2.7) + the
final reconciliation ADR are complete.

Per the user spec for this phase: **Do NOT continue into Phase
3A, migrations, retrofits, token implementation, palette
implementation, or QSS rewrites.** No code change resumes
without explicit phase approval per `BASELINE.md` stop
conditions.

Phase 3A is **architecturally approved** to begin. Only the
user-approval gate remains commons-side.

Awaiting user direction.
