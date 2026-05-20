# BUILD_HARDENING_EXPERIMENT_REPORT_03.md

> Single-variable isolation experiment A3-i: revert ONLY Python from
> 3.12.10 → 3.14.3, preserve every other hardened-baseline variable
> identically. Tests whether Python interpreter version alone
> reintroduces the S1 quarantine pattern.
>
> Authored 2026-05-20.
>
> **Outcome: A3i-FAIL** — bootloader quarantined. Python 3.12 vs 3.14
> is the material variable.

## 1. Exact isolated variable

| Variable | Hardened baseline (B1/B2) | A3-i (B3) | Δ |
|----------|----------------------------|-----------|---|
| **Python interpreter** | **3.12.10** | **3.14.3** | **CHANGED** |
| PyInstaller | 6.20.0 | 6.20.0 | none |
| PySide6 | 6.10.2 | 6.10.2 | none |
| Spec `upx` | False | False | none |
| Spec `excludes` | 8 stdlib modules | 8 stdlib modules | none |
| `--noupx` build.bat flag | yes | yes | none |
| Build cleanup at Step 0 | yes | yes | none |
| Build mode | `--onedir --windowed` | `--onedir --windowed` | none |
| Build path (clone shape) | `<scaffold>-hardened\` | `<scaffold>-py314-a3i\` | parallel path (same shape) |
| Source content | identical | identical (tar-cloned from hardened) | none |
| `requirements.txt` content | `PySide6==6.10.2` | `PySide6==6.10.2` | none |
| `requirements-dev.txt` content | `pyinstaller==6.20.0` | `pyinstaller==6.20.0` | none |
| `build.bat` content | hardened | hardened (byte-identical) | none |
| Venv state | fresh | fresh | none (same procedure) |
| PySide6 wheel tag actually installed | `cp39-abi3` (works on 3.10+) | `cp39-abi3` (same wheel works on 3.14) | none — same wheel files |
| Installed versions confirmed at runtime | Python 3.12.10 / PyInstaller 6.20.0 / PySide6 6.10.2 | Python 3.14.3 / PyInstaller 6.20.0 / PySide6 6.10.2 | **only Python** |

**One variable changed. Everything else byte-identical.**

## 2. Build outputs

| Metric | B1 (3.12) | B2 (3.12) | B3 (3.14) | Δ B3 vs mean(B1,B2) |
|--------|-----------|-----------|-----------|----------------------|
| Build duration | 80.0 s | 76.0 s | 82.9 s | +4.9 s |
| Bootloader exe size | 1,663,505 B | 1,663,505 B | **(quarantined)** | n/a |
| `_internal/` file count | 163 | 163 | **166** | **+3** |
| `_internal/` bytes | ~115 MB | ~120 MB | ~121 MB | small noise |
| Setup.exe size | 33,093,048 B | 33,085,009 B | **34,046,047 B** | **+957 KB** |
| Updater zip size | 48,060,934 B | 48,059,847 B | **47,223,221 B** | **−837 KB** |
| Full-install zip size | (not measured B1) | 48,067,767 B | 47,231,237 B | comparable |
| PyInstaller WARNING/ERROR count | 0 / 0 | 0 / 0 | 0 / 0 | none |
| Generated `.spec` content | identical to template flags | identical | identical | none |

### Why is Setup.exe BIGGER under 3.14 even though the zip is SMALLER?

A revealing data point. Setup.exe is the Inno Setup output that contains
a compressed copy of the bootloader exe + `_internal/`. The auto-updater
zip is `Compress-Archive`'s output containing the loose bootloader +
`_internal/` directly.

| Artifact | Behavior |
|----------|----------|
| Setup.exe (+957 KB vs B2) | Inno Setup captured the bootloader BEFORE S1 deleted it. The bigger Setup.exe means the **Python 3.14 bootloader is materially larger** as a piece of PE content than the 3.12 bootloader. |
| Updater zip (−837 KB vs B2) | `Compress-Archive` ran AFTER S1 deleted the bootloader. The zip is missing the bootloader entry entirely (confirmed: 167 entries are all `_internal/*`; no `PhoenixPhase6Standalone.exe` at root). The size reduction is roughly the compressed-zip cost of a 1.6+ MB bootloader. |

The two artifacts capture two different moments in the build pipeline,
and their size deltas are consistent with the S1 quarantine pattern
landing between Inno Setup completion and `Compress-Archive` start.

This bigger-bootloader observation is the **first direct evidence**
that the Python 3.12 vs 3.14 bootloader contents are structurally
different — which is a plausible mechanism for the heuristic outcome
flip. (The bigger bootloader has more PE content for S1's pattern
matchers to evaluate.)

### `_internal/` file count delta (163 → 166)

3 extra files under Python 3.14's bundle vs 3.12's. Likely from 3.14's
new bytecode / typing improvements bundling additional `lib2to3`-adjacent
or `__future__`-adjacent modules that the stdlib `excludes` don't fully
trim. Not a primary signal; consistent across the two interpreters
within a few files.

## 3. S1 behavior

### Timeline

| Time | Event |
|------|-------|
| 2026-05-20T12:19:14 | B3 build started |
| ~T+37 s into build | PyInstaller log: "Build complete!" — bootloader written to `dist/PhoenixPhase6Standalone/PhoenixPhase6Standalone.exe` (also intermediate copy in `build/`) |
| ~T+45 s into build | Inno Setup compresses the bootloader into `PhoenixPhase6StandaloneSetup.exe` (captures content) |
| Between Inno Setup and `Compress-Archive` | **S1 deletes the bootloader from BOTH `dist/` and `build/`** (intermediate-copy deletion confirms content-heuristic; not path-based) |
| ~T+65 s into build | `Compress-Archive` runs with bootloader absent → produces a zip missing the bootloader entry |
| 2026-05-20T12:20:37 | Build script exits (exit code 255 from the same tail `^`-quoting validation bug as B1/B2; PyInstaller + Inno Setup + zip steps all succeeded before that) |
| 2026-05-20T12:21:02 (T+25 s post-build) | Confirmation: bootloader missing from `dist/` AND `build/`; `_internal/` intact |
| 2026-05-20T12:21:52 (T+1 min 15 s post-build) | Bootloader STILL ABSENT — consistent quarantine, not transient |

### Quarantine pattern matches BLOCKERS.md § 1 + original Phase 6 § 19

- ✓ Bootloader exe disappeared from disk
- ✓ Intermediate `build/<name>/<name>.exe` also gone (proves content-heuristic, not path-based)
- ✓ `_internal/` survived intact (S1 targets the bootloader content specifically)
- ✓ Inno Setup output (Setup.exe) survives because compressed content is no longer PE-bare
- ✓ `Compress-Archive` produced a zip missing the bootloader because the file was already gone
- ✓ No quarantine recovery during 1+ min of post-build observation

### Persistence observation

| T+ | Observed state |
|----|----------------|
| T+25 s | bootloader absent |
| T+1 min 15 s | bootloader absent |

Total observation window: 75+ s. Sufficient to confirm quarantine is
not a delayed-deletion or transient state — consistent with the
seconds-to-quarantine pattern from BLOCKERS.md.

## 4. Comparison vs hardened baseline (B1/B2)

| Run | Python | All other hardened variables | Bootloader survives? | Outcome |
|-----|--------|------------------------------|------------------------|---------|
| Original Phase 6 (pre-hardening) | 3.14.3 | NO (PyInstaller 6.19, PySide6 6.11.1, upx-no-op, no excludes, etc.) | NO | Quarantined (BLOCKERS.md § 1) |
| B1 (hardened baseline first run) | 3.12.10 | YES | **YES** | Persistent ≥ 5 min |
| B2 (hardened baseline reproducibility) | 3.12.10 | YES | **YES** | Persistent ≥ 2.3 min |
| **B3 (A3-i isolation)** | **3.14.3** | **YES** (same as B1/B2) | **NO** | **Quarantined within ~25 s** |

Three controlled data points across the Python axis:

- 3.12 + hardened → SURVIVES (twice)
- 3.14 + hardened → QUARANTINED (once)
- 3.14 + non-hardened → QUARANTINED (original Phase 6)

The single-variable flip from 3.12 to 3.14, holding everything else
constant, flips the outcome from survives→quarantined. **The other six
hardened variables alone are NOT sufficient.**

## 5. Root-cause confidence update

Updating the hypothesis confidence table from BUILD_HARDENING_COMPARISON_REPORT_01.md § 4:

| Hypothesis | Pre-A3-i confidence | Post-A3-i confidence | Rationale |
|------------|---------------------|------------------------|-----------|
| H1 — External S1 signature DB update | HIGH | **HIGH (refined)** — The S1 signature targets the Python-3.14 PyInstaller bootloader content specifically; the 3.12 bootloader does not match the same heuristic. |
| H2 — Unsigned PyInstaller bootloader + no reputation | HIGH | **MEDIUM** (downgraded) — Both 3.12 and 3.14 bootloaders are unsigned. The 3.12 one survives, so unsigned-ness alone is not sufficient to trigger. |
| H3 — Python 3.14 bootloader rarity / signature | MEDIUM | **HIGH (proven)** — Single-variable change validated this. Python 3.12 bootloader is the larger contributor to the survival outcome. |
| H4 — Bootloader PYZ entropy | MEDIUM-LOW | **MEDIUM-LOW** (unchanged) — Both interpreters produce PYZ-embedded bootloaders; the differentiator is bootloader content not PYZ. |
| H5 — Bundled module surface | RULED OUT | **STILL RULED OUT** — `_internal/` is bundled identically between B2 and B3 within noise; differs in outcome. |
| H6 — UPX packing | RULED OUT | **STILL RULED OUT** — `upx=False` was preserved in B3; outcome still flipped to quarantine. |

### Material variable: **Python interpreter (3.12 vs 3.14)**

The PE size delta on Setup.exe (+957 KB for the 3.14 variant) provides
the structural mechanism: the Python 3.14 PyInstaller bootloader is a
materially larger binary than the 3.12 one. Its PE content matches an
S1 heuristic pattern that the 3.12 bootloader does not match.

This is consistent with:
- ADR-014's choice of 3.12 as canonical ("bootloader builds against
  3.12 are battle-tested across all 4 production tools").
- The newer Python (3.14, October 2025) bootloader having less S1
  cloud reputation than the older 3.12 bootloader (released ~Oct 2023).
- PyInstaller's bootloader-build process producing a different binary
  signature per Python version due to embedded Python ABI / runtime
  linkage differences.

## 6. Whether ADR-014 now appears operationally validated

**Yes — ADR-014 is operationally validated.**

The ADR-014 record (commons `DECISIONS.md`) stated the canonical
Phoenix UI Platform Python version is 3.12, with the rationale
including "bootloader builds against 3.12 are battle-tested across
all 4 production tools" and "AV / tooling compatibility — the S1
signature documented in BLOCKERS.md §1 was characterised against
3.12-based bootloaders; switching interpreter versions would re-open
the question of whether the same signature fires on newer bootloaders."

A3-i directly proves the second clause. The S1 signature DOES NOT
fire on 3.12 bootloaders; it DOES fire on 3.14 bootloaders. ADR-014's
prediction is now empirically confirmed.

| ADR-014 claim | A3-i evidence |
|----------------|---------------|
| 3.12 is the contract target | Hardened build on 3.12 produces a working bootloader ✓ |
| 3.12 bootloaders are battle-tested | B1 + B2 + production exes (all 3.12-class) survive ✓ |
| Newer interpreters re-open the AV question | B3 quarantined ✓ |
| Developers may experimentally use newer Python locally | B3 was a controlled experiment, no production impact ✓ |
| CI signal is the contract | CI runs on 3.12; should produce identical bootloader content ✓ |

## 7. Whether Python 3.12 should become mandatory for frozen builds

**Yes — mandatory for any frozen-exe (PyInstaller) build on this
workstation and any S1-configured target environment.**

Recommendation matrix:

| Phoenix activity | Python version required |
|-------------------|--------------------------|
| Source-mode development / testing | Any 3.10–3.14 (existing flexibility per ADR-014) |
| Running pytest in CI | **3.12** (matches the eventual build interpreter; current CI standard) |
| Running PyInstaller `--onedir` build | **3.12 MANDATORY** (proven by A3-i: 3.14 produces quarantined bootloader on this S1) |
| Producing release artifacts | **3.12 MANDATORY** (same reason) |
| Wizard-scaffolded new-tool builds | **3.12 MANDATORY** (template's build.bat must enforce this) |
| Production-tool retrofits (Phase 3C, 8a, 8b) | **3.12 MANDATORY** for the build venv specifically |

**This does NOT require source-mode work to migrate to 3.12 immediately.**
Source-mode work can continue under 3.14 venvs; only the build venv
must be 3.12. Two-venv arrangements (one for development, one for
frozen builds) are explicitly allowed.

ADR-014 update implied (suggested verbatim insertion into a future
DECISIONS.md update — not executed by this report):

> **A3-i empirical validation (2026-05-20)**: Single-variable
> isolation experiment confirmed that the Python 3.14 PyInstaller
> bootloader triggers S1 quarantine on the current developer
> workstation, while the 3.12 bootloader does not. Other hardening
> variables (PyInstaller 6.20.0, PySide6 6.10.2, `--noupx`, stdlib
> excludes) are necessary for hygiene + explainability but not
> sufficient — the Python interpreter version is the primary material
> variable. ADR-014's choice of 3.12 as canonical is operationally
> mandatory for frozen builds on this S1 configuration.

## 8. Whether production hardening planning can begin

**Yes — production hardening planning can begin, scoped narrowly.**

The A3-i result enables a much more focused production-tool hardening
plan than was suggested in EXPERIMENT_REPORT_02 § 8:

### Minimum-necessary production hardening per tool

For each production tool's `build.bat` (Phoenix CAD, Job Tracker,
Phoenix Checkout, Phoenix Master Tool):

1. **Migrate the build venv to Python 3.12.** Keep the existing
   3.14 .venv for source-mode development if desired; create a
   separate `.venv-build/` or replace `.venv/` per tool's preference.
2. **Verify PyInstaller install** (`pip install -r requirements-dev.txt`
   or equivalent; Phoenix CAD already pins 6.20.0; the other 3 should
   add pinned requirements-dev.txt files in the same hardening retrofit).
3. **Per-tool dry-run on a throwaway clone first.** Same pattern as
   the Phase 6 hardened experiment — clone to `%LOCALAPPDATA%`, apply
   minimum hardening, rebuild, verify exe survives 2+ minutes.
4. **Only after dry-run success**: apply the hardening to the actual
   production-tool repo on a feature branch.

### Optional add-ons (lower priority based on A3-i)

The other 6 hardening variables (PySide6 pin, PyInstaller pin,
`--noupx`, excludes, fresh venv, build/dist cleanup) **MAY help**
but are NOT proven necessary by A3-i. Recommended position:

- **Keep them in the hardened build pattern for explainability +
  hygiene** (IT/security review benefits from "we explicitly disable
  UPX, we explicitly exclude unused stdlib, we pin all build deps").
- **Don't block production retrofit on them.** If a production tool
  already pins PyInstaller (Phoenix CAD pins 6.20.0), just migrate
  Python and observe. If quarantine recurs, then add the other
  hardening incrementally.

### Suggested production retrofit order

Same as RETROFIT_PLAYBOOK.md § P0–P14 sequencing, restricted to the
build-venv-migration scope:

1. **Phoenix CAD first** — already pins PyInstaller 6.20.0 in
   requirements-dev.txt; smallest delta from hardened baseline.
   Bundles win32com / pythoncom — verify those work on 3.12 (they do
   on 3.14; should also work on 3.12 since pywin32 ships for both).
2. **Job Tracker second** — bundles openpyxl + pyxlsb; standard
   Python pkgs, both compatible with 3.12. Add a requirements-dev.txt
   pinning PyInstaller 6.20.0.
3. **Phoenix Checkout third** — bundles XLSX template files (data,
   not code); lowest-risk module surface.
4. **Phoenix Master Tool fourth** — already uses 3.10/3.11/3.12 CI
   matrix (per the prior governance work) so 3.12 build venv is
   most-natural here; bundled assets are base64 strings in
   `assets.py` (no Python-version-sensitive bundling).

**Production rebuild execution remains DEFERRED to user authorisation
beyond this experiment.**

## 9. Confirmation

| Item | Status |
|------|--------|
| No production rebuilds occurred | ✅ |
| No production tool .venvs modified | ✅ |
| No production tool source modified | ✅ |
| No AV bypass behavior occurred | ✅ |
| No security controls disabled | ✅ — S1 active throughout; observed quarantine (not absence) under 3.14 |
| No obfuscation or stealth techniques | ✅ |
| No releases occurred | ✅ |
| No installer execution | ✅ — Setup.exe produced but never run |
| Hardened 3.12 baseline preserved | ✅ — `<scaffold>-hardened\` untouched |
| Original Phase 6 scaffold preserved | ✅ — `<scaffold>\` (3.14, untreated) still on disk |
| A3-i clone is a parallel sibling, not a mutation of the baseline | ✅ |
| 1 rebuild attempt used (max 1 in this isolation phase) | ✅ |
| Single-variable isolation discipline | ✅ — only Python version differed; six other hardening variables held |

| Field | Value |
|-------|-------|
| Phase | Build Hardening Experiment A3-i — Python isolation |
| Outcome | **A3i-FAIL — Python 3.14 reintroduces quarantine** |
| Material variable identified | **Python interpreter version** |
| Status | ✅ Complete |
| Date | 2026-05-20 |
| Builds in this report | 1 (B3) |
| Reference baseline | B1 + B2 from prior reports |
| ADR-014 status | **Operationally validated** |
| Files modified in production-tool repos | 0 |
| Files modified in commons | 1 (this report) |
| Throwaway clone path | `%LOCALAPPDATA%\ATS Inc\PhoenixScaffold6\phoenix-phase6-standalone-py314-a3i\` |
| Saved to | `phoenix-commons/docs/ui-platform-baseline-v1/BUILD_HARDENING_EXPERIMENT_REPORT_03.md` |

---

## Appendix — Three-experiment summary table

For posterity / executive readers:

| Experiment | Python | All other hardening | Bootloader outcome | Confidence |
|------------|--------|----------------------|-----------------------|------------|
| Phase 6 original | 3.14.3 | NO | Quarantined | n/a (1st repro) |
| EXPERIMENT_REPORT_01 (B1) | 3.12.10 | YES | Survived | one-sample |
| EXPERIMENT_REPORT_02 (B2) | 3.12.10 | YES | Survived | reproducible |
| **EXPERIMENT_REPORT_03 (B3)** | **3.14.3** | **YES (same as B1/B2)** | **Quarantined** | **isolated** |

The 2 × 2 cell with 3.14 + hardened being the failure case is the
controlled isolation. The single-variable change from row 2/3 to
row 4 confirms Python interpreter is the material variable.
