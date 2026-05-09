#pragma once

#include <QString>
#include <stdexcept>
#include "user.hpp"

namespace calvinc::tools::auth {

/**
 * AuthorizationException thrown when a user lacks required permissions.
 */
class AuthorizationException : public std::runtime_error {
public:
    explicit AuthorizationException(const std::string& message)
        : std::runtime_error(message) {}
};

/**
 * Authorization service for checking user permissions and roles.
 * Replaces Python-style decorators with explicit C++ function calls.
 */
class Authorization {
private:
    Authorization() = delete;
    Authorization(const Authorization&) = delete;
    Authorization& operator=(const Authorization&) = delete;

public:
    /**
     * Check if a user is authenticated (logged in).
     * Throws AuthorizationException if not authenticated.
     * 
     * @return The authenticated user (guaranteed to be non-null and authenticated).
     * @throws AuthorizationException if no user is logged in.
     */
    static User* requireLogin();
    
    /**
     * Check if a user is authenticated AND a superuser.
     * Throws AuthorizationException if not authenticated or not a superuser.
     * 
     * @return The superuser (guaranteed to be non-null and superuser).
     * @throws AuthorizationException if not authenticated or not superuser.
     */
    static User* requireSuperuser();
    
    /**
     * Check if a user is authenticated AND has a specific permission.
     * Throws AuthorizationException if not authenticated or lacking permission.
     * 
     * @param permissionName The permission to check.
     * @return The user with the required permission.
     * @throws AuthorizationException if not authenticated or lacking permission.
     */
    static User* requirePermission(const QString& permissionName);
    
    /**
     * Check if a user is authenticated AND active.
     * Throws AuthorizationException if not authenticated or inactive.
     * 
     * @return The active user.
     * @throws AuthorizationException if not authenticated or inactive.
     */
    static User* requireActive();
};

}  // namespace calvinc::tools::auth
