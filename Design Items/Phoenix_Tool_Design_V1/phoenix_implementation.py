"""
Phoenix Controls Unified Design System - PySide6 Implementation Guide
Dark Modern Theme Implementation with Reusable Components

This module provides:
1. How to load and apply the stylesheet
2. Reusable custom components
3. Window layout patterns
4. Best practices
"""

import sys
from pathlib import Path
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QLineEdit, QTableWidget, QTableWidgetItem,
    QStatusBar, QMenuBar, QMenu
)
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QFont, QColor, QIcon


# ============================================================================
# 1. STYLESHEET LOADING
# ============================================================================

def load_phoenix_stylesheet(app: QApplication) -> None:
    """Load and apply the Phoenix Controls QSS stylesheet to the application.
    
    Usage:
        app = QApplication(sys.argv)
        load_phoenix_stylesheet(app)
    """
    # Option 1: Load from file
    stylesheet_path = Path(__file__).parent / "phoenix_style.qss"
    if stylesheet_path.exists():
        with open(stylesheet_path, "r") as f:
            stylesheet = f.read()
        app.setStyleSheet(stylesheet)
    else:
        print(f"Warning: Stylesheet not found at {stylesheet_path}")
        # Fallback to embedded style (defined in this file)
        apply_embedded_stylesheet(app)


def apply_embedded_stylesheet(app: QApplication) -> None:
    """Fallback: Apply a minimal stylesheet directly if file not found."""
    stylesheet = """
        QMainWindow { background-color: #0a0e27; color: #ffffff; }
        QWidget { color: #ffffff; }
        QPushButton { background-color: #dc2626; color: #ffffff; 
                      border: none; border-radius: 6px; padding: 10px 16px; 
                      font-weight: 600; }
        QPushButton:hover { background-color: #b91c1c; }
        QLineEdit { background-color: #141829; color: #ffffff; 
                    border: 1px solid #2d3748; border-radius: 6px; 
                    padding: 10px 12px; }
    """
    app.setStyleSheet(stylesheet)


# ============================================================================
# 2. REUSABLE CUSTOM COMPONENTS
# ============================================================================

class PrimaryButton(QPushButton):
    """Primary action button (Phoenix Red)."""
    def __init__(self, text: str, parent=None):
        super().__init__(text, parent)
        self.setMinimumHeight(40)
        self.setCursor(Qt.PointingHandCursor)


class SecondaryButton(QPushButton):
    """Secondary action button (Dark Blue)."""
    def __init__(self, text: str, parent=None):
        super().__init__(text, parent)
        self.setObjectName("secondaryButton")
        self.setMinimumHeight(40)
        self.setCursor(Qt.PointingHandCursor)


class TertiaryButton(QPushButton):
    """Tertiary/outline button."""
    def __init__(self, text: str, parent=None):
        super().__init__(text, parent)
        self.setObjectName("tertiaryButton")
        self.setMinimumHeight(40)
        self.setCursor(Qt.PointingHandCursor)


class FormInput(QLineEdit):
    """Standard form input field with label."""
    def __init__(self, placeholder: str = "", parent=None):
        super().__init__(parent)
        self.setPlaceholderText(placeholder)
        self.setMinimumHeight(40)
        
    @staticmethod
    def with_label(label_text: str, placeholder: str = "", parent=None) -> tuple:
        """Create an input with an associated label.
        
        Returns:
            (label_widget, input_widget) tuple for easy layout
        """
        label = QLabel(label_text)
        label.setObjectName("fieldLabel")
        input_field = FormInput(placeholder, parent)
        return label, input_field


class DataTable(QTableWidget):
    """Standard data table with Phoenix styling."""
    def __init__(self, rows: int = 0, columns: int = 0, parent=None):
        super().__init__(rows, columns, parent)
        self.setAlternatingRowColors(True)
        self.setSelectionBehavior(QTableWidget.SelectRows)
        self.setSelectionMode(QTableWidget.SingleSelection)
        # Windows-style resize to content
        self.resizeColumnsToContents()


class PageTitle(QLabel):
    """Large page title label."""
    def __init__(self, text: str, parent=None):
        super().__init__(text, parent)
        self.setObjectName("title")
        font = QFont("Segoe UI", 28)
        font.setBold(True)
        self.setFont(font)


class SectionTitle(QLabel):
    """Section header label."""
    def __init__(self, text: str, parent=None):
        super().__init__(text, parent)
        self.setObjectName("sectionTitle")
        font = QFont("Segoe UI", 18)
        font.setWeight(QFont.DemiBold)
        self.setFont(font)


# ============================================================================
# 3. WINDOW LAYOUT PATTERNS
# ============================================================================

class PhoenixMainWindow(QMainWindow):
    """Base main window with Phoenix Controls design.
    
    Features:
    - Menu bar with File, Edit, View, Tools, Help
    - Title bar with app name
    - Content area with padding
    - Status bar
    """
    
    def __init__(self, title: str = "Phoenix Controls Tool"):
        super().__init__()
        self.setWindowTitle(title)
        self.setWindowIcon(QIcon("assets/phoenix_logo.png"))  # TODO: Add your icon path
        self.setMinimumSize(1024, 600)
        
        # Create menu bar
        self._create_menu_bar()
        
        # Create central widget with layout
        central_widget = QWidget()
        self.main_layout = QVBoxLayout(central_widget)
        self.main_layout.setContentsMargins(16, 16, 16, 16)  # 16px padding
        self.main_layout.setSpacing(16)  # 16px between sections
        
        self.setCentralWidget(central_widget)
        
        # Create status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready")
    
    def _create_menu_bar(self) -> None:
        """Create standard menu bar with File, Edit, View, Tools, Help."""
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu("File")
        file_menu.addAction("New")
        file_menu.addAction("Open")
        file_menu.addAction("Save")
        file_menu.addSeparator()
        file_menu.addAction("Exit")
        
        # Edit menu
        edit_menu = menubar.addMenu("Edit")
        edit_menu.addAction("Undo")
        edit_menu.addAction("Redo")
        edit_menu.addSeparator()
        edit_menu.addAction("Cut")
        edit_menu.addAction("Copy")
        edit_menu.addAction("Paste")
        
        # View menu
        view_menu = menubar.addMenu("View")
        view_menu.addAction("Refresh")
        view_menu.addAction("Zoom In")
        view_menu.addAction("Zoom Out")
        
        # Tools menu
        tools_menu = menubar.addMenu("Tools")
        tools_menu.addAction("Settings")
        
        # Help menu
        help_menu = menubar.addMenu("Help")
        help_menu.addAction("About")
        help_menu.addAction("Documentation")
    
    def add_page_title(self, text: str) -> QLabel:
        """Add a page title at the top of the content area."""
        title = PageTitle(text)
        self.main_layout.insertWidget(0, title)
        return title
    
    def add_section(self, title: str = None) -> QVBoxLayout:
        """Add a section with optional title.
        
        Returns the layout for adding widgets to this section.
        """
        section_layout = QVBoxLayout()
        section_layout.setContentsMargins(0, 0, 0, 0)
        section_layout.setSpacing(12)  # 12px spacing within sections
        
        if title:
            section_title = SectionTitle(title)
            section_layout.addWidget(section_title)
        
        self.main_layout.addLayout(section_layout)
        return section_layout


# ============================================================================
# 4. EXAMPLE: MODEL NUMBER DECODER TOOL
# ============================================================================

class ModelDecoderWindow(PhoenixMainWindow):
    """Example implementation: Model Number Decoder Tool."""
    
    def __init__(self):
        super().__init__("Model Number Decoder - Phoenix Controls")
        self.init_ui()
    
    def init_ui(self) -> None:
        """Initialize the UI."""
        self.add_page_title("Model Number Decoder")
        
        # Input section
        input_section = self.add_section("Decode Model Number")
        
        model_label, model_input = FormInput.with_label(
            "Model Number:", 
            "Enter Phoenix model number..."
        )
        input_section.addWidget(model_label)
        input_section.addWidget(model_input)
        
        # Buttons
        button_layout = QHBoxLayout()
        decode_btn = PrimaryButton("Decode")
        clear_btn = SecondaryButton("Clear")
        help_btn = TertiaryButton("Help")
        
        button_layout.addWidget(decode_btn)
        button_layout.addWidget(clear_btn)
        button_layout.addWidget(help_btn)
        button_layout.addStretch()
        
        input_section.addLayout(button_layout)
        
        # Results section
        results_section = self.add_section("Model Components")
        
        # Example results table
        results_table = DataTable(5, 2)
        results_table.setHorizontalHeaderLabels(["Component", "Value"])
        results_table.setItem(0, 0, QTableWidgetItem("Series"))
        results_table.setItem(0, 1, QTableWidgetItem("CELERIS"))
        results_table.setItem(1, 0, QTableWidgetItem("Size"))
        results_table.setItem(1, 1, QTableWidgetItem("4\""))
        
        results_section.addWidget(results_table)
        
        # Add stretch to push everything to top
        self.main_layout.addStretch()


# ============================================================================
# 5. EXAMPLE: PROJECT MANAGER TOOL
# ============================================================================

class ProjectManagerWindow(PhoenixMainWindow):
    """Example implementation: Project Manager Tool."""
    
    def __init__(self):
        super().__init__("Project Manager - Phoenix Controls")
        self.init_ui()
    
    def init_ui(self) -> None:
        """Initialize the UI."""
        self.add_page_title("Project Manager")
        
        # Toolbar section
        toolbar_section = self.add_section()
        toolbar_layout = QHBoxLayout()
        
        new_project_btn = PrimaryButton("New Project")
        search_input = FormInput("Search projects...")
        search_input.setMaximumWidth(300)
        
        toolbar_layout.addWidget(new_project_btn)
        toolbar_layout.addWidget(search_input)
        toolbar_layout.addStretch()
        
        toolbar_section.addLayout(toolbar_layout)
        
        # Projects table
        projects_section = self.add_section("Active Projects")
        
        projects_table = DataTable(10, 4)
        projects_table.setHorizontalHeaderLabels([
            "Project Name", "Status", "Manager", "Created"
        ])
        projects_table.setItem(0, 0, QTableWidgetItem("HVAC System A"))
        projects_table.setItem(0, 1, QTableWidgetItem("In Progress"))
        projects_table.setItem(0, 2, QTableWidgetItem("John Smith"))
        projects_table.setItem(0, 3, QTableWidgetItem("2024-01-15"))
        
        projects_section.addWidget(projects_table)
        
        # Add stretch
        self.main_layout.addStretch()


# ============================================================================
# 6. EXAMPLE: CHECKOUT TOOL
# ============================================================================

class CheckoutWindow(PhoenixMainWindow):
    """Example implementation: Checkout & Documentation Tool."""
    
    def __init__(self):
        super().__init__("Checkout & Documentation - Phoenix Controls")
        self.init_ui()
    
    def init_ui(self) -> None:
        """Initialize the UI."""
        self.add_page_title("Checkout & Documentation")
        
        # Order details section
        order_section = self.add_section("Order Details")
        
        po_label, po_input = FormInput.with_label(
            "Purchase Order Number:",
            "PO-XXXX-XXXX"
        )
        order_section.addWidget(po_label)
        order_section.addWidget(po_input)
        
        # Items section
        items_section = self.add_section("Items")
        
        items_table = DataTable(5, 4)
        items_table.setHorizontalHeaderLabels([
            "Item", "Quantity", "Price", "Total"
        ])
        items_table.setItem(0, 0, QTableWidgetItem("Venturi Valve"))
        items_table.setItem(0, 1, QTableWidgetItem("2"))
        items_table.setItem(0, 2, QTableWidgetItem("$150.00"))
        items_table.setItem(0, 3, QTableWidgetItem("$300.00"))
        
        items_section.addWidget(items_table)
        
        # Action buttons
        button_section = self.add_section()
        button_layout = QHBoxLayout()
        
        generate_pdf_btn = PrimaryButton("Generate PDF")
        save_draft_btn = SecondaryButton("Save Draft")
        cancel_btn = TertiaryButton("Cancel")
        
        button_layout.addWidget(generate_pdf_btn)
        button_layout.addWidget(save_draft_btn)
        button_layout.addWidget(cancel_btn)
        button_layout.addStretch()
        
        button_section.addLayout(button_layout)
        
        # Add stretch
        self.main_layout.addStretch()


# ============================================================================
# 7. BEST PRACTICES & PATTERNS
# ============================================================================

"""
BEST PRACTICES FOR PHOENIX CONTROLS APPS:

1. WINDOW INITIALIZATION:
   - Always inherit from PhoenixMainWindow for consistency
   - Set minimum size (e.g., 1024x600)
   - Load stylesheet at app startup before showing windows

2. LAYOUTS:
   - Use 16px margins for main content
   - Use 16px spacing between sections
   - Use 12px spacing within sections
   - Always add stretch() at the end to push content to top

3. FORMS:
   - Use FormInput.with_label() for consistent label+input pairs
   - Minimum height for buttons/inputs: 40px
   - Group related fields in sections

4. COLORS:
   - Primary actions (red): PrimaryButton
   - Secondary actions (blue): SecondaryButton
   - Tertiary/optional (outline): TertiaryButton
   - Use status badges for status indicators

5. TYPOGRAPHY:
   - Page titles: PageTitle (28px, bold)
   - Section titles: SectionTitle (18px, semi-bold)
   - Body text: Default label (14px)
   - Hints/helpers: Use objectName="hint" (12px)

6. TABLES:
   - Use DataTable for consistent styling
   - Always set horizontal headers
   - Use setAlternatingRowColors(True)
   - Resize columns to content on init

7. MENUS:
   - File: New, Open, Save, Exit
   - Edit: Undo, Redo, Cut, Copy, Paste
   - View: Refresh, Zoom
   - Tools: Settings
   - Help: About, Documentation

8. STATUS BAR:
   - Use for temporary messages
   - Update when actions complete
   - Keep messages brief

9. ACCESSIBILITY:
   - All buttons must have keyboard focus (Tab navigation)
   - Use meaningful placeholder text
   - Keep color contrast high (handled by stylesheet)
   - Provide keyboard shortcuts where possible

10. TESTING:
    - Test on Windows 10 and 11
    - Test with high-DPI displays (125%, 150%)
    - Verify all buttons are clickable
    - Test keyboard navigation (Tab, Enter, Escape)
"""


# ============================================================================
# 8. MAIN APP LAUNCHER
# ============================================================================

def main():
    """Main application entry point."""
    app = QApplication(sys.argv)
    
    # Load Phoenix stylesheet
    load_phoenix_stylesheet(app)
    
    # Create and show window
    # Uncomment the tool you want to run:
    
    # window = ModelDecoderWindow()
    window = ProjectManagerWindow()
    # window = CheckoutWindow()
    
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
