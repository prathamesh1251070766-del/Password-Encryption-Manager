In the modern digital era, individuals maintain accounts across dozens of online platforms — from email and social media to banking and e-commerce. Managing unique, strong passwords for each platform has become an increasingly complex challenge. The widespread practice of reusing passwords or storing them in plain text introduces severe security vulnerabilities that can lead to catastrophic data breaches.

This project presents the design and implementation of a "Secure Password Manager with Encryption" — a desktop application built using Python that provides users with a secure, organized, and user-friendly solution for managing their digital credentials.

The application employs Fernet symmetric encryption (AES-128-CBC with HMAC-SHA256 authentication) from the Python cryptography library to encrypt all stored passwords before saving them to a local SQLite database. The master password — which serves as the sole authentication mechanism — is hashed using the SHA-256 algorithm, ensuring it is never stored in plain text and cannot be reversed.

The graphical user interface, built with Python's Tkinter library, features a modern dark-themed design with a login screen, a comprehensive dashboard, a password generator, real-time search functionality, clipboard copy support, and password visibility toggles. The application follows a clean modular architecture with dedicated modules for encryption, database operations, password generation, login, and the dashboard.

The system is designed to be secure-by-default: passwords are encrypted before storage and only decrypted on explicit user request; the master password hash is compared using constant-time comparison; and the encryption key is stored separately from the database. The result is a practical, portable, and fully functional password management solution suitable for personal use, academic study, and professional portfolio demonstration.
Keywords: Password Manager, Fernet Encryption, AES-128, SHA-256, Python, Tkinter, SQLite, Cybersecurity, Credential Management, Symmetric Encryption.
 
