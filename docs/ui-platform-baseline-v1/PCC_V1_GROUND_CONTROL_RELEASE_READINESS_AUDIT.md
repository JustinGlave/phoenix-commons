# Phoenix Command Center — v1 "Ground Control" Release Readiness Audit

> **Status:** audit / planning only. No implementation, no build, no publish.
> **Date:** 2026-06-02.
> **Repo:** `JustinGlave/phoenix_command_center` (local `phoenix-command-center`), `main` @ `3a13eed`.
> **Verdict:** **B — ready for v1 RC after small fixes** (details § 13).

---

## 1. Product intent confirmation

PCC is re-scoped from "source-run hub" to the **v1 Ground Control / command center for the Phoenix tool family**, a packaged + installed + self-updating app on the same footing as the 4 shipped production tools. It must: track all apps under the operator-configured root, give a bird's-eye dashboard, drill into per-app detail (health/status/update/history), expose family-standard menu-bar functions, follow the same installer/updater/release contract, and serve as the central validator of the standardization protocol.

**Material consequence of the re-scope:** PCC's prior CLAUDE.md framing ("source-run only; not one of the four shipping production tools; no installer, no auto-updater") is now **superseded**. PCC already carries full packaging infrastructure (build.bat, installer.iss, updater.py, version.py) from the Phase-6 template work, so the re-scope is a finish-the-wiring exercise, not a from-scratch build.

---

## 2. Repo state

| Item | State |
|------|-------|
| Branch / HEAD | `main` @ `3a13eed` (Merge Phase 3G — settings dialog) |
| Tracked source | 53 files, **9,695 `.py` LOC** across 23 modules |
| Modernization | Phases 3C–3G complete (dashboard, detail panel, commons browser, search MVP, settings dialog) |
| Packaging files | `build.bat`, `installer.iss`, `updater.py`, `version.py`, `paths.py` — all present |
| commons submodule | present, pinned `768e36d` (heads/main), clean |
| CI | `.github/workflows/ci.yml` — windows-latest, Py3.12, `submodules: recursive` |
| Tests | `tests/conftest.py` + `tests/test_smoke.py` (CI runs `pytest -q tests/`, green) |
| Governance | LICENSE, SECURITY, CODE_OF_CONDUCT, CONTRIBUTING, CHANGELOG, README, CLAUDE.md all present |
| Working tree | clean (only untracked dev `.venv` etc.) |

PCC is the most infrastructure-complete of any pre-release app the platform has audited — it was built on the canonical wizard/template after the FROZEN_BUILD_BASELINE work, so it inherited the hardened build.bat from day one.

---

## 3. App discovery / tracking audit

| Aspect | Finding (evidence) |
|--------|--------------------|
| Mechanism | Directory auto-scan: `scanner.discover_tools(root)` (`scanner.py:336`) iterates the configured root, keeps dirs containing `.git` (`is_git_repo`, `scanner.py:65`) |
| Root config | Settings → "Tools Root Folder" card (`settings_dialog.py:166`), persisted as `root_path` in `pcc_config.json` (`config.py`) |
| First-run | `main_window.py:217` opens Settings if root missing/invalid |
| Non-app filtering | Only `.git` dirs become tools; `.venv`/`__pycache__`/`node_modules`/`dist`/`build` excluded from stat-walks (`scanner.py:262 _SKIP_DIRS`); no name filters |
| Family coverage | All 5 family repos (CAD, Checkout, ValveMaster, Job Tracker, Screenshot Tool) + commons would appear if they sit as git repos at the root |
| Rescan | `_refresh_all` (`main_window.py:398`) → `_start_scan` rescans **stats of the already-discovered list** (`self.tools`) via `ScanWorker` QThread |

**⚠ Gap — Refresh does not re-discover.** `_refresh_all` calls `_start_scan(self.tools)` but **not** `_load_tools()` (which is the only caller of `discover_tools`). `_load_tools` runs at startup (`:221`), settings-save (`:396`), and `:435` — not on Refresh. So a **newly-added app folder under the root will NOT appear on a plain Refresh** — only after a settings-save or app restart. For a product whose stated intent is "track all apps located in the configured root … newly added apps appear after Refresh/scan," this is a genuine v1 gap.

**Classification: needs-small-fix.** Make "Refresh All" re-run discovery (`_load_tools()` then rescan), or add a separate "Rescan for new apps" action. ~10-line change.

---

## 4. Dashboard bird's-eye audit

| Signal | Present? | Evidence |
|--------|----------|----------|
| All apps listed | ✅ | `ToolsTable` (`dashboard.py:121`) one row/app |
| App identity (name + icon) | ✅ | git-branch icon for tools, package icon for commons (`:258`) |
| Last commit (relative) | ✅ | column 2 (`:276`) ← `scanner.get_git_info().last_commit` |
| LOC | ✅ | column 3 (`:284`) |
| Size | ✅ | column 4 (`:290`) |
| Status (clean/dirty/N changes) | ✅ | StatusBadge column 5 (`:297`) |
| Aggregate tiles | ✅ | 5 tiles: Tools / Total LOC / Open TODOs / Total Size / Needs Commit (`:540`) |
| Recent activity feed | ✅ | top-20 commits w/ per-tool color tag (`:985`) |
| Drill-into action | ✅ | row click → `tool_selected` → `_open_detail` (`:322`, `main_window.py:340`) |
| Context menu | ✅ | Open in VS Code / GitHub / Pull / Launch (`:327`) |
| Per-tool TODO / branch / ahead-behind on dashboard | ✗ | only fleet-wide aggregates; per-tool detail lives in the detail panel |

**Classification: sufficient for v1.** The bird's-eye covers identity, recency, size, dirty-state, fleet TODO/commit aggregates, and activity. Per-tool TODO/branch/sync on the dashboard is a nice-to-have, not a v1 requirement (it's all in the detail panel).

---

## 5. Drill-down detail audit

| Aspect | Finding (evidence) |
|--------|--------------------|
| Detail panel | `DetailPanel` (`detail_panel.py:483`), opened via `_open_detail` (stack page 2) |
| Overview tab | SyncStatusCard (ahead/behind/uncommitted) + Recent Commits (`:618`) |
| TODOs tab | open/done/FIXME badges + per-file grouped TodoItem list w/ file:line (`:648`) |
| Files tab | tree + file viewer + CommonsDropZone (`:693`) |
| Git tab | Pull / Push / Fetch + terminal-style output + push-preview dialog (`:711`) |
| Run source | "Run source" button, enabled if source dir exists, subprocess launch (`:558`) |
| Launch installed | "Launch installed", enabled if mapped exe exists (`:563`, `INSTALLED_APP_RELPATHS:44`) |
| Update/history | last-commit tile + recent-commits + sync card unpushed list |

**⚠ Gap — stale installed-app mapping.** `INSTALLED_APP_RELPATHS` (`detail_panel.py:44`) maps `"ValveMasterTool": "ValveMasterTool\ValveMasterTool.exe"` — but the **actual installed exe is `ValveMasterTool\PhoenixMasterTool.exe`** (renamed at v1.1.0; confirmed in `%LOCALAPPDATA%\ATS Inc\`). So "Launch installed" for ValveMaster points at a nonexistent path and silently disables. The mapping also omits Screenshot Tool and PCC-self. The other 3 entries (Job Tracker, CAD, Checkout) are correct.

**Classification: sufficient for v1 with one small fix.** All 4 tabs + dual launch are functional; fix the stale VM exe name (1 line) and optionally extend the map (Screenshot Tool, plus the renamed-exe reality).

---

## 6. Menu bar / app-standard function audit

| Function | PCC state | Classification |
|----------|-----------|----------------|
| File menu (New Tool/Refresh/Settings/Exit) | ✅ `main_window.py:536`; shortcuts Ctrl+N/Ctrl+R/F5/Ctrl+,/Ctrl+Q | aligned |
| Tools menu (Dashboard/Commons/Explorer) | ✅ `:544`; Ctrl+1 / Ctrl+2 | aligned |
| Help menu (Shortcuts F1 / About) | ✅ `:551` | aligned |
| About dialog (reads version.py) | ✅ `about_dialog.py:54` shows APP_VERSION + APP_BUILD | aligned |
| Settings dialog | ✅ Ctrl+, | aligned |
| Quit | ✅ Ctrl+Q | aligned |
| Search shortcut | ⚠ Ctrl+K wired (`:510`) but **not exposed in any menu** (status-bar hint only) | small polish |
| **Check for Updates entry + UpdateBanner** | ✗ **`updater.py` exists but is NEVER imported/called from the UI**; no UpdateBanner instantiated | **small v1 blocker** |
| Version-history / release-notes view | ✗ `updater.py` parses `release_notes` but it's never displayed | defer to v1.1 |

**Reference (Job Tracker, the family norm):** Help → **Check for Updates** (`project_tracker_gui.py:4440`) + **Version History && Recent Updates** + UpdateBanner in the status bar (`:4051`). Every shipped app self-updates from its menu.

**Classification: mostly aligned; one small v1 blocker.** PCC's menu/About/Settings infrastructure is complete and family-consistent. The one real gap is that the (production-ready) updater backend is **disconnected from the UI** — a packaged self-updating app must surface "Check for Updates" + a banner, or users can never update through the app. ~1–2 hours to wire, mirroring Job Tracker's pattern.

---

## 7. Installer / updater readiness

| Item | State | Evidence |
|------|-------|----------|
| build.bat 3.12 enforcement | ✅ (hard gate, even stricter than the soft-warn standard) | `build.bat:44` |
| commons preflight | ✅ | `:30`, `:67` `import phoenix_commons` |
| Step 0 full cleanup | ✅ `rmdir /s /q build dist` | `:84` |
| `--noupx` | ✅ | `:104` |
| `--collect-all=phoenix_commons` | ✅ | `:111` |
| 8 stdlib excludes | ✅ tkinter/_tkinter/tcl/tk/lib2to3/idlelib/turtle/turtledemo | `:115` |
| installer.iss AppId | ✅ `{B6E4A1F2-3D5C-4B7A-9E1F-8C2D5A7B9E4F}` (stable GUID) | `:15` |
| DefaultDirName | ✅ `{localappdata}\ATS Inc\Phoenix Command Center` | `:29` |
| OutputBaseFilename | ✅ `PhoenixCommandCenterSetup` | `:36` |
| PrivilegesRequired=lowest | ✅ | `:32` |
| Upgrade-in-place | ✅ `UsePreviousAppDir=yes` | `:51` |
| updater.py contract | ✅ full-folder (`expected_internal=True`); validates exe@root + `_internal/` | standalone (not a commons hybrid facade) |
| updater zip name match | ✅ `PhoenixCommandCenter.zip` (updater const = build.bat output) | |
| user-data path | ✅ `%APPDATA%\ATS Inc\Phoenix Command Center` (paths.py:37 + installer uninstall) | |
| requirements | ✅ PySide6 6.10.2 pins + `-e ./commons`; dev: pyinstaller 6.20.0 + pytest + pytest-qt | |

**Classification: packaging is production-ready — no blockers.** PCC's build/installer/updater contract fully matches (and in the 3.12-gate case exceeds) the proven 4-app standard. Two **notes, not blockers:** (a) `updater.py` and `paths.py` are **standalone** (own implementations, not facaded to `phoenix_commons.updater`/`.paths`) — acceptable for v1, candidate for a future commons-facade alignment; (b) the updater is wired-for-build but not wired-to-UI (see § 6).

---

## 8. Version / release policy recommendation

**Current:** `version.py` → `APP_VERSION = "2.0.0"`, `APP_BUILD = "v2 — commons browser, new-tool wizard, push diff preview"`. Existing tags: `pcc-phase-3c-merged-v2.0.0` … `pcc-phase-3g-merged-v2.4.0` (forensic phase tags).

**Recommendation: first public packaged release = `v1.0.0`.**

Rationale:
- The `v2.x` numbers are **forensic phase markers**, not operator-facing releases. Shipping a "v2.0.0" as the *first* public release invites "where was v1?" confusion.
- A clean `v1.0.0` marks the formal handoff: "first real Ground Control release," semver from there (`v1.0.1`, `v1.1.0`, …) — matching the 4-app family convention.
- The `pcc-phase-*` tags stay in git as audit history but are **not** published as GitHub Releases.

**Action at RC time (not now):** set `version.py` → `1.0.0`, update `APP_BUILD` string, create stable tag `v1.0.0` (no `pcc-phase-` prefix).

**This is an operator decision** (§ 12) — the alternative (continue v2.x) is defensible but messier. Recommend v1.0.0.

---

## 9. CI / source-bloat readiness

| Item | State |
|------|-------|
| ci.yml checkout | ✅ `submodules: recursive` — **not** exposed to the phoenix-master-tool Tests-workflow failure |
| ci.yml platform | ✅ windows-latest, Python 3.12 |
| ci.yml steps | install reqs + reqs-dev (split) → `import phoenix_commons` smoke → `compileall` → `pytest -q tests/` |
| Recent CI runs | green (last failure was an unrelated pre-merge cleanup 2026-05-22) |
| Legacy ubuntu `test.yml` | none — PCC has only the single family `ci.yml`, so **no** missing-submodule failure mode |
| Tracked bloat | ✅ zero `dist`/`build`/`_internal`/`.venv`/`*.pyc` tracked |
| `.gitignore` | covers `dist/`, `build/`, `.venv/`, `venv/`, `env/`, `__pycache__/`, `*.pyc`, `*.spec`, caches |
| `.venv*/` suffix glob | ⚠ **missing** (same trivial gap the other 4 repos just had fixed); no `.venv312`-style dir on disk today |
| submodule pin | ✅ clean (`768e36d` heads/main) |

**Classification: CI + bloat ready.** One trivial polish: add `.venv*/` to `.gitignore` (matches the just-applied family housekeeping).

---

## 10. Release blockers

### Real v1 blockers (small)

1. **Updater not wired to UI** (§ 6) — add Help → "Check for Updates" + UpdateBanner. A packaged self-updating app must be able to self-update from its menu. ~1–2 h, mirrors Job Tracker.
2. **Version policy unresolved** (§ 8) — `version.py` at `2.0.0`; must decide v1.0.0 (recommended) vs v2.x before tagging, and bump accordingly. Operator decision + 1-line change.
3. **Refresh doesn't re-discover** (§ 3) — for "track all apps … appear after Refresh," make Refresh re-run `discover_tools`. ~10 lines.

### Small fixes (polish, low risk)

4. **Stale installed-app mapping** (§ 5) — `ValveMasterTool\ValveMasterTool.exe` → `…\PhoenixMasterTool.exe`; optionally add Screenshot Tool. 1–3 lines.
5. **Ctrl+K not in a menu** (§ 6) — add a "Search" affordance (View/Tools menu). 15 min.
6. **`.venv*/` gitignore glob** (§ 9) — 1 line.

### Defer to v1.1

7. Version-history / release-notes dialog (updater already parses `release_notes`).
8. `updater.py` / `paths.py` → commons-facade alignment (currently standalone; works fine).
9. Per-tool TODO/branch/sync on the dashboard surface.

### Not blockers

- Installer / build / updater contract — production-ready (§ 7).
- CI / source-bloat — ready (§ 9).
- Dashboard + drill-down core — sufficient (§ 4, § 5).

---

## 11. Recommended v1 implementation sequence

Single focused phase (call it **PCC v1 / "Ground Control"**), small surface, no UI redesign:

| Step | Work | Files | Risk |
|------|------|-------|------|
| **V1-1** | Wire updater into UI: Help → "Check for Updates" QAction → `updater.check_for_update`; UpdateBanner in status bar on hit; progress + apply on click (mirror Job Tracker) | `main_window.py` (+ reuse commons `UpdateBanner`) | low |
| **V1-2** | Make Refresh re-discover: `_refresh_all` calls `_load_tools()` then rescans; or add "Rescan for new apps" | `main_window.py` | low |
| **V1-3** | Fix stale installed-exe mapping (VM → `PhoenixMasterTool.exe`); add Screenshot Tool | `detail_panel.py` | trivial |
| **V1-4** | Add `.venv*/` to `.gitignore`; add "Search (Ctrl+K)" menu affordance | `.gitignore`, `main_window.py` | trivial |
| **V1-5** | Version policy: set `version.py` → `1.0.0` (per § 8 decision), update README + CHANGELOG | `version.py`, `README.md`, `CHANGELOG.md` | trivial |
| **V1-6** | Source-mode validation: compileall + `pytest tests/` + offscreen launch smoke | — | — |
| **V1-7** | Frozen build under Python 3.12 venv → verify artifacts + commons bundle + full-folder updater zip | — | — |
| **V1-8** | Operator interactive validation: install + 5-min S1 + visual + dashboard tracks all family apps + detail drill-down + Check-for-Updates | — | — |
| **V1-9** | RC tag `v1.0.0-rc1` → operator validate → stable tag `v1.0.0` → draft GitHub Release → publish (same gates as the 4-app arc) | — | — |

Estimated ~1 working session for V1-1..V1-5 (mechanical), ~1 session for build + validate + release (V1-6..V1-9). Mirrors the 2-session cadence of Wave 8a/8b.

---

## 12. Operator decisions needed

1. **Version policy** — confirm first public release is **`v1.0.0`** (recommended), or continue the `v2.x` line. Determines the `version.py` bump + first stable tag.
2. **Updater UI scope for v1** — minimum is "Check for Updates" + UpdateBanner (V1-1). Include the version-history/release-notes dialog in v1, or defer to v1.1? (Recommend defer.)
3. **Refresh semantics** — should "Refresh All" itself re-discover new apps (recommended), or add a separate "Rescan for new apps" action?
4. **Installed-launch scope** — should "Launch installed" support all 5 family apps (incl. Screenshot Tool) + handle the ValveMaster→PhoenixMasterTool rename, or just fix the stale VM entry for v1?
5. **commons-facade alignment** — leave `updater.py`/`paths.py` standalone for v1 (recommended; they work), or fold into a future Wave-style commons-facade pass?
6. **CLAUDE.md re-scope** — update PCC's CLAUDE.md "source-run only / not a shipping tool" framing to reflect the new packaged-Ground-Control intent (recommended as part of V1-5).

---

## 13. Verdict

### **B — ready for v1 RC after small fixes.**

PCC is in **strong shape**: the packaging/installer/updater contract is production-ready (build.bat hardened beyond the family minimum), CI is submodule-safe and green, source is clean, and the dashboard + drill-down + menu infrastructure from Phases 3C–3G is feature-complete and family-consistent. It is **not "not ready"** — there is no architecture work and no redesign required.

The path to RC is a tight set of **small, low-risk fixes**, not feature development:
- 1 genuine functional blocker (wire the existing updater into the UI),
- 1 product-intent fix (Refresh should re-discover so it truly "tracks all apps"),
- 1 stale-data fix (installed-exe mapping),
- 1 policy decision + version bump (v1.0.0),
- 2 trivial polish items (gitignore glob, Ctrl+K menu affordance).

Once the § 12 decisions are made and V1-1..V1-5 land, PCC follows the exact RC → validate → publish gate the 4 shipped apps used.

---

## Confirmation

- **No implementation performed** — read-only audit.
- **No source code changed** in PCC or any repo.
- **No build, no frozen exe, no installer run.**
- **No GitHub Release, no assets, no tags created.**
- **No scanner contract / app behavior / UI changed.**
- The 2 stale-doc edits noted earlier (`WAVE_RC_CAD` report, `RC_KICKOFF_READY`) were operator/linter changes, not made here.

*PCC v1 Ground Control audit complete. Awaiting operator decisions (§ 12) before any implementation.*
