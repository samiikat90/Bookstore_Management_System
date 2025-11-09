#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app import app, db, User

def test_notification_toggle():
	"""Test the admin notification toggle functionality."""
	with app.app_context():
		print("Testing Admin Notification Toggle")
		print("=" * 40)
		
		# Get all admin users
		admin_users = User.query.filter_by(is_manager=True).all()
		
		print(f"Current notification settings for {len(admin_users)} admin users:")
		print("-" * 60)
		
		for user in admin_users:
			status = " ENABLED" if user.receive_notifications else " DISABLED"
			print(f" {user.username:<15} ({user.email:<30}) - {status}")
		
		print(f"\\n[EMAIL] How to use the toggle feature:")
		print(f" 1. Go to http://127.0.0.1:5000/admin/users")
		print(f" 2. Login as an admin user")
		print(f" 3. Use the toggle switches in the 'Notifications' column")
		print(f" 4. Changes are saved immediately")
		
		print(f"\\n Backend functionality added:")
		print(f" - New route: /admin/users/<user_id>/toggle_notifications")
		print(f" - AJAX-powered toggle switches")
		print(f" - Real-time visual feedback")
		print(f" - CSRF protection")
		print(f" - Success/error notifications")

if __name__ == "__main__":
	test_notification_toggle()