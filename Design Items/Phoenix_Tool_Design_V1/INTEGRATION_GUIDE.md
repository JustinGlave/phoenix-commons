# Phoenix Controls Design System - Integration Guide

## Quick Start: Apply the Design to Your Three Apps

This guide walks you through integrating the design system into your existing PySide6 applications.

---

## Step 1: Copy the Stylesheet

1. **Save the QSS file** to your project directory:
   ```
   your_project/
   ├── assets/
   │   └── phoenix_style.qss       ← Put the stylesheet here
   ├── models/
   ├── utils/
   └── main.py
   ```

2. **Load the stylesheet** at app startup (in your main.py or app initialization):
   ```python
   from pathlib import Path
   from PySide6.QtWidgets import QApplication
   
   def load_stylesheet(app):
       style_path = Path(__file__).parent / "assets" / "phoenix_style.qss"
       with open(style_path, "r") as f:
           app.setStyleSheet(f.read())
   
   # In main():
   app = QApplication(sys.argv)
   load_stylesheet(app)
   ```

---

## Step 2: Update Window Base Classes

For each of your three tools, inherit from a consistent base class:

### Option A: Quick Update (Minimal changes)
```python
from PySide6.QtWidgets import QMainWindow, QVBoxLayout

class MyToolWindow(QMainWindow):
    def __init__(self, title):
        super().__init__()
        self.setWindowTitle(title)
        self.setMinimumSize(1024, 600)
        
        # Create menu bar (File, Edit, View, Tools, Help)
        self._setup_menu_bar()
        
        # Central widget with standard layout
        central = QWidget()
        layout = QVBoxLayout(central)
        layout.setContentsMargins(16, 16, 16, 16)  # 16px padding
        layout.setSpacing(16)  # 16px spacing
        self.setCentralWidget(central)
```

### Option B: Use the Provided Base Class
Copy the `PhoenixMainWindow` class from `phoenix_implementation.py` and use it:

```python
from phoenix_implementation import PhoenixMainWindow

class MyDecoderTool(PhoenixMainWindow):
    def __init__(self):
        super().__init__("Model Decoder - Phoenix Controls")
        self.init_ui()
    
    def init_ui(self):
        # Use self.add_section() and self.main_layout
        input_section = self.add_section("Input")
        # ... add widgets to input_section
```

---

## Step 3: Update Your UI Components

### Replace Standard QPushButton

**Before:**
```python
button = QPushButton("Save")
button.clicked.connect(self.save_action)
```

**After:**
```python
from phoenix_implementation import PrimaryButton, SecondaryButton

button = PrimaryButton("Save")  # Red button
button2 = SecondaryButton("Save Draft")  # Blue button
button.clicked.connect(self.save_action)
```

### Replace QLineEdit

**Before:**
```python
name_input = QLineEdit()
name_input.setPlaceholderText("Enter name...")
```

**After:**
```python
from phoenix_implementation import FormInput

label, name_input = FormInput.with_label(
    "Project Name:",
    "Enter project name..."
)
layout.addWidget(label)
layout.addWidget(name_input)
```

### Replace QTableWidget

**Before:**
```python
table = QTableWidget(10, 3)
table.setHorizontalHeaderLabels(["Col1", "Col2", "Col3"])
```

**After:**
```python
from phoenix_implementation import DataTable

table = DataTable(10, 3)
table.setHorizontalHeaderLabels(["Col1", "Col2", "Col3"])
```

---

## Step 4: Update Page Titles and Section Headers

**Before:**
```python
title = QLabel("My Page")
title_font = QFont()
title_font.setPointSize(16)
title_font.setBold(True)
title.setFont(title_font)
```

**After:**
```python
from phoenix_implementation import PageTitle, SectionTitle

title = PageTitle("My Page")  # 28px bold
section = SectionTitle("Section Name")  # 18px semi-bold
```

---

## Step 5: Fix Layout Spacing & Padding

The design system uses consistent spacing:

```python
# Window-level layout
main_layout = QVBoxLayout()
main_layout.setContentsMargins(16, 16, 16, 16)  # 16px all sides
main_layout.setSpacing(16)  # 16px between top-level sections

# Section-level spacing
section_layout = QVBoxLayout()
section_layout.setContentsMargins(0, 0, 0, 0)  # No extra margins
section_layout.setSpacing(12)  # 12px within sections

# Form fields
form_layout = QVBoxLayout()
for label, input_widget in form_fields:
    form_layout.addWidget(label)
    form_layout.addWidget(input_widget)
    form_layout.addSpacing(12)  # 12px between fields
```

---

## Step 6: Add Menu Bar

Each tool should have consistent top-level menus:

```python
def _create_menu_bar(self):
    menubar = self.menuBar()
    
    # File menu
    file_menu = menubar.addMenu("File")
    file_menu.addAction("New", self.new_action)
    file_menu.addAction("Open", self.open_action)
    file_menu.addAction("Save", self.save_action)
    file_menu.addSeparator()
    file_menu.addAction("Exit", self.close)
    
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
    view_menu.addAction("Refresh", self.refresh_action)
    
    # Tools menu
    tools_menu = menubar.addMenu("Tools")
    tools_menu.addAction("Settings", self.settings_action)
    
    # Help menu
    help_menu = menubar.addMenu("Help")
    help_menu.addAction("About", self.about_action)
    help_menu.addAction("Documentation", self.docs_action)
```

---

## Step 7: Use Status Bar

Add consistent status messages:

```python
# In __init__
self.setStatusBar(QStatusBar())

# When performing actions
self.statusBar().showMessage("Loading data...", 2000)  # 2 sec timeout

# On completion
self.statusBar().showMessage("Data loaded successfully", 3000)

# Permanent status
permanent_label = QLabel("Ready")
self.statusBar().addPermanentWidget(permanent_label)
```

---

## Step 8: Apply Custom Styles to Specific Widgets

Use `setObjectName()` to target specific widgets with CSS:

```python
# In your code
save_button = QPushButton("Save")
save_button.setObjectName("secondaryButton")  # Use blue style

status_label = QLabel("Active")
status_label.setObjectName("statusBadge_success")  # Green badge

# The stylesheet uses these object names to apply styles:
# QPushButton#secondaryButton { background-color: #1e3a8a; }
# QWidget#statusBadge_success { background-color: #10b981; }
```

---

## Step 9: Create Custom Widgets (Optional)

For more complex controls, create custom widget classes:

```python
class StatusBadge(QLabel):
    """Colored status indicator."""
    def __init__(self, text, status="info", parent=None):
        super().__init__(text, parent)
        self.setObjectName(f"statusBadge_{status}")
        # Styling is handled by stylesheet

# Usage:
badge = StatusBadge("Active", "success")
badge_warning = StatusBadge("Pending", "warning")
badge_error = StatusBadge("Error", "error")
```

---

## Step 10: Test on Windows

1. **Run your app** after applying the stylesheet:
   ```bash
   python main.py
   ```

2. **Test on different displays:**
   - Windows 10
   - Windows 11
   - High-DPI (125%, 150%)
   - Different screen resolutions

3. **Check keyboard navigation:**
   - Tab through all buttons and inputs
   - Shift+Tab to go backwards
   - Enter to activate buttons
   - Escape to close dialogs

4. **Verify colors:**
   - Are buttons clearly red and blue?
   - Is the background dark navy?
   - Are borders subtle but visible?

---

## Common Integration Patterns

### Pattern 1: Form with Multiple Fields

```python
from phoenix_implementation import PageTitle, SectionTitle, FormInput, PrimaryButton

class OrderForm(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(16)
        
        # Title
        layout.addWidget(PageTitle("New Order"))
        
        # Form section
        form_section = self._create_form_section()
        layout.addLayout(form_section)
        
        # Buttons
        button_layout = self._create_buttons()
        layout.addLayout(button_layout)
        
        layout.addStretch()
    
    def _create_form_section(self):
        section = QVBoxLayout()
        section.addWidget(SectionTitle("Order Details"))
        
        # PO Number
        label1, input1 = FormInput.with_label("PO Number:", "PO-XXXX-XXXX")
        section.addWidget(label1)
        section.addWidget(input1)
        
        # Customer Name
        label2, input2 = FormInput.with_label("Customer:", "Enter name...")
        section.addWidget(label2)
        section.addWidget(input2)
        
        return section
    
    def _create_buttons(self):
        layout = QHBoxLayout()
        layout.addWidget(PrimaryButton("Submit"))
        layout.addWidget(PrimaryButton("Save Draft"))
        layout.addStretch()
        return layout
```

### Pattern 2: Data Table with Actions

```python
from phoenix_implementation import DataTable, PrimaryButton, SecondaryButton

class ProjectList(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(16)
        
        # Toolbar
        toolbar = QHBoxLayout()
        toolbar.addWidget(PrimaryButton("New Project"))
        toolbar.addWidget(SecondaryButton("Refresh"))
        toolbar.addStretch()
        layout.addLayout(toolbar)
        
        # Table
        self.table = DataTable(20, 4)
        self.table.setHorizontalHeaderLabels([
            "Project", "Status", "Manager", "Created"
        ])
        layout.addWidget(self.table)
        
        # Populate data
        self.load_projects()
    
    def load_projects(self):
        # Populate table rows
        self.table.setItem(0, 0, QTableWidgetItem("HVAC System A"))
        self.table.setItem(0, 1, QTableWidgetItem("Active"))
        # ... etc
```

---

## Troubleshooting

### Problem: Stylesheet not loading
**Solution:**
```python
# Check if file path is correct
style_path = Path(__file__).parent / "assets" / "phoenix_style.qss"
if not style_path.exists():
    print(f"ERROR: Stylesheet not found at {style_path}")
else:
    with open(style_path) as f:
        app.setStyleSheet(f.read())
```

### Problem: Colors look different
**Solution:**
- Make sure you're on Windows (styles may differ on other OS)
- Check that stylesheet loaded (inspect with Qt Designer)
- Verify monitor color profile

### Problem: Buttons don't look right
**Solution:**
- Check `setObjectName()` matches stylesheet
- Verify no conflicting stylesheets applied
- Check button is not disabled

### Problem: Focus outline not showing
**Solution:**
```python
# Add explicit focus style
button.setFocusPolicy(Qt.StrongFocus)
# The stylesheet will handle the visual style
```

---

## Performance Tips

1. **Load stylesheet once** at app startup, not per window
2. **Use object names** instead of inline stylesheets
3. **Avoid dynamic stylesheet updates** for many widgets
4. **Test with high-DPI** scaling enabled

---

## Next Steps

1. **Apply to Model Decoder Tool:**
   - Update window class to inherit from PhoenixMainWindow
   - Replace buttons with PrimaryButton/SecondaryButton
   - Update form inputs to FormInput
   - Add menu bar and status bar

2. **Apply to Project Manager:**
   - Use DataTable for project list
   - Update toolbar with new buttons
   - Add search/filter section
   - Consistent spacing

3. **Apply to Checkout Tool:**
   - Multi-step form with sections
   - DataTable for order items
   - Action buttons at bottom
   - Status indicators

4. **Test Integration:**
   - Run all three tools
   - Verify visual consistency
   - Test on Windows 10 & 11
   - Check keyboard navigation

5. **Optional Enhancements:**
   - Create custom icons (24x24 SVGs)
   - Add animations for button clicks
   - Create reusable form templates
   - Add dark mode preference (already dark by default)

---

## Resources

- **Design System Document:** `phoenix_design_system.md`
- **QSS Stylesheet:** `phoenix_style.qss`
- **Implementation Examples:** `phoenix_implementation.py`
- **Visual Mockups:** `phoenix_mockups.html`
- **PySide6 Docs:** https://doc.qt.io/qtforpython-6/

---

## Questions?

When in doubt, reference:
1. The design system document for color/spacing guidelines
2. The implementation examples for code patterns
3. The mockups for visual reference
4. The QSS stylesheet for component styling

Good luck with your Phoenix Controls tools! 🎨
