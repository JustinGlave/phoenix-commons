# DECISIONS.md

> Architecture Decision Log. Three sections:
>
> 1. **Finalized** — decided, in effect now, change requires a new
>    ADR superseding the prior one.
> 2. **Deferred** — explicitly postponed. Has a trigger condition
>    for re-evaluation.
> 3. **Rejected** — considered and rejected. Listed so the same
>    proposal isn't re-litigated later.
>
> Use ADR-style format. New decisions get appended; old ones stay
> visible.

---

## FINALIZED

### ADR-001: phoenix-commons is the UI platform, not a utility grab-bag

| Field | Value |
|-------|-------|
| Date | 2026-05-13 (architecture pivot during Phase 5 wizard work) |
| Status | Finalized |
| Context | Original rollout framed commons as "shared helpers lifted from production tools." That framing produced scope creep (every utility looked reusable) and ambiguous ownership (apps kept local copies for safety). |
| Decision | Reframe commons as a **UI platform** — design tokens, QSS, widgets, paths, updater, icons, resources — with hard scope rules (COMMONS_SCOPE.md). Apps **extend** the platform; they don't fork it. |
| Consequences | Slows down adding things to commons (raises the bar). Makes the contract crisp. Forces apps to use subclassing + extension points instead of copy-paste. |

### ADR-002: Apps extend via addendum, not fork

| Field | Value |
|-------|-------|
| Date | 2026-05-16 (this baseline) |
| Status | Finalized |
| Context | Without an explicit prohibition, retrofitted apps will inevitably copy commons primitives "just to tweak one thing." That re-introduces drift. |
| Decision | Forbid forks. App-specific behaviour MUST come from subclassing, `objectName`-based QSS overrides, or composition. Never modification of commons primitives in-place. |
| Consequences | Some app-specific needs become harder ("how do I change just THIS panel's padding?"). Forces a clean conversation about whether the need is genuinely app-specific (extend) or a commons gap (new token / new variant). |
| Enforcement | Code review per retrofit PR. Future automation in Phase 9 (lint rule for hardcoded hex / commons-selector overrides). |

### ADR-003: Two updater payload contracts coexist long-term

| Field | Value |
|-------|-------|
| Date | 2026-05-13 (Phase 0 production inventory finding) |
| Status | Finalized |
| Context | Phase 0 found two payload shapes shipping in production: full-folder (Job Tracker, Phoenix CAD) and exe-only (Phoenix Checkout, ValveMaster). Switching either group to the other would require a coordinated full-reinstall for existing users. |
| Decision | Preserve both contracts. Commons API exposes the choice via the `expected_internal: bool = True` kwarg on `download_and_apply`. Validator helper exposes it via `--require-internal`. The wizard's standalone scaffold defaults to full-folder (the canonical pattern). Retrofitted production tools keep their existing contract. |
| Consequences | Slightly more complex commons API surface (one kwarg). Eliminates the risk of breaking existing user installs. Removes the temptation to coordinate a high-risk full-reinstall deploy. |
| Cross-reference | PACKAGING_CONTRACT.md §1, DEPENDENCY_GRAPH.md "Updater contracts" |

### ADR-004: Pilot batch is Phoenix Checkout + Phoenix CAD

| Field | Value |
|-------|-------|
| Date | 2026-05-16 (this baseline) |
| Status | Finalized |
| Context | Original rollout planned a sequential retrofit (CAD → Checkout → ValveMaster → Job Tracker). Pilot-of-one approach can't prove the migration **scales** beyond N=1. |
| Decision | Pilot is a batch of two: Phoenix Checkout + Phoenix CAD. Lowest combined risk (CAD already on System A so visible change ≈ 0; Checkout has the simpler updater contract). Two-at-once stress-tests the contract before ValveMaster's high-visibility theme swap and Job Tracker's high surface area. |
| Consequences | Pilot review report becomes a hard gate before Phase 8. Two PRs open simultaneously requires coordinated reviewing. If the pilot finds a commons contract issue, both retrofits get to learn from it. |
| Cross-reference | MIGRATION_RULES.md "Migration order" |

### ADR-005: System A (Phoenix dark navy) is the only design system

| Field | Value |
|-------|-------|
| Date | 2026-05-13 (Phase 0) |
| Status | Finalized |
| Context | ValveMaster shipped with a legacy gray palette ("System B", `#1c1c1c`). The other three production tools shipped with System A (Phoenix dark navy). |
| Decision | System B is deprecated. ValveMaster gets the System A theme in its Phase 8a retrofit, with the visual change explicitly noted in release notes. |
| Consequences | ValveMaster users experience a visible re-skin on the upgrade post-retrofit. Brand consistency across the tool family is restored. |
| Cross-reference | DESIGN_SYSTEM.md "Forbidden patterns" |

### ADR-006: Internal-proprietary license, not open source

| Field | Value |
|-------|-------|
| Date | 2026-05-15 (PCC branding/packaging work) |
| Status | Finalized |
| Context | PCC and `phoenix-commons` ship under an ATS Automation internal license. Public PyPI publishing or open-sourcing the code is not authorized. |
| Decision | All repos use the proprietary license in `LICENSE` (see PCC's file for canonical wording). Public disclosure / redistribution / external use requires written ATS approval. |
| Consequences | Distribution-strategy options for commons narrow (no public PyPI). GitHub Packages, private index, or submodule remain. |
| Cross-reference | `phoenix-command-center/LICENSE`, `SECURITY.md` |

### ADR-007: Commons-backed wizard radio stays non-default until frozen-exe clears

| Field | Value |
|-------|-------|
| Date | 2026-05-13 (Phase 5 wizard implementation) |
| Status | Finalized |
| Context | At wizard implementation time, the AV blocker prevented frozen-exe verification of any scaffolded tool. Defaulting users to the unverified commons-backed scaffold would have created a support burden when their builds failed. |
| Decision | "Phoenix Tool — standalone" stays the default radio. "Phoenix Tool — commons-backed" is enabled (when commons_path is configured) but carries an inline note: "Frozen-exe runtime verification is still blocked by local AV." |
| Consequences | Standalone scaffolds carry their own copy of commons primitives (current PCC pattern). Switch to commons-backed default after Phase 6C verifies the commons-backed frozen exe end-to-end. |
| Cross-reference | `phoenix-commons/docs/rollout/phase-5-report.md`, `phase-5b-commons-ux-fix-report.md` |

### ADR-008: Build pipeline uses sentinel-substitution templates, not f-string formatting

| Field | Value |
|-------|-------|
| Date | 2026-05-13 (Phase 5 templating) |
| Status | Finalized |
| Context | Several wizard template files (QSS, `.bat`, Inno Setup) contain literal `{` / `}` braces. Using `str.format` for `{TOOL_NAME}`-style substitution would have required `{{` / `}}` escaping throughout, creating noise. |
| Decision | Use `__TOKEN__` sentinel substitution in `phoenix_tool_templates.py`. Tokens are `__TOOL_NAME__`, `__PRETTY__`, `__EXE_NAME__`, `__EXE_STEM__`. Substituted via a small `_substitute()` helper using `str.replace`. |
| Consequences | Template files read cleanly with no escaping. Adding a new token is trivial. Verified by post-substitution grep: zero residual `__TOKEN__` markers in any generated file. |
| Cross-reference | `phoenix-command-center/phoenix_tool_templates.py:_substitute` |

### ADR-009: Phase 6A — validator out of inline PowerShell

| Field | Value |
|-------|-------|
| Date | 2026-05-13 (Phase 6 finding, Phase 6A fix) |
| Status | Finalized |
| Context | `build.bat`'s original tail had a multi-line PowerShell snippet that read the auto-updater zip and validated its contents. Using cmd.exe's `^` line-continuation token. Failed when `build.bat` was invoked through a PowerShell wrapper (the outer shell reinterpreted the carets). |
| Decision | Move validation into a dedicated Python helper `scripts/validate_release_zip.py`. `build.bat` calls it via a single-line `.venv\Scripts\python` invocation. Both cmd-direct and PS-wrapped invocations work. |
| Consequences | Build tail is now one line instead of an embedded multi-line script. Helper is testable in isolation (3 pytest cases + 5 CLI scenarios). Replicated into every wizard-scaffolded tool. |
| Cross-reference | `phoenix-commons/docs/rollout/phase-6a-build-template-fix-report.md` |

### ADR-014: Canonical platform Python version = 3.12

| Field | Value |
|-------|-------|
| Date | 2026-05-16 (UI Platform Stabilization 01) |
| Status | Finalized; **empirically validated 2026-05-20** for frozen builds (see § Empirical validation below) |
| Context | Earlier rollout work used Python 3.14 on Justin's developer laptop because that's what was already installed. Stabilizing the platform requires picking a canonical version that CI, the packaging contract, and consuming apps all target. Without an explicit decision, drift between developer laptops, CI runners, and frozen builds was inevitable. |
| Decision | The **canonical Phoenix UI Platform Python version is 3.12.** `phoenix-commons` CI (`.github/workflows/ci.yml`) uses `python-version: "3.12"`. Consuming apps target 3.12 for their packaging contract (build venv, `requirements*.txt`, `installer.iss` runtime checks). `pyproject.toml` keeps `requires-python = ">=3.10"` as a floor so developer machines on 3.10–3.14 can install editable; the *contract target* is 3.12. **For frozen (PyInstaller) builds, 3.12 is now operationally MANDATORY** per `FROZEN_BUILD_BASELINE.md`; source-mode work retains 3.10–3.14 flexibility. |
| Rationale | (1) **PyInstaller maturity** — 6.x has shipped Windows wheels for 3.12 since late 2023; newer interpreter wheels have lagged. Bootloader builds against 3.12 are battle-tested across all 4 production tools. (2) **Qt ecosystem stability** — PySide6 6.10.x is fully validated on 3.12; newer interpreter versions occasionally expose corner-case binding issues that take a release cycle to settle. (3) **CI consistency** — GitHub Actions `setup-python@v5` has 3.12 as a first-tier supported version with reliable cache hits. (4) **Desktop-platform stability** — production tools deploy to ATS workstations whose installer-runtime expectations are pinned to 3.12 today; gratuitously rev'ing the interpreter is a coordinated-deploy burden with no offsetting benefit. (5) **AV / tooling compatibility** — the S1 signature documented in `BLOCKERS.md §1` was characterised against 3.12-based bootloaders; switching interpreter versions would re-open the question of whether the same signature fires on newer bootloaders. |
| Consequences | • **App developers may experimentally use newer Python locally** (3.13, 3.14) for dev convenience, but commits to commons-consuming apps must NOT introduce 3.13-or-newer-only syntax or stdlib usage. • Production tools' `build.bat` files should pin the build venv to 3.12 (`py -3.12 -m venv .venv`) when they migrate to commons-backed. • PCC currently uses 3.14 on Justin's laptop; its packaging pipeline must move to 3.12 before Phase 7 retrofits start so the platform and PCC share the same interpreter target. • 3.14 only enters the platform contract when an explicit superseding ADR replaces this one. |
| Enforcement | CI uses 3.12 (Windows-latest). Per-app `requirements*.txt` pins should declare PySide6 versions known to work on 3.12. `pyproject.toml` keeps `>=3.10` floor for developer convenience but the **CI signal is the contract**. For frozen builds: build.bat MUST verify build venv is 3.12 before invoking PyInstaller (template emits this check per `phoenix_tool_templates.py`). |
| Empirical validation | **2026-05-20**: Single-variable isolation experiment confirmed Python 3.14 PyInstaller bootloader triggers S1 quarantine on the current developer workstation; Python 3.12 bootloader survives identically under otherwise-identical hardened configuration. Three controlled builds: 3.12 + hardening → survives twice; 3.14 + hardening → quarantined. See `BUILD_HARDENING_EXPERIMENT_REPORT_03.md` and `FROZEN_BUILD_BASELINE.md`. Rationale clauses (1) and (5) above are now empirically confirmed for frozen-runtime generation. |
| Cross-reference | `.github/workflows/ci.yml`, `docs/ui-platform-baseline-v1/PHASES.md` (Phase 2.x prep), `docs/ui-platform-baseline-v1/STABILIZATION_REPORT_01.md` (introduction of this ADR), `FROZEN_BUILD_BASELINE.md` (canonical frozen-build baseline), `BUILD_HARDENING_EXPERIMENT_REPORT_03.md` (empirical isolation), `BLOCKERS.md § 1` (S1 trigger). |

### ADR-015: Temporary commons distribution strategy = git submodule

| Field | Value |
|-------|-------|
| Date | 2026-05-19 (Phase 2.6 — Packaging verification) |
| Status | Finalized |
| Scope | Phases 3 through 8 inclusive. Phase 9+ may revisit. |
| Context | The original Phase 0/1 plan deferred the distribution-mechanism question to Phase 9 (see superseded ADR-010). Phase 2.5 + Phase 2.6 verification work now needs a concrete answer so consuming apps can be scaffolded with a stable contract. Three candidates considered: (a) **git submodule** — every consuming tool adds `phoenix-commons` as a submodule under `commons/`, `pip install -e ./commons` from the tool's venv; (b) **private package registry** — host wheels on a private PyPI / GitHub Packages and `pip install phoenix-commons` from there; (c) **vendoring** — copy the package source into each tool's `vendor/phoenix_commons/` (the "Plan B" from the original rollout plan). |
| Decision | **For Phases 3 through 8: git submodule + editable install is the official transport mechanism.** Every consuming app adds a `commons/` submodule pinned to a specific commit (or branch tip — the wizard scaffolds branch-tracking) and installs it via `pip install -e ./commons`. Wheels-from-registry distribution is explicitly deferred to Phase 9+. |
| Rationale | (1) **Matches PCC wizard assumptions** — the new-tool wizard already scaffolds `git submodule add` + `pip install -e ./commons`. No tooling rewrite. (2) **Lowest migration friction** — apps that retrofit later inherit a working pattern from the dogfood phase, no infrastructure burden. (3) **Easiest rollback** — `git submodule update --recursive <prev-sha>` returns a tool to a known-good commons state in one command. No "yank a wheel" coordination. (4) **Easiest branch coordination** — when a commons branch is being developed against a tool branch, both are checked out together; no out-of-band wheel-publish step. (5) **Simplest package-data behaviour** — `pip install -e` puts `phoenix_commons` on `sys.path` from the submodule's working tree, so `importlib.resources` and PyInstaller `--collect-data` work identically in source and frozen mode. (6) **Works offline** — no network call to a registry. Important for ATS workstations behind firewalls. (7) **Avoids premature package-registry complexity** — running a private PyPI mirror (or paying for one) only makes sense once the cross-app commons API is stable. Phase 9+ when the API has settled. |
| Consequences | • Every retrofitted tool gains a `commons/` submodule + `.gitmodules` entry. • Wizard's commons-backed scaffold is the official path for new tools; standalone scaffolds stay the safer default until frozen-exe verification clears (per ADR-007). • Plan B (vendoring) remains documented as the explicit fallback if `pip install -e ./commons` ever fails under PyInstaller — see the original rollout plan. • CI per consuming app must `git submodule update --init --recursive` before installing. • A new pinned-commit policy is needed when commons MAJOR-version bumps land — tools choose when to bump their submodule SHA. • **Eventual revisit** at Phase 9 may flip the decision to a private wheel registry once cross-app stability is proven and the wheel-publish cadence is justified. |
| Expected submodule layout | Every consuming app's repo root contains: `commons/` (the submodule, populated by `git submodule update --init --recursive`); `.gitmodules` (one entry, pointing at `JustinGlave/phoenix-commons` over HTTPS); the tool's `requirements.txt` includes `-e ./commons` immediately after the PySide6 pins; the tool's `build.bat` runs `git submodule update --init --recursive` before `pip install -r requirements.txt`. |
| Editable-install expectations | `pip install -e ./commons` resolves `phoenix_commons.__version__` from `commons/src/phoenix_commons/_version.py`. Package data (`*.qss`, `*.svg`) is reachable via `importlib.resources.files(...)` (verified in Phase 2.6 — see `tests/test_packaging.py`). The editable install puts the working-tree `src/phoenix_commons/` on `sys.path` — changes to commons take effect on next Python interpreter start without a re-install. |
| Consuming-app assumptions | (1) Consuming apps NEVER import from underscore paths in commons (see API_BOUNDARIES.md). (2) Consuming apps NEVER edit commons source as part of their own retrofit (per ADR-002 — extend via addendum, not fork). (3) Consuming apps pin their commons submodule to a specific commit before each release tag so the release is reproducible. (4) Consuming apps respect the Generated Artifacts Policy — the generated `embedded_qss.py` etc. are read-only outputs. |
| Cross-reference | ADR-002 (apps extend via addendum), ADR-007 (commons-backed wizard radio non-default), ADR-010 (the deferred ADR this supersedes for Phases 3-8), PACKAGING_CONTRACT.md, BLOCKERS.md §5 |

### ADR-016: PCC palette reconciliation — controlled accent override

| Field | Value |
|-------|-------|
| Date | 2026-05-19 (final stabilization decision before Phase 3A pilot migrations) |
| Status | Finalized |
| Full text | `ADR_PCC_PALETTE_RECONCILIATION.md` (standalone — this is the only ADR with its own file, given its scope as the final architecture-level decision before pilot migrations) |
| Context | Phase 2.7 surfaced that three palettes coexist in production: `phoenix_style.qss` canonical (navy + red + blue), PCC's `theme.py` (navy + orange + teal), ValveMaster's System B (deprecated gray). PCC and the QSS-file palette are both currently labelled "System A" in different docs — naming collision must resolve before Phase 3A. |
| Decision | **Option B — controlled accent override.** Commons exposes a small named set of brand tokens (`PRIMARY`, `SECONDARY`, `ACCENT`) which apps may override via a controlled `BrandProfile` mechanism. Every other token (`BG`, `SURFACE`, `TEXT`, `MUTED`, `SUCCESS`, `WARNING`, `ERROR`, all spacing, all typography, all radii) is **locked** — apps cannot override. PCC keeps orange + teal as its registered brand profile; Phoenix CAD / Job Tracker / Phoenix Checkout / ValveMaster use the default profile. |
| Options considered | A — PCC adopts full commons canonical (rejected: loses PCC identity, no path for future tool variants). B — controlled accent override (accepted). C — per-app arbitrary themes (rejected: contradicts ADR-001 + ADR-002; slow-motion design-system fork). |
| Consequences | • Phase 3+ commons implementation adds a `BrandProfile` dataclass + sentinel-form QSS template + `apply_dark_theme(app, brand=...)` kwarg. • PCC's retrofit registers its own `BrandProfile`; other tools use the default. • `DESIGN_SYSTEM.md` and `PLATFORM_CONTRACT.md` updated to reflect locked-vs-variant classification. • One widget system, one QSS architecture, one token hierarchy preserved. • Future tools that legitimately need an accent variant have a controlled path; arbitrary palette forks remain forbidden. |
| Cross-reference | `ADR_PCC_PALETTE_RECONCILIATION.md` (the full text), ADR-001 (commons as UI platform), ADR-002 (apps extend, not fork), `STABILIZATION_REPORT_06.md` (where the divergence was surfaced), `STABILIZATION_REPORT_07.md` (where this ADR lands), `DESIGN_SYSTEM.md` (post-update), `PLATFORM_CONTRACT.md` § Theme tokens (post-update), `visual-baselines/pcc/baseline.md` (PCC's retrofit guidance), `visual-baselines/MIGRATION_VISUAL_REVIEW_CHECKLIST.md` (the per-PR addenda) |

---

## DEFERRED

### ADR-010: Commons distribution strategy

| Field | Value |
|-------|-------|
| Date | 2026-05-16 |
| Status | **Superseded by ADR-015** for Phases 3-8. Re-opens at Phase 9. |
| Question | How should `phoenix-commons` be distributed to consumers? Submodule, private PyPI, GitHub Packages, Plan B vendoring? |
| Trigger to re-evaluate | At Phase 9 — when cross-app commons API is proven stable and the wheel-publish cadence is justified. The Phase 8 retrofits will produce real signal on whether submodule-based distribution scales. |
| Current state (post-ADR-015) | Phases 3-8 use **git submodule + `pip install -e ./commons`** per ADR-015. Plan B vendoring remains documented as the explicit fallback if editable install ever fails under PyInstaller. Private package registry / wheels deferred until Phase 9+. |
| Cross-reference | **ADR-015** (the supersession), BLOCKERS.md §5 |

### ADR-011: Light-mode palette

| Field | Value |
|-------|-------|
| Date | 2026-05-16 |
| Status | Deferred indefinitely |
| Question | Should the Phoenix design system support a light-mode palette? |
| Decision | **No light mode on roadmap.** Phoenix apps are dark-mode by design (better for industrial / control-room contexts, lower eye strain in shop-floor environments). |
| Trigger to re-evaluate | Explicit user feedback from production users asking for light mode. None received in 5 years of production use; unlikely to change. |

### ADR-012: Automated lint enforcement for design-system drift

| Field | Value |
|-------|-------|
| Date | 2026-05-16 |
| Status | Deferred to Phase 9 |
| Question | Should a lint rule block hardcoded hex colours / forbidden patterns in app source? |
| Decision | Manually enforced today via code review. Automation deferred until commons-backed retrofits land and we know the false-positive surface. |
| Trigger to re-evaluate | After Phase 8 — if drift is observed in retrofitted apps, add the rule. |

### ADR-013: Telemetry / usage metrics

| Field | Value |
|-------|-------|
| Date | 2026-05-16 |
| Status | Deferred indefinitely |
| Question | Should Phoenix tools collect anonymous usage telemetry? |
| Decision | **No telemetry by default.** Internal tooling, small user base, easier to ask directly. Adding network calls also expands the security surface (see SECURITY.md). |
| Trigger to re-evaluate | If/when the user base grows beyond ATS internal use. |

---

## REJECTED

### ADR-R1: Switch all production tools to a single updater payload contract

| Field | Value |
|-------|-------|
| Date | 2026-05-13 (during Phase 0 inventory) |
| Status | Rejected |
| Proposal | Move Phoenix Checkout + ValveMaster from exe-only updater zips to full-folder updater zips, unifying the contract. |
| Reasoning | Would require a coordinated full-reinstall deploy for every existing user the first time they upgrade post-switch. Higher risk than preserving the asymmetry. The commons API supports both shapes via a kwarg — no code-side reason to force consolidation. |
| Result | Both contracts coexist. See ADR-003. |

### ADR-R2: Lift ValveMaster's QPalette-based theme into commons

| Field | Value |
|-------|-------|
| Date | 2026-05-13 (during Phase 0 inventory) |
| Status | Rejected |
| Proposal | Add a programmatic-palette path to `phoenix_commons.theme` so ValveMaster's existing approach can stay. |
| Reasoning | ValveMaster's palette is the deprecated "System B" gray, not a different way of expressing System A. Lifting it would entrench a non-canonical design. Better: ValveMaster gets the System A QSS in Phase 8a retrofit. |
| Result | Commons only ships QSS-based theming. |

### ADR-R3: Make commons-backed the wizard default before AV clears

| Field | Value |
|-------|-------|
| Date | 2026-05-13 (Phase 5) |
| Status | Rejected |
| Proposal | Promote "Phoenix Tool — commons-backed" to the default wizard radio even though frozen-exe verification is blocked. |
| Reasoning | Would generate scaffolded apps whose `build.bat` produces a broken release zip on this laptop. Operational footgun. Standalone scaffolds work end-to-end source-mode AND frozen-mode (until AV fires on the exe), so they're the safer default. |
| Result | Standalone stays default. Commons-backed enabled with an AV-caveat note. See ADR-007. |

### ADR-R4: Bundle a system font into PyInstaller builds

| Field | Value |
|-------|-------|
| Date | 2026-05-16 |
| Status | Rejected |
| Proposal | Add a bundled `.ttf` (e.g. Inter, Source Sans) to commons so every Phoenix tool renders identically across machines. |
| Reasoning | Adds 200-400 KB per release for marginal gain. Windows users overwhelmingly have Segoe UI; the fallback chain in `theme.py` handles macOS/Linux dev. Also adds licensing surface. |
| Result | System fonts only. See DESIGN_SYSTEM.md "Typography". |

### ADR-R5: One-installer-for-everything ("Phoenix Suite")

| Field | Value |
|-------|-------|
| Date | 2026-05-16 |
| Status | Rejected |
| Proposal | Bundle all 5 tools into a single `PhoenixSuiteSetup.exe` instead of per-tool installers. |
| Reasoning | Production tools have independent release cadences; a unified installer forces synchronised releases. Users often use only 1-2 tools at a time. Disk-space and upgrade-fragility costs exceed the install-once convenience. Each tool's existing installer is already low-friction (per-user install, no admin). |
| Result | Per-tool installers stay the model. |

---

## How to add a new ADR

1. Pick the next sequential number (`ADR-014`, `ADR-015`, …).
2. Use the 5-row table format: Date, Status, Context, Decision, Consequences.
3. Add a "Cross-reference" row if relevant baseline files document the
   decision in more detail.
4. Append to the appropriate section (Finalized / Deferred /
   Rejected). Don't re-order older ADRs.
5. If the new ADR supersedes an existing one, mark the older ADR's
   status as **Superseded by ADR-XXX** and keep it visible.
