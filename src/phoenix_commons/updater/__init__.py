"""Updater — GitHub-Releases-based auto-update for Phoenix tools.

Phase 3 will populate this with:
- `check_for_update(owner, repo, current_version, zip_asset_name) -> UpdateInfo | None`
- `download_and_apply(info, exe_name, *, expected_internal=True, progress_callback=None) -> None`
- `UpdateInfo` dataclass
- `qt.UpdateCheckThread` — QThread wrapper for use from a GUI

Ported (parameterized as kwargs) from
`Job Tracker/starter_package/updater.py:60-188` and
`Job Tracker/starter_package/app_gui.py:52-58`.

The `expected_internal=True` default fits the full-folder updater payload
contract used by Job Tracker and Phoenix CAD. Phoenix Checkout and ValveMaster
ship exe-only updater zips and will need to opt out via `expected_internal=False`
during their per-tool retrofits — see `docs/production-inventory.md` for the
"Critical asymmetry" details.
"""
