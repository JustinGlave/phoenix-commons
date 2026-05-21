"""StatusBadge — canonical Phoenix status-semantic pill.

Lightweight QLabel subclass that wears a small coloured pill conveying
one operational state. The canonical primitive every Phoenix tool
reaches for when it needs to surface "what is the state of X right
now" without taking visual weight from primary surfaces.

Variants — a closed set (adding one requires a commons PR):

    clean    — operation succeeded / state is healthy (green)
    dirty    — has uncommitted/unsaved changes (amber)
    warning  — non-fatal warning / partial success (amber)
    error    — operation failed / state needs attention (red)
    unknown  — state unobservable / not yet scanned (muted)
    syncing  — currently syncing (brand accent)
    scanning — currently scanning (brand accent)

The widget is a thin QLabel — all styling lives in ``phoenix_style.qss``
under the ``#StatusBadge`` selectors. The variant flows to QSS via a
Qt dynamic property; compact mode flows the same way. Both adapt
automatically to BrandProfile (the syncing/scanning variants use the
brand-accent sentinel).

What this widget is **not**:

* Not a state machine — callers own transitions.
* Not a notification system — no animation, no autodismiss, no toast.
* Not a manager — no registry, no broadcast, no observer pattern.

Usage::

    from phoenix_commons.widgets import StatusBadge

    badge = StatusBadge("Clean", variant="clean")
    badge = StatusBadge("3 changes", variant="dirty", compact=True)
    badge.set_status("Syncing…", variant="syncing")
"""
from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QLabel

__all__ = ["StatusBadge"]


class StatusBadge(QLabel):
    """Coloured pill conveying an operational state.

    Args:
        text: User-visible label (e.g. ``"Clean"``, ``"3 changes"``,
            ``"Syncing…"``). Caller's responsibility to keep short —
            the pill is sized for single-line content.
        variant: One of :attr:`VARIANTS`. Invalid values fall back
            to ``"unknown"`` rather than raising.
        compact: If ``True``, renders smaller (font size + padding +
            border-radius) for use inside dense tables and lists.
        parent: Optional parent widget.

    Attributes:
        VARIANTS: The closed set of valid variant strings.
    """

    #: Canonical variant set. Adding to this set requires a commons PR
    #: and a matching QSS selector in ``phoenix_style.qss``.
    VARIANTS: frozenset[str] = frozenset({
        "clean",
        "dirty",
        "warning",
        "error",
        "unknown",
        "syncing",
        "scanning",
    })

    def __init__(
        self,
        text: str = "",
        variant: str = "unknown",
        *,
        compact: bool = False,
        parent=None,
    ) -> None:
        super().__init__(text, parent)
        self.setObjectName("StatusBadge")
        # Centre the label inside its pill so short text ("Clean")
        # doesn't drift left when the container gives it extra width.
        self.setAlignment(Qt.AlignCenter)
        # Dynamic properties drive the QSS variant / compact selectors.
        # Set BEFORE first paint so the initial style is correct.
        self._variant = variant if variant in self.VARIANTS else "unknown"
        self._compact = bool(compact)
        self.setProperty("variant", self._variant)
        self.setProperty("compact", "true" if self._compact else "false")

    # ------------------------------------------------------------------
    # Read-only state accessors
    # ------------------------------------------------------------------

    @property
    def variant(self) -> str:
        """Current variant name. Use :meth:`set_status` to change."""
        return self._variant

    @property
    def compact(self) -> bool:
        """Whether the badge is in compact mode (constructor-only)."""
        return self._compact

    # ------------------------------------------------------------------
    # State updates
    # ------------------------------------------------------------------

    def set_status(self, text: str, variant: str | None = None) -> None:
        """Update the badge text and (optionally) its variant.

        When the variant changes, triggers an ``unpolish``/``polish``
        cycle so Qt re-evaluates the property-selector QSS rules.
        Cheap — no widget recreation.

        Args:
            text: New label text.
            variant: New variant name. ``None`` (default) keeps the
                current variant. Invalid values fall back to
                ``"unknown"``.
        """
        self.setText(text)
        if variant is not None:
            new_variant = variant if variant in self.VARIANTS else "unknown"
            if new_variant != self._variant:
                self._variant = new_variant
                self.setProperty("variant", new_variant)
                # Property-selector QSS doesn't re-evaluate on property
                # change alone; we have to unpolish/polish to refresh.
                self.style().unpolish(self)
                self.style().polish(self)
