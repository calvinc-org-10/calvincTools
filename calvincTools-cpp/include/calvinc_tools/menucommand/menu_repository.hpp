#pragma once

#include <QString>
#include <QMap>
#include <QVariant>
#include <QSqlDatabase>
#include <vector>
#include "calvinc_tools/database/models.hpp"

namespace calvinc::tools::menucommand {

/**
 * MenuRepository provides data access for menu operations.
 * Mirrors the Python MenuRecords class functionality.
 */
class MenuRepository {
private:
    QSqlDatabase db_;
    
public:
    explicit MenuRepository(QSqlDatabase db) : db_(db) {}
    
    /**
     * Get the minimum MenuID for a given menu group.
     */
    int getMinMenuIdForGroup(int menuGroupId);
    
    /**
     * Get the default MenuID for a given menu group.
     * Looks for a menu item with Argument='default' and OptionNumber=0,
     * or returns the minimum MenuID if not found.
     */
    int getDefaultMenuIdForGroup(int menuGroupId);
    
    /**
     * Get the default (first) menu group ID.
     */
    int getDefaultMenuGroup();
    
    /**
     * Get a specific attribute from a menu item.
     * 
     * @param menuGroupId The menu group ID.
     * @param menuId The menu ID.
     * @param optionNumber The option number.
     * @param attrName The attribute name (e.g., "OptionText", "Command").
     * @return The attribute value, or empty/invalid QVariant if not found.
     */
    QVariant getMenuAttribute(int menuGroupId, int menuId, int optionNumber, 
                             const QString& attrName);
    
    /**
     * Get all menu items for a specific menu in a menu group as a dictionary.
     * 
     * @param menuGroupId The menu group ID.
     * @param menuId The menu ID.
     * @return A map from option number to menu item data.
     */
    QMap<int, QMap<QString, QVariant>> getMenuDict(int menuGroupId, int menuId);
    
    /**
     * Create a new menu item in the database.
     */
    bool createMenuItem(const database::MenuItem& item);
    
    /**
     * Update an existing menu item.
     */
    bool updateMenuItem(const database::MenuItem& item);
    
    /**
     * Delete a menu item by ID.
     */
    bool deleteMenuItem(int itemId);
};

}  // namespace calvinc::tools::menucommand
