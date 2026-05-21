"""embedded_qss.py — AUTO-GENERATED FILE. Do not edit manually.

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

__all__ = ["EMBEDDED_QSS"]

# Raw-string so backslashes (rare in QSS but possible) don't need escaping.
EMBEDDED_QSS = r"""/*
   Phoenix Valve Checkout Tool — QSS Stylesheet
   Based on Phoenix Controls Unified Design System
   Dark Navy Theme
*/

/* ============================================================================
   ROOT
   ============================================================================ */

QMainWindow {
    background-color: #0a0e27;
    color: #ffffff;
}

QWidget {
    color: #ffffff;
    font-family: "Segoe UI", Arial, sans-serif;
    font-size: 11pt;
}

/* ============================================================================
   MENU BAR & MENUS
   ============================================================================ */

QMenuBar {
    background-color: #0a0e27;
    color: #ffffff;
    border-bottom: 1px solid #2d3748;
    padding: 4px 0px;
    spacing: 16px;
}

QMenuBar::item:selected {
    background-color: #1f2937;
    color: __BRAND_ACCENT__;
}

QMenuBar::item:pressed {
    background-color: __BRAND_SECONDARY__;
}

QMenu {
    background-color: #141829;
    color: #ffffff;
    border: 1px solid #2d3748;
    border-radius: 4px;
    padding: 4px 0px;
}

QMenu::item {
    padding: 8px 16px;
}

QMenu::item:selected {
    background-color: #1f2937;
    color: __BRAND_ACCENT__;
}

QMenu::item:pressed {
    background-color: __BRAND_SECONDARY__;
}

QMenu::separator {
    background-color: #2d3748;
    height: 1px;
    margin: 4px 0px;
}

/* ============================================================================
   BUTTONS
   ============================================================================ */

QPushButton, QToolButton {
    background-color: __BRAND_PRIMARY__;
    color: #ffffff;
    border: none;
    border-radius: 6px;
    padding: 6px 14px;
    font-weight: 600;
    font-size: 11pt;
    font-family: "Segoe UI", sans-serif;
}

QPushButton:hover, QToolButton:hover {
    background-color: #b91c1c;
}

QPushButton:pressed, QToolButton:pressed {
    background-color: #991b1b;
}

QPushButton:focus {
    outline: none;
    border: 2px solid __BRAND_ACCENT__;
}

QPushButton:disabled, QToolButton:disabled {
    background-color: #4b5563;
    color: #6b7280;
}

QPushButton#secondaryButton {
    background-color: __BRAND_SECONDARY__;
}

QPushButton#secondaryButton:hover {
    background-color: #1e40af;
}

QPushButton#tertiaryButton {
    background-color: transparent;
    border: 1px solid #4b5563;
    color: __BRAND_ACCENT__;
}

QPushButton#tertiaryButton:hover {
    background-color: #1f2937;
    border: 1px solid __BRAND_ACCENT__;
}

/* ============================================================================
   INPUTS
   ============================================================================ */

QLineEdit {
    background-color: #141829;
    color: #ffffff;
    border: 1px solid #2d3748;
    border-radius: 6px;
    padding: 6px 8px;
    selection-background-color: __BRAND_ACCENT__;
}

QLineEdit:focus {
    border: 2px solid __BRAND_ACCENT__;
}

QLineEdit:disabled {
    background-color: #050810;
    color: #6b7280;
}

QTextEdit, QPlainTextEdit {
    background-color: #141829;
    color: #ffffff;
    border: 1px solid #2d3748;
    border-radius: 6px;
    padding: 6px 8px;
    selection-background-color: __BRAND_ACCENT__;
}

QTextEdit:focus, QPlainTextEdit:focus {
    border: 2px solid __BRAND_ACCENT__;
}

QTextEdit:disabled, QPlainTextEdit:disabled {
    background-color: #050810;
    color: #6b7280;
}

/* ============================================================================
   COMBO BOX
   ============================================================================ */

QComboBox {
    background-color: #141829;
    color: #ffffff;
    border: 1px solid #2d3748;
    border-radius: 6px;
    padding: 6px 8px;
}

QComboBox:focus {
    border: 2px solid __BRAND_ACCENT__;
}

QComboBox:disabled {
    background-color: #050810;
    color: #6b7280;
}

QComboBox::drop-down {
    border: none;
    padding-right: 8px;
}

QComboBox::down-arrow {
    image: none;
}

QComboBox QAbstractItemView {
    background-color: #141829;
    color: #ffffff;
    selection-background-color: __BRAND_ACCENT__;
    border: 1px solid #2d3748;
    outline: none;
}

/* PBC linked-valves COM toggle: a 2-button widget replacing what used to be
   a binary-choice combo. The active button takes the brand-blue accent so
   the selected COM trunk is unambiguous at a glance. */

QPushButton#comToggleBtn {
    background-color: #1f2937;
    color: #cbd5e1;
    border: 1px solid #2d3748;
    border-radius: 4px;
    padding: 2px 6px;
    font-size: 9pt;
    font-weight: 500;
    min-height: 22px;
}

QPushButton#comToggleBtn:hover {
    background-color: #2d3748;
    color: #ffffff;
}

QPushButton#comToggleBtn:checked {
    background-color: __BRAND_ACCENT__;
    color: #ffffff;
    border-color: __BRAND_ACCENT__;
    font-weight: 600;
}

QPushButton#comToggleBtn:disabled {
    background-color: #050810;
    color: #4b5563;
    border-color: #1a1f2e;
}

/* ============================================================================
   DATE EDIT
   ============================================================================ */

QDateEdit {
    background-color: #141829;
    color: #ffffff;
    border: 1px solid #2d3748;
    border-radius: 6px;
    padding: 6px 8px;
}

QDateEdit:focus {
    border: 2px solid __BRAND_ACCENT__;
}

/* ============================================================================
   SPINBOX
   ============================================================================ */

QSpinBox, QDoubleSpinBox {
    background-color: #141829;
    color: #ffffff;
    border: 1px solid #2d3748;
    border-radius: 6px;
    padding: 6px 8px;
}

QSpinBox:focus, QDoubleSpinBox:focus {
    border: 2px solid __BRAND_ACCENT__;
}

QSpinBox::up-button, QDoubleSpinBox::up-button,
QSpinBox::down-button, QDoubleSpinBox::down-button {
    background-color: #050810;
    border: none;
    width: 20px;
}

QSpinBox::up-button:hover, QDoubleSpinBox::up-button:hover,
QSpinBox::down-button:hover, QDoubleSpinBox::down-button:hover {
    background-color: #1f2937;
}

/* ============================================================================
   CHECKBOXES & RADIO BUTTONS
   ============================================================================ */

QCheckBox {
    color: #ffffff;
    spacing: 8px;
}

QCheckBox::indicator {
    width: 18px;
    height: 18px;
    border-radius: 4px;
    border: 1px solid #4b5563;
    background-color: #141829;
}

QCheckBox::indicator:hover {
    border: 1px solid __BRAND_ACCENT__;
    background-color: #1f2937;
}

QCheckBox::indicator:checked {
    background-color: #10b981;
    border: 1px solid #10b981;
}

QCheckBox::indicator:focus {
    border: 2px solid __BRAND_ACCENT__;
}

QRadioButton {
    color: #ffffff;
    spacing: 8px;
}

QRadioButton::indicator {
    width: 18px;
    height: 18px;
    border-radius: 9px;
    border: 1px solid #4b5563;
    background-color: #141829;
}

QRadioButton::indicator:hover {
    border: 1px solid __BRAND_ACCENT__;
}

QRadioButton::indicator:checked {
    background-color: __BRAND_SECONDARY__;
    border: 1px solid __BRAND_SECONDARY__;
}

/* ============================================================================
   LABELS
   ============================================================================ */

QLabel {
    color: #ffffff;
    font-family: "Segoe UI", sans-serif;
}

QLabel#title {
    font-size: 20pt;
    font-weight: bold;
}

QLabel#sectionTitle {
    font-size: 13pt;
    font-weight: 600;
}

QLabel#subtitle {
    font-size: 11pt;
    color: #d1d5db;
}

QLabel#hint {
    font-size: 9pt;
    color: #9ca3af;
}

/* ============================================================================
   TABS
   ============================================================================ */

QTabWidget::pane {
    border: 1px solid #2d3748;
    background-color: #141829;
}

QTabBar::tab {
    background-color: #050810;
    color: #9ca3af;
    padding: 6px 18px;
    border: 1px solid #2d3748;
    border-bottom: none;
    border-radius: 6px 6px 0 0;
    font-weight: 500;
}

QTabBar::tab:selected {
    background-color: #141829;
    color: #ffffff;
    font-weight: 600;
    border-bottom: 3px solid __BRAND_PRIMARY__;
}

QTabBar::tab:hover:!selected {
    background-color: #1f2937;
    color: #d1d5db;
}

/* ============================================================================
   TABLES
   ============================================================================ */

QTableWidget, QTableView {
    background-color: transparent;
    alternate-background-color: rgba(10, 14, 39, 140);
    gridline-color: #2d3748;
    border: 1px solid #2d3748;
    border-radius: 6px;
    color: #ffffff;
}

QTableWidget::item, QTableView::item {
    background-color: rgba(20, 24, 41, 140);
    padding: 3px 6px;
    border: none;
    color: #ffffff;
}

QTableWidget::item:alternate, QTableView::item:alternate {
    background-color: rgba(10, 14, 39, 140);
}

QTableWidget::item:selected, QTableView::item:selected {
    background-color: #1e40af;
    color: #ffffff;
}

QTableWidget::item:hover, QTableView::item:hover {
    background-color: #1f2937;
}

QHeaderView::section {
    background-color: rgba(5, 8, 16, 180);
    color: #e5e7eb;
    padding: 6px 8px;
    border: none;
    border-right: 1px solid #2d3748;
    border-bottom: 1px solid #2d3748;
    font-weight: 600;
}

QHeaderView::section:hover {
    background-color: #1f2937;
}

/* ----------------------------------------------------------------------------
   PCC dashboard tools table — quieter header treatment.
   Targets QTableWidget#dashboardToolsTable specifically (Phoenix
   Command Center's primary surface). The default QHeaderView::section
   above stays in place for every other consumer (Phoenix CAD, Phoenix
   Checkout, etc.) — only this one widget gets the lighter chrome.
   ---------------------------------------------------------------------------- */

QTableWidget#dashboardToolsTable {
    background: transparent;
    border: none;
}

QTableWidget#dashboardToolsTable QHeaderView::section {
    background: transparent;
    color: #94a3b8;
    border: none;
    border-bottom: 1px solid #2d3748;
    padding: 8px 8px 6px 8px;
    font-size: 9pt;
    font-weight: 600;
    letter-spacing: 0.6px;
}

QTableWidget#dashboardToolsTable QHeaderView::section:hover {
    background: transparent;
    color: #cbd5e1;
}

/* ============================================================================
   TREE WIDGET (sidebar nav)
   ============================================================================ */

QTreeWidget {
    background: transparent;
    border: 1px solid #2d3748;
    border-radius: 10px;
    padding: 4px;
    color: #ececec;
    outline: none;
}

QTreeWidget::item {
    border-radius: 6px;
    padding: 5px 8px;
    margin: 1px 0;
}

QTreeWidget::item:selected {
    background: __BRAND_SECONDARY__;
    color: white;
}

QTreeWidget::item:hover:!selected {
    background: #1f2937;
}

QTreeView::branch {
    background: transparent;
}

QTreeView::branch:selected {
    background: __BRAND_SECONDARY__;
}

QTreeView::branch:hover:!selected {
    background: #1f2937;
}

/* ============================================================================
   SCROLLBARS
   ============================================================================ */

QScrollBar:vertical {
    background-color: #0a0e27;
    width: 8px;
    border: none;
}

QScrollBar::handle:vertical {
    background-color: #4b5563;
    border-radius: 4px;
    min-height: 20px;
}

QScrollBar::handle:vertical:hover {
    background-color: #6b7280;
}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0;
    border: none;
    background: none;
}

QScrollBar:horizontal {
    background-color: #0a0e27;
    height: 8px;
    border: none;
}

QScrollBar::handle:horizontal {
    background-color: #4b5563;
    border-radius: 4px;
    min-width: 20px;
}

QScrollBar::handle:horizontal:hover {
    background-color: #6b7280;
}

QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
    width: 0;
    border: none;
    background: none;
}

/* ============================================================================
   PROGRESS BAR
   ============================================================================ */

QProgressBar {
    border: 1px solid #2d3748;
    border-radius: 6px;
    background-color: #050810;
    text-align: center;
    color: #ffffff;
}

QProgressBar::chunk {
    background-color: __BRAND_PRIMARY__;
    border-radius: 4px;
}

/* ============================================================================
   GROUPBOX
   ============================================================================ */

QGroupBox {
    color: #ffffff;
    border: 1px solid #2d3748;
    border-radius: 8px;
    margin-top: 12px;
    padding-top: 12px;
    font-weight: 600;
}

QGroupBox::title {
    subcontrol-origin: margin;
    subcontrol-position: top left;
    padding: 0px 4px;
}

/* ============================================================================
   DIALOGS
   ============================================================================ */

QDialog {
    background-color: #0a0e27;
}

QMessageBox QLabel {
    color: #ffffff;
}

QMessageBox QPushButton {
    min-width: 80px;
}

/* ============================================================================
   SPLITTER
   ============================================================================ */

QSplitter::handle {
    background-color: #2d3748;
}

QSplitter::handle:hover {
    background-color: __BRAND_ACCENT__;
}

/* ============================================================================
   FRAME  — only target named/framed widgets, not bare QFrame dividers
   ============================================================================ */

QFrame[frameShape="4"], QFrame[frameShape="5"] {
    border: 1px solid #2d3748;
    background-color: transparent;
}

/* ============================================================================
   TOOLTIPS
   ============================================================================ */

QToolTip {
    background-color: #141829;
    color: #ffffff;
    border: 1px solid #2d3748;
    padding: 6px 10px;
    border-radius: 4px;
}

/* ============================================================================
   STATUS BAR
   ============================================================================ */

QStatusBar {
    background-color: #050810;
    color: #d1d5db;
    border-top: 1px solid #2d3748;
    padding: 2px 12px;
}

/* ============================================================================
   FORM LAYOUT LABELS
   ============================================================================ */

QFormLayout QLabel {
    color: #9ca3af;
}

/* ============================================================================
   APP-SPECIFIC: Panels & Cards
   ============================================================================ */

#Panel, #StatCard {
    background: rgba(20, 24, 41, 180);
    border: 1px solid #2d3748;
    border-radius: 14px;
}

/* ============================================================================
   APP-SPECIFIC: Typography (legacy object names used in code)
   ============================================================================ */

QLabel#ProjectTitle {
    font-size: 14pt;
    font-weight: 700;
    color: #ffffff;
}

QLabel#ProjectSubtitle {
    color: #9ca3af;
    font-size: 10pt;
}

QLabel#SectionTitle {
    font-size: 12pt;
    font-weight: 600;
    color: #ffffff;
}

/* ============================================================================
   APP-SPECIFIC: Update Banner
   ============================================================================ */

#UpdateBanner {
    background: rgba(30, 58, 138, 220);
    border-top: 1px solid __BRAND_ACCENT__;
}

QLabel#UpdateMsg {
    color: #93c5fd;
    font-weight: 600;
}

#InstallBtn {
    background: __BRAND_PRIMARY__;
    border: 1px solid #ef4444;
    color: white;
    font-weight: 700;
}

#InstallBtn:hover {
    background: #b91c1c;
}

#RestoreBtn {
    background: #92400e;
    border: 1px solid #f59e0b;
    color: #f59e0b;
    font-weight: 700;
}

#RestoreBtn:hover {
    background: #b45309;
}

/* ============================================================================
   STATUSBADGE — canonical operational state surface (commons primitive)
   See phoenix_commons.widgets.StatusBadge.
   ============================================================================ */

QLabel#StatusBadge {
    border-radius: 8px;
    font-weight: 600;
    font-size: 10pt;
    padding: 2px 10px;
}

QLabel#StatusBadge[compact="true"] {
    font-size: 9pt;
    padding: 1px 7px;
    border-radius: 7px;
}

/* clean — operation healthy / state is good */
QLabel#StatusBadge[variant="clean"] {
    background: rgba(34, 197, 94, 0.16);
    color: #22c55e;
}

/* dirty — has uncommitted/unsaved changes */
QLabel#StatusBadge[variant="dirty"] {
    background: rgba(245, 158, 11, 0.16);
    color: #f59e0b;
}

/* warning — non-fatal warning / partial */
QLabel#StatusBadge[variant="warning"] {
    background: rgba(245, 158, 11, 0.16);
    color: #f59e0b;
}

/* error — failure / needs attention */
QLabel#StatusBadge[variant="error"] {
    background: rgba(239, 68, 68, 0.16);
    color: #ef4444;
}

/* unknown — state unobservable / not yet scanned */
QLabel#StatusBadge[variant="unknown"] {
    background: rgba(148, 163, 184, 0.12);
    color: #94a3b8;
}

/* syncing — actively syncing (brand-accent aware) */
QLabel#StatusBadge[variant="syncing"] {
    background: rgba(59, 130, 246, 0.16);
    color: __BRAND_ACCENT__;
}

/* scanning — actively scanning (brand-accent aware) */
QLabel#StatusBadge[variant="scanning"] {
    background: rgba(59, 130, 246, 0.16);
    color: __BRAND_ACCENT__;
}

/* ============================================================================
   APP-SPECIFIC: Badges & Indicators
   ============================================================================ */

QLabel#PassBadge {
    background: #10b981;
    color: white;
    border-radius: 8px;
    font-weight: 700;
    font-size: 10pt;
    padding: 2px 6px;
}

QLabel#FailBadge {
    background: #ef4444;
    color: white;
    border-radius: 8px;
    font-weight: 700;
    font-size: 10pt;
    padding: 2px 6px;
}

QLabel#ArchivedBadge {
    background: #92400e;
    color: #f59e0b;
    border-radius: 8px;
    font-weight: 700;
    font-size: 10pt;
    padding: 0px 10px;
}

QLabel#StepBadge {
    background: __BRAND_SECONDARY__;
    color: white;
    border-radius: 19px;
    font-weight: 700;
    font-size: 13pt;
}

/* ============================================================================
   APP-SPECIFIC: Tag preview label
   ============================================================================ */

QLabel#TagPreview {
    color: __BRAND_ACCENT__;
    font-size: 10pt;
}

/* ============================================================================
   APP-SPECIFIC: Row separator in checkout list
   ============================================================================ */

QWidget#RowSep {
    background: rgba(45, 55, 72, 120);
    border: none;
}

/* ============================================================================
   APP-SPECIFIC: Checkout sheet list — tag label
   ============================================================================ */

QLabel#CheckoutTag {
    font-size: 11pt;
    font-weight: 500;
    color: #ffffff;
}

QLabel#errorLabel { color: #ef4444; }
QLabel#dialogTitle { font-size: 18pt; font-weight: 700; color: #ffffff; }
QLabel#dialogSubtitle { font-size: 11pt; color: #9ca3af; }
"""
