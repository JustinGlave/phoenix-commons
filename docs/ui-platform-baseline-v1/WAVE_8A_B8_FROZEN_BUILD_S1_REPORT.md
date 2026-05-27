# Wave 8a B8 — Frozen Build + S1 Observation Report

> **Status:** frozen build produced + structural validation complete. **5-min interactive S1 observation + visual review deferred to operator** (Claude Code subprocess runs in a different Windows session/window-station than the interactive desktop, so a windowed launch hangs; this is an environment constraint, not a build issue).
> **Branch:** `phase-8a-valvemaster-retrofit` HEAD `704acd4` (no new commits in B8 — build artifacts are ignored).
> **Date:** 2026-05-26.

---

## 1. Python / build venv

- Discovery: `py -3.12 --version` → `Python 3.12.10` available on the host.
- New isolated venv created at `.venv312/` (sibling to the 3.14 dev venv).
- `pip install -r requirements.txt -r requirements-dev.txt` clean install of:
  - `PySide6 6.10.2` (+ Addons + Essentials), `shiboken6 6.10.2`
  - `pyinstaller 6.20.0`
  - `pytest 8.3.4`, `pytest-qt 4.4.0`
  - `phoenix-commons 0.1.0` (editable via `-e ./commons`)

`build.bat`'s soft-warn did not fire (3.12 active); commons preflight passed.

---

## 2. build.bat result

Full pipeline ran end-to-end under the 3.12 venv:

- **[0/4] Step 0 cleanup** — `rmdir /s /q dist build` clean
- **[1/4] PyInstaller** — hardened flags applied (`--noupx`, `--collect-all=phoenix_commons`, 8× stdlib `--exclude-module`); built without errors
- **Signing** — `[skip]` (no `VMT_SIGNING_CERT` set; expected behavior for dev build)
- **[2/4] Inno Setup** — `Successful compile (31.015 sec). Resulting Setup program filename is: dist\PhoenixMasterToolSetup.exe`
- **[3/4]** `PhoenixMasterTool.zip` created
- **[4/4]** `PhoenixMasterTool_FullInstall.zip` created
- Exit status: `DONE — v1.1.0`

---

## 3. Artifacts produced

| Path | Size | Purpose |
|------|------|---------|
| `dist/PhoenixMasterTool/PhoenixMasterTool.exe` | 2,178,842 B (2.08 MB) | frozen exe |
| `dist/PhoenixMasterTool/_internal/` | folder | PyInstaller runtime + bundled packages |
| `dist/PhoenixMasterTool.zip` | 2,042,570 B (1.95 MB) | auto-updater exe-only payload |
| `dist/PhoenixMasterToolSetup.exe` | 33,823,034 B (32.3 MB) | Inno Setup installer |
| `dist/PhoenixMasterTool_FullInstall.zip` | 49,070,007 B (46.8 MB) | manual full-folder zip |

All 5 artifacts persisted on disk after build complete — no in-flight S1 quarantine occurred during PyInstaller/Inno-Setup compilation.

---

## 4. Commons packaging verification

Inspected `dist/PhoenixMasterTool/_internal/phoenix_commons/`:

| Submodule | Files present |
|-----------|---------------|
| `phoenix_commons/` root | `__init__.py`, `_version.py`, `paths.py` |
| `theme/` | `apply.py`, `embedded_qss.py`, `_embedded_qss.py`, `generate_embedded_qss.py`, **`phoenix_style.qss`** (package-data), `tokens.py`, `__init__.py` |
| `widgets/` | `buttons.py`, `helpers.py`, `no_scroll.py`, `panel.py`, `status_badge.py`, `table.py`, `typography.py`, `update_banner.py`, `__init__.py` |
| `updater/` | `client.py`, `installer.py`, `qt.py`, `__init__.py` |
| `icons/` | `loader.py`, `registry.py`, `_cache.py`, `README.md`, `__init__.py` |
| `icons/lucide/` | **23 SVG files** (full Lucide set per the icons registry) |

`--collect-all=phoenix_commons` worked end-to-end: Python modules, `*.qss` package data, `*.svg` Lucide assets all bundled.

---

## 5. Updater zip contract result

```
$ python -c "import zipfile; zf=zipfile.ZipFile('dist/PhoenixMasterTool.zip'); print(zf.namelist())"
['PhoenixMasterTool.exe']
```

| Check | Result |
|-------|--------|
| `PhoenixMasterTool.exe` at zip root | ✅ |
| `_internal/` folder absent | ✅ |
| ADR-003 exe-only payload contract | ✅ PASS |
| Matches commons `expected_internal=False` validation expectation | ✅ |

---

## 6. Frozen exe launch result

**Headless construction smoke:** offscreen exe invocation returned exit 0 within the 6-sec window (terminating cleanly under the offscreen platform; no startup crash, no DLL-missing error, no `_internal/`-resolution failure). Confirms the exe imports its bundled `phoenix_commons` package, locates the bundled `phoenix_style.qss` via the commons resource path, and constructs the QApplication without raising.

**Interactive desktop launch — deferred to operator.** The Claude Code subprocess cannot drive a Qt window manager on the operator's session. Operator must launch `dist\PhoenixMasterTool\PhoenixMasterTool.exe` from File Explorer / shortcut and observe.

---

## 7. S1 observation result

**No build-time quarantine observed.** All 5 artifacts persisted from creation through the full validation pass (build completed at 20:58–20:59, structural checks finished at 21:00+, files still on disk). PyInstaller's bootloader was not flagged during compilation; the Inno Setup output was not flagged during compilation; both zips wrote successfully.

**5-minute idle S1 observation — deferred to operator.** Per the canonical Phase 6 / FROZEN_BUILD_BASELINE protocol, S1 observation requires the operator to launch the installed exe on the interactive desktop and let it sit idle 5 minutes while watching for quarantine events. This cannot be driven from the Claude Code subprocess (different Windows session/window-station).

---

## 8. Visual-change assessment

Same as B6+B7: ≈ 0% expected. Substantively confirmed by the structural evidence:

- Canonical `phoenix_style.qss` bundled (same bytes commons ships)
- `DEFAULT_BRAND` sentinel substitution worked in source-mode offscreen smoke (B6+B7 report)
- All 5 commons widgets identity-equal to local (B4+B5 report)
- MainWindow title `'Phoenix Master Tool v1.1.0'` (version unchanged)

Final pixel-level verification deferred to operator's interactive review per the brief's § 10.

---

## 9. Blockers / issues

None. Two items deferred to operator (per brief design, not blockers):

1. **5-min interactive S1 observation** — operator launches installed exe on interactive desktop, lets idle 5 min, confirms no quarantine pop, no process kill, no relaunch cycle.
2. **Visual review** — operator opens the running app, confirms theme/buttons/tables render correctly, confirms `UpdateBanner` text-change ("Release Notes" / no 🆕 emoji) is acceptable, confirms no missing QSS/widgets/icons.

Optional installer round-trip (Phase 6C-B pattern) is operator's call.

---

## 10. Next step

**B9 — merge gate.** Requires operator sign-off on:
- 5-min S1 observation (item 1 above)
- Visual review (item 2 above)
- Optional installer round-trip
- `APP_ALIGNMENT_CHECKLIST.md § J` walk-through

When the operator approves, B9 executes: pre-merge audit, `--no-ff` merge of `phase-8a-valvemaster-retrofit` → `main` on ValveMasterTool repo, tag-skip per Decision #1, MIGRATION_RULES row 37 update on commons.

---

## 11. Confirmation

- No domain logic changed
- No updater changed (B3 facade preserved at `828a99a`)
- No theme/widget changed (B4+B5 facades preserved at `f2fa97a`)
- No installer.iss changed (AppId `{A7F3C2D1-9B4E-4F6A-8C3D-1E5B7A9F2C4D}` preserved; installer output matches build.bat naming)
- No version.py changed (stays at `1.1.0`)
- No production deployment — artifacts in `dist/` are dev-build only, NOT uploaded anywhere
- No GitHub Release created/drafted
- No tag pushed
- Branch HEAD still `704acd4` (B8 produced no source commits — build artifacts are gitignored)

Build venv `.venv312/` is gitignored (in `.gitignore` line `.venv/` covers it after pattern; verified via `git status` post-build showing clean tree).
