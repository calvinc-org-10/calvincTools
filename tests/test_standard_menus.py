"""
Tests for standard menu functionality

This module tests the StandardMenuBuilder, MenuManager, and menu storage utilities.
"""

import pytest
import json
from pathlib import Path

from calvincTools.standard_menu_builder import StandardMenuBuilder, MenuManager
from calvincTools.example_menu_storage import (
    store_menu_structure,
    get_menu_structure,
    delete_menu_structure,
    list_menu_structures,
    ensure_table_exists,
    EXAMPLE_ADMIN_MENU,
    EXAMPLE_USER_MENU,
)
from calvincTools.models import menuGroups
from calvincTools.database import get_cMenu_session


@pytest.fixture
def test_menu_structure():
    """Provide a simple test menu structure."""
    return {
        "menus": [
            {
                "label": "&File",
                "items": [
                    {
                        "label": "&New",
                        "handler": "handleNew",
                        "shortcut": "Ctrl+N",
                        "tooltip": "Create new file"
                    },
                    {
                        "separator": True
                    },
                    {
                        "label": "&Exit",
                        "handler": "handleExit"
                    }
                ]
            },
            {
                "label": "&Edit",
                "items": [
                    {
                        "label": "&Preferences",
                        "submenu": [
                            {
                                "label": "&Theme",
                                "handler": "handleTheme"
                            }
                        ]
                    }
                ]
            }
        ]
    }


@pytest.fixture
def test_menugroup(test_session):
    """Create a test menuGroup."""
    group = menuGroups(
        GroupName="Test Group",
        GroupInfo="Test menu group for testing"
    )
    test_session.add(group)
    test_session.commit()
    test_session.refresh(group)
    return group


class TestMenuStorage:
    """Test menu structure storage and retrieval."""
    
    def test_ensure_table_exists(self):
        """Test that table creation works."""
        # This should not raise an error
        ensure_table_exists()
        
        # Verify table exists
        with get_cMenu_session() as session:
            result = session.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name='menugroup_stdmenus'"
            ).fetchone()
            assert result is not None
    
    def test_store_menu_structure(self, test_menugroup, test_menu_structure):
        """Test storing a menu structure."""
        success = store_menu_structure(test_menugroup.id, test_menu_structure)
        assert success is True
        
        # Verify it was stored
        retrieved = get_menu_structure(test_menugroup.id)
        assert retrieved is not None
        assert retrieved == test_menu_structure
    
    def test_store_menu_structure_update(self, test_menugroup, test_menu_structure):
        """Test updating an existing menu structure."""
        # Store initial structure
        store_menu_structure(test_menugroup.id, test_menu_structure)
        
        # Update with modified structure
        modified_structure = test_menu_structure.copy()
        modified_structure['menus'][0]['label'] = "&Modified"
        
        success = store_menu_structure(test_menugroup.id, modified_structure)
        assert success is True
        
        # Verify update
        retrieved = get_menu_structure(test_menugroup.id)
        assert retrieved['menus'][0]['label'] == "&Modified"
    
    def test_get_menu_structure_not_found(self):
        """Test getting a non-existent menu structure."""
        result = get_menu_structure(99999)
        assert result is None
    
    def test_delete_menu_structure(self, test_menugroup, test_menu_structure):
        """Test deleting a menu structure."""
        # Store first
        store_menu_structure(test_menugroup.id, test_menu_structure)
        
        # Delete
        success = delete_menu_structure(test_menugroup.id)
        assert success is True
        
        # Verify deletion
        result = get_menu_structure(test_menugroup.id)
        assert result is None
    
    def test_list_menu_structures(self, test_menugroup, test_menu_structure):
        """Test listing all menu structures."""
        # Store a structure
        store_menu_structure(test_menugroup.id, test_menu_structure)
        
        # List structures
        structures = list_menu_structures()
        assert len(structures) > 0
        
        # Find our test structure
        found = False
        for struct in structures:
            if struct['menuGroup_id'] == test_menugroup.id:
                found = True
                assert struct['group_name'] == "Test Group"
                break
        
        assert found is True


class TestStandardMenuBuilder:
    """Test StandardMenuBuilder class."""
    
    def test_init(self):
        """Test StandardMenuBuilder initialization."""
        builder = StandardMenuBuilder()
        assert builder.menuGroup_id is None
        assert builder.menu_structure is None
        assert builder.menu_bar is None
    
    def test_load_menu_structure_not_found(self):
        """Test loading a non-existent menu structure."""
        builder = StandardMenuBuilder()
        result = builder.load_menu_structure(99999)
        assert result is False
        assert builder.menu_structure is None
    
    def test_load_menu_structure_success(self, test_menugroup, test_menu_structure):
        """Test loading an existing menu structure."""
        # Store structure first
        store_menu_structure(test_menugroup.id, test_menu_structure)
        
        # Load it
        builder = StandardMenuBuilder()
        result = builder.load_menu_structure(test_menugroup.id)
        
        assert result is True
        assert builder.menuGroup_id == test_menugroup.id
        assert builder.menu_structure == test_menu_structure
    
    def test_build_menubar_no_structure(self):
        """Test building menu bar without loading structure."""
        builder = StandardMenuBuilder()
        menubar = builder.build_menubar()
        assert menubar is None
    
    def test_build_menubar_with_structure(self, test_menugroup, test_menu_structure):
        """Test building menu bar from structure."""
        # Store and load structure
        store_menu_structure(test_menugroup.id, test_menu_structure)
        builder = StandardMenuBuilder()
        builder.load_menu_structure(test_menugroup.id)
        
        # Build menubar
        menubar = builder.build_menubar()
        
        assert menubar is not None
        # Check that menus were created
        actions = menubar.actions()
        assert len(actions) == 2  # File and Edit menus
        assert actions[0].text() == "&File"
        assert actions[1].text() == "&Edit"
    
    def test_build_menu_with_separator(self, test_menugroup, test_menu_structure):
        """Test that separators are created correctly."""
        store_menu_structure(test_menugroup.id, test_menu_structure)
        builder = StandardMenuBuilder()
        builder.load_menu_structure(test_menugroup.id)
        menubar = builder.build_menubar()
        
        # Get File menu
        file_menu = menubar.actions()[0].menu()
        actions = file_menu.actions()
        
        # Check for separator (second item)
        assert actions[1].isSeparator()
    
    def test_build_menu_with_submenu(self, test_menugroup, test_menu_structure):
        """Test that submenus are created correctly."""
        store_menu_structure(test_menugroup.id, test_menu_structure)
        builder = StandardMenuBuilder()
        builder.load_menu_structure(test_menugroup.id)
        menubar = builder.build_menubar()
        
        # Get Edit menu
        edit_menu = menubar.actions()[1].menu()
        actions = edit_menu.actions()
        
        # First item should be Preferences with a submenu
        prefs_action = actions[0]
        assert prefs_action.text() == "&Preferences"
        assert prefs_action.menu() is not None
        
        # Check submenu has Theme item
        submenu = prefs_action.menu()
        submenu_actions = submenu.actions()
        assert len(submenu_actions) == 1
        assert submenu_actions[0].text() == "&Theme"
    
    def test_build_action_with_shortcut(self, test_menugroup, test_menu_structure):
        """Test that shortcuts are set correctly."""
        store_menu_structure(test_menugroup.id, test_menu_structure)
        builder = StandardMenuBuilder()
        builder.load_menu_structure(test_menugroup.id)
        menubar = builder.build_menubar()
        
        # Get File menu and New action
        file_menu = menubar.actions()[0].menu()
        new_action = file_menu.actions()[0]
        
        assert new_action.text() == "&New"
        assert not new_action.shortcut().isEmpty()
    
    def test_build_action_with_tooltip(self, test_menugroup, test_menu_structure):
        """Test that tooltips are set correctly."""
        store_menu_structure(test_menugroup.id, test_menu_structure)
        builder = StandardMenuBuilder()
        builder.load_menu_structure(test_menugroup.id)
        menubar = builder.build_menubar()
        
        # Get File menu and New action
        file_menu = menubar.actions()[0].menu()
        new_action = file_menu.actions()[0]
        
        assert new_action.toolTip() == "Create new file"
    
    def test_switch_menugroup(self, test_menugroup, test_menu_structure):
        """Test switching between menuGroups."""
        # Create second group with different structure
        with get_cMenu_session() as session:
            group2 = menuGroups(GroupName="Group 2", GroupInfo="Second group")
            session.add(group2)
            session.commit()
            session.refresh(group2)
            group2_id = group2.id
        
        simple_structure = {
            "menus": [
                {
                    "label": "&Simple",
                    "items": [{"label": "Item", "handler": "handleItem"}]
                }
            ]
        }
        
        # Store structures for both groups
        store_menu_structure(test_menugroup.id, test_menu_structure)
        store_menu_structure(group2_id, simple_structure)
        
        # Build menu for first group
        builder = StandardMenuBuilder()
        builder.load_menu_structure(test_menugroup.id)
        menubar1 = builder.build_menubar()
        assert len(menubar1.actions()) == 2
        
        # Switch to second group
        menubar2 = builder.switch_menugroup(group2_id)
        assert menubar2 is not None
        assert len(menubar2.actions()) == 1
        assert menubar2.actions()[0].text() == "&Simple"
    
    def test_get_menubar(self, test_menugroup, test_menu_structure):
        """Test getting the current menubar."""
        store_menu_structure(test_menugroup.id, test_menu_structure)
        builder = StandardMenuBuilder()
        builder.load_menu_structure(test_menugroup.id)
        
        # Before building
        assert builder.get_menubar() is None
        
        # After building
        menubar = builder.build_menubar()
        assert builder.get_menubar() is menubar


class TestMenuManager:
    """Test MenuManager class."""
    
    def test_init(self):
        """Test MenuManager initialization."""
        manager = MenuManager()
        assert manager.current_menugroup_id is None
        assert manager.standard_builder is not None
    
    def test_load_menugroup_not_found(self):
        """Test loading a non-existent menuGroup."""
        manager = MenuManager()
        result = manager.load_menugroup(99999)
        
        assert result['menuGroup_id'] == 99999
        assert result['standard_menu_loaded'] is False
        assert result['standard_menubar'] is None
    
    def test_load_menugroup_success(self, test_menugroup, test_menu_structure):
        """Test loading an existing menuGroup."""
        store_menu_structure(test_menugroup.id, test_menu_structure)
        
        manager = MenuManager()
        result = manager.load_menugroup(test_menugroup.id)
        
        assert result['menuGroup_id'] == test_menugroup.id
        assert result['standard_menu_loaded'] is True
        assert result['standard_menubar'] is not None
        assert manager.current_menugroup_id == test_menugroup.id
    
    def test_get_standard_menubar(self, test_menugroup, test_menu_structure):
        """Test getting the standard menubar."""
        store_menu_structure(test_menugroup.id, test_menu_structure)
        
        manager = MenuManager()
        manager.load_menugroup(test_menugroup.id)
        
        menubar = manager.get_standard_menubar()
        assert menubar is not None
    
    def test_switch_menugroup(self, test_menugroup, test_menu_structure):
        """Test switching menuGroups."""
        # Create second group
        with get_cMenu_session() as session:
            group2 = menuGroups(GroupName="Group 2", GroupInfo="Second group")
            session.add(group2)
            session.commit()
            session.refresh(group2)
            group2_id = group2.id
        
        simple_structure = {
            "menus": [
                {
                    "label": "&Simple",
                    "items": [{"label": "Item", "handler": "handleItem"}]
                }
            ]
        }
        
        store_menu_structure(test_menugroup.id, test_menu_structure)
        store_menu_structure(group2_id, simple_structure)
        
        # Load first group
        manager = MenuManager()
        manager.load_menugroup(test_menugroup.id)
        menubar1 = manager.get_standard_menubar()
        assert len(menubar1.actions()) == 2
        
        # Switch to second group
        result = manager.switch_menugroup(group2_id)
        assert result['standard_menu_loaded'] is True
        menubar2 = manager.get_standard_menubar()
        assert len(menubar2.actions()) == 1


class TestExampleMenus:
    """Test example menu structures."""
    
    def test_admin_menu_structure(self):
        """Test that admin menu structure is valid."""
        assert 'menus' in EXAMPLE_ADMIN_MENU
        assert len(EXAMPLE_ADMIN_MENU['menus']) > 0
        
        # Check for File menu
        file_menu = None
        for menu in EXAMPLE_ADMIN_MENU['menus']:
            if menu['label'] == '&File':
                file_menu = menu
                break
        
        assert file_menu is not None
        assert 'items' in file_menu
        assert len(file_menu['items']) > 0
    
    def test_user_menu_structure(self):
        """Test that user menu structure is valid."""
        assert 'menus' in EXAMPLE_USER_MENU
        assert len(EXAMPLE_USER_MENU['menus']) > 0
        
        # User menu should be simpler than admin
        assert len(EXAMPLE_USER_MENU['menus']) <= len(EXAMPLE_ADMIN_MENU['menus'])
