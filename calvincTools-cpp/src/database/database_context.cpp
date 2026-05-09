#include "calvinc_tools/database/database_context.hpp"
#include <QSqlQuery>
#include <QSqlError>
#include <QFile>

namespace calvinc::tools::database {

std::unique_ptr<DatabaseContext> DatabaseContext::instance_;

DatabaseContext::DatabaseContext()
    : initialized_(false) {
}

DatabaseContext& DatabaseContext::getInstance() {
    if (!instance_) {
        instance_ = std::unique_ptr<DatabaseContext>(new DatabaseContext());
    }
    return *instance_;
}

bool DatabaseContext::initialize(const QString& dbPath) {
    dbPath_ = dbPath.isEmpty() ? "cMenudb.sqlite" : dbPath;
    
    db_ = QSqlDatabase::addDatabase("QSQLITE");
    db_.setDatabaseName(dbPath_);
    
    if (!db_.open()) {
        qWarning() << "Failed to open database:" << db_.lastError().text();
        return false;
    }
    
    if (!createTables()) {
        qWarning() << "Failed to create tables";
        return false;
    }
    
    initialized_ = true;
    return true;
}

QSqlDatabase DatabaseContext::getDatabase() {
    return db_;
}

bool DatabaseContext::isOpen() const {
    return db_.isOpen();
}

void DatabaseContext::close() {
    if (db_.isOpen()) {
        db_.close();
    }
    initialized_ = false;
}

bool DatabaseContext::createTables() {
    if (!db_.isOpen()) {
        return false;
    }
    
    // Create menuGroups table
    QSqlQuery query(db_);
    if (!query.exec("CREATE TABLE IF NOT EXISTS cMenu_menuGroups ("
                    "id INTEGER PRIMARY KEY AUTOINCREMENT,"
                    "GroupName TEXT UNIQUE NOT NULL,"
                    "GroupInfo TEXT NOT NULL DEFAULT '')"
                    )) {
        qWarning() << "Failed to create menuGroups table:" << query.lastError().text();
        return false;
    }
    
    // Create menuItems table
    if (!query.exec("CREATE TABLE IF NOT EXISTS cMenu_menuItems ("
                    "id INTEGER PRIMARY KEY AUTOINCREMENT,"
                    "MenuGroup_id INTEGER NOT NULL,"
                    "MenuID SMALLINT NOT NULL,"
                    "OptionNumber SMALLINT NOT NULL,"
                    "OptionText TEXT NOT NULL DEFAULT '',"
                    "Command INTEGER,"
                    "Argument TEXT NOT NULL DEFAULT '',"
                    "PWord TEXT NOT NULL DEFAULT '',"
                    "TopLine BOOLEAN,"
                    "BottomLine BOOLEAN,"
                    "FOREIGN KEY(MenuGroup_id) REFERENCES cMenu_menuGroups(id),"
                    "UNIQUE(MenuGroup_id, MenuID, OptionNumber))"
                    )) {
        qWarning() << "Failed to create menuItems table:" << query.lastError().text();
        return false;
    }
    
    // Create User table
    if (!query.exec("CREATE TABLE IF NOT EXISTS User ("
                    "id INTEGER PRIMARY KEY AUTOINCREMENT,"
                    "username TEXT UNIQUE NOT NULL,"
                    "first_name TEXT NOT NULL,"
                    "last_name TEXT NOT NULL,"
                    "email TEXT UNIQUE NOT NULL,"
                    "password_optional BOOLEAN NOT NULL DEFAULT 0,"
                    "password_hash TEXT NOT NULL,"
                    "active_status BOOLEAN NOT NULL DEFAULT 1,"
                    "is_superuser BOOLEAN NOT NULL DEFAULT 0,"
                    "permissions TEXT NOT NULL DEFAULT '',"
                    "menuGroup INTEGER,"
                    "date_joined DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,"
                    "last_login DATETIME,"
                    "FOREIGN KEY(menuGroup) REFERENCES cMenu_menuGroups(id))"
                    )) {
        qWarning() << "Failed to create User table:" << query.lastError().text();
        return false;
    }
    
    // Create cParameters table
    if (!query.exec("CREATE TABLE IF NOT EXISTS cMenu_cParameters ("
                    "ParmName TEXT PRIMARY KEY,"
                    "ParmValue TEXT NOT NULL,"
                    "UserModifiable BOOLEAN NOT NULL,"
                    "Comments TEXT NOT NULL)"
                    )) {
        qWarning() << "Failed to create cParameters table:" << query.lastError().text();
        return false;
    }
    
    // Create cGreetings table
    if (!query.exec("CREATE TABLE IF NOT EXISTS cMenu_cGreetings ("
                    "id INTEGER PRIMARY KEY AUTOINCREMENT,"
                    "Greeting TEXT NOT NULL)"
                    )) {
        qWarning() << "Failed to create cGreetings table:" << query.lastError().text();
        return false;
    }
    
    return true;
}

}  // namespace calvinc::tools::database
