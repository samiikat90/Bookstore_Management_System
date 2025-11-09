#!/usr/bin/env python3
"""
Test script to check email notifications and admin users
"""
import sys
import os

# Add the app directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from app import app, db, User, send_email_notification

def test_email_system():
	with app.app_context():
		print("=== Email System Test ===")
		
		# Check admin users
		admin_users = User.query.filter_by(is_manager=True).all()
		print(f"\nFound {len(admin_users)} admin users:")
		
		for user in admin_users:
			print(f" - {user.username}: email={user.email}, notifications={user.receive_notifications}")
		
		# Check if notification-enabled admins exist
		notification_admins = User.query.filter_by(is_manager=True, receive_notifications=True).all()
		print(f"\nAdmin users with notifications enabled: {len(notification_admins)}")
		
		# Test email sending
		print("\n=== Testing Email Sending ===")
		test_email = "samiikat90@gmail.com" # Replace with your email for testing
		
		try:
			result = send_email_notification(
				to_email=test_email,
				subject="Test Email from Bookstore System",
				body="This is a test email to verify the email system is working.",
				html_body="<html><body><h2>Test Email</h2><p>This is a test email to verify the email system is working.</p></body></html>"
			)
			
			if result:
				print(f"[SUCCESS] Test email sent successfully to {test_email}")
			else:
				print(f"[FAILED] Failed to send test email to {test_email}")

		except Exception as e:
			print(f"[ERROR] Error sending test email: {e}")

if __name__ == "__main__":
 test_email_system()