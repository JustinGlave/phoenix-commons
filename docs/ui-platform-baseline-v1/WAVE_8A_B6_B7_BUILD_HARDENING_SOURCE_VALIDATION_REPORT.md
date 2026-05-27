# Wave 8a B6+B7 — Build Hardening + Source-Mode Validation Report

> **Status:** B6+B7 committed (lean-mode combined session).
> **Commit:** `704acd4` on `ValveMasterTool:phase-8a-valvemaster-retrofit`.
> **Date:** 2026-05-26.

---

## 1. Files changed

| File | Change |
|------|--------|
| `build.bat` | modified (+33 / -9) |
| `ValveMasterTool.spec` | deleted from disk (gitignored; was never tracked) |

No other files touched. CLAUDE.md from B1 already documents Python 3.12 canonical per ADR-014 — no edit needed here.

---

## 2. build.bat hardening summary

Added (per FROZEN_BUILD_BASELINE):

| Addition | Behavior |
|----------|----------|
| **Python 3.12 soft-warn** | `findstr /b "3.12."` on `python --version`; prints yellow warning if mismatch; build continues (Decision #9) |
| **Commons preflight** | `python -c "import phoenix_commons"` — hard-fail with `git submodule update --init` hint if uninitialised |
| **Step 0 cleanup** | `rmdir /s /q dist build` unconditionally (Decision #10); retired the "keep build/ for cache" branch + `build.bat clean` override |
| **`--noupx`** | added to PyInstaller flags |
| **`--collect-all=phoenix_commons`** | added |
| **Stdlib excludes** | `--exclude-module=` for `tkinter`, `_tkinter`, `tcl`, `tk`, `lib2to3`, `idlelib`, `turtle`, `turtledemo` |

Preserved verbatim:

- `--onedir --windowed`, `--icon=Normal_red.ico`, `--name=PhoenixMasterTool`
- `--add-data` for `version.py`, `phoenix_style.qss`, `inventory.py`
- `--collect-submodules=PySide6.QtCore/QtGui/QtWidgets`
- `VMT_SIGNING_CERT`-driven optional code-signing (both exe + installer subroutines)
- Inno Setup compilation step (path probes at `Program Files (x86)`, `Program Files`, `%LOCALAPPDATA%`)
- Both zip generation steps: `PhoenixMasterTool.zip` (auto-updater exe-only) + `PhoenixMasterTool_FullInstall.zip`
- Release-checklist epilogue + `pause`
- Output names: `PhoenixMasterTool.exe`, `PhoenixMasterToolSetup.exe`, `PhoenixMasterTool.zip` (AppId / install path / updater zip naming all preserved)

---

## 3. Stale spec deletion

`ValveMasterTool.spec` referenced the pre-rename entry name `valve_master_pyside6.py`. build.bat uses CLI flags exclusively — the spec was unused. Deleted from disk per Decision #4. `.spec` is gitignored (`*.spec` in `.gitignore`), so PyInstaller regenerates a fresh, correctly-named spec on each build.

---

## 4. Validation results

| Check | Result |
|-------|--------|
| `compileall -q . -x commons/` | clean ✅ |
| `phoenix_commons` 0.1.0 importable | ✅ |
| 5/5 widget identity-equal to commons (`PrimaryButton`, `SecondaryButton`, `TertiaryButton`, `PhoenixTable`, `UpdateBanner`) | ✅ |
| `tests/test_updater.py` | 10/10 green |
| `tests/test_validation.py` | 146/146 green |
| Full test suite | 156/156 green ✅ |

build.bat itself not executed (B6 is hardening definition only; full frozen build is B8 scope per the brief's "no frozen build yet" constraint).

---

## 5. Source-mode launch result

Offscreen MainWindow construction (the Claude Code subprocess runs in a different Windows session than the operator's interactive desktop, so a windowed launch hangs; offscreen platform is the canonical headless validation path per MIGRATION_RULES § 10 row 11).

```
window_title:           'Phoenix Master Tool v1.1.0'
window_size:            1500 x 940
qss_applied_length:     19420 chars
commons PrimaryButton:   0
commons SecondaryButton: 6   ← materialised inside MainWindow construction
commons TertiaryButton:  0
commons PhoenixTable:    0
no exceptions raised
ALL GATES PASS
```

The 6 `SecondaryButton` instances are the test-models / parts-list / inventory action buttons constructed during `ValveMasterMainWindow.__init__`. Other commons widgets (`PrimaryButton`, `TertiaryButton`, `PhoenixTable`, `UpdateBanner`) are constructed lazily on user interaction / context (e.g. UpdateBanner only when an update check returns a result) and thus don't appear in the initial MainWindow tree — consistent with pre-retrofit behavior.

Interactive desktop launch should be operator-driven before the merge gate (B9). Brief explicitly defers full GUI launch + visual review to the operator's interactive desktop.

---

## 6. Visual-change assessment

≈ 0% expected; substantively confirmed by:

- QSS byte-length matches the canonical phoenix_style.qss size (19,420 chars after sentinel substitution)
- All 5 DEFAULT_BRAND tokens present in the rendered QSS; all 3 brand sentinels (`__BRAND_*__`) absent (substitution worked)
- Widget identity-equal to commons (no behavior drift from inline reimplementation)
- MainWindow geometry (1500×940) matches pre-retrofit defaults
- Window title `'Phoenix Master Tool v1.1.0'` matches version.py (unchanged)

Only known user-visible delta: `UpdateBanner` text "Release Notes" vs. retired "What's new?" + dropped 🆕 emoji (documented in B4+B5 report).

---

## 7. Blockers / issues

None.

---

## 8. Next step

**B8 — frozen build + S1 observation** (operator action: activate Python 3.12 build venv, run `build.bat`, observe S1 for 5 min, validate installer round-trip).

---

## 9. Confirmation

- No domain logic changed
- No updater changed (B3 preserved at `828a99a`)
- No installer.iss changed (AppId `{A7F3C2D1-9B4E-4F6A-8C3D-1E5B7A9F2C4D}` preserved; build.bat output names match installer.iss `OutputBaseFilename=PhoenixMasterToolSetup`)
- No version.py changed (stays at `1.1.0`)
- No production deployment (no `pyinstaller` invocation, no frozen exe, no installer, no GitHub Release)

Branch HEAD: `704acd4`. Ready for **B8**.
