# Phoenix Family — 4-App Source-vs-Build Bloat Audit

> **Status:** read-only audit. No deletions, no commits, no source changes.
> **Date:** 2026-06-01.
> **Trigger:** ~1M-LOC-per-app perception. Investigates whether the bulk is committed source or unchecked build/venv artifacts.

---

## TL;DR

**All 4 tracked repos are small and clean.** No `dist/`, `build/`, `_internal/`, `.venv*/`, or `__pycache__` is committed in any of them. Total tracked `.py` LOC across all 4 repos: **~33,000**. Total tracked LOC (including binaries / README / config / QSS): **~64,000**.

The "~1M LOC per app" perception comes from **untracked working-tree artifacts** — primarily `.venv*/` directories (680–850 MB each, × 2 venvs in VM/JT) plus `dist/` (200–280 MB) and `build/` (8–16 MB). These never reached git.

**No release publication is blocked by bloat.** The only finding worth fixing is a `.gitignore` gap (3 of 4 repos don't ignore `.venv*/` — a future-safety nit, not a present-state risk).

---

## 1. Repo-by-repo tracked source size

| Repo | Tracked files | Tracked `.py` LOC | Total tracked LOC* | Tracked binary files |
|------|---------------|--------------------|---------------------|------------------------|
| Phoenix_CAD_Tool | 83 | 6,524 | 25,541 | 20 |
| Phoenix-Checkout-Tool | 32 | 4,477 | 7,380 | 6 |
| ValveMasterTool | 33 | 10,030 | 12,948 | 9 |
| Job Tracker | 41 | 11,917 | 18,407 | 18 |
| **TOTALS** | **189** | **32,948** | **64,276** | **53** |

\* "Total tracked LOC" includes README/CHANGELOG/CLAUDE.md/.gitignore/build.bat/installer.iss/*.qss + binary line-counts (`wc -l` returns non-meaningful numbers on binaries — included for completeness).

**Conclusion:** the 4 tracked repos are small. The largest single tool by source is Job Tracker at ~12k `.py` LOC + ~18k total tracked LOC. Nothing matches "1M LOC" by 1.5 orders of magnitude.

---

## 2. Tracked generated-artifact findings

Per-repo grep for `dist/`, `build/`, `_internal/`, `.venv*/`, `__pycache__/`, `site-packages/`, `*.pyc` in `git ls-files`:

| Repo | Suspicious tracked paths |
|------|---------------------------|
| Phoenix_CAD_Tool | **none** ✅ |
| Phoenix-Checkout-Tool | **none** ✅ |
| ValveMasterTool | **none** ✅ |
| Job Tracker | **none** ✅ |

**No generated artifacts are tracked in any repo.** All builds + dependencies live in the untracked working tree.

---

## 3. Untracked working-tree generated artifacts

Per repo: artifacts on disk, their size, and gitignore state.

| Repo | Path | Size | Gitignored? |
|------|------|------|-------------|
| **Phoenix_CAD_Tool** | `dist/` | 280 MB | ✅ ignored |
| | `build/` | 8.0 MB | ✅ ignored |
| | `.venv/` | 697 MB | ✅ ignored |
| | `.venv314-bak/` | 698 MB | ❌ NOT ignored (matches no rule) |
| **Phoenix-Checkout-Tool** | `dist/` | 242 MB | ✅ ignored |
| | `build/` | 16 MB | ✅ ignored |
| | `.venv/` | 680 MB | ❌ NOT ignored |
| | `.venv314-bak/` | 678 MB | ❌ NOT ignored |
| **ValveMasterTool** | `dist/` | 200 MB | ✅ ignored |
| | `build/` | 7.5 MB | ✅ ignored |
| | `.venv/` | 851 MB | ❌ NOT ignored |
| | `.venv312/` | 674 MB | ❌ NOT ignored |
| **Job Tracker** | `dist/` | 279 MB | ✅ ignored |
| | `build/` | 12 MB | ✅ ignored |
| | `.venv/` | 702 MB | ❌ NOT ignored |
| | `.venv312/` | 702 MB | ❌ NOT ignored |

### Per-repo untracked working-tree totals

| Repo | Untracked artifact total on disk |
|------|----------------------------------|
| Phoenix_CAD_Tool | ~1.7 GB |
| Phoenix-Checkout-Tool | ~1.6 GB |
| ValveMasterTool | ~1.7 GB |
| Job Tracker | ~1.7 GB |
| **TOTAL** | **~6.7 GB** |

**Critical: none of this is in git.** Even though `.venv*/` is NOT in the `.gitignore` for 3 of 4 repos, the venvs were never `git add`-ed, so they didn't slip into history.

### Classification

| Artifact type | Should be tracked? | Current state |
|---------------|--------------------|--------------------|
| `dist/<App>/<App>.exe` (frozen exe) | NO | not tracked; ignored ✅ |
| `dist/<App>/_internal/` (PyInstaller runtime) | NO | not tracked; ignored ✅ |
| `dist/<App>Setup.exe` (Inno Setup installer) | NO (uploaded to GitHub Release) | not tracked; ignored ✅ |
| `dist/<App>.zip` (updater zip) | NO (uploaded to GitHub Release) | not tracked; ignored ✅ |
| `dist/<App>_FullInstall.zip` (manual install zip) | NO | not tracked; ignored ✅ |
| `build/` (PyInstaller intermediate cache) | NO | not tracked; ignored ✅ |
| `.venv/` (dev/build virtualenv) | NO | not tracked; **mostly NOT in .gitignore** — see § 4 |
| `.venv312/` / `.venv314-bak/` (operator-named alt venvs) | NO | not tracked; NOT in `.gitignore` |

---

## 4. Release artifact necessity — per-app expected shape

All 4 release-bound shapes already verified in `PHOENIX_4_APP_FINAL_RELEASE_DRAFTS_REPORT.md` § 5 and re-confirmed here.

| App | Expected updater zip | Current zip in `dist/` | Contract |
|-----|----------------------|--------------------------|----------|
| Phoenix CAD | **full-folder** (exe + `_internal/*`) | `LabLayoutTool.zip` 55.6 MB, 305 entries | ✅ matches |
| Phoenix Checkout | **exe-only** (just `<App>.exe`) | `PhoenixCheckoutTool.zip` 4.4 MB, 1 entry | ✅ matches |
| ValveMaster | **exe-only** (ADR-003) | `PhoenixMasterTool.zip` 1.9 MB, 1 entry | ✅ matches |
| Job Tracker | **full-folder** (`expected_internal=True`) | `ProjectTrackingTool.zip` 54.8 MB, 260 entries | ✅ matches |

All 8 release-bound artifacts (installer + updater zip per app) are present + correctly shaped. No release blocker.

---

## 5. .gitignore audit

| Repo | Covers `dist/` | Covers `build/` | Covers `.venv/` | Covers `.venv*/`-suffix variants | Covers `__pycache__/` | Covers `*.pyc` | Covers `*.spec` |
|------|----------------|------------------|------------------|----------------------------------|------------------------|------------------|------------------|
| Phoenix_CAD_Tool | ✅ | ✅ | ✅ (`.venv/`) | ❌ no `.venv*/` glob — `.venv314-bak` not caught | ✅ | ✅ (`*.py[cod]`) | ✅ |
| Phoenix-Checkout-Tool | ✅ | ✅ | ❌ | ❌ | ✅ | ✅ | ✅ |
| ValveMasterTool | ✅ | ✅ | ❌ | ❌ | ✅ | ✅ | ✅ |
| Job Tracker | ✅ | ✅ | ❌ | ❌ | ✅ | ✅ | ✅ |

### Gap summary

| Gap | Impact |
|-----|--------|
| 3 of 4 repos don't ignore `.venv/` | A careless `git add -A` would commit ~700 MB of venv binaries. Right now: no venvs are actually staged, so no historical risk. |
| 4 of 4 repos don't catch suffix-named variants (`.venv312/`, `.venv314-bak/`) | Same tripwire as above but for the rename-swap pattern that's been used throughout the RC build process. |

### Recommended .gitignore additions (post-release, non-blocking)

Add to all 4 repos:

```
# Virtual environments (any suffix variant)
.venv/
.venv*/
venv/
env/
ENV/
```

Phoenix_CAD_Tool already has the first 4 patterns. Adding `.venv*/` to all 4 closes the suffix-variant gap.

---

## 6. Is the "~1M LOC per app" perception source or build output?

**It is unambiguously NOT source.**

- Tracked source per app: 4–12k `.py` LOC, 7–25k total tracked LOC.
- Cross-app total tracked: ~33k `.py` LOC, ~64k total tracked LOC.
- "1M LOC per app" would imply each repo's git history holds a million lines. Actual largest is Job Tracker at 18k tracked LOC — **off by ~55×**.

The perception likely comes from:

1. **Recursive line-counting tools** that descend into `.venv*/` directories. A single venv contains the unpacked PySide6 + openpyxl + pyxlsb + reportlab + pyinstaller wheels — easily 1M+ lines of vendored Python code from third-party packages. Counting that as "the repo" inflates the apparent size ~100×.
2. **Disk-size confusion** — each repo's working tree is 1.6–1.7 GB on disk, dominated by 2 venvs. A glance at "this repo is huge" is correct *for disk* but wrong *for source*.
3. **PyInstaller `dist/` directory** — frozen exes ship 200+ MB of PySide6 Qt DLLs + plugins + translations + commons; this is bundled output, not source.

### Where the bulk actually lives

Per repo, dominant disk usage:

| Repo | Largest path on disk | Size | Nature |
|------|-----------------------|------|--------|
| Phoenix_CAD_Tool | `.venv/` + `.venv314-bak/` | 1.4 GB | 2 venvs (3.12 + 3.14 backup) |
| Phoenix-Checkout-Tool | `.venv/` + `.venv314-bak/` | 1.4 GB | 2 venvs |
| ValveMasterTool | `.venv/` + `.venv312/` | 1.5 GB | 2 venvs (3.14 + 3.12) |
| Job Tracker | `.venv/` + `.venv312/` | 1.4 GB | 2 venvs |

Each venv ≈ 680–850 MB because PySide6 alone ships ~500 MB. Two venvs per repo because the RC build process created a 3.12 venv alongside the existing 3.14 dev venv.

---

## 7. Cleanup recommendations

### Now (release-blocking? **no**)

None. The 4-app RC drafts can publish exactly as-is. No bloat is in git history; no required release artifact is missing; all updater contracts intact.

### Soon (operator-discretion, post-release polish)

1. **Add `.venv*/` to 3 gitignore files** (Phoenix-Checkout-Tool, ValveMasterTool, Job Tracker) — and extend Phoenix_CAD_Tool's `.venv/` to `.venv*/` to catch the suffix-variant gap. 1-line change per repo. Eliminates the careless `git add -A` tripwire.
2. **Local working-tree cleanup** (operator's call) — once the 4 RCs publish, the venv backups (`.venv314-bak/`, `.venv312/`) can be deleted from disk without affecting any release or repo. Frees ~3 GB across the 4 repos.

### Later (architectural — out of release-readiness scope)

- Consider documenting the 3.12 build-venv convention in each repo's `CLAUDE.md` so operators don't accidentally end up with parallel 3.14 + 3.12 venvs again. Wave 8a/8b CLAUDE.md updates already document this for VM + JT; CAD + Checkout could benefit from the same note.

---

## 8. Is any release publication blocked?

**No.** All 4 drafts are publish-ready per `PHOENIX_4_APP_FINAL_RELEASE_DRAFTS_REPORT.md`:

- ✅ No suspicious paths in git history
- ✅ All required release artifacts (8 total: 4 installers + 4 updater zips) uploaded to drafts
- ✅ All updater contracts intact (CAD/JT full-folder; Checkout/VM exe-only)
- ✅ No source/version drift
- ✅ All asset filenames byte-exact

The .gitignore gap is a **future-safety nit, not a release blocker.** Adding `.venv*/` to the 3 missing gitignores can happen before, after, or never relative to the release publication — the gap doesn't affect any release artifact.

---

## 9. Confirmation

- **No source changed** in any of the 4 production repos.
- **No artifacts deleted.** All `.venv*/`, `dist/`, `build/`, `.venv314-bak/`, `.venv312/` directories remain on disk untouched.
- **No releases published.** The 4 drafts from `PHOENIX_4_APP_FINAL_RELEASE_DRAFTS_REPORT.md` remain in `draft: true` state.
- **No commits, no pushes, no tag changes** triggered by this audit.

### Stop conditions — none triggered

- ✅ No `dist/`, `build/`, `_internal/`, `.venv*/` is tracked in git in any repo
- ✅ All release artifacts are present + correctly shaped
- ✅ All updater zip contracts are unambiguous + verified
- ✅ The "~1M LOC" perception is fully explained by untracked venv content + bundled frozen-exe output — neither is source-of-truth bloat

---

*Audit complete. Release publication is not blocked. Recommended optional cleanup is a `.gitignore` doc-touch in 3 repos; non-blocking.*
