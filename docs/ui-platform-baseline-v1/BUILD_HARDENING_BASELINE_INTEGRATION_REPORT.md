# BUILD_HARDENING_BASELINE_INTEGRATION_REPORT.md

> Phase 6D deliverable: codify the experimentally-validated hardened
> build configuration as platform doctrine, update existing governance
> docs, update wizard templates, and verify generated output.
> Documentation + template integration only. No production rebuilds.
> No installer execution. No releases. No AV bypass behavior.
>
> Authored 2026-05-20, after `BUILD_HARDENING_EXPERIMENT_REPORT_03.md`
> isolated Python 3.12 as the material variable.

## 1. Final hardened baseline definition

The canonical reference now lives at
`phoenix-commons/docs/ui-platform-baseline-v1/FROZEN_BUILD_BASELINE.md`.

Summary:

| Layer | Value |
|-------|-------|
| Build venv Python | **3.12.x** (mandatory) |
| Source-mode Python | any 3.10–3.14 (unchanged, per ADR-014) |
| PyInstaller | **pinned 6.20.0** |
| PySide6 | **pinned 6.10.2** |
| Build mode | `--onedir --windowed` |
| Anti-pack flag | **`--noupx`** explicit |
| Stdlib excludes | `tkinter`, `_tkinter`, `tcl`, `tk`, `lib2to3`, `idlelib`, `turtle`, `turtledemo` |
| Build hygiene | Step 0 deterministic `rmdir /s /q build dist` at top of `build.bat` |
| Outcome on developer workstation | Bootloader survives ≥ 2 min; no S1 quarantine |
| Outcome attribution | **Python interpreter version** is the material variable (per A3-i isolation) |

## 2. Evidence chain

Four-report progression from observation → isolation → integration:

| Report | Established |
|--------|-------------|
| `BUILD_HARDENING_COMPARISON_REPORT_01.md` | Root-cause analysis; ruled out UPX + bundle surface; identified Python / PyInstaller version + signing as the prime suspects. |
| `BUILD_HARDENING_EXPERIMENT_REPORT_01.md` | First hardened build (multi-variable change): Python 3.12 + pinned deps + `--noupx` + excludes + cleanup. Outcome: S1 quarantine outcome flipped to survival (≥ 5 min observed persistence). |
| `BUILD_HARDENING_EXPERIMENT_REPORT_02.md` | Reproducibility: second identical-configuration build produced a **byte-equivalent** bootloader (only PE TimeDateStamp differs) and survived identically. Build is deterministic at the PyInstaller layer. |
| `BUILD_HARDENING_EXPERIMENT_REPORT_03.md` | Single-variable isolation: reverting only Python 3.12 → 3.14 (holding all other hardening byte-identical) reintroduced the quarantine within ~25 s. **Python is the material variable.** Other hardening adds explainability + hygiene but is not sufficient alone. |

Three-data-point grid:

| Run | Python | Other 6 hardening vars | Bootloader outcome |
|-----|--------|--------------------------|---------------------|
| Phase 6 original | 3.14.3 | NO | Quarantined |
| B1 (hardened baseline) | 3.12.10 | YES | Survived ≥ 5 min |
| B2 (reproducibility) | 3.12.10 | YES | Survived ≥ 2.3 min |
| B3 (A3-i isolation) | **3.14.3** | YES | **Quarantined within ~25 s** |

## 3. Doctrine updates landed

Single integration commit `1ea74e1` on `phoenix-commons:main` updated
four existing doctrine docs. Plus a separate prior commit `e8c5873`
added the new canonical reference.

| File | Change |
|------|--------|
| `FROZEN_BUILD_BASELINE.md` | **NEW.** Canonical reference doc; 200 lines. Defines the baseline, evidence chain, when it applies, when it doesn't, verification protocol, update triggers. Committed `e8c5873`. |
| `DECISIONS.md` § ADR-014 | Status row updated: "Finalized; empirically validated 2026-05-20". Decision + Enforcement rows note frozen-build mandate. New "Empirical validation" row documents the EXPERIMENT_REPORT_03 isolation. Cross-reference row expanded. |
| `RELEASE_CHECKLIST.md` § 5 (Build) | Three new gating checks at the top of the build step: Python 3.12.x build venv; pinned PyInstaller 6.20.0 + PySide6 6.10.2; build.bat uses `--noupx` + stdlib excludes + Step 0 cleanup. |
| `INSTALLER_NOTES.md` | Header expanded to document the build prerequisite (Python 3.12 + hardened build.bat) that feeds Inno Setup. Build pipeline diagram updated. |
| `MIGRATION_RULES.md` § Stop conditions | Two new stop conditions: build venv not 3.12.x; `build.bat` missing hardened flags. Both cite FROZEN_BUILD_BASELINE.md + EXPERIMENT_REPORT_03. |

No doctrine invented; the baseline is consolidated into existing
governance. Source-mode flexibility preserved (any Python 3.10–3.14).

## 4. Template updates landed

Single commit `9f1f3ea` on `phoenix-command-center:main` updated PCC's
wizard template to emit the hardened baseline by default for new
standalone scaffolds:

| Template | Change |
|----------|--------|
| `REQUIREMENTS_DEV_TXT` | `pyinstaller==6.19.0` → `pyinstaller==6.20.0` + cross-reference comment to FROZEN_BUILD_BASELINE.md |
| `REQUIREMENTS_TXT_STANDALONE` | `PySide6>=6.5` → `PySide6==6.10.2` + bump-validation comment |
| `REQUIREMENTS_TXT_COMMONS` | Same upgrade for commons-backed scaffolds |
| `BUILD_BAT` | Five additions, additive only: (1) Header documents the baseline + recovery procedure. (2) Python 3.12 build-venv gate with hard ERROR + recovery hint. (3) Step 0 deterministic `rmdir /s /q build dist` cleanup. (4) `--noupx` flag. (5) 8 `--exclude-module=` flags for unused stdlib. |
| Existing scaffold contents | Preserved verbatim. Only the 4 frozen-build-relevant fields changed. |

PCC's own `build.bat` was NOT modified — PCC's retrofit is Phase 3C,
separate work. PCC's `phoenix_tool_templates.py` is the wizard machinery
that generates other tools; this commit updates the templates only.

## 5. Generated scaffold validation

Throwaway scaffold generated at
`%LOCALAPPDATA%\ATS Inc\PhoenixScaffoldVerify\phoenix-verify\` for
verification only. NOT committed; NOT built into a frozen exe; NOT
deployed.

27 files generated by `template_phoenix_standalone("phoenix-verify")`.
Inspection results:

| Check | Result |
|-------|--------|
| Generated `requirements.txt` content | `PySide6==6.10.2` (matches baseline) |
| Generated `requirements-dev.txt` content | `pyinstaller==6.20.0` + comment block referencing FROZEN_BUILD_BASELINE.md |
| Generated `build.bat` — Python 3.12 gate | ✓ present at line 24 (`if not "%PYVER%"=="3.12"`) |
| Generated `build.bat` — Step 0 cleanup | ✓ present at lines 56–57 |
| Generated `build.bat` — `--noupx` flag | ✓ present |
| Generated `build.bat` — 8 stdlib excludes | ✓ all present (tkinter, _tkinter, tcl, tk, lib2to3, idlelib, turtle, turtledemo) |
| Generated `installer.iss` — naming convention | ✓ `MyAppName=Phoenix Verify`, `OutputBaseFilename=PhoenixVerifySetup` |
| Generated `version.py` — format | ✓ `__version__ = "0.1.0"` |
| Generated `tests/test_smoke.py` — conventions | ✓ pytest + pytest-qt fixtures, smoke-test module-imports/version-format/MainWindow |
| `py -3.12 -m compileall -q <scaffold>` | ✓ clean exit |

The scaffold is structurally sound and ready for source-mode work.
**No PyInstaller build was attempted in this verification step** per
spec ("source-mode sanity check is sufficient").

## 6. Operational implications

| Implication | Effect |
|-------------|--------|
| New tools scaffolded via the wizard automatically inherit the hardened baseline | Future tools start with explicit `--noupx`, stdlib excludes, Python 3.12 gate, pinned PyInstaller + PySide6. No per-tool hardening retrofit needed. |
| `build.bat` enforces Python 3.12 at runtime | Developer trying to build with a 3.14 venv gets an explicit ERROR with recovery instructions, rather than a silent S1 quarantine. |
| Existing production tools' `build.bat` files are now drift-from-template | The 4 production tools' build.bat files still don't have the hardening (they were last rebuilt pre-hardening). When they retrofit, they should adopt the same template pattern. |
| Source-mode work is unchanged | Developers can continue using Python 3.10/3.13/3.14 venvs for source-mode development. Only frozen builds are constrained. |
| CI workflows (all 5 retrofit-family CIs already on 3.12 per the Operational Convergence Phase) are aligned | CI signal matches build signal. |
| The `BUILD_HARDENING_EXPERIMENT_REPORT_*` chain becomes the audit-trail for any IT/security review | Each step of the evidence chain is reproducible from the saved docs. |

## 7. Remaining risks

| Risk | Severity | Mitigation status |
|------|----------|---------------------|
| Python 3.12 EOL (Oct 2028) | Long-term | Re-isolation experiment required when bumping; protocol documented in FROZEN_BUILD_BASELINE.md § 5. |
| PyInstaller 6.21+ release | Low (additive) | Re-isolation experiment required before bumping the pin. |
| PySide6 6.10.x → 6.11.x bump | Low | Same: re-validate on Python 3.12. |
| S1 heuristic database updates that target 3.12 bootloaders too | Medium | Mitigation = pursue code signing per BLOCKERS.md § 1 option 2 + IT/S1 allow-list (option 1). Out-of-band; tracked. |
| Production tool retrofits (Phase 3C / 8a / 8b) producing new exes that DON'T survive | Medium | Per-tool dry-run on throwaway clone before touching the production repo. Documented in EXPERIMENT_REPORT_03 § 8. |
| Production tool surface-area mismatches (Phoenix CAD's COM modules, Job Tracker's pyxlsb, etc.) on Python 3.12 | Medium | Verify in dry-run; pywin32 supports 3.12 fine, pyxlsb is pure Python. Should not block. |
| Developer using the wrong venv | Low | `build.bat` now enforces explicitly. |

## 8. Whether production rebuilds are now safer

**Yes — but per-tool dry-run validation is still mandatory before any
production rebuild.**

Improvements since EXPERIMENT_REPORT_02:

- **Mechanism is now known** (A3-i isolation). The Python 3.12 venv is
  the primary requirement; the other 6 hardening variables are
  hygiene + explainability.
- **Hardened baseline is frozen + canonical** (this report + FROZEN_BUILD_BASELINE.md).
- **Wizard template emits hardening by default** — fresh tools start green.
- **Doctrine references the baseline** so reviewers + future maintainers
  have a single source of truth.

Remaining caveats (unchanged from EXPERIMENT_REPORT_03 § 8):

- Production tools have larger module surfaces (win32com / pythoncom for
  Phoenix CAD; pyxlsb + openpyxl for Job Tracker; XLSX files for
  Phoenix Checkout; base64 assets for Phoenix Master Tool). All compatible
  with Python 3.12, but per-tool dry-run before commitment.
- Production `build.bat` files don't have the hardening yet. Adoption is
  a per-tool retrofit, not a sweeping change.
- Production tools' currently-deployed exes are stable on user machines.
  No urgency to rebuild.

Recommended production rebuild sequence (when authorised — DEFERRED):

1. Phoenix CAD first (already pins PyInstaller 6.20.0; smallest delta
   from baseline).
2. Job Tracker (add pinned `requirements-dev.txt` first).
3. Phoenix Checkout (smallest module surface).
4. Phoenix Master Tool (Ubuntu CI already on 3.10/3.11/3.12 matrix).

Each as: throwaway clone → apply baseline → rebuild → observe S1 →
if green, apply to production repo on a feature branch with full
release-checklist gating.

## 9. Whether Phase 6C can now resume safely

**Yes — Phase 6C readiness is restored.**

Phase 6C's plan (`docs/rollout/phase-6c-frozen-exe-dogfood-plan.md`)
was blocked by BLOCKERS.md § 1 (S1 quarantine). The hardened baseline
removes that blocker for the standalone-scaffold dogfood path:

| Phase 6C step | Status |
|---------------|--------|
| 1. Scaffold a fresh standalone tool via the wizard | ✓ ENABLED. Wizard now emits hardened baseline by default; this report verified the output. |
| 2. Source-mode validation (compileall, pytest, offscreen MainWindow) | ✓ ENABLED. Same as Experiment Report 01 — already proven green. |
| 3. PyInstaller build under the hardened baseline | ✓ ENABLED. Proven by B1 + B2 (twice). |
| 4. Inno Setup compile | ✓ ENABLED. Already worked in Experiment 01 + 02. |
| 5. Local smoke install (run Setup.exe; launch installed app; verify user-data folder) | ⚠ NOT YET RUN. This is the next Phase 6C step. Requires explicit user authorisation since it executes the installer + the installed exe. |
| 6. Uninstall round-trip | ⚠ NOT YET RUN. Same. |
| 7. Auto-updater dry-run against a fake GitHub Release | ⚠ NOT YET RUN. Same. |

Steps 1–4 are the "build" half. Steps 5–7 are the "deploy / runtime"
half. The build half is unblocked; the deploy half requires user
authorisation per the established phase boundaries.

**This report does NOT resume Phase 6C.** It only restores readiness.
Resumption is a follow-up phase requiring explicit authorisation.

Recommended next step for Phase 6C resumption (when authorised):

- Phase 6C-A: Source-build dogfood under the hardened baseline on
  the standalone scaffold (steps 1–4 above). One throwaway scaffold,
  one build, verify all artifacts. Already mostly done by experiments
  01–02; could be re-run for fresh evidence under the now-canonical
  template.
- Phase 6C-B: Local smoke install (step 5). Run Setup.exe in a
  controlled directory. Verify installed app launches. Confirm
  user-data folder created. Uninstall round-trip.
- Phase 6C-C: Auto-updater dry-run (steps 6–7).
- Phase 6C-D: Tag PCC v2.0.0 + first official release.

## 10. Confirmation

| Item | Status |
|------|--------|
| No production rebuilds occurred | ✅ |
| No production tool source modified | ✅ |
| No production tool venvs modified | ✅ |
| No installer execution | ✅ — Throwaway scaffold's installer.iss generated but no ISCC invocation |
| No frozen-exe rollout | ✅ — No PyInstaller build attempted in Step 4 |
| No release publishing | ✅ |
| No AV bypass behavior | ✅ |
| No obfuscation introduced | ✅ |
| No anti-analysis behavior introduced | ✅ |
| No security controls disabled | ✅ |
| No further speculative experiments | ✅ — This phase consolidates existing experiment results |
| Source-mode flexibility preserved (any Python 3.10–3.14) | ✅ |
| Wizard scaffold output verified | ✅ — 27 files, all hardening flags present, compileall green |

| Field | Value |
|-------|-------|
| Phase | Build Hardening Phase 6D — baseline integration |
| Status | ✅ Complete — hardened baseline frozen into doctrine + templates |
| Date | 2026-05-20 |
| Commits this phase | 4 across 2 repos |
| — Commit 1 (commons) | `e8c5873` — FROZEN_BUILD_BASELINE.md (new) |
| — Commit 2 (commons) | `1ea74e1` — 4 doctrine doc updates |
| — Commit 3 (PCC) | `9f1f3ea` — wizard template hardening defaults |
| — Commit 4 (commons) | (this report) |
| Files modified in production-tool repos | 0 |
| Files modified in commons | 5 (new FROZEN_BUILD_BASELINE.md + 4 doctrine doc updates + this report) |
| Files modified in PCC | 1 (phoenix_tool_templates.py) |
| Throwaway verification scaffold | `%LOCALAPPDATA%\ATS Inc\PhoenixScaffoldVerify\phoenix-verify\` (27 generated files; NOT committed) |
| Saved to | `phoenix-commons/docs/ui-platform-baseline-v1/BUILD_HARDENING_BASELINE_INTEGRATION_REPORT.md` |
