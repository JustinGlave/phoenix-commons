# Phase 3A Completion Packet — phoenix-commons

> Status: **Passed.** Targeted fix pass on Phase 3's updater installer — bug fix
> + PS-safe quoting hardening + regression tests. No new public API surface.

## 1. Files changed

Branch `phase-3-paths-updater`. Commit `aebdaff`. 2 files modified, no new files.

| Path | Status | What changed |
|------|--------|--------------|
| `src/phoenix_commons/updater/installer.py` | MODIFIED | (a) `download_and_apply`: captures `actual_size = tmp_zip.stat().st_size` **before** `tmp_zip.unlink()` so the error message can't race the deletion and surface `FileNotFoundError`. (b) `_build_exe_only_batch`: now routes the three PowerShell string arguments (zip path, exe path, exe name) through `_ps_literal` so single quotes can't break the inline PowerShell. |
| `tests/test_updater.py` | MODIFIED | Added 3 new regression tests: `test_incomplete_download_raises_clean_runtime_error`, `test_ps_literal_simple`, `test_ps_literal_escapes_internal_single_quotes`. |

No production tool source touched. No git operation beyond `add` + `commit` on this branch.

## 2. `git status --short`

Captured immediately after the Phase 3A commit:

```
$ git status --short
(no output — clean working tree)
```

## 3. `git diff --stat`

Phase 3A commit on its own (`HEAD~1..HEAD`):

```
 src/phoenix_commons/updater/installer.py |  21 ++++-
 tests/test_updater.py                    | 117 +++++++++++++++++++++++++++++++
 2 files changed, 135 insertions(+), 3 deletions(-)
```

Phase 3 + Phase 3A combined vs `main` (the full branch contents that will eventually merge to main):

```
 docs/rollout/phase-3-report.md           | 911 +++++++++++++++++++++++++++++++
 src/phoenix_commons/paths.py             |  75 +++
 src/phoenix_commons/updater/__init__.py  |  45 +-
 src/phoenix_commons/updater/client.py    | 119 ++++
 src/phoenix_commons/updater/installer.py | 347 ++++++++++++
 src/phoenix_commons/updater/qt.py        |  66 +++
 tests/test_paths.py                      |  75 +++
 tests/test_updater.py                    | 299 ++++++++++
 8 files changed, 1922 insertions(+), 15 deletions(-)
```

## 4. Full diff / relevant file contents

### Fix 1 — `download_and_apply` size-capture bug (`installer.py`)

**Before** (Phase 3):

```python
        if total > 0 and tmp_zip.stat().st_size < total:
            tmp_zip.unlink(missing_ok=True)
            raise RuntimeError(
                f"Download incomplete: got {tmp_zip.stat().st_size} of "
                f"{total} bytes.\nPlease try again or download manually "
                "from GitHub."
            )
```

**After** (Phase 3A):

```python
        if total > 0 and tmp_zip.stat().st_size < total:
            # Capture the size BEFORE unlinking — otherwise the stat() in
            # the error message would race the deletion and raise
            # FileNotFoundError, masking the real "incomplete download" cause.
            actual_size = tmp_zip.stat().st_size
            tmp_zip.unlink(missing_ok=True)
            raise RuntimeError(
                f"Download incomplete: got {actual_size} of "
                f"{total} bytes.\nPlease try again or download manually "
                "from GitHub."
            )
```

Two lines of real change: the `actual_size =` capture (with explanatory comment) and substituting `actual_size` into the f-string.

### Fix 2 — PS-safe quoting in `_build_exe_only_batch` (`installer.py`)

**Before** (Phase 3) — the three PowerShell-level string args (`zip_str`, `exe_name`, `exe_str`) were inline-spliced into the PowerShell command surrounded by literal single quotes. A single quote in any of those values would terminate the PS string and break the script.

**After** (Phase 3A):

```python
def _build_exe_only_batch(
    pid: int,
    zip_path: Path,
    exe_path: Path,
    exe_name: str,
) -> str:
    """Batch + inline PowerShell that waits for the parent, extracts only
    ``<exe_name>`` from the zip over the existing exe, then relaunches.

    The three PowerShell string arguments (zip path, exe path, exe name) use
    :func:`_ps_literal` so values containing a single quote can't terminate
    the PS string and break the script. The ``del`` and ``start`` lines below
    the ``powershell`` invocation are cmd.exe-level — they keep their plain
    double-quoted form, which handles Windows paths with spaces.
    """
    zip_str = str(zip_path)
    exe_str = str(exe_path)
    ps_zip = _ps_literal(zip_path)
    ps_exe = _ps_literal(exe_path)
    ps_exe_name = _ps_literal(exe_name)
    return f"""@echo off
:wait
tasklist /FI "PID eq {pid}" 2>nul | find "{pid}" >nul
if not errorlevel 1 (
    timeout /t 1 /nobreak >nul
    goto wait
)
powershell -ExecutionPolicy Bypass -Command "Add-Type -AssemblyName System.IO.Compression.FileSystem; $zip = [System.IO.Compression.ZipFile]::OpenRead({ps_zip}); $entry = $zip.Entries | Where-Object {{ $_.Name -eq {ps_exe_name} }} | Select-Object -First 1; if ($entry) {{ [System.IO.Compression.ZipFileExtensions]::ExtractToFile($entry, {ps_exe}, $true) }}; $zip.Dispose()"
del "{zip_str}"
start "" "{exe_str}"
del "%~f0"
"""
```

The PS-level arguments are now `{ps_zip}`, `{ps_exe_name}`, `{ps_exe}` (each pre-quoted with doubled-internal-apostrophes via `_ps_literal`). The cmd.exe-level `del` / `start` lines still use the raw `{zip_str}` / `{exe_str}` since those use Windows quoting, not PS quoting.

### New regression tests (`tests/test_updater.py`)

```python
# ─── Phase 3A: regression for the incomplete-download bug ────────────────────

def test_incomplete_download_raises_clean_runtime_error(tmp_path, monkeypatch) -> None:
    """Regression for the Phase 3A bug.

    When the server reports Content-Length larger than the bytes actually
    delivered, ``download_and_apply`` must raise a ``RuntimeError`` whose
    message contains both the captured-actual size and the expected total.
    Before the fix, ``tmp_zip.stat().st_size`` was evaluated AFTER
    ``tmp_zip.unlink()`` which raced the deletion and raised
    ``FileNotFoundError``, masking the real cause. The fix captures
    ``actual_size`` before the unlink call.
    """
    import os
    import sys
    import phoenix_commons.updater.installer as installer
    from phoenix_commons.updater import UpdateInfo, download_and_apply

    # download_and_apply early-exits when not frozen — pretend we are.
    monkeypatch.setattr(sys, "frozen", True, raising=False)
    fake_exe = tmp_path / "fake.exe"
    monkeypatch.setattr(sys, "executable", str(fake_exe))

    EXPECTED_TOTAL = 1000
    ACTUAL_BYTES = b"x" * 100  # Server lies about Content-Length

    class _FakeResponse:
        headers = {"Content-Length": str(EXPECTED_TOTAL)}

        def __init__(self) -> None:
            self._pos = 0

        def read(self, chunk: int) -> bytes:
            if self._pos >= len(ACTUAL_BYTES):
                return b""
            block = ACTUAL_BYTES[self._pos : self._pos + chunk]
            self._pos += len(block)
            return block

        def __enter__(self):
            return self

        def __exit__(self, *args):
            return False

    def fake_urlopen(req, timeout=60):
        return _FakeResponse()

    monkeypatch.setattr(installer.urllib.request, "urlopen", fake_urlopen)

    # Use a known temp path so we can assert cleanup happened
    known_zip = tmp_path / "predictable.zip"

    def fake_mkstemp(suffix: str = ".zip"):
        fd = os.open(str(known_zip), os.O_CREAT | os.O_RDWR)
        return (fd, str(known_zip))

    monkeypatch.setattr(installer.tempfile, "mkstemp", fake_mkstemp)

    info = UpdateInfo(
        current_version="1.0.0",
        latest_version="1.1.0",
        download_url="https://example.com/test.zip",
        release_notes="",
    )

    with pytest.raises(RuntimeError) as exc_info:
        download_and_apply(info, "MyTool.exe", expected_internal=False)

    msg = str(exc_info.value)

    # The friendly "Download incomplete" path, NOT a leaked FileNotFoundError
    assert "Download incomplete" in msg, (
        f"Expected 'Download incomplete' in message, got: {msg!r}"
    )

    # Both byte counts must be present
    assert str(len(ACTUAL_BYTES)) in msg, (
        f"Expected actual size {len(ACTUAL_BYTES)} in message, got: {msg!r}"
    )
    assert str(EXPECTED_TOTAL) in msg, (
        f"Expected total size {EXPECTED_TOTAL} in message, got: {msg!r}"
    )

    # Explicit anti-regression: the original bug surfaced as FileNotFoundError
    assert not isinstance(exc_info.value, FileNotFoundError), (
        "FileNotFoundError leaked instead of the friendly RuntimeError. "
        "The fix's actual_size capture must happen BEFORE tmp_zip.unlink()."
    )

    # And the temp zip must have been cleaned up
    assert not known_zip.exists(), (
        f"Temp zip should have been removed after the failure: {known_zip}"
    )


# ─── Phase 3A: PowerShell-safe quoting helper ───────────────────────────────

def test_ps_literal_simple() -> None:
    """_ps_literal wraps plain strings in single quotes."""
    from phoenix_commons.updater.installer import _ps_literal
    assert _ps_literal("simple") == "'simple'"
    assert _ps_literal("") == "''"


def test_ps_literal_escapes_internal_single_quotes() -> None:
    """PowerShell convention: single quote inside a single-quoted string is
    doubled. Protects exe-only batch generation when a path or exe name
    happens to contain an apostrophe."""
    from phoenix_commons.updater.installer import _ps_literal
    assert _ps_literal("with'quote") == "'with''quote'"
    assert _ps_literal("two'with'quotes") == "'two''with''quotes'"
    # And a realistic Windows path with an apostrophe (rare but legal)
    assert _ps_literal(r"C:\Users\justing's tool\app.exe") == (
        "'C:\\Users\\justing''s tool\\app.exe'"
    )
```

## 5. Exact commands run

```
# Two Edit-tool operations on installer.py (no shell command):
#   1. download_and_apply: capture actual_size before unlink
#   2. _build_exe_only_batch: replace inline PS quoting with _ps_literal

# One Edit-tool operation on tests/test_updater.py (no shell command):
#   - Append 3 regression tests after the last existing test function

# Verification
cd "C:/Users/justing/PycharmProjects/phoenix-commons" && python -m compileall -q src tests
cd "C:/Users/justing/PycharmProjects/phoenix-commons" && python -m pytest -q tests/
python -c "from phoenix_commons.updater import UpdateInfo, check_for_update, download_and_apply; from phoenix_commons.updater.qt import UpdateCheckThread; print('updater imports ok')"

# Stage + commit
cd "C:/Users/justing/PycharmProjects/phoenix-commons" && git add . && git status --short
git commit -m "Phase 3A — fix incomplete-download bug + PS-safe quoting in exe-only batch"
git log --oneline -5
git status --short
git diff --stat main..phase-3-paths-updater
```

No PyInstaller, no Inno Setup, no build, no release commands, no production-tool edits, no `git push`. No new branch (Phase 3A is a fix-up commit on `phase-3-paths-updater`, same branch as Phase 3 itself).

## 6. Raw test output

### `python -m compileall -q src tests`

```
(no output — all .py files compiled cleanly)
```

### `python -m pytest -q tests/`

```
.................................                                        [100%]
33 passed in 0.23s
```

Breakdown:
- 9 tests in `tests/test_smoke.py` (Phase 1 + Phase 2)
- 7 tests in `tests/test_paths.py` (Phase 3)
- 17 tests in `tests/test_updater.py` (14 Phase 3 + 3 Phase 3A — the incomplete-download regression and the two `_ps_literal` tests)

Total: 33 (was 30 at end of Phase 3 — +3 for Phase 3A regressions).

### `python -c "from phoenix_commons.updater import UpdateInfo, check_for_update, download_and_apply; from phoenix_commons.updater.qt import UpdateCheckThread; print('updater imports ok')"`

```
updater imports ok
```

## 7. Confirmation: no production tools were touched

Confirmed. Phase 3A wrote only to two files inside `phoenix-commons\`:

- `src/phoenix_commons/updater/installer.py`
- `tests/test_updater.py`

No reads or writes touched:
- `C:\Users\justing\PycharmProjects\Job Tracker\`
- `C:\Users\justing\PycharmProjects\Phoenix_CAD_Tool\`
- `C:\Users\justing\PycharmProjects\Phoenix-Checkout-Tool\`
- `C:\Users\justing\PycharmProjects\ValveMasterTool\`

No PyInstaller, no `build.bat`, no Inno Setup, no GitHub release commands, no production updater commands, no retrofit steps.

## 8. Confirmation: phoenix-command-center was not touched

Confirmed. No reads or writes inside `C:\Users\justing\PycharmProjects\phoenix-command-center\` during Phase 3A.

## 9. Confirmation: Phase 4 was not started

Confirmed.

- No `pyinstaller --collect-all phoenix_commons` invocation.
- No `vendor/phoenix_commons/` Plan B scaffold.
- No `refresh_commons.bat` generated.
- Phase 4 todo remains `pending`.

## 10. Open design decision (noted per Phase 3A spec)

> **Open design decision:** source-mode `user_data_dir` currently uses `%APPDATA%` for dev/prod parity. Before Phase 5 wizard templates or any production retrofit, decide whether source-mode should instead use project-local storage for safer development.

Context: Phoenix CAD's original `paths.py` returned `_SOURCE_ROOT = Path(__file__).parent` in source mode (so dev data lived inside the CAD repo). My Phase 3 port chose `%APPDATA%/<org>/<app>` in **both** frozen and source modes for parity — that means a `python main.py` from a dev's working copy reads/writes the same data that an installed `.exe` would. Pros: zero divergence between dev and prod. Cons: every test run that calls `user_data_dir(...)` without monkeypatching `APPDATA` creates a real directory under the dev's roaming profile (which is why the Phase 3 verification cleaned up `%APPDATA%\ATS Inc\Test Tool` after the un-monkeypatched smoke call).

Three options to decide before Phase 5:

1. **Keep current behaviour** — dev/prod parity. Tests already monkeypatch `APPDATA` so they never touch real roaming profile. The downside is purely interactive `python -c "..."` smoke calls.
2. **Project-local source mode** — return `Path.cwd() / ".phoenix_data" / app_name` when `is_frozen()` is False. Dev runs write into the working dir; `.gitignore` the `.phoenix_data/` folder in the wizard template. Closer to CAD's original spirit.
3. **Caller-controlled** — add an optional `force_local: bool = False` kwarg, default False. Tools that want source-tree-local data pass `force_local=True` from their `main.py` when `not is_frozen()`. Most flexible; small API addition.

Recommendation: defer the decision; either option works for Phase 4's PyInstaller gate (it doesn't exercise `user_data_dir`'s source-mode path). Lock the choice in Phase 5 before the wizard's template encodes it.

## 11. Recommendation for Phase 4

**Approve Phase 4.**

The original Phase 3 bug surfaced during this review pass — exactly the kind of issue that's easier to fix here than after Phase 4 has built scratch apps around the updater. The fix is small (one captured local), the hardening is small (three swapped variables), and there's now an explicit regression test for the size-capture race so this bug can't slip back in.

Phase 4 scope reminder: read-only on every production tool. The phase builds a scratch `main.py` inside `phoenix-commons` (or a temp dir), runs `pyinstaller --onedir --windowed --collect-all phoenix_commons scratch.py`, and verifies the resulting `.exe` launches with theme + widgets working. If the editable-install + `--collect-all` story holds, the commons-backed template becomes Phase 5's wizard default. If it doesn't, Plan B (vendoring under `vendor/phoenix_commons/` + a generated `refresh_commons.bat`) gets activated instead.

Phase 4 awaiting go/no-go.
