# FROZEN_BUILD_BASELINE.md

> Canonical reference for the Phoenix UI Platform's frozen (PyInstaller)
> build baseline. Mandatory configuration for any Phoenix tool that
> produces a deployable exe via PyInstaller + Inno Setup.
>
> Empirically validated by `BUILD_HARDENING_EXPERIMENT_REPORT_01.md`,
> `_02.md` (reproducibility), and `_03.md` (single-variable Python
> isolation). Codified into platform doctrine 2026-05-20.

## TL;DR — what every frozen Phoenix build must do

```
Build venv MUST be Python 3.12.x.
Build venv MUST pin PyInstaller (6.20.0 currently).
Build venv MUST pin PySide6 (6.10.2 currently).
build.bat MUST use --onedir --windowed --noupx.
build.bat MUST exclude unused stdlib (tkinter family, lib2to3, idlelib, turtle/turtledemo).
build.bat MUST clean build/ + dist/ at the top.
The bootloader exe MUST survive ≥ 2 minutes on disk after the build sequence.
```

Source-mode work (development, pytest, source-launch) can use any
Python 3.10–3.14 per ADR-014. **This document covers the build-time
contract only.**

## 1. Why this baseline exists

The Phoenix developer workstation runs SentinelOne (S1) endpoint
protection. As documented in `BLOCKERS.md § 1`, S1 quarantines the
PyInstaller bootloader exe within seconds of disk write under certain
content-heuristic conditions.

Three controlled experiments isolated the trigger:

| Experiment | Configuration | Outcome |
|------------|----------------|---------|
| Phase 6 original (pre-hardening) | Python 3.14, PyInstaller 6.19, PySide6 6.11.1, `upx=True` no-op, no excludes, untreated venv | Bootloader quarantined within seconds |
| EXPERIMENT_REPORT_01 (B1) | Python 3.12 + all hardening | Bootloader survived ≥ 5 minutes |
| EXPERIMENT_REPORT_02 (B2) | Identical to B1 (reproducibility test) | Bootloader survived ≥ 2.3 minutes; build determinism confirmed |
| EXPERIMENT_REPORT_03 (B3) | Python 3.14 + all other hardening identical to B1/B2 | Bootloader quarantined within ~25 seconds |

The B1 → B2 reproducibility and B2 → B3 single-variable isolation
identified **Python interpreter version** as the primary material
variable. Python 3.12 bootloaders survive on this S1 configuration;
Python 3.14 bootloaders do not.

## 2. The baseline (canonical configuration)

### 2.1 Build venv

| Setting | Value |
|---------|-------|
| Python | **3.12.x** (3.12.10 verified; any 3.12 patch acceptable) |
| Venv creation | `py -3.12 -m venv .venv` from a clean directory (no reuse of an existing 3.14 venv) |
| pip | Latest available (≥ 25.0; pip 26.x verified) |

Build venv MAY coexist alongside a separate development venv on Python
3.13 or 3.14 (e.g. `.venv-dev/`). The build pipeline MUST use the 3.12
venv specifically.

### 2.2 Pinned build dependencies

`requirements.txt`:

```
PySide6==6.10.2
```

`requirements-dev.txt`:

```
pyinstaller==6.20.0
pytest>=8,<10
pytest-qt>=4.4
```

Pin update policy:

- Bumps to `PyInstaller` and `PySide6` pins MUST be validated by a
  fresh isolation experiment before adoption (same protocol as
  EXPERIMENT_REPORT_03 — clone scaffold, change one variable, observe).
- `pytest` / `pytest-qt` pins can float (they don't affect frozen
  output).

### 2.3 build.bat hardening

These flags / steps are mandatory:

```cmd
rem Step 0: Deterministic cleanup
if exist build rmdir /s /q build
if exist dist  rmdir /s /q dist

rem Step 1: PyInstaller with hardening flags
.venv\Scripts\pyinstaller ^
    --noconfirm ^
    --onedir ^
    --windowed ^
    --noupx ^
    --name=<EXE_STEM> ^
    --add-data="phoenix_style.qss;." ^
    --collect-submodules=PySide6.QtCore ^
    --collect-submodules=PySide6.QtGui ^
    --collect-submodules=PySide6.QtWidgets ^
    --exclude-module=tkinter ^
    --exclude-module=_tkinter ^
    --exclude-module=tcl ^
    --exclude-module=tk ^
    --exclude-module=lib2to3 ^
    --exclude-module=idlelib ^
    --exclude-module=turtle ^
    --exclude-module=turtledemo ^
    main.py
```

### 2.4 Source-mode flexibility

Source-mode activities — running the app via `python main.py`, pytest,
compileall, IDE Run/Debug — can use any Python 3.10–3.14. Only the
PyInstaller build venv is constrained.

This matches ADR-014's prior text: "App developers may experimentally
use newer Python locally (3.13, 3.14) for dev convenience".

## 3. What this baseline solves

| Problem | Solution |
|---------|----------|
| S1 quarantines fresh PyInstaller bootloaders | Use Python 3.12; bootloader content matches an existing-trusted shape |
| Build determinism / reproducibility | Pinned PyInstaller + pinned PySide6 + deterministic cleanup produces byte-equivalent bootloader content per build (modulo embedded PE TimeDateStamp) |
| Bundle bloat from unused stdlib | Explicit `--exclude-module` for tkinter/lib2to3/idlelib/turtle |
| Build-time AV-explainability concerns | `--noupx` explicit (signals "we don't pack"); pinned versions (signals "no opportunistic version drift") |
| IT/security audit posture | All flags + pins are documented; nothing speculative |

## 4. What this baseline does NOT solve

| Out of scope | Reason |
|--------------|--------|
| Cross-machine deployment durability | Authenticode code-signing is the durable answer (per `BLOCKERS.md § 1` option 2). This baseline keeps the developer workstation green; user-machine reputational durability is a separate concern. |
| Production-tool exes' current install state | The 4 deployed production exes shipped pre-hardening and survived because they were already installed when S1's heuristic activated. Their next rebuild MUST adopt this baseline. |
| `_internal/` bundle audit (Phoenix Checkout + Job Tracker bundle 22× more files than necessary) | Tracked separately as opportunistic hygiene (see `BUILD_HARDENING_COMPARISON_REPORT_01.md § R8`). Not blocking. |
| IT/S1 allow-list pursuit | Out-of-band; defence in depth (`BLOCKERS.md § 1` option 1). |
| Phase 6C frozen-exe dogfood + installer round-trip | Re-enabled by this baseline; Phase 6C plan in `phoenix-commons/docs/rollout/phase-6c-frozen-exe-dogfood-plan.md` can resume. |

## 5. When to update this baseline

This baseline MUST be updated when any of these become true:

| Trigger | Required update |
|---------|------------------|
| Python 3.12 reaches end-of-life | Re-isolation experiment under the next interpreter (3.13 or 3.14 stable-bootloader release). Update only after empirical S1 validation. |
| PyInstaller releases a new major | Re-isolation experiment. Same protocol as EXPERIMENT_REPORT_03. |
| PySide6 bumps a major version | Re-validate PySide6 6.10.2 → new version on Python 3.12. |
| S1 heuristic database update breaks Python 3.12 bootloaders | Repeat experiments. Possibly pursue signing pipeline urgently. |
| ATS infrastructure migrates off S1 | Hardening still recommended for explainability but no longer mandatory for survival. |

## 6. Verification protocol for any frozen build

Before publishing a release:

1. Confirm build venv is Python 3.12.x: `.venv\Scripts\python --version` reports 3.12.something.
2. Confirm pinned versions: `.venv\Scripts\python -c "import PyInstaller, PySide6; print(PyInstaller.__version__, PySide6.__version__)"` reports 6.20.0 / 6.10.2.
3. Run `build.bat` to completion.
4. Verify the bootloader exe is on disk at `dist\<ExeStem>\<ExeName>.exe` ≥ 2 minutes after PyInstaller finished.
5. Verify the updater zip contains the bootloader at the zip root (use `scripts/validate_release_zip.py` if available).
6. Continue with `RELEASE_CHECKLIST.md` § 6 (local smoke install) and onward.

If any step fails — particularly step 4 — STOP. Do not publish.
Consult `BLOCKERS.md § 1` and the experiment reports.

## 7. Evidence chain

| Report | What it established |
|--------|----------------------|
| `BUILD_HARDENING_COMPARISON_REPORT_01.md` | Root-cause analysis: S1 hits the unsigned PyInstaller bootloader; ruled out UPX, bundle surface; identified Python version + PyInstaller version + signing as the prime suspects. |
| `BUILD_HARDENING_EXPERIMENT_REPORT_01.md` | First hardened build (Python 3.12 + everything pinned + excludes + --noupx + cleanup): S1 quarantine outcome flipped to survival. Multi-variable change. |
| `BUILD_HARDENING_EXPERIMENT_REPORT_02.md` | Reproducibility: A second build under the same hardened config produced a byte-equivalent bootloader (modulo PE TimeDateStamp) and survived identically. |
| `BUILD_HARDENING_EXPERIMENT_REPORT_03.md` | Single-variable isolation: reverting only Python 3.12 → 3.14, keeping all other hardening, quarantined the bootloader. **Python is the material variable.** |

## 8. Cross-references

- `DECISIONS.md` § ADR-014 — canonical Python version (now empirically validated)
- `BLOCKERS.md` § 1 — S1 / corporate AV bootloader quarantine
- `RELEASE_CHECKLIST.md` — release procedure; § 5 cites this baseline
- `INSTALLER_NOTES.md` — installer conventions; references this baseline
- `MIGRATION_RULES.md` — retrofit doctrine; § Stop conditions cites this baseline
- `RETROFIT_PLAYBOOK.md` — operator field manual; build venv setup follows this baseline
- PCC's `phoenix_tool_templates.py` — wizard-scaffolded tools' build.bat / requirements emit this baseline by default
- Rollout sequence: `docs/rollout/phase-6c-frozen-exe-dogfood-plan.md` (resumable now that baseline is frozen)

## 9. Sign-off

| Field | Value |
|-------|-------|
| Status | Canonical — frozen build baseline |
| Authority | `DECISIONS.md` § ADR-014 + empirical validation by experiments 01–03 |
| Effective | 2026-05-20 |
| Next mandatory review | Whenever a trigger in § 5 occurs |
| Owner | Phoenix UI Platform |
