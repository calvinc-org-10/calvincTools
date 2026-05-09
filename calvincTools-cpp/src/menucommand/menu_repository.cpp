#include "calvinc_tools/menucommand/menu_repository.hpp"
#include <QSqlQuery>
#include <QSqlError>
#include <QDebug>

namespace calvinc::tools::menucommand {

int MenuRepository::getMinMenuIdForGroup(int menuGroupId) {
    QSqlQuery query(db_);
    query.prepare("SELECT MIN(MenuID) FROM cMenu_menuItems WHERE MenuGroup_id = ? AND OptionNumber = 0");
    query.addBindValue(menuGroupId);
    
    if (!query.exec() || !query.next()) {
        return 0;
    }
    
    return query.value(0).toInt();
}

int MenuRepository::getDefaultMenuIdForGroup(int menuGroupId) {
    QSqlQuery query(db_);
    query.prepare("SELECT MenuID FROM cMenu_menuItems WHERE MenuGroup_id = ? AND Argument LIKE 'default' AND OptionNumber = 0");
    query.addBindValue(menuGroupId);
    
    if (query.exec() && query.next()) {
        return query.value(0).toInt();
    }
    
    // If no default found, return minimum MenuID
    return getMinMenuIdForGroup(menuGroupId);
}

int MenuRepository::getDefaultMenuGroup() {
    QSqlQuery query(db_);
    if (!query.exec("SELECT MIN(MenuGroup_id) FROM cMenu_menuItems")) {
        return -1;
    }
    
    if (query.next()) {
        return query.value(0).toInt();
    }
    
    return -1;
}

QVariant MenuRepository::getMenuAttribute(int menuGroupId, int menuId, int optionNumber, 
                                         const QString& attrName) {
    QSqlQuery query(db_);
    QString sql = QString("SELECT %1 FROM cMenu_menuItems WHERE MenuGroup_id = ? AND MenuID = ? AND OptionNumber = ?")
                  .arg(attrName);
    query.prepare(sql);
    query.addBindValue(menuGroupId);
    query.addBindValue(menuId);
    query.addBindValue(optionNumber);
    
    if (!query.exec() || !query.next()) {
        return QVariant();
    }
    
    return query.value(0);
}

QMap<int, QMap<QString, QVariant>> MenuRepository::getMenuDict(int menuGroupId, int menuId) {
    QMap<int, QMap<QString, QVariant>> result;
    
    QSqlQuery query(db_);
    query.prepare("SELECT * FROM cMenu_menuItems WHERE MenuGroup_id = ? AND MenuID = ?");
    query.addBindValue(menuGroupId);
    query.addBindValue(menuId);
    
    if (!query.exec()) {
        qWarning() << "Query failed:" << query.lastError().text();
        return result;
    }
    
    while (query.next()) {
        QMap<QString, QVariant> rowMap;
        
        for (int i = 0; i < query.record().count(); ++i) {
            rowMap[query.record().fieldName(i)] = query.value(i);
        }
        
        int optionNumber = query.value("OptionNumber").toInt();
        result[optionNumber] = rowMap;
    }
    
    return result;
}

bool MenuRepository::createMenuItem(const database::MenuItem& item) {
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
    
    if (!query.exec()) {
        qWarning() << "Failed to create menu item:" << query.lastError().text();
        return false;
    }
    
    return true;
}

bool MenuRepository::updateMenuItem(const database::MenuItem& item) {
    QSqlQuery query(db_);
    query.prepare("UPDATE cMenu_menuItems SET OptionText=?, Command=?, Argument=?, PWord=?, TopLine=?, BottomLine=? WHERE id=?");
    query.addBindValue(item.optionText);
    query.addBindValue(item.command != 0 ? item.command : QVariant());
    query.addBindValue(item.argument);
    query.addBindValue(item.password);
    query.addBindValue(item.topLine ? 1 : 0);
    query.addBindValue(item.bottomLine ? 1 : 0);
    query.addBindValue(item.id);
    
    if (!query.exec()) {
        qWarning() << "Failed to update menu item:" << query.lastError().text();
        return false;
    }
    
    return true;
}

bool MenuRepository::deleteMenuItem(int itemId) {
    QSqlQuery query(db_);
    query.prepare("DELETE FROM cMenu_menuItems WHERE id = ?");
    query.addBindValue(itemId);
    
    if (!query.exec()) {
        qWarning() << "Failed to delete menu item:" << query.lastError().text();
        return false;
    }
    
    return true;
}

}  // namespace calvinc::tools::menucommand
