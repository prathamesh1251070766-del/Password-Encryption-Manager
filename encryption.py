# =============================================================================
# encryption.py
# Purpose: Handles Fernet symmetric encryption for password storage
# 
# How it works:
# - Fernet uses AES-128-CBC encryption with HMAC-SHA256 authentication
# - A unique encryption key is generated and stored locally
# - Passwords are encrypted before saving, decrypted only when displayed
# =============================================================================

import os
from cryptography.fernet import Fernet


# Path where the encryption key will be stored
KEY_FILE = "secret.key"


def generate_key():
    """
    Generate a new Fernet encryption key and save it to a file.
    
    IMPORTANT: This key is needed to decrypt all stored passwords.
    If this key is lost, passwords CANNOT be recovered.
    
    Returns:
        bytes: The generated encryption key
    """
    key = Fernet.generate_key()
    
    with open(KEY_FILE, "wb") as key_file:
        key_file.write(key)
    
    print(f"[Encryption] New key generated and saved to '{KEY_FILE}'")
    return key


def load_key():
    """
    Load the encryption key from the key file.
    If key file doesn't exist, generate a new one.
    
    Returns:
        bytes: The encryption key
    """
    if not os.path.exists(KEY_FILE):
        print("[Encryption] Key file not found. Generating new key...")
        return generate_key()
    
    with open(KEY_FILE, "rb") as key_file:
        key = key_file.read()
    
    return key


def get_fernet():
    """
    Create and return a Fernet cipher object using the stored key.
    
    Returns:
        Fernet: Cipher object ready for encryption/decryption
    """
    key = load_key()
    return Fernet(key)


def encrypt_password(plain_password: str) -> str:
    """
    Encrypt a plain text password.
    
    Args:
        plain_password (str): The password to encrypt
        
    Returns:
        str: The encrypted password as a string (base64 encoded)
        
    Example:
        encrypted = encrypt_password("MySecret123!")
        # Returns something like: "gAAAAABh..."
    """
    if not plain_password:
        raise ValueError("Password cannot be empty")
    
    fernet = get_fernet()
    
    # Convert string to bytes, encrypt, then convert back to string for storage
    encrypted_bytes = fernet.encrypt(plain_password.encode("utf-8"))
    
    # Return as string so it can be stored in SQLite TEXT column
    return encrypted_bytes.decode("utf-8")


def decrypt_password(encrypted_password: str) -> str:
    """
    Decrypt an encrypted password back to plain text.
    
    Args:
        encrypted_password (str): The encrypted password string
        
    Returns:
        str: The original plain text password
        
    Raises:
        Exception: If decryption fails (wrong key or corrupted data)
    """
    if not encrypted_password:
        raise ValueError("Encrypted password cannot be empty")
    
    fernet = get_fernet()
    
    try:
        # Convert string back to bytes, decrypt, then decode to string
        decrypted_bytes = fernet.decrypt(encrypted_password.encode("utf-8"))
        return decrypted_bytes.decode("utf-8")
    
    except Exception as e:
        print(f"[Encryption] Decryption failed: {e}")
        raise Exception("Failed to decrypt password. Key may be missing or corrupted.")