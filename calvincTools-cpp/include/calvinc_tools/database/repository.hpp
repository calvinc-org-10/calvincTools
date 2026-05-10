#pragma once

#include <QString>
#include <QSqlQuery>
#include <QSqlDatabase>
#include <vector>
#include <memory>

#include "calvinc_tools/database/models.hpp"


namespace calvinc::tools::database {

/**
 * Generic repository base class for database CRUD operations.
 * Provides standard operations: get, getAll, add, update, remove, etc.
 */
class RepositoryBase {
protected:
    QSqlDatabase db_;
    
    RepositoryBase(QSqlDatabase db) : db_(db) {}

public:
    virtual ~RepositoryBase() = default;
    
    /**
     * Execute a query and return whether it succeeded.
     */
    bool executeQuery(QSqlQuery& query);
    
    /**
     * Check if a table exists in the database.
     */
    bool tableExists(const QString& tableName);
};

/**
 * Specialized repository for MenuItem operations.
 */
class MenuItemRepository : public RepositoryBase {
public:
    MenuItemRepository(QSqlDatabase db) : RepositoryBase(db) {}
    
    /**
     * Get a menu item by its ID.
     */
    MenuItem* getById(int id);
    
    /**
     * Get all menu items for a specific menu group and menu.
     */
    std::vector<MenuItem> getMenuItems(int menuGroupId, int menuId);
    
    /**
     * Create a new menu item.
     */
    bool create(const MenuItem& item);
    
    /**
     * Update an existing menu item.
     */
    bool update(const MenuItem& item);
    
    /**
     * Delete a menu item by ID.
     */
    bool deleteById(int id);
    
    /**
     * Get a specific attribute value for a menu item.
     */
    QString getMenuAttribute(int menuGroupId, int menuId, int optionNumber, const QString& attrName);
};

/**
 * Specialized repository for User operations.
 */
class UserRepository : public RepositoryBase {
public:
    UserRepository(QSqlDatabase db) : RepositoryBase(db) {}
    
    /**
     * Get a user by username.
     */
    User* getByUsername(const QString& username);
    
    /**
     * Get a user by ID.
     */
    User* getById(int id);
    
    /**
     * Get all users.
     */
    std::vector<User> getAll();
    
    /**
     * Create a new user.
     */
    bool create(const User& user);
    
    /**
     * Update an existing user.
     */
    bool update(const User& user);
    
    /**
     * Delete a user by ID.
     */
    bool deleteById(int id);
};

/**
 * Specialized repository for MenuGroup operations.
 */
class MenuGroupRepository : public RepositoryBase {
public:
    MenuGroupRepository(QSqlDatabase db) : RepositoryBase(db) {}
    
    /**
     * Get a menu group by ID.
     */
    MenuGroup* getById(int id);
    
    /**
     * Get all menu groups.
     */
    std::vector<MenuGroup> getAll();
    
    /**
     * Create a new menu group.
     */
    bool create(const MenuGroup& group);
    
    /**
     * Update an existing menu group.
     */
    bool update(const MenuGroup& group);
};

}  // namespace calvinc::tools::database
