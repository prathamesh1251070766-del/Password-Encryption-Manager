# =============================================================================
# main.py
# Purpose: Application entry point
#
# This file:
#   1. Checks Python version
#   2. Initializes the database
#   3. Launches the Login window
#   4. Starts the Tkinter event loop
# =============================================================================

import sys
import os
import tkinter as tk

# Make sure we're running Python 3.8 or higher
if sys.version_info < (3, 8):
    print("ERROR: This application requires Python 3.8 or higher.")
    print(f"Your version: {sys.version}")
    sys.exit(1)


def check_dependencies():
    """
    Check if all required libraries are installed.
    Shows a friendly error if anything is missing.
    """
    missing_libs = []
    
    try:
        import cryptography
    except ImportError:
        missing_libs.append("cryptography")
    
    try:
        import pyperclip
    except ImportError:
        missing_libs.append("pyperclip")
    
    if missing_libs:
        print("=" * 50)
        print("ERROR: Missing required libraries!")
        print("=" * 50)
        print(f"\nMissing: {', '.join(missing_libs)}")
        print("\nPlease run the following command to install:")
        print(f"\n  pip install {' '.join(missing_libs)}\n")
        print("=" * 50)
        
        # Show GUI error if tkinter is available
        try:
            import tkinter.messagebox as mb
            root = tk.Tk()
            root.withdraw()
            mb.showerror(
                "Missing Libraries",
                f"Required libraries not installed:\n\n"
                f"{chr(10).join(missing_libs)}\n\n"
                f"Please run:\n"
                f"pip install {' '.join(missing_libs)}"
            )
            root.destroy()
        except Exception:
            pass
        
        sys.exit(1)


def create_assets_folder():
    """Create the assets folder if it doesn't exist."""
    assets_path = os.path.join(os.path.dirname(__file__), "assets")
    if not os.path.exists(assets_path):
        os.makedirs(assets_path)
        print("[Main] Assets folder created")


def main():
    """
    Main function - entry point of the application.
    
    Steps:
    1. Check dependencies
    2. Create necessary folders
    3. Initialize database
    4. Launch Login window
    5. Start event loop
    """
    print("=" * 50)
    print("  🔐 Secure Password Manager")
    print("  Starting application...")
    print("=" * 50)
    
    # Step 1: Check all libraries are installed
    check_dependencies()
    
    # Step 2: Create assets folder
    create_assets_folder()
    
    # Step 3: Import modules (after dependency check)
    import database
    
    # Step 4: Initialize database (create tables if not exist)
    print("[Main] Initializing database...")
    database.initialize_database()
    
    # Step 5: Create main Tkinter window
    root = tk.Tk()
    
    # Prevent main window from showing (login is the first window)
    # We'll show it through LoginWindow
    root.withdraw()
    
    # Step 6: Import and launch Login window
    from login import LoginWindow
    
    # Re-show as the login window
    root.deiconify()
    
    login_app = LoginWindow(root)
    
    print("[Main] Application launched successfully!")
    print("[Main] Entering event loop...")
    
    # Step 7: Start Tkinter event loop (keeps app running)
    root.mainloop()
    
    print("[Main] Application closed.")


# ===========================================================================
# Run the application
# Python best practice: Only run if this file is executed directly
# ===========================================================================
if __name__ == "__main__":
    main()