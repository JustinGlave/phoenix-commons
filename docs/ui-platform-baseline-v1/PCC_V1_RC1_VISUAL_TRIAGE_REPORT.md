# PCC v1.0.0-rc1 — Visual Triage Report

> **Status:** triage only — **no code edited, no rebuild, RC progression paused.**
> **Date:** 2026-06-02.
> **Repo:** `phoenix-command-center` (RC branch `release/v1.0.0-rc1` @ `0245be0`).
> **Recommendation:** **Apply a tiny fix first** (one scanner skip-set fix +
> two small UI polish items), re-validate, rebuild **rc2**, then resume.

---

## 1. Issues observed (operator interactive validation)

| # | Surface | What looks wrong | Expected |
|---|---------|------------------|----------|
| 1 | Dashboard (sidebar/tiles) | LOC reads 941k / 603k / 817k / 781k per app | Realistic source LOC (tens of k), not inflated |
| 2 | Commons browser — "Used By" footer | Every file shows used-by **all** tools | Per-file accuracy: which apps actually reference each commons file |
| 3 | TODO Workbench — Status column | "Open"/longer labels cut off (too narrow) | Column wide enough for the longest status label |
| 4 | TODO Workbench — rows | TODOs sourced from `.claude/worktrees/…`, `.venv312/Lib/site-packages/…`, `.github/pull_request_template…` | Only real project TODOs (markdown checklists + code-comment tags in source) |
| 5 | Detail panel — Git Actions | Pull / Push / Fetch buttons have no description | Each button explains what it does |

## 2. Notes / evidence used

5 operator screenshots (sidebar TOOLS LOC; Commons "Used By" footer; Workbench
Status column; Workbench File column; Git Actions row) + code inspection of
`scanner.py`, `commons_browser.py`, `todo_workbench.py`, `detail_panel.py`.

## 3. Root-cause findings

**Shared root cause for #1, #4, and most of #2** — `scanner.py`:
```python
_SKIP_DIRS = {".git","__pycache__","node_modules","venv",".venv","dist","build",".mypy_cache"}
...
dirs[:] = [d for d in dirs if d not in _SKIP_DIRS]   # 4 walk sites
```
The skip is **exact-match**, so it misses:
- **`.venv312`** (version-suffixed venvs — the actual venv name here) → walks
  `*/Lib/site-packages/*` → inflated LOC (#1) + thousands of third-party TODOs (#4).
- **`.claude`** (`/.claude/worktrees/<name>/` hold **full repo copies**, incl.
  commons-doc copies) → inflated LOC (#1) + duplicate TODOs (#4) + makes every
  commons file appear in every tool's text corpus → "used by all" (#2).

LOC already restricts to code extensions (`_ALL_CODE_EXTS`), so the **only** fix
needed for #1/#4 is the skip set. `.github/pull_request_template.md` checkboxes
(#4, minor) are real repo files but template boilerplate, not TODO debt.

**#2 second layer** — `scan_commons_usage` matches a commons file to a tool by
**filename substring** in the tool's text. Even after the skip-set fix, common
doc names (`README.md`, `CHANGELOG.md`, `LICENSE`, `CLAUDE.md`…) match in every
tool. Tools don't actually "use" commons *docs* — only code/assets are imported.
Full per-file accuracy is a heuristic refinement.

**#3 / #5** — pure PCC-UI: Status column left at `ResizeToContents` (badge cell
reports a small hint); Git buttons created without `setToolTip`.

## 4. Classification

| # | Issue | Class | Rationale |
|---|-------|-------|-----------|
| 1 | LOC inflated | **A — release blocker** | Core Ground-Control metric is wrong/misleading; undermines the dashboard |
| 4 | TODOs from `.claude`/`.venv312` | **A — release blocker** | Pollutes the flagship TODO Workbench with hundreds of non-project rows |
| 3 | Status column too narrow | **B — small polish** | Pure visual; tiny, low-risk; fix now |
| 5 | Git buttons undocumented | **B — small polish** | Add tooltips; tiny, low-risk; fix now |
| 2 | Commons "Used By" inaccurate | **B (partial) + C (residual)** | Skip-set fix removes the worst (worktree/venv) amplification; full doc-file accuracy is a v1.1 heuristic refinement |
| 4b | `.github/pull_request_template.md` checkboxes | **C — v1.1 (minor)** | Real repo file; template boilerplate noise; optional |

No issue requires a redesign, a scanner **contract** change (data shape/fields
unchanged), a commons-architecture change, or touches TODO source-edit safety or
the updater contract.

## 5. Fix-now items (smallest targeted patches — PROPOSED, awaiting approval)

### Fix S1 — scanner directory-skip (resolves #1 + #4; substantially improves #2)
- **File:** `scanner.py` (one helper + the existing `_SKIP_DIRS` literal; 4 walk
  sites switch to the helper).
- **Change:** add `.claude` (+ `.idea`, `.pytest_cache`, `.ruff_cache`, `.tox`,
  `env`) to `_SKIP_DIRS`, and prefix-match version-suffixed venvs:
  ```python
  def _skip_dir(name: str) -> bool:
      return name in _SKIP_DIRS or name.startswith(".venv")
  # 4 sites: dirs[:] = [d for d in dirs if not _skip_dir(d)]
  ```
- **Not a contract change:** `get_file_stats` (loc int), `get_todos` (same dict
  fields), `discover_tools` (same list), `scan_commons_usage` (same shape) — all
  unchanged in shape/API; only *which directories are walked* changes → accurate
  LOC + clean TODOs + cleaner Used-By.
- **⚠ touches `scanner.py`** — flagged by your "STOP if scanner change" guard, so
  it is **proposed, not applied**, pending your explicit approval. (It's a
  skip-set bug fix, not a contract change.)

### Fix U1 — Workbench Status column width (#3)
- **File:** `todo_workbench.py` — set the Status column to a fixed/interactive
  width (e.g. ~120 px) instead of `ResizeToContents`. ~1 line.

### Fix U2 — Git Actions tooltips (#5)
- **File:** `detail_panel.py` — add `setToolTip` to `pull_btn` / `push_btn` /
  `fetch_btn` ("Pull: fetch + merge origin into this branch", "Push: publish
  local commits to origin", "Fetch: update remote-tracking refs without
  merging"). 3 lines.

### Validation required (after approval, before rebuild)
- `compileall` + `pytest tests/` (expect 83 — these are pure unit tests; the
  skip change affects live scanning only).
- Offscreen scan smoke: run `scanner.get_file_stats`/`get_todos` on a real tool
  dir and assert no `.venv*` / `.claude` paths appear and LOC is realistic.
- Offscreen Workbench render: Status column no longer clips; Git tooltips set.
- Rebuild **v1.0.0-rc2** + re-tag; re-run frozen + installer smokes.

## 6. Deferred (do NOT fix now)

- **#2 residual** — exclude doc/asset files from "Used By" and/or replace the
  filename-substring heuristic with import-aware probes → **v1.1**. (The skip-set
  fix already removes the worst symptom.)
- **#4b** — `.github` PR-template checkbox noise → **v1.1** (or a one-line
  `.github` skip if you want it gone now — your call).

## 7. Release impact

- **#1 + #4 are release blockers** — shipping rc1 would present wrong LOC on the
  dashboard and a TODO Workbench full of `.venv312` / `.claude` noise (the exact
  flagship feature this release is built around). **Do not ship rc1 as-is.**
- **#3 + #5** are small polish — fold into the same fix pass.
- **#2** is materially improved by the same skip-set fix; the residual doc-file
  coarseness is acceptable for v1 (documented heuristic) and refined in v1.1.

## 8. Recommendation

### **Apply tiny fix first**, then rebuild rc2.

One scanner skip-set fix (S1) clears both A blockers and most of #2; two ~1–3
line UI fixes (U1, U2) clear the small-polish items. Re-validate, rebuild
**v1.0.0-rc2**, resume interactive validation. The current `dist\` rc1 artifacts
and the `v1.0.0-rc1` tag remain as forensic markers (superseded by rc2).

**Approval needed** specifically for **Fix S1** (it edits `scanner.py`). U1/U2
are PCC-UI-only. I will not edit anything until you approve.

## 9. Confirmation

- ✅ **No release published.**
- ✅ **No assets uploaded.**
- ✅ **No final stable tag created.**
- ✅ **No broad redesign** — proposed fixes are a skip-set bug fix + two tiny UI
  tweaks; no scanner *contract* change, no commons-architecture change, no
  updater-contract change, no TODO source-edit-safety change.
- ✅ **No code edited yet** (triage + proposals only).

### STOP-condition check

- Broad redesign required? **No.**
- Scanner/commons change required? **#1/#4 (and partial #2) need a `scanner.py`
  skip-set fix** — surfaced here for explicit approval rather than applied
  (honoring the STOP guard); it is a bug fix, not a contract change.
- TODO source-edit safety affected? **No.**
- Updater contract affected? **No.**
- Classification ambiguous? Only **#2's full fix scope** (skip-set vs heuristic
  rework) — split into B-now (skip-set) + C-deferred (heuristic) accordingly.

---

*Triage complete. Two A blockers (#1, #4) + two B polish (#3, #5) have a small,
targeted fix bundle; #2 is largely resolved by the same skip-set fix with a
v1.1 heuristic refinement deferred. Awaiting approval to apply Fix S1 (scanner
skip-set) + U1/U2, then rebuild v1.0.0-rc2.*
