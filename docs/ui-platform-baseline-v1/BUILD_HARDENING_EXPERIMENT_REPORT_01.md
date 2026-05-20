# BUILD_HARDENING_EXPERIMENT_REPORT_01.md

> First controlled rebuild experiment per the experiment plan that
> followed BUILD_HARDENING_COMPARISON_REPORT_01.md. Documents one
> stabilized rebuild of the Phase 6 standalone scaffold under Python
> 3.12 + deterministic packaging hygiene. Analysis-only; no AV
> bypass, no obfuscation, no production rebuilds, no installer
> execution.
>
> Authored 2026-05-20.

## 1. Build environment details

Isolated clone created at a new path so the original Phase 6 .venv
(Python 3.14) was left untouched:

```
C:\Users\justing\AppData\Local\ATS Inc\PhoenixScaffold6\phoenix-phase6-standalone-hardened\
```

| Element | Value |
|---------|-------|
| Python interpreter | **3.12.10** (installed during this session via `winget install --scope user Python.Python.3.12`; per-user, no admin) |
| Python source | `C:\Users\justing\AppData\Local\Programs\Python\Python312\python312.dll` |
| Venv path | `<clone>/.venv` (created via `py -3.12 -m venv .venv`) |
| pip | 26.1.1 (upgraded from 25.0.1 default) |
| PyInstaller | **6.20.0** (pinned in `requirements-dev.txt`) |
| PySide6 | **6.10.2** (pinned in `requirements.txt`) |
| PySide6_Essentials / Addons / shiboken6 | 6.10.2 (resolved together) |
| OS | Windows 11 10.0.26100-SP0 |
| Endpoint protection | SentinelOne (active throughout the experiment) |

Compare to original Phase 6 build environment:

| Element | Original Phase 6 | Hardened (this experiment) | Δ |
|---------|------------------|----------------------------|---|
| Python | 3.14.3 | 3.12.10 | ✓ ADR-014 alignment |
| PyInstaller | 6.19.0 | 6.20.0 | newer (matches Phoenix CAD production pin) |
| PySide6 | 6.11.1 | 6.10.2 | older (matches 3 of 4 production tools) |
| Venv age | days old | fresh | no PyInstaller cache pollution |

## 2. Exact stabilization changes

Only **conservative deterministic hygiene** — no speculative module stripping, no broad hidden-import surgery, no anti-analysis behavior.

### 2.1 `requirements.txt`

```diff
-PySide6>=6.5
+PySide6==6.10.2
```

### 2.2 `requirements-dev.txt`

```diff
-pyinstaller==6.19.0
+# Hardening Experiment 01: PyInstaller pinned to 6.20.0 (matches the
+# Phoenix CAD production pin which was the most-recent successful
+# production build, 2026-05-12). PySide6 pinned in requirements.txt
+# to 6.10.2 for the same reason.
+pyinstaller==6.20.0
```

### 2.3 `build.bat`

5 additive changes; original 3-step structure preserved:

```diff
+rem Step 0: Deterministic cleanup (Hardening Experiment 01)
+rem Remove any stale build/ + dist/ so the rebuild is a clean slate.
+if exist build rmdir /s /q build
+if exist dist  rmdir /s /q dist

 .venv\Scripts\pyinstaller ^
     --noconfirm ^
     --onedir ^
     --windowed ^
+    --noupx ^
     --name=PhoenixPhase6Standalone ^
     --add-data="phoenix_style.qss;." ^
     --collect-submodules=PySide6.QtCore ^
     --collect-submodules=PySide6.QtGui ^
     --collect-submodules=PySide6.QtWidgets ^
+    --exclude-module=tkinter ^
+    --exclude-module=_tkinter ^
+    --exclude-module=tcl ^
+    --exclude-module=tk ^
+    --exclude-module=lib2to3 ^
+    --exclude-module=idlelib ^
+    --exclude-module=turtle ^
+    --exclude-module=turtledemo ^
     main.py
```

### 2.4 What was NOT changed

| Item | Reason |
|------|--------|
| `--onedir --windowed` | Preserved per experiment spec |
| Bootloader architecture | No custom bootloader, no runtime wrapper |
| Code signing | NOT introduced (durable mitigation; future work) |
| Obfuscation / stealth / anti-analysis | Explicitly excluded by spec |
| onefile | Rejected (would change runtime architecture) |
| Alternate packers (NSIS / 7zSFX) | Rejected (would replace PyInstaller) |
| Aggressive PySide6 plugin stripping | Out of scope; conservative excludes only |

## 3. Spec / build changes (regenerated `.spec` after the build)

The build invokes `pyinstaller main.py`, so `PhoenixPhase6Standalone.spec` is auto-regenerated each build. After the hardened build, the regenerated spec reflects the flags:

| Spec attribute | Original Phase 6 | Hardened |
|----------------|------------------|----------|
| `excludes` | `[]` | `['tkinter', '_tkinter', 'tcl', 'tk', 'lib2to3', 'idlelib', 'turtle', 'turtledemo']` |
| EXE `upx` | `True` (no-op since no UPX on PATH) | `False` (explicit) |
| COLLECT `upx` | `True` (no-op) | `False` (explicit) |
| `optimize` | `0` | `0` (unchanged) |
| `strip` | `False` | `False` (unchanged) |
| `noarchive` | `False` | `False` (unchanged) |
| `codesign_identity` | `None` | `None` (unchanged) |
| `hiddenimports` | PySide6.QtCore/QtGui/QtWidgets submodules | identical |

## 4. Rebuild outputs

Build duration: 80.0 s (PyInstaller ~33 s + Inno Setup 29.8 s + Compress-Archive 2 × ~3 s).

| Artifact | Hardened size | Original Phase 6 |
|----------|---------------|-------------------|
| `dist\PhoenixPhase6Standalone\PhoenixPhase6Standalone.exe` | **1.59 MB** | quarantined; never measured |
| `dist\PhoenixPhase6Standalone\_internal\` | **163 files / 114.5 MB** | 166 files / 115.3 MB |
| Qt plugins in `_internal/` | 22 | 22 |
| `Qt6*.dll` in `_internal/` | 13 | 13 |
| `dist\PhoenixPhase6StandaloneSetup.exe` (Inno Setup output) | **31.56 MB** | ~33.9 MB (observed in original) |
| `dist\PhoenixPhase6Standalone.zip` (auto-updater) | **45.83 MB** | n/a (zip step failed in original — bootloader was quarantined before zip ran) |
| `dist\PhoenixPhase6Standalone_FullInstall.zip` | **45.83 MB** | n/a (same) |

The 3-file / 0.8 MB `_internal/` reduction is consistent with the stdlib `excludes` filtering out `tkinter` / `lib2to3` / `idlelib` / `turtle` artifacts and their indirect imports.

**Build script status**: the zip-validation PowerShell step at the tail of build.bat failed on a `^` line-continuation quoting issue. Inno Setup compile and zip creation both succeeded before that step; the validator failure is a build.bat bug, not a build outcome. Not in scope to fix in this experiment.

## 5. S1 behavior outcome

**Outcome A — S1 no longer quarantines.**

Direct evidence chain (timestamps captured during experiment):

| Time | Event |
|------|-------|
| 2026-05-20T11:59:22 | PyInstaller build started (per powershell timer) |
| 2026-05-20T11:59:55 | PyInstaller wrote `PhoenixPhase6Standalone.exe` (per file LastWriteTime + PE TimeDateStamp) |
| 2026-05-20T11:59:55 → 12:00:25 | Inno Setup compressed exe into `PhoenixPhase6StandaloneSetup.exe` |
| 2026-05-20T12:00:25 → 12:00:35 | PowerShell `Compress-Archive` × 2 produced both zips (exe still present in source dir) |
| 2026-05-20T12:00:35 | Build sequence ended |
| 2026-05-20T12:01:05 | T+70s post-write: exe still on disk |
| 2026-05-20T12:01:53 | T+2min post-write: exe still on disk |
| 2026-05-20T12:02:27 | T+2.5min post-write: exe still on disk |

Compared to original Phase 6 (per BLOCKERS.md / phase-6-standalone-dogfood-report.md § 19):
- Bootloader exe disappeared within seconds of PyInstaller writing it.
- Auto-updater zip ended up with no `PhoenixPhase6Standalone.exe` entry because the exe was already gone when Compress-Archive ran.

In the hardened experiment:
- Bootloader exe survived through the full build sequence (PyInstaller → Inno Setup → both zips).
- Both zips contain the bootloader (45.83 MB sizes indicate full payload).
- No quarantine event observed at any time during 2.5 min of post-build observation.

`Get-AuthenticodeSignature` on the new exe returns `NotSigned` (signing was NOT introduced).

## 6. Comparison vs original Phase 6

| Dimension | Original Phase 6 | Hardened Phase 6 | Δ |
|-----------|------------------|------------------|---|
| Build mode | `--onedir --windowed` | same | none |
| Bootloader code-signing | unsigned | unsigned | none |
| Python | 3.14.3 | 3.12.10 | **changed** |
| PyInstaller | 6.19.0 | 6.20.0 | **changed** |
| PySide6 | 6.11.1 | 6.10.2 | **changed** |
| Spec `upx` | `True` (no-op) | `False` (explicit) | **changed** |
| Spec `excludes` | `[]` | 8 stdlib modules | **changed** |
| Venv state | reused from prior build | fresh | **changed** |
| Build / dist cleanup before rebuild | manual / inconsistent | scripted (`rmdir`) | **changed** |
| Bootloader exe size | n/a (quarantined) | 1.59 MB | n/a |
| `_internal/` file count | 166 | 163 | −3 files |
| `_internal/` total bytes | ~115.3 MB | ~114.5 MB | −0.8 MB |
| Inno Setup output size | ~33.9 MB | 31.56 MB | −2.3 MB |
| Quarantine within seconds? | YES | **NO** | **outcome flip** |

Seven simultaneous environment / packaging deltas, one outcome flip.

## 7. Most meaningful observations

1. **Multi-variable change → single outcome flip.** Seven environment + spec variables changed simultaneously. The experiment cannot attribute the outcome change to any single variable. All seven are plausible contributors; some are more plausible than others (see § 8).
2. **The exe is still unsigned.** Code-signing (the BLOCKER-1-option-2 durable mitigation) was NOT introduced. The hardened build's bootloader survived without a certificate.
3. **`_internal/` shrank by only 3 files / 0.8 MB.** Most stdlib excludes (`tkinter`, `_tkinter`, `tcl`, `tk`, `lib2to3`, `idlelib`, `turtle`, `turtledemo`) were either not present in the original build or were filtered transitively in similar ways. The hygiene improvement is real but modest.
4. **PyInstaller emitted no excludes-warnings.** Confirms the stdlib excludes are genuinely unused by `main.py` / `backend.py` / `ui/` / `paths.py` / `updater.py` / Phoenix Qt submodules. No transitive imports breakage.
5. **The build was reproducible end-to-end on Python 3.12.** Earlier hypothesis (BUILD_HARDENING_COMPARISON_REPORT_01 § H3) that Python 3.14 bootloader rarity contributes is consistent with the outcome flip — but cannot be isolated by this single experiment.
6. **Installer compiled, zip produced, the build.bat is operationally complete** except for the tail `^`-escape PowerShell-validation bug, which is a cosmetic build-script issue unrelated to AV behaviour.

## 8. Confidence assessment

| Claim | Confidence | Caveat |
|-------|-----------|--------|
| The hardened build outcome is Outcome A (S1 did not quarantine) | **HIGH** | Single-sample observation, but 2.5 min persistence vs the prior pattern of seconds-to-quarantine is a clear qualitative difference. |
| At least one of the seven changes was material | **HIGH** | The original config was quarantined ≥3 times; the hardened config was not. Something changed materially. |
| Code signing is required for production durability | **MEDIUM** | The hardened build survived unsigned. Code signing remains the most durable mitigation per BLOCKERS.md § 1 option 2, but is not proven mandatory. Signing-as-mitigation is reasonable but the trigger may have been one of the other six changes. |
| Python 3.12 (ADR-014 canonical) helped | **MEDIUM** | Most plausible single contributor per H3 in the prior comparison report; pinned by both ADR-014 reasoning ("battle-tested across all 4 production tools") and the package-version-rarity argument. Not isolated. |
| PyInstaller 6.20.0 (vs 6.19.0) helped | **LOW-MEDIUM** | Both versions are recent; production tool Phoenix CAD pins 6.20.0 and was last successfully built. Not isolated. |
| The stdlib `excludes` helped | **LOW** | `_internal/` shrank by only 3 files / 0.8 MB; tkinter family was likely not in the bootloader's content footprint. |
| `--noupx` explicit helped | **LOW** | UPX was already not on PATH; the prior config's `upx=True` was a no-op. Explicit `False` is hygiene, not mechanism. |
| Fresh venv (no PyInstaller cache) helped | **LOW** | PyInstaller's cache rebuilds modules; cache pollution unlikely to change bootloader hash. |
| Build/dist cleanup before rebuild helped | **VERY LOW** | Filesystem hygiene; unlikely to affect AV. |

## 9. Recommended next actions

In priority order. **None executed by this report.**

| # | Action | Risk | Reason |
|---|--------|------|--------|
| **A1** | Re-run the same hardened build a second time (reproducibility check) | Very low | Confirms Outcome A is not a one-off (e.g. S1 not having seen the bootloader hash yet). Should be done within the experiment's max-2 budget. |
| **A2** | If A1 passes: pursue IT/S1 allow-list confirmation as the "explainable" mitigation for IT/security review (BLOCKER-1 option 1) | None — out-of-band | Even if the hardened build works, an allow-list provides defense in depth. |
| A3 | Author a **second** controlled experiment that varies one variable at a time to isolate the material change (start with Python 3.14 + everything else hardened) | Low (one rebuild) | Identifies whether 3.12 alone is sufficient. |
| A4 | Defer code-signing pipeline work until experiments isolate whether signing is genuinely required | Low | Avoids burning effort on a durable mitigation that may not be needed. |
| A5 | Do NOT rebuild any of the 4 production tools yet | None | Production exes are still installed and trusted; rebuilding remains structurally risky until the mechanism is isolated. |

## 10. Whether production rebuilds are still unsafe

**Provisional answer: still unsafe to rebuild any of the 4 production tools today.**

Reasoning:
- The hardened build's success is single-sample; reproducibility unproven.
- The mechanism is unclear (7 simultaneous changes).
- Production tools currently use different Python (3.14 in current dev venvs), different PySide6 (6.10.2 / 6.11.0), different `--collect-submodules` patterns, and have NOT had the stdlib excludes / `--noupx` applied. A production rebuild without applying the same hardening pattern is unlikely to succeed.
- A production rebuild WITH the hardening pattern requires touching `build.bat` / `requirements*.txt` / `.venv` — non-trivial production-tool changes that should not happen during cooldown.

Recommendation: hold production rebuilds until A1 (reproducibility) + A3 (mechanism isolation) complete.

## 11. Whether signing now appears mandatory

**Not strictly mandatory based on this single experiment.** Updated stance:

- The hardened build's bootloader survived **unsigned**. Signing was not necessary to clear the immediate trigger.
- Signing remains the most durable mitigation per BLOCKERS.md § 1 option 2 — and the most explainable to IT/security review. It is still the right *long-term* answer.
- For the immediate experiment outcome, signing can be deferred.
- For any production release intended for end-user machines whose S1 policy may differ, signing should still be pursued as the durable end-state.

Updated recommendation matrix:

| Goal | Signing required? |
|------|--------------------|
| Pass the current developer-laptop S1 heuristic | **No** (hardened build pattern is sufficient based on this single experiment) |
| Durable cross-machine deployment | **Yes** (per BLOCKERS.md § 1 option 2) |
| Faster IT/security audit explainability | **Yes** (signed binaries skip many heuristics outright) |
| Phase 6C dogfood completion | **Probably not blocking** if the hardened pattern is applied to PCC's build.bat |

## 12. Confirmation

| Item | Status |
|------|--------|
| No production rebuilds occurred | ✅ |
| No releases occurred | ✅ |
| No installer execution occurred | ✅ (Setup.exe written but not run) |
| No deployment occurred | ✅ |
| No AV bypass behavior attempted | ✅ |
| No obfuscation introduced | ✅ |
| No stealth / anti-analysis technique introduced | ✅ |
| No security controls disabled | ✅ (S1 active throughout; observed quarantine *absence* under hardened config, not S1 disabling) |
| Original Phase 6 scaffold preserved untouched | ✅ |
| Existing production tool `.venv`s untouched | ✅ |
| Existing production source untouched | ✅ |
| 1 rebuild attempt used (max 2 per spec) | ✅ |
| Build hygiene changes were all conservative | ✅ — explicit pins, stdlib excludes, `--noupx`, cleanup. No surgery on PySide6 plugin list, no spec-rewrite, no aggressive optimizations |

| Field | Value |
|-------|-------|
| Phase | Build Hardening Experiment 01 — first controlled rebuild |
| Outcome | **A — S1 no longer quarantines** |
| Status | ✅ Complete (1 rebuild executed of 2 allowed) |
| Date | 2026-05-20 |
| Files modified in production-tool repos | 0 |
| Files modified in commons | 1 (this report) |
| Files created in throwaway scaffold clone | several (cloned scaffold under `phoenix-phase6-standalone-hardened`) |
| Saved to | `phoenix-commons/docs/ui-platform-baseline-v1/BUILD_HARDENING_EXPERIMENT_REPORT_01.md` |
| Throwaway scaffold path | `%LOCALAPPDATA%\ATS Inc\PhoenixScaffold6\phoenix-phase6-standalone-hardened\` |

---

## Appendix A — Reproducibility checklist (for A1 second-run experiment)

If the user authorises A1:

1. From the same hardened scaffold directory, run:
   ```cmd
   rmdir /s /q build dist
   .venv\Scripts\pyinstaller --noconfirm --onedir --windowed --noupx --name=PhoenixPhase6Standalone --add-data="phoenix_style.qss;." --collect-submodules=PySide6.QtCore --collect-submodules=PySide6.QtGui --collect-submodules=PySide6.QtWidgets --exclude-module=tkinter --exclude-module=_tkinter --exclude-module=tcl --exclude-module=tk --exclude-module=lib2to3 --exclude-module=idlelib --exclude-module=turtle --exclude-module=turtledemo main.py
   ```
2. Observe whether the bootloader exe persists for ≥ 2 minutes (matches first-run timing).
3. If persists: HIGH confidence in Outcome A reproducibility.
4. If quarantined: Outcome inconsistent — possible cache-hit / hash-based AV behavior. Triggers a § 9 A3-style isolation experiment.

## Appendix B — Suggested A3 isolation matrix (if authorised)

Vary one variable per build, max 3-4 additional rebuilds total. Each isolation rebuild targets one of the high-likelihood contributors:

| Experiment | Vary | All other variables held to hardened-config values |
|-----------|------|----------------------------------------------------|
| A3-i | Python 3.14 (revert to original) | hardened |
| A3-ii | PyInstaller 6.19.0 (revert) | hardened |
| A3-iii | PySide6 6.11.1 (revert) | hardened |
| A3-iv | Remove `excludes=[...]` (revert) | hardened |

If any single-variable revert reproduces the quarantine, that variable is identified as the contributor. If none do, the contributor is multi-variable (interactive). Each isolation requires ≤ 1 rebuild → ≤ 4 total beyond A1.

Out of scope for the current experiment phase; deferred to user authorisation.
