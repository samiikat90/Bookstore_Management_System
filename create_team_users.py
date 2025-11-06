#!/usr/bin/env python3
"""
Script to create all admin users including team members.
"""

import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from app.app import app, db, User
from werkzeug.security import generate_password_hash

def create_all_admin_users():
    """Create all admin users from the README."""
    with app.app_context():
        # Ensure tables exist
        db.create_all()
        
        print("Creating admin users...")
        
        # Team member accounts
        team_users = [
            {
                'username': 'sfranco',
                'password': 'admin123',
                'email': 'samiikat90@gmail.com',
                'full_name': 'Samantha Franco',
                'receive_notifications': True
            },
            {
                'username': 'bmorris',
                'password': 'admin123',
                'email': 'mbrmorris@gmail.com',
                'full_name': 'Becky Morris',
                'receive_notifications': True
            },
            {
                'username': 'fbrown',
                'password': 'admin123',
                'email': 'felicia.brown.711@gmail.com',
                'full_name': 'Felicia Brown',
                'receive_notifications': True
            },
            {
                'username': 'amurphy',
                'password': 'admin123',
                'email': 'almurphy469@gmail.com',
                'full_name': 'Anthony Murphy',
                'receive_notifications': True
            },
            {
                'username': 'admin',
                'password': 'admin123',
                'email': 'admin@plottwist.com',
                'full_name': 'System Administrator',
                'receive_notifications': True
            },
            {
                'username': 'manager1',
                'password': 'admin123',
                'email': 'manager1@plottwist.com',
                'full_name': 'Store Manager',
                'receive_notifications': True
            },
            {
                'username': 'supervisor',
                'password': 'admin123',
                'email': 'supervisor@plottwist.com',
                'full_name': 'Store Supervisor',
                'receive_notifications': True
            }
        ]
        
        created_count = 0
        for user_data in team_users:
            # Check if user already exists
            existing_user = User.query.filter_by(username=user_data['username']).first()
            if existing_user:
                print(f"User '{user_data['username']}' already exists. Skipping...")
                continue
            
            try:
                hashed_password = generate_password_hash(user_data['password'])
                user = User(
                    username=user_data['username'],
                    password=hashed_password,
                    is_manager=True,
                    email=user_data['email'],
                    full_name=user_data['full_name'],
                    receive_notifications=user_data['receive_notifications']
                )
                db.session.add(user)
                created_count += 1
                print(f"Created user: {user_data['username']} ({user_data['full_name']})")
            except Exception as e:
                print(f"Error creating user {user_data['username']}: {e}")
        
        try:
            db.session.commit()
            print(f"\nSuccessfully created {created_count} admin users!")
            print("\nLogin credentials:")
            print("=" * 50)
            for user_data in team_users:
                print(f"Username: {user_data['username']} | Password: {user_data['password']}")
            print("=" * 50)
        except Exception as e:
            db.session.rollback()
            print(f"Error saving users to database: {e}")

if __name__ == "__main__":
    create_all_admin_users()