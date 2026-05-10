#include "calvinc_tools/database/repository.hpp"
#include <QSqlQuery>
#include <QSqlError>
#include <QDebug>

namespace calvinc::tools::database {

bool RepositoryBase::executeQuery(QSqlQuery& query) {
    if (!query.exec()) {
        qWarning() << "Query failed:" << query.lastError().text();
        return false;
    }
    return true;
}

bool RepositoryBase::tableExists(const QString& tableName) {
    QSqlQuery query(db_);
    query.prepare("SELECT name FROM sqlite_master WHERE type='table' AND name=?");
    query.addBindValue(tableName);
    return query.exec() && query.next();
}

// MenuItemRepository implementations
MenuItem* MenuItemRepository::getById(int id) {
    QSqlQuery query(db_);
    query.prepare("SELECT * FROM cMenu_menuItems WHERE id = ?");
    query.addBindValue(id);
    
    if (!executeQuery(query) || !query.next()) {
        return nullptr;
    }
    
    MenuItem* item = new MenuItem();
    item->id = query.value("id").toInt();
    item->menuGroupId = query.value("MenuGroup_id").toInt();
    item->menuId = query.value("MenuID").toInt();
    item->optionNumber = query.value("OptionNumber").toInt();
    item->optionText = query.value("OptionText").toString();
    item->command = query.value("Command").toInt();
    item->argument = query.value("Argument").toString();
    item->password = query.value("PWord").toString();
    item->topLine = query.value("TopLine").toBool();
    item->bottomLine = query.value("BottomLine").toBool();
    
    return item;
}

std::vector<MenuItem> MenuItemRepository::getMenuItems(int menuGroupId, int menuId) {
    std::vector<MenuItem> items;
    QSqlQuery query(db_);
    query.prepare("SELECT * FROM cMenu_menuItems WHERE MenuGroup_id = ? AND MenuID = ?");
    query.addBindValue(menuGroupId);
    query.addBindValue(menuId);
    
    if (!executeQuery(query)) {
        return items;
    }
    
    while (query.next()) {
        MenuItem item;
        item.id = query.value("id").toInt();
        item.menuGroupId = query.value("MenuGroup_id").toInt();
        item.menuId = query.value("MenuID").toInt();
        item.optionNumber = query.value("OptionNumber").toInt();
        item.optionText = query.value("OptionText").toString();
        item.command = query.value("Command").toInt();
        item.argument = query.value("Argument").toString();
        item.password = query.value("PWord").toString();
        item.topLine = query.value("TopLine").toBool();
        item.bottomLine = query.value("BottomLine").toBool();
        
        items.push_back(item);
    }
    
    return items;
}

bool MenuItemRepository::create(const MenuItem& item) {
    QSqlQuery query(db_);
    query.prepare("INSERT INTO cMenu_menuItems (MenuGroup_id, MenuID, OptionNumber, OptionText, Command, Argument, PWord, TopLine, BottomLine) "
                  "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)");
    query.addBindValue(item.menuGroupId);
    query.addBindValue(item.menuId);
    query.addBindValue(item.optionNumber);
    query.addBindValue(item.optionText);
    query.addBindValue(item.command != 0 ? item.command : QVariant());
    query.addBindValue(item.argument);
    query.addBindValue(item.password);
    query.addBindValue(item.topLine ? 1 : 0);
    query.addBindValue(item.bottomLine ? 1 : 0);
    
    return executeQuery(query);
}

bool MenuItemRepository::update(const MenuItem& item) {
    QSqlQuery query(db_);
    query.prepare("UPDATE cMenu_menuItems SET OptionText=?, Command=?, Argument=?, PWord=?, TopLine=?, BottomLine=? WHERE id=?");
    query.addBindValue(item.optionText);
    query.addBindValue(item.command != 0 ? item.command : QVariant());
    query.addBindValue(item.argument);
    query.addBindValue(item.password);
    query.addBindValue(item.topLine ? 1 : 0);
    query.addBindValue(item.bottomLine ? 1 : 0);
    query.addBindValue(item.id);
    
    return executeQuery(query);
}

bool MenuItemRepository::deleteById(int id) {
    QSqlQuery query(db_);
    query.prepare("DELETE FROM cMenu_menuItems WHERE id = ?");
    query.addBindValue(id);
    
    return executeQuery(query);
}

QString MenuItemRepository::getMenuAttribute(int menuGroupId, int menuId, int optionNumber, const QString& attrName) {
    QSqlQuery query(db_);
    QString sql = QString("SELECT %1 FROM cMenu_menuItems WHERE MenuGroup_id = ? AND MenuID = ? AND OptionNumber = ?")
                  .arg(attrName);
    query.prepare(sql);
    query.addBindValue(menuGroupId);
    query.addBindValue(menuId);
    query.addBindValue(optionNumber);
    
    if (!executeQuery(query) || !query.next()) {
        return QString();
    }
    
    return query.value(0).toString();
}

// UserRepository implementations
User* UserRepository::getByUsername(const QString& username) {
    QSqlQuery query(db_);
    query.prepare("SELECT * FROM User WHERE username = ?");
    query.addBindValue(username);
    
    if (!executeQuery(query) || !query.next()) {
        return nullptr;
    }
    
    User* user = new User();
    user->id = query.value("id").toInt();
    user->username = query.value("username").toString();
    user->firstName = query.value("first_name").toString();
    user->lastName = query.value("last_name").toString();
    user->email = query.value("email").toString();
    user->passwordOptional = query.value("password_optional").toBool();
    user->passwordHash = query.value("password_hash").toString();
    user->activeStatus = query.value("active_status").toBool();
    user->isSuperuser = query.value("is_superuser").toBool();
    user->permissions = query.value("permissions").toString();
    user->menuGroup = query.value("menuGroup").toInt();
    user->dateJoined = query.value("date_joined").toDateTime();
    user->lastLogin = query.value("last_login").toDateTime();
    
    return user;
}

User* UserRepository::getById(int id) {
    QSqlQuery query(db_);
    query.prepare("SELECT * FROM User WHERE id = ?");
    query.addBindValue(id);
    
    if (!executeQuery(query) || !query.next()) {
        return nullptr;
    }
    
    User* user = new User();
    user->id = query.value("id").toInt();
    user->username = query.value("username").toString();
    user->firstName = query.value("first_name").toString();
    user->lastName = query.value("last_name").toString();
    user->email = query.value("email").toString();
    user->passwordOptional = query.value("password_optional").toBool();
    user->passwordHash = query.value("password_hash").toString();
    user->activeStatus = query.value("active_status").toBool();
    user->isSuperuser = query.value("is_superuser").toBool();
    user->permissions = query.value("permissions").toString();
    user->menuGroup = query.value("menuGroup").toInt();
    user->dateJoined = query.value("date_joined").toDateTime();
    user->lastLogin = query.value("last_login").toDateTime();
    
    return user;
}

std::vector<User> UserRepository::getAll() {
    std::vector<User> users;
    QSqlQuery query(db_);
 
    query.prepare("SELECT * FROM User");
    // query.bindValue(":id", userId);
    if (!executeQuery(query)) {
        return users;
    }
    
    while (query.next()) {
        User user;
        user.id = query.value("id").toInt();
        user.username = query.value("username").toString();
        user.firstName = query.value("first_name").toString();
        user.lastName = query.value("last_name").toString();
        user.email = query.value("email").toString();
        user.passwordOptional = query.value("password_optional").toBool();
        user.passwordHash = query.value("password_hash").toString();
        user.activeStatus = query.value("active_status").toBool();
        user.isSuperuser = query.value("is_superuser").toBool();
        user.permissions = query.value("permissions").toString();
        user.menuGroup = query.value("menuGroup").toInt();
        user.dateJoined = query.value("date_joined").toDateTime();
        user.lastLogin = query.value("last_login").toDateTime();
        
        users.push_back(user);
    }
    
    return users;
}

bool UserRepository::create(const User& user) {
    QSqlQuery query(db_);
    query.prepare("INSERT INTO User (username, first_name, last_name, email, password_optional, password_hash, active_status, is_superuser, permissions, menuGroup) "
                  "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)");
    query.addBindValue(user.username);
    query.addBindValue(user.firstName);
    query.addBindValue(user.lastName);
    query.addBindValue(user.email);
    query.addBindValue(user.passwordOptional ? 1 : 0);
    query.addBindValue(user.passwordHash);
    query.addBindValue(user.activeStatus ? 1 : 0);
    query.addBindValue(user.isSuperuser ? 1 : 0);
    query.addBindValue(user.permissions);
    query.addBindValue(user.menuGroup > 0 ? user.menuGroup : QVariant());
    
    return executeQuery(query);
}

bool UserRepository::update(const User& user) {
    QSqlQuery query(db_);
    query.prepare("UPDATE User SET username=?, first_name=?, last_name=?, email=?, password_optional=?, password_hash=?, active_status=?, is_superuser=?, permissions=?, menuGroup=? WHERE id=?");
    query.addBindValue(user.username);
    query.addBindValue(user.firstName);
    query.addBindValue(user.lastName);
    query.addBindValue(user.email);
    query.addBindValue(user.passwordOptional ? 1 : 0);
    query.addBindValue(user.passwordHash);
    query.addBindValue(user.activeStatus ? 1 : 0);
    query.addBindValue(user.isSuperuser ? 1 : 0);
    query.addBindValue(user.permissions);
    query.addBindValue(user.menuGroup > 0 ? user.menuGroup : QVariant());
    query.addBindValue(user.id);
    
    return executeQuery(query);
}

bool UserRepository::deleteById(int id) {
    QSqlQuery query(db_);
    query.prepare("DELETE FROM User WHERE id = ?");
    query.addBindValue(id);
    
    return executeQuery(query);
}

// MenuGroupRepository implementations
MenuGroup* MenuGroupRepository::getById(int id) {
    QSqlQuery query(db_);
    query.prepare("SELECT * FROM cMenu_menuGroups WHERE id = ?");
    query.addBindValue(id);
    
    if (!executeQuery(query) || !query.next()) {
        return nullptr;
    }
    
    MenuGroup* group = new MenuGroup();
    group->id = query.value("id").toInt();
    group->groupName = query.value("GroupName").toString();
    group->groupInfo = query.value("GroupInfo").toString();
    
    return group;
}

std::vector<MenuGroup> MenuGroupRepository::getAll() {
    std::vector<MenuGroup> groups;
    QSqlQuery query(db_);
    
    query.prepare("SELECT * FROM cMenu_menuGroups");
    if (!executeQuery(query)) {
        return groups;
    }
    
    while (query.next()) {
        MenuGroup group;
        group.id = query.value("id").toInt();
        group.groupName = query.value("GroupName").toString();
        group.groupInfo = query.value("GroupInfo").toString();
        
        groups.push_back(group);
    }
    
    return groups;
}

bool MenuGroupRepository::create(const MenuGroup& group) {
    QSqlQuery query(db_);
    query.prepare("INSERT INTO cMenu_menuGroups (GroupName, GroupInfo) VALUES (?, ?)");
    query.addBindValue(group.groupName);
    query.addBindValue(group.groupInfo);
    
    return executeQuery(query);
}

bool MenuGroupRepository::update(const MenuGroup& group) {
    QSqlQuery query(db_);
    query.prepare("UPDATE cMenu_menuGroups SET GroupName=?, GroupInfo=? WHERE id=?");
    query.addBindValue(group.groupName);
    query.addBindValue(group.groupInfo);
    query.addBindValue(group.id);
    
    return executeQuery(query);
}

}  // namespace calvinc::tools::database
