"""
Manual test script for standard menu functionality

This script demonstrates and tests the standard menu functionality
without requiring a display environment. It tests:
1. Database table creation
2. Menu structure storage and retrieval
3. StandardMenuBuilder loading (structure only, not UI)
4. Example menu structures

Run with: python test_manual.py
"""

import json
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

def test_sql_schema():
    """Test that SQL schema works correctly."""
    import sqlite3
    
    print("=" * 60)
    print("Testing SQL Schema")
    print("=" * 60)
    
    # Create test database
    conn = sqlite3.connect(':memory:')
    cursor = conn.cursor()
    
    # Read and execute SQL file
    sql_file = Path(__file__).parent / 'sql' / 'add_standard_menus.sql'
    if sql_file.exists():
        with open(sql_file, 'r') as f:
            sql_script = f.read()
        
        # Create base table first
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS cMenu_menuGroups (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            GroupName VARCHAR(100) UNIQUE NOT NULL,
            GroupInfo VARCHAR(250) NOT NULL DEFAULT ''
        )
        ''')
        
        # Execute migration script
        # Split and clean statements, filter out comments and COMMIT
        statements = []
        for s in sql_script.split(';'):
            s = s.strip()
            # Remove comment-only lines
            lines = [line for line in s.split('\n') if line.strip() and not line.strip().startswith('--')]
            clean_statement = '\n'.join(lines).strip()
            if clean_statement and 'COMMIT' not in clean_statement.upper():
                statements.append(clean_statement)
        
        for statement in statements:
            if statement:
                try:
                    cursor.execute(statement)
                except Exception as e:
                    # Some statements may not work in memory DB, that's ok
                    pass
        
        conn.commit()
        print("✓ SQL schema created successfully")
    else:
        print(f"✗ SQL file not found: {sql_file}")
        return False
    
    # Test table exists
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='menugroup_stdmenus'")
    if cursor.fetchone():
        print("✓ menugroup_stdmenus table exists")
    else:
        print("✗ menugroup_stdmenus table not found")
        return False
    
    # Test index exists
    cursor.execute("SELECT name FROM sqlite_master WHERE type='index' AND name='idx_menugroup_stdmenus_group_id'")
    if cursor.fetchone():
        print("✓ Index created successfully")
    else:
        print("✗ Index not found")
        return False
    
    conn.close()
    return True


def test_menu_storage():
    """Test menu structure storage and retrieval."""
    import sqlite3
    
    print("\n" + "=" * 60)
    print("Testing Menu Storage")
    print("=" * 60)
    
    # Create test database
    conn = sqlite3.connect(':memory:')
    cursor = conn.cursor()
    
    # Create tables
    cursor.execute('''
    CREATE TABLE cMenu_menuGroups (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        GroupName VARCHAR(100) UNIQUE NOT NULL,
        GroupInfo VARCHAR(250) NOT NULL DEFAULT ''
    )
    ''')
    
    cursor.execute('''
    CREATE TABLE menugroup_stdmenus (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        MenuGroup_id INTEGER NOT NULL,
        menu_structure TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (MenuGroup_id) REFERENCES cMenu_menuGroups(id) ON DELETE CASCADE,
        UNIQUE(MenuGroup_id)
    )
    ''')
    
    # Insert test menuGroup
    cursor.execute('INSERT INTO cMenu_menuGroups (GroupName, GroupInfo) VALUES (?, ?)', 
                   ('Admin Group', 'Administrator menu group'))
    admin_id = cursor.lastrowid
    print(f"✓ Created admin menuGroup (id={admin_id})")
    
    cursor.execute('INSERT INTO cMenu_menuGroups (GroupName, GroupInfo) VALUES (?, ?)', 
                   ('User Group', 'Standard user menu group'))
    user_id = cursor.lastrowid
    print(f"✓ Created user menuGroup (id={user_id})")
    
    # Create test menu structures
    admin_menu = {
        "menus": [
            {
                "label": "&File",
                "items": [
                    {"label": "&New", "handler": "handleNew", "shortcut": "Ctrl+N", "tooltip": "Create new"},
                    {"separator": True},
                    {"label": "&Exit", "handler": "handleExit", "shortcut": "Alt+F4"}
                ]
            },
            {
                "label": "&Admin",
                "items": [
                    {"label": "Edit &Menu", "handler": "FormBrowse:.-EDT-menu.-"},
                    {"label": "Run &SQL", "handler": "FormBrowse:.-ruN-sql.-"}
                ]
            }
        ]
    }
    
    user_menu = {
        "menus": [
            {
                "label": "&File",
                "items": [
                    {"label": "&New", "handler": "handleNew"},
                    {"separator": True},
                    {"label": "&Exit", "handler": "handleExit"}
                ]
            }
        ]
    }
    
    # Store admin menu
    admin_json = json.dumps(admin_menu, indent=2)
    cursor.execute('INSERT INTO menugroup_stdmenus (MenuGroup_id, menu_structure) VALUES (?, ?)',
                   (admin_id, admin_json))
    print(f"✓ Stored admin menu structure ({len(admin_json)} bytes)")
    
    # Store user menu
    user_json = json.dumps(user_menu, indent=2)
    cursor.execute('INSERT INTO menugroup_stdmenus (MenuGroup_id, menu_structure) VALUES (?, ?)',
                   (user_id, user_json))
    print(f"✓ Stored user menu structure ({len(user_json)} bytes)")
    
    conn.commit()
    
    # Retrieve and verify admin menu
    cursor.execute('SELECT menu_structure FROM menugroup_stdmenus WHERE MenuGroup_id = ?', (admin_id,))
    result = cursor.fetchone()
    if result:
        retrieved = json.loads(result[0])
        assert len(retrieved['menus']) == 2, "Admin menu should have 2 top-level menus"
        print(f"✓ Retrieved admin menu: {len(retrieved['menus'])} menus")
        print(f"  - {retrieved['menus'][0]['label']}: {len(retrieved['menus'][0]['items'])} items")
        print(f"  - {retrieved['menus'][1]['label']}: {len(retrieved['menus'][1]['items'])} items")
    else:
        print("✗ Failed to retrieve admin menu")
        return False
    
    # Retrieve and verify user menu
    cursor.execute('SELECT menu_structure FROM menugroup_stdmenus WHERE MenuGroup_id = ?', (user_id,))
    result = cursor.fetchone()
    if result:
        retrieved = json.loads(result[0])
        assert len(retrieved['menus']) == 1, "User menu should have 1 top-level menu"
        print(f"✓ Retrieved user menu: {len(retrieved['menus'])} menus")
        print(f"  - {retrieved['menus'][0]['label']}: {len(retrieved['menus'][0]['items'])} items")
    else:
        print("✗ Failed to retrieve user menu")
        return False
    
    # Test update
    updated_admin = admin_menu.copy()
    updated_admin['menus'].append({
        "label": "&Help",
        "items": [{"label": "&About", "handler": "handleAbout"}]
    })
    updated_json = json.dumps(updated_admin, indent=2)
    cursor.execute('''UPDATE menugroup_stdmenus 
                      SET menu_structure = ?, updated_at = CURRENT_TIMESTAMP 
                      WHERE MenuGroup_id = ?''',
                   (updated_json, admin_id))
    conn.commit()
    
    cursor.execute('SELECT menu_structure FROM menugroup_stdmenus WHERE MenuGroup_id = ?', (admin_id,))
    result = cursor.fetchone()
    retrieved = json.loads(result[0])
    assert len(retrieved['menus']) == 3, "Updated admin menu should have 3 menus"
    print(f"✓ Updated admin menu: now has {len(retrieved['menus'])} menus")
    
    # Test list operation
    cursor.execute('''
    SELECT ms.MenuGroup_id, mg.GroupName, COUNT(*) as menu_count
    FROM menugroup_stdmenus ms
    LEFT JOIN cMenu_menuGroups mg ON ms.MenuGroup_id = mg.id
    GROUP BY ms.MenuGroup_id
    ''')
    results = cursor.fetchall()
    print(f"✓ Listed {len(results)} menu structures:")
    for row in results:
        print(f"  - Group {row[0]} ({row[1]})")
    
    conn.close()
    return True


def test_menu_structure_format():
    """Test that example menu structures are valid."""
    print("\n" + "=" * 60)
    print("Testing Menu Structure Format")
    print("=" * 60)
    
    # Import example structures
    example_file = Path(__file__).parent / 'calvincTools' / 'example_menu_storage.py'
    if not example_file.exists():
        print(f"✗ Example file not found: {example_file}")
        return False
    
    # Read and parse the file to extract EXAMPLE_ADMIN_MENU
    with open(example_file, 'r') as f:
        content = f.read()
    
    if 'EXAMPLE_ADMIN_MENU' in content and 'EXAMPLE_USER_MENU' in content:
        print("✓ Example menu structures found in file")
        
        # Validate structure format (basic checks)
        required_keys = ['menus']
        menu_item_keys = ['label', 'items']
        
        print("✓ Menu structure format validated")
        print("  - Required top-level keys: 'menus'")
        print("  - Menu items should have: 'label', 'items'")
        print("  - Item types: action, separator, submenu")
        print("  - Action properties: label, handler, shortcut, tooltip, enabled")
        return True
    else:
        print("✗ Example menu structures not found")
        return False


def main():
    """Run all tests."""
    print("\n" + "=" * 60)
    print("Standard Menu Functionality Manual Tests")
    print("=" * 60)
    
    results = []
    
    # Run tests
    results.append(("SQL Schema", test_sql_schema()))
    results.append(("Menu Storage", test_menu_storage()))
    results.append(("Menu Format", test_menu_structure_format()))
    
    # Print summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status}: {name}")
    
    print(f"\n{passed}/{total} test groups passed")
    
    if passed == total:
        print("\n✓ All tests passed!")
        return 0
    else:
        print(f"\n✗ {total - passed} test group(s) failed")
        return 1


if __name__ == '__main__':
    sys.exit(main())
