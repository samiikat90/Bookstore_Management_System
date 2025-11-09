#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app import app, db, User

def check_admin_email_addresses():
	"""Check which admin email addresses are configured to receive notifications."""
	with app.app_context():
		print("Admin Email Notification Configuration")
		print("=" * 45)
		
		# Get all admin users
		admin_users = User.query.filter_by(is_manager=True).all()
		
		print(f"Total admin users: {len(admin_users)}")
		print(f"Admin users with notifications enabled:")
		
		enabled_count = 0
		your_emails = [] # Track emails that go to you specifically
		
		for admin in admin_users:
			status = " ENABLED" if admin.receive_notifications else " DISABLED"
			print(f" - {admin.full_name or admin.username} ({admin.email}) - {status}")
			
			if admin.receive_notifications:
				enabled_count += 1
				# Check which emails are yours
				if admin.email in ['samiikat90@gmail.com', 'samantha199054@gmail.com']:
					your_emails.append(admin.email)
		
		print(f"\\nSummary:")
		print(f" Notifications enabled: {enabled_count}/{len(admin_users)} admins")
		print(f" Your email addresses receiving notifications: {len(your_emails)}")
		
		if your_emails:
			print(f" Your emails: {', '.join(your_emails)}")
			print(f"\\n[EMAIL] You should be receiving admin notifications at:")
			for email in your_emails:
				print(f" {email}")
			print(f"\\n[WARNING] Check these folders:")
			print(f" - Inbox")
			print(f" - Spam/Junk folder") 
			print(f" - Promotions tab (in Gmail)")
			print(f" - Social tab (in Gmail)")
		else:
			print(f"\\n[WARNING] None of the admin emails are configured with your personal email addresses!")
			print(f" This might be why you're not seeing notifications.")
		
		print(f"\\n[STATS] Expected notification volume:")
		print(f" With 10 recent orders, you should have received:")
		print(f" - 8 notifications from customer checkouts (send_admin_order_notification)")
		print(f" - 2 notifications from guest checkouts (send_admin_notification)")
		print(f" - Total: 10 admin notification emails per admin email address")
		print(f" - For {len(your_emails)} of your email addresses = {10 * len(your_emails)} total emails")

if __name__ == "__main__":
 check_admin_email_addresses()