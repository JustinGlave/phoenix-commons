# visual-baselines/ — Phase 2.7 reference snapshots

> Per-app visual baselines captured BEFORE pilot migrations begin.
> These are the comparison references for Phase 3A/B/C retrofit
> review — what each Phoenix tool looked like / behaved like under
> the existing (pre-commons-retrofit) implementation, so reviewers
> can spot regressions and intentional changes deliberately.

## Status

**Source-mode markdown baselines only.** Captured 2026-05-19.

This phase is **observation + documentation only**. No production
tool was modified, no screenshots were captured (offscreen Qt
under the AV-quarantined laptop isn't a faithful pixel reference;
in-app screenshots will be captured when the first migration's
PR review starts). Markdown references describe layout, spacing,
visual hierarchy, palette, notable UI quirks, and legacy styling
patterns.

Where a description is inferred from architecture (QSS selectors,
widget classes, objectName conventions in `PLATFORM_CONTRACT.md`)
rather than observed pixel-by-pixel, the line is marked
**Inferred** and flagged as needing verification during the first
migration screenshot run.

## Structure

```
visual-baselines/
├── README.md                                ← this file
├── VISUAL_BASELINE_RULES.md                 ← governance: naming, sizing,
│                                              DPI, capture consistency,
│                                              "acceptable parity" definition
├── MIGRATION_VISUAL_REVIEW_CHECKLIST.md     ← per-PR review checklist for
│                                              Phase 3A/B/C retrofits
├── checkout/baseline.md                     ← Phoenix Valve Checkout Tool
├── phoenix-cad/baseline.md                  ← Phoenix CAD Tool (source / dev perspective)
├── llt/baseline.md                          ← Lab Layout Tool (the deployed product
│                                              that Phoenix CAD builds to)
├── pcc/baseline.md                          ← Phoenix Command Center
├── job-tracker/baseline.md                  ← Job Tracker (source / dev perspective)
└── ptt/baseline.md                          ← Project Tracking Tool (the deployed
                                               product that Job Tracker builds to)
```

## App name map

Some Phoenix tools have both a **source-repo identity** and a
**deployed-product identity**, with different display names. The
visual-baselines directory carries one folder per identity so
either lookup resolves:

| Source repo | Display name (deployed) | Exe | Baseline folder pair |
|-------------|--------------------------|-----|----------------------|
| `Phoenix_CAD_Tool` | Lab Layout Tool | `LabLayoutTool.exe` | `phoenix-cad/` (dev) + `llt/` (deployed) |
| `Job Tracker` | Project Tracking Tool | `ProjectTrackingTool.exe` | `job-tracker/` (dev) + `ptt/` (deployed) |
| `Phoenix-Checkout-Tool` | Phoenix Valve Checkout Tool | `PhoenixCheckoutTool.exe` | `checkout/` |
| `phoenix-command-center` | Phoenix Command Center | (source-run) | `pcc/` |
| `ValveMasterTool` | ValveMasterTool | `ValveMasterTool.exe` | **not represented as a folder — see below** |

## Apps not represented as subdirectories

### ValveMasterTool / Phoenix Master Tool

**Status revised 2026-05-26 per `WAVE_8A_VALVEMASTER_PREFLIGHT_AUDIT.md`.**
ValveMaster's `v1.1.0` release already shipped the canonical
System A palette in `phoenix_style.qss` (byte-match verified:
BG `#0a0e27`, surface `#141829`, primary `#dc2626`, secondary
`#1e3a8a`, accent `#3b82f6`). The earlier characterization of
ValveMaster as a "System B" tool (deprecated `#1c1c1c` gray
`QPalette`) is **superseded**. Wave 8a is a facade retrofit
(commons-backed architecture alignment + build hardening +
updater/theme/widget facades) — NOT a visible theme swap.
Expected visible change ≈ 0% (Phoenix-CAD profile).

A Phase 2.7-style pre-migration baseline was never captured
because the original framing assumed the surfaces would be
intentionally replaced. The revised assessment means a baseline
COULD be captured before Wave 8a opens, but the operator's
2026-05-22 decision is "light visual review at the merge gate"
rather than a full Phase 2.7-style baseline.

When Wave 8a's retrofit lands (on or after 2026-06-02), a fresh
`valvemaster/baseline.md` may be captured at PR-close time to
seed any future visual-regression review for Phoenix Master Tool.
The "before" and "after" snapshots are expected to be ≈ 0% diff.

## Reading the per-app baselines

Each `baseline.md` follows the same 16-section template, defined
in `VISUAL_BASELINE_RULES.md`. Sections cover:

1. **Identity** — display name, exe, repo, paths, version (from
   `production-inventory.md`)
2. **Current theme system** — what palette, where it lives, how
   loaded
3. **Main window** — layout, dimensions, anchors
4. **Dashboard / home view**
5. **Forms**
6. **Tables / grids**
7. **Dialogs**
8. **Update banner state**
9. **Empty states**
10. **Dense-data states**
11. **Error / warning states**
12. **Sidebar / navigation states**
13. **Known visual debt**
14. **Known inconsistencies**
15. **Migration sensitivity**
16. **High-risk screens**

Sections marked **N/A** mean the app doesn't have that surface
(e.g. PCC has no `UpdateBanner` because it's not packaged).

## Three palettes coexist in production

A key Phase 2.7 finding worth highlighting up front:

| Tool | Palette in use | Source |
|------|----------------|--------|
| Phoenix CAD / Lab Layout Tool | **navy + red + blue** | `phoenix_style.qss` (canonical "System A" per Phase 2.1+2.5) |
| Job Tracker / PTT | navy + red + blue | `phoenix_style.qss` (same file) |
| Phoenix Checkout | navy + red + blue | `phoenix_style.qss` (same file) |
| **Phoenix Command Center** | **navy + orange + teal** | `theme.py` (Python `C` dict generating its own QSS — diverges from the QSS-file palette) |
| **ValveMaster** | **gray "System B"** | programmatic `QPalette` (no QSS file, no shared tokens) |

`DESIGN_SYSTEM.md` documents the PCC palette (orange `#E8783C`,
teal `#3CB8AE`) as "System A" — but the actual System A QSS file
shipping in Phoenix CAD / Job Tracker / Phoenix Checkout uses red
`#dc2626` and blue `#3b82f6`. **`phoenix_commons.theme.tokens`
mirrors the QSS-file values**, so the commons canonical palette
is navy + red + blue.

This divergence is real visual debt — flagged in each of:

- per-app `Known visual debt` sections
- `MIGRATION_VISUAL_REVIEW_CHECKLIST.md`
- `STABILIZATION_REPORT_06.md` § "Visual inconsistencies discovered"

The retrofits will need to make a deliberate decision per tool
whether the "after" matches the QSS-file palette (commons
tokens) or the PCC `theme.py` palette. Treating both as "System
A" is what produced the drift in the first place.

## See also

- `../PLATFORM_CONTRACT.md` — ownership map
- `../DESIGN_SYSTEM.md` — the design-system reference (also one
  side of the palette divergence noted above)
- `../BRANDING_ASSET_GUIDE.md` — brand asset inventory + the
  "four colors" (orange / green / blue / red) per-tool pattern.
  Complementary to the palette discussion above: this README
  covers the QSS / `theme.py` divergence; the asset guide covers
  the icon/logo asset divergence.
- `../production-inventory.md` — the source for all "Identity"
  table values in each per-app baseline
- `../STABILIZATION_REPORT_06.md` — Phase 2.7 deliverable
  summarising findings
