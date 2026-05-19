"""generate_embedded_qss.py — generate ``embedded_qss.py`` from ``phoenix_style.qss``.

The ONLY sanctioned way to update ``embedded_qss.py``. Hand-editing
the generated file is prohibited (it's the canonical fallback used by
``apply.py`` when the runtime QSS resource is missing — drift between
the QSS file and the embedded fallback is the architectural debt
Phase 2.1 retires).

Usage:

    # From the repo root, after ``pip install -e .``:
    python -m phoenix_commons.theme.generate_embedded_qss

    # Or directly:
    python src/phoenix_commons/theme/generate_embedded_qss.py

Both invocations produce a byte-for-byte identical
``src/phoenix_commons/theme/embedded_qss.py``. Determinism is part of
the contract — CI (or a future lint hook) can rerun the generator and
``git diff`` to detect stale embedded fallbacks.

Exit codes:
    0   embedded_qss.py written (or already up to date)
    2   phoenix_style.qss not found
    3   phoenix_style.qss content uses ``\"\"\"`` and would break the raw-string
        wrapper — bail rather than emit invalid Python
"""
from __future__ import annotations

import sys
from pathlib import Path

HERE       = Path(__file__).resolve().parent
QSS_FILE   = HERE / "phoenix_style.qss"
OUT_FILE   = HERE / "embedded_qss.py"

HEADER = '''"""embedded_qss.py — AUTO-GENERATED FILE. Do not edit manually.

Generated from ``phoenix_style.qss`` by
``phoenix_commons.theme.generate_embedded_qss``. Re-run that script
whenever the canonical QSS changes; the generator is deterministic so
identical input produces identical output (CI can diff to detect stale
fallbacks).

Public API:
    EMBEDDED_QSS : str
        The full Phoenix dark-navy QSS embedded as a raw-string literal.
        Used by ``apply_dark_theme`` as a fallback when the on-disk
        ``phoenix_style.qss`` resource cannot be resolved at runtime.
"""
from __future__ import annotations

# Raw-string so backslashes (rare in QSS but possible) don't need escaping.
EMBEDDED_QSS = r"""'''

FOOTER = '"""\n'


def render(qss_text: str) -> str:
    """Build the full content of ``embedded_qss.py`` for the given QSS.

    Deterministic: identical ``qss_text`` always yields byte-identical
    output. Line endings are normalised to ``\\n``.
    """
    # Normalise line endings (in case the QSS file is checked out with
    # CRLF on Windows). Generated file always uses LF.
    qss_text = qss_text.replace("\r\n", "\n").replace("\r", "\n")
    return HEADER + qss_text + FOOTER


def main(argv: list[str] | None = None) -> int:
    if not QSS_FILE.exists():
        print(f"ERROR: canonical QSS not found at {QSS_FILE}", file=sys.stderr)
        return 2

    qss_text = QSS_FILE.read_text(encoding="utf-8")

    # Raw-string wrapper breaks if the source contains the terminator.
    # QSS shouldn't legitimately contain ``\"\"\"`` so this is a guard, not a
    # routine case.
    if '"""' in qss_text:
        print(
            'ERROR: phoenix_style.qss contains triple-double-quotes which '
            'would break the raw-string wrapper. Refactor the QSS to avoid '
            '\"\"\" before regenerating.',
            file=sys.stderr,
        )
        return 3

    rendered = render(qss_text)

    # Idempotent write: skip if the on-disk file already matches the
    # rendered output. Lets CI run the generator without producing a
    # spurious diff when the embedded file is already up to date.
    if OUT_FILE.exists() and OUT_FILE.read_text(encoding="utf-8") == rendered:
        print(f"OK: {OUT_FILE.name} already up to date "
              f"({len(qss_text):,} chars of QSS embedded).")
        return 0

    # Force LF line endings on the generated file so it's byte-identical
    # across Windows / macOS / Linux generators (matches the QSS-file
    # normalisation above).
    OUT_FILE.write_text(rendered, encoding="utf-8", newline="\n")
    print(f"Wrote {OUT_FILE} ({len(rendered):,} chars; "
          f"{len(qss_text):,} chars of QSS embedded).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
