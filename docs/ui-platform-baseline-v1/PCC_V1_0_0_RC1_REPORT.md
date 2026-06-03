# Phoenix Command Center — v1.0.0-rc1 Build Report

> **Status:** ✅ BUILT + TAGGED + automatable-validation green. Awaiting operator
> interactive validation, then draft release.
> **Date:** 2026-06-02.
> **Repo:** `phoenix-command-center`.
> **No GitHub Release / assets / final stable tag — this is the RC build step.**

---

## 1. Branch

| | |
|---|---|
| Source `main` | `0245be0` ("Merge PCC v1 Ground Control") |
| RC branch | **`release/v1.0.0-rc1`** (from `main`, pushed) |
| HEAD | `0245be0` (clean working tree before + after build) |

## 2. RC tag

| | |
|---|---|
| Tag | **`v1.0.0-rc1`** (annotated) → `0245be0` |
| Message | "Phoenix Command Center v1.0.0 RC1 — Ground Control initial release" |
| Pushed | ✅ `origin` (main + `release/v1.0.0-rc1` + `v1.0.0-rc1`) |

`v1.0.0-rc1` is a forensic RC tag; the stable `v1.0.0` tag is a separate later step.

## 3. Build result

`build.bat` (hard Python-**3.12.10** gate, `--noupx`, `--collect-all
phoenix_commons`, stdlib excludes, Step-0 clean) → **"Build complete - v1.0.0"**.
Inno Setup compiled the installer (24 s). build.bat's own updater-zip check
reported **"zip OK: 231 entries, PhoenixCommandCenter.exe present, _internal/
present"**. No S1 quarantine during build (build ran to completion; exe produced
+ persisted).

## 4. Artifacts produced (`dist\`, fresh 2026-06-02 14:11–14:12)

| Artifact | Size | Purpose |
|----------|------|---------|
| `PhoenixCommandCenter\PhoenixCommandCenter.exe` + `_internal\` | — | frozen `--onedir` app |
| `PhoenixCommandCenterSetup.exe` | 35 MB | Inno Setup installer |
| `PhoenixCommandCenter.zip` | 50 MB | **auto-updater** (full-folder) |
| `PhoenixCommandCenter_FullInstall.zip` | 50 MB | full-folder convenience zip |

**Bundling verified** in `_internal\`: `phoenix_commons` package +
`phoenix_commons-0.1.0.dist-info`, **23 Lucide SVG icons**
(`phoenix_commons/icons/lucide/*.svg`), commons theme
(`phoenix_commons/theme/phoenix_style.qss`), `assets`, `base_library.zip`. PCC's
own modules (`updater`, `todo_state`, `todo_verify`, `todo_toggle`,
`todo_workbench`, dashboard/detail/main_window) are frozen into the exe's PYZ —
validated functionally by the frozen launch (§6: a missing/broken import would
crash startup).

## 5. Updater zip contract result

Independently inspected `PhoenixCommandCenter.zip`:
- `PhoenixCommandCenter.exe` at **root**: ✅ True
- `_internal/` at **root**: ✅ True
- entries: **231**

→ **full-folder / `expected_internal=True` contract preserved.** `updater.py`,
`installer.iss`, and `scanner.py` were unchanged by the v1 work (verified at the
merge gate). Exe name `PhoenixCommandCenter.exe`, repo `phoenix_command_center`,
asset `PhoenixCommandCenter.zip` — all intact.

## 6. Frozen exe validation

| Check | Result |
|-------|--------|
| `dist\PhoenixCommandCenter\PhoenixCommandCenter.exe` launches (offscreen) | ✅ alive, survived startup (no crash) |
| All modules import (incl. TODO Workbench + commons) | ✅ implied by clean startup |
| Exe persists on disk after launch+stop | ✅ (no S1 quarantine on launch) |
| `pytest tests/` on the RC commit (`0245be0`) | ✅ 83 passed (post-merge) |

The frozen exe was launched headless (`QT_QPA_PLATFORM=offscreen`) and remained
alive through Qt init + `MainWindow` construction — meaning every frozen import
(updater, todo_*, dashboard, commons widgets/theme/icons) resolved and the window
built without error. **Live visual review + interactive Ctrl+K / Ctrl+3 / toggle
are the operator's interactive pass (§10).**

## 7. Installer validation (silent round-trip)

| Step | Result |
|------|--------|
| Silent install (`/VERYSILENT`) → `%LOCALAPPDATA%\ATS Inc\Phoenix Command Center` | ✅ exe + `_internal\` present |
| Installed exe launches (offscreen) | ✅ alive, no crash |
| Uninstaller (`unins000.exe`) present | ✅ |
| Silent uninstall → install dir removed | ✅ clean round-trip |

A reversible install→launch→uninstall round-trip confirms the installer produces
a launchable installed app; the system was left clean for the operator's
interactive install. **Interactive config-persistence + visual review are the
operator's pass.**

## 8. S1 (AV) observation

No quarantine observed across the full cycle: **build** (exe + setup produced and
persisted), **frozen launch** (exe ran + remained on disk), **silent install**
(installed exe ran), **uninstall** (clean). The PCC build pipeline runs
end-to-end on this host. The standing 5-minute interactive S1 watch on the
running app is the operator's interactive step (§10); automatable signals are
all green.

## 9. TODO Workbench validation (frozen)

- The Workbench modules (`todo_workbench` / `todo_state` / `todo_verify` /
  `todo_toggle`) are frozen into the exe and load cleanly (frozen startup alive).
- Behavioural correctness was proven by the **83-test** suite on `0245be0`
  (state 24 / verify 13 / workbench 25 / toggle 17 + 4 smoke), incl. the
  **code-comment TODO hard-block** and the safe markdown toggle (atomic write +
  post-write verify + path containment) — unchanged in the frozen build.
- Interactive in-app toggle on a real markdown TODO + Ctrl+3 table render are the
  operator's interactive pass.

## 10. Remaining items (operator interactive validation — not blockers)

These require a live interactive desktop session (the Claude subprocess runs
headless/offscreen), and are the standard operator RC pass:
- Dashboard renders with the configured tools-root + existing apps; visual/theme
  review.
- Interactive Ctrl+K search, Ctrl+3 Workbench table render, dashboard
  "Open TODOs" tile click → Workbench(Open).
- Interactive markdown toggle on a real TODO; confirm code TODO stays blocked.
- Updater UI: Help → Check for Updates (note: **no GitHub Release exists yet**,
  so it correctly reports up-to-date / shows no banner — no false positive).
- 5-minute interactive S1 watch on the running installed app.

No code blockers identified.

## 11. Recommendation

### **Ready for draft release** — pending the operator's interactive validation.

Every automatable RC gate passed: clean tagged build, all 4 artifacts, verified
bundling, **full-folder updater contract intact**, frozen-exe + silent-installer
launch round-trips green, no S1 quarantine, 83 tests green on the RC commit. No
tiny fix is outstanding. On a green operator interactive pass, proceed to prepare
the **draft** GitHub Release + assets (`PhoenixCommandCenter.zip` full-folder +
`PhoenixCommandCenterSetup.exe`) as a separate, explicitly-gated step.

## 12. Confirmation

- ✅ **No GitHub Release published.**
- ✅ **No assets uploaded.**
- ✅ **No final stable tag created** (`v1.0.0-rc1` is the forensic RC tag; no
  `v1.0.0`).
- ✅ **No scanner contract changed.**
- ✅ **No commons architecture changed** (submodule clean; consumers only).
- ✅ Working tree clean; `release/v1.0.0-rc1` + `v1.0.0-rc1` @ `0245be0`.

### STOP conditions — none triggered

Build succeeded · updater zip contract unambiguous (exe + `_internal/` at root) ·
frozen exe launches · installer install/uninstall round-trip clean · no S1
quarantine · TODO Workbench source-mutation safe (code blocked; md toggle
atomic+verified) · no visual regression in automatable checks.

---

## Outcome

**PCC v1.0.0-rc1 is built, tagged (`v1.0.0-rc1` @ `0245be0`), and
operator-validation ready.** Artifacts staged in `dist\`; updater contract
preserved; no blockers. Next: operator interactive validation → draft GitHub
Release prep (separate gated step).
