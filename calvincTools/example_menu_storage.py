"""
Example Menu Storage Utilities

This module provides utilities and examples for storing standard menu structures
in the cMenu database. It includes example menu structures for different menuGroups
and functions to easily add/update menu structures.
"""

import json
from typing import Dict, List, Any, Optional

from .database import get_cMenu_sessionmaker, get_cMenu_session
from .models import menuGroups


# Example menu structure for an admin menuGroup
EXAMPLE_ADMIN_MENU = {
    "menus": [
        {
            "label": "&File",
            "items": [
                {
                    "label": "&New",
                    "handler": "FormBrowse:newform",
                    "shortcut": "Ctrl+N",
                    "tooltip": "Create a new record"
                },
                {
                    "label": "&Open Table",
                    "handler": "FormBrowse:.-OPN-tbL.-",
                    "shortcut": "Ctrl+O",
                    "tooltip": "Open a database table"
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
            "label": "&Edit",
            "items": [
                {
                    "label": "Edit &Menu",
                    "handler": "FormBrowse:.-EDT-menu.-",
                    "shortcut": "Ctrl+M",
                    "tooltip": "Edit menu structure"
                },
                {
                    "separator": True
                },
                {
                    "label": "&Preferences",
                    "submenu": [
                        {
                            "label": "&Theme",
                            "handler": "FormBrowse:.-icn-thm-vwr.-",
                            "tooltip": "Change application theme"
                        },
                        {
                            "label": "&Language",
                            "handler": "handleLanguage",
                            "enabled": False,
                            "tooltip": "Change language (coming soon)"
                        }
                    ]
                }
            ]
        },
        {
            "label": "&Database",
            "items": [
                {
                    "label": "Run &SQL Statement",
                    "handler": "FormBrowse:.-ruN-sql.-",
                    "shortcut": "Ctrl+Shift+S",
                    "tooltip": "Execute SQL queries"
                },
                {
                    "label": "&Open Table",
                    "handler": "FormBrowse:.-OPN-tbL.-",
                    "tooltip": "Browse database tables"
                }
            ]
        },
        {
            "label": "&Help",
            "items": [
                {
                    "label": "&About",
                    "handler": "handleAbout",
                    "tooltip": "About this application"
                },
                {
                    "label": "&Documentation",
                    "handler": "handleDocumentation",
                    "shortcut": "F1",
                    "tooltip": "View documentation"
                }
            ]
        }
    ]
}


# Example menu structure for a user menuGroup (simpler, fewer options)
EXAMPLE_USER_MENU = {
    "menus": [
        {
            "label": "&File",
            "items": [
                {
                    "label": "&New",
                    "handler": "FormBrowse:newform",
                    "shortcut": "Ctrl+N",
                    "tooltip": "Create a new record"
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
            "label": "&View",
            "items": [
                {
                    "label": "&Tables",
                    "handler": "FormBrowse:.-OPN-tbL.-",
                    "tooltip": "Browse available tables"
                }
            ]
        },
        {
            "label": "&Help",
            "items": [
                {
                    "label": "&About",
                    "handler": "handleAbout",
                    "tooltip": "About this application"
                },
                {
                    "label": "&Documentation",
                    "handler": "handleDocumentation",
                    "shortcut": "F1",
                    "tooltip": "View documentation"
                }
            ]
        }
    ]
}


def ensure_table_exists():
    """
    Ensure the menugroup_stdmenus table exists in the database.
    
    This function reads the SQL migration script and executes it to create
    the table if it doesn't exist.
    """
    import os
    from pathlib import Path
    
    # Get the SQL file path
    sql_file = Path(__file__).parent.parent / 'sql' / 'add_standard_menus.sql'
    
    if not sql_file.exists():
        print(f"Warning: SQL migration file not found at {sql_file}")
        # Create table directly if SQL file doesn't exist
        create_table_sql = """
        CREATE TABLE IF NOT EXISTS menugroup_stdmenus (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            MenuGroup_id INTEGER NOT NULL,
            menu_structure TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (MenuGroup_id) REFERENCES cMenu_menuGroups(id) ON DELETE CASCADE,
            UNIQUE(MenuGroup_id)
        );
        CREATE INDEX IF NOT EXISTS idx_menugroup_stdmenus_group_id 
        ON menugroup_stdmenus(MenuGroup_id);
        """
        with get_cMenu_session() as session:
            session.execute(create_table_sql)
            session.commit()
        return
    
    # Read and execute SQL file
    with open(sql_file, 'r') as f:
        sql_script = f.read()
    
    with get_cMenu_session() as session:
        # Split by semicolon and execute each statement
        statements = [s.strip() for s in sql_script.split(';') if s.strip() and not s.strip().startswith('--')]
        for statement in statements:
            if statement:
                session.execute(statement)
        session.commit()


def store_menu_structure(menuGroup_id: int, menu_structure: Dict[str, Any]) -> bool:
    """
    Store or update a menu structure for a menuGroup.
    
    Args:
        menuGroup_id: The menu group ID
        menu_structure: Dictionary containing the menu structure
        
    Returns:
        True if successful, False otherwise
    """
    ensure_table_exists()
    
    try:
        menu_json = json.dumps(menu_structure, indent=2)
        
        with get_cMenu_session() as session:
            # Check if structure already exists
            existing = session.execute(
                "SELECT id FROM menugroup_stdmenus WHERE MenuGroup_id = ?",
                (menuGroup_id,)
            ).fetchone()
            
            if existing:
                # Update existing structure
                session.execute(
                    """UPDATE menugroup_stdmenus 
                       SET menu_structure = ?, updated_at = CURRENT_TIMESTAMP 
                       WHERE MenuGroup_id = ?""",
                    (menu_json, menuGroup_id)
                )
            else:
                # Insert new structure
                session.execute(
                    """INSERT INTO menugroup_stdmenus (MenuGroup_id, menu_structure) 
                       VALUES (?, ?)""",
                    (menuGroup_id, menu_json)
                )
            
            session.commit()
            return True
    except Exception as e:
        print(f"Error storing menu structure: {e}")
        return False


def get_menu_structure(menuGroup_id: int) -> Optional[Dict[str, Any]]:
    """
    Retrieve a menu structure for a menuGroup.
    
    Args:
        menuGroup_id: The menu group ID
        
    Returns:
        Dictionary containing the menu structure, or None if not found
    """
    try:
        with get_cMenu_session() as session:
            result = session.execute(
                "SELECT menu_structure FROM menugroup_stdmenus WHERE MenuGroup_id = ?",
                (menuGroup_id,)
            ).fetchone()
            
            if result:
                return json.loads(result[0])
            return None
    except Exception as e:
        print(f"Error retrieving menu structure: {e}")
        return None


def delete_menu_structure(menuGroup_id: int) -> bool:
    """
    Delete a menu structure for a menuGroup.
    
    Args:
        menuGroup_id: The menu group ID
        
    Returns:
        True if successful, False otherwise
    """
    try:
        with get_cMenu_session() as session:
            session.execute(
                "DELETE FROM menugroup_stdmenus WHERE MenuGroup_id = ?",
                (menuGroup_id,)
            )
            session.commit()
            return True
    except Exception as e:
        print(f"Error deleting menu structure: {e}")
        return False


def list_menu_structures() -> List[Dict[str, Any]]:
    """
    List all menu structures in the database.
    
    Returns:
        List of dictionaries with menuGroup_id and basic info
    """
    try:
        with get_cMenu_session() as session:
            results = session.execute(
                """SELECT ms.MenuGroup_id, mg.GroupName, ms.created_at, ms.updated_at
                   FROM menugroup_stdmenus ms
                   LEFT JOIN cMenu_menuGroups mg ON ms.MenuGroup_id = mg.id
                   ORDER BY ms.MenuGroup_id"""
            ).fetchall()
            
            return [
                {
                    'menuGroup_id': row[0],
                    'group_name': row[1],
                    'created_at': row[2],
                    'updated_at': row[3]
                }
                for row in results
            ]
    except Exception as e:
        print(f"Error listing menu structures: {e}")
        return []


def setup_example_menus():
    """
    Set up example menu structures for demonstration.
    
    This function creates example menu structures for the first two menuGroups
    if they exist in the database.
    """
    ensure_table_exists()
    
    # Get existing menuGroups
    with get_cMenu_session() as session:
        groups = session.execute(
            "SELECT id, GroupName FROM cMenu_menuGroups ORDER BY id LIMIT 2"
        ).fetchall()
    
    if len(groups) == 0:
        print("No menuGroups found in database. Please create at least one menuGroup first.")
        return
    
    # Store admin menu for first group
    if len(groups) >= 1:
        group_id, group_name = groups[0]
        print(f"Setting up admin menu for menuGroup {group_id} ({group_name})")
        if store_menu_structure(group_id, EXAMPLE_ADMIN_MENU):
            print(f"  ✓ Admin menu stored for menuGroup {group_id}")
        else:
            print(f"  ✗ Failed to store admin menu for menuGroup {group_id}")
    
    # Store user menu for second group if it exists
    if len(groups) >= 2:
        group_id, group_name = groups[1]
        print(f"Setting up user menu for menuGroup {group_id} ({group_name})")
        if store_menu_structure(group_id, EXAMPLE_USER_MENU):
            print(f"  ✓ User menu stored for menuGroup {group_id}")
        else:
            print(f"  ✗ Failed to store user menu for menuGroup {group_id}")


if __name__ == '__main__':
    """
    Command-line interface for menu storage utilities.
    
    Usage:
        python -m calvincTools.example_menu_storage setup    # Set up example menus
        python -m calvincTools.example_menu_storage list     # List all menu structures
        python -m calvincTools.example_menu_storage get <id>  # Get menu for specific group
    """
    import sys
    
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python -m calvincTools.example_menu_storage setup     # Set up example menus")
        print("  python -m calvincTools.example_menu_storage list      # List all menu structures")
        print("  python -m calvincTools.example_menu_storage get <id>  # Get menu for specific group")
        sys.exit(1)
    
    command = sys.argv[1].lower()
    
    if command == 'setup':
        print("Setting up example menu structures...")
        setup_example_menus()
        print("\nDone! Use 'list' command to see stored menus.")
    
    elif command == 'list':
        print("Menu structures in database:")
        structures = list_menu_structures()
        if not structures:
            print("  No menu structures found.")
        else:
            for struct in structures:
                print(f"  MenuGroup {struct['menuGroup_id']}: {struct['group_name']}")
                print(f"    Created: {struct['created_at']}")
                print(f"    Updated: {struct['updated_at']}")
    
    elif command == 'get':
        if len(sys.argv) < 3:
            print("Error: Please specify a menuGroup ID")
            sys.exit(1)
        
        try:
            group_id = int(sys.argv[2])
            structure = get_menu_structure(group_id)
            if structure:
                print(f"Menu structure for menuGroup {group_id}:")
                print(json.dumps(structure, indent=2))
            else:
                print(f"No menu structure found for menuGroup {group_id}")
        except ValueError:
            print("Error: menuGroup ID must be an integer")
            sys.exit(1)
    
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)
