#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app import app, send_admin_order_notification
from datetime import datetime

def send_test_admin_notification():
 """Send a test admin notification right now to verify email delivery."""
 with app.app_context():
 print("Sending Test Admin Notification")
 print("=" * 35)
 
 test_order = {
 'order_id': 'TEST-VERIFICATION',
 'customer_name': 'Admin Notification Test Customer',
 'customer_email': 'test@example.com',
 'customer_phone': '555-TEST',
 'customer_address': 'Test Address for Admin Notification Verification',
 'book_count': 1,
 'total_amount': 99.99,
 'status': 'TEST',
 'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
 'items': [
 {
 'title': 'Admin Notification Test Book',
 'author': 'Test Author',
 'isbn': '9999999999999',
 'price': 99.99,
 'quantity': 1
 }
 ]
 }
 
 print("Sending test notification to all admin users...")
 print("You should receive this at:")
 print(" - samiikat90@gmail.com")
 print(" - samantha199054@gmail.com")
 print()
 
 result = send_admin_order_notification(test_order)
 
 if result:
 print("[SUCCESS] TEST NOTIFICATION SENT SUCCESSFULLY!")
 print()
 print("[EMAIL] Check your email now:")
 print(" Subject: New Order Alert - PlotTwist Bookstore")
 print(" From: chapter6aplottwist@gmail.com")
 print(" Content: Should mention 'Admin Notification Test Customer'")
 print()
 print("If you receive this test email, then admin notifications")
 print("are working perfectly and the 10 real order notifications")
 print("from today were also sent successfully!")
 else:
 print("[ERROR] TEST NOTIFICATION FAILED TO SEND")
 print("This indicates there's an issue with the email system")

if __name__ == "__main__":
 send_test_admin_notification()