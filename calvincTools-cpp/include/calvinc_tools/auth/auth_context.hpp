#pragma once

#include <memory>
#include <QString>
#include "user.hpp"

namespace calvinc::tools::auth {

/**
 * AuthContext manages the current user session and authentication state.
 * Provides access to the currently authenticated user.
 */
class AuthContext {
private:
    static std::unique_ptr<User> currentUser_;
    
    AuthContext() = delete;
    AuthContext(const AuthContext&) = delete;
    AuthContext& operator=(const AuthContext&) = delete;

public:
    /**
     * Get the currently authenticated user.
     * 
     * @return Pointer to the current User, or nullptr if no user is logged in.
     */
    static User* getCurrentUser();
    
    /**
     * Set the currently authenticated user.
     * 
     * @param user The user to set as current, or nullptr to clear.
     */
    static void setCurrentUser(std::unique_ptr<User> user);
    
    /**
     * Check if a user is currently authenticated.
     */
    static bool isAuthenticated();
    
    /**
     * Log out the current user by clearing the current user pointer.
     */
    static void logout();
};

}  // namespace calvinc::tools::auth
