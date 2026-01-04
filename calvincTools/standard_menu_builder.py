"""
StandardMenuBuilder - Build Qt standard menus from database-stored structures

This module provides functionality to build QMenuBar, QMenu, and QAction widgets
from JSON menu structures stored in the cMenu database. It integrates with the
existing menucommand_handlers module to connect menu actions.
"""

import json
import warnings
from typing import Dict, List, Any, Optional, Callable

from PySide6.QtCore import Qt
from PySide6.QtGui import QKeySequence, QAction
from PySide6.QtWidgets import QMenuBar, QMenu, QWidget

from .database import get_cMenu_sessionmaker
from .apphooks import cTools_apphooks
from . import menucommand_handlers


class StandardMenuBuilder:
    """
    Builds standard Qt menus from database-stored JSON structures.
    
    This class reads menu structures from the menugroup_stdmenus table
    and dynamically creates QMenuBar with nested QMenu and QAction items.
    Menu actions are connected to handler methods in menucommand_handlers.
    
    Attributes:
        parent_widget: The parent QWidget for the menu bar
        menuGroup_id: Current menu group ID
        menu_structure: Current menu structure (dict from JSON)
        menu_bar: The built QMenuBar instance
    """
    
    def __init__(self, parent_widget: Optional[QWidget] = None):
        """
        Initialize the StandardMenuBuilder.
        
        Args:
            parent_widget: Optional parent widget for the menu bar
        """
        self.parent_widget = parent_widget
        self.menuGroup_id: Optional[int] = None
        self.menu_structure: Optional[Dict[str, Any]] = None
        self.menu_bar: Optional[QMenuBar] = None
        self._session_maker = get_cMenu_sessionmaker()
    
    def load_menu_structure(self, menuGroup_id: int) -> bool:
        """
        Load menu structure from database for the given menuGroup.
        
        Args:
            menuGroup_id: The menu group ID to load
            
        Returns:
            True if structure was loaded successfully, False otherwise
        """
        self.menuGroup_id = menuGroup_id
        
        try:
            with self._session_maker() as session:
                result = session.execute(
                    "SELECT menu_structure FROM menugroup_stdmenus WHERE MenuGroup_id = ?",
                    (menuGroup_id,)
                ).fetchone()
                
                if result:
                    self.menu_structure = json.loads(result[0])
                    return True
                else:
                    self.menu_structure = None
                    return False
        except Exception as e:
            warnings.warn(f"Error loading menu structure for group {menuGroup_id}: {e}")
            self.menu_structure = None
            return False
    
    def build_menubar(self) -> Optional[QMenuBar]:
        """
        Build a QMenuBar from the loaded menu structure.
        
        Returns:
            QMenuBar instance if structure exists, None otherwise
        """
        if not self.menu_structure:
            return None
        
        self.menu_bar = QMenuBar(self.parent_widget)
        
        menus = self.menu_structure.get('menus', [])
        for menu_def in menus:
            menu = self._build_menu(menu_def)
            if menu:
                self.menu_bar.addMenu(menu)
        
        return self.menu_bar
    
    def _build_menu(self, menu_def: Dict[str, Any], parent_menu: Optional[QMenu] = None) -> Optional[QMenu]:
        """
        Build a QMenu from a menu definition.
        
        Args:
            menu_def: Dictionary containing menu definition
            parent_menu: Optional parent menu for submenus
            
        Returns:
            QMenu instance
        """
        label = menu_def.get('label', 'Menu')
        menu = QMenu(label, self.parent_widget if not parent_menu else parent_menu)
        
        items = menu_def.get('items', [])
        for item_def in items:
            self._add_menu_item(menu, item_def)
        
        return menu
    
    def _add_menu_item(self, menu: QMenu, item_def: Dict[str, Any]) -> None:
        """
        Add an item (action, separator, or submenu) to a menu.
        
        Args:
            menu: The menu to add the item to
            item_def: Dictionary containing item definition
        """
        # Check if this is a separator
        if item_def.get('separator', False):
            menu.addSeparator()
            return
        
        # Check if this is a submenu
        if 'submenu' in item_def:
            submenu_def = {
                'label': item_def.get('label', 'Submenu'),
                'items': item_def['submenu']
            }
            submenu = self._build_menu(submenu_def, menu)
            if submenu:
                menu.addMenu(submenu)
            return
        
        # This is a regular action
        self._add_action(menu, item_def)
    
    def _add_action(self, menu: QMenu, item_def: Dict[str, Any]) -> None:
        """
        Add a QAction to a menu.
        
        Args:
            menu: The menu to add the action to
            item_def: Dictionary containing action definition
        """
        label = item_def.get('label', 'Action')
        action = QAction(label, self.parent_widget)
        
        # Set tooltip
        tooltip = item_def.get('tooltip')
        if tooltip:
            action.setToolTip(tooltip)
            action.setStatusTip(tooltip)
        
        # Set keyboard shortcut
        shortcut = item_def.get('shortcut')
        if shortcut:
            action.setShortcut(QKeySequence(shortcut))
        
        # Set enabled state
        enabled = item_def.get('enabled', True)
        action.setEnabled(enabled)
        
        # Connect handler
        handler_name = item_def.get('handler')
        if handler_name:
            handler = self._get_handler(handler_name)
            if handler:
                action.triggered.connect(handler)
            else:
                warnings.warn(f"Handler '{handler_name}' not found in menucommand_handlers")
                action.setEnabled(False)
        
        menu.addAction(action)
    
    def _get_handler(self, handler_name: str) -> Optional[Callable]:
        """
        Get a handler function from menucommand_handlers module.
        
        Args:
            handler_name: Name of the handler function
            
        Returns:
            Handler function if found, None otherwise
        """
        if hasattr(menucommand_handlers, handler_name):
            return getattr(menucommand_handlers, handler_name)
        
        # Check if it's a FormBrowse wrapper
        if handler_name.startswith('FormBrowse:'):
            form_name = handler_name.split(':', 1)[1]
            return lambda: menucommand_handlers.FormBrowse(self.parent_widget, form_name)
        
        return None
    
    def switch_menugroup(self, menuGroup_id: int) -> Optional[QMenuBar]:
        """
        Switch to a different menuGroup and rebuild the menu bar.
        
        Args:
            menuGroup_id: The new menu group ID
            
        Returns:
            New QMenuBar instance if successful, None otherwise
        """
        if self.load_menu_structure(menuGroup_id):
            return self.build_menubar()
        return None
    
    def get_menubar(self) -> Optional[QMenuBar]:
        """
        Get the current menu bar instance.
        
        Returns:
            Current QMenuBar instance or None
        """
        return self.menu_bar


class MenuManager:
    """
    Coordinates both custom menu system and standard Qt menus.
    
    This class provides a unified interface to manage both the existing
    custom cMenu button-based system and the new standard QMenuBar system.
    It allows easy switching between menuGroups for both systems.
    """
    
    def __init__(self, parent_widget: Optional[QWidget] = None):
        """
        Initialize the MenuManager.
        
        Args:
            parent_widget: Optional parent widget
        """
        self.parent_widget = parent_widget
        self.standard_builder = StandardMenuBuilder(parent_widget)
        self.current_menugroup_id: Optional[int] = None
    
    def load_menugroup(self, menuGroup_id: int) -> Dict[str, Any]:
        """
        Load both custom and standard menus for a menuGroup.
        
        Args:
            menuGroup_id: The menu group ID to load
            
        Returns:
            Dictionary with status of both menu systems:
            {
                'menuGroup_id': int,
                'standard_menu_loaded': bool,
                'standard_menubar': QMenuBar or None,
            }
        """
        self.current_menugroup_id = menuGroup_id
        
        result = {
            'menuGroup_id': menuGroup_id,
            'standard_menu_loaded': False,
            'standard_menubar': None,
        }
        
        # Load standard menu
        if self.standard_builder.load_menu_structure(menuGroup_id):
            menubar = self.standard_builder.build_menubar()
            result['standard_menu_loaded'] = True
            result['standard_menubar'] = menubar
        
        return result
    
    def get_standard_menubar(self) -> Optional[QMenuBar]:
        """
        Get the current standard menu bar.
        
        Returns:
            QMenuBar instance or None
        """
        return self.standard_builder.get_menubar()
    
    def switch_menugroup(self, menuGroup_id: int) -> Dict[str, Any]:
        """
        Switch to a different menuGroup for both menu systems.
        
        Args:
            menuGroup_id: The new menu group ID
            
        Returns:
            Dictionary with status (same format as load_menugroup)
        """
        return self.load_menugroup(menuGroup_id)
