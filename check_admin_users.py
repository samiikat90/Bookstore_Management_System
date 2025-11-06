#!/usr/bin/env python3
"""
Script to check existing admin users in the database.
"""

import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from app.app import app, db, User

def check_admin_users():
    """Check all existing admin users in the database."""
    with app.app_context():
        # Get all users who are managers (admin users)
        admin_users = User.query.filter_by(is_manager=True).all()
        
        print("Existing Admin Users in Database:")
        print("=" * 50)
        
        if not admin_users:
            print("No admin users found in the database.")
            return
        
        for user in admin_users:
            print(f"Username: {user.username}")
            print(f"  Email: {user.email}")
            print(f"  Full Name: {user.full_name}")
            print(f"  Manager: {user.is_manager}")
            print(f"  Notifications: {user.receive_notifications}")
            print(f"  Created: {user.created_at if hasattr(user, 'created_at') else 'N/A'}")
            print("-" * 30)

if __name__ == "__main__":
    check_admin_users()