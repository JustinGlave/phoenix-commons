# COMPONENT_CONTRACT.md

> Rules for extending the Phoenix widget catalog. Subclassing,
> composition, object-name conventions, constructor stability, and
> the absolute line between QSS-owned visuals and Python-owned
> behaviour.
>
> Read together with `PLATFORM_CONTRACT.md` (which lists who owns
> what) and `API_BOUNDARIES.md` (which lists what's public).

## Core principle

**QSS owns visuals. Python owns behaviour and layout.**

That single rule decides 90% of "should this code live in commons or
in the app" questions:

| Concern | Where it lives |
|---------|----------------|
| Padding, border-radius, font weight, background colour | `phoenix_style.qss` (or per-app QSS *addition*, not override) |
| Hover state, focus ring, disabled appearance | QSS |
| Wheel-event suppression on a spin box | Python (`NoScrollSpinBox.wheelEvent`) |
| Form layout (vertical / horizontal / grid) | Python in the consuming widget |
| Click handlers, signal wiring, validation | Python in the consuming widget |
| "Make this button red and rounded" | QSS via `objectName` |
| "Make this button trigger a save" | Python via `clicked.connect(self.save)` |

When the line is unclear, ask: *if the theme had to be replaced
wholesale, would this code need to change?* If yes → QSS owns it. If
no → Python owns it.

## Widget ownership

The current commons widget catalog (Phase 2.5):

| Widget | Owner | Notes |
|--------|-------|-------|
| `PrimaryButton`, `SecondaryButton`, `TertiaryButton` | commons | objectName driven (`secondaryButton`, `tertiaryButton`; primary uses default `QPushButton` style) |
| `PageTitle`, `PageSubtitle`, `SectionTitle`, `HintLabel` | commons | `QLabel` subclasses with semantic `objectName`s (`ProjectTitle`, `ProjectSubtitle`, `SectionTitle`, `hint`) |
| `Panel` | commons | `QWidget` with `objectName="Panel"` + a default `QVBoxLayout`; optional title via `SectionTitle` |
| `PhoenixTable` | commons | `QTableWidget` with read-only / no-selection / no-focus / alternating-row defaults |
| `NoScrollComboBox`, `NoScrollSpinBox`, `NoScrollDoubleSpinBox`, `NoScrollDateEdit` | commons | Wheel-event guards for scrollable forms |
| `UpdateBanner` | commons | Status-bar banner for "update available" — emits `install_clicked` signal |
| `button_row` | commons | Convenience layout helper |
| App-specific widgets (`CommonsDropZone`, `SidebarSprite`, `ToolCard`, etc.) | each app | Stay in app source |
| Subclasses of commons widgets | each app | `class MyHeader(PageTitle): ...` is encouraged |

Reference: `phoenix_commons.widgets` public API surface in
`API_BOUNDARIES.md`.

## Extension philosophy

**Apps extend via addendum, not fork.** The same line from
`PLATFORM_CONTRACT.md`'s core principle — applied to widgets:

- ✅ **Subclass.** `class JobTrackerToolbar(Panel): ...`
- ✅ **Compose.** A `QDialog` made of commons primitives is encouraged.
- ✅ **Override `objectName`.** Add a new name that your app's QSS
  targets, on top of (not replacing) the commons style.
- ❌ **Don't copy a commons widget into app source and modify it.**
  This is a hard rule. If you find yourself doing this, file a
  commons PR adding the extension point you need.
- ❌ **Don't rebuild a commons widget from scratch under a different
  name.** A "FastButton" that's secretly a re-implementation of
  `PrimaryButton` is a fork.
- ❌ **Don't re-implement design tokens.** `phoenix_commons.theme.tokens`
  is the only place colour constants live (see `ICON_POLICY.md` and
  the tokens module's docstring).

## Subclassing rules

When an app subclasses a commons widget:

1. **Constructor stability.** Commons widgets pin their constructor
   signatures. Subclasses receive the same arguments and may add
   their own as keyword-only:

   ```python
   class JobTrackerToolbar(Panel):
       def __init__(self, *, app_state, parent=None):
           super().__init__(title="Job Tracker", parent=parent)
           # subclass-specific setup
   ```

   Commons reserves the right to add new keyword-only constructor
   arguments in MINOR versions. Positional argument additions or
   removals are MAJOR.

2. **`objectName` discipline.** Subclasses may set their own
   `objectName` (and SHOULD, if they want app-local QSS styling),
   but must not collide with names listed in
   `phoenix_commons.theme.tokens` / `phoenix_style.qss`. See the
   reserved-name list below.

3. **No method shadowing without a reason.** Overriding
   `mousePressEvent` to add a behaviour is fine. Overriding
   `paintEvent` to repaint the whole widget defeats the point of
   subclassing — write a separate widget instead.

4. **Tests live with the subclass.** Commons doesn't test app
   subclasses; the app's `tests/test_smoke.py` should instantiate
   the subclass under `qtbot` to catch construction-time regressions.

## Composition rules

Compose freely. There is no commons-side rule against building
arbitrary layouts of commons primitives — that's the point.

The only convention:

- **Use `button_row(...)` for action-button layouts** when you want
  the standard "stretch + buttons aligned right" pattern. Don't
  reinvent it inline.
- **Use `Panel(title=...)` for card-with-title chrome** instead of
  writing a `QFrame` + `SectionTitle` + `QVBoxLayout` from scratch
  every time.
- **Use the `no_scroll` widget family inside any scrollable form**
  containing combo/spin/date inputs. Page scrolling changing form
  values is a usability bug that's been re-litigated three times
  across the family — the no-scroll widgets are the codified fix.

## `objectName` expectations

`objectName` is **part of the commons public API**. The list of
names used by `phoenix_style.qss` to apply styling:

| objectName | Widget | Used by |
|------------|--------|---------|
| (default) | `PrimaryButton` (no explicit name) | red primary action |
| `secondaryButton` | `SecondaryButton` | blue secondary |
| `tertiaryButton` | `TertiaryButton` | outline / cancel |
| `Panel` | `Panel` | dark rounded card |
| `ProjectTitle` | `PageTitle` | 14pt bold |
| `ProjectSubtitle` | `PageSubtitle` | 10pt muted |
| `SectionTitle` | `SectionTitle` | 12pt semibold |
| `hint` | `HintLabel` | 9pt muted helper |
| `UpdateBanner` | `UpdateBanner` | status-bar update strip |
| `UpdateMsg` | the message label inside `UpdateBanner` | banner copy |
| `InstallBtn` | the install button inside `UpdateBanner` | banner CTA |

### Reserved name rules

1. **Apps may not re-use a commons-owned name on an unrelated widget.**
   E.g. an app's `class FloatingPanel(QFrame)` must not
   `setObjectName("Panel")` — that triggers commons-side QSS selectors
   meant for the dark-card chrome.
2. **Apps may add new names freely** for their own widgets. Use a
   convention like `App-<tool>-<role>` if there's any risk of future
   commons collision (e.g. `App-CAD-Sidebar`).
3. **Commons-owned objectNames are stable across MINOR versions.**
   Renaming `secondaryButton` to `secondary-button` would be MAJOR.

## Styling ownership

| Where | What goes here |
|-------|----------------|
| `phoenix_commons.theme.phoenix_style.qss` | All visual rules for commons widgets. The canonical file. |
| `phoenix_commons.theme.embedded_qss.py` | Generated fallback (Phase 2.1). Same content, byte-substituted from the .qss file. |
| `phoenix_commons.theme.tokens` | Named hex constants. Tokens for everything that has a name. |
| Per-app QSS *addition* | App-specific selectors only. Appended to commons QSS, never replacing commons selectors. Future Phase 2.6 will codify the load order. |
| Inline `setStyleSheet("color: ...")` | **Forbidden** in app code. Bypasses tokens and the design system. |
| Inline `setStyleSheet("...")` in commons | Permitted only for widgets that need runtime-computed values (e.g. dynamic colour interpolation). Use `tokens.SEMANTIC_COLORS` to resolve named colours. |

## Constructor stability expectations

| Change | Allowed in | Notes |
|--------|------------|-------|
| Add a new keyword-only argument with a default | MINOR | Existing callers unaffected. |
| Rename a keyword argument | MAJOR | Even with a deprecation alias, this is a contract change. |
| Remove a keyword argument | MAJOR | |
| Change a parameter's default value | MINOR | Document in CHANGELOG. May behave as a soft-breaking change for visual regression — communicate clearly. |
| Add a positional argument | MAJOR | Positional contracts are stricter than keyword. |
| Change a method's signature | MAJOR for public methods; PATCH for private (underscore-prefixed) | |

Commons aims for **append-only constructors**. New features arrive
as new keyword-only args. Removal / reshape happens through ADRs
+ shims + a MAJOR bump.

## Behaviour vs visuals — worked examples

| Need | Right answer |
|------|--------------|
| "Make all buttons taller globally" | QSS — adjust `min-height` on the `QPushButton` selectors in `phoenix_style.qss` |
| "Make THIS button taller" | Subclass + `objectName` + app-local QSS rule for that name |
| "Add a save shortcut (Ctrl+S) to my form" | Python — connect the `QShortcut` in the form widget's `__init__` |
| "Show a tooltip on hover for a Panel" | Python — `panel.setToolTip(...)` |
| "Change the corner radius on a TertiaryButton" | QSS — modify the `border-radius` in the `tertiaryButton` selector |
| "Disable a button when the form is invalid" | Python — `setEnabled(False)` (the `:disabled` QSS selector handles the visual) |
| "Use a destructive-red save button instead of green primary" | Either subclass `PrimaryButton` with a destructive `objectName`, OR (preferred) just use the existing red `PrimaryButton`. Phoenix System A's primary is red. |

## Things this contract DOESN'T cover (yet)

- **Component composition for forms.** Form-row helpers, label/input
  alignment widgets. May land in Phase 2.6 or later.
- **Dialog and wizard primitives.** PCC has prototypes; nothing has
  been promoted to commons yet.
- **Theming variants (light mode, high-contrast).** Phoenix is dark-
  navy only for the foreseeable future. If light mode lands, the
  policy here will need to grow a "theme variant" section.
- **Animations.** Currently zero commons widgets animate. Adding
  animation requires its own contract.

When any of those land, they get their own section here or their own
companion document.

## See also

- `PLATFORM_CONTRACT.md` — ownership map (the higher-level "who
  owns what")
- `API_BOUNDARIES.md` — public-vs-private import contract
- `ICON_POLICY.md` — icon naming, sizing, and promotion rules
- `MIGRATION_RULES.md` — how to retrofit an app's widgets to commons
- `src/phoenix_commons/widgets/` — the widget catalog source
- `src/phoenix_commons/theme/phoenix_style.qss` — the canonical QSS
