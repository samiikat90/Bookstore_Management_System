#!/usr/bin/env python3
"""
Script to reset password for a specific user and ensure proper authentication.
"""

import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from app.app import app, db, User
from werkzeug.security import generate_password_hash

def reset_user_password(username, new_password):
    """Reset password for a specific user."""
    with app.app_context():
        user = User.query.filter_by(username=username).first()
        if not user:
            print(f"User '{username}' not found!")
            return False
        
        print(f"Found user: {username}")
        print(f"Email: {user.email}")
        print(f"Is Manager: {user.is_manager}")
        
        # Set new password with both hash methods for compatibility
        hashed_password = generate_password_hash(new_password)
        user.password_hash = hashed_password
        user.password = hashed_password  # Legacy compatibility
        
        # Clear any 2FA issues
        user.two_fa_code = None
        user.two_fa_expires = None
        user.two_fa_verified = False
        
        try:
            db.session.commit()
            print(f"✅ Password reset successful for '{username}'!")
            print(f"New password: {new_password}")
            print(f"You can now log in with these credentials.")
            return True
        except Exception as e:
            db.session.rollback()
            print(f"❌ Error resetting password: {e}")
            return False

def main():
    print("=" * 50)
    print("PASSWORD RESET TOOL")
    print("=" * 50)
    
    # Reset sfranco password to something known
    username = "sfranco"
    new_password = "admin123"
    
    print(f"Resetting password for user: {username}")
    if reset_user_password(username, new_password):
        print()
        print("=" * 50)
        print("LOGIN CREDENTIALS:")
        print("=" * 50)
        print(f"Username: {username}")
        print(f"Password: {new_password}")
        print("=" * 50)
    
    # Also show other available accounts
    print()
    print("OTHER AVAILABLE ACCOUNTS:")
    print("Username: admin | Password: admin123")
    print("Username: manager1 | Password: admin123")

if __name__ == "__main__":
    main()