# PHASES.md

> Revised phase ladder. The original rollout (Phases 0–6) is preserved
> as historical record (their reports stay at `docs/rollout/`).
> Platform-stabilization sub-phases (2.1–2.7 and 3A–3C) and the
> migration phases (7, 8, 9) are layered on top.
>
> Implementation work proceeds **one approved phase at a time**.

## At a glance

| # | Phase | Status |
|---|-------|--------|
| 0 | Production inventory | ✅ Done |
| 1 | Commons package skeleton | ✅ Done |
| 2 | Lift theme + widgets from Phoenix CAD | ✅ Done |
| 2.1 | Token formalization | ⏸ Not started |
| 2.2 | Widget API stabilization | ⏸ Not started |
| 2.5 | Runtime resource provider | ⏸ Not started |
| 2.6 | Icon infrastructure | ⏸ Not started |
| 2.7 | Design system documentation | ⏸ Not started (this baseline is a precursor) |
| 3 | Lift paths + updater | ✅ Done |
| 3A | Updater bug fixes + PS-safe quoting | ✅ Done |
| 3B | Paths contract / user-data migration policy | ⏸ Not started |
| 3C | Package-data contract | ⏸ Not started |
| 4 | PyInstaller compatibility verification | ⚠ Partial — AV-blocked |
| 5 | Wizard radios + scaffold generation | ✅ Done |
| 6 | Standalone PCC dogfood | ⚠ Partial — frozen-exe AV-blocked |
| 6A | build.bat validator fix | ✅ Done |
| 6B | Wizard merged to PCC main | ✅ Done |
| 6C | Frozen-exe dogfood after AV gate clears | ⏸ Blocked on AV |
| 7 | **Pilot retrofit**: Phoenix Checkout + Phoenix CAD | ⏸ Deferred |
| 8 | **Wave retrofit**: ValveMaster + Job Tracker | ⏸ Deferred |
| 9 | Long-term stewardship / commons v2 | ⏸ Deferred |

---

## Phase details

### Phase 0 — Production inventory

| Field | Value |
|-------|-------|
| Goal | Freeze the production-tool contract (app names, exe names, install paths, GitHub asset names, updater payload shape) so retrofits never break shipping installers. |
| Dependencies | none |
| Exit criteria | `phoenix-commons/docs/production-inventory.md` exists, all 4 tools rowed. |
| Status | ✅ Done (file present, 2026-05-13). |

### Phase 1 — Commons package skeleton

| Field | Value |
|-------|-------|
| Goal | Create the `phoenix-commons` Python package layout with `pyproject.toml`, `src/phoenix_commons/{__init__,_version}.py`, empty submodules, and a `pip install -e .` happy path. |
| Dependencies | Phase 0 |
| Exit criteria | `pip install -e .` works; `python -c "import phoenix_commons; print(phoenix_commons.__version__)"` returns `0.1.0`. |
| Status | ✅ Done. |

### Phase 2 — Theme + widgets lifted from Phoenix CAD

| Field | Value |
|-------|-------|
| Goal | Copy the canonical theme + the widget catalog from `Phoenix_CAD_Tool` into `phoenix_commons.theme` and `phoenix_commons.widgets` verbatim (no rewrites in this phase). |
| Dependencies | Phase 1 |
| Exit criteria | All listed widgets import; a scratch PySide6 window renders themed `PrimaryButton`, `Panel`, `PhoenixTable`, and `UpdateBanner`. |
| Status | ✅ Done. |

### Phase 2.1 — Token formalization

| Field | Value |
|-------|-------|
| Goal | Promote the colour / typography / spacing / radius constants currently inline in `theme.py` to a dedicated **token module** with a stable public API. Apps reference tokens by name, never hardcode hex. |
| Dependencies | Phase 2 |
| Risk | Low (additive); medium if existing consumers refactor at the same time. |
| Exit criteria | `from phoenix_commons.theme.tokens import C, FONT_FAMILY, SPACING, RADII` resolves; smoke test renders unchanged; no production tool source touched. |
| Blocked-by | Architecture review of the token vocabulary (DESIGN_SYSTEM.md) |
| Approved? | **Not approved** — awaits user go. |

### Phase 2.2 — Widget API stabilization

| Field | Value |
|-------|-------|
| Goal | Lock the public widget surface — names, constructor kwargs, `objectName` values — so downstream apps can rely on stable imports. Anything not in the locked set is private (leading underscore). |
| Dependencies | Phase 2.1 |
| Risk | Medium — locking the API constrains future internal refactors. |
| Exit criteria | `phoenix_commons.widgets.__all__` enumerated; signatures frozen; `NAMING_REGISTRY.md` updated. |
| Approved? | **Not approved.** |

### Phase 2.5 — Runtime resource provider

| Field | Value |
|-------|-------|
| Goal | Commons becomes the single source of truth for runtime resources (QSS file, embedded fallback, font hints). Apps load via `phoenix_commons.resources.qss_path()` or similar — never read the file directly. |
| Dependencies | Phase 2.2 |
| Risk | Medium — package-data bundling under PyInstaller is fiddly (see PACKAGING_CONTRACT.md). |
| Exit criteria | Resource API stable; tests cover both source-run and `_MEIPASS` resolution; a sample consumer (PCC or scratch tool) loads QSS via the new API. |
| Approved? | **Not approved.** |

### Phase 2.6 — Icon infrastructure

| Field | Value |
|-------|-------|
| Goal | Commons provides a base icon set (e.g. settings, refresh, search, error, success, info, warning) and an extension API for app-specific icons. Apps still own their app logo. |
| Dependencies | Phase 2.5 |
| Risk | Low — additive; mostly file shuffle. |
| Exit criteria | `phoenix_commons.icons.<name>` returns a `QIcon`; `app_icon=Path(...)` hook lets apps override / extend; bundled via package-data. |
| Approved? | **Not approved.** |

### Phase 2.7 — Design system documentation

| Field | Value |
|-------|-------|
| Goal | Move `DESIGN_SYSTEM.md` from this baseline directory into the commons repo as the canonical, versioned design document. Includes do/don't examples and component snapshots. |
| Dependencies | Phases 2.1, 2.2, 2.6 |
| Risk | None (docs only). |
| Exit criteria | `phoenix-commons/docs/design-system.md` exists, links from BASELINE / DESIGN_SYSTEM. Auto-generated component gallery deferred to 9. |
| Approved? | **Not approved.** |

### Phase 3 — Paths + updater lifted

| Field | Value |
|-------|-------|
| Goal | Lift the path helpers from Phoenix CAD's `paths.py` and the updater from Job Tracker's `starter_package/updater.py` into commons. Public API: `is_frozen`, `user_data_dir`, `resource_path`, `check_for_update`, `download_and_apply`, `UpdateInfo`, `UpdateCheckThread`. |
| Status | ✅ Done. |

### Phase 3A — Updater bug fixes + PS-safe quoting

| Field | Value |
|-------|-------|
| Goal | Fix the incomplete-download bug (`stat()` after `unlink()`) + ensure PowerShell relaunch script quotes paths safely. |
| Status | ✅ Done. |

### Phase 3B — Paths contract / user-data migration policy

| Field | Value |
|-------|-------|
| Goal | Define + enforce the policy that user data lives at `%APPDATA%\ATS Inc\<App>\` (never `_internal/`). PCC migrates `pcc_config.json` from project-root to `%APPDATA%\ATS Inc\Phoenix Command Center\` for frozen builds, preserving source-run behaviour. |
| Dependencies | Phase 3 |
| Risk | Medium — config-location migration must preserve existing local config or users lose state. |
| Exit criteria | `paths.user_data_dir()` is the only writer for user-data paths in PCC; config migration smoke-tested; documented in PACKAGING_CONTRACT.md. |
| Blocked-by | Frozen-exe verification (Phase 6C) to confirm path resolution under PyInstaller. |
| Approved? | **Not approved.** |

### Phase 3C — Package-data contract

| Field | Value |
|-------|-------|
| Goal | Formalize how commons-owned package data (QSS file, embedded fallback, icons) gets bundled into a downstream PyInstaller build. Document `--collect-data` / `--add-data` invocations + `--collect-all phoenix_commons` semantics. |
| Dependencies | Phase 2.5 |
| Risk | High — historically the source of frozen-exe issues. |
| Exit criteria | Documented `build.bat` snippet for commons-backed scaffolds; verified end-to-end (gated on Phase 4B-clear). |
| Blocked-by | AV (Phase 4B). |
| Approved? | **Not approved.** |

### Phase 4 — PyInstaller compatibility verification

| Field | Value |
|-------|-------|
| Goal | Prove that `pip install -e ./commons` + `pyinstaller --collect-all phoenix_commons main.py` produces a runnable exe. |
| Status | ⚠ Partial. Phase 4 (in-tree path) + Phase 4B-local (external path) both ran cleanly through PyInstaller but the exe was AV-quarantined within seconds. |
| Blocked-by | S1/AV (BLOCKERS.md). |

### Phase 5 — Wizard radios + scaffold generation

| Field | Value |
|-------|-------|
| Goal | Add two radios to the New Tool wizard (standalone default + commons-backed gated) and template the full Phoenix Tool scaffold. |
| Status | ✅ Done (Phases 5, 5A, 5B). Wizard merged to PCC `main`. |

### Phase 6 — Standalone PCC dogfood

| Field | Value |
|-------|-------|
| Goal | Build PCC itself end-to-end (PyInstaller → Inno Setup → install → launch → user-data folder created). |
| Status | ⚠ Partial. Source mode green; PyInstaller + Inno Setup succeeded; exe AV-quarantined immediately after build. |
| Blocked-by | S1/AV. |

### Phase 6A — build.bat validator fix

✅ Done.

### Phase 6B — Wizard merged to PCC main

✅ Done.

### Phase 6C — Frozen-exe dogfood after AV gate clears

| Field | Value |
|-------|-------|
| Goal | Re-run Phase 6 end-to-end after the AV gate clears (allow-list, signing, or alternate host). |
| Plan document | `phoenix-commons/docs/rollout/phase-6c-frozen-exe-dogfood-plan.md` |
| Blocked-by | S1/AV. |
| Approved? | Plan approved; execution **not approved** until §0 gate-clear lands. |

### Phase 7 — Pilot retrofit (Phoenix Checkout + Phoenix CAD)

| Field | Value |
|-------|-------|
| Goal | Retrofit the two lowest-risk production tools to import from `phoenix_commons` (theme + widgets + paths + updater). Each retrofit is a separate PR following MIGRATION_RULES.md. |
| Dependencies | Phase 6C (frozen-exe gate cleared), Phases 2.1, 2.2, 2.5 (token + widget + resource API stable) |
| Risk | Medium-low (pilot batch chosen for least-visible-change-first). |
| Exit criteria | Phoenix Checkout + Phoenix CAD pass all per-retrofit safety-checklist items (NAMING_REGISTRY.md / PACKAGING_CONTRACT.md); deployed installers verified on Justin's laptop. |
| Blocked-by | All Phase 6C + 2.1/2.2/2.5 deps. |
| Approved? | **Not approved.** |

### Phase 8 — Wave retrofit (ValveMaster + Job Tracker)

| Field | Value |
|-------|-------|
| Goal | Retrofit the remaining production tools. ValveMaster gets a visible theme swap (gray → navy); Job Tracker is the largest surface area and goes last. |
| Dependencies | Phase 7 retrofit reports approved as a green pilot |
| Risk | Medium-high (most user-visible change + most surface area). |
| Exit criteria | ValveMaster + Job Tracker pass per-retrofit safety checklist; `starter_package/` removed from Job Tracker in the same PR. |
| Approved? | **Not approved.** |

### Phase 9 — Long-term stewardship / commons v2

| Field | Value |
|-------|-------|
| Goal | Post-retrofit consolidation: commons-package distribution strategy (PyPI / private index / vendoring), component-gallery generator, ADR cadence, deprecation policy. |
| Dependencies | Phases 7 + 8 done |
| Risk | None until scoped. |
| Approved? | **Not approved.** |
