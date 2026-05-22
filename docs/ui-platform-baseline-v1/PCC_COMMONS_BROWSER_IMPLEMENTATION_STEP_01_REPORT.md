# PCC Commons Browser Implementation — Step 1 Report

> **Status:** complete (PCC commit on retrofit branch, pending operator
> review + push).
> **Date:** 2026-05-22.
> **Branch:** `phase-3e-pcc-commons-browser-retrofit` (PCC).
> **Scope:** Summary chip row modernization — local `_Chip(QLabel)`
> class retired in favour of `phoenix_commons.widgets.StatusBadge`.
> Per `PCC_COMMONS_BROWSER_SURFACE_SPEC_V1` §3.2 + §7 step 1.
> **Operator gate:** visual review before Step 2 (UsageFooter
> modernization) starts.

---

## 1. Summary-row audit findings

### Pre-Step-1 (legacy)

The summary chip row in `commons_browser.py:24-36` carried a local
20-LOC `_Chip(QLabel)` class:

```python
class _Chip(QLabel):
    def __init__(self, text: str, color: str, parent=None):
        super().__init__(text, parent)
        self.setStyleSheet(f"""
            color: {color};
            background: {C['surface']};
            border: 1px solid {C['border']};
            border-radius: 14px;
            padding: 4px 12px;
            font-size: 11px;
            font-weight: 700;
        """)
```

Construction (lines 141-147):

```python
self.chip_files = _Chip("— files",       C["text"])
self.chip_refs  = _Chip("— referenced",  C["teal"])
self.chip_orph  = _Chip("— orphans",     C["warning"])
self.chip_size  = _Chip("—",             C["text_sub"])
```

Update flow (`set_usage()`, lines 210-213):

```python
self.chip_files.setText(f"{total_files} files")
self.chip_refs.setText(f"{refed} referenced")
self.chip_orph.setText(f"{orphans} orphans")
self.chip_size.setText(format_size(total_size))
```

Reset flow (`_set_empty_state()`, lines 237-240):

```python
self.chip_files.setText("— files")
self.chip_refs.setText("— referenced")
self.chip_orph.setText("— orphans")
self.chip_size.setText("—")
```

### Documented problems

  - **Bespoke local class** — `_Chip` duplicates StatusBadge's role
    (coloured pill conveying a state) without participating in the
    7-variant semantic system the rest of PCC uses post-Phase-3C.
  - **Static colour-by-construction** — the colour of each chip is
    fixed at construction time (`C["teal"]` for referenced,
    `C["warning"]` for orphans). The pill doesn't reflect *state* —
    e.g. an "orphans" chip with `0 orphans` still renders amber
    (`C["warning"]`), which reads visually as "warning" when it
    should read "clean / all healthy."
  - **Inline `setStyleSheet`** on a local widget — generates one of
    the 12 inline-stylesheet call sites in this file. The B6
    invariant prefers commons primitives + property-selector QSS over
    inline styles.
  - **No variant flips on count changes** — orphans badge is
    visually identical at `0 orphans` and `10 orphans`. Operator
    cannot see "all healthy" vs "needs attention" at a glance.

### Workflow preservation requirement

Pre-Step-1 the summary chip row surfaced:
  1. Initial state (no scan yet) — all four chips show "—" placeholders
  2. After `set_usage(usage)` — counts populated from scanner output
  3. After `_set_empty_state(msg)` — all four chips reset to placeholders
  4. During `set_scanning(True)` — status sub-label shows "Scanning…"; chips unchanged until scan completes
  5. Total size formatted via `format_size()` (e.g. "6.5 KB")

**Step 1 preserves all 5 workflows.** All `set_usage` / `_set_empty_state` / `set_scanning` / scanner integration / `format_size` calls are intact — only the chip widget primitive changes underneath.

---

## 2. `_Chip` replacement details

### Migration

| Chip | Pre-Step-1 | Post-Step-1 |
|------|------------|-------------|
| files | `_Chip("— files", C["text"])` — bespoke pill with `C["text"]` colour | `StatusBadge("— files", variant="unknown", compact=True)` |
| referenced | `_Chip("— referenced", C["teal"])` — fixed teal | `StatusBadge("— referenced", variant="unknown", compact=True)` initial; flips to `clean` on first scan |
| orphans | `_Chip("— orphans", C["warning"])` — fixed amber | `StatusBadge("— orphans", variant="unknown", compact=True)` initial; flips to `dirty` if >0 or `clean` if 0 on first scan |
| size | `_Chip("—", C["text_sub"])` — fixed muted | `StatusBadge("—", variant="unknown", compact=True)` |

`compact=True` matches the convention from Phase 3D's sync-card badge
trio + TodoItem state pills — keeps the row dense and secondary.

### Helper retirement

`_Chip` class itself is retired (20 LOC removed). Replaced by a
comment block:

```python
# Phase 3E Step 1: the legacy `_Chip(QLabel)` class formerly defined here
# retired in favour of the shared `StatusBadge` primitive (imported
# from phoenix_commons.widgets). Four header chips (files / referenced
# / orphans / total size) now use the same 7-variant semantic system
# the dashboard + detail panel use; per-chip variant flips happen in
# `set_usage()` below.
```

Net: ~14 LOC retired (20 LOC class - 6 LOC comment replacement).

### Import diff

Added one import:

```python
from phoenix_commons.widgets import StatusBadge
```

No imports removed (the file still uses `QLabel`, `QFrame`, etc. in
the `UsageFooter` class, which Step 2 will modernize).

---

## 3. StatusBadge variant mapping

Per `PCC_COMMONS_BROWSER_SURFACE_SPEC_V1` §3.2:

| State | files | referenced | orphans | size |
|-------|-------|------------|---------|------|
| **Initial** (no commons path / no scan) | `unknown` "— files" | `unknown` "— referenced" | `unknown` "— orphans" | `unknown` "—" |
| **Scanned, with orphans** | `unknown` "N files" | `clean` "N referenced" | `dirty` "N orphans" | `unknown` "X KB" |
| **Scanned, no orphans** | `unknown` "N files" | `clean` "N referenced" | `clean` "0 orphans" | `unknown` "X KB" |
| **Empty state** (path missing/invalid) | `unknown` "— files" | `unknown` "— referenced" | `unknown` "— orphans" | `unknown` "—" |

Rationale:
  - **files + size** stay `unknown` always — these are reference counts, not state signals. They convey magnitude, not health. The muted slate visual reads as "informational" rather than "good" or "bad."
  - **referenced** is always `clean` post-scan — referenced files are the positive metric. Always green = "this is the healthy population."
  - **orphans** is the only dynamic-variant chip — `dirty` (amber) when >0, `clean` (green) when 0. Lets the operator see "all healthy" vs "needs cleanup" at a glance.

No new StatusBadge variants introduced. The 7 existing variants
(`clean` / `dirty` / `error` / `warning` / `unknown` / `scanning` /
`syncing`) cover this surface; Step 1 only uses three (`unknown` /
`clean` / `dirty`).

---

## 4. Data-contract preservation

### Usage dictionary shape — unchanged

`scanner.scan_commons_usage(commons_path, tools)` returns:

```python
{
    rel_path_in_commons: {
        "size":  int,
        "users": [tool_name, ...],
    },
    ...
}
```

`CommonsBrowser.set_usage(usage)` consumes that shape. **Untouched
by Step 1.** Aggregation formulas inside `set_usage()` are
byte-identical:

```python
total_files = len(self._usage)
refed       = sum(1 for v in self._usage.values() if v.get("users"))
orphans     = total_files - refed
total_size  = sum(v.get("size", 0) for v in self._usage.values())
```

Only the four lines *after* the aggregation changed (the
`setText(...)` → `set_status(...)` migration).

### Public API — unchanged

| Symbol | Pre-Step-1 signature | Post-Step-1 signature |
|--------|----------------------|------------------------|
| `CommonsBrowser.set_commons_path(path)` | unchanged | unchanged |
| `CommonsBrowser.set_scanning(scanning)` | unchanged | unchanged |
| `CommonsBrowser.set_usage(usage)` | unchanged | unchanged |
| `CommonsBrowser.refresh_requested` signal | unchanged | unchanged |
| `CommonsBrowser._on_tree_clicked(index)` | unchanged | unchanged |

`main_window.py` integration untouched (lines 197, 258, 369-378, 394
all continue calling identical methods).

### FileViewer + scanner — unchanged

  - `file_viewer.py` not touched.
  - `scanner.py` not touched.
  - `theme.py` not touched (StatusBadge chrome flows from the commons
    canonical QSS via sentinel substitution; no PCC overlay needed
    for this step).

---

## 5. Empty / error / scanning state behavior

| State | Trigger | Pre-Step-1 visual | Post-Step-1 visual |
|-------|---------|--------------------|--------------------|
| Initial, no path | first show | "— files" "— referenced" "— orphans" "—" in mixed inline colours | 4× StatusBadge `unknown` (muted slate) with "—" texts |
| Scanned, healthy + orphans | `set_usage()` returns mixed users | "N files" (white text) "N referenced" (teal) "N orphans" (always amber, regardless of count) "X KB" (muted) | "N files" `unknown` "N referenced" `clean` (green) "N orphans" `dirty` (amber) "X KB" `unknown` |
| Scanned, no orphans | `set_usage()` returns all-used | identical to above — "0 orphans" still amber | "0 orphans" `clean` (green) — *new flip* communicating "all healthy" |
| Scanning in progress | `set_scanning(True)` | status sub-label "Scanning…" + Rescan disabled; chips unchanged | identical — chip values held until scan completes |
| Invalid path | `_set_empty_state(msg)` | 4× chips reset to "—" placeholders in original mixed colours | 4× chips reset to `unknown` variant + "—" texts (uniform muted) |

**Behavioural deltas:** zero. Visual deltas: chips now have proper
semantic colour state. Specifically: the orphans chip now visibly
reads "all healthy" (green) when no orphans exist, which the prior
fixed-amber pill could not.

The Rescan button + status sub-label flow is unchanged. Tree, viewer,
UsageFooter all unchanged.

---

## 6. Validation results

| Check | Result |
|-------|--------|
| PCC `python -m compileall -q . -x "\.venv\|commons\|build\|dist\|__pycache__"` | ✓ clean (exit 0) |
| PCC `python -m pytest -q tests/` | ✓ **4 passed in 0.52s** |
| Offscreen smoke — initial state | ✓ All 4 chips are `StatusBadge` instances in `unknown` variant |
| Offscreen smoke — `set_usage(healthy + 1 orphan)` | ✓ files `unknown` / referenced `clean` / orphans `dirty` / size `unknown` |
| Offscreen smoke — `set_usage(no orphans)` | ✓ orphans variant flipped `clean` |
| Offscreen smoke — `_set_empty_state` | ✓ all 4 chips reset to `unknown` + "—" texts |
| Offscreen smoke — `_Chip` class removed | ✓ `hasattr(commons_browser, '_Chip')` is False |
| `set_usage` aggregation logic | ✓ unchanged (byte-identical) |
| `_set_empty_state` reset logic | ✓ unchanged (only chip API calls changed) |
| `set_scanning` flow | ✓ unchanged |
| Refresh button + Lucide refresh icon | ✓ unchanged (Phase 3C Step 1 already migrated) |
| `refresh_requested` signal contract | ✓ unchanged |
| `main_window.py` integration | ✓ no caller-side changes needed |
| `scanner.scan_commons_usage` integration | ✓ no scanner-side changes needed |
| FileViewer + tree + UsageFooter | ✓ untouched (Step 2/3/4 scope) |
| B5 invariant (subprocess CREATE_NO_WINDOW) | ✓ preserved (no subprocess calls touched) |
| B6 invariant (no widget-level setStyleSheet on commons primitives) | ✓ preserved — `_Chip`'s inline stylesheet retired; StatusBadge chrome flows from commons canonical QSS |
| BrandProfile invariant | ✓ untouched. StatusBadge variants resolve to commons semantic palette (clean=success-green / dirty=warning-amber / unknown=muted-slate) — brand-independent |
| Theme.py | ✓ untouched (no new QSS rules required) |
| Diff scope | 1 file (`commons_browser.py`); +43 / −27 |

---

## 7. Remaining Commons Browser debt

Per spec §7 sequencing:

| # | Step | Status |
|---|------|--------|
| 1 | **Summary chip row modernization — `_Chip` → `StatusBadge`** | ✅ **done (this step)** |
| 2 | UsageFooter modernization — Panel wrap + per-tool StatusBadge + Lucide icons | pending (recommended next) |
| 3 | Tree / viewer / page cohesion pass — splitter inline-QSS cleanup + Rescan tier migration | pending |
| 4 | Validation + merge gate (closure mirror of Phase 3D) | pending |

### Cosmetic debt remaining in this surface

  - **UsageFooter** still carries inline-styled QFrame card chrome + `◇`/`◈` emoji glyph chips (lines 41-99). The single most operator-visible chrome win pending — addressed in Step 2.
  - **Inline `QSplitter::handle` setStyleSheet** at line 153 — redundant with PCC theme.py overlay (same fix Phase 3D's post-merge cleanup landed on the detail panel). Addressed in Step 3.
  - **Rescan button** is still a raw `QPushButton#ghostBtn` (line 130). Could migrate to commons `SecondaryButton` or `TertiaryButton` in Step 3 (operator picks tier).

### What's intentionally NOT cleaned up (yet)

  - **`UsageFooter` class structure** — out of Step 1 scope. Will be modernized end-to-end in Step 2.
  - **`status_lbl` inline stylesheet** at line 125 — calm semantic content text, not chrome. Will be evaluated in Step 3 (likely B6 carve-out — semantic content, not chrome).
  - **`QCursor` import** at line 15 — currently unused (the Rescan button uses `QCursor(Qt.PointingHandCursor)` at line 133, so it IS used). Keep.

---

## 8. Recommended Step 2 target

**Step 2 — UsageFooter modernization.** Per spec §7.

Sub-steps:
  1. Wrap `UsageFooter` body in a `Panel` container (replaces inline-styled QFrame chrome at line 43-45).
  2. Replace the "USED BY" hand-styled QLabel with a `#sectionHeader` QLabel (lines 53-57) — matches the chip-row + detail-panel convention.
  3. Replace per-tool `◈`-prefixed inline-styled QLabels with `StatusBadge(variant="clean")` pills + leading Lucide `package` icon.
  4. Replace orphan `◇`-prefixed inline-styled QLabel with `StatusBadge(variant="warning")` + leading Lucide `warning` icon.
  5. Keep the placeholder italic muted QLabel as-is (semantic informational text, not chrome).

Estimated scope: medium (~50 LOC delta). No commons additions required —
`package` and `warning` icons already in `ICON_NAMES`.

After Step 2, the Commons Browser's two most operator-visible surfaces
(summary chip row + usage footer) are both on the Phase 3C/3D
vocabulary. Step 3 closes out the splitter + Rescan tier cleanup;
Step 4 closes the phase.

---

## 9. Confirmation

  - **No architecture changes occurred.** No new ADR. No commons API change. No new commons widget. `BrandProfile` unchanged. ADR-014 / ADR-015 / ADR-016 all hold. `StatusBadge` was already part of the commons public API since Phase 3C Step 2.
  - **No BrandProfile changes occurred.** PCC `BrandProfile` (orange + teal) unchanged. StatusBadge variants resolve to commons brand-independent semantic colours (success-green / warning-amber / error-red / muted-slate). PCC's orange + teal accent palette continues to drive `PrimaryButton`/`SecondaryButton`/accent surfaces.
  - **No production deployment occurred.** Source-mode only on `phase-3e-pcc-commons-browser-retrofit` branch. PCC is unpackaged. No installer built. No `dist/` artifact. No GitHub Release. Step 1 commit not yet pushed to PCC origin (operator-gated).
  - **No search backend work occurred.** Search backend remains a deferred Phase 3F+ candidate per the candidate audit report.
  - **No Wave 8a work occurred.** Wave 8a remains operator-gated (cooldown floor 2026-06-02).
  - **No production tool source touched.** Phoenix CAD / Phoenix Checkout / PTT / ValveMaster all unmodified.
  - **No Settings / Wizard / About work occurred.** Each remains a separate deferred candidate.
  - **No UsageFooter / tree / FileViewer / scanner work occurred.** Step 1 scope was the summary chip row only.

---

## Commit summary

| Repo | Commit | Subject | Pushed |
|------|--------|---------|--------|
| `phoenix-command-center` `phase-3e-pcc-commons-browser-retrofit` | `d0434b3` | Commons Browser summary chip row — _Chip → StatusBadge (Phase 3E Step 1) | pending (operator-gated) |
| `phoenix-commons` `main` | (this report, pending) | Add PCC_COMMONS_BROWSER_IMPLEMENTATION_STEP_01_REPORT | pending |

PCC retrofit branch tip after Step 1: `d0434b3` (1 commit ahead of
`160270c` = post-Phase-3D CI-fix tip on `main`).

No commons source change in Step 1 — only this report file is added.

---

*End of report. Phase 3E Step 1 = the first of 4 sequenced steps on
the spec. Operator gate before Step 2 (UsageFooter modernization)
opens.*
