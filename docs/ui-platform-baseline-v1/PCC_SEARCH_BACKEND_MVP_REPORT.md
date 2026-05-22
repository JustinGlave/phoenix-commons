# PCC Search Backend MVP — Phase 3F Report

> **Status:** complete (PCC commit on retrofit branch, pending operator
> review + push).
> **Date:** 2026-05-22.
> **Branch:** `phase-3f-pcc-search-mvp` (PCC).
> **Scope:** Replace the dashboard Ctrl+K search placeholder with a real
> bounded MVP over already-cached tool / TODO / commit / path data.
> Per the Phase 3F operator brief.
> **Operator gate:** visual review before merge-gate preparation.

---

## 1. Data audit findings

### Available in-memory state (no scanner expansion needed)

| Source | Where it lives | Shape | Used in MVP? |
|--------|----------------|-------|--------------|
| Tool list | `MainWindow.tools` (line 38) | `list[dict]` with `{"name": str, "path": str}` per tool | ✅ — tool rows + path-substring matches |
| Per-tool scan payload | `MainWindow._tool_data` (line 38) | `dict[str, dict]` keyed by tool name | ✅ — TODO + commit rows |
| TODOs | `_tool_data[name]["todos"]` | `list[dict]` with `{text, tag, source_file, line_num, done}` | ✅ — open TODOs only (done filtered) |
| Recent commits | `_tool_data[name]["recent_commits"]` | `list[dict]` with `{msg, hash, when}` | ✅ — top-15/tool capped (matches scanner convention) |
| Tool config | `MainWindow.cfg["tools"][name]` | `dict` with `{github_url, launch_cmd, enabled}` | ✗ — not used; would require new "config" result kind which is out of MVP scope |
| Commons usage | `CommonsBrowser._usage` | `{rel_path: {size, users}}` | ✗ — separate page; not exposed to dashboard search |

### What the MVP intentionally does NOT search

  - **Commons file contents** — out of scope per spec §1; would require traversing the commons tree on every keystroke or building a separate index.
  - **File contents inside tools** — would require persistent indexing.
  - **Git history beyond `recent_commits`** — capped at the scanner's 15-commit window per tool.
  - **TODO history (done items)** — filtered out (operator typically wants open work).
  - **Tool config fields** — GitHub URL / launch command are configuration, not searchable content.

### Scanner contract

**Untouched.** `scanner.scan_repo` / `scanner.scan_commons_usage` / `ScanWorker` / `CommonsUsageWorker` — all unchanged. No new fields added to the per-tool payload. No new payload kinds. The MVP consumes only the data already cached by main_window after ScanWorker emits per-tool data.

---

## 2. SearchCorpus implementation

New file: `search.py` (245 LOC, pure-Python, no Qt imports — testable in isolation).

### Public API

```python
from search import SearchResult, build_corpus, search

# Build corpus from main_window's cached state:
corpus = build_corpus(tools, tool_data)

# Run search:
results = search(corpus, query, limit=20)
```

### Implementation summary

**`build_corpus(tools, tool_data)` → list[SearchResult]**:
  - Iterates tools sorted alphabetically by name.
  - For each tool, emits 1 tool-row + up to 50 TODO-rows + up to 15 commit-rows.
  - Tool row's haystack folds in slug + pretty name + path → path-substring search surfaces the tool (no separate "path" kind, avoids dropdown clutter).
  - Empty inputs return `[]`.

**`search(corpus, query, limit=20)` → list[SearchResult]**:
  - Empty / whitespace query → `[]`.
  - Case-insensitive substring filter via the per-row `haystack` field.
  - Stable sort by `(rank, emission_index)` → within a rank bucket, results preserve corpus order (alphabetical by tool name).
  - Default cap `limit=20`.

### Ranking

| Rank | Match type | Example |
|------|------------|---------|
| 0 | Exact tool name (slug OR pretty) | `phoenix-cad` ↔ tool "Phoenix Cad" |
| 1 | Tool name prefix | `phoenix` ↔ tool "Phoenix Cad" |
| 2 | Tool name contains | `cad` ↔ tool "Phoenix Cad" |
| 3 | TODO text contains | `memory leak` ↔ TODO "fix the memory leak" |
| 4 | Commit message contains | `wiring` ↔ commit "Fix wiring bug" |
| 5 | Tool path contains | `Projects` ↔ tool with path containing `Projects` |

Lower rank surfaces first. Stable sort preserves emission order within each rank.

### What it explicitly does NOT do (per spec §3)

  - No fuzzy-search library (`rapidfuzz`, `thefuzz`, etc.).
  - No async indexer.
  - No persistent index on disk.
  - No command-palette behavior (no slash commands, no actions).
  - No history.

---

## 3. Result model

```python
@dataclass(frozen=True)
class SearchResult:
    label:      str   # primary user-visible text
    subtitle:   str   # muted contextual text
    kind:       str   # "tool" / "todo" / "commit" — closed set
    tool_name:  str   # target tool slug
    tab_index:  int   # preferred detail-panel tab on activation
    haystack:   str   # pre-lowercased searchable string (not user-visible)
```

Frozen dataclass (immutable). Three result kinds — closed set per spec §2. `tab_index` follows the detail-panel convention:

| Tab index | Tab |
|-----------|-----|
| 0 | Overview (default, also for commits) |
| 1 | TODOs |
| 2 | Files (not a search-result kind in MVP) |
| 3 | Git (not a search-result kind in MVP) |

---

## 4. Results UI behavior

### `SearchResultsPopup(QFrame)` — new class in `dashboard.py`

Floating result list rendered as a child of the Dashboard widget, positioned dynamically under the search input via `_reposition_results_popup`. Lazily constructed by `_install_search_popup` — Qt widgets aren't allocated until the operator actually types a query.

### Composition

```
┌────────────────────────────────────────────┐
│ [icon] Primary label                       │
│        muted subtitle line                 │  ← one row
├────────────────────────────────────────────┤
│ [icon] Primary label                       │
│        muted subtitle line                 │  ← another row
├────────────────────────────────────────────┤
│ ... up to 8 rows visible, then scrolls ... │
└────────────────────────────────────────────┘
```

Each row: `[Lucide kind icon 14×14]` + `[QLabel label / muted subtitle column]` in a horizontal layout. No "kind pill" duplicating the icon's signal.

Per-kind Lucide icon mapping:

| Kind | Lucide icon | Tint |
|------|-------------|------|
| `tool` | `package` | accent (PCC orange) |
| `todo` | `warning` | warning (amber) |
| `commit` | `git-branch` | info (blue) |

All three icons already in `ICON_NAMES` post-Phase-3D. No new commons icons added.

### No-results state

Non-empty query with zero matches renders a single disabled placeholder row reading `No results for "<query>"`. Empty query hides the popup entirely.

### Pre-scan state

Search before any scan completes (`self.tools` is empty) shows the empty popup + status-bar message `"Search available after scan completes."` — graceful omission per spec §1.

### Sizing

Popup width matches the search input frame width (recomputed on resize via the Dashboard's `resizeEvent`). Height grows row-by-row up to 8 visible rows, then scrolls internally.

### Visual treatment

Calm card chrome via documented B6 carve-out:
```python
self.setStyleSheet(
    f"QFrame#searchResultsPopup {{ "
    f"background: {C['card']}; "
    f"border: 1px solid {C['border_hi']}; "
    f"border-radius: 8px; "
    f"}}"
)
```

Inline `setStyleSheet` here is the same affordance-defining-chrome carve-out the CommonsDropZone uses — the popup chrome IS its identity as a floating search overlay; no global QSS rule for it yet.

---

## 5. Routing behavior

### Three result kinds → three routes

| Kind | Target | Tab index | Detail-panel destination |
|------|--------|-----------|---------------------------|
| `tool` | `_open_detail(name, tab_index=0)` | 0 | Overview (sync card + recent commits) |
| `todo` | `_open_detail(name, tab_index=1)` | 1 | TODOs tab (per-file TODO list) |
| `commit` | `_open_detail(name, tab_index=0)` | 0 | Overview (recent commits feed) |

### Why `commit` doesn't deep-link to a specific commit

The detail panel's Overview tab already renders the recent_commits feed. Deep-linking to a specific commit row would require either:
  - Adding a commit-id query param to `_open_detail` + selection logic, OR
  - Scrolling the commit feed to a specific row

Per spec §5 ("If tab-routing is not clean: open the tool detail panel only. Do NOT add fragile routing."), the commit result opens the Overview tab. Operator can scan the feed visually.

### Why `todo` does deep-link to the TODOs tab

The TODOs tab is exactly the surface that shows TODOs. Opening it directly when the operator searched for a TODO is the obvious cheap win — no scroll-to-row logic needed, the tab itself is the destination.

### Out-of-range tab_index falls back to 0

If a future change passes an invalid `tab_index` (e.g. 5), the routing handler clamps to 0 (Overview). Prevents fragile routing on edge cases. Per spec §5.

### Signal contract

```python
# dashboard.py emits:
search_result_chosen = Signal(str, str, int)   # (kind, tool_name, tab_index)

# main_window.py connects:
self.dashboard.search_result_chosen.connect(self._on_search_result_chosen)
```

Three-arg signal — explicit + readable. No bundled dict, no opaque object payload.

---

## 6. Validation results

| Check | Result |
|-------|--------|
| PCC `python -m compileall -q . -x "\.venv\|commons\|build\|dist\|__pycache__"` | ✓ clean (exit 0) |
| PCC `python -m pytest -q tests/` | ✓ **4 passed in 0.86s** |
| Offscreen 11-scenario smoke | ✓ ALL PASS |

### Smoke scenarios validated

| # | Scenario | Result |
|---|----------|--------|
| 1 | `build_corpus(3 tools + synthetic TODOs/commits)` | ✓ 9 rows (3 + 3 + 3); done item excluded |
| 2 | Exact tool name `phoenix-cad` | ✓ top result kind=`tool` name="Phoenix Cad" |
| 3 | Tool prefix `phoenix` | ✓ top result kind=`tool` |
| 4 | TODO substring `memory leak` | ✓ kind=`todo` text="fix the memory leak" |
| 5 | Commit substring `wiring` | ✓ kind=`commit` msg="Fix wiring bug" |
| 6 | Path substring `Projects` | ✓ 3 tool results matched (all 3 tools have "Projects" in path) |
| 7 | No-results query `asdfgh-no-match` | ✓ empty list returned |
| 8 | Empty query | ✓ empty list returned |
| 9 | Rank "fix" → todos before commits | ✓ rank 3 (todo) surfaces above rank 4 (commit) |
| 10 | Done items excluded | ✓ `old done item` does NOT appear |
| 11 | Popup visible + `current_result` returns first SearchResult | ✓ |
| 12 | Routing: tool / todo / commit → correct kind + tab_index | ✓ (0, 1, 0) respectively |
| 13 | Empty query hides popup; no-results query shows placeholder | ✓ |
| 14 | Placeholder string "backend coming in Step 7" removed from source | ✓ |

### Scanner / FileViewer / tree integrity

| Surface | Status |
|---------|--------|
| `scanner.scan_repo` | ✓ untouched |
| `scanner.scan_commons_usage` | ✓ untouched |
| `ScanWorker` / `CommonsUsageWorker` | ✓ untouched |
| `FileViewer` | ✓ untouched |
| `QTreeView` / `QFileSystemModel` (in Commons Browser + detail panel Files tab) | ✓ untouched |
| `_tool_data` shape | ✓ unchanged — search is a read-only consumer |
| `_open_detail` signature | ✓ unchanged — pre-existing `tab_index` kwarg consumed as-is |
| `MainWindow.tools` list shape | ✓ unchanged |

### Invariants preserved

| Invariant | Status |
|-----------|--------|
| B5 — subprocess CREATE_NO_WINDOW | ✓ preserved (no new subprocess calls) |
| B6 — no widget-level setStyleSheet on commons primitives | ✓ preserved (popup chrome is the documented affordance carve-out) |
| BrandProfile — orange + teal per ADR-016 | ✓ untouched |
| Commons API stability | ✓ no commons changes; reads existing icons |
| Phase 3C / 3D / 3E retrofit chrome | ✓ no regressions; search popup sits on top of the existing dashboard chrome |

---

## 7. Known limitations

These are intentional MVP boundaries, not bugs. Per the Phase 3F spec they're deferred to future-phase candidates.

| Limitation | Why deferred |
|------------|--------------|
| No fuzzy matching | Substring is sufficient for the operator's typical query lengths (3-8 chars). Fuzzy adds dependency + complexity without proven need. |
| No commit deep-link | Spec §5: avoid fragile routing. Operator scans the commit feed visually after the Overview opens. |
| No TODO deep-link to source-file:line | Same reason — would require Files-tab open + tree expand + scroll-to-line; fragile. |
| No tool config search (GitHub URL, launch cmd) | Out of result kinds (`tool`/`todo`/`commit` is closed set per spec §2). |
| No commons file content search | Out of scope per spec §1; would require commons-side indexing. |
| Done TODOs excluded | Operator searches open work, not history. Could surface as a future toggle. |
| Recent-commits window capped at 15/tool | Scanner convention; expanding would require scanner contract change (forbidden by spec §3). |
| Live-update fires on EVERY keystroke | Acceptable at typical tool counts (≤20). A future enhancement could debounce at 50+ keystrokes/sec via QTimer, but no operator complaint observed. |
| Popup positioning recomputes only on `resizeEvent` | Doesn't re-position on Dashboard's parent QStackedWidget switch. Mitigated because the popup is hidden + lifecycle-tied to the dashboard page. |
| Search popup uses inline stylesheet on its outer QFrame | Documented B6 carve-out (affordance-defining chrome). Could be promoted to a global `#searchResultsPopup` rule in PCC `theme.py` as a future polish. |

---

## 8. Recommended next step

### Recommendation: **Operator visual review, then merge-gate preparation.**

Phase 3F's MVP scope is complete and source-mode validated. The natural sequence:

  1. **Operator visual review** — run PCC from `phase-3f-pcc-search-mvp` branch; exercise typing into Ctrl+K, observe the popup, click a tool/TODO/commit result, verify it lands on the right detail-panel tab.
  2. **Phase 3F merge-gate report** — mirroring the Phase 3E closure pattern (holistic review + state validation + merge-readiness audit + merge plan).
  3. **Merge** — `--no-ff` to PCC `main`, tag `pcc-phase-3f-merged-v2.3.0`, governance row in `MIGRATION_RULES.md`.

### What this DOES NOT recommend opening next

  - **Persistent search index** — premature optimisation; substring suffices for current tool counts.
  - **Command palette** — explicit spec §STRICT non-goal.
  - **Search history** — explicit spec non-goal.
  - **Commons file content search** — separate feature; would need its own surface spec.
  - **Wave 8a (ValveMaster)** — remains operator-gated to the existing 2026-06-02 doctrinal cooldown floor. Phase 3F's merge does not affect it.

### Hypothetical small follow-on polish (NOT Phase 3F scope)

  - Debounce the live search on textChanged at 100ms intervals — would matter only above ~30 tools.
  - Promote the popup chrome inline-QSS to a `#searchResultsPopup` rule in `theme.py` — cosmetic cleanup, B6 invariant tightening.
  - Add a "Search across commons files" affordance — would require its own spec.

---

## 9. Confirmation

  - **No architecture changes occurred.** No new ADR. No commons API change. No new commons widget. No new commons icon. `BrandProfile` unchanged. ADR-014 / ADR-015 / ADR-016 all hold.
  - **No BrandProfile changes occurred.** PCC `BrandProfile` (orange + teal per ADR-016) unchanged.
  - **No scanner contract changes occurred.** `scanner.scan_repo`, `scanner.scan_commons_usage`, `ScanWorker`, `CommonsUsageWorker` — all unchanged. No new fields. No new payload kinds.
  - **No production deployment occurred.** PCC is unpackaged per `CLAUDE.md`. No installer built. No `dist/` artifact. No GitHub Release. Phase 3F commit lives on the local `phase-3f-pcc-search-mvp` branch (not yet pushed — operator-gated).
  - **No Wave 8a work occurred.** Wave 8a remains operator-gated to the existing 2026-06-02 doctrinal cooldown floor.
  - **No FileViewer changes occurred.** `file_viewer.py` untouched.
  - **No tree / QTreeView / QFileSystemModel work occurred.** Commons Browser tree + Detail Panel Files-tab tree both unchanged.
  - **No production tool source touched.** Phoenix CAD / Phoenix Checkout / PTT / ValveMaster all unmodified.
  - **No Settings / Wizard / About / Push Preview work occurred.** Each remains a separate deferred candidate.
  - **No new commons primitives or icons added.** `package`, `warning`, `git-branch`, `search` icons all pre-existing in `ICON_NAMES` since Phase 2.2/3D.
  - **No persistent index, no fuzzy library, no command palette.** Spec §STRICT non-goals preserved.

---

## Commit summary

| Repo | Commit | Subject | Pushed |
|------|--------|---------|--------|
| `phoenix-command-center` `phase-3f-pcc-search-mvp` | `19ec360` | Search MVP — make Ctrl+K actually work (Phase 3F) | pending (operator-gated) |
| `phoenix-commons` `main` | (this report, pending) | Add PCC_SEARCH_BACKEND_MVP_REPORT | pending |

PCC retrofit branch tip after Phase 3F: `19ec360` (1 commit ahead of `829c513` = post-Phase-3E main).

No commons source change in Phase 3F — only this report file is added.

---

*End of report. Phase 3F MVP = complete. Operator gate before merge-gate preparation opens.*
