# Phoenix Family — Post-Release Housekeeping Report

> **Status:** safe post-release housekeeping complete.
> **Date:** 2026-06-01.
> **Companion:** `PHOENIX_4_APP_RELEASE_CLOSURE_REPORT.md`.

---

## 1. Docs updated (active planning docs only)

Historical per-step reports (RC reports, drafts report, publish-gate report) left **untouched** — they are state-at-the-time snapshots and remain valid forensic records. Only active/forward-looking docs whose standing claims were now stale were updated:

| Doc | Change |
|-----|--------|
| `PHOENIX_4_APP_RELEASE_CLOSURE_REPORT.md` | **NEW** — canonical "release cycle closed" record; supersedes the forward-looking state in the promotion plan + RC validation summary + kickoff-ready doc |
| `PHOENIX_4_APP_FINAL_RELEASE_PROMOTION_PLAN.md` | Added **✅ EXECUTED + SUPERSEDED 2026-06-01** banner at top, pointing to the closure report; the plan's "no releases published / releases remain drafts" language now explicitly flagged as state-at-authoring (forensic), not current reality |
| `MIGRATION_RULES.md` (§ Migration order, rows 8a + 8b) | Corrected the standing "No production deployment occurred (no GitHub Release, no installer upload)" claim — was accurate *at retrofit-merge time* but read as a misleading present-tense statement in the living migration tracker. Now reads "No production deployment occurred *at the retrofit merge itself*; the coordinated 4-app release subsequently published `v1.1.1` / `v1.8.6` on 2026-06-01 (see closure report)." Additive clarification; merge-phase truth preserved. |

Docs **checked and NOT changed** (no stale forward-looking release-state language found):
- `PHOENIX_4_APP_RC_KICKOFF_READY.md` — already had its decision table + "what's ready" framing; no "releases pending" claim
- `PHOENIX_4_APP_RC_VALIDATION_SUMMARY.md` — describes RC-validation state; § 9 already framed as "ready for GitHub Release drafting" (a correct historical next-step, not a stale present-tense claim)
- `APP_STANDARDIZATION_READINESS_MATRIX.md` — no release-publish-state language
- Per-step RC / drafts / publish-gate reports — historical snapshots, intentionally preserved

---

## 2. .gitignore changes by repo

All 4 app repos audited for venv/build ignore coverage. Pre-existing coverage: every repo already ignored `dist/`, `build/`, `__pycache__/`, and `*.pyc` (CAD via `*.py[cod]`). The gap was virtual-environment directories. Fixes applied on each repo's **default branch** (master/main), committed + pushed:

| Repo | Branch | Pre-state | Added | Commit | Push |
|------|--------|-----------|-------|--------|------|
| Phoenix_CAD_Tool | `master` | had `.venv/` (+ `venv/ env/ ENV/`) | `.venv*/` glob | `17ec3e7` | ✅ `35a0661..17ec3e7` |
| Phoenix-Checkout-Tool | `main` | no venv ignore | `.venv/`, `.venv*/`, `venv/`, `env/`, `ENV/` | `a4fe4b2` | ✅ `274b0a8..a4fe4b2` |
| ValveMasterTool | `main` | no venv ignore | `.venv/`, `.venv*/`, `venv/`, `env/`, `ENV/` | `2fa78ec` | ✅ `e6eefa1..2fa78ec` |
| Job Tracker | `main` | no venv ignore | `.venv/`, `.venv*/`, `venv/`, `env/`, `ENV/` | `8a85aae` | ✅ `689e8ee..8a85aae` |

The `.venv*/` glob specifically catches the suffix-named variants (`.venv312/`, `.venv314-bak/`) created during the RC build process — the exact tripwire flagged in `PHOENIX_4_APP_SOURCE_BLOAT_AUDIT.md` § 5.

**Conflict check:** no `.gitignore` change conflicts with repo conventions. All edits are additive (appended ignore patterns); no existing patterns removed or reordered. CAD's structured "Virtual environments" section received one line; the other 3 (flat-list gitignores) received a 5-line venv block appended after their last existing entry.

**No venvs were deleted.** The local `.venv/`, `.venv312/`, `.venv314-bak/` directories remain on disk untouched — the change only prevents them from being accidentally `git add`-ed in future.

---

## 3. Confirmation — no source logic changed

| Repo | Files changed this housekeeping | Source logic touched? |
|------|----------------------------------|------------------------|
| Phoenix_CAD_Tool | `.gitignore` only | ❌ no |
| Phoenix-Checkout-Tool | `.gitignore` only | ❌ no |
| ValveMasterTool | `.gitignore` only | ❌ no |
| Job Tracker | `.gitignore` only | ❌ no |
| phoenix-commons | docs only (closure report + promotion-plan banner + MIGRATION_RULES rows + this report) | ❌ no |

No `.py`, no `build.bat`, no `installer.iss`, no `version.py`, no `.qss`, no updater, no theme/widget code touched in any repo.

---

## 4. Confirmation — no releases / tags / assets changed

- **No releases modified.** All 4 GitHub Releases (`v0.1.2` / `v1.7.1` / `v1.1.1` / `v1.8.6`) remain published, unchanged, with their original 2 assets each.
- **No tags moved or created.** RC tags (`-rc1`), stable tags, and forensic retrofit tags all intact at their original SHAs. The `.gitignore` commits landed on the mainline branches *after* the tagged commits — they do not affect any tagged/released SHA.
- **No assets uploaded or removed.**
- **No rebuild.**

Note: the 4 `.gitignore` commits advance each repo's mainline HEAD past the released tag (e.g. CAD `master` is now `17ec3e7`, one commit ahead of the `v0.1.2` tag at `35a0661`). This is expected + correct — the release is pinned to its tag; mainline continues forward. The next release of each tool will include the gitignore hardening.

---

## 5. Remaining optional cleanup

| Item | Status | Notes |
|------|--------|-------|
| Delete local `.venv314-bak/` (CAD, Checkout) + `.venv312/` (VM, JT) | deferred | Frees ~3 GB across the 4 repos. Operator's call when convenient — now safely gitignored so they won't be committed regardless. |
| Real-client `download_and_apply` round-trip per tool | deferred | Click "Install & Restart" from a prior-version install; closes the one auto-updater path not headlessly exercised. |
| 24-h S1 reputation watch on published exes | deferred | Monitor for AV reputation lag in the first day post-publish. |
| Wave 8c — Screenshot_Tool retrofit | operator-gated | Per `PHOENIX_FAMILY_RELEASE_READINESS_AUDIT.md` § 5 — operator decides whether Screenshot_Tool joins the commons family. |
| PCC packaging decision | operator-gated | Currently source-run only; packaging infra exists if/when wanted. |
| Asset-naming cleanup | deferred | `ASSET_NAMING_PROPOSAL.md` — retire legacy `PTT_` / `Normal_red` / `Transparent_red` prefixes; broad-surface touch, best as a future sprint. |

---

## 6. End state

- ✅ Release cycle closed (`PHOENIX_4_APP_RELEASE_CLOSURE_REPORT.md`)
- ✅ Active planning docs reflect published reality
- ✅ All 4 app repos protected against accidental venv commits (`.venv*/` ignored)
- ✅ No source logic changed
- ✅ No releases / tags / assets modified
- ✅ No new product/feature work started

The Phoenix family is released, documented, and the repos are hardened against the venv/build-artifact commit tripwire. Remaining items are all operator-discretion follow-ups; none are blocking.

---

*Post-release housekeeping complete 2026-06-01. Release cycle fully closed.*
