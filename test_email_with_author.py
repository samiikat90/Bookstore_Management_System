#!/usr/bin/env python3

"""
Test script to verify email notifications work with proper book data
"""

import os
import sys

# Add the app directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

# Import functions from app.py
from app import send_order_confirmation_email, send_admin_order_notification

def test_with_real_book_data():
 """Test email notifications with complete book data including author"""
 print("=== Testing Email Notifications with Complete Book Data ===")
 
 # Test customer order confirmation with complete data
 order_details = {
 'total': 29.95,
 'date': 'November 8, 2025 at 2:30 PM',
 'payment_method': 'Credit Card',
 'items': [
 {
 'title': 'Test Book 1',
 'author': 'Test Author', # This was missing!
 'quantity': 2,
 'price': 14.95
 }
 ]
 }
 
 print("Testing customer order confirmation...")
 customer_result = send_order_confirmation_email(
 customer_email="chapter6aplottwist@gmail.com",
 customer_name="Test Customer",
 order_details=order_details
 )
 print(f"Customer notification result: {'PASS' if customer_result else 'FAIL'}")
 
 # Test admin order notification with complete data 
 admin_order_details = {
 'customer_name': 'Test Customer',
 'customer_email': 'customer@test.com',
 'date': 'November 8, 2025 at 2:30 PM',
 'total': 29.95,
 'payment_method': 'Credit Card',
 'items': [
 {
 'title': 'Test Book 1',
 'author': 'Test Author', # This was missing!
 'quantity': 2,
 'price': 14.95
 }
 ]
 }
 
 print("Testing admin order notification...")
 admin_result = send_admin_order_notification(admin_order_details)
 print(f"Admin notification result: {'PASS' if admin_result else 'FAIL'}")
 
 return customer_result and admin_result

if __name__ == "__main__":
 print("Testing Email Notifications with Fixed Data...")
 print("=" * 50)
 
 success = test_with_real_book_data()
 
 print("\n" + "=" * 50)
 print(f"Overall test result: {'SUCCESS' if success else 'FAILED'}")
 
 if success:
 print("Email notifications should now work during checkout!")
 else:
 print("Still have issues - check the error messages above.")