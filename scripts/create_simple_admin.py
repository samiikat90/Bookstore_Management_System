#!/usr/bin/env python3
"""
Simple script to create a single admin user.
"""

import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from app.app import app, db, User
from werkzeug.security import generate_password_hash

def create_simple_admin():
    """Create a simple admin user."""
    with app.app_context():
        # Ensure database tables exist
        db.create_all()
        
        # Check if any admin users exist
        existing_admin = User.query.filter_by(is_manager=True).first()
        if existing_admin:
            print(f"Admin user already exists: {existing_admin.username}")
            return
        
        # Create default admin user
        username = "admin"
        password = "admin123"
        email = "admin@plottwist.com"
        full_name = "Administrator"
        
        hashed_password = generate_password_hash(password)
        new_user = User(
            username=username,
            password_hash=hashed_password,
            password=hashed_password,  # For legacy compatibility
            is_manager=True,
            email=email,
            full_name=full_name,
            receive_notifications=True
        )
        
        try:
            db.session.add(new_user)
            db.session.commit()
            print("=" * 50)
            print("ADMIN USER CREATED SUCCESSFULLY!")
            print("=" * 50)
            print(f"Username: {username}")
            print(f"Password: {password}")
            print(f"Email: {email}")
            print("=" * 50)
            print("You can now log in to the bookstore system!")
            print("Visit: http://127.0.0.1:5000")
            print("=" * 50)
        except Exception as e:
            db.session.rollback()
            print(f"Error creating admin user: {e}")

if __name__ == "__main__":
    create_simple_admin()