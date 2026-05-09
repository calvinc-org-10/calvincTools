#include "calvinc_tools/auth/user.hpp"

namespace calvinc::tools::auth {

User::User(const database::User& userData)
    : userData_(userData) {
}

bool User::hasPermission(const QString& permissionName) const {
    if (userData_.isSuperuser) {
        return true;  // Superusers have all permissions
    }
    
    QStringList permList = userData_.permissions.split(',', Qt::SkipEmptyParts);
    for (const QString& perm : permList) {
        if (perm.trimmed().compare(permissionName, Qt::CaseInsensitive) == 0) {
            return true;
        }
    }
    
    return false;
}

}  // namespace calvinc::tools::auth
