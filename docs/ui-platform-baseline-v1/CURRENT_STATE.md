# CURRENT_STATE.md

> Accurate snapshot of every repo, branch, CI surface, and verification
> result as of 2026-05-16. Items are tagged **Verified**, **Assumed**,
> **Blocked**, or **Deferred** so the next implementer knows which
> claims they can rely on.

## Repos

| Repo | Branch (local HEAD) | Origin | Notes |
|------|---------------------|--------|-------|
| `phoenix-commons` | `baseline-v1` (this baseline) | not pushed | `phase-4-pyinstaller-compatibility` is the long-running rollout branch, last commit `ba3d2c4` (Phase 6C backup report). `main` exists locally. |
| `phoenix-command-center` | `main` @ `a9d9433` | `JustinGlave/phoenix_command_center` (synced) | All Phase-5/5B/6A/6B work + GUI polish + packaging + smoke tests merged |
| `Job Tracker` | (production, untouched) | `JustinGlave/project-tracking-tool` | Verified v1.8.5 — full-folder updater pattern |
| `Phoenix_CAD_Tool` | (production, untouched) | `JustinGlave/lab-layout-tool` | Verified v0.1.1 — full-folder updater pattern; canonical theme source |
| `Phoenix-Checkout-Tool` | (production, untouched) | `JustinGlave/Phoenix-Checkout-Tool` | Verified v1.7.0 — **exe-only** updater pattern |
| `ValveMasterTool` | (production, untouched) | `JustinGlave/valve-master-tool` | Verified v1.0.9 — **exe-only** updater pattern, legacy gray theme |

## phoenix-commons source layout (Verified)

```
phoenix-commons/
├── pyproject.toml
├── src/phoenix_commons/
│   ├── __init__.py
│   ├── _version.py                  # 0.1.0
│   ├── paths.py                     # is_frozen, user_data_dir, resource_path
│   ├── theme/
│   │   ├── __init__.py
│   │   ├── apply.py                 # apply_dark_theme(app)
│   │   ├── _embedded_qss.py         # embedded fallback (verbatim from Phoenix CAD)
│   │   └── phoenix_style.qss        # canonical QSS file
│   ├── widgets/
│   │   ├── __init__.py
│   │   ├── buttons.py               # PrimaryButton, SecondaryButton, TertiaryButton
│   │   ├── helpers.py               # button_row, etc.
│   │   ├── no_scroll.py             # NoScroll[ComboBox|SpinBox|DoubleSpinBox|DateEdit]
│   │   ├── panel.py                 # Panel
│   │   ├── table.py                 # PhoenixTable
│   │   ├── typography.py            # PageTitle, PageSubtitle, SectionTitle, HintLabel
│   │   └── update_banner.py         # UpdateBanner
│   └── updater/
│       ├── __init__.py
│       ├── client.py                # check_for_update
│       ├── installer.py             # download_and_apply (with expected_internal kwarg)
│       └── qt.py                    # UpdateCheckThread
├── tests/
│   ├── __init__.py
│   ├── test_smoke.py
│   ├── test_paths.py
│   └── test_updater.py
└── docs/
    ├── production-inventory.md      # Phase 0 deliverable
    ├── phase-1-completion-packet.md
    ├── phase-1-report.md
    ├── rollout/                     # Phase 1A → 6C reports (16 files)
    └── ui-platform-baseline-v1/     # this baseline
```

**Maturity:** Verified end-of-Phase-3A. No source changes since.

## phoenix-command-center source layout (Verified)

Flat-layout PySide6 app (NOT the wizard-generated `ui/`-subdir layout):

```
phoenix-command-center/
├── main.py / main_window.py / dashboard.py / detail_panel.py /
│   commons_browser.py / new_tool_wizard.py / phoenix_tool_templates.py /
│   push_preview_dialog.py / scanner.py / settings_dialog.py /
│   sidebar_tool_widget.py / sidebar_sprite.py / theme.py / tool_card.py /
│   file_viewer.py / about_dialog.py / config.py / version.py
├── paths.py                         # local copy (added in packaging branch)
├── updater.py                       # local copy (full-folder pattern)
├── build.bat                        # PyInstaller + Inno Setup + zips + validator
├── installer.iss
├── pcc_config.example.json
├── pcc_config.json                  # machine-specific, gitignored
├── scripts/validate_release_zip.py
├── tests/
│   ├── conftest.py
│   └── test_smoke.py                # 4 tests, all green in CI
├── requirements.txt                 # PySide6 6.10.2 pinned exact
├── requirements-dev.txt             # pyinstaller 6.20.0, pytest 8.3.4, pytest-qt 4.4.0
├── assets/
│   ├── logo.png / logo.ico / watermark.png
│   ├── ats_automation_stable_transparent.webp / .apng
│   └── README.md
├── docs/
│   ├── README.md / CHANGELOG.md / LICENSE / SECURITY.md /
│   │   CONTRIBUTING.md / CODE_OF_CONDUCT.md
│   ├── known-issues.md              # S1/AV blocker
│   ├── build_notes.md
│   ├── release_checklist.md
│   ├── branding-packaging-report.md
│   └── build-notes-clarification-report.md
└── .github/
    ├── workflows/ci.yml
    ├── ISSUE_TEMPLATE/{bug_report,feature_request}.md
    └── pull_request_template.md
```

**Maturity:** Verified. CI green on every push since `a9d9433`.

PCC's `paths.py` and `updater.py` are **local copies**, not imports
from `phoenix_commons`. The migration to commons-backed imports
is one of the open items in `TODOS.md`.

## CI state (Verified)

| Repo | Workflow | Trigger | Last result |
|------|----------|---------|-------------|
| `phoenix-command-center` | `.github/workflows/ci.yml` | push to `main`, any PR | ✅ green on `a9d9433` (after smoke baseline merged) |
| `phoenix-commons` | none | n/a | No CI yet — see TODOs.md |

PCC CI runs on `windows-latest`, Python 3.14, installs both
requirements files, runs `python -m compileall -q .` and
`QT_QPA_PLATFORM=offscreen python -m pytest -q tests/`.

## Packaging state

| Surface | State | Tag |
|---------|-------|-----|
| `phoenix-command-center` `build.bat` | Source authored, never executed | Blocked |
| `phoenix-command-center` `installer.iss` | Source authored, AppId GUID locked | Blocked |
| `phoenix-command-center` `updater.py` | Source authored, never run against live release | Blocked |
| `scripts/validate_release_zip.py` | Source authored, unit-tested in Phase 6A | Verified |
| `assets/logo.{png,ico}` + `watermark.png` | Placeholders (letterboxed sprite) | Verified-as-placeholder |
| 4 production-tool installers | Last shipped versions are the canonical artifact | Unchanged |

## AV / S1 state

| Aspect | State |
|--------|-------|
| Bootloader quarantine reproduces? | **Yes** — observed in Phase 4, 4B-local, and Phase 6 (3 independent reproductions on this laptop) |
| Resolution paths identified? | Yes (IT/S1 allow-list, Authenticode signing, alternate build host) | 
| Resolution path selected? | **No** — pending DevOps + IT input |
| Workarounds in place? | External-build-path isolation (Phase 4B-local) protects source tree but not the exe |
| Impact | All frozen-exe verification phases (4, 6, 6C, 7, 8) blocked on this laptop |

## Source-mode verification state (Verified)

| Component | Last verification |
|-----------|-------------------|
| `phoenix-commons` package import | Verified Phase 1, no regressions |
| Theme renders a PySide6 window | Verified Phase 2 (smoke window) |
| Updater check + dry-run validation | Verified Phase 3A (with PS-safe quoting fix) |
| Wizard generates standalone scaffold | Verified Phase 5 (26 files, pytest 4/4) |
| Wizard generates commons-backed scaffold | Verified Phase 5A (20 files, pytest 5/5) |
| Wizard auto-checks submodule on commons radio | Verified Phase 5B |
| Standalone scaffold builds via PyInstaller | Verified Phase 6 (until exe quarantined) |
| Inno Setup compiles the throwaway installer | Verified Phase 6 (Setup.exe survived) |
| `scripts/validate_release_zip.py` | Verified Phase 6A (5 CLI scenarios + 3 pytest cases) |
| Command Center smoke tests | Verified post-merge `a9d9433` |

## Frozen-exe verification state

**Blocked.** Last attempt: Phase 6 (standalone dogfood). Exe was
written to `dist\PhoenixPhase6Standalone\` by PyInstaller, picked up
by Inno Setup for compression into the installer, then deleted from
disk within seconds by S1. Same pattern observed in Phase 4 and Phase
4B-local. No frozen-exe has been launched successfully on this laptop.

## Backups (Verified)

Local git bundles at `C:\Users\justing\PycharmProjects\Backups\`
(Phase 6C Layer 1):

- `phoenix-command-center-20260513.bundle` — pre-baseline snapshot
- `phoenix-commons-20260513.bundle` — pre-baseline snapshot

Neither has been pushed to OneDrive yet (Phase 6C report flagged the
same-disk tradeoff). Backups are not refreshed on a schedule.

## Rollout maturity summary

| Phase | Status |
|-------|--------|
| 0     | ✅ done (production inventory) |
| 1     | ✅ done (commons skeleton) |
| 1A    | ✅ done (git init + housekeeping) |
| 2     | ✅ done (theme + widgets lifted) |
| 2.1–2.7 | ⏸ defined in `PHASES.md`, not started |
| 3     | ✅ done (paths + updater lifted) |
| 3A    | ✅ done (download bug + PS quoting fix) |
| 3B / 3C | ⏸ defined in `PHASES.md`, not started |
| 4     | ⚠ partial (PyInstaller compat — exe AV-blocked) |
| 4B-local | ⚠ partial (external-path build, AV still fires) |
| 4C-init | ✅ done (PCC became a git repo) |
| 5     | ✅ done (wizard radios + scaffolds) |
| 5A / 5B | ✅ done (wizard smoke + UX gap fix) |
| 6     | ⚠ partial (source mode green; frozen exe AV-blocked) |
| 6A    | ✅ done (release-zip validator out of inline PowerShell) |
| 6B    | ✅ done (wizard merged to PCC main) |
| 6C    | ⏸ planned, **blocked on AV** |
| 7     | ⏸ deferred (production retrofit pilot — Checkout + Phoenix CAD) |
| 8     | ⏸ deferred (remaining retrofits — ValveMaster + Job Tracker) |
| 9     | ⏸ deferred (long-term stewardship / commons v2) |

## Separating Verified / Assumed / Blocked / Deferred

| Tag | Meaning |
|-----|---------|
| **Verified** | Has a report or test result that proves it. Use freely as a foundation for new work. |
| **Assumed** | Plausible but unverified — needs a smoke test before any consumer relies on it. |
| **Blocked** | Verification attempt failed for a documented reason (see `BLOCKERS.md`). Don't retry without addressing the blocker. |
| **Deferred** | Intentionally not yet attempted. Has a defined entry condition in `PHASES.md`. |
