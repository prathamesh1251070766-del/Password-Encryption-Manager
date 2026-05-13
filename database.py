# =============================================================================
# database.py
# Purpose: Manages all SQLite database operations
#
# Tables:
#   1. master_password - Stores the hashed master password
#   2. credentials     - Stores encrypted website credentials
#
# Uses SQLite3 (built into Python, no installation needed)
# =============================================================================

import sqlite3
import hashlib
import os


# Database file path
DB_FILE = "vault.db"


def get_connection():
    """
    Create and return a connection to the SQLite database.
    The database file is created automatically if it doesn't exist.
    
    Returns:
        sqlite3.Connection: Active database connection
    """
    connection = sqlite3.connect(DB_FILE)
    
    # Enable foreign key constraints
    connection.execute("PRAGMA foreign_keys = ON")
    
    return connection


def initialize_database():
    """
    Create database tables if they don't already exist.
    
    Tables Created:
        master_password: Stores hashed master password
        credentials: Stores website login credentials
        
    This function is called when the app starts.
    """
    connection = get_connection()
    cursor = connection.cursor()
    
    try:
        # Create master_password table
        # Only ONE row will exist here (the master password hash)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS master_password (
                id       INTEGER PRIMARY KEY AUTOINCREMENT,
                pw_hash  TEXT NOT NULL
            )
        """)
        
        # Create credentials table
        # Stores all website login information
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS credentials (
                id                 INTEGER PRIMARY KEY AUTOINCREMENT,
                website            TEXT NOT NULL,
                username           TEXT NOT NULL,
                encrypted_password TEXT NOT NULL,
                created_at         DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        connection.commit()
        print("[Database] Tables initialized successfully")
        
    except sqlite3.Error as e:
        print(f"[Database] Error initializing database: {e}")
        raise
    
    finally:
        connection.close()


# =============================================================================
# MASTER PASSWORD FUNCTIONS
# =============================================================================

def hash_password(plain_password: str) -> str:
    """
    Hash a password using SHA-256 algorithm.
    
    SHA-256 is a one-way hash function - you cannot reverse it to get
    the original password, making it secure for storing master passwords.
    
    Args:
        plain_password (str): The plain text password to hash
        
    Returns:
        str: The SHA-256 hash as a hexadecimal string
    """
    # Encode the password to bytes and hash it
    password_bytes = plain_password.encode("utf-8")
    hash_object = hashlib.sha256(password_bytes)
    return hash_object.hexdigest()  # Returns 64-character hex string


def is_master_password_set() -> bool:
    """
    Check if a master password has been created.
    
    Returns:
        bool: True if master password exists, False if first-time setup
    """
    connection = get_connection()
    cursor = connection.cursor()
    
    try:
        cursor.execute("SELECT COUNT(*) FROM master_password")
        count = cursor.fetchone()[0]
        return count > 0
    
    except sqlite3.Error as e:
        print(f"[Database] Error checking master password: {e}")
        return False
    
    finally:
        connection.close()


def set_master_password(plain_password: str) -> bool:
    """
    Hash and save the master password to the database.
    
    Args:
        plain_password (str): The master password chosen by user
        
    Returns:
        bool: True if saved successfully, False otherwise
    """
    if not plain_password or len(plain_password) < 4:
        print("[Database] Master password too short")
        return False
    
    connection = get_connection()
    cursor = connection.cursor()
    
    try:
        pw_hash = hash_password(plain_password)
        
        # Remove any existing master password (shouldn't exist, but safety check)
        cursor.execute("DELETE FROM master_password")
        
        # Insert new master password hash
        cursor.execute(
            "INSERT INTO master_password (pw_hash) VALUES (?)",
            (pw_hash,)
        )
        
        connection.commit()
        print("[Database] Master password saved successfully")
        return True
    
    except sqlite3.Error as e:
        print(f"[Database] Error saving master password: {e}")
        connection.rollback()
        return False
    
    finally:
        connection.close()


def verify_master_password(plain_password: str) -> bool:
    """
    Verify if entered master password matches the stored hash.
    
    Args:
        plain_password (str): Password entered by user at login
        
    Returns:
        bool: True if password is correct, False otherwise
    """
    connection = get_connection()
    cursor = connection.cursor()
    
    try:
        cursor.execute("SELECT pw_hash FROM master_password LIMIT 1")
        row = cursor.fetchone()
        
        if not row:
            print("[Database] No master password found in database")
            return False
        
        stored_hash = row[0]
        entered_hash = hash_password(plain_password)
        
        # Compare hashes (secure comparison)
        return stored_hash == entered_hash
    
    except sqlite3.Error as e:
        print(f"[Database] Error verifying master password: {e}")
        return False
    
    finally:
        connection.close()


# =============================================================================
# CREDENTIALS FUNCTIONS
# =============================================================================

def add_credential(website: str, username: str, encrypted_password: str) -> bool:
    """
    Save a new credential entry to the database.
    
    Args:
        website (str): Website name or URL
        username (str): Username or email address
        encrypted_password (str): Already-encrypted password
        
    Returns:
        bool: True if saved successfully, False otherwise
    """
    if not website or not username or not encrypted_password:
        print("[Database] Cannot save - fields are empty")
        return False
    
    connection = get_connection()
    cursor = connection.cursor()
    
    try:
        cursor.execute("""
            INSERT INTO credentials (website, username, encrypted_password)
            VALUES (?, ?, ?)
        """, (website.strip(), username.strip(), encrypted_password))
        
        connection.commit()
        print(f"[Database] Credential saved for '{website}'")
        return True
    
    except sqlite3.Error as e:
        print(f"[Database] Error saving credential: {e}")
        connection.rollback()
        return False
    
    finally:
        connection.close()


def get_all_credentials() -> list:
    """
    Retrieve all saved credentials from the database.
    
    Returns:
        list: List of tuples (id, website, username, encrypted_password, created_at)
              Returns empty list if none found or on error
    """
    connection = get_connection()
    cursor = connection.cursor()
    
    try:
        cursor.execute("""
            SELECT id, website, username, encrypted_password, created_at
            FROM credentials
            ORDER BY website ASC
        """)
        
        rows = cursor.fetchall()
        return rows
    
    except sqlite3.Error as e:
        print(f"[Database] Error fetching credentials: {e}")
        return []
    
    finally:
        connection.close()


def search_credentials(search_term: str) -> list:
    """
    Search credentials by website name or username.
    Uses SQL LIKE for partial matching (case-insensitive).
    
    Args:
        search_term (str): Text to search for
        
    Returns:
        list: Matching credential rows
    """
    if not search_term:
        return get_all_credentials()
    
    connection = get_connection()
    cursor = connection.cursor()
    
    try:
        # Use % wildcards for partial matching
        search_pattern = f"%{search_term}%"
        
        cursor.execute("""
            SELECT id, website, username, encrypted_password, created_at
            FROM credentials
            WHERE website LIKE ? OR username LIKE ?
            ORDER BY website ASC
        """, (search_pattern, search_pattern))
        
        rows = cursor.fetchall()
        return rows
    
    except sqlite3.Error as e:
        print(f"[Database] Error searching credentials: {e}")
        return []
    
    finally:
        connection.close()


def delete_credential(credential_id: int) -> bool:
    """
    Delete a credential entry from the database by ID.
    
    Args:
        credential_id (int): The ID of the credential to delete
        
    Returns:
        bool: True if deleted successfully, False otherwise
    """
    connection = get_connection()
    cursor = connection.cursor()
    
    try:
        cursor.execute(
            "DELETE FROM credentials WHERE id = ?",
            (credential_id,)
        )
        
        connection.commit()
        
        if cursor.rowcount > 0:
            print(f"[Database] Credential ID {credential_id} deleted")
            return True
        else:
            print(f"[Database] No credential found with ID {credential_id}")
            return False
    
    except sqlite3.Error as e:
        print(f"[Database] Error deleting credential: {e}")
        connection.rollback()
        return False
    
    finally:
        connection.close()


def update_credential(credential_id: int, website: str, username: str, encrypted_password: str) -> bool:
    """
    Update an existing credential entry.
    
    Args:
        credential_id (int): ID of credential to update
        website (str): New website name
        username (str): New username
        encrypted_password (str): New encrypted password
        
    Returns:
        bool: True if updated successfully
    """
    connection = get_connection()
    cursor = connection.cursor()
    
    try:
        cursor.execute("""
            UPDATE credentials
            SET website = ?, username = ?, encrypted_password = ?
            WHERE id = ?
        """, (website.strip(), username.strip(), encrypted_password, credential_id))
        
        connection.commit()
        print(f"[Database] Credential ID {credential_id} updated")
        return True
    
    except sqlite3.Error as e:
        print(f"[Database] Error updating credential: {e}")
        connection.rollback()
        return False
    
    finally:
        connection.close()


def get_credential_by_id(credential_id: int):
    """
    Fetch a single credential by its ID.
    
    Args:
        credential_id (int): The credential ID
        
    Returns:
        tuple or None: Credential row or None if not found
    """
    connection = get_connection()
    cursor = connection.cursor()
    
    try:
        cursor.execute("""
            SELECT id, website, username, encrypted_password
            FROM credentials
            WHERE id = ?
        """, (credential_id,))
        
        return cursor.fetchone()
    
    except sqlite3.Error as e:
        print(f"[Database] Error fetching credential by ID: {e}")
        return None
    
    finally:
        connection.close()