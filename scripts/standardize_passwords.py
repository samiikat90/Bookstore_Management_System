#!/usr/bin/env python3
"""
Script to standardize all admin passwords to admin123.
"""

import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from app.app import app, db, User
from werkzeug.security import generate_password_hash

def standardize_admin_passwords():
    """Set all admin users to use admin123 password."""
    with app.app_context():
        # Get all admin users
        admin_users = User.query.filter_by(is_manager=True).all()
        
        if not admin_users:
            print("No admin users found!")
            return
        
        print("Standardizing all admin passwords to 'admin123'...")
        print("=" * 50)
        
        standard_password = "admin123"
        hashed_password = generate_password_hash(standard_password)
        
        updated_count = 0
        for user in admin_users:
            print(f"Updating password for: {user.username}")
            
            # Set password with both hash methods for compatibility
            user.password_hash = hashed_password
            user.password = hashed_password  # Legacy compatibility
            
            # Clear any 2FA issues
            user.two_fa_code = None
            user.two_fa_expires = None
            user.two_fa_verified = False
            
            updated_count += 1
        
        try:
            db.session.commit()
            print(f"Successfully updated {updated_count} admin accounts!")
            print("=" * 50)
            print("ALL ADMIN LOGIN CREDENTIALS:")
            print("=" * 50)
            for user in admin_users:
                print(f"Username: {user.username} | Password: {standard_password}")
            print("=" * 50)
            print("All admin users now use the same password for easy access!")
            
        except Exception as e:
            db.session.rollback()
            print(f"Error updating passwords: {e}")

def main():
    print("=" * 60)
    print("ADMIN PASSWORD STANDARDIZATION TOOL")
    print("=" * 60)
    standardize_admin_passwords()

if __name__ == "__main__":
    main()