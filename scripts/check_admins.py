import sys
import os

# Ensure the project root is on sys.path so `app` package can be imported
ROOT = os.path.dirname(os.path.dirname(__file__))
if ROOT not in sys.path:
 sys.path.insert(0, ROOT)

from app.app import app, db, User

def main():
 with app.app_context():
 print("=== ADMIN USERS EMAIL CONFIGURATION ===")
 
 # Get all admin users
 admin_users = User.query.filter_by(is_manager=True).all()
 
 if not admin_users:
 print("No admin users found!")
 return
 
 print(f"Found {len(admin_users)} admin user(s):\n")
 
 for i, admin in enumerate(admin_users, 1):
 print(f"Admin {i}:")
 print(f" Username: {admin.username}")
 print(f" Full Name: {admin.full_name or 'Not set'}")
 print(f" Email: {admin.email or 'NOT SET'}")
 print(f" Notifications Enabled: {admin.receive_notifications}")
 print(f" Can receive notifications: {admin.email and admin.receive_notifications}")
 print()
 
 # Check if any admin can receive notifications
 can_notify = any(admin.email and admin.receive_notifications for admin in admin_users)
 print(f"Can send notifications to at least one admin: {can_notify}")
 
 if not can_notify:
 print("\nNO ADMIN CAN RECEIVE EMAIL NOTIFICATIONS!")
 print("Fix needed: Set admin email addresses and enable notifications")

if __name__ == '__main__':
 main()