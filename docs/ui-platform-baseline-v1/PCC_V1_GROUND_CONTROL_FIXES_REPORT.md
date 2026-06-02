# PCC v1 — Ground Control Small-Fixes Report

> **Status:** ✅ COMPLETE — all 7 v1 small fixes implemented, validated, committed.
> **Date:** 2026-06-02.
> **Repo:** `phoenix-command-center` · branch `pcc-v1-ground-control-fixes`.
> **Scope:** PART 1 of the approved PCC v1 plan — the small blocker/fix set
> only. **TODO Workbench was NOT implemented** (PART 2, dedicated V1-T steps,
> per the operator's sequencing decision).

---

## 1. Mandate

Operator-approved PCC v1 scope finalization. PART 1 = 7 small fixes, to be
completed **before** the TODO Workbench. Strict carve-outs honoured:

- Do **not** implement TODO Workbench yet.
- Do **not** redesign the dashboard or detail panel.
- Do **not** change scanner contracts.
- Do **not** change commons architecture.
- Do **not** publish releases, upload assets, or create final tags.

STOP conditions (none triggered — see §6):

- Updater contract becomes ambiguous.
- Refresh rediscovery requires a scanner rewrite.
- Installed-launch mapping turns into a broad registry design.
- Source-mode launch fails.
- Validation fails.

---

## 2. The seven fixes

| # | Fix | File(s) | Outcome |
|---|-----|---------|---------|
| 1 | Version policy → **v1.0.0** | `version.py` | `APP_VERSION` `2.0.0` → `1.0.0`; `APP_BUILD` reworded to Ground Control v1 |
| 2 | Updater UI (Help → Check for Updates + `UpdateBanner`) | `main_window.py` | Manual + silent-startup check; banner in status bar; install gated to frozen builds; contract preserved |
| 3 | Refresh All re-discovers | `main_window.py` | `_refresh_all` now routes through `_load_tools` → `scanner.discover_tools` |
| 4 | Installed-launch mappings | `detail_panel.py` | VM corrected, Screenshot Tool added, 3 verified-unchanged, fallback preserved |
| 5 | Search / Ctrl+K menu item | `main_window.py` | `Tools → Search Tools` (Ctrl+K) surfaced with a search icon |
| 6 | Repo hygiene | `.gitignore` | `.venv*/` glob added |
| 7 | Docs | `CLAUDE.md`, `README.md`, `CHANGELOG.md` | Reframed source-run hub → packaged Ground Control app; v1.0.0 RC |

7 files changed, +352 / −90.

---

### Fix 1 — Version policy (v1.0.0)

`version.py`:

```python
APP_VERSION = "1.0.0"   # was "2.0.0"
APP_BUILD   = "v1 — Ground Control: fleet dashboard, drill-down detail, "
              "installed/source launch, auto-updater"
```

The prior `2.0.0` / `pcc-phase-v2.x` numbers are treated as **forensic phase
markers**, not published releases. v1.0.0 is the first public Ground Control
release. No tags were created or moved (out of scope). The `CHANGELOG`
versioning note records the reset so the history reads cleanly.

### Fix 2 — Updater UI

Wired PCC's **existing** standalone `updater.py` (not the commons facade — PCC's
updater keeps module-level constants) into the GUI:

- **`Help → Check for Updates…`** (manual) — runs a background check and reports
  either way: status-bar banner if an update exists, an info dialog ("you're up
  to date") if not.
- **Silent startup check** — `QTimer.singleShot(2000, …)` after window build.
  Surfaces the banner only when a newer release exists; no-update / network
  errors stay quiet. The 2 s defer means it never fires during a short-lived
  smoke test (the event loop isn't spun that long), keeping CI deterministic.
- **`_UpdateCheckThread(QThread)`** — runs `updater.check_for_update(APP_VERSION)`
  off the GUI thread; any exception collapses to `None`, so nothing propagates
  into the event loop.
- **`UpdateBanner`** (from `phoenix_commons.widgets`) — mounted as a permanent
  status-bar widget per the commons banner contract. A small **inline
  stylesheet** (PCC `C` tokens) keeps it legible, since PCC's chrome doesn't
  ship the commons `#UpdateBanner` QSS.
- **Install gate** — the banner's *Install & Restart* calls
  `updater.download_and_apply(info)` **only when `paths.is_frozen()`**. In source
  mode it shows a "pull the latest from git" dialog instead — because PCC's
  `download_and_apply` derives the install dir from `sys.executable`, which in
  source mode is the Python interpreter, not the app.

**Contract preserved end-to-end** (`updater.py` untouched): `PhoenixCommandCenter.zip`
asset, full-folder payload, `expected_internal=True`, `PhoenixCommandCenter.exe`
— all defaults of the existing `check_for_update` / `download_and_apply`. **No
release-history dialog** was added (the banner's built-in single-release "Release
Notes" button is part of the commons primitive, not a history view).

### Fix 3 — Refresh All re-discovers

Before, `_refresh_all` re-scanned only the *known* tool set. Now:

```python
def _refresh_all(self):
    if self._scan_worker and self._scan_worker.isRunning():
        return
    self._load_tools()
```

`_load_tools` is the same discovery path startup and Settings-save already use —
it re-runs `scanner.discover_tools(root)`, rebuilds the sidebar/dashboard, rewires
commons, and kicks the scan. So repos added/removed under the root since the last
load now appear/disappear. The running-scan guard prevents a double-trigger from
rebuilding the surface out from under an in-flight `ScanWorker`. **No scanner
contract change** (STOP condition avoided).

### Fix 4 — Installed-launch mappings

`detail_panel.INSTALLED_APP_RELPATHS` is keyed by the discovered **repo-folder
name** → relpath under `%LOCALAPPDATA%\ATS Inc\`. Every value was re-verified
against the tool's own `installer.iss` (`DefaultDirName` tail + `MyAppExeName`):

| Repo folder (key) | Relpath (value) | Change | Source of truth |
|---|---|---|---|
| `Job Tracker` | `Project Tracking Tool\ProjectTrackingTool.exe` | unchanged ✓ | JT `installer.iss` |
| `Phoenix_CAD_Tool` | `Lab Layout Tool\LabLayoutTool.exe` | unchanged ✓ | CAD `installer.iss` |
| `Phoenix-Checkout-Tool` | `Phoenix Valve Checkout Tool\PhoenixCheckoutTool.exe` | unchanged ✓ | Checkout `installer.iss` |
| `ValveMasterTool` | `PhoenixMasterTool\PhoenixMasterTool.exe` | **corrected** | VM `installer.iss` (`MyAppName="PhoenixMasterTool"`) |
| `Screenshot_Tool` | `Screenshot Tool\ScreenshotTool.exe` | **added** | Screenshot `installer.iss` |

The stale VM entry was `ValveMasterTool\ValveMasterTool.exe` — **both** the
install dir and the exe were wrong; the installer's `DefaultDirName` is
`…\ATS Inc\PhoenixMasterTool` and the exe is `PhoenixMasterTool.exe`. The
source/open-folder **fallback is preserved**: `_resolve_installed_exe` returns
`None` for unmapped repos (button disables with an explanatory tooltip) and for
mapped-but-not-installed exes. This stayed a **static, verified dict** — no
registry scan (STOP condition avoided). PCC-self is intentionally not mapped.

### Fix 5 — Search / Ctrl+K menu item

The `Ctrl+K` focus-search `QAction` already existed but wasn't in any menu. It's
now `Tools → Search Tools` (relabelled from "Focus Search", search icon added),
sitting under Commons Browser. The stale "not surfaced in menus" comment was
corrected. **No TODO Workbench menu entry was added** — that belongs to PART 2.

### Fix 6 — Repo hygiene

`.gitignore` gains `.venv*/` alongside the existing `.venv/` / `venv/` / `env/`,
catching version-suffixed build envs (`.venv312/`, `.venv314/`) created under the
ADR-014 pinned-interpreter build flow.

### Fix 7 — Docs

- **`CLAUDE.md`** — reframed from "source-run only … not a shipping tool (no
  installer, no auto-updater)" to a **packaged Ground Control app** with a
  Packaging (v1.0.0) table, a Commons-integration section that matches the actual
  code (`apply_pcc_theme` = `apply_dark_theme` + `BrandProfile` + local overlay
  per ADR-016), and an expanded "Do NOT change casually" table (updater contract,
  installer AppId, `INSTALLED_APP_RELPATHS`). Removed the stale "no `updater.py`
  to retrofit" / "not yet retrofitted" claims the code already contradicted.
- **`README.md`** — Ground Control intro; `py -3.14` → `py -3.12` (ADR-014) +
  `--recurse-submodules`; new "Self-update" feature bullet; `Ctrl+K` row in the
  shortcuts table; the "installer blocked" banner reframed to a v1.0.0 RC +
  honest S1/AV frozen-build caveat (no false claim that a build shipped).
- **`CHANGELOG.md`** — single canonical `[1.0.0] — 2026-06-02 (release
  candidate)` section consolidating the Ground Control surface + the 7 fixes; a
  versioning note explaining the `2.0.0 → 1.0.0` reset; prior `2.0.0` / `1.0.0`
  history relabelled under "Pre-release development history (internal phase
  milestones)" so there is exactly one release-version `[1.0.0]`.

---

## 3. Files changed

```
 .gitignore      |   3 +
 CHANGELOG.md    |  95 +++++++---
 CLAUDE.md       |  85 +++++---
 README.md       |  40 ++--
 detail_panel.py |  25 +-
 main_window.py  | 190 ++++++++++++++++-
 version.py      |   4 +-
 7 files changed, 352 insertions(+), 90 deletions(-)
```

No source outside this set was touched. No `updater.py`, `scanner.py`,
`installer.iss`, `build.bat`, `requirements*`, commons submodule, tags, or
releases changed.

---

## 4. Validation

All run with the canonical Python 3.12 venv, `QT_QPA_PLATFORM=offscreen`.

| Check | Result |
|-------|--------|
| `py_compile` (edited files) | ✅ OK |
| `compileall` (repo, excl. venv/commons/build/dist) | ✅ OK |
| `pytest -q tests/` | ✅ **4 passed** in 0.44s |
| MainWindow constructs offscreen (≈ source-mode launch) | ✅ no raise |
| `Tools → Search Tools` present, shortcut `Ctrl+K` | ✅ |
| `Help → Check for Updates…` present | ✅ |
| Updater methods present; banner starts `None` | ✅ |
| `UpdateBanner` imports + constructs | ✅ |
| `INSTALLED_APP_RELPATHS` — 5 entries, VM + Screenshot correct, 3 unchanged | ✅ |
| `_resolve_installed_exe` graceful for unknown + missing exe (no raise) | ✅ |
| Refresh All re-runs `discover_tools` (monkeypatched proof) | ✅ |
| `is_frozen()` False in source mode (install-gate works) | ✅ |
| Change surface = the 7 intended files only (no build/venv bloat) | ✅ |

The `test_app_version` smoke test (strict `X.Y.Z`) confirms `1.0.0` is
well-formed for `build.bat` / `installer.iss` / `updater.py` consumers.

---

## 5. What was explicitly NOT done

- **TODO Workbench** — PART 2. To be implemented as dedicated V1-T steps
  (`todo_state.py` + `todo_id`, `todo_verify.py`, `todo_workbench.py` read-only
  Ctrl+3 view, non-mutating actions, safe markdown-checkbox toggle, integration,
  validate) per `PCC_TODO_WORKBENCH_MVP_SPEC.md` — A1 full MVP, Ctrl+3 top-level
  view + menu entry, manual clear only.
- Dashboard / detail-panel redesign.
- Scanner contract changes.
- Commons changes.
- Release publish / asset upload / final tags.

---

## 6. STOP conditions — none triggered

| Condition | Status |
|-----------|--------|
| Updater contract ambiguous | ❌ not hit — contract is explicit in `updater.py` constants; preserved verbatim |
| Refresh rediscovery needs scanner rewrite | ❌ not hit — reused existing `discover_tools` / `_load_tools` |
| Installed-launch mapping → broad registry | ❌ not hit — stayed a static, installer-verified dict |
| Source-mode launch fails | ❌ not hit — constructs clean; install action gated to frozen |
| Validation fails | ❌ not hit — all checks green |

---

## 7. Next steps

1. **Operator review** of these 7 fixes (especially the updater UX and the
   corrected install mappings).
2. On approval → **PART 2: TODO Workbench** (V1-T1…V1-T7).
3. Then → **v1.0.0 RC build** → operator validation → stable release.

Branch `pcc-v1-ground-control-fixes` is pushed; **not** merged (awaiting review).
