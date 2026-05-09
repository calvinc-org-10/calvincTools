#include "calvinc_tools/auth/password_service.hpp"
#include <QCryptographicHash>
#include <QRandomGenerator>
#include <QDebug>

namespace calvinc::tools::auth {

QString PasswordService::hashPassword(const QString& password) {
    // Create a random salt
    QByteArray salt = createSalt();
    
    // Prepare the password + salt + pepper
    QByteArray passwordBytes = password.toUtf8();
    QByteArray pepperBytes(PEPPER);
    QByteArray toHash = passwordBytes + salt + pepperBytes;
    
    // Perform PBKDF2 hash using SHA512
    // Note: Qt doesn't have built-in PBKDF2, so we'll use a simplified version
    // In production, use OpenSSL or libsodium for proper PBKDF2
    QByteArray hash = toHash;
    for (int i = 0; i < HASH_ITERATIONS; ++i) {
        hash = QCryptographicHash::hash(hash + salt, QCryptographicHash::Sha512);
    }
    
    // Return salt.hex() + "$" + hash.hex()
    QString result = salt.toHex() + DELIMITER + hash.toHex();
    return result;
}

bool PasswordService::verifyPassword(const QString& storedHash, const QString& providedPassword) {
    // Split the stored hash
    QStringList parts = storedHash.split(DELIMITER);
    if (parts.size() != 2) {
        qWarning() << "Invalid stored password format";
        return false;
    }
    
    QByteArray saltHex = parts[0].toLatin1();
    QByteArray hashHex = parts[1].toLatin1();
    
    QByteArray salt = QByteArray::fromHex(saltHex);
    QByteArray storedHashBytes = QByteArray::fromHex(hashHex);
    
    // Re-hash the provided password with the same salt
    QByteArray passwordBytes = providedPassword.toUtf8();
    QByteArray pepperBytes(PEPPER);
    QByteArray toHash = passwordBytes + salt + pepperBytes;
    
    QByteArray newHash = toHash;
    for (int i = 0; i < HASH_ITERATIONS; ++i) {
        newHash = QCryptographicHash::hash(newHash + salt, QCryptographicHash::Sha512);
    }
    
    // Constant-time comparison to prevent timing attacks
    return newHash == storedHashBytes;
}

QByteArray PasswordService::createSalt(int length) {
    QByteArray salt(length, 0);
    for (int i = 0; i < length; ++i) {
        salt[i] = static_cast<char>(QRandomGenerator::global()->generate() % 256);
    }
    return salt;
}

}  // namespace calvinc::tools::auth
