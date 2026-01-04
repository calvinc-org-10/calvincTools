# Standard Qt Menu Support

This document describes the standard Qt menu support added to the calvincTools cMenu system.

## Overview

The standard menu support allows menuGroups to have both the existing custom button-based menu system and modern Qt standard menus (QMenuBar with QMenu and QAction widgets). Menu structures are stored in the database as JSON and built dynamically at runtime.

## Architecture

### Components

1. **Database Schema** (`sql/add_standard_menus.sql`)
   - New table `menugroup_stdmenus` stores menu structures per menuGroup
   - JSON format for flexible menu definitions
   - Foreign key relationship to `cMenu_menuGroups`
   - Automatic timestamp tracking

2. **StandardMenuBuilder** (`calvincTools/standard_menu_builder.py`)
   - Reads menu structures from database
   - Builds QMenuBar, QMenu, and QAction widgets
   - Supports nested submenus, separators, shortcuts, tooltips
   - Connects actions to existing `menucommand_handlers`
   - Allows switching between menuGroups

3. **MenuManager** (`calvincTools/standard_menu_builder.py`)
   - Coordinates custom and standard menu systems
   - Unified interface for loading menuGroups
   - Easy menuGroup switching

4. **Example Utilities** (`calvincTools/example_menu_storage.py`)
   - Functions to store/retrieve menu structures
   - Example menu structures (admin vs user)
   - Command-line interface for menu management

## Database Schema

### menugroup_stdmenus Table

```sql
CREATE TABLE menugroup_stdmenus (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    MenuGroup_id INTEGER NOT NULL,
    menu_structure TEXT NOT NULL,  -- JSON format
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (MenuGroup_id) REFERENCES cMenu_menuGroups(id) ON DELETE CASCADE,
    UNIQUE(MenuGroup_id)
);
```

### Migration

Run the migration script to add the table to existing databases:

```bash
sqlite3 cMenudb.sqlite < sql/add_standard_menus.sql
```

Or use the Python utility which automatically ensures the table exists:

```python
from calvincTools.example_menu_storage import ensure_table_exists
ensure_table_exists()
```

## Menu Structure Format

Menu structures are stored as JSON with the following format:

```json
{
  "menus": [
    {
      "label": "&File",
      "items": [
        {
          "label": "&New",
          "handler": "handleNew",
          "shortcut": "Ctrl+N",
          "tooltip": "Create a new file",
          "enabled": true
        },
        {
          "separator": true
        },
        {
          "label": "&Preferences",
          "submenu": [
            {
              "label": "&Theme",
              "handler": "handleTheme"
            }
          ]
        },
        {
          "label": "&Exit",
          "handler": "handleExit",
          "shortcut": "Alt+F4"
        }
      ]
    },
    {
      "label": "&Help",
      "items": [
        {
          "label": "&About",
          "handler": "handleAbout"
        }
      ]
    }
  ]
}
```

### Menu Item Properties

- **label**: Menu item text (use `&` for keyboard mnemonics)
- **handler**: Method name from `menucommand_handlers` to connect
  - Direct handler: `"handler": "handleNew"`
  - FormBrowse wrapper: `"handler": "FormBrowse:formname"`
- **shortcut**: Keyboard shortcut (e.g., "Ctrl+N", "Alt+F4")
- **tooltip**: Optional tooltip/status text
- **enabled**: Optional boolean (default: true)
- **separator**: Boolean to indicate a separator line
- **submenu**: List of submenu items for nested menus

## Usage Examples

### 1. Setting Up Example Menus

```python
from calvincTools.example_menu_storage import setup_example_menus

# Creates example menus for first two menuGroups
setup_example_menus()
```

Or via command line:

```bash
python -m calvincTools.example_menu_storage setup
```

### 2. Storing a Custom Menu Structure

```python
from calvincTools.example_menu_storage import store_menu_structure

menu_structure = {
    "menus": [
        {
            "label": "&File",
            "items": [
                {
                    "label": "&New",
                    "handler": "handleNew",
                    "shortcut": "Ctrl+N"
                },
                {
                    "separator": True
                },
                {
                    "label": "&Exit",
                    "handler": "handleExit"
                }
            ]
        }
    ]
}

# Store for menuGroup 1
store_menu_structure(1, menu_structure)
```

### 3. Building Standard Menus

```python
from calvincTools.standard_menu_builder import StandardMenuBuilder

# Create builder
builder = StandardMenuBuilder(parent_widget)

# Load and build menu for a menuGroup
if builder.load_menu_structure(menuGroup_id):
    menubar = builder.build_menubar()
    # Add menubar to your window
    window.setMenuBar(menubar)
```

### 4. Using MenuManager

```python
from calvincTools.standard_menu_builder import MenuManager

# Create manager
manager = MenuManager(parent_widget)

# Load both menu systems for a menuGroup
result = manager.load_menugroup(menuGroup_id)

if result['standard_menu_loaded']:
    menubar = result['standard_menubar']
    window.setMenuBar(menubar)

# Switch to different menuGroup
result = manager.switch_menugroup(another_menuGroup_id)
```

### 5. Listing Menu Structures

```python
from calvincTools.example_menu_storage import list_menu_structures

structures = list_menu_structures()
for struct in structures:
    print(f"MenuGroup {struct['menuGroup_id']}: {struct['group_name']}")
    print(f"  Created: {struct['created_at']}")
    print(f"  Updated: {struct['updated_at']}")
```

Or via command line:

```bash
python -m calvincTools.example_menu_storage list
```

## Handler Connection

Menu actions are connected to handler methods in `menucommand_handlers.py`:

### Direct Handlers

```python
# Menu structure
{
    "label": "&About",
    "handler": "handleAbout"
}

# menucommand_handlers.py should have:
def handleAbout():
    # Show about dialog
    pass
```

### FormBrowse Handlers

For existing forms, use the `FormBrowse:` prefix:

```python
# Menu structure
{
    "label": "Edit &Menu",
    "handler": "FormBrowse:.-EDT-menu.-"
}

# This calls: FormBrowse(parent_widget, '.-EDT-menu.-')
```

### Missing Handlers

If a handler doesn't exist:
- A warning is printed to console
- The menu item is disabled
- The application continues to work

## Integration with Existing System

The standard menu support is designed for **minimal disruption**:

- **No changes to cMenu.py** - existing button-based menus work as before
- **No changes to menucommand_handlers.py** - reuses existing handlers
- **Opt-in per menuGroup** - only menuGroups with stored structures get standard menus
- **Database-driven** - all menu definitions in database, not code
- **Backward compatible** - existing functionality unchanged

### Using Both Systems

You can use both custom buttons and standard menus simultaneously:

```python
from calvincTools.cMenu import cMenu
from calvincTools.standard_menu_builder import MenuManager

# Create main window with custom menu
menu_window = cMenu(parent, initMenu=(menuGroup_id, menuID))

# Add standard menubar
manager = MenuManager(menu_window)
result = manager.load_menugroup(menuGroup_id)
if result['standard_menu_loaded']:
    menu_window.window().setMenuBar(result['standard_menubar'])
```

## Testing

### Manual Tests

Run the manual test suite:

```bash
python test_manual.py
```

This tests:
- SQL schema creation
- Menu structure storage and retrieval
- Menu structure format validation

### Automated Tests

Run pytest (requires display environment or offscreen platform):

```bash
QT_QPA_PLATFORM=offscreen pytest tests/test_standard_menus.py
```

## Design Principles

1. **Database-driven**: All menu structures in database, not hardcoded
2. **Minimal changes**: No modifications to existing core files
3. **Reuse existing**: Connect to existing menucommand_handlers
4. **menuGroup-specific**: Each menuGroup has independent menu structure
5. **Easy to extend**: Simple to add menus for new menuGroups
6. **Graceful degradation**: Missing handlers don't break the application

## Future Enhancements

Possible future improvements:

1. **Dynamic menu updates**: Update menus without restarting
2. **Menu icons**: Support for icons in menu items
3. **Context menus**: Right-click context menu support
4. **Menu state**: Remember menu state (enabled/disabled) per user
5. **Permission-based**: Show/hide menus based on user permissions
6. **Visual menu editor**: GUI tool to design menu structures

## Files

- `sql/add_standard_menus.sql` - Database migration script
- `calvincTools/standard_menu_builder.py` - Main implementation (StandardMenuBuilder, MenuManager)
- `calvincTools/example_menu_storage.py` - Storage utilities and examples
- `tests/test_standard_menus.py` - Automated test suite
- `test_manual.py` - Manual test script
- `STANDARD_MENUS.md` - This documentation

## Support

For issues or questions:
1. Check the example menu structures in `example_menu_storage.py`
2. Review the test cases in `tests/test_standard_menus.py`
3. Run manual tests with `python test_manual.py`
4. Examine SQL schema in `sql/add_standard_menus.sql`
