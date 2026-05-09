#include "calvinc_tools/auth/auth_context.hpp"

namespace calvinc::tools::auth {

std::unique_ptr<User> AuthContext::currentUser_;

User* AuthContext::getCurrentUser() {
    return currentUser_.get();
}

void AuthContext::setCurrentUser(std::unique_ptr<User> user) {
    currentUser_ = std::move(user);
}

bool AuthContext::isAuthenticated() {
    return currentUser_ != nullptr && currentUser_->isAuthenticated();
}

void AuthContext::logout() {
    currentUser_.reset();
}

}  // namespace calvinc::tools::auth
