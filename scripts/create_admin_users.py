#!/usr/bin/env python3
"""
Script to create admin users with notification preferences for the Chapter 6: A Plot Twist bookstore.
This script allows you to add multiple admin users who can receive email notifications
for new orders and order status changes.
"""

import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from app.app import app, db, User
from werkzeug.security import generate_password_hash

def create_admin_user(username, password, email, full_name=None, receive_notifications=True):
    """Create a new admin user with notification preferences."""
    with app.app_context():
        # Check if user already exists
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            print(f"User '{username}' already exists. Skipping...")
            return False
        
        # Check if email already exists
        existing_email = User.query.filter_by(email=email).first()
        if existing_email:
            print(f"Email '{email}' already exists. Skipping...")
            return False
        
        # Create new admin user
        hashed_password = generate_password_hash(password)
        new_user = User(
            username=username,
            password=hashed_password,
            is_manager=True,  # Use is_manager instead of role
            email=email,
            full_name=full_name or username,
            receive_notifications=receive_notifications
        )
        
        try:
            db.session.add(new_user)
            db.session.commit()
            print(f"Successfully created admin user: {username} ({email})")
            if receive_notifications:
                print(f"   Email notifications enabled")
            return True
        except Exception as e:
            db.session.rollback()
            print(f"Error creating user {username}: {e}")
            return False

def main():
    """Main function to create admin users."""
    print("Chapter 6: A Plot Twist - Admin User Creation Tool")
    print("=" * 55)
    
    print("Welcome! This tool helps you create admin users for your bookstore.")
    print("You can either create users interactively or skip to use existing accounts.")
    
    print("\nOptions:")
    print("1. Create custom admin users (recommended for your own users)")
    print("2. Create default test users (admin, manager1, manager2, supervisor)")
    print("3. Exit")
    
    choice = input("\nEnter your choice (1-3): ").strip()
    
    if choice == "3":
        print("Exiting...")
        return
    
    created_count = 0
    
    if choice == "1":
        # Interactive custom user creation
        print(f"\nCustom Admin User Creation Mode")
        print("=" * 40)
        print("Create admin users with your own usernames and email addresses.")
        print("Press Enter on username when you're done adding users.\n")
        
        while True:
            print(f"--- New Admin User #{created_count + 1} ---")
            username = input("Username: ").strip()
            if not username:
                print("Finished creating custom users.")
                break
            
            password = input("Password: ").strip()
            if not password:
                print("Password cannot be empty. Skipping user.")
                continue
            
            email = input("Email address: ").strip()
            if not email:
                print("Email cannot be empty. Skipping user.")
                continue
            
            # Validate email format (basic check)
            if "@" not in email or "." not in email:
                print("Please enter a valid email address. Skipping user.")
                continue
            
            full_name = input("Full name (optional): ").strip()
            if not full_name:
                full_name = username.title()  # Use username as default
            
            notifications = input("Enable email notifications? (Y/n): ").strip().lower()
            receive_notifications = notifications not in ['n', 'no', '0', 'false']
            
            print(f"\nCreating admin user '{username}'...")
            if create_admin_user(username, password, email, full_name, receive_notifications):
                created_count += 1
                print(f"User '{username}' created successfully!")
            else:
                print(f"Failed to create user '{username}'.")
            
            print()  # Empty line for readability
    
    elif choice == "2":
        # Default test users
        print(f"\nCreating Default Test Users...")
        print("=" * 35)
        
        admin_users = [
            ("admin", "admin123", "admin@plottwist.com", "Primary Administrator", True),
            ("manager1", "manager123", "manager1@plottwist.com", "Store Manager 1", True),
            ("manager2", "manager123", "manager2@plottwist.com", "Store Manager 2", True),
            ("supervisor", "super123", "supervisor@plottwist.com", "Store Supervisor", True),
        ]
        
        for username, password, email, full_name, notifications in admin_users:
            print(f"Creating user: {username} ({email})")
            if create_admin_user(username, password, email, full_name, notifications):
                created_count += 1
    
    # Summary
    print(f"\nSummary")
    print("=" * 20)
    print(f"Successfully created {created_count} admin users.")
    
    if created_count > 0:
        print(f"\nWhat you can do now:")
        print(f"  - Visit http://127.0.0.1:5000 to access the bookstore")
        print(f"  - Log in with any of the admin accounts you created")
        print(f"  - Receive email notifications for new orders and status changes")
        print(f"  - Manage inventory, orders, and other admin users")
        print(f"  - Access admin user management at http://127.0.0.1:5000/admin/users")
        
        print(f"\nTips:")
        print(f"  - Test the notification system by placing a sample order")
        print(f"  - Use the web interface to manage notification preferences")
        print(f"  - Create additional admin users through the web interface")
    else:
        print(f"\nNo new users were created. You can run this script again anytime.")
    
    print(f"\nThank you for using Chapter 6: A Plot Twist!")

if __name__ == "__main__":
    main()