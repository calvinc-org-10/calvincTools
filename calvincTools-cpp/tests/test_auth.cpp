#include <iostream>
#include <cassert>
#include <memory>
#include "calvinc_tools/auth/password_service.hpp"
#include "calvinc_tools/auth/auth_context.hpp"
#include "calvinc_tools/auth/user.hpp"

using namespace calvinc::tools::auth;
using namespace calvinc::tools::database;

int main() {
    std::cout << "Running Authentication Tests\n";
    
    // Test password hashing
    QString password = "myPassword123";
    QString hash1 = PasswordService::hashPassword(password);
    QString hash2 = PasswordService::hashPassword(password);
    
    // Hashes should be different (different salts)
    assert(hash1 != hash2);
    
    // But both should verify with the same password
    assert(PasswordService::verifyPassword(hash1, password));
    assert(PasswordService::verifyPassword(hash2, password));
    
    // Wrong password should fail
    assert(!PasswordService::verifyPassword(hash1, "wrongPassword"));
    
    // Test auth context
    assert(!AuthContext::isAuthenticated());
    
    User userData;
    userData.username = "testuser";
    userData.firstName = "Test";
    userData.lastName = "User";
    userData.email = "test@example.com";
    userData.activeStatus = true;
    
    auto user = std::make_unique<User>(userData);
    AuthContext::setCurrentUser(std::move(user));
    
    assert(AuthContext::isAuthenticated());
    User* current = AuthContext::getCurrentUser();
    assert(current != nullptr);
    assert(current->getUsername() == "testuser");
    
    AuthContext::logout();
    assert(!AuthContext::isAuthenticated());
    
    std::cout << "All authentication tests passed!\n";
    return 0;
}
