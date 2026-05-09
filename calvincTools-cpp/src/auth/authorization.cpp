#include "calvinc_tools/auth/authorization.hpp"
#include "auth_context.hpp"

namespace calvinc::tools::auth {

User* Authorization::requireLogin() {
    User* user = AuthContext::getCurrentUser();
    if (!user || !user->isAuthenticated()) {
        throw AuthorizationException("User must be logged in to access this resource.");
    }
    return user;
}

User* Authorization::requireSuperuser() {
    User* user = requireLogin();
    if (!user->isSuperuser()) {
        throw AuthorizationException("User does not have permission to access this resource (superuser required).");
    }
    return user;
}

User* Authorization::requirePermission(const QString& permissionName) {
    User* user = requireLogin();
    if (!user->hasPermission(permissionName)) {
        throw AuthorizationException(
            QString("User does not have the required permission: %1")
                .arg(permissionName).toStdString()
        );
    }
    return user;
}

User* Authorization::requireActive() {
    User* user = requireLogin();
    if (!user->isActive()) {
        throw AuthorizationException("User account is not active.");
    }
    return user;
}

}  // namespace calvinc::tools::auth
