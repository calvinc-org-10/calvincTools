-- Migration script to add standard menu support to cMenu database
-- This script adds a new table to store standard Qt menu structures for each menuGroup
-- 
-- Usage: Execute this SQL against an existing cMenu database to add standard menu support
-- The script is idempotent - safe to run multiple times

-- Create table to store standard menu structures per menuGroup
CREATE TABLE IF NOT EXISTS menugroup_stdmenus (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    MenuGroup_id INTEGER NOT NULL,
    menu_structure TEXT NOT NULL,  -- JSON format menu structure
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (MenuGroup_id) REFERENCES cMenu_menuGroups(id) ON DELETE CASCADE,
    UNIQUE(MenuGroup_id)  -- Each menuGroup has exactly one standard menu structure
);

-- Create index on MenuGroup_id for faster lookups
CREATE INDEX IF NOT EXISTS idx_menugroup_stdmenus_group_id 
ON menugroup_stdmenus(MenuGroup_id);

-- Add trigger to update updated_at timestamp
CREATE TRIGGER IF NOT EXISTS update_menugroup_stdmenus_timestamp 
AFTER UPDATE ON menugroup_stdmenus
FOR EACH ROW
BEGIN
    UPDATE menugroup_stdmenus 
    SET updated_at = CURRENT_TIMESTAMP 
    WHERE id = NEW.id;
END;

-- Example menu structure (commented out - use example_menu_storage.py instead)
-- The JSON structure should follow this format:
-- {
--   "menus": [
--     {
--       "label": "&File",
--       "items": [
--         {
--           "label": "&New",
--           "handler": "handleNew",
--           "shortcut": "Ctrl+N",
--           "tooltip": "Create a new file"
--         },
--         {
--           "separator": true
--         },
--         {
--           "label": "&Exit",
--           "handler": "handleExit",
--           "shortcut": "Alt+F4"
--         }
--       ]
--     }
--   ]
-- }
