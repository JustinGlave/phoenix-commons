# TODOS.md

> Unified actionable todo list. Four sections by horizon:
>
> 1. **Immediate** — could start today, not blocked by anything.
> 2. **Before migrations** — must land before Phase 7 pilot.
> 3. **Before releases** — must land before any PCC v2.0.0 release.
> 4. **Future platform work** — Phase 9 candidates.
>
> No speculative feature creep. Every item ties back to a phase or
> a blocker in the rest of the baseline.

## Immediate (no blockers)

| Item | Why | Effort | Phase tie-in |
|------|-----|--------|--------------|
| Add CI workflow to `phoenix-commons` (Python 3.14 + `pip install -e .` + `pytest -q tests/`) | No automated guardrail today; manual smoke per phase | S | BLOCKERS.md §6 |
| Push `phoenix-commons` to a private GitHub repo | Currently no remote — disaster-recovery gap | S | BLOCKERS.md §7 |
| Copy Phase 6C bundle backups to `OneDrive - ATS` | Same-disk backup doesn't survive whole-disk failure | S | BLOCKERS.md §7 |
| Delete merged feature branches on `phoenix-command-center`'s origin (`feature-command-center-gui-polish`, `feature-command-center-branding-packaging`, `fix-ci-smoke-tests`) once you're comfortable | Branch-list hygiene; merge commits preserve history | S | n/a |
| Wire `assets/watermark.png` into PCC's UI (dashboard background or About dialog) | Asset is bundled but unused | S–M | PCC polish backlog |
| Address remaining items from the GUI polish list (sidebar `inline setStyleSheet` cleanup, `tool_card.py` palette fix, `_open_github` Settings affordance, status badge glyph consistency, `mono` font centralisation, dashboard empty-state CTA, About-dialog font-weight tiers, `closeEvent` exception logging) | All identified in the pre-baseline polish survey; small wins | S each (1–2 hours each) | PCC polish backlog |

## Before migrations (gating Phase 7)

| Item | Why | Effort | Phase tie-in |
|------|-----|--------|--------------|
| **Resolve the AV blocker** (one of: IT/S1 allow-list, Authenticode signing, or alternate build host) | Hard gate for Phase 6C and everything downstream | L (depends on path) | BLOCKERS.md §1 |
| **Execute Phase 6C** (frozen-exe dogfood) after the AV gate clears | Proves the end-to-end pipeline works for at least PCC | M | PHASES.md Phase 6C |
| **Phase 2.1 — token formalization** (move `C` dict to `phoenix_commons.theme.tokens`, freeze names) | Apps importing tokens need a stable public API | M | PHASES.md Phase 2.1 |
| **Phase 2.2 — widget API stabilization** (lock `__all__`, freeze signatures, document `objectName` set) | Retrofits need to subclass safely | M | PHASES.md Phase 2.2 |
| **Phase 2.5 — runtime resource provider** (commons-owned `apply_dark_theme(app)` loads QSS via API, not direct file read) | Apps must NOT read commons files directly; need the API | M | PHASES.md Phase 2.5 |
| **Phase 3B — paths contract** (PCC's `pcc_config.json` migrates from project-root to `%APPDATA%\ATS Inc\Phoenix Command Center\` for frozen builds; source-run still reads project-root) | Otherwise PCC v2.0.0 install loses config on every update | M | PHASES.md Phase 3B |
| **Phase 3C — package-data contract** (document `--collect-data phoenix_commons` + `pyproject.toml` `package-data`) | Retrofitted apps need to know how to bundle commons assets | S | PHASES.md Phase 3C |
| Add a pilot-readiness checklist gating Phase 7 kickoff | Phase 7 needs ALL of the above plus an architectural sign-off | S | MIGRATION_RULES.md |
| Update each production tool's AppId GUID in `NAMING_REGISTRY.md` (currently marked "existing — verify") | Pilot retrofit reviewers need the values without hunting through 4 installer.iss files | S | NAMING_REGISTRY.md |

## Before releases (gating any PCC v2.0.0 installer release)

| Item | Why | Effort | Phase tie-in |
|------|-----|--------|--------------|
| Replace placeholder `assets/logo.png` / `logo.ico` with finalised brand artwork | Current logos are letterboxed sprite frames — placeholder | S | PCC branding |
| Add `WizardImageFile` + `WizardSmallImageFile` BMP assets for Inno Setup wizard pages | Currently commented out in `installer.iss` | S | PCC branding |
| Verify PCC v2.0.0 release end-to-end on a fresh machine (or fresh user profile): download installer → install → launch → set tools root → ensure config persists across an upgrade to v2.0.1 | Phase 6C single-machine verification isn't enough for first public release | M | Phase 6C + release process |
| Add a screenshot to PCC's `README.md` | Currently text-only README | S | PCC docs |
| Author release notes for PCC v2.0.0 (`CHANGELOG.md` already has the content; release-page body needs to be drafted) | First public release deserves a clear narrative | S | Release process |

## Future platform work (Phase 9 candidates)

| Item | Phase | Notes |
|------|-------|-------|
| Commons distribution strategy decision (GitHub Packages vs private index vs submodule-as-default) | 9 | BLOCKERS.md §5 / DECISIONS.md ADR-010 |
| Automated lint rule blocking hardcoded hex / `setStyleSheet` with literals in app source | 9 | DECISIONS.md ADR-012 |
| Auto-generated component gallery (visual snapshots of every widget in every state) | 9 | DESIGN_SYSTEM.md "Future work" |
| WCAG audit of all accent / status colour combos against text colours | 9 | DESIGN_SYSTEM.md "Future work" |
| Migrate production-tool installers to a signed-binary pipeline (one of the AV resolution paths becomes mandatory if the others fail) | 9 | DECISIONS.md / BLOCKERS.md §1 |
| Phoenix CAD's `cad/` subsystem audit (BricsCAD COM integration) | n/a — out of retrofit scope | Phase 0 inventory note. Touch only if BricsCAD COM behaviour needs change. |
| Migrate PCC's flat-layout source to wizard's `ui/` subdir layout for consistency with other Phoenix tools | 9 | Cosmetic; not required for any contract |
| Replace ValveMaster's bundled `assets.py` (base64-embedded icons) with a normal `assets/` folder | 9 | Tied to Phase 8a retrofit |
| Delete `Job Tracker/starter_package/` after Phase 8b retrofit lands | 8b | MIGRATION_RULES.md |
| Telemetry / usage metrics | n/a | DECISIONS.md ADR-013 (deferred indefinitely) |
| Light-mode palette | n/a | DECISIONS.md ADR-011 (deferred indefinitely) |

## Not on this list (deliberately)

To keep this file actionable, the following are **intentionally excluded**:

- Bug reports for specific runtime issues — those go in GitHub issues
  per-repo, not in this baseline.
- Feature requests that haven't been tied to a phase — propose via
  GitHub issues; if they cross-cut commons + apps, they may earn a
  new ADR.
- Refactors that improve internal quality but don't change the
  contract — those happen inside each phase's scope as needed, not
  as standalone items.

## Backlog ownership

| Section | Owner | Cadence |
|---------|-------|---------|
| Immediate | Justin (single developer) | Review weekly |
| Before migrations | Justin + DevOps (for AV blocker) | Review at start of every phase |
| Before releases | Justin | Review before each release tag |
| Future platform work | Justin + Architecture | Review at start of each fiscal quarter (or when blocking) |
