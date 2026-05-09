#pragma once

#include <QString>
#include <QDateTime>
#include "calvinc_tools/database/models.hpp"

namespace calvinc::tools::auth {

/**
 * User authentication and information model.
 * Represents an authenticated user in the application.
 */
class User {
private:
    database::User userData_;
    
public:
    /**
     * Construct a user from raw user data.
     */
    explicit User(const database::User& userData = {});
    
    // Getters
    int getId() const { return userData_.id; }
    const QString& getUsername() const { return userData_.username; }
    const QString& getFirstName() const { return userData_.firstName; }
    const QString& getLastName() const { return userData_.lastName; }
    const QString& getEmail() const { return userData_.email; }
    bool isActive() const { return userData_.activeStatus; }
    bool isSuperuser() const { return userData_.isSuperuser; }
    const QString& getPermissions() const { return userData_.permissions; }
    int getMenuGroup() const { return userData_.menuGroup; }
    QDateTime getDateJoined() const { return userData_.dateJoined; }
    QDateTime getLastLogin() const { return userData_.lastLogin; }
    
    // Authentication properties (Flask-Login compatible)
    bool isAuthenticated() const { return userData_.id > 0 && userData_.activeStatus; }
    bool isAnonymous() const { return userData_.id <= 0; }
    QString getId_str() const { return QString::number(userData_.id); }
    
    /**
     * Check if this user has a specific permission.
     * Superusers automatically have all permissions.
     */
    bool hasPermission(const QString& permissionName) const;
    
    /**
     * Check the user's password against a provided plain-text password.
     * (Actual password checking is done via PasswordService)
     */
    const QString& getPasswordHash() const { return userData_.passwordHash; }
    
    /**
     * Set password hash (internal use by password service).
     */
    void setPasswordHash(const QString& hash) { userData_.passwordHash = hash; }
};

}  // namespace calvinc::tools::auth
