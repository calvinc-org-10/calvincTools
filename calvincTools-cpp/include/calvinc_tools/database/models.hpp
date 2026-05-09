#pragma once

#include <QString>
#include <QDateTime>
#include <QSqlDatabase>
#include <memory>

namespace calvinc::tools::database {

/**
 * menuGroups model - represents a group of menus in the system.
 */
struct MenuGroup {
    int id = -1;
    QString groupName;
    QString groupInfo;
};

/**
 * menuItems model - represents individual menu items.
 */
struct MenuItem {
    int id = -1;
    int menuGroupId = -1;
    int menuId = 0;
    int optionNumber = 0;
    QString optionText;
    int command = 0;  // nullable
    QString argument;
    QString password;
    bool topLine = false;  // nullable
    bool bottomLine = false;  // nullable
};

/**
 * User model - represents an application user.
 */
struct User {
    int id = -1;
    QString username;
    QString firstName;
    QString lastName;
    QString email;
    bool passwordOptional = false;
    QString passwordHash;
    bool activeStatus = true;
    bool isSuperuser = false;
    QString permissions;
    int menuGroup = -1;  // nullable
    QDateTime dateJoined;
    QDateTime lastLogin;  // nullable
};

/**
 * cParameters model - key-value configuration parameters.
 */
struct Parameter {
    QString paramName;
    QString paramValue;
    bool userModifiable = false;
    QString comments;
};

/**
 * cGreetings model - greeting messages.
 */
struct Greeting {
    int id = -1;
    QString greeting;
};

}  // namespace calvinc::tools::database
