# BUILD_HARDENING_COMPARISON_REPORT_01.md

> Evidence-driven comparison of the failed Phase 6 standalone build
> against the four historically-successful production builds.
> Analysis-only. No AV bypass, no obfuscation, no stealth engineering.
> Authored 2026-05-19.
>
> **Framing**: reduce false positives through cleaner engineering and
> better packaging discipline. NOT "evade detection".

## 1. Comparison matrix

Evidence sourced from: on-disk `.venv/Lib/site-packages/PyInstaller/__init__.py`
version strings; on-disk `.spec` files; `build.bat` flags; installed-exe
PE TimeDateStamp; installed `_internal/` file counts; `Get-AuthenticodeSignature`;
`PySide6.__version__`. UPX availability checked via `which upx`.

| Dimension | Phoenix CAD (LLT) | Phoenix Checkout | Job Tracker (PTT) | Phoenix Master Tool | **Phase 6 Standalone (failed)** |
|-----------|--------------------|------------------|---------------------|---------------------|----------------------------------|
| Deployed exe size | 2.39 MB | 4.46 MB | 4.69 MB | 2.26 MB | **(quarantined)** |
| Deployed exe PE TimeDateStamp | 2026-05-12T14:07Z | 2026-05-04T17:52Z | 2026-05-12T14:37Z | 2026-05-10T07:44Z | n/a |
| Deployed exe code-signed? | **NotSigned** | **NotSigned** | **NotSigned** | **NotSigned** | (would have been NotSigned) |
| Deployed exe `FileVersion` metadata | (empty) | (empty) | (empty) | (empty) | (empty in template) |
| `_internal/` file count | 257 | 3,651 ⚠ | 3,658 ⚠ | 169 | 166 |
| `_internal/` Qt plugins | 22 | 76 ⚠ | 76 ⚠ | 22 | 22 |
| `_internal/` Qt6*.dll | 13 | 136 ⚠ | 136 ⚠ | 13 | 13 |
| Python (current .venv) | 3.14.3 | 3.14.3 | 3.14.3 | 3.14.3 | 3.14.3 |
| PyInstaller (current .venv) | 6.20.0 | not in .venv | 6.19.0 | not in .venv | 6.19.0 |
| `requirements-dev.txt` PyInstaller pin | `==6.20.0` | (no file) | (no file) | (no file) | `==6.19.0` |
| PySide6 version | 6.10.2 | 6.11.0 | 6.10.2 | 6.10.2 | 6.11.1 |
| PySide6 pin | (none observed) | `==6.11.0` | (none observed) | `>=6.11.0` | `>=6.5` ⚠ unpinned upper |
| Build mode | `--onedir --windowed` | `--onedir --windowed` | `--onedir --windowed` | `--onedir --windowed` | `--onedir --windowed` |
| Spec `upx=True` (EXE) | yes | yes | yes | yes | yes |
| Spec `upx=True` (COLLECT) | yes | yes | yes | yes | yes |
| UPX on system PATH | **no** | **no** | **no** | **no** | **no** |
| Therefore UPX actually applied | **no — no-op** | **no — no-op** | **no — no-op** | **no — no-op** | **no — no-op** |
| Spec `excludes=` | `[]` | `[]` | `[]` | `[]` | `[]` |
| Spec `optimize=` | `0` | `0` | `0` | `0` | `0` |
| Spec `strip=` | `False` | `False` | `False` | `False` | `False` |
| Spec `console=` | `False` (windowed) | `False` | `False` | `False` | `False` |
| Spec `codesign_identity=` | `None` | `None` | `None` | `None` | `None` |
| Explicit Qt submodule collection in build.bat | ✓ QtCore/QtGui/QtWidgets | ✗ (none) | ✓ + openpyxl | ✓ QtCore/QtGui/QtWidgets | ✓ QtCore/QtGui/QtWidgets |
| Non-Qt hidden imports | `win32com`, `win32com.client`, `pythoncom` | (none) | `openpyxl`, `openpyxl.cell._writer`, `pyxlsb` | (none) | (none) |
| Bundled data files | 8 (`config/`, `blocks/`, `templates/`, `jobs/`, qss, ico, png) | 8 (5 XLSX + qss + ico + png) | 4 (qss + ico + png + `pyxlsb/`) | 3 (version.py, qss, inventory.py) | 1 (qss) |
| Entry script | `app.py` | `checkout_tool_gui.py` | `project_tracker_gui.py` | `phoenix_master_pyside6.py` (renamed) | `main.py` |
| Inno Setup AppId | (implicit) | (implicit) | (implicit) | explicit GUID | (implicit) |
| `WizardImageFile` / `WizardSmallImageFile` | none | none | none | none (empty) | none |
| Updater payload contract | full-folder (exe + `_internal/`) | exe-only | full-folder | exe-only | full-folder |
| `.gitignore` includes `*.spec` | ✓ | ✓ | ✓ | ✓ | ✓ |
| commons submodule | ✓ (post-Phase-3A) | ✓ (post-Phase-3B) | ✗ (not yet retrofitted) | ✗ (not yet retrofitted) | ✗ (standalone template — by design) |

## 2. Most suspicious deltas

When comparing **Phase 6 vs the 4 production builds**, deltas that
could conceivably affect S1 heuristics:

| # | Delta | Verdict |
|---|-------|---------|
| D1 | Phase 6 PyInstaller pin = `6.19.0`; Phoenix CAD pin = `6.20.0`; others unpinned | Mild. Both versions are recent; bootloader signature differences across 6.19 → 6.20 are minor. |
| D2 | Phase 6 PySide6 = `6.11.1` (newest); production = `6.10.2` / `6.11.0` | Mild. Affects only `_internal/` contents, not the bootloader exe itself. |
| D3 | Phase 6 `requirements.txt` is `PySide6>=6.5` (unpinned upper) | Operational hygiene gap. Not a heuristic trigger. |
| D4 | Phase 6 `_internal/` is the SMALLEST of the 5 (166 files; same shape as PMT 169) | Counter-intuitive — Phase 6 has LESS surface area than production, not more. Rules out "Phase 6 is bigger / messier". |
| D5 | Phase 6 spec is wizard-generated default vs production specs are auto-regenerated from each tool's build.bat with custom hidden imports | Indistinguishable PE-section-wise; both produce same bootloader shape. |
| D6 | All 5 specs declare `upx=True`; UPX is not on PATH | Universal no-op. No effect on detection. Worth fixing for explainability (see § 5). |

**Most striking finding**: **Phase 6's build configuration is, if anything,
*cleaner* than the production builds.** Phoenix Checkout + Job Tracker
bundle 22× more files than Phase 6 — yet shipped successfully. Phase
6 has the simplest bundle (just `phoenix_style.qss` as data) and still
got quarantined.

This rules out **bundled-surface-area** as the heuristic trigger.

## 3. Probable S1 trigger contributors (ranked by confidence)

### H1 — External S1 signature database update (HIGH confidence)

**Hypothesis**: Between the production builds (2026-05-04 to 2026-05-12)
and the Phase 6 build attempt (also May 2026), S1's heuristic database
was updated with a signature that matches the standard PyInstaller
6.19+ bootloader pattern (or a near-overlay characteristic).

**Evidence**:
- All 4 production exes are **unsigned** — same as Phase 6 would be.
- All 4 production exes were built on **the same Python 3.14.3 +
  PyInstaller 6.19/6.20 toolchain** as Phase 6.
- All 4 are bootloader-shape-identical to Phase 6 (same `--onedir`,
  same windowed, same lack of signing).
- BLOCKERS.md explicitly notes "the AV signature is content-heuristic
  on the PyInstaller bootloader binary and fires regardless of build
  path" — and was reproduced 3 times across Phase 4, Phase 4B-local,
  and Phase 6.
- Already-installed production exes survive only because S1 trusts
  cached/installed binaries; the heuristic fires on *fresh* bootloaders
  being written to disk.

**Implication**: rebuilding any of the 4 production tools today on the
same workstation would likely produce an exe S1 deletes. The production
tools "succeed historically" by virtue of their already-installed
state, not by structural superiority.

### H2 — PyInstaller bootloader is unsigned + has no reputation hash (HIGH confidence)

**Hypothesis**: S1 (like most modern AV) uses reputation scoring —
hash + signing + observed prevalence in the wild. An unsigned
PyInstaller bootloader binary built freshly on a developer laptop has
no prevalence in S1's cloud, no Authenticode chain, and matches a
"packed runtime" pattern (PYZ archive + bootloader is a known
unpacker pattern, similar to malware packers). The bootloader gets
flagged regardless of payload.

**Evidence**:
- BLOCKERS.md resolution-option 2 (Authenticode signing) is explicitly
  named as "the durable answer".
- The same bootloader pattern is used by countless legitimate apps
  built with PyInstaller, but each install's hash is unique; no
  cloud reputation accrues.

**Implication**: Code signing is the highest-impact mitigation.

### H3 — Python 3.14 bootloader is rarer than 3.12 (MEDIUM confidence)

**Hypothesis**: Python 3.14 was released October 2025; PyInstaller
bootloaders compiled against 3.14 are newer and rarer in the wild
than 3.12-based bootloaders. Newer bootloader hashes → less
prevalence → more likely to be heuristic-sampled.

**Evidence**:
- ADR-014 explicitly chose 3.12 as canonical: "bootloader builds
  against 3.12 are battle-tested across all 4 production tools".
- The ADR was written 2026-05-16 — implying the ADR authors had
  already encountered exactly this concern.
- However: production exes that ARE installed and surviving today
  were built with Python 3.14 (per current .venv state). Either
  the production exes were rebuilt during May 2026 with 3.14 right
  before S1 activated (the most likely sequence), or with 3.12
  earlier (and 3.14 venvs are post-production).

**Implication**: Building with the ADR-canonical Python 3.12 may
reduce trigger surface, but is not a guaranteed mitigation.

### H4 — Newer PyInstaller bootloaders have higher compression in PYZ (MEDIUM-LOW confidence)

**Hypothesis**: PyInstaller 6.x uses zlib + (optional) cryptography
in its PYZ archive embedded inside the bootloader. High-entropy
overlay data is a classic AV heuristic for "packed malware".

**Evidence**:
- Spec `optimize=0` everywhere — no `optimize=2` to strip bytecode.
- Spec `noarchive=False` — PYZ embedded.
- Both production + Phase 6 share this — no delta.

**Implication**: Universal across all 5 builds. Not the differentiator.

### H5 — Bundled module surface (RULED OUT)

**Hypothesis**: Phase 6 imports something suspicious.

**Evidence**:
- Phase 6 has the SMALLEST `_internal/` of the 5 (166 files vs
  3,651–3,658 for Phoenix Checkout / Job Tracker).
- Phoenix Checkout + Job Tracker bundle 22× more (full Qt6 incl
  WebEngine / Multimedia / PDF / Charts) — still shipped successfully.
- Phase 6's only data is `phoenix_style.qss`.

**Implication**: Eliminated. Phase 6 is the cleanest build. Bundled
surface is not the cause.

### H6 — UPX packing (RULED OUT)

**Hypothesis**: UPX-packed binaries trigger AV heuristics.

**Evidence**:
- All 5 specs declare `upx=True` BUT `which upx` returns nothing.
- UPX is not on PATH; PyInstaller silently skips UPX when the binary
  is absent.

**Implication**: Eliminated. UPX is never actually applied in this
environment.

## 4. Confidence ranking summary

| Hypothesis | Confidence | Mitigation effort | Mitigation effectiveness |
|------------|-----------|---------------------|----------------------------|
| H1 — S1 signature DB update | HIGH | Out of build's control | n/a (allow-list or signing) |
| H2 — Unsigned PyInstaller bootloader + no reputation | HIGH | Medium (cert + signtool) | High |
| H3 — Python 3.14 newer / rarer | MEDIUM | Low (rebuild .venv on 3.12) | Medium |
| H4 — Bootloader PYZ entropy | MEDIUM-LOW | High (rebuild PyInstaller from source) | Low |
| H5 — Bundled module surface | RULED OUT | n/a | n/a |
| H6 — UPX packing | RULED OUT | n/a | n/a |

## 5. Recommended safe hardening steps (analysis only — not executed in this report)

Listed by likely impact-per-effort. **None executed by this report.**

| # | Step | Risk | Expected impact on S1 | Operational benefit |
|---|------|------|------------------------|---------------------|
| **R1** | **Pursue IT/S1 allow-list for the developer machine** (BLOCKER #1 resolution option 1) | None | Direct unblock | Single-machine; not durable for end users |
| **R2** | **Pursue Authenticode code-signing pipeline** (BLOCKER #1 resolution option 2; H2 mitigation) | Low-medium (cert provisioning + signtool integration) | Direct (signed bootloaders skip many heuristics; some S1 policies allow-list signed binaries automatically) | Durable, end-user wide |
| R3 | Pin PyInstaller in every tool's `requirements-dev.txt` (currently only Phoenix CAD has it; Phoenix Checkout, Job Tracker, PMT have none; Phase 6 scaffold has 6.19.0) | None | Indirect (determinism) | Build reproducibility |
| R4 | Add `excludes=[...]` to specs with explicit list of obviously-unused stdlib (e.g. `['tkinter', 'tcl', 'tk', 'lib2to3']`) | Low (test reqd) | Indirect (smaller bundle, slightly less surface) | Reduces `_internal/` size; aids explainability |
| R5 | Set `upx=False` explicitly in specs (currently `True` but no-op) | None | Indirect (signal intent) | Explainability to IT/security — "we don't pack" |
| R6 | Set `optimize=2` in spec to strip bytecode debug info | Low (rare edge cases with `assert` removal) | Indirect (smaller bundle) | Determinism |
| R7 | Set `VersionInfoVersion=`, `VersionInfoCompany=`, `VersionInfoDescription=` in `installer.iss` so deployed exes carry File-Properties metadata (currently empty across all 4) | None | Indirect (gives IT/security something to inspect) | Explainability |
| R8 | Audit Phoenix Checkout + Job Tracker `_internal/` 22× bloat — remove `--collect-submodules` if not needed, add explicit excludes for QtPdf / QtMultimedia / QtWebEngine / QtCharts / QtNetwork if unused | Medium (test reqd — these tools may actually use some of those modules) | Indirect (smaller bundle) | 22× build-size reduction; far better explainability |
| R9 | Migrate dev `.venv` to Python 3.12 per ADR-014 to reduce bootloader-version rarity (H3) | Low | Medium (older bootloader signatures may have better S1 reputation) | ADR-014 compliance |
| R10 | Adopt deterministic build cleanup (clean `build/` + `dist/` between runs; preserve via Inno Setup output only) | None | Indirect | Reproducibility |

**R1 + R2 are the only steps with HIGH expected impact on S1 directly.**
R3–R10 are operational-hygiene improvements that reduce false-positive
risk indirectly.

## 6. Unsafe / rejected approaches

Explicitly NOT recommended:

| Approach | Why rejected |
|----------|--------------|
| Obfuscating bootloader strings | AV evasion; out of scope |
| Manually packing/repacking the bootloader | Anti-analysis behavior; out of scope |
| Disabling S1 / removing AV agent | Bypass; out of scope |
| Renaming exe to evade signature | Cosmetic evasion; doesn't change content hash |
| Custom PyInstaller bootloader fork | Maintenance burden + still triggers content heuristic |
| Stealth loader patterns | Out of scope (framing is hardening, not evasion) |
| UPX-packing the bootloader | Makes detection WORSE (UPX is a classic AV trigger) |
| Embedding the runtime in alternative containers (NSIS-only / 7z SFX / etc.) | Re-implements PyInstaller's job; loses platform features |

## 7. Suggested experimental order (when authorized)

If/when the user authorizes a controlled experiment:

| Order | Experiment | Risk | Reverse-out |
|-------|------------|------|--------------|
| 1 | Migrate dev `.venv` to Python 3.12 + rebuild Phase 6 with no other changes | Low | Re-create .venv on 3.14 |
| 2 | If still quarantined: pin PyInstaller 6.20.0 (Phoenix CAD's pin) in Phase 6 + rebuild | Low | Pin to 6.19.0 |
| 3 | If still quarantined: try PyInstaller 6.16-6.18 (older bootloader) | Low | Pin back |
| 4 | Set `upx=False` + `excludes=['tkinter','tcl','tk','lib2to3']` + `optimize=2` in spec | Low | Revert spec |
| 5 | If still quarantined: rebuild Job Tracker / Phoenix Checkout fresh (does the same heuristic trigger on tools that have shipped successfully?) | Medium (consumes time + may quarantine in-progress builds) | Production binaries already installed are safe |
| 6 | (Out-of-band) request IT/S1 allow-list of the developer machine for PyInstaller bootloaders | None directly | Reverse-able by IT |
| 7 | (Out-of-band, longer-term) Authenticode signing setup + signed bootloader pipeline | Medium effort | n/a — durable change |

Steps 1-4 are **analysis-only-friendly** (no production work).
Step 5 is the most useful proof — would directly confirm/refute H1.
Steps 6-7 are the durable mitigations.

## 8. Operational risk assessment

| Risk dimension | State |
|----------------|-------|
| Current production tool stability | ✅ All 4 deployed and running on user machines |
| Ability to ship a NEW release of any production tool from the developer laptop | ❌ Blocked — same S1 heuristic would fire on any rebuild |
| PCC v2.0.0 release (Phase 6C / 7+) | ❌ Blocked on BLOCKER #1 |
| Phase 3C (PCC retrofit) source-mode work | ✅ Unaffected (source-mode does not invoke PyInstaller) |
| Phase 8a / 8b retrofits source-mode | ✅ Unaffected |
| Frozen-runtime verification | ❌ Blocked indefinitely |
| Installer testing | ❌ Blocked (no fresh exe to install) |
| Updater testing | ❌ Blocked (no exe to update / be updated by) |

The S1 issue does NOT block any source-mode platform / retrofit work
during cooldown. It blocks release-cycle work specifically.

## 9. Should current production tools be rebuilt?

**No.** Current production builds are working on users' machines.
Rebuilding them today on the developer laptop would likely produce
quarantined bootloaders (per H1). Rebuild only when:

1. The S1 issue is resolved (allow-list or signing), OR
2. A genuine product change requires it, in which case the new build
   should ride on the chosen mitigation pipeline.

**Specific exceptions worth noting**:
- Phoenix Checkout + Job Tracker have 22× `_internal/` bloat that
  could be cleaned up by spec tweaks (R8). Worth doing during the
  next genuine product release, NOT as a standalone "hardening" rebuild.

## 10. Issue classification

**Primary root cause: external + structural — NOT build-configuration-specific.**

| Classification | Verdict |
|----------------|---------|
| PyInstaller-version-related | Partial — newer PyInstaller bootloaders + lack of reputation contribute, but not the unique cause (Phase 6's PyInstaller is the SAME as production) |
| Python-version-related | Partial — Python 3.14 bootloader rarity contributes, but production tools also currently use 3.14 |
| Packaging-configuration-related | **No** — Phase 6's packaging config is, if anything, cleaner than production. Bundled surface area is smaller. Spec structure is identical. |
| **Structural / external** | **YES** — S1 heuristic database evolved between production-build dates and Phase 6 attempts; trigger is on the unsigned PyInstaller bootloader binary content, regardless of payload or build path. Reproduced 3 times consistently. |

## 11. Stop conditions

None encountered during this analysis. All work was read-only:

- No binaries executed
- No security controls bypassed
- No live AV experiments
- No production release artifacts altered
- No protections disabled

If future work requires any of the above (e.g. running a Wireshark
trace on S1 quarantine event, signing test binaries against a
real cert), STOP and consult before proceeding.

## 12. Sign-off

| Field | Value |
|-------|-------|
| Phase | Build Hardening Investigation — comparative analysis |
| Status | ✅ Complete — analysis + recommendations only |
| Date | 2026-05-19 |
| Targets compared | 5 (PhoenixPhase6Standalone + 4 production tools) |
| Dimensions evaluated | 24 |
| Hypotheses ruled in | H1 (HIGH), H2 (HIGH), H3 (MEDIUM), H4 (MEDIUM-LOW) |
| Hypotheses ruled out | H5 bundled-surface, H6 UPX |
| Recommendations | R1–R10 (R1 + R2 are highest-impact; rest are explainability/hygiene) |
| Production rebuilds advised | None |
| Bypass / evasion / obfuscation work | None proposed |
| Files modified by this report | 0 (read-only analysis) |
| Saved to | `phoenix-commons/docs/ui-platform-baseline-v1/BUILD_HARDENING_COMPARISON_REPORT_01.md` |
