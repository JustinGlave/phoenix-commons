# Phoenix Controls Unified Design System
## Dark Modern Theme with Blue & Red Brand Colors

---

## 1. COLOR PALETTE

### Primary Colors
- **Dark Navy (Background)**: `#0a0e27` – Main window background
- **Navy (Secondary)**: `#141829` – Cards, panels, raised surfaces
- **Darker Navy (Tertiary)**: `#050810` – Borders, deep contrast

### Brand Accent Colors
- **Phoenix Red**: `#dc2626` – Primary action, alerts, emphasis
- **Dark Blue**: `#1e3a8a` – Secondary action, links
- **Bright Blue**: `#3b82f6` – Interactive states, focus, highlights
- **Cyan Accent**: `#0891b2` – Tertiary actions, success states

### Neutral Colors (for text & UI)
- **White**: `#ffffff` – Primary text
- **Light Gray**: `#e5e7eb` – Secondary text
- **Medium Gray**: `#9ca3af` – Placeholder, disabled text
- **Dark Gray**: `#4b5563` – Borders, subtle dividers
- **Darker Gray**: `#2d3748` – Secondary borders

### Semantic Colors
- **Success**: `#10b981` – Confirmations, completed actions
- **Warning**: `#f59e0b` – Warnings, pending states
- **Error**: `#ef4444` – Errors, destructive actions
- **Info**: `#0891b2` – Information, help text

---

## 2. TYPOGRAPHY

### Font Stack
```
Display/Headlines: 'Segoe UI', 'Inter', sans-serif (Bold, 600-700)
Body/UI: 'Segoe UI', 'Segoe UI Variable', sans-serif (Regular, 400-500)
Monospace (for model numbers, codes): 'Courier New', 'Consolas', monospace
```

### Type Scale
- **H1 (Page Title)**: 28px, Bold (700), Line-height 1.2
- **H2 (Section Title)**: 22px, Bold (700), Line-height 1.25
- **H3 (Subsection)**: 18px, Semi-bold (600), Line-height 1.3
- **Body (Default)**: 14px, Regular (400), Line-height 1.5
- **Small (Labels, hints)**: 12px, Regular (400), Line-height 1.4
- **Code/Model Numbers**: 13px, Monospace (400), Line-height 1.6

### Text Colors
- **Primary Text**: `#ffffff`
- **Secondary Text**: `#d1d5db`
- **Tertiary Text**: `#9ca3af`
- **Disabled Text**: `#6b7280` (50% opacity)

---

## 3. SPACING & RHYTHM

### Base Unit: 8px
- **XS**: 4px (micro interactions)
- **S**: 8px (tight spacing, internal padding)
- **M**: 16px (standard padding, gaps)
- **L**: 24px (section spacing)
- **XL**: 32px (major sections)
- **2XL**: 48px (page sections)

### Layout
- **Window Padding**: 16px (M)
- **Section Spacing**: 24px (L)
- **Component Padding**: 12px vertical, 16px horizontal
- **Border Radius**: 6px (standard), 4px (compact)

---

## 4. COMPONENT PATTERNS

### Buttons
```
Primary Button (Phoenix Red):
  - Background: #dc2626
  - Hover: #b91c1c
  - Active: #991b1b
  - Padding: 10px 16px
  - Border-radius: 6px
  - Font: 14px, Semi-bold (600)

Secondary Button (Dark Blue):
  - Background: #1e3a8a
  - Hover: #1e40af
  - Active: #1e3a8a (darker)
  - Padding: 10px 16px
  - Border-radius: 6px

Tertiary Button (Transparent):
  - Background: transparent
  - Border: 1px #4b5563
  - Text: #3b82f6
  - Hover: Background #1f2937
```

### Input Fields
```
Background: #141829
Border: 1px #2d3748
Border-radius: 6px
Padding: 10px 12px
Text Color: #ffffff
Placeholder: #9ca3af
Focus: Border #3b82f6, Box-shadow 0 0 0 3px rgba(59, 130, 246, 0.1)
```

### Menus & Navigation
```
Background: #0a0e27
Item Padding: 12px 16px
Text Color: #ffffff
Hover: Background #1f2937, Text #3b82f6
Active: Text #dc2626, Left border 3px #dc2626
Divider: 1px #2d3748
```

### Cards/Panels
```
Background: #141829
Border: 1px #2d3748
Border-radius: 8px
Padding: 16px
Box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3)
```

### Tables
```
Header Background: #050810
Header Text: #e5e7eb, Semi-bold (600)
Row Background: #141829
Row Hover: #1f2937
Border: 1px #2d3748
Padding: 12px 16px
```

### Status Indicators
```
Active/Success: #10b981
Pending/Warning: #f59e0b
Error/Inactive: #ef4444
Neutral: #9ca3af
```

---

## 5. INTERACTION PATTERNS

### Focus States
- **Keyboard Focus**: 2px solid #3b82f6, Border-radius 4px
- **All interactive elements** must have visible focus

### Hover States
- **Buttons**: Shift color to next shade (lighter or darker)
- **Text Links**: Underline + color change to #3b82f6
- **Table Rows**: Subtle background shift to #1f2937

### Active/Pressed States
- **Buttons**: Darker shade, slight inset shadow
- **Menu Items**: Left border accent (#dc2626), bold text

### Disabled States
- **All**: 50% opacity, cursor: not-allowed
- **Text**: #6b7280
- **Background**: No change, but opacity applied

---

## 6. WINDOW LAYOUT (Top Menu Bar Pattern)

```
┌─ File  Edit  View  Tools  Help  ────────────────────────────┐
├─────────────────────────────────────────────────────────────┤
│  [Icon] Page Title                                    [⚙] [×] │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  Main Content Area                                            │
│  (Scrollable)                                                │
│                                                               │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

### Menu Bar
- Background: `#0a0e27`
- Text: `#ffffff`
- Items: 14px, Regular
- Spacing: 16px horizontal
- Border-bottom: 1px `#2d3748`

### Title/Header Bar
- Background: `#141829`
- Title: H2 weight, left-aligned with icon
- Right side: Settings icon, minimize/maximize/close buttons
- Border-bottom: 1px `#2d3748`

---

## 7. THREE TOOLS - LAYOUT EXAMPLES

### Tool 1: Model Number Decoder/Builder
**Purpose**: Decode Phoenix model numbers, build new ones

**Layout**:
- Form-based (inputs on left, reference table on right)
- Input fields for each model component
- Real-time validation (green/red borders)
- Code display (monospace) for generated model number
- Action buttons: Copy, Clear, Save to history

**Key Components**:
- Text inputs (form fields)
- Toggle buttons (for binary options)
- Dropdown selects (for predefined choices)
- Large code display area
- History sidebar or panel

---

### Tool 2: Project Manager
**Purpose**: Track and manage Phoenix control projects

**Layout**:
- Left sidebar: Project list (searchable, filterable)
- Main area: Project details (tabs: Overview, Tasks, Documents, Settings)
- Top toolbar: Create new, Search, Filter, Sort
- Cards or table view for project summaries

**Key Components**:
- Data table (projects list)
- Detail cards (project information)
- Status badges/pills
- Form inputs (project creation/editing)
- Date pickers
- Drag-drop for task ordering (optional)
- Progress indicators

---

### Tool 3: Checkout & Documentation
**Purpose**: Manage purchase orders, document configurations

**Layout**:
- Form-based (order details at top)
- Checkout section: Items list, quantities, pricing
- Documentation section: Generated spec sheets, attachments
- Summary/review area
- Action buttons: Generate PDF, Send, Save Draft, Print

**Key Components**:
- Multi-section form
- Item list/table (add/remove rows)
- Pricing calculator
- File upload/attachment area
- Buttons for PDF generation, export
- Print preview

---

## 8. IMPLEMENTATION CHECKLIST

- [ ] Create QSS stylesheet with all color variables and component styles
- [ ] Define reusable PySide6 component classes (CustomButton, CustomInput, etc.)
- [ ] Set up consistent window sizing and layouts
- [ ] Apply stylesheet to all windows on startup
- [ ] Test focus/tab navigation across all fields
- [ ] Verify color contrast (WCAG AA minimum)
- [ ] Create icon set (using Font Awesome or similar)
- [ ] Document all deviations from standard Qt components
- [ ] Create consistent dialog/modal patterns

---

## 9. WINDOWS-SPECIFIC NOTES

- Use `QFileDialog`, `QColorDialog` for native Windows dialogs (consistency)
- System font: Segoe UI (native to Windows, excellent readability)
- Window title bar: Let Windows handle it (system chrome)
- DPI awareness: Test on high-DPI displays (scaling)
- Taskbar icon: Create 256x256 PNG with Phoenix logo

---

## 10. ASSET GUIDELINES

### Icons
- Style: Outlined, 24x24px (standard), 32x32px (toolbar)
- Stroke Width: 2px
- Color: Match context (#ffffff for light backgrounds, #3b82f6 for accents)
- Consistency: Use a single icon set (Font Awesome, Material Design, or custom)

### Images
- Model number diagrams: Use dark backgrounds
- Screenshots: Add subtle border (`1px #2d3748`) and shadow
- Logo: Phoenix Controls logo in top-left corner of main window

---

## QUICK REFERENCE: Colors to Remember

| Purpose | Color | Hex |
|---------|-------|-----|
| Primary Action | Red | `#dc2626` |
| Secondary Action | Dark Blue | `#1e3a8a` |
| Focus/Highlight | Bright Blue | `#3b82f6` |
| Success | Green | `#10b981` |
| Warning | Amber | `#f59e0b` |
| Error | Red | `#ef4444` |
| Background | Navy | `#0a0e27` |
| Cards | Navy 2 | `#141829` |
| Text | White | `#ffffff` |
| Secondary Text | Gray | `#d1d5db` |
