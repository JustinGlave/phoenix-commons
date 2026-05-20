# Changelog

All notable changes to **phoenix-commons** are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/).

Versions are tracked in `src/phoenix_commons/_version.py`. Commons is a
library — there is no tagged release cadence yet (per ADR-014 and
ADR-015 phase plan); the consuming tools' submodule SHAs are the
de-facto distribution mechanism.

## [Unreleased]

### Added
- Operational Hardening Sprint (2026-05-19): CHANGELOG.md and
  release-prep reference docs (`RELEASE_CHECKLIST.md`,
  `INSTALLER_NOTES.md`, `BRANDING_ASSET_GUIDE.md`,
  `VERSIONING_POLICY.md`). Documentation-only — no API change.
- `Design Items/README.md` — per-folder inventory of the brand-asset
  source files (the "four colors" pattern source-of-truth).
- `OPERATIONAL_STABILIZATION_REPORT_01.md` — 11-section audit of all
  6 Phoenix repos' branding + governance state.
- `PHASE_3B_POST_REVIEW_AND_MERGE_REPORT.md` — 14-section Phase 3B
  Phoenix Checkout retrofit merge report.
- `MIGRATION_RULES.md` § 0 (Pre-flight commons-API gap inventory),
  § 1 hybrid coexistence refinement, § 10 row 11 (actual launch
  as retrofit gate), § 11 (Monolith inline-class retrofit pattern)
  — four codified additions from the Phase 3B retrofit.
- `PHASE_3B_PHOENIX_CHECKOUT_REPORT.md` — 21-section retrofit report.

### Changed
- `MIGRATION_RULES.md` § Migration order row for 3B updated from
  "Not started" → "Merged 2026-05-19 (merge commit `26a4689`)".

## [0.1.0] — Phase 2 Stabilization

Initial baseline of the Phoenix UI Platform package. Released as a
git-submodule + editable install per ADR-015. No PyPI publication yet.

### Added
- `phoenix_commons.theme` — `apply_dark_theme(app, brand=None)` with
  BrandProfile sentinel substitution per ADR-016.
- `phoenix_commons.theme.tokens` — canonical color tokens (System A
  navy + red + blue).
- `phoenix_commons.widgets` — PrimaryButton, SecondaryButton,
  TertiaryButton, Panel, PageTitle, PageSubtitle, SectionTitle,
  HintLabel, PhoenixTable, UpdateBanner, button_row.
- `phoenix_commons.widgets.no_scroll` — NoScrollComboBox,
  NoScrollSpinBox, NoScrollDoubleSpinBox, NoScrollDateEdit.
- `phoenix_commons.paths` — is_frozen, user_data_dir, resource_path.
- `phoenix_commons.updater` — UpdateInfo, check_for_update,
  download_and_apply (full-folder payload contract default).
- `phoenix_commons.updater.qt` — UpdateCheckThread.
- `phoenix_commons.icons` — Lucide icon set (check, info, plus,
  refresh, save, search, settings, trash, warning, x).
- `docs/ui-platform-baseline-v1/` — full platform contract,
  migration rules, ADR series (ADR-001 through ADR-016),
  design-system reference, per-app visual baselines.
- `tests/` — smoke tests + packaging contract tests
  (90+ passing as of Phase 2.6).
- CI workflow on GitHub Actions (Windows-latest, Python 3.12 per
  ADR-014).
