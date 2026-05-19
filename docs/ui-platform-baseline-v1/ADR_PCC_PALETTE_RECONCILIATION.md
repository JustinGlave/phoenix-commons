# ADR-016 — PCC palette reconciliation

> Standalone ADR resolving the three-palettes-in-production
> finding from Phase 2.7 (see `STABILIZATION_REPORT_06.md`
> § "Visual inconsistencies discovered"). This is the final
> architecture-level design decision before pilot migrations
> begin.
>
> Summary row mirrored in `DECISIONS.md` § FINALIZED.

## Identity

| Field | Value |
|-------|-------|
| ADR number | **016** |
| Date | 2026-05-19 |
| Status | **Finalized** |
| Supersedes | — (no prior ADR on this question) |
| Superseded by | — |
| Cross-reference | `STABILIZATION_REPORT_06.md` (where the divergence was surfaced), `STABILIZATION_REPORT_07.md` (where this ADR lands), `DESIGN_SYSTEM.md` (updated post-decision), `PLATFORM_CONTRACT.md` § Theme tokens (updated post-decision), `phoenix_commons.theme.tokens` (the module that gains brand-profile classification when implemented in Phase 3+) |

## 1. Current state

Three palettes coexist in production today (cataloged in
`visual-baselines/README.md` § "Three palettes coexist in
production"):

| Tool | Palette | Source of palette |
|------|---------|--------------------|
| Phoenix CAD / Lab Layout Tool | navy + red + blue | `phoenix_style.qss` (the "canonical System A" per Phase 2.1 / 2.5) |
| Job Tracker / Project Tracking Tool | navy + red + blue | `phoenix_style.qss` (same file) |
| Phoenix Checkout / Phoenix Valve Checkout Tool | navy + red + blue | `phoenix_style.qss` (same file) |
| **Phoenix Command Center (PCC)** | **navy + orange + teal** | `theme.py` (Python `C` dict generating its own QSS — diverges from the QSS-file palette) |
| ValveMaster | gray "System B" (deprecated) | programmatic `QPalette` (no QSS file, no shared tokens) |

The commons canonical, as established by Phase 2.1 + Phase 2.5
work and shipping today in `phoenix_commons.theme.tokens`:

| Token | Value | Role |
|-------|-------|------|
| `BG` | `#0a0e27` | Window background |
| `SURFACE` | `#141829` | Cards / panels / inputs |
| `SURFACE_ALT` | `#0f1219` | Alternating rows |
| `PRIMARY` | `#dc2626` | **Brand red** — primary CTAs |
| `SECONDARY` | `#1e3a8a` | **Deep blue** — secondary chrome |
| `ACCENT` | `#3b82f6` | **Blue** — focus / link chrome |
| `TEXT` | `#ffffff` | Body text |
| `MUTED` | `#94a3b8` | Subdued text |
| `SUCCESS` | `#22c55e` | Status: success |
| `WARNING` | `#f59e0b` | Status: warning |
| `ERROR` | `#ef4444` | Status: error |
| `INFO` | aliased to `ACCENT` | Informational chrome |

PCC's `theme.py` per `DESIGN_SYSTEM.md` (which currently
documents PCC's palette as the canonical "System A" — a
collision this ADR resolves):

| Equivalent role | PCC `C` dict | Commons canonical |
|------------------|---------------|--------------------|
| Window background | `#18181F` | `#0a0e27` |
| Card surface | `#27273A` | `#141829` |
| Primary brand colour | **`#E8783C`** (Phoenix orange) | **`#dc2626`** (Phoenix red) |
| Secondary brand colour | **`#3CB8AE`** (teal) | **`#1e3a8a`** (deep blue) |
| Body text | `#E4E4F0` (light gray) | `#ffffff` (pure white) |

These are not "small drifts" — they're two distinct visual
systems, both currently labeled "System A" in different docs.
The collision must resolve before Phase 3A pilot migrations
proceed.

## 2. Why the divergence exists

Three historical factors compounded into the current state:

1. **Two design lineages.** `phoenix_style.qss` was authored
   alongside Phoenix CAD's `ui/style.py` — the canonical theme
   pre-platform-stabilization. PCC's `theme.py` was written
   independently, intended to express PCC's identity as the
   platform-owner tool. The two were never explicitly
   reconciled.
2. **`DESIGN_SYSTEM.md` documented PCC's palette as "System A"**
   because it was the most-recently-iterated design at the time
   of writing. Subsequent Phase 2.1 / 2.5 work canonicalized
   the QSS-file palette into `phoenix_commons.theme.tokens`
   without revisiting `DESIGN_SYSTEM.md` — producing the
   naming collision.
3. **PCC was never in scope for the same retrofit batch as the
   production tools** (per the original rollout plan, PCC is
   the management/scaffolding tool, not a "deployed Phoenix
   tool" in the sense Job Tracker / Phoenix CAD are). So PCC's
   distinct palette stayed unchallenged longer than it
   otherwise would have.

The divergence isn't a bug to fix; it's a **design choice that
was never made explicitly**. This ADR makes it.

## 3. Options evaluated

Three options. Pros / cons / migration cost / long-term
maintenance burden / fragmentation risk for each.

### Option A — PCC adopts the full commons canonical palette

PCC's retrofit replaces `theme.py`'s `C` dict with imports from
`phoenix_commons.theme.tokens`. Orange and teal disappear from
PCC. Every CTA becomes red; every accent becomes blue. PCC
visually becomes indistinguishable from Phoenix CAD / Job
Tracker / Phoenix Checkout.

**Pros:**

- ✅ Simplest design — one palette, one source of truth, zero
  variance. The platform contract reads as "one design system,
  full stop."
- ✅ Lowest cognitive load for any future Phoenix tool author —
  no decision about "do I get a brand override" to make.
- ✅ Eliminates the "two System A" naming collision at the
  root by reducing to one System A.
- ✅ No code surface added to commons (no brand-profile
  mechanism to implement, test, or document).
- ✅ Strongest forcing function against future drift — anyone
  who wants a non-canonical palette has to file a commons PR
  to add it, which is a meaningful bar.

**Cons:**

- ❌ PCC loses its current brand identity. Orange + teal are
  recognized by ATS internal users as "the Command Center
  tool" — five years of muscle memory.
- ❌ The Phoenix family's only deliberate accent-color variety
  disappears. Every tool looks the same; users can't
  distinguish at-a-glance which app is in focus.
- ❌ Sunk cost — PCC's existing icons / sprite / wordmark
  were designed with orange in mind; some assets may need
  re-tinting.
- ❌ Doesn't address the legitimate use case where a new
  internal tool genuinely needs a non-canonical accent (e.g.
  a safety tool that uses high-visibility orange for its
  primary alarm CTA).

**Migration cost:**

- PCC retrofit PR: ~moderate. Delete `theme.py`'s `C` dict;
  swap imports to `phoenix_commons.theme.tokens`; re-test
  every screen for any hardcoded orange/teal that escaped the
  `C` dict; re-tint sprite if needed.
- One-time pain; no ongoing maintenance burden.

**Long-term maintenance:**

- Lowest. Single palette, single source of truth.

**Fragmentation risk:**

- Zero by design.

### Option B — PCC keeps an accent override (recommended)

Commons defines a small, named set of **brand tokens**
(`PRIMARY`, `SECONDARY`, `ACCENT`) which apps may override via
a controlled mechanism. Every other token (`BG`, `SURFACE`,
`TEXT`, `MUTED`, `SUCCESS`, `WARNING`, `ERROR`, every
spacing, every typography, every radius) is **locked** — apps
cannot vary them.

PCC retrofits onto commons widgets / spacing / typography /
QSS structure as usual, but registers its own brand profile:
`PRIMARY=#E8783C`, `SECONDARY=#3CB8AE`, `ACCENT=#3CB8AE`.

Widgets render PCC orange / teal where they'd render commons
red / blue in other tools. Layout, hierarchy, sizing,
interaction semantics, iconography — all identical.

**Pros:**

- ✅ Preserves PCC's brand identity. Orange + teal stay.
- ✅ Preserves the design-system commitments PCC made
  pre-platform: surface chrome, text, spacing, typography all
  align with the commons canonical.
- ✅ One widget system, one QSS architecture, one token
  hierarchy — **no design-system fork**.
- ✅ Migration friction lowest for PCC (it gets to keep the
  parts that mattered to it).
- ✅ Future tools that legitimately need an accent variant
  (e.g. a safety tool with high-visibility orange) have an
  explicit, controlled path — they register a brand profile;
  they don't fork the design system.
- ✅ The "no design-system fork" rule (ADR-002) stays in
  force — apps still extend, never fork. The brand profile
  IS an extension point, codified.

**Cons:**

- ❌ Adds commons API surface — `BrandProfile` class /
  `apply_dark_theme(app, brand=...)` kwarg / QSS template
  sentinels. Implementation cost in Phase 3+ (not this phase).
- ❌ Future Phoenix tool authors must decide "default brand
  or PCC-style override" — a small cognitive load tax.
- ❌ Risk of future drift if more apps register custom brand
  profiles. Mitigation: governance (see § 9).
- ❌ Slightly more complex story to document — "everything is
  shared except these three named slots." The line between
  brand and structural tokens has to be drawn somewhere.

**Migration cost:**

- PCC retrofit PR: moderate. Slightly larger than Option A
  because it involves the new commons brand-profile mechanism.
- Phoenix CAD / Job Tracker / Phoenix Checkout retrofits:
  ~unchanged from Option A baseline. They use the default
  brand profile, no behavioural difference.
- Commons implementation cost (Phase 3+): one-time, modest
  — see § 7 for the architecture.

**Long-term maintenance:**

- Modest. One additional concept (`BrandProfile`) to
  document, test, and enforce. Versus the alternative (Option
  A drops it; Option C explodes it).

**Fragmentation risk:**

- Low — by construction. Brand-profile registration is
  controlled (commons-defined slot list); no app can register
  arbitrary tokens. The set of slots is intentionally small
  (3 tokens) so the divergence surface stays bounded.

### Option C — Per-app arbitrary themes (rejected)

Every app may define its own complete palette via a private
theme module. Commons provides widget classes and structural
QSS rules, but each app supplies all colour values at startup.

**Pros:**

- ✅ Maximum flexibility.
- ✅ No commons-side decisions about which tokens are "brand"
  vs "structural."

**Cons:**

- ❌ **Forks the design system in slow motion.** Two years
  later, every tool's palette has drifted subtly; users
  perceive the Phoenix family as a collection of related
  apps rather than one product.
- ❌ Accessibility regressions are inevitable. Apps lose the
  curated text/bg contrast guarantees commons provides.
- ❌ Status colour semantics break (e.g. one app's "warning"
  amber clashes with another's "error" red).
- ❌ Widget visual consistency breaks. A `PrimaryButton` in
  one app looks materially different from a `PrimaryButton`
  in another.
- ❌ Increases the surface a malicious / buggy app can drift
  into — losing the curated-platform value entirely.

**Migration cost:**

- Lowest commons-side; highest app-side and ongoing.

**Long-term maintenance:**

- High. Every app's palette becomes its own maintenance
  burden. Curated platform value evaporates.

**Fragmentation risk:**

- **Maximum.** This option IS fragmentation by design.

**Rejection rationale:** Option C contradicts ADR-001 ("phoenix-
commons is the UI platform, not a utility grab-bag") and
ADR-002 ("apps extend via addendum, not fork"). Adopting it
would invalidate the architecture-stabilization work of the
last six phases.

## 4. Decision

**Option B — PCC keeps an accent override via a controlled
brand-profile mechanism.**

Approved 2026-05-19. Takes effect immediately for documentation
purposes; implementation (the actual commons-side brand-profile
mechanism) happens in Phase 3+ once user-approval gates that
work.

## 5. Risks of forcing PCC into canonical red/blue (Option A — rejected risks)

The arguments against Option A that pushed the decision toward
Option B:

1. **Loss of distinct PCC identity.** PCC is the platform-
   owner tool. Users routinely have it open alongside one of
   the production tools (Job Tracker, Phoenix CAD). If both
   look identical, alt-tab disambiguation suffers.
2. **Sunk-cost asset friction.** PCC's `SidebarSprite`,
   wordmark, screenshots, and onboarding materials were
   designed against orange. Replacing them is real work with
   no offsetting user benefit.
3. **Premature constraint.** Option B retains the option to
   force PCC to canonical *later* if the brand-profile
   mechanism turns out to be a maintenance burden in practice.
   Option A is one-way.
4. **No legitimate future-tool variant has a path.** If a
   future internal Phoenix tool needs (e.g.) high-visibility
   orange for a safety-critical primary CTA, Option A forces
   it to either accept red or fork the design system. Option
   B gives it a controlled path.

## 6. Risks of allowing arbitrary app palettes (Option C — rejected risks)

The arguments against Option C — kept here for the record so
the same proposal isn't re-litigated later:

1. **Slow-motion design-system fork** (see Option C cons).
2. **Accessibility regression risk** — apps lose the curated
   text/bg contrast guarantee.
3. **Status colour semantic drift** — semantic colours must
   remain universal across the platform; per-app variation
   defeats the purpose.
4. **Widget visual consistency breaks** — the whole point of
   `phoenix_commons.widgets` is one button looks like one
   button across every tool.
5. **Contradicts ADR-001 + ADR-002** — would invalidate the
   architecture-stabilization work that preceded this ADR.

## 7. Token-level implications (the Option B design)

### Token classification

Commons-canonical tokens (currently in
`phoenix_commons.theme.tokens`) are reclassified into two
tiers:

#### Locked tokens (commons-owned; apps may NOT override)

| Token | Current value | Reason locked |
|-------|---------------|----------------|
| `BG` | `#0a0e27` | Universal Phoenix dark chrome. Visual identity across tools. |
| `SURFACE` | `#141829` | Universal card / panel surface. |
| `SURFACE_ALT` | `#0f1219` | Universal alternating-row surface. |
| `TEXT` | `#ffffff` | Accessibility / contrast guarantee. |
| `MUTED` | `#94a3b8` | Accessibility / contrast guarantee. |
| `SUCCESS` | `#22c55e` | Semantic affordance — must be universal. |
| `WARNING` | `#f59e0b` | Semantic affordance — must be universal. |
| `ERROR` | `#ef4444` | Semantic affordance — must be universal. |
| All spacing constants | (planned) | Structural — drift here is design-system fork. |
| All typography constants | (planned) | Same. |
| All radius constants | (planned) | Same. |

These tokens are commons-owned and version with commons. Apps
that attempt to override them at runtime fail loudly (Phase 3+
implementation enforces).

#### Variant-allowed brand tokens (apps may override via brand profile)

| Token | Default value | Variant-allowed? |
|-------|---------------|-------------------|
| `PRIMARY` | `#dc2626` (red) | ✅ |
| `SECONDARY` | `#1e3a8a` (deep blue) | ✅ |
| `ACCENT` | `#3b82f6` (blue) | ✅ |
| `INFO` | aliased to `ACCENT` | ✅ (follows `ACCENT` automatically) |

Three named brand tokens (PRIMARY / SECONDARY / ACCENT). INFO
is a derived alias and doesn't get a separate override slot —
it follows whatever ACCENT resolves to per app.

### Brand profile shape (Phase 3+ implementation will provide)

When implementation lands, commons will expose:

```python
# phoenix_commons.theme.tokens (sketch — NOT implemented this phase)

@dataclass(frozen=True)
class BrandProfile:
    primary:   str = PRIMARY     # default: commons canonical red
    secondary: str = SECONDARY   # default: commons canonical deep blue
    accent:    str = ACCENT      # default: commons canonical blue

DEFAULT_BRAND = BrandProfile()  # navy + red + blue

# Apps that want PCC's identity register their profile:
PCC_BRAND = BrandProfile(
    primary   = "#E8783C",  # orange
    secondary = "#3CB8AE",  # teal
    accent    = "#3CB8AE",  # teal (or whichever PCC chooses for accent)
)
```

`apply_dark_theme(app, brand=DEFAULT_BRAND)` substitutes brand
values into the QSS template at apply time.

### Existing `SEMANTIC_COLORS` dict

`SEMANTIC_COLORS` and the `C` alias remain. After Phase 3+
implementation, they become functions of the active brand
profile — `SEMANTIC_COLORS["primary"]` returns the brand-active
primary, not always the canonical default.

This phase makes no code change to the dict — it stays the
default-canonical map until Phase 3+ implementation.

## 8. QSS implications

The current `phoenix_commons.theme.phoenix_style.qss` contains
literal hex values for every token. Implementation (Phase 3+)
introduces **sentinel substitution** for the three brand tokens:

```css
/* phoenix_style.qss — sentinel form (Phase 3+) */
QPushButton {
    background-color: __BRAND_PRIMARY__;   /* was #dc2626 */
}
QPushButton#secondaryButton {
    background-color: __BRAND_SECONDARY__;  /* was #1e3a8a */
}
QPushButton#accentBtn:focus {
    border-color: __BRAND_ACCENT__;        /* was #3b82f6 */
}
/* Locked tokens stay literal: */
QMainWindow {
    background-color: #0a0e27;             /* BG — locked */
}
QLabel {
    color: #ffffff;                        /* TEXT — locked */
}
```

`apply_dark_theme(app, brand=brand_profile)`:

1. Reads `phoenix_style.qss` via importlib.resources
2. Substitutes `__BRAND_PRIMARY__` → `brand.primary`,
   `__BRAND_SECONDARY__` → `brand.secondary`,
   `__BRAND_ACCENT__` → `brand.accent`
3. Applies the substituted QSS to the QApplication

The substitution happens in-memory before
`QApplication.setStyleSheet()`. The on-disk QSS stays
sentinel-form so a fresh app gets the appropriate brand
without rebuilding.

The Phase 2.1 generated `embedded_qss.py` also becomes
sentinel-form; the generator's idempotency contract is
preserved (sentinel-form QSS deterministically produces
sentinel-form embedded module). Substitution still happens at
apply time in both paths.

**Sentinel naming convention:** `__BRAND_<TOKEN_UPPER>__` —
double underscores both ends so it's visually distinct from
any legitimate CSS / QSS identifier. Substituted via plain
string replacement (no regex; no risk of partial matches
because the surrounding double underscores can't legitimately
appear in QSS).

**Validation:** Phase 3+ implementation adds a test that asserts
post-substitution QSS contains no `__BRAND_*__` sentinels —
catches missing brand tokens in the substitution table.

## 9. Migration implications

### For PCC

PCC's retrofit PR (Phase 3C per the planning) gets specific
new work:

1. Declare PCC's brand profile (in PCC's source, not in
   commons):

   ```python
   from phoenix_commons.theme.tokens import BrandProfile

   PCC_BRAND = BrandProfile(
       primary   = "#E8783C",
       secondary = "#3CB8AE",
       accent    = "#3CB8AE",
   )
   ```

2. Pass it to `apply_dark_theme` in PCC's startup:

   ```python
   from phoenix_commons.theme import apply_dark_theme
   from .theme import PCC_BRAND
   apply_dark_theme(app, brand=PCC_BRAND)
   ```

3. Delete `theme.py`'s `C` dict + QSS generator (the part
   that diverged from the QSS-file palette).
4. Keep PCC's local widget classes that are PCC-specific
   (`CommonsDropZone`, `SidebarSprite`, `ToolCard`) — they
   stay app-local per `PLATFORM_CONTRACT.md` § Widgets.
5. Re-test every screen for hardcoded hex literals that
   escaped the `C` dict; replace with brand-token references.
6. Run `MIGRATION_VISUAL_REVIEW_CHECKLIST.md` § "Phoenix
   Command Center" addenda row-by-row.

PCC's `MIGRATION_VISUAL_REVIEW_CHECKLIST.md` addendum gets
updated to remove the "Decision recorded in an ADR before
this PR opens" gate (because this ADR IS that decision) and
to add new rows verifying the brand profile is correctly
registered.

### For Phoenix CAD / Lab Layout Tool

**No change.** Lab Layout Tool uses the default brand profile.
The retrofit PR doesn't reference `BrandProfile` at all —
default is implicit.

### For Job Tracker / Project Tracking Tool

**No change.** Same — uses the default brand profile.

### For Phoenix Checkout

**No change.** Same — uses the default brand profile.

### For ValveMaster (Phase 8a)

ValveMaster's Phase 8a retrofit adopts the default brand
profile by default. The "before" state is System B gray; the
"after" state is the canonical navy + red + blue. No PCC-style
brand override.

If for some reason ValveMaster's retrofit team wants to
preserve any ValveMaster-distinct accent (e.g. the existing
red icon files match the canonical red — no override needed; or
preserve the `#487cff` blue — would require an override slot,
unlikely to be requested), the same brand-profile mechanism is
available.

### For future Phoenix tools

The new-tool wizard (Phase 5+ Command Center work) gains a
brand-profile question on the scaffold:

- Default: use commons canonical (navy + red + blue) — the
  expected answer for ~90% of tools.
- Override: declare a `BrandProfile` in the tool's source —
  for the rare case where a tool genuinely needs distinct brand
  identity.

The wizard generates the appropriate boilerplate either way.

## 10. Governance implications

### Adding new brand-profile slots

If experience shows that 3 brand tokens isn't enough — e.g. a
future tool needs to override a fourth slot — adding it
requires a **new ADR** that supersedes this one. The slot list
is intentionally small to keep the divergence surface bounded.

### App-local additions outside the brand profile

Apps may **NOT** override locked tokens at runtime. Attempts
fail loudly. This is the boundary between "controlled
extension" (brand profile) and "design-system fork" (not
allowed).

Apps **MAY** add app-local QSS rules targeting their own
objectNames (per `COMPONENT_CONTRACT.md` § Reserved objectName
rules) — these are app-local additions, not platform-level
overrides.

### Validation

Phase 3+ implementation adds (planned):

- A test that asserts `BrandProfile` can be constructed with
  only the 3 named slots — refusing extra keyword arguments
  prevents apps from adding "stealth tokens."
- A test that asserts the substituted QSS for the default
  brand is byte-identical to the previous (pre-sentinel) QSS
  (regression guard during the sentinel-conversion PR).
- A test that asserts apps cannot mutate locked tokens at
  runtime — e.g. setting `tokens.BG` from app code raises or
  is otherwise blocked.

### Change-management for brand profiles

Once a tool has a registered brand profile (PCC), changes to
that profile:

- Require a commit to the tool's source (the BrandProfile
  literal lives there).
- Reflect in the next build / release.
- Don't require a commons-side change.

This makes brand-profile changes lightweight and
tool-specific while keeping the design-system itself rigid.

## 11. Future extensibility implications

### Light mode (deferred per ADR-011)

If light mode ever lands (not on roadmap; ADR-011 deferred
indefinitely), the brand-profile mechanism extends naturally:

- A separate `LightBrandProfile` set with light-mode
  appropriate values
- `apply_dark_theme` becomes `apply_theme(app, brand, mode)`
- Locked tokens get light-mode equivalents in a parallel
  `LightLocked` set

This ADR doesn't commit to light mode; it just notes the
extension path is clean.

### Per-tool semantic colour tinting

If a tool argues "my warning should be more orange" (e.g. a
safety tool that wants high-visibility warning chrome), the
answer is **no** — `WARNING` is locked. The semantic colours
must remain universal so users transferring between tools have
consistent affordances.

If the tool's argument is "my primary CTA should be high-
visibility orange," that's a brand-profile override — allowed.

### Future palette evolution

If commons-canonical itself evolves (e.g. the brand red ages
into a slightly different shade), the default `BrandProfile`
value updates, but the brand-profile mechanism stays
unchanged. Existing apps that override see no change. Apps on
the default rev with commons.

## 12. Implementation phase

**Not this phase.** This ADR is documentation only. The
brand-profile mechanism implementation slots into Phase 3+
work, likely either:

- Phase 3A (Phoenix CAD retrofit) — implement BrandProfile +
  default + sentinel-form QSS as enabling work, even though
  Phoenix CAD itself uses the default and won't exercise the
  override path.
- Phase 3C / PCC retrofit — implement at the same time as
  PCC's actual brand-profile registration.

Recommendation: **implement in Phase 3A** as enabling work, so
PCC's later retrofit doesn't have to land both the mechanism
AND its usage simultaneously. The Phase 3A test suite
exercises the default path; Phase 3C exercises the override
path.

This choice belongs in Phase 3A's approval — not in this ADR.

## 13. Approval

Approved 2026-05-19.

Sign-off:

| Role | Name | Status |
|------|------|--------|
| Phoenix UI Platform owner | Justin Glave | ✅ recommendation accepted (per phase-prompt explicit hint toward Option B + the documented "I strongly evaluate" framing) |

This ADR is the **final architecture-level design decision
before pilot migrations begin.** With it landed, Phase 3A is
unblocked at the architecture level.

## See also

- `DECISIONS.md` § ADR-016 — summary row mirroring this file
- `STABILIZATION_REPORT_06.md` — Phase 2.7 deliverable that
  surfaced the divergence
- `STABILIZATION_REPORT_07.md` — Phase deliverable that lands
  this ADR
- `DESIGN_SYSTEM.md` — updated post-this-ADR to reflect the
  brand-profile structure (commit 2 of this phase)
- `PLATFORM_CONTRACT.md` § Theme tokens — updated post-this-
  ADR (commit 2 of this phase)
- `visual-baselines/pcc/baseline.md` § Migration sensitivity —
  the PCC retrofit guidance that this ADR resolves
- `visual-baselines/MIGRATION_VISUAL_REVIEW_CHECKLIST.md` §
  "Phoenix Command Center" — addendum to update at PCC
  retrofit time
- `phoenix_commons.theme.tokens` — the module that gains
  `BrandProfile` in Phase 3+
- `phoenix_commons.theme.apply.apply_dark_theme` — gains the
  `brand=` kwarg in Phase 3+
