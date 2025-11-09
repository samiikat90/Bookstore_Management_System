#!/usr/bin/env python3

"""
Test script to verify email notification system is working
"""

import os
import sys

# Add the app directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

# Import functions from app.py
from app import send_email_notification, send_order_confirmation_email, send_admin_order_notification
import logging

# Enable debug logging
logging.basicConfig(level=logging.DEBUG)

def test_basic_email():
	"""Test basic email sending functionality"""
	print("=== Testing Basic Email Notification ===")
	
	test_email = "chapter6aplottwist@gmail.com"  # Sending to same account for testing
	subject = "Test Email Notification"
	body = "This is a test email from the bookstore notification system."
	
	result = send_email_notification(test_email, subject, body)
	print(f"Basic email test result: {result}")
	return result

def test_order_confirmation():
	"""Test customer order confirmation email"""
	print("\n=== Testing Order Confirmation Email ===")
	
	test_email = "chapter6aplottwist@gmail.com"
	customer_name = "Test Customer"
	
	order_details = {
		'total': 29.95,
		'date': 'November 8, 2024',
		'payment_method': 'Credit Card',
		'items': [
			{
				'title': 'Test Book 1',
				'author': 'Test Author',
				'quantity': 2,
				'price': 14.95
			}
		]
	}
	
	result = send_order_confirmation_email(test_email, customer_name, order_details)
	print(f"Order confirmation test result: {result}")
	return result

def test_admin_notification():
	"""Test admin order notification"""
	print("\n=== Testing Admin Order Notification ===")
	
	admin_order_details = {
		'customer_name': 'Test Customer',
		'customer_email': 'customer@test.com',
		'date': 'November 8, 2024 at 2:30 PM',
		'total': 29.95,
		'payment_method': 'Credit Card',
		'items': [
			{
				'title': 'Test Book 1',
				'author': 'Test Author',
				'quantity': 2,
				'price': 14.95
			}
		]
	}
	
	result = send_admin_order_notification(admin_order_details)
	print(f"Admin notification test result: {result}")
	return result

def check_admin_users():
	"""Check if there are admin users with notifications enabled"""
	print("\n=== Checking Admin Users ===")
	try:
		from app import User, app, db
		
		with app.app_context():
			admin_users = User.query.filter_by(is_manager=True).all()
			print(f"Total admin users: {len(admin_users)}")
			
			notification_enabled_admins = User.query.filter_by(is_manager=True, receive_notifications=True).all()
			print(f"Admin users with notifications enabled: {len(notification_enabled_admins)}")
			
			for admin in admin_users:
				print(f"- Admin: {admin.username}, Email: {admin.email}, Notifications: {admin.receive_notifications}")
				
	except Exception as e:
		print(f"Error checking admin users: {e}")

if __name__ == "__main__":
	# Test email functionality
	print("Testing Email Notification System...")
	print("=====================================")
	
	# Check admin users first
	check_admin_users()
	
	# Test basic email
	basic_result = test_basic_email()
	
	# Test order confirmation
	confirmation_result = test_order_confirmation()
	
	# Test admin notification 
	admin_result = test_admin_notification()
	
	print("\n=== Summary ===")
	print(f"Basic email: {'PASS' if basic_result else 'FAIL'}")
	print(f"Order confirmation: {'PASS' if confirmation_result else 'FAIL'}")
	print(f"Admin notification: {'PASS' if admin_result else 'FAIL'}")