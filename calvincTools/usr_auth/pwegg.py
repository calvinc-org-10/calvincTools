"""
Password scramblers, based on hashlib functions. These are not meant to be used directly, but rather as part of a larger authentication system that handles user management and security.
"""
from typing import Any, Text
import hashlib, hmac

DEFAULT_HASH_FUNC:str = 'sha512'
SALT_LENGTH:int = 16
_DEFAULT_PEPPER: str = 'sH0uLdBEsecrit'
HASH_ITERATIONS: int = 100000


# def password_hash(password:Text, hash_func:str='', salt:Text=''):
#     hash_input = salt + password if salt else password
#     if not hash_func:
#         hash_func = DEFAULT_HASH_FUNC
#     assert hash_func in hashlib.algorithms_available, f"Hash function '{hash_func}' is not available in hashlib."
#     hash_ = hashlib.new(hash_func, hash_input.encode('utf-8'))
#     return hash_.hexdigest() if hasattr(hash_, 'hexdigest') else str(hash_)

def hash_password(password: str, pepper:str = _DEFAULT_PEPPER, hash_func:str = DEFAULT_HASH_FUNC) -> str:
    # 1. Generate a 16-byte random salt
    salt = create_salt(SALT_LENGTH)

    assert hash_func in hashlib.algorithms_available, f"Hash function '{hash_func}' is not available in hashlib."

    # 2. Hash the password + salt + pepper
    pw_hash = hashlib.pbkdf2_hmac(
        hash_func,
        password.encode('utf-8') + salt + pepper.encode('utf-8'),
        salt,
        HASH_ITERATIONS
    )
    
    # 3. Store as salt.hex() + "$" + hash.hex()
    # This makes it one single string for your DB
    return f"{salt.hex()}${pw_hash.hex()}"

def verify_password(stored_string: str, provided_password: str, pepper:str = _DEFAULT_PEPPER, hash_func:str = DEFAULT_HASH_FUNC) -> bool:
    # 1. Split the stored string back into salt and hash
    splitstr = stored_string.split('$')
    if len(splitstr) != 2:
        # raise ValueError("Stored password string is not in the expected 'salt$hash' format.")
        return False 
    salt_hex, stored_hash_hex = splitstr[0], splitstr[1]
    
    salt = bytes.fromhex(salt_hex)
    stored_hash = bytes.fromhex(stored_hash_hex)
    
    assert hash_func in hashlib.algorithms_available, f"Hash function '{hash_func}' is not available in hashlib."

    # 2. Re-hash the provided password using the same salt and pepper
    new_hash = hashlib.pbkdf2_hmac(
        hash_func,
        provided_password.encode('utf-8') + salt + pepper.encode('utf-8'),
        salt,
        HASH_ITERATIONS
    )
    
    # 3. Compare them securely to prevent timing attacks
    return hmac.compare_digest(new_hash, stored_hash)

def create_salt(length=SALT_LENGTH) -> bytes:
    """Create a random salt string of the specified length."""
    import os
    return os.urandom(length)

def change_password(username:Text, new_password:Text, hash_func:str='', salt:Text=''):
    """Change the password for the specified user."""
    # This function would interact with the database to update the user's password hash.
    # The implementation would depend on the specific database and ORM being used.
    pass

