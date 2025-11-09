#!/usr/bin/env python3
"""
Test the customer order status update email functionality
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.app import app, send_customer_order_status_update

def test_customer_order_status_email():
 with app.app_context():
 print("[DEBUG] TESTING CUSTOMER ORDER STATUS EMAIL")
 print("=" * 45)
 
 # Test email details
 customer_email = "samantha199054@gmail.com"
 customer_name = "Test Customer"
 order_id = 11
 old_status = "Confirmed"
 new_status = "Shipped"
 
 order_details = {
 'book_title': 'Test Book Title',
 'book_author': 'Test Author',
 'quantity': 2
 }
 
 try:
 print(f"[EMAIL] Sending test order status update email...")
 print(f" To: {customer_email}")
 print(f" Customer: {customer_name}")
 print(f" Order: #{order_id}")
 print(f" Status: {old_status} → {new_status}")
 
 result = send_customer_order_status_update(
 customer_email=customer_email,
 customer_name=customer_name,
 order_id=order_id,
 old_status=old_status,
 new_status=new_status,
 order_details=order_details
 )
 
 if result:
 print("[SUCCESS] Customer order status update email sent successfully!")
 print(" Check the customer's email inbox")
 else:
 print("[ERROR] Failed to send customer order status update email")
 
 except Exception as e:
 print(f"[ERROR] Error sending customer order status update email: {e}")
 import traceback
 traceback.print_exc()

if __name__ == "__main__":
 test_customer_order_status_email()