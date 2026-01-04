"""
Integration Example: Using Standard Menus with cMenu

This example demonstrates how to integrate the new standard Qt menu system
with the existing cMenu custom button-based menu system.

This example shows:
1. Creating a standard menu structure
2. Storing it in the database
3. Building and displaying the standard menubar alongside custom menu
4. Switching between menuGroups
"""

# Example: Basic Integration
def example_basic_integration():
    """
    Basic example of adding a standard menubar to a cMenu window.
    """
    # Note: This example shows the code structure
    # Actual execution requires a display environment
    
    print("Example code structure:")
    print("""
    from calvincTools.cMenu import cMenu
    from calvincTools.standard_menu_builder import StandardMenuBuilder
    from calvincTools.example_menu_storage import store_menu_structure, ensure_table_exists
    """)
    
    # Ensure the table exists (would run without display in proper environment)
    # from calvincTools.example_menu_storage import ensure_table_exists
    # ensure_table_exists()
    print("✓ Table would be created")
    
    # Define a simple menu structure
    menu_structure = {
        "menus": [
            {
                "label": "&File",
                "items": [
                    {
                        "label": "&New Form",
                        "handler": "FormBrowse:newform",
                        "shortcut": "Ctrl+N",
                        "tooltip": "Create a new form"
                    },
                    {
                        "separator": True
                    },
                    {
                        "label": "&Exit",
                        "handler": "handleExit",
                        "shortcut": "Alt+F4",
                        "tooltip": "Exit the application"
                    }
                ]
            },
            {
                "label": "&Tools",
                "items": [
                    {
                        "label": "Edit &Menu",
                        "handler": "FormBrowse:.-EDT-menu.-",
                        "tooltip": "Edit menu structure"
                    },
                    {
                        "label": "Open &Table",
                        "handler": "FormBrowse:.-OPN-tbL.-",
                        "tooltip": "Browse database tables"
                    },
                    {
                        "label": "Run &SQL",
                        "handler": "FormBrowse:.-ruN-sql.-",
                        "shortcut": "Ctrl+Shift+S",
                        "tooltip": "Execute SQL queries"
                    }
                ]
            }
        ]
    }
    
    # Store the menu structure for menuGroup 1 (skipped - needs menuGroup to exist)
    menuGroup_id = 1
    # store_menu_structure(menuGroup_id, menu_structure)
    print(f"✓ Menu structure defined for menuGroup {menuGroup_id}")
    
    # In your application code:
    # 
    # # Create the main cMenu window
    # menu_window = cMenu(parent=None, initMenu=(1, 0))
    # 
    # # Create and add standard menubar
    # builder = StandardMenuBuilder(menu_window)
    # if builder.load_menu_structure(1):
    #     menubar = builder.build_menubar()
    #     menu_window.window().setMenuBar(menubar)
    #     print("✓ Standard menubar added to cMenu window")
    # 
    # # Show the window
    # menu_window.show()


# Example: Using MenuManager
def example_menu_manager():
    """
    Example using MenuManager to coordinate both menu systems.
    """
    print("Example code structure:")
    print("""
    from calvincTools.standard_menu_builder import MenuManager
    from calvincTools.example_menu_storage import setup_example_menus
    
    # Set up example menus for multiple groups
    setup_example_menus()
    """)
    
    # In your application code:
    #
    # # Create MenuManager
    # manager = MenuManager(parent_widget)
    # 
    # # Load menuGroup 1 (admin menu)
    # result = manager.load_menugroup(1)
    # if result['standard_menu_loaded']:
    #     menubar = result['standard_menubar']
    #     window.setMenuBar(menubar)
    #     print(f"✓ Loaded menuGroup 1 with {len(menubar.actions())} menus")
    # 
    # # Later, switch to menuGroup 2 (user menu)
    # result = manager.switch_menugroup(2)
    # if result['standard_menu_loaded']:
    #     menubar = result['standard_menubar']
    #     window.setMenuBar(menubar)
    #     print(f"✓ Switched to menuGroup 2 with {len(menubar.actions())} menus")


# Example: Custom Menu Structure for Specific Use Case
def example_custom_structure():
    """
    Example of creating a custom menu structure for a specific use case.
    """
    print("Example menu structure for data entry application:")
    
    # Define a menu structure for a data entry application
    data_entry_menu = {
        "menus": [
            {
                "label": "&Records",
                "items": [
                    {
                        "label": "&New Record",
                        "handler": "FormBrowse:newrecord",
                        "shortcut": "Ctrl+N"
                    },
                    {
                        "label": "&Search",
                        "handler": "FormBrowse:search",
                        "shortcut": "Ctrl+F"
                    },
                    {
                        "separator": True
                    },
                    {
                        "label": "&Import",
                        "submenu": [
                            {
                                "label": "From &Excel",
                                "handler": "handleImportExcel"
                            },
                            {
                                "label": "From &CSV",
                                "handler": "handleImportCSV"
                            }
                        ]
                    },
                    {
                        "label": "&Export",
                        "submenu": [
                            {
                                "label": "To &Excel",
                                "handler": "handleExportExcel"
                            },
                            {
                                "label": "To &PDF",
                                "handler": "handleExportPDF"
                            }
                        ]
                    }
                ]
            },
            {
                "label": "&View",
                "items": [
                    {
                        "label": "&Tables",
                        "handler": "FormBrowse:.-OPN-tbL.-"
                    },
                    {
                        "separator": True
                    },
                    {
                        "label": "&Refresh",
                        "handler": "handleRefresh",
                        "shortcut": "F5"
                    }
                ]
            },
            {
                "label": "&Help",
                "items": [
                    {
                        "label": "&Documentation",
                        "handler": "handleDocumentation",
                        "shortcut": "F1"
                    },
                    {
                        "label": "&About",
                        "handler": "handleAbout"
                    }
                ]
            }
        ]
    }
    
    # Store for menuGroup 3 (assuming it's a data entry group)
    menuGroup_id = 3
    # store_menu_structure(menuGroup_id, data_entry_menu)
    print(f"✓ Custom menu structure defined (has {len(data_entry_menu['menus'])} top-level menus)")


# Example: Conditional Menu Items
def example_conditional_menus():
    """
    Example showing how to create different menus based on user roles.
    """
    print("Example: Role-based menu structures")
    
    # Admin menu - full access
    admin_menu = {
        "menus": [
            {
                "label": "&File",
                "items": [
                    {"label": "&New", "handler": "handleNew", "shortcut": "Ctrl+N"},
                    {"separator": True},
                    {"label": "&Exit", "handler": "handleExit"}
                ]
            },
            {
                "label": "&Admin",
                "items": [
                    {"label": "&User Management", "handler": "FormBrowse:users"},
                    {"label": "&System Settings", "handler": "FormBrowse:settings"},
                    {"label": "Edit &Menu", "handler": "FormBrowse:.-EDT-menu.-"}
                ]
            },
            {
                "label": "&Database",
                "items": [
                    {"label": "Run &SQL", "handler": "FormBrowse:.-ruN-sql.-"},
                    {"label": "&Open Table", "handler": "FormBrowse:.-OPN-tbL.-"}
                ]
            }
        ]
    }
    
    # User menu - limited access
    user_menu = {
        "menus": [
            {
                "label": "&File",
                "items": [
                    {"label": "&New", "handler": "handleNew", "shortcut": "Ctrl+N"},
                    {"separator": True},
                    {"label": "&Exit", "handler": "handleExit"}
                ]
            },
            {
                "label": "&View",
                "items": [
                    {"label": "&My Records", "handler": "FormBrowse:myrecords"},
                    {"label": "&Reports", "handler": "FormBrowse:reports"}
                ]
            }
        ]
    }
    
    # Store admin menu for menuGroup 10
    # store_menu_structure(10, admin_menu)
    print(f"✓ Admin menu defined ({len(admin_menu['menus'])} menus)")
    
    # Store user menu for menuGroup 11
    # store_menu_structure(11, user_menu)
    print(f"✓ User menu defined ({len(user_menu['menus'])} menus)")
    
    # In application code:
    # user_role = get_current_user_role()
    # if user_role == 'admin':
    #     manager.load_menugroup(10)  # Load admin menu
    # else:
    #     manager.load_menugroup(11)  # Load user menu


def main():
    """
    Run all examples.
    """
    print("=" * 60)
    print("Standard Menu Integration Examples")
    print("=" * 60)
    
    print("\n1. Basic Integration")
    print("-" * 60)
    example_basic_integration()
    
    print("\n2. Using MenuManager")
    print("-" * 60)
    example_menu_manager()
    
    print("\n3. Custom Menu Structure")
    print("-" * 60)
    example_custom_structure()
    
    print("\n4. Conditional Menus")
    print("-" * 60)
    example_conditional_menus()
    
    print("\n" + "=" * 60)
    print("Integration Notes:")
    print("=" * 60)
    print("• No changes needed to cMenu.py or menucommand_handlers.py")
    print("• Standard menus and custom button menus work independently")
    print("• Each menuGroup can have its own standard menu structure")
    print("• Missing handlers are handled gracefully (warnings printed)")
    print("• Switching menuGroups updates both menu systems")
    print("\nSee STANDARD_MENUS.md for full documentation")


if __name__ == '__main__':
    main()
