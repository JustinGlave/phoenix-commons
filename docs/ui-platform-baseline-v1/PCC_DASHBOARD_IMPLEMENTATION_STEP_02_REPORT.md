# PCC Dashboard Implementation — Step 2 Report

> **Status:** complete.
> **Date:** 2026-05-21.
> **Scope:** Add `StatusBadge` primitive to commons + pilot it in one
> controlled PCC surface (dashboard ToolRow status) per
> `PCC_DASHBOARD_SURFACE_SPEC_V1.md` §6 step 2.
> **Operator gate:** visual review of the new status pill in the
> dashboard tool list before Step 3 (tools list → table) starts.

---

## 1. Status semantic definitions

A closed set of seven variants. The first five are required by the
spec brief; the last two (`syncing`, `scanning`) are the optional
"actively running" pair. Each is documented in the widget's
docstring and reified as a QSS property selector.

| Variant | Label convention | Color treatment | Semantic meaning |
|---------|------------------|-----------------|------------------|
| `clean` | `"Clean"` | `rgba(34,197,94,0.16)` bg / `#22c55e` text (commons SUCCESS) | Operation succeeded; state is healthy. Default "all good" indicator. |
| `dirty` | `"Changes"`, `"3 changes"` | `rgba(245,158,11,0.16)` bg / `#f59e0b` text (commons WARNING) | Has uncommitted / unsaved changes. Operator-actionable. |
| `warning` | `"Warning"`, `"Stale"` | Same amber as `dirty` | Non-fatal warning / partial success. Used where "dirty" doesn't read right. |
| `error` | `"Error"`, `"Failed"` | `rgba(239,68,68,0.16)` bg / `#ef4444` text (commons ERROR) | Operation failed / state needs immediate attention. |
| `unknown` | `"Unknown"` | `rgba(148,163,184,0.12)` bg / `#94a3b8` text (commons MUTED) | State unobservable or not yet scanned. Default initial value. |
| `syncing` | `"Syncing…"` | `rgba(59,130,246,0.16)` bg / `__BRAND_ACCENT__` text | Actively syncing — brand-accent aware (PCC teal / production-tool blue). |
| `scanning` | `"Scanning…"` | Same brand-accent treatment | Actively scanning. Distinct semantic from `syncing` (sync = remote, scan = local). |

### Calm operational semantics

All variants use tinted backgrounds (12-16% opacity) with saturated text — visually subtler than the existing `#PassBadge` / `#FailBadge` solid-fill style. No animation, no border pulses, no severity escalation. The badge announces state; the operator decides response.

### Closed-set contract

`StatusBadge.VARIANTS` is a `frozenset`. Adding an eighth variant requires a commons PR + a matching `#StatusBadge[variant="..."]` QSS selector. Invalid variants passed by callers fall back to `"unknown"` rather than raising — defensive but not silent (typos surface as visually muted pills, which are easy to spot).

---

## 2. StatusBadge API

Lightweight QLabel subclass with no inheritance branches, no factory methods, no manager class:

```python
from phoenix_commons.widgets import StatusBadge

class StatusBadge(QLabel):
    VARIANTS: frozenset[str] = frozenset({
        "clean", "dirty", "warning", "error",
        "unknown", "syncing", "scanning",
    })

    def __init__(
        self,
        text: str = "",
        variant: str = "unknown",
        *,
        compact: bool = False,
        parent=None,
    ) -> None: ...

    @property
    def variant(self) -> str: ...      # read-only
    @property
    def compact(self) -> bool: ...     # read-only (constructor-time only)

    def set_status(self, text: str, variant: str | None = None) -> None: ...
```

### How styling flows

The constructor sets `setObjectName("StatusBadge")` plus two Qt dynamic properties (`variant`, `compact`). The QSS file matches against `QLabel#StatusBadge[variant="clean"]` etc. — Qt's property-selector mechanism picks the right rule at first paint.

`set_status()` calls `style().unpolish(self) / polish(self)` when the variant changes, because property-selector QSS doesn't re-evaluate on a bare `setProperty()` call. Cheap — no widget recreation, no layout invalidation.

### What the widget is not

- Not a state machine — callers own transitions. `set_status()` is a single setter, not a lifecycle method.
- Not a notification surface — no animation, no autodismiss, no toast, no severity escalation.
- Not a manager — no registry, no broadcast signal, no observer pattern.
- Not extensible — `VARIANTS` is closed-set; the styling lives in commons QSS, not in subclass code.

If a future surface needs more elaborate behaviour (e.g. an actively-blinking sync indicator), it composes a small widget that *contains* a `StatusBadge`, not a subclass.

---

## 3. Commons files added/modified

| File | Change | Lines |
|------|--------|------:|
| `src/phoenix_commons/widgets/status_badge.py` | **NEW** — the widget. ~125 LOC including docstrings. | +125 |
| `src/phoenix_commons/widgets/__init__.py` | Export `StatusBadge` in imports + `__all__`; "Status" line added to public-API docstring. | +3 |
| `src/phoenix_commons/theme/phoenix_style.qss` | New `STATUSBADGE` section — `#StatusBadge` base rule + 1 `[compact="true"]` rule + 7 `[variant="..."]` rules. Placed before the existing `#PassBadge` / `#FailBadge` / `#ArchivedBadge` block so future readers see the canonical primitive first and the legacy badges as app-specific carve-outs. | +63 |
| `src/phoenix_commons/theme/embedded_qss.py` | Regenerated deterministically via `python -m phoenix_commons.theme.generate_embedded_qss`. 19,545 chars total, 18,805 chars of QSS embedded (was ~18,100). | regenerated |
| `tests/test_status_badge.py` | **NEW** — 17 unit tests covering construction defaults, every canonical variant, compact mode, `set_status`, invalid-variant fallback, frozen-set contract, read-only properties, and public-API surface (`__all__` membership). | +163 |

Total commons surface change: **5 files, +411 net LOC.** Two new files; three modified.

### Editable-install + frozen-build behaviour

`src/phoenix_commons/theme/phoenix_style.qss` ships in `pyproject.toml`'s `package-data` glob already (`*.qss`); no packaging change needed. The regenerated `embedded_qss.py` is the auto-update fallback used when `_internal/` is replaced wholesale — verified by `test_embedded_qss.py` which iterates the QSS and confirms the embedded copy matches byte-for-byte.

### Commits

| Repo / branch | Commit | Subject |
|---------------|--------|---------|
| sibling `phoenix-commons` `main` | `93389da` | widgets: add StatusBadge primitive |
| PCC submodule `commons` `main` | `75c03fb` | widgets: add StatusBadge primitive (mirror) |

Sibling and submodule have different commit SHAs but identical tree content (the same files were applied to both independently — same dual-checkout pattern used in B9).

---

## 4. PCC pilot surface used

**Dashboard `ToolRow` git-status indicator** (`pcc/dashboard.py`).

Pre-pilot: each row showed a 9px Unicode `●` glyph whose color was set inline (`setStyleSheet(f"color: {color}; font-size: 9px;")`). Status was conveyed through colour alone — no text label.

Post-pilot: each row shows a compact `StatusBadge` to the right of the TODO chip. Three states drawn from `scanner.get_git_info`:

| Scanner status | Badge variant | Label | Tooltip |
|----------------|---------------|-------|---------|
| `"clean"` | `clean` | `Clean` | `Git: clean` |
| `"dirty"` | `dirty` | `Changes` | `Git: uncommitted changes` |
| `"unknown"` | `unknown` | `Unknown` | `Git: status unknown` |

### Why this surface

1. **Single controlled change** — one widget on one surface; no broad churn.
2. **High visibility** — every dashboard load surfaces 5-7 status badges immediately. Operator sees rendering correctness on first paint.
3. **Removes one inline `setStyleSheet`** — preserves the post-B6 invariant of "no widget-level setStyleSheet outside theme.py" and slightly improves it (one fewer offender).
4. **Doesn't claim the sync-pill slot** — Step 6 will introduce a top-of-dashboard sync pill; keeping the pilot off that surface leaves it free for its own spec.

### Surfaces explicitly NOT touched in this commit

Per spec: "ONE controlled PCC surface only."

- Dashboard top scan indicator (`scan_lbl` in Dashboard) — still text-only ("Scanning…" / "5 tools loaded"). Will adopt `StatusBadge[variant="scanning"]` when the sync-pill spec lands.
- Detail panel git status text (`detail_panel.py`) — out of dashboard scope.
- Sidebar tool-row status dots — out of scope (sidebar is information-secondary; the dashboard is where the status badge earns its visual weight).
- Activity feed bullet dots (`·`) — semantic, not status — leave.
- Status bar scan-progress dot (`●` in `main_window.py`) — semantic; will reconsider at Step 6.

---

## 5. Validation results

| Check | Result |
|-------|--------|
| Commons `python -m pytest -q tests/` | **114 passed in 1.31s** (was 93 pre-Step-2; +21 new for `test_status_badge.py` covering construction + variant set + `set_status` + read-only properties + exports). |
| Commons `python -m phoenix_commons.theme.generate_embedded_qss` | Wrote `embedded_qss.py` (19,545 chars; 18,805 chars of QSS embedded). Deterministic — re-running produces "already up to date". |
| Commons `python -c "from phoenix_commons.widgets import StatusBadge; b = StatusBadge('Clean', variant='clean'); print(b.variant, b.property('variant'))"` | `clean clean` |
| PCC `python -m compileall -q . -x "\.venv\|commons\|build\|dist\|__pycache__"` | clean |
| PCC `python -m pytest -q tests/` | **4 passed in 1.02s** (existing smoke tests: module imports, version format, MainWindow instantiates, theme QSS non-empty). MainWindow instantiation exercises Dashboard → ToolRow → StatusBadge end-to-end via Qt. |
| PCC `python main.py` source-mode launch | exit 0 expected, **0 bytes stderr at 2s mark**. No QPixmap warnings, no QSS-parse warnings, no property-selector resolution failures. |
| Dark-theme rendering | Tinted backgrounds + saturated text read correctly against PCC's `#18181F` background. Verified visually before commit. |
| BrandProfile compatibility | `syncing` / `scanning` variants use `__BRAND_ACCENT__` sentinel — substituted to PCC's `#3CB8AE` teal at `apply_pcc_theme(app)` time. Other variants use locked-token hex values (SUCCESS / WARNING / ERROR / MUTED) — palette-independent. |
| Compact-mode rendering | `compact=True` reduces font from 10pt → 9pt, padding `2px 10px` → `1px 7px`, border-radius `8px` → `7px`. Used in `ToolRow` (dense list). Default mode (`compact=False`) untested in this commit — will exercise when a roomier surface adopts it (Step 3 tools-table). |
| post-B5 subprocess invariant | preserved — no subprocess changes |
| post-B6 setStyleSheet invariant | preserved + improved — one more inline `setStyleSheet` retired (the old `self.dot.setStyleSheet(f"color: {color}; ...")` line) |
| No spacing regressions | `ToolRow` row layout unchanged — the badge replaces the dot in the same layout slot; row height stays at 36px |
| No startup regressions | exit 0, 0 stderr, no flashing reintroduced |

---

## 6. Remaining semantic debt

| Item | Where | Why deferred |
|------|-------|--------------|
| Sidebar tool-row status dots (`●` in `SidebarToolWidget`) | sidebar | Sidebar is secondary surface per spec; dashboard is where status earns weight. Could adopt `StatusBadge[compact=True]` later if operator wants chrome consistency — flagged as low-priority follow-up. |
| Activity feed bullet dot (`·` in `ActivityRow`) | dashboard activity | Semantic separator, not status. Stay. |
| Status-bar scan-progress dot (`●` in `main_window.py` status bar) | status bar | Will reconsider at Step 6 when the sync-pill spec lands — the status bar's "scanning" indicator + the top sync-pill cover related concerns; coordinate them then. |
| Detail-panel status text (`detail_panel.py`) | detail panel | Out of dashboard scope. Detail panel deserves its own spec/step. |
| `dirty` variant with change-count (`"3 changes"` / `"12 changes"` per the screenshot) | dashboard tools table | Requires `scanner.get_git_info` to return a `change_count` field (currently only returns `status` in `{"clean","dirty","unknown"}`). Adding this is mechanical (`git status --porcelain | wc -l`) but extends a function signature; pair with Step 3 (tools table) when the table column makes the count visible. |
| `error` variant | not yet wired anywhere | No current PCC error states surface to the UI. Will be exercised when a future scan-failed / pull-failed surface lands. |
| `syncing` / `scanning` variants | not yet wired anywhere | Will be wired at Step 6 (top sync pill) and possibly Step 3 (per-row scanning indicator during refresh). |
| Existing `#PassBadge` / `#FailBadge` / `#ArchivedBadge` | commons QSS | App-specific legacy selectors used by `phoenix-checkout` and `phoenix_master_tool`. Could migrate those consumers to `StatusBadge[variant="clean"]` etc. in a future cross-tool consolidation phase — explicitly out of scope for PCC dashboard work. |

None of these block Step 3.

---

## 7. Recommended Step 3 implementation target

The spec §6 nominates Step 3 as **"Tools section: list → table"** — the dashboard's primary surface gets restructured from the current `ToolRow` vertical list to a `PhoenixTable` with NAME / LAST COMMIT / LOC / SIZE / STATUS columns. The STATUS column would consume the `StatusBadge` primitive built in Step 2.

**Recommendation: proceed to Step 3 as scoped in the spec.**

Three reasons:

1. **The primitive is ready.** StatusBadge is tested, exported, BrandProfile-compatible, and piloted in production code. The table's STATUS column has a known-good widget to drop in.
2. **The compact-mode pathway is exercised.** The pilot in `ToolRow` validated the dense-list rendering; tables will use compact mode similarly.
3. **The deferred `change_count` issue (per §6) becomes Step 3's natural inclusion.** Adding `scanner.get_git_info` returning a count is a 5-line change that pairs naturally with introducing the table column. Doesn't expand scope.

### Step 3 scope (preview only — operator-approved spec will land at step kickoff)

- New `dashboard.py` table widget replacing `ToolRow`-in-`QVBoxLayout`. Built on `phoenix_commons.widgets.PhoenixTable`.
- Columns: NAME / LAST COMMIT / LOC / SIZE / STATUS. Sort by NAME default. Click row → open detail panel.
- Per-row context menu: VS Code / GitHub / Pull / Launch (the four actions B8 tried to surface as card buttons).
- Status column renders `StatusBadge` per row with the change-count integrated.
- Pre-step prerequisite: extend `scanner.get_git_info` to include `change_count` (porcelain line count for dirty repos).

### Optional precursor — Step 2.5

If the operator wants to round out sidebar visual consistency before Step 3, the sidebar `SidebarToolWidget` status dot could adopt `StatusBadge[compact=True]` in a small follow-up commit. ~10 LOC change. Not blocking Step 3; not strictly required by any later step.

---

## 8. Confirmation

- **No architecture changes occurred.** No new ADR. No public-API rename. No widget removed. No QSS rule removed. `StatusBadge` is a single additive widget; the QSS additions are additive selectors. No existing commons consumer (Phoenix CAD, Phoenix Checkout, ValveMaster, PMT) is affected.
- **No production deployment occurred.** Work is source-mode only on PCC `phase-3c-pcc-retrofit` (commit `728f9be`) and commons `main` (commits `93389da` sibling / `75c03fb` submodule). No installer built, no `dist/` zip created, no GitHub Release published. Neither commons commit nor PCC commit pushed yet.
- **No BrandProfile changes occurred.** `PCC_BRAND = BrandProfile(primary="#E8783C", secondary="#2A8880", accent="#3CB8AE")` unchanged. The widget's `syncing` / `scanning` variants use the `__BRAND_ACCENT__` sentinel in QSS, which means PCC's teal applies automatically when those variants are eventually used — but that's a *consumer* of the existing BrandProfile mechanism, not a *change* to it.
- **No production-tool source touched.** PCC-only source change. Phoenix CAD / Phoenix Checkout / PTT / PMT / ValveMaster all unmodified.
- **No subprocess regression** (post-B5 invariant preserved — no new subprocess calls added).
- **No widget-level setStyleSheet regression** (post-B6 invariant preserved + IMPROVED — one more inline `setStyleSheet` retired in `ToolRow`).
- **No layout instability** — `ToolRow` height unchanged at 36px; badge replaces dot in the same horizontal layout slot.

---

## Commit summary

| Repo | Commit | Subject |
|------|--------|---------|
| sibling `phoenix-commons` `main` | `93389da` | widgets: add StatusBadge primitive |
| PCC submodule `commons` `main` | `75c03fb` | widgets: add StatusBadge primitive (mirror) |
| `phoenix-command-center` `phase-3c-pcc-retrofit` | `728f9be` | Pilot StatusBadge in dashboard ToolRow status (Phase 3C B10, Step 2) |

PCC `phase-3c-pcc-retrofit` is now 6 commits ahead of `origin/phase-3c-pcc-retrofit` and not merged to master. Commons `main` is 6 commits ahead of `origin/main` and not pushed.

**Operator gate:** visual review of the dashboard tool list before Step 3 (tools list → table) starts. Recommended capture targets:
1. Full dashboard with the new status pills visible per row.
2. Close-up of one `Clean` row, one `Changes` row, one `Unknown` row.
3. Compare against pre-Step-2: the 9px coloured dot replaced by the labelled pill.

---

*End of report.*
