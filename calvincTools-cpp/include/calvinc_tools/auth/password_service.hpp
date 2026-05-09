#pragma once

#include <QString>
#include <string>

namespace calvinc::tools::auth {

/**
 * PasswordService handles password hashing and verification using PBKDF2.
 * 
 * Default configuration:
 * - Hash function: SHA512
 * - Salt length: 16 bytes
 * - Iterations: 100,000
 * - Format: "{salt_hex}${hash_hex}"
 */
class PasswordService {
private:
    static constexpr int SALT_LENGTH = 16;
    static constexpr int HASH_ITERATIONS = 100000;
    static constexpr const char* HASH_FUNC = "SHA512";
    static constexpr const char* PEPPER = "sH0uLdBEsecrit";
    static constexpr const char* DELIMITER = "2$3g";
    
public:
    /**
     * Hash a plain-text password using PBKDF2 with a random salt.
     * 
     * @param password The plain-text password to hash.
     * @return A hashed password string in the format "{salt}${hash}".
     */
    static QString hashPassword(const QString& password);
    
    /**
     * Verify a plain-text password against a stored hash.
     * Uses constant-time comparison to prevent timing attacks.
     * 
     * @param storedHash The stored password hash.
     * @param providedPassword The plain-text password to verify.
     * @return true if the password matches, false otherwise.
     */
    static bool verifyPassword(const QString& storedHash, const QString& providedPassword);
    
private:
    /**
     * Create a random salt for hashing.
     */
    static QByteArray createSalt(int length = SALT_LENGTH);
};

}  // namespace calvinc::tools::auth
